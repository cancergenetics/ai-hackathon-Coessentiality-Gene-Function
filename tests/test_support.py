"""Toy tests for src/support.py (DESIGN.md v2.3 §5.3): planted positives, null size ~5%, Simes/Holm, states,
contradiction rule."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.orthogonal import Source, symmetric_csr, compartments_match  # noqa: E402
from src import support  # noqa: E402

COMPS = ["nucleus", "nucleolus", "cytosol", "mitochondrion", "ER", "Golgi", "plasma membrane"]


def chung_lu(n, rng, mean_deg=8.0, module=None, p_in=0.5):
    """Degree-heterogeneous random graph (+ optional planted dense module)."""
    w = rng.pareto(2.5, n) + 1
    w = w / w.mean() * mean_deg
    P = np.outer(w, w) / w.sum()
    A = rng.random((n, n)) < np.clip(P, 0, 1)
    if module is not None:
        A[np.ix_(module, module)] |= rng.random((len(module), len(module))) < p_in
    i, j = np.where(np.triu(A, 1))
    return symmetric_csr(i, j, n)


def toy_binary(n=1500, seed=1, module=None):
    rng = np.random.default_rng(seed)
    genes = [f"G{k}" for k in range(n)]
    return Source(name="toyP", cls="P", kind="binary", genes=genes, adj=chung_lu(n, rng, module=module))


def toy_continuous(n=600, seed=2, module=None, shift=1.5):
    rng = np.random.default_rng(seed)
    genes = [f"G{k}" for k in range(n)]
    hub = rng.normal(0, 0.3, n)                       # gene-level hubness
    M = rng.normal(0, 1, (n, n)) + hub[:, None] + hub[None, :]
    M = (M + M.T) / 2
    if module is not None:
        M[np.ix_(module, module)] += shift
    np.fill_diagonal(M, np.nan)
    return Source(name="toyA", cls="A", kind="continuous", genes=genes, mat=M.astype(np.float32))


def toy_loc(n=1500, seed=3, module=None, comp="mitochondrion", name="toyL"):
    rng = np.random.default_rng(seed)
    genes = [f"G{k}" for k in range(n)]
    comp_d = {}
    for k, g in enumerate(genes):
        if rng.random() < 0.7:
            m = 1 + (rng.random() < 0.3)
            comp_d[g] = frozenset(rng.choice(COMPS, m, replace=False))
    if module is not None:
        for k in module:
            comp_d[genes[k]] = frozenset([comp])
    keep = {g: c for g, c in comp_d.items() if c}
    return Source(name=name, cls="L", kind="localisation", genes=sorted(keep), comp=keep, comp_hr=dict(keep))


# ============================================================================================ combination
def test_simes_and_holm():
    assert support.simes([0.01, 0.04, 0.5]) == pytest.approx(min(3 * 0.01, 3 * 0.04 / 2, 0.5))
    assert support.simes([0.2]) == pytest.approx(0.2)
    assert np.isnan(support.simes([]))
    r = support.holm({"P": 0.01, "A": 0.02, "L": 0.04, "G": np.nan}, alpha=0.05)
    # m = 3 tested: 0.01 <= 0.05/3 yes; 0.02 <= 0.025 yes; 0.04 <= 0.05 yes
    assert r == {"P": True, "A": True, "L": True, "G": False}
    r = support.holm({"P": 0.02, "A": 0.03}, alpha=0.05)
    assert r == {"P": True, "A": True}
    r = support.holm({"P": 0.03, "A": 0.04, "S": 0.5}, alpha=0.05)
    assert r == {"P": False, "A": False, "S": False}     # 0.03 > 0.05/3 stops the step-down


def test_compartment_match_parent_rule():
    assert compartments_match({"nucleolus"}, {"nucleus"})
    assert not compartments_match({"nucleolus"}, {"nuclear envelope"})
    assert not compartments_match({"cytosol"}, {"mitochondrion"})
    assert not compartments_match(set(), {"cytosol"})


# ============================================================================================ planted positives
def test_planted_binary_supports():
    module = list(range(100, 125))
    src = toy_binary(module=module)
    g, members = "G100", [f"G{k}" for k in module[1:]]
    r = support.source_test(src, g, members, B=1000, seed=0)
    assert r.measured and r.n_measured == 24
    assert r.p <= 2 / 1001 and r.stat > r.null_mean
    res = support.support_test(g, members, [src], B=1000)
    assert res.class_state["P"] == "supports" and res.supporting_classes == ["P"]
    assert res.class_state["A"] == "not measured"


def test_planted_continuous_supports():
    module = list(range(10, 40))
    src = toy_continuous(module=module)
    r = support.source_test(src, "G10", [f"G{k}" for k in module[1:]], B=1000, seed=0)
    assert r.measured and r.p < 0.01 and r.stat > 0.8


def test_planted_localisation_supports():
    module = list(range(200, 230))
    src = toy_loc(module=module)
    r = support.source_test(src, "G200", [f"G{k}" for k in module[1:]], B=1000, seed=0)
    assert r.measured and r.stat == 1.0 and r.p < 0.01


def test_pair_binary_planted_and_covered_null():
    rng = np.random.default_rng(5)
    n = 400
    genes = [f"G{k}" for k in range(n)]
    i = rng.integers(0, n, 6000)
    j = rng.integers(0, n, 6000)
    cov = symmetric_csr(i, j, n)
    c = cov.tocoo()
    e = rng.random(len(c.row)) < 0.1
    module = list(range(0, 15))
    # every covered g0-module pair is an edge
    sel = e | ((c.row == 0) & np.isin(c.col, module)) | ((c.col == 0) & np.isin(c.row, module))
    adj = symmetric_csr(c.row[sel], c.col[sel], n)
    # cover all g0-module pairs
    cov = symmetric_csr(np.r_[c.row, np.zeros(14, int)], np.r_[c.col, np.arange(1, 15)], n)
    adj = symmetric_csr(np.r_[adj.tocoo().row, np.zeros(14, int)], np.r_[adj.tocoo().col, np.arange(1, 15)], n)
    src = Source(name="toyS", cls="S", kind="pair_binary", genes=genes, covered=cov, adj=adj)
    r = support.source_test(src, "G0", [f"G{k}" for k in module[1:]], B=1000, seed=0)
    assert r.measured and r.n_measured == 14 and r.stat == 14 and r.p < 0.01


# ================================================================================================ null size
def _null_rate(src, n_genes=300, k=15, B=200, seed=11):
    rng = np.random.default_rng(seed)
    ps = []
    pool = src.genes
    for t in range(n_genes):
        g = pool[rng.integers(len(pool))]
        members = list(rng.choice(pool, k, replace=False))
        r = support.source_test(src, g, members, B=B, rng=rng)
        if r.measured:
            ps.append(r.p)
    ps = np.array(ps)
    return float(np.mean(ps <= 0.05)), ps


def test_null_binary_rejects_about_5pct():
    rate, ps = _null_rate(toy_binary(seed=7))
    assert 0.01 <= rate <= 0.09, rate


def test_null_continuous_rejects_about_5pct():
    rate, ps = _null_rate(toy_continuous(seed=8), n_genes=300, k=20)
    assert 0.01 <= rate <= 0.09, rate
    assert 0.4 <= np.mean(ps) <= 0.6          # roughly uniform


def test_null_localisation_is_valid():
    rate, ps = _null_rate(toy_loc(seed=9), k=20)
    assert rate <= 0.09, rate                 # discrete statistic: conservative


def test_gene_level_null_fwer():
    """Random member sets, three measured classes: Holm across classes keeps the any-class support rate <= ~5%."""
    P, A, L = toy_binary(n=600, seed=21), toy_continuous(n=600, seed=22), toy_loc(n=600, seed=23)
    rng = np.random.default_rng(3)
    hits, n = 0, 0
    for t in range(200):
        g = f"G{rng.integers(600)}"
        members = [f"G{x}" for x in rng.choice(600, 20, replace=False)]
        res = support.support_test(g, members, [P, A, L], B=200, seed=t)
        n += 1
        hits += bool(res.supporting_classes)
    assert hits / n <= 0.08, hits / n


# ======================================================================================== states, contradiction
def test_not_measured_and_absence_is_not_contradiction():
    src = toy_binary()
    res = support.support_test("NOT_A_GENE", ["G1", "G2"], [src], B=100)
    assert res.class_state["P"] == "not measured"
    # measured gene with no edge to any member: 'no support', never 'contradicts'
    adj = src.adj.tolil()
    adj[5, :] = 0
    adj[:, 5] = 0
    src2 = Source(name="p2", cls="P", kind="binary", genes=src.genes, adj=adj.tocsr())
    res = support.support_test("G5", [f"G{k}" for k in range(10, 30)], [src2], B=100)
    assert res.class_state["P"] == "no support"


def _loc(name, comp):
    return Source(name=name, cls="L", kind="localisation", genes=sorted(comp), comp=comp, comp_hr=dict(comp))


def test_contradiction_rule():
    members = [f"M{k}" for k in range(10)]
    mito = {m: frozenset(["mitochondrion"]) for m in members}
    hpa = _loc("HPA", {**mito, "g": frozenset(["nucleus"])})
    oc = _loc("OpenCell_loc", {**mito, "g": frozenset(["nucleolus"])})
    hcm = _loc("HCM_NMF", dict(mito))
    c = support.contradiction("g", members, [hpa, oc, hcm])
    assert c["assessable"] and c["term_compartments"] == ("mitochondrion",)
    assert c["incompatible_sources"] == ["HPA", "OpenCell_loc"] and c["contradicts"]
    res = support.support_test("g", members, [hpa, oc, hcm], B=200)
    assert res.class_state["L"] == "contradicts"
    # only one incompatible high-reliability source -> no contradiction
    c1 = support.contradiction("g", members, [hpa, hcm])
    assert not c1["contradicts"]
    # multi-localised g (nucleus + cytosol in an admitted source) -> no contradiction
    hpa_multi = _loc("HPA", {**mito, "g": frozenset(["nucleus", "cytosol"])})
    hpa_multi.comp_hr = {**mito, "g": frozenset(["nucleus"])}
    c2 = support.contradiction("g", members, [hpa_multi, oc, hcm])
    assert c2["multi_localised"] and not c2["contradicts"]
    # nucleus + nucleolus is NOT multi-localised (collapsed)
    hpa_nn = _loc("HPA", {**mito, "g": frozenset(["nucleus", "nucleolus"])})
    assert support.contradiction("g", members, [hpa_nn, oc, hcm])["contradicts"]
    # compatible localisation -> no contradiction
    hpa_ok = _loc("HPA", {**mito, "g": frozenset(["mitochondrion"])})
    assert not support.contradiction("g", members, [hpa_ok, oc, hcm])["contradicts"]
    # non-high-reliability source names do not count
    other = _loc("OtherLoc", {**mito, "g": frozenset(["nucleus"])})
    assert not support.contradiction("g", members, [other, oc, hcm])["contradicts"]


def test_degree_matched_null_controls_hubness():
    """A hub-heavy member set should not look like support for a random g when the null is degree-matched."""
    src = toy_binary(n=1500, seed=31)
    deg = src.degree()
    hubs = [src.genes[k] for k in np.argsort(-deg)[:30]]
    rng = np.random.default_rng(0)
    ps = []
    for t in range(120):
        g = src.genes[rng.integers(1500)]
        if g in hubs:
            continue
        ps.append(support.source_test(src, g, hubs, B=200, rng=rng).p)
    assert np.mean(np.array(ps) <= 0.05) <= 0.12
