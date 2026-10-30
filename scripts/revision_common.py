"""revision_common.py -- helpers for the manuscript round-1 revision analyses (scripts/90_revision_analyses.py).

EXPLORATORY / POST-REVIEW. Nothing here changes a frozen rule; every number produced with these helpers is labelled
exploratory in results/revision/. Not a pipeline step.

Contents: output registry (numbers_<section>.json -> SUMMARY.md), Wilson intervals, exact sign-flip and exact
slot-permutation tests (integer dynamic programming on rational values), AUC, symbol -> HGNC mapping for external
catalogues, and small TSV/markdown utilities.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction
from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "revision"
OUT.mkdir(parents=True, exist_ok=True)
LABEL = "[exploratory, post-review]"


# ------------------------------------------------------------------------------------------------ registry
class Registry:
    """Collects (key, value, file, note) rows for one analysis section; written to results/revision/numbers_<sec>.json
    and assembled into SUMMARY.md by ``write_summary``."""

    def __init__(self, section: str, title: str):
        self.section, self.title, self.rows, self.notes = section, title, [], []

    def add(self, key: str, value, file: str, note: str = ""):
        if isinstance(value, float):
            value = float(f"{value:.6g}")
        self.rows.append(dict(key=key, value=value if not isinstance(value, (np.integer, np.floating)) else
                              value.item(), file=file, note=note))

    def note(self, text: str):
        self.notes.append(text)

    def save(self):
        (OUT / f"numbers_{self.section}.json").write_text(json.dumps(
            dict(section=self.section, title=self.title, rows=self.rows, notes=self.notes), indent=1, default=str)
            + "\n")


def write_summary(order: list[str], header: list[str]):
    L = list(header)
    for sec in order:
        p = OUT / f"numbers_{sec}.json"
        if not p.exists():
            L += [f"## {sec}: NOT RUN", ""]
            continue
        d = json.loads(p.read_text())
        L += [f"## {d['title']}", "", "| quantity | value | file | note |", "|---|---|---|---|"]
        for r in d["rows"]:
            v = r["value"]
            v = ", ".join(map(str, v)) if isinstance(v, list) else str(v)
            L.append(f"| {r['key'].replace('|', '/')} | {v.replace('|', '/')} | `{r['file']}` | {r['note'].replace('|', '/')} |")
        if d["notes"]:
            L += [""] + [f"- {n}" for n in d["notes"]]
        L.append("")
    (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n")


def tsv(df: pd.DataFrame, name: str, **kw) -> str:
    df.to_csv(OUT / name, sep="\t", index=False, float_format=kw.pop("float_format", "%.6g"), **kw)
    return f"results/revision/{name}"


def md(lines: list[str], name: str) -> str:
    (OUT / name).write_text("\n".join(lines) + "\n")
    return f"results/revision/{name}"


# ------------------------------------------------------------------------------------------------ intervals
def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def fmt_rate(k, n, nd=3):
    if n == 0:
        return f"{k}/0"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.{nd}f} ({lo:.{nd}f}–{hi:.{nd}f})"


def cp_upper_one_sided(k, n, alpha=0.05):
    """One-sided Clopper-Pearson upper bound (k = 0: 1 - alpha^(1/n))."""
    from scipy.stats import beta
    return 1.0 if k >= n else float(beta.ppf(1 - alpha, k + 1, n - k))


# ------------------------------------------------------------------------------------------------ exact tests
def _to_int_scale(vals):
    fr = [Fraction(v).limit_denominator(1000) for v in vals]
    den = reduce(lambda a, b: a * b // math.gcd(a, b), [f.denominator for f in fr], 1)
    return [int(f * den) for f in fr], den


def exact_signflip(d) -> tuple[float, int]:
    """Exact one-sided sign-flip p = P(sum of randomly signed |d| >= observed sum) over the 2^n sign patterns of the
    non-zero d (integer DP on rationals, denominators <= 1000)."""
    d = [x for x in d if abs(x) > 1e-12]
    n = len(d)
    if n == 0:
        return 1.0, 0
    ints, _ = _to_int_scale(d)
    obs = sum(ints)
    a = [abs(x) for x in ints]
    dist = {0: 1}
    for x in a:
        nd = {}
        for s, c in dist.items():
            nd[s + x] = nd.get(s + x, 0) + c
            nd[s - x] = nd.get(s - x, 0) + c
        dist = nd
    cnt = sum(c for s, c in dist.items() if s >= obs)
    return cnt / 2 ** n, n


def exact_slot_permutation(score_rows) -> float:
    """Exact one-sided slot-permutation p. ``score_rows``: list of (scores of the 4 slots, index of the real slot).
    Under H0 the real slot is uniform over the 4 slots of each gene (independently across genes). Statistic = sum over
    genes of real - mean(other three) = sum (4 s_real - T) / 3; distribution by exact convolution."""
    dist = {0: Fraction(1)}
    obs = 0
    for sc, ri in score_rows:
        sc = [int(x) for x in sc]
        T = sum(sc)
        vals = [4 * s - T for s in sc]
        obs += vals[ri]
        nd = {}
        for s, c in dist.items():
            for v in vals:
                nd[s + v] = nd.get(s + v, 0) + c / 4
        dist = nd
    return float(sum(c for s, c in dist.items() if s >= obs))


def auc(p, y) -> float:
    p, y = np.asarray(p, float), np.asarray(y, float)
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = pd.Series(p).rank(method="average").values
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


# ------------------------------------------------------------------------------------------------ symbols
def hgnc_symbol_map() -> tuple[dict, dict]:
    """symbol -> hgnc_id: current approved symbols first, then previous symbols, then aliases (only if unique and not
    an approved symbol of another gene). Returns (map, provenance)."""
    h = pd.read_csv(ROOT / "data/raw/hgnc/hgnc_complete_set.txt", sep="\t", dtype=str, keep_default_na=False,
                    usecols=["hgnc_id", "symbol", "prev_symbol", "alias_symbol"])
    m, prov = {}, {}
    for g, s in zip(h.hgnc_id, h.symbol):
        m[s.upper()] = g
        prov[s.upper()] = "symbol"
    for col in ("prev_symbol", "alias_symbol"):
        cand = {}
        for g, ss in zip(h.hgnc_id, h[col]):
            for s in [x.strip().upper() for x in ss.split("|") if x.strip()]:
                cand.setdefault(s, set()).add(g)
        for s, gs in cand.items():
            if s not in m and len(gs) == 1:
                m[s] = next(iter(gs))
                prov[s] = col
    return m, prov


def df_md(df: pd.DataFrame, nd: int = 4) -> list[str]:
    """Plain markdown table (no tabulate dependency)."""
    def f(x):
        if isinstance(x, (float, np.floating)):
            return "" if not np.isfinite(x) else f"{x:.{nd}g}"
        return str(x).replace("|", "/")
    L = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    L += ["| " + " | ".join(f(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return L
