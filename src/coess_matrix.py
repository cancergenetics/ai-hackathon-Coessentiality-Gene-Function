"""coess_matrix.py -- full gene x gene similarity matrices (DESIGN.md v2 §2.2, §4.2, §8).

Two families of matrices, both written as float32 ``.npy`` files (opened as memmaps; never committed) with an explicit
gene index TSV next to them:

1. **Tool matrices** -- zavg_BEF and its components z_B, z_E, z_F from the *unmodified*
   ``coessential.method.CoessentialityModel`` (tool @ 3c684c9). Values come from the model's genome-wide block API
   ``CoessentialityModel.z_block(rows)`` over the model's own fixed gene blocks (``Config.block`` genes), exactly as
   ``coessential.all_pairs.score_all_pairs`` does: zavg_BEF = (z_B + z_E + z_F) / 3 computed in float64, the upper
   triangle (row < column) is the computed value, the lower triangle its exact mirror, the diagonal NaN.
   ``fit_model`` optionally subsets cell lines (split halves, §4.2); genes with no observation in the chosen lines
   are dropped before fitting (the tool raises on them) and recorded. Background genes (NaN fraction < max_nan) and
   the tool's neighbour count K = round(q/100 * |BG|) are recorded in the gene table / manifest.
2. **Baseline matrices** -- pairwise-complete Pearson r and the GLS signed t-statistic (Wainberg et al. 2021) as
   defined by ``coessential.baselines.Baselines`` but computed blockwise:
   * Pearson: masked matmuls in float64 (NaN -> 0, observation mask O; per pair the sums n, Sx, Sy, Sxx, Syy, Sxy
     over the lines observed for both genes), r = cov / sqrt(vx vy), clipped to [-1, 1]; NaN where undefined.
   * GLS: genes are grouped by missingness pattern; for every pair of patterns (P, Q) the shared lines S = P & Q get
     the tool's own whitening (``baselines.sample_covariance`` of the FULL input matrix, ``baselines.whitening``),
     every gene of P and Q is warped, the warped intercept projected out, rows normalised, r = R_P R_Q', and
     t = r sqrt(df / (1 - r^2)), df = |S_kept| - 2 -- the arithmetic of ``Baselines._gls``.
   ``verify_against_baselines`` compares a stored matrix with ``Baselines.score`` on random pairs (gate: max abs
   diff < 1e-4); ``verify_tool_matrices`` compares the tool matrices with the model's pair API ``zavg``.

Memory (18.4k genes, ~1.1k lines): each float32 matrix is 1.35 GB on disk and is written row-block by row-block
through ``np.lib.format.open_memmap``; transient RAM per block is a few x (block x G x 8 bytes) (~150 MB for a
1024-gene block), plus the model state (< 1 GB). See docs/PIPELINE.md.

Nothing here reads DepMap files; callers pass a DataFrame (lines x genes). Scripts that call this on DepMap data must
pass ``gate.check()`` first.
"""
from __future__ import annotations

import json
import math
import platform
import resource
import time
from dataclasses import dataclass, field, fields
from pathlib import Path

import numpy as np
import pandas as pd

from coessential.baselines import Baselines, sample_covariance, whitening
from coessential.method import COMPONENTS, Config, CoessentialityModel

TOOL_KINDS = ("zavg_BEF", "z_B", "z_E", "z_F")
BASELINE_KINDS = ("pearson", "gls")
PUBLISHED_CONFIG = Config()


# ------------------------------------------------------------------------------------------ fitting
@dataclass
class FittedModel:
    """A fitted tool model with the labels it was fitted on.

    genes: column labels in model order (model gene index i <-> genes[i]); lines: row labels used;
    dropped_genes: input genes with no observation in ``lines`` (not in the model)."""
    model: CoessentialityModel
    genes: pd.Index
    lines: pd.Index
    dropped_genes: list = field(default_factory=list)
    fit_s: float = 0.0

    @property
    def config(self) -> Config:
        return self.model.cfg

    def gene_table(self) -> pd.DataFrame:
        """matrix-independent per-gene state: model_index, gene, bg, nan_fraction, mean, sd."""
        m = self.model
        return pd.DataFrame(dict(model_index=np.arange(m.G), gene=np.asarray(self.genes, dtype=object),
                                 bg=m.bg.astype(np.int8), nan_fraction=m.nan_frac, mean=m.mean, sd=m.sd))


def config_dict(cfg: Config) -> dict:
    return {f.name: getattr(cfg, f.name) for f in fields(cfg)}


def is_published_config(cfg: Config) -> bool:
    """True iff cfg equals the tool's published defaults (real DepMap runs must use these)."""
    return config_dict(cfg) == config_dict(PUBLISHED_CONFIG)


def fit_model(effect: pd.DataFrame, config: Config | None = None, lines=None) -> FittedModel:
    """Fit ``CoessentialityModel`` on a gene-effect DataFrame (rows = cell lines, columns = genes).

    lines: optional subset of row labels (order irrelevant; the input row order is kept). Values are cast to float32
    first, as ``coessential.data.load_depmap`` does, so results equal the tool's CLI path bit for bit."""
    cfg = PUBLISHED_CONFIG if config is None else config
    df = effect if lines is None else effect.loc[effect.index.isin(pd.Index(lines))]
    if lines is not None and len(df) != len(pd.Index(lines).unique()):
        raise KeyError("some requested lines are not rows of the effect matrix")
    X = np.asarray(df.values, dtype=np.float32)
    allnan = np.isnan(X).all(0)
    dropped = list(df.columns[allnan])
    if allnan.any():
        X = X[:, ~allnan]
    t = time.perf_counter()
    model = CoessentialityModel(X, cfg)
    return FittedModel(model=model, genes=df.columns[~allnan], lines=df.index, dropped_genes=dropped,
                       fit_s=time.perf_counter() - t)


def _gidx(fm: FittedModel, genes) -> np.ndarray:
    if genes is None:
        return np.arange(fm.model.G)
    pos = pd.Index(fm.genes).get_indexer(pd.Index(genes))
    if (pos < 0).any():
        raise KeyError(f"{int((pos < 0).sum())} genes not in the model")
    if not (np.diff(pos) > 0).all():
        raise ValueError("genes must be in model order without duplicates")
    return pos


def _peak_rss_gb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(r / (1e9 if platform.system() == "Darwin" else 1e6), 3)


def mirror_upper(M: np.ndarray, step: int = 2048) -> None:
    """In place: lower triangle := mirror of the upper triangle, diagonal := NaN (same as the tool's all_pairs)."""
    n = len(M)
    for i0 in range(0, n, step):
        i1 = min(i0 + step, n)
        M[i0:i1, :i0] = M[:i0, i0:i1].T
        D = np.array(M[i0:i1, i0:i1])
        lo = np.tril_indices(i1 - i0, -1)
        D[lo] = D.T[lo]
        np.fill_diagonal(D, np.nan)
        M[i0:i1, i0:i1] = D


# ------------------------------------------------------------------------------------------ tool matrices
class ModelBlockSource:
    """Row blocks of a tool score computed on the fly from a fitted model (no dense matrix; used for split halves).

    ``iter_blocks(rows)`` yields (matrix row positions, float64 block rows x n_genes) over the model's fixed gene
    blocks, restricted to the genes ``gidx`` (rows and columns)."""

    def __init__(self, fm: FittedModel, kind: str = "zavg_BEF", genes=None):
        if kind not in TOOL_KINDS:
            raise ValueError(kind)
        self.fm, self.kind = fm, kind
        self.gidx = _gidx(fm, genes)
        self.pos = np.full(fm.model.G, -1)
        self.pos[self.gidx] = np.arange(len(self.gidx))
        self.shape = (len(self.gidx), len(self.gidx))

    def iter_blocks(self, rows=None):
        m = self.fm.model
        want = None if rows is None else np.zeros(self.shape[0], bool)
        if want is not None:
            want[np.asarray(rows, dtype=np.int64)] = True
        for b in range(math.ceil(m.G / m.cfg.block)):
            mrows = np.arange(b * m.cfg.block, min((b + 1) * m.cfg.block, m.G))
            local = np.flatnonzero(self.pos[mrows] >= 0)
            if want is not None:
                local = local[want[self.pos[mrows[local]]]]
            if not len(local):
                continue
            Z = m.z_block(mrows)
            if self.kind == "zavg_BEF":
                blk = (Z["B"] + Z["E"] + Z["F"]) / 3.0
            else:
                blk = Z[self.kind[2:]]
            yield self.pos[mrows[local]], blk[local][:, self.gidx]


def write_tool_matrices(fm: FittedModel, out_dir, genes=None, kinds=TOOL_KINDS, extra_gene_columns=None,
                        hash_outputs: bool = False, log=print) -> dict:
    """Write dense float32 matrices ``<kind>.npy`` (memmap), ``genes.tsv`` and ``manifest.json`` to out_dir.

    genes: optional subset of model gene labels in model order (e.g. protein genes); default all model genes.
    extra_gene_columns: optional DataFrame indexed by gene label whose columns are added to genes.tsv (e.g. hgnc_id).
    Returns the manifest dict."""
    kinds = tuple(kinds)
    if any(k not in TOOL_KINDS for k in kinds):
        raise ValueError(f"kinds must be in {TOOL_KINDS}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    m = fm.model
    gidx = _gidx(fm, genes)
    n = len(gidx)
    pos = np.full(m.G, -1)
    pos[gidx] = np.arange(n)
    t_all = time.perf_counter()
    t = time.perf_counter()
    moments = {c: m.null_moments(c) for c in COMPONENTS}           # builds the whole genome-wide state
    t_state = time.perf_counter() - t
    mats = {k: np.lib.format.open_memmap(out / f"{k}.npy", mode="w+", dtype=np.float32, shape=(n, n)) for k in kinds}
    t = time.perf_counter()
    nb = math.ceil(m.G / m.cfg.block)
    for b in range(nb):
        rows = np.arange(b * m.cfg.block, min((b + 1) * m.cfg.block, m.G))
        local = np.flatnonzero(pos[rows] >= 0)
        if not len(local):
            continue
        ip = pos[rows[local]]
        Zb = m.z_block(rows)
        Z = {c: Zb[c][local][:, gidx] for c in COMPONENTS}
        del Zb
        if "zavg_BEF" in mats:
            mats["zavg_BEF"][ip] = (Z["B"] + Z["E"] + Z["F"]) / 3.0  # same arithmetic as zavg_block / all_pairs
        for c in COMPONENTS:
            if f"z_{c}" in mats:
                mats[f"z_{c}"][ip] = Z[c]
        log(f"block {b + 1}/{nb}: {len(ip)} rows ({time.perf_counter() - t:.0f} s)")
    t_block = time.perf_counter() - t
    t = time.perf_counter()
    for M in mats.values():
        mirror_upper(M)
        M.flush()
    t_mirror = time.perf_counter() - t
    gt = fm.gene_table().iloc[gidx].reset_index(drop=True)
    gt.insert(0, "matrix_index", np.arange(n))
    if extra_gene_columns is not None:
        gt = gt.join(extra_gene_columns, on="gene")
    gt.to_csv(out / "genes.tsv", sep="\t", index=False, float_format="%.6g")
    files = {f"{k}.npy": dict(dtype="float32", shape=[n, n]) for k in kinds}
    if hash_outputs:
        from .gate import sha256_file
        for name in files:
            files[name]["sha256"] = sha256_file(out / name)
    man = dict(
        kind="tool_matrices", created=time.strftime("%Y-%m-%dT%H:%M:%S"),
        config=config_dict(m.cfg), published_config=is_published_config(m.cfg),
        n_lines=int(m.n), lines=[str(x) for x in fm.lines], n_model_genes=int(m.G), n_matrix_genes=int(n),
        n_bg=int(m.n_bg), K_tool=int(m.K), dropped_all_nan_genes=[str(g) for g in fm.dropped_genes],
        null_moments={c: dict(mean=mu, sd=sd) for c, (mu, sd) in moments.items()},
        matrices="upper triangle = z_block value (row < col), lower = mirror, diagonal NaN; float32",
        files=files,
        runtime=dict(fit_s=round(fm.fit_s, 2), state_and_null_s=round(t_state, 2), blocks_s=round(t_block, 2),
                     mirror_s=round(t_mirror, 2), total_s=round(time.perf_counter() - t_all + fm.fit_s, 2),
                     peak_rss_gb=_peak_rss_gb()))
    (out / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    return man


def open_matrix(out_dir, kind: str, mmap: bool = True) -> tuple[np.ndarray, pd.DataFrame]:
    """(matrix (read-only memmap by default), gene table) written by write_tool_matrices / write_baseline_matrix."""
    out = Path(out_dir)
    M = np.load(out / f"{kind}.npy", mmap_mode="r" if mmap else None)
    gt = pd.read_csv(out / "genes.tsv", sep="\t", dtype={"gene": str})
    if len(gt) != M.shape[0]:
        raise ValueError("gene table and matrix disagree")
    return M, gt


def verify_tool_matrices(fm: FittedModel, out_dir, n_pairs: int = 100_000, seed: int = 0, genes=None) -> dict:
    """Max |stored - pair API| over random pairs for each stored tool matrix (pair API = model.zavg / model.z)."""
    gidx = _gidx(fm, genes)
    rng = np.random.default_rng(seed)
    n = len(gidx)
    i, j = rng.integers(0, n, n_pairs), rng.integers(0, n, n_pairs)
    keep = i != j
    i, j = i[keep], j[keep]
    za, Z = fm.model.zavg(gidx[i], gidx[j])
    ref = {"zavg_BEF": za, **{f"z_{c}": Z[c] for c in COMPONENTS}}
    res = {}
    for k in TOOL_KINDS:
        p = Path(out_dir) / f"{k}.npy"
        if not p.exists():
            continue
        M = np.load(p, mmap_mode="r")
        res[k] = _compare(np.asarray(M[i, j], dtype=np.float64), ref[k])
    return res


def _compare(got: np.ndarray, ref: np.ndarray) -> dict:
    fg, fr = np.isfinite(got), np.isfinite(ref)
    both = fg & fr
    d = np.abs(got[both] - ref[both])
    return dict(n=int(len(got)), n_compared=int(both.sum()), n_nonfinite_mismatch=int((fg != fr).sum()),
                max_abs_diff=float(d.max()) if len(d) else 0.0)


# ------------------------------------------------------------------------------------------ baselines
def _alloc(out_path, n):
    if out_path is None:
        return np.empty((n, n), np.float32)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    return np.lib.format.open_memmap(out_path, mode="w+", dtype=np.float32, shape=(n, n))


def pearson_matrix(X: np.ndarray, gidx=None, out_path=None, block: int = 512) -> np.ndarray:
    """Pairwise-complete Pearson r between the gene columns ``gidx`` of X (lines x genes), float32, NaN diagonal.

    Masked-matmul form (float64): with V = centred values (NaN -> 0) and O = observation mask, for genes a, b:
    n = O_a.O_b, Sx = V_a.O_b, Sy = O_a.V_b, Sxx = V_a^2.O_b, Syy = O_a.V_b^2, Sxy = V_a.V_b over lines; the
    per-gene centring by the overall observed mean leaves r unchanged and reduces cancellation."""
    X = np.asarray(X, dtype=np.float64)
    gidx = np.arange(X.shape[1]) if gidx is None else np.asarray(gidx)
    Xg = X[:, gidx]
    O = (~np.isnan(Xg)).astype(np.float64)
    V = np.nan_to_num(Xg - np.nanmean(Xg, 0))
    V2 = V * V
    OT, VT, V2T = O.T.copy(), V.T.copy(), V2.T.copy()           # genes x lines
    n = Xg.shape[1]
    M = _alloc(out_path, n)
    for r0 in range(0, n, block):
        r = slice(r0, min(r0 + block, n))
        cnt = OT[r] @ O
        sx, sy = VT[r] @ O, OT[r] @ V
        sxx, syy = V2T[r] @ O, OT[r] @ V2
        sxy = VT[r] @ V
        with np.errstate(invalid="ignore", divide="ignore"):
            cov = sxy - sx * sy / cnt
            vx = sxx - sx * sx / cnt
            vy = syy - sy * sy / cnt
            R = cov / np.sqrt(vx * vy)
        R[(cnt < 2) | ~(vx > 0) | ~(vy > 0)] = np.nan
        M[r] = np.clip(R, -1.0, 1.0)
    idx = np.arange(n)
    M[idx, idx] = np.nan
    if hasattr(M, "flush"):
        M.flush()
    return M


def missingness_patterns(X: np.ndarray, gidx=None) -> tuple[np.ndarray, list]:
    """(pattern id per gene of gidx, list of boolean observed-line masks), first-seen order."""
    X = np.asarray(X)
    gidx = np.arange(X.shape[1]) if gidx is None else np.asarray(gidx)
    valid = ~np.isnan(X[:, gidx])
    keys = [valid[:, j].tobytes() for j in range(valid.shape[1])]
    uniq = {k: i for i, k in enumerate(dict.fromkeys(keys))}
    return np.array([uniq[k] for k in keys], dtype=np.int64), [np.frombuffer(k, dtype=bool) for k in uniq]


def gls_matrix(X: np.ndarray, gidx=None, out_path=None, chunk: int = 1024, log=None) -> tuple[np.ndarray, dict]:
    """GLS signed t between the gene columns ``gidx`` of X (lines x genes), float32, NaN diagonal; plus stats.

    The line covariance is estimated on ALL columns of X (as ``Baselines(X)`` does), so pass the full matrix and
    select genes with gidx."""
    X = np.asarray(X)
    gidx = np.arange(X.shape[1]) if gidx is None else np.asarray(gidx)
    XT = np.ascontiguousarray(np.asarray(X[:, gidx], dtype=np.float64).T)    # genes x lines
    sigma = sample_covariance(X)
    pid, pmask = missingness_patterns(X, gidx)
    members = [np.flatnonzero(pid == p) for p in range(len(pmask))]
    n = len(gidx)
    M = _alloc(out_path, n)
    cache: dict = {}

    def white(S):
        key = S.tobytes()
        if key not in cache:                             # identical to Baselines._whiten
            A, keep = whitening(sigma[np.ix_(S, S)])
            w0 = A.sum(1)
            cache[key] = (A, np.flatnonzero(S)[keep], w0 / np.linalg.norm(w0))
        return cache[key]

    def warp(genes, A, Sk, w0):
        W = np.nan_to_num(XT[genes][:, Sk]) @ A.T
        R = W - np.outer(W @ w0, w0)
        with np.errstate(invalid="ignore", divide="ignore"):
            return R / np.linalg.norm(R, axis=1, keepdims=True)

    t0 = time.perf_counter()
    npair = 0
    for p in range(len(pmask)):
        for q in range(p, len(pmask)):
            S = pmask[p] & pmask[q]
            gp, gq = members[p], members[q]
            A, Sk, w0 = white(S)
            df = A.shape[0] - 2
            npair += 1
            if df < 1:
                M[np.ix_(gp, gq)] = np.nan
                M[np.ix_(gq, gp)] = np.nan
                continue
            Rq = warp(gq, A, Sk, w0)
            for c0 in range(0, len(gp), chunk):
                rows = gp[c0:c0 + chunk]
                Rp = Rq[c0:c0 + chunk] if p == q else warp(rows, A, Sk, w0)
                r = np.clip(Rp @ Rq.T, -1.0, 1.0)
                with np.errstate(invalid="ignore", divide="ignore"):
                    t = (r * np.sqrt(df / (1.0 - r * r))).astype(np.float32)
                M[np.ix_(rows, gq)] = t
                if p != q:
                    M[np.ix_(gq, rows)] = t.T
            while len(cache) > 256:                          # bounded FIFO cache of whitening operators
                cache.pop(next(iter(cache)))
    idx = np.arange(n)
    M[idx, idx] = np.nan
    if hasattr(M, "flush"):
        M.flush()
    stats = dict(n_genes=n, n_patterns=len(pmask), n_pattern_pairs=npair, seconds=round(time.perf_counter() - t0, 2))
    if log:
        log(stats)
    return M, stats


def write_baseline_matrix(X: np.ndarray, genes: pd.Index, out_dir, method: str, gidx=None) -> dict:
    """Write ``<method>.npy`` (float32 memmap) + ``genes_<method>.tsv`` + ``manifest_<method>.json`` to out_dir.

    genes: labels of ALL columns of X; gidx selects the matrix genes (default all)."""
    if method not in BASELINE_KINDS:
        raise ValueError(method)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    gidx = np.arange(X.shape[1]) if gidx is None else np.asarray(gidx)
    t = time.perf_counter()
    stats = {}
    if method == "pearson":
        pearson_matrix(X, gidx, out / "pearson.npy")
    else:
        _, stats = gls_matrix(X, gidx, out / "gls.npy")
    pd.DataFrame(dict(matrix_index=np.arange(len(gidx)), gene=np.asarray(genes)[gidx])).to_csv(
        out / f"genes_{method}.tsv", sep="\t", index=False)
    man = dict(kind=method, n_lines=int(X.shape[0]), n_matrix_genes=int(len(gidx)), stats=stats,
               runtime=dict(total_s=round(time.perf_counter() - t, 2), peak_rss_gb=_peak_rss_gb()))
    (out / f"manifest_{method}.json").write_text(json.dumps(man, indent=1) + "\n")
    return man


def verify_against_baselines(M: np.ndarray, X: np.ndarray, method: str, gidx=None, n_pairs: int = 100_000,
                             seed: int = 0, baselines: Baselines | None = None) -> dict:
    """Compare stored matrix M (over genes gidx of X) with the tool's ``Baselines(X).score`` on random pairs.

    Returns n, n_compared, n_nonfinite_mismatch, max_abs_diff (acceptance: max_abs_diff < 1e-4 and no mismatch)."""
    if method not in BASELINE_KINDS:
        raise ValueError(method)
    gidx = np.arange(X.shape[1]) if gidx is None else np.asarray(gidx)
    rng = np.random.default_rng(seed)
    n = len(gidx)
    i, j = rng.integers(0, n, n_pairs), rng.integers(0, n, n_pairs)
    keep = i != j
    i, j = i[keep], j[keep]
    bl = baselines if baselines is not None else Baselines(X)
    ref = bl.score(method, gidx[i], gidx[j])
    out = _compare(np.asarray(M[i, j], dtype=np.float64), ref)
    out["passed"] = bool(out["max_abs_diff"] < 1e-4 and out["n_nonfinite_mismatch"] == 0)
    return out
