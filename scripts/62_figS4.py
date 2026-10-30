#!/usr/bin/env python
"""62_figS4.py -- S4 Fig: summary of the post-review exploratory analyses (manuscript review round 1).

[post-review exploratory] Reads only committed tables written by scripts/90_revision_analyses.py (results/revision/). No new analysis of H outcomes. The only quantities
computed here are combined counts of existing flags (Kim 2019 edge OR cluster), written to
source_data/FigS4_derived_numbers.tsv.

Panels
  A  N1 (function established) rate by entry route (D3 only vs D1&D2) and by definition-artefact flag, for the
     random-50 audit (prevalence) and for the selected candidates (top 40 + S20 + extra30; not a prevalence).
  B  Overlap of the top 40, S20 and the ten report genes with prior catalogues and interaction resources.
  C  Assessability (C1) against the count expected from the clean-negative false-call rates (null-adjusted bound).
  D  Calibration-model comparison: frozen §3.7 model versus one- and two-covariate models (slope, c-statistic).

Style follows scripts/60_figures.py. Writes manuscript/figures/FigS4.png (300 dpi) and .svg, and one source-data TSV
per panel in manuscript/figures/source_data/.

Run: ./.env/bin/python -I scripts/62_figS4.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "results/revision"
FIG = ROOT / "manuscript/figures"
SD = FIG / "source_data"
SD.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- style (as scripts/60_figures.py)
S1, S2, S3, S4, S5, S6, S7, S8 = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6",
                                  "#e34948")
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#9a9993", "#e4e3df"
LIGHT = "#c9c8c2"
plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"], "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "svg.fonttype": "none", "legend.frameon": False, "lines.linewidth": 1.2,
})
MM = 1 / 25.4
W2 = 180 * MM


def tsv(path, **kw):
    return pd.read_csv(path, sep="\t", **kw)


def b(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def letter(ax, s, x=-0.12, y=1.04):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom", ha="left")


def hgrid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


DERIVED = []

fig = plt.figure(figsize=(W2, 150 * MM))
gs = fig.add_gridspec(2, 2, hspace=0.6, wspace=1.05, width_ratios=[1.0, 1.1])

# ====================================================================== A: N1 rate by entry route / flag
n1 = tsv(RV / "a1_N1_rates_by_route_and_flag.tsv")
popmap = {"random-50 audit (prevalence)": "random 50 (audit)",
          "top40 + S20 + extra30 (L class; selected, not prevalence)": "candidates (L)"}
rows = []
for pop, plab in popmap.items():
    for strat, lab in (("entry route", None), ("definition-artefact flag", None)):
        sub = n1[(n1.population == pop) & (n1.stratifier == strat)]
        for _, r in sub.iterrows():
            rows.append(dict(population=plab, stratifier=strat, stratum=r.stratum, n=int(r.n), n_N1=int(r.n_N1),
                             N1_rate=r.N1_rate, wilson_lo=r.wilson_lo, wilson_hi=r.wilson_hi))
A = pd.DataFrame(rows)
A.to_csv(SD / "FigS4a_N1_by_route_and_flag.tsv", sep="\t", index=False)

ax = fig.add_subplot(gs[0, 0])
labels = {"D3 only": "D3 only (literature route)", "D1&D2": "D1 & D2 (UniProt score ≤ 2)",
          "flag": "definition-artefact flag", "no flag": "no flag"}
order = [("entry route", "D3 only"), ("entry route", "D1&D2"), ("definition-artefact flag", "flag"),
         ("definition-artefact flag", "no flag")]
ylab, ypos = [], []
y = 0
for strat, st in order:
    for pop, col, dy in (("random 50 (audit)", S1, 0.17), ("candidates (L)", S2, -0.17)):
        r = A[(A.population == pop) & (A.stratifier == strat) & (A.stratum == st)].iloc[0]
        ax.errorbar(r.N1_rate, y + dy, xerr=[[r.N1_rate - r.wilson_lo], [r.wilson_hi - r.N1_rate]], fmt="o",
                    ms=3.5, color=col, ecolor=col, elinewidth=0.9, capsize=1.5, zorder=3,
                    label=pop if (strat, st) == order[0] else None)
        ax.text(1.03, y + dy, f"{r.n_N1}/{r.n}", va="center", ha="left", fontsize=6.0, color=col)
    ylab.append(labels[st])
    ypos.append(y)
    y -= 1 if st != "D1&D2" else 1.4
ax.set_yticks(ypos)
ax.set_yticklabels(ylab)
ax.set_xlim(0, 1.2)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel("fraction N1 (function established), Wilson 95% CI")
hgrid(ax)
ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, fontsize=6.3, handletextpad=0.3)
letter(ax, "A", x=-0.62)

# ====================================================================== B: novelty overlap
nov = tsv(RV / "a2_novelty_overlap.tsv")
for c in ["in_top40", "in_S20", "in_reports10", "humap_cocomplex_top10", "predictomes_spoc_ge0p5_top10",
          "wainberg_module_d_ge0p5_with_top10", "wainberg_gls_pair_top10", "kim2019_edge_top10",
          "kim2019_cluster_with_top10", "coessentiality_catalogue_prior", "physical_resource_prior", "any_prior"]:
    nov[c] = b(nov[c])
nov["wainberg_sd3"] = nov.wainberg_uncharacterised_prediction.fillna("").astype(str).str.len() > 0
nov["kim_any"] = nov.kim2019_edge_top10 | nov.kim2019_cluster_with_top10
res = [("humap_cocomplex_top10", "hu.MAP 3.0 co-complex"),
       ("predictomes_spoc_ge0p5_top10", "Predictomes SPOC ≥ 0.5"),
       ("wainberg_gls_pair_top10", "Wainberg 2021 GLS pair"),
       ("wainberg_module_d_ge0p5_with_top10", "Wainberg 2021 module (d ≥ 0.5)"),
       ("wainberg_sd3", "Wainberg 2021 function prediction"),
       ("kim_any", "Kim 2019 edge or cluster"),
       ("coessentiality_catalogue_prior", "any co-essentiality catalogue"),
       ("any_prior", "any prior resource")]
sets = [("in_top40", "top 40", S2), ("in_S20", "S20", S3), ("in_reports10", "10 report genes", S7)]
rows = []
for col, lab in res:
    for sc, slab, _ in sets:
        sub = nov[nov[sc]]
        rows.append(dict(resource=lab, column=col, set=slab, k=int(sub[col].sum()), n=len(sub),
                         fraction=sub[col].mean()))
B = pd.DataFrame(rows)
B.to_csv(SD / "FigS4b_novelty_overlap.tsv", sep="\t", index=False)
for sc, slab, _ in sets:
    sub = nov[nov[sc]]
    DERIVED.append(dict(key=f"novelty_kim_edge_or_cluster_{slab.replace(' ', '_')}",
                        value=f"{int(sub.kim_any.sum())}/{len(sub)}",
                        note="Kim 2019 network edge OR shared MCL cluster with >= 1 top-10 partner",
                        inputs="results/revision/a2_novelty_overlap.tsv"))

ax = fig.add_subplot(gs[0, 1])
h = 0.26
for i, (col, lab) in enumerate(res):
    for j, (sc, slab, colr) in enumerate(sets):
        r = B[(B.column == col) & (B.set == slab)].iloc[0]
        yy = -i + (1 - j) * h
        ax.barh(yy, r.fraction, height=h * 0.92, color=colr, zorder=3, label=slab if i == 0 else None)
        ax.text(r.fraction + 0.01, yy, f"{r.k}/{r.n}", va="center", ha="left", fontsize=5.6, color=INK2)
    if col == "coessentiality_catalogue_prior":
        ax.axhline(-i + 0.5, color=MUTED, lw=0.5, ls=":")
ax.set_yticks([-i for i in range(len(res))])
ax.set_yticklabels([lab for _, lab in res])
ax.set_xlim(0, 1.2)
ax.set_ylim(-len(res) + 0.45, 0.55)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel("fraction with the relationship already published")
hgrid(ax)
ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=3, fontsize=6.3, handletextpad=0.3)
letter(ax, "B", x=-0.6)

# ====================================================================== C: null-adjusted assessability
a6 = tsv(RV / "a6_assessability_null_adjusted.tsv")
a6.to_csv(SD / "FigS4c_assessability_null_adjusted.tsv", sep="\t", index=False)
ax = fig.add_subplot(gs[1, 0])
strat_lab = {"any_dependency": "null rates by\nany-dependency class", "sd_tertile_withinU": "null rates by\nprofile-SD tertile"}
expr_lab = {"frozen expressed (635)": "frozen column (635)", "DESIGN expressed (646)": "design definition (646)"}
yt, yl = [], []
y = 0
for st in ("any_dependency", "sd_tertile_withinU"):
    for ex in ("DESIGN expressed (646)", "frozen expressed (635)"):
        r = a6[(a6.stratifier == st) & (a6.expression == ex)].iloc[0]
        ax.barh(y, r.observed, height=0.62, color=LIGHT, zorder=2, label="assessable (observed)" if y == 0 else None)
        ax.barh(y, r.implied_true, height=0.62, color=S1, zorder=3,
                label="null-adjusted (observed − expected null calls)" if y == 0 else None)
        ax.errorbar(r.implied_true, y, xerr=[[r.implied_true - r.implied_lo], [r.implied_hi - r.implied_true]],
                    fmt="none", ecolor=INK, elinewidth=0.8, capsize=1.5, zorder=4)
        ax.text(r.observed + 8, y, f"{r.implied_true:.0f} ({r.implied_lo:.0f}–{r.implied_hi:.0f}); "
                f"{100 * r.implied_frac_U:.1f}% of U", va="center", ha="left", fontsize=6.0, color=INK2)
        yt.append(y)
        yl.append(expr_lab[ex])
        y -= 1
    ax.text(-0.43, y + 1.5, strat_lab[st], transform=ax.get_yaxis_transform(), ha="right", va="center",
            fontsize=6.2, color=MUTED)
    y -= 0.5
ax.set_yticks(yt)
ax.set_yticklabels(yl)
ax.set_xlim(0, 1050)
ax.set_xlabel("U genes (scorable, expressed)")
hgrid(ax)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.55), fontsize=6.3, ncol=1, handletextpad=0.3)
letter(ax, "C", x=-0.62)

# ====================================================================== D: calibration-model comparison
cm = tsv(RV / "a4_calibration_models.tsv")
su = tsv(RV / "a4_simple_models_on_U.tsv")
keep = ["frozen §3.7 model (4 covariates + family)", "zmean only", "zmean + coverage"]
mlab = {keep[0]: "frozen model\n(4 covariates + family)", keep[1]: "top-K mean\nzavg_BEF only",
        keep[2]: "zavg_BEF +\ncoverage"}
cm = cm[cm.model.isin(keep)].set_index("model").loc[keep].reset_index()
D = cm[["model", "events", "n_params_excl_intercept", "events_per_param", "slope", "slope_wald_lo", "slope_wald_hi",
        "slope_boot_lo", "slope_boot_hi", "c", "c_boot_lo", "c_boot_hi", "brier", "brier_ref", "brier_skill"]].copy()
D = D.merge(su[["model", "sigma_on_frozen_support", "top40_overlap_with_primary"]], on="model", how="left")
D.to_csv(SD / "FigS4d_calibration_models.tsv", sep="\t", index=False)

sub = gs[1, 1].subgridspec(1, 2, wspace=0.25, width_ratios=[1, 1])
axs = fig.add_subplot(sub[0, 0])
axc = fig.add_subplot(sub[0, 1], sharey=axs)
cols = [S8, S1, S3]
for i, r in D.iterrows():
    yy = -i
    axs.plot([r.slope_wald_lo, r.slope_wald_hi], [yy + 0.12] * 2, color=cols[i], lw=0.9)
    axs.plot([r.slope_boot_lo, r.slope_boot_hi], [yy - 0.12] * 2, color=cols[i], lw=0.9, ls=(0, (2, 1)))
    axs.plot(r.slope, yy, "o", ms=3.5, color=cols[i], zorder=3)
    axc.plot([r.c_boot_lo, r.c_boot_hi], [yy] * 2, color=cols[i], lw=0.9)
    axc.plot(r.c, yy, "o", ms=3.5, color=cols[i], zorder=3)
    axc.text(1.02, yy, f"EPP {r.events_per_param:.1f}\nBSS {r.brier_skill:.3f}", transform=axc.get_yaxis_transform(),
             va="center", ha="left", fontsize=5.6, color=INK2)
axs.axvline(1, color=MUTED, lw=0.6, ls="--")
axs.set_yticks([-i for i in range(len(D))])
axs.set_yticklabels([mlab[m] for m in D.model])
axs.set_xlim(0.4, 1.4)
axs.set_xlabel("calibration slope\n(solid Wald;\ndashed bootstrap)")
axc.set_xlim(0.7, 0.95)
axc.set_xlabel("c-statistic\n(bootstrap CI)")
plt.setp(axc.get_yticklabels(), visible=False)
for a in (axs, axc):
    hgrid(a)
    a.set_ylim(-len(D) + 0.4, 0.6)
letter(axs, "D", x=-0.95)

pd.DataFrame(DERIVED).to_csv(SD / "FigS4_derived_numbers.tsv", sep="\t", index=False)

fig.savefig(FIG / "FigS4.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "FigS4.svg", bbox_inches="tight")
plt.close(fig)
print("wrote FigS4")
for d in DERIVED:
    print(d["key"], d["value"])
