#!/usr/bin/env python
"""61_figure5.py -- Figure 5 and Table 2 for claim C4 (literature novelty and blinded judging; no new judging).

Reads committed M7 results only: results/m7/judge/analysis_{main,hval}{.md,_genes.tsv}, results/m7/answer_key_slots.tsv,
results/m7/{s20,extra30}.tsv, results/m7/recall_probe_90.tsv, results/m7/L/index_batch_*.tsv,
results/ledger/top40_primary.tsv, results/audit/{recall_probe_random50,curation_lag_audit}.tsv.

Writes manuscript/figures/Fig5.png (300 dpi) and Fig5.svg, one source-data TSV per panel, Table2_rediscovery.tsv and
Fig5_derived_numbers.tsv (descriptive numbers computed here, not pre-specified; the primary sign-flip p is recomputed
exactly and checked against results/m7/judge/analysis_main.md).

Panels: (a) blinded judging per set: real-statement outcome (+1/0/-1) and decoy support rate, with exact one-sided
sign-flip p; (b) literature support of the real statement vs p_cal (extra30 p_cal quintile bins + primary top 40 in two
halves), Wilson 95% CIs; (c) novelty class (N1/N2/N3) composition per set, and support within class; (d) closed-book
recall-probe "recognised" rate by literature class (random 50 audit genes, auditor classes; 90 candidates, agent-L classes).

Run: ./.env/bin/python -I scripts/61_figure5.py
"""
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import fisher_exact  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
M7 = R / "m7"
FIG = ROOT / "manuscript/figures"
SD = FIG / "source_data"
SD.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- style (copied from scripts/60_figures.py)
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
C4 = S7  # accent for C4 (C1 = S1, C2 = S2, C3 = S3 in Figs 1-4)
SUP, UNADDR, CONTRA = C4, "#d9d6f3", S8
DERIVED = []


def derived(key, value, note, source):
    DERIVED.append({"key": key, "value": value, "note": note, "inputs": source})


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


def hgrid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def tsv(path, **kw):
    return pd.read_csv(path, sep="\t", **kw)


def signflip_exact(d):
    """Exact one-sided sign-flip p over genes with d != 0 (d in multiples of 1/3 -> integer DP)."""
    v = [int(round(abs(x) * 3)) for x in d if abs(x) > 1e-12]
    obs = int(round(sum(x * 3 for x in d)))
    dist = Counter({0: 1})
    for a in v:
        nxt = Counter()
        for s, c in dist.items():
            nxt[s + a] += c
            nxt[s - a] += c
        dist = nxt
    return sum(c for s, c in dist.items() if s >= obs) / 2 ** len(v), len(v)


# ---------------------------------------------------------------- data
G = pd.concat([tsv(M7 / "judge/analysis_main_genes.tsv"), tsv(M7 / "judge/analysis_hval_genes.tsv")],
              ignore_index=True)
LIDX = pd.concat([tsv(f, header=None, names=["hgnc_id", "symbol", "L_class", "n_items", "n_functional",
                                              "n_depmap_derived"]) for f in sorted(M7.glob("L/index_batch_*.tsv"))])
G = G.merge(LIDX[["hgnc_id", "L_class", "n_items", "n_functional", "n_depmap_derived"]], on="hgnc_id", how="left")
assert (G.nclass == G.L_class).all(), "novelty class mismatch between judge analysis and L index"
KEY = tsv(M7 / "answer_key_slots.tsv")
REAL = KEY[KEY.is_real.astype(str) == "True"][["hgnc_id", "term", "term_name", "label", "label_name", "family"]]
G = G.merge(REAL, on="hgnc_id", how="left")
T40 = tsv(R / "ledger/top40_primary.tsv")
X30 = tsv(M7 / "extra30.tsv")
S20 = tsv(M7 / "s20.tsv")
pcal = pd.concat([T40[["hgnc_id", "p_cal"]], X30[["hgnc_id", "p_cal"]]])
G = G.merge(pcal, on="hgnc_id", how="left").merge(
    S20[["hgnc_id", "zmean", "support_reason"]], on="hgnc_id", how="left")
RP90 = tsv(M7 / "recall_probe_90.tsv")
G = G.merge(RP90[["hgnc_id", "recognised", "confidence"]], on="hgnc_id", how="left")

main_md = (M7 / "judge/analysis_main.md").read_text()
hval_md = (M7 / "judge/analysis_hval.md").read_text()
kappa_main = float(re.search(r"kappa = ([0-9.]+) over (\d+)", main_md).group(1))
kappa_hval = float(re.search(r"kappa = ([0-9.]+) over (\d+)", hval_md).group(1))

SETS = [("hval10", "H validation\n(10 genes)"), ("top40", "primary top 40"), ("s20", "S20\n(secondary)"),
        ("extra30", "extra30\n(secondary)")]
rows = []
for s, lab in SETS:
    g = G[G.set == s]
    n = len(g)
    p, nnz = signflip_exact(g.d.values)
    k_dec = int(g.n_decoy_supported.sum())
    lo, hi = wilson(k_dec, 3 * n)
    rows.append({"set": s, "n_genes": n, "real_supported": int((g.real == 1).sum()),
                 "real_unaddressed": int((g.real == 0).sum()), "real_contradicted": int((g.real == -1).sum()),
                 "decoys_supported": k_dec, "n_decoys": 3 * n, "decoy_support_rate": k_dec / (3 * n),
                 "decoy_wilson_lo": lo, "decoy_wilson_hi": hi, "mean_d": g.d.mean(),
                 "signflip_p_one_sided": p if s != "hval10" else np.nan, "n_nonzero_d": nnz,
                 "role": {"top40": "primary (pre-specified)", "hval10": "judge validation (pre-specified)",
                          "extra30": "secondary (pre-specified)", "s20": "secondary (deviation: post hoc list)"}[s]})
A = pd.DataFrame(rows)
A.to_csv(SD / "Fig5a_judging_by_set.tsv", sep="\t", index=False)
p_primary = A.set_index("set").loc["top40", "signflip_p_one_sided"]
p_md = float(re.search(r"top40.*?sign-flip p = ([0-9.e-]+)", main_md, re.S).group(1))
assert abs(p_primary - p_md) / p_md < 1e-3, (p_primary, p_md)
for r in A.itertuples():
    derived(f"{r.set}_real_supported", f"{r.real_supported}/{r.n_genes}",
            "real statement adjudicated +1", "results/m7/judge/analysis_*_genes.tsv")
    lo, hi = wilson(r.real_supported, r.n_genes)
    derived(f"{r.set}_real_supported_wilson", f"{r.real_supported / r.n_genes:.3f} ({lo:.3f}-{hi:.3f})",
            "Wilson 95% CI (descriptive)", "results/m7/judge/analysis_*_genes.tsv")
    derived(f"{r.set}_decoy_supported", f"{r.decoys_supported}/{r.n_decoys} ({r.decoy_support_rate:.3f}; "
            f"{r.decoy_wilson_lo:.3f}-{r.decoy_wilson_hi:.3f})", "decoys adjudicated +1, Wilson CI (decoys nested "
            "in genes; descriptive)", "results/m7/judge/analysis_*_genes.tsv")
    if r.set != "hval10":
        derived(f"{r.set}_signflip_p", f"{r.signflip_p_one_sided:.3g} (n non-zero {r.n_nonzero_d})",
                "exact one-sided sign-flip, recomputed by integer DP", "results/m7/judge/analysis_main_genes.tsv")

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(W2, 150 * MM))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1.15, 1], hspace=0.62, wspace=0.32)

# ---- a: blinded judging per set
ax = fig.add_subplot(gs[0, 0])
letter(ax, "a", x=-0.13)
x = np.arange(len(A)) * 1.25
w = 0.5
f_sup = A.real_supported / A.n_genes
f_un = A.real_unaddressed / A.n_genes
f_con = A.real_contradicted / A.n_genes
ax.bar(x, f_sup, width=w, color=SUP, zorder=2, label="real: supported (+1)")
ax.bar(x, f_un, bottom=f_sup, width=w, color=UNADDR, zorder=2, label="real: unaddressed (0)")
ax.bar(x, f_con, bottom=f_sup + f_un, width=w, color=CONTRA, zorder=2, label="real: contradicted (−1)")
ax.bar(x + 0.42, A.decoy_support_rate, width=0.26, color=MUTED, zorder=2, label="decoys: supported")
ax.errorbar(x + 0.42, A.decoy_support_rate, yerr=[A.decoy_support_rate - A.decoy_wilson_lo,
                                                  A.decoy_wilson_hi - A.decoy_support_rate],
            fmt="none", ecolor=INK2, elinewidth=0.7, capsize=1.8, zorder=3)
for xi, r in zip(x, A.itertuples()):
    fs = f_sup[r.Index]
    ax.text(xi, fs / 2 if fs > 0.15 else fs + 0.03, f"{r.real_supported}/{r.n_genes}", ha="center",
            va="center" if fs > 0.15 else "bottom", fontsize=6.3, color="white" if fs > 0.15 else INK,
            fontweight="bold")
    ax.text(xi + 0.42, r.decoy_wilson_hi + 0.025, f"{r.decoys_supported}/{r.n_decoys}", ha="center", fontsize=5.6,
            color=INK2, rotation=90, va="bottom")
    if r.set == "hval10":
        txt = "PASSED\n(≥ 7/10, ≤ 3/30)"
    else:
        pv = r.signflip_p_one_sided
        txt = f"p = {pv:.1g}" if pv < 0.01 else f"p = {pv:.2g}"
        if r.set == "top40":
            txt = "primary\n" + txt.replace("2e-04", "0.0002")
    ax.text(xi + 0.15, 1.04, txt, ha="center", va="bottom", fontsize=6.1,
            fontweight="bold" if r.set == "top40" else "normal", color=INK if r.set == "top40" else INK2)
ax.set_xticks(x + 0.15)
ax.set_xticklabels([lab for _, lab in SETS], fontsize=6.4)
ax.set_ylim(0, 1.0)
ax.set_ylabel("fraction of statements")
ax.set_xlim(-0.45, x[-1] + 0.8)
hgrid(ax)
ax.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.2), fontsize=6.0, handlelength=1.0, ncol=4,
          columnspacing=0.9)
ax.set_title("Blinded judging: real vs 3 decoys per gene", loc="left", fontsize=8, pad=22)
ax.text(0.0, -0.36, f"exact one-sided sign-flip on real − mean(decoys); κ = {kappa_main:.3f} (main), "
        f"{kappa_hval:.3f} (validation)", transform=ax.transAxes, fontsize=5.8, color=MUTED)

# ---- b: literature support vs p_cal
ax = fig.add_subplot(gs[0, 1])
letter(ax, "b", x=-0.2)
brows = []
for b_, sub in X30.groupby("bin"):
    gg = G[G.hgnc_id.isin(sub.hgnc_id)]
    brows.append({"set": "extra30", "bin": f"Q{b_ + 1}", "pcal_min": sub.bin_pcal_min.iloc[0],
                  "pcal_max": sub.bin_pcal_max.iloc[0], "n": len(gg), "supported": int((gg.real == 1).sum()),
                  "mean_pcal": gg.p_cal.mean(), "n_N1": int((gg.nclass == "N1").sum())})
for lab, rk in (("top 40, ranks 21–40", (21, 40)), ("top 40, ranks 1–20", (1, 20))):
    gg = G[(G.set == "top40") & G["rank"].between(*rk)]
    brows.append({"set": "top40", "bin": lab, "pcal_min": gg.p_cal.min(), "pcal_max": gg.p_cal.max(), "n": len(gg),
                  "supported": int((gg.real == 1).sum()), "mean_pcal": gg.p_cal.mean(),
                  "n_N1": int((gg.nclass == "N1").sum())})
B = pd.DataFrame(brows)
B["frac"] = B.supported / B.n
B[["wilson_lo", "wilson_hi"]] = [wilson(k, n) for k, n in zip(B.supported, B.n)]
B.to_csv(SD / "Fig5b_support_vs_pcal.tsv", sep="\t", index=False)
xb = np.arange(len(B)) + np.where(B.set == "top40", 0.5, 0)
for xi, r in zip(xb, B.itertuples()):
    col = C4 if r.set == "top40" else INK2
    ax.vlines(xi, r.wilson_lo, r.wilson_hi, color=col, lw=1.3, zorder=3)
    ax.plot(xi, r.frac, "o", ms=4.8, color=col, mec="white", mew=0.6, zorder=4)
    ax.text(xi, r.wilson_hi + 0.03, f"{r.supported}/{r.n}", ha="center", fontsize=6.0, color=INK2)
ax.plot(xb, B.mean_pcal, "D", ms=2.8, color=MUTED, zorder=3, label="mean p_cal of bin")
ax.set_xticks(xb)
ax.set_xticklabels([f"{r.pcal_min:.3f}–\n{r.pcal_max:.3f}" if r.pcal_min > 1e-4 else f"<{r.pcal_max:.3f}"
                    for r in B.itertuples()], fontsize=5.6)
ax.set_xlabel("p_cal range of bin", labelpad=2)
ax.set_ylabel("real statement supported (Wilson 95% CI)")
ax.set_ylim(-0.02, 1.0)
hgrid(ax)
ax.text(np.mean(xb[:5]), 0.93, "extra30 (p_cal quintiles of the\nfill pool outside the top 40)", ha="center",
        fontsize=6.0, color=INK2)
ax.text(np.mean(xb[5:]), 0.93, "primary top 40", ha="center", fontsize=6.0, color=C4, fontweight="bold")
ax.axvline(np.mean(xb[4:6]), color=GRID, lw=0.6)
ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.62), fontsize=5.9, handletextpad=0.3)
ax.set_title("Literature support tracks p_cal", loc="left", fontsize=8)

# ---- c: novelty class composition and support within class
gsc = gs[1, 0].subgridspec(1, 2, width_ratios=[1.05, 1], wspace=0.55)
ax = fig.add_subplot(gsc[0, 0])
letter(ax, "c", x=-0.42, y=1.06)
AUD = tsv(R / "audit/curation_lag_audit.tsv")
crow = []
for s, lab in (("random50", "random 50 U\n(audit)"), ("top40", "top 40"), ("s20", "S20"), ("extra30", "extra30"),
               ("hval10", "H validation")):
    cls = AUD["class"] if s == "random50" else G.loc[G.set == s, "nclass"]
    n = len(cls)
    for c in ("N1", "N2", "N3"):
        k = int((cls == c).sum())
        g = G[(G.set == s) & (G.nclass == c)]
        ksup = int((g.real == 1).sum()) if s != "random50" else np.nan
        lo, hi = wilson(ksup, len(g)) if s != "random50" and len(g) else (np.nan, np.nan)
        crow.append({"set": s, "label": lab, "class": c, "n_class": k, "n_set": n, "frac": k / n,
                     "real_supported": ksup, "support_frac": ksup / len(g) if len(g) else np.nan,
                     "support_wilson_lo": lo, "support_wilson_hi": hi,
                     "classifier": "curation-lag auditor" if s == "random50" else "agent L"})
C = pd.DataFrame(crow)
C.to_csv(SD / "Fig5c_novelty_class.tsv", sep="\t", index=False)
labs = C.drop_duplicates("set")[["set", "label"]].reset_index(drop=True)
yc = -np.arange(len(labs), dtype=float)
yc[1:] -= 0.35
ccol = {"N1": C4, "N2": "#a79de8", "N3": UNADDR}
for yi, s in zip(yc, labs.set):
    left = 0
    for c in ("N1", "N2", "N3"):
        r = C[(C.set == s) & (C["class"] == c)].iloc[0]
        ax.barh(yi, r.frac, left=left, height=0.62, color=ccol[c], zorder=2,
                label=c if s == "random50" else None)
        if r.n_class:
            ax.text(left + r.frac / 2, yi, str(r.n_class), ha="center", va="center", fontsize=5.9,
                    color="white" if c == "N1" else INK)
        left += r.frac
ax.set_yticks(yc)
ax.set_yticklabels(labs.label, fontsize=6.3)
ax.set_xlim(0, 1)
ax.set_xlabel("fraction of genes")
hgrid(ax, "x")
ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, fontsize=6.0, handlelength=1.0, columnspacing=0.8)
ax.set_title("Literature class", loc="left", fontsize=8, pad=14)

ax = fig.add_subplot(gsc[0, 1])
off = {"top40": -0.22, "s20": 0.0, "extra30": 0.22}
scol = {"top40": C4, "s20": INK2, "extra30": MUTED}
for s in ("top40", "s20", "extra30"):
    for i, c in enumerate(("N1", "N2", "N3")):
        r = C[(C.set == s) & (C["class"] == c)].iloc[0]
        if r.n_class == 0:
            continue
        xi = i + off[s]
        ax.vlines(xi, r.support_wilson_lo, r.support_wilson_hi, color=scol[s], lw=1.1, zorder=3)
        ax.plot(xi, r.support_frac, "o", ms=4.0, color=scol[s], mec="white", mew=0.5, zorder=4,
                label={"top40": "top 40", "s20": "S20", "extra30": "extra30"}[s] if i == 0 else None)
        ax.text(xi, -0.1, f"{int(r.real_supported)}/{r.n_class}", ha="center", fontsize=5.0, color=scol[s],
                rotation=90, va="top")
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["N1", "N2", "N3"])
ax.set_ylim(-0.32, 1.05)
ax.set_yticks([0, 0.5, 1])
ax.set_ylabel("real statement supported")
hgrid(ax)
ax.legend(loc="upper right", fontsize=5.8, handletextpad=0.2, borderaxespad=0.1)
ax.set_title("Support within class", loc="left", fontsize=8, pad=14)

# ---- d: recall probe vs literature class
ax = fig.add_subplot(gs[1, 1])
letter(ax, "d", x=-0.2, y=1.06)
RP50 = tsv(R / "audit/recall_probe_random50.tsv").merge(AUD[["hgnc_id", "class"]], on="hgnc_id")
cand = G[G.set.isin(["top40", "s20", "extra30"])]
assert len(cand) == 90 and cand.recognised.notna().all()
drow = []
for grp, df, ccl in (("random 50 U genes (auditor class)", RP50, "class"),
                     ("90 candidates (agent-L class)", cand, "nclass")):
    for c in ("N1", "N2", "N3"):
        sub = df[df[ccl] == c]
        k, n = int((sub.recognised == "yes").sum()), len(sub)
        lo, hi = wilson(k, n)
        drow.append({"group": grp, "class": c, "recognised": k, "n": n, "frac": k / n if n else np.nan,
                     "wilson_lo": lo, "wilson_hi": hi})
    k, n = int((df.recognised == "yes").sum()), len(df)
    derived(f"recall_probe_{grp.split()[0]}_{grp.split()[1]}", f"{k}/{n}", "recognised by closed-book probe",
            "results/audit/recall_probe_random50.tsv; results/m7/recall_probe_90.tsv")
D = pd.DataFrame(drow)
D.to_csv(SD / "Fig5d_recall_probe.tsv", sep="\t", index=False)
for grp, o, col in (("random 50 U genes (auditor class)", -0.15, MUTED), ("90 candidates (agent-L class)", 0.15, C4)):
    s = D[D.group == grp].reset_index(drop=True)
    xi = np.arange(3) + o
    ax.bar(xi, s.frac, width=0.28, color=col, alpha=0.85, zorder=2, label=grp)
    ax.errorbar(xi, s.frac, yerr=[s.frac - s.wilson_lo, s.wilson_hi - s.frac], fmt="none", ecolor=INK,
                elinewidth=0.7, capsize=2, zorder=3)
    for xx, r in zip(xi, s.itertuples()):
        ax.text(xx, r.wilson_hi + 0.03, f"{r.recognised}/{r.n}", ha="center", fontsize=5.8, color=INK2)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["N1\nfunction published", "N2\npartial", "N3\nnone"], fontsize=6.3)
ax.set_ylim(0, 1.18)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
ax.set_ylabel("“recognised” by closed-book LLM probe")
hgrid(ax)
ax.legend(loc="upper right", fontsize=6.0, handlelength=1.0)
ax.set_title("LLM knowledge tracks the literature", loc="left", fontsize=8)

fig.savefig(FIG / "Fig5.png", dpi=300, bbox_inches="tight")
fig.savefig(FIG / "Fig5.svg", bbox_inches="tight")
plt.close(fig)
print("wrote Fig5")

# ---------------------------------------------------------------- Table 2: supported top-40 and S20 genes
T = G[G.set.isin(["top40", "s20"]) & (G.real == 1)].copy()
T["set_order"] = T.set.map({"top40": 0, "s20": 1})
T = T.sort_values(["set_order", "rank"])
T2 = T[["set", "rank", "symbol", "hgnc_id", "term", "term_name", "label", "label_name", "family", "p_cal", "zmean",
        "nclass", "n_items", "n_functional", "n_depmap_derived", "recognised", "n_decoy_supported"]].rename(
    columns={"term": "predicted_V2_term", "term_name": "predicted_V2_term_name", "label": "V1prime_label",
             "label_name": "V1prime_label_name", "nclass": "literature_class_L", "recognised": "recall_probe"})
T2.to_csv(SD / "Table2_rediscovery.tsv", sep="\t", index=False)

# ---------------------------------------------------------------- derived numbers
for s in ("top40", "s20", "extra30"):
    g = G[G.set == s]
    sup = g[g.real == 1]
    derived(f"{s}_supported_by_class", "; ".join(f"{c} {int((sup.nclass == c).sum())}/{int((g.nclass == c).sum())}"
                                                 for c in ("N1", "N2", "N3")),
            "supported / genes in class", "results/m7/judge/analysis_main_genes.tsv")
    derived(f"{s}_supported_recognised", f"{int((sup.recognised == 'yes').sum())}/{len(sup)}",
            "supported genes recognised by the recall probe", "results/m7/recall_probe_90.tsv")
    derived(f"{s}_recognised", f"{int((g.recognised == 'yes').sum())}/{len(g)}", "recall probe",
            "results/m7/recall_probe_90.tsv")
t40, x30 = G[G.set == "top40"], G[G.set == "extra30"]
tab = [[int((t40.real == 1).sum()), int((t40.real != 1).sum())], [int((x30.real == 1).sum()), int((x30.real != 1).sum())]]
derived("top40_vs_extra30_support_fisher", f"OR {fisher_exact(tab)[0]:.1f}; one-sided p {fisher_exact(tab, 'greater')[1]:.2g}",
        "descriptive, not pre-specified", "results/m7/judge/analysis_main_genes.tsv")
n1t, n1x = t40[t40.nclass == "N1"], x30[x30.nclass == "N1"]
tab = [[int((n1t.real == 1).sum()), int((n1t.real != 1).sum())], [int((n1x.real == 1).sum()), int((n1x.real != 1).sum())]]
derived("top40_vs_extra30_support_within_N1_fisher", f"{tab[0][0]}/{len(n1t)} vs {tab[1][0]}/{len(n1x)}; one-sided p "
        f"{fisher_exact(tab, 'greater')[1]:.2g}", "descriptive, not pre-specified", "results/m7/judge/analysis_main_genes.tsv")
derived("top40_pcal_supported_vs_not", f"median {t40[t40.real == 1].p_cal.median():.4f} vs "
        f"{t40[t40.real != 1].p_cal.median():.4f}", "descriptive", "results/ledger/top40_primary.tsv")
derived("top40_sum_pcal", f"{t40.p_cal.sum():.2f}", "expected GO confirmations (point)", "results/ledger/top40_primary.tsv")
derived("extra30_sum_pcal", f"{x30.p_cal.sum():.3f}", "expected GO confirmations (point)", "results/m7/extra30.tsv")
allL = G[G.set != "hval10"]
derived("L_classes_90", "; ".join(f"{c} {int((allL.nclass == c).sum())}" for c in ("N1", "N2", "N3")),
        "agent L, 90 U candidates", "results/m7/L/index_batch_*.tsv")
derived("L_classes_100", "; ".join(f"{c} {int((G.nclass == c).sum())}" for c in ("N1", "N2", "N3")),
        "agent L, 100 genes incl. hval10", "results/m7/L/index_batch_*.tsv")
derived("L_items", f"{int(G.n_items.sum())} items; {int(G.n_functional.sum())} functional; "
        f"{int(G.n_depmap_derived.sum())} DepMap-derived", "agent L evidence items, 100 genes",
        "results/m7/L/index_batch_*.tsv")
derived("contradicted_top40", ", ".join(t40[t40.real == -1].symbol), "real statement -1",
        "results/m7/judge/analysis_main_genes.tsv")
derived("decoy_supported_genes", "; ".join(f"{r.set}:{r.symbol}" for r in G[G.n_decoy_supported > 0].itertuples()),
        "genes with a supported decoy", "results/m7/judge/analysis_*_genes.tsv")
pd.DataFrame(DERIVED).to_csv(SD / "Fig5_derived_numbers.tsv", sep="\t", index=False)
print(pd.DataFrame(DERIVED).to_string())
