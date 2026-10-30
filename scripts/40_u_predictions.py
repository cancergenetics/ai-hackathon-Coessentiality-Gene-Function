#!/usr/bin/env python
"""40_u_predictions.py -- M6 step 1: TF list and the machine-generated prediction ledger for every scorable U gene
(DESIGN.md v2.3 §4.1, §3.0-§3.1; DEVIATIONS.md 2026-10-30 TF-list row and 2026-10-29 M6 rows).

1. config/tf_list.tsv -- genes annotated (any evidence incl. IEA; non-NOT rows of the current GAF) to GO:0003700
   'DNA-binding transcription factor activity' or a descendant (current obo). Written before any U prediction.
2. Predictor §3.1 with CURRENT annotations, exactly the H code path of M5b: full-data zavg_BEF N(g) (K = 25; self, non-BG,
   same arm and Ensembl paralogues excluded), V2 current (D1 evidence, IPI with/from rule), per-query 5-200 window,
   ``vocab.score_queries(loo=False)``, ranker R1 (LOOKS.md), reportable = >= 2 supporting partners.
   Per gene: top reportable V2 term (S, n_sup, x, per-query size, hypergeometric p descriptive), module family
   (config/term_families.tsv), most specific term among the top 5 (descriptive), V1 and V1' labels (top reportable R1
   term, window 5-200), the §3.7 covariates (top-K mean zavg, R(g), coverage and its current-release percentile, top-term
   size percentile), strata, hu.MAP-train membership.
3. Top-10 partners per gene: zavg_BEF and z_B / z_E / z_F from the tool's pair scorer (``CoessentialityModel.zavg``,
   published Config, refitted on the full data; checked against the stored zavg_BEF), supporting-partner status,
   partner annotations (number of V2 candidate terms, 3 most specific), essentiality (mean effect, fraction of lines
   < -0.5), chromosome / location / distance to g, paralogue flags, in-degree and top-1% hub flag, hu.MAP-train.
No narrative. Outputs: config/tf_list.tsv; results/ledger/u_predictions.tsv, u_partners.tsv, u_top5.tsv,
40_manifest.json; data/derived/ledger/u_scores.pkl (score tables for scripts 41-44).
Run: .env/bin/python -I scripts/40_u_predictions.py
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

import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import coess_matrix as cm  # noqa: E402
from src import knownness as kn  # noqa: E402
from src import ledger as LG  # noqa: E402
from src import predictor as pr  # noqa: E402
from src import vocab  # noqa: E402

log = C.log
K = B.K
NP = C.fz("predictions", "ledger_partners_per_gene")
HUBF = C.fz("artefacts", "hub_in_degree_top_fraction")
TF_ROOT = "GO:0003700"

base = B.Base()
gt, G, onto = base.gt, base.G, base.onto
hgnc = kn.load_hgnc_pc(str(C.ROOT / M5.HGNC))
sym_of = dict(zip(hgnc.hgnc_id, hgnc.symbol))

# ============================================================================================ 1. TF list
t = time.perf_counter()
gaf = kn.read_gaf(str(C.ROOT / M5.GAF_CUR))
gaf = gaf[~kn.is_not_qualified(gaf.qualifier) & (gaf.aspect == "F")]
res = {x: onto.resolve(x)[0] for x in gaf.go_id.unique()}
tf_terms = {x for x, r in res.items() if r and TF_ROOT in onto.ancestors(r)}
tfr = gaf[gaf.go_id.isin(tf_terms)].copy()
tfr["hgnc_id"] = tfr.acc.map(lambda a: sorted(base.acc_map.get(kn.strip_isoform(a), ())))
tfr = tfr.explode("hgnc_id").dropna(subset=["hgnc_id"])
tfr = tfr[tfr.hgnc_id.isin(sym_of)]
TF = tfr.groupby("hgnc_id").agg(n_rows=("go_id", "size"),
                                evidence=("evidence", lambda s: "|".join(sorted(set(s))))).reset_index()
TF["symbol"] = TF.hgnc_id.map(sym_of)
TF = TF[["hgnc_id", "symbol", "n_rows", "evidence"]].sort_values("symbol")
hdr = (f"# config/tf_list.tsv -- DESIGN §4.3 TF list (DEVIATIONS 2026-10-30): protein-coding genes annotated (any "
       f"evidence incl. IEA; non-NOT rows) to {TF_ROOT} 'DNA-binding transcription factor activity' or a descendant "
       f"in the current goa_human GAF (current go-basic.obo). Written by scripts/40_u_predictions.py before any U "
       f"prediction was computed. Lineage markers: not used. n = {len(TF)}.\n")
(C.ROOT / "config" / "tf_list.tsv").write_text(hdr + TF.to_csv(sep="\t", index=False))
log(f"TF list: {len(TF)} genes ({time.perf_counter() - t:.0f} s)")
del gaf, tfr

# ============================================================================================ 2. scoring
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
v1 = B.build_v1(base, M5.GAF_CUR, label="current")
v1p, v1p_names = B.build_v1prime(base, v1, B.LO, B.HI)
U = pd.read_csv(C.ROOT / M6.U_TSV, sep="\t", dtype=str, keep_default_na=False)
AS = pd.read_csv(C.ROOT / M6.ASSESS, sep="\t", dtype={"hgnc_id": str})
Upos = np.array(sorted(base.pos[h] for h in U[U.scorable == "True"].hgnc_id if h in base.pos), dtype=np.int64)
assert base.scor[Upos].all()
log(f"scorable U genes: {len(Upos)}")

t = time.perf_counter()
sc2 = vocab.score_queries(v2, base.nb, base.matches, Upos, loo=False, log=log)
sc1 = vocab.score_queries(v1, base.nb, base.matches, Upos, loo=False)
scp = vocab.score_queries(v1p, base.nb, base.matches, Upos, loo=False)
log(f"scored U on V2/V1/V1' in {time.perf_counter() - t:.0f} s")
r2, r1v, rpv = sc2.ranked("R1"), sc1.ranked("R1"), scp.ranked("R1")
qi = {int(g): i for i, g in enumerate(sc2.queries)}
tab = sc2.table.set_index(["query", "term"])
tabp = scp.table.set_index(["query", "term"])

core = pd.read_pickle(C.DERIVED / "holdout_eval" / "core.pkl")
cov_cur = B.coverage(base, v2)
assert np.allclose(cov_cur, core["cov_cur"], equal_nan=True), "coverage differs from the M5b current coverage"
cov_pct = B.pct_rank(cov_cur, cov_cur[base.scor])
ref_size = core["ref_size_cur"][base.scor]
ref_log = np.log(ref_size[np.isfinite(ref_size)])
fams = B.load_families()

tp = set(pd.read_csv(C.ROOT / "data/raw/humap_train/Train_positive_pairs.txt", sep="\t", header=None,
                     dtype=str).stack().unique())
humap_train = {base.pos[h] for a in tp for h in base.acc_map.get(a, ()) if h in base.pos}
tp_pairs = pd.read_csv(C.ROOT / "data/raw/humap_train/Train_positive_pairs.txt", sep="\t", header=None, dtype=str)
humap_pairs = set()
for a, b in zip(tp_pairs[0], tp_pairs[1]):
    for x in base.acc_map.get(a, ()):
        for y in base.acc_map.get(b, ()):
            if x in base.pos and y in base.pos:
                humap_pairs.add((base.pos[x], base.pos[y]))
                humap_pairs.add((base.pos[y], base.pos[x]))


def term_label(v, c, names=None):
    t_ = v.terms[c]
    if names is not None and t_.startswith("MC:"):
        return t_, names.get(t_, "")
    return t_, (names.get(t_, "") if names is not None else onto.name(t_)) or onto.name(t_)


AS = AS.set_index("hgnc_id")
rows, top5 = [], []
for g in Upos:
    g = int(g)
    i = qi[g]
    h = gt.hgnc_id.values[g]
    a = AS.loc[h]
    lst = r2.get(g, [])
    r = dict(hgnc_id=h, symbol=gt.symbol.values[g], matrix_index=g, bg=bool(base.bg[g]),
             expressed=bool(a.expressed), expressed_design=bool(a.expressed_design),
             lineage_restricted=bool(a.lineage_restricted), clean_negative=bool(a.clean_negative),
             assessable_p=float(a.p), assessable_design=bool(a.assessable_design),
             low_coverage=bool(a.low_coverage), sd_tertile_withinU=a.sd_tertile_withinU,
             headline_design=bool(a.headline_design), family_stratum=a.family_stratum, core=a.core,
             n_reportable=len(lst), has_prediction=bool(lst))
    if lst:
        c = lst[0]
        x = tab.loc[(g, c)]
        tid = v2.terms[c]
        size = int(sc2.sizes[i, c])
        t5 = [v2.terms[cc] for cc in lst[:5]]
        ms = pr.most_specific(t5, onto.ancestors)[0]
        r.update(top_term=tid, top_term_name=onto.name(tid), top_S=float(x.S), top_n_sup=int(x.n_sup),
                 top_x=int(x.x), top_size=size, top_p_hyper=float(x.p_hyper),
                 family=B.family_of(tid, onto, fams), most_specific_top5=ms,
                 most_specific_top5_name=onto.name(ms), top5="|".join(t5))
        for k, cc in enumerate(lst[:5]):
            xx = tab.loc[(g, cc)]
            top5.append(dict(hgnc_id=h, symbol=r["symbol"], rank=k + 1, term=v2.terms[cc],
                             term_name=onto.name(v2.terms[cc]), S=float(xx.S), n_sup=int(xx.n_sup),
                             size=int(sc2.sizes[i, cc]), p_hyper=float(xx.p_hyper),
                             family=B.family_of(v2.terms[cc], onto, fams)))
    else:
        r.update(top_term="", top_term_name="", top_S=np.nan, top_n_sup=0, top_x=0, top_size=np.nan,
                 top_p_hyper=np.nan, family="", most_specific_top5="", most_specific_top5_name="", top5="")
    l1 = r1v.get(g, [])
    r["v1_label"], r["v1_label_name"] = term_label(v1, l1[0]) if l1 else ("", "")
    lp = rpv.get(g, [])
    if lp:
        tid, nm = term_label(v1p, lp[0], v1p_names)
        r["v1p_label"], r["v1p_label_name"] = tid, nm
        r["v1p_label_n_sup"] = int(tabp.loc[(g, lp[0])].n_sup)
    else:
        r["v1p_label"], r["v1p_label_name"], r["v1p_label_n_sup"] = "", "", 0
    r.update(zmean=float(base.zmean[g]), R=float(base.R[g]), coverage=float(cov_cur[g]), cov_pct=float(cov_pct[g]),
             size_pct=float(B.pct_rank(np.log([r["top_size"]]), ref_log)[0]) if lst else np.nan,
             humap_train=g in humap_train, n_paralogues=len(base.par.get(g, ())),
             location=gt.location.values[g] if "location" in gt.columns else "")
    rows.append(r)
P = pd.DataFrame(rows)
loc = C.gene_index(gt.gene.values).set_index("matrix_index")
P["location"] = loc.location.reindex(P.matrix_index).values
P["arm"] = base.cov.arm.values[P.matrix_index.values]
log(f"U with a top reportable term: {int(P.has_prediction.sum())} / {len(P)}")

# ============================================================================================ 3. partners
t = time.perf_counter()
effect = C.load_effect()
assert list(effect.columns) == list(gt.gene.values)
fm = cm.fit_model(effect, cm.PUBLISHED_CONFIG)
assert not fm.dropped_genes and list(fm.genes) == list(gt.gene.values)
log(f"tool refitted (published Config) in {time.perf_counter() - t:.0f} s")
E = effect.values
frac_dep = np.nanmean(E < -0.5, axis=0)
mean_eff = np.nanmean(E, axis=0)
indeg = LG.in_degree(base.nb.ids, base.scor, G)
hub = LG.hub_genes(indeg, base.bg, HUBF)
hub_thr = int(indeg[hub].min())
ens = C.load_hub().set_index("hgnc_id").ensembl_gene_id
co = pd.read_csv(C.ROOT / "data/raw/ensembl/ensembl116_gene_coordinates.tsv", sep="\t", dtype=str)
co.columns = ["ensg", "name", "entrez", "chrom", "start", "end"]
co = co[co.chrom.isin([str(i) for i in range(1, 23)] + ["X", "Y", "MT"])].drop_duplicates("ensg").set_index("ensg")
coord = {}
for p_, h in enumerate(gt.hgnc_id.values):
    e = ens.get(h)
    if isinstance(e, str) and e in co.index:
        coord[p_] = (co.at[e, "chrom"], float(co.at[e, "start"]), float(co.at[e, "end"]))
cand_mask = v2.candidates(v2.size)
ann_cols = {}


def partner_ann(j):
    if j not in ann_cols:
        c = v2.A.indices[v2.A.indptr[j]:v2.A.indptr[j + 1]]
        c = c[cand_mask[c]]
        o = c[np.argsort(v2.size[c], kind="stable")][:3]
        ann_cols[j] = (len(c), "|".join(f"{v2.terms[x]} {onto.name(v2.terms[x])}" for x in o))
    return ann_cols[j]


prow, ia, ib = [], [], []
for g in Upos:
    g = int(g)
    ids, zz = base.ids100[g, :K], base.z100[g, :K]
    has = bool(r2.get(g))
    sup = {}
    if has:
        c = r2[g][0]
        sup = dict(M6.supporting(v2, g, c, ids, zz))
        S_chk = sum(sup.values())
        assert abs(S_chk - float(tab.loc[(g, c)].S)) < 1e-4, (g, S_chk)
    nbset = set(int(x) for x in ids if x >= 0)
    for k in range(NP):
        j = int(ids[k])
        if j < 0:
            continue
        n_ann, top_ann = partner_ann(j)
        d = LG.interval_gap(coord.get(g), coord.get(j))
        prow.append(dict(hgnc_id=gt.hgnc_id.values[g], symbol=gt.symbol.values[g], rank=k + 1,
                         partner_hgnc_id=gt.hgnc_id.values[j], partner_symbol=gt.symbol.values[j],
                         zavg_BEF_stored=float(zz[k]), supporting_top_term=j in sup,
                         partner_n_v2_candidate_terms=n_ann, partner_top_annotations=top_ann,
                         partner_in_U=False, partner_mean_effect=float(mean_eff[j]),
                         partner_frac_lines_lt_m0p5=float(frac_dep[j]),
                         partner_location=loc.location.get(j, ""), partner_arm=base.cov.arm.values[j],
                         partner_chrom=coord[j][0] if j in coord else "",
                         same_chromosome=bool(j in coord and g in coord and coord[j][0] == coord[g][0]),
                         distance_bp=d if np.isfinite(d) else np.nan,
                         paralogue_of_g=bool(j in set(base.par.get(g, np.array([], int)).tolist())),
                         paralogue_of_other_partner=bool(set(base.par.get(j, np.array([], int)).tolist())
                                                         & (nbset - {j})),
                         partner_in_degree=int(indeg[j]), partner_hub=bool(hub[j]),
                         partner_humap_train=j in humap_train, pair_humap_train=(g, j) in humap_pairs))
        ia.append(g)
        ib.append(j)
t = time.perf_counter()
zavg, Z = fm.model.zavg(np.asarray(ia), np.asarray(ib))
log(f"pair scorer: {len(ia)} pairs in {time.perf_counter() - t:.0f} s")
PT = pd.DataFrame(prow)
PT["zavg_BEF"], PT["z_B"], PT["z_E"], PT["z_F"] = zavg, Z["B"], Z["E"], Z["F"]
dmax = float(np.nanmax(np.abs(PT.zavg_BEF - PT.zavg_BEF_stored)))
assert dmax < 1e-3, f"pair scorer vs stored zavg_BEF: max abs diff {dmax}"
Uset = set(U.hgnc_id)
PT["partner_in_U"] = PT.partner_hgnc_id.isin(Uset)
PT = PT[["hgnc_id", "symbol", "rank", "partner_hgnc_id", "partner_symbol", "zavg_BEF", "z_B", "z_E", "z_F",
         "zavg_BEF_stored", "supporting_top_term", "partner_n_v2_candidate_terms", "partner_top_annotations",
         "partner_in_U", "partner_mean_effect", "partner_frac_lines_lt_m0p5", "partner_location", "partner_arm",
         "partner_chrom", "same_chromosome", "distance_bp", "paralogue_of_g", "paralogue_of_other_partner",
         "partner_in_degree", "partner_hub", "partner_humap_train", "pair_humap_train"]]
assert not PT.paralogue_of_g.any()
P["mean_effect"], P["frac_lines_lt_m0p5"] = mean_eff[P.matrix_index], frac_dep[P.matrix_index]
P["in_degree"], P["hub"] = indeg[P.matrix_index], hub[P.matrix_index]

# ============================================================================================ write
P.to_csv(M6.OUT / "u_predictions.tsv", sep="\t", index=False, float_format="%.6g")
PT.to_csv(M6.OUT / "u_partners.tsv", sep="\t", index=False, float_format="%.6g")
pd.DataFrame(top5).to_csv(M6.OUT / "u_top5.tsv", sep="\t", index=False, float_format="%.6g")
pd.to_pickle(dict(table2=sc2.table, sizes2=sc2.sizes, queries=sc2.queries, ranked2=r2, info2=sc2.info,
                  indeg=indeg, hub=hub, hub_threshold=hub_thr, coord=coord, humap_train=humap_train),
             M6.DER / "u_scores.pkl")
man = C.write_manifest(M6.OUT / "40_manifest.json", "scripts/40_u_predictions.py", gate,
                       [*M5.INPUTS, M6.U_TSV, M6.ASSESS, "results/assessability/R_all.tsv",
                        "data/raw/ensembl/ensembl116_gene_coordinates.tsv",
                        "data/raw/humap_train/Train_positive_pairs.txt", "config/tf_list.tsv"],
                       seed=0, t0=T_START,
                       extra=dict(n_U_scorable=len(Upos), n_with_prediction=int(P.has_prediction.sum()),
                                  n_tf=len(TF), pair_scorer_max_abs_diff=dmax, hub_in_degree_threshold=hub_thr,
                                  n_hub_genes=int(hub.sum()), v2_stats=v2.stats, v1_columns=int(v1.T),
                                  v1p_columns=int(v1p.T)))
log(f"done in {time.perf_counter() - T_START:.0f} s")
