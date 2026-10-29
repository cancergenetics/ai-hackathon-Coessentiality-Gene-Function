#!/usr/bin/env python
"""03_build_preregistration.py -- pre-registered list of uncharacterised genes U (DESIGN.md v2.1 §1).

U = D1 & (D2 | D3) over the HGNC protein-coding universe (criteria: src/knownness.py), plus the pre-registered
reporting strata of §1.4. SINGLE-GENE data only: DepMap Chronos per-gene mean / SD / NaN fraction / lines < -0.5 and
per-gene expression summaries. No pairwise quantity of any kind is computed; the co-essentiality tool is not run.

Inputs (data/raw, read-only): hgnc/hgnc_complete_set.txt; go/current/{goa_human.gaf.gz, go-basic.obo};
uniprot/uniprot_human_reviewed.tsv; ncbi_gene/gene2pubmed_9606.tsv; tcrd/PharosTCRD_UniProt_Mapping.tsv;
depmap/CRISPRGeneEffect.csv; depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv;
ensembl/ensembl116_{human_paralogues,gene_coordinates}.tsv. Also results/ids/hgnc_hub.tsv (src/hgnc_hub.py) and,
for cross-checks only, results/preregistration/gene_knownness_features.tsv.

Outputs: preregistration/uncharacterised_genes.tsv, preregistration/sensitivity_sets.tsv,
preregistration/CRITERIA.md, results/preregistration/depmap_gene_summaries.tsv (all DepMap genes; single-gene),
results/preregistration/prereg_crosschecks.md.

Run: .env/bin/python -I scripts/03_build_preregistration.py
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import hgnc_hub, knownness as kn  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw")
PREREG = os.path.join(ROOT, "preregistration")
RES = os.path.join(ROOT, "results", "preregistration")
HUB = os.path.join(ROOT, "results", "ids", "hgnc_hub.tsv")
OUT_U = os.path.join(PREREG, "uncharacterised_genes.tsv")
OUT_SENS = os.path.join(PREREG, "sensitivity_sets.tsv")
OUT_CRIT = os.path.join(PREREG, "CRITERIA.md")
OUT_DEP = os.path.join(RES, "depmap_gene_summaries.tsv")
OUT_XC = os.path.join(RES, "prereg_crosschecks.md")

CURRENT_RELEASE = "GO goa_human GAF 2026-05-21 / go-basic 2026-07-26"
EXPR_MIN_LOG2TPM = 1.0
EXPR_MIN_FRAC = 0.10
DEP_THRESHOLD = -0.5
ANY_DEP_FRAC = 0.01
TANDEM_WINDOW_BP = 1_000_000
TANDEM_MIN_PARALOGUES = 2
TANDEM_TYPES = None  # primary: all Ensembl 116 paralogue types (DESIGN: "Ensembl paralogues")
TANDEM_TYPES_SENS = ("within_species_paralog", "gene_split")  # sensitivity: Ensembl within-species paralogues only
CORE_MAX_PMIDS = 3

# Chemosensory / epidermal HGNC gene groups (exact names; matched on the gene_group field, '|'-separated)
CHEMO_EPI_GROUP_PATTERNS = [
    r"^Olfactory receptors, family \d+$",
    r"^Taste 1 receptors$", r"^Taste 2 receptors$",
    r"^Vomeronasal receptors$", r"^Trace amine receptors$",
    r"^Keratin associated proteins$",
    r"^Late cornified envelope proteins$", r"^Small proline rich proteins$",
    r"^Cornified envelope precursor family$", r"^S100 fused type protein family$",
]

INPUT_FILES = [
    "hgnc/hgnc_complete_set.txt", "go/current/goa_human.gaf.gz", "go/current/go-basic.obo",
    "uniprot/uniprot_human_reviewed.tsv", "ncbi_gene/gene2pubmed_9606.tsv", "tcrd/PharosTCRD_UniProt_Mapping.tsv",
    "depmap/CRISPRGeneEffect.csv", "depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
    "ensembl/ensembl116_human_paralogues.tsv", "ensembl/ensembl116_gene_coordinates.tsv",
]


# ============================================================================================ single-gene data
def depmap_gene_summaries(path: str) -> pd.DataFrame:
    """Per-gene Chronos summaries (single-gene only): mean, SD (ddof=0, as the tool), NaN fraction, number and
    fraction (of non-NaN lines) with effect < DEP_THRESHOLD."""
    df = pd.read_csv(path, index_col=0)
    X = df.to_numpy(dtype=np.float64)
    nan = np.isnan(X)
    n_obs = (~nan).sum(0)
    with np.errstate(invalid="ignore"):
        out = pd.DataFrame({
            "depmap_column": df.columns,
            "entrez_id": [hgnc_hub.parse_depmap_column(c)[1] for c in df.columns],
            "n_lines": X.shape[0], "n_obs": n_obs,
            "chronos_mean": np.nanmean(X, 0), "chronos_sd": np.nanstd(X, 0),
            "nan_frac": nan.mean(0),
            "n_lines_lt_m0.5": np.nansum(X < DEP_THRESHOLD, 0).astype(int),
        })
    out["frac_lines_lt_m0.5"] = out["n_lines_lt_m0.5"] / out["n_obs"].where(out["n_obs"] > 0)
    out["tool_background"] = out["nan_frac"] < 0.10  # tool's BG rule (method.py max_nan)
    return out


def expression_summaries(path: str, crispr_models: set) -> tuple[pd.DataFrame, dict]:
    """Per-gene fraction of DepMap models (default expression entry per model) with log2(TPM+1) >= 1."""
    df = pd.read_csv(path, low_memory=False)
    meta = ["Unnamed: 0", "SequencingID", "ModelConditionID", "ModelID", "IsDefaultEntryForMC",
            "IsDefaultEntryForModel"]
    d = df[df.IsDefaultEntryForModel == "Yes"]
    assert d.ModelID.is_unique
    genes = [c for c in df.columns if c not in meta]
    X = d[genes].to_numpy(dtype=np.float64)
    in_crispr = d.ModelID.isin(crispr_models).to_numpy()
    with np.errstate(invalid="ignore"):
        ok = ~np.isnan(X)
        frac = (X >= EXPR_MIN_LOG2TPM).sum(0) / ok.sum(0)
        frac_c = (X[in_crispr] >= EXPR_MIN_LOG2TPM).sum(0) / ok[in_crispr].sum(0)
    out = pd.DataFrame({"expr_column": genes, "entrez_id": [hgnc_hub.parse_depmap_column(c)[1] for c in genes],
                        "expr_frac_ge1": frac, "expr_frac_ge1_crispr_lines": frac_c,
                        "expr_median_log2tpm1": np.nanmedian(X, 0)})
    st = dict(rows=len(df), default_model_rows=len(d), n_models=int(d.ModelID.nunique()),
              n_models_in_crispr=int(in_crispr.sum()), n_gene_columns=len(genes))
    return out, st


def tandem_counts(pc_ensg: pd.Series, paral_path: str, coord_path: str, types=None) -> pd.Series:
    """Number of distinct Ensembl paralogues (homology types ``types``; None = all) on the same chromosome within
    TANDEM_WINDOW_BP (gap between gene bodies) of each ENSG in ``pc_ensg``."""
    p = pd.read_csv(paral_path, sep="\t", dtype=str, usecols=[0, 2, 6])
    p.columns = ["a", "b", "type"]
    p = p[p.b.notna() & p.a.str.startswith("ENSG")]
    if types is not None:
        p = p[p.type.isin(types)]
    p = p[p.a.isin(set(pc_ensg)) & (p.a != p.b)].drop_duplicates(["a", "b"])
    c = pd.read_csv(coord_path, sep="\t", dtype=str)
    c.columns = ["ensg", "name", "entrez", "chrom", "start", "end"]
    c = c[c.chrom.isin(hgnc_hub.PRIMARY_CHROMS)].drop_duplicates("ensg").set_index("ensg")
    c["start"], c["end"] = c.start.astype(np.int64), c.end.astype(np.int64)
    p = p[p.a.isin(c.index) & p.b.isin(c.index)]
    ca, cb = c.reindex(p.a), c.reindex(p.b)
    same = ca.chrom.values == cb.chrom.values
    gap = np.maximum(0, np.maximum(ca.start.values, cb.start.values) - np.minimum(ca.end.values, cb.end.values))
    near = same & (gap <= TANDEM_WINDOW_BP)
    cnt = p[near].groupby("a").b.nunique()
    return pc_ensg.map(cnt).fillna(0).astype(int)


def chemo_groups(gene_group: pd.Series) -> tuple[pd.Series, list]:
    pats = [re.compile(x) for x in CHEMO_EPI_GROUP_PATTERNS]
    used = set()

    def hit(s):
        out = False
        for g in kn.split_multi(s):
            if any(p.match(g) for p in pats):
                used.add(g)
                out = True
        return out
    flags = gene_group.map(hit)
    return flags, sorted(used)


# ============================================================================================ main
def main():
    os.makedirs(PREREG, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    xc = []  # cross-check lines

    # ---------------------------------------------------------------- universe, hub, accession map
    if not os.path.exists(HUB):
        hgnc_hub.main()
    hub = pd.read_csv(HUB, sep="\t", dtype=str, keep_default_na=False).set_index("hgnc_id")
    pc = kn.load_hgnc_pc(os.path.join(RAW, "hgnc", "hgnc_complete_set.txt"))
    assert len(pc) == 19296 and pc.hgnc_id.is_unique
    up = pd.read_csv(os.path.join(RAW, "uniprot", "uniprot_human_reviewed.tsv"), sep="\t", dtype=str,
                     keep_default_na=False)
    acc_map, acc_st = kn.build_acc_map(pc, up)
    U_IDX = pd.Index(pc.hgnc_id, name="hgnc_id")

    # ---------------------------------------------------------------- D1 (current release)
    d1, ann, d1st = kn.d1(os.path.join(RAW, "go", "current", "goa_human.gaf.gz"),
                          os.path.join(RAW, "go", "current", "go-basic.obo"), CURRENT_RELEASE, acc_map,
                          universe=pc.hgnc_id)
    # ---------------------------------------------------------------- D2, D3
    d2, d2st = kn.d2(up, pc)
    g2p = kn.load_g2p(os.path.join(RAW, "ncbi_gene", "gene2pubmed_9606.tsv"))
    tc = pd.read_csv(os.path.join(RAW, "tcrd", "PharosTCRD_UniProt_Mapping.tsv"), sep="\t", dtype=str)
    d3 = kn.d3(g2p, tc, pc, acc_map)
    ent_num = pd.to_numeric(pc.entrez_id, errors="coerce")
    n_foc_all = pd.Series(ent_num.map(kn.focused_pmid_counts(g2p, max_genes=None)).fillna(0).astype(int).values,
                          index=U_IDX)

    T = pd.DataFrame(index=U_IDX)
    T["symbol"] = pc.symbol.values
    T["entrez_id"] = pc.entrez_id.values
    T["uniprot_ids"] = pc.uniprot_ids.fillna("").values
    T["ensembl_gene_id"] = pc.ensembl_gene_id.fillna("").values
    T["location"] = pc.location.fillna("").values
    T = T.join(d1[["n_d1_terms_informative", "n_d1_terms_generic", "n_d1_rows", "D1"]])
    T = T.join(d2).join(d3)
    T["n_pubmed_all"] = n_foc_all
    T["U"] = kn.combine_u(T.D1, T.D2, T.D3)

    # ---------------------------------------------------------------- cross-checks against the feature table
    ft = pd.read_csv(os.path.join(RES, "gene_knownness_features.tsv"), sep="\t", dtype={"entrez_id": str},
                     low_memory=False).set_index("hgnc_id").reindex(U_IDX)
    eq_score = ((ft.annotation_score == T.annotation_score) | (ft.annotation_score.isna() & T.annotation_score.isna()))
    xc.append(f"- annotation_score identical to feature table: {int(eq_score.sum())}/{len(T)}")
    xc.append(f"- TDL identical: {int((ft.tdl.fillna('') == T.tdl).sum())}/{len(T)}")
    xc.append(f"- n_pubmed_focused identical: {int((ft.n_pubmed_focused == T.n_pubmed_focused).sum())}/{len(T)}")
    viol = ((ft.n_exp_informative_BPMF_lowthroughput > 0) & T.D1)
    xc.append(f"- genes with >=1 low-throughput experimental informative BP/MF term in the feature table but D1=True "
              f"(expected only where the feature table's current-GAF symbol fallback mapped a row): {int(viol.sum())} "
              f"{list(T.symbol[viol])[:20]}")
    extra = ((ft.n_exp_informative_BPMF_lowthroughput == 0) & ~T.D1)
    xc.append(f"- genes D1=False only because of TAS/IC (no EXP/IDA/IPI/IMP/IGI/IEP informative term): "
              f"{int(extra.sum())}")
    # diagnostic: effect of a symbol fallback (not used by D1)
    gaf = kn.read_gaf(os.path.join(RAW, "go", "current", "goa_human.gaf.gz"))
    gaf = gaf[~kn.is_not_qualified(gaf.qualifier) & gaf.aspect.isin(kn.D1_ASPECTS) & gaf.evidence.isin(kn.D1_EVIDENCE)
              & (gaf.db == "UniProtKB")]
    unm = gaf[~gaf.acc.map(kn.strip_isoform).isin(acc_map)]
    sym2h = dict(zip(pc.symbol, pc.hgnc_id))
    resc = unm[unm.symbol.isin(sym2h) & ~unm.go_id.isin(kn.GENERIC)]
    rescued_genes = sorted(set(resc.symbol.map(sym2h)) & set(T.index[T.D1]))
    xc.append(f"- diagnostic: D1-eligible UniProtKB rows with unmapped accession {len(unm)}; a symbol fallback would "
              f"map {len(resc)} informative rows and flip D1 for {len(rescued_genes)} genes "
              f"({', '.join(T.loc[rescued_genes, 'symbol'])}). Not applied (accession-only mapping for every "
              f"release); these genes are flagged `d1_symbol_fallback_would_flip`.")
    T["d1_symbol_fallback_would_flip"] = T.index.isin(rescued_genes)

    # ---------------------------------------------------------------- DepMap / scorable
    T["depmap_column"] = hub.depmap_column.reindex(U_IDX).values
    T["in_depmap"] = T.depmap_column != ""
    T["tool_mapped_uniprot"] = hub.tool_mapped_uniprot.reindex(U_IDX).values
    T["scorable"] = hub.scorable.reindex(U_IDX).values == "True"
    dep = depmap_gene_summaries(os.path.join(RAW, "depmap", "CRISPRGeneEffect.csv"))
    dep_h = dep.merge(hub.reset_index()[["hgnc_id", "depmap_column"]], on="depmap_column", how="left")
    dep_h.to_csv(OUT_DEP, sep="\t", index=False)
    dsum = dep.set_index("depmap_column")
    for c in ["n_obs", "chronos_mean", "chronos_sd", "nan_frac", "n_lines_lt_m0.5", "frac_lines_lt_m0.5",
              "tool_background"]:
        T[c] = T.depmap_column.map(dsum[c]).where(T.in_depmap)
    T["any_dependency"] = (T["frac_lines_lt_m0.5"] >= ANY_DEP_FRAC).where(T.in_depmap)

    # ---------------------------------------------------------------- expression
    crispr_models = set(pd.read_csv(os.path.join(RAW, "depmap", "CRISPRGeneEffect.csv"), usecols=[0]).iloc[:, 0])
    ex, exst = expression_summaries(os.path.join(RAW, "depmap", "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"),
                                    crispr_models)
    exd = ex.drop_duplicates("entrez_id").set_index("entrez_id")
    for c in ["expr_frac_ge1", "expr_frac_ge1_crispr_lines", "expr_median_log2tpm1"]:
        T[c] = T.entrez_id.map(exd[c])
    T["has_expression_data"] = T.expr_frac_ge1.notna()
    T["expressed"] = np.where(T.has_expression_data, T.expr_frac_ge1 >= EXPR_MIN_FRAC, False)
    T["expression_stratum"] = np.where(~T.has_expression_data, "no_expression_data",
                                       np.where(T.expressed, "expressed", "not_expressed"))

    # ---------------------------------------------------------------- family strata
    T["chemosensory_epidermal"], groups_used = chemo_groups(pd.Series(pc.gene_group.fillna("").values, index=U_IDX))
    ensg = pd.Series(T.ensembl_gene_id.values, index=U_IDX)
    paral = os.path.join(RAW, "ensembl", "ensembl116_human_paralogues.tsv")
    coord = os.path.join(RAW, "ensembl", "ensembl116_gene_coordinates.tsv")
    T["n_paralogues_within_1Mb"] = tandem_counts(ensg, paral, coord, TANDEM_TYPES).values
    T["n_paralogues_within_1Mb_withinspecies"] = tandem_counts(ensg, paral, coord, TANDEM_TYPES_SENS).values
    T["tandem_cluster"] = T.n_paralogues_within_1Mb >= TANDEM_MIN_PARALOGUES
    T["tandem_cluster_withinspecies"] = T.n_paralogues_within_1Mb_withinspecies >= TANDEM_MIN_PARALOGUES
    T["family_stratum"] = np.where(T.chemosensory_epidermal, "chemosensory_epidermal",
                                   np.where(T.tandem_cluster, "tandem_cluster", "other"))
    T["is_kzfp"] = hub.reindex(U_IDX).gene_group.str.contains("Zinc fingers C2H2-type", regex=False).values & \
        T.symbol.str.startswith(("ZNF", "ZSCAN", "ZKSCAN", "ZIK", "ZFP")).values

    # ---------------------------------------------------------------- profile informativeness (tertiles within U)
    um = T.U & T.in_depmap & T.chronos_sd.notna()
    q = T.loc[um, "chronos_sd"].quantile([1 / 3, 2 / 3]).values
    T["sd_tertile_withinU"] = pd.Series(pd.NA, index=U_IDX, dtype="object")
    T.loc[um, "sd_tertile_withinU"] = pd.cut(T.loc[um, "chronos_sd"], [-np.inf, q[0], q[1], np.inf],
                                             labels=["low", "mid", "high"]).astype(str)
    # ---------------------------------------------------------------- core
    T["core"] = (T.n_pubmed_focused <= CORE_MAX_PMIDS) & T.D3_tdark
    T["headline_stratum"] = T.expressed & ~T.chemosensory_epidermal & ~T.tandem_cluster

    # ---------------------------------------------------------------- write U table
    U = T[T.U].copy()
    cols = ["symbol", "entrez_id", "uniprot_ids", "ensembl_gene_id", "location",
            "D1", "n_d1_terms_informative", "n_d1_terms_generic", "n_d1_rows", "d1_symbol_fallback_would_flip",
            "D2", "annotation_score", "D3", "D3_pubmed", "D3_tdark", "n_pubmed_focused", "n_pubmed_all", "tdl",
            "in_depmap", "depmap_column", "tool_mapped_uniprot", "scorable",
            "family_stratum", "chemosensory_epidermal", "tandem_cluster", "n_paralogues_within_1Mb",
            "tandem_cluster_withinspecies", "n_paralogues_within_1Mb_withinspecies", "is_kzfp",
            "has_expression_data", "expr_frac_ge1", "expr_frac_ge1_crispr_lines", "expr_median_log2tpm1",
            "expressed", "expression_stratum",
            "n_obs", "chronos_mean", "chronos_sd", "nan_frac", "n_lines_lt_m0.5", "frac_lines_lt_m0.5",
            "any_dependency", "sd_tertile_withinU", "tool_background", "core", "headline_stratum"]
    U = U[cols].reset_index()
    U = U.sort_values("hgnc_id", key=lambda s: s.str.replace("HGNC:", "").astype(int))
    U.to_csv(OUT_U, sep="\t", index=False, float_format="%.6g")

    # ---------------------------------------------------------------- sensitivity sets (one table)
    D1, D2, D3 = T.D1, T.D2, T.D3
    sets = [
        ("D1", D1), ("D2", D2), ("D3", D3), ("D3_pubmed (<=10 focused PMIDs)", T.D3_pubmed),
        ("D3_tdark", T.D3_tdark),
        ("D1 & D2", D1 & D2), ("D1 & D3", D1 & D3), ("D2 & D3", D2 & D3), ("D1 & D2 & D3", D1 & D2 & D3),
        ("D2 | D3", D2 | D3), ("U = D1 & (D2 | D3)", T.U),
        ("region: D1 only", D1 & ~D2 & ~D3), ("region: D2 only", ~D1 & D2 & ~D3),
        ("region: D3 only", ~D1 & ~D2 & D3), ("region: D1 & D2 only", D1 & D2 & ~D3),
        ("region: D1 & D3 only", D1 & ~D2 & D3), ("region: D2 & D3 only", ~D1 & D2 & D3),
        ("region: D1 & D2 & D3", D1 & D2 & D3), ("region: none", ~D1 & ~D2 & ~D3),
        ("U & core", T.U & T.core), ("D1 & D2 & D3_tdark & <=3 PMIDs (strictest)", D1 & D2 & T.core),
    ]
    rows = []
    for name, m in sets:
        rows.append(dict(set=name, n_genes=int(m.sum()), n_in_depmap=int((m & T.in_depmap).sum()),
                         n_scorable=int((m & T.scorable).sum()),
                         n_scorable_expressed=int((m & T.scorable & T.expressed).sum()),
                         frac_of_universe=round(m.mean(), 4)))
    sens = pd.DataFrame(rows)
    sens.to_csv(OUT_SENS, sep="\t", index=False)

    # ---------------------------------------------------------------- strata counts
    def cnt(mask):
        return int(mask.sum())
    Um = T.U
    strata = []

    def add(name, m):
        strata.append((name, cnt(Um & m), cnt(Um & m & T.in_depmap), cnt(Um & m & T.scorable)))
    add("all U", pd.Series(True, index=U_IDX))
    for v in ["chemosensory_epidermal", "tandem_cluster", "other"]:
        add(f"family = {v}", T.family_stratum == v)
    add("tandem_cluster (any family; all Ensembl paralogue types, primary)", T.tandem_cluster)
    add("tandem_cluster (within_species_paralog/gene_split only; sensitivity)", T.tandem_cluster_withinspecies)
    add("KZFP (C2H2 ZNF group, ZNF/ZSCAN/ZKSCAN/ZFP symbols)", T.is_kzfp)
    add("KZFP & tandem_cluster", T.is_kzfp & T.tandem_cluster)
    for v in ["expressed", "not_expressed", "no_expression_data"]:
        add(f"expression = {v}", T.expression_stratum == v)
    for v in ["low", "mid", "high"]:
        add(f"SD tertile within U = {v}", T.sd_tertile_withinU == v)
    add("any-dependency (>=1% lines < -0.5)", T.any_dependency == True)  # noqa: E712
    add("tool background (NaN fraction < 0.10)", T.tool_background == True)  # noqa: E712
    add("NaN fraction > 0", T.nan_frac > 0)
    add("core (<=3 focused PMIDs & Tdark)", T.core)
    add("headline: expressed & not chemosensory & not tandem", T.headline_stratum)
    add("headline & scorable & any-dependency", T.headline_stratum & T.scorable & (T.any_dependency == True))  # noqa
    strata_df = pd.DataFrame(strata, columns=["stratum", "n_U", "n_U_in_depmap", "n_U_scorable"])

    # ---------------------------------------------------------------- CRITERIA.md
    ck = pd.read_csv(os.path.join(ROOT, "config", "data_checksums.tsv"), sep=r"\s+", header=None,
                     names=["sha256", "path"])
    ckd = dict(zip(ck.path, ck.sha256))
    inp = []
    for f in INPUT_FILES:
        rel = f"data/raw/{f}"
        rec = ckd.get(rel, "")
        act = kn.sha256(os.path.join(ROOT, rel))
        inp.append((rel, rec, "match" if rec == act else f"MISMATCH (actual {act})"))
    for rel in ["results/ids/hgnc_hub.tsv", "results/preregistration/pmid_date_cutoffs.tsv"]:
        inp.append((rel, kn.sha256(os.path.join(ROOT, rel)), "derived (hash at build)"))
    code = [(p, kn.sha256(os.path.join(ROOT, p))) for p in
            ["src/knownness.py", "src/hgnc_hub.py", "scripts/03_build_preregistration.py"]]

    nU = int(T.U.sum())
    n_dep = int((T.U & T.in_depmap).sum())
    n_sc = int((T.U & T.scorable).sum())
    L = []
    L += ["# CRITERIA.md -- pre-registered uncharacterised genes (U)", "",
          "Built by `scripts/03_build_preregistration.py` (criteria code: `src/knownness.py`; IDs: `src/hgnc_hub.py`). "
          "DESIGN.md v2.1 §1. **Not frozen by this script**: the PI freezes (FREEZE.sha256, tag `preregistration-v1`).",
          "No pairwise / co-essentiality quantity was computed; DepMap was used only for single-gene summaries "
          "(mean, SD, NaN fraction, lines < -0.5) and expression single-gene summaries.", "",
          "## Headline counts", "",
          f"- **|U| = {nU:,}** (of {len(T):,} HGNC Approved protein-coding genes)",
          f"- **|U ∩ DepMap| = {n_dep:,}** (DepMap 26Q3 CRISPRGeneEffect column by Entrez)",
          f"- **|U scorable| = {n_sc:,}** (DepMap column and >= 1 HGNC UniProt accession mapped uniquely to it by the "
          "tool's rule, `external/coessentiality/mvp/src/coessential/data.py::build_uniprot_map`)",
          f"- |U ∩ headline stratum (expressed, not chemosensory/epidermal, not tandem)| = "
          f"{int((T.U & T.headline_stratum).sum()):,}; of which scorable {int((T.U & T.headline_stratum & T.scorable).sum()):,}",
          "", "## Exact criteria", "",
          "Universe: HGNC `hgnc_complete_set.txt`, status Approved, locus_group 'protein-coding gene' (19,296).", "",
          f"**D1** (`knownness.d1(gaf, obo, release, acc_map)`; release here: {CURRENT_RELEASE}): zero informative GO "
          "BP/MF terms with evidence in {" + ", ".join(sorted(kn.D1_EVIDENCE)) + "}.",
          "- rows whose qualifier contains the token NOT are removed first; `contributes_to` rows count; IPI rows count "
          "for any non-generic term regardless of the with/from partner;",
          "- aspects P and F only (CC-only does not count); all other evidence codes ignored (HTP/HDA/HMP/HGI/HEP, IEA, "
          "ISS/ISO/ISA/ISM/IGC, IBA/IBD/IKR/IRD, RCA, NAS, ND);",
          "- GO ids normalised with the same release's go-basic.obo (alt_id -> primary; obsolete with a single "
          "replaced_by -> replacement; unresolvable ids kept as-is);",
          "- gene mapping: GAF column-2 UniProtKB accession (isoform suffix stripped) via HGNC `uniprot_ids` plus "
          "Swiss-Prot entries whose HGNC cross-reference names a protein-coding gene; no symbol fallback (identical "
          "rule for every release);",
          f"- generic terms that do not count ({len(kn.GENERIC_TERMS)}):", ""]
    L += [f"  - {k}: {v}" for k, v in kn.GENERIC_TERMS.items()]
    L += ["", "**D2**: UniProt (Swiss-Prot, 2026_03) annotation score <= 2, max over the gene's reviewed entries "
          "(entry -> gene via the entry's HGNC xref, else HGNC uniprot_ids). Genes without a reviewed entry: D2 = False "
          f"({d2st['genes_no_reviewed_entry']} genes).",
          "", "**D3**: <= 10 focused PubMed records (distinct PMIDs linked to the gene's Entrez id in gene2pubmed "
          "(human, 2026-10-29), counting only PMIDs linked to <= 10 distinct human GeneIDs) **or** IDG TDL = Tdark "
          "(TCRD 2023 `PharosTCRD_UniProt_Mapping.tsv`; highest TDL over the gene's accessions).",
          "", "**U = D1 ∩ (D2 ∪ D3)**. No gene is ever removed from U.", "",
          "## Pre-registered strata (§1.4; reporting only)", "",
          "- *Family* (exclusive, in this priority): `chemosensory_epidermal` = gene belongs to one of the HGNC gene "
          "groups below; `tandem_cluster` = >= 2 Ensembl 116 paralogues (any homology type in the BioMart "
          "paralogue export: within_species_paralog, other_paralog, gene_split) whose gene body lies on the same chromosome within 1 Mb (gap between gene "
          "bodies <= 1,000,000 bp; Ensembl 116 coordinates, primary chromosomes; gene -> ENSG via HGNC); `other`. "
          "Sensitivity: tandem counting only within_species_paralog/gene_split pairs is reported as "
          "`tandem_cluster_withinspecies` (it misses most chr19 KZFP and many OR clusters, which Ensembl labels "
          "other_paralog).",
          "- HGNC gene groups used for chemosensory/epidermal (exact names found in the universe, from patterns "
          f"{CHEMO_EPI_GROUP_PATTERNS}):", ""]
    L += [f"  - {g}" for g in groups_used]
    L += ["", f"- *Expression*: expressed = log2(TPM+1) >= {EXPR_MIN_LOG2TPM} in >= {EXPR_MIN_FRAC:.0%} of DepMap "
          f"models with expression data (`OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv`, one default entry per "
          f"model: {exst['n_models']} models, {exst['n_models_in_crispr']} also in CRISPRGeneEffect); genes with no "
          "expression column: `no_expression_data` (counted as not expressed in `headline_stratum`).",
          "- *Profile informativeness*: Chronos SD (ddof=0, as in the tool), number/fraction of lines with effect < "
          "-0.5 (fraction of non-NaN lines), NaN fraction; SD tertiles computed within U ∩ DepMap "
          f"(cut points {q[0]:.4f}, {q[1]:.4f}); any-dependency = >= 1% of lines < -0.5.",
          "- *Core*: <= 3 focused PMIDs and Tdark.",
          "- *Headline stratum*: expressed & not chemosensory/epidermal & not tandem_cluster.", "",
          "## Counts by stratum", "", "| stratum | n U | n U ∩ DepMap | n U scorable |", "|---|---|---|---|"]
    L += [f"| {a} | {b:,} | {c:,} | {d:,} |" for a, b, c, d in strata_df.itertuples(index=False)]
    L += ["", "## Sensitivity sets (D1, D2, D3 alone and overlaps)", "",
          "| set | n genes | n in DepMap | n scorable | n scorable & expressed |", "|---|---|---|---|---|"]
    L += [f"| {r.set} | {r.n_genes:,} | {r.n_in_depmap:,} | {r.n_scorable:,} | {r.n_scorable_expressed:,} |"
          for r in sens.itertuples()]
    L += ["", "## Input files (SHA-256)", "", "| file | SHA-256 (config/data_checksums.tsv) | check |", "|---|---|---|"]
    L += [f"| {a} | `{b}` | {c} |" for a, b, c in inp]
    L += ["", "Code at build time:", ""] + [f"- {p}: `{h}`" for p, h in code]
    L += ["", "## Mapping statistics", "",
          f"- accession map: {acc_st}", f"- D1 current: { {k: v for k, v in d1st.items()} }",
          f"- UniProt entries: {d2st}", f"- expression: {exst}", "",
          "<!-- BEGIN holdout (written by scripts/04_holdout_sizing.py) -->"]
    # keep an existing hold-out block
    hold = ""
    if os.path.exists(OUT_CRIT):
        txt = open(OUT_CRIT).read()
        m = re.search(r"<!-- BEGIN holdout.*?-->\n(.*?)<!-- END holdout -->", txt, re.S)
        if m:
            hold = m.group(1)
    L += [hold.rstrip("\n")] if hold else []
    L += ["<!-- END holdout -->", ""]
    with open(OUT_CRIT, "w") as f:
        f.write("\n".join(L))

    # ---------------------------------------------------------------- cross-check report
    xc_l = ["# Pre-registration cross-checks", "", *xc, "",
            f"- D1 genes: {int(T.D1.sum())}; D2: {int(T.D2.sum())}; D3: {int(T.D3.sum())}; U: {nU}",
            f"- U genes in DepMap but not scorable: {int((T.U & T.in_depmap & ~T.scorable).sum())} "
            f"{list(T.symbol[T.U & T.in_depmap & ~T.scorable])}",
            f"- U genes in DepMap with NaN fraction >= 0.10 (outside the tool background): "
            f"{int((T.U & (T.tool_background == False)).sum())}",  # noqa: E712
            f"- U genes without expression column: {int((T.U & ~T.has_expression_data).sum())}",
            "- Known common essentials (sign check; mean Chronos): " + ", ".join(
                f"{s} {dsum.chronos_mean.get(c, np.nan):.2f}" for s, c in
                [(s, hub.depmap_column[hub.symbol == s].iloc[0]) for s in ["RPL3", "PCNA", "POLR2B", "SNRPD1"]]),
            "- KZFP tandem check: fraction of U KZFPs on chr19 flagged tandem = "
            f"{(T.U & T.is_kzfp & T.location.str.startswith('19') & T.tandem_cluster).sum()}/"
            f"{(T.U & T.is_kzfp & T.location.str.startswith('19')).sum()}",
            "- Olfactory receptor tandem check (all universe ORs): "
            f"{int((T.symbol.str.match(r'^OR\d') & T.tandem_cluster).sum())}/{int(T.symbol.str.match(r'^OR\d').sum())}"]
    with open(OUT_XC, "w") as f:
        f.write("\n".join(xc_l) + "\n")
    print("\n".join(xc_l))
    print(f"|U|={nU} |U∩DepMap|={n_dep} |U scorable|={n_sc}")
    print(strata_df.to_string(index=False))
    print(sens.to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
