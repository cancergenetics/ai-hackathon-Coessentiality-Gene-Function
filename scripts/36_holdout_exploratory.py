#!/usr/bin/env python
"""36_holdout_exploratory.py -- EXPLORATORY (post hoc; not pre-specified) look at the temporal hold-out H.

Logged in LOOKS.md ("EXPLORATORY post hoc look at H: complementarity of zavg_BEF with homology and PPI baselines;
hit@k"). No specification change; the primary analysis (scripts/32) is already reported (aa381fc).
Re-runs the scripts/32-33 code path (same primary H set, targets, circularity exclusion, R1, hu.MAP network and
homology list as scripts/33; imports m5b_common and src; nothing modified) because the homology / PPI per-gene
outputs were not saved, and asserts agreement with per_gene_core.tsv / secondary.tsv before using them.
  1. 2x2 tables of per-gene hit@1: zavg_BEF vs homology, zavg_BEF vs hu.MAP PPI transfer; McNemar exact p; union.
  2. zavg_BEF precision@1 where homology makes no prediction (no t0 IEA/ISS/IBA candidate term) and where there is
     no hu.MAP coverage; gene-bootstrap 95% CIs (10,000 replicates, seed 0); cluster (PMID-only) CIs alongside.
  3. hit@3 / hit@5 for zavg_BEF, GLS, homology, PPI, prior-only.
  4. precision@1 by out-of-fold p_cal bin and by top-K mean zavg quintile: read from the saved M5b outputs.
Outputs: results/holdout_eval/exploratory_complementarity.md, .tsv.
Run: .env/bin/python -I scripts/36_holdout_exploratory.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

gate = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import binomtest  # noqa: E402

import m5b_common as B  # noqa: E402
from src import knownness as kn  # noqa: E402

OUT, DER = B.OUT, B.DER
CORE = pd.read_pickle(DER / "core.pkl")
P, Tp, Dp, nulls = (CORE[k] for k in ("P", "Tp", "Dp", "nulls"))
clP = np.array([CORE["cl_primary"][g] for g in P])
PG = pd.read_csv(OUT / "per_gene_core.tsv", sep="\t", index_col="pos")
assert list(PG.index) == list(P)
SEC = pd.read_csv(OUT / "secondary.tsv", sep="\t")

base = B.Base()
v2t0 = B.build_v2(base, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
S = B.Scored(v2t0, base.nb, base.matches, P, "zavg t0")
sizes = S.sizes
lists = {"zavg_BEF": S.r1, "prior-only": {g: S.prior(g) for g in P}}
nb_gls = B.baseline_network(base, "gls", P)
lists["GLS"] = B.Scored(v2t0, nb_gls, base.matches, P, "GLS t0").r1

# ---- homology list (verbatim from scripts/33 section 2)
g0 = kn.read_gaf(str(C.ROOT / B.T0_DIR / "goa_human.gaf.gz"))
g0 = g0[~kn.is_not_qualified(g0.qualifier)]
g0 = g0[~g0.qualifier.fillna("").str.split("|").apply(lambda x: "colocalizes_with" in x)]
g0 = g0[g0.aspect.isin(["P", "F"]) & g0.evidence.isin(["IEA", "ISS", "IBA"])]
res = {t: base.onto.resolve(t)[0] for t in g0.go_id.unique()}
g0 = g0.assign(go_id=g0.go_id.map(res)).dropna(subset=["go_id"])
Pset = set(P)
hom = {}
for a, t in zip(g0.acc.values, g0.go_id.values):
    for h in base.acc_map.get(kn.strip_isoform(a), ()):
        p = base.pos.get(h)
        if p in Pset:
            hom.setdefault(p, set()).add(t)
hom_cols = {}
for p, ts in hom.items():
    s = set()
    for t in ts:
        s |= base.onto.ancestors(t)
    hom_cols[p] = {v2t0.col[t] for t in s if t in v2t0.col}
hl, hcov = {}, {}
for g in P:
    pl = S.prior(g)
    hc = [c for c in pl if c in hom_cols.get(g, set())]
    hcov[g] = bool(hc)
    hl[g] = hc + [c for c in pl if c not in set(hc)]
lists["homology"] = hl

# ---- hu.MAP PPI (scripts/33 section 3)
nb_h, hst = B.humap_network(base, P)
lists["PPI (hu.MAP)"] = B.Scored(v2t0, nb_h, base.matches, P, "hu.MAP t0").r1
row_of = {int(r): i for i, r in enumerate(nb_h.rows)}
n_partner = {g: int((nb_h.ids[g] >= 0).sum()) for g in P}     # nb_h.rows = arange(G) (padded)


def hits_at(lst_by_gene, ks=(1, 3, 5)):
    out = {k: [] for k in ks}
    pred = []
    for g in P:
        lst = [c for c in lst_by_gene.get(int(g), []) if c not in Dp.get(int(g), set())]
        T = Tp[int(g)]
        pred.append(bool(lst))
        for k in ks:
            out[k].append(float(any(c in T for c in lst[:k])))
    return {k: np.array(v) for k, v in out.items()}, np.array(pred)


H, PRED = {}, {}
for m, l in lists.items():
    H[m], PRED[m] = hits_at(l)

# ---- consistency with the saved primary / secondary outputs
assert np.allclose(H["zavg_BEF"][1], PG.hit1_zavg.values), "zavg differs"
assert np.allclose(H["GLS"][1], PG.hit1_gls.values), "GLS differs"
assert np.allclose(H["prior-only"][1], PG.hit1_prior.values), "prior differs"
for m, nm in (("homology", "Homology"), ("PPI (hu.MAP)", "PPI module")):
    ref = SEC[SEC.analysis.str.startswith(nm)].p1_method.iloc[0]
    assert abs(H[m][1].mean() - ref) < 1e-6, f"{m}: {H[m][1].mean()} vs {ref}"
C.log("consistency with scripts/32-33 outputs OK")

N = len(P)
rng = np.random.default_rng(B.SEED)
NB = B.NBOOT
BOOT_IDX = rng.integers(0, N, size=(NB, N))          # shared gene-level bootstrap indices (seed 0)


def gene_ci(x, mask=None):
    """Gene-level bootstrap percentile 95% CI of mean(x[mask]); resampling within the subset (seed 0)."""
    x = np.asarray(x, float)
    idx = np.arange(N) if mask is None else np.flatnonzero(mask)
    r = np.random.default_rng(B.SEED)
    bs = r.integers(0, len(idx), size=(NB, len(idx)))
    m = x[idx][bs].mean(1)
    return float(x[idx].mean()), float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975)), len(idx)


def clus_ci(x, mask):
    idx = np.flatnonzero(mask)
    b = B.mci(np.asarray(x, float)[idx], clP[idx])
    return b["ci_percentile"]


def mcnemar(a, b):
    a, b = a.astype(bool), b.astype(bool)
    n11, n10, n01, n00 = int((a & b).sum()), int((a & ~b).sum()), int((~a & b).sum()), int((~a & ~b).sum())
    d = n10 + n01
    p = binomtest(n10, d, 0.5).pvalue if d else 1.0
    return n11, n10, n01, n00, p


z1 = H["zavg_BEF"][1]
tsv = []
L = ["# EXPLORATORY (post hoc; not pre-specified)", "",
     "Exploratory complementarity analysis on the temporal hold-out H (scripts/36; LOOKS.md row dated 2026-10-29). "
     "The primary analysis (M5b, aa381fc) is unchanged. Nothing here is a confirmatory test; p-values and CIs are "
     "descriptive, uncorrected, and chosen after seeing the primary results (homology 0.218 and PPI 0.049 hit@1 vs "
     f"zavg_BEF {z1.mean():.3f}). Primary H n = {N}; same genes, targets, circularity exclusion, R1 and >= 2-partner "
     "reportability as scripts/32-33 (per-gene hit@1 of zavg_BEF, GLS, prior-only, homology and PPI reproduce the "
     "saved outputs exactly). Gene-level bootstrap CIs: 10,000 replicates, seed 0; PMID-only cluster CIs (the primary "
     "cluster rule) given alongside where noted.", "",
     "## 1. Per-gene hit@1 agreement (2x2) and union", ""]
for m, lab in (("homology", "homology baseline"), ("PPI (hu.MAP)", "hu.MAP PPI transfer")):
    o = H[m][1]
    n11, n10, n01, n00, p = mcnemar(z1, o)
    un = np.maximum(z1, o)
    u, ulo, uhi, _ = gene_ci(un)
    ucl = clus_ci(un, np.ones(N, bool))
    L += [f"### zavg_BEF vs {lab}", "",
          f"| | {lab} hit | {lab} miss | total |", "|---|---|---|---|",
          f"| zavg_BEF hit | {n11} | {n10} | {n11 + n10} |", f"| zavg_BEF miss | {n01} | {n00} | {n01 + n00} |",
          f"| total | {n11 + n01} | {n10 + n00} | {N} |", "",
          f"Discordant: zavg-only {n10}, {lab}-only {n01}; McNemar exact p = {p:.3g}. "
          f"Union hit rate (zavg_BEF OR {lab}) = {u:.3f} (gene-bootstrap {ulo:.3f}-{uhi:.3f}; cluster "
          f"{ucl[0]:.3f}-{ucl[1]:.3f}) vs zavg_BEF {z1.mean():.3f} and {lab} {o.mean():.3f}; "
          f"gain of the union over the better single method = {u - max(z1.mean(), o.mean()):+.3f} "
          f"({int(un.sum()) - int(max(z1.sum(), o.sum()))} genes).", ""]
    tsv.append(dict(section="2x2", comparator=m, n=N, n_both=n11, n_zavg_only=n10, n_comp_only=n01, n_neither=n00,
                    mcnemar_exact_p=p, p1_zavg=z1.mean(), p1_comp=o.mean(), union=u, union_lo=ulo, union_hi=uhi))

L += ["## 2. zavg_BEF precision@1 in genes the baselines cannot cover", ""]
hom_none = ~np.array([hcov[g] for g in P])
no_partner = np.array([n_partner[g] == 0 for g in P])
no_ppi_pred = ~PRED["PPI (hu.MAP)"]
no_ppi_pred_rel = H["PPI (hu.MAP)"][1] * 0 + (~PRED["PPI (hu.MAP)"])
subs = [("homology makes no prediction (no t0 IEA/ISS/IBA candidate term)", hom_none),
        ("homology makes a prediction", ~hom_none),
        ("no hu.MAP coverage: no scorable hu.MAP partner", no_partner),
        ("no hu.MAP coverage: no reportable PPI prediction (< 2 supporting partners)", no_ppi_pred),
        ("hu.MAP covered (>= 1 partner)", ~no_partner),
        ("neither homology prediction nor hu.MAP partner", hom_none & no_partner),
        ("all primary H", np.ones(N, bool))]
L += ["| subset | n | zavg_BEF p@1 | gene-bootstrap 95% CI | cluster 95% CI | hits | homology p@1 | PPI p@1 |",
      "|---|---|---|---|---|---|---|---|"]
for lab, mk in subs:
    e, lo, hi, n = gene_ci(z1, mk)
    clo, chi = clus_ci(z1, mk)
    L.append(f"| {lab} | {n} | {e:.3f} | {lo:.3f}-{hi:.3f} | {clo:.3f}-{chi:.3f} | {int(z1[mk].sum())} | "
             f"{H['homology'][1][mk].mean():.3f} | {H['PPI (hu.MAP)'][1][mk].mean():.3f} |")
    tsv.append(dict(section="subset", subset=lab, n=n, p1_zavg=e, lo=lo, hi=hi, cl_lo=clo, cl_hi=chi,
                    hits=int(z1[mk].sum()), p1_homology=H["homology"][1][mk].mean(),
                    p1_ppi=H["PPI (hu.MAP)"][1][mk].mean()))
L += ["", "Note: genes with no hu.MAP coverage or no homology prediction are a selected subset (e.g. poorly studied "
      "genes), so these rates are not comparable to the full-H rate without that caveat.", ""]

L += ["## 3. hit@k (any target term among the top k reportable terms)", "",
      "Denominator = all primary H genes (a gene with no reportable list scores 0); homology and prior-only lists are "
      "complete rankings of candidate terms, the others are limited to reportable terms (>= 2 supporting partners). "
      "Gene-bootstrap 95% CIs.", "",
      "| method | hit@1 | hit@3 | hit@5 | coverage (>= 1 term) |", "|---|---|---|---|---|"]
for m in ("zavg_BEF", "GLS", "homology", "PPI (hu.MAP)", "prior-only"):
    cells, d = [], dict(section="hit_at_k", method=m, coverage=PRED[m].mean())
    for k in (1, 3, 5):
        e, lo, hi, _ = gene_ci(H[m][k])
        cells.append(f"{e:.3f} ({lo:.3f}-{hi:.3f})")
        d.update({f"hit{k}": e, f"hit{k}_lo": lo, f"hit{k}_hi": hi})
    L.append(f"| {m} | " + " | ".join(cells) + f" | {PRED[m].mean():.3f} |")
    tsv.append(d)
L.append("")

# ---- 4. cite saved outputs
L += ["## 4. precision@1 by out-of-fold p_cal bin and by signal quintile (already reported in M5b; cited, not recomputed)",
      "", "Source: results/holdout_eval/reliability_oof.tsv (decile bins of p_cal_oof) and signal_quintiles.tsv "
      "(quintiles of top-K mean zavg).", "",
      "| p_cal_oof bin | n | p range | mean predicted | observed p@1 | Wilson 95% CI |", "|---|---|---|---|---|---|"]
R = pd.read_csv(OUT / "reliability_oof.tsv", sep="\t")
for x in R.itertuples():
    L.append(f"| {x.bin} | {x.n} | {x.p_min:.3f}-{x.p_max:.3f} | {x.mean_pred:.3f} | {x.obs_rate:.3f} | "
             f"{x.ci_lo:.3f}-{x.ci_hi:.3f} |")
    tsv.append(dict(section="p_cal_bin", bin=x.bin, n=x.n, p_min=x.p_min, p_max=x.p_max, mean_pred=x.mean_pred,
                    obs_rate=x.obs_rate, lo=x.ci_lo, hi=x.ci_hi))
Q = pd.read_csv(OUT / "signal_quintiles.tsv", sep="\t")
L += ["", "Quintiles of top-K mean zavg (all columns as saved):", "", "\n".join(
    ["| " + " | ".join(Q.columns) + " |", "|" + "---|" * len(Q.columns)] +
    ["| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r) + " |" for r in Q.itertuples(index=False)]), ""]
for r in Q.to_dict("records"):
    tsv.append(dict(section="signal_quintile", **{k: v for k, v in r.items()}))

(OUT / "exploratory_complementarity.md").write_text("\n".join(L))
pd.DataFrame(tsv).to_csv(OUT / "exploratory_complementarity.tsv", sep="\t", index=False, float_format="%.6f")
C.log("done")
