"""calibration.py -- calibrated probability that a top prediction is correct (DESIGN.md v2 §0 C3, §3.7).

Model. Logistic regression of hit@1 (0/1) on per-gene covariates with pre-specified coefficient signs
(``signs``: +1 = non-decreasing, -1 = non-increasing, 0 = free, e.g. module-family dummies), fitted by L-BFGS-B
with sign bounds on the coefficients of internally standardised covariates (standardisation does not change signs);
the intercept is free; optional ridge ``l2`` on the slopes (default 0).

Cross-fitting. k folds (default 10) formed from whole clusters (metrics.clusters_from_links), balanced by gene count,
for each fold-assignment seed (default seeds 0-4); every hold-out gene gets the mean of its out-of-fold predictions
over seeds; new genes (U) get the mean prediction of all k x seeds fold models (``CrossFit.predict``).

Support restriction. A new gene gets no p_cal (NaN) if any continuous covariate lies outside the 5th-95th
percentile range of the hold-out set (``support_mask``).

Headline. Sigma p_cal over supported U genes; 95% CI from a cluster bootstrap of the hold-out set (each replicate
refits one full model on the resampled clusters and re-predicts U; percentile CI), optionally widened by
Bernoulli outcome noise ('predictive' interval).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit


class MonotoneLogistic:
    """Sign-constrained logistic regression (see module docstring)."""

    def __init__(self, signs, l2: float = 0.0):
        self.signs = np.asarray(signs, dtype=int)
        if not np.isin(self.signs, (-1, 0, 1)).all():
            raise ValueError("signs must be -1, 0 or +1")
        self.l2 = l2

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float)
        if X.shape[1] != len(self.signs):
            raise ValueError("X columns != len(signs)")
        self.mu_ = X.mean(0)
        sd = X.std(0)
        self.sd_ = np.where(sd > 0, sd, 1.0)
        Z = (X - self.mu_) / self.sd_
        n = len(y)

        def f(w):
            eta = w[0] + Z @ w[1:]
            nll = np.sum(np.logaddexp(0, eta) - y * eta) / n + 0.5 * self.l2 * (w[1:] @ w[1:])
            r = (expit(eta) - y) / n
            g = np.r_[r.sum(), Z.T @ r + self.l2 * w[1:]]
            return nll, g

        bounds = [(None, None)] + [((0, None) if s > 0 else (None, 0) if s < 0 else (None, None)) for s in self.signs]
        p0 = np.clip(y.mean(), 1e-3, 1 - 1e-3)
        w0 = np.r_[np.log(p0 / (1 - p0)), np.zeros(len(self.signs))]
        res = minimize(f, w0, jac=True, method="L-BFGS-B", bounds=bounds, options=dict(maxiter=2000, gtol=1e-9))
        self.w_ = res.x
        self.converged_ = bool(res.success)
        self.coef_ = self.w_[1:] / self.sd_                    # on the original covariate scale
        self.intercept_ = self.w_[0] - (self.coef_ * self.mu_).sum()
        return self

    def predict_proba(self, X) -> np.ndarray:
        Z = (np.asarray(X, float) - self.mu_) / self.sd_
        return expit(self.w_[0] + Z @ self.w_[1:])


def cluster_folds(clusters, k: int = 10, seed: int = 0) -> np.ndarray:
    """Fold id per gene; whole clusters per fold; clusters shuffled (seed) then assigned largest-first to the
    fold with the fewest genes."""
    lab, inv, cnt = np.unique(np.asarray(clusters), return_inverse=True, return_counts=True)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(lab))
    order = order[np.argsort(-cnt[order], kind="stable")]
    load = np.zeros(k)
    fold_of = np.empty(len(lab), int)
    for c in order:
        f = int(np.argmin(load))
        fold_of[c] = f
        load[f] += cnt[c]
    return fold_of[inv]


@dataclass
class CrossFit:
    oof: np.ndarray                                   # mean out-of-fold prediction per hold-out gene
    oof_by_seed: np.ndarray                           # seeds x n
    models: list = field(default_factory=list)       # all k x seeds fold models

    def predict(self, X) -> np.ndarray:
        return np.mean([m.predict_proba(X) for m in self.models], axis=0)


def cross_fit(X, y, clusters, signs, k: int = 10, seeds=(0, 1, 2, 3, 4), l2: float = 0.0) -> CrossFit:
    X, y = np.asarray(X, float), np.asarray(y, float)
    oof = np.full((len(seeds), len(y)), np.nan)
    models = []
    for si, s in enumerate(seeds):
        folds = cluster_folds(clusters, k, s)
        for f in range(k):
            te = folds == f
            if not te.any():
                continue
            m = MonotoneLogistic(signs, l2).fit(X[~te], y[~te])
            oof[si, te] = m.predict_proba(X[te])
            models.append(m)
    return CrossFit(oof=oof.mean(0), oof_by_seed=oof, models=models)


def support_mask(X_new, X_ref, cols=None, lo: float = 5.0, hi: float = 95.0) -> np.ndarray:
    """True where every covariate in ``cols`` (default all) lies within [P_lo, P_hi] of X_ref."""
    X_new, X_ref = np.atleast_2d(np.asarray(X_new, float)), np.asarray(X_ref, float)
    cols = np.arange(X_ref.shape[1]) if cols is None else np.asarray(cols)
    a, b = np.percentile(X_ref[:, cols], [lo, hi], axis=0)
    V = X_new[:, cols]
    return ((V >= a) & (V <= b)).all(1)


def p_cal(cf: CrossFit, X_new, X_ref, support_cols=None) -> np.ndarray:
    """Calibrated probabilities for new genes; NaN outside the hold-out support."""
    p = cf.predict(X_new)
    p[~support_mask(X_new, X_ref, support_cols)] = np.nan
    return p


def sum_pcal(X_H, y_H, clusters_H, X_U, signs, k: int = 10, seeds=(0, 1, 2, 3, 4), support_cols=None,
             n_boot: int = 1000, seed: int = 0, l2: float = 0.0, predictive: bool = True) -> dict:
    """Sigma p_cal over supported U genes with a cluster-bootstrap CI (see module docstring)."""
    X_H, y_H, X_U = np.asarray(X_H, float), np.asarray(y_H, float), np.asarray(X_U, float)
    cf = cross_fit(X_H, y_H, clusters_H, signs, k, seeds, l2)
    p = p_cal(cf, X_U, X_H, support_cols)
    sup = np.isfinite(p)
    est = float(p[sup].sum())
    lab, inv = np.unique(np.asarray(clusters_H), return_inverse=True)
    members = [np.flatnonzero(inv == c) for c in range(len(lab))]
    rng = np.random.default_rng(seed)
    sums, pred = np.empty(n_boot), np.empty(n_boot)
    for b in range(n_boot):
        idx = np.concatenate([members[c] for c in rng.integers(0, len(lab), len(lab))])
        if y_H[idx].min() == y_H[idx].max():
            sums[b] = pred[b] = np.nan
            continue
        pb = MonotoneLogistic(signs, l2).fit(X_H[idx], y_H[idx]).predict_proba(X_U[sup])
        sums[b] = pb.sum()
        pred[b] = (rng.random(len(pb)) < pb).sum() if predictive else np.nan
    ok = np.isfinite(sums)
    out = dict(sum_pcal=est, n_supported=int(sup.sum()), n_U=int(len(p)), ci_model=tuple(np.quantile(sums[ok],
               [0.025, 0.975]).tolist()), n_boot=int(ok.sum()), seed=seed, p_cal=p)
    if predictive:
        out["ci_predictive"] = tuple(np.quantile(pred[ok], [0.025, 0.975]).tolist())
    return out
