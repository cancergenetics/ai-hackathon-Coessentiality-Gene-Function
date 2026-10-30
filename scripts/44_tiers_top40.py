#!/usr/bin/env python
"""44_tiers_top40.py -- M6 step 5: tiers (DESIGN.md v2.3 §6.1), the top-40 fill, the top-40-only §4.3 checks and the
§4.4 relationship type (operational details: DEVIATIONS.md 2026-10-29 M6 rows).

Tier A = scorable, expressed (DESIGN incl. lineage-restricted), assessable, in-support p_cal >= 0.5, no §4.3 exclusion
(scripts/42), diagnostic-class support when one is measured, no contradiction (scripts/43), no top-40 demotion
(lineage leave-out failure, DEMETER2 or TP53 flag -> Tier B at best). low_coverage genes are not excluded (H contains
non-background genes). Tier B = Tier A conditions except p_cal >= 0.5 (needs >= 0.3) and/or diagnostic support.
Top 40 = Tier A -> Tier B -> p_cal fill (pool: expressed, assessable, in-support p_cal; clean fill first), ties by number
of supporting classes then symbol; <= 6 mitochondrial-family calls in the top 20.
Iteration: rank -> support for entrants lacking it (scripts/m6_common.support_for, with matched and decoy rows) ->
top-40 checks for entrants lacking them -> re-rank, until the top 40 is stable (logged).
Top-40 checks: lineage leave-out (the tool refitted without g's most dependent lineage; same top reportable term?),
dependency-expression coupling (|Spearman rho| > 0.3), TF enrichment of N(g) (Fisher OR > 3, BH q < 0.05), TP53-status
Mann-Whitney (BH q < 0.05), DEMETER2 replication (mean supporting-partner r >= 95th percentile of random sets), GLS rank
(descriptive). Relationship type by script: e -> a -> c -> b -> d (unresolved).
Outputs: results/ledger/top40.tsv, top40_checks.tsv, top40_fill_log.tsv, top40_partners_gls.tsv, tiers_all.tsv,
support.tsv / support_sources.tsv (entrant rows appended), 44_manifest.json; data/derived/ledger/checks_cache.pkl,
lineage_*.npz, gls_top40.npy.
Run: .env/bin/python -I scripts/44_tiers_top40.py   (after scripts/43)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
DATA = (C.EFFECT_CSV, "data/raw/depmap/Model.csv", "data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
        "data/raw/depmap/OmicsSomaticMutationsMatrixDamaging.csv", "data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv",
        "data/raw/depmap_rnai/D2_combined_gene_dep_scores.csv")
gate = C.gate_check(data_files=DATA)
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import mannwhitneyu, spearmanr  # noqa: E402

import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import coess_matrix as cm  # noqa: E402
from src import ledger as LG  # noqa: E402
from src import neighbours as nbm  # noqa: E402
from src import vocab  # noqa: E402
from src.neighbours import Neighbours  # noqa: E402

log = C.log
K = B.K
NTOP = C.fz("tiers", "top_n")
RHO = C.fz("artefacts", "expression_coupling_abs_spearman")
TF_OR, TF_Q = C.fz("artefacts", "tf_enrichment_fisher_or_min"), C.fz("artefacts", "tf_enrichment_q_max")
TP53_Q = C.fz("artefacts", "tp53_mannwhitney_q")
D2_PCT = C.fz("artefacts", "demeter2_percentile")
NB_D2 = 1000
MIN_LINES = 20
PRECOMPUTE = None       # None = every pool gene (one refit per lineage; results are per gene, grouping-invariant)

base = B.Base()
gt, G = base.gt, base.G
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
P = M6.read_tsv("u_predictions.tsv")
PC = M6.read_tsv("u_pcal.tsv")
FL = M6.read_tsv("u_flags.tsv")
ST = M6.read_tsv("support.tsv")
SS = M6.read_tsv("support_sources.tsv")
D = pd.read_pickle(M6.DER / "u_scores.pkl")
ranked = D["ranked2"]
Pi = P.set_index("hgnc_id")
effect = C.load_effect()
E = effect.values
lines = np.asarray(effect.index)
MODEL = M6.model_line_lineage()
lin_of = MODEL.OncotreeLineage.reindex(lines).fillna("unknown").values
TF = pd.read_csv(C.ROOT / "config/tf_list.tsv", sep="\t", comment="#", dtype=str)
tf_pos = {base.pos[h] for h in TF.hgnc_id if h in base.pos}
CK_FILE = M6.DER / "checks_cache.pkl"
CK = pd.read_pickle(CK_FILE) if CK_FILE.exists() else {}

# ------------------------------------------------------------------------------------------ omics for checks
def header(path):
    return pd.read_csv(C.ROOT / path, nrows=0).columns


def gene_cols(path, positions):
    """Default-entry omics values (ModelID x requested matrix positions; matched on Entrez)."""
    h = header(path)
    ent = M6.entrez_of_col(h)
    want = {}
    eg = M6.entrez_of_col(gt.gene.values[list(positions)])
    for p_, e in zip(positions, eg):
        k = [c for c, x in zip(h, ent) if x == e]
        if k:
            want[p_] = k[0]
    meta = [c for c in ("ModelID", "IsDefaultEntryForModel") if c in h]
    df = pd.read_csv(C.ROOT / path, usecols=meta + sorted(set(want.values())))
    if "IsDefaultEntryForModel" in df.columns:
        df = df[df.IsDefaultEntryForModel.astype(str).isin(["Yes", "True", "true", "1"])]
    df = df.drop_duplicates("ModelID").set_index("ModelID")
    return pd.DataFrame({p_: df[c] for p_, c in want.items()}, index=df.index)


tp53_pos = base.pos[gt.hgnc_id.values[np.flatnonzero(gt.symbol.values == "TP53")[0]]]
mut = []
for f in ("data/raw/depmap/OmicsSomaticMutationsMatrixDamaging.csv",
          "data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv"):
    mut.append(gene_cols(f, [tp53_pos])[tp53_pos])
mm = pd.concat(mut, axis=1)
tp53_mut = (mm.fillna(0) > 0).any(axis=1)
tp53_status = pd.Series(lines).map(tp53_mut).values          # True / False / NaN (no mutation data)
log(f"TP53: {np.nansum(tp53_status == True)} mutant / {np.nansum(tp53_status == False)} WT lines with data")

from src import orthogonal as og  # noqa: E402
d2s = og.load_demeter2()
ccle2model = {c: m for m, c in zip(MODEL.index, MODEL.CCLEName) if isinstance(c, str)}
d2 = d2s.profile.copy()
d2.columns = [ccle2model.get(c) for c in d2.columns]
d2 = d2.loc[:, [c is not None and c in set(lines) for c in d2.columns]]
d2 = d2.loc[:, ~pd.Index(d2.columns).duplicated()]
d2_pos = np.array([base.pos.get(h, -1) for h in d2.index])
D2M = d2.values.astype(float)
d2_row = {int(p_): i for i, p_ in enumerate(d2_pos) if p_ >= 0}
log(f"DEMETER2: {D2M.shape[0]} genes x {D2M.shape[1]} shared tool lines")


# ------------------------------------------------------------------------------------------ checks
def most_dependent_lineage(g):
    s = pd.DataFrame(dict(lin=lin_of, e=E[:, g])).dropna()
    cnt = s.groupby("lin").e.agg(["mean", "size"])
    cnt = cnt[(cnt["size"] >= 10) & (cnt.index != "unknown")]
    return cnt["mean"].idxmin(), float(cnt["mean"].min()), int(cnt.loc[cnt["mean"].idxmin(), "size"])


def lineage_leaveout(genes):
    """{g: dict(lineage, retained, new_top)} -- refit the tool without each lineage (grouped)."""
    out = {}
    groups = {}
    for g in genes:
        lin, m_, n_ = most_dependent_lineage(g)
        groups.setdefault(lin, []).append((g, m_, n_))
    for lin, gl in groups.items():
        t = time.perf_counter()
        keep = lines[lin_of != lin]
        fm = cm.fit_model(effect, cm.PUBLISHED_CONFIG, lines=keep)
        pos = pd.Index(gt.gene.values).get_indexer(fm.genes)
        inv = np.full(G, -1)
        inv[pos] = np.arange(len(pos))
        src = cm.ModelBlockSource(fm, "zavg_BEF")
        bg_h = fm.model.bg.copy() & base.bg[pos]
        arm_h = base.arm[pos]
        par_h = {}
        for g_, s in base.par.items():
            if inv[g_] >= 0:
                tt = inv[np.asarray(s, dtype=np.int64)]
                par_h[int(inv[g_])] = tt[tt >= 0]
        gs = [g for g, _, _ in gl]
        rows = inv[gs]
        assert (rows >= 0).all()
        nb = nbm.top_k(src, K, rows=rows, bg=bg_h, arm=arm_h, paralogues=par_h)
        I, Z = base.nb.ids.copy(), base.nb.z.copy()
        I[gs] = np.where(nb.ids >= 0, pos[np.where(nb.ids >= 0, nb.ids, 0)], -1)
        Z[gs] = nb.z
        nb_all = Neighbours(rows=np.arange(G), ids=I, z=Z, K=K)
        sc = vocab.score_queries(v2, nb_all, base.matches, np.asarray(sorted(gs)), loo=False)
        r1 = sc.ranked("R1")
        for g, m_, n_ in gl:
            new = v2.terms[r1[g][0]] if r1.get(g) else ""
            old = v2.terms[ranked[g][0]]
            overlap = len(set(I[g]) & set(base.nb.ids[g])) / K
            out[g] = dict(lineage=lin, lineage_mean_effect=m_, lineage_n_lines=n_, lineage_removed_lines=int(
                (lin_of == lin).sum()), leaveout_top_term=new, leaveout_retained=bool(new == old),
                leaveout_nb_overlap=overlap)
        np.savez_compressed(M6.DER / f"lineage_{lin.replace('/', '_').replace(' ', '_')}.npz", genes=np.asarray(gs),
                            ids=I[gs], z=Z[gs])
        log(f"lineage leave-out {lin}: {len(gs)} genes, refit + rescoring {time.perf_counter() - t:.0f} s")
    return out


EXPR = "data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"


def other_checks(genes):
    out = {}
    ex = gene_cols(EXPR, genes)
    bgset = set(np.flatnonzero(base.bg).tolist())
    for g in genes:
        r = {}
        # coupling
        if g in ex.columns:
            x = pd.Series(E[:, g], index=lines)
            y = ex[g].reindex(lines)
            ok = x.notna() & y.notna()
            if ok.sum() >= MIN_LINES and y[ok].nunique() > 1:
                rho = spearmanr(x[ok], y[ok]).correlation
            else:
                rho = np.nan
            r.update(coupling_rho=float(rho), coupling_n=int(ok.sum()))
        else:
            r.update(coupling_rho=np.nan, coupling_n=0)
        r["coupling_flag"] = bool(np.isfinite(r["coupling_rho"]) and abs(r["coupling_rho"]) > RHO)
        # TF enrichment
        nbg = [int(x) for x in base.nb.ids[g] if x >= 0]
        fe = LG.fisher_enrichment(nbg, tf_pos, bgset - {g})
        r.update(tf_in_N=fe["a"], tf_OR=fe["OR"], tf_p=fe["p"])
        # TP53
        e = E[:, g]
        mu = e[(tp53_status == True) & np.isfinite(e)]
        wt = e[(tp53_status == False) & np.isfinite(e)]
        r.update(tp53_n_mut=len(mu), tp53_n_wt=len(wt),
                 tp53_p=float(mannwhitneyu(mu, wt, alternative="two-sided").pvalue) if min(len(mu), len(wt)) >= 5
                 else np.nan, tp53_median_diff=float(np.median(mu) - np.median(wt)) if min(len(mu), len(wt)) else np.nan)
        # DEMETER2
        sup = [j for j, _ in M6.supporting(v2, g, ranked[g][0], base.ids100[g, :K], base.z100[g, :K])]
        if g in d2_row:
            pj = [j for j in sup if j in d2_row]
            xg = D2M[d2_row[g]]
            if pj:
                rj = LG.pearson_pairwise(xg, D2M[[d2_row[j] for j in pj]].T, min_n=MIN_LINES)
                obs = float(np.nanmean(rj)) if np.isfinite(rj).any() else np.nan
                pool = np.array([d2_row[j] for j in d2_row if base.bg[j] and j != g and j not in set(sup)])
                rall = LG.pearson_pairwise(xg, D2M[pool].T, min_n=MIN_LINES)
                fin = np.isfinite(rall)
                rng = np.random.default_rng([0, g])
                k = int(np.isfinite(rj).sum())
                if np.isfinite(obs) and fin.sum() > k:
                    vals = rall[fin]
                    null = np.array([vals[rng.choice(len(vals), k, replace=False)].mean() for _ in range(NB_D2)])
                    p95 = float(np.percentile(null, D2_PCT))
                    r.update(d2_measured=True, d2_n_partners=k, d2_mean_r=obs, d2_null_p95=p95,
                             d2_replicated=bool(obs >= p95))
                else:
                    r.update(d2_measured=False, d2_n_partners=k, d2_mean_r=obs, d2_null_p95=np.nan,
                             d2_replicated=np.nan)
            else:
                r.update(d2_measured=False, d2_n_partners=0, d2_mean_r=np.nan, d2_null_p95=np.nan, d2_replicated=np.nan)
        else:
            r.update(d2_measured=False, d2_n_partners=0, d2_mean_r=np.nan, d2_null_p95=np.nan, d2_replicated=np.nan)
        r["d2_flag"] = bool(r["d2_measured"] and r["d2_replicated"] is False)
        out[g] = r
    return out


def ensure_checks(genes, lineage=True):
    need = [g for g in genes if g not in CK]
    if not need:
        return
    oc = other_checks(need)
    lo = lineage_leaveout(need) if lineage else {}
    for g in need:
        CK[g] = dict(oc[g], **lo.get(g, {}))
    pd.to_pickle(CK, CK_FILE)


def checks_frame(top_pos):
    """Per gene check table with BH over the current top set; monotone demotion."""
    rows = []
    for g in top_pos:
        rows.append(dict(matrix_index=g, **CK[g]))
    T = pd.DataFrame(rows)
    T["tf_q"] = LG.bh(T.tf_p.values)
    T["tf_flag"] = (T.tf_OR > TF_OR) & (T.tf_q < TF_Q)
    T["tp53_q"] = LG.bh(T.tp53_p.values)
    T["tp53_flag"] = T.tp53_q < TP53_Q
    T["leaveout_fail"] = ~T.leaveout_retained.astype(bool)
    T["demote_now"] = T.leaveout_fail | T.d2_flag.astype(bool) | T.tp53_flag
    return T


# ------------------------------------------------------------------------------------------ iteration
runner = None
cands = M6.decoy_candidates(P, v2)
demoted = {}                      # hgnc_id -> reason (monotone)
fill_log = []
new_support_rows = []


def sup_real():
    r = ST[ST.set == "real"].drop_duplicates("anchor_hgnc_id")
    r = r.rename(columns={"anchor_hgnc_id": "hgnc_id"})
    return r


d0 = M6.pool_table(PC, FL, sup_real())
pre_order = M6.rank_pool(d0, PRECOMPUTE or int(d0.pool.sum()))
ensure_checks([int(Pi.loc[h].matrix_index) for h in pre_order.hgnc_id])
prev = None
for it in range(1, 30):
    chk = pd.DataFrame(dict(hgnc_id=list(demoted), demote_A=True)) if demoted else None
    if chk is not None:
        # genes already checked but not demoted -> demote_A False
        done = [gt.hgnc_id.values[g] for g in CK if gt.hgnc_id.values[g] not in demoted]
        chk = pd.concat([chk, pd.DataFrame(dict(hgnc_id=done, demote_A=False))])
    else:
        chk = pd.DataFrame(dict(hgnc_id=[gt.hgnc_id.values[g] for g in CK], demote_A=False))
    d = M6.pool_table(PC, FL, sup_real(), chk)
    top = M6.rank_pool(d, NTOP)
    hs = top.hgnc_id.tolist()
    need_sup = [h for h in hs if h not in set(ST[ST.set == "real"].anchor_hgnc_id)]
    tpos = [int(Pi.loc[h].matrix_index) for h in hs]
    need_chk = [g for g in tpos if g not in CK]
    T = checks_frame([g for g in tpos if g in CK])
    newly = [gt.hgnc_id.values[int(g)] for g in T[T.demote_now].matrix_index if gt.hgnc_id.values[int(g)] not in demoted]
    for h in newly:
        x = T[T.matrix_index == Pi.loc[h].matrix_index].iloc[0]
        demoted[h] = "|".join(n for n, f in (("lineage_leaveout", x.leaveout_fail), ("DEMETER2", x.d2_flag),
                                             ("TP53", x.tp53_flag)) if f)
    fill_log.append(dict(iteration=it, top40="|".join(top.symbol), entrants=",".join(
        top.symbol[~top.hgnc_id.isin(prev)]) if prev is not None else "", left=",".join(
        Pi.loc[[h for h in prev if h not in set(hs)]].symbol) if prev is not None else "",
        need_support=len(need_sup), need_checks=len(need_chk), newly_demoted=",".join(Pi.loc[newly].symbol)))
    log(f"iteration {it}: need support {len(need_sup)}, checks {len(need_chk)}, newly demoted {len(newly)}")
    if not need_sup and not need_chk and not newly and prev is not None and prev == hs:
        break
    if need_sup:
        if runner is None:
            runner = M6.SupportRunner()
        rows = []
        for h in need_sup:
            r = Pi.loc[h]
            rows += M6.support_for(dict(hgnc_id=h, symbol=r.symbol, pos=int(r.matrix_index), term=r.top_term,
                                        family=r.family), runner, v2, base, cands, base.onto)
        runner.save()
        X = pd.DataFrame(rows)
        X["scope"] = "top40_entrant"
        ST = pd.concat([ST, X], ignore_index=True)
        SS = pd.concat([SS, M6.source_rows(runner, rows)], ignore_index=True)
        new_support_rows += rows
    if need_chk:
        ensure_checks(need_chk)
    prev = hs
else:
    raise RuntimeError("top-40 fill did not converge in 30 iterations")

# ------------------------------------------------------------------------------------------ final top 40
d = M6.pool_table(PC, FL, sup_real(), chk)
d.to_csv(M6.OUT / "tiers_all.tsv", sep="\t", index=False, float_format="%.6g")
top = M6.rank_pool(d, NTOP)
tpos = [int(Pi.loc[h].matrix_index) for h in top.hgnc_id]
T = checks_frame(tpos).set_index("matrix_index")

# GLS rows (descriptive) for the final top 40
t = time.perf_counter()
cols = np.flatnonzero(base.bg)
Xe = effect.to_numpy()
gls, gst = cm.gls_rows(Xe, np.asarray(tpos), cols, out_path=M6.DER / "gls_top40.npy", log=log)
ver = cm.verify_rows_against_baselines(np.asarray(gls), Xe, "gls", np.asarray(tpos), cols,
                                       n_pairs=C.fz("infra", "pair_check_min_pairs") + 1000, seed=0)
assert ver["passed"], ver
log(f"GLS rows for the top 40 in {time.perf_counter() - t:.0f} s; verification {ver}")
rs = M6.read_tsv("u_partners.tsv")
gls_part, gls_top = [], {}
src_rows = B.RowSource(gls, {g: i for i, g in enumerate(tpos)}, cols, G)
nbg = nbm.top_k(src_rows, K, rows=np.asarray(tpos), bg=base.bg, arm=base.arm, paralogues=base.par)
nb_gls = B.padded(G, np.asarray(tpos), nbg.ids, nbg.z, K)
scg = vocab.score_queries(v2, nb_gls, base.matches, np.asarray(sorted(tpos)), loo=False)
r1g = scg.ranked("R1")
for i, g in enumerate(tpos):
    row = np.asarray(gls[i], float).copy()
    full = np.full(G, -np.inf)
    full[cols] = row
    ex = nbm.exclusion_mask(np.array([g]), G, base.bg, base.arm, base.par)[0]
    full[ex | ~np.isfinite(full)] = -np.inf
    lst = r1g.get(g, [])
    zt = ranked[g][0]
    gls_top[g] = dict(gls_top_term=v2.terms[lst[0]] if lst else "",
                      gls_rank_of_zavg_top_term=(lst.index(zt) + 1) if zt in lst else np.nan)
    sub = rs[rs.hgnc_id == gt.hgnc_id.values[g]]
    for x in sub.itertuples():
        j = base.pos[x.partner_hgnc_id]
        v = full[j]
        gls_part.append(dict(hgnc_id=x.hgnc_id, symbol=x.symbol, rank=x.rank, partner_symbol=x.partner_symbol,
                             zavg_BEF=x.zavg_BEF, gls_t=v if np.isfinite(v) else np.nan,
                             gls_rank=int((full > v).sum() + 1) if np.isfinite(v) else np.nan))
GP = pd.DataFrame(gls_part)
GP.to_csv(M6.OUT / "top40_partners_gls.tsv", sep="\t", index=False, float_format="%.6g")

# relationship type
up = pd.read_csv(C.ROOT / M5.UNIPROT, sep="\t", dtype=str, keep_default_na=False)
up["hgnc"] = up.HGNC.str.split(";").map(lambda x: [y for y in x if y])
up = up.explode("hgnc")


def prot_info(h):
    u = up[up.hgnc == h]
    names = " ".join(u["Protein names"])
    kw = ";".join(u.Keywords).lower()
    loc = " ".join(u["Subcellular location [CC]"])
    enz = "(EC " in names
    trans = any(k.strip() in ("transport", "ion transport", "sugar transport", "amino-acid transport",
                              "lipid transport", "protein transport", "mrna transport", "electron transport")
                for k in kw.split(";"))
    return dict(enzyme_EC=enz, transport_keyword=trans, multipass="Multi-pass membrane protein" in loc,
                uniprot=",".join(u.Entry))


SR = sup_real().set_index("hgnc_id")
out = []
for x in top.itertuples():
    g = int(Pi.loc[x.hgnc_id].matrix_index)
    p = Pi.loc[x.hgnc_id]
    c = T.loc[g]
    s = SR.loc[x.hgnc_id] if x.hgnc_id in SR.index else None
    cs = {k: (s[f"state_{k}"] if s is not None else "not assessed") for k in ("P", "A", "L", "G", "S")}
    pi = prot_info(x.hgnc_id)
    v1p_complex = isinstance(p.v1p_label, str) and (p.v1p_label.startswith("CP:") or p.v1p_label.startswith("GO:"))
    complex_like = bool(v1p_complex and p.v1p_label_n_sup >= 3)
    assembly = "assembly" in f"{p.top_term_name} {p.v1p_label_name}".lower()
    ty, why = LG.relationship_type(bool(c.coupling_flag), bool(c.tf_flag), cs, pi["enzyme_EC"] or pi["transport_keyword"],
                                   pi["multipass"], complex_like, assembly)
    fl = FL.set_index("hgnc_id").loc[x.hgnc_id]
    flags = [n for n, f in (("excl43", fl.excl43), ("hub_driven", fl.hub_driven), ("locus", fl.n_locus > 0),
                            ("CN", fl.n_cn > 0), ("contradiction", x.contradiction),
                            ("lineage_leaveout_fail", c.leaveout_fail), ("DEMETER2", c.d2_flag), ("TP53", c.tp53_flag),
                            ("coupling", c.coupling_flag), ("TF", c.tf_flag), ("low_coverage", x.low_coverage),
                            ("mito_deferred", x.mito_deferred)) if bool(f)]
    out.append(dict(
        rank=x.rank, symbol=x.symbol, hgnc_id=x.hgnc_id, v2_term=p.top_term, v2_term_name=p.top_term_name,
        v1p_label=p.v1p_label, v1p_label_name=p.v1p_label_name, family=p.family, p_cal=x.p_cal,
        tier=x.tier if x.tier else "", fill_group={0: "Tier A", 1: "Tier B", 2: "p_cal fill (clean)",
                                                  3: "p_cal fill (flagged)"}[int(x.group)],
        cond_scorable=True, cond_expressed=bool(x.expressed), cond_assessable=bool(x.assessable),
        cond_in_support=bool(x.in_support), cond_pcal_ge_0p5=bool(x.p_cal >= 0.5), cond_pcal_ge_0p3=bool(x.p_cal >= 0.3),
        cond_no_43_exclusion=not bool(x.excl43), cond_diag_support_or_unmeasured=bool(x.diag_ok),
        cond_diag_support=bool(x.diag_support), cond_no_contradiction=not bool(x.contradiction),
        cond_no_top40_demotion=not bool(c.demote_now or x.hgnc_id in demoted),
        supporting_classes=x.supporting_classes, n_classes=int(x.n_classes),
        **{f"class_{k}": v for k, v in cs.items()},
        n_supporting_partners=int(fl.n_supporting), frac_partners_flagged=fl.frac_any_flag, hub_share=fl.hub_share,
        lineage=c.lineage, leaveout_top_term=c.leaveout_top_term, leaveout_retained=bool(c.leaveout_retained),
        leaveout_nb_overlap=c.leaveout_nb_overlap, coupling_rho=c.coupling_rho, tf_OR=c.tf_OR, tf_q=c.tf_q,
        tp53_p=c.tp53_p, tp53_q=c.tp53_q, d2_measured=bool(c.d2_measured), d2_mean_r=c.d2_mean_r,
        d2_null_p95=c.d2_null_p95, d2_replicated=c.d2_replicated, **gls_top[g],
        relationship_type=ty, relationship_reason=why, enzyme_EC=pi["enzyme_EC"],
        transport_keyword=pi["transport_keyword"], multipass=pi["multipass"], complex_like_partners=complex_like,
        zmean=p.zmean, R=p.R, cov_pct=p.cov_pct, size_pct=p.size_pct, top_size=p.top_size, top_n_sup=p.top_n_sup,
        low_coverage=bool(x.low_coverage), mito_deferred=bool(x.mito_deferred), flags="|".join(flags)))
TOP = pd.DataFrame(out)
TOP.to_csv(M6.OUT / "top40.tsv", sep="\t", index=False, float_format="%.6g")
T.reset_index().assign(symbol=lambda z: gt.symbol.values[z.matrix_index]).to_csv(
    M6.OUT / "top40_checks.tsv", sep="\t", index=False, float_format="%.6g")
ALLC = pd.DataFrame([dict(matrix_index=g, symbol=gt.symbol.values[g], hgnc_id=gt.hgnc_id.values[g], **v)
                     for g, v in CK.items()])
ALLC["demoted"] = ALLC.hgnc_id.isin(demoted)
ALLC["demotion_reason"] = ALLC.hgnc_id.map(demoted).fillna("")
ALLC.to_csv(M6.OUT / "checks_all_evaluated.tsv", sep="\t", index=False, float_format="%.6g")
pd.DataFrame(fill_log).to_csv(M6.OUT / "top40_fill_log.tsv", sep="\t", index=False)
ST.to_csv(M6.OUT / "support.tsv", sep="\t", index=False, float_format="%.6g")
SS.to_csv(M6.OUT / "support_sources.tsv", sep="\t", index=False, float_format="%.6g")
summ = dict(n_tier_A=int((d.tier == "A").sum()), n_tier_B=int((d.tier == "B").sum()),
            n_pool=int(d.pool.sum()), iterations=len(fill_log), n_checked=len(CK), n_demoted=len(demoted),
            demoted={Pi.loc[h].symbol: r for h, r in demoted.items()}, gls_verification=ver,
            type_counts=TOP.relationship_type.value_counts().to_dict(),
            n_new_support_anchors=len({r["anchor_hgnc_id"] for r in new_support_rows}))
C.write_manifest(M6.OUT / "44_manifest.json", "scripts/44_tiers_top40.py", gate,
                 ["results/ledger/u_predictions.tsv", "results/ledger/u_pcal.tsv", "results/ledger/u_flags.tsv",
                  "results/ledger/support.tsv", "config/tf_list.tsv", *DATA], seed=0, t0=T_START, extra=summ)
log(f"done: {summ}")
