"""metrics.py -- the single metrics module (DESIGN.md v2 §3.3, §3.5, §3.7, §6.4, §9).

Per-gene metrics (gene = unit of analysis)
  * ``hit_at_1``: 1 if the top-ranked term is in the gene's target set T(g); a gene with no reportable prediction
    scores 0 (it stays in the denominator).
  * ``reciprocal_rank``: 1 / rank of the first correct term in the ranked list; 0 if none is ranked.
  * ``average_precision`` (AUPRC; only genes with |T(g)| >= 3): mean over targets of precision at the rank where the
    target is retrieved; targets that are never ranked contribute 0 (non-interpolated IR average precision).
  * ``hit_at_1_restricted``: ranked list and targets both restricted to terms with size <= max_size (default 50);
    genes with no target left are excluded (NaN).
Paired comparisons and resampling
  * ``paired_cluster_bootstrap``: mean paired difference a - b, cluster bootstrap (resample clusters with
    replacement; default 10,000 replicates, seed argument), percentile and BCa CIs (acceleration from the cluster
    jackknife), design effect = cluster-bootstrap variance / i.i.d. variance of the mean.
  * ``clusters_from_links``: connected components of genes linked by a shared PMID or by appearing in each other's
    neighbour list (union of both link types).
  * ``sign_flip_test``: one-sided test of mean(d) > 0 by sign flipping (exact enumeration for n <= 20, else Monte
    Carlo with seed); p = #{flips with mean >= observed} / #flips (identity included).
Agreement and calibration
  * ``cohens_kappa`` (two raters, nominal categories).
  * ``reliability_diagram`` (bins of predicted probability: n, mean predicted, observed rate, Wilson 95% CI), ``ece``.
  * ``brier``; ``calibration_intercept_slope``: slope = coefficient of logit(p) in a logistic regression of y on
    logit(p); intercept = calibration-in-the-large (intercept-only logistic regression with offset logit(p));
    Wald 95% CIs (Newton-Raphson / IRLS; no external dependency).
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from scipy.special import expit, logit
from scipy.stats import norm


# ------------------------------------------------------------------------------------------ per-gene metrics
def hit_at_1(ranked, targets) -> float:
    ranked = list(ranked)
    return float(bool(ranked) and ranked[0] in set(targets))


def reciprocal_rank(ranked, targets) -> float:
    T = set(targets)
    for i, t in enumerate(ranked, 1):
        if t in T:
            return 1.0 / i
    return 0.0


def average_precision(ranked, targets, min_targets: int = 3) -> float:
    T = set(targets)
    if len(T) < min_targets:
        return np.nan
    hits, s = 0, 0.0
    for i, t in enumerate(ranked, 1):
        if t in T:
            hits += 1
            s += hits / i
    return s / len(T)


def hit_at_1_restricted(ranked, targets, term_size: dict, max_size: int = 50) -> float:
    keep = lambda t: term_size.get(t, np.inf) <= max_size          # noqa: E731
    T = {t for t in targets if keep(t)}
    if not T:
        return np.nan
    return hit_at_1([t for t in ranked if keep(t)], T)


def per_gene_metrics(ranked: dict, targets: dict, term_size: dict | None = None, max_size: int = 50) -> pd.DataFrame:
    """ranked: {gene: ranked term list (reportable terms only)}; targets: {gene: set}. One row per target gene."""
    rows = []
    for g, T in targets.items():
        r = list(ranked.get(g, []))
        row = dict(gene=g, n_targets=len(T), has_prediction=bool(r), hit1=hit_at_1(r, T), rr=reciprocal_rank(r, T),
                   ap=average_precision(r, T))
        if term_size is not None:
            row["hit1_small"] = hit_at_1_restricted(r, T, term_size, max_size)
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------ clusters
def clusters_from_links(genes, pmids: dict | None = None, neighbours: dict | None = None) -> np.ndarray:
    """Cluster label per gene (connected components). pmids: {gene: iterable of PMIDs}; neighbours: {gene: iterable
    of genes}; links to genes outside ``genes`` are ignored."""
    genes = list(genes)
    pos = {g: i for i, g in enumerate(genes)}
    n = len(genes)
    r, c = [], []
    if pmids:
        by_pmid: dict = {}
        for g, ps in pmids.items():
            if g in pos:
                for p in set(ps):
                    by_pmid.setdefault(p, []).append(pos[g])
        for members in by_pmid.values():
            r += members[:-1]
            c += members[1:]
    if neighbours:
        for g, nbs in neighbours.items():
            if g in pos:
                for h in nbs:
                    if h in pos and h != g:
                        r.append(pos[g])
                        c.append(pos[h])
    A = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n))
    return connected_components(A, directed=False)[1]


# ------------------------------------------------------------------------------------------ bootstrap
def _cluster_sums(d: np.ndarray, clusters) -> tuple[np.ndarray, np.ndarray]:
    lab, inv = np.unique(np.asarray(clusters), return_inverse=True)
    return np.bincount(inv, weights=d, minlength=len(lab)), np.bincount(inv, minlength=len(lab)).astype(float)


def cluster_bootstrap_mean(d, clusters, n_boot: int = 10_000, seed: int = 0, alpha: float = 0.05) -> dict:
    """Cluster bootstrap of mean(d) (ratio estimator sum/count over resampled clusters); percentile + BCa CIs."""
    d = np.asarray(d, dtype=np.float64)
    ok = np.isfinite(d)
    d, clusters = d[ok], np.asarray(clusters)[ok]
    s, c = _cluster_sums(d, clusters)
    k = len(s)
    est = s.sum() / c.sum()
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b0 in range(0, n_boot, 1000):
        nb = min(1000, n_boot - b0)
        W = rng.multinomial(k, np.full(k, 1.0 / k), size=nb).astype(float)     # cluster resampling counts
        boot[b0:b0 + nb] = (W @ s) / (W @ c)
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    # BCa: bias correction z0 and acceleration a from the cluster jackknife
    p0 = np.clip((boot < est).mean() + 0.5 * (boot == est).mean(), 1.0 / (n_boot + 1), 1 - 1.0 / (n_boot + 1))
    z0 = norm.ppf(p0)
    jack = (s.sum() - s) / (c.sum() - c) if k > 1 else np.array([est])
    jd = jack.mean() - jack
    den = 6.0 * (jd ** 2).sum() ** 1.5
    a = (jd ** 3).sum() / den if den > 0 else 0.0
    za = norm.ppf([alpha / 2, 1 - alpha / 2])
    adj = norm.cdf(z0 + (z0 + za) / (1 - a * (z0 + za)))
    blo, bhi = np.quantile(boot, adj)
    var_iid = d.var(ddof=1) / len(d) if len(d) > 1 else np.nan
    var_boot = boot.var(ddof=1)
    return dict(estimate=float(est), n=int(len(d)), n_clusters=int(k), ci_percentile=(float(lo), float(hi)),
                ci_bca=(float(blo), float(bhi)), se_boot=float(np.sqrt(var_boot)),
                design_effect=float(var_boot / var_iid) if var_iid and var_iid > 0 else np.nan,
                z0=float(z0), acceleration=float(a), n_boot=n_boot, seed=seed)


def paired_cluster_bootstrap(a, b, clusters, n_boot: int = 10_000, seed: int = 0, alpha: float = 0.05) -> dict:
    """Mean paired difference a - b (per gene) with cluster bootstrap CIs (see cluster_bootstrap_mean); also the
    two arm means."""
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    out = cluster_bootstrap_mean(a - b, clusters, n_boot, seed, alpha)
    ok = np.isfinite(a - b)
    out.update(mean_a=float(a[ok].mean()), mean_b=float(b[ok].mean()))
    out["excludes_zero_bca"] = bool(out["ci_bca"][0] > 0 or out["ci_bca"][1] < 0)
    out["excludes_zero_percentile"] = bool(out["ci_percentile"][0] > 0 or out["ci_percentile"][1] < 0)
    return out


def sign_flip_test(d, n_perm: int = 100_000, seed: int = 0, exact_max_n: int = 20) -> dict:
    """One-sided sign-flip test of mean(d) > 0."""
    d = np.asarray(d, dtype=np.float64)
    d = d[np.isfinite(d)]
    n = len(d)
    obs = d.mean()
    if n <= exact_max_n:
        signs = np.array(list(itertools.product((1.0, -1.0), repeat=n)))
        exact = True
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice((1.0, -1.0), size=(n_perm, n))
        signs[0] = 1.0
        exact = False
    m = signs @ d / n
    p = float((m >= obs - 1e-12).mean())
    return dict(mean=float(obs), n=n, p=p, exact=exact, n_flips=len(signs))


# ------------------------------------------------------------------------------------------ agreement
def cohens_kappa(r1, r2) -> float:
    r1, r2 = np.asarray(r1), np.asarray(r2)
    cats = np.unique(np.r_[r1, r2])
    po = (r1 == r2).mean()
    pe = sum((r1 == c).mean() * (r2 == c).mean() for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else 1.0


# ------------------------------------------------------------------------------------------ calibration
def brier(p, y) -> float:
    p, y = np.asarray(p, float), np.asarray(y, float)
    return float(np.mean((p - y) ** 2))


def _wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def reliability_diagram(p, y, n_bins: int = 10, strategy: str = "uniform") -> pd.DataFrame:
    """Bins of predicted probability ('uniform' width or 'quantile'): n, mean_pred, obs_rate, Wilson CI."""
    p, y = np.asarray(p, float), np.asarray(y, float)
    if strategy == "uniform":
        edges = np.linspace(0, 1, n_bins + 1)
    else:
        edges = np.unique(np.quantile(p, np.linspace(0, 1, n_bins + 1)))
    b = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    rows = []
    for i in range(len(edges) - 1):
        m = b == i
        n = int(m.sum())
        lo, hi = _wilson(y[m].sum(), n)
        rows.append(dict(bin=i, lo_edge=edges[i], hi_edge=edges[i + 1], n=n,
                         mean_pred=p[m].mean() if n else np.nan, obs_rate=y[m].mean() if n else np.nan,
                         ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(rows)


def ece(p, y, n_bins: int = 10, strategy: str = "uniform") -> float:
    r = reliability_diagram(p, y, n_bins, strategy)
    r = r[r.n > 0]
    return float((r.n * (r.mean_pred - r.obs_rate).abs()).sum() / r.n.sum())


def _logistic_newton(X, y, offset=None, max_iter: int = 100, tol: float = 1e-10):
    X = np.asarray(X, float)
    off = np.zeros(len(y)) if offset is None else offset
    beta = np.zeros(X.shape[1])
    for _ in range(max_iter):
        mu = expit(X @ beta + off)
        w = mu * (1 - mu)
        H = X.T @ (X * w[:, None])
        step = np.linalg.solve(H + 1e-12 * np.eye(len(beta)), X.T @ (y - mu))
        beta += step
        if np.abs(step).max() < tol:
            break
    mu = expit(X @ beta + off)
    cov = np.linalg.pinv(X.T @ (X * (mu * (1 - mu))[:, None]))
    return beta, np.sqrt(np.diag(cov))


def calibration_intercept_slope(p, y, eps: float = 1e-6) -> dict:
    """Calibration slope (logistic y ~ a + b logit p) and calibration-in-the-large intercept (y ~ a + offset
    logit p), each with a Wald 95% CI. Perfect calibration: intercept 0, slope 1."""
    p = np.clip(np.asarray(p, float), eps, 1 - eps)
    y = np.asarray(y, float)
    lp = logit(p)
    (a_s, b), (se_a_s, se_b) = _logistic_newton(np.c_[np.ones(len(y)), lp], y)
    (a,), (se_a,) = _logistic_newton(np.ones((len(y), 1)), y, offset=lp)
    return dict(intercept=float(a), intercept_ci=(float(a - 1.96 * se_a), float(a + 1.96 * se_a)),
                slope=float(b), slope_ci=(float(b - 1.96 * se_b), float(b + 1.96 * se_b)), n=int(len(y)))
