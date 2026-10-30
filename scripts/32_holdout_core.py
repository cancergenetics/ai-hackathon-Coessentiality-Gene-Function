#!/usr/bin/env python
"""32_holdout_core.py -- M5b: the single pre-registered look at the temporal hold-out H, core analyses
(DESIGN.md v2.3 §3.0-§3.6, §8 'core'; LOOKS.md specification row 47631ed; DEVIATIONS.md).

Vocabulary V2 at t0 = GO 2018-07-02 GAF propagated with the current obo (src/vocab.build_v2) for neighbour
membership, candidate terms (5-200 annotated scorable genes at t0, per query after the IPI with/from rule), term sizes
and prior-only. Queries are scored in the H setting (``loo=False``: the query's own t0 rows stay; H genes have no
informative D1 term at t0). Ranker R1 (raw S, LOOKS.md), reportable = >= 2 supporting partners.
Targets T(g) = results/holdout/H_targets.tsv (current-propagated minus t0-propagated V2 terms, candidate at t0).
Primary: circularity-flagged targets (>= 1 supporting PMID flagged, results/holdout/circularity_annotations.tsv)
removed from T(g) and from every ranked list (the scripts/30 LOO convention); genes left without a target leave H.
Endpoint hit@1 = top reportable term in T(g); denominator = all primary H genes (no reportable term -> 0).
Comparators: prior-only (candidate terms by t0 size, ties by GO id); matched-gene null (first 5 matches of the
500-list not annotated at t0 to any term of T(g); each scored like an H query; null hit = mean over the 5); GLS
(scripts/16 rows, same exclusions and predictor). Primary test (intersection-union): precision@1 zavg - prior > 0
and zavg - matched null > 0, each paired cluster bootstrap (10,000 replicates, seed 0) 95% percentile CI excluding 0
(BCa reported). Clusters = connected components of H genes sharing a supporting PMID or appearing in each other's
zavg_BEF N(g), fixed once on all H genes; fallback (DEVIATIONS 2026-10-30): if the largest PMID+N(g) component holds
> 20% of H genes, primary CIs use PMID-only clusters and PMID+N(g) is the sensitivity.
Also (core): zavg - GLS two-sided overall and by neighbourhood/complex-size stratum; MRR; precision@1 with candidate
and target terms <= 50 genes; top-1 term size per method; primary metric on each of the 10 split-half networks;
V1 (GO CC complexes) with/without ETC complex I and mitoribosome and by hu.MAP-train membership; circularity
sensitivity; named-control case series (window 2-300, V1' label); covariate SMDs (H, U, LOO); metrics by signal
quintile; §3.7 covariates for scripts/34.

Outputs: results/holdout_eval/core.md, core_results.json, per_gene_core.tsv, comparisons_core.tsv,
splithalf.tsv, v1.tsv, circularity_sensitivity.tsv, controls_case_series.tsv, covariate_smd.tsv,
signal_quintiles.tsv, top1_size.tsv, core_manifest.json; data/derived/holdout_eval/core.pkl.
Run: .env/bin/python -I scripts/32_holdout_core.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
gate = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import m5b_common as B  # noqa: E402
from src import knownness as kn  # noqa: E402
from src import metrics as mt  # noqa: E402
from src import vocab  # noqa: E402

log = C.log
OUT, DER = B.OUT, B.DER
timing = {}
RES = dict(dry_run=B.DRY, n_boot=B.NBOOT, seed=B.SEED)

# ============================================================================================ inputs
base = B.Base()
gt, G = base.gt, base.G
v2t0 = B.build_v2(base, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
v2cur = B.build_v2(base, "data/raw/go/current/goa_human.gaf.gz", label="current")
RES["v2_t0_stats"] = v2t0.stats
RES["v2_cur_stats"] = v2cur.stats

if not B.DRY:
    HG = pd.read_csv(C.ROOT / "results/holdout/H_genes.tsv", sep="\t", dtype={"hgnc_id": str})
    TT = pd.read_csv(C.ROOT / "results/holdout/H_targets.tsv", sep="\t", dtype={"support_pmids": str},
                     keep_default_na=False)
    CA = pd.read_csv(C.ROOT / "results/holdout/circularity_annotations.tsv", sep="\t")
    TT = TT.merge(CA[["hgnc_id", "go_id", "any_pmid_flagged", "fully_circular"]], on=["hgnc_id", "go_id"],
                  how="left", validate="1:1")
    assert TT.any_pmid_flagged.notna().all()
    TT["pmids"] = [[int(p) for p in str(s).split("|") if p] for s in TT.support_pmids]
    pmid_cluster = dict(zip(HG.hgnc_id, HG.pmid_cluster))
else:
    # dry run: LOO-sample genes with pseudo-targets (current minus t0 V2, t0 base size 5-200); no H gene used
    loo = pd.read_csv(C.ROOT / "results/loo_sample.tsv", sep="\t", dtype={"hgnc_id": str})
    cand_t0 = {t for t, s in zip(v2t0.terms, v2t0.size) if B.LO <= s <= B.HI}
    rows = []
    for p in loo.matrix_index.values[:600]:
        T = (v2cur.prop.get(int(p), frozenset()) - v2t0.prop.get(int(p), frozenset())) & cand_t0
        for t in sorted(T):
            rows.append(dict(hgnc_id=gt.hgnc_id.values[p], symbol=gt.symbol.values[p], go_id=t,
                             term_size_t0=int(v2t0.size[v2t0.col[t]]),
                             pmids=B.support_pmids(v2cur, int(p), t)))
    TT = pd.DataFrame(rows)
    keep = TT.hgnc_id.drop_duplicates().values[:300]
    TT = TT[TT.hgnc_id.isin(keep)].reset_index(drop=True)
    rng = np.random.default_rng(1)
    TT["any_pmid_flagged"] = rng.random(len(TT)) < 0.02
    TT["fully_circular"] = TT.any_pmid_flagged & (rng.random(len(TT)) < 0.5)
    TT["support_all_pmids_post_cutoff"] = rng.random(len(TT)) < 0.4
    HG = pd.DataFrame(dict(hgnc_id=keep))
    gp = TT.groupby("hgnc_id").pmids.apply(lambda s: {p for x in s for p in x}).to_dict()
    cl0 = mt.clusters_from_links(list(keep), pmids=gp)
    pmid_cluster = dict(zip(keep, cl0))

flags = B.circ_lookup({p for ps in TT.pmids for p in ps})
st = B.target_states(TT.pmids, flags)
TT["unscannable"] = [s[2] for s in st]
TT["flagged"] = TT.any_pmid_flagged.astype(bool)
TT["fully_circular"] = TT.fully_circular.astype(bool)
TT["pos"] = TT.hgnc_id.map(base.pos)
assert TT.pos.notna().all()
TT["pos"] = TT.pos.astype(int)
TT["col"] = TT.go_id.map(lambda t: v2t0.col.get(t, -1))
Hpos = sorted(TT.pos.unique().tolist())
T_all = TT.groupby("pos").go_id.apply(set).to_dict()


def tsets(mask, drop_from_lists=True):
    """targets (columns) and per-gene list drops for the targets kept by ``mask`` (excluded targets dropped)."""
    k, x = TT[mask], TT[~mask]
    tg = {int(g): set(int(c) for c in d.col if c >= 0) for g, d in k.groupby("pos")}
    genes = sorted(k.pos.unique().tolist())
    drops = ({int(g): set(int(c) for c in d.col if c >= 0) for g, d in x.groupby("pos")} if drop_from_lists else {})
    return genes, tg, drops


P, Tp, Dp = tsets(~TT.flagged.values)
RES["H"] = dict(n_H=len(Hpos), n_pairs=len(TT), n_flagged_pairs=int(TT.flagged.sum()),
                n_fully_circular_pairs=int(TT.fully_circular.sum()), n_unscannable_pairs=int(TT.unscannable.sum()),
                n_primary=len(P), n_genes_losing_all=len(Hpos) - len(P),
                n_target_pairs_not_v2t0_column=int((TT.col < 0).sum()),
                n_new_pmids_queried=int(flags.attrs.get("n_new_queried", 0)))
log(f"H: {len(Hpos)} genes; primary {len(P)}; flagged pairs {int(TT.flagged.sum())}")

# ============================================================================================ clusters
pmid_sets = {base.pos[h]: {int(c)} for h, c in pmid_cluster.items() if h in base.pos}
CLall = B.clusters_for(Hpos, pmid_sets, base.nb)
cl_index = {g: i for i, g in enumerate(Hpos)}


def cl(genes, which="primary"):
    return np.asarray(CLall[which])[[cl_index[int(g)] for g in genes]]


RES["clusters"] = dict(CLall["summary"], primary=CLall["primary_name"], sensitivity=CLall["sensitivity_name"],
                       fallback_threshold=B.CLUSTER_FALLBACK_FRAC)
log(f"clusters: {CLall['summary']}; primary = {CLall['primary_name']}")

# ============================================================================================ main scoring
t = time.perf_counter()
nulls, skipped = B.select_nulls(v2t0, base.matches, Hpos, T_all)
assert all(len(v) == B.NNULL for v in nulls.values())
S_main = B.Scored(v2t0, base.nb, base.matches, set(Hpos) | {m for v in nulls.values() for m in v}, "zavg t0")
prior_lists = {g: S_main.prior(g) for g in Hpos}
nb_gls = B.baseline_network(base, "gls", Hpos)
S_gls = B.Scored(v2t0, nb_gls, base.matches, Hpos, "GLS t0")
timing["main_scoring_s"] = round(time.perf_counter() - t, 1)


def eval_all(genes, tg, drops):
    return dict(zavg=B.evaluate(genes, S_main.r1, tg, drops, S_main.sizes),
                prior=B.evaluate(genes, prior_lists, tg, drops, S_main.sizes),
                null=B.evaluate_null(genes, nulls, S_main.r1, tg, drops, S_main.sizes),
                gls=B.evaluate(genes, S_gls.r1, tg, drops, S_main.sizes))


E = eval_all(P, Tp, Dp)
clP, clPs = cl(P), cl(P, "sensitivity")
METH = ["zavg", "prior", "null", "gls"]
LAB = dict(zavg="zavg_BEF (R1)", prior="prior-only", null="matched-gene null", gls="GLS (R1)")

# ---------------------------------------------------------------- per-method summaries
summ = []
for m in METH:
    e = E[m]
    r = dict(method=m, label=LAB[m], n=len(e), precision_at_1=e.hit1.mean(), MRR=e.rr.mean(),
             coverage=e.has_pred.mean())
    b = B.mci(e.hit1.values, clP)
    r.update(p1_ci_lo=b["ci_percentile"][0], p1_ci_hi=b["ci_percentile"][1])
    b = B.mci(e.rr.values, clP)
    r.update(mrr_ci_lo=b["ci_percentile"][0], mrr_ci_hi=b["ci_percentile"][1])
    s = e.hit1_small.dropna()
    b = B.mci(s.values, cl(s.index))
    r.update(n_small=len(s), p1_small=s.mean(), p1_small_ci_lo=b["ci_percentile"][0],
             p1_small_ci_hi=b["ci_percentile"][1])
    summ.append(r)
SUMM = pd.DataFrame(summ)
SUMM.to_csv(OUT / "methods_core.tsv", sep="\t", index=False, float_format="%.6f")

# ---------------------------------------------------------------- primary IUT
comp = []
prim = {}
for b_ in ("prior", "null"):
    for which, c_ in (("primary", clP), ("sensitivity", clPs)):
        r = B.pdiff(E["zavg"].hit1, E[b_].hit1, c_)
        name = f"precision@1 zavg - {b_}"
        comp.append(B.drow(name, r, dict(clusters=CLall[f"{which}_name"], role="primary IUT" if which == "primary"
                                         else "primary IUT (cluster sensitivity)")))
        if which == "primary":
            prim[b_] = r
iut_pass = all(prim[b_]["ci_percentile"][0] > 0 for b_ in prim)
iut_pass_bca = all(prim[b_]["ci_bca"][0] > 0 for b_ in prim)
neff = {b_: len(P) / prim[b_]["design_effect"] for b_ in prim}
RES["primary"] = dict(
    pass_=iut_pass, pass_bca=iut_pass_bca, clusters=CLall["primary_name"], n=len(P),
    p1={m: float(E[m].hit1.mean()) for m in METH}, coverage={m: float(E[m].has_pred.mean()) for m in METH},
    diff={b_: dict(est=prim[b_]["estimate"], ci=prim[b_]["ci_percentile"], bca=prim[b_]["ci_bca"],
                   design_effect=prim[b_]["design_effect"], n_clusters=prim[b_]["n_clusters"],
                   effective_n=neff[b_]) for b_ in prim},
    underpowered=bool(min(neff.values()) < C.fz("bootstrap", "underpowered_effective_n")))
log(f"PRIMARY: zavg {E['zavg'].hit1.mean():.4f} prior {E['prior'].hit1.mean():.4f} null "
    f"{E['null'].hit1.mean():.4f}; IUT pass = {iut_pass}")

# ---------------------------------------------------------------- GLS key secondary + strata
r = B.pdiff(E["zavg"].hit1, E["gls"].hit1, clP)
comp.append(B.drow("precision@1 zavg - GLS (two-sided)", r, dict(clusters=CLall["primary_name"],
                                                                 role="key secondary")))
RES["gls"] = dict(est=r["estimate"], ci=r["ci_percentile"], bca=r["ci_bca"], p1_gls=float(E["gls"].hit1.mean()),
                  gls_ge_zavg=bool(E["gls"].hit1.mean() >= E["zavg"].hit1.mean()),
                  significant=bool(r["ci_percentile"][0] > 0 or r["ci_percentile"][1] < 0))
minsize = TT[~TT.flagged].groupby("pos").term_size_t0.min()
strata2 = pd.Series(np.where(minsize.loc[P].values <= B.SMALL, f"<= {B.SMALL}", f"> {B.SMALL}"), index=P)
strata3 = pd.Series(pd.cut(minsize.loc[P].values, [0, 20, 50, 10 ** 6], labels=["5-20", "21-50", "51-200"])
                    .astype(str), index=P)
gls_strata = []
for nm, ss in (("2-way", strata2), ("3-way", strata3)):
    for lev in sorted(ss.unique()):
        g = ss.index[ss.values == lev]
        r = B.pdiff(E["zavg"].hit1.loc[g], E["gls"].hit1.loc[g], cl(g))
        d = B.drow(f"precision@1 zavg - GLS, smallest-target-size stratum {lev}", r,
                   dict(clusters=CLall["primary_name"], role="key secondary (stratum)", stratification=nm,
                        stratum=lev))
        comp.append(d)
        gls_strata.append(d)
RES["gls_strata"] = gls_strata

# ---------------------------------------------------------------- MRR, <= 50, top-1 size
for b_ in ("prior", "null", "gls"):
    r = B.pdiff(E["zavg"].rr, E[b_].rr, clP)
    comp.append(B.drow(f"MRR zavg - {b_}", r, dict(clusters=CLall["primary_name"], role="core")))
small_genes = E["zavg"].hit1_small.dropna().index
for b_ in ("prior", "null", "gls"):
    r = B.pdiff(E["zavg"].hit1_small.loc[small_genes], E[b_].hit1_small.loc[small_genes], cl(small_genes))
    comp.append(B.drow(f"precision@1 (terms <= {B.SMALL}) zavg - {b_}", r,
                       dict(clusters=CLall["primary_name"], role="core")))
RES["small"] = dict(n_genes=len(small_genes), n_dropped=len(P) - len(small_genes))
null_sizes = []
for g in P:
    for m in nulls[g]:
        lst = [c for c in S_main.r1.get(m, []) if c not in Dp.get(g, set())]
        if lst:
            null_sizes.append(S_main.sizes(g)[lst[0]])
sz_rows = []
for m, vals in (("zavg", E["zavg"].top1size.dropna().values), ("prior", E["prior"].top1size.dropna().values),
                ("null (pooled matches)", np.asarray(null_sizes, float)), ("gls", E["gls"].top1size.dropna().values)):
    q = np.quantile(vals, [0.1, 0.25, 0.5, 0.75, 0.9])
    sz_rows.append(dict(method=m, n=len(vals), p10=q[0], q1=q[1], median=q[2], q3=q[3], p90=q[4], mean=vals.mean(),
                        frac_le50=(vals <= B.SMALL).mean()))
SZ = pd.DataFrame(sz_rows)
SZ.to_csv(OUT / "top1_size.tsv", sep="\t", index=False, float_format="%.4f")

# ============================================================================================ split halves
t = time.perf_counter()
sh_rows = []
for s, h, nbh in B.half_networks(base):
    Eh, _ = B.method_set(v2t0, nbh, base.matches, P, Tp, Dp, nulls, f"half s{s}h{h}")
    row = dict(seed=s, half=h, n=len(P), p1_zavg=Eh["net"].hit1.mean(), p1_null=Eh["null"].hit1.mean(),
               p1_prior=Eh["prior"].hit1.mean(), coverage=Eh["net"].has_pred.mean())
    b = B.mci(Eh["net"].hit1.values, clP)
    row.update(p1_ci_lo=b["ci_percentile"][0], p1_ci_hi=b["ci_percentile"][1])
    for b_ in ("prior", "null"):
        r = B.pdiff(Eh["net"].hit1, Eh[b_].hit1, clP)
        row.update({f"d_{b_}": r["estimate"], f"d_{b_}_lo": r["ci_percentile"][0], f"d_{b_}_hi": r["ci_percentile"][1]})
    sh_rows.append(row)
SH = pd.DataFrame(sh_rows)
SH.to_csv(OUT / "splithalf.tsv", sep="\t", index=False, float_format="%.6f")
timing["splithalf_s"] = round(time.perf_counter() - t, 1)
RES["splithalf"] = dict(p1_min=float(SH.p1_zavg.min()), p1_max=float(SH.p1_zavg.max()),
                        p1_mean=float(SH.p1_zavg.mean()), n_pass_both=int(((SH.d_prior_lo > 0) &
                                                                           (SH.d_null_lo > 0)).sum()))

# ============================================================================================ circularity sensitivity
cs_rows = []
for name, mask, dl in (("primary: flagged excluded (targets + lists)", ~TT.flagged.values, True),
                       ("flagged + unscannable excluded", ~(TT.flagged | TT.unscannable).values, True),
                       ("fully circular only excluded", ~TT.fully_circular.values, True),
                       ("flagged removed from targets only", ~TT.flagged.values, False),
                       ("no circularity exclusion", np.ones(len(TT), bool), True)):
    gs, tg, dr = tsets(mask, dl)
    Ec = dict(zavg=B.evaluate(gs, S_main.r1, tg, dr, S_main.sizes),
              prior=B.evaluate(gs, prior_lists, tg, dr, S_main.sizes),
              null=B.evaluate_null(gs, nulls, S_main.r1, tg, dr, S_main.sizes))
    row = dict(analysis=name, n=len(gs), p1_zavg=Ec["zavg"].hit1.mean(), p1_prior=Ec["prior"].hit1.mean(),
               p1_null=Ec["null"].hit1.mean())
    for b_ in ("prior", "null"):
        r = B.pdiff(Ec["zavg"].hit1, Ec[b_].hit1, cl(gs))
        row.update({f"d_{b_}": r["estimate"], f"d_{b_}_lo": r["ci_percentile"][0], f"d_{b_}_hi": r["ci_percentile"][1]})
    row["iut_pass"] = bool(row["d_prior_lo"] > 0 and row["d_null_lo"] > 0)
    cs_rows.append(row)
CS = pd.DataFrame(cs_rows)
CS.to_csv(OUT / "circularity_sensitivity.tsv", sep="\t", index=False, float_format="%.6f")

# ============================================================================================ V1 (GO CC complexes)
t = time.perf_counter()
v1t0 = B.build_v1(base, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
v1cur = B.build_v1(base, "data/raw/go/current/goa_human.gaf.gz", label="current")
cand_v1 = {t_ for t_, s in zip(v1t0.terms, v1t0.size) if B.LO <= s <= B.HI}
vrows = []
for g in Hpos:
    for t_ in sorted((v1cur.prop.get(g, frozenset()) - v1t0.prop.get(g, frozenset())) & cand_v1):
        vrows.append(dict(pos=g, go_id=t_, col=v1t0.col[t_], size_t0=int(v1t0.size[v1t0.col[t_]]),
                          pmids=B.support_pmids(v1cur, g, t_)))
V1T = pd.DataFrame(vrows, columns=["pos", "go_id", "col", "size_t0", "pmids"])
fl1 = B.circ_lookup({p for ps in V1T.pmids for p in ps}) if len(V1T) else None
V1T["flagged"] = [s[0] for s in B.target_states(V1T.pmids, fl1)] if len(V1T) else []
etc = {c for c, t_ in enumerate(v1t0.terms) if base.onto.ancestors(t_) & set(B.ETC1_MITORIBO)}
V1T["etc1_mitoribo"] = V1T.col.isin(etc)
tp = set(pd.read_csv(C.ROOT / "data/raw/humap_train/Train_positive_pairs.txt", sep="\t", header=None,
                     dtype=str).stack().unique())
humap_train = {base.pos[h] for a in tp for h in base.acc_map.get(a, ()) if h in base.pos}
RES["v1"] = dict(n_target_pairs=len(V1T), n_flagged=int(V1T.flagged.sum()) if len(V1T) else 0,
                 n_new_pmids_queried=int(fl1.attrs.get("n_new_queried", 0)) if fl1 is not None else 0,
                 n_etc1_mitoribo_terms=len(etc), n_humap_train_genes=len(humap_train))
v1_rows = []
if len(V1T):
    kp = V1T[~V1T.flagged]
    H1 = sorted(kp.pos.unique().tolist())
    T1all = V1T.groupby("pos").go_id.apply(set).to_dict()
    n1, _ = B.select_nulls(v1t0, base.matches, H1, T1all)
    S1 = B.Scored(v1t0, base.nb, base.matches, set(H1) | {m for v in n1.values() for m in v}, "V1 t0")
    pl1 = {g: S1.prior(g) for g in H1}
    D1all = V1T[V1T.flagged].groupby("pos").col.apply(set).to_dict()
    pmid_v1 = {g: pmid_sets.get(g, set()) for g in H1}
    CL1 = B.clusters_for(H1, pmid_v1, base.nb)
    variants = []
    tg = kp.groupby("pos").col.apply(set).to_dict()
    variants.append(("V1 all complexes", H1, tg, D1all))
    kp2 = kp[~kp.etc1_mitoribo]
    tg2 = kp2.groupby("pos").col.apply(set).to_dict()
    d2 = {g: set(D1all.get(g, set())) | etc for g in H1}
    variants.append(("V1 without ETC complex I and mitoribosome", sorted(tg2), tg2, d2))
    variants.append(("V1, hu.MAP-train members", [g for g in H1 if g in humap_train], tg, D1all))
    variants.append(("V1, not hu.MAP-train members", [g for g in H1 if g not in humap_train], tg, D1all))
    variants.append(("V1 without ETC-I/mitoribosome, hu.MAP-train members",
                     [g for g in tg2 if g in humap_train], tg2, d2))
    variants.append(("V1 without ETC-I/mitoribosome, not hu.MAP-train members",
                     [g for g in tg2 if g not in humap_train], tg2, d2))
    idx1 = {g: i for i, g in enumerate(H1)}
    for name, gs, tgv, dv in variants:
        if not gs:
            v1_rows.append(dict(analysis=name, n=0))
            continue
        e = dict(zavg=B.evaluate(gs, S1.r1, tgv, dv, S1.sizes), prior=B.evaluate(gs, pl1, tgv, dv, S1.sizes),
                 null=B.evaluate_null(gs, n1, S1.r1, tgv, dv, S1.sizes))
        c1 = np.asarray(CL1["primary"])[[idx1[g] for g in gs]]
        row = dict(analysis=name, n=len(gs), clusters=CL1["primary_name"], p1_zavg=e["zavg"].hit1.mean(),
                   p1_prior=e["prior"].hit1.mean(), p1_null=e["null"].hit1.mean(),
                   coverage=e["zavg"].has_pred.mean())
        b = B.mci(e["zavg"].hit1.values, c1)
        row.update(p1_ci_lo=b["ci_percentile"][0], p1_ci_hi=b["ci_percentile"][1])
        for b_ in ("prior", "null"):
            r = B.pdiff(e["zavg"].hit1, e[b_].hit1, c1)
            row.update({f"d_{b_}": r["estimate"], f"d_{b_}_lo": r["ci_percentile"][0],
                        f"d_{b_}_hi": r["ci_percentile"][1]})
        v1_rows.append(row)
    RES["v1"].update(n_genes=len(H1), clusters=CL1["summary"], cluster_rule=CL1["primary_name"])
V1R = pd.DataFrame(v1_rows)
V1R.to_csv(OUT / "v1.tsv", sep="\t", index=False, float_format="%.6f")
timing["v1_s"] = round(time.perf_counter() - t, 1)

# ============================================================================================ named controls
t = time.perf_counter()
lo_w, hi_w = B.CASE_WINDOW
v2t0w = B.build_v2(base, f"{B.T0_DIR}/goa_human.gaf.gz", lo=lo_w, hi=hi_w, label="t0 window 2-300")
v1p, v1p_names = B.build_v1prime(base, v1cur, lo_w, hi_w)
if B.DRY:
    ctrl = [(gt.symbol.values[g], g) for g in Hpos[:5]]
else:
    ctrl = [(s, int(np.flatnonzero(gt.symbol.values == s)[0])) for s in B.CONTROLS
            if (gt.symbol.values == s).any() and base.scor[np.flatnonzero(gt.symbol.values == s)[0]]]
    RES["controls_not_scorable"] = [s for s in B.CONTROLS if s not in {x for x, _ in ctrl}]
cpos = [g for _, g in ctrl]
cand_w = {t_ for t_, s in zip(v2t0w.terms, v2t0w.size) if lo_w <= s <= hi_w}
ctg = {}
for s, g in ctrl:
    T = (v2cur.prop.get(g, frozenset()) - v2t0w.prop.get(g, frozenset())) & cand_w
    ctg[g] = {t_: B.support_pmids(v2cur, g, t_) for t_ in T}
flc = B.circ_lookup({p for d in ctg.values() for ps in d.values() for p in ps})
Sc = B.Scored(v2t0w, base.nb, base.matches, cpos, "controls t0 2-300")
scp = vocab.score_queries(v1p, base.nb, base.matches, np.asarray(sorted(cpos)), loo=True)
v1p_r1 = scp.ranked("R1")
crows = []
Hset = set(Hpos)
for s, g in ctrl:
    T = ctg[g]
    stt = dict(zip(T, B.target_states(list(T.values()), flc))) if T else {}
    keep_t = {t_ for t_ in T if not stt[t_][0]}
    drop_c = {v2t0w.col[t_] for t_ in T if stt[t_][0]}
    lst = [c for c in Sc.r1.get(g, []) if c not in drop_c]
    tcols = {v2t0w.col[t_] for t_ in keep_t}
    ranks = [i + 1 for i, c in enumerate(lst) if c in tcols]
    best = min(ranks) if ranks else None
    lab = v1p_r1.get(g, [])
    crows.append(dict(symbol=s, hgnc_id=gt.hgnc_id.values[g], weak=s in C.fz("holdout", "weak_controls"),
                      in_H=g in Hset, n_targets_2_300=len(T), n_targets_flagged=len(T) - len(keep_t),
                      n_reportable=len(lst), rank_best_true_term=best,
                      best_true_term=(v2t0w.terms[lst[best - 1]] + " " + base.onto.name(v2t0w.terms[lst[best - 1]])
                                      if best else ""),
                      best_true_term_size_t0=int(v2t0w.size[lst[best - 1]]) if best else None,
                      top1_term=(v2t0w.terms[lst[0]] + " " + base.onto.name(v2t0w.terms[lst[0]])) if lst else "",
                      top1_size_t0=int(Sc.sizes(g)[lst[0]]) if lst else None,
                      hit_at_1=bool(best == 1),
                      top_v1prime_label=((v1p_names.get(v1p.terms[lab[0]], "") if v1p.terms[lab[0]].startswith("MC:") else v1p.terms[lab[0]] + " " + v1p_names.get(v1p.terms[lab[0]], "")) if lab else ""),
                      zmean=float(base.zmean[g]), R=float(base.R[g])))
CT = pd.DataFrame(crows)
CT.to_csv(OUT / "controls_case_series.tsv", sep="\t", index=False)
timing["controls_s"] = round(time.perf_counter() - t, 1)
RES["controls"] = dict(n=len(CT), n_hit1=int(CT.hit_at_1.sum()),
                       n_rank_le5=int((CT.rank_best_true_term.fillna(1e9) <= 5).sum()),
                       n_rank_le10=int((CT.rank_best_true_term.fillna(1e9) <= 10).sum()),
                       n_no_true_term_ranked=int(CT.rank_best_true_term.isna().sum()),
                       n_new_pmids_queried=int(flc.attrs.get("n_new_queried", 0)))

# ============================================================================================ covariates, SMDs, quintiles
cov_t0 = B.coverage(base, v2t0)
cov_cur = B.coverage(base, v2cur)
sc_ = base.scor
cov_t0_pct = B.pct_rank(cov_t0, cov_t0[sc_])
cov_cur_pct = B.pct_rank(cov_cur, cov_cur[sc_])
ref_size_t0 = B.base_top_sizes(base, v2t0)
ref_size_cur = B.base_top_sizes(base, v2cur)          # aggregate reference only (no per-gene U output)
Ulist = pd.read_csv(C.ROOT / "preregistration/uncharacterised_genes.tsv", sep="\t", dtype=str)
Upos = np.array(sorted(base.pos[h] for h in Ulist[Ulist.scorable == "True"].hgnc_id if h in base.pos))
LOOpos = pd.read_csv(C.ROOT / "results/loo_sample.tsv", sep="\t").matrix_index.values
mean_eff = base.cov["mean"].values
sd_eff = np.exp(base.cov.log_sd.values)
nanf = base.cov.nan_fraction.values
covs = dict(mean_effect=(mean_eff, mean_eff), sd=(sd_eff, sd_eff), nan_fraction=(nanf, nanf),
            topK_mean_zavg=(base.zmean, base.zmean), R=(base.R, base.R),
            coverage_pct=(cov_t0_pct, cov_cur_pct), coverage_raw=(cov_t0, cov_cur))
Parr = np.asarray(P)
smd_rows = []
for nm, (h_, c_) in covs.items():
    smd_rows.append(dict(covariate=nm, mean_H=np.nanmean(h_[Parr]), mean_U=np.nanmean(c_[Upos]),
                         mean_LOO=np.nanmean(c_[LOOpos]), smd_H_vs_U=B.smd(h_[Parr], c_[Upos]),
                         smd_H_vs_LOO=B.smd(h_[Parr], c_[LOOpos]), smd_U_vs_LOO=B.smd(c_[Upos], c_[LOOpos])))
SMD = pd.DataFrame(smd_rows)
SMD.to_csv(OUT / "covariate_smd.tsv", sep="\t", index=False, float_format="%.4f")
RES["smd"] = dict(n_H=len(P), n_U=len(Upos), n_LOO=len(LOOpos), note="H at t0 (coverage), U/LOO at current")

zq = pd.qcut(base.zmean[Parr], 5, labels=[f"Q{i}" for i in range(1, 6)])
qrows = []
for lev in [f"Q{i}" for i in range(1, 6)]:
    g = Parr[np.asarray(zq == lev)]
    row = dict(quintile=lev, n=len(g), zmean_min=base.zmean[g].min(), zmean_max=base.zmean[g].max())
    for m in METH:
        v = E[m].hit1.loc[g].values
        b = B.mci(v, cl(g))
        row.update({f"p1_{m}": v.mean(), f"p1_{m}_lo": b["ci_percentile"][0], f"p1_{m}_hi": b["ci_percentile"][1]})
    r = B.pdiff(E["zavg"].hit1.loc[g], E["prior"].hit1.loc[g], cl(g))
    row.update(d_prior=r["estimate"], d_prior_lo=r["ci_percentile"][0], d_prior_hi=r["ci_percentile"][1])
    qrows.append(row)
QT = pd.DataFrame(qrows)
QT.to_csv(OUT / "signal_quintiles.tsv", sep="\t", index=False, float_format="%.6f")

# ============================================================================================ per-gene table
fams = B.load_families()
PG = pd.DataFrame(index=pd.Index(P, name="pos"))
PG["hgnc_id"] = gt.hgnc_id.values[Parr]
PG["symbol"] = gt.symbol.values[Parr]
PG["n_targets"] = [len(Tp[g]) for g in P]
PG["min_target_size_t0"] = minsize.loc[P].values
PG["stratum2"], PG["stratum3"] = strata2.values, strata3.values
for m in METH:
    for c in ("hit1", "rr", "hit1_small", "has_pred", "top1size"):
        PG[f"{c}_{m}"] = E[m][c].values
    if m != "null":
        PG[f"top1_{m}"] = [v2t0.terms[c] if c >= 0 else "" for c in E[m].top1.values]
PG["null_matches"] = [";".join(str(gt.hgnc_id.values[m]) for m in nulls[g]) for g in P]
PG["null_skipped"] = [skipped[g] for g in P]
PG["cluster_pmid"], PG["cluster_pmid_ng"], PG["cluster_primary"] = cl(P, "pmid"), cl(P, "both"), clP
PG["zmean"], PG["R"] = base.zmean[Parr], base.R[Parr]
PG["coverage_raw"], PG["cov_pct"] = cov_t0[Parr], cov_t0_pct[Parr]
PG["size_pct"] = B.pct_rank(np.log(PG.top1size_zavg.values), np.log(ref_size_t0[sc_]))
PG["family"] = [B.family_of(t_, base.onto, fams) if t_ else "" for t_ in PG.top1_zavg]
PG["mean_effect"], PG["sd"], PG["nan_fraction"] = mean_eff[Parr], sd_eff[Parr], nanf[Parr]
PG["signal_quintile"] = np.asarray(zq).astype(str)
PG["humap_train"] = [g in humap_train for g in P]
PG.to_csv(OUT / "per_gene_core.tsv", sep="\t", float_format="%.6g")

CMP = pd.DataFrame(comp)
CMP.to_csv(OUT / "comparisons_core.tsv", sep="\t", index=False, float_format="%.6f")
pd.to_pickle(dict(Hpos=Hpos, P=P, Tp=Tp, Dp=Dp, T_all=T_all, nulls=nulls, TT=TT, pmid_sets=pmid_sets,
                  cl_primary=dict(zip(P, clP)), cl_sens=dict(zip(P, clPs)), CLall_names=(CLall["primary_name"],
                                                                                        CLall["sensitivity_name"]),
                  cov_t0=cov_t0, cov_cur=cov_cur, cov_t0_pct=cov_t0_pct, cov_cur_pct=cov_cur_pct,
                  ref_size_t0=ref_size_t0, ref_size_cur=ref_size_cur, Upos=Upos, LOOpos=LOOpos,
                  E={m: E[m] for m in METH}), DER / "core.pkl")
pd.DataFrame(dict(matrix_index=np.flatnonzero(sc_), coverage_t0=cov_t0[sc_], coverage_cur=cov_cur[sc_])).to_csv(
    DER / "coverage_reference.tsv.gz", sep="\t", index=False, float_format="%.6g")
RES["timing"] = timing

# ============================================================================================ report
man = C.write_manifest(OUT / "core_manifest.json", "scripts/32_holdout_core.py", gate,
                       [*B.M5.INPUTS, f"{B.T0_DIR}/goa_human.gaf.gz",
                                     "results/holdout/H_genes.tsv", "results/holdout/H_targets.tsv",
                                     "results/holdout/circularity_annotations.tsv",
                                     "results/holdout/circularity_flags.tsv", "results/assessability/R_all.tsv",
                                     "data/derived/baselines/gls_rows.npy"],
                       seed=B.SEED, t0=T_START, extra=dict(timing=timing))
RES["runtime_s"] = man["runtime_s"]
B.jdump(RES, OUT / "core_results.json")


def f3(x):
    return f"{x:.3f}"


L = ["# M5b core results on the temporal hold-out H (scripts/32)", "",
     f"Generated {man['created']} (runtime {man['runtime_s']} s). Gate tag `{gate['tag']}`. Ranker R1; bootstrap "
     f"{B.NBOOT:,} replicates, seed {B.SEED}; CIs 95% percentile (BCa in comparisons_core.tsv)."
     + (" **DRY RUN (LOO genes, pseudo-targets) -- not H.**" if B.DRY else ""), "",
     "## H", "",
     f"H genes {len(Hpos)}; (gene, target) pairs {len(TT)}; flagged {int(TT.flagged.sum())} (fully circular "
     f"{int(TT.fully_circular.sum())}); unscannable {int(TT.unscannable.sum())}. Primary H (>= 1 non-flagged target): "
     f"**{len(P)}** ({len(Hpos) - len(P)} genes lose every target). Target pairs whose term is not a t0 V2 column: "
     f"{int((TT.col < 0).sum())}.", "",
     f"Clusters (all {len(Hpos)} H genes): PMID-only {CLall['summary']['PMID-only']}; PMID+N(g) "
     f"{CLall['summary']['PMID+N(g)']}. Largest PMID+N(g) component fraction "
     f"{CLall['summary']['PMID+N(g)']['largest_frac']:.3f} vs fallback threshold {B.CLUSTER_FALLBACK_FRAC} -> "
     f"**primary clusters: {CLall['primary_name']}** (sensitivity: {CLall['sensitivity_name']}).", "",
     "## Primary test (intersection-union)", "",
     "| method | precision@1 | 95% CI | MRR | 95% CI | coverage | precision@1 (≤50) | n (≤50) |",
     "|---|---|---|---|---|---|---|---|"]
for x in SUMM.itertuples():
    L.append(f"| {x.label} | {f3(x.precision_at_1)} | {f3(x.p1_ci_lo)}–{f3(x.p1_ci_hi)} | {f3(x.MRR)} | "
             f"{f3(x.mrr_ci_lo)}–{f3(x.mrr_ci_hi)} | {x.coverage:.3f} | {f3(x.p1_small)} "
             f"({f3(x.p1_small_ci_lo)}–{f3(x.p1_small_ci_hi)}) | {x.n_small} |")
L += ["", "| comparison | clusters | difference | 95% percentile CI | BCa CI | design effect | CI excludes 0 |",
      "|---|---|---|---|---|---|---|"]
for x in CMP.itertuples():
    L.append(f"| {x.comparison} | {x.clusters} | {x.diff:+.4f} | {x.ci_lo:+.4f} to {x.ci_hi:+.4f} | "
             f"{x.bca_lo:+.4f} to {x.bca_hi:+.4f} | {x.design_effect:.2f} | {x.excludes_zero} |")
L += ["", f"**Primary IUT: {'PASS' if iut_pass else 'FAIL'}** (both percentile CIs > 0: {iut_pass}; BCa: "
      f"{iut_pass_bca}). Effective n = |H| / design effect: "
      + ", ".join(f"{k} {v:.0f}" for k, v in neff.items())
      + f" -> {'underpowered label applies' if RES['primary']['underpowered'] else 'not underpowered'} (rule < 300).",
      "", f"Key secondary: GLS precision@1 {f3(E['gls'].hit1.mean())}; zavg - GLS "
      f"{RES['gls']['est']:+.4f} ({B.fmt_ci(RES['gls']['ci'], 4, True)}); GLS ≥ zavg: "
      f"{RES['gls']['gls_ge_zavg']}.", "", "## Top-1 term size (t0 annotated scorable genes)", "",
      "| method | n | p10 | Q1 | median | Q3 | p90 | mean | fraction ≤ 50 |", "|---|---|---|---|---|---|---|---|---|"]
for x in SZ.itertuples():
    L.append(f"| {x.method} | {x.n} | {x.p10:.0f} | {x.q1:.0f} | {x.median:.0f} | {x.q3:.0f} | {x.p90:.0f} | "
             f"{x.mean:.1f} | {x.frac_le50:.3f} |")
L += ["", "## Split-half networks (half-specific N(g))", "",
      "| seed | half | precision@1 | 95% CI | − prior | 95% CI | − matched null | 95% CI |", "|---|---|---|---|---|---|---|---|"]
for x in SH.itertuples():
    L.append(f"| {x.seed} | {x.half} | {f3(x.p1_zavg)} | {f3(x.p1_ci_lo)}–{f3(x.p1_ci_hi)} | {x.d_prior:+.3f} | "
             f"{x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f} | {x.d_null:+.3f} | {x.d_null_lo:+.3f} to {x.d_null_hi:+.3f} |")
L += ["", "## Circularity sensitivity", "",
      "| analysis | n | zavg | prior | null | − prior (CI) | − null (CI) | IUT |", "|---|---|---|---|---|---|---|---|"]
for x in CS.itertuples():
    L.append(f"| {x.analysis} | {x.n} | {f3(x.p1_zavg)} | {f3(x.p1_prior)} | {f3(x.p1_null)} | {x.d_prior:+.3f} "
             f"({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | {x.d_null:+.3f} ({x.d_null_lo:+.3f} to "
             f"{x.d_null_hi:+.3f}) | {'pass' if x.iut_pass else 'fail'} |")
L += ["", "## V1 (GO CC complexes, t0)", "",
      f"V1 target pairs {RES['v1']['n_target_pairs']} (flagged {RES['v1']['n_flagged']}); ETC-I/mitoribosome "
      f"terms {RES['v1']['n_etc1_mitoribo_terms']}; hu.MAP-train genes {RES['v1']['n_humap_train_genes']}.", "",
      "| analysis | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) |", "|---|---|---|---|---|---|---|"]
for x in V1R.itertuples():
    if x.n == 0:
        L.append(f"| {x.analysis} | 0 | | | | | |")
        continue
    L.append(f"| {x.analysis} | {x.n} | {f3(x.p1_zavg)} ({f3(x.p1_ci_lo)}–{f3(x.p1_ci_hi)}) | {f3(x.p1_prior)} | "
             f"{f3(x.p1_null)} | {x.d_prior:+.3f} ({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) | {x.d_null:+.3f} "
             f"({x.d_null_lo:+.3f} to {x.d_null_hi:+.3f}) |")
L += ["", "## Named-control case series (window 2–300; descriptive, never pooled)", "",
      "| control | weak | in H | targets (flagged) | reportable terms | rank of best true term | best true term | "
      "top-1 term | top V1′ label |", "|---|---|---|---|---|---|---|---|---|"]
for x in CT.itertuples():
    rk = "—" if pd.isna(x.rank_best_true_term) else int(x.rank_best_true_term)
    L.append(f"| {x.symbol} | {x.weak} | {x.in_H} | {x.n_targets_2_300} ({x.n_targets_flagged}) | {x.n_reportable} | "
             f"{rk} | {x.best_true_term} | {x.top1_term} | {x.top_v1prime_label} |")
L += ["", "## Covariate shift (SMD)", "", "| covariate | mean H | mean U | mean LOO | SMD H−U | SMD H−LOO | SMD U−LOO |",
      "|---|---|---|---|---|---|---|"]
for x in SMD.itertuples():
    L.append(f"| {x.covariate} | {x.mean_H:.4g} | {x.mean_U:.4g} | {x.mean_LOO:.4g} | {x.smd_H_vs_U:+.3f} | "
             f"{x.smd_H_vs_LOO:+.3f} | {x.smd_U_vs_LOO:+.3f} |")
L += ["", "Coverage enters as within-release percentile (H at t0, U and LOO at current); raw shown for reference.", "",
      "## Precision@1 by signal quintile (top-K mean zavg within H)", "",
      "| quintile | n | zavg range | zavg | prior | null | GLS | zavg − prior (CI) |", "|---|---|---|---|---|---|---|---|"]
for x in QT.itertuples():
    L.append(f"| {x.quintile} | {x.n} | {x.zmean_min:.2f}–{x.zmean_max:.2f} | {f3(x.p1_zavg)} ({f3(x.p1_zavg_lo)}–"
             f"{f3(x.p1_zavg_hi)}) | {f3(x.p1_prior)} | {f3(x.p1_null)} | {f3(x.p1_gls)} | {x.d_prior:+.3f} "
             f"({x.d_prior_lo:+.3f} to {x.d_prior_hi:+.3f}) |")
L += ["", "## Notes", "",
      f"- Matched null: first {B.NNULL} matches not annotated at t0 to any term of the full T(g) (before circularity "
      f"exclusion, so the same matches serve every sensitivity); matches skipped: median "
      f"{int(np.median(list(skipped.values())))}, max {max(skipped.values())}. Each match is scored like an H query "
      "(loo=False, IPI rule for that match) and its list is compared with T(g) after g's flagged terms are dropped.",
      "- ≤ 50 analysis: ranked lists and targets restricted to terms with ≤ 50 annotated scorable genes at t0 (g's "
      f"per-query size); genes without such a target dropped ({RES['small']['n_dropped']}).",
      "- GLS strata: smallest primary-target size at t0 (the gene's true complex/module size; review round 1 item 8).",
      "- Split halves: half top-60 lists restricted to BG_A ∩ BG_B ∩ BG_full, first 25 (scripts/15 rule); matched "
      "null and prior recomputed on each half network; clusters fixed (full-data).",
      "- V1: same rules as V2 on GO CC terms under GO:0032991 (rows citing hu.MAP papers dropped); targets = current − "
      "t0 V1 terms of H genes with t0 size 5–200; flagged targets excluded; ETC-I = GO:0045271, mitoribosome = "
      "GO:0005761 and descendants removed from targets and lists; hu.MAP-train = gene in the tool's positive training "
      "pairs.",
      "- Controls: targets = current − t0 V2 terms with t0 size 2–300, flagged excluded; ranked at t0 with window "
      "2–300; V1′ (current: V1 ∪ Complex Portal ∪ MitoCarta3.0 pathways, window 2–300, own annotations removed) top "
      "reportable label.", ""]
(OUT / "core.md").write_text("\n".join(L))
log(f"done in {man['runtime_s']} s; primary IUT {'PASS' if iut_pass else 'FAIL'}")
