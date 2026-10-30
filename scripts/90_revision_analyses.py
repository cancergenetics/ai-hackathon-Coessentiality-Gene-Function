#!/usr/bin/env python
"""90_revision_analyses.py -- EXPLORATORY / POST-REVIEW analyses requested by manuscript review round 1
(reviews/ms_round1_referee_domain.md, reviews/ms_round1_referee_stats.md). LOOKS.md row 2026-10-30 ("post-review
exploratory analyses on H, no spec change") was appended BEFORE any code here computed an H outcome.

No frozen rule, frozen file or earlier output is changed; existing scripts are imported, never modified. Every number
written here is exploratory and labelled so. Outputs: results/revision/ (one TSV/MD per analysis, numbers_<a>.json,
and SUMMARY.md listing every number and its file).

Sections (run all, or a subset with --only a1,a5,...):
  a1  entry-route re-stratification of U (domain M1)
  a2  novelty overlap with external catalogues (domain M4)
  a3  conditional interpretation of p_cal: annotation-gain rate among t0-eligible genes (stats M1)       [touches H]
  a4  calibration sensitivity: simpler models cross-fitted on H, separation (domain M3 / stats M3)        [touches H]
  a5  judging sensitivities: term-only, slot permutation, module-clustered (stats M4 / S2)
  a6  assessability null-adjusted estimate (stats M7)
  a7  deployable homology-else-zavg_BEF rule on H (stats M6)                                              [touches H]
  a8  named-control misses (domain M8)                                                                    [touches H]
Run: .env/bin/python -I scripts/90_revision_analyses.py [--only a1,a2]
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
GATE = C.gate_check()
C.log("gate OK")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import revision_common as RC  # noqa: E402
from revision_common import LABEL, Registry, fmt_rate, wilson  # noqa: E402

ROOT = C.ROOT
log = C.log
SEED = 0
_BASE = None


def base():
    global _BASE
    if _BASE is None:
        import m5b_common as B
        _BASE = B.Base()
    return _BASE


def as_bool(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def read(p, **kw):
    return pd.read_csv(ROOT / p, sep="\t", **kw)


def set_tables():
    """Primary top 40, S20, extra30, 10 report genes (hgnc ids), L classes, judged support."""
    t40 = read("results/ledger/top40_primary.tsv")
    s20 = read("results/m7/s20.tsv")
    x30 = read("results/m7/extra30.tsv")
    rep = ["TRAPPC5", "RBM34", "PLEKHH3", "CCDC71L", "TM2D2", "TM2D1", "C5orf34", "BICRAL", "INAFM1", "ANKRD52"]
    sets = {"top40": list(t40.hgnc_id), "S20": list(s20.hgnc_id), "extra30": list(x30.hgnc_id),
            "reports10": list(t40.set_index("symbol").loc[rep, "hgnc_id"])}
    Lx = pd.concat([pd.read_csv(f, sep="\t", header=None) for f in sorted((ROOT / "results/m7/L").glob(
        "index_batch_*.tsv"))])
    Lcls = dict(zip(Lx[0], Lx[2]))
    jg = read("results/m7/judge/analysis_main_genes.tsv")
    return sets, Lcls, jg, t40, s20, x30


# ================================================================================================ a1
def a1():
    R = Registry("a1", "A1. Entry-route re-stratification of U (domain M1) " + LABEL)
    U = read("preregistration/uncharacterised_genes.tsv", dtype={"hgnc_id": str}, low_memory=False)
    for c in ("D1", "D2", "D3"):
        U[c] = as_bool(U[c])
    F = read("results/preregistration/gene_knownness_features.tsv", low_memory=False)[["hgnc_id", "n_exp_CC"]]
    U = U.merge(F, on="hgnc_id", how="left")
    A = read("results/assessability/assessability_U.tsv")[["hgnc_id", "assessable", "assessable_design"]]
    U = U.merge(A, on="hgnc_id", how="left")
    b = base()
    # Complex Portal participants (curated human complexes; 'Identifiers' + 'Expanded participant list')
    cp = pd.read_csv(ROOT / "data/raw/complexportal/9606.tsv", sep="\t", dtype=str, keep_default_na=False)
    cp_of = {}
    for ac, nm, a, e in zip(cp["#Complex ac"], cp["Recommended name"], cp.iloc[:, 4], cp["Expanded participant list"]):
        for tok in (a + "|" + e).split("|"):
            acc = re.sub(r"\(.*", "", tok).strip()
            acc = acc.split("-")[0]
            for h in b.acc_map.get(acc, ()):
                cp_of.setdefault(h, set()).add(f"{ac} {nm}")
    U["cp_subunit"] = U.hgnc_id.map(lambda h: h in cp_of)
    U["cp_complexes"] = U.hgnc_id.map(lambda h: "; ".join(sorted(cp_of.get(h, ())))[:300])
    # experimental GO CC (current GAF, D1 evidence codes, NOT rows dropped): any CC term (feature table n_exp_CC) and
    # specifically a protein-containing complex term (descendant of GO:0032991)
    import src.knownness as kn
    old = kn.D1_ASPECTS
    try:
        kn.D1_ASPECTS = frozenset({"C"})
        ann, _ = kn.d1_annotations(str(ROOT / "data/raw/go/current/goa_human.gaf.gz"), b.onto, b.acc_map)
    finally:
        kn.D1_ASPECTS = old
    root = "GO:0032991"
    cx = {t for t in ann.go_id.unique() if t != root and root in b.onto.ancestors(t)}
    exp_cc_any = set(ann[ann.go_id != "GO:0005575"].hgnc_id)
    exp_cc_cx = set(ann[ann.go_id.isin(cx)].hgnc_id)
    U["exp_CC"] = U.n_exp_CC.fillna(0) > 0
    U["exp_CC_recomputed"] = U.hgnc_id.isin(exp_cc_any)
    U["exp_CC_complex"] = U.hgnc_id.isin(exp_cc_cx)
    U["route"] = np.where(U.D2, "D1&D2", np.where(U.D3, "D1&D3 only", "other"))
    U["score5"] = U.annotation_score == 5
    U["score_ge4"] = U.annotation_score >= 4
    U["tdark"] = U.tdl == "Tdark"
    U["artefact_flag"] = U.score5 | U.cp_subunit | U.exp_CC
    U["artefact_flag_cx"] = U.score5 | U.cp_subunit | U.exp_CC_complex
    U["assessable"] = as_bool(U.assessable)
    # memberships
    sets, Lcls, jg, *_ = set_tables()
    aud = read("results/audit/curation_lag_audit.tsv")
    U["audit_class"] = U.hgnc_id.map(dict(zip(aud.hgnc_id, aud["class"])))
    # auditor's own date split of N1 (results/audit/curation_lag_audit.md, "Patterns"): recent (key evidence 2021+)
    recent = {"ERG28", "GNG8", "SRBD1", "JHY", "NOL10", "CNPY1", "STOML3", "PRRC1", "ZKSCAN5", "TSHZ2", "TAF7L",
              "ARL14", "SELENOM"}
    U["audit_N1_timing"] = np.where(U.audit_class != "N1", "", np.where(U.symbol.isin(recent), "key evidence 2021+",
                                                                         "key evidence before 2021"))
    for s, ids in sets.items():
        U[f"in_{s}"] = U.hgnc_id.isin(ids)
    U["L_class"] = U.hgnc_id.map(Lcls)
    real = dict(zip(jg.hgnc_id, jg.real))
    U["judged_real"] = U.hgnc_id.map(real)
    cols = ["hgnc_id", "symbol", "D1", "D2", "D3", "route", "annotation_score", "score5", "score_ge4", "cp_subunit",
            "cp_complexes", "n_exp_CC", "exp_CC", "exp_CC_recomputed", "exp_CC_complex", "tdl", "tdark",
            "artefact_flag", "artefact_flag_cx", "scorable", "expressed", "assessable", "audit_class",
            "audit_N1_timing"] + [f"in_{s}" for s in sets] + ["L_class", "judged_real"]
    f_genes = RC.tsv(U[cols], "a1_U_entry_flags.tsv")

    # ---- counts in U and in each population
    pops = {"U (4,924)": U, "U scorable": U[as_bool(U.scorable)], "U assessable (C1, 635)": U[U.assessable],
            "random-50 audit": U[U.audit_class.notna()], "top 40": U[U.in_top40], "S20": U[U.in_S20],
            "extra30": U[U.in_extra30], "10 report genes": U[U.in_reports10]}
    flags = ["D2", "route_D3only", "score5", "score_ge4", "cp_subunit", "exp_CC", "exp_CC_complex", "tdark",
             "artefact_flag"]
    U["route_D3only"] = U.route == "D1&D3 only"
    for k in pops:
        pops[k] = U.loc[pops[k].index]
    rows = []
    for pn, d in pops.items():
        r = dict(population=pn, n=len(d))
        for f in flags:
            r[f] = int(d[f].sum())
        rows.append(r)
    CT = pd.DataFrame(rows)
    f_ct = RC.tsv(CT, "a1_flag_counts.tsv")
    u = pops["U (4,924)"]
    R.add("U genes entering via D1&D2 (UniProt score <= 2)", int(u.D2.sum()), f_ct)
    R.add("U genes entering via D3 only (not D2)", int(u.route_D3only.sum()), f_ct)
    R.add("U genes with UniProt annotation score 5", int(u.score5.sum()), f_ct)
    R.add("U genes with UniProt annotation score >= 4", int(u.score_ge4.sum()), f_ct)
    R.add("U genes that are Complex Portal subunits", int(u.cp_subunit.sum()), f_ct, "CORUM not in data/raw: not checked")
    R.add("U genes with >= 1 experimental GO CC term (any)", int(u.exp_CC.sum()), f_ct,
          "feature table n_exp_CC (current GAF, D1 evidence codes)")
    R.add("U genes with experimental GO CC protein-complex term (GO:0032991 desc.)", int(u.exp_CC_complex.sum()), f_ct)
    R.add("U genes Tdark", int(u.tdark.sum()), f_ct)
    R.add("U genes with any definition-artefact flag (score 5 | CP subunit | exp CC)", int(u.artefact_flag.sum()), f_ct)
    for pn in ("U assessable (C1, 635)", "top 40", "S20", "10 report genes"):
        d = pops[pn]
        R.add(f"{pn}: score 5 / CP subunit / exp CC / any artefact flag / D3-only",
              f"{int(d.score5.sum())} / {int(d.cp_subunit.sum())} / {int(d.exp_CC.sum())} / "
              f"{int(d.artefact_flag.sum())} / {int(d.route_D3only.sum())} of {len(d)}", f_ct)

    # ---- N1 rates by route and by artefact flag, Wilson CIs
    rows = []

    def rate_rows(pop_name, d, cls_col):
        d = d[d[cls_col].notna()]
        for f, lab in [("route_D3only", "entry route"), ("artefact_flag", "definition-artefact flag"),
                       ("artefact_flag_cx", "artefact flag (exp CC = complex term)"), ("score5", "UniProt score 5"),
                       ("cp_subunit", "Complex Portal subunit"), ("exp_CC", "experimental GO CC"),
                       ("tdark", "Tdark")]:
            for val in (True, False):
                x = d[d[f] == val]
                k, n = int((x[cls_col] == "N1").sum()), len(x)
                lo, hi = wilson(k, n)
                name = {("route_D3only", True): "D3 only", ("route_D3only", False): "D1&D2"}.get(
                    (f, val), "flag" if val else "no flag")
                rows.append(dict(population=pop_name, stratifier=lab, stratum=name, n=n, n_N1=k,
                                 N1_rate=k / n if n else np.nan, wilson_lo=lo, wilson_hi=hi))
            a = d[d[f]]
            bq = d[~d[f]]
            from scipy.stats import fisher_exact
            tab = [[int((a[cls_col] == "N1").sum()), int((a[cls_col] != "N1").sum())],
                   [int((bq[cls_col] == "N1").sum()), int((bq[cls_col] != "N1").sum())]]
            rows[-1]["fisher_two_sided_p_flag_vs_rest"] = fisher_exact(tab)[1] if min(len(a), len(bq)) else np.nan

    rate_rows("random-50 audit (prevalence)", pops["random-50 audit"], "audit_class")
    cand = U[U.in_top40 | U.in_S20 | U.in_extra30]
    rate_rows("top40 + S20 + extra30 (L class; selected, not prevalence)", cand, "L_class")
    rate_rows("top 40 (L class)", pops["top 40"], "L_class")
    RT = pd.DataFrame(rows)
    f_rt = RC.tsv(RT, "a1_N1_rates_by_route_and_flag.tsv")
    r50 = RT[RT.population.str.startswith("random-50")]
    for strat, lab in [("entry route", "route"), ("definition-artefact flag", "artefact flag")]:
        for _, x in r50[r50.stratifier == strat].iterrows():
            R.add(f"random-50 N1 rate, {lab} = {x.stratum}", fmt_rate(x.n_N1, x.n), f_rt)
    cr = RT[RT.population.str.startswith("top40 + S20")]
    for strat, lab in [("entry route", "route"), ("definition-artefact flag", "artefact flag")]:
        for _, x in cr[cr.stratifier == strat].iterrows():
            R.add(f"top40+S20+extra30 N1 rate (L), {lab} = {x.stratum}", fmt_rate(x.n_N1, x.n), f_rt,
                  "selected genes; not a prevalence")
    a50 = pops["random-50 audit"]
    n1 = a50[a50.audit_class == "N1"]
    k_old = int((n1.audit_N1_timing == "key evidence before 2021").sum())
    R.add("random-50 N1 split: key evidence 2021+ / before 2021 (auditor's dating)",
          f"{int((n1.audit_N1_timing == 'key evidence 2021+').sum())} / {k_old} of {len(n1)}", f_genes,
          "2021+ = recent work not yet curated (lag, sense a); before 2021 = older evidence never curated or "
          "invisible to D1/D3 (sense b). Dating is the auditor's, from curation_lag_audit.md")
    R.add("random-50 N1 'old' genes with an artefact flag",
          f"{int(n1[(n1.audit_N1_timing == 'key evidence before 2021') & n1.artefact_flag].shape[0])} of {k_old}",
          f_genes)

    # ---- judged support and assessability by flag
    rows = []
    for s in ("top40", "S20", "extra30"):
        d = U[U[f"in_{s}"]]
        for f in ("artefact_flag", "cp_subunit", "score5", "exp_CC", "route_D3only"):
            for val in (True, False):
                x = d[d[f] == val]
                k = int((x.judged_real == 1).sum())
                lo, hi = wilson(k, len(x))
                rows.append(dict(set=s, flag=f, value=val, n=len(x), n_supported=k,
                                 rate=k / len(x) if len(x) else np.nan, wilson_lo=lo, wilson_hi=hi))
    JS = pd.DataFrame(rows)
    f_js = RC.tsv(JS, "a1_judged_support_by_flag.tsv")
    for s in ("top40", "S20"):
        x = JS[(JS.set == s) & (JS.flag == "artefact_flag")]
        t, f = x[x.value].iloc[0], x[~x.value].iloc[0]
        R.add(f"{s} judged support: artefact-flag vs no flag", f"{fmt_rate(t.n_supported, t.n)} vs "
              f"{fmt_rate(f.n_supported, f.n)}", f_js)
    rows = []
    sc = U[as_bool(U.scorable)]
    for f in ("artefact_flag", "cp_subunit", "score5", "exp_CC", "route_D3only", "tdark"):
        for val in (True, False):
            x = sc[sc[f] == val]
            k = int(x.assessable.sum())
            lo, hi = wilson(k, len(x))
            rows.append(dict(flag=f, value=val, n_scorable=len(x), n_assessable=k, rate=k / len(x) if len(x) else
                             np.nan, wilson_lo=lo, wilson_hi=hi))
    AS = pd.DataFrame(rows)
    f_as = RC.tsv(AS, "a1_assessable_by_flag.tsv")
    for f, lab in (("artefact_flag", "artefact flag"), ("route_D3only", "D3-only route")):
        x = AS[AS.flag == f]
        t, n = x[x.value].iloc[0], x[~x.value].iloc[0]
        R.add(f"C1 assessable among scorable U, {lab} vs rest", f"{fmt_rate(t.n_assessable, t.n_scorable)} vs "
              f"{fmt_rate(n.n_assessable, n.n_scorable)}", f_as)
    R.note("Entry routes: U = D1 & (D2 | D3); 'D1&D2' = D2 true (UniProt score <= 2), with or without D3; 'D3 only' = D3 "
           "true and D2 false. Definition-artefact flag = UniProt score 5 OR Complex Portal subunit OR >= 1 experimental "
           "GO CC term (current GAF, D1 evidence codes). CORUM is not in data/raw and was not used.")
    R.note("N1 classes: random-50 = audit agent (results/audit/curation_lag_audit.tsv); candidate sets = agent L "
           "(results/m7/L/index_batch_*.tsv). Fisher p-values in the TSVs are exploratory and unadjusted.")
    R.save()
    log("a1 done")


# ================================================================================================ a2
def a2():
    R = Registry("a2", "A2. Novelty overlap with external catalogues (domain M4) " + LABEL)
    b = base()
    sets, Lcls, jg, t40, s20, x30 = set_tables()
    genes = list(dict.fromkeys(sets["top40"] + sets["S20"]))
    sym = dict(zip(b.gt.hgnc_id, b.gt.symbol))
    UP = read("results/ledger/u_partners.tsv")
    UP = UP[UP.hgnc_id.isin(genes) & (UP["rank"] <= 10)]
    P10 = UP.groupby("hgnc_id").partner_hgnc_id.apply(list).to_dict()
    assert all(len(P10.get(g, [])) == 10 for g in genes), "top-10 partners missing"
    smap, _ = RC.hgnc_symbol_map()
    acc_of = {}
    for a, hs in b.acc_map.items():
        for h in hs:
            acc_of.setdefault(h, set()).add(a)

    def h_of_acc(a):
        return b.acc_map.get(str(a).split("-")[0], ())

    # hu.MAP 3.0 complexes
    hm = pd.read_csv(ROOT / "data/raw/humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv")
    cx_of = {}
    for cid, conf, accs in zip(hm.HuMAP3_ID, hm.ComplexConfidence, hm.Uniprot_ACCs):
        mem = {h for a in str(accs).split() for h in h_of_acc(a)}
        for h in mem:
            cx_of.setdefault(h, []).append((cid, int(conf), mem))
    # Predictomes 2025 (SPOC)
    need = {a for g in genes for h in [g] + P10[g] for a in acc_of.get(h, ())}
    pr = pd.read_csv(ROOT / "data/raw/predictomes2025/20251110_hs_predictome_pair_scores.csv.gz",
                     usecols=["uniprot_ids", "spoc_score"])
    ab = pr.uniprot_ids.str.split(":", expand=True)
    keep = ab[0].isin(need) & ab[1].isin(need)
    spoc = {}
    for (a1_, a2_), s in zip(ab[keep].values, pr.spoc_score[keep].values):
        for h1 in h_of_acc(a1_):
            for h2 in h_of_acc(a2_):
                k = frozenset((h1, h2))
                spoc[k] = max(spoc.get(k, -1), float(s))
    # Wainberg 2021 Supplementary Data 1-3
    W = ROOT / "data/raw/revision_downloads/wainberg2021"

    def xl(zp):
        z = zipfile.ZipFile(zp)
        return io.BytesIO(z.read(z.namelist()[0]))

    def clean(s):
        s = re.sub(r"\s*\(chr[^)]*\)", "", str(s)).strip().rstrip("*").strip()
        return smap.get(s.upper())

    wpairs, wmod, wpred = set(), {}, {}
    w_ok = (W / "41588_2021_840_MOESM3_ESM.zip").exists()
    if w_ok:
        d1 = pd.read_excel(xl(W / "41588_2021_840_MOESM3_ESM.zip"), sheet_name=0, header=2)
        lead = d1["Lead gene"].ffill()
        for a, p in zip(lead, d1["Partner gene"]):
            ha, hp = clean(a), clean(p)
            if ha and hp:
                wpairs.add(frozenset((ha, hp)))
        d2 = pd.read_excel(xl(W / "41588_2021_840_MOESM4_ESM.zip"), sheet_name=0, header=2)
        gi = list(d2.columns).index("Genes")
        for r in d2.itertuples(index=False):
            mem = {clean(x) for x in r[gi:] if isinstance(x, str)} - {None}
            for h in mem:
                wmod.setdefault(h, []).append((int(r[0]), float(r[1]), str(r[4]), mem))
        d3 = pd.read_excel(W / "41588_2021_840_MOESM5_ESM.xlsx", sheet_name=0, header=2)
        for r in d3.itertuples(index=False):
            h = clean(r[0])
            if h:
                wpred.setdefault(h, []).append(str(r[5]))
    # Kim 2019 Table S5 (edges) and S6 (MCL clusters)
    K_ = ROOT / "data/raw/revision_downloads/kim2019"
    kedges, kcl = set(), {}
    k_ok = (K_ / "lsa_201800278_TableS5.txt").exists()
    if k_ok:
        ke = pd.read_csv(K_ / "lsa_201800278_TableS5.txt", sep="\t")
        for a, p in zip(ke.GENEA, ke.GENEB):
            ha, hp = clean(a), clean(p)
            if ha and hp:
                kedges.add(frozenset((ha, hp)))
        kc = pd.read_excel(K_ / "lsa_201800278_TableS6.xlsx", sheet_name=0, header=None)
        for r in kc.iloc[1:].itertuples(index=False):
            mem = {clean(x) for x in r[1:] if isinstance(x, str)} - {None}
            for h in mem:
                kcl.setdefault(h, set()).add(int(r[0]))
    rows = []
    for g in genes:
        P = P10[g]
        hcx = cx_of.get(g, [])
        hu_any = [c for c in hcx if set(P) & c[2]]
        sp = [(sym.get(p, p), spoc.get(frozenset((g, p)), np.nan)) for p in P]
        sp_hit = [f"{s}:{v:.2f}" for s, v in sp if v >= 0.5]
        wm = wmod.get(g, [])
        wm_hit = [m for m in wm if set(P) & m[3]]
        wp_hit = [sym.get(p, p) for p in P if frozenset((g, p)) in wpairs]
        ke_hit = [sym.get(p, p) for p in P if frozenset((g, p)) in kedges]
        kc_hit = [sym.get(p, p) for p in P if kcl.get(g, set()) & kcl.get(p, set())]
        rows.append(dict(
            hgnc_id=g, symbol=sym.get(g), in_top40=g in sets["top40"], in_S20=g in sets["S20"],
            in_reports10=g in sets["reports10"], L_class=Lcls.get(g),
            top10_partners=",".join(sym.get(p, p) for p in P),
            humap_n_complexes_with_gene=len(hcx), humap_cocomplex_top10=bool(hu_any),
            humap_partners_cocomplexed=",".join(sorted({sym.get(p, p) for c in hu_any for p in set(P) & c[2]})),
            predictomes_spoc_max_top10=np.nanmax([v for _, v in sp]) if np.isfinite([v for _, v in sp]).any() else np.nan,
            predictomes_spoc_ge0p5_top10=bool(sp_hit), predictomes_pairs_ge0p5=",".join(sp_hit),
            wainberg_in_any_module=bool(wm) if w_ok else np.nan,
            wainberg_module_with_top10=bool(wm_hit) if w_ok else np.nan,
            wainberg_module_d_ge0p5_with_top10=any(m[1] >= 0.5 for m in wm_hit) if w_ok else np.nan,
            wainberg_modules=";".join(f"{m[0]}(d={m[1]},n={len(m[3])}):{m[2][:60]}"
                                      for m in sorted(wm_hit, key=lambda m: -m[1])[:3]),
            wainberg_gls_pair_top10=bool(wp_hit) if w_ok else np.nan, wainberg_pair_partners=",".join(wp_hit),
            wainberg_uncharacterised_prediction="; ".join(wpred.get(g, []))[:200],
            kim2019_edge_top10=bool(ke_hit) if k_ok else np.nan, kim2019_edge_partners=",".join(ke_hit),
            kim2019_cluster_with_top10=bool(kc_hit) if k_ok else np.nan,
            replogle2022_cluster="unavailable (no gene-cluster assignment file in data/raw/replogle2022_perturbseq)",
            pan2018="not obtainable", fireworks2021="not obtainable (supplement = undruggable-target table only)"))
    T = pd.DataFrame(rows)
    T["coessentiality_catalogue_prior"] = (T.wainberg_module_d_ge0p5_with_top10.fillna(False).astype(bool)
                                           | T.wainberg_gls_pair_top10.fillna(False).astype(bool)
                                           | (T.wainberg_uncharacterised_prediction.fillna("") != "")
                                           | T.kim2019_edge_top10.fillna(False).astype(bool)
                                           | T.kim2019_cluster_with_top10.fillna(False).astype(bool))
    T["physical_resource_prior"] = T.humap_cocomplex_top10 | T.predictomes_spoc_ge0p5_top10
    T["any_prior"] = T.coessentiality_catalogue_prior | T.physical_resource_prior
    f = RC.tsv(T, "a2_novelty_overlap.tsv")
    for s, col in (("top 40", "in_top40"), ("S20", "in_S20"), ("10 report genes", "in_reports10")):
        d = T[T[col]]
        n = len(d)
        R.add(f"{s}: hu.MAP 3.0 co-complex with >= 1 top-10 partner", f"{int(d.humap_cocomplex_top10.sum())}/{n}", f)
        R.add(f"{s}: Predictomes SPOC >= 0.5 with >= 1 top-10 partner",
              f"{int(d.predictomes_spoc_ge0p5_top10.sum())}/{n}", f)
        if w_ok:
            R.add(f"{s}: Wainberg 2021 module shared with >= 1 top-10 partner (any d / d >= 0.5)",
                  f"{int(d.wainberg_module_with_top10.astype(bool).sum())}/{n} / "
                  f"{int(d.wainberg_module_d_ge0p5_with_top10.astype(bool).sum())}/{n}", f,
                  "d = 0.2 modules are large and diffuse; the d >= 0.5 version enters the 'catalogue prior'")
            R.add(f"{s}: Wainberg 2021 GLS pair (10% FDR) with >= 1 top-10 partner",
                  f"{int(d.wainberg_gls_pair_top10.astype(bool).sum())}/{n}", f)
            R.add(f"{s}: listed in Wainberg 2021 Supp. Data 3 (uncharacterised-gene predictions)",
                  f"{int((d.wainberg_uncharacterised_prediction.fillna('') != '').sum())}/{n}", f,
                  ",".join(d[d.wainberg_uncharacterised_prediction.fillna('') != ''].symbol))
        if k_ok:
            R.add(f"{s}: Kim 2019 network edge with >= 1 top-10 partner",
                  f"{int(d.kim2019_edge_top10.astype(bool).sum())}/{n}", f)
            R.add(f"{s}: Kim 2019 MCL cluster shared with >= 1 top-10 partner",
                  f"{int(d.kim2019_cluster_with_top10.astype(bool).sum())}/{n}", f)
        R.add(f"{s}: any co-essentiality catalogue prior (Wainberg GLS pair, module d>=0.5 or Supp. Data 3; Kim edge/cluster)",
              f"{int(d.coessentiality_catalogue_prior.sum())}/{n}", f)
        R.add(f"{s}: any prior (catalogue or hu.MAP/Predictomes)", f"{int(d.any_prior.sum())}/{n}", f)
        R.add(f"{s}: no prior in any obtained resource", f"{int((~d.any_prior).sum())}/{n}", f,
              ",".join(d[~d.any_prior].symbol))
    rep = T[T.in_reports10]
    R.add("10 report genes with no prior in any obtained resource", ", ".join(rep[~rep.any_prior].symbol) or "none", f)
    R.note("Partners = the gene's top-10 zavg_BEF neighbours (results/ledger/u_partners.tsv, rank <= 10). Symbol mapping "
           "for 2019-era catalogues: HGNC approved, then unique previous symbols, then unique aliases.")
    R.note("Replogle 2022: no gene-cluster assignment file in data/raw/replogle2022_perturbseq "
           "(annotated_embedding_coordinates.csv holds embedding coordinates only) -> unavailable. Pan 2018 (Cell "
           "Systems): Cell Press SI returned HTTP 403 (bot protection), Europe PMC: not open access, PMC author "
           "manuscript supplement is a PDF only -> not obtainable. FIREWORKS 2021: the only supplementary file is the "
           "'undruggables' co-essential-partner table (not a genome-wide prediction table) -> not obtainable.")
    R.note("Overlap flags say that the co-essential (or physical) relationship between the gene and >= 1 of its own "
           "top-10 partners was already published; they do not check that the resource assigned the same function. "
           "Only Wainberg Supp. Data 3 is an explicit function prediction for uncharacterised genes.")
    R.note("Downloads and checksums: results/revision/external_manifest.tsv (DATA.md-ready).")
    R.save()
    # manifest of downloads
    man = [("wainberg2021/41588_2021_840_MOESM3_ESM.zip", "Wainberg et al. 2021 Nat Genet, Supplementary Data 1 (co-essential pairs, 10% per-gene FDR)",
            "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-021-00840-z/MediaObjects/41588_2021_840_MOESM3_ESM.zip",
            "publisher ESM, no open licence stated (article not OA); internal use only, not redistributed"),
           ("wainberg2021/41588_2021_840_MOESM4_ESM.zip", "Wainberg et al. 2021, Supplementary Data 2 (5,229 co-essential modules)",
            "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-021-00840-z/MediaObjects/41588_2021_840_MOESM4_ESM.zip",
            "publisher ESM, no open licence stated; internal use only"),
           ("wainberg2021/41588_2021_840_MOESM5_ESM.xlsx", "Wainberg et al. 2021, Supplementary Data 3 (uncharacterised-gene predictions)",
            "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-021-00840-z/MediaObjects/41588_2021_840_MOESM5_ESM.xlsx",
            "publisher ESM, no open licence stated; internal use only"),
           ("kim2019/lsa_201800278_TableS5.txt", "Kim et al. 2019 Life Sci Alliance, Table S5 (co-essentiality network edges)",
            "https://www.life-science-alliance.org/content/lsa/2/2/e201800278/DC5/embed/inline-supplementary-material-5.txt?download=true",
            "CC BY 4.0 (Life Science Alliance article licence)"),
           ("kim2019/lsa_201800278_TableS6.xlsx", "Kim et al. 2019, Table S6 (MCL gene clusters)",
            "https://www.life-science-alliance.org/content/lsa/2/2/e201800278/DC6/embed/inline-supplementary-material-6.xlsx?download=true",
            "CC BY 4.0 (Life Science Alliance article licence)"),
           ("fireworks2021/lsa_202000882_DC1.xlsx", "Amici et al. 2021 (FIREWORKS) Life Sci Alliance, Table S1 ('undruggables'; NOT a genome-wide prediction table; not used)",
            "https://www.life-science-alliance.org/content/lsa/4/2/e202000882/DC1/embed/inline-supplementary-material-1.xlsx?download=true",
            "CC BY 4.0 (Life Science Alliance article licence)")]
    import hashlib
    mrows = []
    for p, desc, url, lic in man:
        fp = ROOT / "data/raw/revision_downloads" / p
        if fp.exists():
            mrows.append(dict(path=f"data/raw/revision_downloads/{p}", description=desc, url=url,
                              sha256=hashlib.sha256(fp.read_bytes()).hexdigest(), bytes=fp.stat().st_size,
                              retrieved="2026-10-30", licence=lic))
    mrows += [dict(path="", description="Pan et al. 2018 Cell Systems supplementary tables", url="https://doi.org/10.1016/j.cels.2018.04.011",
                   sha256="", bytes="", retrieved="2026-10-30",
                   licence="NOT OBTAINABLE without login/bot check (cell.com 403; Europe PMC not OA; PMC supplement PDF only)"),
              dict(path="", description="Replogle et al. 2022 gene-cluster assignments", url="https://doi.org/10.1016/j.cell.2022.05.013",
                   sha256="", bytes="", retrieved="", licence="not fetched (task: use data/raw only); unavailable in data/raw")]
    RC.tsv(pd.DataFrame(mrows), "external_manifest.tsv")
    log("a2 done")


# ================================================================================================ a3
def a3():
    R = Registry("a3", "A3. Conditional interpretation of p_cal: annotation-gain rate (stats M1) " + LABEL)
    import m5b_common as B
    import src.knownness as kn
    from scipy.stats import beta as Beta
    b = base()
    spec = importlib.util.spec_from_file_location("hs04", ROOT / "scripts/04_holdout_sizing.py")
    hs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hs)
    hub = pd.read_csv(hs.HUB, sep="\t", dtype=str, keep_default_na=False)
    pc = kn.load_hgnc_pc(str(ROOT / "data/raw/hgnc/hgnc_complete_set.txt"))
    up = pd.read_csv(ROOT / "data/raw/uniprot/uniprot_human_reviewed.tsv", sep="\t", dtype=str, keep_default_na=False)
    acc_map, _ = kn.build_acc_map(pc, up)
    scorable = (hub.set_index("hgnc_id").scorable == "True").to_dict()
    onto_cur = b.onto
    g2p = kn.load_g2p(str(ROOT / "data/raw/ncbi_gene/gene2pubmed_9606.tsv"))
    ann_cur, _ = kn.d1_annotations(str(ROOT / "data/raw/go/current/goa_human.gaf.gz"), onto_cur, acc_map,
                                   resolve_mode="strict")
    prop_cur = kn.propagate_annotations(ann_cur, onto_cur)
    cut = pd.read_csv(ROOT / "results/preregistration/pmid_date_cutoffs.tsv", sep="\t",
                      dtype={"cutoff_date": str}).set_index("cutoff_date").cutoff_pmid
    ctx = dict(pc=pc, acc_map=acc_map, onto_cur=onto_cur, g2p=g2p, ann_cur=ann_cur, prop_cur=prop_cur,
               scorable=scorable)
    R18 = hs.build_holdout("2018-07-02", int(cut["2018-07-01"]), 10, ctx)
    HG = read("results/holdout/H_genes.tsv")
    assert len(R18["cand"]) == 5051 and len(R18["H"]) == 820 and set(R18["H"]) == set(HG.hgnc_id), \
        (len(R18["cand"]), len(R18["H"]))
    R22 = hs.build_holdout("2022-07-01", int(cut["2022-07-01"]), 10, ctx)
    PG = read("results/holdout_eval/per_gene_core.tsv")
    fit = PG[as_bool(PG.has_pred_zavg)]
    n_fit, n_hit = len(fit), int(fit.hit1_zavg.sum())
    # eligible genes with a reportable top term at t0 (H setting, as for H queries)
    v2t0 = B.build_v2(b, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
    cpos = [b.pos[g] for g in R18["cand"]]
    S = B.Scored(v2t0, b.nb, b.matches, cpos, "t0-eligible candidates")
    has_pred = {g: bool(S.r1.get(b.pos[g])) for g in R18["cand"]}
    n_ep = int(sum(has_pred.values()))
    H_ep = sum(1 for g in R18["H"] if has_pred[g])
    years18 = (pd.Timestamp("2026-05-20") - pd.Timestamp("2018-07-02")).days / 365.25
    years22 = (pd.Timestamp("2026-05-20") - pd.Timestamp("2022-07-01")).days / 365.25
    rows = []

    def add(name, k, n, horizon, note=""):
        lo, hi = wilson(k, n)
        lam = -np.log(1 - k / n) / horizon
        rows.append(dict(rate=name, k=k, n=n, p=k / n, wilson_lo=lo, wilson_hi=hi, horizon_years=round(horizon, 2),
                         annual_hazard=lam, p_over_7p88y_constant_hazard=1 - np.exp(-lam * years18), note=note))

    add("any new target (|H| / t0-eligible)", 820, 5051, years18, "holdout_sizing.md definition")
    add("primary H (non-circular target) / t0-eligible", int(len(PG)), 5051, years18)
    add("H fit set (primary H with prediction) / t0-eligible with prediction", n_fit, n_ep, years18,
        "matches the conditioning set of p_cal (PRIMARY scaling)")
    add("any new target among t0-eligible with prediction", H_ep, n_ep, years18)
    add("2022 cohort: any new target / 2022-eligible", len(R22["H"]), len(R22["cand"]), years22,
        "t0 = GO 2022-07-01, cut-off PMID 2022-07-01")
    surv = [g for g in R22["cand"] if g in set(R18["cand"])]
    add("survivors: eligible in 2018 AND still eligible in 2022 -> new target after 2022",
        sum(1 for g in surv if g in set(R22["H"])), len(surv), years22,
        "genes that stayed uncharacterised 2018->2022 (U-like survivors); gain 2022->now")
    RT = pd.DataFrame(rows)
    f_r = RC.tsv(RT, "a3_annotation_gain_rates.tsv")
    # gain rate by signal (top-K mean zavg) quintile among eligible with prediction
    elig_pred = [g for g in R18["cand"] if has_pred[g]]
    z = np.array([b.zmean[b.pos[g]] for g in elig_pred])
    inH = np.array([g in set(PG.hgnc_id) for g in elig_pred])
    q = pd.qcut(z, 5, labels=[f"Q{i}" for i in range(1, 6)])
    QR = pd.DataFrame(dict(q=q, inH=inH)).groupby("q", observed=True).inH.agg(["sum", "count"]).reset_index()
    QR["rate"] = QR["sum"] / QR["count"]
    QR[["lo", "hi"]] = [wilson(k, n) for k, n in zip(QR["sum"], QR["count"])]
    f_q = RC.tsv(QR.rename(columns={"sum": "n_in_primary_H", "count": "n_eligible_with_prediction"}),
                 "a3_gain_rate_by_signal_quintile.tsv")
    from scipy.stats import spearmanr
    # sigma p_cal rescaling with propagated interval
    pc_ = read("results/ledger/u_pcal.tsv")
    ins = pc_.support_category == "in_support"
    p = pc_.p_cal[ins].values
    Spc = float(p.sum())
    bz = np.load(ROOT / "data/derived/ledger/pcal_boot.npz", allow_pickle=True)   # own derived file (scripts/41)
    boot, ok, hid = bz["boot"], bz["ok"], bz["hgnc_id"]
    mask = np.isin(hid, pc_.hgnc_id[ins].values)
    bs = boot[ok][:, mask].sum(1).astype(float)
    t40 = read("results/ledger/top40_primary.tsv")
    m40 = np.isin(hid, t40.hgnc_id.values)
    b40 = boot[ok][:, m40].sum(1).astype(float)
    rng = np.random.default_rng(SEED)
    res = {}
    for name, k, n in (("fit", n_fit, n_ep), ("any", 820, 5051)):
        r = k / n
        rb = Beta(k + 0.5, n - k + 0.5).rvs(size=len(bs), random_state=rng)
        res[name] = dict(r=r, sigma=Spc * r, ci=np.quantile(bs * rb, [0.025, 0.975]),
                         top40=float(t40.p_cal.sum()) * r, top40_ci=np.quantile(b40 * rb, [0.025, 0.975]))
    # signal-adjusted rescaling: gain rate by top-K mean zavg quintile of the eligible cohort, applied per U gene
    edges = np.quantile(z, [0.2, 0.4, 0.6, 0.8])
    qU = np.searchsorted(edges, pc_.zmean[ins].values, side="right")
    kq, nq = QR["sum"].values.astype(int), QR["count"].values.astype(int)
    rq = kq / nq
    adj_pt = float(np.sum(p * rq[qU]))
    rqb = np.column_stack([Beta(k + 0.5, n - k + 0.5).rvs(size=len(bs), random_state=rng) for k, n in zip(kq, nq)])
    bsub = boot[ok][:, mask].astype(float)
    adj_b = (bsub * rqb[:, qU]).sum(1)
    q40 = np.searchsorted(edges, t40.zmean.values, side="right")
    adj40 = float(np.sum(t40.p_cal.values * rq[q40]))
    adj40_b = (boot[ok][:, m40].astype(float) * rqb[:, np.searchsorted(edges, pd.Series(t40.zmean.values,
                                                                                          index=t40.hgnc_id).loc[hid[m40]].values, side="right")]).sum(1)
    U_in_q = np.bincount(qU, minlength=5)
    sd_cond = float(np.sqrt(np.sum(p * (1 - p))))
    rr = res["fit"]["r"]
    sd_unc = float(np.sqrt(np.sum(p * rr * (1 - p * rr))))
    R.add("t0-eligible genes (scorable, D1 at 2018-07, <= 10 focused PMIDs pre-cut-off)", 5051, f_r)
    R.add("annotation-gain rate, any new target: 820/5,051", fmt_rate(820, 5051), f_r)
    R.add("t0-eligible genes with a reportable top term at t0", n_ep, f_r)
    R.add("gain rate matching the p_cal conditioning set (H fit set / eligible with prediction)",
          fmt_rate(n_fit, n_ep), f_r, "PRIMARY scaling factor")
    R.add("2022 cohort gain rate (3.9 y horizon)", fmt_rate(len(R22["H"]), len(R22["cand"])), f_r)
    R.add("2018->2022 survivor cohort gain after 2022 (3.9 y)", fmt_rate(int(RT.iloc[5].k), int(RT.iloc[5].n)), f_r)
    R.add("annual hazard: 2018 cohort / 2022 cohort / 2018->2022 survivors",
          f"{RT.iloc[0].annual_hazard:.4f} / {RT.iloc[4].annual_hazard:.4f} / {RT.iloc[5].annual_hazard:.4f}", f_r,
          "constant-hazard check of stationarity and survivorship")
    R.add("gain rate by top-K mean zavg quintile (Q1..Q5)", " / ".join(f"{x:.3f}" for x in QR.rate), f_q,
          f"Spearman(zmean, gained) rho = {spearmanr(z, inH)[0]:.3f}")
    R.add("Sigma p_cal in-support U (conditional; parameter CI)", f"{Spc:.1f} ({np.quantile(bs, .025):.1f}–"
          f"{np.quantile(bs, .975):.1f})", "results/ledger/pcal_summary.json")
    R.add("Poisson-binomial SD of realised conditional count, sqrt(sum p(1-p))", round(sd_cond, 2), f_r)
    for nm, lab in (("fit", "conditioning-set rate"), ("any", "any-target rate 820/5,051")):
        x = res[nm]
        R.add(f"unconditional Sigma p_cal ~= Sigma x rate ({lab})", f"{x['sigma']:.2f} ({x['ci'][0]:.2f}–"
              f"{x['ci'][1]:.2f})", f_r, "interval: bootstrap Sigma x Jeffreys-Beta rate draws (independent)")
        R.add(f"top-40 Sigma p_cal unconditional ({lab})", f"{x['top40']:.3f} ({x['top40_ci'][0]:.3f}–"
              f"{x['top40_ci'][1]:.3f})", f_r)
    R.add("Poisson-binomial SD of realised unconditional count (conditioning-set rate)", round(sd_unc, 2), f_r)
    R.add("signal-adjusted unconditional Sigma p_cal (gain rate by zmean quintile)", f"{adj_pt:.2f} "
          f"({np.quantile(adj_b, .025):.2f}–{np.quantile(adj_b, .975):.2f})", f_q,
          f"in-support U genes per eligible-cohort zmean quintile Q1..Q5: {'/'.join(map(str, U_in_q))}")
    R.add("signal-adjusted unconditional top-40 Sigma p_cal", f"{adj40:.3f} ({np.quantile(adj40_b, .025):.3f}–"
          f"{np.quantile(adj40_b, .975):.3f})", f_q)
    md_ = ["# A3. p_cal is conditional on annotation " + LABEL, "",
           "p_cal estimates P(top term confirmed | the gene receives >= 1 new experimental BP/MF annotation in the "
           "5–200 window over ~7.9 years), because H requires >= 1 target. An unconditional expectation is "
           "approximately Σp_cal × r, where r = P(gene gains such an annotation).", "",
           "Assumptions: (1) r estimated on t0-eligible genes (2018-07) applies to U genes over a similar horizon "
           "(stationary curation; PAN-GO and similar efforts may change it); (2) gaining annotation is independent of "
           "whether the top term is right, conditional on the p_cal covariates. This is VIOLATED for top-K mean zavg: "
           "the gain rate is ~0.13-0.14 in quintiles 1-4 and 0.25 in quintile 5 (table below), so a signal-adjusted "
           "rescaling (quintile-specific rate per U gene) is also reported; (3) U genes are survivors that stayed uncharacterised to 2026, so the 2018 "
           "cohort rate is likely optimistic for them (the 2022-cohort and 2018-survivor hazards are reported as "
           "checks); (4) the interval combines bootstrap parameter uncertainty in Σp_cal with binomial uncertainty "
           "in r assuming independence; it is an interval for an expectation, not a prediction interval.", "",
           *RC.df_md(RT), "", *RC.df_md(QR)]
    RC.md(md_, "a3_pcal_conditional.md")
    R.note("Sigma p_cal rows use results/ledger/u_pcal.tsv and the 2,000 saved bootstrap refits "
           "(data/derived/ledger/pcal_boot.npz); see results/revision/a3_pcal_conditional.md for assumptions.")
    R.save()
    log("a3 done")


# ================================================================================================ a4
def a4():
    R = Registry("a4", "A4. Calibration sensitivity: simpler models, separation (domain M3 / stats M3) " + LABEL)
    import m5b_common as B
    from src import calibration as cal
    from src import metrics as mt
    PG = read("results/holdout_eval/per_gene_core.tsv")
    Hc = PG[as_bool(PG.has_pred_zavg)].reset_index(drop=True)
    y = Hc.hit1_zavg.values.astype(float)
    clu = Hc.cluster_primary.values
    MOD = json.loads((ROOT / "results/calibration/model_H.json").read_text())
    OOF = read("results/holdout_eval/calibration_oof.tsv")
    assert (OOF.hgnc_id.values == Hc.hgnc_id.values).all()
    labs, inv = np.unique(clu, return_inverse=True)
    members = [np.flatnonzero(inv == c) for c in range(len(labs))]
    NB = 2000

    def metrics(p, label, n_par):
        m = B.calib_metrics(p, y)
        rng = np.random.default_rng(SEED)
        bi, bs, bb, bc = [], [], [], []
        for _ in range(NB):
            idx = np.concatenate([members[c] for c in rng.integers(0, len(labs), len(labs))])
            if y[idx].min() == y[idx].max():
                continue
            r = mt.calibration_intercept_slope(p[idx], y[idx])
            bi.append(r["intercept"]); bs.append(r["slope"]); bb.append(mt.brier(p[idx], y[idx]))
            bc.append(RC.auc(p[idx], y[idx]))
        q = lambda a: np.quantile(a, [0.025, 0.975])  # noqa: E731
        return dict(model=label, n=len(y), events=int(y.sum()), n_params_excl_intercept=n_par,
                    events_per_param=y.sum() / n_par, mean_pred=m["mean_pred"], obs_rate=m["obs_rate"],
                    citl_mean_pred_minus_obs=m["mean_pred"] - m["obs_rate"],
                    brier=m["brier"], brier_ref=m["brier_ref_constant"], brier_skill=1 - m["brier"] / m["brier_ref_constant"],
                    brier_ci_lo=q(bb)[0], brier_ci_hi=q(bb)[1],
                    intercept=m["intercept"], intercept_wald_lo=m["intercept_ci"][0], intercept_wald_hi=m["intercept_ci"][1],
                    intercept_boot_lo=q(bi)[0], intercept_boot_hi=q(bi)[1],
                    slope=m["slope"], slope_wald_lo=m["slope_ci"][0], slope_wald_hi=m["slope_ci"][1],
                    slope_boot_lo=q(bs)[0], slope_boot_hi=q(bs)[1],
                    c=RC.auc(p, y), c_boot_lo=q(bc)[0], c_boot_hi=q(bc)[1])

    rows = [metrics(OOF.p_oof.values, "frozen §3.7 model (4 covariates + family)", len(MOD["covariates"]))]
    specs = {"zmean only": (["zmean"], [1]), "zmean + coverage": (["zmean", "cov_pct"], [1, 1]),
             "zmean + term size": (["zmean", "size_pct"], [1, -1])}
    fits = {}
    for lab, (cols, signs) in specs.items():
        X = Hc[cols].values.astype(float)
        cf = cal.cross_fit(X, y, clu, signs, k=10, seeds=(0, 1, 2, 3, 4))
        rows.append(metrics(cf.oof, lab, len(cols)))
        m = cal.MonotoneLogistic(signs).fit(X, y)
        fits[lab] = (cols, signs, m, cf.oof)
    # frozen model without the signalling family (separation)
    fam = Hc.family.values
    nsig = fam != "signalling_lineage"
    pfz = OOF.p_oof.values
    r_ns = B.calib_metrics(pfz[nsig], y[nsig])
    MT = pd.DataFrame(rows)
    f_m = RC.tsv(MT, "a4_calibration_models.tsv")
    for r in rows:
        R.add(f"{r['model']}: events/parameters", f"{r['events']}/{r['n_params_excl_intercept']} = "
              f"{r['events_per_param']:.1f}", f_m, "parameters excl. intercept")
        R.add(f"{r['model']}: slope (Wald; cluster-bootstrap)", f"{r['slope']:.2f} ({r['slope_wald_lo']:.2f}–"
              f"{r['slope_wald_hi']:.2f}; {r['slope_boot_lo']:.2f}–{r['slope_boot_hi']:.2f})", f_m)
        R.add(f"{r['model']}: calibration intercept (Wald)", f"{r['intercept']:+.2f} ({r['intercept_wald_lo']:+.2f} to "
              f"{r['intercept_wald_hi']:+.2f})", f_m)
        R.add(f"{r['model']}: mean pred - observed (CITL)", f"{r['citl_mean_pred_minus_obs']:+.4f}", f_m)
        R.add(f"{r['model']}: Brier (CI) / constant / skill", f"{r['brier']:.4f} ({r['brier_ci_lo']:.4f}–"
              f"{r['brier_ci_hi']:.4f}) / {r['brier_ref']:.4f} / {r['brier_skill']:.3f}", f_m)
        R.add(f"{r['model']}: c-statistic (cluster-bootstrap CI)", f"{r['c']:.3f} ({r['c_boot_lo']:.3f}–"
              f"{r['c_boot_hi']:.3f})", f_m)
    # separation
    fc = Hc.groupby("family").hit1_zavg.agg(["sum", "count"]).reset_index()
    f_f = RC.tsv(fc.rename(columns={"sum": "hits", "count": "n"}), "a4_family_hits_H.tsv")
    sg = fc[fc.family == "signalling_lineage"].iloc[0]
    R.add("signalling/lineage family in H fit set: hits / genes", f"{int(sg['sum'])}/{int(sg['count'])}", f_f,
          f"coefficient {MOD['coef'].get('fam_signalling_lineage', float('nan')):.2f} (quasi-separation)")
    ub = RC.cp_upper_one_sided(0, int(sg["count"]))
    pc_ = read("results/ledger/u_pcal.tsv")
    ins = pc_.support_category == "in_support"
    sig_u = ins & (pc_.family == "signalling_lineage")
    R.add("one-sided 95% upper bound for signalling hit rate (0/n)", f"{ub:.4f}", f_f)
    R.add("in-support U signalling genes; their Sigma p_cal; Sigma if each at the upper bound",
          f"{int(sig_u.sum())}; {pc_.p_cal[sig_u].sum():.5f}; {ub * sig_u.sum():.1f}", f_f)
    R.add("frozen model OOF without signalling genes: n, slope (Wald), c",
          f"{int(nsig.sum())}, {r_ns['slope']:.2f} ({r_ns['slope_ci'][0]:.2f}–{r_ns['slope_ci'][1]:.2f}), "
          f"{RC.auc(pfz[nsig], y[nsig]):.3f}", f_m)
    # apply simpler models to U: support = used covariates within H P5-P95, all families
    U = read("results/ledger/tiers_all.tsv")
    Uv = U[as_bool(U.has_prediction)].copy()
    rows = []
    t40 = read("results/ledger/top40_primary.tsv")
    t40set = set(t40.hgnc_id)
    tops = {}
    for lab, (cols, signs, m, _) in fits.items():
        lo = {c: np.percentile(Hc[c], 5) for c in cols}
        hi = {c: np.percentile(Hc[c], 95) for c in cols}
        sup = np.ones(len(Uv), bool)
        for c in cols:
            sup &= (Uv[c].values >= lo[c]) & (Uv[c].values <= hi[c])
        Xu = Uv[cols].values.astype(float)
        pu = m.predict_proba(Xu)
        Uv[f"p_{lab}"] = np.where(sup, pu, np.nan)
        # bootstrap Sigma
        rng = np.random.default_rng(SEED)
        X = Hc[cols].values.astype(float)
        sums = []
        for _ in range(NB):
            idx = np.concatenate([members[c] for c in rng.integers(0, len(labs), len(labs))])
            if y[idx].min() == y[idx].max():
                continue
            sums.append(cal.MonotoneLogistic(signs).fit(X[idx], y[idx]).predict_proba(Xu[sup]).sum())
        # top 40 under this model (script 46 rules; contradiction known only for the original support set)
        pool = Uv[sup & as_bool(Uv.expressed_design) & as_bool(Uv.assessable_design)].copy()
        pool["p"] = pu[sup & as_bool(Uv.expressed_design).values & as_bool(Uv.assessable_design).values]
        pool = pool[~(as_bool(pool.excl43) | as_bool(pool.contradiction))].sort_values(["p", "symbol"],
                                                                                         ascending=[False, True])
        top, nm = [], 0
        for r in pool.itertuples():
            if len(top) < 20 and r.family == "mitochondrial":
                if nm >= 6:
                    continue
                nm += 1
            top.append(r)
            if len(top) == 40:
                break
        tdf = pd.DataFrame(top)
        tops[lab] = tdf
        rows.append(dict(model=lab, coef=";".join(f"{c}={v:.3f}" for c, v in zip(cols, m.coef_)),
                         n_in_support=int(sup.sum()), sigma_p=float(pu[sup].sum()),
                         sigma_lo=float(np.quantile(sums, .025)), sigma_hi=float(np.quantile(sums, .975)),
                         max_p=float(pu[sup].max()), top40_sigma=float(tdf.p.sum()),
                         sigma_on_frozen_support=float(pu[Uv.hgnc_id.isin(pc_.hgnc_id[ins]).values].sum()),
                         sigma_on_frozen_support_expressed=float(pu[(Uv.hgnc_id.isin(pc_.hgnc_id[ins])
                                                                     & as_bool(Uv.expressed_design)).values].sum()),
                         sigma_primary_top40=float(pu[Uv.hgnc_id.isin(t40set).values].sum()),
                         top40_overlap_with_primary=int(tdf.hgnc_id.isin(t40set).sum()),
                         top40_new=",".join(tdf.symbol[~tdf.hgnc_id.isin(t40set)])))
    SU = pd.DataFrame(rows)
    f_s = RC.tsv(SU, "a4_simple_models_on_U.tsv")
    pd.concat([t.assign(model=k)[["model", "symbol", "hgnc_id", "p", "family", "top_term_name", "zmean", "cov_pct",
                                  "size_pct", "p_cal"]] for k, t in tops.items()]).to_csv(
        RC.OUT / "a4_simple_model_top40.tsv", sep="\t", index=False, float_format="%.5g")
    R.add("frozen model: Sigma p_cal in-support U (CI); n in support", f"30.5 (13.8–49.7); {int(ins.sum())}",
          "results/ledger/pcal_summary.json")
    for r in rows:
        R.add(f"{r['model']}: Sigma p in-support U (CI); n in support; max p",
              f"{r['sigma_p']:.1f} ({r['sigma_lo']:.1f}–{r['sigma_hi']:.1f}); {r['n_in_support']}; {r['max_p']:.3f}", f_s)
        R.add(f"{r['model']}: Sigma p over the frozen model's 2,583 in-support genes (expressed only)",
              f"{r['sigma_on_frozen_support']:.1f} ({r['sigma_on_frozen_support_expressed']:.1f})", f_s,
              "like-for-like comparison with 30.5")
        R.add(f"{r['model']}: Sigma p of the primary top-40 genes under this model", f"{r['sigma_primary_top40']:.2f}",
              f_s, "frozen: 2.50")
        R.add(f"{r['model']}: top-40 Sigma p; overlap with primary top 40", f"{r['top40_sigma']:.2f}; "
              f"{r['top40_overlap_with_primary']}/40", "results/revision/a4_simple_model_top40.tsv")
    R.note("zmean + term size: the term-size coefficient sits at its sign bound (0), so this model equals zmean only.")
    R.add("frozen model: Sigma p_cal of expressed in-support U genes", f"{pc_.p_cal[ins & as_bool(pc_.expressed_design)].sum():.1f}",
          "results/ledger/u_pcal.tsv", "stats S5b")
    R.note("Simple models: sign-constrained logistic (src/calibration.MonotoneLogistic), 10-fold cluster cross-fitting "
           "with fold seeds 0–4 (as §3.7), primary PMID clusters; bootstrap = 2,000 cluster resamples (seed 0) of OOF "
           "predictions (slope/intercept/Brier/c) or refits (Sigma). U support = used covariates within H 5th–95th "
           "percentiles, no family restriction. Top 40 under a simple model follows scripts/46 (expressed, assessable, "
           "§4.3 exclusions, contradictions, mito cap); contradictions were evaluated only for the original support "
           "set, so new entrants are unchecked for contradiction.")
    R.save()
    log("a4 done")


# ================================================================================================ a5
def a5():
    R = Registry("a5", "A5. Judging sensitivities: term-only, slot permutation, module clusters (stats M4/S2) " + LABEL)
    import glob
    J = ROOT / "results/m7/judge/scores"

    def ld(j):
        fs = [f for bt in ("main1", "main2", "main3") for f in glob.glob(str(J / f"{j}_{bt}.tsv"))]
        return pd.concat([pd.read_csv(f, sep="\t") for f in fs]).set_index(["packet_id", "slot"])

    j1, j2, adj = ld("J1"), ld("J2"), ld("ADJ")
    pk = read("results/m7/judge/packet_key.tsv")
    ak = read("results/m7/answer_key.tsv")
    sl = read("results/m7/answer_key_slots.tsv")
    key = pk.merge(ak[["hgnc_id", "symbol", "real_slot"]], on="hgnc_id")
    # basis of every +1: real statements per manuscript Table 2 'Basis' column (module-only: YPEL5, DPCD, WDR7);
    # all 6 supported decoys (main sets) are term-based (justifications: process named; listed in a5_plus1_basis.tsv)
    module_only_real = {"YPEL5", "DPCD", "WDR7"}
    rows, basis = [], []
    main_ids = set(j1.index.get_level_values(0))
    for r in key.itertuples():
        if r.J_id not in main_ids:          # hval10 packets (judge validation) are not part of the main sets
            continue
        sc, sct = {}, {}
        for s in "ABCD":
            a, b_ = int(j1.loc[(r.J_id, s), "score"]), int(j2.loc[(r.J_id, s), "score"])
            f = a if a == b_ else int(adj.loc[(r.J_id, s), "score"])
            sc[s] = f
            real = s == r.real_slot
            t = f
            if f == 1:
                mod = real and r.symbol in module_only_real
                basis.append(dict(J_id=r.J_id, set=r.set, symbol=r.symbol, slot=s, real=real,
                                  basis="module label only" if mod else "term",
                                  adjudicated=a != b_, j1=j1.loc[(r.J_id, s), "justification"],
                                  j2=j2.loc[(r.J_id, s), "justification"]))
                if mod:
                    t = 0
            sct[s] = t
        lab = sl[(sl.item_id.isin(ak[ak.hgnc_id == r.hgnc_id].item_id)) & (sl.slot == r.real_slot)]
        rows.append(dict(J_id=r.J_id, hgnc_id=r.hgnc_id, symbol=r.symbol, set=r.set, real_slot=r.real_slot,
                         scores="".join("+" if sc[s] == 1 else "-" if sc[s] == -1 else "0" for s in "ABCD"),
                         scores_term="".join("+" if sct[s] == 1 else "-" if sct[s] == -1 else "0" for s in "ABCD"),
                         real=sc[r.real_slot], real_term=sct[r.real_slot],
                         d=sc[r.real_slot] - np.mean([sc[s] for s in "ABCD" if s != r.real_slot]),
                         d_term=sct[r.real_slot] - np.mean([sct[s] for s in "ABCD" if s != r.real_slot]),
                         v1p_label=lab.label.iloc[0] if len(lab) else "", v1p_label_name=lab.label_name.iloc[0]
                         if len(lab) else "", _sc=[sc[s] for s in "ABCD"], _sct=[sct[s] for s in "ABCD"],
                         _ri="ABCD".index(r.real_slot)))
    G = pd.DataFrame(rows)
    ref = read("results/m7/judge/analysis_main_genes.tsv").set_index("J_id")
    assert np.allclose(G.set_index("J_id").loc[ref.index, "d"].values, ref.d.values), "reconstruction differs"
    f_b = RC.tsv(pd.DataFrame(basis), "a5_plus1_basis.tsv")
    out = []
    for s in ("top40", "s20", "extra30"):
        g = G[G.set == s]
        for var, dcol, scol, rcol in (("primary (process or module)", "d", "_sc", "real"),
                                      ("term-only", "d_term", "_sct", "real_term")):
            p_sf, n_nz = RC.exact_signflip(g[dcol].values)
            p_slot = RC.exact_slot_permutation(list(zip(g[scol], g._ri)))
            cl = g.groupby("v1p_label")[dcol].mean()
            p_cl, n_cl = RC.exact_signflip(cl.values)
            out.append(dict(set=s, scoring=var, n=len(g), real_supported=int((g[rcol] == 1).sum()),
                            decoys_supported=int(sum(np.sum(np.array(x)[[i for i in range(4) if i != ri]] == 1)
                                                     for x, ri in zip(g[scol], g._ri))),
                            mean_d=g[dcol].mean(), signflip_p=p_sf, n_nonzero=n_nz, slot_perm_p=p_slot,
                            n_module_clusters=len(cl), n_clusters_nonzero=n_cl, cluster_signflip_p=p_cl))
    OUTT = pd.DataFrame(out)
    f_o = RC.tsv(OUTT, "a5_judging_sensitivity.tsv")
    RC.tsv(G.drop(columns=["_sc", "_sct", "_ri"]), "a5_judging_per_gene.tsv")
    for r in out:
        R.add(f"{r['set']} {r['scoring']}: real supported; decoys supported",
              f"{r['real_supported']}/{r['n']}; {r['decoys_supported']}/{3 * r['n']}", f_o)
        R.add(f"{r['set']} {r['scoring']}: exact sign-flip p (n non-zero)", f"{r['signflip_p']:.3g} ({r['n_nonzero']})",
              f_o)
        R.add(f"{r['set']} {r['scoring']}: exact slot-permutation p", f"{r['slot_perm_p']:.3g}", f_o)
        R.add(f"{r['set']} {r['scoring']}: V1'-label-clustered sign-flip p (clusters non-zero / all)",
              f"{r['cluster_signflip_p']:.3g} ({r['n_clusters_nonzero']}/{r['n_module_clusters']})", f_o)
    nb = pd.DataFrame(basis)
    R.add("supported decoys classified term-based (all sets)", f"{int(((~nb.real) & (nb.basis == 'term')).sum())}/"
          f"{int((~nb.real).sum())}", f_b)
    R.add("supported real statements resting on module label only", ", ".join(
        f"{x.symbol} ({x.set})" for x in nb[nb.real & (nb.basis != 'term')].itertuples()), f_b)
    R.note("Final per-slot scores = J1 where J1 = J2, else ADJ (scripts/52 rule); reconstruction asserted equal to "
           "analysis_main_genes.tsv. Term-only: the three real +1s that the manuscript's Table 2 'Basis' column marks "
           "as module-only (YPEL5, DPCD, WDR7; read from judge justifications) set to 0; every supported decoy's "
           "justification names the process (term) -> unchanged. Term vs module was not re-judged blind.")
    R.note("Slot permutation: real slot uniform over the 4 slots within each gene, statistic = Σ(real − mean of the other "
           "three), exact convolution. Module-clustered: d averaged within genes sharing the real statement's V1′ "
           "label, exact sign-flip over cluster means.")
    R.save()
    log("a5 done")


# ================================================================================================ a6
def a6():
    R = Registry("a6", "A6. Assessability: null-adjusted estimate (stats M7) " + LABEL)
    from scipy.stats import beta as Beta
    A = read("results/assessability/assessability_U.tsv")
    for c in ("scorable", "expressed", "clean_negative", "p_lt_alpha", "assessable", "expressed_design",
              "assessable_design", "any_dependency"):
        A[c] = as_bool(A[c])
    sc = A[A.scorable]
    cn = sc[sc.clean_negative]
    rng = np.random.default_rng(SEED)
    NS = 100_000
    rows, summ = [], []
    for strat in ("sd_tertile_withinU", "any_dependency"):
        for expcol, acol, lab in (("expressed", "assessable", "frozen expressed (635)"),
                                  ("expressed_design", "assessable_design", "DESIGN expressed (646)")):
            ex = sc[sc[expcol]]
            tot_exp = np.zeros(NS)
            tot_pt = 0.0
            obs = 0
            for lev, d in ex.groupby(strat):
                c = cn[cn[strat] == lev]
                k, n = int(c.p_lt_alpha.sum()), len(c)
                ne, no = len(d), int(d[acol].sum())
                r = k / n
                draws = rng.binomial(ne, Beta(k + 0.5, n - k + 0.5).rvs(NS, random_state=rng))
                tot_exp += draws
                tot_pt += ne * r
                obs += no
                lo, hi = wilson(k, n)
                rows.append(dict(stratifier=strat, expression=lab, level=lev, clean_neg_n=n, clean_neg_p_lt_0p05=k,
                                 false_call_rate=r, rate_lo=lo, rate_hi=hi, expressed_scorable=ne,
                                 observed_assessable=no, expected_false=ne * r, excess=no - ne * r))
            implied = obs - tot_exp
            summ.append(dict(stratifier=strat, expression=lab, observed=obs, expected_false=tot_pt,
                             expected_lo=np.quantile(tot_exp, .025), expected_hi=np.quantile(tot_exp, .975),
                             implied_true=obs - tot_pt, implied_lo=np.quantile(implied, .025),
                             implied_hi=np.quantile(implied, .975), implied_frac_U=(obs - tot_pt) / 4924,
                             implied_frac_U_lo=np.quantile(implied, .025) / 4924,
                             implied_frac_U_hi=np.quantile(implied, .975) / 4924))
    D = pd.DataFrame(rows)
    S = pd.DataFrame(summ)
    f_d = RC.tsv(D, "a6_assessability_null_by_stratum.tsv")
    f_s = RC.tsv(S, "a6_assessability_null_adjusted.tsv")
    for r in S.itertuples():
        R.add(f"by {r.stratifier}, {r.expression}: expected null calls (95% int.)",
              f"{r.expected_false:.0f} ({r.expected_lo:.0f}–{r.expected_hi:.0f}) of {r.observed}", f_s)
        R.add(f"by {r.stratifier}, {r.expression}: implied true-assessable (95% int.); % of U",
              f"{r.implied_true:.0f} ({r.implied_lo:.0f}–{r.implied_hi:.0f}); {100 * r.implied_frac_U:.1f}% "
              f"({100 * r.implied_frac_U_lo:.1f}–{100 * r.implied_frac_U_hi:.1f}%)", f_s)
    for r in D[(D.expression.str.startswith("frozen"))].itertuples():
        R.add(f"clean-negative false-call rate, {r.stratifier} = {r.level}",
              f"{r.clean_neg_p_lt_0p05}/{r.clean_neg_n} = {r.false_call_rate:.3f} ({r.rate_lo:.3f}–{r.rate_hi:.3f}); "
              f"applied to {r.expressed_scorable} expressed", f_d)
    R.note("Bound, not an estimate of specificity: assumes the clean-negative p < 0.05 rate in each stratum equals the "
           "null false-call rate among expressed genes of that stratum. Interval: Jeffreys-Beta draws of each rate "
           "plus binomial sampling of the false-call count (100,000 draws, seed 0), stratum-wise independent.")
    R.save()
    log("a6 done")


# ================================================================================================ a7
def a7():
    R = Registry("a7", "A7. Deployable combination rules on H (stats M6) " + LABEL)
    import m5b_common as B
    import src.knownness as kn
    b = base()
    CORE = pd.read_pickle(B.DER / "core.pkl")
    P, Tp, Dp = CORE["P"], CORE["Tp"], CORE["Dp"]
    clP = np.array([CORE["cl_primary"][g] for g in P])
    PG = pd.read_csv(B.OUT / "per_gene_core.tsv", sep="\t", index_col="pos")
    assert list(PG.index) == list(P)
    SEC = pd.read_csv(B.OUT / "secondary.tsv", sep="\t")
    v2t0 = B.build_v2(b, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0")
    S = B.Scored(v2t0, b.nb, b.matches, P, "zavg t0")
    # homology list: verbatim logic of scripts/36 (= scripts/33 section 2)
    g0 = kn.read_gaf(str(ROOT / B.T0_DIR / "goa_human.gaf.gz"))
    g0 = g0[~kn.is_not_qualified(g0.qualifier)]
    g0 = g0[~g0.qualifier.fillna("").str.split("|").apply(lambda x: "colocalizes_with" in x)]
    g0 = g0[g0.aspect.isin(["P", "F"]) & g0.evidence.isin(["IEA", "ISS", "IBA"])]
    res = {t: b.onto.resolve(t)[0] for t in g0.go_id.unique()}
    g0 = g0.assign(go_id=g0.go_id.map(res)).dropna(subset=["go_id"])
    Pset = set(P)
    hom = {}
    for a, t in zip(g0.acc.values, g0.go_id.values):
        for h in b.acc_map.get(kn.strip_isoform(a), ()):
            p = b.pos.get(h)
            if p in Pset:
                hom.setdefault(p, set()).add(t)
    hom_cols = {}
    for p, ts in hom.items():
        s = set()
        for t in ts:
            s |= b.onto.ancestors(t)
        hom_cols[p] = {v2t0.col[t] for t in s if t in v2t0.col}
    hl, hcov = {}, {}
    for g in P:
        pl = S.prior(g)
        hc = [c for c in pl if c in hom_cols.get(g, set())]
        hcov[g] = bool(hc)
        hl[g] = hc + [c for c in pl if c not in set(hc)]

    def hit1(lst_by_gene):
        out = []
        for g in P:
            lst = [c for c in lst_by_gene.get(int(g), []) if c not in Dp.get(int(g), set())]
            out.append(float(bool(lst) and lst[0] in Tp[int(g)]))
        return np.array(out)

    hz, hh = hit1(S.r1), hit1(hl)
    assert np.allclose(hz, PG.hit1_zavg.values)
    ref = SEC[SEC.analysis.str.startswith("Homology")].p1_method.iloc[0]
    assert abs(hh.mean() - ref) < 1e-6, (hh.mean(), ref)
    zpred = PG.has_pred_zavg.astype(bool).values
    hcv = np.array([hcov[g] for g in P])
    rules = {"zavg_BEF alone": hz, "homology alone": hh,
             "homology if it predicts, else zavg_BEF": np.where(hcv, hh, hz),
             "zavg_BEF if it predicts, else homology": np.where(zpred, hz, hh),
             "oracle union (either right; upper bound)": np.maximum(hz, hh)}
    rows = []
    for k, v in rules.items():
        ci = B.mci(v, clP)["ci_percentile"]
        dh = B.pdiff(v, hh, clP)
        rows.append(dict(rule=k, n=len(v), hits=int(v.sum()), p1=v.mean(), ci_lo=ci[0], ci_hi=ci[1],
                         d_vs_homology=v.mean() - hh.mean(), d_lo=dh["ci_percentile"][0], d_hi=dh["ci_percentile"][1]))
    # U-reweighting (inverse-odds weights; verbatim logic of scripts/33 section 8)
    Upos, cov_cur_pct = CORE["Upos"], CORE["cov_cur_pct"]
    Hc = PG[PG.has_pred_zavg.astype(bool)]
    lo5, hi95 = (np.percentile(Hc[["zmean", "R", "cov_pct"]].values, q, axis=0) for q in (5, 95))
    UX = np.column_stack([b.zmean[Upos], b.R[Upos], cov_cur_pct[Upos]])
    Uel = Upos[((UX >= lo5) & (UX <= hi95)).all(1)]
    me, sd, nf = b.cov["mean"].values, np.exp(b.cov.log_sd.values), b.cov.nan_fraction.values
    XU = np.column_stack([me[Uel], sd[Uel], nf[Uel], b.zmean[Uel], b.R[Uel], cov_cur_pct[Uel]])
    XH = PG[["mean_effect", "sd", "nan_fraction", "zmean", "R", "cov_pct"]].values.astype(float)
    TRIM = C.fz("covariate_shift", "weight_trim_percentiles")

    def weights(idx):
        f = B.logistic_fit(np.r_[XH[idx], XU], np.r_[np.zeros(len(idx)), np.ones(len(XU))])
        p = f(XH[idx])
        w = p / (1 - p)
        a, c = np.percentile(w, TRIM)
        return np.clip(w, a, c)

    w0 = weights(np.arange(len(P)))
    labs, inv = np.unique(clP, return_inverse=True)
    members = [np.flatnonzero(inv == c) for c in range(len(labs))]
    rng = np.random.default_rng(B.SEED)
    NBW = 2000
    bw = {k: np.empty(NBW) for k in rules}
    for i in range(NBW):
        idx = np.concatenate([members[c] for c in rng.integers(0, len(labs), len(labs))])
        w = weights(idx)
        for k, v in rules.items():
            bw[k][i] = np.sum(w * v[idx]) / w.sum()
    sec_uw = SEC[SEC.analysis.str.startswith("U-reweighted")].p1_zavg.iloc[0]
    for r in rows:
        v = rules[r["rule"]]
        r["p1_U_reweighted"] = float(np.sum(w0 * v) / w0.sum())
        r["uw_lo"], r["uw_hi"] = np.quantile(bw[r["rule"]], [0.025, 0.975])
    T = pd.DataFrame(rows)
    f = RC.tsv(T, "a7_combination_rules.tsv")
    assert abs(T.iloc[0].p1_U_reweighted - sec_uw) < 1e-6, (T.iloc[0].p1_U_reweighted, sec_uw)
    for r in T.itertuples():
        R.add(f"{r.rule}: precision@1 on H (cluster-bootstrap CI)", f"{r.hits}/{r.n} = {r.p1:.3f} ({r.ci_lo:.3f}–"
              f"{r.ci_hi:.3f})", f)
        if r.rule != "homology alone":
            R.add(f"{r.rule}: minus homology alone (paired cluster CI)", f"{r.d_vs_homology:+.3f} ({r.d_lo:+.3f} to "
                  f"{r.d_hi:+.3f})", f)
        R.add(f"{r.rule}: U-reweighted precision@1 (CI)", f"{r.p1_U_reweighted:.3f} ({r.uw_lo:.3f}–{r.uw_hi:.3f})", f)
    R.add("H genes where homology predicts (>= 1 t0 IEA/ISS/IBA candidate term)", f"{int(hcv.sum())}/{len(P)}", f)
    R.note("Homology 'predicts' = >= 1 candidate V2 term from t0 IEA/ISS/IBA annotations (else its list is the "
           "frequency fallback). Cluster-bootstrap CIs: 10,000 resamples of primary PMID clusters (seed 0). "
           "U-reweighted: inverse-odds weights of scripts/33 §8 (trimmed 1/99), 2,000 cluster-bootstrap refits; the "
           "zavg_BEF-alone weighted value reproduces secondary.tsv exactly (asserted).")
    R.save()
    log("a7 done")


# ================================================================================================ a8
def a8():
    R = Registry("a8", "A8. Named-control misses (domain M8) " + LABEL)
    import m5b_common as B
    from src import vocab
    b = base()
    gt = b.gt
    v2t0w = B.build_v2(b, f"{B.T0_DIR}/goa_human.gaf.gz", lo=2, hi=300, label="t0 window 2-300")
    v2t0 = B.build_v2(b, f"{B.T0_DIR}/goa_human.gaf.gz", label="t0 5-200")
    v2cur = B.build_v2(b, "data/raw/go/current/goa_human.gaf.gz", label="current")
    CT = read("results/holdout_eval/controls_case_series.tsv")
    ctrl = [(s, b.pos[h]) for s, h in zip(CT.symbol, CT.hgnc_id)]
    cpos = [g for _, g in ctrl]
    Sw = B.Scored(v2t0w, b.nb, b.matches, cpos, "controls t0 2-300")
    S5 = B.Scored(v2t0, b.nb, b.matches, cpos, "controls t0 5-200")
    tabw = Sw.sc.table
    trows, srows = [], []
    for s, g in ctrl:
        Tcur = (v2cur.prop.get(g, frozenset()) - v2t0w.prop.get(g, frozenset()))
        Tcur = {t for t in Tcur if t in v2t0w.col}            # terms present in the t0 vocabulary (any size)
        pm = {t: B.support_pmids(v2cur, g, t) for t in Tcur}
        flc = B.circ_lookup({p for ps in pm.values() for p in ps})
        stt = dict(zip(pm, B.target_states(list(pm.values()), flc))) if pm else {}
        nbr = [int(x) for x in b.nb.ids[g] if x >= 0]
        sizes_w = Sw.sizes(g)
        lst = Sw.r1.get(g, [])
        rank = {c: i + 1 for i, c in enumerate(lst)}
        tq = tabw[tabw["query"] == g].set_index("term")
        for t in sorted(Tcur):
            c = v2t0w.col[t]
            ann_nb = [gt.symbol.values[j] for j in nbr if t in v2t0w.prop.get(j, frozenset())]
            size = int(sizes_w[c])
            nsup = int(tq.loc[c, "n_sup"]) if c in tq.index else 0
            flagged = bool(stt[t][0]) if t in stt else False
            if flagged:
                reason = "circularity-flagged (excluded)"
            elif not (2 <= size <= 300):
                reason = "outside 2–300 window"
            elif c in rank:
                reason = f"ranked {rank[c]} (below rank 1)" if rank[c] > 1 else "ranked 1 (hit)"
            elif nsup < 2:
                reason = f"not reportable: {nsup} supporting partner(s) annotated at t0"
            else:
                reason = "not reportable (other)"
            trows.append(dict(control=s, term=t, term_name=b.onto.name(t), size_t0=size, in_5_200=5 <= size <= 200,
                              circ_flagged=flagged, n_partners_annotated_t0=len(ann_nb), n_sup_scored=nsup,
                              annotated_partners=",".join(ann_nb), rank_2_300=rank.get(c), reason=reason))
        top = [(v2t0w.terms[c], b.onto.name(v2t0w.terms[c]), int(sizes_w[c]),
                float(tq.loc[c, "S"]) if c in tq.index else np.nan,
                int(tq.loc[c, "n_sup"]) if c in tq.index else 0) for c in lst[:5]]
        top5_5_200 = [(v2t0.terms[c], b.onto.name(v2t0.terms[c])) for c in S5.r1.get(g, [])[:3]]
        partners = [f"{gt.symbol.values[j]}({b.nb.z[g][i]:.1f})" for i, j in enumerate(b.nb.ids[g][:10]) if j >= 0]
        srows.append(dict(control=s, in_H=bool(CT.set_index("symbol").loc[s, "in_H"]), zmean=float(b.zmean[g]),
                          R=float(b.R[g]), top10_partners=", ".join(partners),
                          n_partners_with_any_t0_term=int(sum(1 for j in nbr if v2t0.prop.get(j))),
                          top5_terms_2_300="; ".join(f"{t} {n} (size {z}, S {sv:.1f}, n_sup {ns})"
                                                    for t, n, z, sv, ns in top),
                          top3_terms_5_200="; ".join(f"{t} {n}" for t, n in top5_5_200)))
    TT = pd.DataFrame(trows)
    SS = pd.DataFrame(srows)
    rs = TT.groupby("control").reason.apply(lambda x: "; ".join(f"{k}: {v}" for k, v in
                                                                  x.map(lambda r: r.split(":")[0].split(" (")[0])
                                                                  .value_counts().items())).rename("reason_counts")
    SS = SS.merge(rs, left_on="control", right_index=True, how="left")
    f_t = RC.tsv(TT, "a8_control_target_reasons.tsv")
    f_s = RC.tsv(SS, "a8_control_summary.tsv")
    for s in CT.symbol:
        d = TT[TT.control == s]
        ss = SS[SS.control == s].iloc[0]
        R.add(f"{s}: new terms in t0 vocabulary; reasons", f"{len(d)}; {ss.reason_counts}", f_t)
        if s in ("INTS15", "TMEM41B"):
            R.add(f"{s}: top-10 partners (z)", ss.top10_partners, f_s)
            R.add(f"{s}: top terms (2–300)", ss.top5_terms_2_300, f_s)
            best = d[d.in_5_200 & ~d.circ_flagged].sort_values("n_partners_annotated_t0", ascending=False).head(3)
            R.add(f"{s}: in-window clean targets with most annotated partners",
                  "; ".join(f"{x.term_name} (size {x.size_t0}; {x.n_partners_annotated_t0} partners: "
                            f"{x.annotated_partners or '-'}; {x.reason})" for x in best.itertuples()), f_t)
    R.note("Targets here = current minus t0 V2 terms of the control present in the t0 vocabulary (any size), so terms "
           "outside 2–300 are listed with that reason. Reportable = >= 2 supporting partners (n_sup from the scorer, "
           "H setting, window 2–300 as Fig 2E). 'Annotated partners' = members of N(g) (K = 25) carrying the term at "
           "t0 (propagated); the scorer's n_sup can be lower after the IPI with/from rule.")
    R.save()
    log("a8 done")


# ================================================================================================ main
SECTIONS = dict(a1=a1, a2=a2, a3=a3, a4=a4, a5=a5, a6=a6, a7=a7, a8=a8)
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=",".join(SECTIONS))
    a = ap.parse_args()
    for s in a.only.split(","):
        t = time.perf_counter()
        SECTIONS[s.strip()]()
        log(f"{s} in {time.perf_counter() - t:.0f} s")
    hdr = ["# Revision analyses (manuscript review round 1) — SUMMARY " + LABEL, "",
           "All analyses below are EXPLORATORY and POST-REVIEW: requested by reviews/ms_round1_referee_domain.md and "
           "reviews/ms_round1_referee_stats.md, not pre-specified, no frozen rule changed. Analyses touching H outcomes "
           "(a3, a4, a7, a8) follow the LOOKS.md row dated 2026-10-30 ('post-review exploratory analyses on H, no spec "
           "change'). Generated by scripts/90_revision_analyses.py (helpers: scripts/revision_common.py); CLAIMS "
           "preview by scripts/91_claims_from_manuscript.py → results/revision/CLAIMS_preview.tsv.", ""]
    RC.write_summary(list(SECTIONS) + ["a9"], hdr)
    C.write_manifest(RC.OUT / "90_manifest.json", "scripts/90_revision_analyses.py", GATE, [], seed=SEED, t0=T_START,
                     extra=dict(sections=a.only))
    log(f"done in {time.perf_counter() - T_START:.0f} s")
