#!/usr/bin/env python
"""35_holdout_figures.py -- M5b figures and the single summary of the hold-out look (scripts/32-34 outputs only;
no new computation on H).

Figure-ready TSVs (results/holdout_eval/fig_*.tsv) and PNG/SVG panels (manuscript/figures/m5b_*.{png,svg}):
  a. precision@1 by method with 95% cluster-bootstrap CIs (core + secondary comparators);
  b. reliability diagram (out-of-fold §3.7 model; LOO-fitted model for comparison);
  c. named-control case series: rank of the best-ranked true term (window 2-300);
  d. precision@1 by signal quintile (top-K mean zavg) for zavg_BEF, prior-only, matched null, GLS.
Writes results/holdout_eval/SUMMARY.md (every number with its CI; verdicts).
Run: .env/bin/python -I scripts/35_holdout_figures.py   (after scripts/32-34)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
gate = C.gate_check()

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5b_common as B  # noqa: E402

OUT, FIG = B.OUT, B.FIG
core = json.loads((OUT / "core_results.json").read_text())
sec = json.loads((OUT / "secondary_results.json").read_text())
calr = json.loads((OUT / "calibration_results.json").read_text())
MC = pd.read_csv(OUT / "methods_core.tsv", sep="\t")
CMP = pd.read_csv(OUT / "comparisons_core.tsv", sep="\t")
SEC = pd.read_csv(OUT / "secondary.tsv", sep="\t")
SH = pd.read_csv(OUT / "splithalf.tsv", sep="\t")
CS = pd.read_csv(OUT / "circularity_sensitivity.tsv", sep="\t")
V1 = pd.read_csv(OUT / "v1.tsv", sep="\t")
CT = pd.read_csv(OUT / "controls_case_series.tsv", sep="\t")
QT = pd.read_csv(OUT / "signal_quintiles.tsv", sep="\t")
SMD = pd.read_csv(OUT / "covariate_smd.tsv", sep="\t")
SZ = pd.read_csv(OUT / "top1_size.tsv", sep="\t")
REL = pd.read_csv(OUT / "reliability_oof.tsv", sep="\t")
RLO = pd.read_csv(OUT / "loo_fitted_reliability.tsv", sep="\t")

# reference palette (dataviz skill, light mode): slots 1-4; neutral ink for text and comparators
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "svg.fonttype": "none"})
PFX = "m5b_"


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{PFX}{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------------------------------ a. precision by method
rows = [dict(method=x.label, group="core", p1=x.precision_at_1, lo=x.p1_ci_lo, hi=x.p1_ci_hi, coverage=x.coverage)
        for x in MC.itertuples()]
for x in SEC[SEC.kind == "comparator"].itertuples():
    rows.append(dict(method=x.analysis.split(" (")[0], group="secondary", p1=x.p1_method, lo=x.p1_method_lo,
                     hi=x.p1_method_hi, coverage=x.coverage))
FA = pd.DataFrame(rows)
FA.to_csv(OUT / "fig_precision_by_method.tsv", sep="\t", index=False, float_format="%.5f")
fig, ax = plt.subplots(figsize=(5.2, 0.32 * len(FA) + 0.9))
yy = np.arange(len(FA))[::-1]
for y, x in zip(yy, FA.itertuples()):
    c = S1 if x.method.startswith("zavg") else INK2
    ax.plot([x.lo, x.hi], [y, y], color=c, lw=2, solid_capstyle="round")
    ax.plot(x.p1, y, "o", ms=7, color=c, mec=SURF, mew=2)
    ax.text(x.hi + 0.004, y, f"{x.p1:.3f}", va="center", fontsize=8, color=INK2)
ax.set_yticks(yy, [f"{m}{' †' if g == 'secondary' else ''}" for m, g in zip(FA.method, FA.group)])
ax.set_xlabel("precision@1 on H (95% cluster-bootstrap CI)")
ax.set_xlim(0, max(FA.hi.max() * 1.18, 0.05))
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
ax.set_title(f"Temporal hold-out H (n = {core['primary']['n']}); † secondary batch", fontsize=9, loc="left")
save(fig, "precision_by_method")

# ------------------------------------------------------------------------------------------ b. reliability
REL.assign(model="§3.7 out-of-fold").to_csv(OUT / "fig_reliability.tsv", sep="\t", index=False, float_format="%.5f")
pd.concat([REL.assign(model="§3.7 out-of-fold"), RLO.assign(model="LOO-fitted")]).to_csv(
    OUT / "fig_reliability.tsv", sep="\t", index=False, float_format="%.5f")
fig, ax = plt.subplots(figsize=(3.8, 3.8))
mx = max(REL.ci_hi.max(), RLO.ci_hi.max(), REL.mean_pred.max(), RLO.mean_pred.max()) * 1.1
ax.plot([0, mx], [0, mx], color=INK2, lw=1, ls="--", zorder=0)
for d, c, lab, off in ((REL, S1, "H out-of-fold (§3.7)", 0.0), (RLO, S2, "LOO-fitted model", 0.002)):
    ax.errorbar(d.mean_pred + off, d.obs_rate, yerr=[d.obs_rate - d.ci_lo, d.ci_hi - d.obs_rate], fmt="o", ms=6,
                color=c, ecolor=c, elinewidth=1.5, capsize=0, mec=SURF, mew=1.5, label=lab)
ax.set_xlim(0, mx)
ax.set_ylim(0, mx)
ax.set_xlabel("mean predicted p (bin)")
ax.set_ylabel("observed hit@1 rate (Wilson 95% CI)")
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.grid(color=GRID, lw=0.8)
ax.set_axisbelow(True)
o = calr["oof"]
ax.set_title(f"slope {o['slope']:.2f} ({o['slope_ci'][0]:.2f}–{o['slope_ci'][1]:.2f}); "
             f"intercept {o['intercept']:+.2f}", fontsize=8, loc="left")
save(fig, "reliability")

# ------------------------------------------------------------------------------------------ c. controls
FC = CT[["symbol", "weak", "in_H", "n_targets_2_300", "n_targets_flagged", "n_reportable", "rank_best_true_term",
         "best_true_term", "top1_term", "top_v1prime_label"]].copy()
FC.to_csv(OUT / "fig_controls.tsv", sep="\t", index=False)
fig, ax = plt.subplots(figsize=(5.2, 0.3 * len(FC) + 0.9))
yy = np.arange(len(FC))[::-1]
nr = max(FC.n_reportable.max(), 10) * 1.6
for y, x in zip(yy, FC.itertuples()):
    if pd.notna(x.rank_best_true_term):
        ax.plot(x.rank_best_true_term, y, "o", ms=7, color=S1 if not x.weak else S2, mec=SURF, mew=1.5)
        ax.text(x.rank_best_true_term * 1.15, y, f"{int(x.rank_best_true_term)}", va="center", fontsize=8, color=INK2)
    else:
        ax.plot(nr, y, "x", ms=6, color=INK2)
        ax.text(nr * 1.12, y, "no true term ranked" if x.n_targets_2_300 else "no target", va="center",
                fontsize=7, color=INK2)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
ax.set_yticks(yy, [f"{s}{' (weak)' if w else ''}" for s, w in zip(FC.symbol, FC.weak)])
ax.set_xlabel("rank of best true term among reportable R1 terms (t0, window 2–300; log)")
ax.axvline(1, color=GRID, lw=1, zorder=0)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
ax.set_title("Named positive controls (case series; descriptive)", fontsize=9, loc="left")
save(fig, "controls")

# ------------------------------------------------------------------------------------------ d. quintiles
QT.to_csv(OUT / "fig_signal_quintiles.tsv", sep="\t", index=False, float_format="%.5f")
fig, ax = plt.subplots(figsize=(4.6, 3.4))
x0 = np.arange(len(QT))
for k, (m, c, lab) in enumerate((("zavg", S1, "zavg_BEF"), ("gls", S4, "GLS"), ("null", S3, "matched null"),
                                  ("prior", S2, "prior-only"))):
    off = (k - 1.5) * 0.08
    ax.errorbar(x0 + off, QT[f"p1_{m}"], yerr=[QT[f"p1_{m}"] - QT[f"p1_{m}_lo"], QT[f"p1_{m}_hi"] - QT[f"p1_{m}"]],
                fmt="-o", ms=5, lw=2, color=c, elinewidth=1, capsize=0, mec=SURF, mew=1, label=lab)
ax.set_xticks(x0, [f"{q}\n{a:.1f}–{b:.1f}" for q, a, b in zip(QT.quintile, QT.zmean_min, QT.zmean_max)])
ax.set_xlabel("signal quintile (top-K mean zavg_BEF)")
ax.set_ylabel("precision@1 (95% CI)")
ax.set_ylim(bottom=0)
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.grid(axis="y", color=GRID, lw=0.8)
ax.set_axisbelow(True)
save(fig, "signal_quintiles")

# ============================================================================================ SUMMARY.md
pr = core["primary"]


def ci(c, nd=3, sign=False):
    return B.fmt_ci(c, nd, sign)


def crow(name, clusters=None):
    d = CMP[CMP.comparison == name]
    if clusters:
        d = d[d.clusters == clusters]
    return d.iloc[0]


mc = MC.set_index("method")
gls = core["gls"]
o = calr["oof"]
L = ["# M5b — the single pre-registered look at the temporal hold-out H: SUMMARY", "",
     ("**DRY RUN on LOO genes with pseudo-targets — NOT H.**" if B.DRY else
      "Scripts 32–35 (one execution each unless noted in LOOKS.md); specification: LOOKS.md row f0922e1 (ranker R1, "
      "§3.7 calibration spec, cluster fallback), DEVIATIONS.md. All CIs are 95% paired cluster-bootstrap percentile "
      f"intervals ({core['n_boot']:,} replicates, seed 0) unless stated; BCa intervals are in comparisons_core.tsv."), "",
     "## Verdicts", "",
     f"1. **Primary IUT (C2): {'PASS' if pr['pass_'] else 'FAIL'}.** precision@1 zavg_BEF {pr['p1']['zavg']:.3f} vs "
     f"prior-only {pr['p1']['prior']:.3f} (Δ {pr['diff']['prior']['est']:+.3f}, {ci(pr['diff']['prior']['ci'], 3, True)})"
     f" and vs matched-gene null {pr['p1']['null']:.3f} (Δ {pr['diff']['null']['est']:+.3f}, "
     f"{ci(pr['diff']['null']['ci'], 3, True)}); clusters: {pr['clusters']}; BCa verdict "
     f"{'PASS' if pr['pass_bca'] else 'FAIL'}. Effective n {pr['diff']['prior']['effective_n']:.0f} / "
     f"{pr['diff']['null']['effective_n']:.0f} ({'underpowered' if pr['underpowered'] else 'not underpowered'}; "
     "rule < 300).",
     f"2. **GLS (key secondary, two-sided):** GLS precision@1 {gls['p1_gls']:.3f}; zavg − GLS {gls['est']:+.3f} "
     f"({ci(gls['ci'], 3, True)}) — {'CI excludes 0' if gls['significant'] else 'CI includes 0 (no detectable difference)'}"
     f"; GLS ≥ zavg_BEF (point estimate): {gls['gls_ge_zavg']}.",
     f"3. **Calibration (§3.7, out-of-fold):** slope {o['slope']:.3f} (Wald {ci(o['slope_ci'])}; bootstrap "
     f"{ci(o['slope_ci_boot'])}), intercept {o['intercept']:+.3f} (Wald {ci(o['intercept_ci'], 3, True)}; bootstrap "
     f"{ci(o['intercept_ci_boot'], 3, True)}), Brier {o['brier']:.4f} ({ci(o['brier_ci_boot'], 4)}), c-statistic "
     f"{o['c_statistic']:.3f}. Poor-calibration rule met: {calr['poor_calibration_wald']} (Wald; bootstrap "
     f"{calr['poor_calibration_bootstrap']}).", "", "**Decision branches (DESIGN §0):**", ""]
L += [f"- {b}" for b in calr["branches"]]
h = core["H"]
L += ["", "## H", "",
      f"|H| = {h['n_H']} genes, {h['n_pairs']} (gene, target) pairs; circularity-flagged pairs {h['n_flagged_pairs']} "
      f"(fully circular {h['n_fully_circular_pairs']}), unscannable {h['n_unscannable_pairs']}; primary H = "
      f"**{h['n_primary']}** genes ({h['n_genes_losing_all']} lose every target). Clusters: PMID-only "
      f"{core['clusters']['PMID-only']['n_clusters']} (largest {core['clusters']['PMID-only']['largest']}); PMID+N(g) "
      f"{core['clusters']['PMID+N(g)']['n_clusters']} (largest {core['clusters']['PMID+N(g)']['largest']}, "
      f"{core['clusters']['PMID+N(g)']['largest_frac']:.1%} of H) → primary = **{core['clusters']['primary']}**.", "",
      "## Core metrics", "", "| method | precision@1 (CI) | MRR (CI) | coverage | precision@1, terms ≤ 50 (CI; n) |",
      "|---|---|---|---|---|"]
for x in MC.itertuples():
    L.append(f"| {x.label} | {x.precision_at_1:.3f} ({x.p1_ci_lo:.3f}–{x.p1_ci_hi:.3f}) | {x.MRR:.3f} "
             f"({x.mrr_ci_lo:.3f}–{x.mrr_ci_hi:.3f}) | {x.coverage:.3f} | {x.p1_small:.3f} ({x.p1_small_ci_lo:.3f}–"
             f"{x.p1_small_ci_hi:.3f}; {x.n_small}) |")
L += ["", "| comparison | clusters | Δ | 95% CI | BCa |", "|---|---|---|---|---|"]
for x in CMP.itertuples():
    L.append(f"| {x.comparison} | {x.clusters} | {x.diff:+.3f} | {x.ci_lo:+.3f} to {x.ci_hi:+.3f} | "
             f"{x.bca_lo:+.3f} to {x.bca_hi:+.3f} |")
L += ["", "Top-1 term size (t0 annotated scorable genes): " + "; ".join(
    f"{x.method} median {x.median:.0f} (IQR {x.q1:.0f}–{x.q3:.0f}), ≤ 50: {x.frac_le50:.2f}" for x in SZ.itertuples()) + ".",
    "", "## Split-half networks", "",
    f"precision@1 range {SH.p1_zavg.min():.3f}–{SH.p1_zavg.max():.3f} over 10 half networks; both primary differences "
    f"exclude 0 in {int(((SH.d_prior_lo > 0) & (SH.d_null_lo > 0)).sum())}/10.", "",
    "| seed/half | precision@1 (CI) | − prior (CI) | − null (CI) |", "|---|---|---|---|"]
for x in SH.itertuples():
    L.append(f"| {x.seed}/{x.half} | {x.p1_zavg:.3f} ({x.p1_ci_lo:.3f}–{x.p1_ci_hi:.3f}) | {x.d_prior:+.3f} "
             f"({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | {x.d_null:+.3f} ({x.d_null_lo:+.3f} to {x.d_null_hi:+.3f}) |")
L += ["", "## Circularity sensitivity", "", "| analysis | n | zavg | − prior (CI) | − null (CI) | IUT |",
      "|---|---|---|---|---|---|"]
for x in CS.itertuples():
    L.append(f"| {x.analysis} | {x.n} | {x.p1_zavg:.3f} | {x.d_prior:+.3f} ({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | "
             f"{x.d_null:+.3f} ({x.d_null_lo:+.3f} to {x.d_null_hi:+.3f}) | {'pass' if x.iut_pass else 'fail'} |")
L += ["", "## V1 (GO CC complexes)", "", "| analysis | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) |",
      "|---|---|---|---|---|---|---|"]
for x in V1.itertuples():
    if x.n == 0:
        continue
    L.append(f"| {x.analysis} | {x.n} | {x.p1_zavg:.3f} ({x.p1_ci_lo:.3f}–{x.p1_ci_hi:.3f}) | {x.p1_prior:.3f} | "
             f"{x.p1_null:.3f} | {x.d_prior:+.3f} ({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | {x.d_null:+.3f} "
             f"({x.d_null_lo:+.3f} to {x.d_null_hi:+.3f}) |")
L += ["", "## Named controls (window 2–300; descriptive)", "",
      "| control | in H | targets (flagged) | rank of best true term / reportable | top-1 term | top V1′ label |",
      "|---|---|---|---|---|---|"]
for x in CT.itertuples():
    rk = "—" if pd.isna(x.rank_best_true_term) else f"{int(x.rank_best_true_term)}"
    L.append(f"| {x.symbol}{' (weak)' if x.weak else ''} | {x.in_H} | {x.n_targets_2_300} ({x.n_targets_flagged}) | "
             f"{rk} / {x.n_reportable} | {x.top1_term if isinstance(x.top1_term, str) else ''} | "
             f"{x.top_v1prime_label if isinstance(x.top_v1prime_label, str) else ''} |")
L += ["", "## Covariate shift and signal quintiles", "", "| covariate | SMD H−U | SMD H−LOO | SMD U−LOO |", "|---|---|---|---|"]
for x in SMD.itertuples():
    L.append(f"| {x.covariate} | {x.smd_H_vs_U:+.3f} | {x.smd_H_vs_LOO:+.3f} | {x.smd_U_vs_LOO:+.3f} |")
L += ["", "| quintile (zavg range) | n | zavg (CI) | prior | null | GLS | zavg − prior (CI) |", "|---|---|---|---|---|---|---|"]
for x in QT.itertuples():
    L.append(f"| {x.quintile} ({x.zmean_min:.2f}–{x.zmean_max:.2f}) | {x.n} | {x.p1_zavg:.3f} ({x.p1_zavg_lo:.3f}–"
             f"{x.p1_zavg_hi:.3f}) | {x.p1_prior:.3f} | {x.p1_null:.3f} | {x.p1_gls:.3f} | {x.d_prior:+.3f} "
             f"({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) |")
L += ["", "## Secondary batch (reported all or none)", "",
      "| comparator | precision@1 (CI) | coverage | zavg − comparator (CI) |", "|---|---|---|---|"]
for x in SEC[SEC.kind == "comparator"].itertuples():
    L.append(f"| {x.analysis} | {x.p1_method:.3f} ({x.p1_method_lo:.3f}–{x.p1_method_hi:.3f}) | {x.coverage:.3f} | "
             f"{x.d_zavg_minus_method:+.3f} ({x.d_lo:+.3f} to {x.d_hi:+.3f}) |")
L += ["", "| variant | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) | IUT |", "|---|---|---|---|---|---|---|---|"]
for x in SEC[SEC.kind.isin(["variant", "reweighted"])].itertuples():
    L.append(f"| {x.analysis} | {x.n} | {x.p1_zavg:.3f} ({x.p1_zavg_lo:.3f}–{x.p1_zavg_hi:.3f}) | {x.p1_prior:.3f} | "
             f"{x.p1_null:.3f} | {x.d_prior:+.3f} ({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | {x.d_null:+.3f} "
             f"({x.d_null_lo:+.3f} to {x.d_null_hi:+.3f}) | {'pass' if x.iut_pass else 'fail'} |")
uw, lf = sec["u_reweighted"], sec["loo_fitted_calibration"]
L += ["", f"U-reweighting: {uw['n_U_eligible']} U-eligible of {uw['n_U_scorable']} scorable U genes; ESS "
      f"{uw['ess']:.0f}; weighted zavg − GLS {uw['d_gls']:+.3f} ({ci(uw['d_gls_ci'], 3, True)}).",
      f"LOO-fitted calibration on H: mean p {lf['mean_pred']:.3f} vs observed {lf['obs_rate']:.3f}; Brier "
      f"{lf['brier']:.4f}; intercept {lf['intercept']:+.3f} ({ci(lf['intercept_ci'], 3, True)}); slope "
      f"{lf['slope']:.3f} ({ci(lf['slope_ci'])}).", "",
      "## Calibration model for U", "",
      f"Fitted on {calr['n_fit']} H genes with a top term ({calr['n_without_prediction']} without). Families with ≥ 30 "
      f"H genes: {', '.join(calr['families_kept'])} (reference {calr['reference_family']}). Coefficients: "
      + "; ".join(f"{k} {v:+.4f}" for k, v in calr["coef"].items()) + f"; intercept {calr['intercept']:+.4f}. "
      "Saved to results/calibration/model_H.json.", "",
      "## Files", "",
      "core.md, secondary.md, calibration.md; methods_core.tsv, comparisons_core.tsv, per_gene_core.tsv, splithalf.tsv, "
      "circularity_sensitivity.tsv, v1.tsv, controls_case_series.tsv, covariate_smd.tsv, signal_quintiles.tsv, "
      "top1_size.tsv, secondary.tsv, reliability_oof.tsv, loo_fitted_reliability.tsv, calibration_oof.tsv, fig_*.tsv; "
      "figures manuscript/figures/m5b_{precision_by_method,reliability,controls,signal_quintiles}.{png,svg}.", ""]
(OUT / "SUMMARY.md").write_text("\n".join(L))
C.log(f"figures + SUMMARY written in {time.perf_counter() - T_START:.0f} s")
