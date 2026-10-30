"""Toy tests for src/ledger.py (M6 rules; hand-computed answers)."""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.special import expit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import ledger as LG  # noqa: E402

MODEL = dict(
    covariates=["zmean", "R", "cov_pct", "size_pct", "fam_ER", "fam_sig", "fam_rare"],
    families_kept=["ER", "other", "sig"],
    standardised=dict(w=[-2.0, 1.0, 0.0, 0.5, -0.5, 0.2, -3.0, 1.0],
                      mu=[5.0, 0.1, 0.5, 0.5, 0.1, 0.1, 0.1], sd=[2.0, 0.2, 0.25, 0.3, 0.3, 0.3, 0.3]),
)
BOUNDS = dict(zmean=[3.0, 11.0], R=[0.0, 0.5], cov_pct=[0.1, 0.9], size_pct=[0.05, 0.95])


def test_design_row_and_pcal():
    df = pd.DataFrame([dict(zmean=7.0, R=0.1, cov_pct=0.75, size_pct=0.5, family="other"),
                       dict(zmean=7.0, R=0.1, cov_pct=0.75, size_pct=0.5, family="sig"),
                       dict(zmean=7.0, R=0.1, cov_pct=0.75, size_pct=0.5, family="mito"),
                       dict(zmean=7.0, R=0.1, cov_pct=0.75, size_pct=0.5, family="")])
    assert LG.design_row(df.iloc[0], MODEL).tolist() == [7.0, 0.1, 0.75, 0.5, 0, 0, 0]
    assert LG.design_row(df.iloc[1], MODEL)[4:].tolist() == [0, 1, 0]
    assert LG.design_row(df.iloc[2], MODEL)[4:].tolist() == [0, 0, 1]
    p = LG.pcal_from_model(df, MODEL)
    eta = -2.0 + 1.0 * (7 - 5) / 2 + 0.5 * (0.75 - 0.5) / 0.25 - 0.5 * 0 + 0.2 * (-0.1 / 0.3) - 3 * (-0.1 / 0.3) \
        + 1.0 * (-0.1 / 0.3)
    assert p[0] == pytest.approx(expit(eta))
    assert p[1] < p[0]
    assert np.isnan(p[3])


def test_support_category():
    base = dict(zmean=5.0, R=0.2, cov_pct=0.5, size_pct=0.5, family="other")
    assert LG.support_category(base, BOUNDS, MODEL["families_kept"]) == "in_support"
    assert LG.support_category({**base, "zmean": 2.0}, BOUNDS, MODEL["families_kept"]) == "upper_bound"
    assert LG.support_category({**base, "zmean": 12.0}, BOUNDS, MODEL["families_kept"]) == "no_pcal"
    assert LG.support_category({**base, "cov_pct": 0.05}, BOUNDS, MODEL["families_kept"]) == "no_pcal"
    assert LG.support_category({**base, "zmean": 2.0, "cov_pct": 0.05}, BOUNDS, MODEL["families_kept"]) == "no_pcal"
    assert LG.support_category({**base, "family": "mito"}, BOUNDS, MODEL["families_kept"]) == "no_pcal"
    assert LG.support_category({**base, "size_pct": np.nan}, BOUNDS, MODEL["families_kept"]) == "no_pcal"


def test_locus_flags():
    g = ("1", 1000.0, 2000.0)
    parts = {"a": ("1", 2500.0, 3000.0),       # 500 bp from g -> flagged
             "b": ("2", 0.0, 100.0),            # alone
             "c": ("2", 1000.0, 1100.0),        # 900 bp from b -> both flagged
             "d": ("3", 0.0, 100.0),            # alone
             "e": ("4", 0.0, 10.0)}             # readthrough
    f = LG.locus_flags(g, {**parts, "b": ("2", 0.0, 99.0)}, window=1000, readthrough={"e"})
    assert f == {"a": True, "b": True, "c": True, "d": False, "e": True}
    assert LG.interval_gap(("1", 0, 10), ("1", 5, 20)) == 0
    assert LG.interval_gap(("1", 0, 10), ("2", 5, 20)) == math.inf
    assert LG.interval_gap(None, ("2", 5, 20)) == math.inf
    # exactly 1 kb apart is not "< 1 kb"
    assert LG.locus_flags(("1", 0, 10), {"x": ("1", 1010, 1100)}, window=1000) == {"x": False}


def test_in_degree_hub_share():
    ids = np.array([[1, 2], [2, 3], [2, -1], [0, 1]])
    deg = LG.in_degree(ids, np.array([True, True, True, False]), 4)
    assert deg.tolist() == [0, 1, 3, 1]
    hub = LG.hub_genes(deg, np.array([True, True, True, True]), top_fraction=0.25)
    assert hub.tolist() == [False, False, True, False]
    assert LG.hub_share([1.0, 3.0], [True, False]) == pytest.approx(0.25)
    assert np.isnan(LG.hub_share([0.0], [True]))


def test_pearson_pairwise_and_exclusion():
    x = np.arange(30, dtype=float)
    Y = np.c_[2 * x + 1, -x, np.r_[np.full(15, np.nan), x[15:]]]
    r = LG.pearson_pairwise(x, Y, min_n=20)
    assert r[0] == pytest.approx(1.0) and r[1] == pytest.approx(-1.0) and np.isnan(r[2])
    F = pd.DataFrame(dict(locus=[True, False, False, False], cn=[False, True, False, False],
                          hub=[False, False, False, False]))
    assert LG.exclusion_43(F, False) == (True, 0.5)
    assert LG.exclusion_43(F.iloc[[0, 2, 3]], False) == (False, pytest.approx(1 / 3))
    assert LG.exclusion_43(F.iloc[[2, 3]], True)[0] is True


def test_bh_and_fisher():
    q = LG.bh([0.01, 0.04, 0.03, np.nan])
    assert q[0] == pytest.approx(0.03) and q[1] == pytest.approx(0.04) and q[2] == pytest.approx(0.04)
    assert np.isnan(q[3])
    fe = LG.fisher_enrichment(["a", "b", "c", "d"], {"a", "b", "x"}, ["a", "b", "c", "d"] + [f"g{i}" for i in range(96)] + ["x"])
    assert (fe["a"], fe["b"], fe["c"], fe["d"]) == (2, 2, 1, 96)
    assert fe["OR"] == pytest.approx(96.0)
    assert fe["p"] < 0.01


def test_support_condition():
    st = dict(P="no support", A="supports", L="not measured", G="not measured", S="not measured")
    assert LG.support_condition(st, "mitochondrial")["passes"]            # A diagnostic for mito
    c = LG.support_condition(st, "ER_Golgi_secretory_lipid")                # L only; not measured -> passes
    assert c["passes"] and not c["diag_measured"] and not c["strict"]
    st2 = dict(st, L="no support")
    assert not LG.support_condition(st2, "ER_Golgi_secretory_lipid")["passes"]
    st3 = dict(st, L="contradicts")
    assert not LG.support_condition(st3, "other")["passes"]
    assert LG.support_condition(st, "other")["strict"]


def _row(**k):
    r = dict(scorable=True, expressed=True, assessable=True, in_support=True, p_cal=0.6, excl43=False, diag_ok=True,
             diag_support=True, contradiction=False)
    r.update(k)
    return r


def test_tier_of():
    assert LG.tier_of(_row()) == "A"
    assert LG.tier_of(_row(diag_ok=False)) == "B"
    assert LG.tier_of(_row(demote_A=True)) == "B"
    assert LG.tier_of(_row(p_cal=0.35)) == "B"
    assert LG.tier_of(_row(p_cal=0.2)) == ""
    assert LG.tier_of(_row(excl43=True)) == ""
    assert LG.tier_of(_row(contradiction=True)) == ""
    assert LG.tier_of(_row(expressed=False)) == ""
    assert LG.tier_of(_row(p_cal=np.nan)) == ""


def test_fill_top_mito_cap():
    n = 30
    d = pd.DataFrame(dict(symbol=[f"G{i:02d}" for i in range(n)], group=[2] * n,
                          p_cal=np.linspace(0.9, 0.1, n), n_classes=0,
                          family=["mitochondrial"] * 10 + ["other"] * 20))
    d.loc[29, "group"] = 1                                        # tier B goes first despite low p_cal
    top = LG.fill_top(d, n=25, cap_top=20, cap_max=6)
    assert top.symbol.iloc[0] == "G29"
    first20 = top.iloc[:20]
    assert (first20.family == "mitochondrial").sum() == 6
    assert list(top["rank"]) == list(range(1, 26))
    # deferred mito genes come back right after position 20, in order
    assert top.symbol.iloc[20] == "G06" and bool(top.mito_deferred.iloc[20])


def test_relationship_type_precedence():
    st = dict(P="supports", A="no support", L="no support", G="no support", S="not measured")
    assert LG.relationship_type(True, False, st, True, True, False, True)[0] == "e"
    assert LG.relationship_type(False, False, st, True, True, False, True)[0] == "a"
    st2 = dict(st, P="no support")
    assert LG.relationship_type(False, False, st2, True, False, False, True)[0] == "c"
    assert LG.relationship_type(False, False, st2, False, True, True, True)[0] == "b"
    assert LG.relationship_type(False, False, st2, False, True, False, False)[0] == "c"
    assert LG.relationship_type(False, False, st2, False, False, False, False) == ("d", "type unresolved")


def test_choose_decoy():
    anc = {"t": {"t", "root"}, "child": {"child", "t", "root"}, "x": {"x", "root"}, "y": {"y", "root"},
           "z": {"z", "root"}, "w": {"w", "root"}}
    cands = pd.DataFrame(dict(term=["t", "child", "x", "y", "z", "w"],
                              family=["other", "other", "other", "other", "other", "mito"],
                              log_size=np.log([50, 20, 52, 49, 500, 50]),
                              members=[frozenset(range(50)), frozenset(range(20)), frozenset(range(100, 152)),
                                       frozenset(range(45, 94)), frozenset(range(1000, 1500)),
                                       frozenset(range(200, 250))]))
    rng = np.random.default_rng(0)
    # 'child' is a descendant, 'y' has Jaccard 5/94 < 0.1 (allowed), 'w' wrong family
    picks = {LG.choose_decoy("t", "other", np.log(50), frozenset(range(50)), cands, lambda t: anc[t], rng,
                             n_near=2).term for _ in range(20)}
    assert picks == {"x", "y"}
    tight = LG.choose_decoy("t", "other", np.log(50), frozenset(range(50)), cands, lambda t: anc[t], rng,
                            n_near=1, max_jaccard=0.01)
    assert tight.term == "x"
