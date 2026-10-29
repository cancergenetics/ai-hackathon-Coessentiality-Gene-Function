#!/usr/bin/env python
"""20_source_admission.py -- orthogonal source admission (DESIGN.md v2.3 §5.2; run at M4 before any U prediction).

Pair sources (binary, continuous, pair_binary): co-complex odds ratio on a non-hu.MAP complex gold standard
(Complex Portal + current GO CC complex terms with D1 evidence codes, ``orthogonal.complex_gold_standard``; size 2-300;
GO membership direct = primary, propagated = sensitivity) versus degree-matched random pairs:
  * universe of a source = its measured genes that are in the gold standard;
  * co-complex pairs = all pairs of measured members within each complex (a pair in several complexes counts once per
    complex: the complex is the resampling unit);
  * each co-complex pair gets R = 10 random pairs (seed 0) whose genes fall in the same degree bins
    (``support.degree_bins``: degree deciles; continuous: hubness deciles, Perturb-seq hubness x phenotype-strength
    quintiles), not co-complex in any gold complex; Burke 2023: co-complex and random pairs are restricted to pairs
    covered by Burke (HuRI u hu.MAP), random pairs stratified by the two genes' coverage-degree bins;
  * continuous sources are dichotomised at the 95th row percentile: pair score = mean of the two row percentiles,
    edge if >= 0.95 (pairs with a NaN score are dropped);
  * OR = (a/b)/(c/d) (Haldane +0.5 if a cell is 0); 95% percentile CI from 1,000 bootstrap resamples of complexes
    (seed 0; DESIGN gives no replicate number for §5.2, so 1,000 is used); admitted iff lower CI > 2.
The §5.1b P source group (BioGRID LTP, BioPlex, OpenCell, STRING experiments) is admitted as the union of its admitted
components (re-tested as a union). hu.MAP 3.0 is reported (not independent); DEMETER2 has no pair score here.

Localisation sources (HPA, OpenCell, Human Cell Map NMF, MitoCarta3.0): agreement of the source's compartment set with
the gene's current GO CC compartment set (D1 evidence codes; annotations citing the localisation sources themselves --
HPA GO_REF:0000052, OpenCell, Human Cell Map, MitoCarta papers -- excluded) on H genes
(results/holdout/H_genes.tsv) having both; agreement = shared compartment (``orthogonal.compartments_match``); Wilson
95% CI; admitted iff >= 200 H genes and lower CI > 0.6. Annotation agreement only -- no prediction outcome is used.
The same agreement on all other universe genes is reported as descriptive context (not the admission rule).

Outputs: results/orthogonal/admission.tsv, admission.md, mapping_qc.md, coverage.tsv, admission_manifest.json.
No DepMap gene-effect values or co-essentiality outputs are read (Model.csv metadata only, via the CCLE loader).
Run: .env/bin/python -I scripts/20_source_admission.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src import orthogonal as o  # noqa: E402
from src import support  # noqa: E402
from src.knownness import GoOntology  # noqa: E402

OUT = os.path.join(ROOT, "results", "orthogonal")
R_RANDOM = 10
N_BOOT = 1000
SEED = o.fz("seeds", "bootstraps")
OR_MIN = o.fz("orthogonal", "admission_or_lower_ci_min")
PCT = o.fz("orthogonal", "admission_continuous_dichotomise_percentile") / 100.0
LOC_MIN = o.fz("orthogonal", "localisation_admission_agreement_ci_lower_min")
LOC_N = o.fz("orthogonal", "localisation_admission_min_h_genes")
CI = o.fz("orthogonal", "admission_ci_level")


# ============================================================================================ pair admission
def complex_pairs(src, gold):
    """-> arrays (complex_k, a, b) of source indices for co-complex pairs of measured gold genes."""
    idx = src.index
    ks, aa, bb = [], [], []
    for k, (_, mem) in enumerate(gold):
        ii = sorted(idx[g] for g in mem if g in idx)
        if len(ii) < 2:
            continue
        ii = np.array(ii)
        iu, ju = np.triu_indices(len(ii), 1)
        ks.append(np.full(len(iu), k))
        aa.append(ii[iu])
        bb.append(ii[ju])
    if not ks:
        return np.array([], int), np.array([], int), np.array([], int)
    return np.concatenate(ks), np.concatenate(aa), np.concatenate(bb)


def pair_keys(a, b, n):
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    return lo.astype(np.int64) * n + hi


def edge_values(src, a, b):
    """1/0 edge indicator (float; NaN = not computable) for index arrays a, b."""
    if src.kind in ("binary", "pair_binary"):
        return np.asarray(src.adj[a, b]).ravel().astype(float)
    P = src.row_percentiles()
    s = (P[a, b].astype(float) + P[b, a].astype(float)) / 2
    out = (s >= PCT).astype(float)
    out[~np.isfinite(s)] = np.nan
    return out


def random_pairs(src, ka, a, b, gold_mask, cc_keys, rng):
    """R degree-matched random pairs per co-complex pair; returns (k, a', b')."""
    n = len(src.genes)
    bins = support.degree_bins(src)
    if src.kind == "pair_binary":
        cov = src.covered.tocoo()
        sel = (cov.row < cov.col) & gold_mask[cov.row] & gold_mask[cov.col]
        ca, cb = cov.row[sel], cov.col[sel]
        keep = ~np.isin(pair_keys(ca, cb, n), cc_keys)
        ca, cb = ca[keep], cb[keep]
        strata = defaultdict(list)
        sb = np.minimum(bins[ca], bins[cb]) * 100 + np.maximum(bins[ca], bins[cb])
        order = np.argsort(sb, kind="stable")
        sbo = sb[order]
        uniq, start = np.unique(sbo, return_index=True)
        ends = np.r_[start[1:], len(sbo)]
        strata = {u: order[s:e] for u, s, e in zip(uniq, start, ends)}
        want = np.minimum(bins[a], bins[b]) * 100 + np.maximum(bins[a], bins[b])
        outk, outa, outb = [], [], []
        for u in np.unique(want):
            pos = np.where(want == u)[0]
            pool = strata.get(u, np.arange(len(ca)))
            pick = pool[rng.integers(0, len(pool), size=(len(pos), R_RANDOM))]
            outk.append(np.repeat(ka[pos], R_RANDOM))
            outa.append(ca[pick].ravel())
            outb.append(cb[pick].ravel())
        return np.concatenate(outk), np.concatenate(outa), np.concatenate(outb)
    pools = {v: np.where(gold_mask & (bins == v))[0] for v in np.unique(bins[gold_mask])}
    ra = np.empty((len(a), R_RANDOM), dtype=np.int64)
    rb = np.empty((len(b), R_RANDOM), dtype=np.int64)
    for arr, out in ((a, ra), (b, rb)):
        bv = bins[arr]
        for v in np.unique(bv):
            pos = np.where(bv == v)[0]
            pool = pools[v]
            out[pos] = pool[rng.integers(0, len(pool), size=(len(pos), R_RANDOM))]
    rk = np.repeat(ka, R_RANDOM)
    ra, rb = ra.ravel(), rb.ravel()
    ok = (ra != rb) & ~np.isin(pair_keys(ra, rb, n), cc_keys)
    return rk[ok], ra[ok], rb[ok]


def odds_ratio(a, n1, c, n2):
    b, d = n1 - a, n2 - c
    a, b, c, d = (np.asarray(x, float) for x in (a, b, c, d))
    zero = (a == 0) | (b == 0) | (c == 0) | (d == 0)
    a, b, c, d = (np.where(zero, x + 0.5, x) for x in (a, b, c, d))
    return (a / b) / (c / d)


def pair_admission(src, gold, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(src.genes)
    gold_genes = set().union(*[m for _, m in gold])
    gold_mask = np.array([g in gold_genes for g in src.genes])
    if src.kind == "continuous":
        gold_mask &= np.isfinite(support.degree_bins(src)) & (support.degree_bins(src) >= 0)
    ka, a, b = complex_pairs(src, gold)
    keep = gold_mask[a] & gold_mask[b]          # continuous: genes without a hubness bin (empty rows) dropped
    ka, a, b = ka[keep], a[keep], b[keep]
    res = dict(source=src.name, cls=src.cls, kind=src.kind, independent=src.independent,
               measured_genes=n, gold_genes_measured=int(gold_mask.sum()))
    if src.kind == "pair_binary":
        cov = np.asarray(src.covered[a, b]).ravel() > 0
        ka, a, b = ka[cov], a[cov], b[cov]
    if len(a) == 0:
        return res | dict(note="no co-complex pairs measured")
    cc_keys = np.unique(pair_keys(a, b, n))
    rk, ra, rb = random_pairs(src, ka, a, b, gold_mask, cc_keys, rng)
    ec = edge_values(src, a, b)
    er = edge_values(src, ra, rb)
    okc, okr = np.isfinite(ec), np.isfinite(er)
    K = len(gold)
    x_cc = np.bincount(ka[okc], weights=ec[okc], minlength=K)
    n_cc = np.bincount(ka[okc], minlength=K).astype(float)
    x_r = np.bincount(rk[okr], weights=er[okr], minlength=K)
    n_r = np.bincount(rk[okr], minlength=K).astype(float)
    used = np.where((n_cc > 0) & (n_r > 0))[0]
    est = float(odds_ratio(x_cc[used].sum(), n_cc[used].sum(), x_r[used].sum(), n_r[used].sum()))
    W = np.zeros((N_BOOT, len(used)))
    for r in range(N_BOOT):
        W[r] = np.bincount(rng.integers(0, len(used), len(used)), minlength=len(used))
    boot = odds_ratio(W @ x_cc[used], W @ n_cc[used], W @ x_r[used], W @ n_r[used])
    lo, hi = np.percentile(boot, [100 * (1 - CI) / 2, 100 * (1 + CI) / 2])
    res.update(complexes_used=int(len(used)), cc_pairs=int(n_cc.sum()), cc_edge_rate=float(x_cc.sum() / n_cc.sum()),
               random_pairs=int(n_r.sum()), random_edge_rate=float(x_r.sum() / max(n_r.sum(), 1)), OR=est,
               CI_lo=float(lo), CI_hi=float(hi), admitted=bool(lo > OR_MIN))
    return res


# ======================================================================================== localisation
def wilson(k, n, level=CI):
    from scipy.stats import norm
    if n == 0:
        return np.nan, np.nan
    z = norm.ppf(0.5 + level / 2)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def loc_admission(src, go_comp, h_genes, universe):
    def agree(genes):
        gs = [g for g in genes if src.comp.get(g) and go_comp.get(g)]
        k = sum(o.compartments_match(src.comp[g], go_comp[g]) for g in gs)
        return k, len(gs)
    k, n = agree(h_genes)
    lo, hi = wilson(k, n)
    k2, n2 = agree(sorted(set(universe) - set(h_genes)))
    lo2, hi2 = wilson(k2, n2)
    return dict(source=src.name, cls="L", kind="localisation", independent=True, measured_genes=len(src.genes),
                H_genes_evaluated=n, H_agree=k, agreement=k / n if n else np.nan, CI_lo=lo, CI_hi=hi,
                admitted=bool(n >= LOC_N and lo > LOC_MIN),
                nonH_genes_evaluated=n2, nonH_agreement=k2 / n2 if n2 else np.nan, nonH_CI_lo=lo2, nonH_CI_hi=hi2,
                note="" if n >= LOC_N else f"fewer than {LOC_N} H genes evaluable")


# ================================================================================================= main
def sha256(path, block=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b_ in iter(lambda: f.read(block), b""):
            h.update(b_)
    return h.hexdigest()


def fmt(x, d=2):
    return "" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    m = o.mapper()
    onto = GoOntology.from_obo(os.path.join(o.RAW, "go", "current", "go-basic.obo"))
    print("loading sources ...", flush=True)
    S = {}
    for name, fn in o.LOADERS.items():
        t = time.time()
        S[name] = fn(m)
        print(f"  {name}: {len(S[name].genes)} genes ({time.time() - t:.0f}s)", flush=True)
    cc = o.go_cc_d1(m, onto)
    gold, gqc = o.complex_gold_standard(m, onto, cc, propagate=False)
    gold_p, gqc_p = o.complex_gold_standard(m, onto, cc, propagate=True)
    print("gold standard:", gqc, flush=True)

    # ---------------------------------------------------------------- pair sources
    rows = []
    pair_names = [n for n, s in S.items() if s.kind in ("binary", "continuous", "pair_binary")]
    for name in pair_names:
        t = time.time()
        r = pair_admission(S[name], gold)
        rp = pair_admission(S[name], gold_p)
        r.update(OR_propagated=rp.get("OR"), CI_lo_propagated=rp.get("CI_lo"), CI_hi_propagated=rp.get("CI_hi"))
        if not S[name].independent:
            r["note"] = "not independent: reported only"
            r["admitted_raw"], r["admitted"] = r.get("admitted"), False
        rows.append(r)
        print(f"  {name}: OR {r.get('OR', np.nan):.2f} [{r.get('CI_lo', np.nan):.2f}, {r.get('CI_hi', np.nan):.2f}] "
              f"admitted={r.get('admitted')} ({time.time() - t:.0f}s)", flush=True)
    adm = {r["source"]: r for r in rows}
    comps = [c for c in o.P_GROUP if adm[c].get("admitted")]
    if comps:
        grp = o.union_sources("P_group", "P", [S[c] for c in comps])
        r = pair_admission(grp, gold)
        rp = pair_admission(grp, gold_p)
        r.update(OR_propagated=rp.get("OR"), CI_lo_propagated=rp.get("CI_lo"), CI_hi_propagated=rp.get("CI_hi"),
                 note="§5.1b P source group = union of admitted components: " + ", ".join(comps))
        rows.append(r)
        S["P_group"] = grp
        print(f"  P_group ({comps}): OR {r['OR']:.2f} [{r['CI_lo']:.2f}, {r['CI_hi']:.2f}]", flush=True)

    # ---------------------------------------------------------------- localisation
    h = pd.read_csv(os.path.join(ROOT, "results", "holdout", "H_genes.tsv"), sep="\t", dtype=str)
    h_genes = sorted(set(h.hgnc_id))
    go_comp = o.go_cc_compartments(cc, onto)
    loc_rows = [loc_admission(S[n], go_comp, h_genes, m.universe) for n in ("HPA", "OpenCell_loc", "HCM_NMF",
                                                                            "MitoCarta3")]
    for r in loc_rows:
        print(f"  {r['source']}: n_H={r['H_genes_evaluated']} agreement {r['agreement']:.3f} "
              f"[{r['CI_lo']:.3f}, {r['CI_hi']:.3f}] admitted={r['admitted']}", flush=True)

    # ---------------------------------------------------------------- reported-only rows
    rep = [dict(source="Homology_IBA_ISO", cls="H", kind="annotation", independent=True,
                measured_genes=len(S["Homology_IBA_ISO"].genes), admitted=False,
                note="reported only (§5.1); not a pair or localisation source -- admission not applicable"),
           dict(source="DEMETER2_NI", cls="NI", kind="profile", independent=False,
                measured_genes=len(S["DEMETER2_NI"].genes), admitted=False,
                note="not independent (DepMap RNAi); §4.3 robustness only; no pair score computed here")]
    tab = pd.DataFrame(rows + loc_rows + rep)

    # ---------------------------------------------------------------- coverage
    hub = m.hub
    scor = set(hub.hgnc_id[hub.scorable == "True"])
    u_path = os.path.join(ROOT, "preregistration", "uncharacterised_genes.tsv")
    U = set()
    if os.path.exists(u_path):
        u = pd.read_csv(u_path, sep="\t", dtype=str)
        U = set(u.hgnc_id) if "hgnc_id" in u.columns else set()
    cov = []
    for name, s in S.items():
        g = set(s.genes) if s.kind != "localisation" else set(s.comp)
        cov.append(dict(source=name, cls=s.cls, kind=s.kind, independent=s.independent,
                        universe_genes=len(g & m.universe), scorable_genes=len(g & scor),
                        H_genes=len(g & set(h_genes)), U_genes=len(g & U)))
    cov = pd.DataFrame(cov)
    cov.to_csv(os.path.join(OUT, "coverage.tsv"), sep="\t", index=False)
    tab = tab.merge(cov[["source", "universe_genes", "U_genes"]], on="source", how="left")
    tab.to_csv(os.path.join(OUT, "admission.tsv"), sep="\t", index=False)
    o.write_mapping_qc(S, os.path.join(OUT, "mapping_qc.md"), m,
                       extra={"gold_standard (direct GO membership, primary)": gqc,
                              "gold_standard (propagated, sensitivity)": gqc_p,
                              "GO CC D1 rows mapped": len(cc),
                              "genes with GO CC compartments (self-refs excluded)": len(go_comp)})
    write_md(tab, cov, gqc, gqc_p, comps)

    # ---------------------------------------------------------------- manifest
    files = {
        "bioplex": ["bioplex/BioPlex_293T_Network_10K_Dec_2019.tsv", "bioplex/BioPlex_HCT116_Network_5.5K_Dec_2019.tsv"],
        "other": ["opencell/opencell-protein-interactions.csv", "opencell/opencell-localization-annotations.csv",
                  "humancellmap/saint-latest.txt", "humancellmap/preys-latest.txt", "humancellmap/baits-latest.txt",
                  "hpa/subcellular_location.tsv.zip", "mitocarta/Human.MitoCarta3.0.xls",
                  "burke2023_af2/table_AF2_HURI_HuMap_UNIQUE.csv", "complexportal/9606.tsv",
                  "go/current/go-basic.obo", "go/current/goa_human.gaf.gz",
                  "olivieri2020/biorxiv_845446_TableS2_NormZ_media-2.xlsx",
                  "ccle_proteomics/protein_quant_current_normalized.xlsx", "proteomehd/coregulation_scores.zip",
                  "string/9606.protein.physical.links.detailed.v12.5.txt.gz", "string/9606.protein.aliases.v12.5.txt.gz",
                  "biogrid/BIOGRID-ORGANISM-Homo_sapiens-5.0.262.tab3.txt",
                  "humap3/humap3_complex_pairs_20240929.pairsWprob", "depmap/Model.csv",
                  "replogle2022_perturbseq/K562_gwps_normalized_bulk_01.h5ad",
                  "replogle2022_perturbseq/K562_essential_normalized_bulk_01.h5ad",
                  "replogle2022_perturbseq/rpe1_normalized_bulk_01.h5ad",
                  "depmap_rnai/D2_combined_gene_dep_scores.csv"]}
    sha = {f: sha256(os.path.join(o.RAW, f)) for fs in files.values() for f in fs}
    man = dict(script="scripts/20_source_admission.py", design="v2.3 §5.2", seed=SEED, n_boot=N_BOOT,
               random_pairs_per_cc_pair=R_RANDOM, or_lower_ci_min=OR_MIN, continuous_percentile=PCT,
               loc_ci_lower_min=LOC_MIN, loc_min_h=LOC_N, runtime_s=round(time.time() - t0, 1), inputs_sha256=sha,
               hub_sha256=sha256(o.HUB_TSV), localisation_map_sha256=sha256(o.LOC_MAP_TSV),
               h_genes_sha256=sha256(os.path.join(ROOT, "results", "holdout", "H_genes.tsv")),
               depmap_gene_effect_read=False, coessentiality_outputs_read=False)
    with open(os.path.join(OUT, "admission_manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(f"done in {time.time() - t0:.0f}s", flush=True)


def write_md(tab, cov, gqc, gqc_p, comps):
    L = ["# Orthogonal source admission (DESIGN.md v2.3 §5.2)", "",
         "Generated by `scripts/20_source_admission.py` (M4, before any U prediction; annotation and orthogonal data "
         "only -- no DepMap gene effects, no co-essentiality output, no hit@1 outcome). Loaders: `src/orthogonal.py`; "
         "ID mapping QC: `mapping_qc.md`; per-source gene coverage: `coverage.tsv`; machine-readable: `admission.tsv`.",
         "",
         "## Rules applied",
         "",
         f"- Pair sources: co-complex odds ratio vs degree-matched random pairs ({R_RANDOM} per co-complex pair, same "
         "degree bins, not co-complex), continuous sources dichotomised at the 95th row percentile (mean of the two "
         f"row percentiles >= {PCT}); 95% percentile CI over {N_BOOT} bootstrap resamples of complexes (seed {SEED}); "
         f"**admitted iff lower CI > {OR_MIN}**. Burke 2023: co-complex and random pairs restricted to modelled "
         "(HuRI u hu.MAP) pairs.",
         f"- Gold standard (primary): {gqc['complexes_kept']} non-hu.MAP complexes (Complex Portal "
         f"{gqc['complexportal_kept']} after excluding {gqc['complexportal_humap_identity_excluded']} entries "
         f"cross-referenced to hu.MAP as 'identity'; GO CC {gqc['go_cc_kept']} complex terms under GO:0032991 with D1 "
         f"evidence, direct membership), 2-300 members, {gqc['genes_in_gold_standard']} genes. Sensitivity: GO CC "
         f"membership propagated over is_a/part_of ({gqc_p['complexes_kept']} complexes; columns `*_propagated`).",
         f"- Localisation sources: agreement (shared compartment, `config/localisation_map.tsv`) with current GO CC "
         f"(D1 evidence; annotations from the sources themselves excluded) on H genes; Wilson 95% CI; **admitted iff "
         f">= {LOC_N} H genes and lower CI > {LOC_MIN}**. Non-H agreement is descriptive only.",
         "- §5.1b: STRING experiments, BioGRID LTP, BioPlex and OpenCell form one P source group (union of the "
         f"admitted components: {', '.join(comps) if comps else 'none'}); Human Cell Map SAINT is a separate P source.",
         "",
         "## Pair sources", "",
         "| source | class | genes (universe) | U genes | gold genes measured | complexes | co-complex pairs | "
         "edge rate cc / random | OR [95% CI] | OR propagated [95% CI] | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in tab[tab.kind.isin(["binary", "continuous", "pair_binary"])].iterrows():
        verdict = "admitted" if r.admitted else ("reported only" if not r.independent else "not admitted")
        L.append(f"| {r.source} | {r.cls} | {int(r.universe_genes) if pd.notna(r.universe_genes) else ''} | "
                 f"{int(r.U_genes) if pd.notna(r.U_genes) else ''} | {int(r.gold_genes_measured)} | "
                 f"{int(r.complexes_used) if pd.notna(r.get('complexes_used')) else ''} | "
                 f"{int(r.cc_pairs) if pd.notna(r.get('cc_pairs')) else ''} | {fmt(r.get('cc_edge_rate'), 3)} / "
                 f"{fmt(r.get('random_edge_rate'), 3)} | {fmt(r.OR)} [{fmt(r.CI_lo)}, {fmt(r.CI_hi)}] | "
                 f"{fmt(r.OR_propagated)} [{fmt(r.CI_lo_propagated)}, {fmt(r.CI_hi_propagated)}] | {verdict}"
                 f"{' -- ' + r.note if isinstance(r.note, str) and r.note else ''} |")
    L += ["", "## Localisation sources", "",
          "| source | genes (universe) | U genes | H genes evaluable | agreement [95% CI] | verdict | non-H agreement "
          "[95% CI] (descriptive) |", "|---|---|---|---|---|---|---|"]
    for _, r in tab[tab.kind == "localisation"].iterrows():
        L.append(f"| {r.source} | {int(r.universe_genes)} | {int(r.U_genes)} | {int(r.H_genes_evaluated)} | "
                 f"{fmt(r.agreement, 3)} [{fmt(r.CI_lo, 3)}, {fmt(r.CI_hi, 3)}] | "
                 f"{'admitted' if r.admitted else 'not admitted'}{' -- ' + r.note if r.note else ''} | "
                 f"{fmt(r.nonH_agreement, 3)} [{fmt(r.nonH_CI_lo, 3)}, {fmt(r.nonH_CI_hi, 3)}] (n = "
                 f"{int(r.nonH_genes_evaluated)}) |")
    L += ["", "## Reported only", ""]
    for _, r in tab[tab.kind.isin(["annotation", "profile"])].iterrows():
        L.append(f"- {r.source} ({int(r.universe_genes)} genes): {r.note}")
    ni = tab[(tab.independent == False) & tab.kind.isin(["binary", "continuous"])]  # noqa: E712
    for _, r in ni.iterrows():
        L.append(f"- {r.source}: OR {fmt(r.OR)} [{fmt(r.CI_lo)}, {fmt(r.CI_hi)}] -- not independent, never used for "
                 "support.")
    L += ["", "## Notes", "",
          "- Admission uses only annotation agreement / co-complex enrichment; no U-gene prediction and no hold-out "
          "outcome was read.",
          "- CCLE proteomics is flagged (lines shared with DepMap, §5.1).",
          "- Consequence for §5.3/§5.4 (PI attention): OpenCell, Human Cell Map NMF and MitoCarta agree well with GO CC "
          "but fail only the >= 200-H-gene rule, so HPA is the only admitted L source. The contradiction rule needs "
          ">= 2 high-reliability sources; with admitted sources only it can never fire. `src/support.py` accepts "
          "`contradiction_sources` so the four named high-reliability sources can be used for the contradiction "
          "gate regardless of admission -- whether to do so is a PI decision (DEVIATIONS.md if adopted).",
          "- Bootstrap replicates for §5.2 are not fixed in DESIGN/frozen.yaml; 1,000 used (seed 0). Gold-standard "
          "size window 2-300 and direct GO CC membership are implementation choices of this script (propagated "
          "membership reported as sensitivity)."]
    with open(os.path.join(OUT, "admission.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
