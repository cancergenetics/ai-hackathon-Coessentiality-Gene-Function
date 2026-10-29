"""support.py -- orthogonal support test of DESIGN.md v2.3 §5.3 (sources from ``src/orthogonal.py``).

For a gene g and its called V2 term t:

* **Members** M = scorable genes annotated to t, excluding g (computed by the caller; Tier A support uses the V2
  member set). Only admitted, independent sources of classes P, A, L, G, S enter the test; homology (H) and the
  not-independent sources are reported only (``homology_descriptive``).
* **Statistic per source** (members measured in the source, g measured):
  binary -- number of g-member edges; pair_binary (Burke) -- number of g-member pairs with an edge among the pairs
  that are covered; continuous -- mean member percentile in g's row (row percentiles of the source);
  localisation -- fraction of members sharing a compartment with g (``orthogonal.compartments_match``).
* **Null**: B = 1,000 equal-size member sets, degree-matched within the source: every measured member is replaced
  by a random measured gene (not g; no repeats within a set) of the same degree bin -- binary: degree deciles;
  continuous: hubness (mean row score) deciles, and for Perturb-seq hubness quintile x phenotype-strength quintile;
  localisation: number of compartments (1, 2, >= 3); pair_binary: g's covered partners (pairs covered by Burke).
  Empirical p = (1 + b) / (1 + B), b = #{null >= observed}.
* **Combination**: Simes across the tested sources of a class; Holm across the measured classes at alpha = 0.05
  (per gene).
* **States per class**: 'not measured' (no source of the class measures g and >= 1 member), 'no support',
  'supports' (Holm-rejected), 'contradicts' (L only; the contradiction rule below). Absence of an interaction is
  never a contradiction.
* **Contradiction**: incompatible localisation from >= 2 high-reliability sources (HPA Enhanced/Supported,
  OpenCell, Human Cell Map, MitoCarta; ``comp_hr``), and g not multi-localised (>= 2 distinct compartments in any
  admitted localisation source; nucleolus / nuclear envelope collapsed into nucleus). A source is incompatible when
  g's high-reliability compartment set is non-empty and does not match the term's compartment set, defined as the
  compartments held by >= 50% of the localised members (union over the admitted localisation sources; >= 3
  localised members required, else contradiction is not assessable). MitoCarta contributes positive calls only.
  A contradiction sets the L state to 'contradicts' (it takes precedence over 'supports').
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .orthogonal import Source, compartments_match, n_distinct_compartments

TESTED_CLASSES = ("P", "A", "L", "G", "S")
HIGH_RELIABILITY_SOURCES = ("HPA", "OpenCell_loc", "HCM_NMF", "MitoCarta3")


# ================================================================================================ combination
def simes(ps) -> float:
    """Simes combination p = min_i (n p_(i) / i)."""
    p = np.sort(np.asarray([x for x in ps if x is not None and np.isfinite(x)], dtype=float))
    if len(p) == 0:
        return np.nan
    n = len(p)
    return float(min(1.0, np.min(n * p / np.arange(1, n + 1))))


def holm(ps: dict, alpha: float = 0.05) -> dict:
    """Holm step-down over {key: p}; returns {key: rejected}. NaN p-values are not tested (False)."""
    items = sorted(((p, k) for k, p in ps.items() if p is not None and np.isfinite(p)), key=lambda x: x[0])
    m = len(items)
    out = {k: False for k in ps}
    for r, (p, k) in enumerate(items):
        if p <= alpha / (m - r):
            out[k] = True
        else:
            break
    return out


# ===================================================================================================== bins
def _quantile_bins(x: np.ndarray, q: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full(len(x), -1, dtype=int)
    ok = np.isfinite(x)
    if ok.sum() == 0:
        return out
    r = pd.Series(x[ok]).rank(method="average", pct=True).values
    out[ok] = np.minimum((r * q).astype(int), q - 1) if q > 1 else 0
    # ties share a rank, hence a bin
    return out


def degree_bins(src: Source, n_bins: int = 10) -> np.ndarray:
    """Degree-matching bins over src.genes (see module docstring)."""
    if "_bins" in src.meta:
        return src.meta["_bins"]
    if src.kind in ("binary", "pair_binary"):
        b = _quantile_bins(src.degree(), n_bins)
    elif src.kind == "continuous":
        hub = src.degree()
        if src.strength is not None:
            b = _quantile_bins(hub, 5) * 5 + _quantile_bins(src.strength, 5)
            b[(_quantile_bins(hub, 5) < 0) | (_quantile_bins(src.strength, 5) < 0)] = -1
        else:
            b = _quantile_bins(hub, n_bins)
    elif src.kind == "localisation":
        b = np.minimum(src.degree(), 3)
    else:
        raise ValueError(src.kind)
    src.meta["_bins"] = b
    return b


# ================================================================================================ per source
@dataclass
class SourceResult:
    source: str
    cls: str
    kind: str
    measured: bool
    n_members: int = 0
    n_measured: int = 0
    stat: float = np.nan
    null_mean: float = np.nan
    p: float = np.nan
    note: str = ""


def _draw(pools: dict, member_bins: np.ndarray, B: int, rng: np.random.Generator) -> np.ndarray:
    """B x k matrix of null gene indices; member j replaced by a random gene of pool[member_bins[j]] (no repeats
    within a row and bin when the pool is large enough)."""
    k = len(member_bins)
    out = np.empty((B, k), dtype=np.int64)
    for b, cnt in Counter(member_bins.tolist()).items():
        cols = np.where(member_bins == b)[0]
        pool = pools[b]
        if len(pool) == 0:
            raise ValueError("empty pool")
        if cnt <= len(pool):
            if len(pool) * B <= 5_000_000:
                keys = rng.random((B, len(pool)))
                pick = np.argpartition(keys, cnt - 1, axis=1)[:, :cnt] if cnt < len(pool) else \
                    np.tile(np.arange(len(pool)), (B, 1))
            else:
                pick = np.stack([rng.choice(len(pool), cnt, replace=False) for _ in range(B)])
        else:
            pick = rng.integers(0, len(pool), size=(B, cnt))
        out[:, cols] = pool[pick]
    return out


def source_test(src: Source, g: str, members, B: int = 1000, rng=None, seed: int = 0) -> SourceResult:
    rng = rng if rng is not None else np.random.default_rng(seed)
    members = [x for x in dict.fromkeys(members) if x != g]
    res = SourceResult(source=src.name, cls=src.cls, kind=src.kind, measured=False, n_members=len(members))
    idx = src.index
    if src.kind == "localisation":
        gc = src.comp.get(g)
        if not gc:
            res.note = "g not localised"
            return res
        mi = np.array([idx[x] for x in members if x in idx and src.comp.get(x)], dtype=np.int64)
    else:
        if g not in idx:
            res.note = "g not measured"
            return res
        mi = np.array([idx[x] for x in members if x in idx], dtype=np.int64)
    gi = idx.get(g)
    if src.kind == "pair_binary":
        partners = src.covered[gi].indices
        mi = np.intersect1d(mi, partners)
    if src.kind == "continuous":
        pct_row = np.asarray(src.row_percentiles()[gi], dtype=float)
        mi = mi[np.isfinite(pct_row[mi])]
    if len(mi) == 0:
        res.note = "no measured member"
        return res
    res.measured = True
    res.n_measured = len(mi)

    # ------------------------------------------------------------- statistic function over index arrays
    if src.kind in ("binary", "pair_binary"):
        row = np.zeros(len(src.genes), dtype=float)
        a = src.adj[gi]
        row[a.indices] = 1.0
        stat_fn = lambda ix: row[ix].sum(axis=-1)
    elif src.kind == "continuous":
        row = np.nan_to_num(pct_row, nan=0.0)
        stat_fn = lambda ix: row[ix].mean(axis=-1)
    else:
        gc = src.comp[g]
        row = np.array([1.0 if compartments_match(gc, src.comp.get(x, ())) else 0.0 for x in src.genes])
        stat_fn = lambda ix: row[ix].mean(axis=-1)
    res.stat = float(stat_fn(mi))

    # ------------------------------------------------------------- null
    if src.kind == "pair_binary":
        pool = np.setdiff1d(src.covered[gi].indices, [gi])
        k = len(mi)
        if len(pool) <= k:
            null = np.full(B, res.stat)
            res.note = "all covered partners are members"
        else:
            keys = rng.random((B, len(pool)))
            null = stat_fn(pool[np.argpartition(keys, k - 1, axis=1)[:, :k]])
    else:
        bins = degree_bins(src)
        eligible = np.ones(len(src.genes), dtype=bool)
        eligible[gi] = False
        eligible &= bins >= 0
        if src.kind == "continuous":
            eligible &= np.isfinite(pct_row)
        mb = bins[mi]
        pools = {}
        for b in set(mb.tolist()):
            pools[b] = np.where(eligible & (bins == b))[0]
            if len(pools[b]) == 0:              # no gene of this bin left: fall back to all eligible genes
                pools[b] = np.where(eligible)[0]
                res.note = "bin fallback"
        null = stat_fn(_draw(pools, mb, B, rng))
    res.null_mean = float(np.mean(null))
    res.p = float((1 + np.sum(null >= res.stat - 1e-12)) / (1 + B))
    return res


# ========================================================================================== contradiction
def contradiction(g: str, members, loc_sources: list[Source], hr_names=HIGH_RELIABILITY_SOURCES,
                  min_member_fraction: float = 0.5, min_localised_members: int = 3,
                  min_sources: int = 2) -> dict:
    """§5.3 contradiction rule (see module docstring). ``loc_sources`` = admitted localisation sources (used for
    the term compartment set and the multi-localisation rule); the high-reliability sources are the members of
    ``loc_sources`` named in ``hr_names`` (their ``comp_hr`` sets)."""
    members = [x for x in members if x != g]
    union = {}
    for s in loc_sources:
        for x in members:
            c = s.comp.get(x)
            if c:
                union.setdefault(x, set()).update(c)
    out = dict(contradicts=False, assessable=False, term_compartments=(), incompatible_sources=[],
               multi_localised=False, n_localised_members=len(union))
    out["multi_localised"] = any(n_distinct_compartments(s.comp.get(g, ())) >= 2 for s in loc_sources)
    if len(union) < min_localised_members:
        return out
    cnt = Counter(c for cs in union.values() for c in cs)
    term = {c for c, n in cnt.items() if n / len(union) >= min_member_fraction}
    out["term_compartments"] = tuple(sorted(term))
    if not term:
        return out
    out["assessable"] = True
    inc = []
    for s in loc_sources:
        if s.name not in hr_names:
            continue
        gc = (s.comp_hr or {}).get(g)
        if gc and not compartments_match(gc, term):
            inc.append(s.name)
    out["incompatible_sources"] = inc
    out["contradicts"] = len(inc) >= min_sources and not out["multi_localised"]
    return out


# ============================================================================================== gene level
@dataclass
class SupportResult:
    gene: str
    sources: list = field(default_factory=list)
    class_p: dict = field(default_factory=dict)
    class_state: dict = field(default_factory=dict)
    holm_rejected: dict = field(default_factory=dict)
    contradiction: dict = field(default_factory=dict)
    supporting_classes: list = field(default_factory=list)

    def table(self) -> pd.DataFrame:
        return pd.DataFrame([r.__dict__ for r in self.sources])


def support_test(g: str, members, sources: list[Source], B: int = 1000, alpha: float = 0.05, seed: int = 0,
                 hr_names=HIGH_RELIABILITY_SOURCES, classes=TESTED_CLASSES,
                 contradiction_sources: list[Source] | None = None) -> SupportResult:
    """Full §5.3 test for one gene. ``sources``: admitted sources (independent ones of ``classes`` are tested;
    others are skipped). ``contradiction_sources``: localisation sources for the contradiction rule (default: the
    localisation sources among ``sources``; the caller may pass the four named high-reliability sources even when
    not admitted -- a PI decision, see results/orthogonal/admission.md). Random draws: one Generator seeded with
    ``seed`` per gene call, sources in list order."""
    rng = np.random.default_rng(seed)
    out = SupportResult(gene=g)
    by_cls = {c: [] for c in classes}
    for s in sources:
        if not s.independent or s.cls not in classes:
            continue
        r = source_test(s, g, members, B=B, rng=rng)
        out.sources.append(r)
        by_cls[s.cls].append(r)
    for c, rs in by_cls.items():
        tested = [r.p for r in rs if r.measured]
        out.class_p[c] = simes(tested) if tested else np.nan
    out.holm_rejected = holm(out.class_p, alpha)
    for c in classes:
        if not np.isfinite(out.class_p[c]):
            out.class_state[c] = "not measured"
        else:
            out.class_state[c] = "supports" if out.holm_rejected[c] else "no support"
    loc = contradiction_sources if contradiction_sources is not None else \
        [s for s in sources if s.kind == "localisation" and s.independent]
    if loc:
        out.contradiction = contradiction(g, members, loc, hr_names=hr_names)
        if out.contradiction["contradicts"]:
            out.class_state["L"] = "contradicts"
    out.supporting_classes = [c for c in classes if out.class_state[c] == "supports"]
    return out


def homology_descriptive(src: Source, g: str, term: str) -> bool | None:
    """Homology (H, reported only): g carries an IBA/ISO annotation to ``term`` or a descendant (propagated
    terms). None if g has no IBA/ISO annotation."""
    t = src.terms.get(g)
    return None if t is None else term in t
