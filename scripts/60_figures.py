#!/usr/bin/env python
"""60_figures.py -- manuscript figures for claims C1-C3 (no new analysis of H or U outcomes).

Reads only committed result files (results/assessability, results/audit, results/verification, results/orthogonal,
results/calibration, results/holdout_eval, results/ledger). Does NOT read results/m7/ (blinded literature step).

Writes manuscript/figures/Fig1..Fig4 and FigS1..FigS3 (.png at 300 dpi and .svg) and one source-data TSV per panel in
manuscript/figures/source_data/. Numbers that are derived here rather than copied (Wilson CIs on census-type
proportions, top-40 flag counts, Sigma p_cal of the primary top 40, descriptive paired comparisons of orthogonal support)
are written to manuscript/figures/source_data/derived_numbers.tsv; they are descriptive and not pre-specified.

Run: ./.env/bin/python -I scripts/60_figures.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from scipy.stats import binomtest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
FIG = ROOT / "manuscript/figures"
SD = FIG / "source_data"
SD.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- style
# Categorical slots (dataviz reference palette, fixed order); neutral inks for text, comparators and grids.
S1, S2, S3, S4, S5, S6, S7, S8 = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6",
                                  "#e34948")
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#9a9993", "#e4e3df"
LIGHT = "#c9c8c2"
plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"], "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "legend.fontsize": 6.8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "svg.fonttype": "none", "legend.frameon": False, "lines.linewidth": 1.2,
})
MM = 1 / 25.4
W2 = 180 * MM  # full page width
DERIVED = []


def derived(key, value, note, source):
    DERIVED.append({"key": key, "value": value, "note": note, "inputs": source})


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def letter(ax, s, x=-0.12, y=1.04):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom", ha="left")


def wilson(k, n, z=1.959964):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def hgrid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def tsv(path, **kw):
    return pd.read_csv(path, sep="\t", **kw)


def b(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


FAM_LABEL = {"other": "other", "signalling_lineage": "signalling/lineage", "ER_Golgi_secretory_lipid": "ER/Golgi/secretory",
             "centrosome_cilia_mitosis": "centrosome/cilia/mitosis", "ribosome_biogenesis_translation":
                 "ribosome/translation", "nuclear_RNA_machinery": "nuclear RNA machinery",
             "DNA_replication_repair": "DNA replication/repair", "mitochondrial": "mitochondrial"}

# ====================================================================== FIGURE 1
AU = tsv(R / "assessability/assessability_U.tsv")
AU["assess"] = b(AU.assessable_design)
AU["scor"] = b(AU.scorable)
AU["expr_d"] = b(AU.expressed_design)

fig = plt.figure(figsize=(W2, 140 * MM))
gs = fig.add_gridspec(2, 3, height_ratios=[0.62, 1.25], width_ratios=[1.05, 1.25, 0.95], hspace=0.32, wspace=0.75)

# ---- a: study design schematic
ax = fig.add_subplot(gs[0, :])
ax.set_xlim(0, 100)
ax.set_ylim(0, 30)
ax.axis("off")
letter(ax, "a", x=-0.035, y=0.97)
boxes = [
    (1, 17, 17, 11, "Pre-registration", "U = D1 ∩ (D2 ∪ D3):\n4,924 genes; list, code,\ndesign hash-frozen", S1),
    (21, 17, 17, 11, "Tool verification", "published HT-AP\nreproduced; 14/14\nsanity checks", INK2),
    (41, 17, 17, 11, "Ranker choice (LOO)", "3,000 characterised\ngenes; R1 chosen by\nMRR; label shuffle", INK2),
    (61, 17, 17, 11, "Temporal hold-out H", "unknown at GO 2018-07;\none look; precision@1\nvs prior, matched null", S2),
    (81, 17, 18, 11, "Calibration", "logistic model on H\n(cross-fitted); p_cal\nwithin support", S2),
    (1, 2, 17, 11, "C1 census", "scorable, expressed,\nassessable (split-\nhalf reproducibility)", S1),
    (21, 2, 17, 11, "Curation-lag audit", "random 50 U genes;\nN1/N2/N3; LLM\nrecall probe", S1),
    (41, 2, 17, 11, "Predictions for U", "top V2 term (R1)\nfor 4,137 genes;\nartefact flags", S3),
    (61, 2, 17, 11, "C3 catalogue", "p_cal, Σp_cal (CI);\nclean-negative\ncontrol", S3),
    (81, 2, 18, 11, "Orthogonal support", "real vs matched-gene\nvs decoy; top 40\n→ literature (C4)", S3),
]
for x, y, w, h, title, body, col in boxes:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8", fc="white", ec=col,
                                lw=1.0))
    ax.add_patch(FancyBboxPatch((x, y + h - 2.6), w, 2.6, boxstyle="round,pad=0.25,rounding_size=0.8", fc=col,
                                ec=col, lw=1.0, alpha=0.14))
    ax.text(x + w / 2, y + h - 1.3, title, ha="center", va="center", fontsize=6.6, fontweight="bold")
    ax.text(x + w / 2, y + (h - 2.6) / 2, body, ha="center", va="center", fontsize=5.9, color=INK2,
            linespacing=1.25)
arrow = dict(arrowstyle="-|>", color=INK2, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=7)
for x0 in (18.6, 38.6, 58.6, 78.6):
    ax.annotate("", xy=(x0 + 2.0, 22.5), xytext=(x0, 22.5), arrowprops=arrow)
    ax.annotate("", xy=(x0 + 2.0, 7.5), xytext=(x0, 7.5), arrowprops=arrow)
ax.annotate("", xy=(9.5, 13.6), xytext=(9.5, 16.4), arrowprops=arrow)
ax.annotate("", xy=(49.5, 13.6), xytext=(89.5, 16.4),
            arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.7, mutation_scale=7, connectionstyle="arc3,rad=0.0"))
ax.text(64, 15.0, "model applied to U", fontsize=5.8, color=INK2, ha="center", va="center", style="italic",
        bbox=dict(fc="white", ec="none", pad=0.6))
for txt, x, col in (("pre-registration & C1", 0.5, S1), ("C2 accuracy & calibration", 60.5, S2),
                    ("C3 catalogue", 40.5, S3)):
    pass  # colour key carried by box outlines; legend below
for i, (lab, col) in enumerate((("C1 census / pre-registration", S1), ("C2 hold-out & calibration", S2),
                                ("C3 catalogue", S3), ("verification / ranker choice", INK2))):
    ax.plot([1 + i * 24, 3.5 + i * 24], [30.2, 30.2], color=col, lw=2.2, solid_capstyle="round", clip_on=False)
    ax.text(4.3 + i * 24, 30.2, lab, va="center", fontsize=6.3, color=INK2, clip_on=False)

# ---- b: census funnel
ax = fig.add_subplot(gs[1, 0])
letter(ax, "b", x=-0.62)
n_u = len(AU)
in_depmap = int(b(AU.in_depmap).sum())
n_scor = int(AU.scor.sum())
n_se = int((AU.scor & AU.expr_d).sum())
n_as = int(AU.assess.sum())
n_as_frozen = int(b(AU.assessable).sum())
funnel = pd.DataFrame({
    "step": ["HGNC protein-coding", "pre-registered U", "in DepMap 26Q3", "scorable", "scorable & expressed",
             "assessable"],
    "n": [19296, n_u, in_depmap, n_scor, n_se, n_as],
    "source": ["preregistration/CRITERIA.md"] + ["results/assessability/assessability_U.tsv"] * 5})
funnel["frac_of_U"] = funnel.n / n_u
funnel.to_csv(SD / "Fig1b_census_funnel.tsv", sep="\t", index=False)
y = np.arange(len(funnel))[::-1]
cols = [LIGHT, S1, S1, S1, S1, S1]
alphas = [1, 0.35, 0.5, 0.6, 0.8, 1.0]
for yi, n, c, a in zip(y, funnel.n, cols, alphas):
    ax.barh(yi, n, color=c, alpha=a, height=0.66, zorder=2)
for yi, n, f, i in zip(y, funnel.n, funnel.frac_of_U, range(len(funnel))):
    lab = f"{n:,}" + ("" if i < 1 else f"  ({100 * f:.1f}% of U)" if i > 1 else "")
    ax.text(n + 300, yi, lab, va="center", fontsize=6.4, color=INK)
ax.set_yticks(y)
ax.set_yticklabels(funnel.step)
ax.set_xlim(0, 30000)
ax.set_xticks([0, 10000, 20000])
ax.set_xticklabels(["0", "10", "20"])
ax.set_xlabel("genes (thousands)")
hgrid(ax)
ax.set_title("Census of U (C1)", loc="left", fontsize=8)

# ---- c: assessable fraction by stratum
ax = fig.add_subplot(gs[1, 1])
letter(ax, "c", x=-0.75)
rows = []


def add(group, label, mask):
    m = mask.fillna(False).astype(bool)
    n = int(m.sum())
    k = int((AU.assess & m).sum())
    s = int((AU.scor & m).sum())
    rows.append({"group": group, "stratum": label, "n_U": n, "n_scorable": s, "n_assessable": k,
                 "frac_of_U": k / n if n else np.nan, "frac_of_scorable": k / s if s else np.nan})


add("all", "all U", AU.hgnc_id.notna())
add("all", "headline stratum", b(AU.headline_design))
for v, lab in (("other", "other"), ("tandem_cluster", "tandem cluster"),
               ("chemosensory_epidermal", "chemosensory/epidermal")):
    add("family", lab, AU.family_stratum == v)
add("expression", "expressed (incl. lineage-restricted)", AU.expr_d)
add("expression", "not expressed", ~AU.expr_d & AU.expression_stratum.ne("no_expression_data"))
for v in ("high", "mid", "low"):
    add("profile SD (tertile within U)", f"{v} SD", AU.sd_tertile_withinU == v)
add("dependency", "any dependency", b(AU.any_dependency))
add("dependency", "no dependency", AU.any_dependency.astype(str).str.lower() == "false")
add("other strata", "low coverage (non-background)", b(AU.low_coverage))
add("other strata", "core (≤ 3 PMIDs and Tdark)", b(AU.core))
add("other strata", "transmembrane", AU.tm_or_secreted.isin(["TM", "TM & secreted"]))
add("other strata", "secreted", AU.tm_or_secreted.isin(["secreted", "TM & secreted"]))
ST = pd.DataFrame(rows)
ST.to_csv(SD / "Fig1c_assessable_by_stratum.tsv", sep="\t", index=False)
yy, ylabels, ypos, ycur, prev = [], [], [], 0, None
for r in ST.itertuples():
    if prev is not None and r.group != prev:
        ycur += 0.6
    ypos.append(ycur)
    ycur += 1
    prev = r.group
ypos = -np.array(ypos)
ax.barh(ypos, ST.frac_of_U, height=0.7, color=[S1 if g != "all" else INK2 for g in ST.group], zorder=2)
for yi, r in zip(ypos, ST.itertuples()):
    ax.text(r.frac_of_U + 0.01, yi, f"{r.n_assessable:,}/{r.n_U:,}", va="center", fontsize=6.0, color=INK2)
ax.set_yticks(ypos)
ax.set_yticklabels(ST.stratum, fontsize=6.6)
ax.set_xlim(0, 0.55)
ax.set_xlabel("fraction of U genes assessable")
hgrid(ax)
ax.set_title("Assessable fraction by stratum", loc="left", fontsize=8)

# ---- d: curation-lag audit + recall probe
ax = fig.add_subplot(gs[1, 2])
letter(ax, "d", x=-0.3)
aud = tsv(R / "audit/curation_lag_audit.tsv")
rp = tsv(R / "audit/recall_probe_random50.tsv")
m = aud.merge(rp[["hgnc_id", "recognised"]], on="hgnc_id")
rows = []
for c in ("N1", "N2", "N3"):
    sub = m[m["class"] == c]
    k, n = len(sub), len(m)
    lo, hi = wilson(k, n)
    rec = int((sub.recognised == "yes").sum())
    rows.append({"class": c, "n": k, "of": n, "frac": k / n, "wilson_lo": lo, "wilson_hi": hi,
                 "recognised_by_probe": rec, "not_recognised": k - rec})
AUD = pd.DataFrame(rows)
AUD.to_csv(SD / "Fig1d_curation_lag_audit.tsv", sep="\t", index=False)
for r in AUD.itertuples():
    derived(f"audit_{r._1}_wilson", f"{r.n}/{r.of} = {r.frac:.2f} ({r.wilson_lo:.2f}-{r.wilson_hi:.2f})",
            "curation-lag class share, Wilson 95% CI", "results/audit/curation_lag_audit.tsv")
x = np.arange(3)
rec_f = AUD.recognised_by_probe / AUD.of
nrec_f = AUD.not_recognised / AUD.of
ax.bar(x, rec_f, width=0.62, color=S1, zorder=2, label="recognised by recall probe")
ax.bar(x, nrec_f, bottom=rec_f, width=0.62, color=S1, alpha=0.3, zorder=2, label="not recognised")
ax.errorbar(x, AUD.frac, yerr=[AUD.frac - AUD.wilson_lo, AUD.wilson_hi - AUD.frac], fmt="none", ecolor=INK,
            elinewidth=0.8, capsize=2.5, zorder=3)
for xi, r in zip(x, AUD.itertuples()):
    ax.text(xi, r.wilson_hi + 0.02, f"{r.n}/50", ha="center", fontsize=6.4)
ax.set_xticks(x)
ax.set_xticklabels(["N1\nestablished", "N2\npartial", "N3\nnone"], fontsize=6.0)
ax.set_ylim(0, 0.8)
ax.set_ylabel("fraction of random 50 U genes")
hgrid(ax, "y")
ax.legend(loc="upper right", fontsize=6.0, handlelength=1.2, bbox_to_anchor=(1.08, 1.03))
ax.set_title("Curation-lag audit", loc="left", fontsize=8)
save(fig, "Fig1")

# ====================================================================== FIGURE 2
HE = R / "holdout_eval"
PM = tsv(HE / "fig_precision_by_method.tsv")
CMP = tsv(HE / "comparisons_core.tsv")
SEC = tsv(HE / "secondary.tsv")
QT = tsv(HE / "fig_signal_quintiles.tsv")
REL = tsv(HE / "fig_reliability.tsv")
CT = tsv(HE / "controls_case_series.tsv")

fig = plt.figure(figsize=(W2, 150 * MM))
gs = fig.add_gridspec(2, 6, hspace=0.55, wspace=1.9)

# ---- a: precision@1 by method
ax = fig.add_subplot(gs[0, 0:2])
letter(ax, "a", x=-0.62)
order = ["zavg_BEF (R1)", "GLS (R1)", "Pearson", "matched-gene null", "prior-only", "PPI module transfer",
         "Homology baseline"]
lab = {"zavg_BEF (R1)": "zavg_BEF", "GLS (R1)": "GLS", "Pearson": "Pearson", "matched-gene null": "matched-gene null",
       "prior-only": "prior-only", "PPI module transfer": "hu.MAP PPI transfer",
       "Homology baseline": "homology (t0 IEA/ISS/IBA)"}
P = PM.set_index("method").loc[order].reset_index()
P.to_csv(SD / "Fig2a_precision_by_method.tsv", sep="\t", index=False)
yv = -np.arange(len(P)) - np.array([0, 0, 0, 0, 0, 0.6, 0.6])
for yi, r in zip(yv, P.itertuples()):
    col = S2 if r.method.startswith("zavg") else (INK2 if r.group == "core" else MUTED)
    ax.plot([r.lo, r.hi], [yi, yi], color=col, lw=1.4, solid_capstyle="round", zorder=3)
    ax.plot(r.p1, yi, "o", ms=4.5, color=col, mec="white", mew=0.6, zorder=4)
    ax.text(r.hi + 0.006, yi, f"{r.p1:.3f}", va="center", fontsize=6.2, color=INK2)
ax.set_yticks(yv)
ax.set_yticklabels([lab[m] for m in P.method])
ax.set_xlabel("precision@1 on H (n = 809)")
ax.set_xlim(-0.005, 0.29)
hgrid(ax)
ax.text(0.285, yv[5] + 0.55, "secondary batch", fontsize=6, color=MUTED, ha="right")
ax.axhline(yv[4] - 0.8, color=GRID, lw=0.6)

# ---- b: paired differences
ax = fig.add_subplot(gs[0, 2:4])
letter(ax, "b", x=-0.55)
c703 = CMP[CMP.n_clusters == 703].set_index("comparison")
drows = [
    ("prior-only", "primary", c703.loc["precision@1 zavg - prior"]),
    ("matched-gene null", "primary", c703.loc["precision@1 zavg - null"]),
    ("GLS", "key secondary", c703.loc["precision@1 zavg - GLS (two-sided)"]),
]
D = pd.DataFrame([{"comparator": a, "role": r_, "diff": s["diff"], "ci_lo": s.ci_lo, "ci_hi": s.ci_hi,
                   "source": "results/holdout_eval/comparisons_core.tsv (PMID-only clusters)"} for a, r_, s in drows])
for name, key in (("Pearson", "Pearson (R1)"), ("hu.MAP PPI transfer", "PPI module transfer (hu.MAP 3.0 top-25)"),
                  ("homology (t0 IEA/ISS/IBA)", "Homology baseline (t0 IEA/ISS/IBA, then frequency)")):
    s = SEC.set_index("analysis").loc[key]
    D.loc[len(D)] = {"comparator": name, "role": "secondary batch", "diff": s.d_zavg_minus_method, "ci_lo": s.d_lo,
                     "ci_hi": s.d_hi, "source": "results/holdout_eval/secondary.tsv"}
D.to_csv(SD / "Fig2b_paired_differences.tsv", sep="\t", index=False)
yv = -np.arange(len(D)) - np.array([0, 0, 0.5, 1.0, 1.0, 1.0])
for yi, r in zip(yv, D.itertuples()):
    col = S2 if r.role == "primary" else (INK2 if r.role == "key secondary" else MUTED)
    ax.plot([r.ci_lo, r.ci_hi], [yi, yi], color=col, lw=1.4, solid_capstyle="round", zorder=3)
    ax.plot(r.diff, yi, "o", ms=4.5, color=col, mec="white", mew=0.6, zorder=4)
ax.axvline(0, color=INK2, lw=0.7)
ax.set_yticks(yv)
ax.set_yticklabels([{"homology (t0 IEA/ISS/IBA)": "homology", "hu.MAP PPI transfer": "PPI transfer",
                    "matched-gene null": "matched null"}.get(c, c) for c in D.comparator])
ax.set_xlabel("Δ precision@1, zavg_BEF − comparator")
ax.set_xlim(-0.24, 0.06)
hgrid(ax)
for txt, yy_ in (("primary IUT", yv[0] + 0.55), ("key secondary", yv[2] + 0.55), ("secondary batch", yv[3] + 0.55)):
    ax.text(-0.235, yy_, txt, fontsize=6, color=MUTED, ha="left")

# ---- c: precision by signal quintile
ax = fig.add_subplot(gs[0, 4:6])
letter(ax, "c", x=-0.32)
QT.to_csv(SD / "Fig2c_signal_quintiles.tsv", sep="\t", index=False)
x = np.arange(len(QT))
for off, col_, k, labl in ((-0.2, S2, "zavg", "zavg_BEF"), (0.0, INK2, "gls", "GLS"), (0.2, MUTED, "null",
                                                                                         "matched null")):
    v = QT[f"p1_{k}"].values
    lo, hi = QT[f"p1_{k}_lo"].values, QT[f"p1_{k}_hi"].values
    ax.vlines(x + off, lo, hi, color=col_, lw=1.2, zorder=3)
    ax.plot(x + off, v, "o", ms=4, color=col_, mec="white", mew=0.5, zorder=4, label=labl)
ax.set_xticks(x)
ax.set_xticklabels([f"Q{i + 1}" for i in range(len(QT))])
ax.set_xlabel("quintile of top-K mean zavg_BEF")
ax.set_ylabel("precision@1")
ax.set_ylim(-0.005, 0.19)
hgrid(ax, "y")
ax.legend(loc="upper left", handletextpad=0.2)
ax.text(0.02, 0.58, "prior-only = 0 in every quintile\nQ1 2.7–3.7 … Q5 5.4–15.5", transform=ax.transAxes, fontsize=6, color=MUTED)

# ---- d: reliability
gsb = gs[1, :].subgridspec(1, 2, width_ratios=[1, 1.9], wspace=0.62)
ax = fig.add_subplot(gsb[0, 0])
letter(ax, "d", x=-0.32, y=1.1)
REL.to_csv(SD / "Fig2d_reliability.tsv", sep="\t", index=False)
ax.plot([0, 0.3], [0, 0.3], color=LIGHT, lw=0.8, ls="--", zorder=1)
for mod, col_, mk, labl in (("§3.7 out-of-fold", S2, "o", "pre-specified model (out-of-fold)"),
                            ("LOO-fitted", INK2, "s", "LOO-fitted (secondary)")):
    s = REL[REL.model == mod]
    ax.vlines(s.mean_pred, s.ci_lo, s.ci_hi, color=col_, lw=0.9, alpha=0.8, zorder=2)
    ax.plot(s.mean_pred, s.obs_rate, mk, ms=3.8, color=col_, mec="white", mew=0.5, label=labl, zorder=3)
ax.set_xlim(-0.01, 0.48)
ax.set_ylim(-0.01, 0.30)
ax.set_xlabel("mean predicted probability (bin)")
ax.set_ylabel("observed hit@1 (Wilson 95% CI)")
hgrid(ax, "y")
ax.legend(loc="upper left", fontsize=5.9)
ax.set_title("out-of-fold slope 0.82 (0.51–1.13),\nintercept −0.01 (−0.44 to 0.43), c = 0.86", fontsize=6.3,
             color=INK2, loc="right")

# ---- e: named controls
ax = fig.add_subplot(gsb[0, 1])
letter(ax, "e", x=-0.2, y=1.1)
CT = CT.copy()
CT["n_unflagged"] = CT.n_targets_2_300 - CT.n_targets_flagged
CT[["symbol", "weak", "in_H", "n_targets_2_300", "n_targets_flagged", "n_unflagged", "n_reportable",
    "rank_best_true_term", "best_true_term", "top1_term", "top_v1prime_label"]].to_csv(
    SD / "Fig2e_named_controls.tsv", sep="\t", index=False)
yv = -np.arange(len(CT))
ax.barh(yv, CT.n_unflagged, height=0.62, color=S2, zorder=2, label="new terms, clean")
ax.barh(yv, CT.n_targets_flagged, left=CT.n_unflagged, height=0.62, color="white", edgecolor=MUTED, hatch="/////",
        lw=0.5, zorder=2, label="new terms citing DepMap/co-essentiality work (excluded)")
ax.set_yticks(yv)
ax.set_yticklabels([f"{s}{' (weak)' if w else ''}{'' if h else ' †'}" for s, w, h in
                    zip(CT.symbol, CT.weak, CT.in_H)], fontsize=6.6)
ax.set_xlabel("new V2 terms since t0 (window 2–300)")
ax.set_xlim(0, 34)
hgrid(ax)
for yi, r in zip(yv, CT.itertuples()):
    txt = (f"rank {int(r.rank_best_true_term)} of {r.n_reportable}" if pd.notna(r.rank_best_true_term)
           else f"no clean true term ranked ({r.n_reportable} reportable)")
    ax.text(24.5, yi, txt, va="center", fontsize=6.2, color=INK if pd.notna(r.rank_best_true_term) else MUTED)
ax.text(24.5, 0.9, "best-ranked true term", fontsize=6.3, fontweight="bold", va="center")
ax.legend(loc="lower left", fontsize=6.0, bbox_to_anchor=(0.0, 1.0), ncol=2)
ax.text(0, -0.27, "† not in H (no new term in the 5–200 window at build time); case series only",
        fontsize=6, color=MUTED, transform=ax.transAxes)
save(fig, "Fig2")

# ====================================================================== FIGURE 3
LG = R / "ledger"
PU = tsv(LG / "figdata/pcal_all_U.tsv")
PU["cn"] = b(PU.clean_negative)
PU["ea"] = b(PU.expressed_design) & b(PU.assessable_design)
fig = plt.figure(figsize=(W2, 132 * MM))
gs = fig.add_gridspec(2, 2, hspace=0.6, wspace=0.75)

# ---- a: ECDF of p_cal
ax = fig.add_subplot(gs[0, 0])
letter(ax, "a", x=-0.17)
ins = PU.support_category == "in_support"
groups = [("in support, expressed & assessable", ins & PU.ea, S3),
          ("all in support", ins, INK2),
          ("clean negatives (in support)", ins & PU.cn, S7)]
ec_rows = []
for labl, mask, col_ in groups:
    v = np.sort(PU.loc[mask, "p_cal"].values)
    yv_ = np.arange(1, len(v) + 1) / len(v)
    ax.step(v, yv_, where="post", color=col_, lw=1.3, label=f"{labl} (n = {len(v):,})")
    q = np.quantile(v, [0.5, 0.9, 1.0])
    ec_rows.append({"set": labl, "n": len(v), "median": q[0], "p90": q[1], "max": q[2], "sum": v.sum()})
pd.DataFrame(ec_rows).to_csv(SD / "Fig3a_pcal_ecdf_summary.tsv", sep="\t", index=False)
PU.loc[ins, ["hgnc_id", "symbol", "family", "p_cal", "expressed_design", "assessable_design", "clean_negative"]].to_csv(
    SD / "Fig3a_pcal_in_support_U.tsv", sep="\t", index=False)
ax.set_xlim(0, 0.16)
ax.set_ylim(0, 1.02)
ax.set_xlabel("p_cal (in-support U genes)")
ax.set_ylabel("cumulative fraction")
hgrid(ax, "y")
ax.legend(loc="lower right", fontsize=6.2)
ax.text(0.155, 0.62, "Tier B (≥ 0.3) and Tier A (≥ 0.5)\nthresholds lie off scale:\nno gene reaches them", ha="right",
        fontsize=6.2, color=INK2)

# ---- b: Sigma p_cal
ax = fig.add_subplot(gs[0, 1])
letter(ax, "b", x=-0.42)
ps = __import__("json").loads((LG / "pcal_summary.json").read_text())
TP = tsv(LG / "top40_primary.tsv")
sig = pd.DataFrame([
    {"set": "all in-support U", "n": ps["category_counts"]["in_support"], "sum": ps["sum_pcal_in_support"],
     "lo": ps["ci_in_support"][0], "hi": ps["ci_in_support"][1], "source": "results/ledger/pcal_summary.json"},
    {"set": "in support, expr. & assessable", "n": ps["n_in_support_expressed_assessable"],
     "sum": ps["sum_pcal_in_support_expressed_assessable"], "lo": ps["ci_in_support_expressed_assessable"][0],
     "hi": ps["ci_in_support_expressed_assessable"][1], "source": "results/ledger/pcal_summary.json"},
    {"set": "boundary genes (upper bound)", "n": ps["category_counts"]["upper_bound"],
     "sum": ps["sum_pcal_upper_bound"], "lo": ps["ci_upper_bound"][0], "hi": ps["ci_upper_bound"][1],
     "source": "results/ledger/pcal_summary.json"},
    {"set": "primary top 40", "n": len(TP), "sum": TP.p_cal.sum(), "lo": np.nan, "hi": np.nan,
     "source": "results/ledger/top40_primary.tsv (point sum; no bootstrap CI)"},
])
sig.to_csv(SD / "Fig3b_sigma_pcal.tsv", sep="\t", index=False)
derived("sigma_pcal_top40_primary", f"{TP.p_cal.sum():.2f}", "sum of p_cal over the primary top 40 (no CI)",
        "results/ledger/top40_primary.tsv")
yv = -np.arange(len(sig))
for yi, r in zip(yv, sig.itertuples()):
    col_ = S3 if "upper" not in r.set else MUTED
    if pd.notna(r.lo):
        ax.plot([r.lo, r.hi], [yi, yi], color=col_, lw=1.5, solid_capstyle="round")
        ax.plot(r.sum, yi, "o", ms=5, color=col_, mec="white", mew=0.6)
        ax.text(r.hi + 1.0, yi, f"{r.sum:.1f} ({r.lo:.1f}–{r.hi:.1f})", va="center", fontsize=6.3)
    else:
        ax.plot(r.sum, yi, "o", ms=5, mfc="white", mec=col_, mew=1.0)
        ax.text(r.sum + 2.0, yi, f"{r.sum:.1f} (point sum, no CI)", va="center", fontsize=6.3)
ax.set_yticks(yv)
ax.set_yticklabels([f"{s}\n(n = {n:,})" for s, n in zip(sig.set, sig.n)], fontsize=6.5)
ax.set_xlim(0, 70)
ax.set_xlabel("Σ p_cal = expected confirmed top terms (95% CI)")
hgrid(ax)

# ---- c: orthogonal support real / matched / decoy
ax = fig.add_subplot(gs[1, 0])
letter(ax, "c", x=-0.17)
SP = tsv(LG / "support.tsv")
for c in ("diag_ok", "strict", "any_support"):
    SP[c] = b(SP[c])
for c in "PALGS":
    SP[f"sup_{c}"] = SP[f"state_{c}"] == "supports"
metrics = [("diag_ok", "rule"), ("strict", "strict"),
           ("any_support", "any"), ("sup_P", "P"), ("sup_A", "A"), ("sup_L", "L"), ("sup_G", "G")]
sets = [("real", S3), ("matched", INK2), ("decoy", LIGHT)]
rows = []
for mk, ml in metrics:
    for st, _ in sets:
        s = SP[SP.set == st]
        k, n = int(s[mk].sum()), len(s)
        lo, hi = wilson(k, n)
        rows.append({"metric": ml.replace("\n", " "), "set": st, "k": k, "n": n, "rate": k / n, "wilson_lo": lo,
                     "wilson_hi": hi})
SR = pd.DataFrame(rows)
# descriptive paired comparison (same anchor genes): exact McNemar on discordant pairs
pr = []
real = SP[SP.set == "real"].set_index("anchor_hgnc_id")
for other in ("matched", "decoy"):
    o = SP[SP.set == other].set_index("anchor_hgnc_id").loc[real.index]
    for mk, ml in metrics[:3]:
        a_, b_ = real[mk].values, o[mk].values
        n10, n01 = int((a_ & ~b_).sum()), int((~a_ & b_).sum())
        p = binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0
        pr.append({"metric": ml.replace("\n", " "), "comparison": f"real vs {other}", "n_pairs": len(a_),
                   "real_only": n10, "other_only": n01, "diff": a_.mean() - b_.mean(), "mcnemar_exact_p": p})
PR = pd.DataFrame(pr)
SR.to_csv(SD / "Fig3c_orthogonal_support_rates.tsv", sep="\t", index=False)
PR.to_csv(SD / "Fig3c_orthogonal_support_paired.tsv", sep="\t", index=False)
for r in PR.itertuples():
    derived(f"support_{r.metric.replace(' ', '_')}_{r.comparison.replace(' ', '_')}",
            f"diff {r.diff:+.3f}; discordant {r.real_only}/{r.other_only}; McNemar exact p = {r.mcnemar_exact_p:.3g}",
            "descriptive paired comparison over 247 anchors (not pre-specified)", "results/ledger/support.tsv")
x = np.arange(len(metrics)) + np.array([0, 0, 0, 0.5, 0.5, 0.5, 0.5])
w = 0.26
for i, (st, col_) in enumerate(sets):
    s = SR[SR.set == st]
    ax.bar(x + (i - 1) * w, s.rate, width=w - 0.03, color=col_, zorder=2, label={"real": "real predictions",
                                                                                    "matched": "matched-gene",
                                                                                    "decoy": "decoy term"}[st])
    ax.vlines(x + (i - 1) * w, s.wilson_lo, s.wilson_hi, color=INK, lw=0.6, zorder=3)
ax.set_xticks(x)
ax.set_xticklabels([m_[1] for m_ in metrics], fontsize=6.3)
ax.set_ylabel("fraction of predictions (n = 247 per set)")
ax.set_ylim(0, 0.58)
hgrid(ax, "y")
ax.legend(loc="upper right", fontsize=6.2, ncol=1)
ax.text(x[1], -0.17, "Tier-A support condition", fontsize=6.2, color=INK2, ha="center",
        transform=ax.get_xaxis_transform())
ax.text((x[3] + x[6]) / 2, -0.17, "individual class supports", fontsize=6.2, color=INK2, ha="center",
        transform=ax.get_xaxis_transform())

# ---- d: family composition by support category
ax = fig.add_subplot(gs[1, 1])
letter(ax, "d", x=-0.42)
pred = PU[b(PU.has_prediction)]
FC = pd.crosstab(pred.family, pred.support_category).reindex(columns=["in_support", "upper_bound", "no_pcal"],
                                                             fill_value=0)
nH = __import__("json").loads((HE / "calibration_results.json").read_text())["family_counts"]
FC["n_H_genes"] = [nH.get(f, 0) for f in FC.index]
FC["total"] = FC[["in_support", "upper_bound", "no_pcal"]].sum(axis=1)
FC = FC.sort_values("total", ascending=True)
FC.to_csv(SD / "Fig3d_family_support_category.tsv", sep="\t")
yv = np.arange(len(FC))
left = np.zeros(len(FC))
for cat, col_, labl in (("in_support", S3, "p_cal (in support)"), ("upper_bound", S4, "upper bound only"),
                        ("no_pcal", LIGHT, "no p_cal (out of support)")):
    ax.barh(yv, FC[cat], left=left, height=0.66, color=col_, edgecolor="white", lw=0.6, zorder=2, label=labl)
    left += FC[cat].values
for yi, (f, r) in zip(yv, FC.iterrows()):
    ax.text(r.total + 40, yi, f"{int(r.total):,}  (H: {int(r.n_H_genes)})", va="center", fontsize=6.0, color=INK2)
ax.set_yticks(yv)
ax.set_yticklabels([FAM_LABEL[f] for f in FC.index], fontsize=6.6)
ax.set_xlabel("U genes with a top term, by module family")
ax.set_xlim(0, 3900)
hgrid(ax)
ax.legend(loc="lower right", fontsize=6.0)
save(fig, "Fig3")

# ====================================================================== FIGURE 4
T = TP.copy()
T["lineage_fail"] = ~b(T.leaveout_retained)
T["d2_meas"] = b(T.d2_measured)
T["d2_fl"] = b(T.d2_flag)
T["tp53_fl"] = T.demotion_reason.fillna("").str.contains("TP53")
T["classes"] = T.supporting_classes.fillna("")
T["diag"] = b(T.diag_support)
T["lowcov"] = b(T.low_coverage)
T[["rank", "symbol", "top_term", "top_term_name", "family", "p_cal", "zmean", "R", "cov_pct", "lineage_fail",
   "d2_meas", "d2_fl", "tp53_fl", "classes", "diag", "lowcov", "demotion_reason"]].to_csv(
    SD / "Fig4_top40_primary.tsv", sep="\t", index=False)
derived("top40_n_any_top40_check_fail", int(b(T.demoted).sum()), "primary top 40 genes failing >= 1 top-40-only check",
        "results/ledger/top40_primary.tsv")
derived("top40_n_lineage_fail", int(T.lineage_fail.sum()), "lineage leave-out changes top term",
        "results/ledger/top40_primary.tsv")
derived("top40_n_d2_measured", int(T.d2_meas.sum()), "DEMETER2 measured", "results/ledger/top40_primary.tsv")
derived("top40_n_d2_flag", int(T.d2_fl.sum()), "DEMETER2 not replicated", "results/ledger/top40_primary.tsv")
derived("top40_n_tp53_flag", int(T.tp53_fl.sum()), "TP53 flag", "results/ledger/top40_primary.tsv")
derived("top40_n_any_class_support", int((T.classes != "").sum()), ">= 1 orthogonal class supports",
        "results/ledger/top40_primary.tsv")
derived("top40_n_diag_support", int(T.diag.sum()), "diagnostic-class support", "results/ledger/top40_primary.tsv")
derived("top40_family_counts", "; ".join(f"{k} {v}" for k, v in T.family.value_counts().items()),
        "module family of the V2 top term", "results/ledger/top40_primary.tsv")
derived("top40_pcal_range", f"{T.p_cal.min():.3f}-{T.p_cal.max():.3f}", "p_cal range", "results/ledger/top40_primary.tsv")
derived("top40_n_unflagged", int((~b(T.demoted)).sum()), "no top-40-only check failure",
        "results/ledger/top40_primary.tsv")
derived("top40_n_lowcov", int(T.lowcov.sum()), "low_coverage genes", "results/ledger/top40_primary.tsv")
TA = tsv(LG / "tiers_all.tsv")
pool = TA[b(TA.has_prediction) & b(TA.expressed_design) & b(TA.assessable_design) & (TA.support_category == "in_support")]
derived("top40_pool_n", len(pool), "fill pool: expressed, assessable, in-support U genes with a prediction",
        "results/ledger/tiers_all.tsv")
derived("top40_pool_excluded", f"{int((b(pool.excl43) | b(pool.contradiction)).sum())} (artefact exclusion "
        f"{int(b(pool.excl43).sum())}, contradiction {int(b(pool.contradiction).sum())})",
        "pool genes removed by section 4.3 exclusion or contradiction", "results/ledger/tiers_all.tsv")
derived("top40_pool_families", "; ".join(f"{k} {v}" for k, v in pool.family.value_counts().items()),
        "module families in the fill pool (mito cap cannot bind)", "results/ledger/tiers_all.tsv")
CF = tsv(LG / "top40.tsv")
derived("top40_overlap_primary_vs_cleanfirst", len(set(CF.symbol) & set(T.symbol)),
        "genes shared by the primary (p_cal order) and clean-first sensitivity top 40",
        "results/ledger/top40_primary.tsv; results/ledger/top40.tsv")
derived("top40_term_counts", "; ".join(f"{k} {v}" for k, v in T.top_term_name.value_counts().head(6).items()),
        "most frequent V2 top terms", "results/ledger/top40_primary.tsv")

fig = plt.figure(figsize=(W2, 175 * MM))
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.04)
ax = fig.add_subplot(gs[0, 0])
letter(ax, "a", x=-0.62, y=1.005)
yv = -np.arange(len(T))
fcol = {"other": S1, "ER_Golgi_secretory_lipid": S2}
ax.barh(yv, T.p_cal, height=0.7, color=[fcol.get(f, MUTED) for f in T.family], zorder=2)


def short(s, n=46):
    return s if len(s) <= n else s[: n - 1] + "…"


ax.set_yticks(yv)
ax.set_yticklabels([f"{r.symbol}  ·  {short(r.top_term_name)}" for r in T.itertuples()], fontsize=6.3)
for t_ in ax.get_yticklabels():
    t_.set_fontfamily("Arial")
ax.set_ylim(yv[-1] - 0.7, 0.7)
ax.set_xlim(0, 0.16)
ax.set_xlabel("p_cal (probability the V2 top term is later confirmed)")
hgrid(ax)
from matplotlib.patches import Patch  # noqa: E402

ax.legend(handles=[Patch(color=S1, label="other"), Patch(color=S2, label="ER/Golgi/secretory/lipid")],
          title="module family of top term", title_fontsize=6.3, loc="lower right", fontsize=6.3)
ax.xaxis.set_ticks_position("bottom")
# check matrix
ax2 = fig.add_subplot(gs[0, 1], sharey=ax)
letter(ax2, "b", x=-0.04, y=1.045)
cols_ = ["lineage\nleave-out", "DEMETER2\n(RNAi)", "TP53\nstatus", "orthogonal\nclasses", "diagnostic\nsupport"]
XC = [0, 1.35, 2.6, 3.9, 5.3]
for j, c in zip(XC, cols_):
    ax2.text(j, 0.9, c, ha="center", va="bottom", fontsize=6.0, fontweight="bold")
for yi, r in zip(yv, T.itertuples()):
    marks = ["×" if r.lineage_fail else "·",
             ("×" if r.d2_fl else "·") if r.d2_meas else "–",
             "×" if r.tp53_fl else "·"]
    for j, mk in zip(XC, marks):
        ax2.text(j, yi, mk, ha="center", va="center", fontsize=8 if mk == "×" else 7,
                 color=INK if mk == "×" else MUTED, fontweight="bold" if mk == "×" else "normal")
    ax2.text(XC[3], yi, r.classes if r.classes else "–", ha="center", va="center", fontsize=6.3,
             color=INK if r.classes else MUTED)
    ax2.text(XC[4], yi, "yes" if r.diag else "–", ha="center", va="center", fontsize=6.3,
             color=INK if r.diag else MUTED)
for yi in yv[::2]:
    ax2.axhspan(yi - 0.5, yi + 0.5, color="#f4f3f0", zorder=0, lw=0)
ax2.set_xlim(-0.7, 6.0)
ax2.axis("off")
ax2.text(-0.6, yv[-1] - 1.6, "× check failed (would cap at Tier B; inert without tiers)\n· passed   – not measured / none\n"
         "classes: P physical, A co-abundance, L localisation,\nG Perturb-seq",
         fontsize=6.0, color=INK2, va="top")
save(fig, "Fig4")

# ====================================================================== FIGURE S1 (LOO rankers, label shuffle)
LR = tsv(R / "calibration/loo_ranker_choice.tsv")
LS = tsv(R / "calibration/label_shuffle.tsv")
prim = LR[LR.analysis.str.startswith("primary")].copy()


def ci(s):
    a_, b_ = str(s).split("-")
    return float(a_), float(b_)


prim[["mrr_lo", "mrr_hi"]] = prim.MRR_ci_gene.apply(lambda s: pd.Series(ci(s)))
prim[["p1_lo", "p1_hi"]] = prim.p1_ci_gene.apply(lambda s: pd.Series(ci(s)))
prim.to_csv(SD / "FigS1a_loo_rankers.tsv", sep="\t", index=False)
LS.to_csv(SD / "FigS1b_label_shuffle.tsv", sep="\t", index=False)
fig, axs = plt.subplots(1, 2, figsize=(W2 * 0.8, 62 * MM), gridspec_kw={"wspace": 0.45})
ax = axs[0]
letter(ax, "a", x=-0.2)
x = np.arange(len(prim))
ax.vlines(x - 0.12, prim.mrr_lo, prim.mrr_hi, color=S1, lw=1.2)
ax.plot(x - 0.12, prim.MRR, "o", color=S1, ms=4.5, mec="white", mew=0.5, label="MRR")
ax.vlines(x + 0.12, prim.p1_lo, prim.p1_hi, color=S2, lw=1.2)
ax.plot(x + 0.12, prim.precision_at_1, "s", color=S2, ms=4, mec="white", mew=0.5, label="precision@1")
ax.set_xticks(x)
ax.set_xticklabels(["R1 (chosen)", "R2", "R3", "prior-only"])
ax.set_ylabel("value on LOO (n = 2,519 genes)")
ax.set_ylim(0, 0.2)
hgrid(ax, "y")
ax.legend(loc="upper right")
ax = axs[1]
letter(ax, "b", x=-0.2)
rk = ["R1", "R2", "R3", "prior"]
real_p1 = prim.set_index("ranker").precision_at_1
s0 = LS[LS.seed == 0].set_index("ranker")
x = np.arange(4)
ax.bar(x - 0.18, [real_p1[k] for k in rk], width=0.34, color=S1, label="real labels", zorder=2)
ax.bar(x + 0.18, [s0.loc[k, "precision_at_1"] for k in rk], width=0.34, color=LIGHT, label="shuffled labels (seed 0)",
       zorder=2)
for k_, xi in zip(rk, x):
    oth = LS[(LS.seed != 0) & (LS.ranker == k_)].precision_at_1
    ax.plot([xi + 0.18] * len(oth), oth, "_", color=INK, ms=6, mew=0.8)
    lo, hi = ci(s0.loc[k_, "p1_ci"])
    ax.vlines(xi + 0.18, lo, hi, color=INK, lw=0.7)
ax.set_xticks(x)
ax.set_xticklabels(["R1", "R2", "R3", "prior-only"])
ax.set_ylabel("precision@1 (LOO)")
hgrid(ax, "y")
ax.legend(loc="upper right", fontsize=6.2)
ax.text(0.98, 0.62, "ticks: shuffle seeds 1–4", transform=ax.transAxes, ha="right", fontsize=6, color=MUTED)
save(fig, "FigS1")

# ====================================================================== FIGURE S2 (split-half R)
RA = tsv(R / "assessability/R_all.tsv")
RA = RA[b(RA.scorable)]
fig, axs = plt.subplots(1, 3, figsize=(W2, 60 * MM), gridspec_kw={"wspace": 0.95, "width_ratios": [1, 0.9, 1]})
ax = axs[0]
letter(ax, "a", x=-0.22)
grp = [("U", b(RA.in_U), S1), ("H", b(RA.in_H), S2), ("LOO sample", b(RA.in_LOO), INK2),
       ("other scorable", ~b(RA.in_U) & ~b(RA.in_H) & ~b(RA.in_LOO), LIGHT)]
rows = []
for labl, mask, col_ in grp:
    v = np.sort(RA.loc[mask, "R"].values)
    ax.step(v, 1 - np.arange(len(v)) / len(v), where="post", color=col_, lw=1.3, label=f"{labl} (n = {len(v):,})")
    rows.append({"set": labl, "n": len(v), "mean_R": v.mean(), "frac_R0": (v == 0).mean(), "frac_ge_0.2": (v >= 0.2).mean(),
                 "frac_ge_0.5": (v >= 0.5).mean()})
pd.DataFrame(rows).to_csv(SD / "FigS2a_R_by_set.tsv", sep="\t", index=False)
ax.set_xlabel("split-half reproducibility R(g)")
ax.set_ylabel("fraction of genes with R ≥ x")
ax.set_ylim(0, 0.6)
hgrid(ax, "y")
ax.legend(fontsize=5.8, loc="upper right", bbox_to_anchor=(1.08, 1.02))
ax = axs[1]
letter(ax, "b", x=-0.22)
AUs = AU[AU.scor].copy()
AUs["pl"] = b(AUs.p_lt_alpha)
sets_ = [("expressed", AUs.expr_d), ("not expressed", ~AUs.expr_d), ("clean negative", b(AUs.clean_negative)),
         ("clean neg., any dependency", b(AUs.clean_negative) & b(AUs.any_dependency)),
         ("clean neg., no dependency", b(AUs.clean_negative) & (AUs.any_dependency.astype(str).str.lower() == "false"))]
rows = []
for labl, mask in sets_:
    k, n = int((AUs.pl & mask).sum()), int(mask.sum())
    lo, hi = wilson(k, n)
    rows.append({"set": labl, "k_p_lt_0.05": k, "n": n, "rate": k / n, "wilson_lo": lo, "wilson_hi": hi})
PL = pd.DataFrame(rows)
PL.to_csv(SD / "FigS2b_reproducibility_rate.tsv", sep="\t", index=False)
yv = -np.arange(len(PL))
ax.barh(yv, PL.rate, color=[S1, MUTED, S7, S7, S7], height=0.62, zorder=2)
ax.hlines(yv, PL.wilson_lo, PL.wilson_hi, color=INK, lw=0.7, zorder=3)
for yi, r in zip(yv, PL.itertuples()):
    ax.text(r.wilson_hi + 0.01, yi, f"{r._2:,}/{r.n:,}", va="center", fontsize=6)
ax.set_yticks(yv)
ax.set_yticklabels(PL.set, fontsize=6.5)
ax.axvline(0.05, color=INK2, lw=0.7, ls="--")
ax.set_xlim(0, 0.42)
ax.set_xlabel("fraction with split-half p < 0.05 (scorable U)")
hgrid(ax)
ax = axs[2]
letter(ax, "c", x=-0.22)
SH = tsv(HE / "splithalf.tsv")
SH.to_csv(SD / "FigS2c_splithalf_networks.tsv", sep="\t", index=False)
x = np.arange(len(SH))
ax.vlines(x, SH.p1_ci_lo, SH.p1_ci_hi, color=S2, lw=1.1)
ax.plot(x, SH.p1_zavg, "o", color=S2, ms=4, mec="white", mew=0.5, label="zavg_BEF (half network)")
ax.plot(x, SH.p1_null, "_", color=INK2, ms=6, mew=1, label="matched null")
ax.axhline(PM.set_index("method").loc["zavg_BEF (R1)", "p1"], color=S2, lw=0.7, ls="--", label="full network")
ax.set_xticks(x)
ax.set_xticklabels([f"{s}/{h}" for s, h in zip(SH.seed, SH.half)], fontsize=6, rotation=90)
ax.set_xlabel("split (seed/half)")
ax.set_ylabel("precision@1 on H")
ax.set_ylim(0, 0.075)
hgrid(ax, "y")
ax.legend(fontsize=5.8, loc="upper right", bbox_to_anchor=(1.08, 1.02))
save(fig, "FigS2")

# ====================================================================== FIGURE S3 (orthogonal admission)
AD = tsv(R / "orthogonal/admission.tsv")
pairs = AD[AD.kind != "localisation"].copy() if "kind" in AD else AD
pairs = AD[AD.OR.notna()].copy()
loc = AD[AD.agreement.notna()].copy()
pairs.to_csv(SD / "FigS3a_pair_admission.tsv", sep="\t", index=False)
loc.to_csv(SD / "FigS3b_localisation_admission.tsv", sep="\t", index=False)
fig, axs = plt.subplots(1, 2, figsize=(W2, 68 * MM), gridspec_kw={"wspace": 0.75, "width_ratios": [1.4, 1]})
ax = axs[0]
letter(ax, "a", x=-0.38)
pairs = pairs.sort_values("OR")
yv = np.arange(len(pairs))
for yi, r in zip(yv, pairs.itertuples()):
    adm = str(r.admitted).lower() == "true"
    col_ = MUTED if r.cls == "NI" else (S1 if adm else S8)
    ax.plot([r.CI_lo, r.CI_hi], [yi, yi], color=col_, lw=1.3)
    ax.plot(r.OR, yi, "o" if adm else "D", color=col_, ms=4, mec="white", mew=0.5)
ax.set_xscale("log")
ax.set_xticks([1, 2, 5, 10, 20, 50, 100])
ax.set_xticklabels(["1", "2", "5", "10", "20", "50", "100"])
ax.axvline(2, color=INK2, ls="--", lw=0.7)
ax.text(2.1, len(pairs) - 0.4, "admission: lower CI > 2", fontsize=6, color=INK2)
ax.set_yticks(yv)
ax.set_yticklabels([f"{s} ({c})" + (" — not independent" if c == "NI" else "") for s, c in
                    zip(pairs.source, pairs.cls)], fontsize=6.3)
ax.set_xlabel("co-complex odds ratio (95% CI, bootstrap over complexes)")
hgrid(ax)
ax = axs[1]
letter(ax, "b", x=-0.45)
yv = np.arange(len(loc))
for yi, r in zip(yv, loc.itertuples()):
    lo, hi = wilson(int(r.H_agree), int(r.H_genes_evaluated))
    adm = str(r.admitted).lower() == "true"
    col_ = S1 if adm else S8
    ax.plot([lo, hi], [yi, yi], color=col_, lw=1.3)
    ax.plot(r.agreement, yi, "o" if adm else "D", color=col_, ms=4, mec="white", mew=0.5)
    ax.text(1.0, yi, f"n = {int(r.H_genes_evaluated)} H genes", fontsize=6, va="center", color=INK2)
ax.axvline(0.6, color=INK2, ls="--", lw=0.7)
ax.set_xlim(0.5, 1.0)
ax.set_yticks(yv)
ax.set_yticklabels(loc.source, fontsize=6.5)
ax.set_xlabel("agreement with GO CC on H (Wilson 95% CI)")
hgrid(ax)
ax.text(0.5, -0.32, "admission: lower CI > 0.6 and ≥ 200 H genes; red = not admitted", transform=ax.transAxes,
        fontsize=6, color=INK2, ha="center")
save(fig, "FigS3")

pd.DataFrame(DERIVED).to_csv(SD / "derived_numbers.tsv", sep="\t", index=False)
print("derived numbers:", len(DERIVED))
