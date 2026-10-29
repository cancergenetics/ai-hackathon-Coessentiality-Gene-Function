"""12_sanity_checks.py -- sign / orientation assertions on DepMap 26Q3 and the full zavg_BEF matrix (DESIGN §2.4).

Checks (each reported PASS/FAIL; thresholds from config/frozen.yaml where they exist):
A. Chronos sign
   A1 data-defined common essentials (effect < -0.5 in >= 90% of lines): count > 0 and mean effect < -0.5
      (frozen infra.common_essential_mean_max = -0.5);
   A2 canonical core essentials defined without DepMap (cytosolic ribosomal proteins, symbols ^RP[LS]\\d+A?$, and
      the 20S proteasome core, Complex Portal CPX-8806): median per-gene mean effect < -0.5;
   A3 non-expressed genes (log2(TPM+1) < 0.5 in >= 95% of CRISPR lines with expression, default entry per model):
      mean of per-gene mean effects within +-0.1 of 0 (|median| also reported) -- the expected ~0 orientation.
B. Matrix structure: exact symmetry M[i,j] == M[j,i] over the whole matrix (tile by tile; NaN == NaN), diagonal
   all NaN, off-diagonal NaN count; ``neighbours.top_k`` never returns the query with the NaN diagonal (2,000 random
   rows, no background restriction) and ``assert_valid`` passes.
C. Known co-complex pairs (Complex Portal members; UniProt -> HGNC hub -> matrix): Integrator core (CPX-6441),
   CCT/TRiC (CPX-6030), 28S and 39S mitoribosome (CPX-5225, CPX-5226), 20S proteasome (CPX-8806), 26S proteasome
   (CPX-5993), RNA exosome DIS3 variant (CPX-593): median within-complex zavg_BEF over background-gene pairs > 3
   (frozen infra.control_pair_min_score).
D. Random pairs: 1,000,000 random background-gene pairs (seed 0): mean ~ 0 (|mean| < 0.1), SD, fraction > 3.

Output: results/verification/sanity_checks.md (+ run manifest in data/derived/sanity/).
Run: .env/bin/python -I scripts/12_sanity_checks.py
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

t0 = time.perf_counter()
EXPR = "data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"
CPX = "data/raw/complexportal/9606.tsv"
g = C.gate_check(data_files=(C.EFFECT_CSV, EXPR, CPX))
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import neighbours as nbm  # noqa: E402
from src.coess_matrix import open_matrix  # noqa: E402

CE_MAX = C.fz("infra", "common_essential_mean_max")
PAIR_MIN = C.fz("infra", "control_pair_min_score")
DEP = C.fz("strata", "any_dependency_effect_max")              # -0.5
effect = C.load_effect()
M, gt = open_matrix(C.FULL_DIR, "zavg_BEF")
assert (gt.gene.values == np.asarray(effect.columns)).all()
X = effect.values.astype(np.float64)
bg = gt.bg.values.astype(bool)
mean_eff = np.nanmean(X, 0)
results = []


def add(check, passed, detail):
    results.append((check, "PASS" if passed else "FAIL", detail))
    C.log(f"{check}: {'PASS' if passed else 'FAIL'} {detail}")


# ---------------------------------------------------------------- A. Chronos sign
frac_dep = (X < DEP).sum(0) / (~np.isnan(X)).sum(0)
ce = frac_dep >= 0.9
add("A1 data-defined common essentials (< -0.5 in >= 90% lines): mean effect < -0.5",
    ce.sum() > 0 and mean_eff[ce].mean() < CE_MAX,
    f"n = {ce.sum()}, mean of per-gene means = {mean_eff[ce].mean():.3f}, max = {mean_eff[ce].max():.3f}")

hub = C.load_hub()
up2pos = {}
pos_of_hgnc = pd.Series(gt.index.values, index=gt.hgnc_id.values)
for hid, ups in zip(hub.hgnc_id, hub.uniprot_ids):
    if isinstance(ups, str) and hid in pos_of_hgnc.index:
        for u in ups.split("|"):
            up2pos.setdefault(u, set()).add(int(pos_of_hgnc[hid]))
cpx = pd.read_csv(C.ROOT / CPX, sep="\t", dtype=str)


def members(ac):
    row = cpx[cpx["#Complex ac"] == ac].iloc[0]
    ids = [re.sub(r"\(\d+\)$", "", x).split("-")[0] for x in row["Identifiers (and stoichiometry) of molecules in complex"].split("|")]
    pos, unm = set(), []
    for u in ids:
        p = up2pos.get(u)
        if p and len(p) == 1:
            pos |= p
        else:
            unm.append(u)
    return row["Recommended name"], np.array(sorted(pos)), unm


ribo = gt.symbol.str.match(r"^RP[LS]\d+A?$").values
_, prot20, _ = members("CPX-8806")
core = ribo.copy()
core[prot20] = True
add("A2 canonical core essentials (cytosolic RPL/RPS + 20S proteasome): median per-gene mean < -0.5",
    np.median(mean_eff[core]) < CE_MAX,
    f"n = {core.sum()} ({ribo.sum()} RP + {len(prot20)} 20S), median = {np.median(mean_eff[core]):.3f}, "
    f"fraction < -0.5 = {(mean_eff[core] < CE_MAX).mean():.2f}")

ex = pd.read_csv(C.ROOT / EXPR, low_memory=False)
ex = ex[ex.IsDefaultEntryForModel == "Yes"].drop_duplicates("ModelID").set_index("ModelID")
ex = ex.loc[ex.index.intersection(effect.index)]
gcols = [c for c in ex.columns if re.match(r"^.+ \(\d+\)$", c)]
E = ex[gcols].to_numpy(dtype=np.float64)
frac_low = (E < 0.5).mean(0)
nonexp_cols = pd.Index(gcols)[frac_low >= 0.95]
ne = gt.gene.isin(nonexp_cols).values
ne_bg = ne & bg
add("A3 non-expressed genes (log2(TPM+1) < 0.5 in >= 95% of lines): mean effect ~ 0 (|mean| < 0.1)",
    abs(mean_eff[ne].mean()) < 0.1,
    f"{len(ex)} lines with expression; n = {ne.sum()} genes in the effect matrix; mean = {mean_eff[ne].mean():.3f}, "
    f"median = {np.median(mean_eff[ne]):.3f}, fraction with any-dependency (>= 1% lines < -0.5) = "
    f"{(frac_dep[ne] >= 0.01).mean():.3f}; all genes: mean = {mean_eff.mean():.3f}")

# ---------------------------------------------------------------- B. matrix structure
n = M.shape[0]
step = 2048
asym, nan_mismatch = 0, 0
for i0 in range(0, n, step):
    A = np.asarray(M[i0:i0 + step])
    for j0 in range(i0, n, step):
        a = A[:, j0:j0 + step]
        b = np.asarray(M[j0:j0 + step, i0:i0 + step]).T
        both = np.isfinite(a) & np.isfinite(b)
        asym += int((a[both] != b[both]).sum())
        nan_mismatch += int((np.isnan(a) != np.isnan(b)).sum())
diag = np.asarray([M[i, i] for i in range(n)])
off_nan = 0
for i0 in range(0, n, step):
    A = np.isnan(np.asarray(M[i0:i0 + step]))
    A[np.arange(A.shape[0]), np.arange(i0, i0 + A.shape[0])] = False
    off_nan += int(A.sum())
add("B1 exact symmetry (all pairs)", asym == 0 and nan_mismatch == 0,
    f"asymmetric finite pairs = {asym}, NaN-pattern mismatches = {nan_mismatch}")
add("B2 diagonal NaN", bool(np.isnan(diag).all()), f"{int(np.isnan(diag).sum())}/{n} NaN; off-diagonal NaN = {off_nan}")
rng = np.random.default_rng(0)
rows = np.sort(rng.choice(n, 2000, replace=False))
nb = nbm.top_k(M, 25, rows=rows)
self_hits = int(sum(r in ids for r, ids in zip(nb.rows, nb.ids)))
nbm.assert_valid(nb)
add("B3 NaN diagonal handled by neighbours.top_k (no self, no BG restriction)", self_hits == 0,
    f"2,000 random rows, K = 25: self returned {self_hits} times; assert_valid passed")

# ---------------------------------------------------------------- C. known complexes
crow = []
for ac, label in [("CPX-6441", "Integrator core"), ("CPX-6030", "CCT/TRiC"), ("CPX-5225", "28S mitoribosome"),
                  ("CPX-5226", "39S mitoribosome"), ("CPX-8806", "20S proteasome"), ("CPX-5993", "26S proteasome"),
                  ("CPX-593", "RNA exosome (DIS3)")]:
    name, pos, unm = members(ac)
    pb = pos[bg[pos]]
    S = np.asarray(M[np.ix_(pb, pb)], dtype=np.float64)
    iu = np.triu_indices(len(pb), 1)
    v = S[iu]
    v = v[np.isfinite(v)]
    med = float(np.median(v))
    crow.append(f"| {label} | {ac} | {name} | {len(pos)} ({len(pb)} BG) | {len(unm)} | {len(v)} | {med:.2f} | "
                f"{np.mean(v):.2f} | {(v > PAIR_MIN).mean():.2f} | {'PASS' if med > PAIR_MIN else 'FAIL'} |")
    add(f"C {label} median within-complex zavg_BEF > {PAIR_MIN}", med > PAIR_MIN, f"median {med:.2f}, {len(v)} pairs")

# ---------------------------------------------------------------- D. random pairs
bgi = np.flatnonzero(bg)
i, j = bgi[rng.integers(0, len(bgi), 1_000_000)], bgi[rng.integers(0, len(bgi), 1_000_000)]
k = i != j
i, j = i[k], j[k]
o = np.lexsort((j, i))
v = np.asarray(M[i[o], j[o]], dtype=np.float64)
v = v[np.isfinite(v)]
add("D random background pairs: |mean| < 0.1", abs(v.mean()) < 0.1,
    f"n = {len(v)}, mean = {v.mean():.4f}, SD = {v.std():.3f}, median = {np.median(v):.4f}, "
    f"fraction > 3 = {(v > 3).mean():.5f}, 99.9th pct = {np.quantile(v, 0.999):.2f}")

run = C.write_manifest(C.DERIVED / "sanity" / "run_manifest.json", "scripts/12_sanity_checks.py", g,
                       [C.EFFECT_CSV, EXPR, CPX, C.HUB_TSV, "data/derived/matrices/zavg_full/genes.tsv"], seed=0,
                       t0=t0, extra=dict(results=results))
npass = sum(r[1] == "PASS" for r in results)
L = ["# Sanity checks: Chronos sign, matrix structure, known complexes, random pairs (DESIGN §2.4)", "",
     f"Generated by `scripts/12_sanity_checks.py` ({run['created']}; runtime {run['runtime_s']} s, peak RSS "
     f"{run['peak_rss_gb']} GB). Matrix: `data/derived/matrices/zavg_full/zavg_BEF.npy` ({n} genes, "
     f"{int(bg.sum())} background). Gate: tag `{g['tag']}` @ {g['tag_commit'][:10]}.", "",
     f"**{npass}/{len(results)} checks pass.**", "",
     "| check | result | detail |", "|---|---|---|", *[f"| {a} | {b} | {c} |" for a, b, c in results], "",
     "## Known complexes (Complex Portal; within-complex pairs of background genes)", "",
     "| complex | accession | Complex Portal name | members mapped (BG) | unmapped / ambiguous ids | pairs | median "
     "zavg_BEF | mean | fraction > 3 | median > 3 |", "|---|---|---|---|---|---|---|---|---|---|", *crow, "",
     "Notes: UniProt accessions (isoform suffix stripped) map to genes through `results/ids/hgnc_hub.tsv`; an "
     "accession listed by several HGNC genes is not used. The label-shuffle control of §2.4 needs the predictor "
     "and annotation matrices (M5) and is not part of this script.", ""]
dst = C.ROOT / "results" / "verification" / "sanity_checks.md"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text("\n".join(L))
C.log(f"wrote {dst}")
