#!/usr/bin/env python
"""41_pcal.py -- M6 step 2: calibrated probabilities for U predictions (DESIGN.md v2.3 §3.7, §4.2; DEVIATIONS.md
2026-10-29 M6 rows).

p_cal = the all-H fit of results/calibration/model_H.json (scripts/34; LOOKS spec row f0922e1) applied to the U
covariates of results/ledger/u_predictions.tsv (current release). Support (frozen rule, model_H.json): all four
continuous covariates within the H 5th-95th percentiles and family with >= 30 H genes -> p_cal; below the 5th percentile
only on top-K mean zavg and/or R(g) -> boundary p_cal reported as an UPPER BOUND (not tiered; summed separately); any
other out-of-support (or no top term) -> no p_cal.
Sigma p_cal CI: 2,000 cluster-bootstrap refits of the same sign-constrained model on the H fit set (PMID-only primary
clusters, DEVIATIONS 2026-10-30 fallback; seed 0), percentile 95% CI; per-replicate U predictions saved so the Tier A
sum (script 44/45) uses the same replicates.
Negative control (§4.2): scorable clean-negative U genes (non-expressed by construction) scored the same way; p_cal
distribution and the rate of Tier-A-like calls by informativeness (SD) tertile -- the §4.3 exclusion part of the
Tier-A-like definition is joined in script 45 (after script 42).
Outputs: results/ledger/u_pcal.tsv, pcal_summary.json, negative_control_pcal.tsv, 41_manifest.json;
data/derived/ledger/pcal_boot.npz.
Run: .env/bin/python -I scripts/41_pcal.py   (after scripts/40)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
gate = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import calibration as cal  # noqa: E402
from src import ledger as LG  # noqa: E402

log = C.log
NB = C.fz("bootstrap", "sigma_pcal_replicates")
SEED = C.fz("seeds", "bootstraps")
PA, PB = C.fz("tiers", "tier_a_pcal_min"), C.fz("tiers", "tier_b_pcal_min")

MOD = M6.model()
P = M6.read_tsv("u_predictions.tsv")
P["family"] = P.family.fillna("")
bounds = MOD["support"]["bounds_5_95"]
kept = MOD["families_kept"]

# ------------------------------------------------------------------------------------------ point estimates
P["p_model"] = LG.pcal_from_model(P, MOD)
P["support_category"] = [LG.support_category(r, bounds, kept) if r.has_prediction else "no_prediction"
                         for _, r in P.iterrows()]


def reasons(r):
    if not r.has_prediction:
        return "no top reportable term"
    out = []
    if r.family not in kept:
        out.append(f"family {r.family} (< 30 H genes)")
    for c in LG.CONT:
        lo, hi = bounds[c]
        if r[c] < lo:
            out.append(f"{c} < P5")
        elif r[c] > hi:
            out.append(f"{c} > P95")
    return "; ".join(out)


P["support_reason"] = [reasons(r) for _, r in P.iterrows()]
P["p_cal"] = np.where(P.support_category == "in_support", P.p_model, np.nan)
P["p_cal_upper"] = np.where(P.support_category == "upper_bound", P.p_model, np.nan)

# refit check: MonotoneLogistic on the H fit set reproduces model_H.json
PG = pd.read_csv(C.ROOT / "results/holdout_eval/per_gene_core.tsv", sep="\t", index_col="pos")
Hc = PG[PG.has_pred_zavg.astype(bool)].copy()
XH, names, signs = B.design(Hc, kept, MOD["reference_family"])
assert names == MOD["covariates"] and signs == MOD["signs"], (names, MOD["covariates"])
yH = Hc.hit1_zavg.values.astype(float)
clu = Hc.cluster_primary.values
m_full = cal.MonotoneLogistic(signs).fit(XH, yH)
assert np.allclose(m_full.coef_, [MOD["coef"][n] for n in names], atol=1e-6), "refit differs from model_H.json"
ins = P.support_category == "in_support"
ub = P.support_category == "upper_bound"
XU = np.vstack([LG.design_row(r, MOD) for _, r in P[ins | ub].iterrows()]) if (ins | ub).any() else np.zeros((0, len(names)))
pchk = m_full.predict_proba(XU)
assert np.allclose(pchk, P.loc[ins | ub, "p_model"].values, atol=1e-9)

# ------------------------------------------------------------------------------------------ bootstrap
t = time.perf_counter()
lab, inv = np.unique(clu, return_inverse=True)
members = [np.flatnonzero(inv == c) for c in range(len(lab))]
rng = np.random.default_rng(SEED)
boot = np.full((NB, len(XU)), np.nan, np.float32)
skipped = 0
for b in range(NB):
    idx = np.concatenate([members[c] for c in rng.integers(0, len(lab), len(lab))])
    if yH[idx].min() == yH[idx].max():
        skipped += 1
        continue
    boot[b] = cal.MonotoneLogistic(signs).fit(XH[idx], yH[idx]).predict_proba(XU)
ok = np.isfinite(boot[:, 0]) if len(XU) else np.zeros(NB, bool)
log(f"bootstrap {NB} refits in {time.perf_counter() - t:.0f} s ({skipped} skipped)")
sub_ins = ins[ins | ub].values
sub_ub = ub[ins | ub].values


def ci(mask):
    s = boot[ok][:, mask].sum(1)
    return [float(np.quantile(s, 0.025)), float(np.quantile(s, 0.975))] if len(s) else [np.nan, np.nan]


SUM = dict(n_scorable=len(P), n_with_prediction=int(P.has_prediction.sum()),
           category_counts=P.support_category.value_counts().to_dict(),
           sum_pcal_in_support=float(P.p_cal.sum()), ci_in_support=ci(sub_ins),
           sum_pcal_upper_bound=float(P.p_cal_upper.sum()), ci_upper_bound=ci(sub_ub),
           n_boot_used=int(ok.sum()), n_boot_skipped=skipped, seed=SEED,
           max_p_cal=float(np.nanmax(P.p_cal)) if ins.any() else np.nan,
           max_p_cal_upper=float(np.nanmax(P.p_cal_upper)) if ub.any() else np.nan,
           n_pcal_ge_tierB=int((P.p_cal >= PB).sum()), n_pcal_ge_tierA=int((P.p_cal >= PA).sum()),
           reasons_no_pcal=P[P.support_category == "no_pcal"].support_reason.str.split("; ").explode()
           .value_counts().to_dict(),
           family_counts_with_prediction=P[P.has_prediction].family.value_counts().to_dict())
# same sums restricted to expressed & assessable (DESIGN definition)
ea = (P.expressed_design.astype(bool) & P.assessable_design.astype(bool))
SUM["sum_pcal_in_support_expressed_assessable"] = float(P.p_cal[ea].sum())
SUM["n_in_support_expressed_assessable"] = int((ins & ea).sum())
SUM["ci_in_support_expressed_assessable"] = ci((ins & ea)[ins | ub].values)
np.savez_compressed(M6.DER / "pcal_boot.npz", boot=boot, hgnc_id=P.loc[ins | ub, "hgnc_id"].values.astype(str),
                    ok=ok)

# ------------------------------------------------------------------------------------------ negative control
cn = P[P.clean_negative.astype(bool)].copy()
cn["repro_p_lt_0p05"] = cn.assessable_p < C.fz("assessability", "alpha")
cn["tierA_like_pre43"] = (cn.p_cal >= PA) & cn.repro_p_lt_0p05
rows = []
for lev, d in [("all", cn)] + [(k, v) for k, v in cn.groupby("sd_tertile_withinU")]:
    pc = d.p_cal.dropna()
    rows.append(dict(tertile=lev, n=len(d), n_prediction=int(d.has_prediction.sum()),
                     n_in_support=int((d.support_category == "in_support").sum()),
                     n_upper_bound=int((d.support_category == "upper_bound").sum()),
                     p_cal_median=float(pc.median()) if len(pc) else np.nan,
                     p_cal_p90=float(pc.quantile(0.9)) if len(pc) else np.nan,
                     p_cal_max=float(pc.max()) if len(pc) else np.nan, sum_p_cal=float(pc.sum()),
                     n_pcal_ge_0p3=int((d.p_cal >= PB).sum()), n_pcal_ge_0p5=int((d.p_cal >= PA).sum()),
                     n_repro_p_lt_0p05=int(d.repro_p_lt_0p05.sum()),
                     n_tierA_like_pre43=int(d.tierA_like_pre43.sum()),
                     rate_tierA_like_pre43=float(d.tierA_like_pre43.mean()) if len(d) else np.nan))
NC = pd.DataFrame(rows)
NC.to_csv(M6.OUT / "negative_control_pcal.tsv", sep="\t", index=False, float_format="%.6g")
# expressed comparison distribution
SUM["p_cal_quantiles_expressed_assessable"] = P.p_cal[ea].quantile([.1, .25, .5, .75, .9, 1]).to_dict()
SUM["p_cal_quantiles_clean_negative"] = cn.p_cal.quantile([.1, .25, .5, .75, .9, 1]).to_dict()

cols = ["hgnc_id", "symbol", "matrix_index", "has_prediction", "top_term", "top_term_name", "family", "zmean", "R",
        "cov_pct", "size_pct", "support_category", "support_reason", "p_model", "p_cal", "p_cal_upper",
        "expressed_design", "assessable_design", "clean_negative", "low_coverage", "sd_tertile_withinU"]
P[cols].to_csv(M6.OUT / "u_pcal.tsv", sep="\t", index=False, float_format="%.6g")
M6.jdump(SUM, M6.OUT / "pcal_summary.json")
C.write_manifest(M6.OUT / "41_manifest.json", "scripts/41_pcal.py", gate,
                 ["results/ledger/u_predictions.tsv", M6.MODEL_JSON, "results/holdout_eval/per_gene_core.tsv"],
                 seed=SEED, t0=T_START, extra=dict(n_boot=NB))
log(f"Sigma p_cal (in support) {SUM['sum_pcal_in_support']:.2f} {SUM['ci_in_support']}; upper bound "
    f"{SUM['sum_pcal_upper_bound']:.2f}; categories {SUM['category_counts']}; max p_cal {SUM['max_p_cal']:.3f}")
