"""Draw the five figures of the readable explainer (docs/explainer_v2/README.md).

Usage (from the project root):
    ./.env/bin/python -I docs/explainer_v2/make_figures.py
Writes PNG and SVG files to docs/explainer_v2/figures/.

Every number is read from a committed results file where one exists; the few
hard-coded values carry a comment naming their source (see also NOTES.md).
Colours: one blue for "this method", one orange for the strongest comparator,
greys for everything else (blue/orange is safe for the common colour-vision
deficiencies, and every bar is also labelled in text).
"""
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)
WE = ROOT / "docs/explainer/worked_example_output"

BLUE = "#2a78d6"      # this method
ORANGE = "#eb6834"    # homology (strongest comparator)
GREY = "#9a9893"      # comparators / decoys
LIGHT = "#d9d7d2"     # background bars
INK = "#0b0b0b"
INK2 = "#52514e"
SURFACE = "#ffffff"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 15,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "text.color": INK,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "svg.fonttype": "none",
})


def read_tsv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(left=False)


# --------------------------------------------------------------------------- data
pcal = json.loads((ROOT / "results/ledger/pcal_summary.json").read_text())
n_scorable = pcal["n_scorable"]                     # 4,271
n_calibrated = pcal["category_counts"]["in_support"]  # 2,583
max_pcal = pcal["max_p_cal"]                        # 0.141

methods = {r["method"]: float(r["p1"]) for r in
           read_tsv(ROOT / "results/holdout_eval/fig_precision_by_method.tsv")}

top40 = read_tsv(ROOT / "results/ledger/top40_primary.tsv")
assert len(top40) == 40 and top40[0]["symbol"] == "ANKRD52"

neigh = read_tsv(WE / "step2_neighbours_top25.tsv")
we = json.loads((WE / "worked_example.json").read_text())
R_ankrd52 = we["step3"]["R"]                        # 0.472
R0_mean = we["step3"]["R0_mean"]                    # 0.0037
judging = read_tsv(WE / "step7_judging.tsv")

# Hard-coded with sources:
N_ALL = 19296         # preregistration/CRITERIA.md (HGNC protein-coding genes)
N_U = 4924            # preregistration/CRITERIA.md
N_ASSESSABLE = 646    # results/ledger/M6_SUMMARY.md (scorable, expressed, assessable)
N_POOL = 269          # results/ledger/M6_SUMMARY.md (in support, expressed & assessable)
N_REAL = 322          # results/revision/a10_assessability_excess_and_implied.tsv (DESIGN expressed, 646 basis)
N_SUPPORTED = 18      # results/m7/judge/analysis_main.md (top40: real supported 18)
N_SUPPORTED_N1 = 16   # results/m7/judge/analysis_main.md (N1: real supported 16)
N_DECOY_SUPP, N_DECOY = 3, 120  # results/m7/judge/analysis_main.md
LOO_PROMISED, LOO_OBS = 0.089, 0.031   # results/holdout_eval/SUMMARY.md (LOO-fitted calibration on H)
H_PROMISED, H_OBS = 0.031, 0.031       # results/holdout_eval/calibration.md (mean out-of-fold p vs observed)


# --------------------------------------------------------------------------- (a) funnel
def fig_funnel():
    stages = [
        (N_ALL, "All human protein-coding genes"),
        (N_U, "Pre-registered as “uncharacterised”"),
        (n_scorable, "Measurable by the tool in the screens"),
        (N_ASSESSABLE, "Partner list is reproducible (and expressed)"),
        (N_POOL, "…and also given a calibrated confidence"),
        (40, "Top 40 by calibrated confidence"),
        (N_SUPPORTED, "Supported by the blinded literature check"),
    ]
    fig, ax = plt.subplots(figsize=(12, 7.0))
    import math
    lmax = math.log10(N_ALL)
    for i, (n, label) in enumerate(stages):
        w = math.log10(n) / lmax  # log-scaled width
        col = BLUE if i >= 3 else GREY
        ax.barh(i, w, left=-w / 2, height=0.72, color=col, edgecolor=SURFACE, linewidth=2)
        ax.text(0, i, f"{n:,}", ha="center", va="center", color="white",
                fontsize=17, fontweight="bold")
        ax.text(0.55, i, label, ha="left", va="center", fontsize=15, color=INK)
    ax.text(0.55, 3.38, f"(at least about {round(N_REAL, -1):,} after allowing for chance passes)",
            ha="left", va="center", fontsize=12.5, color=INK2)
    ax.text(0.55, 6.38, f"({N_SUPPORTED_N1} of them already published)",
            ha="left", va="center", fontsize=12.5, color=INK2)
    ax.set_ylim(6.6, -0.6)
    ax.set_xlim(-0.55, 1.75)
    ax.axis("off")
    ax.text(-0.55, 7.0, "Bar widths on a log scale", fontsize=11, color=INK2)
    save(fig, "a_funnel")


# --------------------------------------------------------------------------- (b) pipeline
def fig_pipeline():
    steps = [
        ("Pick genes\nfirst", "Freeze a list of\n4,924 genes that\ndatabases call\nuncharacterised"),
        ("Find\npartners", "Its 25 most\nco-essential genes\nacross 1,361\ncancer cell lines"),
        ("Check\nreproducibility", "Same partners in\ntwo halves of the\ncell lines? If not,\nflag the gene"),
        ("Guess +\nconfidence", "The best-scoring\nshared function, with\na probability learned\nfrom later discoveries"),
        ("Test\nhonestly", "Genes annotated\nafter 2018, decoys\nfor the literature,\nindependent data"),
    ]
    fig, ax = plt.subplots(figsize=(16, 5.2))
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, (title, body) in enumerate(steps):
        x0 = i + 0.06
        box = FancyBboxPatch((x0, 0.04), 0.82, 0.78, boxstyle="round,pad=0.0,rounding_size=0.06",
                             facecolor="#eef4fc" if i != 4 else "#fdf0ea",
                             edgecolor=BLUE if i != 4 else ORANGE, linewidth=2)
        ax.add_patch(box)
        ax.text(x0 + 0.41, 0.86, str(i + 1), ha="center", va="center", color="white",
                fontsize=20, fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.35", fc=BLUE if i != 4 else ORANGE, ec="none"))
        ax.text(x0 + 0.41, 0.64, title, ha="center", va="center", fontsize=15, fontweight="bold")
        ax.text(x0 + 0.41, 0.29, body, ha="center", va="center", fontsize=12.5, color=INK2,
                linespacing=1.35)
        if i < 4:
            ax.annotate("", xy=(i + 1.06, 0.43), xytext=(i + 0.88, 0.43),
                        arrowprops=dict(arrowstyle="-|>", color=INK2, lw=2, mutation_scale=22))
    save(fig, "b_pipeline")


# --------------------------------------------------------------------------- (c) ANKRD52 strip
def fig_ankrd52():
    fig = plt.figure(figsize=(20, 5.6))
    gs = fig.add_gridspec(1, 5, width_ratios=[0.9, 1.35, 0.9, 1.15, 1.3], wspace=0.5)
    titles = ["1  Picked", "2  Partners", "3  Reproducible", "4  Guess + confidence", "5  Tested"]

    # 1 picked
    ax = fig.add_subplot(gs[0])
    ax.axis("off")
    ax.text(0, 0.78, "No informative\nexperimental\nGO term", fontsize=13.5, va="top")
    ax.text(0, 0.45, f"Only {we['step0']['n_pubmed_focused']} papers\nfocused on it", fontsize=13.5, va="top")
    ax.text(0, 0.14, "→ on the frozen list", fontsize=13.5, va="top", color=BLUE, fontweight="bold")

    # 2 partners
    ax = fig.add_subplot(gs[1])
    rows = neigh[:8]
    names = [r["partner"] for r in rows][::-1]
    vals = [float(r["zavg_BEF"]) for r in rows][::-1]
    cols = [BLUE if r["supports_top_term"] == "True" else GREY for r in rows][::-1]
    ax.barh(names, vals, color=cols, height=0.7, edgecolor=SURFACE, linewidth=2)
    ax.set_xlabel("co-essentiality score", fontsize=12.5)
    ax.tick_params(axis="y", labelsize=12.5)
    ax.tick_params(axis="x", labelsize=11)
    clean(ax)
    ax.text(14.3, 0, "PP6 phosphatase\n(its known partner)", fontsize=10.5, color=INK2, va="center",
            ha="left")
    ax.set_xlim(0, 27)
    ax.text(26.5, 7.75, "blue = gene-silencing\nmachinery (8th, DDX6,\nranks 23rd)", fontsize=10.5, color=BLUE, va="center",
            ha="right")

    # 3 reproducible
    ax = fig.add_subplot(gs[2])
    shared = [R_ankrd52 * 25, R0_mean * 25]
    ax.bar([0, 1], shared, color=[BLUE, GREY], width=0.6, edgecolor=SURFACE, linewidth=2)
    ax.set_xticks([0, 1], ["ANKRD52", "200 look-\nalike genes"], fontsize=12)
    ax.set_ylabel("partners shared\nbetween halves (of 25)", fontsize=12)
    ax.set_ylim(0, 14)
    ax.text(0, shared[0] + 0.4, f"{shared[0]:.0f}", ha="center", fontsize=14, fontweight="bold")
    ax.text(1, shared[1] + 0.4, "~0", ha="center", fontsize=14, fontweight="bold")
    clean(ax)
    ax.spines["left"].set_visible(True)
    ax.tick_params(left=True, labelsize=11)

    # 4 guess + confidence
    ax = fig.add_subplot(gs[3])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0, 0.95, "ncRNA-mediated\ngene silencing", fontsize=14.5, fontweight="bold", va="top",
            color=BLUE)
    ax.text(0, 0.62, "(the microRNA pathway)\n8 of 25 partners vote for it", fontsize=12, color=INK2, va="top")
    # confidence gauge 0..0.3
    y = 0.3
    ax.add_patch(FancyBboxPatch((0, y), 1, 0.09, boxstyle="round,pad=0,rounding_size=0.02",
                                facecolor=LIGHT, edgecolor="none"))
    ax.add_patch(FancyBboxPatch((0, y), max_pcal / 0.3, 0.09, boxstyle="round,pad=0,rounding_size=0.02",
                                facecolor=BLUE, edgecolor="none"))
    ax.text(0, y + 0.13, f"confidence {max_pcal:.2f} (about 1 in 7)", fontsize=12.5, va="bottom")
    ax.text(0, y - 0.04, "0", fontsize=10.5, va="top", color=INK2)
    ax.text(1, y - 0.04, "0.3 = pre-set bar", fontsize=10.5, va="top", ha="right", color=INK2)
    ax.text(0, 0.08, f"highest of {n_calibrated:,} genes", fontsize=12, color=INK2)

    # 5 tested
    ax = fig.add_subplot(gs[4])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ordered = sorted(judging, key=lambda r: r["is_real"] != "True")
    labels = {"GO:0031047": "gene silencing (real)", "GO:0050804": "decoy: synapses",
              "GO:0160215": "decoy: deacylase", "GO:0043648": "decoy: acid metabolism"}
    for k, r in enumerate(ordered):
        yy = 0.86 - k * 0.17
        real = r["is_real"] == "True"
        mark = "✓✓" if int(r["judge1"]) + int(r["judge2"]) == 2 else "– –"
        ax.text(0, yy, labels[r["term"]], fontsize=12.5, va="center",
                fontweight="bold" if real else "normal", color=INK if real else INK2)
        ax.text(1, yy, mark, fontsize=14, va="center", ha="right",
                color=BLUE if real else GREY, fontweight="bold")
    ax.text(1, 1.0, "2 judges", fontsize=10.5, ha="right", color=INK2)
    ax.text(0, 0.12, "Already published\n(Golden 2017)", fontsize=12, color=INK2, va="center")

    for g, t in zip(range(5), titles):
        fig.text(fig.axes[g].get_position().x0, 0.97, t, fontsize=16, fontweight="bold", va="top")
    fig.subplots_adjust(top=0.82)
    save(fig, "c_ankrd52")


# --------------------------------------------------------------------------- (d) scorecard
def fig_scorecard():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), gridspec_kw={"wspace": 0.55,
                                                                   "width_ratios": [1.2, 1, 0.9]})

    # Test 1 accuracy on the 2018 test set
    ax = axes[0]
    rows = [("Look-alike genes\n(chance)", methods["matched-gene null"], GREY),
            ("Older co-essentiality\nscore (GLS)", methods["GLS (R1)"], GREY),
            ("This method", methods["zavg_BEF (R1)"], BLUE),
            ("Homology\n(inferred GO terms)", methods["Homology baseline"], ORANGE)]
    for i, (lab, v, c) in enumerate(rows):
        ax.barh(i, v * 100, color=c, height=0.65, edgecolor=SURFACE, linewidth=2)
        ax.text(v * 100 + 0.5, i, f"{v * 100:.1f}%", va="center", fontsize=14, fontweight="bold")
    ax.set_yticks(range(4), [r[0] for r in rows], fontsize=12.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 27)
    ax.set_xlabel("top guess right (%)", fontsize=12.5)
    clean(ax)
    ax.set_title("1  Predict functions found\n    after 2018 (809 genes)", loc="left", fontsize=15,
                 fontweight="bold")

    # Test 2 honesty of confidence
    ax = axes[1]
    xs = [0, 1]
    prom = [LOO_PROMISED * 100, H_PROMISED * 100]
    obs = [LOO_OBS * 100, H_OBS * 100]
    w = 0.36
    ax.bar([x - w / 2 for x in xs], prom, w, color=LIGHT, edgecolor=SURFACE, linewidth=2, label="promised")
    ax.bar([x + w / 2 for x in xs], obs, w, color=BLUE, edgecolor=SURFACE, linewidth=2, label="delivered")
    for x, p, o in zip(xs, prom, obs):
        ax.text(x - w / 2, p + 0.2, f"{p:.1f}%", ha="center", fontsize=12.5)
        ax.text(x + w / 2, o + 0.2, f"{o:.1f}%", ha="center", fontsize=12.5, fontweight="bold")
    ax.set_xticks(xs, ["learned on\nwell-studied genes", "learned on the\n2018 test set"], fontsize=12)
    ax.set_ylim(0, 10.5)
    ax.set_ylabel("average hit rate (%)", fontsize=12.5)
    ax.legend(frameon=False, fontsize=12, loc="upper right")
    clean(ax)
    ax.spines["left"].set_visible(True)
    ax.tick_params(left=True)
    ax.set_title("2  Average predicted vs\n    observed hit rate", loc="left", fontsize=15, fontweight="bold")

    # Test 3 literature
    ax = axes[2]
    real_pct = N_SUPPORTED / 40 * 100
    n1_pct = N_SUPPORTED_N1 / 40 * 100
    decoy_pct = N_DECOY_SUPP / N_DECOY * 100
    ax.bar(0, n1_pct, 0.6, color=BLUE, edgecolor=SURFACE, linewidth=2)
    ax.bar(0, real_pct - n1_pct, 0.6, bottom=n1_pct, color="#8fb8ea", edgecolor=SURFACE, linewidth=2)
    ax.bar(1, decoy_pct, 0.6, color=GREY, edgecolor=SURFACE, linewidth=2)
    ax.text(0, real_pct + 1.2, f"{N_SUPPORTED}/40 ({real_pct:.0f}%)", ha="center", fontsize=14, fontweight="bold")
    ax.text(1, decoy_pct + 1.2, f"{N_DECOY_SUPP}/{N_DECOY} ({decoy_pct:.1f}%)", ha="center", fontsize=14,
            fontweight="bold")
    ax.text(0.36, n1_pct + (real_pct - n1_pct) / 2, f"{N_SUPPORTED - N_SUPPORTED_N1} not\nestablished", va="center",
            fontsize=11, color=INK2)
    ax.text(0, n1_pct / 2, f"{N_SUPPORTED_N1}\nalready\npublished", ha="center", va="center",
            color="white", fontsize=11.5)
    ax.set_xticks([0, 1], ["real\npredictions", "decoys"], fontsize=12.5)
    ax.set_ylim(0, 55)
    ax.set_ylabel("judged supported (%)", fontsize=12.5)
    clean(ax)
    ax.spines["left"].set_visible(True)
    ax.tick_params(left=True)
    ax.set_title("3  Does the literature\n    agree? (top 40)", loc="left", fontsize=15, fontweight="bold")
    save(fig, "d_scorecard")


# --------------------------------------------------------------------------- (e) how the claims shrank
def fig_shrink():
    """Journey figure: each headline claim before and after the check that tested it."""
    loo = 0.1385  # results/calibration/label_shuffle.md (R1 precision@1, 2,519 known genes)
    rows = [
        # label, first estimate, after the check, before text, after text, turning points (README section 7)
        ("Top guess right", loo * 100, methods["zavg_BEF (R1)"] * 100, "13.9% on well-studied genes",
         "3.0% on genes annotated after 2018", "moments 1, 4"),
        ("Average confidence", LOO_PROMISED * 100, LOO_OBS * 100, "8.9% promised (learned on known genes)",
         "3.1% delivered", "moment 4"),
        ("Genes with a real signal", N_ASSESSABLE, N_REAL, "646 pass the check",
         "at least ~320 after chance passes", "moments 3, 6"),
        ("Expected confirmed guesses", 30.5, 4.9, "~30 if every gene is annotated",
         "~5 at the real annotation rate", "moment 6"),
        ("Supported top-40 guesses,\nfunction not yet established", N_SUPPORTED, N_SUPPORTED - N_SUPPORTED_N1,
         "18 supported by judges", "2 for genes not already characterised", "moment 6"),
    ]
    fig, ax = plt.subplots(figsize=(15, 6.4))
    for i, (lab, a, b, ta, tb, tp) in enumerate(rows):
        frac = b / a * 100
        ax.barh(i, 100, color=LIGHT, height=0.62, edgecolor=SURFACE, linewidth=2)
        ax.barh(i, frac, color=BLUE, height=0.62, edgecolor=SURFACE, linewidth=2)
        ax.text(-2, i, lab, ha="right", va="center", fontsize=14, fontweight="bold")
        ax.text(frac + 1.2, i + 0.13, tb, va="center", fontsize=12.5, color=INK, fontweight="bold")
        ax.text(98.5, i - 0.15, ta, ha="right", va="center", fontsize=11.5, color=INK2)
        ax.text(102, i, tp, va="center", fontsize=11.5, color=INK2)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlim(0, 113)
    ax.set_xticks([0, 25, 50, 75, 100], ["0", "25%", "50%", "75%", "100%"], fontsize=11)
    ax.set_xlabel("share of the first estimate that survived the stricter check", fontsize=12.5)
    ax.set_yticks([])
    clean(ax)
    save(fig, "e_claims_shrank")


if __name__ == "__main__":
    fig_funnel()
    fig_pipeline()
    fig_ankrd52()
    fig_scorecard()
    fig_shrink()
