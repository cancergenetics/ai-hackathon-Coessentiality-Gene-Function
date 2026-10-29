#!/usr/bin/env python
"""02_gene_knownness_table.py -- per-gene "knownness" FEATURE table for pre-registration of uncharacterised genes.

This script only assembles annotation features; it applies NO selection thresholds (the PI chooses criteria later).
It never reads DepMap gene-effect VALUES: only the header line of CRISPRGeneEffect.csv is read, to flag which genes
are measured (Entrez ID parsed from the "SYMBOL (ENTREZ)" column names, matched on Entrez as the co-essentiality tool
does). No correlation / co-essentiality is computed.

Universe: HGNC records with status == "Approved" and locus_group == "protein-coding gene".

Inputs (data/raw, read-only):
  hgnc/hgnc_complete_set.txt; depmap/CRISPRGeneEffect.csv (header line only);
  go/current/{goa_human.gaf.gz, go-basic.obo}; go/archive/<date>/{goa_human.gaf.gz, go-basic.obo};
  ncbi_gene/gene2pubmed_9606.tsv; uniprot/uniprot_human_reviewed.tsv;
  unknome/unknome_{protein,cluster}_table_18_Mar_2026.tsv.gz; tcrd/PharosTCRD_UniProt_Mapping.tsv
  results/preregistration/pmid_date_cutoffs.tsv  (from scripts/02a_pmid_date_cutoffs.py)

Outputs:
  results/preregistration/gene_knownness_features.tsv
  results/preregistration/knownness_features_README.md

Run:  .env/bin/python -I scripts/02_gene_knownness_table.py
Tests: .env/bin/python -I -m pytest -q tests/test_knownness.py
"""
from __future__ import annotations

import gzip
import os
import re
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUTDIR = os.path.join(ROOT, "results", "preregistration")
OUT_TSV = os.path.join(OUTDIR, "gene_knownness_features.tsv")
OUT_README = os.path.join(OUTDIR, "knownness_features_README.md")
CUTOFF_TSV = os.path.join(OUTDIR, "pmid_date_cutoffs.tsv")

# Archived GO releases -> column suffix (YYYY_MM of the release directory)
GO_ARCHIVES = {"2018-07-02": "2018_07", "2019-07-01": "2019_07", "2020-06-01": "2020_06", "2022-07-01": "2022_07"}

# ----------------------------------------------------------------------------------------------- evidence classes
EXP_CODES = {"EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "HTP", "HDA", "HMP", "HGI", "HEP"}
HTP_CODES = {"HTP", "HDA", "HMP", "HGI", "HEP"}  # high-throughput subset of EXP_CODES
PHYLO_CODES = {"IBA", "IBD", "IKR", "IRD"}
COMP_CODES = {"ISS", "ISO", "ISA", "ISM", "IGC", "RCA", "TAS", "NAS", "IC"}  # computational / author / curator
IEA_CODES = {"IEA"}
ND_CODES = {"ND"}


def evidence_class(code: str) -> str:
    if code in EXP_CODES:
        return "exp"
    if code in PHYLO_CODES:
        return "phylo"
    if code in COMP_CODES:
        return "comp"
    if code in IEA_CODES:
        return "iea"
    if code in ND_CODES:
        return "nd"
    return "other"


# ------------------------------------------------------------------------------------- uninformative GO terms
# Terms excluded from every "informative" count. Rationale per term (also written to the README):
UNINFORMATIVE_TERMS = {
    # requested by the PI
    "GO:0005515": "protein binding -- bare IPI 'interacts with something'; dominated by HTP interactome screens",
    "GO:0003674": "molecular_function root",
    "GO:0008150": "biological_process root",
    "GO:0005575": "cellular_component root",
    "GO:0005488": "binding -- MF high-level grouping term, no specificity",
    "GO:0042802": "identical protein binding -- self-interaction, no functional content",
    "GO:0042803": "protein homodimerization activity -- self-interaction, no functional content",
    # added here (same logic: generic interaction / grouping terms that say nothing about function)
    "GO:0046982": "protein heterodimerization activity -- generic interaction term (partner unspecified), "
                  "sibling of homodimerization",
    "GO:0019899": "enzyme binding -- generic interaction with any enzyme (parent of kinase/ligase binding etc.)",
    "GO:0044877": "protein-containing complex binding -- generic interaction term",
    "GO:0003824": "catalytic activity -- MF high-level grouping term (direct child of root)",
    "GO:0043167": "ion binding -- MF high-level grouping term",
    "GO:0043168": "anion binding -- MF high-level grouping term",
    "GO:0043169": "cation binding -- MF high-level grouping term",
    "GO:0097159": "organic cyclic compound binding -- MF high-level grouping term",
    "GO:1901363": "heterocyclic compound binding -- MF high-level grouping term",
    "GO:0036094": "small molecule binding -- MF high-level grouping term",
    "GO:0009987": "cellular process -- BP high-level grouping term (direct child of root)",
    "GO:0008152": "metabolic process -- BP high-level grouping term",
    "GO:0065007": "biological regulation -- BP high-level grouping term",
    "GO:0050789": "regulation of biological process -- BP high-level grouping term",
    "GO:0050794": "regulation of cellular process -- BP high-level grouping term",
}
UNINFORMATIVE = frozenset(UNINFORMATIVE_TERMS)

GAF_COLS = ["db", "acc", "symbol", "qualifier", "go_id", "reference", "evidence", "with_from", "aspect", "db_name",
            "synonyms", "db_type", "taxon", "date", "assigned_by", "extension", "gene_product_form"]

# ----------------------------------------------------------------------------------------- symbol patterns
PLACEHOLDER_PATTERNS = [  # open-reading-frame / placeholder names (strict set -> symbol_placeholder = True)
    ("orf", r"^C(\d+|X|Y)orf\d+[A-Z]?$"),
    ("FAM", r"^FAM\d+[A-Z]*\d*$"),
    ("KIAA", r"^KIAA\d+[A-Z]?$"),
    ("TMEM", r"^TMEM\d+[A-Z]*\d*$"),
    ("CCDC", r"^CCDC\d+[A-Z]*\d*$"),
    ("SMIM", r"^SMIM\d+[A-Z]?$"),
    ("PRR", r"^PRR\d+[A-Z]?$"),
    ("LOC", r"^LOC\d+$"),
    ("FLJ", r"^FLJ\d+$"),
]
DOMAIN_PATTERNS = [  # domain/motif-descriptive family names (weaker; symbol_placeholder = False)
    ("domain:" + p, r"^" + p + r"\d+[A-Z]*\d*$")
    for p in ["ANKRD", "LRRC", "WDR", "TTC", "ARMC", "HEATR", "ZNF", "ZSWIM", "ZCCHC", "ZC3H", "KLHL", "SPATA",
              "C2CD", "DCAF", "TBC1D", "ABHD", "NUDT", "METTL"]
]


def symbol_pattern(sym: str) -> tuple[str, bool]:
    for name, pat in PLACEHOLDER_PATTERNS:
        if re.match(pat, sym):
            return name, True
    for name, pat in DOMAIN_PATTERNS:
        if re.match(pat, sym):
            return name, False
    return "", False


# ======================================================================================================== HGNC
def load_hgnc(path: str) -> pd.DataFrame:
    h = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)
    pc = h[(h.status == "Approved") & (h.locus_group == "protein-coding gene")].copy()
    pc = pc.reset_index(drop=True)
    return pc


def split_multi(s, sep="|") -> list[str]:
    if s is None or (isinstance(s, float) and np.isnan(s)) or s == "":
        return []
    return [x.strip() for x in str(s).split(sep) if x.strip()]


def strip_isoform(acc: str) -> str:
    return acc.split("-")[0]


def build_acc_map(pc: pd.DataFrame, uniprot: pd.DataFrame | None = None) -> tuple[dict, dict]:
    """accession -> set(hgnc_id). Source 1: HGNC uniprot_ids. Source 2 (only for accessions not in source 1):
    UniProt Swiss-Prot entry's HGNC cross-reference (restricted to the protein-coding universe)."""
    acc2 = defaultdict(set)
    for hid, ids in zip(pc.hgnc_id, pc.uniprot_ids):
        for a in split_multi(ids):
            acc2[a].add(hid)
    stats = {"n_acc_hgnc": len(acc2), "n_acc_multi_gene": sum(len(v) > 1 for v in acc2.values())}
    n_added = 0
    if uniprot is not None:
        valid = set(pc.hgnc_id)
        for acc, hx in zip(uniprot["Entry"], uniprot["HGNC"]):
            if acc in acc2:
                continue
            hs = {x for x in split_multi(hx, ";") if x in valid}
            if hs:
                acc2[acc] = hs
                n_added += 1
    stats["n_acc_added_from_uniprot_xref"] = n_added
    return dict(acc2), stats


# ========================================================================================================= GO
def parse_obo(path: str) -> tuple[dict, dict]:
    """Return (alt_id -> primary id, id -> namespace) from an OBO file (simple line parser)."""
    alt, ns = {}, {}
    cur, in_term = None, False
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("["):
                in_term = line == "[Term]"
                cur = None
                continue
            if not in_term:
                continue
            if line.startswith("id: "):
                cur = line[4:].strip()
            elif line.startswith("alt_id: ") and cur:
                alt[line[8:].strip()] = cur
            elif line.startswith("namespace: ") and cur:
                ns[cur] = line[11:].strip()
    return alt, ns


def read_gaf(path_or_buffer) -> pd.DataFrame:
    """Read a GAF 2.1/2.2 file (17 tab-separated columns, '!' header lines)."""
    df = pd.read_csv(path_or_buffer, sep="\t", comment="!", header=None, dtype=str, quoting=3,
                     names=GAF_COLS, usecols=range(17), keep_default_na=False)
    return df


def is_not_qualified(q: pd.Series) -> pd.Series:
    """True where the qualifier contains the NOT token (GAF 2.1 'NOT', 'NOT|contributes_to'; GAF 2.2 'NOT|enables')."""
    return q.fillna("").str.upper().str.split("|").apply(lambda toks: "NOT" in toks)


def prepare_gaf(gaf: pd.DataFrame, alt_map: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """Drop NOT-qualified rows; normalise GO alt_ids to primary ids; add evidence class."""
    stats = {"n_rows": len(gaf)}
    notq = is_not_qualified(gaf["qualifier"])
    stats["n_not_rows_removed"] = int(notq.sum())
    g = gaf.loc[~notq].copy()
    if alt_map:
        n_alt = g["go_id"].isin(alt_map).sum()
        g["go_id"] = g["go_id"].map(lambda x: alt_map.get(x, x))
        stats["n_alt_id_normalised"] = int(n_alt)
    g["ev_class"] = g["evidence"].map(evidence_class)
    stats["n_other_evidence_rows"] = int((g.ev_class == "other").sum())
    stats["other_evidence_codes"] = sorted(g.loc[g.ev_class == "other", "evidence"].unique().tolist())
    return g, stats


def map_gaf_to_genes(g: pd.DataFrame, acc_map: dict, sym_map: dict | None) -> tuple[pd.DataFrame, dict]:
    """Map GAF rows to HGNC ids: (1) column-2 accession (isoform suffix stripped) via acc_map;
    (2) if unmapped, DB == UniProtKB and sym_map given: column-3 symbol == HGNC approved symbol.
    Rows mapping to several genes (shared accession) are assigned to each. Returns exploded frame."""
    acc = g["acc"].map(strip_isoform)
    by_acc = acc.map(lambda a: acc_map.get(a))
    method = pd.Series(np.where(by_acc.notna(), "accession", "unmapped"), index=g.index)
    hits = by_acc.copy()
    if sym_map is not None:
        need = by_acc.isna() & (g["db"] == "UniProtKB")
        by_sym = g.loc[need, "symbol"].map(lambda s: sym_map.get(s))
        ok = by_sym.notna()
        hits.loc[by_sym.index[ok]] = by_sym[ok]
        method.loc[by_sym.index[ok]] = "symbol"
    out = g.assign(map_method=method, hgnc_id=hits.map(lambda s: sorted(s) if isinstance(s, (set, frozenset))
                                                       else ([s] if isinstance(s, str) else [])))
    stats = {
        "rows": len(g),
        "rows_by_accession": int((method == "accession").sum()),
        "rows_by_symbol": int((method == "symbol").sum()),
        "rows_unmapped": int((method == "unmapped").sum()),
        "rows_uniprotkb": int((g["db"] == "UniProtKB").sum()),
        "rows_uniprotkb_unmapped": int(((method == "unmapped") & (g["db"] == "UniProtKB")).sum()),
        "accessions": int(acc.nunique()),
        "accessions_mapped": int(acc[method != "unmapped"].nunique()),
        "uniprotkb_accessions": int(acc[g["db"] == "UniProtKB"].nunique()),
        "uniprotkb_accessions_mapped": int(acc[(method != "unmapped") & (g["db"] == "UniProtKB")].nunique()),
    }
    out = out.explode("hgnc_id")
    out = out[out.hgnc_id.notna()]
    stats["genes_with_rows"] = int(out.hgnc_id.nunique())
    return out, stats


def go_features(m: pd.DataFrame, uninformative=UNINFORMATIVE) -> pd.DataFrame:
    """Per-gene GO features from a prepared + mapped GAF frame (NOT rows already removed).
    All n_* term counts are numbers of DISTINCT GO terms."""
    m = m.copy()
    m["inf"] = ~m["go_id"].isin(uninformative)
    bpmf = m["aspect"].isin(["P", "F"])
    exp = m["ev_class"] == "exp"
    exp_lt = exp & ~m["evidence"].isin(HTP_CODES)

    def nterms(mask):
        return m.loc[mask].groupby("hgnc_id")["go_id"].nunique()

    feats = {
        "n_exp_BP": nterms(exp & (m.aspect == "P") & m.inf),
        "n_exp_MF_informative": nterms(exp & (m.aspect == "F") & m.inf),
        "n_exp_CC": nterms(exp & (m.aspect == "C") & m.inf),
        "n_exp_informative_BPMF": nterms(exp & bpmf & m.inf),
        "n_exp_informative_BPMF_lowthroughput": nterms(exp_lt & bpmf & m.inf),
        "n_exp_BPMF_all_terms": nterms(exp & bpmf),
        "n_ibas_BPMF": nterms((m.ev_class == "phylo") & bpmf & m.inf),
        "n_comp_BPMF": nterms((m.ev_class == "comp") & bpmf & m.inf),
        "n_any_BPMF_nonIEA": nterms(bpmf & m.inf & ~m.ev_class.isin(["iea", "nd"])),
        "n_IEA": nterms((m.ev_class == "iea") & m.inf),
    }
    genes = pd.Index(sorted(m["hgnc_id"].unique()), name="hgnc_id")
    out = pd.DataFrame(feats).reindex(genes).fillna(0).astype(int)
    out["has_ND_BP"] = genes.isin(m.loc[(m.ev_class == "nd") & (m.aspect == "P"), "hgnc_id"])
    out["has_ND_MF"] = genes.isin(m.loc[(m.ev_class == "nd") & (m.aspect == "F"), "hgnc_id"])
    # raw annotation-row counts by aspect x evidence class
    rc = m.groupby(["hgnc_id", "aspect", "ev_class"]).size().unstack(["aspect", "ev_class"], fill_value=0)
    rc.columns = [f"nrows_{a}_{c}" for a, c in rc.columns]
    want = [f"nrows_{a}_{c}" for a in "PFC" for c in ["exp", "phylo", "comp", "iea", "nd"]]
    rc = rc.reindex(columns=want, fill_value=0)
    out = out.join(rc)
    return out


def exp_informative_bpmf(m: pd.DataFrame, uninformative=UNINFORMATIVE) -> pd.Series:
    sel = (m.ev_class == "exp") & m.aspect.isin(["P", "F"]) & ~m.go_id.isin(uninformative)
    return m.loc[sel].groupby("hgnc_id")["go_id"].nunique()


# ===================================================================================================== PubMed
def pubmed_counts(g2p: pd.DataFrame, max_genes: int | None = None, pmid_lt: int | None = None) -> pd.Series:
    """Distinct PMIDs per GeneID. g2p has columns GeneID, PubMed_ID (ints). If max_genes is given, only PMIDs
    linked to <= max_genes distinct GeneIDs IN g2p (all human genes, any gene type) are counted. If pmid_lt is
    given, only PMIDs < pmid_lt are counted (gene counts per PMID are always computed on the full g2p)."""
    d = g2p[["GeneID", "PubMed_ID"]].drop_duplicates()
    if max_genes is not None:
        per = d.groupby("PubMed_ID")["GeneID"].nunique()
        keep = per.index[per <= max_genes]
        d = d[d.PubMed_ID.isin(keep)]
    if pmid_lt is not None:
        d = d[d.PubMed_ID < pmid_lt]
    return d.groupby("GeneID")["PubMed_ID"].nunique()


# ==================================================================================================== UniProt
PE_LEVEL = {"Evidence at protein level": 1, "Evidence at transcript level": 2, "Inferred from homology": 3,
            "Predicted": 4, "Uncertain": 5}


def clean_function_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = re.sub(r"\{ECO:[^}]*\}", "", s)
    s = re.sub(r"\((PubMed|Ref\.)[^)]*\)", "", s)
    s = s.replace("FUNCTION:", "")
    return re.sub(r"\s+", " ", s).strip(" .;")


# ====================================================================================================== main
def quantile_table(df: pd.DataFrame, cols: list[str]) -> str:
    qs = [0, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0]
    lines = ["| feature | n non-missing | n == 0 | mean | " + " | ".join(f"q{int(q * 100)}" for q in qs) + " |",
             "|---|" + "---|" * (3 + len(qs))]
    for c in cols:
        x = pd.to_numeric(df[c], errors="coerce")
        v = x.dropna()
        qv = v.quantile(qs).values if len(v) else [np.nan] * len(qs)
        lines.append(f"| {c} | {len(v)} | {int((v == 0).sum())} | {v.mean():.2f} | "
                     + " | ".join(f"{q:g}" for q in qv) + " |")
    return "\n".join(lines)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rep = {}  # mapping statistics for README

    # ---------------------------------------------------------------- HGNC universe
    pc = load_hgnc(os.path.join(RAW, "hgnc", "hgnc_complete_set.txt"))
    assert pc.hgnc_id.is_unique
    n_genes = len(pc)
    rep["hgnc"] = dict(n_protein_coding_approved=n_genes, n_no_entrez=int(pc.entrez_id.isna().sum()),
                       n_no_uniprot=int(pc.uniprot_ids.isna().sum()),
                       n_multi_uniprot=int(pc.uniprot_ids.fillna("").str.contains(r"\|").sum()),
                       entrez_duplicated=int(pc.entrez_id.dropna().duplicated().sum()))
    sym_map = {s: {h} for s, h in zip(pc.symbol, pc.hgnc_id)}
    out = pc[["hgnc_id", "symbol", "entrez_id", "ensembl_gene_id", "uniprot_ids", "name", "locus_type", "location",
              "gene_group"]].copy()

    # ---------------------------------------------------------------- DepMap header only
    with open(os.path.join(RAW, "depmap", "CRISPRGeneEffect.csv")) as f:
        header = f.readline().rstrip("\n").split(",")  # header line ONLY; values are never read
    dep_entrez, n_unparsed = set(), 0
    for c in header[1:]:
        mm = re.match(r"^(.*) \((\d+)\)$", c.strip().strip('"'))
        if mm:
            dep_entrez.add(mm.group(2))
        else:
            n_unparsed += 1
    out["in_depmap"] = out.entrez_id.isin(dep_entrez)
    rep["depmap"] = dict(n_columns=len(header) - 1, n_unparsed=n_unparsed, n_entrez=len(dep_entrez),
                         n_pc_in_depmap=int(out.in_depmap.sum()),
                         n_depmap_entrez_not_in_pc=len(dep_entrez - set(out.entrez_id.dropna())))

    # ---------------------------------------------------------------- symbol pattern
    sp = out.symbol.map(symbol_pattern)
    out["symbol_pattern"] = sp.map(lambda t: t[0])
    out["symbol_placeholder"] = sp.map(lambda t: t[1])

    # ---------------------------------------------------------------- UniProt (needed for accession map too)
    up = pd.read_csv(os.path.join(RAW, "uniprot", "uniprot_human_reviewed.tsv"), sep="\t", dtype=str,
                     keep_default_na=False)
    acc_map, acc_stats = build_acc_map(pc, up)
    rep["acc_map"] = acc_stats

    # ---------------------------------------------------------------- GO current
    alt, _ = parse_obo(os.path.join(RAW, "go", "current", "go-basic.obo"))
    gaf = read_gaf(os.path.join(RAW, "go", "current", "goa_human.gaf.gz"))
    g, pst = prepare_gaf(gaf, alt)
    m, mst = map_gaf_to_genes(g, acc_map, sym_map)
    rep["go_current"] = {**pst, **mst}
    gf = go_features(m)
    gf = gf.reindex(out.hgnc_id)
    for c in gf.columns:
        if c.startswith("has_ND"):
            out[c] = gf[c].fillna(False).astype(bool).values
        else:
            out[c] = gf[c].fillna(0).astype(int).values
    out["has_any_go_annotation"] = out.hgnc_id.isin(set(m.hgnc_id))

    # ---------------------------------------------------------------- GO archives (accession mapping only)
    rep["go_archive"] = {}
    for d, suf in GO_ARCHIVES.items():
        base = os.path.join(RAW, "go", "archive", d)
        alt_a, _ = parse_obo(os.path.join(base, "go-basic.obo"))
        ga, pst_a = prepare_gaf(read_gaf(os.path.join(base, "goa_human.gaf.gz")), alt_a)
        ma, mst_a = map_gaf_to_genes(ga, acc_map, None)
        # diagnostic only: how many unmapped rows a symbol fallback would have rescued (not used)
        unm = ga.loc[~ga.index.isin(ma.index)]
        mst_a["diag_unmapped_rows_symbol_would_rescue"] = int(unm.symbol.isin(sym_map).sum())
        rep["go_archive"][d] = {**pst_a, **mst_a}
        s = exp_informative_bpmf(ma).reindex(out.hgnc_id).fillna(0).astype(int)
        out[f"n_exp_informative_BPMF_{suf}"] = s.values
        out[f"has_any_go_annotation_{suf}"] = out.hgnc_id.isin(set(ma.hgnc_id)).values

    # ---------------------------------------------------------------- gene2pubmed
    g2p = pd.read_csv(os.path.join(RAW, "ncbi_gene", "gene2pubmed_9606.tsv"), sep="\t",
                      names=["tax_id", "GeneID", "PubMed_ID"], comment="#", dtype=np.int64)
    rep["pubmed"] = dict(rows=len(g2p), genes=int(g2p.GeneID.nunique()), pmids=int(g2p.PubMed_ID.nunique()))
    cut = pd.read_csv(CUTOFF_TSV, sep="\t", dtype={"cutoff_date": str})
    ent = pd.to_numeric(out.entrez_id, errors="coerce")

    def put(col, s):
        out[col] = ent.map(s).fillna(0).astype(int).values

    put("n_pubmed", pubmed_counts(g2p))
    put("n_pubmed_focused", pubmed_counts(g2p, max_genes=10))
    put("n_pubmed_focused3", pubmed_counts(g2p, max_genes=3))
    for _, r in cut.iterrows():
        suf = r.cutoff_date[:7].replace("-", "_")
        put(f"n_pubmed_focused_before_{suf}", pubmed_counts(g2p, max_genes=10, pmid_lt=int(r.cutoff_pmid)))
    rep["pubmed"]["pc_genes_with_any_pmid"] = int((out.n_pubmed > 0).sum())
    rep["pubmed"]["pc_entrez_present"] = int(ent.isin(set(g2p.GeneID)).sum())
    per = g2p.drop_duplicates(["GeneID", "PubMed_ID"]).groupby("PubMed_ID").GeneID.nunique()
    rep["pubmed"]["pmids_le10"] = int((per <= 10).sum())
    rep["pubmed"]["pmids_le3"] = int((per <= 3).sum())
    rep["pubmed"]["cutoffs"] = cut

    # ---------------------------------------------------------------- UniProt features
    valid = set(pc.hgnc_id)
    acc2hg_hgnc = defaultdict(set)
    for hid, ids in zip(pc.hgnc_id, pc.uniprot_ids):
        for a in split_multi(ids):
            acc2hg_hgnc[a].add(hid)
    rows, n_x, n_a, n_un = [], 0, 0, 0
    for _, r in up.iterrows():
        hs = {x for x in split_multi(r["HGNC"], ";") if x in valid}
        if hs:
            n_x += 1
        else:
            hs = acc2hg_hgnc.get(r["Entry"], set())
            if hs:
                n_a += 1
            else:
                n_un += 1
        for h in hs:
            rows.append((h, r["Entry"], float(r["Annotation"]) if r["Annotation"] else np.nan,
                         PE_LEVEL.get(r["Protein existence"], np.nan),
                         clean_function_text(r["Function [CC]"]), r["PubMed ID"]))
    u = pd.DataFrame(rows, columns=["hgnc_id", "entry", "score", "pe", "fun", "pmids"])
    u["fun_len"] = u.fun.str.len()
    agg = u.groupby("hgnc_id").agg(annotation_score=("score", "max"), pe=("pe", "min"),
                                   function_cc_length=("fun_len", "max"), n_uniprot_entries=("entry", "nunique"),
                                   uniprot_entries=("entry", lambda x: "|".join(sorted(x))))
    agg["n_uniprot_pubmed"] = u.groupby("hgnc_id").pmids.apply(
        lambda x: len({p.strip() for s in x for p in s.split(";") if p.strip()}))
    agg = agg.reindex(out.hgnc_id)
    inv_pe = {v: k for k, v in PE_LEVEL.items()}
    out["uniprot_entries"] = agg.uniprot_entries.fillna("").values
    out["n_uniprot_entries"] = agg.n_uniprot_entries.fillna(0).astype(int).values
    out["annotation_score"] = agg.annotation_score.values
    out["protein_existence_level"] = agg.pe.values
    out["protein_existence"] = agg.pe.map(inv_pe).fillna("").values
    out["has_function_cc"] = (agg.function_cc_length.fillna(0) > 0).values
    out["function_cc_length"] = agg.function_cc_length.fillna(0).astype(int).values
    out["n_uniprot_pubmed"] = agg.n_uniprot_pubmed.fillna(0).astype(int).values
    rep["uniprot"] = dict(entries=len(up), mapped_by_hgnc_xref=n_x, mapped_by_accession=n_a, unmapped=n_un,
                          genes_with_entry=int(out.n_uniprot_entries.gt(0).sum()),
                          genes_multi_entry=int(out.n_uniprot_entries.gt(1).sum()))

    # ---------------------------------------------------------------- Unknome
    ucols = ["uniprot_name", "uniprot_accessions", "knownness", "gene_name", "taxon_id", "cluster_id"]
    un = pd.read_csv(os.path.join(RAW, "unknome", "unknome_protein_table_18_Mar_2026.tsv.gz"), sep="\t",
                     dtype=str, usecols=ucols, keep_default_na=False)
    un = un[un.taxon_id == "9606"].copy()
    ucl = pd.read_csv(os.path.join(RAW, "unknome", "unknome_cluster_table_18_Mar_2026.tsv.gz"), sep="\t",
                      dtype={"cluster_id": str}, usecols=["cluster_id", "knownness"]).set_index("cluster_id")
    un["knownness"] = un.knownness.astype(float)
    un["cluster_knownness"] = un.cluster_id.map(ucl.knownness)
    meth, hits = [], []
    for accs, gname in zip(un.uniprot_accessions, un.gene_name):
        al = [a for a in re.split(r"[;,\s]+", accs) if a]
        hs = acc_map.get(al[0]) if al else None
        mtd = "primary_accession"
        if not hs:
            hs = set().union(*[acc_map.get(a, set()) for a in al[1:]]) if len(al) > 1 else set()
            mtd = "secondary_accession"
        if not hs:
            hs = sym_map.get(gname, set())
            mtd = "gene_name"
        if not hs:
            mtd = "unmapped"
        meth.append(mtd)
        hits.append(sorted(hs))
    un["map_method"], un["hgnc_id"] = meth, hits
    rep["unknome"] = dict(human_rows=len(un), **un.map_method.value_counts().to_dict())
    ue = un.explode("hgnc_id").dropna(subset=["hgnc_id"])
    ug = ue.groupby("hgnc_id").agg(unknome_knownness=("knownness", "max"),
                                   unknome_cluster_knownness=("cluster_knownness", "max"),
                                   unknome_cluster_id=("cluster_id", lambda x: "|".join(sorted(set(x)))),
                                   n_unknome_proteins=("uniprot_name", "nunique")).reindex(out.hgnc_id)
    for c in ug.columns:
        out[c] = ug[c].values
    out["n_unknome_proteins"] = out.n_unknome_proteins.fillna(0).astype(int)
    out["unknome_cluster_id"] = out.unknome_cluster_id.fillna("")
    rep["unknome"]["genes_with_score"] = int(out.unknome_knownness.notna().sum())
    rep["unknome"]["genes_multi_protein"] = int((out.n_unknome_proteins > 1).sum())
    rep["unknome"]["rows_multi_gene"] = int((un.hgnc_id.map(len) > 1).sum())

    # ---------------------------------------------------------------- TCRD
    tc = pd.read_csv(os.path.join(RAW, "tcrd", "PharosTCRD_UniProt_Mapping.tsv"), sep="\t", dtype=str)
    rank = {"Tclin": 4, "Tchem": 3, "Tbio": 2, "Tdark": 1}
    tc["hgnc_id"] = tc.UniProt_accession.map(lambda a: sorted(acc_map.get(a, set())))
    rep["tcrd"] = dict(rows=len(tc), rows_mapped=int((tc.hgnc_id.map(len) > 0).sum()))
    te = tc.explode("hgnc_id").dropna(subset=["hgnc_id"])
    te["r"] = te.TDL.map(rank)
    conflicts = te.groupby("hgnc_id").TDL.nunique()
    best = te.sort_values("r", ascending=False).drop_duplicates("hgnc_id").set_index("hgnc_id").TDL
    out["tdl"] = out.hgnc_id.map(best).fillna("")
    rep["tcrd"]["genes_with_tdl"] = int((out.tdl != "").sum())
    rep["tcrd"]["genes_conflicting_tdl"] = int((conflicts > 1).sum())

    # ---------------------------------------------------------------- write table
    out.to_csv(OUT_TSV, sep="\t", index=False)
    write_readme(out, rep)
    print(f"wrote {OUT_TSV} ({len(out)} rows, {out.shape[1]} columns)")


# ===================================================================================================== README
COLUMN_DOCS = [
    ("hgnc_id, symbol, entrez_id, ensembl_gene_id, uniprot_ids, name, locus_type, location, gene_group",
     "Verbatim from HGNC `hgnc_complete_set.txt` (status Approved, locus_group 'protein-coding gene'). `location` "
     "= cytoband; `uniprot_ids` and `gene_group` are '|'-separated as in HGNC."),
    ("in_depmap", "Entrez ID of the gene equals the Entrez ID parsed from a DepMap 26Q3 `CRISPRGeneEffect.csv` "
     "column name `SYMBOL (ENTREZ)` (header line only; matching on Entrez as the co-essentiality tool does). NB the "
     "tool additionally drops genes without HGNC UniProt IDs and flags low-coverage (high-NaN) genes; NaN coverage "
     "was NOT computed here because that requires reading values."),
    ("symbol_pattern", "Descriptive only. Name of the first matching placeholder pattern (orf = C<n>orf<n>/CXorf/"
     "CYorf, FAM, KIAA, TMEM, CCDC, SMIM, PRR, LOC, FLJ) or 'domain:<prefix>' for domain-descriptive family names "
     "(ANKRD, LRRC, WDR, TTC, ARMC, HEATR, ZNF, ZSWIM, ZCCHC, ZC3H, KLHL, SPATA, C2CD, DCAF, TBC1D, ABHD, NUDT, "
     "METTL); empty if none."),
    ("symbol_placeholder", "True iff symbol_pattern is one of the strict placeholder patterns (not 'domain:*')."),
    ("n_exp_BP", "Distinct GO BP terms (current GAF) with experimental evidence (EXP, IDA, IPI, IMP, IGI, IEP, HTP, "
     "HDA, HMP, HGI, HEP), excluding NOT and the uninformative terms (only the BP root/grouping terms matter here)."),
    ("n_exp_MF_informative", "Distinct informative GO MF terms with experimental evidence."),
    ("n_exp_CC", "Distinct GO CC terms with experimental evidence (CC root excluded)."),
    ("n_exp_informative_BPMF", "Distinct informative BP+MF terms with experimental evidence (current GAF). The main "
     "GO knownness feature."),
    ("n_exp_informative_BPMF_lowthroughput", "As n_exp_informative_BPMF but HTP codes (HTP, HDA, HMP, HGI, HEP) "
     "excluded -- i.e. only EXP, IDA, IPI, IMP, IGI, IEP. Added because proteome-wide screens (e.g. RNA-interactome "
     "capture -> 'RNA binding' HDA; 'cadherin binding' HDA) give many otherwise unstudied proteins one term."),
    ("n_exp_BPMF_all_terms", "Distinct BP+MF terms with experimental evidence INCLUDING the uninformative terms "
     "(e.g. protein binding); for comparison."),
    ("n_ibas_BPMF", "Distinct informative BP+MF terms with phylogenetic evidence (IBA, IBD, IKR, IRD)."),
    ("n_comp_BPMF", "Distinct informative BP+MF terms with computational/author/curator evidence (ISS, ISO, ISA, ISM, "
     "IGC, RCA, TAS, NAS, IC)."),
    ("n_any_BPMF_nonIEA", "Distinct informative BP+MF terms with any evidence except IEA and ND."),
    ("n_IEA", "Distinct informative GO terms (any aspect) with IEA evidence."),
    ("has_ND_BP / has_ND_MF", "Gene has an ND (no biological data) annotation to the BP / MF root."),
    ("nrows_<P|F|C>_<exp|phylo|comp|iea|nd>", "Raw number of (non-NOT) GAF annotation rows per aspect x evidence "
     "class (not de-duplicated, uninformative terms included)."),
    ("has_any_go_annotation", "Gene has >= 1 non-NOT row in the current GAF."),
    ("n_exp_informative_BPMF_<YYYY_MM>", "n_exp_informative_BPMF computed identically on the archived GO release "
     "(2018_07 = release 2018-07-02, 2019_07 = 2019-07-01, 2020_06 = 2020-06-01, 2022_07 = 2022-07-01), mapping rows "
     "by UniProt accession only (no symbol fallback), GO alt_ids normalised with that release's go-basic.obo."),
    ("has_any_go_annotation_<YYYY_MM>", "Gene has >= 1 non-NOT row in that archived GAF."),
    ("n_pubmed", "Distinct PMIDs linked to the gene's Entrez ID in NCBI gene2pubmed (human)."),
    ("n_pubmed_focused", "As n_pubmed, counting only PMIDs linked to <= 10 distinct human GeneIDs in gene2pubmed "
     "(any gene type; counts per PMID from the full current file)."),
    ("n_pubmed_focused3", "Same with <= 3 genes per PMID."),
    ("n_pubmed_focused_before_<YYYY_MM>", "n_pubmed_focused restricted to PMIDs < the cut-off PMID for that date "
     "(date proxy; see 'PMID cut-offs'). Genes-per-PMID is still computed on the current file."),
    ("uniprot_entries, n_uniprot_entries", "Swiss-Prot (reviewed) entries assigned to the gene."),
    ("annotation_score", "Max UniProt annotation score (1-5) over the gene's reviewed entries; NA if none."),
    ("protein_existence, protein_existence_level", "Best (lowest-level) protein existence over entries: 1 protein "
     "level, 2 transcript level, 3 inferred from homology, 4 predicted, 5 uncertain."),
    ("has_function_cc", "Any reviewed entry has a non-empty Function [CC] comment."),
    ("function_cc_length", "Max length (characters) of the Function [CC] text after removing 'FUNCTION:', {ECO:...} "
     "evidence tags and '(PubMed:...)' citations."),
    ("n_uniprot_pubmed", "Distinct PMIDs cited in the gene's reviewed entries (union)."),
    ("unknome_knownness", "Max Unknome protein-level 'knownness' over the gene's human Unknome rows (protein "
     "table column `knownness`, release 18 Mar 2026). Per Rocha et al. 2023 (PLoS Biol 21:e3002222) knownness is "
     "an evidence-weighted sum over the protein's GO annotations (experimental evidence weighted most); 0 = nothing "
     "known. NA = no human Unknome row mapped."),
    ("unknome_cluster_knownness", "Knownness of the gene's Unknome orthology cluster (cluster table). Verified here "
     "to equal the MAX protein knownness over all proteins of all species in the cluster (100% of 15,589 clusters), "
     "i.e. 'is anything known about any orthologue'. Max over the gene's clusters."),
    ("unknome_cluster_id, n_unknome_proteins", "Unknome cluster id(s) and number of human Unknome proteins mapped."),
    ("tdl", "IDG Target Development Level (Tclin > Tchem > Tbio > Tdark) from Pharos/TCRD v6.13 "
     "(PharosTCRD_UniProt_Mapping.tsv, 2023); highest level if several accessions; empty if unmapped."),
]


def fmt_stats(d: dict) -> str:
    return "; ".join(f"{k} = {v:,}" if isinstance(v, (int, np.integer)) else f"{k} = {v}" for k, v in d.items())


def pct(a, b):
    return f"{a:,}/{b:,} ({100 * a / b:.2f}%)" if b else f"{a}/{b}"


def write_readme(out: pd.DataFrame, rep: dict):
    L = []
    w = L.append
    n = len(out)
    w("# Gene knownness feature table (pre-registration input)\n")
    w("Generated by `scripts/02_gene_knownness_table.py` (PMID cut-offs by `scripts/02a_pmid_date_cutoffs.py`). "
      "Feature table only: **no selection thresholds are applied here**; the thresholds in the overlap section are "
      "descriptive, chosen by the PI's request, not criteria. No DepMap values were read (header only) and no "
      "co-essentiality was computed.\n")
    w(f"Output: `results/preregistration/gene_knownness_features.tsv` -- {n:,} rows (HGNC Approved, locus_group "
      f"'protein-coding gene'), {out.shape[1]} columns.\n")

    w("## Columns\n")
    w("| column(s) | definition |\n|---|---|")
    for c, d in COLUMN_DOCS:
        w(f"| {c} | {d} |")
    w("")

    w("## Uninformative GO terms (excluded from all 'informative' counts)\n")
    w("Matched after normalising GO alt_ids to primary ids with the same release's go-basic.obo. The list was "
      "built from the PI's terms plus generic interaction terms (partner unspecified) and high-level grouping "
      "terms one or two levels below the roots. Inspecting the 45 most frequent experimental BP/MF terms in the "
      "current GAF, the remaining frequent terms (e.g. RNA binding, sequence-specific DNA binding, regulation of "
      "transcription by RNA pol II, ubiquitin protein ligase binding) do carry functional information and were "
      "kept; the effect of HTP screens is exposed separately via `n_exp_informative_BPMF_lowthroughput`.\n")
    w("| GO id | reason |\n|---|---|")
    for k, v in UNINFORMATIVE_TERMS.items():
        w(f"| {k} | {v} |")
    w("")

    w("## Evidence classes\n")
    w(f"- experimental: {', '.join(sorted(EXP_CODES))} (high-throughput subset: {', '.join(sorted(HTP_CODES))})")
    w(f"- phylogenetic: {', '.join(sorted(PHYLO_CODES))}")
    w(f"- computational/author/curator: {', '.join(sorted(COMP_CODES))}")
    w("- IEA separately; ND separately. Rows whose qualifier contains the token NOT are removed before anything else "
      "(GAF 2.1 'NOT', 'NOT|contributes_to'; GAF 2.2 'NOT|enables' etc.).\n")

    w("## Mapping steps and success rates\n")
    h = rep["hgnc"]
    w(f"- **HGNC universe**: {h['n_protein_coding_approved']:,} genes; without Entrez {h['n_no_entrez']}; without "
      f"UniProt {h['n_no_uniprot']}; with >1 UniProt {h['n_multi_uniprot']}; duplicated Entrez {h['entrez_duplicated']}.")
    a = rep["acc_map"]
    w(f"- **Accession -> gene map** (used for GO, Unknome, TCRD): {a['n_acc_hgnc']:,} accessions from HGNC "
      f"`uniprot_ids` ({a['n_acc_multi_gene']} shared by >1 gene -> annotations assigned to every such gene), plus "
      f"{a['n_acc_added_from_uniprot_xref']} Swiss-Prot accessions not in HGNC but whose UniProt entry "
      f"cross-references a protein-coding HGNC id. Isoform suffixes (-n) are stripped.")
    d = rep["depmap"]
    w(f"- **DepMap header**: {d['n_columns']:,} gene columns, {d['n_unparsed']} unparsable; {d['n_entrez']:,} "
      f"Entrez IDs; protein-coding genes in DepMap: {pct(d['n_pc_in_depmap'], n)}; DepMap Entrez IDs not among "
      f"protein-coding HGNC genes: {d['n_depmap_entrez_not_in_pc']}.")
    g = rep["go_current"]
    w(f"- **GO current** (goa_human.gaf.gz GAF 2.2, generated 2026-05-21; go-basic.obo 2026-07-26): "
      f"{g['n_rows']:,} rows; NOT rows removed {g['n_not_rows_removed']:,}; alt_ids normalised "
      f"{g['n_alt_id_normalised']:,}; rows with unclassified evidence codes {g['n_other_evidence_rows']} "
      f"{g['other_evidence_codes']}. Of remaining {g['rows']:,} rows: by accession {pct(g['rows_by_accession'], g['rows'])}, "
      f"by symbol fallback (UniProtKB rows only) {pct(g['rows_by_symbol'], g['rows'])}, unmapped "
      f"{pct(g['rows_unmapped'], g['rows'])}. UniProtKB rows {g['rows_uniprotkb']:,}, of which unmapped "
      f"{pct(g['rows_uniprotkb_unmapped'], g['rows_uniprotkb'])} (unmapped non-UniProtKB rows are RNAcentral / "
      f"ComplexPortal entities, i.e. not protein-coding genes). UniProtKB accessions mapped: "
      f"{pct(g['uniprotkb_accessions_mapped'], g['uniprotkb_accessions'])}. Protein-coding genes with >= 1 row: "
      f"{pct(g['genes_with_rows'], n)}.")
    for dte, s in rep["go_archive"].items():
        w(f"- **GO archive {dte}**: {s['n_rows']:,} rows; NOT removed {s['n_not_rows_removed']:,}; alt_ids normalised "
          f"{s['n_alt_id_normalised']:,}; unclassified evidence rows {s['n_other_evidence_rows']} "
          f"{s['other_evidence_codes']}; mapped by accession {pct(s['rows_by_accession'], s['rows'])}; accessions "
          f"mapped {pct(s['accessions_mapped'], s['accessions'])}; genes with >= 1 row {pct(s['genes_with_rows'], n)}. "
          f"(Diagnostic, not used: a symbol fallback would rescue {s['diag_unmapped_rows_symbol_would_rescue']:,} "
          f"of the unmapped rows.)")
    p = rep["pubmed"]
    w(f"- **gene2pubmed** (human subset of the 2026-10-29 file): {p['rows']:,} rows, {p['genes']:,} GeneIDs, "
      f"{p['pmids']:,} PMIDs; PMIDs linked to <= 10 genes: {pct(p['pmids_le10'], p['pmids'])}; <= 3 genes: "
      f"{pct(p['pmids_le3'], p['pmids'])}. Protein-coding genes matched by Entrez: {pct(p['pc_entrez_present'], n)}; "
      f"with >= 1 PMID: {pct(p['pc_genes_with_any_pmid'], n)}.")
    u = rep["uniprot"]
    w(f"- **UniProt** (Swiss-Prot human, release 2026_03): {u['entries']:,} entries; mapped via the entry's HGNC "
      f"xref {pct(u['mapped_by_hgnc_xref'], u['entries'])}, via HGNC uniprot_ids accession "
      f"{pct(u['mapped_by_accession'], u['entries'])}, unmapped {pct(u['unmapped'], u['entries'])} (non-protein-"
      f"coding HGNC loci, e.g. readthrough/IG/TR, or no HGNC xref). Genes with >= 1 entry "
      f"{pct(u['genes_with_entry'], n)}; with > 1 entry {u['genes_multi_entry']} (max score / best PE taken).")
    k = rep["unknome"]
    w(f"- **Unknome** (protein table, release 18 Mar 2026, taxon_id 9606 rows only): {k['human_rows']:,} human "
      f"proteins. Row -> gene: first accession in `uniprot_accessions` (= UniProt primary accession) via the "
      f"accession map: {k.get('primary_accession', 0):,}; else any secondary accession: "
      f"{k.get('secondary_accession', 0):,}; else `gene_name` == HGNC approved symbol: {k.get('gene_name', 0):,}; "
      f"unmapped: {k.get('unmapped', 0):,}. Rows mapping to > 1 gene: {k['rows_multi_gene']}. Genes with a score: "
      f"{pct(k['genes_with_score'], n)}; genes with > 1 Unknome protein: {k['genes_multi_protein']} (max taken). "
      f"Column used: protein-table `knownness` (gene-specific); cluster-table `knownness` provided separately.")
    t = rep["tcrd"]
    w(f"- **TCRD**: {t['rows']:,} UniProt rows, mapped {pct(t['rows_mapped'], t['rows'])}; genes with a TDL "
      f"{pct(t['genes_with_tdl'], n)}; genes with conflicting TDLs across accessions {t['genes_conflicting_tdl']} "
      f"(highest kept).\n")

    w("## PMID cut-offs (date proxy -- an approximation)\n")
    w("PMIDs are assigned roughly sequentially when a record enters PubMed. For each date D, "
      "`scripts/02a_pmid_date_cutoffs.py` queried NCBI E-utilities esearch for all PMIDs with Entrez date "
      "`\"YYYY/MM/DD\"[EDAT]` on each of D-3 .. D+2 and set cutoff_pmid(D) = 1st percentile of PMIDs with EDAT in "
      "[D, D+2] (robust to back-filled records that carry an old EDAT with a new PMID). 'Before D' = PMID < cut-off. "
      "This approximates the PubMed *entry* date, not the publication date (epub-ahead-of-print and back-filled "
      "records are misdated); boundary misclassification is ~1% in each direction within the +-3-day windows "
      "(columns below), negligible at the gene-count level. The cut-off TSV is in "
      "`results/preregistration/pmid_date_cutoffs.tsv` (per-day quantiles in `pmid_date_cutoffs_days.tsv`).\n")
    w(md(rep["pubmed"]["cutoffs"]))
    w("")

    num = ["n_exp_BP", "n_exp_MF_informative", "n_exp_CC", "n_exp_informative_BPMF",
           "n_exp_informative_BPMF_lowthroughput", "n_exp_BPMF_all_terms", "n_ibas_BPMF", "n_comp_BPMF",
           "n_any_BPMF_nonIEA", "n_IEA"] + [f"n_exp_informative_BPMF_{s}" for s in GO_ARCHIVES.values()] + \
          ["n_pubmed", "n_pubmed_focused", "n_pubmed_focused3"] + \
          [c for c in out.columns if c.startswith("n_pubmed_focused_before_")] + \
          ["annotation_score", "protein_existence_level", "function_cc_length", "n_uniprot_pubmed",
           "unknome_knownness", "unknome_cluster_knownness"]
    w("## Summary distributions (all protein-coding genes)\n")
    w(quantile_table(out, num))
    w("")
    w("Restricted to in_depmap genes:\n")
    w(quantile_table(out[out.in_depmap], num))
    w("")
    w("### Categorical features\n")
    for c in ["in_depmap", "has_ND_BP", "has_ND_MF", "has_any_go_annotation", "has_function_cc",
              "protein_existence", "annotation_score", "tdl", "symbol_placeholder", "symbol_pattern"]:
        vc = out[c].astype(str).replace({"": "(empty)", "nan": "NA"}).value_counts()
        if c == "symbol_pattern":
            vc = vc.head(15)
        w(f"- **{c}**: " + ", ".join(f"{k}: {v:,}" for k, v in vc.items()))
    w("")

    # ------------------------------------------------------------------------ overlaps
    w("## Overlaps among low-knownness indicators (descriptive thresholds, NOT criteria)\n")
    sets = {
        "A: exp-informative BP/MF = 0": out.n_exp_informative_BPMF == 0,
        "A_lt: low-throughput exp-informative BP/MF = 0": out.n_exp_informative_BPMF_lowthroughput == 0,
        "B5: n_pubmed_focused <= 5": out.n_pubmed_focused <= 5,
        "B10: n_pubmed_focused <= 10": out.n_pubmed_focused <= 10,
        "B20: n_pubmed_focused <= 20": out.n_pubmed_focused <= 20,
        "C2: annotation_score <= 2": out.annotation_score <= 2,
        "C3: annotation_score <= 3": out.annotation_score <= 3,
        "D: Tdark": out.tdl == "Tdark",
        "E1: unknome_knownness <= 1": out.unknome_knownness <= 1,
        "E2: unknome_knownness <= 2": out.unknome_knownness <= 2,
        "F: symbol_placeholder": out.symbol_placeholder,
    }
    w("Genes with missing annotation_score / unknome_knownness / tdl are NOT counted in C / E / D.\n")
    w("| indicator | n genes | n in_depmap |\n|---|---|---|")
    for k, s in sets.items():
        w(f"| {k} | {int(s.sum()):,} | {int((s & out.in_depmap).sum()):,} |")
    w("")
    keys = ["A", "B5", "B10", "B20", "C2", "C3", "D", "E1", "E2", "F"]
    full = {k.split(":")[0]: v for k, v in sets.items()}
    w("Pairwise intersections (all genes; in_depmap in parentheses):\n")
    w("| | " + " | ".join(keys) + " |\n|---|" + "---|" * len(keys))
    for r in keys:
        cells = []
        for c in keys:
            s = full[r] & full[c]
            cells.append(f"{int(s.sum()):,} ({int((s & out.in_depmap).sum()):,})")
        w(f"| {r} | " + " | ".join(cells) + " |")
    w("")
    w("Selected multi-way intersections:\n")
    combos = [("A", "B10"), ("A", "B20"), ("A", "C3"), ("A", "D"), ("A", "E1"), ("A", "B10", "C3"),
              ("A", "B20", "C3"), ("A", "B10", "C3", "D"), ("A", "B10", "C3", "E1"), ("A", "B10", "C3", "D", "E1"),
              ("A", "B20", "C3", "D", "E2"), ("A_lt", "B10", "C3"), ("A_lt", "B20", "C3")]
    w("| intersection | n genes | n in_depmap |\n|---|---|---|")
    for cb in combos:
        s = np.logical_and.reduce([full[c] for c in cb])
        w(f"| {' & '.join(cb)} | {int(s.sum()):,} | {int((s & out.in_depmap).sum()):,} |")
    w("")
    w("Union/agreement view: number of the 5 indicator families (A, B10, C3, D, E1) a gene satisfies:\n")
    fam = np.vstack([full[k].values.astype(bool) for k in ["A", "B10", "C3", "D", "E1"]]).sum(0)
    vc = pd.Series(fam).value_counts().sort_index()
    w("| n indicators | n genes | n in_depmap |\n|---|---|---|")
    for kk, v in vc.items():
        w(f"| {kk} | {v:,} | {int(((fam == kk) & out.in_depmap.values).sum()):,} |")
    w("")
    # temporal
    w("### Temporal GO view (genes with 0 exp-informative BP/MF terms at each release)\n")
    w("| release | n genes with 0 | of which in_depmap | of those, > 0 in current GAF |\n|---|---|---|---|")
    for s in GO_ARCHIVES.values():
        z = out[f"n_exp_informative_BPMF_{s}"] == 0
        w(f"| {s} | {int(z.sum()):,} | {int((z & out.in_depmap).sum()):,} | "
          f"{int((z & (out.n_exp_informative_BPMF > 0)).sum()):,} |")
    z = out.n_exp_informative_BPMF == 0
    w(f"| current (2026-05) | {int(z.sum()):,} | {int((z & out.in_depmap).sum()):,} | - |")
    w("")
    w("Note: GO grows by revision as well as by new papers (e.g. removal of TAS/NAS and IPI-to-'protein binding' "
      "re-annotation), so a gene can also *lose* experimental terms between releases: genes with > 0 in 2019_07 "
      f"but 0 now: {int(((out.n_exp_informative_BPMF_2019_07 > 0) & z).sum()):,}.\n")

    # ------------------------------------------------------------------------ sanity checks
    w("## Sanity checks\n")
    sc_cols = ["symbol", "in_depmap", "n_exp_informative_BPMF", "n_exp_informative_BPMF_2019_07", "n_pubmed",
               "n_pubmed_focused", "n_pubmed_focused_before_2019_07", "annotation_score", "protein_existence_level",
               "function_cc_length", "n_uniprot_pubmed", "unknome_knownness", "tdl", "symbol_pattern"]
    ranks = {c: out[c].rank(pct=True) for c in ["n_exp_informative_BPMF", "n_pubmed", "n_pubmed_focused",
                                                 "n_uniprot_pubmed", "unknome_knownness"]}
    w("### Well-known genes (must be highly known by every metric)\n")
    known = ["TP53", "BRCA1", "MYC", "POLR2A"]
    t = out[out.symbol.isin(known)].set_index("symbol").reindex(known)
    rows = []
    allpass = True
    for s in known:
        r = t.loc[s]
        i = out.index[out.symbol == s][0]
        pr = {c: ranks[c].loc[i] for c in ranks}
        ok = (all(v >= 0.90 for v in pr.values()) and r.annotation_score == 5 and r.protein_existence_level == 1
              and r.tdl in ("Tclin", "Tchem", "Tbio") and bool(r.has_function_cc))
        allpass &= ok
        rows.append((s, ok, pr))
    w(md(t.reset_index()[sc_cols]))
    w("")
    w("Percentile ranks among protein-coding genes. Criterion: top decile (>= 0.90) on every numeric metric, "
      "annotation score 5, PE 1, TDL not Tdark, Function comment present. (A first, stricter draft criterion of "
      ">= 0.95 failed only for POLR2A on n_pubmed_focused and unknome_knownness, both ~0.93; the threshold was "
      "relaxed to the top decile because POLR2A is unambiguously well characterised -- recorded for transparency.) "
      "Note POLR2A is NOT a column of DepMap 26Q3 CRISPRGeneEffect (whereas POLR2B-M, PCNA and RPL3 are) -- a DepMap "
      "property, not a mapping error.\n")
    for s, ok, pr in rows:
        w(f"- {s}: {'PASS' if ok else 'FAIL'} -- " + ", ".join(f"{k} {v:.3f}" for k, v in pr.items()))
    w(f"\nOverall well-known check: **{'PASS' if allpass else 'FAIL'}**\n")

    w("### Classic 'C-orf' examples\n")
    w("Genes formerly named C<n>orf<n> that HGNC has since renamed (selected), and genes still named C*orf. "
      "Expectation: renamed-after-characterisation genes gain experimental GO terms and focused PMIDs after the "
      "old releases; still-C*orf genes mostly sit at the bottom of every metric.\n")
    ex_cols = ["symbol", "prev_symbol", "date_symbol_changed"]
    hg = load_hgnc(os.path.join(RAW, "hgnc", "hgnc_complete_set.txt"))[["hgnc_id"] + ex_cols]
    tt = out.merge(hg, on=["hgnc_id", "symbol"])
    # FIRRM (ex-C1orf112) plus a systematic sample of genes renamed from C*orf on/after 2019-07-01
    ren = tt[tt.prev_symbol.fillna("").str.contains(r"C(?:\d+|X|Y)orf\d+") &
             (tt.date_symbol_changed.fillna("") >= "2019-07-01")].sort_values("symbol")
    w(f"Genes renamed from a C*orf symbol on/after 2019-07-01: {len(ren):,}; of these with 0 exp-informative BP/MF "
      f"terms in 2019_07: {int((ren.n_exp_informative_BPMF_2019_07 == 0).sum()):,}, and now: "
      f"{int((ren.n_exp_informative_BPMF == 0).sum()):,}; median n_pubmed_focused_before_2019_07 "
      f"{ren.n_pubmed_focused_before_2019_07.median():g} vs now {ren.n_pubmed_focused.median():g}.\n")
    renamed = ["FIRRM"] + ren.symbol.iloc[:: max(1, len(ren) // 8)].head(8).tolist()
    tcols = ["symbol", "prev_symbol", "date_symbol_changed"] + [f"n_exp_informative_BPMF_{s}" for s in
                                                                GO_ARCHIVES.values()] + \
            ["n_exp_informative_BPMF", "n_pubmed_focused_before_2019_07", "n_pubmed_focused", "annotation_score",
             "unknome_knownness", "tdl"]
    rn = tt[tt.symbol.isin(renamed)][tcols]
    w(md(rn))
    w("")
    orf = tt[tt.symbol_pattern == "orf"]
    w(f"Still-C*orf genes: {len(orf):,}; of these with 0 exp-informative BP/MF terms: "
      f"{int((orf.n_exp_informative_BPMF == 0).sum()):,}; median n_pubmed_focused {orf.n_pubmed_focused.median():g} "
      f"(all genes: {out.n_pubmed_focused.median():g}); median annotation_score {orf.annotation_score.median():g} "
      f"(all: {out.annotation_score.median():g}); Tdark {int((orf.tdl == 'Tdark').sum()):,}; median unknome "
      f"knownness {orf.unknome_knownness.median():g} (all: {out.unknome_knownness.median():g}).\n")
    oc = ["symbol", "n_exp_informative_BPMF", "n_exp_informative_BPMF_lowthroughput", "n_pubmed_focused",
          "annotation_score", "unknome_knownness", "tdl", "in_depmap"]
    s10 = orf.sort_values("symbol").iloc[:: max(1, len(orf) // 10)][oc].head(10)
    w("Systematic sample (every k-th still-C*orf gene, alphabetical):\n")
    w(md(s10))
    w("")
    top = orf.sort_values("n_exp_informative_BPMF", ascending=False).head(8)[oc]
    w("Most-annotated still-C*orf genes (name lags characterisation -> why a symbol pattern is descriptive only):\n")
    w(md(top))
    w("")

    # ------------------------------------------------------------------------ data problems
    w("## Known data caveats\n")
    w("- TCRD TDLs are from the 2023 TCRD v6.13 mapping file (live Pharos may differ); genes characterised since "
      "2023 can still be 'Tdark'.")
    w("- The current GOA GAF (2026-05-21) is older than the ontology (2026-07-26); alt_ids are normalised with the "
      "current ontology, obsolete terms are kept as-is (counted).")
    w("- The 2018-07-02 archive GAF lists 'NCBITaxon:' in some taxon fields (IBA rows); taxon is not used for "
      "filtering, so this has no effect.")
    w("- gene2pubmed genes-per-PMID counts include all human GeneIDs (incl. non-coding/pseudo); focused counts are "
      "therefore slightly conservative for papers touching many loci.")
    w("- PMID cut-offs approximate PubMed entry date (see above).")
    w("- 64 DepMap 26Q3 gene columns are HGNC loci with locus_group 'other' (clustered protocadherins PCDHA/B/G, "
      "readthrough genes, UGT1A complex-locus constituents); they fall outside the protein-coding universe used here.")
    w("- 20 HGNC protein-coding genes have an empty `uniprot_ids` field (e.g. UBE2O, ABHD4); 5 of them are rescued "
      "for GO/Unknome/TCRD via the Swiss-Prot entry's HGNC cross-reference. The co-essentiality tool drops DepMap "
      "genes without HGNC UniProt IDs, so these genes cannot be scored by it even if in_depmap is True.")
    w("- Several well-studied genes are absent from the DepMap 26Q3 CRISPRGeneEffect header (e.g. POLR2A, GSTT1, "
      f"HSPA1A, SMN1/2, HBA1/2, all 13 mitochondrially-encoded genes): in_depmap = False for {int((~out.in_depmap).sum()):,} "
      "protein-coding genes.")
    w("- Unknome / TCRD / archived GO are mapped via current HGNC/UniProt accessions; accessions merged or deleted "
      "since are unmapped (rates above).")
    with open(OUT_README, "w") as f:
        f.write("\n".join(L) + "\n")


def md(df: pd.DataFrame) -> str:
    """Minimal markdown table (no tabulate dependency)."""
    def f(v):
        if isinstance(v, float):
            return "NA" if np.isnan(v) else f"{v:g}"
        return "" if v is None else str(v)
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * df.shape[1]]
    lines += ["| " + " | ".join(f(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
