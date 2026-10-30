"""Draw the research-journey timeline from journey_data.json.

Usage (from the project root):
    ./.env/bin/python -I docs/explainer/journey_figure.py
Writes docs/explainer/figures/journey_timeline.svg and .png.
Colours: Okabe-Ito (colour-blind safe); milestone groups are also named in the bands.
"""
import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "journey_data.json").read_text())

GROUP_COLOUR = {  # Okabe-Ito
    "design": "#56B4E9",
    "evaluation": "#E69F00",
    "predictions": "#009E73",
    "writing": "#CC79A7",
}
MARKER = "#D55E00"
INK = "#222222"


def t(s):
    return mdates.date2num(datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))


# label placement (x anchor as HH:MM on the TP's own day, y level); chosen so leader lines never cross
LABEL_Y = {1: 5.95, 2: 7.05, 3: 4.85, 4: 3.75, 5: 2.65, 6: 4.85, 7: 3.75, 8: 2.65}
LANE_Y0, LANE_Y1 = 0.0, 1.0
MARK_Y = 1.55

fig, ax = plt.subplots(figsize=(14, 6.2), dpi=150)
x0, x1 = t(DATA["range"][0]), t(DATA["range"][1])

# milestone bands
NARROW = []
for ph in DATA["phases"]:
    a, b = t(ph["start"]), t(ph["end"])
    ax.add_patch(Rectangle((a, LANE_Y0), b - a, LANE_Y1 - LANE_Y0, facecolor=GROUP_COLOUR[ph["group"]],
                           alpha=0.38, edgecolor="white", linewidth=1.5, zorder=1))
    width_h = (b - a) * 24
    mid = (a + b) / 2
    if width_h >= 1.5:
        ax.text(mid, 0.5, f"{ph['milestones']}\n{ph['label']}", ha="center", va="center", fontsize=8.2,
                color=INK, zorder=3)
    else:  # narrow band: milestone code inside, name in the key line below the axis
        ax.text(mid, 0.5, ph["milestones"].replace("-", "–"), ha="center", va="center", fontsize=7.5,
                color=INK, rotation=90, zorder=3)
        NARROW.append(f"{ph['milestones'].replace('-', '–')} {ph['label'].lower()}")

# hatched gaps
for g in DATA["gaps"]:
    a, b = t(g["start"]), t(g["end"])
    ax.add_patch(Rectangle((a, LANE_Y0), b - a, LANE_Y1 - LANE_Y0, facecolor="none", edgecolor="#777777",
                           hatch="///", linewidth=0, alpha=0.6, zorder=2))
    ax.text((a + b) / 2, LANE_Y1 + 0.12, g["label"], ha="center", va="bottom", fontsize=7, color="#555555",
            style="italic")

# turning points
for tp in DATA["turning_points"]:
    n = tp["n"]
    xm = t(tp["time"])
    xs, xe = t(tp["time_start"]), t(tp["time_end"])
    ax.scatter([xm], [MARK_Y], s=230, color=MARKER, edgecolor="white", linewidth=1.2, zorder=6)
    ax.text(xm, MARK_Y, str(n), ha="center", va="center", fontsize=8.5, color="white", fontweight="bold",
            zorder=7)
    ly = LABEL_Y[n]
    ax.plot([xm, xm], [MARK_Y + 0.17, ly - 0.08], color=MARKER, linewidth=0.8, alpha=0.8, zorder=3)
    label = f"TP{n}  {tp['short_label']}\n{tp['key_number']}"
    ha = "left"
    xt = xm
    if n == 8:  # keep the last label inside the axis
        ha = "right"
        xt = xm + 0.3 / 24 * 10
    ax.text(xt, ly, label, ha=ha, va="bottom", fontsize=8.3, color=INK, zorder=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=MARKER, linewidth=0.8))

# axes
ax.set_xlim(x0, x1)
ax.set_ylim(-1.45, 8.1)
ax.yaxis.set_visible(False)
for side in ("left", "right", "top"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_position(("data", LANE_Y0))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.tick_params(axis="x", labelsize=7.5, colors="#333333", length=3)
for lab in ax.get_xticklabels():
    lab.set_rotation(0)
mid = t("2026-10-30T00:00:00Z")
ax.text(x0 + 0.002, -0.95, "Narrow bands:  " + "  ·  ".join(NARROW), fontsize=7.5, color="#444444", ha="left")
ax.text(t("2026-10-29T19:35:00Z"), -1.35, "29 Oct 2026 (UTC)", fontsize=7.5, color="#333333", ha="left")
ax.text(mid - 0.004, -1.35, "30 Oct →", fontsize=7.5, color="#333333", ha="left")

# legend for groups
handles = [Rectangle((0, 0), 1, 1, facecolor=c, alpha=0.38) for c in GROUP_COLOUR.values()]
names = ["Design and pre-registration", "Verification and hold-out", "Predictions and literature checks",
         "Paper and review"]
ax.legend(handles, names, loc="upper right", fontsize=7.5, frameon=False, ncol=2,
          bbox_to_anchor=(1.0, 1.02))
ax.set_title("How the method took shape: eight turning points in 15 hours", loc="left", fontsize=11,
             color=INK, pad=6)

fig.tight_layout()
out = HERE / "figures"
out.mkdir(exist_ok=True)
fig.savefig(out / "journey_timeline.svg")
fig.savefig(out / "journey_timeline.png", dpi=150)
print("wrote", out / "journey_timeline.svg", out / "journey_timeline.png")
