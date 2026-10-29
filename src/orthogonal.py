"""orthogonal.py -- loaders for the orthogonal evidence sources of DESIGN.md v2.3 §5.1 / §5.1b.

Every loader returns a :class:`Source` keyed on HGNC ids (``hgnc_id`` of the protein-coding universe in
``results/ids/hgnc_hub.tsv``), of one of these kinds:

* ``binary``        -- symmetric gene-pair edges (scipy CSR adjacency over ``genes``); ``genes`` = measured genes
                       (source-specific definition in ``meta['measured']``).
* ``continuous``    -- dense gene x gene score matrix over ``genes`` (float32, NaN = not computable); the support and
                       admission statistics use per-row percentiles (``row_percentiles``).
* ``pair_binary``   -- pair-level coverage (Burke 2023): ``covered`` CSR (pairs scored) and ``adj`` (pDockQ >= cut).
* ``localisation``  -- gene -> frozenset of common-vocabulary compartments (``comp``), plus the high-reliability
                       subset (``comp_hr``) used by the §5.3 contradiction rule.
* ``annotation``    -- gene -> frozenset of propagated GO terms (homology: IBA/ISO; reported only).
* ``profile``       -- per-gene profile DataFrame (DEMETER2; not independent; reported only, no pair scores).

Identifier rules (DESIGN §2.1, ``results/ids/hgnc_hub.tsv``): join on the most specific ID a source provides -- HGNC id
> Entrez > Ensembl gene > UniProt accession (isoform suffix stripped; HGNC ``uniprot_ids`` first, Swiss-Prot HGNC
cross-reference second) > RefSeq protein (via STRING aliases -> ENSP -> HGNC id); approved symbol only when no ID
exists (Olivieri 2020) or as a recorded fallback, with previous symbols / aliases used only when unique. IDs mapping to
>1 gene are dropped and counted. Each loader records its mapping QC in ``Source.qc`` (written by
``write_mapping_qc``).

Heavy intermediates (parsed spreadsheets, correlation matrices) are cached under ``data/derived/orthogonal/``
(git-ignored); pass ``cache=False`` to rebuild. No loader reads DepMap gene-effect values (Model.csv metadata only, for
the CCLE proteomics line mapping); the DEMETER2 loader returns the RNAi profile matrix only (no pairwise scores).
"""
from __future__ import annotations

import gzip
import io
import json
import os
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd
import scipy.sparse as sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DERIVED = os.path.join(ROOT, "data", "derived", "orthogonal")
HUB_TSV = os.path.join(ROOT, "results", "ids", "hgnc_hub.tsv")
LOC_MAP_TSV = os.path.join(ROOT, "config", "localisation_map.tsv")
FROZEN_YAML = os.path.join(ROOT, "config", "frozen.yaml")

COMPARTMENTS = ("nucleus", "nucleolus", "nuclear envelope", "cytosol", "mitochondrion", "ER", "Golgi",
                "plasma membrane", "vesicles/endosome/lysosome", "peroxisome", "lipid droplet", "centrosome/cilium",
                "cytoskeleton")
COMPARTMENT_PARENT = {"nucleolus": "nucleus", "nuclear envelope": "nucleus"}
D1_EVIDENCE = ("EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC")
HOMOLOGY_EVIDENCE = ("IBA", "ISO")
# GO CC references that ARE one of the localisation sources (excluded from the GO CC side of the localisation
# admission so that agreement is not circular): HPA (GO_REF:0000052), OpenCell (Cho 2022), Human Cell Map (Go 2021),
# MitoCarta (Pagliarini 2008, Calvo 2016, Rath 2021).
LOCALISATION_SELF_REFS = {"GO_REF:0000052", "PMID:35271311", "PMID:34079125", "PMID:18614015", "PMID:26450961",
                          "PMID:33174596"}
# hu.MAP publications (1.0 Drew 2017; 2.0 Drew 2021; 3.0 Fischer 2025 not in PubMed at GAF date): GO annotations
# citing them are excluded from the complex gold standard ("non-hu.MAP complexes", §5.2).
HUMAP_REFS = {"PMID:28298427", "PMID:33973408"}


# ======================================================================================================== config
def frozen() -> dict:
    """config/frozen.yaml as {section: {key: entry}} (one-line JSON flow mappings; same parser as scripts/07)."""
    out, group = {}, None
    with open(FROZEN_YAML, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line.startswith(" "):
                group = line.strip().rstrip(":")
                out[group] = {}
                continue
            k, _, v = line.strip().partition(": ")
            out[group][k] = json.loads(v)
    return out


def fz(section: str, key: str, default=None):
    try:
        return frozen()[section][key]["value"]
    except KeyError:
        if default is None:
            raise
        return default


# ====================================================================================================== Source
@dataclass
class Source:
    name: str
    cls: str                    # P, A, L, G, S, H (homology) or NI (not independent)
    kind: str                   # binary | continuous | pair_binary | localisation | annotation | profile
    independent: bool = True
    genes: list = field(default_factory=list)
    adj: sp.csr_matrix | None = None
    covered: sp.csr_matrix | None = None
    mat: np.ndarray | None = None
    strength: np.ndarray | None = None          # Perturb-seq phenotype strength (null matching)
    comp: dict | None = None
    comp_hr: dict | None = None
    terms: dict | None = None
    profile: pd.DataFrame | None = None
    qc: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
    _index: dict | None = None
    _pct: np.ndarray | None = None

    @property
    def index(self) -> dict:
        if self._index is None:
            self._index = {g: i for i, g in enumerate(self.genes)}
        return self._index

    def degree(self) -> np.ndarray:
        """Binary/pair_binary: number of edges (pair_binary: number of covered pairs). Continuous: hubness = mean
        finite off-diagonal score of the row. Localisation: number of compartments."""
        if self.kind == "binary":
            return np.asarray(self.adj.sum(1)).ravel()
        if self.kind == "pair_binary":
            return np.asarray(self.covered.sum(1)).ravel()
        if self.kind == "continuous":
            with np.errstate(invalid="ignore"):
                return np.nanmean(self.mat, axis=1)
        if self.kind == "localisation":
            return np.array([len(self.comp.get(g, ())) for g in self.genes])
        raise ValueError(self.kind)

    def row_percentiles(self) -> np.ndarray:
        """Continuous sources: P[i, j] = fraction of finite off-diagonal entries of row i that are <= mat[i, j]
        (average rank / n_finite; ties averaged); NaN where mat is NaN. Cached on the object."""
        if self._pct is None:
            self._pct = row_percentiles(self.mat)
        return self._pct

    def n_edges(self) -> int:
        a = self.adj if self.adj is not None else None
        return int(a.nnz // 2) if a is not None else 0


def row_percentiles(mat: np.ndarray, block: int = 512) -> np.ndarray:
    """Row-wise percentile ranks (average ties) of finite entries; diagonal excluded (set NaN)."""
    n, m = mat.shape
    out = np.full((n, m), np.nan, dtype=np.float32)
    for s in range(0, n, block):
        X = np.array(mat[s:s + block], dtype=np.float64)
        for r in range(X.shape[0]):
            i = s + r
            if i < m:
                X[r, i] = np.nan
        fin = np.isfinite(X)
        nf = fin.sum(1)
        Xf = np.where(fin, X, np.inf)
        order = np.argsort(Xf, axis=1, kind="mergesort")
        Xs = np.take_along_axis(Xf, order, axis=1)
        for r in range(X.shape[0]):
            k = nf[r]
            if k == 0:
                continue
            v = Xs[r, :k]
            # average ranks with ties (1-based)
            uniq, first, counts = np.unique(v, return_index=True, return_counts=True)
            avg = first + (counts + 1) / 2.0
            ranks = np.repeat(avg, counts)
            out[s + r, order[r, :k]] = (ranks / k).astype(np.float32)
    return out


def symmetric_csr(i, j, n) -> sp.csr_matrix:
    i = np.asarray(i, dtype=np.int64)
    j = np.asarray(j, dtype=np.int64)
    keep = i != j
    i, j = i[keep], j[keep]
    a = sp.coo_matrix((np.ones(len(i), dtype=np.int8), (i, j)), shape=(n, n))
    a = ((a + a.T) > 0).astype(np.int8).tocsr()
    a.eliminate_zeros()
    return a


def edges_to_source(name, cls, pairs: pd.DataFrame, measured=None, independent=True, qc=None, meta=None) -> Source:
    """pairs: DataFrame [a, b] of hgnc ids (unmapped rows already removed). measured: iterable of hgnc ids (default:
    the nodes of ``pairs``)."""
    nodes = set(pairs.a) | set(pairs.b)
    genes = sorted(nodes | set(measured or ()))
    idx = {g: k for k, g in enumerate(genes)}
    adj = symmetric_csr(pairs.a.map(idx).values, pairs.b.map(idx).values, len(genes))
    s = Source(name=name, cls=cls, kind="binary", independent=independent, genes=genes, adj=adj, qc=qc or {},
               meta=meta or {})
    s.qc.update(measured_genes=len(genes), edges=s.n_edges(), genes_with_edge=int((s.degree() > 0).sum()))
    return s


# ============================================================================================== identifier hub
class IdMapper:
    """HGNC-id mapping from the hub (protein-coding universe only)."""

    def __init__(self, hub_path: str = HUB_TSV, uniprot_path: str | None = None):
        hub = pd.read_csv(hub_path, sep="\t", dtype=str, keep_default_na=False)
        hub = hub[hub.in_universe == "True"].reset_index(drop=True)
        self.hub = hub
        self.universe = set(hub.hgnc_id)
        self.symbol = dict(zip(hub.hgnc_id, hub.symbol))
        self.entrez = {e: h for h, e in zip(hub.hgnc_id, hub.entrez_id) if e}
        self.ensg = {e: h for h, e in zip(hub.hgnc_id, hub.ensembl_gene_id) if e}
        acc = defaultdict(set)
        for h, ids in zip(hub.hgnc_id, hub.uniprot_ids):
            for a in ids.split("|"):
                if a:
                    acc[a].add(h)
        n_hgnc_acc = len(acc)
        uniprot_path = uniprot_path or os.path.join(RAW, "uniprot", "uniprot_human_reviewed.tsv")
        n_add = 0
        if os.path.exists(uniprot_path):
            up = pd.read_csv(uniprot_path, sep="\t", usecols=["Entry", "HGNC"], dtype=str, keep_default_na=False)
            for a, hx in zip(up.Entry, up.HGNC):
                if a in acc:
                    continue
                hs = {x.strip() for x in hx.split(";") if x.strip() in self.universe}
                if hs:
                    acc[a] = hs
                    n_add += 1
        self.acc = dict(acc)
        self.acc_stats = {"acc_from_hgnc": n_hgnc_acc, "acc_added_from_swissprot_xref": n_add}
        sym = defaultdict(set)
        prev = defaultdict(set)
        alias = defaultdict(set)
        for h, s, p, a in zip(hub.hgnc_id, hub.symbol, hub.prev_symbols, hub.alias_symbols):
            sym[s.upper()].add(h)
            for t in p.split("|"):
                if t:
                    prev[t.upper()].add(h)
            for t in a.split("|"):
                if t:
                    alias[t.upper()].add(h)
        self.sym, self.prev, self.alias = dict(sym), dict(prev), dict(alias)
        self._ensp = None

    # ---------------------------------------------------------------- single-ID maps (None if unmapped/ambiguous)
    def from_hgnc(self, x):
        return x if x in self.universe else None

    def from_entrez(self, x):
        x = str(x).strip().split(".")[0] if x is not None else ""
        return self.entrez.get(x)

    def from_ensg(self, x):
        return self.ensg.get(str(x).split(".")[0]) if x else None

    def from_acc(self, x):
        if not x:
            return None
        hs = self.acc.get(str(x).strip().split("-")[0])
        return next(iter(hs)) if hs and len(hs) == 1 else None

    def acc_status(self, x) -> str:
        hs = self.acc.get(str(x).strip().split("-")[0]) if x else None
        return "unmapped" if not hs else ("mapped" if len(hs) == 1 else "ambiguous")

    def from_symbol(self, x) -> tuple[str | None, str]:
        """(hgnc_id, route): route in approved / previous / alias / ambiguous / unmapped. Approved symbol wins; a
        previous symbol or alias is used only if it names exactly one gene and is not another gene's approved
        symbol."""
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return None, "unmapped"
        u = str(x).strip().upper()
        if u in self.sym:
            hs = self.sym[u]
            return (next(iter(hs)), "approved") if len(hs) == 1 else (None, "ambiguous")
        for route, d in (("previous", self.prev), ("alias", self.alias)):
            if u in d:
                hs = d[u]
                return (next(iter(hs)), route) if len(hs) == 1 else (None, "ambiguous")
        return None, "unmapped"

    # ---------------------------------------------------------------- STRING ENSP / RefSeq
    def ensp_map(self) -> dict:
        """STRING protein id (9606.ENSP...) -> hgnc_id: 'Ensembl_HGNC_hgnc_id' alias (if in universe), else the
        'Ensembl_gene' ENSG via the hub. Also returns RefSeq protein (unversioned NP_/XP_) -> set(hgnc_id)."""
        if self._ensp is None:
            path = os.path.join(RAW, "string", "9606.protein.aliases.v12.5.txt.gz")
            al = pd.read_csv(path, sep="\t", dtype=str, names=["p", "alias", "source"], skiprows=1)
            hg = al[al.source == "Ensembl_HGNC_hgnc_id"]
            en = al[al.source == "Ensembl_gene"]
            m, route = {}, Counter()
            for p, h in zip(hg.p, hg.alias):
                if h in self.universe:
                    m[p] = h
            for p, e in zip(en.p, en.alias):
                if p not in m:
                    h = self.from_ensg(e)
                    if h:
                        m[p] = h
                        route["ensg"] += 1
            proteins = set(al.p)
            route["hgnc_alias"] = len(m) - route["ensg"]
            route["string_proteins"] = len(proteins)
            route["unmapped"] = len(proteins - set(m))
            rs = al[al.source == "Ensembl_RefSeq_short"]
            refseq = defaultdict(set)
            for p, r in zip(rs.p, rs.alias):
                if p in m:
                    refseq[r].add(m[p])
            self._ensp = (m, dict(refseq), dict(route))
        return self._ensp


_MAPPER: IdMapper | None = None


def mapper() -> IdMapper:
    global _MAPPER
    if _MAPPER is None:
        _MAPPER = IdMapper()
    return _MAPPER


def _ok(h) -> bool:
    return isinstance(h, str) and h != ""


def _map_col(values, fn) -> tuple[list, Counter]:
    out, c = [], Counter()
    cache = {}
    for v in values:
        if v not in cache:
            cache[v] = fn(v)
        h = cache[v]
        out.append(h)
        c["mapped" if h else "unmapped"] += 1
    return out, c


def _id_qc(raw_ids, mapped_ids) -> dict:
    raw = pd.Series(list(raw_ids)).dropna().astype(str)
    raw = raw[raw != ""]
    u = raw.unique()
    m = pd.Series(list(mapped_ids))
    return {"distinct_source_ids": int(len(u)), "distinct_hgnc_mapped": int(m.dropna().nunique())}


# ============================================================================================== xlsx (streaming)
def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _col_index(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx(path: str, sheet: str | int = 0, header: int = 0, max_rows: int | None = None) -> pd.DataFrame:
    """Streaming xlsx reader that works for transitional AND strict OOXML workbooks (namespaces are ignored; only
    cells with values are visited, so 'A1:XFD...' dimensions cost nothing). ``sheet``: sheet name or 0-based
    position in workbook order. Values: shared/inline strings as str, numbers as float, booleans as str, errors as
    NaN. Row ``header`` (0-based among non-empty rows) gives column names; columns without a header are dropped."""
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    sheets = [(s.get("name"), [v for k, v in s.attrib.items() if _local(k) == "id"][0])
              for s in wb.iter() if _local(s.tag) == "sheet"]
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels.iter() if _local(r.tag) == "Relationship"}
    if isinstance(sheet, int):
        name, rid = sheets[sheet]
    else:
        name, rid = next((n, r) for n, r in sheets if n == sheet)
    t = target[rid].lstrip("/")
    sheet_path = t if t.startswith("xl/") else "xl/" + t
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        with z.open("xl/sharedStrings.xml") as f:
            for ev, el in ET.iterparse(f, events=("end",)):
                if _local(el.tag) == "si":
                    ss.append("".join(x.text or "" for x in el.iter() if _local(x.tag) == "t"))
                    el.clear()
    rows = []
    with z.open(sheet_path) as f:
        for ev, el in ET.iterparse(f, events=("end",)):
            if _local(el.tag) != "row":
                continue
            row = {}
            for c in el:
                if _local(c.tag) != "c":
                    continue
                typ = c.get("t")
                v = None
                if typ == "inlineStr":
                    v = "".join(x.text or "" for x in c.iter() if _local(x.tag) == "t")
                else:
                    ve = next((x for x in c if _local(x.tag) == "v"), None)
                    if ve is None or ve.text is None:
                        continue
                    if typ == "s":
                        v = ss[int(ve.text)]
                    elif typ in ("str", "b"):
                        v = ve.text
                    elif typ == "e":
                        v = np.nan
                    else:
                        try:
                            v = float(ve.text)
                        except ValueError:
                            v = ve.text
                row[_col_index(c.get("r"))] = v
            el.clear()
            if row:
                rows.append(row)
            if max_rows is not None and len(rows) > max_rows + header:
                break
    hdr = rows[header]
    used = set()
    for r in rows[header + 1:]:
        used.update(r)
    cols = sorted(c for c in hdr if c in used)    # header cells without any data (e.g. table 'ColumnN') dropped
    data = [[r.get(c, np.nan) for c in cols] for r in rows[header + 1:]]
    df = pd.DataFrame(data, columns=[str(hdr[c]) for c in cols])
    df.attrs["sheet"] = name
    return df


# ============================================================================================ correlation helpers
def masked_pearson(X: np.ndarray, min_n: int, block: int = 1024) -> tuple[np.ndarray, np.ndarray]:
    """Pairwise-complete Pearson r between the rows of X (genes x samples, NaN = missing). Returns (r float32 with
    NaN where n < min_n or a variance is 0, n_shared int32). Diagonal NaN."""
    X = np.asarray(X, dtype=np.float64)
    M = np.isfinite(X).astype(np.float64)
    X0 = np.where(M > 0, X, 0.0)
    X2 = X0 * X0
    G = X.shape[0]
    R = np.full((G, G), np.nan, dtype=np.float32)
    N = np.zeros((G, G), dtype=np.int32)
    for s in range(0, G, block):
        sl = slice(s, s + block)
        n = M[sl] @ M.T
        sx = X0[sl] @ M.T
        sy = M[sl] @ X0.T
        sxx = X2[sl] @ M.T
        syy = M[sl] @ X2.T
        sxy = X0[sl] @ X0.T
        with np.errstate(invalid="ignore", divide="ignore"):
            num = n * sxy - sx * sy
            den = np.sqrt(np.clip(n * sxx - sx * sx, 0, None) * np.clip(n * syy - sy * sy, 0, None))
            r = num / den
        r[(n < min_n) | ~np.isfinite(r)] = np.nan
        R[sl] = r.astype(np.float32)
        N[sl] = n.astype(np.int32)
    np.fill_diagonal(R, np.nan)
    return R, N


def pearson_excluding_own(X: np.ndarray, own_feature: np.ndarray, block: int = 1024) -> np.ndarray:
    """Pearson r between rows of X (perturbations x features, complete) where, for the pair (i, j), the features
    own_feature[i] and own_feature[j] (index of the perturbed gene's own transcript among the features; -1 if not
    measured) are removed from BOTH profiles (DESIGN §5.1b: own and partner transcripts excluded). Exact, via
    sum corrections. Diagonal NaN."""
    X = np.asarray(X, dtype=np.float64)
    P, F = X.shape
    has = own_feature >= 0
    fi = np.where(has, own_feature, 0)
    Gx = X[:, fi] * has[None, :]          # Gx[i, j] = x_i[f_j] (0 if gene j's transcript not measured)
    S = X.sum(1)
    SS = (X * X).sum(1)
    diag = np.diag(Gx).copy()             # x_i[f_i]
    R = np.full((P, P), np.nan, dtype=np.float32)
    for s in range(0, P, block):
        sl = slice(s, s + block)
        ii = np.arange(s, min(s + block, P))
        gij = Gx[sl]                       # x_i[f_j]
        gji = Gx[:, sl].T                  # x_j[f_i]  (rows i, cols j)
        gii = diag[sl][:, None]            # x_i[f_i]
        gjj = diag[None, :]                # x_j[f_j]
        n = F - has[sl][:, None].astype(np.float64) - has[None, :].astype(np.float64)
        sx = S[sl][:, None] - gii - gij
        sxx = SS[sl][:, None] - gii ** 2 - gij ** 2
        sy = S[None, :] - gjj - gji
        syy = SS[None, :] - gjj ** 2 - gji ** 2
        sxy = X[sl] @ X.T - gii * gji - gij * gjj
        with np.errstate(invalid="ignore", divide="ignore"):
            r = (n * sxy - sx * sy) / np.sqrt(np.clip(n * sxx - sx ** 2, 0, None) * np.clip(n * syy - sy ** 2, 0,
                                                                                          None))
        R[sl] = r.astype(np.float32)
        R[ii, ii] = np.nan
    return R


def _cache_path(name: str) -> str:
    os.makedirs(DERIVED, exist_ok=True)
    return os.path.join(DERIVED, name)


def _save_continuous(src: Source, name: str):
    np.save(_cache_path(name + ".mat.npy"), src.mat)
    meta = dict(genes=src.genes, qc=src.qc, meta=src.meta,
                strength=None if src.strength is None else [float(x) for x in src.strength])
    with open(_cache_path(name + ".json"), "w") as f:
        json.dump(meta, f)


def _load_continuous(name: str, cls: str, independent=True) -> Source | None:
    p, j = _cache_path(name + ".mat.npy"), _cache_path(name + ".json")
    if not (os.path.exists(p) and os.path.exists(j)):
        return None
    with open(j) as f:
        meta = json.load(f)
    s = Source(name=name, cls=cls, kind="continuous", independent=independent, genes=meta["genes"],
               mat=np.load(p, mmap_mode="r"), qc=meta["qc"], meta=meta["meta"])
    if meta.get("strength") is not None:
        s.strength = np.asarray(meta["strength"])
    return s


# ================================================================================================ P: physical
def load_bioplex(m: IdMapper | None = None) -> Source:
    """BioPlex 3.0, 293T and HCT116 networks; edge if present in either line (§5.1b); measured = node in either.
    IDs: Entrez (GeneA/GeneB), UniProt fallback."""
    m = m or mapper()
    frames, qc = [], {}
    for line, f in (("293T", "BioPlex_293T_Network_10K_Dec_2019.tsv"), ("HCT116", "BioPlex_HCT116_Network_5.5K_Dec_2019.tsv")):
        d = pd.read_csv(os.path.join(RAW, "bioplex", f), sep="\t", dtype=str)
        for side in "AB":
            ent = d[f"Gene{side}"].map(m.from_entrez)
            acc = d[f"Uniprot{side}"].map(m.from_acc)
            d[side.lower()] = ent.where(ent.notna(), acc)
            qc[f"{line}_{side}_entrez_mapped"] = int(ent.notna().sum())
            qc[f"{line}_{side}_uniprot_fallback"] = int((ent.isna() & acc.notna()).sum())
        qc[f"{line}_rows"] = len(d)
        qc[f"{line}_rows_unmapped"] = int((d.a.isna() | d.b.isna()).sum())
        qc[f"{line}_distinct_entrez"] = int(pd.concat([d.GeneA, d.GeneB]).nunique())
        frames.append(d[["a", "b"]].dropna())
    pairs = pd.concat(frames).drop_duplicates()
    return edges_to_source("BioPlex3", "P", pairs, qc=qc,
                           meta=dict(measured="node in the 293T or HCT116 network", edge="edge in either line"))


def load_opencell_ppi(m: IdMapper | None = None) -> Source:
    """OpenCell reported interactions (target / interactor ENSG)."""
    m = m or mapper()
    d = pd.read_csv(os.path.join(RAW, "opencell", "opencell-protein-interactions.csv"), dtype=str)
    d["a"] = d.target_ensg_id.map(m.from_ensg)
    d["b"] = d.interactor_ensg_id.map(m.from_ensg)
    qc = {}
    for side, ens, sym, accs in (("a", "target_ensg_id", "target_gene_name", None),
                                 ("b", "interactor_ensg_id", "interactor_gene_name", "interactor_uniprot_ids")):
        miss = d[side].isna()
        qc[f"{side}_ensg_mapped"] = int((~miss).sum())
        if accs:
            def acc_fb(x):
                hs = {m.from_acc(a) for a in str(x).split(";") if m.acc_status(a) == "mapped"}
                return next(iter(hs)) if len(hs) == 1 else None
            fb = d.loc[miss, accs].map(acc_fb)
            d.loc[miss, side] = fb
            qc[f"{side}_uniprot_fallback"] = int(fb.notna().sum())
            miss = d[side].isna()
        fs = d.loc[miss, sym].map(lambda x: m.from_symbol(x)[0])
        d.loc[miss, side] = fs
        qc[f"{side}_symbol_fallback"] = int(fs.notna().sum())
    qc.update(rows=len(d), rows_unmapped=int((d.a.isna() | d.b.isna()).sum()),
              **_id_qc(pd.concat([d.target_ensg_id, d.interactor_ensg_id]), pd.concat([d.a, d.b])))
    return edges_to_source("OpenCell_PPI", "P", d[["a", "b"]].dropna().drop_duplicates(), qc=qc,
                           meta=dict(measured="node (target or interactor)", edge="reported interaction"))


def load_biogrid_ltp(m: IdMapper | None = None) -> Source:
    """BioGRID 5.0.262 physical, human-human, Throughput == 'Low Throughput' only (non-HTP). IDs: Entrez."""
    m = m or mapper()
    cols = ["Entrez Gene Interactor A", "Entrez Gene Interactor B", "Experimental System Type",
            "Organism ID Interactor A", "Organism ID Interactor B", "Throughput"]
    d = pd.read_csv(os.path.join(RAW, "biogrid", "BIOGRID-ORGANISM-Homo_sapiens-5.0.262.tab3.txt"), sep="\t",
                    usecols=cols, dtype=str)
    qc = dict(rows=len(d))
    d = d[(d["Experimental System Type"] == "physical") & (d["Organism ID Interactor A"] == "9606") &
          (d["Organism ID Interactor B"] == "9606")]
    qc["rows_physical_human"] = len(d)
    qc["throughput_values"] = dict(Counter(d.Throughput))
    d = d[d.Throughput == "Low Throughput"].copy()
    qc["rows_low_throughput"] = len(d)
    d["a"] = d["Entrez Gene Interactor A"].map(m.from_entrez)
    d["b"] = d["Entrez Gene Interactor B"].map(m.from_entrez)
    qc["rows_unmapped"] = int((d.a.isna() | d.b.isna()).sum())
    qc.update(_id_qc(pd.concat([d["Entrez Gene Interactor A"], d["Entrez Gene Interactor B"]]),
                     pd.concat([d.a, d.b])))
    return edges_to_source("BioGRID_LTP", "P", d[["a", "b"]].dropna().drop_duplicates(), qc=qc,
                           meta=dict(measured="node in a low-throughput physical interaction",
                                     edge="physical, Throughput = Low Throughput"))


def load_string_experiments(m: IdMapper | None = None, min_score: int | None = None) -> Source:
    """STRING v12.5 physical.links.detailed, experimental channel >= 400 (§5.1b). Measured = protein with any
    experimental score > 0. ENSP -> HGNC via STRING aliases."""
    m = m or mapper()
    min_score = min_score if min_score is not None else fz("orthogonal", "string_experiments_min")
    d = pd.read_csv(os.path.join(RAW, "string", "9606.protein.physical.links.detailed.v12.5.txt.gz"), sep=" ",
                    usecols=["protein1", "protein2", "experimental"])
    ensp, _, route = m.ensp_map()
    qc = dict(rows_directed=len(d), ensp_route=route)
    d = d[d.experimental > 0]
    d["a"] = d.protein1.map(ensp)
    d["b"] = d.protein2.map(ensp)
    qc["proteins_with_exp"] = int(pd.concat([d.protein1, d.protein2]).nunique())
    qc["proteins_with_exp_unmapped"] = int(pd.concat([d.protein1[d.a.isna()], d.protein2[d.b.isna()]]).nunique())
    measured = set(d.a.dropna()) | set(d.b.dropna())
    e = d[d.experimental >= min_score]
    qc["rows_directed_ge_min"] = len(e)
    return edges_to_source("STRING_exp", "P", e[["a", "b"]].dropna().drop_duplicates(), measured=measured, qc=qc,
                           meta=dict(measured="protein with experimental score > 0",
                                     edge=f"experimental >= {min_score}"))


def load_hcm_saint(m: IdMapper | None = None, bfdr_max: float | None = None) -> Source:
    """Human Cell Map SAINTexpress bait-prey table; edge if BFDR <= 0.01 (§5.1b). Measured = baits + every prey in
    the table. Bait -> HGNC via the baits table HGNC column (bait names carry suffixes); prey RefSeq protein ->
    STRING RefSeq alias -> HGNC; prey symbol fallback (recorded)."""
    m = m or mapper()
    bfdr_max = bfdr_max if bfdr_max is not None else fz("orthogonal", "hcm_saint_bfdr_max")
    d = pd.read_csv(os.path.join(RAW, "humancellmap", "saint-latest.txt"), sep="\t",
                    usecols=["Bait", "Prey", "PreyGene", "BFDR"], dtype={"BFDR": float})
    b = pd.read_csv(os.path.join(RAW, "humancellmap", "baits-latest.txt"), sep="\t", dtype=str)
    bait_map = {}
    for nm, h, e in zip(b.bait, b.HGNC, b.Entrez):
        hh = m.from_hgnc(h) or m.from_entrez(e)
        if hh:
            bait_map[nm] = hh
    _, refseq, _ = m.ensp_map()

    def prey(rs):
        hs = refseq.get(str(rs).split(".")[0])
        return next(iter(hs)) if hs and len(hs) == 1 else None

    d["a"] = d.Bait.map(bait_map)
    d["b"] = d.Prey.map(prey)
    fb = d.b.isna()
    sym = d.loc[fb, "PreyGene"].map(lambda s: m.from_symbol(s)[0])
    d.loc[fb, "b"] = sym
    qc = dict(rows=len(d), baits=int(d.Bait.nunique()), baits_unmapped=sorted(set(d.Bait[d.a.isna()])),
              prey_refseq_distinct=int(d.Prey.nunique()), prey_rows_refseq_mapped=int((~fb).sum()),
              prey_rows_symbol_fallback=int(sym.notna().sum()), prey_rows_unmapped=int(d.b.isna().sum()))
    measured = set(d.a.dropna()) | set(d.b.dropna())
    e = d[d.BFDR <= bfdr_max]
    qc["rows_bfdr_ok"] = len(e)
    return edges_to_source("HCM_SAINT", "P", e[["a", "b"]].dropna().drop_duplicates(), measured=measured, qc=qc,
                           meta=dict(measured="bait or any prey in the SAINT table", edge=f"BFDR <= {bfdr_max}"))


def union_sources(name: str, cls: str, sources: list[Source], meta=None) -> Source:
    """Union of binary sources (edges and measured genes). Used for the §5.1b P source group (BioGRID, BioPlex,
    OpenCell and STRING experiments counted as one source)."""
    genes = sorted(set().union(*[set(s.genes) for s in sources]))
    idx = {g: k for k, g in enumerate(genes)}
    ii, jj = [], []
    for s in sources:
        c = s.adj.tocoo()
        gmap = np.array([idx[g] for g in s.genes])
        ii.append(gmap[c.row])
        jj.append(gmap[c.col])
    adj = symmetric_csr(np.concatenate(ii), np.concatenate(jj), len(genes))
    out = Source(name=name, cls=cls, kind="binary", genes=genes, adj=adj,
                 meta=meta or {"components": [s.name for s in sources]})
    out.qc.update(measured_genes=len(genes), edges=out.n_edges(), components=[s.name for s in sources])
    return out


# ============================================================================================ A: co-abundance
def load_proteomehd(m: IdMapper | None = None, cache: bool = True) -> Source:
    """ProteomeHD v1.1 co-regulation scores. Protein groups (';'-separated UniProt ACCs incl. isoforms) are mapped
    to genes: a group maps to the gene(s) of its accessions (isoform suffix stripped); groups mapping to > 1 gene are
    dropped (counted). Gene-pair score = max over the gene's groups. Row percentiles are computed downstream."""
    name = "ProteomeHD"
    if cache:
        s = _load_continuous(name, "A")
        if s is not None:
            return s
    m = m or mapper()
    with zipfile.ZipFile(os.path.join(RAW, "proteomehd", "coregulation_scores.zip")) as z:
        d = pd.read_csv(z.open("coregulation_scores.csv"), dtype={"Protein_1": str, "Protein_2": str,
                                                                    "coregulation_score": np.float64})
    groups = pd.unique(pd.concat([d.Protein_1, d.Protein_2]))
    gmap, st = {}, Counter()
    for g in groups:
        hs = set()
        amb = False
        for a in g.split(";"):
            s_ = m.acc_status(a)
            if s_ == "mapped":
                hs.add(m.from_acc(a))
            elif s_ == "ambiguous":
                amb = True
        if len(hs) == 1 and not amb:
            gmap[g] = next(iter(hs))
            st["group_mapped"] += 1
        elif len(hs) > 1 or amb:
            st["group_multi_gene_dropped"] += 1
        else:
            st["group_unmapped"] += 1
    genes = sorted(set(gmap.values()))
    idx = {g: k for k, g in enumerate(genes)}
    gi = d.Protein_1.map(gmap).map(idx)
    gj = d.Protein_2.map(gmap).map(idx)
    ok = gi.notna() & gj.notna()
    i, j, v = gi[ok].astype(int).values, gj[ok].astype(int).values, d.coregulation_score[ok].values
    M = np.full((len(genes), len(genes)), -np.inf)
    np.maximum.at(M, (i, j), v)
    np.maximum.at(M, (j, i), v)
    M[np.isinf(M)] = np.nan
    np.fill_diagonal(M, np.nan)
    qc = dict(pairs=len(d), protein_groups=len(groups), **st, genes=len(genes),
              genes_with_multiple_groups=int(pd.Series(list(gmap.values())).duplicated().sum()),
              pair_rows_used=int(ok.sum()))
    s = Source(name=name, cls="A", kind="continuous", genes=genes, mat=M.astype(np.float32), qc=qc,
               meta=dict(score="coregulation_score (max over protein groups)", measured="gene with a mapped group"))
    _save_continuous(s, name)
    return s


def _ccle_table(cache: bool = True) -> pd.DataFrame:
    p = _cache_path("ccle_proteomics_raw.pkl")
    if cache and os.path.exists(p):
        return pd.read_pickle(p)
    df = read_xlsx(os.path.join(RAW, "ccle_proteomics", "protein_quant_current_normalized.xlsx"),
                   sheet="Normalized Protein Expression")
    df.to_pickle(p)
    return df


def load_ccle_proteomics(m: IdMapper | None = None, cache: bool = True, min_lines: int | None = None) -> Source:
    """CCLE proteomics (Nusinow 2020) normalised protein expression. Key Uniprot_Acc (§5.1b); line columns
    '<CCLEName>_TenPxNN' mapped to ModelID via DepMap Model.csv CCLEName; replicate columns of one ModelID averaged
    before the >= 50-line rule; several protein rows of one gene -> the row with most non-missing lines. Pearson r,
    pairwise complete >= 50 lines. Flagged: lines are shared with DepMap (§5.1)."""
    name = "CCLE_proteomics"
    if cache:
        s = _load_continuous(name, "A")
        if s is not None:
            return s
    m = m or mapper()
    min_lines = min_lines or fz("orthogonal", "ccle_proteomics_min_lines")
    df = _ccle_table(cache)
    line_cols = [c for c in df.columns if re.search(r"_TenPx\d+$", c)]
    model = pd.read_csv(os.path.join(RAW, "depmap", "Model.csv"), usecols=["ModelID", "CCLEName"], dtype=str)
    ccle2model = {}
    for mid, cn in zip(model.ModelID, model.CCLEName):
        if isinstance(cn, str) and cn:
            ccle2model.setdefault(cn, set()).add(mid)
    colmodel, unm, amb = {}, [], []
    for c in line_cols:
        cn = re.sub(r"_TenPx\d+$", "", c)
        ms = ccle2model.get(cn)
        if not ms:
            unm.append(c)
        elif len(ms) > 1:
            amb.append(c)
        else:
            colmodel[c] = next(iter(ms))
    X = df[list(colmodel)].apply(pd.to_numeric, errors="coerce")
    X.columns = [colmodel[c] for c in colmodel]
    n_rep = pd.Series(X.columns).value_counts()
    X = X.T.groupby(level=0).mean().T     # collapse replicate columns per ModelID
    acc = df["Uniprot_Acc"].astype(str)
    st = Counter(acc.map(m.acc_status))
    gene = acc.map(m.from_acc)
    X["__gene"] = gene.values
    X["__n"] = X.drop(columns="__gene").notna().sum(1).values
    X = X[X.__gene.notna()].sort_values(["__gene", "__n"], ascending=[True, False])
    n_rows_per_gene = X.__gene.value_counts()
    X = X.drop_duplicates("__gene")
    genes = list(X.__gene)
    V = X.drop(columns=["__gene", "__n"]).values.astype(np.float64)
    R, N = masked_pearson(V, min_n=min_lines)
    qc = dict(protein_rows=len(df), line_columns=len(line_cols), line_columns_mapped=len(colmodel),
              line_columns_unmapped=unm, line_columns_ambiguous=amb, models=int(V.shape[1]),
              models_with_replicates=int((n_rep > 1).sum()), uniprot_acc_status=dict(st), genes=len(genes),
              genes_with_multiple_protein_rows=int((n_rows_per_gene > 1).sum()),
              pairs_computable_fraction=float(np.isfinite(R).mean()))
    s = Source(name=name, cls="A", kind="continuous", genes=genes, mat=R, qc=qc,
               meta=dict(score=f"Pearson r, pairwise complete >= {min_lines} lines", flagged="lines shared with DepMap"))
    _save_continuous(s, name)
    return s


# =============================================================================================== L: localisation
def localisation_map(path: str = LOC_MAP_TSV) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", comment="#", dtype=str, keep_default_na=False)


def _label_map(source: str) -> dict:
    lm = localisation_map()
    lm = lm[lm.source == source]
    return {l: frozenset(c.split("|")) if c else frozenset() for l, c in zip(lm.label, lm.compartment)}


def _labels_to_comp(labels, lab: dict, unknown: Counter) -> frozenset:
    out = set()
    for l in labels:
        l = l.strip()
        if not l:
            continue
        if l not in lab:
            unknown[l] += 1
            continue
        out |= lab[l]
    return frozenset(out)


def compartments_match(a, b) -> bool:
    """Two compartment sets match if they share a compartment after adding parents (nucleolus, nuclear envelope ->
    nucleus)."""
    if not a or not b:
        return False
    ea = set(a) | {COMPARTMENT_PARENT[x] for x in a if x in COMPARTMENT_PARENT}
    eb = set(b) | {COMPARTMENT_PARENT[x] for x in b if x in COMPARTMENT_PARENT}
    # a child matches its parent, not its sibling: compare each original against the other's expanded set
    return bool(set(a) & eb) or bool(set(b) & ea)


def n_distinct_compartments(c) -> int:
    """Compartment count for the multi-localisation rule (nucleolus / nuclear envelope collapsed into nucleus)."""
    return len({COMPARTMENT_PARENT.get(x, x) for x in c})


def _loc_source(name, comp: dict, comp_hr: dict, qc: dict, meta: dict) -> Source:
    comp = {g: c for g, c in comp.items() if c}
    comp_hr = {g: c for g, c in comp_hr.items() if c}
    s = Source(name=name, cls="L", kind="localisation", genes=sorted(comp), comp=comp, comp_hr=comp_hr, qc=qc,
               meta=meta)
    s.qc.update(genes_with_compartment=len(comp), genes_high_reliability=len(comp_hr),
                compartment_counts=dict(Counter(x for c in comp.values() for x in c)))
    return s


def load_hpa(m: IdMapper | None = None) -> Source:
    """HPA v25.1 subcellular locations (ENSG). Compartments = locations listed under Enhanced, Supported or Approved
    (Uncertain excluded); high-reliability (§5.3) = locations under Enhanced or Supported."""
    m = m or mapper()
    with zipfile.ZipFile(os.path.join(RAW, "hpa", "subcellular_location.tsv.zip")) as z:
        d = pd.read_csv(z.open("subcellular_location.tsv"), sep="\t", dtype=str, keep_default_na=False)
    lab, unk = _label_map("HPA"), Counter()
    d["h"] = d.Gene.map(m.from_ensg)
    comp, hr = {}, {}
    for h, e, s_, a in zip(d.h, d.Enhanced, d.Supported, d.Approved):
        if not _ok(h):
            continue
        hrl = [x for x in (e + ";" + s_).split(";") if x]
        al = hrl + [x for x in a.split(";") if x]
        comp[h] = _labels_to_comp(al, lab, unk)
        hr[h] = _labels_to_comp(hrl, lab, unk)
    qc = dict(rows=len(d), rows_unmapped=int(d.h.isna().sum()), reliability=dict(Counter(d.Reliability)),
              unknown_labels=dict(unk))
    return _loc_source("HPA", comp, hr, qc, dict(levels="Enhanced+Supported+Approved", high_reliability="Enhanced+Supported"))


def load_opencell_loc(m: IdMapper | None = None) -> Source:
    """OpenCell localisation annotations (ENSG); grades 3 and 2 used (grade 1 = weakest, excluded). All OpenCell
    calls count as high-reliability (§5.3)."""
    m = m or mapper()
    d = pd.read_csv(os.path.join(RAW, "opencell", "opencell-localization-annotations.csv"), dtype=str,
                    keep_default_na=False)
    lab, unk = _label_map("OpenCell"), Counter()
    d["h"] = d.ensg_id.map(m.from_ensg)
    comp = {}
    for h, g3, g2 in zip(d.h, d.annotations_grade_3, d.annotations_grade_2):
        if _ok(h):
            comp[h] = _labels_to_comp((g3 + ";" + g2).split(";"), lab, unk)
    qc = dict(rows=len(d), rows_unmapped=int(d.h.isna().sum()), unknown_labels=dict(unk))
    return _loc_source("OpenCell_loc", comp, dict(comp), qc, dict(levels="grade 3 + grade 2"))


def load_hcm_nmf(m: IdMapper | None = None) -> Source:
    """Human Cell Map NMF localisation of preys (column 'MMF localization' = NMF compartment names; HGNC id, Entrez
    fallback). All calls count as high-reliability (§5.3)."""
    m = m or mapper()
    d = pd.read_csv(os.path.join(RAW, "humancellmap", "preys-latest.txt"), sep="\t", dtype=str, keep_default_na=False)
    lab, unk = _label_map("HCM_NMF"), Counter()
    hh = [m.from_hgnc(h) or m.from_entrez(e) for h, e in zip(d.HGNC, d.Entrez)]
    comp = {}
    for h, l in zip(hh, d["MMF localization"]):
        if h:
            comp[h] = _labels_to_comp(l.split(","), lab, unk)
    qc = dict(rows=len(d), rows_unmapped=int(sum(h is None for h in hh)), unknown_labels=dict(unk))
    return _loc_source("HCM_NMF", comp, dict(comp), qc, dict(levels="NMF compartment ('MMF localization')"))


def load_mitocarta(m: IdMapper | None = None) -> Source:
    """MitoCarta3.0 (sheet 'B Human All Genes', HumanGeneID = Entrez): listed genes -> {mitochondrion}. Positive
    calls only (absence is not a localisation); ``meta['assessed']`` = all genes of sheet B."""
    import xlrd
    m = m or mapper()
    b = xlrd.open_workbook(os.path.join(RAW, "mitocarta", "Human.MitoCarta3.0.xls")).sheet_by_name("B Human All Genes")
    hdr = b.row_values(0)
    rows = [b.row_values(i) for i in range(1, b.nrows)]
    d = pd.DataFrame(rows, columns=hdr)
    ent = d.HumanGeneID.map(lambda x: str(int(x)) if isinstance(x, float) else str(x))
    d["h"] = ent.map(m.from_entrez)
    d["listed"] = d["MitoCarta3.0_List"].astype(str).str.strip() == "MitoCarta3.0"   # 0 / 'mito-interacting' = not listed
    lab = _label_map("MitoCarta")
    comp = {h: lab["MitoCarta3.0"] for h, l in zip(d.h, d.listed) if _ok(h) and l}
    qc = dict(rows=len(d), listed=int(d.listed.sum()), rows_unmapped=int(d.h.isna().sum()),
              listed_unmapped=int((d.h.isna() & d.listed).sum()))
    s = _loc_source("MitoCarta3", comp, dict(comp), qc, dict(levels="MitoCarta3.0 list (positive calls only)"))
    s.meta["assessed"] = sorted(set(d.h.dropna()))
    return s


# ======================================================================================= G: perturbation phenotype
PERTURBSEQ_FILES = {"PerturbSeq_K562_GW": "K562_gwps_normalized_bulk_01.h5ad",
                    "PerturbSeq_K562_essential": "K562_essential_normalized_bulk_01.h5ad",
                    "PerturbSeq_RPE1_essential": "rpe1_normalized_bulk_01.h5ad"}


def _h5_str(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def _h5_col(grp, k):
    import h5py
    v = grp[k]
    if isinstance(v, h5py.Dataset):
        return v[:]
    cats = _h5_str(v["categories"][:])
    return cats[v["codes"][:]]


def load_perturbseq(name: str = "PerturbSeq_K562_GW", m: IdMapper | None = None, cache: bool = True,
                    kd_min: float | None = None, min_cells: int | None = None) -> Source:
    """Replogle 2022 pseudo-bulk z-normalised profiles (h5ad read with h5py). A perturbation counts if on-target
    knockdown >= 30% (1 - fold_expr >= kd_min; fold_expr NaN = not reported -> excluded) and >= 25 cells
    (num_cells_filtered). Perturbed gene from the ENSG in gene_transcript; if a gene has several qualifying
    perturbations, the one with the strongest knockdown is kept. Pair score = Pearson r of the two profiles with both
    perturbed genes' own transcripts removed (§5.1b). Phenotype strength = profile RMS (null matching)."""
    if cache:
        s = _load_continuous(name, "G")
        if s is not None:
            return s
    import h5py
    m = m or mapper()
    kd_min = kd_min if kd_min is not None else fz("orthogonal", "perturbseq_knockdown_min")
    min_cells = min_cells if min_cells is not None else fz("orthogonal", "perturbseq_min_cells")
    with h5py.File(os.path.join(RAW, "replogle2022_perturbseq", PERTURBSEQ_FILES[name]), "r") as h:
        obs = h["obs"]
        gt = _h5_str(_h5_col(obs, "gene_transcript"))
        fold = np.asarray(_h5_col(obs, "fold_expr"), dtype=float)
        ncell = np.asarray(_h5_col(obs, "num_cells_filtered"), dtype=float)
        core = np.asarray(_h5_col(obs, "core_control")).astype(str)
        var = h["var"]
        var_ids = _h5_str(var[var.attrs["_index"]][:])
        X = h["X"][:]
    ensg = np.array([t.split("_")[-1] if t.split("_")[-1].startswith("ENSG") else "" for t in gt])
    hg = np.array([m.from_ensg(e) or "" for e in ensg])
    kd = 1 - fold
    ok_kd = np.isfinite(kd) & (kd >= kd_min)
    ok_cells = ncell >= min_cells
    is_ctrl = np.array([("non-targeting" in t) for t in gt]) | (core == "True")
    keep = (hg != "") & ok_kd & ok_cells & ~is_ctrl
    qc = dict(perturbations=len(gt), controls=int(is_ctrl.sum()), ensg_parsed=int((ensg != "").sum()),
              mapped=int((hg != "").sum()), knockdown_reported=int(np.isfinite(kd).sum()),
              knockdown_ge_min=int(ok_kd.sum()), cells_ge_min=int(ok_cells.sum()), passing=int(keep.sum()),
              features=len(var_ids), X_nan_fraction=float(np.isnan(X).mean()))
    cand = pd.DataFrame(dict(row=np.where(keep)[0], h=hg[keep], kd=kd[keep])).sort_values(["h", "kd"],
                                                                                          ascending=[True, False])
    qc["genes_with_multiple_perturbations"] = int(cand.h.duplicated().sum())
    cand = cand.drop_duplicates("h")
    genes = list(cand.h)
    rows = cand.row.values
    fin_feat = np.isfinite(X).all(0)               # features with any inf/NaN (zero control variance) dropped
    qc["features_nonfinite_dropped"] = int((~fin_feat).sum())
    var_ids = var_ids[fin_feat]
    Xp = X[rows][:, fin_feat].astype(np.float64)
    feat_idx = {e: k for k, e in enumerate(var_ids)}
    own = np.array([feat_idx.get(e, -1) for e in ensg[rows]])
    qc["own_transcript_measured"] = int((own >= 0).sum())
    R = pearson_excluding_own(Xp, own)
    strength = np.sqrt((Xp ** 2).mean(1))
    qc["genes"] = len(genes)
    s = Source(name=name, cls="G", kind="continuous", genes=genes, mat=R, strength=strength, qc=qc,
               meta=dict(score="Pearson r of pseudo-bulk z profiles, own+partner transcripts removed",
                         filters=f"knockdown >= {kd_min}, cells >= {min_cells}"))
    _save_continuous(s, name)
    return s


def read_olivieri(path: str | None = None) -> pd.DataFrame:
    """Olivieri 2020 Table S2 'Zscores_28screens' (strict OOXML; openpyxl/pandas cannot open it) -> DataFrame
    [Gene, 28 screen columns] via the streaming reader."""
    path = path or os.path.join(RAW, "olivieri2020", "biorxiv_845446_TableS2_NormZ_media-2.xlsx")
    return read_xlsx(path, sheet=0)


def load_olivieri(m: IdMapper | None = None, cache: bool = True, min_shared: int | None = None) -> Source:
    """Olivieri 2020 chemogenomic NormZ profiles (28 screens, RPE1-hTERT TP53-/-); symbols only (no ID in the
    table) -> approved/previous/alias symbol rule with ambiguity dropped. Pair score = Pearson r across screens,
    >= 10 shared screens (§5.1b)."""
    name = "Olivieri2020"
    if cache:
        s = _load_continuous(name, "G")
        if s is not None:
            return s
    m = m or mapper()
    min_shared = min_shared or fz("orthogonal", "chemogenomic_min_shared_screens")
    d = read_olivieri()
    gcol = d.columns[0]
    screens = [c for c in d.columns[1:]]
    mp = d[gcol].map(m.from_symbol)
    d["h"] = mp.map(lambda x: x[0])
    route = Counter(mp.map(lambda x: x[1]))
    d = d[d.h.notna()]
    dup = int(d.h.duplicated().sum())
    d = d.drop_duplicates("h", keep=False)      # two symbols -> one gene: ambiguous, drop both
    V = d[screens].apply(pd.to_numeric, errors="coerce").values
    R, N = masked_pearson(V, min_n=min_shared)
    genes = list(d.h)
    qc = dict(rows=int(len(mp)), screens=len(screens), symbol_route=dict(route), genes_collapsing_dropped=dup,
              genes=len(genes))
    s = Source(name=name, cls="G", kind="continuous", genes=genes, mat=R, qc=qc,
               meta=dict(score=f"Pearson r across screens, >= {min_shared} shared", sheet="Zscores_28screens"))
    _save_continuous(s, name)
    return s


# ================================================================================================= S: structure
def load_burke(m: IdMapper | None = None, pdockq_min: float | None = None) -> Source:
    """Burke 2023 AF2 models of HuRI and hu.MAP pairs (UniProt id1/id2). covered = pair modelled; edge = pDockQ >=
    0.23. Null pairs for admission / support are drawn from covered pairs (§5.1b)."""
    m = m or mapper()
    pdockq_min = pdockq_min if pdockq_min is not None else fz("orthogonal", "pdockq_min")
    d = pd.read_csv(os.path.join(RAW, "burke2023_af2", "table_AF2_HURI_HuMap_UNIQUE.csv"),
                    usecols=["id1", "id2", "pDockQ", "Dataset"], dtype={"id1": str, "id2": str})
    d["a"] = d.id1.map(m.from_acc)
    d["b"] = d.id2.map(m.from_acc)
    qc = dict(rows=len(d), rows_unmapped=int((d.a.isna() | d.b.isna()).sum()), datasets=dict(Counter(d.Dataset)))
    d = d.dropna(subset=["a", "b"])
    d = d[d.a != d.b]
    d["pDockQ"] = pd.to_numeric(d.pDockQ, errors="coerce")
    d = d.sort_values("pDockQ", ascending=False).drop_duplicates(subset=["a", "b"])
    genes = sorted(set(d.a) | set(d.b))
    idx = {g: k for k, g in enumerate(genes)}
    i, j = d.a.map(idx).values, d.b.map(idx).values
    cov = symmetric_csr(i, j, len(genes))
    e = (d.pDockQ >= pdockq_min).values
    adj = symmetric_csr(i[e], j[e], len(genes))
    s = Source(name="Burke2023_AF2", cls="S", kind="pair_binary", genes=genes, covered=cov, adj=adj, qc=qc,
               meta=dict(edge=f"pDockQ >= {pdockq_min}", measured="pair modelled (HuRI or hu.MAP)"))
    s.qc.update(genes=len(genes), covered_pairs=int(cov.nnz // 2), edges=int(adj.nnz // 2))
    return s


# ================================================================================================== H: homology
def read_go_cc_or_codes(evidence, aspect=None, m: IdMapper | None = None, path=None) -> pd.DataFrame:
    """Current GAF rows (non-NOT) with the given evidence codes (and aspect), mapped to HGNC ids by accession."""
    from .knownness import read_gaf, is_not_qualified
    m = m or mapper()
    path = path or os.path.join(RAW, "go", "current", "goa_human.gaf.gz")
    g = read_gaf(path)
    g = g[~is_not_qualified(g.qualifier) & g.evidence.isin(evidence)]
    if aspect:
        g = g[g.aspect == aspect]
    g = g.assign(hgnc_id=g.acc.map(m.from_acc))
    return g


def load_homology(m: IdMapper | None = None, obo=None) -> Source:
    """Orthologue-based annotation (IBA, ISO) from the current GAF, propagated over is_a/part_of (reported only)."""
    from .knownness import GoOntology
    m = m or mapper()
    onto = obo or GoOntology.from_obo(os.path.join(RAW, "go", "current", "go-basic.obo"))
    g = read_go_cc_or_codes(HOMOLOGY_EVIDENCE, m=m)
    qc = dict(rows=len(g), rows_unmapped=int(g.hgnc_id.isna().sum()), evidence=dict(Counter(g.evidence)))
    g = g.dropna(subset=["hgnc_id"])
    terms = {}
    for h, ts in g.groupby("hgnc_id").go_id:
        s = set()
        for t in set(ts):
            r, _ = onto.resolve(t)
            if r:
                s |= onto.ancestors(r)
        terms[h] = frozenset(s)
    src = Source(name="Homology_IBA_ISO", cls="H", kind="annotation", genes=sorted(terms), terms=terms, qc=qc,
                 meta=dict(note="reported only"))
    src.qc["genes"] = len(terms)
    return src


# ============================================================================================ not independent
def load_humap(m: IdMapper | None = None) -> Source:
    """hu.MAP 3.0 complex co-membership pairs (UniProt) -- NOT independent (built from BioPlex/OpenCell/etc.);
    reported only."""
    m = m or mapper()
    d = pd.read_csv(os.path.join(RAW, "humap3", "humap3_complex_pairs_20240929.pairsWprob"), sep="\t", header=None,
                    names=["u1", "u2", "p"], dtype={"u1": str, "u2": str})
    d["a"] = d.u1.map(m.from_acc)
    d["b"] = d.u2.map(m.from_acc)
    qc = dict(rows=len(d), rows_unmapped=int((d.a.isna() | d.b.isna()).sum()))
    s = edges_to_source("huMAP3_NI", "NI", d[["a", "b"]].dropna().drop_duplicates(), independent=False, qc=qc,
                        meta=dict(edge="pair within a hu.MAP 3.0 complex", note="not independent; reported only"))
    return s


def load_demeter2(m: IdMapper | None = None) -> Source:
    """DEMETER2 combined RNAi gene dependency (rows 'SYMBOL (ENTREZ)', columns CCLE lines) -> genes x lines profile
    keyed by hgnc_id (Entrez). NOT independent of DepMap; used only for the §4.3 robustness check; no pair scores
    are computed here."""
    m = m or mapper()
    d = pd.read_csv(os.path.join(RAW, "depmap_rnai", "D2_combined_gene_dep_scores.csv"), index_col=0)
    ent = d.index.to_series().str.extract(r"\((\d+)\)\s*$")[0]
    h = ent.map(m.from_entrez)
    qc = dict(rows=len(d), lines=d.shape[1], rows_unmapped=int(h.isna().sum()))
    d = d[h.notna().values]
    d.index = h[h.notna()].values
    qc["duplicated_genes_dropped"] = int(d.index.duplicated().sum())
    d = d[~d.index.duplicated(keep=False)]
    s = Source(name="DEMETER2_NI", cls="NI", kind="profile", independent=False, genes=list(d.index), profile=d,
               qc=qc, meta=dict(note="not independent; §4.3 robustness only; no pair scores"))
    s.qc["genes"] = len(d)
    return s


# =============================================================================================== GO CC helpers
def go_cc_d1(m: IdMapper | None = None, onto=None) -> pd.DataFrame:
    """Current GAF CC rows with D1 evidence codes (non-NOT), resolved GO ids, mapped to HGNC (unique accession)."""
    from .knownness import GoOntology
    m = m or mapper()
    onto = onto or GoOntology.from_obo(os.path.join(RAW, "go", "current", "go-basic.obo"))
    g = read_go_cc_or_codes(D1_EVIDENCE, aspect="C", m=m)
    g = g.dropna(subset=["hgnc_id"]).copy()
    res = {t: onto.resolve(t)[0] for t in g.go_id.unique()}
    g["go_id"] = g.go_id.map(res)
    return g.dropna(subset=["go_id"])


def go_cc_compartments(cc: pd.DataFrame, onto, exclude_refs=LOCALISATION_SELF_REFS) -> dict:
    """gene -> frozenset(compartments) from GO CC rows via the GO_CC priority map in config/localisation_map.tsv."""
    lm = localisation_map()
    lm = lm[lm.source == "GO_CC"].copy()
    lm["priority"] = lm.priority.astype(int)
    order = list(lm.sort_values("priority").itertuples(index=False))
    term_comp = {}

    def comp_of(t):
        if t not in term_comp:
            anc = onto.ancestors(t)
            term_comp[t] = next((r.compartment for r in order if r.label in anc), None)
        return term_comp[t]

    refs_bad = cc.reference.map(lambda r: any(x in exclude_refs for x in str(r).split("|")))
    cc = cc[~refs_bad]
    out = defaultdict(set)
    for h, t in zip(cc.hgnc_id, cc.go_id):
        c = comp_of(t)
        if c:
            out[h].add(c)
    return {h: frozenset(c) for h, c in out.items()}


def complex_gold_standard(m: IdMapper | None = None, onto=None, cc: pd.DataFrame | None = None,
                          size_range=(2, 300), propagate: bool = False) -> tuple[list, dict]:
    """Non-hu.MAP complex gold standard (§5.2): Complex Portal human complexes (expanded participant list; entries
    cross-referenced to hu.MAP with 'identity' excluded) + current GO CC terms under GO:0032991 (root excluded) with
    D1 evidence codes (rows citing hu.MAP papers excluded). Membership of a GO term = genes annotated directly to it
    (``propagate=False``, primary: propagation turns class-level terms such as 'ubiquitin ligase complex' or 'ion
    channel complex' into aggregates of unrelated complexes) or to it or a descendant (``propagate=True``,
    sensitivity). Member sets restricted to the universe, de-duplicated (identical member sets kept once), size
    within ``size_range``.
    Returns (list of (complex_id, frozenset(hgnc))), qc)."""
    from .knownness import GoOntology
    m = m or mapper()
    onto = onto or GoOntology.from_obo(os.path.join(RAW, "go", "current", "go-basic.obo"))
    qc = {}
    cp = pd.read_csv(os.path.join(RAW, "complexportal", "9606.tsv"), sep="\t", dtype=str, keep_default_na=False)
    qc["complexportal_rows"] = len(cp)
    hm = cp["Cross references"].str.contains(r"humap:[^|]*\(identity\)")
    qc["complexportal_humap_identity_excluded"] = int(hm.sum())
    cp = cp[~hm]
    comps, acc_st = [], Counter()
    for cid, part in zip(cp["#Complex ac"], cp["Expanded participant list"]):
        mem = set()
        for tok in part.split("|"):
            a = re.sub(r"\(.*$", "", tok).strip()
            if not re.match(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]|^[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}", a):
                acc_st["non_protein_participant"] += 1
                continue
            st = m.acc_status(a)
            acc_st[st] += 1
            if st == "mapped":
                mem.add(m.from_acc(a))
        comps.append(("CP:" + cid, frozenset(mem)))
    qc["complexportal_participants"] = dict(acc_st)
    cc = cc if cc is not None else go_cc_d1(m, onto)
    hmref = cc.reference.map(lambda r: any(x in HUMAP_REFS for x in str(r).split("|")))
    qc["go_cc_rows_humap_ref_excluded"] = int(hmref.sum())
    cc = cc[~hmref]
    root = "GO:0032991"
    members = defaultdict(set)
    for h, t in zip(cc.hgnc_id, cc.go_id):
        for a in (onto.ancestors(t) if propagate else (t,)):
            if a != root and root in onto.ancestors(a):
                members[a].add(h)
    comps += [("GO:" + t.split(":")[1], frozenset(s)) for t, s in members.items()]
    lo, hi = size_range
    seen, out = set(), []
    n_size = Counter()
    for cid, mem in comps:
        if not (lo <= len(mem) <= hi):
            n_size["outside_size"] += 1
            continue
        if mem in seen:
            n_size["duplicate_member_set"] += 1
            continue
        seen.add(mem)
        out.append((cid, mem))
    qc.update(n_size)
    qc["complexes_kept"] = len(out)
    qc["complexportal_kept"] = sum(c.startswith("CP:") for c, _ in out)
    qc["go_cc_kept"] = sum(c.startswith("GO:") for c, _ in out)
    qc["genes_in_gold_standard"] = len(set().union(*[s for _, s in out]))
    qc["go_membership"] = "propagated" if propagate else "direct"
    return out, qc


# ================================================================================================ registry / QC
LOADERS = {
    "BioPlex3": load_bioplex, "OpenCell_PPI": load_opencell_ppi, "BioGRID_LTP": load_biogrid_ltp,
    "STRING_exp": load_string_experiments, "HCM_SAINT": load_hcm_saint,
    "ProteomeHD": load_proteomehd, "CCLE_proteomics": load_ccle_proteomics,
    "HPA": load_hpa, "OpenCell_loc": load_opencell_loc, "HCM_NMF": load_hcm_nmf, "MitoCarta3": load_mitocarta,
    "PerturbSeq_K562_GW": lambda m=None: load_perturbseq("PerturbSeq_K562_GW", m),
    "PerturbSeq_K562_essential": lambda m=None: load_perturbseq("PerturbSeq_K562_essential", m),
    "PerturbSeq_RPE1_essential": lambda m=None: load_perturbseq("PerturbSeq_RPE1_essential", m),
    "Olivieri2020": load_olivieri, "Burke2023_AF2": load_burke, "Homology_IBA_ISO": load_homology,
    "huMAP3_NI": load_humap, "DEMETER2_NI": load_demeter2,
}
P_GROUP = ("BioPlex3", "OpenCell_PPI", "BioGRID_LTP", "STRING_exp")


def coverage(src: Source, universe=None) -> int:
    g = set(src.genes)
    return len(g & set(universe)) if universe is not None else len(g)


def write_mapping_qc(sources: dict, path: str, m: IdMapper | None = None, extra: dict | None = None):
    m = m or mapper()
    lines = ["# Orthogonal sources -- identifier mapping QC", "",
             "Generated by `scripts/20_source_admission.py` via `src/orthogonal.py` (DESIGN.md v2.3 §2.1, §5.1). Join "
             "keys follow the hub rule: HGNC id > Entrez > ENSG > UniProt (isoform stripped; HGNC uniprot_ids, then "
             "Swiss-Prot HGNC xref) > RefSeq protein via STRING aliases; symbols only where a source has no ID "
             "(Olivieri 2020) or as a counted fallback (Human Cell Map prey). IDs mapping to > 1 universe gene are "
             "dropped. Universe = HGNC Approved protein-coding genes (19,296).", "",
             f"UniProt accession map: {m.acc_stats}.", "",
             "| source | class | kind | genes (measured, universe) | edges / pairs | QC |", "|---|---|---|---|---|---|"]
    for name, s in sources.items():
        e = ""
        if s.kind == "binary":
            e = f"{s.n_edges():,} edges"
        elif s.kind == "pair_binary":
            e = f"{s.qc.get('covered_pairs', 0):,} covered / {s.qc.get('edges', 0):,} edges"
        elif s.kind == "continuous":
            e = f"{len(s.genes):,}^2 matrix"
        qc = {k: v for k, v in s.qc.items() if k not in ("compartment_counts",)}
        qs = "; ".join(f"{k}={v}" for k, v in qc.items())
        lines.append(f"| {name} | {s.cls} | {s.kind} | {len(s.genes):,} | {e} | {qs} |")
    if extra:
        lines += ["", "## Other", ""] + [f"- {k}: {v}" for k, v in extra.items()]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
