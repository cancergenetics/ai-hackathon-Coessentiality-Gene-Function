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
