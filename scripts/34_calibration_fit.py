#!/usr/bin/env python
"""34_calibration_fit.py -- M5b: the DESIGN.md v2.3 §3.7 calibration model on H, exactly as logged in LOOKS.md
(specification row f0922e1), and the §0 decision branches.

Model: logistic regression of hit@1 (zavg_BEF, R1, primary targets; scripts/32) on top-K mean zavg_BEF (>= 0, raw),
R(g) (>= 0, raw), neighbourhood annotation coverage (fraction of N(g) in the t0 annotated background; >= 0; within-
release percentile rank among all scorable genes at t0), log top-term size (per-query t0 size of the R1 top term;
<= 0; percentile rank against the base top-term sizes of all scorable genes at t0), module family of the top term
(config/term_families.tsv, first match wins, else 'other'; unconstrained dummies, reference 'other'; families with
< 30 H genes pooled as 'rare' -- such families get no p_cal for U). Sign constraints by src/calibration.MonotoneLogistic.
Fit set = primary H genes with a top reportable term (genes without one have no p_cal; counted).
H metrics from out-of-fold predictions: 10-fold cluster cross-fitting (clusters = the primary clusters of scripts/32),
fold seeds 0-4, averaged (src/calibration.cross_fit). Reliability = deciles of out-of-fold p merged to >= 30 genes;
Brier; calibration intercept (calibration-in-the-large) and slope with Wald 95% CIs (src/metrics; used for the §0
branch) and cluster-bootstrap percentile CIs (2,000 replicates, seed 0; sensitivity).
Model for U = one fit on all H; saved to results/calibration/model_H.json with coefficients, standardisation,
covariate percentile references (t0 and current release), support bounds (H 5th-95th percentiles) and the families
with >= 30 H genes. Decision branches of DESIGN §0 evaluated.
Outputs: results/calibration/model_H.json, model_H_percentile_reference.tsv.gz; results/holdout_eval/calibration.md,
calibration_results.json, calibration_oof.tsv, reliability_oof.tsv, calibration_manifest.json.
Run: .env/bin/python -I scripts/34_calibration_fit.py   (after scripts/32, 33)
"""
import json
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
from src import calibration as cal  # noqa: E402
from src import metrics as mt  # noqa: E402

log = C.log
OUT, DER = B.OUT, B.DER
CALDIR = (B.OUT / "calibration") if B.DRY else C.ROOT / "results" / "calibration"
CALDIR.mkdir(parents=True, exist_ok=True)
CORE = pd.read_pickle(DER / "core.pkl")
PG = pd.read_csv(OUT / "per_gene_core.tsv", sep="\t", index_col="pos")
core = json.loads((OUT / "core_results.json").read_text())
sec = json.loads((OUT / "secondary_results.json").read_text())
FOLDS = C.fz("calibration", "cv_folds")
FSEEDS = tuple(C.fz("seeds", "calibration_fold_seeds"))
LOP, HIP = C.fz("calibration", "support_percentile_range")
NB_CAL = C.fz("bootstrap", "sigma_pcal_replicates") if not B.DRY else 200

Hc = PG[PG.has_pred_zavg.astype(bool)].copy()
kept, ref, fcnt = B.fams_kept(Hc)
X, names, signs = B.design(Hc, kept, ref)
y = Hc.hit1_zavg.values.astype(float)
clu = Hc.cluster_primary.values
log(f"fit set {len(Hc)} of {len(PG)}; families kept {kept} (ref {ref}); hit rate {y.mean():.4f}")

# ------------------------------------------------------------------------------------------ out-of-fold
cf = cal.cross_fit(X, y, clu, signs, k=FOLDS, seeds=FSEEDS)
oof = cf.oof
M = B.calib_metrics(oof, y)
REL = B.reliability(oof, y, C.fz("calibration", "reliability_bins"), C.fz("calibration", "reliability_min_genes_per_bin"))
REL.to_csv(OUT / "reliability_oof.tsv", sep="\t", index=False, float_format="%.5f")
# c-statistic (descriptive)
order = np.argsort(oof)
ranks = np.empty(len(oof))
ranks[order] = np.arange(1, len(oof) + 1)
n1 = y.sum()
auc = float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(y) - n1))) if 0 < n1 < len(y) else np.nan
# cluster bootstrap of intercept / slope / Brier (sensitivity CIs)
labs, inv = np.unique(clu, return_inverse=True)
members = [np.flatnonzero(inv == c) for c in range(len(labs))]
rng = np.random.default_rng(B.SEED)
bi, bs, bb = [], [], []
for _ in range(NB_CAL):
    idx = np.concatenate([members[c] for c in rng.integers(0, len(labs), len(labs))])
    if y[idx].min() == y[idx].max():
        continue
    r = mt.calibration_intercept_slope(oof[idx], y[idx])
    bi.append(r["intercept"])
    bs.append(r["slope"])
    bb.append(mt.brier(oof[idx], y[idx]))
M.update(c_statistic=auc, intercept_ci_boot=tuple(np.quantile(bi, [0.025, 0.975])),
         slope_ci_boot=tuple(np.quantile(bs, [0.025, 0.975])), brier_ci_boot=tuple(np.quantile(bb, [0.025, 0.975])),
         n_boot=len(bi), oof_by_seed_sd=float(np.nanmean(cf.oof_by_seed.std(0))))
poor_wald = bool(M["slope_ci"][0] > 1 or M["slope_ci"][1] < 1 or M["intercept_ci"][0] > 0 or M["intercept_ci"][1] < 0)
poor_boot = bool(M["slope_ci_boot"][0] > 1 or M["slope_ci_boot"][1] < 1 or M["intercept_ci_boot"][0] > 0
                 or M["intercept_ci_boot"][1] < 0)
OOF = Hc[["hgnc_id", "symbol", "hit1_zavg", "zmean", "R", "cov_pct", "size_pct", "family", "cluster_primary"]].copy()
OOF["p_oof"] = oof
OOF.to_csv(OUT / "calibration_oof.tsv", sep="\t", float_format="%.6g")

# ------------------------------------------------------------------------------------------ fit on all H
m = cal.MonotoneLogistic(signs).fit(X, y)
p_in = m.predict_proba(X)
sup = {c: [float(np.percentile(Hc[c], LOP)), float(np.percentile(Hc[c], HIP))] for c in B.CAL_COVS}
scor = None
ref_t0_cov = CORE["cov_t0"][~np.isnan(CORE["cov_t0"])]
qgrid = np.linspace(0, 1, 1001)


def grid(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    return np.quantile(a, qgrid).tolist()


sc_mask = np.zeros(len(CORE["cov_t0"]), bool)
cov_ref = pd.read_csv(DER / "coverage_reference.tsv.gz", sep="\t")
sc_mask[cov_ref.matrix_index.values] = True
refs = dict(coverage_t0=np.sort(CORE["cov_t0"][sc_mask]), coverage_current=np.sort(CORE["cov_cur"][sc_mask]),
            log_top_term_size_t0=np.sort(np.log(CORE["ref_size_t0"][sc_mask][np.isfinite(CORE["ref_size_t0"][sc_mask])])),
            log_top_term_size_current=np.sort(np.log(CORE["ref_size_cur"][sc_mask][np.isfinite(
                CORE["ref_size_cur"][sc_mask])])))
RT = pd.concat([pd.DataFrame(dict(reference=k, value=v)) for k, v in refs.items()])
RT.to_csv(CALDIR / "model_H_percentile_reference.tsv.gz", sep="\t", index=False, float_format="%.8g")
model = dict(
    spec="DESIGN v2.3 §3.7; LOOKS.md specification row (f0922e1); scripts/34_calibration_fit.py",
    outcome="hit@1 of the V2 top reportable R1 term (zavg_BEF, K=25) against T(g), primary circularity rule",
    covariates=names, signs=signs, intercept=float(m.intercept_), coef=dict(zip(names, m.coef_.tolist())),
    standardised=dict(w=m.w_.tolist(), mu=m.mu_.tolist(), sd=m.sd_.tolist(),
                      formula="p = expit(w[0] + sum_j w[j+1] * (x_j - mu_j) / sd_j)"),
    converged=m.converged_, n_fit=int(len(y)), n_hits=int(y.sum()),
    covariate_definitions=dict(
        zmean="mean zavg_BEF over the K=25 full-data neighbours N(g) (raw)",
        R="split-half reproducibility R(g) (results/assessability/R_all.tsv; raw)",
        cov_pct="fraction of N(g) in the release's annotated background (>=1 non-generic V2 BP/MF term), as a "
                "mid-rank percentile (0-1) among all scorable genes in that release",
        size_pct="log size of the V2 top reportable term (annotated scorable genes, release in use), as a mid-rank "
                 "percentile (0-1) against the base top-term log sizes of all scorable genes in that release",
        family="module family of the top term (config/term_families.tsv; first match wins; else other)"),
    families_kept=kept, reference_family=ref, family_counts_H=fcnt,
    family_rule=f"families with >= {C.fz('calibration', 'min_h_genes_per_family')} H genes get p_cal; others "
                "('rare' dummy in the fit) get no p_cal",
    support=dict(bounds_5_95=sup, rule="all four continuous covariates within H 5th-95th percentiles and family "
                 "kept -> p_cal; below the 5th percentile only on zmean and/or R (others in support) -> boundary "
                 "p_cal as an upper bound (not tiered; summed separately); anything else -> no p_cal"),
    percentile_references=dict(file="results/calibration/model_H_percentile_reference.tsv.gz",
                               method="mid-rank: (#ref < x + #ref <= x) / (2 n)",
                               quantile_grid_step_0p001={k: grid(v) for k, v in refs.items()},
                               n={k: int(len(v)) for k, v in refs.items()}),
    oof_metrics=dict(brier=M["brier"], intercept=M["intercept"], intercept_ci=M["intercept_ci"], slope=M["slope"],
                     slope_ci=M["slope_ci"], c_statistic=auc),
    sigma_pcal_ci="2,000 cluster-bootstrap refits of this model on H (seed 0), percentile CI -- computed at M6")
B.jdump(model, CALDIR / "model_H.json")

# ------------------------------------------------------------------------------------------ decision branches
c2_pass = bool(core["primary"]["pass_"])
branches = []
if c2_pass:
    branches.append("C2 primary PASSES -> calibrated claims for U are permitted (p_cal from the pre-specified model).")
else:
    branches.append("C2 primary FAILS -> no calibrated claims for U; top 40 = assessable, expressed U genes ranked by "
                    "the frozen ranker's (R1) top-term score, labelled 'uncalibrated'.")
if poor_wald:
    branches.append("Calibration POOR on H (Wald: slope CI excludes 1 or intercept CI excludes 0) -> p_cal still "
                    "reported from the pre-specified model with that caveat; no other recalibration.")
else:
    branches.append("Calibration branch: slope 95% CI includes 1 and intercept 95% CI includes 0 (Wald) -> "
                    "calibration not poor; p_cal reported without the poor-calibration caveat.")
gls_ge = bool(core["gls"]["gls_ge_zavg"])
branches.append(("GLS ≥ zavg_BEF on H (point estimate) -> stated plainly; zavg_BEF remains the pre-specified "
                 "generator.") if gls_ge else "GLS < zavg_BEF on H (point estimate): the 'GLS ≥ zavg' branch does "
                "not apply.")
branches.append("Tier-A (< 10) and assessable-count (< 100) branches are decided at M6/M7 (C1: 646 assessable, so "
                "the < 100 branch does not hold).")
RES = dict(dry_run=B.DRY, n_H_primary=len(PG), n_fit=len(Hc), n_without_prediction=int(len(PG) - len(Hc)),
           families_kept=kept, reference_family=ref, family_counts=fcnt, oof=M, poor_calibration_wald=poor_wald,
           poor_calibration_bootstrap=poor_boot, c2_primary_pass=c2_pass, gls_ge_zavg=gls_ge, branches=branches,
           in_sample=dict(mean_pred=float(p_in.mean()), brier=mt.brier(p_in, y)),
           coef=model["coef"], intercept=model["intercept"], support=sup, converged=m.converged_)
man = C.write_manifest(OUT / "calibration_manifest.json", "scripts/34_calibration_fit.py", gate,
                       ["results/holdout_eval/per_gene_core.tsv"] if not B.DRY else [], seed=B.SEED, t0=T_START)
B.jdump(RES, OUT / "calibration_results.json")

L = ["# M5b calibration on H (§3.7; scripts/34)", "",
     f"Generated {man['created']}." + (" **DRY RUN -- not H.**" if B.DRY else ""),
     f"Fit set: {len(Hc)} primary H genes with a top reportable term ({len(PG) - len(Hc)} without; no p_cal). "
     f"Hit rate {y.mean():.3f}. Families with ≥ 30 H genes: {kept} (reference {ref}); counts {fcnt}.", "",
     "## Out-of-fold performance (10-fold cluster cross-fitting, fold seeds 0–4, averaged)", "",
     f"- Mean out-of-fold p {M['mean_pred']:.3f} vs observed {M['obs_rate']:.3f}; Brier {M['brier']:.4f} (95% "
     f"cluster-bootstrap CI {B.fmt_ci(M['brier_ci_boot'], 4)}; constant-rate reference {M['brier_ref_constant']:.4f}); "
     f"c-statistic {auc:.3f}.",
     f"- Calibration intercept {M['intercept']:+.3f} (Wald 95% CI {B.fmt_ci(M['intercept_ci'], 3, True)}; cluster "
     f"bootstrap {B.fmt_ci(M['intercept_ci_boot'], 3, True)}).",
     f"- Calibration slope {M['slope']:.3f} (Wald 95% CI {B.fmt_ci(M['slope_ci'], 3)}; cluster bootstrap "
     f"{B.fmt_ci(M['slope_ci_boot'], 3)}).",
     f"- Poor calibration (§0 rule): Wald {poor_wald}; bootstrap {poor_boot}.", "",
     "| bin | n | p range | mean predicted | observed | Wilson 95% CI |", "|---|---|---|---|---|---|"]
for x in REL.itertuples():
    L.append(f"| {x.bin} | {x.n} | {x.p_min:.3f}–{x.p_max:.3f} | {x.mean_pred:.3f} | {x.obs_rate:.3f} | "
             f"{x.ci_lo:.3f}–{x.ci_hi:.3f} |")
L += ["", "## Model fitted on all H (for U; results/calibration/model_H.json)", "",
      "| term | coefficient (original scale) | sign constraint |", "|---|---|---|",
      f"| intercept | {m.intercept_:+.4f} | free |"]
for n_, c_, s_ in zip(names, m.coef_, signs):
    L.append(f"| {n_} | {c_:+.4f} | {'≥ 0' if s_ > 0 else '≤ 0' if s_ < 0 else 'free'} |")
L += ["", "Support bounds (H 5th–95th percentiles): " + "; ".join(f"{k} {v[0]:.4g}–{v[1]:.4g}" for k, v in sup.items()),
      "", "## Decision branches (DESIGN §0)", ""] + [f"- {b}" for b in branches] + [""]
(OUT / "calibration.md").write_text("\n".join(L))
log("done: " + " | ".join(branches))
