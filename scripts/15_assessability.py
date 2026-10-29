"""15_assessability.py -- split-half reproducibility R(g) and the assessability call (DESIGN.md v2.3 §4.2; claim C1).

Inputs: the 10 split-half neighbour lists of scripts/14 (top 60 per gene per half), the matched lists of scripts/13
(first 200 = assessability null), the frozen U table (``expressed`` and the pre-registered strata), and -- for the
§1.4 strata that the frozen U table does not carry (clean negative, lineage-restricted expressed) -- the DepMap
expression file and Model.csv (single-gene marginals only).

Per seed s (0-4): N_A^s(g), N_B^s(g) = the first K = 25 of g's top-60 list in half A / B after restriction to
BG_A ∩ BG_B ∩ BG_full (genes background in both halves and in the full data); the §3.1 exclusions (self, same arm,
paralogues) were applied when the lists were built (scripts/14).
  R(g)     = mean_s |N_A^s(g) ∩ N_B^s(g)| / K                   (every gene; reported for all scorable genes)
  R0(g, m) = mean_s |N_A^s(g) ∩ N_B^s(m)| / K                   (U genes; m = first 200 matches of g)
  p(g)     = (1 + #{m : R0(g, m) >= R(g)}) / 201                (frozen rule; ties counted as >=, integer overlaps)
  assessable = p < 0.05 AND expressed (U table column ``expressed``, pre-registered §1.4).
DESIGN §1.4 also says lineage-restricted expressed genes count as expressed; the frozen U table has no such column,
so it is computed here (same expression file and models as scripts/03) and reported as ``assessable_design``.
RBO sensitivity (§4.2; persistence p = 0.9, extrapolated RBO, depth 25 -- not fixed by DESIGN/frozen.yaml, chosen
here before any U prediction exists): same p rule with RBO in place of |N_A ∩ N_B| / K.

Outputs: results/assessability/assessability_U.tsv (all 4,924 U genes), results/assessability/R_all.tsv (R, R_rbo
and per-seed overlaps for every DepMap gene; U/H/LOO flags), results/assessability/summary.md (C1 counts by
pre-registered stratum, clean negatives, R distributions, RBO sensitivity); run manifest in
data/derived/splithalf/assessability_manifest.json.
Run: .env/bin/python -I scripts/15_assessability.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

EXPR_CSV = "data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"
MODEL_CSV = "data/raw/depmap/Model.csv"
UNIPROT_TSV = "data/raw/uniprot/uniprot_human_reviewed.tsv"

t0 = time.perf_counter()
g = C.gate_check((C.EFFECT_CSV, EXPR_CSV, MODEL_CSV))
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import hgnc_hub  # noqa: E402
from src import splithalf as sh  # noqa: E402

K = C.fz("assessability", "half_list_k")
NNULL = C.fz("assessability", "null_genes")
DEN = C.fz("assessability", "p_denominator")
ALPHA = C.fz("assessability", "alpha")
SEEDS = C.fz("assessability", "split_seeds")
RETAINED = C.fz("assessability", "half_list_retained_top")
ST = {k: C.fz("strata", k) for k in ("expressed_log2tpm1_min", "expressed_min_line_fraction",
                                     "clean_negative_log2tpm1_max", "clean_negative_min_line_fraction",
                                     "lineage_restricted_min_line_fraction", "lineage_restricted_min_lines_per_lineage")}
RBO_P = 0.9
assert DEN == NNULL + 1
S = len(SEEDS)
gt = C.load_full_index()
G = len(gt)
bg_full = gt.bg.values.astype(bool)
scor = gt.scorable.values.astype(bool)
SH = C.DERIVED / "splithalf"

# ---------------------------------------------------------------- half lists -> filtered top K
pairs, short, per_seed, common_n = [], {}, [], {}
for s in SEEDS:
    lists, bgs = [], []
    for h in (0, 1):
        z = np.load(SH / f"seed{s}_half{h}.npz")
        assert z["ids"].shape == (G, RETAINED)
        lists.append(z["ids"].astype(np.int64))
        bgs.append(z["bg_half"].astype(bool))
    common = bgs[0] & bgs[1] & bg_full
    common_n[s] = int(common.sum())
    cut = [sh.restrict_lists(ids, common, K) for ids in lists]
    for x in cut:                                   # never self; only common-BG genes
        assert not (x == np.arange(G)[:, None]).any()
        assert common[x[x >= 0]].all()
    pairs.append(tuple(cut))
    short[s] = [int(((x < 0).any(1) & scor).sum()) for x in cut]
    per_seed.append(np.array([len(np.intersect1d(a[a >= 0], b[b >= 0])) for a, b in zip(*cut)]))
    C.log(f"seed {s}: common BG {common_n[s]}; scorable genes with < {K} filtered neighbours: {short[s]}")

# ---------------------------------------------------------------- matched lists (first 200)
M = np.load(C.DERIVED / "matched" / "matched_lists.npz", allow_pickle=True)   # own derived file (object hgnc_id)
mq, mids = M["queries"], M["ids"]
assert (np.asarray(M["hgnc_id"], dtype=str) == np.asarray(gt.hgnc_id.tolist(), dtype=str)).all()
U = pd.read_csv(C.ROOT / C.U_TSV, sep="\t", dtype={"hgnc_id": str, "entrez_id": str})
pos = pd.Series(np.arange(G), index=gt.hgnc_id.values)
U["matrix_index"] = pos.reindex(U.hgnc_id).values
u_scor = U.scorable.astype(bool) & U.matrix_index.notna()
assert int(u_scor.sum()) == int(U.scorable.sum())
assert (scor[U.matrix_index[u_scor].astype(int)]).all()
qrow = pd.Series(np.arange(len(mq)), index=mq)
uq = U.matrix_index[u_scor].astype(int).tolist()
matches = {q: mids[qrow[q], :NNULL].astype(np.int64) for q in uq}
assert all((v >= 0).all() and len(v) == NNULL and q not in v for q, v in matches.items())

R, R0 = sh.reproducibility(pairs, K, matches)
R_seed = np.vstack(per_seed).T
assert np.allclose(R, R_seed.mean(1) / K)
P = sh.conservative_p(R, R0, n_seeds=S, K=K).set_index("gene")
C.log("R / R0 done")
t = time.perf_counter()
Rr, R0r = sh.reproducibility_rbo(pairs, RBO_P, matches)
Pr = pd.DataFrame([dict(gene=q, n=int((R0r[q] >= Rr[q] - 1e-12).sum())) for q in sorted(R0r)]).set_index("gene")
Pr["p"] = (1 + Pr.n) / DEN
C.log(f"RBO done ({time.perf_counter() - t:.0f} s)")

# ---------------------------------------------------------------- expression strata (§1.4; single-gene marginals)
ex = pd.read_csv(C.ROOT / EXPR_CSV, low_memory=False)
ex = ex[ex.IsDefaultEntryForModel == "Yes"]
assert ex.ModelID.is_unique
meta_cols = ["Unnamed: 0", "SequencingID", "ModelConditionID", "ModelID", "IsDefaultEntryForMC",
             "IsDefaultEntryForModel"]
ecols = [c for c in ex.columns if c not in meta_cols]
model = pd.read_csv(C.ROOT / MODEL_CSV, usecols=["ModelID", "OncotreeLineage"]).set_index("ModelID")
lin = model.OncotreeLineage.reindex(ex.ModelID.values).values
es = sh.expression_strata(ex[ecols].to_numpy(dtype=np.float64), lin, expr_min=ST["expressed_log2tpm1_min"],
                          expr_frac=ST["expressed_min_line_fraction"], neg_max=ST["clean_negative_log2tpm1_max"],
                          neg_frac=ST["clean_negative_min_line_fraction"],
                          lin_frac=ST["lineage_restricted_min_line_fraction"],
                          lin_min_lines=ST["lineage_restricted_min_lines_per_lineage"])
es["entrez_id"] = [hgnc_hub.parse_depmap_column(c)[1] for c in ecols]
es = es.drop_duplicates("entrez_id").set_index("entrez_id")
n_expr_models = len(ex)
n_lineages = es.attrs.get("n_lineages_eligible")
del ex
for c in ("expressed", "clean_negative", "lineage_criterion", "lineage_restricted"):
    U[f"_{c}"] = U.entrez_id.map(es[c]).fillna(False).astype(bool)
U["lineage_max"] = U.entrez_id.map(es.lineage_max)
U["frac_lt_0.5"] = U.entrez_id.map(es.frac_lt_neg)
mism = int((U._expressed != U.expressed.astype(bool)).sum())
assert mism == 0, f"recomputed 'expressed' differs from the frozen column for {mism} U genes"
C.log(f"expression strata: {n_expr_models} models, {n_lineages} lineages with >= "
      f"{ST['lineage_restricted_min_lines_per_lineage']} models; recomputed 'expressed' matches the frozen column")

# ---------------------------------------------------------------- TM / secreted (descriptive; UniProt keywords)
up = pd.read_csv(C.ROOT / UNIPROT_TSV, sep="\t", usecols=["Entry", "Keywords"]).set_index("Entry")
kw = up.Keywords.fillna("").str.split(";")
tm_acc = set(kw.index[kw.map(lambda x: "Transmembrane" in x)])
sec_acc = set(kw.index[kw.map(lambda x: "Secreted" in x)])


def acc_any(s, accs):
    return isinstance(s, str) and any(a in accs for a in s.split("|"))


U["tm"] = U.uniprot_ids.map(lambda s: acc_any(s, tm_acc))
U["secreted"] = U.uniprot_ids.map(lambda s: acc_any(s, sec_acc))
U["tm_or_secreted"] = np.where(U.tm & U.secreted, "TM & secreted",
                               np.where(U.tm, "TM", np.where(U.secreted, "secreted", "neither")))

# ---------------------------------------------------------------- U table
rows = []
for r in U.itertuples():
    if not (r.scorable and pd.notna(r.matrix_index)):
        rows.append(dict(R=np.nan, R0_mean=np.nan, R0_max=np.nan, n_R0_ge_R=np.nan, p=np.nan, R_rbo=np.nan,
                         R0_rbo_mean=np.nan, n_R0_rbo_ge_R=np.nan, p_rbo=np.nan))
        continue
    i = int(r.matrix_index)
    rows.append(dict(R=R[i], R0_mean=R0[i].mean(), R0_max=R0[i].max(), n_R0_ge_R=int(P.loc[i, "n_R0_ge_R"]),
                     p=P.loc[i, "p"], R_rbo=Rr[i], R0_rbo_mean=R0r[i].mean(), n_R0_rbo_ge_R=int(Pr.loc[i, "n"]),
                     p_rbo=Pr.loc[i, "p"]))
A = pd.concat([U[["hgnc_id", "symbol", "in_depmap", "scorable", "matrix_index"]].reset_index(drop=True),
               pd.DataFrame(rows)], axis=1)
A["p_lt_alpha"] = (A.p < ALPHA).fillna(False) & A.scorable.astype(bool)
A["expressed"] = U.expressed.astype(bool).values
A["lineage_restricted"] = U._lineage_restricted.values
A["expressed_design"] = A.expressed | A.lineage_restricted
A["clean_negative"] = U._clean_negative.values
A["assessable"] = A.p_lt_alpha & A.expressed
A["assessable_design"] = A.p_lt_alpha & A.expressed_design
A["p_rbo_lt_alpha"] = (A.p_rbo < ALPHA).fillna(False) & A.scorable.astype(bool)
A["assessable_rbo"] = A.p_rbo_lt_alpha & A.expressed
A["headline_design"] = A.expressed_design & ~U.chemosensory_epidermal.astype(bool).values & \
    ~U.tandem_cluster.astype(bool).values
strata = ["family_stratum", "expression_stratum", "headline_stratum", "core", "sd_tertile_withinU", "any_dependency",
          "tool_background", "tandem_cluster", "tandem_cluster_withinspecies", "chemosensory_epidermal", "is_kzfp",
          "nan_frac", "lineage_max", "frac_lt_0.5", "tm", "secreted", "tm_or_secreted"]
for c in strata:
    A[c] = U[c].values
A["low_coverage"] = U.in_depmap.astype(bool).values & ~U.tool_background.fillna(False).astype(bool).values
A["nan_frac_gt0"] = U.nan_frac.fillna(0).values > 0
outd = C.ROOT / "results" / "assessability"
outd.mkdir(parents=True, exist_ok=True)
A.to_csv(outd / "assessability_U.tsv", sep="\t", index=False, float_format="%.6g")

# ---------------------------------------------------------------- R for all genes
H = pd.read_csv(C.ROOT / "results/holdout/H_genes.tsv", sep="\t", dtype={"hgnc_id": str})
LOO = pd.read_csv(C.ROOT / "results/loo_sample.tsv", sep="\t", dtype={"hgnc_id": str})
Rall = pd.DataFrame(dict(matrix_index=np.arange(G), hgnc_id=gt.hgnc_id.values, symbol=gt.symbol.values,
                         scorable=scor, bg=bg_full, in_U=gt.hgnc_id.isin(U.hgnc_id).values,
                         in_H=gt.hgnc_id.isin(H.hgnc_id).values, in_LOO=gt.hgnc_id.isin(LOO.hgnc_id).values,
                         R=R, R_rbo=Rr, **{f"overlap_seed{s}": R_seed[:, k] for k, s in enumerate(SEEDS)}))
Rall.to_csv(outd / "R_all.tsv", sep="\t", index=False, float_format="%.6g")

# ---------------------------------------------------------------- summary
run = C.write_manifest(SH / "assessability_manifest.json", "scripts/15_assessability.py", g,
                       [C.U_TSV, "results/holdout/H_genes.tsv", "results/loo_sample.tsv", EXPR_CSV, MODEL_CSV,
                        UNIPROT_TSV, "data/derived/matched/matched_lists.npz",
                        *[f"data/derived/splithalf/seed{s}_half{h}.npz" for s in SEEDS for h in (0, 1)]],
                       seed=SEEDS, t0=t0, extra=dict(K=K, n_null=NNULL, alpha=ALPHA, rbo_p=RBO_P, short_rows=short,
                                                     common_bg=common_n, n_expression_models=n_expr_models,
                                                     n_lineages_eligible=n_lineages,
                                                     n_assessable=int(A.assessable.sum()),
                                                     n_assessable_design=int(A.assessable_design.sum())))


def fr(a, b):
    return f"{a / b:.3f}" if b else "–"


def line(name, d):
    n, ns = len(d), int(d.scorable.sum())
    ne = int((d.scorable & d.expressed).sum())
    nP = int(d.p_lt_alpha.sum())
    na, nad = int(d.assessable.sum()), int(d.assessable_design.sum())
    return (f"| {name} | {n:,} | {ns:,} | {ne:,} | {nP:,} ({fr(nP, ns)}) | **{na:,}** | {fr(na, n)} | {fr(na, ns)} | "
            f"{fr(na, ne)} | {nad:,} |")


def count_table(df, col, label=None):
    return [line(f"{label or col} = {v}", d) for v, d in df.groupby(col, dropna=False, sort=True)]


T = [line("**all U**", A),
     line("**headline stratum** (expressed, not chemosensory/epidermal, not tandem; frozen column)",
          A[A.headline_stratum.astype(bool)]),
     line("headline stratum, DESIGN expressed (incl. lineage-restricted)", A[A.headline_design]),
     line("headline & any-dependency", A[A.headline_stratum.astype(bool) & A.any_dependency.fillna(False).astype(bool)])]
for col in ["family_stratum", "expression_stratum", "lineage_restricted", "clean_negative", "tandem_cluster",
            "tandem_cluster_withinspecies", "chemosensory_epidermal", "is_kzfp", "core", "sd_tertile_withinU",
            "any_dependency", "tool_background", "low_coverage", "nan_frac_gt0", "tm_or_secreted"]:
    T += count_table(A, col)


def dist(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return "0 | – | – | – | – | –"
    q = np.quantile(x, [0.1, 0.25, 0.5, 0.75, 0.9])
    return (f"{len(x):,} | {x.mean():.3f} | {q[0]:.2f} / {q[1]:.2f} / {q[2]:.2f} / {q[3]:.2f} / {q[4]:.2f} | "
            f"{(x == 0).mean():.3f} | {(x >= 0.2).mean():.3f} | {(x >= 0.5).mean():.3f}")


sc = Rall[Rall.scorable]
As = A[A.scorable.astype(bool)]
Ddist = [f"| all scorable | {dist(sc.R)} |",
         f"| U (scorable) | {dist(sc.R[sc.in_U])} |",
         f"| non-U (scorable) | {dist(sc.R[~sc.in_U])} |",
         f"| U, BG | {dist(sc.R[sc.in_U & sc.bg])} |",
         f"| non-U, BG | {dist(sc.R[~sc.in_U & sc.bg])} |",
         f"| U, non-BG (low coverage) | {dist(sc.R[sc.in_U & ~sc.bg])} |",
         f"| non-U, non-BG | {dist(sc.R[~sc.in_U & ~sc.bg])} |",
         f"| U, expressed | {dist(As.R[As.expressed])} |",
         f"| U, not expressed | {dist(As.R[~As.expressed])} |",
         f"| U, clean negative | {dist(As.R[As.clean_negative])} |",
         f"| U, headline stratum | {dist(As.R[As.headline_stratum.astype(bool)])} |",
         f"| H | {dist(sc.R[sc.in_H])} |",
         f"| LOO sample | {dist(sc.R[sc.in_LOO])} |"]
Dr = [f"| U (scorable) | {dist(sc.R_rbo[sc.in_U])} |", f"| non-U (scorable) | {dist(sc.R_rbo[~sc.in_U])} |",
      f"| H | {dist(sc.R_rbo[sc.in_H])} |"]

# clean negatives (negative control, §4.2)
cn = As[As.clean_negative]
ne_ = As[~As.expressed]
CN = [f"| all clean negatives (scorable) | {len(cn):,} | {int(cn.p_lt_alpha.sum()):,} | "
      f"{fr(int(cn.p_lt_alpha.sum()), len(cn))} | {int(cn.p_rbo_lt_alpha.sum()):,} |"]
for v, d in cn.groupby("sd_tertile_withinU", dropna=False):
    CN.append(f"| clean negatives, SD tertile = {v} | {len(d):,} | {int(d.p_lt_alpha.sum()):,} | "
              f"{fr(int(d.p_lt_alpha.sum()), len(d))} | {int(d.p_rbo_lt_alpha.sum()):,} |")
for v, d in cn.groupby("any_dependency", dropna=False):
    CN.append(f"| clean negatives, any-dependency = {v} | {len(d):,} | {int(d.p_lt_alpha.sum()):,} | "
              f"{fr(int(d.p_lt_alpha.sum()), len(d))} | {int(d.p_rbo_lt_alpha.sum()):,} |")
CN.append(f"| all non-expressed (scorable; frozen column) | {len(ne_):,} | {int(ne_.p_lt_alpha.sum()):,} | "
          f"{fr(int(ne_.p_lt_alpha.sum()), len(ne_))} | {int(ne_.p_rbo_lt_alpha.sum()):,} |")
ex_ = As[As.expressed]
CN.append(f"| expressed (scorable; for comparison) | {len(ex_):,} | {int(ex_.p_lt_alpha.sum()):,} | "
          f"{fr(int(ex_.p_lt_alpha.sum()), len(ex_))} | {int(ex_.p_rbo_lt_alpha.sum()):,} |")

# RBO concordance
ct = pd.crosstab(As.assessable, As.assessable_rbo)
both = int((As.assessable & As.assessable_rbo).sum())
only_j = int((As.assessable & ~As.assessable_rbo).sum())
only_r = int((~As.assessable & As.assessable_rbo).sum())
rho = pd.Series(As.R.astype(float)).corr(pd.Series(As.R_rbo.astype(float)), method="spearman")

n_assess = int(A.assessable.sum())
n_ad = int(A.assessable_design.sum())
pv = As.p.values.astype(float)
nU, nS = len(A), int(A.scorable.sum())
nSE = int((A.scorable & A.expressed).sum())
nSED = int((A.scorable & A.expressed_design).sum())
hl = A.headline_stratum.astype(bool)
L = ["# Assessability of U genes (DESIGN §4.2; claim C1)", "",
     f"Generated by `scripts/15_assessability.py` ({run['created']}; runtime {run['runtime_s']} s, peak RSS "
     f"{run['peak_rss_gb']} GB). Gate: tag `{g['tag']}` @ {g['tag_commit'][:10]}. Split-half lists: "
     "`scripts/14_splithalf.py` (5 seeds × 2 halves, lineage × library strata, PatientID kept together); matched "
     "lists: `scripts/13_matched_lists.py` (seed 0, first 200).", "",
     f"Rule (frozen): K = {K}; half lists (top {RETAINED}) restricted to BG_A ∩ BG_B ∩ BG_full (common BG "
     f"{', '.join(f'{v:,}' for v in common_n.values())} genes per seed), then cut to {K}; R(g) = mean over seeds of "
     f"|N_A ∩ N_B| / K; R0(g, m) = mean over seeds of |N_A(g) ∩ N_B(m)| / K for the first {NNULL} matched genes; "
     f"p = (1 + #{{m: R0 ≥ R}}) / {DEN} (ties compared on integer overlap totals); assessable = p < {ALPHA} AND "
     "expressed (frozen `expressed` column of `preregistration/uncharacterised_genes.tsv`).", "",
     f"**C1: {n_assess:,} of {nU:,} U genes ({n_assess / nU:.1%}) are scorable, expressed and assessable. "
     f"{nS:,} are scorable ({nS / nU:.1%}); {nSE:,} scorable and expressed; {int(A.p_lt_alpha.sum()):,} of {nS:,} "
     f"scorable genes have p < {ALPHA} ({A.p_lt_alpha.sum() / nS:.1%}) regardless of expression; "
     f"{n_assess:,} / {nSE:,} = {n_assess / nSE:.1%} of scorable expressed genes are assessable.**", "",
     f"**Headline stratum** (frozen column: expressed, not chemosensory/epidermal, not tandem): "
     f"{int(A.assessable[hl].sum()):,} of {int(hl.sum()):,} assessable ({A.assessable[hl].mean():.1%}; "
     f"{int((hl & A.scorable).sum()):,} scorable).", "",
     "### Expression definition: frozen column vs DESIGN §1.4 (flag for the PI)", "",
     "DESIGN §1.4 says lineage-restricted expressed genes (expressed, log2(TPM+1) ≥ 1, in ≥ 50% of the lines of any "
     "lineage with ≥ 10 lines) *count as expressed, assessable*; the frozen U table has no lineage-restricted column "
     "and its `expressed` uses only the ≥ 10%-of-lines rule. Recomputed here from the same expression file "
     f"({n_expr_models:,} default-entry models; lineage = Model.csv OncotreeLineage; {n_lineages} lineages with ≥ 10 "
     f"models); the recomputed ≥ 10% rule reproduces the frozen `expressed` column exactly. Lineage-restricted (not "
     f"expressed by the global rule): {int(A.lineage_restricted.sum()):,} U genes "
     f"({int((A.lineage_restricted & A.scorable).sum()):,} scorable). **Under the DESIGN definition: {n_ad:,} "
     f"assessable** ({nSED:,} scorable & expressed); +{n_ad - n_assess} vs the frozen column. Both are reported; the "
     "choice is the PI's (DEVIATIONS.md).", "",
     "## Counts by pre-registered stratum", "",
     "Columns: n U; scorable; scorable & expressed (frozen); p < 0.05 (fraction of scorable); **assessable** (frozen "
     "expressed); assessable / n U; / scorable; / scorable & expressed; assessable under DESIGN expressed (incl. "
     "lineage-restricted).", "",
     "| stratum | n U | scorable | scor. & expr. | p < 0.05 | assessable | /n U | /scorable | /scor. & expr. | "
     "assessable (DESIGN expr.) |", "|---|---|---|---|---|---|---|---|---|---|", *T, "",
     "Strata: frozen columns of `preregistration/uncharacterised_genes.tsv` except `lineage_restricted` and "
     "`clean_negative` (DESIGN §1.4, recomputed here from the expression file: clean negative = log2(TPM+1) < 0.5 in "
     "≥ 95% of models with expression), `low_coverage` = in DepMap but not tool background (NaN fraction ≥ 0.10), "
     "`nan_frac_gt0`, and `tm_or_secreted` (descriptive: UniProt reviewed keyword 'Transmembrane' / 'Secreted' on any "
     "of the gene's accessions). HPA tissue/testis-enriched (descriptive, §1.4) is **not computed**: no HPA tissue "
     "RNA-specificity file was obtained (data/raw/hpa holds subcellular location only). Genes without a DepMap column "
     "or without a tool-mapped UniProt accession are not scorable (R, p empty).", "",
     "## Clean negatives (negative control, §4.2)", "",
     "Non-expressed genes are scored anyway; a p < 0.05 call on a clean negative is a false reproducibility call "
     "(the Tier-A-like false-call rate itself needs p_cal and tiers, M6).", "",
     "| set | n scorable | p < 0.05 | rate | p_RBO < 0.05 |", "|---|---|---|---|---|", *CN, "",
     "## p-value distribution (scorable U genes)", "",
     f"p = 1/201 (no matched gene reaches R): {int(np.isclose(pv, 1 / DEN).sum()):,}; p < 0.05: "
     f"{int((pv < ALPHA).sum()):,}; p = 1 (every matched gene ≥ R, e.g. R = 0): {int((pv == 1).sum()):,}; "
     f"median over U genes of mean R0 = {np.nanmedian(As.R0_mean.astype(float)):.4f}; mean R0 = "
     f"{np.nanmean(As.R0_mean.astype(float)):.4f}.", "",
     "## R(g) distribution", "",
     "| genes | n | mean | 10th / 25th / 50th / 75th / 90th pct | fraction R = 0 | R ≥ 0.2 | R ≥ 0.5 |",
     "|---|---|---|---|---|---|---|", *Ddist, "",
     f"Filtered half lists short of {K} neighbours (scorable genes, per seed, halves A/B): {short}.", "",
     f"## RBO sensitivity (§4.2)", "",
     f"R_RBO(g) = mean over seeds of extrapolated RBO (Webber et al. 2010, eq. 32; persistence p = {RBO_P}, depth "
     f"{K}) between N_A(g) and N_B(g); R0_RBO(g, m) between N_A(g) and N_B(m); same p rule and expression "
     f"requirement. p = {RBO_P} is not fixed by DESIGN/frozen.yaml (chosen at M4 before any U prediction; log in "
     "DEVIATIONS.md).", "",
     f"- Assessable (RBO): **{int(A.assessable_rbo.sum()):,}** vs {n_assess:,} (overlap rule); both {both:,}, overlap "
     f"rule only {only_j:,}, RBO only {only_r:,}. p_RBO < 0.05 among scorable U: {int(A.p_rbo_lt_alpha.sum()):,}. "
     f"Spearman(R, R_RBO) over scorable U = {rho:.3f}.", "",
     "| genes | n | mean | 10th / 25th / 50th / 75th / 90th pct | fraction 0 | ≥ 0.2 | ≥ 0.5 |",
     "|---|---|---|---|---|---|---|", *Dr, "",
     "Files: `results/assessability/assessability_U.tsv` (U genes: R, R0 mean/max, n R0 ≥ R, p, RBO analogues, "
     "expressed (frozen / DESIGN), clean negative, assessable (frozen / DESIGN / RBO), strata), "
     f"`results/assessability/R_all.tsv` (R, R_RBO and per-seed overlap counts for all {G:,} DepMap genes; U/H/LOO "
     "flags).", ""]
(outd / "summary.md").write_text("\n".join(L))
C.log(f"assessable U genes: {n_assess} (DESIGN expressed: {n_ad}; RBO: {int(A.assessable_rbo.sum())}); wrote {outd}")
