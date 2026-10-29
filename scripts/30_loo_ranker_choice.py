#!/usr/bin/env python
"""30_loo_ranker_choice.py -- ranker choice on the LOO benchmark (DESIGN.md v2.3 §3.1, §3.2.1, §3.2.3); M5a.

LOO sample: results/loo_sample.tsv (3,000 scorable genes in neither U nor H; scripts/16). No H or U gene is scored.
Vocabulary: V2 current (src/vocab.py; D1 evidence codes, NOT and colocalizes_with rows dropped, BP+MF propagated over
is_a/part_of with the current obo, candidate terms 5-200 annotated scorable genes with the query's annotations removed,
IPI with/from rule). Neighbours N(g): full zavg_BEF, K = 25 (scripts/13). Matched lists: 500 (scripts/13).

Targets T(g) = the query's own current V2 terms that are candidate terms for that query (size window computed with the
query removed). Circularity (§3.2.3, round-2 item O2): every PMID supporting a target (the query's kept GAF rows to the
target or a descendant) is queried in Europe PMC with the scripts/05 query (imported unchanged: same terms, batching,
cache). Target states: flagged (>= 1 supporting PMID flagged; = scripts/05 ``any_pmid_flagged``), unscannable (not
flagged and no supporting PMID found in Europe PMC: GO_REF/Reactome-only rows or PMIDs unknown to Europe PMC), clean.
Primary: flagged targets are excluded (removed from T(g) and from the ranked lists -- an annotated-but-circular term is
neither a hit nor a miss); unscannable targets are included. Genes with no remaining target leave the benchmark.
Sensitivities: exclusion only of "fully circular" targets (every supporting row flagged = scripts/05 ``fully_circular``);
also excluding unscannable targets; flagged targets removed from T(g) only (kept in ranked lists); no exclusion.

Rankers R1 (S), R2 (hypergeometric p), R3 (p_emp, 500 matched genes minus A_t); reportable = >= 2 supporting partners;
metric = MRR of the first correct reportable term (RR = 0 if none); precision@1 (no reportable term -> 0).
Ranker choice (frozen rule): highest MRR; any ranker within |dMRR| < 0.005 of the best is tied; among tied rankers R3,
then R1 (R2 only if it beats both by >= 0.005). Prior-only (context): candidate terms ranked by current size (query
removed), ties by GO id. CIs (descriptive): gene bootstrap and cluster bootstrap (connected components of LOO genes
sharing a supporting target PMID or appearing in each other's N(g)), 1,000 replicates, seed 0, percentile. The cluster
bootstrap is computed only when the largest component holds <= 20% of the genes; on the LOO sample both link graphs
form one giant component (N(g) links among 3,000 genes of an 18k-gene network), so only the gene bootstrap is reported
and the component sizes are given.

Outputs: results/calibration/loo_ranker_choice.md, loo_ranker_choice.tsv (summary), loo_per_gene.tsv.gz,
loo_targets.tsv.gz, loo_circularity_pmids.tsv.gz, loo_ranker_choice_manifest.json; data/derived/calibration/
loo_scores.pkl (score table, git-ignored).
Run: .env/bin/python -I scripts/30_loo_ranker_choice.py
"""
import importlib.util
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
from src import knownness as kn  # noqa: E402
from src import metrics as mt  # noqa: E402
from src import vocab  # noqa: E402

K = C.fz("predictor", "k_neighbours")
LO, HI = C.fz("vocabulary", "candidate_term_min_genes"), C.fz("vocabulary", "candidate_term_max_genes")
TIE = C.fz("predictor", "ranker_tie_mrr_delta")
TIE_ORDER = C.fz("predictor", "ranker_tie_order")
RANKERS = C.fz("predictor", "rankers")
SMALL = C.fz("vocabulary", "small_term_max_genes")
SEED = C.fz("seeds", "bootstraps")
NBOOT = 1000                                  # descriptive CIs (task spec); primary H CIs use 10,000 (§3.5)
OUT = C.ROOT / "results" / "calibration"
DER = C.DERIVED / "calibration"
OUT.mkdir(parents=True, exist_ok=True)
DER.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------------------------ inputs
gt = M5.load_index()
G = len(gt)
nb = M5.load_neighbours(K, G)
matches = M5.load_matches()
loo = M5.load_loo(gt)
Q = loo.matrix_index.values.astype(np.int64)
v2 = M5.build_current_v2(gt, LO, HI)
terms = v2.terms

# ------------------------------------------------------------------------------------------------ scoring
t = time.perf_counter()
base = vocab.all_gene_scores(nb, v2)
sc = vocab.score_queries(v2, nb, matches, Q, loo=True, base=base, log=C.log)
t_score = time.perf_counter() - t
C.log(f"scored {len(Q)} LOO queries in {t_score:.0f} s")
pd.to_pickle(dict(table=sc.table, info=sc.info, queries=sc.queries, terms=terms), DER / "loo_scores.pkl")

# brute-force check (explicit re-propagation) on 12 queries: 6 with IPI removals, 6 random
info = sc.info.set_index("query")
rng = np.random.default_rng(SEED)
ipi_q = info.index[info.n_ipi_genes > 0].values
chk = np.r_[ipi_q[:6], rng.choice(Q, 6, replace=False)]
for g in chk:
    ref = vocab.explicit_scores(v2, nb, matches, int(g), loo=True)
    got = sc.table[sc.table["query"] == g]
    a, b = ref[ref.reportable].set_index("term").sort_index(), got[got.reportable].set_index("term").sort_index()
    assert list(a.index) == list(b.index), g
    for c in ("S", "p_hyper", "p_emp"):
        assert np.allclose(a[c].astype(float), b[c].astype(float), rtol=1e-9, atol=1e-12), (g, c)
    for c in ("rank_R1", "rank_R2", "rank_R3"):
        assert (a[c].values == b[c].values).all(), (g, c)
C.log(f"brute-force check passed on {len(chk)} queries ({min(6, len(ipi_q))} with IPI-rule removals)")

# ------------------------------------------------------------------------------------------------ targets
qpos = {int(g): i for i, g in enumerate(Q)}
rows_by = {int(p): d for p, d in v2.rows[v2.rows.pos.isin(set(Q))].groupby("pos")}
trows = []
for g in Q:
    i = qpos[int(g)]
    cand = v2.candidates(sc.sizes[i])
    own = v2.own_terms(int(g))
    tg = own[cand[own]]
    if not len(tg):
        continue
    d = rows_by[int(g)]
    anc = [v2.onto.ancestors(x) for x in d.go_id.values]
    refs = d.reference.values
    for c in tg:
        tid = terms[c]
        m = np.array([tid in s for s in anc])
        row_pm = [kn.pmids_from_refs([r]) for r in refs[m]]
        trows.append(dict(pos=int(g), term=int(c), go_id=tid, n_rows=int(m.sum()),
                          row_pmids=";".join("|".join(map(str, p)) for p in row_pm),
                          size=int(sc.sizes[i, c])))
TT = pd.DataFrame(trows)
C.log(f"targets: {len(TT)} (gene, term) pairs over {TT.pos.nunique()} LOO genes")

# ------------------------------------------------------------------------------------------------ circularity
spec = importlib.util.spec_from_file_location("circ05", C.ROOT / "scripts" / "05_circularity_query.py")
circ = importlib.util.module_from_spec(spec)
spec.loader.exec_module(circ)
Path(circ.CACHE).mkdir(parents=True, exist_ok=True)
pmids = sorted({int(p) for s in TT.row_pmids for r in s.split(";") for p in r.split("|") if p})
C.log(f"circularity: {len(pmids)} supporting PMIDs; querying Europe PMC (cached)")
t = time.perf_counter()
meta, hits = {}, set()
for i in range(0, len(pmids), circ.BATCH):
    b = pmids[i:i + circ.BATCH]
    for r in circ.search_all(circ.ext_clause(b) + " AND SRC:MED", "lite"):
        if r.get("pmid"):
            meta[int(r["pmid"])] = r
    for r in circ.search_all(circ.ext_clause(b) + " AND SRC:MED AND " + circ.TERM_CLAUSE, "idlist"):
        if r.get("pmid"):
            hits.add(int(r["pmid"]))
    if (i // circ.BATCH + 1) % 100 == 0:
        C.log(f"  {i + len(b)}/{len(pmids)} PMIDs, {len(hits)} flagged")
# per-PMID validation of the batched form (systematic sample + Wainberg 2021 + up to 40 flagged)
val = sorted(set(pmids[:: max(1, len(pmids) // 40)][:40]) | set(sorted(hits)[:40]) | {circ.WAINBERG_2021})
disagree = []
for p in val:
    d = circ.get({"query": f"EXT_ID:{p} AND SRC:MED AND {circ.TERM_CLAUSE}", "resultType": "idlist",
                  "format": "json", "pageSize": 25})
    if (d.get("hitCount", 0) > 0) != (p in hits) and p in set(pmids):
        disagree.append(p)
term_hits = {p: [] for p in hits}
hl = sorted(hits)
for tm in circ.TERMS:
    for i in range(0, len(hl), circ.BATCH):
        for r in circ.search_all(circ.ext_clause(hl[i:i + circ.BATCH]) + f" AND SRC:MED AND ({tm})", "idlist"):
            if r.get("pmid") and int(r["pmid"]) in term_hits:
                term_hits[int(r["pmid"])].append(tm)
t_circ = time.perf_counter() - t
F = pd.DataFrame({"pmid": pmids})
F["found_in_europepmc"] = F.pmid.isin(meta)
F["full_text_searchable"] = F.pmid.map(lambda p: meta.get(p, {}).get("inEPMC") == "Y")
F["pub_year"] = F.pmid.map(lambda p: meta.get(p, {}).get("pubYear", ""))
F["circular_flag"] = F.pmid.isin(hits)
F["matched_terms"] = F.pmid.map(lambda p: "|".join(term_hits.get(p, [])))
F.to_csv(OUT / "loo_circularity_pmids.tsv.gz", sep="\t", index=False)
flag, found, ftxt = (dict(zip(F.pmid, F[c])) for c in ("circular_flag", "found_in_europepmc", "full_text_searchable"))


def tstate(s):
    rows = [[int(p) for p in r.split("|") if p] for r in s.split(";")]
    allp = [p for r in rows for p in r]
    any_flag = any(flag[p] for p in allp)
    row_flag = [bool(r) and any(flag[p] for p in r) for r in rows]
    full = bool(rows) and all(row_flag)
    unscan = (not any_flag) and not any(found[p] for p in allp)
    abstract_only = bool(allp) and not any(ftxt[p] for p in allp)
    return any_flag, full, unscan, abstract_only, len(allp)


st = np.array([tstate(s) for s in TT.row_pmids], dtype=object)
TT["flagged"], TT["fully_circular"], TT["unscannable"] = st[:, 0].astype(bool), st[:, 1].astype(bool), st[:, 2].astype(bool)
TT["abstract_only"], TT["n_pmids"] = st[:, 3].astype(bool), st[:, 4].astype(int)
TT["state"] = np.where(TT.flagged, "flagged", np.where(TT.unscannable, "unscannable", "clean"))
TT.insert(1, "hgnc_id", gt.hgnc_id.values[TT.pos.values])
TT.insert(2, "symbol", gt.symbol.values[TT.pos.values])
TT["go_name"] = TT.go_id.map(v2.onto.name)
TT.drop(columns=["row_pmids"]).assign(
    pmids=[";".join(r for r in s.split(";")) for s in TT.row_pmids]).to_csv(OUT / "loo_targets.tsv.gz", sep="\t",
                                                                           index=False)
C.log(f"circularity done in {t_circ:.0f} s: {len(hits)} PMIDs flagged; targets flagged {int(TT.flagged.sum())}")

# ------------------------------------------------------------------------------------------------ metrics
ranked_all = {r: sc.ranked(r) for r in RANKERS}
size_of = lambda g, c: int(sc.sizes[qpos[g], c])  # noqa: E731


def prior_ranked(g, excl=()):
    i = qpos[g]
    cand = v2.candidates(sc.sizes[i]).copy()
    if len(excl):
        cand[list(excl)] = False
    return sc.prior_rank(i, cand)


def evaluate(exclude_mask, drop_from_lists=True):
    """Per-gene metrics with targets = TT[~exclude_mask]; excluded (gene, term) pairs are dropped from the ranked
    lists when drop_from_lists."""
    keep = TT[~exclude_mask]
    excl = TT[exclude_mask].groupby("pos").term.apply(set).to_dict() if drop_from_lists else {}
    tg = keep.groupby("pos").term.apply(set).to_dict()
    rows = []
    for g, T in tg.items():
        ex = excl.get(g, set())
        row = dict(pos=g, n_targets=len(T), n_excluded=len(ex))
        for r in RANKERS:
            lst = [c for c in ranked_all[r][g] if c not in ex]
            row[f"rr_{r}"] = mt.reciprocal_rank(lst, T)
            row[f"hit1_{r}"] = mt.hit_at_1(lst, T)
            row[f"top1_{r}"] = lst[0] if lst else -1
            row[f"top1size_{r}"] = size_of(g, lst[0]) if lst else np.nan
            row[f"has_pred_{r}"] = bool(lst)
        pl = prior_ranked(g, sorted(ex))
        hitpos = np.flatnonzero(np.isin(pl, list(T)))
        row["rr_prior"] = 1.0 / (hitpos[0] + 1) if len(hitpos) else 0.0
        row["hit1_prior"] = float(len(pl) > 0 and pl[0] in T)
        row["top1_prior"] = int(pl[0]) if len(pl) else -1
        row["top1size_prior"] = size_of(g, pl[0]) if len(pl) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("pos").reset_index(drop=True)


analyses = {
    "primary (flagged excluded; unscannable included)": (TT.flagged.values, True),
    "sens: fully-circular only excluded": (TT.fully_circular.values, True),
    "sens: flagged + unscannable excluded": ((TT.flagged | TT.unscannable).values, True),
    "sens: flagged removed from targets only": (TT.flagged.values, False),
    "sens: no circularity exclusion": (np.zeros(len(TT), bool), True),
}
PG = {k: evaluate(*v) for k, v in analyses.items()}
P = PG["primary (flagged excluded; unscannable included)"]

# clusters: shared supporting PMID of a primary target, or N(g) links among LOO genes
keep = TT[~TT.flagged]
pm_by = {g: {int(p) for s in d.row_pmids for r in s.split(";") for p in r.split("|") if p}
         for g, d in keep.groupby("pos")}
nbd = {int(g): set(nb.ids[g][nb.ids[g] >= 0].tolist()) for g in P.pos}
cl_both = mt.clusters_from_links(list(P.pos), pmids=pm_by, neighbours=nbd)
cl_nb = mt.clusters_from_links(list(P.pos), neighbours=nbd)
cl_gene = np.arange(len(P))


def csize(cl):
    s = np.bincount(np.unique(cl, return_inverse=True)[1])
    return dict(n_clusters=int(len(s)), largest=int(s.max()))


cs = {"gene": csize(cl_gene), "N(g)+PMID": csize(cl_both), "N(g) only": csize(cl_nb)}
# a cluster bootstrap is only meaningful without a giant component; otherwise gene bootstrap only
use_cl_name = next((n for n in ("N(g)+PMID", "N(g) only") if cs[n]["largest"] <= 0.2 * len(P)), None)
use_cl = {"N(g)+PMID": cl_both, "N(g) only": cl_nb}.get(use_cl_name, cl_gene)
BOOTS = [("gene", cl_gene)] + ([("cluster", use_cl)] if use_cl_name else [])


def boot(d, cl):
    b = mt.cluster_bootstrap_mean(np.asarray(d, float), cl, n_boot=NBOOT, seed=SEED)
    return b["estimate"], b["ci_percentile"]


summ = []
for name, D in PG.items():
    for r in [*RANKERS, "prior"]:
        rr, h1 = D[f"rr_{r}"].values, D[f"hit1_{r}"].values
        row = dict(analysis=name, ranker=r, n_genes=len(D), MRR=rr.mean(), precision_at_1=h1.mean(),
                   coverage=D[f"has_pred_{r}"].mean() if r != "prior" else 1.0)
        if name.startswith("primary"):
            for lab, cl in BOOTS:
                e, ci = boot(rr, cl)
                row[f"MRR_ci_{lab}"] = f"{ci[0]:.4f}-{ci[1]:.4f}"
                e, ci = boot(h1, cl)
                row[f"p1_ci_{lab}"] = f"{ci[0]:.4f}-{ci[1]:.4f}"
            sz = D[f"top1size_{r}"].dropna().values
            q = np.quantile(sz, [0.1, 0.25, 0.5, 0.75, 0.9]) if len(sz) else [np.nan] * 5
            row.update(top1_size_p10=q[0], top1_size_q1=q[1], top1_size_median=q[2], top1_size_q3=q[3],
                       top1_size_p90=q[4], top1_size_mean=sz.mean() if len(sz) else np.nan,
                       top1_frac_le50=(sz <= SMALL).mean() if len(sz) else np.nan)
        summ.append(row)
S = pd.DataFrame(summ)


def choose(mrr: dict) -> tuple[str, list]:
    best = max(mrr, key=mrr.get)
    tied = [r for r in mrr if mrr[best] - mrr[r] < TIE]
    for r in TIE_ORDER:
        if r in tied:
            return r, tied
    return best, tied


choice = {}
for name in PG:
    s = S[(S.analysis == name) & S.ranker.isin(RANKERS)].set_index("ranker").MRR.to_dict()
    choice[name] = choose(s)
S["chosen_by_frozen_rule"] = [r == choice[a][0] for a, r in zip(S.analysis, S.ranker)]
S.to_csv(OUT / "loo_ranker_choice.tsv", sep="\t", index=False, float_format="%.6f")
chosen, tied = choice["primary (flagged excluded; unscannable included)"]

# paired differences (primary, descriptive)
pairs = []
for a, b in (("R1", "R2"), ("R1", "R3"), ("R2", "R3"), ("R1", "prior"), ("R2", "prior"), ("R3", "prior")):
    for lab, cl in BOOTS:
        d = mt.paired_cluster_bootstrap(P[f"rr_{a}"], P[f"rr_{b}"], cl, n_boot=NBOOT, seed=SEED)
        d1 = mt.paired_cluster_bootstrap(P[f"hit1_{a}"], P[f"hit1_{b}"], cl, n_boot=NBOOT, seed=SEED)
        pairs.append(dict(pair=f"{a} - {b}", boot=lab, dMRR=d["estimate"], dMRR_ci=d["ci_percentile"],
                          dP1=d1["estimate"], dP1_ci=d1["ci_percentile"]))
PD = pd.DataFrame(pairs)

# per-gene output
out = P.copy()
out.insert(1, "hgnc_id", gt.hgnc_id.values[out.pos.values])
out.insert(2, "symbol", gt.symbol.values[out.pos.values])
for r in [*RANKERS, "prior"]:
    out[f"top1_{r}"] = [terms[c] if c >= 0 else "" for c in out[f"top1_{r}"]]
out["cluster_ng_pmid"] = cl_both
out.to_csv(OUT / "loo_per_gene.tsv.gz", sep="\t", index=False, float_format="%.5f")

# ------------------------------------------------------------------------------------------------ report
man = C.write_manifest(OUT / "loo_ranker_choice_manifest.json", "scripts/30_loo_ranker_choice.py", gate,
                       M5.INPUTS, seed=SEED, t0=t0,
                       extra=dict(v2_stats=v2.stats, n_boot=NBOOT, chosen=chosen, tied=tied, clusters=cs,
                                  runtime_scoring_s=round(t_score, 1), runtime_circularity_s=round(t_circ, 1),
                                  n_pmids=len(pmids), n_pmids_flagged=len(hits), validation_disagreements=disagree))
n_tg_genes = TT.pos.nunique()
n_no_target = len(Q) - n_tg_genes
fmt = lambda x: f"{x:.4f}"  # noqa: E731
prim = S[S.analysis.str.startswith("primary")].set_index("ranker")
L = ["# LOO ranker choice (DESIGN §3.1, §3.2.1) — M5a", "",
     f"Generated by `scripts/30_loo_ranker_choice.py` ({man['created']}; runtime {man['runtime_s']} s; scoring "
     f"{t_score:.0f} s; circularity {t_circ:.0f} s). Gate: tag `{gate['tag']}` @ {gate['tag_commit'][:10]}. "
     f"Bootstrap seed {SEED}, {NBOOT} replicates (descriptive). No H or U gene was scored or opened.", "",
     f"## Decision: **{chosen}**", "",
     f"Frozen rule: highest MRR of the first correct reportable term; rankers within |ΔMRR| < {TIE} of the best are "
     f"tied and the tie goes to {' then '.join(TIE_ORDER)}. Primary MRR: "
     + ", ".join(f"{r} {fmt(prim.loc[r, 'MRR'])}" for r in RANKERS)
     + f". Tied set: {tied}. Chosen ranker: **{chosen}**. The same choice under each sensitivity analysis: "
     + "; ".join(f"{k}: {v[0]}" for k, v in choice.items()) + ".", "",
     "## Primary results (flagged targets excluded; unscannable included)", "",
     f"LOO genes: {len(Q)}; with >= 1 candidate V2 target: {n_tg_genes} ({n_no_target} without); with >= 1 target "
     f"after circularity exclusion: **{len(P)}**. CIs: 95% percentile, {NBOOT} reps, gene bootstrap"
     + (f" and cluster bootstrap ({use_cl_name} components)" if use_cl_name else
        f". No cluster bootstrap: the link graphs form one giant component (N(g)+PMID: "
        f"{cs['N(g)+PMID']['n_clusters']} components, largest {cs['N(g)+PMID']['largest']}; N(g) only: "
        f"{cs['N(g) only']['n_clusters']} components, largest {cs['N(g) only']['largest']} of {len(P)} genes), so a "
        f"cluster bootstrap would resample essentially one unit; gene-level CIs ignore this dependence and are "
        f"descriptive only") + ".", "",
     "| ranker | MRR | MRR 95% CI | precision@1 | p@1 95% CI | coverage (any reportable term) |",
     "|---|---|---|---|---|---|"]
for r in [*RANKERS, "prior"]:
    x = prim.loc[r]
    L.append(f"| {r if r != 'prior' else 'prior-only'} | {fmt(x.MRR)} | {x.MRR_ci_gene} | "
             f"{fmt(x.precision_at_1)} | {x.p1_ci_gene} | {x.coverage:.3f} |")
L += ["", "Paired differences (primary; per-gene RR and hit@1; percentile CI):", "",
      "| pair | bootstrap | ΔMRR | 95% CI | Δprecision@1 | 95% CI |", "|---|---|---|---|---|---|"]
for x in PD.itertuples():
    L.append(f"| {x.pair} | {x.boot} | {x.dMRR:+.4f} | {x.dMRR_ci[0]:+.4f} to {x.dMRR_ci[1]:+.4f} | {x.dP1:+.4f} | "
             f"{x.dP1_ci[0]:+.4f} to {x.dP1_ci[1]:+.4f} |")
L += ["", "Top-1 term size (number of annotated scorable genes, query removed) among genes with a top-1 term:", "",
      f"| ranker | p10 | Q1 | median | Q3 | p90 | mean | fraction ≤ {SMALL} |", "|---|---|---|---|---|---|---|---|"]
for r in [*RANKERS, "prior"]:
    x = prim.loc[r]
    L.append(f"| {r if r != 'prior' else 'prior-only'} | {x.top1_size_p10:.0f} | {x.top1_size_q1:.0f} | "
             f"{x.top1_size_median:.0f} | {x.top1_size_q3:.0f} | {x.top1_size_p90:.0f} | {x.top1_size_mean:.1f} | "
             f"{x.top1_frac_le50:.3f} |")
L += ["", "## Sensitivity analyses", "", "| analysis | n genes | R1 MRR | R2 MRR | R3 MRR | prior MRR | R1 p@1 | "
      "R2 p@1 | R3 p@1 | prior p@1 | frozen-rule choice |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for name in PG:
    x = S[S.analysis == name].set_index("ranker")
    L.append(f"| {name} | {int(x.n_genes.iloc[0])} | " + " | ".join(fmt(x.loc[r, 'MRR']) for r in [*RANKERS, 'prior'])
             + " | " + " | ".join(fmt(x.loc[r, 'precision_at_1']) for r in [*RANKERS, 'prior'])
             + f" | {choice[name][0]} |")
ns = TT.state.value_counts()
L += ["", "## Circularity (§3.2.3 applied to LOO targets)", "",
      f"- Supporting PMIDs queried: {len(pmids):,} (found in Europe PMC {int(F.found_in_europepmc.sum()):,}; full "
      f"text searchable {int(F.full_text_searchable.sum()):,}); **flagged {len(hits):,}** "
      f"({len(hits) / max(len(pmids), 1):.2%}). Matched terms among flagged: "
      + ", ".join(f"{tm} {int(F.matched_terms.str.contains(tm, regex=False).sum())}" for tm in circ.TERMS) + ".",
      f"- Query = scripts/05 (imported unchanged): `EXT_ID:<pmid> AND SRC:MED AND {circ.TERM_CLAUSE}`, batched "
      f"{circ.BATCH} PMIDs/request; per-PMID validation on {len(val)} PMIDs (systematic sample, up to 40 flagged, "
      f"Wainberg 2021): disagreements {len(disagree)} {disagree[:10]}.",
      f"- (gene, target) pairs: {len(TT):,} over {n_tg_genes:,} genes; **flagged {int(ns.get('flagged', 0)):,}** "
      f"({ns.get('flagged', 0) / len(TT):.2%}; fully circular {int(TT.fully_circular.sum()):,}); **unscannable "
      f"{int(ns.get('unscannable', 0)):,}** (included in the primary); clean {int(ns.get('clean', 0)):,}; targets "
      f"whose PMIDs are all abstract-only {int(TT.abstract_only.sum()):,}.",
      f"- Genes with >= 1 flagged target: {TT[TT.flagged].pos.nunique():,}; genes losing every target (leave the "
      f"primary benchmark): {n_tg_genes - len(P):,}.", "",
      "## Vocabulary and scoring details", "",
      f"- V2 current: GAF rows {v2.stats['gaf_rows']:,}; NOT removed {v2.stats['not_rows_removed']:,}; "
      f"colocalizes_with removed {v2.stats['colocalizes_with_rows_removed']:,}; BP/MF with D1 evidence "
      f"{v2.stats['rows_bpmf_d1_evidence']:,}; replaced_by {v2.stats['rows_replaced_by']}, obsolete dropped "
      f"{v2.stats['rows_obsolete_dropped']}; unmapped accession {v2.stats['rows_unmapped_accession']:,}; mapped to "
      f"non-scorable/non-DepMap genes {v2.stats['rows_mapped_not_scorable']:,}; kept {v2.stats['rows_kept']:,} rows "
      f"on {v2.stats['genes_with_rows']:,} genes. Annotated background B (>= 1 non-generic BP/MF term): "
      f"{v2.stats['n_annotated_background']:,}. Base candidate terms (5–200): {v2.stats['n_candidate_terms_base']:,}; "
      f"matrix columns (5–{HI + v2.stats['size_slack']}, per-query window applied after removals): "
      f"{v2.stats['n_columns']:,}.",
      f"- IPI rows {v2.stats['ipi_rows']:,} ({v2.stats['ipi_rows_with_mapped_partner']:,} with a with/from "
      f"UniProtKB partner mapped to a scorable gene). LOO queries with >= 1 other gene losing a candidate-term "
      f"membership under the IPI rule: {int((sc.info.n_ipi_genes > 0).sum())} (max genes affected "
      f"{int(sc.info.n_ipi_genes.max())}; genes leaving B: {int(sc.info.n_lost_bg.sum())}).",
      f"- Per query: candidate terms median {int(sc.info.n_candidates.median())}; reportable terms median "
      f"{int(sc.info.n_reportable.median())}; queries with no reportable term {int((sc.info.n_reportable == 0).sum())}.",
      f"- Sparse-correction scoring verified against explicit re-propagation (predictor.term_scores / hypergeom_p / "
      f"empirical_p on the per-query membership) on {len(chk)} LOO queries (S, p_hyper, p_emp, all three ranks "
      f"identical); toy tests in tests/test_vocab.py.",
      "- Matched lists: per-term exclusion of A_t (matched genes annotated to t after the query's removals); "
      "p_emp floor 1/501; ties by S then GO id.",
      "- Interpretation choices (not specified verbatim in DESIGN): flagged target = any supporting PMID flagged "
      "(the scripts/05 conservative definition); flagged (gene, term) pairs are removed from both T(g) and the "
      "ranked lists in the primary (other variants as sensitivities); unscannable = no supporting PMID found in "
      "Europe PMC; annotated background = >= 1 non-generic BP/MF term (scripts/04 convention); the candidate window "
      "is evaluated after the query's own annotations and IPI-rule rows are removed.", ""]
(OUT / "loo_ranker_choice.md").write_text("\n".join(L))
C.log(f"chosen ranker {chosen}; wrote {OUT / 'loo_ranker_choice.md'}")
print(S[S.analysis.str.startswith("primary")][["ranker", "MRR", "MRR_ci_gene", "precision_at_1", "p1_ci_gene",
                                                 "coverage"]].to_string())
