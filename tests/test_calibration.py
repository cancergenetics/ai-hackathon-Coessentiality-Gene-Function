"""Toy tests for src/calibration.py: sign constraints, cluster cross-fitting, support restriction, Sigma p_cal.

Run: .env/bin/python -I -m pytest -q tests/test_calibration.py
"""
import os
import sys

import numpy as np
import pytest
from scipy.special import expit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import calibration as cal  # noqa: E402
from src import metrics as mt  # noqa: E402


def sim(n, seed):
    rng = np.random.default_rng(seed)
    X = np.c_[rng.normal(2, 1, n), rng.random(n), rng.normal(size=n)]
    eta = -1.0 + 1.2 * (X[:, 0] - 2) + 1.5 * X[:, 1] - 0.0 * X[:, 2]
    y = (rng.random(n) < expit(eta)).astype(float)
    return X, y, expit(eta)


def test_recovers_coefficients_and_respects_signs():
    X, y, _ = sim(20000, 0)
    m = cal.MonotoneLogistic([1, 1, 0]).fit(X, y)
    assert m.converged_
    assert m.coef_[0] == pytest.approx(1.2, abs=0.08) and m.coef_[1] == pytest.approx(1.5, abs=0.15)
    # wrong pre-specified sign: the coefficient is held at the bound 0
    m2 = cal.MonotoneLogistic([-1, 1, 0]).fit(X, y)
    assert m2.coef_[0] == pytest.approx(0, abs=1e-8)
    # an irrelevant covariate constrained positive stays >= 0
    m3 = cal.MonotoneLogistic([1, 1, 1]).fit(X, y)
    assert m3.coef_[2] >= 0
    with pytest.raises(ValueError):
        cal.MonotoneLogistic([2, 0, 0])


def test_cluster_folds_keep_clusters_whole_and_balanced():
    cl = np.repeat(np.arange(200), np.random.default_rng(0).integers(1, 6, 200))
    f = cal.cluster_folds(cl, k=10, seed=0)
    for c in np.unique(cl):
        assert len(set(f[cl == c])) == 1
    cnt = np.bincount(f, minlength=10)
    assert cnt.max() - cnt.min() <= 5
    assert not np.array_equal(f, cal.cluster_folds(cl, k=10, seed=1))


def test_cross_fit_is_calibrated_out_of_fold():
    X, y, p_true = sim(4000, 1)
    cl = np.arange(4000) // 2
    cf = cal.cross_fit(X, y, cl, [1, 1, 0], k=10, seeds=(0, 1))
    assert len(cf.models) == 20 and np.isfinite(cf.oof).all()
    c = mt.calibration_intercept_slope(cf.oof, y)
    assert c["slope_ci"][0] < 1 < c["slope_ci"][1]
    assert np.corrcoef(cf.oof, p_true)[0, 1] > 0.97


def test_support_mask():
    ref = np.c_[np.arange(101.0), np.arange(101.0)]
    new = np.array([[4.0, 50], [5, 50], [95, 95], [50, 96]])
    assert cal.support_mask(new, ref).tolist() == [False, True, True, False]
    assert cal.support_mask(new, ref, cols=[0]).tolist() == [False, True, True, True]


def test_sum_pcal_covers_truth():
    X, y, _ = sim(3000, 2)
    XU, _, pU = sim(500, 3)
    r = cal.sum_pcal(X, y, np.arange(3000) // 3, XU, [1, 1, 0], k=5, seeds=(0,), n_boot=200, seed=0)
    sup = np.isfinite(r["p_cal"])
    truth = pU[sup].sum()
    assert r["n_supported"] == sup.sum() < 500
    assert r["ci_model"][0] < truth < r["ci_model"][1]
    assert r["ci_predictive"][0] <= r["ci_model"][0] and r["ci_predictive"][1] >= r["ci_model"][1]
