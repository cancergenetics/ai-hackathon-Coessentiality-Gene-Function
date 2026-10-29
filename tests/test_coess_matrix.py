"""Toy tests for src/coess_matrix.py: tool matrices via the block API, Pearson / GLS full matrices vs the tool's
Baselines, line subsetting. Synthetic data only.

Run: .env/bin/python -I -m pytest -q tests/test_coess_matrix.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import coess_matrix as cm  # noqa: E402
from coessential import all_pairs  # noqa: E402
from coessential.baselines import Baselines  # noqa: E402
from coessential.method import Config  # noqa: E402

CFG = Config(k=0, tau=0.1, q=2.5, d=16, n_null=5000, block=128)   # small-data config; 128-gene blocks


def toy_effect(n_lines=120, G=400, seed=0):
    """Modules of 15 genes (genes 0..89) + noise, with block-structured and idiosyncratic missingness:
    genes 300-329 miss lines 0-19 (a 'library'), genes 330-334 miss 5 random lines each, gene 335 misses 60% of
    lines (non-background), gene 336 misses lines 100-119 only."""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n_lines, G)) - 0.2
    for m in range(6):
        X[:, m * 15:(m + 1) * 15] += rng.standard_normal((n_lines, 1))
    X[:20, 300:330] = np.nan
    for g in range(330, 335):
        X[rng.choice(n_lines, 5, replace=False), g] = np.nan
    X[rng.choice(n_lines, int(0.6 * n_lines), replace=False), 335] = np.nan
    X[100:, 336] = np.nan
    lines = [f"ACH-{i:06d}" for i in range(n_lines)]
    genes = [f"G{j} ({j + 1})" for j in range(G)]
    return pd.DataFrame(X.astype(np.float32), index=lines, columns=genes)


@pytest.fixture(scope="module")
def effect():
    return toy_effect()


@pytest.fixture(scope="module")
def written(effect, tmp_path_factory):
    out = tmp_path_factory.mktemp("tool")
    fm = cm.fit_model(effect, CFG)
    man = cm.write_tool_matrices(fm, out, log=lambda *_: None)
    return fm, out, man


def test_tool_matrices_match_pair_api(written):
    fm, out, man = written
    res = cm.verify_tool_matrices(fm, out, n_pairs=20_000, seed=0)
    for k, r in res.items():
        assert r["n_nonfinite_mismatch"] == 0, k
        assert r["max_abs_diff"] < 1e-4, (k, r)


def test_tool_matrices_equal_tool_all_pairs(written):
    """Our memmap writer reproduces coessential.all_pairs.score_all_pairs (zavg_BEF, float32) exactly."""
    fm, out, _ = written
    mats, _, _ = all_pairs.score_all_pairs(fm.model, np.arange(fm.model.G), threshold=6.0)
    Z, _ = cm.open_matrix(out, "zavg_BEF")
    assert np.array_equal(np.asarray(Z), mats["zavg_BEF"], equal_nan=True)


def test_matrix_layout_and_manifest(written, effect):
    fm, out, man = written
    Z, gt = cm.open_matrix(out, "zavg_BEF")
    assert Z.dtype == np.float32 and Z.shape == (400, 400)
    assert np.isnan(np.diag(Z)).all()
    A = np.asarray(Z)
    assert np.array_equal(A, A.T, equal_nan=True)
    assert list(gt.gene) == list(effect.columns)
    assert gt.bg.sum() == man["n_bg"] == 400 - 32          # 30 'library' genes (20/120 NaN) + 335 + 336
    assert man["K_tool"] == round(0.025 * man["n_bg"])
    assert not man["published_config"]
    assert json.loads((out / "manifest.json").read_text())["n_lines"] == 120
    # module genes are each other's best partners
    assert np.nanmean(A[:15, :15]) > 3 and abs(np.nanmean(A[100:200, 100:200])) < 1


def test_block_source_matches_matrix(written):
    fm, out, _ = written
    Z, _ = cm.open_matrix(out, "z_E")
    src = cm.ModelBlockSource(fm, "z_E")
    seen = []
    for rows, blk in src.iter_blocks(rows=[3, 130, 399]):
        ref = np.asarray(Z[rows], dtype=np.float64)
        off = ~np.isnan(ref)                                     # diagonal is NaN in the stored matrix
        np.testing.assert_allclose(blk[off], ref[off], atol=1e-5)
        seen += list(rows)
    assert sorted(seen) == [3, 130, 399]


def test_gene_subset(effect, tmp_path):
    fm = cm.fit_model(effect, CFG)
    genes = effect.columns[::3]
    cm.write_tool_matrices(fm, tmp_path, genes=genes, kinds=("zavg_BEF",), log=lambda *_: None)
    Z, gt = cm.open_matrix(tmp_path, "zavg_BEF")
    full = fm.model.zavg_block(np.array([0]))[0, np.arange(0, 400, 3)]
    np.testing.assert_allclose(Z[0, 1:], full[1:], atol=1e-5)
    assert list(gt.gene) == list(genes)


def test_line_subset_drops_all_nan_genes(effect):
    lines = effect.index[:20]                                # genes 300-329 are all-NaN here
    fm = cm.fit_model(effect, CFG, lines=lines)
    assert fm.model.n == 20 and len(fm.dropped_genes) == 30
    assert set(fm.dropped_genes) == set(effect.columns[300:330])
    with pytest.raises(KeyError):
        cm.fit_model(effect, CFG, lines=["nope"])


@pytest.mark.parametrize("method", ["pearson", "gls"])
def test_baseline_matrices_match_tool(effect, method, tmp_path):
    X = effect.values
    man = cm.write_baseline_matrix(X, effect.columns, tmp_path, method)
    M = np.load(tmp_path / f"{method}.npy", mmap_mode="r")
    assert np.isnan(np.diag(M)).all()
    bl = Baselines(X)
    res = cm.verify_against_baselines(M, X, method, n_pairs=50_000, seed=0, baselines=bl)
    assert res["passed"], res
    # every pair touching an irregular-missingness gene, exhaustively
    ia = np.repeat(np.arange(300, 337), 400)
    ib = np.tile(np.arange(400), 37)
    keep = ia != ib
    ref = bl.score(method, ia[keep], ib[keep])
    got = np.asarray(M[ia[keep], ib[keep]], dtype=np.float64)
    assert np.array_equal(np.isnan(ref), np.isnan(got))
    assert np.nanmax(np.abs(ref - got)) < 1e-4
    if method == "gls":
        assert man["stats"]["n_patterns"] == 9                  # complete, library, 5 random, 335, 336


def test_baseline_gene_subset_uses_full_covariance(effect):
    X = effect.values
    gidx = np.arange(0, 400, 7)
    M, _ = cm.gls_matrix(X, gidx)
    res = cm.verify_against_baselines(M, X, "gls", gidx=gidx, n_pairs=5000)
    assert res["passed"], res


@pytest.mark.parametrize("method", ["pearson", "gls"])
def test_baseline_rows_match_tool_and_full_matrix(effect, method):
    """M4 addition: rows x cols baseline blocks equal Baselines.score and the square matrix (incl. self -> NaN,
    rows with block-structured / heavy missingness, columns a subset)."""
    X = effect.to_numpy()
    rows = np.array([3, 17, 300, 331, 335, 336, 399, 5])          # unsorted, mixed missingness patterns
    cols = np.r_[0:200, 300:340]                                  # includes some row genes (self pairs)
    f = cm.pearson_rows if method == "pearson" else (lambda *a, **k: cm.gls_rows(*a, chunk=17, **k)[0])
    M = f(X, rows, cols)
    assert M.shape == (len(rows), len(cols)) and M.dtype == np.float32
    bl = Baselines(X)
    ii, jj = np.meshgrid(np.arange(len(rows)), np.arange(len(cols)), indexing="ij")
    ii, jj = ii.ravel(), jj.ravel()
    selfp = rows[ii] == cols[jj]
    assert np.isnan(M[ii[selfp], jj[selfp]]).all() and selfp.sum() == 7
    ref = bl.score(method, rows[ii[~selfp]], cols[jj[~selfp]])
    got = M[ii[~selfp], jj[~selfp]].astype(np.float64)
    assert (np.isfinite(ref) == np.isfinite(got)).all()
    fin = np.isfinite(ref)
    assert np.abs(ref[fin] - got[fin]).max() < 1e-4
    full = cm.pearson_matrix(X) if method == "pearson" else cm.gls_matrix(X)[0]
    sub = full[np.ix_(rows, cols)]
    both = np.isfinite(sub) & np.isfinite(M)
    assert (np.isfinite(sub) == np.isfinite(M)).all() and np.abs(sub[both] - M[both]).max() < 1e-5
    v = cm.verify_rows_against_baselines(M, X, method, rows, cols, n_pairs=2000, baselines=bl)
    assert v["passed"] and v["n_compared"] > 1000
