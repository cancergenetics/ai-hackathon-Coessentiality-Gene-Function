"""Toy tests for src/splithalf.py: lineage-stratified, patient-grouped splits; background invariance check; R / R0
by hand; assessability rules.

Run: .env/bin/python -I -m pytest -q tests/test_splithalf.py
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import splithalf as sh  # noqa: E402


def model_table(n=300, seed=0):
    rng = np.random.default_rng(seed)
    lines = [f"ACH-{i:06d}" for i in range(n)]
    lin = rng.choice(["Lung", "Breast", "CNS", "Skin", "Bowel", "Blood"], n, p=[.3, .2, .15, .15, .1, .1])
    pat = [f"PT-{i // 2 if i < 60 else i}" for i in range(n)]            # first 60 lines: 30 patients x 2 lines
    return pd.DataFrame(dict(OncotreeLineage=lin, PatientID=pat), index=lines)


def test_split_keeps_patients_and_balances_lineages():
    mt = model_table()
    lines = list(mt.index) + ["ACH-999999"]                                # line missing from the Model table
    h = sh.split_halves(lines, mt, seed=0)
    assert set(h.unique()) == {0, 1} and len(h) == 301
    for _, d in mt.join(h).groupby("PatientID"):
        assert d[h.name].nunique() == 1
    for _, d in mt.join(h).groupby("OncotreeLineage"):
        n0 = (d[h.name] == 0).sum()
        assert abs(2 * n0 - len(d)) <= 3                                   # at most a 2-line patient off
    assert h.equals(sh.split_halves(lines, mt, seed=0))
    assert not h.equals(sh.split_halves(lines, mt, seed=1))


def test_extra_strata():
    mt = model_table()
    lib = pd.Series(np.where(np.arange(300) < 150, "libA", "libB"), index=mt.index)
    h = sh.split_halves(mt.index, mt, seed=2, extra_strata=lib)
    for _, d in pd.DataFrame(dict(h=h, lib=lib)).groupby("lib"):
        assert abs(2 * (d.h == 0).sum() - len(d)) <= 14                   # within-lineage x library rounding


def test_background_check():
    X = np.zeros((10, 3))
    X[:5, 1] = np.nan                       # NaN in half 0 only -> all-NaN there, BG changes
    X[0, 2] = np.nan
    eff = pd.DataFrame(X, index=[f"l{i}" for i in range(10)], columns=["a", "b", "c"])
    half = pd.Series([0] * 5 + [1] * 5, index=eff.index)
    bc = sh.background_check(eff, half, max_nan=0.1)
    assert bc.loc["b", "allnan_0"] and not bc.loc["b", "allnan_1"] and bc.loc["b", "bg_changed"]
    assert bc.loc["c", "bg_changed"] and not bc.loc["a", "bg_changed"]


def test_reproducibility_by_hand():
    K = 2
    # 4 genes, 2 seeds; gene 3 has no neighbours in half A
    A1 = np.array([[1, 2], [0, 3], [0, 1], [-1, -1]])
    B1 = np.array([[2, 3], [2, 3], [0, 1], [0, 1]])
    A2, B2 = A1.copy(), np.array([[1, 2], [2, 3], [0, 3], [0, 1]])
    R, R0 = sh.reproducibility([(A1, B1), (A2, B2)], K, matches={0: np.array([1, 2, 3])})
    assert R.tolist() == [(1 + 2) / 4, (1 + 1) / 4, (2 + 1) / 4, 0.0]
    # R0(0, m) = mean_s |A_s(0) n B_s(m)| / K with A_s(0) = {1, 2}: m=1: (1+1)/4; m=2: (1+0)/4; m=3: (1+1)/4
    assert R0[0].tolist() == [0.5, 0.25, 0.5]


def test_assessable_rules():
    R = np.array([0.4, 0.0, 0.04])
    R0 = {0: np.zeros(200), 1: np.zeros(200), 2: np.r_[np.zeros(150), np.full(50, 0.04)]}
    a = sh.assessable(R, R0, seed=0).set_index("gene")
    assert a.loc[0, "percentile"] and a.loc[0, "conservative"] and a.loc[0, "randomized"]
    assert not a.loc[1, "percentile"] and not a.loc[1, "conservative"]
    assert a.loc[2, "p_conservative"] == (1 + 50) / 201 and not a.loc[2, "conservative"]


def test_assessability_null_rates_at_real_scale():
    """Combinatorial null at DepMap scale (|BG| = 17,500, K = 25, 5 seeds, M = 200): neighbour sets are random.
    The randomized rule has size ~5%; the DESIGN-v2 'percentile' rule is conservative (~1.7%) because R0 is
    discrete and mostly 0."""
    rng = np.random.default_rng(0)
    G, K, M, nq = 17_500, 25, 200, 800

    def rand_ids():
        return np.array([rng.choice(G, K, replace=False) for _ in range(G)])

    pairs = [(rand_ids(), rand_ids()) for _ in range(5)]
    q = rng.choice(G, nq, replace=False)
    matches = {int(g): rng.choice(np.setdiff1d(np.arange(G), [g]), M, replace=False) for g in q}
    R, R0 = sh.reproducibility(pairs, K, matches)
    a = sh.assessable(R, R0, seed=0)
    assert abs(a.randomized.mean() - 0.05) < 0.025
    assert a.percentile.mean() < 0.035 and a.conservative.mean() < 0.035


# ------------------------------------------------------------------------------------------ M4 additions
def test_restrict_lists():
    ids = np.array([[5, 1, 7, 2, -1], [3, 4, 6, 0, 1]])
    allowed = np.array([True, True, False, True, True, True, False, True])
    out = sh.restrict_lists(ids, allowed, 3)
    assert out.tolist() == [[5, 1, 7], [3, 4, 0]]
    out = sh.restrict_lists(np.array([[2, 6, 5, -1, -1]]), allowed, 3)
    assert out.tolist() == [[5, -1, -1]]


def _rbo_naive(a, b, p):
    a, b = [x for x in a if x >= 0], [x for x in b if x >= 0]
    K = max(len(a), len(b))
    X = [len(set(a[:d]) & set(b[:d])) for d in range(1, K + 1)]
    return X[-1] / K * p ** K + (1 - p) / p * sum(X[d - 1] / d * p ** d for d in range(1, K + 1))


def test_rbo_ext_by_hand():
    A = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]])
    B = np.array([[1, 2, 3], [4, 5, 6], [2, 1, 3], [3, 9, 1]])
    v = sh.rbo_ext(A, B, p=0.9)
    assert np.isclose(v[0], 1.0) and v[1] == 0.0
    # [1,2,3] vs [2,1,3]: X = 0, 2, 3 -> 3/3 * .729 + (.1/.9) * (0 + 2/2 * .81 + 3/3 * .729)
    assert np.isclose(v[2], 0.729 + (0.1 / 0.9) * (0.81 + 0.729))
    rng = np.random.default_rng(0)
    for _ in range(50):
        a, b = rng.choice(40, 25, replace=False), rng.choice(40, 25, replace=False)
        assert np.isclose(sh.rbo_ext(a[None], b[None], 0.9)[0], _rbo_naive(a, b, 0.9))
    assert np.isclose(v[3], _rbo_naive([1, 2, 3], [3, 9, 1], 0.9))
    # empty slots never match
    assert sh.rbo_ext(np.array([[-1, -1]]), np.array([[-1, -1]]))[0] == 0.0


def test_reproducibility_rbo_matches_definition():
    A1 = np.array([[1, 2], [0, 3], [0, 1], [-1, -1]])
    B1 = np.array([[2, 3], [2, 3], [0, 1], [0, 1]])
    A2, B2 = A1.copy(), np.array([[1, 2], [2, 3], [0, 3], [0, 1]])
    pairs = [(A1, B1), (A2, B2)]
    R, R0 = sh.reproducibility_rbo(pairs, p=0.9, matches={0: np.array([1, 2, 3]), 2: np.array([0])}, chunk=1)
    for g in range(4):
        exp = np.mean([sh.rbo_ext(a[g][None], b[g][None], 0.9)[0] for a, b in pairs])
        assert np.isclose(R[g], exp)
    for g, ms in {0: [1, 2, 3], 2: [0]}.items():
        exp = [np.mean([sh.rbo_ext(a[g][None], b[m][None], 0.9)[0] for a, b in pairs]) for m in ms]
        assert np.allclose(R0[g], exp)


def test_conservative_p_integer_ties():
    K, S = 25, 5
    R = np.array([3 / (S * K), 0.0])
    R0 = {0: np.r_[np.full(8, 3 / (S * K)), np.zeros(192)], 1: np.zeros(200)}
    t = sh.conservative_p(R, R0, n_seeds=S, K=K).set_index("gene")
    assert t.loc[0, "n_R0_ge_R"] == 8 and np.isclose(t.loc[0, "p"], 9 / 201) and t.loc[0, "p"] < 0.05
    assert t.loc[1, "p"] == 1.0
    a = sh.assessable(R, R0).set_index("gene")
    assert np.allclose(a.p_conservative.values, t.p.values)


def test_expression_strata():
    # 30 models: lineage L1 (12 models), L2 (10), L3 (8, too small)
    lin = np.array(["L1"] * 12 + ["L2"] * 10 + ["L3"] * 8, dtype=object)
    X = np.zeros((30, 5))
    X[:3, 0] = 2.0                         # gene 0: 3/30 = 10% >= 1 -> expressed
    X[:6, 1] = 2.0                         # gene 1: 6/30 = 20%; 6/12 = 50% of L1 -> expressed (not lineage-restricted)
    X[12:17, 2] = 1.5                      # gene 2: 5/30 = 16.7% -> expressed
    X[:, 3] = 0.7                          # gene 3: never >= 1, never < 0.5 -> neither expressed nor clean negative
    X[22:30, 4] = 3.0                      # gene 4: 8/30 = 26.7% expressed; L3 too small for the lineage rule
    X[0, 3] = np.nan
    s = sh.expression_strata(X, lin)
    assert s.expressed.tolist() == [True, True, True, False, True]
    assert s.clean_negative.tolist() == [False, False, False, False, False]
    assert s.attrs["n_lineages_eligible"] == 2
    # lineage-restricted: 2/30 overall (< 10%) but 6/10 of L2 >= 50% ; clean negative: 29/30 < 0.5 (>= 95%)
    Y = np.zeros((30, 3))
    Y[12:18, 0] = 2.0                      # 6/30 = 20% -> expressed (and lineage criterion)
    Y[12:14, 1] = 2.0
    Y[14:17, 1] = 1.2                      # 5/30 = 16.7% expressed overall
    Y[12:17, 2] = 1.0                      # 5/10 of L2 = 50% -> lineage criterion; 5/30 >= 10% -> expressed anyway
    s = sh.expression_strata(Y, lin, expr_frac=0.2)
    assert s.expressed.tolist() == [True, False, False]
    assert s.lineage_criterion.tolist() == [True, True, True]
    assert s.lineage_restricted.tolist() == [False, True, True]
    assert s.lineage_max.tolist() == ["L2", "L2", "L2"]
    Z = np.zeros((40, 2))
    Z[0, 0] = 0.6                          # 39/40 = 97.5% < 0.5 -> clean negative
    Z[:3, 1] = 0.6                         # 37/40 = 92.5% -> not clean negative
    s = sh.expression_strata(Z, None)
    assert s.clean_negative.tolist() == [True, False] and not s.lineage_criterion.any()
