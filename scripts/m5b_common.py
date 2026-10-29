"""m5b_common.py -- shared code for the M5b hold-out look (scripts/32_*.py ... 35_*.py). Not a pipeline step.

Implements the evaluation pieces of DESIGN.md v2.3 §3.0-§3.7 that the M5b scripts share: V2/V1/V1' vocabularies at a
release, the H-setting scorer (``vocab.score_queries`` with ``loo=False``: the query's own annotations are kept; the
IPI with/from rule is applied), R1 ranked lists, prior-only lists, matched-gene null selection, per-gene metrics
(``src/metrics.py``), clusters and paired cluster bootstraps, alternative networks (GLS/Pearson rows, split halves,
K = 10/50, no exclusions, hu.MAP 3.0 PPI), circularity look-ups (scripts/05 query, cached), and the §3.7 covariates.

Dry-run mode (``M5B_DRYRUN=1``, outputs to ``M5B_OUT``): H is replaced by LOO-sample genes with pseudo-targets
(current minus t0 V2 terms), named controls by LOO genes, bootstraps by 300 replicates; nothing in results/ is
written and no H outcome is computed. Used only to debug the code before the single logged look.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402
import m5_common as M5  # noqa: E402

from src import knownness as kn  # noqa: E402
from src import metrics as mt  # noqa: E402
from src import neighbours as nbm  # noqa: E402
from src import vocab  # noqa: E402
from src.neighbours import Neighbours  # noqa: E402

DRY = os.environ.get("M5B_DRYRUN") == "1"
ROOT = C.ROOT
if DRY:
    OUT = Path(os.environ["M5B_OUT"])
    DER, FIG = OUT / "derived", OUT / "figures"
else:
    OUT = ROOT / "results" / "holdout_eval"
    DER = C.DERIVED / "holdout_eval"
    FIG = ROOT / "manuscript" / "figures"
for d in (OUT, DER, FIG):
    d.mkdir(parents=True, exist_ok=True)

K = C.fz("predictor", "k_neighbours")
LO, HI = C.fz("vocabulary", "candidate_term_min_genes"), C.fz("vocabulary", "candidate_term_max_genes")
SMALL = C.fz("vocabulary", "small_term_max_genes")
SEED = C.fz("seeds", "bootstraps")
NBOOT = 300 if DRY else C.fz("bootstrap", "paired_cluster_replicates")
NNULL = C.fz("predictor", "matched_null_comparator_size")
T0 = C.fz("meta", "t0_go_release")
T0_DIR = f"data/raw/go/archive/{T0}"
T19_DIR = "data/raw/go/archive/2019-07-01"
CUTOFFS = "results/preregistration/pmid_date_cutoffs.tsv"
V1_ROOT = C.fz("vocabulary", "v1_cc_root")
CLUSTER_FALLBACK_FRAC = 0.20          # DEVIATIONS 2026-10-30 (§3.5 fallback), logged in LOOKS before H was opened
CONTROLS = C.fz("holdout", "named_controls") + C.fz("holdout", "weak_controls")
CASE_WINDOW = C.fz("holdout", "case_series_candidate_window")
ETC1_MITORIBO = ("GO:0045271", "GO:0005761")   # respiratory chain complex I; mitochondrial ribosome (+ descendants)
HUMAP_REFS = {"PMID:28298427", "PMID:33973408"}  # = src/orthogonal.HUMAP_REFS (hu.MAP papers; excluded from V1)
log = C.log


def jdump(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
                          + "\n")


# ============================================================================================ base data
class Base:
    """Gene index, neighbour lists, matched lists, arms, paralogues, ID maps, ontology (current)."""

    def __init__(self):
        t = time.perf_counter()
        self.gt = M5.load_index()
        self.G = len(self.gt)
        z = np.load(ROOT / M5.NB_NPZ, allow_pickle=False)
        assert (z["rows"] == np.arange(self.G)).all()
        self.ids100, self.z100 = z["ids"].astype(np.int64), z["z"].astype(np.float32)
        self.nb = self.nb_k(K)
        self.matches = M5.load_matches()
        self.cov = pd.read_csv(ROOT / "data/derived/matched/covariates.tsv", sep="\t", dtype={"hgnc_id": str})
        assert (self.cov.matrix_index.values == np.arange(self.G)).all()
        self.arm = nbm.arm_codes(self.cov.arm.values)
        self.par = C.paralogue_map(C.gene_index(self.gt.gene.values))
        self.bg = self.gt.bg.values.astype(bool)
        self.scor = self.gt.scorable.values.astype(bool)
        self.pos = {h: i for i, h in enumerate(self.gt.hgnc_id.values)}
        self.sym = self.gt.symbol.values
        self.acc_map = M5.acc_map()
        self.onto = kn.GoOntology.from_obo(str(ROOT / M5.OBO_CUR), "current")
        R = pd.read_csv(ROOT / "results/assessability/R_all.tsv", sep="\t", dtype={"hgnc_id": str})
        assert (R.matrix_index.values == np.arange(self.G)).all()
        self.R = R.R.values.astype(float)
        self.zmean = np.nanmean(self.z100[:, :K].astype(np.float64), 1)
        log(f"base loaded in {time.perf_counter() - t:.0f} s")

    def nb_k(self, k: int) -> Neighbours:
        return Neighbours(rows=np.arange(self.G), ids=self.ids100[:, :k].copy(), z=self.z100[:, :k].copy(), K=k)


# ============================================================================================ vocabularies
def build_v2(base: Base, gaf: str, lo: int = LO, hi: int = HI, label: str = "") -> vocab.V2:
    t = time.perf_counter()
    v = vocab.build_v2(str(ROOT / gaf), base.onto, base.acc_map, base.gt.hgnc_id.values, base.scor, lo=lo, hi=hi)
    log(f"V2 {label} built in {time.perf_counter() - t:.0f} s: {v.stats['n_columns']} columns, "
        f"{v.stats['n_candidate_terms_base']} base candidates, B = {v.stats['n_annotated_background']}")
    return v


def build_v1(base: Base, gaf: str, lo: int = LO, hi: int = HI, label: str = "") -> vocab.V2:
    """V1 = GO CC terms under GO:0032991 (root excluded), same rules as V2 (D1 evidence, NOT and colocalizes_with
    dropped, current obo, is_a/part_of propagation, IPI with/from rule); rows citing hu.MAP papers dropped
    (DESIGN §3.0 'hu.MAP excluded'; = src/orthogonal.complex_gold_standard). Built with ``vocab.build_v2`` with the
    aspect/namespace constants temporarily set to CC (src/ is not modified), then restricted to V1 columns."""
    t = time.perf_counter()
    g = kn.read_gaf(str(ROOT / gaf))
    hm = g.reference.map(lambda r: any(x in HUMAP_REFS for x in str(r).split("|")))
    g = g[~hm.values]
    old_asp, old_ns = kn.D1_ASPECTS, vocab.BPMF_NS
    try:
        kn.D1_ASPECTS = frozenset({"C"})
        vocab.BPMF_NS = ("cellular_component",)
        v = vocab.build_v2(g, base.onto, base.acc_map, base.gt.hgnc_id.values, base.scor, lo=lo, hi=hi)
    finally:
        kn.D1_ASPECTS, vocab.BPMF_NS = old_asp, old_ns
    keep = np.array([t != V1_ROOT and V1_ROOT in base.onto.ancestors(t) for t in v.terms])
    A = v.A[:, keep].tocsr()
    v1 = vocab.V2(genes=v.genes, scorable=v.scorable, terms=v.terms[keep], A=A, size=v.size[keep],
                  annotated=np.asarray(A.sum(1)).ravel() > 0, lo=lo, hi=hi, onto=v.onto, rows=v.rows,
                  prop={p: frozenset(x for x in s if x != V1_ROOT and V1_ROOT in base.onto.ancestors(x))
                        for p, s in v.prop.items()},
                  stats=dict(v.stats, humap_rows_dropped=int(hm.sum()), n_columns=int(keep.sum()),
                             n_candidate_terms_base=int(((v.size[keep] >= lo) & (v.size[keep] <= hi)).sum())),
                  ipi_rule=True)
    log(f"V1 {label} built in {time.perf_counter() - t:.0f} s: {v1.stats['n_columns']} columns")
    return v1


def build_v1prime(base: Base, v1_cur: vocab.V2, lo: int, hi: int) -> tuple[vocab.V2, dict]:
    """V1' (current) = V1 ∪ Complex Portal (hu.MAP-identity entries excluded) ∪ MitoCarta3.0 MitoPathways (every
    level of the pathway hierarchy). Membership matrix over scorable genes; IPI rule not applicable (no GAF rows)."""
    import re
    import xlrd
    from src import orthogonal as og
    m = og.mapper()
    members: dict = {}
    names: dict = {}
    # V1 (current, propagated)
    for p, s in v1_cur.prop.items():
        for t in s:
            members.setdefault(t, set()).add(p)
    for t in members:
        names[t] = base.onto.name(t)
    cp = pd.read_csv(ROOT / "data/raw/complexportal/9606.tsv", sep="\t", dtype=str, keep_default_na=False)
    cp = cp[~cp["Cross references"].str.contains(r"humap:[^|]*\(identity\)")]
    for cid, nm, part in zip(cp["#Complex ac"], cp["Recommended name"], cp["Expanded participant list"]):
        mem = set()
        for tok in part.split("|"):
            a = re.sub(r"\(.*$", "", tok).strip()
            h = m.from_acc(a) if m.acc_status(a) == "mapped" else None
            if h and h in base.pos and base.scor[base.pos[h]]:
                mem.add(base.pos[h])
        if mem:
            members["CP:" + cid] = mem
            names["CP:" + cid] = nm
    b = xlrd.open_workbook(str(ROOT / "data/raw/mitocarta/Human.MitoCarta3.0.xls")).sheet_by_name(
        "A Human MitoCarta3.0")
    hdr = b.row_values(0)
    ci, pi = hdr.index("HumanGeneID"), hdr.index("MitoCarta3.0_MitoPathways")
    for i in range(1, b.nrows):
        r = b.row_values(i)
        e = str(int(r[ci])) if isinstance(r[ci], float) else str(r[ci])
        h = m.from_entrez(e)
        if not (h and h in base.pos and base.scor[base.pos[h]]):
            continue
        for path in str(r[pi]).split("|"):
            parts = [x.strip() for x in path.split(">") if x.strip() and x.strip() != "0"]
            for k in range(1, len(parts) + 1):
                key = "MC:" + " > ".join(parts[:k])
                members.setdefault(key, set()).add(base.pos[h])
                names[key] = "MitoCarta: " + " > ".join(parts[:k])
    terms = sorted(t for t, s in members.items() if len(s) >= lo)
    col = {t: i for i, t in enumerate(terms)}
    r, c = [], []
    for t in terms:
        for p in members[t]:
            r.append(p)
            c.append(col[t])
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(base.G, len(terms)))
    A.sum_duplicates()
    A.sort_indices()
    v = vocab.V2(genes=base.gt.hgnc_id.values, scorable=base.scor, terms=np.asarray(terms, dtype=object), A=A,
                 size=np.asarray(A.sum(0)).ravel().astype(np.int64), annotated=np.asarray(A.sum(1)).ravel() > 0,
                 lo=lo, hi=hi, onto=base.onto, rows=None, prop=None, stats=dict(n_columns=len(terms)), ipi_rule=False)
    return v, names


# ============================================================================================ networks
def padded(G: int, rows, ids, z, k: int) -> Neighbours:
    """Neighbours over all G rows; rows not in ``rows`` are empty (-1 / NaN)."""
    I = np.full((G, k), -1, np.int64)
    Z = np.full((G, k), np.nan, np.float32)
    I[rows], Z[rows] = ids, z
    return Neighbours(rows=np.arange(G), ids=I, z=Z, K=k)


class RowSource:
    """Square-shaped score source for ``neighbours.top_k`` from a rows x columns baseline block (columns = matrix
    positions ``cols``); non-columns are -inf."""

    def __init__(self, mat, row_of: dict, cols: np.ndarray, G: int):
        self.mat, self.row_of, self.cols, self.shape = mat, row_of, cols, (G, G)

    def iter_blocks(self, rows):
        for s in range(0, len(rows), 256):
            r = rows[s:s + 256]
            V = np.full((len(r), self.shape[1]), -np.inf)
            V[:, self.cols] = np.asarray(self.mat[[self.row_of[int(x)] for x in r]], dtype=np.float64)
            yield r, V


def baseline_network(base: Base, kind: str, queries) -> Neighbours:
    """GLS or Pearson rows (scripts/16) -> N(g) with the §3.1 exclusions (self, BG only, same arm, paralogues)."""
    rows = pd.read_csv(ROOT / "data/derived/baselines/rows.tsv", sep="\t")
    cols = pd.read_csv(ROOT / "data/derived/baselines/cols.tsv", sep="\t")
    mat = np.load(ROOT / f"data/derived/baselines/{kind}_rows.npy", mmap_mode="r")
    row_of = dict(zip(rows.matrix_index.values, rows.row_index.values))
    q = np.asarray(sorted(set(int(x) for x in queries)), dtype=np.int64)
    miss = [int(x) for x in q if int(x) not in row_of]
    assert not miss, f"{kind}: {len(miss)} queries without baseline rows"
    src = RowSource(mat, row_of, cols.matrix_index.values.astype(np.int64), base.G)
    nb = nbm.top_k(src, K, rows=q, bg=base.bg, arm=base.arm, paralogues=base.par)
    nbm.assert_valid(nb, bg=base.bg, arm=base.arm, paralogues=base.par)
    return padded(base.G, q, nb.ids, nb.z, K)


def restrict_with_z(ids, z, allowed, k):
    ids = np.asarray(ids, dtype=np.int64)
    ok = (ids >= 0) & allowed[np.where(ids >= 0, ids, 0)]
    rank = np.cumsum(ok, 1)
    keep = ok & (rank <= k)
    I = np.full((ids.shape[0], k), -1, np.int64)
    Z = np.full((ids.shape[0], k), np.nan, np.float32)
    r, c = np.nonzero(keep)
    I[r, rank[r, c] - 1] = ids[r, c]
    Z[r, rank[r, c] - 1] = z[r, c]
    return I, Z


def half_networks(base: Base):
    """Yield (seed, half, Neighbours) for the 10 split-half runs: top-60 half lists restricted to BG_A ∩ BG_B ∩
    BG_full, first K (scripts/15 rule; §3.1 exclusions were applied when the half lists were built)."""
    SH = C.DERIVED / "splithalf"
    for s in C.fz("seeds", "split_half_seeds"):
        zz = [np.load(SH / f"seed{s}_half{h}.npz") for h in (0, 1)]
        common = zz[0]["bg_half"].astype(bool) & zz[1]["bg_half"].astype(bool) & base.bg
        for h in (0, 1):
            I, Z = restrict_with_z(zz[h]["ids"], zz[h]["z"], common, K)
            yield s, h, Neighbours(rows=np.arange(base.G), ids=I, z=Z, K=K)


def noexcl_network(base: Base, queries) -> Neighbours:
    """Full zavg_BEF, K = 25, self excluded and BG only, no same-arm / paralogue exclusion (secondary batch)."""
    M = np.load(C.FULL_DIR / "zavg_BEF.npy", mmap_mode="r")
    q = np.asarray(sorted(set(int(x) for x in queries)), dtype=np.int64)
    nb = nbm.top_k(M, K, rows=q, bg=base.bg)
    nbm.assert_valid(nb, bg=base.bg)
    return padded(base.G, q, nb.ids, nb.z, K)


def humap_network(base: Base, queries) -> tuple[Neighbours, dict]:
    """hu.MAP 3.0 PPI module transfer: N(g) = top-25 scorable partners by hu.MAP 3.0 probability (all-PPI file,
    UniProt accessions mapped with the HGNC/UniProt accession map; a pair mapping to several genes is expanded;
    max probability per gene pair); weight = probability. Self excluded; no BG, arm or paralogue restriction."""
    q = set(int(x) for x in queries)
    accs = {a for a, hs in base.acc_map.items() if any(base.pos.get(h) in q for h in hs)}
    parts = []
    for ch in pd.read_csv(ROOT / "data/raw/humap3/humap3_all_ppis_202305.pairsWprob.gz", sep="\t", header=None,
                          names=["a", "b", "p"], dtype={"a": str, "b": str, "p": float}, chunksize=2_000_000):
        parts.append(ch[ch.a.isin(accs) | ch.b.isin(accs)])
    E = pd.concat(parts)
    st = dict(pairs_touching_queries=len(E))

    def to_pos(a):
        return [base.pos[h] for h in base.acc_map.get(kn.strip_isoform(a), ()) if h in base.pos
                and base.scor[base.pos[h]]]
    best: dict = {}
    for a, b, p in zip(E.a.values, E.b.values, E.p.values):
        pa, pb = to_pos(a), to_pos(b)
        for x in pa:
            for y in pb:
                if x == y:
                    continue
                for g, j in ((x, y), (y, x)):
                    if g in q and best.get((g, j), -1) < p:
                        best[(g, j)] = p
    by: dict = {}
    for (g, j), p in best.items():
        by.setdefault(g, []).append((-p, j))
    rows = np.asarray(sorted(q), dtype=np.int64)
    I = np.full((len(rows), K), -1, np.int64)
    Z = np.full((len(rows), K), np.nan, np.float32)
    for i, g in enumerate(rows):
        lst = sorted(by.get(int(g), []))[:K]
        for k, (mp, j) in enumerate(lst):
            I[i, k], Z[i, k] = j, -mp
    st["queries_with_partner"] = int((I[:, 0] >= 0).sum())
    st["queries_with_ge2_partners"] = int((I[:, 1] >= 0).sum())
    return padded(base.G, rows, I, Z, K), st


# ============================================================================================ scoring
class Scored:
    """R1 ranked lists and per-query sizes for a set of queries scored in the H setting (loo=False)."""

    def __init__(self, v2: vocab.V2, nb_all: Neighbours, matches: dict, queries, label: str = ""):
        t = time.perf_counter()
        q = np.asarray(sorted(set(int(x) for x in queries)), dtype=np.int64)
        self.sc = vocab.score_queries(v2, nb_all, matches, q, loo=False)
        self.v2 = v2
        self.qpos = {int(g): i for i, g in enumerate(q)}
        self.r1 = self.sc.ranked("R1")
        log(f"scored {len(q)} queries ({label}) in {time.perf_counter() - t:.0f} s")

    def sizes(self, g: int) -> np.ndarray:
        return self.sc.sizes[self.qpos[int(g)]]

    def prior(self, g: int) -> list:
        i = self.qpos[int(g)]
        return [int(c) for c in self.sc.prior_rank(i, self.v2.candidates(self.sc.sizes[i]))]


def select_nulls(v2: vocab.V2, matches: dict, queries, targets_ids: dict, n: int = NNULL) -> tuple[dict, dict]:
    """First n matches of g (500-list order) that are not t0-annotated (V2 membership at the release in use) to any
    term of T(g) (§3.3 'the comparator alone additionally skips matches annotated to T(g)')."""
    out, skipped = {}, {}
    for g in queries:
        T = set(targets_ids[g])
        sel, sk = [], 0
        for m in matches[int(g)]:
            if T & v2.prop.get(int(m), frozenset()):
                sk += 1
                continue
            sel.append(int(m))
            if len(sel) == n:
                break
        out[int(g)], skipped[int(g)] = sel, sk
    return out, skipped


def metrics_one(lst, T: set, drop: set, size: np.ndarray) -> dict:
    lst = [c for c in lst if c not in drop]
    hit = mt.hit_at_1(lst, T)
    sz = {int(c): int(size[c]) for c in set(lst) | set(T)}
    return dict(hit1=hit, rr=mt.reciprocal_rank(lst, T), top1=lst[0] if lst else -1,
                top1size=float(size[lst[0]]) if lst else np.nan, has_pred=bool(lst),
                hit1_small=mt.hit_at_1_restricted(lst, T, sz, SMALL))


def evaluate(queries, lists: dict, targets: dict, drops: dict, sizes_of) -> pd.DataFrame:
    """lists: {g: ranked columns}; targets: {g: set of columns}; drops: {g: set of columns removed from lists};
    sizes_of(g): per-query size vector of g (used for the top-1 size and the <= 50 restriction)."""
    rows = []
    for g in queries:
        r = metrics_one(lists.get(int(g), []), targets[int(g)], drops.get(int(g), set()), sizes_of(int(g)))
        r["pos"] = int(g)
        rows.append(r)
    return pd.DataFrame(rows).set_index("pos")


def evaluate_null(queries, nulls: dict, lists: dict, targets: dict, drops: dict, sizes_of) -> pd.DataFrame:
    """Matched-gene null: mean over the selected matches of each match's metrics against T(g) (top-1 size: mean)."""
    rows = []
    for g in queries:
        ms = nulls[int(g)]
        rr = [metrics_one(lists.get(m, []), targets[int(g)], drops.get(int(g), set()), sizes_of(int(g)))
              for m in ms]
        d = pd.DataFrame(rr)
        rows.append(dict(pos=int(g), hit1=d.hit1.mean(), rr=d.rr.mean(), top1=-1,
                         top1size=d.top1size.mean(), has_pred=d.has_pred.mean(),
                         hit1_small=d.hit1_small.mean() if d.hit1_small.notna().any() else np.nan,
                         n_null=len(ms)))
    return pd.DataFrame(rows).set_index("pos")


def method_set(v2, nb_all, matches, queries, targets, drops, nulls, label, extra_null_lists=None):
    """zavg (or network) R1, prior-only and matched-null per-gene metrics on one network/vocabulary."""
    allq = set(int(g) for g in queries) | {m for ms in nulls.values() for m in ms}
    S = Scored(v2, nb_all, matches, allq, label)
    sizes_of = S.sizes
    out = dict(net=evaluate(queries, S.r1, targets, drops, sizes_of),
               prior=evaluate(queries, {int(g): S.prior(g) for g in queries}, targets, drops, sizes_of),
               null=evaluate_null(queries, nulls, S.r1, targets, drops, sizes_of))
    return out, S


# ============================================================================================ statistics
def clusters_for(genes, pmid_sets: dict, nb_all: Neighbours) -> dict:
    """PMID-only and PMID + N(g) cluster labels (DESIGN §3.5) and the fallback choice (DEVIATIONS 2026-10-30)."""
    genes = [int(g) for g in genes]
    nbd = {g: set(nb_all.ids[g][nb_all.ids[g] >= 0].tolist()) for g in genes}
    pm = mt.clusters_from_links(genes, pmids=pmid_sets)
    both = mt.clusters_from_links(genes, pmids=pmid_sets, neighbours=nbd)

    def summ(cl):
        s = np.bincount(np.unique(cl, return_inverse=True)[1])
        return dict(n_clusters=int(len(s)), largest=int(s.max()), largest_frac=float(s.max() / len(cl)),
                    singletons=int((s == 1).sum()))
    sb, sp_ = summ(both), summ(pm)
    use = "PMID-only (fallback)" if sb["largest_frac"] > CLUSTER_FALLBACK_FRAC else "PMID+N(g)"
    return dict(pmid=pm, both=both, primary=pm if use.startswith("PMID-only") else both,
                sensitivity=both if use.startswith("PMID-only") else pm, primary_name=use,
                sensitivity_name="PMID+N(g)" if use.startswith("PMID-only") else "PMID-only",
                summary={"PMID-only": sp_, "PMID+N(g)": sb})


def pdiff(a, b, cl, n_boot=None) -> dict:
    r = mt.paired_cluster_bootstrap(np.asarray(a, float), np.asarray(b, float), cl, n_boot=n_boot or NBOOT, seed=SEED)
    return r


def mci(a, cl, n_boot=None) -> dict:
    return mt.cluster_bootstrap_mean(np.asarray(a, float), cl, n_boot=n_boot or NBOOT, seed=SEED)


def fmt_ci(ci, nd=3, sign=False):
    f = f"{{:+.{nd}f}}" if sign else f"{{:.{nd}f}}"
    return f"{f.format(ci[0])} to {f.format(ci[1])}"


def drow(name, r, extra=None) -> dict:
    d = dict(comparison=name, n=r["n"], n_clusters=r["n_clusters"], mean_a=r.get("mean_a", np.nan),
             mean_b=r.get("mean_b", np.nan), diff=r["estimate"], ci_lo=r["ci_percentile"][0],
             ci_hi=r["ci_percentile"][1], bca_lo=r["ci_bca"][0], bca_hi=r["ci_bca"][1],
             design_effect=r["design_effect"], excludes_zero=bool(r["ci_percentile"][0] > 0 or r["ci_percentile"][1] < 0))
    if extra:
        d.update(extra)
    return d


# ============================================================================================ circularity
_CIRC = None


def circ_module():
    global _CIRC
    if _CIRC is None:
        spec = importlib.util.spec_from_file_location("circ05", ROOT / "scripts" / "05_circularity_query.py")
        _CIRC = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_CIRC)
        Path(_CIRC.CACHE).mkdir(parents=True, exist_ok=True)
    return _CIRC


def circ_lookup(pmids) -> pd.DataFrame:
    """pmid -> found_in_europepmc, full_text_searchable, circular_flag. Known PMIDs from results/holdout/
    circularity_flags.tsv and the LOO table; others queried with the scripts/05 query (cached, batched)."""
    pmids = sorted({int(p) for p in pmids})
    known = pd.read_csv(ROOT / "results/holdout/circularity_flags.tsv", sep="\t")[
        ["pmid", "found_in_europepmc", "full_text_searchable", "circular_flag"]]
    loo = pd.read_csv(ROOT / "results/calibration/loo_circularity_pmids.tsv.gz", sep="\t")[
        ["pmid", "found_in_europepmc", "full_text_searchable", "circular_flag"]]
    known = pd.concat([known, loo]).drop_duplicates("pmid").set_index("pmid")
    new = [p for p in pmids if p not in known.index]
    rows = []
    if new and not DRY:
        circ = circ_module()
        meta, hits = {}, set()
        for i in range(0, len(new), circ.BATCH):
            b = new[i:i + circ.BATCH]
            for r in circ.search_all(circ.ext_clause(b) + " AND SRC:MED", "lite"):
                if r.get("pmid"):
                    meta[int(r["pmid"])] = r
            for r in circ.search_all(circ.ext_clause(b) + " AND SRC:MED AND " + circ.TERM_CLAUSE, "idlist"):
                if r.get("pmid"):
                    hits.add(int(r["pmid"]))
        for p in new:
            rows.append(dict(pmid=p, found_in_europepmc=p in meta,
                             full_text_searchable=meta.get(p, {}).get("inEPMC") == "Y", circular_flag=p in hits))
    elif new:
        rows = [dict(pmid=p, found_in_europepmc=True, full_text_searchable=False, circular_flag=False) for p in new]
    out = pd.concat([known.reset_index(), pd.DataFrame(rows)]) if rows else known.reset_index()
    out = out[out.pmid.isin(pmids)].drop_duplicates("pmid").set_index("pmid")
    out.attrs["n_new_queried"] = len(new)
    return out


def target_states(pmid_lists, flags: pd.DataFrame):
    """Per target (list of supporting PMIDs): flagged (any PMID flagged), unscannable (not flagged and no PMID found
    in Europe PMC, incl. no PMID at all) -- the scripts/05 / scripts/30 definitions."""
    fl, fd = flags.circular_flag.to_dict(), flags.found_in_europepmc.to_dict()
    out = []
    for ps in pmid_lists:
        anyf = any(fl.get(p, False) for p in ps)
        allf = bool(ps) and all(fl.get(p, False) for p in ps)
        uns = (not anyf) and not any(fd.get(p, False) for p in ps)
        out.append((anyf, allf, uns))
    return out


def support_pmids(v: vocab.V2, pos: int, term: str) -> list:
    """Supporting PMIDs of (gene, term) from the kept rows of a vocabulary (rows to the term or a descendant)."""
    d = v.rows[v.rows.pos == pos]
    m = [term in v.onto.ancestors(t) for t in d.go_id.values]
    return kn.pmids_from_refs(d.reference.values[np.asarray(m, bool)]) if len(d) else []


# ============================================================================================ covariates (§3.6, §3.7)
def coverage(base: Base, v: vocab.V2, nb: Neighbours | None = None) -> np.ndarray:
    nb = nb or base.nb
    ids = nb.ids
    ok = ids >= 0
    a = v.annotated[np.where(ok, ids, 0)] & ok
    return a.sum(1) / np.maximum(ok.sum(1), 1)


def base_top_sizes(base: Base, v: vocab.V2) -> np.ndarray:
    """Per gene: per-release size of the top reportable R1 term with the base membership (no per-query removals);
    NaN when there is none or the gene is not scorable. Percentile reference for log top-term size (§3.7)."""
    ts = vocab.all_gene_scores(base.nb, v)
    S, P = ts.S.tocsr(), ts.n_sup.tocsr()
    cand = v.candidates(v.size)
    out = np.full(base.G, np.nan)
    for i in np.flatnonzero(base.scor):
        a, b = S.indptr[i], S.indptr[i + 1]
        idx, val = S.indices[a:b], S.data[a:b]
        n = np.asarray(P[i, idx].todense()).ravel() if len(idx) else np.array([])
        ok = cand[idx] & (np.round(n) >= 2) & (val > 0)
        if ok.any():
            j = idx[ok][np.argmax(val[ok])]
            out[i] = v.size[j]
    return out


def pct_rank(x, ref) -> np.ndarray:
    """Mid-rank percentile (0-1) of x within the sorted finite reference."""
    ref = np.sort(np.asarray(ref, float)[np.isfinite(ref)])
    x = np.asarray(x, float)
    lo = np.searchsorted(ref, x, "left")
    hi = np.searchsorted(ref, x, "right")
    p = (lo + hi) / (2.0 * len(ref))
    return np.where(np.isfinite(x), p, np.nan)


def load_families():
    f = pd.read_csv(ROOT / "config/term_families.tsv", sep="\t", comment="#")
    f = f.sort_values("order", kind="stable")
    return [(fam, set(d.go_id)) for fam, d in f.groupby("family", sort=False)]


def family_of(term: str, onto, fams) -> str:
    anc = onto.ancestors(term)
    for fam, ids in fams:
        if anc & ids:
            return fam
    return "other"


CAL_COVS = ["zmean", "R", "cov_pct", "size_pct"]
CAL_SIGNS = [1, 1, 1, -1]


def design(df: pd.DataFrame, fams_kept: list, ref_fam: str) -> tuple[np.ndarray, list, list]:
    """§3.7 design: top-K mean zavg (>= 0), R(g) (>= 0), coverage percentile (>= 0), log top-term size percentile
    (<= 0), family dummies (free; reference family = ``ref_fam``; families with < 30 H genes pooled as 'rare')."""
    X = [df[c].values.astype(float) for c in CAL_COVS]
    names, signs = list(CAL_COVS), list(CAL_SIGNS)
    fam = df.family.where(df.family.isin(fams_kept), "rare")
    for f in [*[x for x in fams_kept if x != ref_fam], "rare"]:
        X.append((fam == f).values.astype(float))
        names.append(f"fam_{f}")
        signs.append(0)
    return np.column_stack(X), names, signs


def reliability(p, y, n_bins=10, min_n=30) -> pd.DataFrame:
    """Deciles of predicted probability (quantile bins), adjacent bins merged until each holds >= min_n genes."""
    p, y = np.asarray(p, float), np.asarray(y, float)
    edges = np.unique(np.quantile(p, np.linspace(0, 1, n_bins + 1)))
    b = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    groups = [np.flatnonzero(b == i) for i in range(len(edges) - 1)]
    groups = [g for g in groups if len(g)]
    merged = []
    for g in groups:
        if merged and len(merged[-1]) < min_n:
            merged[-1] = np.r_[merged[-1], g]
        else:
            merged.append(g)
    if len(merged) > 1 and len(merged[-1]) < min_n:
        merged[-2] = np.r_[merged[-2], merged.pop()]
    rows = []
    for i, g in enumerate(merged):
        lo, hi = mt._wilson(y[g].sum(), len(g))
        rows.append(dict(bin=i, n=len(g), p_min=p[g].min(), p_max=p[g].max(), mean_pred=p[g].mean(),
                         obs_rate=y[g].mean(), ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(rows)


def smd(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    v = (a.var(ddof=1) + b.var(ddof=1)) / 2
    return float((a.mean() - b.mean()) / np.sqrt(v)) if v > 0 else 0.0


def logistic_fit(X, y, w=None, iters=50):
    """Plain (unconstrained) logistic regression by Newton-Raphson on standardised X (for the §3.6 U-vs-H model)."""
    X = np.asarray(X, float)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1
    Z = np.c_[np.ones(len(X)), (X - mu) / sd]
    beta = np.zeros(Z.shape[1])
    for _ in range(iters):
        eta = np.clip(Z @ beta, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        W = p * (1 - p)
        H = Z.T @ (Z * W[:, None]) + 1e-8 * np.eye(Z.shape[1])
        step = np.linalg.solve(H, Z.T @ (y - p))
        beta += step
        if np.abs(step).max() < 1e-9:
            break
    return lambda Xn: 1 / (1 + np.exp(-np.clip(np.c_[np.ones(len(Xn)), (np.asarray(Xn, float) - mu) / sd] @ beta,
                                              -30, 30)))


def fams_kept(df: pd.DataFrame, min_n: int | None = None):
    """Families with >= 30 H genes (among genes with a top term) and the reference family ('other' if kept)."""
    min_n = min_n or C.fz("calibration", "min_h_genes_per_family")
    cnt = df.family.value_counts()
    kept = sorted(cnt[cnt >= min_n].index.tolist())
    ref = "other" if "other" in kept else cnt.idxmax()
    return kept, ref, cnt.to_dict()


def calib_metrics(p, y) -> dict:
    ci = mt.calibration_intercept_slope(p, y)
    return dict(n=int(len(y)), mean_pred=float(np.mean(p)), obs_rate=float(np.mean(y)), brier=mt.brier(p, y),
                brier_ref_constant=mt.brier(np.full(len(y), np.mean(y)), y),
                intercept=ci["intercept"], intercept_ci=ci["intercept_ci"], slope=ci["slope"], slope_ci=ci["slope_ci"])
