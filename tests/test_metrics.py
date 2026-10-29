"""Toy tests for src/metrics.py with hand-computed or simulation-known answers.

Run: .env/bin/python -I -m pytest -q tests/test_metrics.py
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import metrics as mt  # noqa: E402


def test_rank_metrics_by_hand():
    ranked = ["a", "b", "c", "d"]
    assert mt.hit_at_1(ranked, {"a"}) == 1 and mt.hit_at_1(ranked, {"b"}) == 0 and mt.hit_at_1([], {"a"}) == 0
    assert mt.reciprocal_rank(ranked, {"c", "d"}) == pytest.approx(1 / 3)
    assert mt.reciprocal_rank(ranked, {"z"}) == 0
    # targets b, d, z: precisions 1/2 at rank 2, 2/4 at rank 4, z never ranked -> (0.5 + 0.5 + 0) / 3
    assert mt.average_precision(ranked, {"b", "d", "z"}) == pytest.approx(1 / 3)
    assert np.isnan(mt.average_precision(ranked, {"a", "b"}))
    size = {"a": 300, "b": 20, "c": 40, "d": 10}
    assert mt.hit_at_1_restricted(ranked, {"b", "a"}, size) == 1        # a removed (>50) -> b is top
    assert np.isnan(mt.hit_at_1_restricted(ranked, {"a"}, size))
    df = mt.per_gene_metrics({"g1": ranked, "g2": []}, {"g1": {"a"}, "g2": {"a", "b", "c"}}, size)
    assert df.hit1.tolist() == [1, 0] and df.has_prediction.tolist() == [True, False]


def test_clusters_from_links():
    genes = ["a", "b", "c", "d", "e"]
    lab = mt.clusters_from_links(genes, pmids={"a": [1], "b": [1, 2], "c": [3], "x": [3]},
                                 neighbours={"d": ["e", "zz"]})
    assert lab[0] == lab[1] and lab[3] == lab[4] and len({lab[0], lab[2], lab[3]}) == 3


def test_bootstrap_iid_matches_normal_theory():
    rng = np.random.default_rng(0)
    a = rng.binomial(1, 0.4, 2000).astype(float)
    b = rng.binomial(1, 0.3, 2000).astype(float)
    r = mt.paired_cluster_bootstrap(a, b, np.arange(2000), n_boot=4000, seed=0)
    d = a - b
    se = d.std(ddof=1) / np.sqrt(len(d))
    assert r["estimate"] == pytest.approx(d.mean())
    assert r["se_boot"] == pytest.approx(se, rel=0.08)
    assert r["design_effect"] == pytest.approx(1, abs=0.15)
    assert r["ci_percentile"][0] == pytest.approx(d.mean() - 1.96 * se, abs=0.01)
    assert r["ci_bca"][1] == pytest.approx(d.mean() + 1.96 * se, abs=0.01)
    assert r["excludes_zero_bca"]
    r2 = mt.paired_cluster_bootstrap(a, b, np.arange(2000), n_boot=4000, seed=0)
    assert r2["ci_bca"] == r["ci_bca"]                                   # seeded


def test_bootstrap_design_effect_with_duplicated_clusters():
    """Each cluster = 5 identical copies of one gene -> variance (design effect) ~ 5x the iid formula."""
    rng = np.random.default_rng(1)
    d0 = rng.normal(size=400)
    d = np.repeat(d0, 5)
    cl = np.repeat(np.arange(400), 5)
    r = mt.cluster_bootstrap_mean(d, cl, n_boot=4000, seed=0)
    assert 4 < r["design_effect"] < 6.3
    assert r["n_clusters"] == 400


def test_bca_corrects_skewed_statistic():
    """Exponential data: BCa interval shifted right of the percentile interval (positive skew)."""
    rng = np.random.default_rng(3)
    d = rng.exponential(size=60)
    r = mt.cluster_bootstrap_mean(d, np.arange(60), n_boot=10_000, seed=0)
    assert r["acceleration"] > 0
    assert r["ci_bca"][1] > r["ci_percentile"][1]


def test_sign_flip_exact():
    d = np.array([1.0, 2.0, 3.0])
    # 8 sign patterns; means >= 2: only (+,+,+) -> 1/8
    r = mt.sign_flip_test(d)
    assert r["exact"] and r["p"] == pytest.approx(1 / 8)
    r = mt.sign_flip_test(np.array([1.0, -1.0, 1.0, -1.0]))
    assert r["p"] > 0.5
    rng = np.random.default_rng(0)
    r = mt.sign_flip_test(rng.normal(0.5, 1, 60), n_perm=20000, seed=0)
    assert not r["exact"] and r["p"] < 0.01


def test_cohens_kappa_against_sklearn():
    from sklearn.metrics import cohen_kappa_score
    rng = np.random.default_rng(0)
    r1 = rng.choice([-1, 0, 1], 200)
    r2 = np.where(rng.random(200) < 0.7, r1, rng.choice([-1, 0, 1], 200))
    assert mt.cohens_kappa(r1, r2) == pytest.approx(cohen_kappa_score(r1, r2))
    assert mt.cohens_kappa([1, 1, 0], [1, 1, 0]) == 1.0


def test_calibration_of_perfectly_calibrated_predictions():
    rng = np.random.default_rng(0)
    p = rng.beta(2, 3, 20000)
    y = (rng.random(20000) < p).astype(float)
    c = mt.calibration_intercept_slope(p, y)
    assert c["intercept_ci"][0] < 0 < c["intercept_ci"][1]
    assert c["slope_ci"][0] < 1 < c["slope_ci"][1]
    assert mt.ece(p, y) < 0.02
    assert mt.brier(p, y) == pytest.approx(np.mean(p * (1 - p)), abs=0.01)
    rd = mt.reliability_diagram(p, y, 10)
    assert rd.n.sum() == 20000 and (rd.dropna().eval("ci_lo <= obs_rate <= ci_hi")).all()
    # overconfident predictions -> slope < 1
    q = 1 / (1 + np.exp(-3 * np.log(p / (1 - p))))
    assert mt.calibration_intercept_slope(q, y)["slope_ci"][1] < 1
    rq = mt.reliability_diagram(p, y, 5, strategy="quantile")
    assert (rq.n.between(3900, 4100)).all()
