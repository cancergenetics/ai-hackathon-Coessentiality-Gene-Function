"""14_splithalf.py -- split-half tool runs for assessability (DESIGN.md v2.3 §4.2, §8).

Splits (``splithalf.split_halves``; seeds 0-4 = frozen seeds.split_half_seeds): cell lines of CRISPRGeneEffect are
split into two halves, stratified by OncotreeLineage (Model.csv) x screen library, keeping PatientID together (each
patient goes to one half; a patient is assigned to its majority stratum). Screen library per line = the combination of
``Library*`` indicator columns equal to 1 in data/raw/depmap/CRISPRConfounders.csv (e.g. 'Avana', 'Avana+KY');
recorded for every line.

Runs: for each seed and half the tool (published Config, unmodified) is refitted on that half's lines
(``coess_matrix.fit_model``; genes with no observation in the half are dropped by fit_model and recorded); the top 60
zavg_BEF neighbours of every gene are taken on the fly from the model's block API (no dense matrix;
``splithalf.half_neighbours``) with the §3.1 exclusions (self, same arm, Ensembl paralogues) and candidates restricted
to genes that are background both in that half and in the full data. The 60-list is filtered to the background of
the other half and cut to 25 in scripts/15_assessability.py (DESIGN: top-60 per half retained before filtering).

Outputs: data/derived/splithalf/seed{s}_half{h}.npz (ids G x 60 matrix positions, -1 padding; z; bg_half; dropped
genes), data/derived/splithalf/half_assignment.tsv (line, lineage, library, patient, half per seed),
data/derived/splithalf/run_manifest.json (per run: lines, |BG|, tool K, dropped all-NaN genes, BG changes, fit and
neighbour time, peak RSS) and results/assessability/splithalf_runs.md (summary).
Run: .env/bin/python -I scripts/14_splithalf.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

t0 = time.perf_counter()
MODEL, CONF = "data/raw/depmap/Model.csv", "data/raw/depmap/CRISPRConfounders.csv"
g = C.gate_check(data_files=(C.EFFECT_CSV, MODEL, CONF))
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import coess_matrix as cm  # noqa: E402
from src import neighbours as nbm  # noqa: E402
from src import splithalf as sh  # noqa: E402

SEEDS = C.fz("assessability", "split_seeds")
KEEP = C.fz("assessability", "half_list_retained_top")
effect = C.load_effect()
gt = C.load_full_index()
assert (gt.gene.values == np.asarray(effect.columns)).all()
idx = C.gene_index(effect.columns)
arm = nbm.arm_codes(C.arms_for(idx).arm.values)
par = C.paralogue_map(idx)
bg_full = gt.bg.values.astype(bool)
G = len(gt)

model = pd.read_csv(C.ROOT / MODEL, dtype=str).set_index("ModelID")
conf = pd.read_csv(C.ROOT / CONF, index_col=0)
libcols = [c for c in conf.columns if c.startswith("Library")]
lib = conf[libcols].fillna(0).apply(lambda r: "+".join(c[7:] for c in libcols if r[c] > 0) or "none", axis=1)
lines = effect.index
library = lib.reindex(lines).fillna("unrecorded")
asg = pd.DataFrame(dict(lineage=model.OncotreeLineage.reindex(lines).values,
                        patient=model.PatientID.reindex(lines).values, library=library.values), index=lines)
halves = {}
for s in SEEDS:
    halves[s] = sh.split_halves(lines, model, seed=s, extra_strata=library)
    asg[f"half_seed{s}"] = halves[s].values
out = C.DERIVED / "splithalf"
out.mkdir(parents=True, exist_ok=True)
asg.to_csv(out / "half_assignment.tsv", sep="\t", index_label="ModelID")

# patient integrity and balance
for s in SEEDS:
    assert asg.groupby("patient")[f"half_seed{s}"].nunique().max() == 1

runs = []
for s in SEEDS:
    bc = sh.background_check(effect, halves[s])
    for h in (0, 1):
        f = out / f"seed{s}_half{h}.npz"
        lh = lines[halves[s].values == h]
        t = time.perf_counter()
        ids, z, info = sh.half_neighbours(effect, lh, KEEP, cm.PUBLISHED_CONFIG, bg=bg_full, arm=arm,
                                          paralogues=par)
        dt = time.perf_counter() - t
        bg_half = (bc[f"nan_{h}"].values < cm.PUBLISHED_CONFIG.max_nan) & ~bc[f"allnan_{h}"].values
        # integrity: neighbours are BG in this half and in the full data; no self/arm/paralogue
        nb = nbm.Neighbours(rows=np.arange(G), ids=ids, z=z, K=KEEP)
        nbm.assert_valid(nb, bg=bg_half & bg_full, arm=arm, paralogues=par)
        np.savez(f, ids=ids.astype(np.int32), z=z, bg_half=bg_half, lines=np.asarray(lh, dtype=str),
                 dropped=np.asarray(info["dropped_all_nan"], dtype=str))
        r = dict(seed=s, half=h, n_lines=info["n_lines"], n_patients=int(asg.loc[lh, "patient"].nunique()),
                 n_bg_half=info["n_bg"], K_tool=info["K_tool"], n_dropped_all_nan=len(info["dropped_all_nan"]),
                 dropped_all_nan=info["dropped_all_nan"], n_bg_changed_vs_full=int((bg_half != bg_full).sum()),
                 n_genes_short_of_60=int((ids[:, -1] < 0).sum()), fit_s=info["fit_s"], total_s=round(dt, 1),
                 peak_rss_gb=C.peak_rss_gb())
        runs.append(r)
        C.log(f"seed {s} half {h}: {r['n_lines']} lines, BG {r['n_bg_half']}, K_tool {r['K_tool']}, "
              f"dropped {r['n_dropped_all_nan']}, {dt:.0f} s")

# stratum balance
bal = []
for s in SEEDS:
    st = asg.lineage.astype(str) + "|" + asg.library.astype(str)
    ct = pd.crosstab(st, asg[f"half_seed{s}"])
    bal.append(dict(seed=s, n0=int((asg[f"half_seed{s}"] == 0).sum()), n1=int((asg[f"half_seed{s}"] == 1).sum()),
                    max_stratum_imbalance=int((ct[0] - ct[1]).abs().max()),
                    strata_imbalance_gt1=int(((ct[0] - ct[1]).abs() > 1).sum()), n_strata=len(ct)))
run = C.write_manifest(out / "run_manifest.json", "scripts/14_splithalf.py", g,
                       [C.EFFECT_CSV, MODEL, CONF, C.HUB_TSV, C.PARALOGUE_TSV,
                        "data/derived/matrices/zavg_full/genes.tsv"], seed=SEEDS, t0=t0,
                       extra=dict(keep=KEEP, config=cm.config_dict(cm.PUBLISHED_CONFIG), runs=runs, balance=bal,
                                  library_counts=library.value_counts().to_dict()))
rows = [f"| {r['seed']} | {r['half']} | {r['n_lines']} | {r['n_patients']} | {r['n_bg_half']} | {r['K_tool']} | "
        f"{r['n_dropped_all_nan']} | {r['n_bg_changed_vs_full']} | {r['total_s']} |" for r in runs]
brow = [f"| {b['seed']} | {b['n0']} / {b['n1']} | {b['n_strata']} | {b['max_stratum_imbalance']} | "
        f"{b['strata_imbalance_gt1']} |" for b in bal]
dropped_all = sorted({x for r in runs for x in r["dropped_all_nan"]})
L = ["# Split-half tool runs (DESIGN §4.2)", "",
     f"Generated by `scripts/14_splithalf.py` ({run['created']}; runtime {run['runtime_s']} s, peak RSS "
     f"{run['peak_rss_gb']} GB). Gate: tag `{g['tag']}` @ {g['tag_commit'][:10]}, tool {g['tool_commit'][:10]}. "
     f"Published tool Config (unmodified). Seeds {SEEDS}.", "",
     f"- Lines: {len(lines)} (CRISPRGeneEffect); lineage = Model.csv OncotreeLineage ({asg.lineage.nunique()} "
     f"lineages, none missing: {asg.lineage.notna().all()}); PatientID kept together ({asg.patient.nunique()} "
     f"patients; {int((asg.groupby('patient').size() > 1).sum())} with > 1 line).",
     "- **Screen library: available** — `CRISPRConfounders.csv` `Library*` indicator columns (Avana, HumagneCD, KY, "
     "TKOv3, Brunello); the stratum label is the combination of libraries used for the line: " +
     ", ".join(f"{k} {v}" for k, v in library.value_counts().items()) + ". Strata = lineage × library "
     "combination.",
     f"- Neighbour lists: top {KEEP} per gene per half (zavg_BEF, half-specific tool fit), candidates = genes BG in "
     "that half and in the full data, self/same-arm/paralogue excluded (`neighbours.assert_valid` passed on every "
     "run). Filtering to BG_A ∩ BG_B ∩ BG_full and the cut to 25 happen in `scripts/15_assessability.py`.",
     f"- All-NaN columns dropped per half (recorded per run): {len(dropped_all)} distinct genes over the 10 runs"
     + (f" ({', '.join(dropped_all[:20])}{' …' if len(dropped_all) > 20 else ''})" if dropped_all else "") + ".", "",
     "| seed | half | lines | patients | BG genes (half) | tool K | all-NaN genes dropped | BG status differs from "
     "full | time (s) |", "|---|---|---|---|---|---|---|---|---|", *rows, "",
     "Stratum balance (lines per half; |half 0 − half 1| per lineage × library stratum):", "",
     "| seed | lines half 0 / half 1 | strata | max imbalance | strata with imbalance > 1 |", "|---|---|---|---|---|",
     *brow, "",
     "Files (git-ignored): `data/derived/splithalf/seed{s}_half{h}.npz`, `half_assignment.tsv`, "
     "`run_manifest.json`.", ""]
dst = C.ROOT / "results" / "assessability" / "splithalf_runs.md"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text("\n".join(L))
C.log(f"wrote {dst}")
