"""16_baseline_rows.py -- GLS and Pearson baseline rows (DESIGN.md v2.3 §2.2, §3.2, §3.3).

Rows: the hold-out genes H (results/holdout/H_genes.tsv), the LOO sample and the 14 named controls (frozen
holdout.named_controls + holdout.weak_controls); columns: all tool-background genes of the full data. Values: the
tool's baselines (``coessential.baselines``) -- pairwise-complete Pearson r and the GLS signed t (Wainberg et al.
2021) with the line covariance estimated on the whole CRISPRGeneEffect matrix -- computed blockwise by
``coess_matrix.pearson_rows`` / ``gls_rows`` and verified against the tool's ``Baselines.score`` on 100,000 random
(row, column) pairs (acceptance: max abs diff < 1e-4, no finiteness mismatch; frozen infra.pair_check_*).
The U top-40 rows (§2.2) are added at M6, after the ledger exists.

LOO sample (§3.2.1): 3,000 genes drawn without replacement (numpy default_rng(0).choice) from the sampling frame =
protein-coding universe genes (HGNC locus group "protein-coding gene") that are scorable (DepMap column + tool-mapped
UniProt) and in neither U nor H, sorted by numeric HGNC id; the sample is saved in draw order to results/loo_sample.tsv.

Outputs: data/derived/baselines/{pearson,gls}_rows.npy (float32 rows x BG columns), rows.tsv, cols.tsv,
run_manifest.json; results/loo_sample.tsv; results/verification/baseline_rows.md.
Run: .env/bin/python -I scripts/16_baseline_rows.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

t0 = time.perf_counter()
g = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from coessential.baselines import Baselines  # noqa: E402

from src import coess_matrix as cm  # noqa: E402

LOO_N = C.fz("predictor", "loo_sample_size")
LOO_SEED = C.fz("seeds", "loo_sample")
NPAIRS = C.fz("infra", "pair_check_min_pairs")
TOL = C.fz("infra", "pair_check_max_abs_diff")
CONTROLS = C.fz("holdout", "named_controls") + C.fz("holdout", "weak_controls")

effect = C.load_effect()
gt = C.load_full_index()
assert (gt.gene.values == np.asarray(effect.columns)).all()
G = len(gt)
pos = pd.Series(np.arange(G), index=gt.hgnc_id.values)
hub = C.load_hub()
U = pd.read_csv(C.ROOT / C.U_TSV, sep="\t", dtype={"hgnc_id": str})
H = pd.read_csv(C.ROOT / "results/holdout/H_genes.tsv", sep="\t", dtype={"hgnc_id": str})

# ---------------------------------------------------------------- LOO sample
idx = C.gene_index(effect.columns)
frame = idx[idx.in_universe & idx.scorable & ~idx.hgnc_id.isin(U.hgnc_id) & ~idx.hgnc_id.isin(H.hgnc_id)].copy()
frame["_n"] = frame.hgnc_id.str.replace("HGNC:", "").astype(int)
frame = frame.sort_values("_n").reset_index(drop=True)
draw = np.random.default_rng(LOO_SEED).choice(len(frame), size=LOO_N, replace=False)
loo = frame.iloc[draw][["hgnc_id", "symbol", "matrix_index", "depmap_column"]].reset_index(drop=True)
loo.insert(0, "draw_order", np.arange(1, LOO_N + 1))
loo["bg"] = gt.bg.values[loo.matrix_index.values].astype(bool)
kf = pd.read_csv(C.ROOT / "results/preregistration/gene_knownness_features.tsv", sep="\t", dtype={"hgnc_id": str},
                 usecols=["hgnc_id", "n_exp_informative_BPMF"])
loo = loo.merge(kf, on="hgnc_id", how="left")
loo_path = C.ROOT / "results" / "loo_sample.tsv"
if loo_path.exists():                       # committed at 8fcf923: must be reproduced exactly, never silently changed
    old = pd.read_csv(loo_path, sep="\t", dtype={"hgnc_id": str})
    assert old.hgnc_id.tolist() == loo.hgnc_id.tolist(), "results/loo_sample.tsv differs from the seed-0 redraw"
    loo_status = "reproduced exactly (existing file kept)"
else:
    loo.to_csv(loo_path, sep="\t", index=False)
    loo_status = "written"
C.log(f"LOO sample: {len(loo)} of a frame of {len(frame)}; {loo_status}")

# ---------------------------------------------------------------- controls
ap = hub[hub.locus_group == "protein-coding gene"].set_index("symbol")
ctrl = []
for s in CONTROLS:
    hid = ap.hgnc_id.get(s)
    ctrl.append(dict(symbol=s, hgnc_id=hid, matrix_index=pos.get(hid, np.nan) if hid else np.nan,
                     weak=s in C.fz("holdout", "weak_controls")))
ctrl = pd.DataFrame(ctrl)
assert ctrl.hgnc_id.notna().all(), ctrl

# ---------------------------------------------------------------- rows / cols
H["matrix_index"] = pos.reindex(H.hgnc_id).values
assert H.matrix_index.notna().all()
sets = {"H": set(H.matrix_index.astype(int)), "LOO": set(loo.matrix_index.astype(int)),
        "control": set(ctrl.matrix_index.dropna().astype(int))}
rows = np.array(sorted(set().union(*sets.values())), dtype=np.int64)
cols = np.flatnonzero(gt.bg.values.astype(bool))
rt = pd.DataFrame(dict(row_index=np.arange(len(rows)), matrix_index=rows, hgnc_id=gt.hgnc_id.values[rows],
                       symbol=gt.symbol.values[rows], bg=gt.bg.values[rows].astype(bool),
                       **{f"in_{k}": np.isin(rows, list(v)) for k, v in sets.items()}))
out = C.DERIVED / "baselines"
out.mkdir(parents=True, exist_ok=True)


def reusable(method):
    """An existing rows matrix is reused only if rows.tsv / cols.tsv list exactly these rows and columns, the array
    has the right shape, and it holds no exact 0.0 (memmaps are zero-initialised, so a run that died before filling
    a block leaves zeros). Values are then re-verified against Baselines.score like a fresh run."""
    f = out / f"{method}_rows.npy"
    try:
        r_old = pd.read_csv(out / "rows.tsv", sep="\t").matrix_index.to_numpy()
        c_old = pd.read_csv(out / "cols.tsv", sep="\t").matrix_index.to_numpy()
        Mx = np.load(f, mmap_mode="r")
    except (FileNotFoundError, ValueError, AttributeError):
        return False, "missing"
    if not (np.array_equal(r_old, rows) and np.array_equal(c_old, cols)):
        return False, "row/column index differs"
    if Mx.shape != (len(rows), len(cols)) or Mx.dtype != np.float32:
        return False, f"shape/dtype {Mx.shape} {Mx.dtype}"
    nz = sum(int((np.asarray(Mx[i:i + 512]) == 0).sum()) for i in range(0, len(rows), 512))
    if nz:
        return False, f"{nz} exact zeros (incomplete run)"
    return True, "reused (index, shape, completeness checked; values re-verified)"


reuse = {m: reusable(m) for m in ("pearson", "gls")}
C.log(f"existing rows: {reuse}")
rt.to_csv(out / "rows.tsv", sep="\t", index=False)
pd.DataFrame(dict(col_index=np.arange(len(cols)), matrix_index=cols, hgnc_id=gt.hgnc_id.values[cols])).to_csv(
    out / "cols.tsv", sep="\t", index=False)
C.log(f"rows {len(rows)} (H {len(sets['H'])}, LOO {len(sets['LOO'])}, controls {len(sets['control'])}); "
      f"cols {len(cols)}")

X = effect.to_numpy()
res, stats = {}, {}
if reuse["pearson"][0]:
    stats["pearson"] = dict(seconds="reused")
else:
    t = time.perf_counter()
    cm.pearson_rows(X, rows, cols, out_path=out / "pearson_rows.npy")
    stats["pearson"] = dict(seconds=round(time.perf_counter() - t, 1))
C.log(f"pearson rows {stats['pearson']}")
if reuse["gls"][0]:
    pid, _ = cm.missingness_patterns(X)
    stats["gls"] = dict(n_rows=len(rows), n_cols=len(cols), n_row_patterns=int(len(np.unique(pid[rows]))),
                        n_col_patterns=int(len(np.unique(pid[cols]))),
                        n_pattern_pairs=int(len(np.unique(pid[rows])) * len(np.unique(pid[cols]))), seconds="reused")
else:
    _, stats["gls"] = cm.gls_rows(X, rows, cols, out_path=out / "gls_rows.npy", log=C.log)
bl = Baselines(X)
for method in ("pearson", "gls"):
    Mx = np.load(out / f"{method}_rows.npy", mmap_mode="r")
    t = time.perf_counter()
    res[method] = cm.verify_rows_against_baselines(Mx, X, method, rows, cols, n_pairs=NPAIRS + 1000, seed=0,
                                                   baselines=bl)
    res[method]["passed"] = bool(res[method]["max_abs_diff"] < TOL and res[method]["n_nonfinite_mismatch"] == 0
                                 and res[method]["n_compared"] >= NPAIRS)
    res[method]["verify_s"] = round(time.perf_counter() - t, 1)
    fin = np.isfinite(np.asarray(Mx)).mean()
    res[method]["finite_fraction"] = float(fin)
    C.log(f"{method}: {res[method]}")

run = C.write_manifest(out / "run_manifest.json", "scripts/16_baseline_rows.py", g,
                       [C.EFFECT_CSV, C.U_TSV, "results/holdout/H_genes.tsv", C.HUB_TSV,
                        "results/preregistration/gene_knownness_features.tsv",
                        "data/derived/matrices/zavg_full/genes.tsv"], seed=LOO_SEED, t0=t0,
                       extra=dict(verification=res, stats=stats, n_rows=int(len(rows)), n_cols=int(len(cols)),
                                  reuse={m: v[1] for m, v in reuse.items()}, loo_status=loo_status,
                                  controls=ctrl.to_dict("records")))
ok = all(r["passed"] for r in res.values())


def secs(st):
    return "n/a (reused)" if st["seconds"] == "reused" else f"{st['seconds']} s"


L = ["# GLS and Pearson baseline rows (DESIGN §2.2)", "",
     f"Generated by `scripts/16_baseline_rows.py` ({run['created']}; runtime {run['runtime_s']} s, peak RSS "
     f"{run['peak_rss_gb']} GB). Gate: tag `{g['tag']}` @ {g['tag_commit'][:10]}, tool {g['tool_commit'][:10]}.", "",
     f"**Verification against the tool's `Baselines.score`: {'PASS' if ok else 'FAIL'}.**", "",
     f"- Rows: {len(rows):,} genes = H {len(sets['H'])} ∪ LOO sample {len(sets['LOO'])} ∪ named controls "
     f"{len(sets['control'])} ({', '.join(ctrl.symbol)}); {int((~rt.bg).sum())} row genes are not tool "
     "background. Columns: all "
     f"{len(cols):,} tool-background genes. float32; NaN for a gene paired with itself.",
     f"- GLS: line covariance from all {X.shape[1]:,} columns (complete-data genes, as `Baselines(X)`); "
     f"{stats['gls']['n_row_patterns']} row × {stats['gls']['n_col_patterns']} column missingness patterns, "
     f"{stats['gls']['n_pattern_pairs']} pattern pairs, compute time {secs(stats['gls'])}. Pearson: compute time "
     f"{secs(stats['pearson'])}.",
     f"- Existing rows in `data/derived/baselines/` (from an earlier run of this script that died before writing its "
     f"manifest): Pearson -- {reuse['pearson'][1]}; GLS -- {reuse['gls'][1]}. Reuse requires identical row/column "
     "index, shape and no zero-initialised (unwritten) entries; reused values pass the same verification.",
     f"- Named controls (14 = frozen named + weak): "
     + "; ".join(f"{r.symbol} {'(weak) ' if r.weak else ''}{'row ' + str(int(r.matrix_index)) if pd.notna(r.matrix_index) else 'NOT in DepMap matrix'}"
                 for r in ctrl.itertuples()) + ".", "",
     "| method | pairs compared | max abs diff vs Baselines.score | finiteness mismatches | finite fraction of "
     "matrix | verification time (s) | pass (< 1e-4) |", "|---|---|---|---|---|---|---|",
     *[f"| {m} | {r['n_compared']:,} | {r['max_abs_diff']:.2e} | {r['n_nonfinite_mismatch']} | "
       f"{r['finite_fraction']:.4f} | {r['verify_s']} | {'PASS' if r['passed'] else 'FAIL'} |" for m, r in res.items()],
     "",
     f"## LOO sample (`results/loo_sample.tsv`)", "",
     f"- Frame: {len(frame):,} protein-coding, scorable genes in neither U nor H, sorted by numeric HGNC id; "
     f"{LOO_N:,} drawn with `numpy.random.default_rng({LOO_SEED}).choice(n, {LOO_N}, replace=False)`; saved in "
     f"draw order ({loo_status}). Tool background: {int(loo.bg.sum()):,}; with ≥ 1 informative experimental-evidence BP/MF term (current; "
     f"`gene_knownness_features.tsv` n_exp_informative_BPMF): "
     f"{int((loo.n_exp_informative_BPMF.fillna(0) > 0).sum()):,} "
     "(the frozen LOO definition does not condition on annotation; LOO genes without V2 targets score RR = 0 in "
     "M5 unless M5 decides otherwise).", "",
     "Files (git-ignored): `data/derived/baselines/{pearson,gls}_rows.npy`, `rows.tsv`, `cols.tsv`, "
     "`run_manifest.json`.", ""]
(C.ROOT / "results" / "verification" / "baseline_rows.md").write_text("\n".join(L))
C.log("done")
