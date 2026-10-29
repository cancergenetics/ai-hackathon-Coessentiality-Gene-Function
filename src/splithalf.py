"""splithalf.py -- split-half reproducibility of neighbourhoods and the assessability flag (DESIGN.md v2 §4.2).

Splits. Cell lines are split into two halves per seed (seeds 0-4): lines are grouped by PatientID (all lines of a
patient go to the same half), each patient is assigned to its majority stratum (OncotreeLineage, optionally crossed
with extra per-line strata such as a missingness/library pattern -- round-1 review 4.3), and within each stratum the
patients are shuffled (seed) and assigned greedily, largest first, to the half with fewer lines of that stratum (ties
broken at random). Lines missing from the Model table are their own patient in stratum 'unknown'.

Neighbourhoods. The tool is refitted on each half (``coess_matrix.fit_model(lines=...)``) and top-K neighbours are
taken on the fly from the model's block API (no dense matrix) with the same exclusions as the predictor (§3.1).
Neighbours are restricted to a common background (genes BG in the full data and in both halves, passed by the
caller), so the neighbour universe is identical in both halves. Genes with no observation in a half are recorded
and get no neighbours there (treated as not reproducible).

Reproducibility.
  R(g)      = mean_s |N_A^s(g) n N_B^s(g)| / K
  R0(g, m)  = mean_s |N_A^s(g) n N_B^s(m)| / K     for M matched genes m of g (predictor.match_genes; M = 200)
Assessability rules (computed side by side; the rule used is a pre-registration decision):
  'percentile'   : R(g) > 95th percentile of R0(g, .)                         (DESIGN v2 text)
  'conservative' : (1 + #{R0 >= R}) / (1 + M) <= 0.05
  'randomized'   : (#{R0 > R} + U (1 + #{R0 = R})) / (1 + M) <= 0.05, U ~ Uniform(0, 1) (seeded)
R0 is mostly exactly 0 (expected overlap ~ K^2 / |BG|), so 'percentile' admits any gene with a single shared
neighbour; the randomized rule has exact size 0.05 under exchangeability (see tests/test_toy_pipeline.py).
The final flag also requires 'expressed' (§1.4), applied by the caller.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp

from .coess_matrix import ModelBlockSource, fit_model
from .neighbours import top_k

RULES = ("percentile", "conservative", "randomized")


# ------------------------------------------------------------------------------------------ splits
def split_halves(lines, model_table: pd.DataFrame | None = None, seed: int = 0, lineage_col: str = "OncotreeLineage",
                 patient_col: str = "PatientID", extra_strata: pd.Series | None = None) -> pd.Series:
    """Half label (0 / 1) per line (index = lines). model_table: indexed by line id with lineage and patient
    columns; extra_strata: optional per-line labels crossed with the lineage."""
    lines = pd.Index(lines)
    mt = model_table.reindex(lines) if model_table is not None else pd.DataFrame(index=lines)
    lin = mt[lineage_col] if lineage_col in mt else pd.Series(np.nan, index=lines)
    lin = lin.astype(object).where(lin.notna(), "unknown").astype(str)
    pat = mt[patient_col] if patient_col in mt else pd.Series(np.nan, index=lines)
    pat = pat.astype(object).where(pat.notna(), pd.Series(["line:" + str(x) for x in lines], index=lines)).astype(str)
    stratum = lin if extra_strata is None else lin + "|" + extra_strata.reindex(lines).astype(str)
    df = pd.DataFrame(dict(patient=pat.values, stratum=stratum.values), index=lines)
    pstrat = df.groupby("patient").stratum.agg(lambda s: s.value_counts().sort_index().idxmax())
    psize = df.groupby("patient").size()
    rng = np.random.default_rng(seed)
    half_of_patient = {}
    for st in sorted(pstrat.unique()):
        pats = np.array(sorted(pstrat.index[pstrat == st]))
        pats = pats[rng.permutation(len(pats))]
        sizes = psize.reindex(pats).values
        pats = pats[np.argsort(-sizes, kind="stable")]
        load = [0, 0]
        for p in pats:
            h = int(rng.integers(2)) if load[0] == load[1] else int(np.argmin(load))
            half_of_patient[p] = h
            load[h] += int(psize[p])
    return pd.Series([half_of_patient[p] for p in df.patient], index=lines, name=f"half_seed{seed}")


def background_check(effect: pd.DataFrame, half: pd.Series, max_nan: float = 0.10) -> pd.DataFrame:
    """Per gene: NaN fraction and BG status in the full data and in each half; all-NaN flags."""
    X = effect.to_numpy(dtype=np.float64)
    h = half.reindex(effect.index).values
    out = pd.DataFrame(index=effect.columns)
    nf = np.isnan(X).mean(0)
    out["nan_full"], out["bg_full"] = nf, nf < max_nan
    for k in (0, 1):
        sub = np.isnan(X[h == k])
        out[f"nan_{k}"] = sub.mean(0)
        out[f"bg_{k}"] = out[f"nan_{k}"] < max_nan
        out[f"allnan_{k}"] = sub.all(0)
    out["bg_changed"] = (out.bg_full != out.bg_0) | (out.bg_full != out.bg_1)
    return out


# ------------------------------------------------------------------------------------------ neighbourhoods
def half_neighbours(effect: pd.DataFrame, lines, K: int, config=None, bg=None, arm=None, paralogues=None):
    """Top-K zavg_BEF neighbours of every gene (columns of ``effect``) from a tool fit on ``lines``.

    bg / arm / paralogues are in the column order of ``effect`` (positions). Returns (ids G x K in that order with -1
    padding, z, fitted-model info dict)."""
    genes = effect.columns
    fm = fit_model(effect, config, lines=lines)
    pos = genes.get_indexer(fm.genes)                       # model gene -> position in `genes`
    src = ModelBlockSource(fm, "zavg_BEF")
    bg_h = fm.model.bg.copy()
    if bg is not None:
        bg_h &= np.asarray(bg, bool)[pos]
    arm_h = None if arm is None else np.asarray(arm)[pos]
    par_h = None
    if paralogues:
        inv = np.full(len(genes), -1)
        inv[pos] = np.arange(len(pos))
        par_h = {}
        for g, s in paralogues.items():
            if inv[g] >= 0:
                t = inv[np.asarray(s, dtype=np.int64)]
                par_h[int(inv[g])] = t[t >= 0]
    nb = top_k(src, K, bg=bg_h, arm=arm_h, paralogues=par_h)
    ids = np.full((len(genes), K), -1, np.int64)
    z = np.full((len(genes), K), np.nan, np.float32)
    ids[pos] = np.where(nb.ids >= 0, pos[np.where(nb.ids >= 0, nb.ids, 0)], -1)
    z[pos] = nb.z
    info = dict(n_lines=int(fm.model.n), n_bg=int(fm.model.n_bg), K_tool=int(fm.model.K),
                dropped_all_nan=[str(g) for g in fm.dropped_genes], fit_s=round(fm.fit_s, 2))
    return ids, z, info


def _indicator(ids: np.ndarray, G: int) -> sp.csr_matrix:
    ok = ids >= 0
    r = np.repeat(np.arange(ids.shape[0]), ids.shape[1])[ok.ravel()]
    return sp.csr_matrix((np.ones(ok.sum()), (r, ids[ok])), shape=(ids.shape[0], G))


def reproducibility(pairs, K: int, matches: dict | None = None) -> tuple[np.ndarray, dict]:
    """R(g) for all genes and R0(g, m) for the matched genes of every query in ``matches``.

    pairs: list over seeds of (ids_A, ids_B) (G x K arrays, -1 padding). matches: {g: array of matched genes}.
    Returns (R array G, {g: R0 array aligned with matches[g]})."""
    G = pairs[0][0].shape[0]
    R = np.zeros(G)
    R0 = {int(g): np.zeros(len(m)) for g, m in (matches or {}).items()}
    for ids_a, ids_b in pairs:
        IA, IB = _indicator(ids_a, G), _indicator(ids_b, G)
        R += np.asarray(IA.multiply(IB).sum(1)).ravel()
        if matches:
            for g in R0:
                m = np.asarray(matches[g], dtype=np.int64)
                R0[g] += np.asarray((IB[m] @ IA[g].T).todense()).ravel()
    R /= len(pairs) * K
    for g in R0:
        R0[g] /= len(pairs) * K
    return R, R0


def assessable(R: np.ndarray, R0: dict, alpha: float = 0.05, seed: int = 0) -> pd.DataFrame:
    """Per query gene: R, R0 summary, p-values and flags under the three rules (module docstring)."""
    rng = np.random.default_rng(seed)
    rows = []
    for g in sorted(R0):
        r0 = R0[g]
        r = R[g]
        M = len(r0)
        q95 = np.quantile(r0, 0.95) if M else np.nan
        p_cons = (1 + (r0 >= r).sum()) / (1 + M)
        p_rand = ((r0 > r).sum() + rng.random() * (1 + (r0 == r).sum())) / (1 + M)
        rows.append(dict(gene=g, R=r, R0_mean=r0.mean() if M else np.nan, R0_q95=q95, M=M,
                         p_conservative=p_cons, p_randomized=p_rand,
                         percentile=bool(r > q95), conservative=bool(p_cons <= alpha),
                         randomized=bool(p_rand <= alpha)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------ added at M4
def restrict_lists(ids: np.ndarray, allowed: np.ndarray, K: int) -> np.ndarray:
    """First K entries of each ranked list (rows of ``ids``, -1 padding) that are in ``allowed`` (bool mask over
    gene positions), order preserved; -1 padding if fewer than K remain (DESIGN §4.2: the top-60 half lists are
    restricted to BG_A n BG_B n BG_full, then cut to K)."""
    ids = np.asarray(ids, dtype=np.int64)
    allowed = np.asarray(allowed, bool)
    ok = (ids >= 0) & allowed[np.where(ids >= 0, ids, 0)]
    rank = np.cumsum(ok, 1)
    keep = ok & (rank <= K)
    out = np.full((ids.shape[0], K), -1, np.int64)
    r, c = np.nonzero(keep)
    out[r, rank[r, c] - 1] = ids[r, c]
    return out


def rbo_ext(A: np.ndarray, B: np.ndarray, p: float = 0.9) -> np.ndarray:
    """Extrapolated rank-biased overlap (Webber, Moffat & Zobel 2010, eq. 32, equal-length lists) of each row pair of
    A and B (n x K ranked id lists, -1 = empty slot, never matches):
        RBO_ext = X_K / K * p^K + (1 - p) / p * sum_{d=1..K} X_d / d * p^d,  X_d = |A[:d] n B[:d]|.
    Identical lists -> 1, disjoint -> 0. Rows are assumed to hold distinct ids."""
    A = np.atleast_2d(np.asarray(A, dtype=np.int64))
    B = np.atleast_2d(np.asarray(B, dtype=np.int64))
    n, K = A.shape
    eq = (A[:, :, None] == B[:, None, :]) & (A[:, :, None] >= 0)
    hit = eq.any(2)
    j = eq.argmax(2)
    depth = np.where(hit, np.maximum(np.arange(K)[None, :], j) + 1, K + 1)    # depth at which A[:, i] is shared
    d = np.arange(1, K + 1)
    X = (depth[:, :, None] <= d[None, None, :]).sum(1)                       # n x K: X_d
    w = p ** d
    return X[:, -1] / K * p ** K + (1 - p) / p * (X / d * w).sum(1)


def reproducibility_rbo(pairs, p: float = 0.9, matches: dict | None = None, chunk: int = 64) -> tuple[np.ndarray, dict]:
    """RBO analogue of ``reproducibility`` (DESIGN §4.2 'RBO = sensitivity'):
        R_rbo(g)     = mean_s RBO_ext(N_A^s(g), N_B^s(g))
        R0_rbo(g, m) = mean_s RBO_ext(N_A^s(g), N_B^s(m))."""
    G = pairs[0][0].shape[0]
    R = np.zeros(G)
    qs = [int(g) for g in (matches or {})]
    R0 = {g: np.zeros(len(matches[g])) for g in qs}
    for ids_a, ids_b in pairs:
        R += rbo_ext(ids_a, ids_b, p)
        for c0 in range(0, len(qs), chunk):
            cg = qs[c0:c0 + chunk]
            lens = [len(matches[g]) for g in cg]
            a = np.repeat(np.asarray(ids_a)[cg], lens, axis=0)
            b = np.asarray(ids_b)[np.concatenate([np.asarray(matches[g], dtype=np.int64) for g in cg])]
            v = rbo_ext(a, b, p)
            for g, part in zip(cg, np.split(v, np.cumsum(lens)[:-1])):
                R0[g] += part
    R /= len(pairs)
    for g in R0:
        R0[g] /= len(pairs)
    return R, R0


def conservative_p(R: np.ndarray, R0: dict, n_seeds: int | None = None, K: int | None = None) -> pd.DataFrame:
    """Frozen §4.2 p per query: (1 + #{m: R0(g, m) >= R(g)}) / (1 + M). If n_seeds and K are given, R and R0 are
    converted to integer overlap totals (x n_seeds K) before comparing, so ties are exact."""
    rows = []
    for g in sorted(R0):
        r, r0 = R[g], np.asarray(R0[g])
        if n_seeds and K:
            r, r0 = np.rint(r * n_seeds * K), np.rint(r0 * n_seeds * K)
        n_ge = int((r0 >= r).sum())
        rows.append(dict(gene=g, n_R0_ge_R=n_ge, M=len(r0), p=(1 + n_ge) / (1 + len(r0))))
    return pd.DataFrame(rows)


def expression_strata(X: np.ndarray, lineage=None, expr_min: float = 1.0, expr_frac: float = 0.10,
                      neg_max: float = 0.5, neg_frac: float = 0.95, lin_frac: float = 0.5,
                      lin_min_lines: int = 10) -> pd.DataFrame:
    """DESIGN §1.4 expression strata from a models x genes log2(TPM+1) matrix (NaN = missing; fractions over
    non-missing models):
      expressed           frac(X >= expr_min) >= expr_frac
      clean_negative      frac(X < neg_max) >= neg_frac
      lineage_criterion   frac(X >= expr_min) >= lin_frac within some lineage with >= lin_min_lines models
                          (lineage = per-model label; missing labels ignored)
      lineage_restricted  lineage_criterion and not expressed (counts as expressed, §1.4)
    Returns one row per gene (column order of X)."""
    X = np.asarray(X, dtype=np.float64)
    ok = ~np.isnan(X)
    n_ok = ok.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        f_exp = (X >= expr_min).sum(0) / n_ok
        f_neg = (X < neg_max).sum(0) / n_ok
    best = np.full(X.shape[1], np.nan)
    best_lin = np.full(X.shape[1], None, dtype=object)
    n_lin = 0
    if lineage is not None:
        lab = pd.Series(lineage).astype(object)
        for L in sorted(lab.dropna().astype(str).unique()):
            m = (lab.astype(str) == L).to_numpy() & lab.notna().to_numpy()
            if m.sum() < lin_min_lines:
                continue
            n_lin += 1
            with np.errstate(invalid="ignore", divide="ignore"):
                f = (X[m] >= expr_min).sum(0) / ok[m].sum(0)
            better = np.nan_to_num(f, nan=-1) > np.nan_to_num(best, nan=-1)
            best = np.where(better, f, best)
            best_lin = np.where(better, L, best_lin)
    expressed = np.nan_to_num(f_exp, nan=0) >= expr_frac
    lin_crit = np.nan_to_num(best, nan=0) >= lin_frac
    out = pd.DataFrame(dict(n_models=n_ok, frac_ge_expr=f_exp, expressed=expressed & (n_ok > 0),
                            frac_lt_neg=f_neg, clean_negative=(np.nan_to_num(f_neg, nan=0) >= neg_frac) & (n_ok > 0),
                            lineage_max_frac=best, lineage_max=best_lin, lineage_criterion=lin_crit,
                            lineage_restricted=lin_crit & ~expressed))
    out.attrs["n_lineages_eligible"] = n_lin
    return out
