"""vocab.py -- the V2 vocabulary (DESIGN.md v2.3 §3.0), per-query membership views and S(g,t) (§3.1, §3.2.1, §8).

V2 for one release (that release's GAF, propagated with the CURRENT obo):
  * GAF rows kept: qualifier without the NOT token; qualifier without ``colocalizes_with``; aspect P (BP) or F (MF);
    evidence in the D1 codes (``knownness.D1_EVIDENCE`` = EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC); GO ids resolved with
    the obo (alt_id and single replaced_by followed; obsolete/unknown ids dropped and counted = knownness 'strict'
    mode); UniProtKB accession (isoform suffix stripped) -> HGNC id through ``acc_map`` (``knownness.build_acc_map``;
    no symbol fallback). Only scorable genes of the matrix gene index carry annotations.
  * membership: gene g is in term t iff g has a kept row to t or to a descendant of t (reflexive is_a/part_of closure,
    ``knownness.GoOntology.ancestors``).
  * annotated background B = scorable genes with >= 1 non-generic (``knownness.GENERIC``) propagated BP/MF term (the
    t0-background convention of scripts/04); term size = number of scorable genes annotated to t (= |t n B| for every
    non-generic term).
  * candidate terms: non-generic BP/MF terms with 5-200 annotated scorable genes, sizes computed AFTER the query's
    removals (below), so the window is per query. The columns of ``A`` are the non-generic BP/MF terms whose base
    size lies in [lo, hi + slack] with slack = the largest per-query size reduction possible, so every term that can be
    a candidate for some query is a column; the per-query window is applied by ``query_view``.

Per-query removals (applied to S, supporting partners, x, the annotated background, K_t, A_t, the matched-gene S
values, term sizes and prior-only, i.e. to every count used when that query is scored):
  * LOO (``loo=True``): the query's own row is emptied (DESIGN §3.2.1 "the query's annotations removed from all
    counts").
  * IPI with/from rule (DESIGN §3.0, round-2 item O1): rows of any other gene j with evidence IPI whose with/from
    field names the query (UniProtKB accession mapped through ``acc_map``) are dropped and j's membership is
    re-propagated from its remaining rows; applied identically for LOO, H and U queries.
  * The query never belongs to the hypergeometric population (as ``predictor.hypergeom_p``).
Removals are applied as sparse corrections to precomputed gene x term matrices (``score_queries``);
``V2.explicit_view`` re-propagates from the filtered rows and is the brute-force reference used by the tests.

Rankers and ties follow ``predictor.score_table`` (R1 S desc; R2 p_hyper asc; R3 p_emp asc; ties by S desc, then
term column = sorted GO id). Prior-only ranks the candidate terms by per-query term size (desc), ties by column.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import hypergeom

from . import knownness as kn
from . import predictor as pr
from .neighbours import Neighbours

BPMF_NS = ("biological_process", "molecular_function")
_SPLIT = re.compile(r"[|,]")


# ------------------------------------------------------------------------------------------------ rows
def v2_rows(gaf, onto: kn.GoOntology, acc_map: dict, gene_pos: dict) -> tuple[pd.DataFrame, dict]:
    """Kept GAF rows mapped to matrix positions. ``gene_pos``: {hgnc_id: matrix position} for SCORABLE genes only.
    Returns rows [row_id, pos, go_id, evidence, qualifier, reference, partners (tuple of positions named in with/from
    for IPI rows)] and stats."""
    g = kn.read_gaf(gaf) if not isinstance(gaf, pd.DataFrame) else gaf.copy()
    st = {"gaf_rows": len(g)}
    notq = kn.is_not_qualified(g["qualifier"])
    st["not_rows_removed"] = int(notq.sum())
    g = g.loc[~notq]
    coloc = g["qualifier"].fillna("").str.split("|").apply(lambda toks: "colocalizes_with" in toks)
    st["colocalizes_with_rows_removed"] = int(coloc.sum())
    g = g.loc[~coloc]
    sel = g["aspect"].isin(kn.D1_ASPECTS) & g["evidence"].isin(kn.D1_EVIDENCE)
    g = g.loc[sel].copy()
    st["rows_bpmf_d1_evidence"] = len(g)
    res = {t: onto.resolve(t) for t in pd.unique(g["go_id"])}
    g["resolve_status"] = g["go_id"].map(lambda t: res[t][1])
    g["go_id"] = g["go_id"].map(lambda t: res[t][0])
    for s in ("alt_id", "replaced_by", "obsolete_dropped", "unknown_dropped"):
        st[f"rows_{s}"] = int((g["resolve_status"] == s).sum())
    g = g[g["go_id"].notna()]
    acc = g["acc"].map(kn.strip_isoform)
    hits = acc.map(lambda a: sorted(acc_map.get(a, ())))
    st["rows_unmapped_accession"] = int((hits.map(len) == 0).sum())
    g = g.assign(hgnc_id=hits).explode("hgnc_id")
    g = g[g["hgnc_id"].notna()]
    g["pos"] = g["hgnc_id"].map(gene_pos)
    st["rows_mapped_not_scorable"] = int(g["pos"].isna().sum())
    g = g[g["pos"].notna()].copy()
    g["pos"] = g["pos"].astype(np.int64)

    n_tok = {"uniprot": 0, "uniprot_unmapped": 0, "other_db": 0}

    def partners(wf):
        out = set()
        for tok in _SPLIT.split(wf or ""):
            tok = tok.strip()
            if not tok:
                continue
            db, _, ident = tok.partition(":")
            if db != "UniProtKB":
                n_tok["other_db"] += 1
                continue
            n_tok["uniprot"] += 1
            hs = [gene_pos[h] for h in acc_map.get(kn.strip_isoform(ident), ()) if h in gene_pos]
            if not hs:
                n_tok["uniprot_unmapped"] += 1
            out.update(hs)
        return tuple(sorted(out))

    ipi = g["evidence"] == "IPI"
    g["partners"] = [partners(wf) if e == "IPI" else () for wf, e in zip(g["with_from"].values, g["evidence"].values)]
    st.update({f"ipi_withfrom_tokens_{k}": v for k, v in n_tok.items()})
    st["ipi_rows"] = int(ipi.sum())
    st["ipi_rows_with_mapped_partner"] = int((g.loc[ipi, "partners"].map(len) > 0).sum())
    out = g[["pos", "go_id", "evidence", "qualifier", "reference", "partners"]].reset_index(drop=True)
    out.insert(0, "row_id", np.arange(len(out)))
    st["rows_kept"] = len(out)
    st["genes_with_rows"] = int(out["pos"].nunique())
    return out, st


def _propagate(rows: pd.DataFrame, onto: kn.GoOntology) -> dict:
    """{pos: frozenset of propagated term ids} from kept rows."""
    out = {}
    for p, terms in rows.groupby("pos")["go_id"]:
        s = set()
        for t in set(terms):
            s |= onto.ancestors(t)
        out[int(p)] = frozenset(s)
    return out


# ------------------------------------------------------------------------------------------------ V2
@dataclass
class Removal:
    """Per-query removals: rows[r] = column indices removed from gene r; lost_bg = genes that leave B."""
    query: int
    rows: dict
    lost_bg: set

    def size_delta(self, T: int) -> np.ndarray:
        d = np.zeros(T, np.int64)
        for c in self.rows.values():
            np.add.at(d, c, 1)
        return d


@dataclass
class V2:
    genes: np.ndarray                 # hgnc ids, matrix order (G)
    scorable: np.ndarray              # bool G
    terms: np.ndarray                 # column term ids (sorted)
    A: sp.csr_matrix                  # G x T float 0/1 base membership
    size: np.ndarray                  # base size per column
    annotated: np.ndarray             # bool G, annotated background B
    lo: int
    hi: int
    onto: kn.GoOntology | None
    rows: pd.DataFrame | None
    prop: dict | None
    stats: dict = field(default_factory=dict)
    ipi_rule: bool = True
    _ipi_by_partner: dict | None = None
    _rows_by_gene: dict | None = None
    _col: dict | None = None

    @property
    def G(self) -> int:
        return self.A.shape[0]

    @property
    def T(self) -> int:
        return self.A.shape[1]

    @property
    def col(self) -> dict:
        if self._col is None:
            self._col = {t: i for i, t in enumerate(self.terms)}
        return self._col

    # ------------------------------------------------------------ removals
    def _index(self):
        if self._ipi_by_partner is None:
            ipi = self.rows[self.rows.partners.map(len) > 0]
            d: dict = {}
            for rid, j, ps in zip(ipi.row_id.values, ipi.pos.values, ipi.partners.values):
                for p in ps:
                    d.setdefault(int(p), {}).setdefault(int(j), set()).add(int(rid))
            self._ipi_by_partner = d
            self._rows_by_gene = {int(p): (d_.row_id.values, d_.go_id.values) for p, d_ in self.rows.groupby("pos")}

    def removal(self, g: int, loo: bool = True) -> Removal:
        """Removals applied when query g is scored (see module docstring)."""
        g = int(g)
        rows, lost = {}, set()
        if loo:
            c = self.A.indices[self.A.indptr[g]:self.A.indptr[g + 1]]
            if len(c):
                rows[g] = c.copy()
        if self.ipi_rule:
            self._index()
            col = self.col
            for j, rids in self._ipi_by_partner.get(g, {}).items():
                if j == g:
                    continue
                rid, gos = self._rows_by_gene[j]
                keep = ~np.isin(rid, list(rids))
                new = set()
                for t in set(gos[keep]):
                    new |= self.onto.ancestors(t)
                lost_terms = self.prop[j] - new
                if self.annotated[j] and not (new - kn.GENERIC):
                    lost.add(j)
                c = np.array(sorted(col[t] for t in lost_terms if t in col), dtype=np.int64)
                if len(c):
                    rows[j] = c
        return Removal(query=g, rows=rows, lost_bg=lost)

    def query_sizes(self, rem: Removal) -> np.ndarray:
        return self.size - rem.size_delta(self.T)

    def candidates(self, sizes: np.ndarray) -> np.ndarray:
        return (sizes >= self.lo) & (sizes <= self.hi)

    def own_terms(self, g: int) -> np.ndarray:
        """Column indices of g's own (base, propagated) membership."""
        return self.A.indices[self.A.indptr[g]:self.A.indptr[g + 1]].copy()

    def explicit_view(self, g: int, loo: bool = True) -> tuple[sp.csr_matrix, np.ndarray]:
        """Brute-force reference: (A^(g), B^(g)) re-propagated from the filtered rows (B^(g) excludes g)."""
        r = self.rows
        drop = np.zeros(len(r), bool)
        if loo:
            drop |= r.pos.values == g
        if self.ipi_rule:
            drop |= (r.pos.values != g) & r.partners.map(lambda ps: g in ps).values
        prop = _propagate(r[~drop], self.onto)
        A, ann = _matrix(prop, self.terms, self.G)
        ann[g] = False
        return A, ann

    # ------------------------------------------------------------ label shuffle (§2.4)
    def permuted(self, seed: int = 0, block: int = 20) -> tuple["V2", pd.DataFrame]:
        """Label-shuffle copy: rows of A permuted among annotated-background genes within blocks of ``block`` genes
        of similar candidate-term count (genes sorted by count, random tie order), so per-gene annotation counts are
        (nearly) preserved and term sizes exactly preserved. The IPI rule is disabled (with/from no longer refers to
        the gene carrying the row). Returns (copy, per-gene count table)."""
        rng = np.random.default_rng(seed)
        cnt = np.asarray(self.A[:, (self.size >= self.lo) & (self.size <= self.hi)].sum(1)).ravel()
        idx = np.flatnonzero(self.annotated)
        o = np.lexsort((rng.random(len(idx)), cnt[idx]))
        idx = idx[o]
        perm = np.arange(self.G)
        nb = max(1, len(idx) // block)
        for chunk in np.array_split(idx, nb):
            perm[chunk] = rng.permutation(chunk)
        # new row g = old row perm[g]
        A = self.A[perm].tocsr()
        tab = pd.DataFrame(dict(pos=idx, count_before=cnt[idx], count_after=cnt[perm[idx]],
                                moved=perm[idx] != idx))
        new = V2(genes=self.genes, scorable=self.scorable, terms=self.terms, A=A, size=self.size.copy(),
                 annotated=self.annotated.copy(), lo=self.lo, hi=self.hi, onto=self.onto, rows=None, prop=None,
                 stats=dict(self.stats, permuted_seed=seed, permuted_block=block), ipi_rule=False)
        return new, tab


def _matrix(prop: dict, terms, G: int) -> tuple[sp.csr_matrix, np.ndarray]:
    col = {t: i for i, t in enumerate(terms)}
    r, c = [], []
    ann = np.zeros(G, bool)
    for p, s in prop.items():
        if s - kn.GENERIC:
            ann[p] = True
        cc = [col[t] for t in s if t in col]
        r += [p] * len(cc)
        c += cc
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(G, len(terms)))
    A.sum_duplicates()
    A.sort_indices()
    return A, ann


def build_v2(gaf, onto: kn.GoOntology, acc_map: dict, genes, scorable, lo: int = 5, hi: int = 200,
             ipi_rule: bool = True) -> V2:
    """V2 for one release. ``genes``: hgnc ids in matrix order; ``scorable``: bool mask (same order)."""
    genes = np.asarray(genes, dtype=object)
    scorable = np.asarray(scorable, bool)
    gene_pos = {h: i for i, h in enumerate(genes) if scorable[i]}
    rows, st = v2_rows(gaf, onto, acc_map, gene_pos)
    prop = _propagate(rows, onto)
    G = len(genes)
    cnt: dict = {}
    for s in prop.values():
        for t in s:
            cnt[t] = cnt.get(t, 0) + 1
    # slack: largest number of genes that can lose a term when one query is scored (query + IPI partners naming it)
    n_naming: dict = {}
    for j, ps in zip(rows.pos.values, rows.partners.values):
        for p in ps:
            n_naming.setdefault(int(p), set()).add(int(j))
    slack = 1 + (max((len(v) for v in n_naming.values()), default=0) if ipi_rule else 0)
    terms = sorted(t for t, n in cnt.items() if lo <= n <= hi + slack and t not in kn.GENERIC
                   and onto.namespace(t) in BPMF_NS)
    A, ann = _matrix(prop, terms, G)
    size = np.asarray(A.sum(0)).ravel().astype(np.int64)
    st.update(n_genes=G, n_scorable=int(scorable.sum()), n_annotated_background=int(ann.sum()),
              n_columns=len(terms), size_slack=slack, n_candidate_terms_base=int(((size >= lo) & (size <= hi)).sum()),
              lo=lo, hi=hi, ipi_rule=ipi_rule)
    return V2(genes=genes, scorable=scorable, terms=np.asarray(terms, dtype=object), A=A, size=size, annotated=ann,
              lo=lo, hi=hi, onto=onto, rows=rows, prop=prop, stats=st, ipi_rule=ipi_rule)


# ------------------------------------------------------------------------------------------------ scoring
@dataclass
class QueryScores:
    """Scores for a set of queries under their own removals. ``table``: predictor.score_table output (columns
    query, term (column index), S, n_sup, x, n_draw, p_hyper, p_emp, M_t, reportable, rank_R1..R3) restricted to the
    query's candidate terms; ``sizes``: Q x T per-query term sizes; ``info``: per-query n_draw, population, number of
    removals."""
    queries: np.ndarray
    table: pd.DataFrame
    sizes: np.ndarray
    info: pd.DataFrame

    def ranked(self, ranker: str) -> dict:
        t = self.table[self.table[f"rank_{ranker}"].notna()].sort_values(["query", f"rank_{ranker}"])
        out = {int(g): [] for g in self.queries}
        for g, d in t.groupby("query", sort=False):
            out[int(g)] = d.term.astype(int).tolist()
        return out

    def prior_rank(self, i: int, cand: np.ndarray) -> np.ndarray:
        """Candidate columns of query i ranked by per-query size (desc), ties by column."""
        c = np.flatnonzero(cand)
        return c[np.lexsort((c, -self.sizes[i, c]))]


def all_gene_scores(nb_all: Neighbours, v2: V2) -> pr.TermScores:
    """S, n_sup, x for every gene (rows of nb_all must be 0..G-1 in order) with the base membership."""
    assert (nb_all.rows == np.arange(v2.G)).all()
    return pr.term_scores(nb_all, v2.A, annot_bg=v2.annotated)


def score_queries(v2: V2, nb_all: Neighbours, matches: dict, queries, loo: bool = True, base: pr.TermScores | None
                  = None, tol: float = 1e-9, log=None) -> QueryScores:
    """Score queries with R1/R2/R3 under per-query removals (module docstring). ``matches``: {pos: matched positions
    (nearest first, 500)}. p_emp is computed for reportable candidate terms (only these are ranked)."""
    base = all_gene_scores(nb_all, v2) if base is None else base
    S_all, P_all, X_all = base.S.tocsr(), base.n_sup.tocsr(), base.x.tocsr()
    A = v2.A
    z = np.nan_to_num(nb_all.z.astype(np.float64), nan=0.0)
    W = np.clip(z, 0, None)
    POS = (z > 0).astype(np.float64)
    ids = nb_all.ids
    T = v2.T
    queries = np.asarray(queries, dtype=np.int64)
    sizes = np.zeros((len(queries), T), np.int32)
    Sr, Nr, Xr, Hr, info = [], [], [], [], []
    pemp = {}
    nB = int(v2.annotated.sum())
    for i, g in enumerate(queries):
        g = int(g)
        rem = v2.removal(g, loo)
        sz = v2.query_sizes(rem)
        sizes[i] = sz
        cand = v2.candidates(sz)
        s = S_all.getrow(g).toarray().ravel()
        n = P_all.getrow(g).toarray().ravel()
        x = X_all.getrow(g).toarray().ravel()
        nbg = ids[g]
        for k, r in enumerate(nbg):
            if r >= 0 and int(r) in rem.rows:
                c = rem.rows[int(r)]
                s[c] -= W[g, k]
                n[c] -= POS[g, k]
                x[c] -= 1
        s[np.abs(s) < tol] = 0.0
        bg_g = v2.annotated.copy()
        bg_g[g] = False
        if rem.lost_bg:
            bg_g[list(rem.lost_bg)] = False
        valid = nbg >= 0
        n_draw = int(bg_g[nbg[valid]].sum())
        N = int(bg_g.sum())
        terms = np.flatnonzero(cand & (s > 0))
        Kt = sz.copy()
        if not loo:                                   # the query is never in the hypergeometric population
            Kt[v2.own_terms(g)] -= 1
        ph = hypergeom.sf(np.round(x[terms]).astype(int) - 1, N, Kt[terms], n_draw)
        rep = terms[np.round(n[terms]) >= pr.MIN_SUPPORT]
        # ---- p_emp over M(g) \ A_t for reportable terms, with the query's removals applied to matched genes
        m = np.asarray(matches[g], dtype=np.int64)
        m = m[m >= 0]
        if len(rep):
            rp = np.full(T, -1)
            rp[rep] = np.arange(len(rep))
            Sm = S_all[m][:, rep].toarray()
            Am = A[m][:, rep].toarray() > 0
            if rem.rows:
                rkeys = np.fromiter(rem.rows.keys(), dtype=np.int64)
                hit = np.isin(ids[m], rkeys)
                for a, k in zip(*np.nonzero(hit)):
                    cc = rp[rem.rows[int(ids[m[a], k])]]
                    cc = cc[cc >= 0]
                    Sm[a, cc] -= W[m[a], k]
                for a in np.flatnonzero(np.isin(m, rkeys)):
                    cc = rp[rem.rows[int(m[a])]]
                    Am[a, cc[cc >= 0]] = False
            elig = ~Am
            sg = s[rep]
            Mt = elig.sum(0)
            p = (1 + ((Sm >= sg - tol) & elig).sum(0)) / (1 + Mt)
            pemp[g] = (rep, p, Mt)
        else:
            pemp[g] = (rep, np.array([]), np.array([], dtype=int))
        Sr.append((i, terms, s[terms]))
        Nr.append(np.round(n[terms]))
        Xr.append(np.round(x[terms]))
        Hr.append(np.clip(ph, 1e-300, 1.0))
        info.append(dict(query=g, n_draw=n_draw, population=N, n_rows_removed=len(rem.rows),
                         n_ipi_genes=len(rem.rows) - (1 if (loo and g in rem.rows) else 0),
                         n_lost_bg=len(rem.lost_bg), n_candidates=int(cand.sum()), n_terms_S=len(terms),
                         n_reportable=len(rep)))
        if log is not None and (i + 1) % 500 == 0:
            log(f"scored {i + 1}/{len(queries)}")
    rr = np.concatenate([np.full(len(t), i) for i, t, _ in Sr]) if Sr else np.array([], int)
    cc = np.concatenate([t for _, t, _ in Sr]) if Sr else np.array([], int)
    shape = (len(queries), T)

    def mk(vals):
        M = sp.csr_matrix((np.concatenate(vals) if vals else np.array([]), (rr, cc)), shape=shape)
        M.sort_indices()
        return M
    Smat = mk([v for _, _, v in Sr])
    ts = pr.TermScores(rows=queries, S=Smat, n_sup=mk(Nr), x=mk(Xr), n_draw=np.array([d["n_draw"] for d in info]))
    tab = pr.score_table(ts, p_hyper=mk(Hr), p_emp=pemp)
    return QueryScores(queries=queries, table=tab, sizes=sizes, info=pd.DataFrame(info))


def explicit_scores(v2: V2, nb_all: Neighbours, matches: dict, g: int, loo: bool = True) -> pd.DataFrame:
    """Brute-force reference for one query: re-propagated membership, predictor.term_scores / hypergeom_p /
    empirical_p / score_table on it, candidate window from the re-propagated sizes."""
    A_g, B_g = v2.explicit_view(g, loo)
    sz = np.asarray(A_g.sum(0)).ravel()
    cand = v2.candidates(sz)
    S_all = pr.term_scores(nb_all, A_g, annot_bg=B_g).S
    nbq = Neighbours(rows=np.array([g]), ids=nb_all.ids[[g]], z=nb_all.z[[g]], K=nb_all.K)
    ts = pr.term_scores(nbq, A_g, annot_bg=B_g)
    if not cand[ts.S.indices].any():
        return pd.DataFrame(columns=["term", "S", "query", "n_sup", "x", "n_draw", "p_hyper", "p_emp", "M_t",
                                     "reportable", "rank_R1", "rank_R2", "rank_R3"]).astype({"reportable": bool})
    ph = pr.hypergeom_p(ts, A_g, annot_bg=B_g)
    mt = pr.Matches(matches={g: np.asarray(matches[g])}, n_admissible={}, n_outside_caliper={}, M=len(matches[g]),
                    caliper=None, mode="relaxed")
    pe = pr.empirical_p(ts, S_all, mt, A_g, term_ok=cand)
    return pr.score_table(ts, p_hyper=ph, p_emp=pe, term_ok=cand)
