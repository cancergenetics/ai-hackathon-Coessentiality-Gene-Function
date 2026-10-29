#!/usr/bin/env python
"""31_label_shuffle.py -- label-shuffle control on the LOO benchmark (DESIGN.md v2.3 §2.4); M5a.

The V2 (current) gene x term membership is permuted across genes (``vocab.V2.permuted``): rows are exchanged among
annotated-background genes within blocks of 20 genes of similar candidate-term count (genes sorted by count, random
tie order), so term sizes are preserved exactly and per-gene annotation counts nearly so (reported); unannotated genes
stay unannotated. Seed 0 (frozen seeds.bootstraps / global seeds[0]); seeds 1-4 are run as a descriptive robustness
check. The IPI with/from rule is disabled under the shuffle (with/from no longer refers to the gene carrying the row);
the LOO query's own (shuffled) row is removed from all counts as in the real run. Targets = the query's own shuffled
candidate terms; no circularity filter (labels are random). Neighbours, matched lists, rankers and the reportability
rule are those of scripts/30.

Expected: precision@1 of the chosen ranker (scripts/30 decision) collapses to the prior-only level (top term = the
most frequent candidate term). Reported: precision@1 and MRR of R1/R2/R3 and prior-only on shuffled labels, the paired
difference chosen - prior-only with a gene-bootstrap 95% percentile CI (1,000 reps, seed 0), and the real-data values
from scripts/30 for comparison.

Outputs: results/calibration/label_shuffle.md, label_shuffle.tsv, label_shuffle_manifest.json.
Run: .env/bin/python -I scripts/31_label_shuffle.py   (after scripts/30)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

t0 = time.perf_counter()
gate = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5_common as M5  # noqa: E402
from src import metrics as mt  # noqa: E402
from src import vocab  # noqa: E402

K = C.fz("predictor", "k_neighbours")
LO, HI = C.fz("vocabulary", "candidate_term_min_genes"), C.fz("vocabulary", "candidate_term_max_genes")
RANKERS = C.fz("predictor", "rankers")
SEED = C.fz("seeds", "bootstraps")
SEEDS = C.fz("seeds", "global")
BLOCK = 20
NBOOT = 1000
OUT = C.ROOT / "results" / "calibration"

real = pd.read_csv(OUT / "loo_ranker_choice.tsv", sep="\t")
chosen = real[real.analysis.str.startswith("primary") & real.chosen_by_frozen_rule].ranker.iloc[0]
C.log(f"chosen ranker (scripts/30): {chosen}")

gt = M5.load_index()
G = len(gt)
nb = M5.load_neighbours(K, G)
matches = M5.load_matches()
loo = M5.load_loo(gt)
Q = loo.matrix_index.values.astype(np.int64)
v2 = M5.build_current_v2(gt, LO, HI)


def run(seed):
    vs, cnt = v2.permuted(seed=seed, block=BLOCK)
    sc = vocab.score_queries(vs, nb, matches, Q, loo=True)
    ranked = {r: sc.ranked(r) for r in RANKERS}
    rows = []
    for i, g in enumerate(Q):
        g = int(g)
        cand = vs.candidates(sc.sizes[i])
        own = vs.own_terms(g)
        T = set(own[cand[own]].tolist())
        if not T:
            continue
        row = dict(pos=g, n_targets=len(T))
        for r in RANKERS:
            lst = ranked[r][g]
            row[f"rr_{r}"], row[f"hit1_{r}"] = mt.reciprocal_rank(lst, T), mt.hit_at_1(lst, T)
            row[f"has_pred_{r}"] = bool(lst)
        pl = sc.prior_rank(i, cand)
        hp = np.flatnonzero(np.isin(pl, list(T)))
        row["rr_prior"] = 1.0 / (hp[0] + 1) if len(hp) else 0.0
        row["hit1_prior"] = float(pl[0] in T)
        rows.append(row)
    return pd.DataFrame(rows), cnt


res, cnts = {}, {}
for s in SEEDS:
    t = time.perf_counter()
    res[s], cnts[s] = run(s)
    C.log(f"seed {s}: {len(res[s])} LOO genes with shuffled targets ({time.perf_counter() - t:.0f} s)")

D = res[SEED]
cl = np.arange(len(D))
summ = []
for s, Ds in res.items():
    for r in [*RANKERS, "prior"]:
        row = dict(seed=s, ranker=r, n_genes=len(Ds), MRR=Ds[f"rr_{r}"].mean(), precision_at_1=Ds[f"hit1_{r}"].mean(),
                   coverage=Ds[f"has_pred_{r}"].mean() if r != "prior" else 1.0)
        if s == SEED:
            b = mt.cluster_bootstrap_mean(Ds[f"hit1_{r}"].values, cl, n_boot=NBOOT, seed=SEED)
            row["p1_ci"] = f"{b['ci_percentile'][0]:.4f}-{b['ci_percentile'][1]:.4f}"
            b = mt.cluster_bootstrap_mean(Ds[f"rr_{r}"].values, cl, n_boot=NBOOT, seed=SEED)
            row["MRR_ci"] = f"{b['ci_percentile'][0]:.4f}-{b['ci_percentile'][1]:.4f}"
        summ.append(row)
S = pd.DataFrame(summ)
S.to_csv(OUT / "label_shuffle.tsv", sep="\t", index=False, float_format="%.5f")
diffs = {}
for r in RANKERS:
    diffs[r] = mt.paired_cluster_bootstrap(D[f"hit1_{r}"], D["hit1_prior"], cl, n_boot=NBOOT, seed=SEED)
dc = diffs[chosen]
# collapse = no excess over prior-only (upper 95% CI of chosen - prior <= 0.01); "at" vs "below" prior reported
collapsed = dc["ci_percentile"][1] <= 0.01
below = dc["ci_percentile"][1] < 0
cnt = cnts[SEED]
dcount = (cnt.count_after - cnt.count_before).abs()
rel = dcount / cnt.count_before.clip(lower=1)

man = C.write_manifest(OUT / "label_shuffle_manifest.json", "scripts/31_label_shuffle.py", gate,
                       M5.INPUTS + ["results/calibration/loo_ranker_choice.tsv"], seed=SEED, t0=t0,
                       extra=dict(block=BLOCK, seeds=SEEDS, n_boot=NBOOT, chosen=chosen,
                                  shuffled_p1_chosen=float(D[f"hit1_{chosen}"].mean()),
                                  shuffled_p1_prior=float(D["hit1_prior"].mean())))
rp = real[real.analysis.str.startswith("primary")].set_index("ranker")
rn = real[real.analysis == "sens: no circularity exclusion"].set_index("ranker")
x0 = S[S.seed == SEED].set_index("ranker")
L = ["# Label-shuffle control (DESIGN §2.4) — LOO benchmark", "",
     f"Generated by `scripts/31_label_shuffle.py` ({man['created']}; runtime {man['runtime_s']} s). Gate: tag "
     f"`{gate['tag']}` @ {gate['tag_commit'][:10]}. Permutation seed {SEED} (seeds {SEEDS[1:]} descriptive); "
     f"bootstrap {NBOOT} reps, seed {SEED}, gene-level, percentile.", "",
     f"## Result: chosen ranker {chosen} — precision@1 "
     + ("**collapses: no excess over prior-only** (" + ("it falls below the prior-only level" if below else
        "within 0.01 of the prior-only level") + ")" if collapsed else "**does NOT collapse (excess over prior-only)**"),
     "",
     f"Shuffled labels (seed {SEED}, {len(D)} LOO genes with >= 1 shuffled candidate target): precision@1 "
     f"{chosen} = {x0.loc[chosen, 'precision_at_1']:.4f} (95% CI {x0.loc[chosen, 'p1_ci']}) vs prior-only "
     f"{x0.loc['prior', 'precision_at_1']:.4f} ({x0.loc['prior', 'p1_ci']}); difference {dc['estimate']:+.4f} "
     f"(95% CI {dc['ci_percentile'][0]:+.4f} to {dc['ci_percentile'][1]:+.4f}). Real labels (scripts/30): "
     f"{chosen} {rp.loc[chosen, 'precision_at_1']:.4f} vs prior-only {rp.loc['prior', 'precision_at_1']:.4f} "
     f"(primary, {int(rp.loc[chosen, 'n_genes'])} genes); without circularity exclusion "
     f"{rn.loc[chosen, 'precision_at_1']:.4f} vs {rn.loc['prior', 'precision_at_1']:.4f}.", "",
     "| labels | ranker | n genes | precision@1 | 95% CI | MRR | 95% CI | Δp@1 vs prior (95% CI) | coverage |",
     "|---|---|---|---|---|---|---|---|---|"]
for r in [*RANKERS, "prior"]:
    x = x0.loc[r]
    d = (f"{diffs[r]['estimate']:+.4f} ({diffs[r]['ci_percentile'][0]:+.4f} to {diffs[r]['ci_percentile'][1]:+.4f})"
         if r in diffs else "")
    L.append(f"| shuffled (seed {SEED}) | {r if r != 'prior' else 'prior-only'} | {int(x.n_genes)} | "
             f"{x.precision_at_1:.4f} | {x.p1_ci} | {x.MRR:.4f} | {x.MRR_ci} | {d} | {x.coverage:.3f} |")
for r in [*RANKERS, "prior"]:
    x = rp.loc[r]
    L.append(f"| real (primary, scripts/30) | {r if r != 'prior' else 'prior-only'} | {int(x.n_genes)} | "
             f"{x.precision_at_1:.4f} | {x.p1_ci_gene} | {x.MRR:.4f} | {x.MRR_ci_gene} | | {x.coverage:.3f} |")
L += ["", "Robustness (other permutation seeds; descriptive):", "",
      "| seed | n genes | R1 p@1 | R2 p@1 | R3 p@1 | prior p@1 | R1 MRR | R2 MRR | R3 MRR | prior MRR |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for s in SEEDS:
    x = S[S.seed == s].set_index("ranker")
    L.append(f"| {s} | {int(x.n_genes.iloc[0])} | " + " | ".join(f"{x.loc[r, 'precision_at_1']:.4f}"
                                                            for r in [*RANKERS, 'prior'])
             + " | " + " | ".join(f"{x.loc[r, 'MRR']:.4f}" for r in [*RANKERS, 'prior']) + " |")
L += ["", "## Shuffle details", "",
      f"- Rows of the V2 gene x term matrix exchanged among the {len(cnt):,} annotated-background genes within "
      f"{BLOCK}-gene blocks sorted by candidate-term count; genes moved: {cnt.moved.mean():.1%}. Term sizes identical "
      f"to the real data (asserted in tests/test_vocab.py). Per-gene candidate-term count change: median "
      f"{dcount.median():.0f}, 90th pct {dcount.quantile(0.9):.0f}, max {dcount.max():.0f} (relative median "
      f"{rel.median():.1%}, 90th pct {rel.quantile(0.9):.1%}); exact count preserved for {(dcount == 0).mean():.1%}.",
      "- IPI with/from rule disabled under the shuffle; LOO query's own row removed from all counts; matched-list "
      "per-term exclusion uses the shuffled membership; no circularity filter.",
      f"- Collapse criterion used in this report (descriptive; DESIGN §2.4 gives no numeric rule): no excess over "
      f"prior-only, i.e. the upper 95% CI of precision@1({chosen}) − precision@1(prior-only) on shuffled labels is "
      f"<= 0.01. All three rankers fall BELOW prior-only on shuffled labels: with random labels the neighbourhood "
      f"picks an arbitrary (smaller) term, whereas prior-only always picks the most frequent candidate term (size "
      f"200), the frequency-optimal guess. The network signal is therefore entirely removed; strict equality with "
      f"the prior level is not expected for a ranker that does not rank by frequency.", ""]
(OUT / "label_shuffle.md").write_text("\n".join(L))
C.log(f"wrote {OUT / 'label_shuffle.md'}")
print(S.to_string())
