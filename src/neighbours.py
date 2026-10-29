"""neighbours.py -- top-K neighbour extraction with artefact exclusions (DESIGN.md v2 §2.2, §3.1, §4.3).

N(g) = the K highest-scoring genes j for query g after:
  * j == g removed (diagonal set to -inf; the stored tool matrices have a NaN diagonal and ``argpartition`` on NaN
    can silently return the query itself -- round-1 review 4.2);
  * j restricted to background genes (``bg`` mask; e.g. the tool's BG = NaN fraction < 10%);
  * j on the same chromosome arm as g removed (``arm`` codes; -1 / missing = unknown, no arm exclusion -- callers
    should report how many queries have an unknown arm);
  * j a paralogue of g removed (``paralogues``: {query position: iterable of gene positions});
  * j in an optional per-query extra exclusion set (``extra``, same format);
  * NaN scores treated as -inf.
Ties are broken by the lower gene index (deterministic). Rows with fewer than K admissible genes are padded with
id -1 and z NaN.

The score source can be a dense array / memmap (genes x genes, same gene order on both axes) or any object with
``shape`` and ``iter_blocks(rows)`` yielding (row positions, block) -- e.g. ``coess_matrix.ModelBlockSource``, so
split-half runs never materialise a dense matrix.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Neighbours:
    """ids[i, k] = gene position of the k-th neighbour of query rows[i] (-1 = none); z[i, k] its score (NaN)."""
    rows: np.ndarray
    ids: np.ndarray
    z: np.ndarray
    K: int

    def as_dict(self) -> dict:
        """{query position: array of neighbour positions (padding removed)}."""
        return {int(r): ids[ids >= 0] for r, ids in zip(self.rows, self.ids)}

    def to_frame(self, genes=None) -> pd.DataFrame:
        """Long table: query, rank (1..K), neighbour, z (labels if ``genes`` given)."""
        q = np.repeat(self.rows, self.K)
        rank = np.tile(np.arange(1, self.K + 1), len(self.rows))
        nb, z = self.ids.ravel(), self.z.ravel()
        ok = nb >= 0
        df = pd.DataFrame(dict(query=q[ok], rank=rank[ok], neighbour=nb[ok], z=z[ok]))
        if genes is not None:
            g = np.asarray(genes, dtype=object)
            df["query"], df["neighbour"] = g[df["query"].values], g[df["neighbour"].values]
        return df


def arm_codes(arms) -> np.ndarray:
    """Integer codes for arm labels (e.g. '1p', '1q'); missing / empty -> -1."""
    s = pd.Series(list(arms), dtype=object)
    miss = s.isna() | (s.astype(str).str.strip() == "")
    codes = pd.Series(-1, index=s.index, dtype=np.int64)
    codes[~miss] = pd.factorize(s[~miss].astype(str))[0]
    return codes.values


def index_sets(mapping: dict, genes) -> dict:
    """Translate {gene label: iterable of gene labels} into {position: int array of positions} (unknown labels
    dropped)."""
    pos = {g: i for i, g in enumerate(genes)}
    out = {}
    for g, others in mapping.items():
        if g in pos:
            idx = [pos[o] for o in others if o in pos]
            if idx:
                out[pos[g]] = np.asarray(sorted(set(idx)), dtype=np.int64)
    return out


def _iter_source(S, rows, block):
    if hasattr(S, "iter_blocks"):
        yield from S.iter_blocks(rows)
        return
    for s in range(0, len(rows), block):
        r = rows[s:s + block]
        yield r, np.asarray(S[r], dtype=np.float64)


def exclusion_mask(rows: np.ndarray, n: int, bg=None, arm=None, paralogues=None, extra=None) -> np.ndarray:
    """Boolean (len(rows) x n): True = column excluded for that query row."""
    ex = np.zeros((len(rows), n), bool)
    ex[np.arange(len(rows)), rows] = True                   # self
    if bg is not None:
        ex[:, ~np.asarray(bg, bool)] = True
    if arm is not None:
        arm = np.asarray(arm)
        a = arm[rows]
        ex |= (arm[None, :] == a[:, None]) & (a[:, None] >= 0)
    for sets in (paralogues, extra):
        if sets:
            for i, r in enumerate(rows):
                s = sets.get(int(r))
                if s is not None and len(s):
                    ex[i, np.asarray(s, dtype=np.int64)] = True
    return ex


def top_k(S, K: int, rows=None, bg=None, arm=None, paralogues=None, extra=None, block: int = 1024) -> Neighbours:
    """Top-K admissible neighbours of each query row of score source S (see module docstring)."""
    n = S.shape[1]
    if S.shape[0] != n:
        raise ValueError("score matrix must be square (same genes on both axes)")
    rows = np.arange(n) if rows is None else np.asarray(rows, dtype=np.int64)
    where = np.full(n, -1)
    where[rows] = np.arange(len(rows))
    ids = np.full((len(rows), K), -1, np.int64)
    zz = np.full((len(rows), K), np.nan, np.float32)
    done = np.zeros(len(rows), bool)
    for r, blk in _iter_source(S, rows, block):
        r = np.asarray(r, dtype=np.int64)
        V = np.array(blk, dtype=np.float64)                 # copy: never modify the source
        V[~np.isfinite(V)] = -np.inf
        V[exclusion_mask(r, n, bg, arm, paralogues, extra)] = -np.inf
        k = min(K, n)
        part = np.argpartition(-V, k - 1, axis=1)[:, :k]
        pv = np.take_along_axis(V, part, 1)
        o = np.lexsort((part, -pv), axis=1)                 # descending score, ties by lower index
        part, pv = np.take_along_axis(part, o, 1), np.take_along_axis(pv, o, 1)
        ok = np.isfinite(pv)
        w = where[r]
        ids[w, :k] = np.where(ok, part, -1)
        zz[w, :k] = np.where(ok, pv, np.nan)
        done[w] = True
    if not done.all():
        raise RuntimeError("score source did not return every requested row")
    return Neighbours(rows=rows, ids=ids, z=zz, K=K)


def assert_valid(nb: Neighbours, bg=None, arm=None, paralogues=None) -> None:
    """Assertion test (§2.2): no self, all neighbours background, no same-arm, no paralogue, no duplicates,
    scores non-increasing."""
    for r, ids, z in zip(nb.rows, nb.ids, nb.z):
        v = ids[ids >= 0]
        assert r not in v, f"gene {r} is its own neighbour"
        assert len(np.unique(v)) == len(v), f"duplicate neighbours for {r}"
        if bg is not None:
            assert np.asarray(bg, bool)[v].all(), f"non-background neighbour for {r}"
        if arm is not None and arm[r] >= 0:
            assert (np.asarray(arm)[v] != arm[r]).all(), f"same-arm neighbour for {r}"
        if paralogues and int(r) in paralogues:
            assert not np.isin(v, paralogues[int(r)]).any(), f"paralogue neighbour for {r}"
        zf = z[ids >= 0]
        assert (np.diff(zf) <= 0).all(), f"scores not sorted for {r}"
