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
