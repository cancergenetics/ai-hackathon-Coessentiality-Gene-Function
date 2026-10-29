"""knownness.py -- gene "knownness" criteria D1, D2, D3 (DESIGN.md v2 §1.2) and GO target-set utilities (§3.2.2).

ONE function, ``d1(gaf, obo, release, acc_map)``, implements criterion D1 for any GO release (current and t0 =
2018-07-02 use the same code path):

  D1 (gene is "uncharacterised by GO"): zero *informative* GO BP/MF terms supported by evidence in
  D1_EVIDENCE = {EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC}.
    * rows whose qualifier contains the token NOT are dropped first (GAF 2.1 'NOT', GAF 2.2 'NOT|enables' ...);
    * only aspects P (BP) and F (MF) count; CC-only annotation does not count;
    * all other evidence codes are ignored (HTP/HDA/HMP/HGI/HEP, IEA, ISS/ISO/ISA/ISM/IGC, IBA/IBD/IKR/IRD, RCA,
      NAS, ND);
    * GO ids are normalised with the release's own ontology (alt_id -> primary id; obsolete terms with a single
      replaced_by -> replacement); terms that cannot be resolved are kept as-is (an experimental annotation to an
      obsolete term is still evidence of study) and counted in the stats;
    * generic terms (GENERIC_TERMS: protein binding, binding, identical protein binding, homodimerisation, the three
      roots and generic grouping/interaction terms; full list below with reasons) do not count;
    * gene mapping: GAF column 2 (UniProtKB accession, isoform suffix stripped) -> HGNC id through ``acc_map``
      (HGNC ``uniprot_ids`` plus Swiss-Prot entries whose HGNC cross-reference names a protein-coding gene); no
      symbol fallback, so every release is mapped identically.
  D2: UniProt annotation score <= 2 (max over the gene's reviewed entries; genes with no reviewed entry -> NA,
      D2 False).
  D3: <= 10 focused PubMed records (PMIDs linked to <= 10 human GeneIDs in gene2pubmed) OR IDG TDL == Tdark.
  U = D1 & (D2 | D3).

GO target utilities (temporal hold-out, §3.2.2): ``GoOntology`` (own OBO parser keeping obsolete terms,
alt_id, replaced_by, consider, is_a and part_of), ``GoOntology.resolve`` (alt_id / replaced_by resolution with
status), ``GoOntology.ancestors`` (is_a + part_of closure, self included), ``propagate_annotations``,
``target_sets``.

No DepMap values are read here and no pairwise computation is done.
"""
from __future__ import annotations

import gzip
import io
import os
from collections import defaultdict

import numpy as np
import pandas as pd

# ------------------------------------------------------------------------------------------------ constants
D1_EVIDENCE = frozenset({"EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC"})
D1_ASPECTS = frozenset({"P", "F"})

# Generic terms that never count as "informative" (same list as scripts/02_gene_knownness_table.py, which DESIGN
# §1.2 calls "the full list in the script").
GENERIC_TERMS = {
    "GO:0005515": "protein binding -- bare 'interacts with something'; dominated by interactome screens",
    "GO:0003674": "molecular_function root",
    "GO:0008150": "biological_process root",
    "GO:0005575": "cellular_component root",
    "GO:0005488": "binding -- MF high-level grouping term, no specificity",
    "GO:0042802": "identical protein binding -- self-interaction, no functional content",
    "GO:0042803": "protein homodimerization activity -- self-interaction, no functional content",
    "GO:0046982": "protein heterodimerization activity -- generic interaction term (partner unspecified)",
    "GO:0019899": "enzyme binding -- generic interaction with any enzyme",
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
GENERIC = frozenset(GENERIC_TERMS)

GAF_COLS = ["db", "acc", "symbol", "qualifier", "go_id", "reference", "evidence", "with_from", "aspect", "db_name",
            "synonyms", "db_type", "taxon", "date", "assigned_by", "extension", "gene_product_form"]

PROPAGATION_RELATIONS = ("is_a", "part_of")


# ================================================================================================= ontology
class GoOntology:
    """Minimal OBO model. Keeps obsolete terms (needed to resolve replaced_by). Edges: is_a and part_of only."""

    def __init__(self, terms: dict, alt: dict, release: str = ""):
        # terms: id -> dict(namespace, name, obsolete, replaced_by[list], consider[list], parents[set])
        self.terms = terms
        self.alt = alt
        self.release = release
        self._anc: dict = {}

    # ---------------------------------------------------------------- parsing
    @classmethod
    def from_obo(cls, path_or_text: str, release: str = "") -> "GoOntology":
        if "\n" in path_or_text:
            fh = io.StringIO(path_or_text)
        else:
            opener = gzip.open if path_or_text.endswith(".gz") else open
            fh = opener(path_or_text, "rt")
        terms, alt = {}, {}
        cur, in_term, data_version = None, False, ""
        with fh:
            for line in fh:
                line = line.rstrip("\n")
                if line.startswith("data-version:") and not data_version:
                    data_version = line.split(":", 1)[1].strip()
                if line.startswith("["):
                    in_term = line.strip() == "[Term]"
                    cur = None
                    continue
                if not in_term or not line or line.startswith("!"):
                    continue
                key, _, val = line.partition(": ")
                val = val.split(" ! ")[0].strip()
                if key == "id":
                    cur = val
                    terms[cur] = dict(namespace="", name="", obsolete=False, replaced_by=[], consider=[],
                                      parents=set())
                elif cur is None:
                    continue
                elif key == "name":
                    terms[cur]["name"] = val
                elif key == "namespace":
                    terms[cur]["namespace"] = val
                elif key == "alt_id":
                    alt[val] = cur
                elif key == "is_obsolete" and val.lower() == "true":
                    terms[cur]["obsolete"] = True
                elif key == "replaced_by":
                    terms[cur]["replaced_by"].append(val)
                elif key == "consider":
                    terms[cur]["consider"].append(val)
                elif key == "is_a":
                    terms[cur]["parents"].add(val.split()[0])
                elif key == "relationship":
                    rel, tgt = val.split()[:2]
                    if rel in PROPAGATION_RELATIONS:
                        terms[cur]["parents"].add(tgt)
        return cls(terms, alt, release or data_version)

    # ---------------------------------------------------------------- id resolution
    def resolve(self, go_id: str) -> tuple[str | None, str]:
        """Map a GO id to a current, non-obsolete primary id.
        Returns (id or None, status); status in {'primary', 'alt_id', 'replaced_by', 'obsolete_dropped',
        'unknown_dropped'}. Chains (alt_id -> obsolete -> replaced_by -> ...) are followed (max 10 steps)."""
        status = "primary"
        cur = go_id
        for _ in range(10):
            if cur in self.alt and cur not in self.terms:
                cur = self.alt[cur]
                status = "alt_id" if status == "primary" else status
                continue
            t = self.terms.get(cur)
            if t is None:
                return None, "unknown_dropped"
            if not t["obsolete"]:
                return cur, status
            if len(t["replaced_by"]) == 1:
                cur = t["replaced_by"][0]
                status = "replaced_by"
                continue
            return None, "obsolete_dropped"  # no (or ambiguous) replaced_by; 'consider' is not followed
        return None, "obsolete_dropped"

    def normalise_alt(self, go_id: str) -> tuple[str, str]:
        """For D1: resolve when possible, else keep the id as-is. Returns (id, status)."""
        r, st = self.resolve(go_id)
        return (r, st) if r is not None else (go_id, st)

    # ---------------------------------------------------------------- propagation
    def ancestors(self, go_id: str) -> frozenset:
        """Reflexive is_a/part_of closure of a (resolved, non-obsolete) term."""
        if go_id in self._anc:
            return self._anc[go_id]
        seen, stack = {go_id}, [go_id]
        while stack:
            t = stack.pop()
            for p in self.terms.get(t, {}).get("parents", ()):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        fs = frozenset(seen)
        self._anc[go_id] = fs
        return fs

    def namespace(self, go_id: str) -> str:
        return self.terms.get(go_id, {}).get("namespace", "")

    def name(self, go_id: str) -> str:
        return self.terms.get(go_id, {}).get("name", "")


def as_ontology(obo, release: str = "") -> GoOntology:
    return obo if isinstance(obo, GoOntology) else GoOntology.from_obo(obo, release)


# ====================================================================================================== GAF
def read_gaf(path_or_buffer) -> pd.DataFrame:
    """Read a GAF 2.1/2.2 file (17 tab-separated columns, '!' header lines). Accepts a path, buffer or text."""
    if isinstance(path_or_buffer, str) and "\n" in path_or_buffer:
        path_or_buffer = io.StringIO(path_or_buffer)
    return pd.read_csv(path_or_buffer, sep="\t", comment="!", header=None, dtype=str, quoting=3, names=GAF_COLS,
                       usecols=range(17), keep_default_na=False)


def is_not_qualified(q: pd.Series) -> pd.Series:
    """True where the qualifier contains the NOT token ('NOT', 'NOT|contributes_to', 'NOT|enables', ...)."""
    return q.fillna("").str.upper().str.split("|").apply(lambda toks: "NOT" in toks)


def strip_isoform(acc: str) -> str:
    return acc.split("-")[0]


def split_multi(s, sep="|") -> list[str]:
    if s is None or (isinstance(s, float) and np.isnan(s)) or s == "":
        return []
    return [x.strip() for x in str(s).split(sep) if x.strip()]


def build_acc_map(hgnc_pc: pd.DataFrame, uniprot: pd.DataFrame | None = None) -> tuple[dict, dict]:
    """UniProt accession -> set(hgnc_id). Source 1: HGNC ``uniprot_ids`` (protein-coding universe). Source 2 (only
    accessions not in source 1): Swiss-Prot entries whose HGNC cross-reference names a gene of the universe."""
    acc2 = defaultdict(set)
    for hid, ids in zip(hgnc_pc.hgnc_id, hgnc_pc.uniprot_ids):
        for a in split_multi(ids):
            acc2[a].add(hid)
    stats = {"n_acc_hgnc": len(acc2), "n_acc_multi_gene": sum(len(v) > 1 for v in acc2.values())}
    n_added = 0
    if uniprot is not None:
        valid = set(hgnc_pc.hgnc_id)
        for acc, hx in zip(uniprot["Entry"], uniprot["HGNC"]):
            if acc in acc2:
                continue
            hs = {x for x in split_multi(hx, ";") if x in valid}
            if hs:
                acc2[acc] = hs
                n_added += 1
    stats["n_acc_added_from_uniprot_xref"] = n_added
    return dict(acc2), stats


def d1_annotations(gaf, obo, acc_map: dict, resolve_mode: str = "normalise") -> tuple[pd.DataFrame, dict]:
    """GAF rows that are eligible for D1 (non-NOT, aspect P/F, evidence in D1_EVIDENCE), mapped to HGNC ids.

    resolve_mode 'normalise' (D1): ids resolved with ``obo`` when possible, unresolvable ids kept as-is.
    resolve_mode 'strict' (targets): ids resolved with ``obo``; unresolvable (obsolete without single replaced_by,
    unknown) rows are dropped and counted.
    Returns a long frame [hgnc_id, go_id, go_id_raw, aspect, evidence, reference, resolve_status] and stats."""
    g = read_gaf(gaf) if not isinstance(gaf, pd.DataFrame) else gaf
    onto = as_ontology(obo)
    st = {"rows": len(g)}
    notq = is_not_qualified(g["qualifier"])
    st["not_rows_removed"] = int(notq.sum())
    g = g.loc[~notq]
    sel = g["aspect"].isin(D1_ASPECTS) & g["evidence"].isin(D1_EVIDENCE)
    st["rows_bpmf_d1_evidence"] = int(sel.sum())
    g = g.loc[sel].copy()
    # resolve GO ids (memoised per distinct id)
    uniq = pd.unique(g["go_id"])
    res = {t: onto.resolve(t) for t in uniq}
    g["go_id_raw"] = g["go_id"]
    g["resolve_status"] = g["go_id"].map(lambda t: res[t][1])
    if resolve_mode == "strict":
        g["go_id"] = g["go_id"].map(lambda t: res[t][0])
    else:
        g["go_id"] = g["go_id"].map(lambda t: res[t][0] if res[t][0] is not None else t)
    for s in ("primary", "alt_id", "replaced_by", "obsolete_dropped", "unknown_dropped"):
        st[f"rows_{s}"] = int((g["resolve_status"] == s).sum())
        st[f"terms_{s}"] = int(g.loc[g["resolve_status"] == s, "go_id_raw"].nunique())
    if resolve_mode == "strict":
        g = g[g["go_id"].notna()]
    # gene mapping by accession
    acc = g["acc"].map(strip_isoform)
    hits = acc.map(lambda a: sorted(acc_map.get(a, ())))
    st["rows_unmapped"] = int((hits.map(len) == 0).sum())
    st["rows_uniprotkb_unmapped"] = int(((hits.map(len) == 0) & (g["db"] == "UniProtKB")).sum())
    g = g.assign(hgnc_id=hits).explode("hgnc_id")
    g = g[g["hgnc_id"].notna()]
    out = g[["hgnc_id", "go_id", "go_id_raw", "aspect", "evidence", "reference", "resolve_status"]].reset_index(
        drop=True)
    st["rows_mapped"] = len(out)
    st["genes_with_rows"] = int(out["hgnc_id"].nunique())
    return out, st


def d1(gaf, obo, release: str, acc_map: dict, universe=None, generic=GENERIC) -> tuple[pd.DataFrame, pd.DataFrame,
                                                                                         dict]:
    """Criterion D1 for one GO release (the single implementation used for every release).

    Returns (per_gene, annotations, stats). per_gene is indexed by hgnc_id (``universe`` if given, else genes with
    rows) with columns: release, n_d1_terms_informative, n_d1_terms_generic, n_d1_rows, d1_terms (';'-joined
    informative ids), D1 (bool: n_d1_terms_informative == 0)."""
    onto = as_ontology(obo, release)
    ann, st = d1_annotations(gaf, onto, acc_map, resolve_mode="normalise")
    ann["informative"] = ~ann["go_id"].isin(generic)
    inf = ann[ann.informative]
    n_inf = inf.groupby("hgnc_id")["go_id"].nunique()
    n_gen = ann[~ann.informative].groupby("hgnc_id")["go_id"].nunique()
    n_rows = ann.groupby("hgnc_id").size()
    terms = inf.groupby("hgnc_id")["go_id"].apply(lambda s: ";".join(sorted(set(s))))
    idx = pd.Index(sorted(set(universe)) if universe is not None else sorted(ann.hgnc_id.unique()), name="hgnc_id")
    pg = pd.DataFrame(index=idx)
    pg["release"] = release
    pg["n_d1_terms_informative"] = n_inf.reindex(idx).fillna(0).astype(int)
    pg["n_d1_terms_generic"] = n_gen.reindex(idx).fillna(0).astype(int)
    pg["n_d1_rows"] = n_rows.reindex(idx).fillna(0).astype(int)
    pg["d1_terms"] = terms.reindex(idx).fillna("")
    pg["D1"] = pg["n_d1_terms_informative"] == 0
    st["release"] = release
    st["n_genes_D1"] = int(pg.D1.sum())
    return pg, ann, st


# =================================================================================================== D2, D3
def uniprot_gene_table(uniprot: pd.DataFrame, hgnc_pc: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Swiss-Prot entry -> hgnc_id (entry's HGNC xref restricted to the universe; else HGNC uniprot_ids)."""
    valid = set(hgnc_pc.hgnc_id)
    acc2hg = defaultdict(set)
    for hid, ids in zip(hgnc_pc.hgnc_id, hgnc_pc.uniprot_ids):
        for a in split_multi(ids):
            acc2hg[a].add(hid)
    rows, n_x, n_a, n_un = [], 0, 0, 0
    for entry, hx, score in zip(uniprot["Entry"], uniprot["HGNC"], uniprot["Annotation"]):
        hs = {x for x in split_multi(hx, ";") if x in valid}
        if hs:
            n_x += 1
        else:
            hs = acc2hg.get(entry, set())
            n_a += bool(hs)
            n_un += not hs
        for h in hs:
            rows.append((h, entry, float(score) if score not in ("", None) else np.nan))
    return (pd.DataFrame(rows, columns=["hgnc_id", "entry", "annotation_score"]),
            dict(entries=len(uniprot), by_hgnc_xref=n_x, by_accession=n_a, unmapped=n_un))


def d2(uniprot: pd.DataFrame, hgnc_pc: pd.DataFrame, max_score: float = 2) -> tuple[pd.DataFrame, dict]:
    """D2: max UniProt annotation score over the gene's reviewed entries <= max_score (NA -> False)."""
    u, st = uniprot_gene_table(uniprot, hgnc_pc)
    s = u.groupby("hgnc_id")["annotation_score"].max().reindex(hgnc_pc.hgnc_id)
    out = pd.DataFrame({"annotation_score": s.values}, index=pd.Index(hgnc_pc.hgnc_id, name="hgnc_id"))
    out["D2"] = out["annotation_score"].le(max_score).fillna(False).astype(bool)
    st["genes_no_reviewed_entry"] = int(out.annotation_score.isna().sum())
    return out, st


def focused_pmid_counts(g2p: pd.DataFrame, max_genes: int | None = 10, pmid_lt: int | None = None) -> pd.Series:
    """Distinct PMIDs per GeneID. Only PMIDs linked to <= max_genes distinct GeneIDs in g2p (full human file) are
    counted; if pmid_lt is given, only PMIDs < pmid_lt (genes-per-PMID always from the full g2p)."""
    d = g2p[["GeneID", "PubMed_ID"]].drop_duplicates()
    if max_genes is not None:
        per = d.groupby("PubMed_ID")["GeneID"].nunique()
        d = d[d.PubMed_ID.isin(per.index[per <= max_genes])]
    if pmid_lt is not None:
        d = d[d.PubMed_ID < pmid_lt]
    return d.groupby("GeneID")["PubMed_ID"].nunique()


TDL_RANK = {"Tclin": 4, "Tchem": 3, "Tbio": 2, "Tdark": 1}


def tdl_per_gene(tcrd: pd.DataFrame, acc_map: dict, hgnc_ids) -> pd.Series:
    """Highest IDG TDL over the gene's accessions ('' if unmapped)."""
    tc = tcrd.copy()
    tc["hgnc_id"] = tc.UniProt_accession.map(lambda a: sorted(acc_map.get(a, set())))
    te = tc.explode("hgnc_id").dropna(subset=["hgnc_id"])
    te["r"] = te.TDL.map(TDL_RANK)
    best = te.sort_values("r", ascending=False).drop_duplicates("hgnc_id").set_index("hgnc_id").TDL
    return pd.Series(hgnc_ids, index=hgnc_ids).map(best).fillna("")


def d3(g2p: pd.DataFrame, tcrd: pd.DataFrame, hgnc_pc: pd.DataFrame, acc_map: dict, max_pmids: int = 10,
       max_genes_per_pmid: int = 10) -> pd.DataFrame:
    """D3: n focused PMIDs <= max_pmids OR TDL == Tdark."""
    ent = pd.to_numeric(hgnc_pc.entrez_id, errors="coerce")
    n_foc = ent.map(focused_pmid_counts(g2p, max_genes=max_genes_per_pmid)).fillna(0).astype(int)
    tdl = tdl_per_gene(tcrd, acc_map, list(hgnc_pc.hgnc_id))
    out = pd.DataFrame({"n_pubmed_focused": n_foc.values, "tdl": tdl.values},
                       index=pd.Index(hgnc_pc.hgnc_id, name="hgnc_id"))
    out["D3_pubmed"] = out.n_pubmed_focused <= max_pmids
    out["D3_tdark"] = out.tdl == "Tdark"
    out["D3"] = out.D3_pubmed | out.D3_tdark
    return out


def combine_u(d1_flag: pd.Series, d2_flag: pd.Series, d3_flag: pd.Series) -> pd.Series:
    """U = D1 & (D2 | D3)."""
    return d1_flag.astype(bool) & (d2_flag.astype(bool) | d3_flag.astype(bool))


# ============================================================================================ target sets
def propagate_annotations(ann: pd.DataFrame, onto: GoOntology, generic=GENERIC) -> dict:
    """gene -> frozenset of propagated (reflexive is_a/part_of closure) term ids. ``ann`` must hold resolved,
    non-obsolete go_ids (d1_annotations(..., resolve_mode='strict')). Generic terms are NOT removed here
    (subtraction must see them); callers drop them from targets."""
    out = {}
    for gene, terms in ann.groupby("hgnc_id")["go_id"]:
        s = set()
        for t in set(terms):
            s |= onto.ancestors(t)
        out[gene] = frozenset(s)
    return out


def term_sizes(prop: dict, genes) -> pd.Series:
    """Number of ``genes`` annotated (propagated) to each term."""
    cnt = defaultdict(int)
    for g in genes:
        for t in prop.get(g, ()):
            cnt[t] += 1
    return pd.Series(cnt, dtype=int)


def target_sets(cur_prop: dict, t0_prop: dict, genes, sizes: pd.Series, lo: int = 5, hi: int = 200,
                generic=GENERIC, aspects_ns=("biological_process", "molecular_function"),
                onto: GoOntology | None = None) -> dict:
    """T(g) = propagated current terms - propagated t0 terms, minus generic terms, restricted to terms whose size
    (``sizes``, at t0) is within [lo, hi] (and, if onto is given, to BP/MF namespaces)."""
    out = {}
    for g in genes:
        diff = set(cur_prop.get(g, ())) - set(t0_prop.get(g, ())) - set(generic)
        keep = {t for t in diff if lo <= int(sizes.get(t, 0)) <= hi}
        if onto is not None:
            keep = {t for t in keep if onto.namespace(t) in aspects_ns}
        out[g] = keep
    return out


def supporting_rows(ann: pd.DataFrame, onto: GoOntology, gene: str, term: str) -> pd.DataFrame:
    """Annotation rows of ``gene`` whose (resolved) term equals ``term`` or is a descendant of it."""
    a = ann[ann.hgnc_id == gene]
    return a[a.go_id.map(lambda t: term in onto.ancestors(t))]


def pmids_from_refs(refs) -> list[int]:
    out = set()
    for r in refs:
        for tok in str(r).split("|"):
            tok = tok.strip()
            if tok.upper().startswith("PMID:"):
                try:
                    out.add(int(tok[5:]))
                except ValueError:
                    pass
    return sorted(out)


def sha256(path: str, block: int = 1 << 20) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def load_hgnc_pc(path: str) -> pd.DataFrame:
    h = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)
    return h[(h.status == "Approved") & (h.locus_group == "protein-coding gene")].reset_index(drop=True)


def load_g2p(path: str) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", names=["tax_id", "GeneID", "PubMed_ID"], comment="#", dtype=np.int64)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
