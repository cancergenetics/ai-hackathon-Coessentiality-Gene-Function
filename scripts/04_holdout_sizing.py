#!/usr/bin/env python
"""04_holdout_sizing.py -- temporal hold-out H and its targets (DESIGN.md v2.1 §3.2.2, §3.5); ANNOTATION ONLY.

H = scorable genes that (i) meet D1 at t0 = GO release 2018-07-02 (same ``knownness.d1`` function, t0 GAF, t0 obo),
(ii) have <= 10 focused PMIDs with PMID < the 2018-07 cut-off (results/preregistration/pmid_date_cutoffs.tsv), and
(iii) have >= 1 target. Targets T(g) = propagated current D1-evidence BP/MF terms minus propagated t0 D1-evidence
BP/MF terms, generic terms removed, restricted to terms of size 5-200 at t0. All ID mapping and propagation use the
CURRENT obo (alt_id and single replaced_by resolved; annotations to obsolete terms without a single replacement are
dropped and counted); propagation over is_a + part_of. Term size at t0 = number of t0-background genes annotated to the
term (t0 background = scorable genes with >= 1 non-generic D1-evidence BP/MF term in the t0 GAF after mapping to the
current obo).

Also: supporting references for every (gene, target) from the current GAF; preliminary clusters (connected components
of H genes sharing a supporting PMID; neighbourhood links are added later); design effect; minimum detectable paired
precision@1 difference; named controls; sensitivity sizes (t0 = 2019-07; <= 5 PMIDs; PMID-dated targets).
No DepMap values and no pairwise quantity are used (scorable comes from the ID hub: DepMap header + UniProt rule).

Outputs: results/holdout/H_genes.tsv, results/holdout/H_targets.tsv, results/holdout/holdout_sizing.md and the
hold-out block of preregistration/CRITERIA.md.
Run: .env/bin/python -I scripts/04_holdout_sizing.py
"""
from __future__ import annotations

import math
import os
import re
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import knownness as kn  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "results", "holdout")
HUB = os.path.join(ROOT, "results", "ids", "hgnc_hub.tsv")
CUTOFFS = os.path.join(ROOT, "results", "preregistration", "pmid_date_cutoffs.tsv")
U_TSV = os.path.join(ROOT, "preregistration", "uncharacterised_genes.tsv")
CRIT = os.path.join(ROOT, "preregistration", "CRITERIA.md")

T0 = "2018-07-02"
T0_CUTOFF_DATE = "2018-07-01"
MAX_PMIDS = 10
SIZE_LO, SIZE_HI = 5, 200
CONTROLS = ["SPRING1", "PEDS1", "CCDC32", "INTS15", "HAPSTR1", "SLC25A51", "TEDC1", "TEDC2", "POU2AF2", "POU2AF3",
            "TMEM242"]
WEAK_CONTROLS = ["FIRRM", "AIRIM", "TMEM41B"]
ALPHA, POWER = 0.05, 0.80
DISCORDANT = (0.10, 0.20)
RHOS = (1.0, 0.5, 0.2)


# ============================================================================================ core builder
def build_holdout(t0: str, cutoff_pmid: int, max_pmids: int, ctx: dict) -> dict:
    pc, acc_map, onto_cur, g2p, ann_cur, prop_cur, scorable = (ctx[k] for k in
                                                               ["pc", "acc_map", "onto_cur", "g2p", "ann_cur",
                                                                "prop_cur", "scorable"])
    base = os.path.join(RAW, "go", "archive", t0)
    gaf_t0 = kn.read_gaf(os.path.join(base, "goa_human.gaf.gz"))
    onto_t0 = kn.GoOntology.from_obo(os.path.join(base, "go-basic.obo"), t0)
    d1_t0, _, d1st = kn.d1(gaf_t0, onto_t0, t0, acc_map, universe=pc.hgnc_id)
    # t0 annotations re-mapped with the CURRENT obo (strict: unresolvable obsolete terms dropped and counted)
    ann_t0, st_t0 = kn.d1_annotations(gaf_t0, onto_cur, acc_map, resolve_mode="strict")
    prop_t0 = kn.propagate_annotations(ann_t0, onto_cur)
    ent = pd.to_numeric(pc.entrez_id, errors="coerce")
    nfoc = pd.Series(ent.map(kn.focused_pmid_counts(g2p, max_genes=10, pmid_lt=cutoff_pmid)).fillna(0)
                     .astype(int).values, index=pc.hgnc_id)
    cand = [g for g in pc.hgnc_id if scorable.get(g, False) and d1_t0.at[g, "D1"] and nfoc[g] <= max_pmids]
    inf_t0 = ann_t0[~ann_t0.go_id.isin(kn.GENERIC)]
    background = sorted(set(inf_t0.hgnc_id) & {g for g, s in scorable.items() if s})
    sizes = kn.term_sizes(prop_t0, background)
    targets = kn.target_sets(prop_cur, prop_t0, cand, sizes, SIZE_LO, SIZE_HI, onto=onto_cur)
    H = [g for g in cand if targets[g]]
    # diagnostics: why candidates have no targets
    no_cur = sum(1 for g in cand if not (set(prop_cur.get(g, ())) - kn.GENERIC))
    return dict(t0=t0, cutoff_pmid=cutoff_pmid, max_pmids=max_pmids, d1_t0=d1_t0, d1st=d1st, st_t0=st_t0,
                nfoc=nfoc, cand=cand, background=background, sizes=sizes, targets=targets, H=H,
                prop_t0=prop_t0, n_cand_no_current_informative=no_cur)


# ============================================================================================ statistics
def connor_n(delta: float, psi: float, alpha=ALPHA, power=POWER) -> float:
    """Connor (1987) sample size for McNemar's test (paired binary), discordant proportion psi, difference delta."""
    za, zb = norm.ppf(1 - alpha / 2), norm.ppf(power)
    return (za * math.sqrt(psi) + zb * math.sqrt(psi - delta ** 2)) ** 2 / delta ** 2


def mde(n_eff: float, psi: float, alpha=ALPHA, power=POWER) -> float:
    """Smallest paired difference detectable with n_eff pairs (Connor 1987, solved for delta)."""
    if n_eff <= 0:
        return float("nan")
    f = lambda d: connor_n(d, psi, alpha, power) - n_eff  # noqa: E731
    hi = math.sqrt(psi) * 0.999999
    if f(hi) > 0:
        return float("nan")
    return brentq(f, 1e-6, hi)


def clusters_from_pmids(gene_pmids: dict) -> dict:
    """Connected components of genes linked by >= 1 shared PMID. Returns gene -> cluster id (1..)."""
    parent = {g: g for g in gene_pmids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_pmid = defaultdict(list)
    for g, ps in gene_pmids.items():
        for p in ps:
            by_pmid[p].append(g)
    for gs in by_pmid.values():
        for g in gs[1:]:
            ra, rb = find(gs[0]), find(g)
            if ra != rb:
                parent[rb] = ra
    roots = {}
    out = {}
    for g in sorted(gene_pmids):
        r = find(g)
        roots.setdefault(r, len(roots) + 1)
        out[g] = roots[r]
    return out


def design_effect(sizes, rho: float) -> tuple[float, float]:
    """Kish design effect for unequal clusters, deff = 1 + (m_w - 1) rho with m_w = sum m^2 / sum m;
    returns (deff, n_eff = n / deff)."""
    m = np.asarray(sizes, dtype=float)
    n = m.sum()
    mw = (m ** 2).sum() / n
    deff = 1 + (mw - 1) * rho
    return deff, n / deff


# ============================================================================================ main
def main():
    os.makedirs(OUT, exist_ok=True)
    hub = pd.read_csv(HUB, sep="\t", dtype=str, keep_default_na=False)
    pc = kn.load_hgnc_pc(os.path.join(RAW, "hgnc", "hgnc_complete_set.txt"))
    up = pd.read_csv(os.path.join(RAW, "uniprot", "uniprot_human_reviewed.tsv"), sep="\t", dtype=str,
                     keep_default_na=False)
    acc_map, _ = kn.build_acc_map(pc, up)
    hubi = hub.set_index("hgnc_id")
    scorable = (hubi.scorable == "True").to_dict()
    sym = dict(zip(pc.hgnc_id, pc.symbol))
    onto_cur = kn.GoOntology.from_obo(os.path.join(RAW, "go", "current", "go-basic.obo"), "current")
    g2p = kn.load_g2p(os.path.join(RAW, "ncbi_gene", "gene2pubmed_9606.tsv"))
    ann_cur, st_cur = kn.d1_annotations(os.path.join(RAW, "go", "current", "goa_human.gaf.gz"), onto_cur, acc_map,
                                        resolve_mode="strict")
    prop_cur = kn.propagate_annotations(ann_cur, onto_cur)
    cut = pd.read_csv(CUTOFFS, sep="\t", dtype={"cutoff_date": str}).set_index("cutoff_date").cutoff_pmid
    ctx = dict(pc=pc, acc_map=acc_map, onto_cur=onto_cur, g2p=g2p, ann_cur=ann_cur, prop_cur=prop_cur,
               scorable=scorable)

    R = build_holdout(T0, int(cut[T0_CUTOFF_DATE]), MAX_PMIDS, ctx)
    cutoff = R["cutoff_pmid"]
    H, targets, sizes = R["H"], R["targets"], R["sizes"]
    Uset = set(pd.read_csv(U_TSV, sep="\t", usecols=["hgnc_id"]).hgnc_id) if os.path.exists(U_TSV) else set()

    # ---------------------------------------------------------------- supporting references per (gene, target)
    ann_cur_g = {g: d for g, d in ann_cur[ann_cur.hgnc_id.isin(set(H))].groupby("hgnc_id")}
    trows = []
    for g in H:
        a = ann_cur_g[g]
        anc = [onto_cur.ancestors(t) for t in a.go_id]
        for t in sorted(targets[g]):
            m = np.array([t in s for s in anc])
            sup = a[m]
            row_pmids = [kn.pmids_from_refs([r]) for r in sup.reference]
            pm = sorted({p for ps in row_pmids for p in ps})
            other = sorted({tok for r in sup.reference for tok in str(r).split("|")
                            if tok and not tok.upper().startswith("PMID:")})
            any_post = any(ps and all(p >= cutoff for p in ps) for ps in row_pmids)
            all_post = bool(pm) and all(p >= cutoff for p in pm)
            trows.append(dict(hgnc_id=g, symbol=sym[g], go_id=t, go_name=onto_cur.name(t),
                              namespace=onto_cur.namespace(t), term_size_t0=int(sizes.get(t, 0)),
                              n_support_rows=len(sup), support_evidence="|".join(sorted(set(sup.evidence))),
                              support_direct_terms="|".join(sorted(set(sup.go_id))),
                              support_pmids="|".join(map(str, pm)), support_other_refs="|".join(other),
                              n_support_pmids=len(pm),
                              support_any_row_post_cutoff=any_post, support_all_pmids_post_cutoff=all_post))
    TT = pd.DataFrame(trows)
    TT["gene_in_U"] = TT.hgnc_id.isin(Uset)
    TT.to_csv(os.path.join(OUT, "H_targets.tsv"), sep="\t", index=False)

    # ---------------------------------------------------------------- clusters from shared supporting PMIDs
    gene_pmids = {g: set() for g in H}
    for g, ps in zip(TT.hgnc_id, TT.support_pmids):
        gene_pmids[g] |= {int(p) for p in str(ps).split("|") if p and p != "nan"}
    cl = clusters_from_pmids(gene_pmids)
    csize = pd.Series(cl).value_counts()
    nt = TT.groupby("hgnc_id").size()
    nt_post = TT[TT.support_any_row_post_cutoff].groupby("hgnc_id").size()
    HG = pd.DataFrame({"hgnc_id": H})
    HG["symbol"] = HG.hgnc_id.map(sym)
    HG["entrez_id"] = HG.hgnc_id.map(hubi.entrez_id)
    HG["depmap_column"] = HG.hgnc_id.map(hubi.depmap_column)
    HG["n_d1_terms_generic_t0"] = HG.hgnc_id.map(R["d1_t0"].n_d1_terms_generic)
    HG["n_pubmed_focused_before_cutoff"] = HG.hgnc_id.map(R["nfoc"])
    HG["n_targets"] = HG.hgnc_id.map(nt).fillna(0).astype(int)
    HG["n_targets_post_cutoff_support"] = HG.hgnc_id.map(nt_post).fillna(0).astype(int)
    HG["n_support_pmids"] = HG.hgnc_id.map(lambda g: len(gene_pmids[g]))
    HG["pmid_cluster"] = HG.hgnc_id.map(cl)
    HG["pmid_cluster_size"] = HG.pmid_cluster.map(csize)
    HG["in_U"] = HG.hgnc_id.isin(Uset)
    HG["named_control"] = HG.symbol.isin(CONTROLS + WEAK_CONTROLS)
    HG.to_csv(os.path.join(OUT, "H_genes.tsv"), sep="\t", index=False)

    # ---------------------------------------------------------------- power
    nH = len(H)
    csizes = csize.values
    deffs = {rho: design_effect(csizes, rho) for rho in RHOS}
    mde_rows = []
    for psi in DISCORDANT:
        r = dict(psi=psi, mde_naive=mde(nH, psi), mde_clusters_equal=mde(len(csize), psi))
        for rho in RHOS:
            r[f"mde_rho{rho}"] = mde(deffs[rho][1], psi)
        mde_rows.append(r)

    # ---------------------------------------------------------------- controls
    ctrl_rows = []
    pc_i = pc.set_index("symbol")
    for s in CONTROLS + WEAK_CONTROLS:
        if s not in pc_i.index:
            ctrl_rows.append(dict(symbol=s, status="symbol not in universe"))
            continue
        g = pc_i.at[s, "hgnc_id"]
        reasons = []
        if not scorable.get(g, False):
            reasons.append("not scorable")
        if not R["d1_t0"].at[g, "D1"]:
            reasons.append(f"not D1 at t0 ({R['d1_t0'].at[g, 'd1_terms']})")
        if R["nfoc"][g] > MAX_PMIDS:
            reasons.append(f"{R['nfoc'][g]} focused PMIDs before cut-off")
        tg = targets.get(g, set()) if g in R["cand"] else set()
        if g in R["cand"] and not tg:
            reasons.append("no target of size 5-200")
        if g not in R["cand"]:  # targets it would have had (diagnostic)
            tg_diag = kn.target_sets(prop_cur, R["prop_t0"], [g], sizes, SIZE_LO, SIZE_HI, onto=onto_cur)[g]
        else:
            tg_diag = tg
        tg_any = kn.target_sets(prop_cur, R["prop_t0"], [g], sizes, 0, 10 ** 9, onto=onto_cur)[g] - tg_diag
        ctrl_rows.append(dict(symbol=s, hgnc_id=g, weak=s in WEAK_CONTROLS, in_H=g in set(H), in_U=g in Uset,
                              status="in H" if g in set(H) else "; ".join(reasons),
                              n_focused_before=int(R["nfoc"][g]), n_targets=len(tg_diag),
                              targets="; ".join(f"{t} {onto_cur.name(t)} ({int(sizes.get(t, 0))})"
                                                for t in sorted(tg_diag, key=lambda t: sizes.get(t, 0))),
                              out_of_window="; ".join(f"{t} {onto_cur.name(t)} ({int(sizes.get(t, 0))})"
                                                      for t in sorted(tg_any, key=lambda t: sizes.get(t, 0)))))
    CT = pd.DataFrame(ctrl_rows)

    # ---------------------------------------------------------------- sensitivity sizes
    sens = []
    R19 = build_holdout("2019-07-01", int(cut["2019-07-01"]), MAX_PMIDS, ctx)
    sens.append(("t0 = 2019-07-01 (cut-off 2019-07)", len(R19["H"]), len(R19["cand"])))
    h5 = [g for g in H if R["nfoc"][g] <= 5]
    sens.append(("<= 5 focused PMIDs before cut-off", len(h5), sum(R["nfoc"][g] <= 5 for g in R["cand"])))
    hpost = sorted(set(TT.hgnc_id[TT.support_any_row_post_cutoff]))
    sens.append(("targets supported by >= 1 annotation whose PMIDs all >= 2018-07 cut-off", len(hpost), nH))
    hpost_all = sorted(set(TT.hgnc_id[TT.support_all_pmids_post_cutoff]))
    sens.append(("targets whose supporting PMIDs ALL >= 2018-07 cut-off", len(hpost_all), nH))

    # ---------------------------------------------------------------- report
    tsz = nt.reindex(H).values
    q = np.percentile(tsz, [0, 10, 25, 50, 75, 90, 100])
    st = R["st_t0"]
    n_HU = int(HG.in_U.sum())
    L = ["# Temporal hold-out H -- sizing (annotation only)", "",
         "Generated by `scripts/04_holdout_sizing.py` (criteria code `src/knownness.py`). DESIGN.md v2.1 §3.2.2/§3.5. "
         "No DepMap values, no co-essentiality, no tool run.", "",
         "## Definition", "",
         f"- t0 = GO release {T0} (goa_human GAF + go-basic.obo of that release). D1 at t0 = `knownness.d1` (same "
         "function as for U) on the t0 GAF with the t0 obo.",
         f"- <= {MAX_PMIDS} focused PMIDs (<= 10 genes per PMID, gene2pubmed 2026-10-29) with PMID < {cutoff} "
         f"(cut-off for {T0_CUTOFF_DATE}, `results/preregistration/pmid_date_cutoffs.tsv`).",
         "- scorable (ID hub: DepMap column by Entrez + tool UniProt rule).",
         f"- Targets: propagated (is_a + part_of, current go-basic) current D1-evidence BP/MF terms minus propagated t0 "
         f"D1-evidence BP/MF terms; generic terms removed; term size at t0 in [{SIZE_LO}, {SIZE_HI}], size = number of "
         f"t0-background genes annotated (t0 background = {len(R['background']):,} scorable genes with >= 1 "
         "non-generic D1-evidence BP/MF term at t0 after mapping to the current obo).",
         f"- ID mapping of the t0 GAF with the current obo: D1-evidence BP/MF rows {st['rows_bpmf_d1_evidence']:,}; "
         f"primary {st['rows_primary']:,}; alt_id resolved {st['rows_alt_id']:,} rows ({st['terms_alt_id']} terms); "
         f"replaced_by resolved {st['rows_replaced_by']:,} rows ({st['terms_replaced_by']} terms); **dropped obsolete "
         f"{st['rows_obsolete_dropped']:,} rows ({st['terms_obsolete_dropped']} terms)**; unknown ids dropped "
         f"{st['rows_unknown_dropped']} rows. Current GAF: obsolete dropped {st_cur['rows_obsolete_dropped']} rows "
         f"({st_cur['terms_obsolete_dropped']} terms), alt_id {st_cur['rows_alt_id']}, replaced_by "
         f"{st_cur['rows_replaced_by']}.", "",
         "## Size", "",
         f"- D1 at t0 (universe): {int(R['d1_t0'].D1.sum()):,}; candidates (scorable & D1 at t0 & <= {MAX_PMIDS} PMIDs): "
         f"{len(R['cand']):,}; of which without any current non-generic D1-evidence term: "
         f"{R['n_cand_no_current_informative']:,}",
         f"- **|H| = {nH:,}** genes with >= 1 target; **{len(TT):,}** (gene, target) pairs.",
         f"- |T(g)| distribution: min {q[0]:.0f}, p10 {q[1]:.0f}, p25 {q[2]:.0f}, median {q[3]:.0f}, p75 {q[4]:.0f}, "
         f"p90 {q[5]:.0f}, max {q[6]:.0f}; mean {tsz.mean():.1f}. BP targets {int((TT.namespace == 'biological_process').sum()):,}, "
         f"MF targets {int((TT.namespace == 'molecular_function').sum()):,}.",
         f"- **H ∩ U = {n_HU}** gene(s) (flagged `in_U` in H_genes.tsv): "
         f"{', '.join(HG.symbol[HG.in_U]) if n_HU else 'none'}. Expected ~0, because a target requires a current "
         "D1-evidence term; overlap arises only where targets come from ancestors of generic terms.",
         f"- (gene, target) pairs supported only by non-PMID references (GO_REF/Reactome): "
         f"{int((TT.n_support_pmids == 0).sum())}; distinct supporting PMIDs: "
         f"{len(set().union(*gene_pmids.values())):,}.", "",
         "## Preliminary clusters (shared supporting PMIDs only; N(g) links come later)", "",
         f"- clusters: **{len(csize):,}**; singletons {int((csize == 1).sum()):,}; largest {int(csize.max())}; "
         f"cluster-size distribution (size: count) "
         + ", ".join(f"{k}: {v}" for k, v in csize.value_counts().sort_index().items()) + ".",
         "- design effect deff = 1 + (m_w - 1) rho, m_w = sum m^2 / sum m (size-weighted mean cluster size "
         f"{(csizes ** 2).sum() / csizes.sum():.2f}):"]
    L += [f"  - rho = {rho}: deff {d:.2f}, effective n {ne:.0f}" for rho, (d, ne) in deffs.items()]
    L += ["", "## Minimum detectable paired precision@1 difference", "",
          "Connor (1987) McNemar approximation, two-sided alpha 0.05, power 0.80, psi = proportion of discordant pairs; "
          "n = effective number of genes. 'clusters' = number of clusters treated as independent units.", "",
          "| psi | n = |H| | n = #clusters | " + " | ".join(f"n_eff (rho={r})" for r in RHOS) + " |",
          "|---|---|---|" + "---|" * len(RHOS)]
    for r in mde_rows:
        L.append(f"| {r['psi']:.2f} | {r['mde_naive']:.3f} | {r['mde_clusters_equal']:.3f} | "
                 + " | ".join(f"{r[f'mde_rho{rho}']:.3f}" for rho in RHOS) + " |")
    worst = deffs[1.0][1]
    L += ["", f"Effective n under the worst case (rho = 1): {worst:.0f}; DESIGN §3.5 rule (effective n < 300 -> primary "
          f"pre-declared underpowered): **{'UNDERPOWERED' if worst < 300 else 'not underpowered'} at rho = 1**"
          f"; at rho = 0.5: {'UNDERPOWERED' if deffs[0.5][1] < 300 else 'not underpowered'}. Clusters will be "
          "enlarged by N(g) links later, so these are upper bounds on effective n.", "",
          "## Sensitivity hold-outs (sizes only)", "", "| variant | |H| | candidates/base |", "|---|---|---|"]
    L += [f"| {a} | {b:,} | {c:,} |" for a, b, c in sens]
    L += ["", "## Named controls", "",
          "| symbol | weak | in H | in U | status | focused PMIDs < cut-off | n targets | targets (term, size at t0) | "
          "new terms outside the 5-200 window (term, size at t0) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in CT.itertuples():
        L.append(f"| {r.symbol} | {getattr(r, 'weak', '')} | {getattr(r, 'in_H', '')} | {getattr(r, 'in_U', '')} | "
                 f"{r.status} | {getattr(r, 'n_focused_before', '')} | {getattr(r, 'n_targets', '')} | "
                 f"{getattr(r, 'targets', '')} | {getattr(r, 'out_of_window', '')} |")
    L += ["", "Targets listed for controls not in H are diagnostic (what they would have been). The last column lists "
          "new (current minus t0) non-generic terms excluded only by the pre-specified size window."]
    with open(os.path.join(OUT, "holdout_sizing.md"), "w") as f:
        f.write("\n".join(L) + "\n")

    # ---------------------------------------------------------------- CRITERIA.md hold-out block
    blk = ["", "## Temporal hold-out H (annotation only; `scripts/04_holdout_sizing.py`)", "",
           f"- |H| = {nH:,}; (gene, target) pairs {len(TT):,}; |T(g)| median {q[3]:.0f} (p25 {q[2]:.0f}, p75 "
           f"{q[4]:.0f}, max {q[6]:.0f}); H ∩ U = {n_HU}",
           f"- preliminary PMID clusters {len(csize):,} (largest {int(csize.max())}); effective n {deffs[1.0][1]:.0f} "
           f"(rho = 1), {deffs[0.5][1]:.0f} (rho = 0.5)",
           "- MDE (paired precision@1, 80% power, alpha 0.05 two-sided): " + "; ".join(
               f"psi {r['psi']:.2f}: {r['mde_rho1.0']:.3f} (rho 1), {r['mde_rho0.5']:.3f} (rho 0.5), "
               f"{r['mde_naive']:.3f} (no clustering)" for r in mde_rows),
           f"- named controls in H: {', '.join(CT.symbol[CT.get('in_H', False) == True]) or 'none'}",  # noqa: E712
           "- details: `results/holdout/holdout_sizing.md`", ""]
    if os.path.exists(CRIT):
        txt = open(CRIT).read()
        txt = re.sub(r"(<!-- BEGIN holdout.*?-->\n).*?(<!-- END holdout -->)",
                     lambda m: m.group(1) + "\n".join(blk) + "\n" + m.group(2), txt, flags=re.S)
        with open(CRIT, "w") as f:
            f.write(txt)
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
