"""13_matched_lists.py -- full-data neighbour lists N(g) and matched lists M(g) (DESIGN.md v2.3 §3.1, §2.2).

N(g): from the full zavg_BEF matrix (scripts/10), neighbours.top_k with diagonal -> -inf, columns restricted to tool
background genes, same-arm genes and Ensembl 116 paralogues of g removed (all homology types, as in the
pre-registered tandem-cluster stratum). The top 100 are stored (data/derived/neighbours/full_top100.npz); N(g) = the
first K = 25 (frozen predictor.k_neighbours). ``assert_valid`` is run on every row.

Chromosome arm: from the HGNC ``location`` (results/ids/hgnc_hub.tsv): chromosome + first p/q letter ('17q24.3' ->
'17q'); a range uses the arm of its first band (none of the 18,434 DepMap genes crosses the centromere); a location
listing two places ('Xp22.33 and Yp11.2', PAR genes) uses the first; 'mitochondria' -> one arm 'MT'; a location
without p/q would be 'unknown' and get no same-arm exclusion (count reported; 0 at build time).

M(g), for every scorable gene g: the 500 nearest scorable genes by Mahalanobis distance on (mean effect, log SD,
NaN fraction) (``predictor.profile_covariates`` on CRISPRGeneEffect; inverse covariance of all scorable genes, so
one metric for every query), BG status (tool background, NaN fraction < 0.10) matched exactly, excluding g, N(g),
genes on g's arm and paralogues of g; caliper 0.2 Mahalanobis units with nearest-available fallback
(``predictor.match_genes(mode='relaxed', caliper_metric='mahalanobis')``): the list is ordered by distance, so all
within-caliper genes come first and fallback genes fill the remainder; a "violation" = a match with distance > 0.2.
Seed 0 (frozen seeds.matched_lists; the procedure is deterministic, ties by lower matrix index).

Outputs: data/derived/neighbours/full_top100.npz; data/derived/matched/matched_lists.npz (query positions, 500
matched positions, distances, n_admissible) + genes index; results/verification/matched_lists.md (violation rates,
SMD balance overall / by BG stratum / U / H, first 5 / first 200 / all 500).
Run: .env/bin/python -I scripts/13_matched_lists.py
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

from src import neighbours as nbm  # noqa: E402
from src import predictor as pr  # noqa: E402
from src.coess_matrix import open_matrix  # noqa: E402

K = C.fz("predictor", "k_neighbours")
MSIZE = C.fz("predictor", "matched_list_size")
CAL = C.fz("predictor", "caliper_mahalanobis")
SEED = C.fz("seeds", "matched_lists")
KEEP = 100

effect = C.load_effect()
M, gt = open_matrix(C.FULL_DIR, "zavg_BEF")
assert (gt.gene.values == np.asarray(effect.columns)).all()
idx = C.gene_index(effect.columns)
assert (idx.hgnc_id.values == gt.hgnc_id.values).all()
arms = C.arms_for(idx)
arm = nbm.arm_codes(arms.arm.values)
par = C.paralogue_map(idx)
bg = gt.bg.values.astype(bool)
scor = gt.scorable.values.astype(bool)
G = len(gt)

# ---------------------------------------------------------------- N(g)
t = time.perf_counter()
nb = nbm.top_k(M, KEEP, bg=bg, arm=arm, paralogues=par)
nbm.assert_valid(nb, bg=bg, arm=arm, paralogues=par)
t_nb = time.perf_counter() - t
out_nb = C.DERIVED / "neighbours"
out_nb.mkdir(parents=True, exist_ok=True)
np.savez(out_nb / "full_top100.npz", rows=nb.rows, ids=nb.ids.astype(np.int32), z=nb.z,
         hgnc_id=np.asarray(gt.hgnc_id.tolist(), dtype="U"))
nK = nbm.Neighbours(rows=nb.rows, ids=nb.ids[:, :K], z=nb.z[:, :K], K=K)
n_short = int((nb.ids[:, K - 1] < 0).sum())
C.log(f"N(g): top-{KEEP} for {G} genes in {t_nb:.0f} s; rows with < {K} admissible neighbours: {n_short}")

# ---------------------------------------------------------------- M(g)
cov = pr.profile_covariates(effect)
cov.index = np.arange(G)
Cv = cov.to_numpy()
ok = scor & np.isfinite(Cv).all(1)
VI = np.linalg.pinv(np.cov(Cv[ok], rowvar=False))
queries = np.flatnonzero(ok)
t = time.perf_counter()
m = pr.match_genes(cov, queries, ok, MSIZE, caliper=CAL, mode="relaxed", nb=nK, arm=arm, paralogues=par,
                   seed=SEED, caliper_metric="mahalanobis", exact=bg.astype(int), vi=VI)
t_m = time.perf_counter() - t
C.log(f"M(g): {len(queries)} queries in {t_m:.0f} s")
ids = np.full((len(queries), MSIZE), -1, np.int32)
dist = np.full((len(queries), MSIZE), np.nan, np.float32)
for i, q in enumerate(queries):
    v = m.matches[int(q)]
    ids[i, :len(v)] = v
    dist[i, :len(v)] = m.distances[int(q)]
nadm = np.array([m.n_admissible[int(q)] for q in queries])
# integrity checks
for i, q in enumerate(queries):
    v = ids[i][ids[i] >= 0]
    assert q not in v and (bg[v] == bg[q]).all() and scor[v].all()
    assert not np.isin(v, nb.ids[np.searchsorted(nb.rows, q), :K]).any()
    if arm[q] >= 0:
        assert (arm[v] != arm[q]).all()
    if q in par:
        assert not np.isin(v, par[q]).any()
out_m = C.DERIVED / "matched"
out_m.mkdir(parents=True, exist_ok=True)
np.savez(out_m / "matched_lists.npz", queries=queries, ids=ids, dist=dist, n_admissible=nadm,
         hgnc_id=np.asarray(gt.hgnc_id.tolist(), dtype="U"), caliper=CAL, M=MSIZE, seed=SEED)
cov.assign(hgnc_id=gt.hgnc_id.values, bg=bg.astype(int), scorable=scor.astype(int), arm=arms.arm.values,
           arm_rule=arms.arm_rule.values,
           n_paralogues=[len(par.get(i, [])) for i in range(G)]).to_csv(out_m / "covariates.tsv", sep="\t",
                                                                          index_label="matrix_index")

# ---------------------------------------------------------------- report
U = pd.read_csv(C.ROOT / C.U_TSV, sep="\t", dtype={"hgnc_id": str})
H = pd.read_csv(C.ROOT / "results/holdout/H_genes.tsv", sep="\t", dtype={"hgnc_id": str})
pos = pd.Series(np.arange(G), index=gt.hgnc_id.values)
isU = np.isin(queries, pos.reindex(U.hgnc_id).dropna().astype(int).values)
isH = np.isin(queries, pos.reindex(H.hgnc_id).dropna().astype(int).values)


def viol(sel, n):
    d = dist[sel][:, :n]
    full = (ids[sel][:, :n] >= 0).all(1)
    return (np.nanmean(d > CAL), float(np.mean((d <= CAL).all(1))), float(full.mean()),
            float(np.nanmedian(d[:, -1])))


def bal(sel, n):
    q = queries[sel]
    mm = pr.Matches(matches={int(a): ids[i][:n][ids[i][:n] >= 0] for a, i in zip(q, np.flatnonzero(sel))},
                    n_admissible={}, n_outside_caliper={}, M=n, caliper=CAL, mode="relaxed")
    b = pr.balance(cov, q, mm)
    return {r.covariate: r.smd for r in b.itertuples()}


groups = [("all scorable", np.ones(len(queries), bool)), ("BG (tool background)", bg[queries]),
          ("non-BG", ~bg[queries]), ("U (scorable)", isU), ("H", isH)]
vrows, brows = [], []
for name, sel in groups:
    for n in (5, 200, MSIZE):
        v = viol(sel, n)
        vrows.append(f"| {name} | {sel.sum()} | first {n} | {v[0]:.3f} | {v[1]:.3f} | {v[2]:.3f} | {v[3]:.3f} |")
        b = bal(sel, n)
        brows.append(f"| {name} | first {n} | {b['mean']:+.3f} | {b['log_sd']:+.3f} | {b['nan_fraction']:+.3f} |")
qa = np.quantile(nadm, [0, 0.1, 0.5, 0.9])
qa_bg = np.quantile(nadm[bg[queries]], [0.1, 0.5])
qa_nbg = np.quantile(nadm[~bg[queries]], [0.1, 0.5])
run = C.write_manifest(out_m / "run_manifest.json", "scripts/13_matched_lists.py", g,
                       [C.EFFECT_CSV, C.HUB_TSV, C.PARALOGUE_TSV, C.U_TSV, "results/holdout/H_genes.tsv",
                        "data/derived/matrices/zavg_full/genes.tsv"], seed=SEED, t0=t0,
                       extra=dict(K=K, keep=KEEP, M=MSIZE, caliper=CAL, n_queries=int(len(queries)),
                                  violation_rate_all500=float(np.nanmean(dist > CAL)),
                                  runtime_neighbours_s=round(t_nb, 1), runtime_matching_s=round(t_m, 1)))
npar = np.array([len(par.get(i, [])) for i in range(G)])
L = ["# Matched lists M(g) and full-data neighbour lists N(g) (DESIGN §3.1)", "",
     f"Generated by `scripts/13_matched_lists.py` ({run['created']}; runtime {run['runtime_s']} s, peak RSS "
     f"{run['peak_rss_gb']} GB; neighbours {t_nb:.0f} s, matching {t_m:.0f} s). Gate: tag `{g['tag']}` @ "
     f"{g['tag_commit'][:10]}. Seed {SEED}.", "",
     "## Neighbour lists N(g)", "",
     f"- Full zavg_BEF matrix, {G} genes; candidates = {int(bg.sum())} tool-background genes; self (NaN diagonal "
     f"-> -inf), same-arm genes and Ensembl 116 paralogues (all homology types) excluded; top {KEEP} stored, "
     f"N(g) = first {K}. `neighbours.assert_valid` passed for all {G} rows; rows with < {K} admissible neighbours: "
     f"{n_short}.",
     f"- Arms from HGNC `location`: rule counts {arms.arm_rule.value_counts().to_dict()}; genes without an arm "
     f"(no same-arm exclusion): {int((arm < 0).sum())}. Handling: chromosome + first p/q letter; ranges use the "
     "first band's arm (none crosses the centromere); 'X… and Y…' PAR locations use the first; 'mitochondria' = "
     "one arm 'MT'; a location with no p/q would be unknown (none here). Number of distinct arms: "
     f"{len(set(arm[arm >= 0]))}.",
     f"- Paralogues: {int((npar > 0).sum())} of {G} genes have >= 1 paralogue in the matrix (median "
     f"{int(np.median(npar[npar > 0]))}, max {int(npar.max())}).", "",
     "## Matched lists M(g)", "",
     f"- Queries: every scorable gene ({len(queries)}; {int(bg[queries].sum())} BG, {int((~bg[queries]).sum())} "
     f"non-BG). Pool: scorable genes with the same BG status, excluding g, N(g) (K = {K}), same-arm genes and "
     f"paralogues. Mahalanobis distance on (mean effect, log SD (ddof 0), NaN fraction), inverse covariance of all "
     f"scorable genes; caliper {CAL}; nearest-available fallback; M = {MSIZE}.",
     f"- Genes within the caliper (admissible) per query: min {qa[0]:.0f}, 10th pct {qa[1]:.0f}, median "
     f"{qa[2]:.0f}, 90th pct {qa[3]:.0f}; BG queries 10th/50th pct {qa_bg[0]:.0f}/{qa_bg[1]:.0f}; non-BG "
     f"{qa_nbg[0]:.0f}/{qa_nbg[1]:.0f}.",
     f"- **Violation rate (matches beyond the caliper, all 500): {np.nanmean(dist > CAL):.3f}**; "
     f"first 200: {np.nanmean(dist[:, :200] > CAL):.3f}; first 5: {np.nanmean(dist[:, :5] > CAL):.3f}.", "",
     "| queries | n | matches | violation rate | queries with no violation | queries with full list | median "
     "distance of last match |", "|---|---|---|---|---|---|---|", *vrows, "",
     "SMD balance (query mean − matched mean, pooled SD; each query's matches weighted 1/|M(g)|; "
     "`predictor.balance`):", "",
     "| queries | matches | SMD mean effect | SMD log SD | SMD NaN fraction |", "|---|---|---|---|---|", *brows, "",
     "Files: `data/derived/neighbours/full_top100.npz` (rows, ids, z, hgnc_id; matrix positions), "
     "`data/derived/matched/matched_lists.npz` (queries, ids 500 per query nearest first, dist, n_admissible), "
     "`data/derived/matched/covariates.tsv`.", ""]
dst = C.ROOT / "results" / "verification" / "matched_lists.md"
dst.write_text("\n".join(L))
C.log(f"wrote {dst}")
