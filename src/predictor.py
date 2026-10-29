"""predictor.py -- neighbourhood term scores, rankers and reporting rules (DESIGN.md v2 §3.1, §3.4).

Conventions. Genes are positions 0..G-1 in matrix order; terms are columns 0..T-1 of a sparse boolean annotation
matrix ``A`` (G x T; row = gene's propagated annotations in the vocabulary/release used; rows of query genes whose
annotations must not be seen -- U genes, hold-out genes, the LOO query -- are expected to be empty or are ignored:
a gene is never its own neighbour, so S never uses the query's row). Term size filters (e.g. 5-200) are applied by
passing ``term_ok``.

* S(g,t) = sum_{j in N(g), j in t} max(z_gj, 0)                                  (R1, raw)
* supporting partners n_sup(g,t) = #{j in N(g) n t : z_gj > 0}; a term is *reportable* only if n_sup >= 2.
* Hypergeometric p (R2; descriptive): background B = annotated background genes (scorable genes with >= 1
  annotation in the vocabulary at the release used, ``annot_bg``) with the query removed; population N = |B \\ {g}|;
  successes K_t = |t n B \\ {g}|; draws n = |N(g) n B|; observed x = |N(g) n t|; p = P(X >= x).
* Matched-gene empirical p (R3): p_emp(g,t) = (1 + #{m in M_t(g): S(m,t) >= S(g,t)}) / (1 + |M_t(g)|), where M(g)
  are g's matched genes (``match_genes``) and M_t(g) drops matched genes annotated to t (a matched gene that is a
  member of t is not a null for t; on H this includes the §3.4 rule "exclude genes annotated to g's targets").
  ``randomize_ties`` gives the tie-randomised version (exactly uniform under exchangeability; used for the toy
  calibration test only).
* Rankings: R1 by S desc; R2 by p_hyper asc; R3 by p_emp asc; ties by S desc, then term index. Only reportable
  terms are ranked.
* Reported outputs: top term (rank 1) and the most specific term among the top 5 (``most_specific``: a term is
  dropped when one of its descendants is also in the top 5).

Matched genes (§3.4): Mahalanobis distance on profile covariates (mean effect, log SD, NaN fraction; covariance
of the pool), caliper ``caliper`` x pool SD on every covariate, M nearest within caliper (``mode='strict'``; fewer
than M if not enough) or M nearest regardless of caliper with violations counted (``mode='relaxed'``); within one
query no gene is used twice; ``global_without_replacement`` also forbids re-use across queries (for the 5-match
null comparator). Excluded from g's pool: g, N(g), same-arm genes, paralogues and any ``extra`` set.
DESIGN v2.3 §3.1 caliper (added at M4): ``caliper_metric='mahalanobis'`` = Mahalanobis distance <= caliper (the
distance is invariant to standardising the covariates); ``exact`` = per-gene labels that must match exactly (BG
status); ``vi`` = a fixed inverse covariance (default: pool covariance). ``Matches.distances`` holds the
Mahalanobis distance of every returned match.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import hypergeom

from .neighbours import Neighbours

RANKERS = ("R1", "R2", "R3")
MIN_SUPPORT = 2


# ------------------------------------------------------------------------------------------ term scores
@dataclass
class TermScores:
    """Sparse (Q x T) S, n_sup (z > 0 partners) and x (all partners in t) for query rows; n_draw = |N(g) n B|."""
    rows: np.ndarray
    S: sp.csr_matrix
    n_sup: sp.csr_matrix
    x: sp.csr_matrix
    n_draw: np.ndarray


def _nb_matrix(nb: Neighbours, G: int, values) -> sp.csr_matrix:
    ok = nb.ids >= 0
    r = np.repeat(np.arange(len(nb.rows)), nb.K)[ok.ravel()]
    return sp.csr_matrix((np.asarray(values, np.float64)[ok], (r, nb.ids[ok])), shape=(len(nb.rows), G))


def as_annotation(A) -> sp.csr_matrix:
    A = sp.csr_matrix(A, dtype=np.float64)
    A.data[:] = 1.0
    A.eliminate_zeros()
    return A


def term_scores(nb: Neighbours, A, annot_bg=None) -> TermScores:
    """S, supporting-partner counts and membership counts for the query rows of ``nb``."""
    A = as_annotation(A)
    G = A.shape[0]
    annot_bg = (np.asarray(A.sum(1)).ravel() > 0) if annot_bg is None else np.asarray(annot_bg, bool)
    z = np.nan_to_num(nb.z.astype(np.float64), nan=0.0)
    W = _nb_matrix(nb, G, np.clip(z, 0, None))
    P = _nb_matrix(nb, G, (z > 0).astype(np.float64))
    I = _nb_matrix(nb, G, np.ones_like(z))
    S, n_sup, x = (W @ A).tocsr(), (P @ A).tocsr(), (I @ A).tocsr()
    for M in (S, n_sup, x):
        M.eliminate_zeros()
        M.sort_indices()
    ids = np.where(nb.ids >= 0, nb.ids, 0)
    n_draw = ((nb.ids >= 0) & annot_bg[ids]).sum(1)
    return TermScores(rows=nb.rows, S=S, n_sup=n_sup, x=x, n_draw=n_draw)


def hypergeom_p(ts: TermScores, A, annot_bg=None) -> sp.csr_matrix:
    """Sparse upper-tail hypergeometric p on the nonzero pattern of ts.x (p = 1 elsewhere)."""
    A = as_annotation(A)
    annot_bg = (np.asarray(A.sum(1)).ravel() > 0) if annot_bg is None else np.asarray(annot_bg, bool)
    Kt_all = np.asarray(A[annot_bg].sum(0)).ravel()
    x = ts.x.tocoo()
    q = ts.rows[x.row]
    inB = annot_bg[q]
    N = annot_bg.sum() - inB
    self_in_t = np.asarray(A[q, x.col]).ravel() > 0
    Kt = Kt_all[x.col] - (inB & self_in_t)
    p = hypergeom.sf(x.data - 1, N, Kt, ts.n_draw[x.row])
    return sp.csr_matrix((np.clip(p, 1e-300, 1.0), (x.row, x.col)), shape=x.shape)


# ------------------------------------------------------------------------------------------ matching
def profile_covariates(effect) -> pd.DataFrame:
    """Per gene: mean effect, log SD (ddof 0, observed values), NaN fraction. ``effect``: lines x genes."""
    X = np.asarray(effect, dtype=np.float64)
    with np.errstate(divide="ignore"):
        out = pd.DataFrame(dict(mean=np.nanmean(X, 0), log_sd=np.log(np.nanstd(X, 0)),
                                nan_fraction=np.isnan(X).mean(0)))
    if isinstance(effect, pd.DataFrame):
        out.index = effect.columns
    return out


@dataclass
class Matches:
    """matches[q] = array of matched gene positions (nearest first); n_admissible / n_outside_caliper per query."""
    matches: dict
    n_admissible: dict
    n_outside_caliper: dict
    M: int
    caliper: float | None
    mode: str
    caliper_metric: str = "sd_box"
    distances: dict | None = None

    def summary(self) -> dict:
        n = np.array([len(v) for v in self.matches.values()])
        o = np.array(list(self.n_outside_caliper.values()))
        return dict(n_queries=len(n), M=self.M, caliper=self.caliper, mode=self.mode,
                    caliper_metric=self.caliper_metric,
                    frac_full_M=float((n >= self.M).mean()) if len(n) else np.nan,
                    median_matched=float(np.median(n)) if len(n) else np.nan,
                    frac_matches_outside_caliper=float(o.sum() / max(n.sum(), 1)))


def match_genes(cov, queries, pool, M: int, caliper: float | None = 0.2, mode: str = "strict", nb=None,
                arm=None, paralogues=None, extra=None, global_without_replacement: bool = False,
                seed: int = 0, caliper_metric: str = "sd_box", exact=None, vi=None) -> Matches:
    """Matched genes for each query position (see module docstring). ``cov``: G x p covariate array/DataFrame;
    ``pool``: boolean G mask of eligible genes (e.g. scorable, BG); ``nb``: Neighbours whose N(g) are excluded.
    caliper_metric: 'sd_box' (|difference| <= caliper x pool SD on every covariate) or 'mahalanobis' (Mahalanobis
    distance <= caliper; DESIGN v2.3). exact: optional G array of labels matched exactly (e.g. BG status).
    vi: optional fixed inverse covariance matrix (default: pinv of the pool covariance)."""
    if mode not in ("strict", "relaxed"):
        raise ValueError(mode)
    if caliper_metric not in ("sd_box", "mahalanobis"):
        raise ValueError(caliper_metric)
    C = np.asarray(cov, dtype=np.float64)
    pool = np.asarray(pool, bool) & np.isfinite(C).all(1)
    Cp = C[pool]
    sd = Cp.std(0)
    VI = np.linalg.pinv(np.cov(Cp, rowvar=False)) if vi is None else np.asarray(vi, dtype=np.float64)
    nbd = nb.as_dict() if nb is not None else {}
    arm = None if arm is None else np.asarray(arm)
    exact = None if exact is None else np.asarray(exact)
    avail = pool.copy()
    queries = np.asarray(queries, dtype=np.int64)
    order = np.random.default_rng(seed).permutation(len(queries)) if global_without_replacement \
        else np.arange(len(queries))
    out, nadm, nout, dist = {}, {}, {}, {}
    for qi in order:
        g = int(queries[qi])
        cand = avail.copy()
        cand[g] = False
        if g in nbd:
            cand[nbd[g]] = False
        if arm is not None and arm[g] >= 0:
            cand &= arm != arm[g]
        if exact is not None:
            cand &= exact == exact[g]
        for sets in (paralogues, extra):
            if sets and g in sets:
                cand[np.asarray(sets[g], dtype=np.int64)] = False
        idx = np.flatnonzero(cand)
        D = C[idx] - C[g]
        d2 = np.maximum(np.einsum("ij,jk,ik->i", D, VI, D), 0.0)
        if caliper is None:
            within = np.ones(len(idx), bool)
        elif caliper_metric == "mahalanobis":
            within = np.sqrt(d2) <= caliper
        else:
            within = (np.abs(D) <= caliper * np.where(sd > 0, sd, np.inf)).all(1)
        nadm[g] = int(within.sum())
        if mode == "strict":
            idx, d2, within = idx[within], d2[within], within[within]
        o = np.lexsort((idx, d2))[:M]
        out[g] = idx[o]
        dist[g] = np.sqrt(d2[o])
        nout[g] = int((~within[o]).sum())
        if global_without_replacement:
            avail[out[g]] = False
    out = {int(g): out[int(g)] for g in queries}
    return Matches(matches=out, n_admissible=nadm, n_outside_caliper=nout, M=M, caliper=caliper, mode=mode,
                   caliper_metric=caliper_metric, distances={int(g): dist[int(g)] for g in queries})


def balance(cov, queries, matches: Matches) -> pd.DataFrame:
    """Standardised mean differences (queries vs matched genes, each query's matches weighted 1/|M(g)|)."""
    C = np.asarray(cov, dtype=np.float64)
    names = list(cov.columns) if isinstance(cov, pd.DataFrame) else [f"c{i}" for i in range(C.shape[1])]
    q = np.asarray(queries, dtype=np.int64)
    q = q[[len(matches.matches[int(g)]) > 0 for g in q]]
    idx = np.concatenate([matches.matches[int(g)] for g in q])
    w = np.concatenate([np.full(len(matches.matches[int(g)]), 1.0 / len(matches.matches[int(g)])) for g in q])
    rows = []
    for k, nm in enumerate(names):
        a, b = C[q, k], C[idx, k]
        mb = np.average(b, weights=w)
        vb = np.average((b - mb) ** 2, weights=w)
        smd = (a.mean() - mb) / np.sqrt((a.var() + vb) / 2) if (a.var() + vb) > 0 else 0.0
        rows.append(dict(covariate=nm, mean_query=a.mean(), mean_matched=mb, smd=smd))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------ empirical p
def empirical_p(ts: TermScores, S_all: sp.csr_matrix, matches: Matches, A, term_ok=None, all_terms: bool = False,
                drop_annotated: bool = True, randomize_ties: bool = False, seed: int = 0) -> dict:
    """{query position: (term indices, p_emp, M_t)}. S_all: S for ALL genes (G x T; row = gene position), computed
    with each gene's own neighbourhood. all_terms=False: terms with S(g,t) > 0 only (other terms have p_emp = 1
    by definition); True: every term with term_ok (toy tests)."""
    A = as_annotation(A)
    S_all = sp.csr_matrix(S_all)
    T = A.shape[1]
    term_ok = np.ones(T, bool) if term_ok is None else np.asarray(term_ok, bool)
    rng = np.random.default_rng(seed)
    out = {}
    for i, g in enumerate(ts.rows):
        row = ts.S.getrow(i)
        terms = np.flatnonzero(term_ok) if all_terms else row.indices[term_ok[row.indices]]
        sg = np.asarray(row[:, terms].todense()).ravel()
        m = matches.matches[int(g)]
        Sm = S_all[m][:, terms].toarray()
        elig = ~(A[m][:, terms].toarray() > 0) if drop_annotated else np.ones_like(Sm, bool)
        Mt = elig.sum(0)
        if randomize_ties:
            gt = ((Sm > sg) & elig).sum(0)
            eq = ((Sm == sg) & elig).sum(0)
            p = (gt + rng.random(len(terms)) * (1 + eq)) / (1 + Mt)
        else:
            p = (1 + ((Sm >= sg) & elig).sum(0)) / (1 + Mt)
        out[int(g)] = (terms, p, Mt)
    return out


# ------------------------------------------------------------------------------------------ ranking / reporting
def score_table(ts: TermScores, p_hyper: sp.csr_matrix | None = None, p_emp: dict | None = None, term_ok=None,
                term_names=None, min_support: int = MIN_SUPPORT) -> pd.DataFrame:
    """Long table, one row per (query, term) with S > 0 and term_ok: query, term, S, n_sup, x, n_draw, p_hyper,
    p_emp, M_t, reportable, rank_R1, rank_R2, rank_R3 (ranks among reportable terms; NaN otherwise)."""
    S = ts.S.tocoo()
    df = pd.DataFrame(dict(qi=S.row, term=S.col, S=S.data))
    term_ok = np.ones(ts.S.shape[1], bool) if term_ok is None else np.asarray(term_ok, bool)
    df = df[term_ok[df.term.values]].copy()
    df["query"] = ts.rows[df.qi.values]
    df["n_sup"] = np.asarray(ts.n_sup[df.qi.values, df.term.values]).ravel().astype(int)
    df["x"] = np.asarray(ts.x[df.qi.values, df.term.values]).ravel().astype(int)
    df["n_draw"] = ts.n_draw[df.qi.values]
    df["p_hyper"] = np.asarray(p_hyper[df.qi.values, df.term.values]).ravel() if p_hyper is not None else np.nan
    if p_emp is not None:
        lut = {}
        for g, (terms, p, Mt) in p_emp.items():
            for t, pv, mt in zip(terms, p, Mt):
                lut[(g, int(t))] = (pv, mt)
        pm = [lut.get((int(g), int(t)), (1.0, np.nan)) for g, t in zip(df["query"].values, df.term.values)]
        df["p_emp"] = [v[0] for v in pm]
        df["M_t"] = [v[1] for v in pm]
    else:
        df["p_emp"], df["M_t"] = np.nan, np.nan
    df["reportable"] = df.n_sup >= min_support
    keys = {"R1": ["S"], "R2": ["p_hyper", "S"], "R3": ["p_emp", "S"]}
    asc = {"R1": [False], "R2": [True, False], "R3": [True, False]}
    rep = df[df.reportable]
    for r in RANKERS:
        o = rep.sort_values(["query", *keys[r], "term"], ascending=[True, *asc[r], True], kind="mergesort")
        df[f"rank_{r}"] = np.nan
        df.loc[o.index, f"rank_{r}"] = o.groupby("query").cumcount().values + 1
    if term_names is not None:
        df.insert(df.columns.get_loc("term") + 1, "term_id", np.asarray(term_names, dtype=object)[df.term.values])
    return df.drop(columns="qi").reset_index(drop=True)


def _proper_ancestors(ancestors, t):
    a = ancestors(t) if callable(ancestors) else ancestors.get(t, set())
    return set(a) - {t}


def most_specific(ranked_terms, ancestors) -> list:
    """Drop every term that is a proper ancestor of another term in the list; keep order. ``ancestors``: dict or
    callable term -> set of ancestor terms (self included or not)."""
    ranked_terms = list(ranked_terms)
    anc = set()
    for t in ranked_terms:
        anc |= _proper_ancestors(ancestors, t)
    return [t for t in ranked_terms if t not in anc]


def top_terms(table: pd.DataFrame, ranker: str = "R3", ancestors=None, top: int = 5, term_col: str = "term") \
        -> pd.DataFrame:
    """Per query: top1 term, the top-``top`` reportable terms, and the most specific term among them."""
    col = f"rank_{ranker}"
    t = table[table[col] <= top].sort_values(["query", col])
    rows = []
    for g, d in t.groupby("query", sort=True):
        lst = list(d[term_col].values)
        ms = most_specific(lst, ancestors)[0] if ancestors is not None else lst[0]
        r1 = d.iloc[0]
        rows.append(dict(query=g, top1=lst[0], top1_S=r1.S, top1_p_hyper=r1.p_hyper, top1_p_emp=r1.p_emp,
                         top1_n_sup=int(r1.n_sup), most_specific=ms, top=lst))
    return pd.DataFrame(rows, columns=["query", "top1", "top1_S", "top1_p_hyper", "top1_p_emp", "top1_n_sup",
                                       "most_specific", "top"])
