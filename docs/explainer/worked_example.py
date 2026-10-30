#!/usr/bin/env python
"""worked_example.py -- trace ONE pre-registered gene (ANKRD52) through every step of the final pipeline, plus one
hold-out control (TMEM242), by re-running the project's own code, and check the results against the committed ledger.

Nothing here is a new method: every number comes from the functions the pipeline scripts use
(scripts/m4_common.py, m5_common.py, m5b_common.py, m6_common.py, src/*.py, and load_scores from
scripts/52_judge_analysis.py). Where a script's logic lives only inside the script body (not in a function), the
few lines are repeated here verbatim in spirit and marked "as in scripts/NN".

Steps (see docs/explainer/worked_example_notes.md for the narrative):
  0 pre-registration (D1/D2/D3, the D1 GAF rows)         4 function assignment (V2 term scores, top term, V1/V1' label)
  1 input profile (DepMap effect, expression)          5 calibration covariates and p_cal
  2 co-essentiality neighbours N(g) and exclusions     6 orthogonal support (real / matched / decoy)
  3 assessability (split-half R(g), empirical p)       7 blinded literature judging
  H hold-out example TMEM242 (2018 annotations, current DepMap neighbours)

Writes only under docs/explainer/: worked_example_output/*.tsv|json, figures/we_*.png. Never writes results/, data/
or config/ (the support cache is used in memory only and never saved).
Needs the git-ignored local data (data/raw, data/derived) and gate.check() to pass.
Run from the repository root:  ./.env/bin/python -I docs/explainer/worked_example.py      (~8-10 min, ~6 GB RAM)
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import m4_common as C  # noqa: E402

T0 = time.perf_counter()
GATE = C.gate_check()            # required before any pairwise DepMap information is read
C.log("gate OK")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import coess_matrix as cm  # noqa: E402
from src import knownness as kn  # noqa: E402
from src import ledger as LG  # noqa: E402
from src import neighbours as nbm  # noqa: E402
from src import predictor as pr  # noqa: E402
from src import splithalf as sh  # noqa: E402
from src import vocab  # noqa: E402

log = C.log
GENE, CTRL = "ANKRD52", "TMEM242"
EXP = ROOT / "docs" / "explainer"
OUT = EXP / "worked_example_output"
FIG = EXP / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
LED = ROOT / "results" / "ledger"
K = B.K

# ------------------------------------------------------------------------------------------------ plotting style
BLUE, ORANGE, AQUA, GREY, INK, INK2 = "#2a78d6", "#eb6834", "#1baf7a", "#b8b6ae", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.titlesize": 11, "axes.titleweight": "bold", "figure.dpi": 150, "savefig.bbox": "tight",
                     "font.family": "DejaVu Sans"})


def savefig(fig, name):
    fig.savefig(FIG / name, facecolor="white")
    plt.close(fig)
    log(f"figure {name}")


# ------------------------------------------------------------------------------------------------ outputs + checks
CHECKS: list[dict] = []
SUMMARY: dict = {"gene": GENE, "control": CTRL, "gate": GATE}


def tsv(df: pd.DataFrame, name: str):
    df.to_csv(OUT / name, sep="\t", index=False, float_format="%.6g")


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def check(step: str, quantity: str, ours, ref, source: str, rtol: float = 1e-5, atol: float = 1e-6):
    """Record one reproduction check (ledger floats are written with %.6g, hence the relative tolerance)."""
    if isinstance(ref, str) and np.isfinite(num(ref)) and not isinstance(ours, (str, bool, np.bool_)):
        ref = num(ref)              # numeric value read from a string-typed table
    if isinstance(ref, (str, bool, np.bool_)) or isinstance(ours, (str, bool, np.bool_)):
        o, r = str(ours), str(ref)
        if isinstance(ref, (bool, np.bool_)) or o in ("True", "False") or r in ("True", "False"):
            o, r = str(o).lower() in ("true", "1"), str(r).lower() in ("true", "1")
        ok = o == r
    else:
        o, r = num(ours), num(ref)
        ok = (np.isnan(o) and np.isnan(r)) or (np.isfinite(o) and np.isfinite(r) and abs(o - r) <= atol + rtol * abs(r))
    CHECKS.append(dict(step=step, quantity=quantity, this_run=ours, committed=ref, source=source,
                       match="yes" if ok else "NO"))
    if not ok:
        log(f"MISMATCH {step} {quantity}: ours {ours} vs committed {ref} ({source})")


def ledger_row(name: str, hgnc: str, **kw) -> pd.Series:
    d = M6.read_tsv(name, **kw)
    return d[d.hgnc_id == hgnc].iloc[0]


# ================================================================================================ base data
base = B.Base()
gt, G, onto = base.gt, base.G, base.onto
g = int(np.flatnonzero(gt.symbol.values == GENE)[0])
H = gt.hgnc_id.values[g]
SUMMARY["matrix_index"] = g
SUMMARY["hgnc_id"] = H
log(f"{GENE}: matrix index {g}, {H}")
PRED = ledger_row("u_predictions.tsv", H)
PCAL = ledger_row("u_pcal.tsv", H)
TIER = ledger_row("tiers_all.tsv", H)

# ================================================================================================ step 0
log("step 0: pre-registration")
UP = pd.read_csv(ROOT / M6.U_TSV, sep="\t", dtype=str, keep_default_na=False)
u = UP[UP.hgnc_id == H].iloc[0]
s0 = {c: u[c] for c in ["hgnc_id", "symbol", "location", "D1", "n_d1_terms_informative", "n_d1_terms_generic",
                        "n_d1_rows", "D2", "annotation_score", "D3", "D3_pubmed", "D3_tdark", "n_pubmed_focused",
                        "n_pubmed_all", "tdl", "in_depmap", "scorable", "family_stratum", "expressed", "core",
                        "headline_stratum"]}
s0["U_rule"] = "U = D1 and (D2 or D3)"
s0["in_U_by_rule"] = (u.D1 == "True") and (u.D2 == "True" or u.D3 == "True")
# the D1 rows themselves: knownness.d1 (the single D1 implementation) on the pre-registration GAF/obo, this gene only
d1pg, d1ann, _ = kn.d1(str(ROOT / M5.GAF_CUR), onto, "current (pre-registration release)", base.acc_map,
                       universe=[H])
d1rows = d1ann[d1ann.hgnc_id == H].copy()
d1rows["term_name"] = d1rows.go_id.map(onto.name)
d1rows["generic"] = d1rows.go_id.isin(kn.GENERIC)
tsv(d1rows[["hgnc_id", "go_id", "term_name", "aspect", "evidence", "reference", "generic"]], "step0_d1_rows.tsv")
check("0", "D1 (no informative BP/MF term with experimental evidence)", bool(d1pg.loc[H, "D1"]), u.D1 == "True",
      "preregistration/uncharacterised_genes.tsv")
check("0", "n_d1_rows", int(d1pg.loc[H, "n_d1_rows"]), int(u.n_d1_rows), "preregistration/uncharacterised_genes.tsv")
check("0", "n_d1_terms_generic", int(d1pg.loc[H, "n_d1_terms_generic"]), int(u.n_d1_terms_generic),
      "preregistration/uncharacterised_genes.tsv")
SUMMARY["step0"] = s0
lit = (ROOT / "results/m7/L/HGNC_26614.md").read_text()
SUMMARY["step0"]["literature_novelty_class_L"] = [x.split(": ")[1] for x in lit.splitlines()
                                                  if x.startswith("novelty_class")][0]

# ================================================================================================ step 1
log("step 1: input profile")
effect = C.load_effect()
assert list(effect.columns) == list(gt.gene.values)
x = effect.iloc[:, g].values.astype(np.float64)
ok = np.isfinite(x)
s1 = dict(depmap_column=gt.gene.values[g], n_lines_total=int(len(x)), n_lines_observed=int(ok.sum()),
          nan_fraction=float(1 - ok.mean()), mean_effect=float(np.nanmean(x)), sd_effect=float(np.nanstd(x)),
          n_lines_lt_m0p5=int((x[ok] < -0.5).sum()), frac_lines_lt_m0p5=float((x[ok] < -0.5).mean()),
          min_effect=float(np.nanmin(x)), median_effect=float(np.nanmedian(x)),
          tool_background=bool(base.bg[g]))
check("1", "cell lines with a value", s1["n_lines_observed"], int(u.n_obs), "preregistration/uncharacterised_genes.tsv")
check("1", "mean gene effect", s1["mean_effect"], u.chronos_mean, "preregistration/uncharacterised_genes.tsv")
check("1", "SD of gene effect", s1["sd_effect"], u.chronos_sd, "preregistration/uncharacterised_genes.tsv")
check("1", "fraction of lines < -0.5", s1["frac_lines_lt_m0p5"], PRED.frac_lines_lt_m0p5,
      "results/ledger/u_predictions.tsv")
# expression: splithalf.expression_strata (the §1.4 function used by scripts/15) on this gene's column
EXPR = "data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"
hdr = pd.read_csv(ROOT / EXPR, nrows=0).columns
ecol = [c for c in hdr if c.startswith(f"{GENE} (")][0]
ex = pd.read_csv(ROOT / EXPR, usecols=["ModelID", "IsDefaultEntryForModel", ecol])
ex = ex[ex.IsDefaultEntryForModel == "Yes"]
lin = pd.read_csv(ROOT / "data/raw/depmap/Model.csv", usecols=["ModelID", "OncotreeLineage"]).set_index("ModelID")
es = sh.expression_strata(ex[[ecol]].to_numpy(np.float64), lin.OncotreeLineage.reindex(ex.ModelID.values).values,
                          **dict(expr_min=C.fz("strata", "expressed_log2tpm1_min"),
                                 expr_frac=C.fz("strata", "expressed_min_line_fraction"),
                                 neg_max=C.fz("strata", "clean_negative_log2tpm1_max"),
                                 neg_frac=C.fz("strata", "clean_negative_min_line_fraction"),
                                 lin_frac=C.fz("strata", "lineage_restricted_min_line_fraction"),
                                 lin_min_lines=C.fz("strata", "lineage_restricted_min_lines_per_lineage"))).iloc[0]
ev = ex[ecol].to_numpy(np.float64)
s1.update(expr_n_models=int(es.n_models), expr_frac_log2tpm1_ge1=float(es.frac_ge_expr),
          expr_median_log2tpm1=float(np.nanmedian(ev)), expressed=bool(es.expressed),
          clean_negative=bool(es.clean_negative))
check("1", "expression: fraction of models log2(TPM+1) >= 1", s1["expr_frac_log2tpm1_ge1"], u.expr_frac_ge1,
      "preregistration/uncharacterised_genes.tsv")
check("1", "expression: median log2(TPM+1)", s1["expr_median_log2tpm1"], u.expr_median_log2tpm1,
      "preregistration/uncharacterised_genes.tsv")
check("1", "expressed flag", s1["expressed"], u.expressed == "True", "preregistration/uncharacterised_genes.tsv")
SUMMARY["step1"] = s1
del ex

# ================================================================================================ step 2
log("step 2: co-essentiality neighbours")
Mz, mgt = cm.open_matrix(C.FULL_DIR, "zavg_BEF")
assert (mgt.gene.values == gt.gene.values).all()
row = np.asarray(Mz[g], dtype=np.float64)
# N(g) exactly as scripts/13: neighbours.top_k with BG, same-arm and paralogue exclusions
nb = nbm.top_k(Mz, 100, rows=np.array([g]), bg=base.bg, arm=base.arm, paralogues=base.par)
nbm.assert_valid(nb, bg=base.bg, arm=base.arm, paralogues=base.par)
ids, zz = nb.ids[0, :K], nb.z[0, :K]
assert (ids == base.ids100[g, :K]).all() and np.allclose(zz, base.z100[g, :K])
check("2", "N(g) (25 neighbours, order) recomputed from the matrix == stored full_top100.npz", "identical",
      "identical", "data/derived/neighbours/full_top100.npz")
# the same row with only self excluded: what did the exclusions remove?
nb0 = nbm.top_k(Mz, 100, rows=np.array([g]))
arm_g = base.cov.arm.values[g]
par_g = set(base.par.get(g, np.array([], int)).tolist())
cut = float(zz[-1])
order_all = np.argsort(-np.where(np.isfinite(row), row, -np.inf), kind="stable")
rank_all = {int(j): i + 1 for i, j in enumerate(order_all)}
removed = []
for j, s in zip(nb0.ids[0], nb0.z[0]):
    j = int(j)
    if j < 0 or s < cut or j in set(ids.tolist()):
        continue
    why = [w for w, f in [("not tool background (NaN fraction >= 0.10)", not base.bg[j]),
                          (f"same chromosome arm ({arm_g})", base.cov.arm.values[j] == arm_g),
                          ("Ensembl paralogue", j in par_g)] if f]
    removed.append(dict(gene=gt.symbol.values[j], zavg_BEF=float(s), rank_without_exclusions=rank_all[j],
                        location=base.cov.location.values[j] if "location" in base.cov else "",
                        arm=base.cov.arm.values[j], reason="; ".join(why)))
for j in sorted(par_g):              # every paralogue, wherever it ranks
    if gt.symbol.values[j] not in {r["gene"] for r in removed}:
        removed.append(dict(gene=gt.symbol.values[j], zavg_BEF=float(row[j]), rank_without_exclusions=rank_all.get(j),
                            location="", arm=base.cov.arm.values[j],
                            reason="Ensembl paralogue (would not have entered the top 25 anyway)"))
REM = pd.DataFrame(removed)
tsv(REM, "step2_excluded_genes.tsv")
same_arm_total = int(((base.cov.arm.values == arm_g) & base.bg).sum()) - 1
SUMMARY["step2"] = dict(arm=arm_g, n_paralogues_in_matrix=len(par_g), paralogues=[gt.symbol.values[j] for j in
                                                                                    sorted(par_g)],
                        n_bg_genes_same_arm=same_arm_total, kth_score=cut, n_removed_above_cutoff=int(
                            (REM.rank_without_exclusions.notna() & (REM.zavg_BEF >= cut)).sum()) if len(REM) else 0,
                        n_bg_genes=int(base.bg.sum()), zmean_top25=float(np.mean(zz)),
                        row_quantiles={q: float(np.nanquantile(row[base.bg], q)) for q in (0.5, 0.99, 0.999)})
# z_B / z_E / z_F for the top-10 partners from the tool's pair scorer (as scripts/40, refitted at published Config)
log("refitting the tool (published Config) for the pair scorer ...")
fm = cm.fit_model(effect, cm.PUBLISHED_CONFIG)
assert not fm.dropped_genes and list(fm.genes) == list(gt.gene.values)
zavg10, Z10 = fm.model.zavg(np.full(K, g), ids.astype(np.int64))
SUMMARY["step2"]["tool"] = dict(n_lines=int(fm.model.n_lines) if hasattr(fm.model, "n_lines") else len(effect),
                                K_tool=int(fm.model.K), n_bg=int(fm.model.n_bg))
PT = M6.read_tsv("u_partners.tsv")
PT = PT[PT.hgnc_id == H].set_index("rank")
mean_eff = np.nanmean(effect.values, 0)
frac_dep = np.nanmean(effect.values < -0.5, 0)
nrows = []
for k in range(K):
    j = int(ids[k])
    nrows.append(dict(rank=k + 1, partner=gt.symbol.values[j], partner_hgnc_id=gt.hgnc_id.values[j],
                      zavg_BEF=float(zz[k]), z_B=float(Z10["B"][k]), z_E=float(Z10["E"][k]), z_F=float(Z10["F"][k]),
                      zavg_pair_scorer=float(zavg10[k]), arm=base.cov.arm.values[j],
                      partner_mean_effect=float(mean_eff[j]), partner_frac_lt_m0p5=float(frac_dep[j])))
NB = pd.DataFrame(nrows)
for k in range(1, 11):
    r = NB.iloc[k - 1]
    check("2", f"partner {k} symbol", r.partner, PT.loc[k, "partner_symbol"], "results/ledger/u_partners.tsv")
    for c in ("zavg_BEF", "z_B", "z_E", "z_F"):
        check("2", f"partner {k} ({r.partner}) {c}", r[c] if c != "zavg_BEF" else r.zavg_BEF, PT.loc[k, c],
              "results/ledger/u_partners.tsv", rtol=1e-4, atol=1e-3)
del fm

# ================================================================================================ step 3
log("step 3: assessability")
KA = C.fz("assessability", "half_list_k")
NNULL = C.fz("assessability", "null_genes")
SEEDS = C.fz("assessability", "split_seeds")
SH = C.DERIVED / "splithalf"
pairs, bg_full = [], gt.bg.values.astype(bool)
for s in SEEDS:                      # as scripts/15: top-60 half lists -> common BG -> first K
    zs = [np.load(SH / f"seed{s}_half{h}.npz") for h in (0, 1)]
    common = zs[0]["bg_half"].astype(bool) & zs[1]["bg_half"].astype(bool) & bg_full
    pairs.append(tuple(sh.restrict_lists(z["ids"].astype(np.int64), common, KA) for z in zs))
matches200 = {g: base.matches[g][:NNULL]}
Rv, R0 = sh.reproducibility(pairs, KA, matches200)
Pv = sh.conservative_p(Rv, R0, n_seeds=len(SEEDS), K=KA).set_index("gene")
per_seed = []
for s, (a, b) in zip(SEEDS, pairs):
    sa, sb = set(a[g][a[g] >= 0].tolist()), set(b[g][b[g] >= 0].tolist())
    both = sa & sb
    per_seed.append(dict(seed=s, overlap=len(both), overlap_frac=len(both) / KA,
                         shared_neighbours=",".join(sorted(gt.symbol.values[list(both)]))))
PS = pd.DataFrame(per_seed)
tsv(PS, "step3_splithalf_overlap_by_seed.tsv")
r0 = np.asarray(R0[g], float)
tsv(pd.DataFrame(dict(matched_gene=gt.symbol.values[matches200[g]], R0=r0)), "step3_R0_matched200.tsv")
AS = pd.read_csv(ROOT / M6.ASSESS, sep="\t", dtype={"hgnc_id": str})
a = AS[AS.hgnc_id == H].iloc[0]
s3 = dict(R=float(Rv[g]), R0_mean=float(r0.mean()), R0_max=float(r0.max()), n_R0_ge_R=int(Pv.loc[g, "n_R0_ge_R"]),
          p=float(Pv.loc[g, "p"]), alpha=C.fz("assessability", "alpha"), expressed=bool(a.expressed),
          expressed_design=bool(a.expressed_design), assessable=bool(Pv.loc[g, "p"] < 0.05 and a.expressed),
          K=KA, n_matched=NNULL, seeds=SEEDS)
SUMMARY["step3"] = s3
check("3", "R(g) split-half reproducibility", s3["R"], a.R, "results/assessability/assessability_U.tsv")
check("3", "mean R0 over 200 matched genes", s3["R0_mean"], a.R0_mean, "results/assessability/assessability_U.tsv")
check("3", "max R0", s3["R0_max"], a.R0_max, "results/assessability/assessability_U.tsv")
check("3", "#{R0 >= R}", s3["n_R0_ge_R"], a.n_R0_ge_R, "results/assessability/assessability_U.tsv")
check("3", "empirical p", s3["p"], a.p, "results/assessability/assessability_U.tsv")
check("3", "assessable", s3["assessable"], bool(a.assessable), "results/assessability/assessability_U.tsv")
check("3", "R(g) used by the ledger", s3["R"], PRED.R, "results/ledger/u_predictions.tsv")

# ================================================================================================ step 4
log("step 4: function assignment (V2 current)")
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
sc = vocab.score_queries(v2, base.nb, base.matches, np.array([g]), loo=False)
r1 = sc.ranked("R1")[g]
fams = B.load_families()
tab = sc.table[sc.table["query"] == g].copy()
tab["go_id"] = v2.terms[tab.term.astype(int).values]
tab["term_name"] = tab.go_id.map(onto.name)
tab["size"] = sc.sizes[0, tab.term.astype(int).values]
tab["family"] = [B.family_of(t, onto, fams) for t in tab.go_id]
tab = tab.sort_values(["rank_R1", "S"], ascending=[True, False], na_position="last")
tsv(tab[["go_id", "term_name", "size", "S", "n_sup", "x", "n_draw", "p_hyper", "p_emp", "reportable", "rank_R1",
         "family"]], "step4_term_scores_all.tsv")
info = sc.info.iloc[0].to_dict()
top = r1[0]
top_id = v2.terms[top]
sup_top = M6.supporting(v2, g, top, ids, zz)
sup_set = {j for j, _ in sup_top}
# neighbour x top-5 term membership (supporting = annotated to the term, z > 0, after the IPI with/from rule)
mem = {}
for c in r1[:5]:
    mem[v2.terms[c]] = {j for j, _ in M6.supporting(v2, g, c, ids, zz)}
NB["supports_top_term"] = [int(j) in sup_set for j in ids]
NB["n_v2_terms"] = [int(v2.A[int(j)].sum()) for j in ids]
for t_, s_ in mem.items():
    NB[f"in_{t_}"] = [int(j) in s_ for j in ids]
tsv(NB, "step2_neighbours_top25.tsv")
top5 = []
for k, c in enumerate(r1[:5]):
    xx = tab[tab.term == c].iloc[0]
    top5.append(dict(rank=k + 1, go_id=v2.terms[c], term_name=onto.name(v2.terms[c]), S=float(xx.S),
                     n_sup=int(xx.n_sup), x=int(xx.x), size=int(xx["size"]), p_hyper=float(xx.p_hyper),
                     family=xx.family,
                     supporting_partners=",".join(gt.symbol.values[sorted(mem[v2.terms[c]],
                                                                          key=lambda j: -row[j])])))
T5 = pd.DataFrame(top5)
tsv(T5, "step4_top5_terms.tsv")
U5 = M6.read_tsv("u_top5.tsv")
U5 = U5[U5.hgnc_id == H].set_index("rank")
for r in T5.itertuples():
    check("4", f"top-5 term {r.rank}", r.go_id, U5.loc[r.rank, "term"], "results/ledger/u_top5.tsv")
    check("4", f"top-5 term {r.rank} S", r.S, U5.loc[r.rank, "S"], "results/ledger/u_top5.tsv")
    check("4", f"top-5 term {r.rank} supporting partners", r.n_sup, U5.loc[r.rank, "n_sup"], "results/ledger/u_top5.tsv")
check("4", "top term", top_id, PRED.top_term, "results/ledger/u_predictions.tsv")
check("4", "top term S", T5.S[0], PRED.top_S, "results/ledger/u_predictions.tsv")
check("4", "top term size (per query)", T5["size"][0], PRED.top_size, "results/ledger/u_predictions.tsv")
check("4", "top term hypergeometric p", T5.p_hyper[0], PRED.top_p_hyper, "results/ledger/u_predictions.tsv", rtol=1e-4)
check("4", "number of reportable terms (>= 2 supporting partners)", len(r1), PRED.n_reportable,
      "results/ledger/u_predictions.tsv")
check("4", "S = sum of positive z of supporting partners", sum(z for _, z in sup_top), PRED.top_S,
      "results/ledger/u_predictions.tsv")
for k in range(1, 11):
    check("4", f"partner {k} supports top term", bool(NB.supports_top_term[k - 1]),
          PT.loc[k, "supporting_top_term"], "results/ledger/u_partners.tsv")
ms = pr.most_specific([v2.terms[c] for c in r1[:5]], onto.ancestors)[0]
check("4", "most specific term among the top 5 (descriptive)", ms, PRED.most_specific_top5,
      "results/ledger/u_predictions.tsv")
fam = B.family_of(top_id, onto, fams)
check("4", "module family of the top term", fam, PRED.family, "results/ledger/u_predictions.tsv")
# descriptive module labels V1 (GO CC complexes) and V1' (V1 + Complex Portal + MitoCarta)
v1 = B.build_v1(base, M5.GAF_CUR, label="current")
v1p, v1p_names = B.build_v1prime(base, v1, B.LO, B.HI)
l1 = vocab.score_queries(v1, base.nb, base.matches, np.array([g]), loo=False).ranked("R1")[g]
scp = vocab.score_queries(v1p, base.nb, base.matches, np.array([g]), loo=False)
lp = scp.ranked("R1")[g]
v1_label = v1.terms[l1[0]] if l1 else ""
v1p_label = v1p.terms[lp[0]] if lp else ""
check("4", "V1 module label", v1_label, PRED.v1_label, "results/ledger/u_predictions.tsv")
check("4", "V1' module label", v1p_label, PRED.v1p_label, "results/ledger/u_predictions.tsv")
v1p_sup = {j for j, _ in M6.supporting(v1p, g, lp[0], ids, zz)} if lp else set()
SUMMARY["step4"] = dict(n_candidate_terms=int(info["n_candidates"]), n_terms_with_S=int(info["n_terms_S"]),
                        n_reportable=len(r1), n_draw_annotated_neighbours=int(info["n_draw"]),
                        population_annotated_background=int(info["population"]),
                        n_ipi_partner_genes_with_rows_removed=int(info["n_ipi_genes"]), top_term=top_id,
                        top_term_name=onto.name(top_id), family=fam, most_specific_top5=ms,
                        most_specific_top5_name=onto.name(ms),
                        supporting_partners=[gt.symbol.values[j] for j, _ in sup_top],
                        v1_label=v1_label, v1_label_name=onto.name(v1_label) if v1_label else "",
                        v1p_label=v1p_label, v1p_label_n_sup=len(v1p_sup),
                        vocabulary=dict(n_columns=int(v2.stats["n_columns"]),
                                        n_candidate_terms=int(v2.stats["n_candidate_terms_base"]),
                                        n_annotated_background=int(v2.stats["n_annotated_background"]),
                                        window=[B.LO, B.HI]))

# ================================================================================================ step 5
log("step 5: calibration covariates and p_cal")
cov = B.coverage(base, v2)
cov_pct = B.pct_rank(cov, cov[base.scor])
ref_size = B.base_top_sizes(base, v2)[base.scor]
core = pd.read_pickle(C.DERIVED / "holdout_eval" / "core.pkl")
check("5", "coverage reference (all genes) == M5b current coverage", bool(np.allclose(cov, core["cov_cur"],
                                                                                     equal_nan=True)), True,
      "data/derived/holdout_eval/core.pkl")
check("5", "top-term size reference (all scorable genes) == M5b reference",
      bool(np.allclose(ref_size, core["ref_size_cur"][base.scor], equal_nan=True)), True,
      "data/derived/holdout_eval/core.pkl")
ref_log = np.log(ref_size[np.isfinite(ref_size)])
covs = dict(zmean=float(base.zmean[g]), R=float(base.R[g]), coverage=float(cov[g]), cov_pct=float(cov_pct[g]),
            size_pct=float(B.pct_rank(np.log([T5["size"][0]]), ref_log)[0]), family=fam)
MOD = M6.model()
st = MOD["standardised"]
xrow = LG.design_row(covs, MOD)
p_cal = float(LG.pcal_from_model(pd.DataFrame([covs]), MOD)[0])
cat = LG.support_category(covs, MOD["support"]["bounds_5_95"], MOD["families_kept"])
contrib = []
w, mu, sd = np.asarray(st["w"]), np.asarray(st["mu"]), np.asarray(st["sd"])
for k, name in enumerate(MOD["covariates"]):
    zst = (xrow[k] - mu[k]) / sd[k]
    contrib.append(dict(covariate=name, value=float(xrow[k]), H_mean=float(mu[k]), H_sd=float(sd[k]),
                        standardised=float(zst), weight=float(w[k + 1]), logit_contribution=float(w[k + 1] * zst),
                        coef_original_scale=float(MOD["coef"][name]), sign_constraint=int(MOD["signs"][k]),
                        H_P5=MOD["support"]["bounds_5_95"].get(name, [np.nan])[0],
                        H_P95=MOD["support"]["bounds_5_95"].get(name, [np.nan, np.nan])[1]))
contrib.append(dict(covariate="intercept (standardised scale)", logit_contribution=float(w[0])))
CT = pd.DataFrame(contrib)
tsv(CT, "step5_pcal_contributions.tsv")
logit = float(CT.logit_contribution.sum())
SUMMARY["step5"] = dict(covariates=covs, support_category=cat, logit=logit, p_cal=p_cal,
                        H_fit=dict(n_fit=MOD["n_fit"], n_hits=MOD["n_hits"], hit_rate=MOD["n_hits"] / MOD["n_fit"]))
for c in ("zmean", "R", "coverage", "cov_pct", "size_pct"):
    check("5", f"covariate {c}", covs[c], PRED[c], "results/ledger/u_predictions.tsv")
check("5", "support category", cat, PCAL.support_category, "results/ledger/u_pcal.tsv")
check("5", "p_cal", p_cal, PCAL.p_cal, "results/ledger/u_pcal.tsv")
check("5", "p_cal (tiers table)", p_cal, TIER.p_cal, "results/ledger/tiers_all.tsv")
# rank in the primary top 40 (logic of scripts/46: pool, exclusions, p_cal order, mito cap)
TA = pd.read_csv(LED / "tiers_all.tsv", sep="\t")


def as_bool(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


pool = TA[as_bool(TA.has_prediction) & as_bool(TA.expressed_design) & as_bool(TA.assessable_design)
          & (TA.support_category == "in_support")].copy()
pool["excluded"] = as_bool(pool.excl43) | as_bool(pool.contradiction)
elig = pool[~pool.excluded].sort_values(["p_cal", "symbol"], ascending=[False, True]).reset_index(drop=True)
rank40 = int(np.flatnonzero(elig.symbol.values == GENE)[0]) + 1
SUMMARY["step5"].update(top40_rank=rank40, n_pool=len(pool), n_eligible=len(elig),
                        tier=str(TIER.tier) if isinstance(TIER.tier, str) else "",
                        tier_thresholds=dict(A=C.fz("tiers", "tier_a_pcal_min"), B=C.fz("tiers", "tier_b_pcal_min")),
                        n_U_with_pcal=int(M6.read_tsv("u_pcal.tsv").p_cal.notna().sum()))
TP = pd.read_csv(LED / "top40_primary.tsv", sep="\t")
check("5", "rank in primary top 40", rank40, int(TP.loc[TP.symbol == GENE, "rank"].iloc[0]),
      "results/ledger/top40_primary.tsv")

# ================================================================================================ step 6
log("step 6: orthogonal support (fresh run; the on-disk cache is not used or written)")
runner = M6.SupportRunner()
runner.cache = {}                    # recompute; runner.save() is never called
Pall = M6.read_tsv("u_predictions.tsv")
cands = M6.decoy_candidates(Pall, v2)
srows = M6.support_for(dict(hgnc_id=H, symbol=GENE, pos=g, term=top_id, family=fam), runner, v2, base, cands, onto)
SR = pd.DataFrame(srows)
tsv(SR, "step6_support_real_matched_decoy.tsv")
SC = pd.read_csv(LED / "support.tsv", sep="\t")
SC = SC[SC.anchor_symbol == GENE].set_index("set")
for r in SR.itertuples():
    check("6", f"{r.set}: tested gene", r.tested_symbol, SC.loc[r.set, "tested_symbol"], "results/ledger/support.tsv")
    check("6", f"{r.set}: term", r.term, SC.loc[r.set, "term"], "results/ledger/support.tsv")
    for c in ("P", "A", "L", "G", "S"):
        check("6", f"{r.set}: class {c} state", getattr(r, f"state_{c}"), SC.loc[r.set, f"state_{c}"],
              "results/ledger/support.tsv")
        if np.isfinite(num(getattr(r, f"p_{c}"))):
            check("6", f"{r.set}: class {c} Simes p", getattr(r, f"p_{c}"), SC.loc[r.set, f"p_{c}"],
                  "results/ledger/support.tsv")
    check("6", f"{r.set}: passes Tier-A support rule", bool(r.diag_ok), bool(SC.loc[r.set, "diag_ok"]),
          "results/ledger/support.tsv")
check("6", "diag_ok in tiers table", bool(SR.diag_ok[0]), bool(TIER.diag_ok), "results/ledger/tiers_all.tsv")
# per-source table (real prediction) and the pair-level hits behind it
src_tab = runner.cache[(H, top_id)]["sources"].copy()
members = [gt.hgnc_id.values[j] for j in M6.term_members(v2, v2.col[top_id]) if j != g]
sym_of = dict(zip(gt.hgnc_id.values, gt.symbol.values))
hits = []
for s in runner.sources:
    if s.kind in ("binary", "pair_binary") and H in s.index:
        nbr = set(np.asarray(s.genes)[s.adj[s.index[H]].indices].tolist())
        hits.append(dict(source=s.name, cls=s.cls, kind=s.kind,
                         member_hits=",".join(sorted(sym_of.get(m, m) for m in set(members) & nbr)),
                         n_edges_of_gene=len(nbr),
                         coessential_neighbours_with_edge=",".join(
                             sym_of[x] for x in gt.hgnc_id.values[ids] if x in nbr)))
    elif s.kind == "continuous" and H in s.index:
        pr_ = np.asarray(s.row_percentiles()[s.index[H]], float)
        mm = sorted(((pr_[s.index[m]], sym_of.get(m, m)) for m in members if m in s.index
                     and np.isfinite(pr_[s.index[m]])), reverse=True)[:5]
        nn = sorted(((pr_[s.index[x]], sym_of[x]) for x in gt.hgnc_id.values[ids] if x in s.index
                     and np.isfinite(pr_[s.index[x]])), reverse=True)[:5]
        hits.append(dict(source=s.name, cls=s.cls, kind=s.kind,
                         member_hits="top members by percentile in the gene's row: "
                         + ", ".join(f"{n} {p:.3f}" for p, n in mm),
                         coessential_neighbours_with_edge="top N(g) partners by percentile: "
                         + ", ".join(f"{n} {p:.3f}" for p, n in nn)))
    elif s.kind == "localisation":
        gc = s.comp.get(H)
        hits.append(dict(source=s.name, cls=s.cls, kind=s.kind,
                         member_hits=f"gene compartments: {sorted(gc) if gc else 'not localised'}"))
HT = pd.DataFrame(hits)
src_tab = src_tab.merge(HT, left_on="source", right_on="source", how="left", suffixes=("", "_h"))
tsv(src_tab, "step6_support_sources_real.tsv")
cd = runner.cache[(H, top_id)]["contradiction_detail"] or {}
SUMMARY["step6"] = dict(n_term_members_tested=len(members), class_state=runner.cache[(H, top_id)]["class_state"],
                        class_p=runner.cache[(H, top_id)]["class_p"], holm_alpha=runner.alpha,
                        null_sets=runner.B, diagnostic_classes=list(LG.DIAGNOSTIC.get(fam, LG.DIAGNOSTIC["other"])),
                        contradiction=dict(cd), passes_rule=bool(SR.diag_ok[0]),
                        matched_gene=SR.tested_symbol[1] if len(SR) > 1 else "",
                        decoy_term=SR.term_name[2] if len(SR) > 2 else "")

# ================================================================================================ step 7
log("step 7: blinded literature judging")
spec = importlib.util.spec_from_file_location("judge52", ROOT / "scripts" / "52_judge_analysis.py")
J52 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(J52)        # import only (main() is guarded; nothing is written)
SJ = J52.load_scores(["main1", "main2", "main3"])
pk = pd.read_csv(ROOT / "results/m7/judge/packet_key.tsv", sep="\t")
jid = pk.loc[pk.hgnc_id == H, "J_id"].iloc[0]
ak = pd.read_csv(ROOT / "results/m7/answer_key_slots.tsv", sep="\t")
ak = ak[ak.hgnc_id == H]
jrows = []
for r in ak.itertuples():
    s1_, s2_ = SJ["J1"].get((jid, r.slot), np.nan), SJ["J2"].get((jid, r.slot), np.nan)
    fin = s1_ if s1_ == s2_ else SJ.get("ADJ", pd.Series(dtype=float)).get((jid, r.slot), np.nan)
    jrows.append(dict(packet=jid, slot=r.slot, is_real=r.is_real, statement=r.statement, term=r.term,
                      term_size=r.size, decoy_donor=r.donor_symbol if not r.is_real else "",
                      judge1=s1_, judge2=s2_, final=fin))
JR = pd.DataFrame(jrows)
tsv(JR, "step7_judging.tsv")
real = float(JR.final[JR.is_real].iloc[0])
dmean = float(JR.final[~JR.is_real].mean())
AJ = pd.read_csv(ROOT / "results/m7/judge/analysis_main_genes.tsv", sep="\t")
aj = AJ[AJ.hgnc_id == H].iloc[0]
check("7", "real statement score", real, aj.real, "results/m7/judge/analysis_main_genes.tsv")
check("7", "mean decoy score", dmean, aj.decoy_mean, "results/m7/judge/analysis_main_genes.tsv")
check("7", "d = real - mean(decoys)", real - dmean, aj.d, "results/m7/judge/analysis_main_genes.tsv")
Ltab = [ln for ln in lit.splitlines() if ln.startswith("| ") and not ln.startswith("| #") and "---" not in ln]
LT = pd.DataFrame([dict(item=c[1].strip(), claim_paraphrase=c[2].strip(), source=c[3].strip(), year=c[4].strip(),
                        evidence_level=c[6].strip(), depmap_derived=c[7].strip())
                   for c in (ln.split("|") for ln in Ltab)])
tsv(LT, "step7_literature_items.tsv")
probe = pd.read_csv(ROOT / "results/m7/recall_probe_90.tsv", sep="\t")
probe = probe[probe.hgnc_id == H]
SUMMARY["step7"] = dict(packet=jid, real_slot=JR.slot[JR.is_real].iloc[0], real=real, decoy_mean=dmean,
                        d=real - dmean, novelty_class=aj.nclass, n_literature_items=len(LT),
                        n_functional_items=int((LT.evidence_level == "functional").sum()),
                        recall_probe=probe.iloc[0].to_dict() if len(probe) else None)

# ================================================================================================ hold-out
log(f"hold-out example: {CTRL}")
gc_ = int(np.flatnonzero(gt.symbol.values == CTRL)[0])
hc = gt.hgnc_id.values[gc_]
v2t0 = B.build_v2(base, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
lo_w, hi_w = B.CASE_WINDOW
v2t0w = B.build_v2(base, f"{B.T0_DIR}/goa_human.gaf.gz", lo=lo_w, hi=hi_w, label="t0 window 2-300")
# (a) primary H setting (window 5-200), as scripts/32 main scoring
Sp = B.Scored(v2t0, base.nb, base.matches, [gc_], "TMEM242 t0 5-200")
lst_p = Sp.r1.get(gc_, [])
TT = pd.read_csv(ROOT / "results/holdout/H_targets.tsv", sep="\t", dtype={"support_pmids": str}, keep_default_na=False)
TTc = TT[TT.hgnc_id == hc]
tcols_p = {v2t0.col[t] for t in TTc.go_id if t in v2t0.col}
ranks_p = {v2t0.terms[c]: i + 1 for i, c in enumerate(lst_p) if c in tcols_p}
PG = pd.read_csv(ROOT / "results/holdout_eval/per_gene_core.tsv", sep="\t")
pg = PG[PG.symbol == CTRL].iloc[0]
check("H", "primary (5-200) top-1 term at t0", v2t0.terms[lst_p[0]] if lst_p else "", pg.top1_zavg,
      "results/holdout_eval/per_gene_core.tsv")
check("H", "primary hit@1", int(bool(lst_p) and lst_p[0] in tcols_p), int(pg.hit1_zavg),
      "results/holdout_eval/per_gene_core.tsv")
# (b) named-control case series (window 2-300), as scripts/32 'named controls'
cand_w = {t_ for t_, s_ in zip(v2t0w.terms, v2t0w.size) if lo_w <= s_ <= hi_w}
v2cur = v2
Tw = sorted((v2cur.prop.get(gc_, frozenset()) - v2t0w.prop.get(gc_, frozenset())) & cand_w)
Tpm = {t_: B.support_pmids(v2cur, gc_, t_) for t_ in Tw}
known = pd.concat([pd.read_csv(ROOT / "results/holdout/circularity_flags.tsv", sep="\t"),
                   pd.read_csv(ROOT / "results/calibration/loo_circularity_pmids.tsv.gz", sep="\t")])
allp = {p for ps in Tpm.values() for p in ps}
if allp <= set(known.pmid):
    flc = B.circ_lookup(allp)                       # all PMIDs known locally -> no network query
    stt = dict(zip(Tw, B.target_states(list(Tpm.values()), flc)))
    circ_note = "re-checked from local circularity tables"
else:
    stt = {t_: (False, False, False) for t_ in Tw}
    circ_note = "some PMIDs not in local tables; circularity not re-queried (committed file reports 0 flagged)"
Sw = B.Scored(v2t0w, base.nb, base.matches, [gc_], "TMEM242 t0 2-300")
drop_c = {v2t0w.col[t_] for t_ in Tw if stt[t_][0]}
lst = [c for c in Sw.r1.get(gc_, []) if c not in drop_c]
tcols = {v2t0w.col[t_] for t_ in Tw if not stt[t_][0]}
ranks = [i + 1 for i, c in enumerate(lst) if c in tcols]
best = min(ranks) if ranks else None
CS = pd.read_csv(ROOT / "results/holdout_eval/controls_case_series.tsv", sep="\t")
cs = CS[CS.symbol == CTRL].iloc[0]
check("H", "case series: number of later terms (window 2-300)", len(Tw), cs.n_targets_2_300,
      "results/holdout_eval/controls_case_series.tsv")
check("H", "case series: reportable terms at t0", len(lst), cs.n_reportable,
      "results/holdout_eval/controls_case_series.tsv")
check("H", "case series: rank of best later-annotated term", best, cs.rank_best_true_term,
      "results/holdout_eval/controls_case_series.tsv")
top_w = v2t0w.terms[lst[0]]
check("H", "case series: top-1 term at t0", f"{top_w} {onto.name(top_w)}", cs.top1_term,
      "results/holdout_eval/controls_case_series.tsv")
idc, zc = base.ids100[gc_, :K], base.z100[gc_, :K]
sup_c = {j for j, _ in M6.supporting(v2t0w, gc_, lst[0], idc, zc)}
cur_c = M6.term_members(v2cur, v2cur.col[top_w]) if top_w in v2cur.col else np.array([], int)
HN = pd.DataFrame(dict(rank=np.arange(1, K + 1), partner=gt.symbol.values[idc], zavg_BEF=zc,
                       annotated_to_top_term_at_t0=[int(j) in sup_c for j in idc],
                       annotated_to_top_term_now=[int(j) in set(cur_c.tolist()) for j in idc]))
tsv(HN, "holdout_TMEM242_neighbours.tsv")
TW = []
for i, c in enumerate(lst[:15]):
    t_ = v2t0w.terms[c]
    xx = Sw.sc.table[(Sw.sc.table["query"] == gc_) & (Sw.sc.table.term == c)].iloc[0]
    TW.append(dict(rank=i + 1, go_id=t_, term_name=onto.name(t_), S=float(xx.S), n_sup=int(xx.n_sup),
                   size_t0=int(Sw.sizes(gc_)[c]), later_annotated=c in tcols))
TW = pd.DataFrame(TW)
tsv(TW, "holdout_TMEM242_t0_terms.tsv")
LT_ = pd.DataFrame([dict(go_id=t_, term_name=onto.name(t_), size_t0=int(v2t0w.size[v2t0w.col[t_]]),
                         in_primary_window_5_200=B.LO <= int(v2t0w.size[v2t0w.col[t_]]) <= B.HI,
                         support_pmids="|".join(map(str, Tpm[t_])), circularity_flagged=bool(stt[t_][0]),
                         rank_at_t0=(lst.index(v2t0w.col[t_]) + 1) if v2t0w.col[t_] in lst else None)
                    for t_ in Tw])
tsv(LT_, "holdout_TMEM242_later_terms.tsv")
SUMMARY["holdout"] = dict(gene=CTRL, t0=B.T0, primary_top1=v2t0.terms[lst_p[0]] if lst_p else "",
                          primary_top1_name=onto.name(v2t0.terms[lst_p[0]]) if lst_p else "",
                          primary_targets=dict(zip(TTc.go_id, TTc.go_name)), primary_target_ranks=ranks_p,
                          primary_hit1=int(bool(lst_p) and lst_p[0] in tcols_p),
                          case_top1=top_w, case_top1_name=onto.name(top_w), case_rank_best=best,
                          case_n_later_terms=len(Tw), circularity=circ_note,
                          supporting_partners_t0=[gt.symbol.values[j] for j in idc if int(j) in sup_c],
                          zmean=float(base.zmean[gc_]), R=float(base.R[gc_]),
                          v1prime_label_committed=cs.top_v1prime_label)

# ================================================================================================ figures
log("figures")
# 1. neighbours
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 6.2), gridspec_kw=dict(width_ratios=[2.2, 1]))
yy = np.arange(K)[::-1]
cols = [BLUE if s else GREY for s in NB.supports_top_term]
ax.barh(yy, NB.zavg_BEF, color=cols, height=0.72)
ax.set_yticks(yy, [f"{r.rank:>2}  {r.partner}" for r in NB.itertuples()], fontsize=8.5)
ax.set_xlabel("co-essentiality score zavg_BEF with ANKRD52")
ax.set_title("N(g): the 25 neighbours used for prediction", loc="left")
ax.grid(axis="x", color="#e6e5e0", lw=0.6)
ax.set_axisbelow(True)
from matplotlib.patches import Patch  # noqa: E402
ax.legend(handles=[Patch(color=BLUE, label=f"annotated to the top term\n({onto.name(top_id)})"),
                   Patch(color=GREY, label="not annotated to it")], loc="lower right", frameon=False, fontsize=8.5)
R2 = REM.sort_values("zavg_BEF", ascending=True)
y2 = np.arange(len(R2))
ax2.barh(y2, R2.zavg_BEF, color=ORANGE, height=0.6)
ax2.axvline(cut, color=INK2, ls="--", lw=1)
ax2.text(cut, len(R2) - 0.4, f" 25th neighbour\n {cut:.1f}", fontsize=7.5, color=INK2, va="top")
ax2.set_yticks(y2, [f"{r.gene}\n({'paralogue' if 'paralogue' in r.reason else 'same arm' if 'arm' in r.reason else 'non-BG'})"
                    for r in R2.itertuples()], fontsize=8)
ax2.set_xlabel("zavg_BEF")
ax2.set_title("removed by the exclusions", loc="left")
ax2.grid(axis="x", color="#e6e5e0", lw=0.6)
ax2.set_axisbelow(True)
fig.tight_layout()
savefig(fig, "we_neighbours.png")

# 2. profiles
fig, axs = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
for axp, pn in zip(axs, ["AGO2", "PPP6C"]):
    jp = int(np.flatnonzero(gt.symbol.values == pn)[0])
    yv = effect.iloc[:, jp].values.astype(float)
    okp = np.isfinite(x) & np.isfinite(yv)
    rr = np.corrcoef(x[okp], yv[okp])[0, 1]
    axp.scatter(yv[okp], x[okp], s=7, alpha=0.45, color=BLUE, edgecolors="none")
    axp.axhline(-0.5, color=GREY, lw=0.8, ls=":")
    axp.axvline(-0.5, color=GREY, lw=0.8, ls=":")
    zp = float(row[jp])
    rk = rank_all.get(jp)
    axp.set_title(f"ANKRD52 vs {pn}", loc="left")
    axp.text(0.02, 0.03, f"Pearson r = {rr:.2f}\nzavg_BEF = {zp:.1f} (rank {rk} genome-wide)\n{okp.sum()} cell lines",
             transform=axp.transAxes, fontsize=8.5, color=INK, va="bottom")
    axp.set_xlabel(f"{pn} gene effect (Chronos)")
axs[0].set_ylabel("ANKRD52 gene effect (Chronos)")
fig.tight_layout()
savefig(fig, "we_profile.png")

# 3. assessability
fig, ax = plt.subplots(figsize=(7, 3.8))
bins = np.arange(0, max(r0.max(), s3["R"]) + 0.04, 0.008)
ax.hist(r0, bins=bins, color=GREY, label=f"R0: ANKRD52 half-A list vs the half-B list of\neach of its {NNULL} matched genes")
ax.axvline(s3["R"], color=ORANGE, lw=2.5)
ax.text(s3["R"], ax.get_ylim()[1] * 0.9, f"  R(ANKRD52) = {s3['R']:.3f}\n  p = 1/201 = {s3['p']:.4f}", color=INK,
        fontsize=9, va="top")
ax.set_xlabel("split-half neighbour overlap (mean over 5 seeds, fraction of K = 25)")
ax.set_ylabel("matched genes")
ax.set_title("Assessability: is the neighbourhood reproducible?", loc="left")
ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0.12, 0.98))
fig.tight_layout()
savefig(fig, "we_assessability.png")

# 4. term scores
TS = tab[tab.reportable.astype(bool)].sort_values("S", ascending=False).head(12)
TS = pd.concat([TS, tab[~tab.reportable.astype(bool)].sort_values("S", ascending=False).head(3)])
fig, ax = plt.subplots(figsize=(9.5, 5.6))
yy = np.arange(len(TS))[::-1]
colt = [ORANGE if t == top_id else (BLUE if rep else GREY) for t, rep in zip(TS.go_id, TS.reportable.astype(bool))]
ax.barh(yy, TS.S, color=colt, height=0.7)
for y_, r in zip(yy, TS.itertuples()):
    ax.text(r.S + 1.5, y_, f"{int(r.n_sup)} partner{'s' if int(r.n_sup) != 1 else ''}, size {int(r.size)}", va="center", fontsize=7.5, color=INK2)
ax.set_yticks(yy, [n if len(n) <= 62 else n[:60] + "..." for n in TS.term_name], fontsize=8)
ax.set_xlabel("term score S = sum of positive zavg_BEF of neighbours annotated to the term")
ax.set_title("Function assignment: GO term scores from the 25 neighbours", loc="left")
ax.legend(handles=[Patch(color=ORANGE, label="top reportable term (the prediction)"),
                   Patch(color=BLUE, label="other reportable terms (>= 2 supporting partners)"),
                   Patch(color=GREY, label="not reportable (1 supporting partner)")], frameon=False, fontsize=8,
          loc="lower right")
ax.set_xlim(0, TS.S.max() * 1.3)
ax.grid(axis="x", color="#e6e5e0", lw=0.6)
ax.set_axisbelow(True)
fig.tight_layout()
savefig(fig, "we_term_scores.png")

# 5. calibration
RB = pd.read_csv(ROOT / "results/holdout_eval/reliability_oof.tsv", sep="\t")
UPc = M6.read_tsv("u_pcal.tsv")
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
ax.plot([0, 0.25], [0, 0.25], color=GREY, lw=1, ls="--")
ax.errorbar(RB.mean_pred, RB.obs_rate, yerr=[RB.obs_rate - RB.ci_lo, RB.ci_hi - RB.obs_rate], fmt="o", color=BLUE,
            ms=6, capsize=2, lw=1)
ax.axvline(p_cal, color=ORANGE, lw=2)
ax.text(p_cal, 0.235, f" ANKRD52\n p_cal = {p_cal:.3f}", color=INK, fontsize=9, va="top")
ax.set_xlim(-0.005, 0.25)
ax.set_ylim(-0.005, 0.25)
ax.set_xlabel("predicted probability (out-of-fold, hold-out genes)")
ax.set_ylabel("observed fraction whose top term\nwas later annotated (Wilson 95% CI)")
ax.set_title("Calibration on the 2018 hold-out (deciles)", loc="left")
pc = UPc.p_cal.dropna()
ax2.hist(pc, bins=np.linspace(0, 0.15, 31), color=GREY)
ax2.axvline(p_cal, color=ORANGE, lw=2)
ax2.set_yscale("log")
ax2.text(p_cal, ax2.get_ylim()[1] * 0.6, f"ANKRD52 \n(highest of {len(pc)}) ", ha="right", fontsize=9, color=INK,
         va="top")
ax2.set_xlabel("p_cal")
ax2.set_ylabel("U genes (log scale)")
ax2.set_title("p_cal of all U genes in support", loc="left")
fig.tight_layout()
savefig(fig, "we_calibration.png")

# 6. support: class-level Simes p against the Holm step-down thresholds
cp_ = {c: v for c, v in runner.cache[(H, top_id)]["class_p"].items() if np.isfinite(v)}
ordc = sorted(cp_, key=cp_.get)
m_ = len(ordc)
fig, ax = plt.subplots(figsize=(8, 3.4))
ccl = {"P": BLUE, "A": AQUA, "L": ORANGE, "G": "#6250d6", "S": "#e87ba4"}
cname = {"P": "P  physical interaction", "A": "A  protein co-abundance", "L": "L  localisation",
         "G": "G  Perturb-seq", "S": "S  structure"}
yy = np.arange(m_)[::-1]
for y_, (i, c) in zip(yy, enumerate(ordc)):
    thr = 0.05 / (m_ - i)
    ax.barh(y_, -np.log10(cp_[c]), color=ccl[c], height=0.55)
    ax.plot([-np.log10(thr)] * 2, [y_ - 0.38, y_ + 0.38], color=INK, lw=2)
    ax.text(max(-np.log10(cp_[c]), -np.log10(thr)) + 0.04, y_,
            f"Simes p = {cp_[c]:.3f}  vs Holm threshold {thr:.4f}", va="center", fontsize=8, color=INK2)
ax.set_yticks(yy, [cname[c] for c in ordc], fontsize=9)
ax.set_xlim(0, 3.2)
ax.set_xlabel("-log10 class p (black tick = Holm step-down threshold; bar must pass it)")
ax.set_title("Orthogonal evidence for ANKRD52 -> ncRNA-mediated silencing", loc="left")
ax.text(0, -0.32, "G and S classes: not measured for ANKRD52. No class passes, so the state is 'no support' for "
        "P, A and L.", fontsize=8, color=INK2, transform=ax.transAxes, va="top")
ax.grid(axis="x", color="#e6e5e0", lw=0.6)
ax.set_axisbelow(True)
fig.tight_layout()
savefig(fig, "we_support.png")

# 7. hold-out TMEM242
fig, ax = plt.subplots(figsize=(9, 4.6))
TWp = TW.head(10)
yy = np.arange(len(TWp))[::-1]
ax.barh(yy, TWp.S, color=[ORANGE if v else GREY for v in TWp.later_annotated], height=0.7)
for y_, r in zip(yy, TWp.itertuples()):
    ax.text(r.S + 1, y_, f"{r.n_sup} partners, size {r.size_t0}", va="center", fontsize=7.5, color=INK2)
ax.set_yticks(yy, [n[:55] for n in TWp.term_name], fontsize=8)
ax.set_xlabel("term score S (neighbours annotated as of GO 2018-07-02)")
ax.set_title("Hold-out control TMEM242: 2018 term ranking vs terms added later", loc="left")
ax.legend(handles=[Patch(color=ORANGE, label="term TMEM242 received after 2018"),
                   Patch(color=GREY, label="not (yet) annotated")], frameon=False, fontsize=8, loc="lower right")
ax.set_xlim(0, TWp.S.max() * 2.4)
ax.text(0, -0.2, "Case-series window: terms with 2-300 annotated genes in 2018. Under the primary 5-200 window\n"
        "'mitochondrion organization' (204 genes) is not a candidate, so the primary top term was\n"
        "'generation of precursor metabolites and energy' (a miss).", transform=ax.transAxes, fontsize=7.5,
        color=INK2, va="top")
ax.grid(axis="x", color="#e6e5e0", lw=0.6)
ax.set_axisbelow(True)
fig.tight_layout()
savefig(fig, "we_holdout_tmem242.png")

# ================================================================================================ write
CK = pd.DataFrame(CHECKS)
tsv(CK, "reproduction_check.tsv")
SUMMARY["reproduction"] = dict(n_checks=len(CK), n_match=int((CK.match == "yes").sum()),
                               mismatches=CK[CK.match != "yes"].to_dict("records"))
SUMMARY["runtime_s"] = round(time.perf_counter() - T0, 1)
(OUT / "worked_example.json").write_text(json.dumps(SUMMARY, indent=1, default=lambda o: o.item() if hasattr(
    o, "item") else (list(o) if isinstance(o, (set, frozenset, tuple)) else str(o))) + "\n")
print("\n=== reproduction check ===")
print(CK.to_string(index=False, max_colwidth=60))
print(f"\n{SUMMARY['reproduction']['n_match']} / {len(CK)} checks match; runtime {SUMMARY['runtime_s']} s")
