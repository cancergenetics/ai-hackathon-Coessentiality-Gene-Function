"""m6_common.py -- shared code for the M6 hypothesis-generation scripts (scripts/40_*.py ... 45_*.py). Not a step.

U genes are scored with exactly the H code path of M5b (``m5b_common.Base``, ``vocab.score_queries(loo=False)``,
current V2, R1, reportable = >= 2 supporting partners). Operational choices: DEVIATIONS.md rows dated 2026-10-29 (M6).
Outputs: results/ledger/ (committed), data/derived/ledger/ (git-ignored caches).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

ROOT = C.ROOT
OUT = ROOT / "results" / "ledger"
FIG = OUT / "figdata"
DER = C.DERIVED / "ledger"
for d in (OUT, FIG, DER):
    d.mkdir(parents=True, exist_ok=True)
log = C.log
U_TSV = "preregistration/uncharacterised_genes.tsv"
ASSESS = "results/assessability/assessability_U.tsv"
MODEL_JSON = "results/calibration/model_H.json"


def jdump(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
                          + "\n")


def read_tsv(name: str, **kw) -> pd.DataFrame:
    return pd.read_csv(OUT / name, sep="\t", dtype={"hgnc_id": str}, keep_default_na=False,
                       na_values=["", "nan", "NaN"], **kw)


def model() -> dict:
    return json.loads((ROOT / MODEL_JSON).read_text())


def supporting(v2, g: int, col: int, ids: np.ndarray, z: np.ndarray, removal=None) -> list[tuple[int, float]]:
    """[(partner position, z)] for partners j in N(g) with z > 0 that are members of column ``col`` under g's
    per-query removals (the S(g,t) definition of ``vocab.score_queries``)."""
    rem = v2.removal(g, loo=False) if removal is None else removal
    out = []
    for j, zz in zip(ids, z):
        if j < 0 or not np.isfinite(zz) or zz <= 0:
            continue
        a = v2.A.indices[v2.A.indptr[j]:v2.A.indptr[j + 1]]
        if col not in a:
            continue
        if int(j) in rem.rows and col in set(rem.rows[int(j)].tolist()):
            continue
        out.append((int(j), float(zz)))
    return out


def model_line_lineage() -> pd.Series:
    m = pd.read_csv(ROOT / "data/raw/depmap/Model.csv", usecols=["ModelID", "OncotreeLineage", "CCLEName"],
                    dtype=str)
    return m.set_index("ModelID")


def default_entry(path: str, usecols=None) -> pd.DataFrame:
    """DepMap Omics wide matrix (rows = profiles) -> ModelID-indexed DataFrame of the default entry per model
    (IsDefaultEntryForModel == Yes); gene columns 'SYMBOL (ENTREZ)' kept."""
    t = time.perf_counter()
    df = pd.read_csv(ROOT / path, usecols=usecols, low_memory=False)
    if "IsDefaultEntryForModel" in df.columns:
        df = df[df.IsDefaultEntryForModel.astype(str).isin(["Yes", "True", "true", "1"])]
    df = df.drop_duplicates("ModelID").set_index("ModelID")
    drop = [c for c in df.columns if not (isinstance(c, str) and c.endswith(")"))]
    df = df.drop(columns=drop)
    log(f"read {path}: {df.shape} in {time.perf_counter() - t:.0f} s")
    return df


def entrez_of_col(cols) -> np.ndarray:
    return pd.Series(list(cols)).str.extract(r"\((\d+)\)\s*$")[0].values


def omics_by_position(df: pd.DataFrame, gt: pd.DataFrame, cache: str | None = None) -> tuple[np.ndarray, list]:
    """Omics matrix (models x matrix positions; NaN where the gene has no column), matched on Entrez id of the
    DepMap gene-effect column labels (gt.gene = 'SYMBOL (ENTREZ)'). Cached as float32 .npy under DER."""
    if cache and (DER / f"{cache}.npy").exists():
        X = np.load(DER / f"{cache}.npy")
        rows = json.loads((DER / f"{cache}.json").read_text())
        return X, rows
    ent_cols = entrez_of_col(df.columns)
    col_of = {}
    for i, e in enumerate(ent_cols):
        if isinstance(e, str) and e not in col_of:
            col_of[e] = i
    ent_g = entrez_of_col(gt.gene.values)
    X = np.full((len(df), len(gt)), np.nan, np.float32)
    V = df.values.astype(np.float32)
    for p, e in enumerate(ent_g):
        k = col_of.get(e)
        if k is not None:
            X[:, p] = V[:, k]
    rows = [str(x) for x in df.index]
    if cache:
        np.save(DER / f"{cache}.npy", X)
        (DER / f"{cache}.json").write_text(json.dumps(rows))
    return X, rows


def fmt(x, nd=3):
    try:
        return "—" if x is None or not np.isfinite(float(x)) else f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


# ============================================================================================ ranking (§6.1)
def pool_table(pc: pd.DataFrame, fl: pd.DataFrame, sup: pd.DataFrame | None = None,
               chk: pd.DataFrame | None = None) -> pd.DataFrame:
    """Per U gene with a prediction: §6.1 conditions, tier and fill group. pc = u_pcal.tsv, fl = u_flags.tsv,
    sup = real-prediction support rows (hgnc_id, diag_ok, diag_support, contradiction, n_classes, classes), chk =
    top-40 checks (hgnc_id, demote_A). Missing support -> treated as not yet assessed (diag_ok False, no contradiction,
    n_classes 0, support_done False)."""
    from src import ledger as LG
    d = pc[pc.has_prediction.astype(bool)].merge(fl[["hgnc_id", "excl43"]], on="hgnc_id", how="left")
    d["excl43"] = d.excl43.fillna(False).astype(bool)
    if sup is not None and len(sup):
        s = sup[["hgnc_id", "diag_ok", "diag_support", "contradiction", "n_classes", "supporting_classes"]]
        d = d.merge(s, on="hgnc_id", how="left")
        d["support_done"] = d.diag_ok.notna()
    else:
        d["diag_ok"], d["diag_support"], d["contradiction"], d["n_classes"] = np.nan, np.nan, np.nan, np.nan
        d["supporting_classes"], d["support_done"] = "", False
    d["diag_ok"] = d.diag_ok.fillna(False).astype(bool)
    d["diag_support"] = d.diag_support.fillna(False).astype(bool)
    d["contradiction"] = d.contradiction.fillna(False).astype(bool)
    d["n_classes"] = d.n_classes.fillna(0).astype(int)
    d["supporting_classes"] = d.supporting_classes.fillna("")
    if chk is not None and len(chk):
        d = d.merge(chk[["hgnc_id", "demote_A"]], on="hgnc_id", how="left")
    else:
        d["demote_A"] = np.nan
    d["checks_done"] = d.demote_A.notna()
    d["demote_A"] = d.demote_A.fillna(False).astype(bool)
    d["scorable"] = True
    d["expressed"] = d.expressed_design.astype(bool)
    d["assessable"] = d.assessable_design.astype(bool)
    d["in_support"] = d.support_category == "in_support"
    d["tier"] = [LG.tier_of(r) for r in d.to_dict("records")]
    d["pool"] = d.expressed & d.assessable & d.in_support
    clean = ~d.excl43 & ~d.contradiction & ~d.demote_A
    d["group"] = np.where(d.tier == "A", 0, np.where(d.tier == "B", 1, np.where(clean, 2, 3)))
    return d


def rank_pool(d: pd.DataFrame, n: int = 40) -> pd.DataFrame:
    from src import ledger as LG
    # mito cap: <= 6 mitochondrial-family calls within the top 20 (frozen tiers.mito_cap_top20_max_count)
    return LG.fill_top(d[d.pool], n=n, cap_top=20, cap_max=C.fz("tiers", "mito_cap_top20_max_count"))


# ============================================================================================ orthogonal support (§5.3)
class SupportRunner:
    """Admitted independent sources (results/orthogonal/admission.tsv; the §5.1b P components folded into P_group),
    the four named high-reliability localisation sources for the contradiction rule (DEVIATIONS 2026-10-29
    interpretation row), homology (reported only). Results cached in data/derived/ledger/support_cache.pkl keyed by
    (tested gene, term)."""

    CACHE = DER / "support_cache.pkl"

    def __init__(self):
        from src import orthogonal as o
        t = time.perf_counter()
        self.o = o
        m = o.mapper()
        adm = pd.read_csv(ROOT / "results/orthogonal/admission.tsv", sep="\t")
        admitted = set(adm.loc[adm.admitted.astype(str) == "True", "source"])
        comps = [c for c in o.P_GROUP if c in admitted]
        names = [n for n in o.LOADERS if n in admitted or n in comps or n in ("OpenCell_loc", "HCM_NMF", "MitoCarta3",
                                                                              "Homology_IBA_ISO")]
        S = {n: o.LOADERS[n](m) for n in names}
        S["P_group"] = o.union_sources("P_group", "P", [S[c] for c in comps])
        self.sources = [S[n] for n in ["P_group", *[x for x in o.LOADERS if x in admitted and x not in comps]]
                        if n in S and S[n].independent]
        self.contra = [S[n] for n in ("HPA", "OpenCell_loc", "HCM_NMF", "MitoCarta3")]
        self.hpa = S["HPA"]
        self.homology = S["Homology_IBA_ISO"]
        self.B = C.fz("orthogonal", "support_null_sets")
        self.alpha = C.fz("orthogonal", "support_alpha")
        self.cache = pd.read_pickle(self.CACHE) if self.CACHE.exists() else {}
        log(f"support sources loaded in {time.perf_counter() - t:.0f} s: {[s.name for s in self.sources]}; "
            f"contradiction: {[s.name for s in self.contra]}")

    def run(self, g: str, term: str, members) -> dict:
        from src import support as sp
        key = (g, term)
        if key in self.cache:
            return self.cache[key]
        r = sp.support_test(g, members, self.sources, B=self.B, alpha=self.alpha, seed=0,
                            contradiction_sources=self.contra)
        hpa_only = sp.contradiction(g, members, [self.hpa])
        out = dict(class_state=dict(r.class_state), class_p=dict(r.class_p),
                   supporting_classes="".join(r.supporting_classes), contradiction_detail=r.contradiction,
                   contradiction_hpa_only=bool(hpa_only["contradicts"]), sources=r.table(),
                   homology=sp.homology_descriptive(self.homology, g, term), n_members=len(members))
        self.cache[key] = out
        return out

    def save(self):
        pd.to_pickle(self.cache, self.CACHE)


def term_members(v2, col: int) -> np.ndarray:
    """Positions of scorable genes annotated (base current V2 membership) to column col."""
    return np.flatnonzero(v2.A[:, col].toarray().ravel() > 0)


def decoy_candidates(P: pd.DataFrame, v2) -> pd.DataFrame:
    """Unique top terms of U predictions with family, log base size and member sets (decoy pool, §6.4 rules)."""
    t = P[P.has_prediction.astype(bool)].drop_duplicates("top_term")[["top_term", "family"]].copy()
    t.columns = ["term", "family"]
    t["col"] = t.term.map(v2.col)
    t["log_size"] = np.log(v2.size[t.col.values].astype(float))
    t["members"] = [frozenset(term_members(v2, int(c)).tolist()) for c in t.col.values]
    return t.reset_index(drop=True)


def support_for(anchor: dict, runner: SupportRunner, v2, base, cands: pd.DataFrame, onto) -> list[dict]:
    """Real, matched-gene and decoy support rows for one anchor prediction (DEVIATIONS 2026-10-29 M6 row).
    anchor: hgnc_id, symbol, pos, term, family."""
    from src import ledger as LG
    gt = base.gt
    g, term, fam = int(anchor["pos"]), anchor["term"], anchor["family"]
    col = v2.col[term]
    mem = term_members(v2, col)
    out = []

    def one(kind, tested_pos, tm, tm_col, tm_fam, mem_pos):
        h = gt.hgnc_id.values[tested_pos]
        members = [gt.hgnc_id.values[j] for j in mem_pos if j != tested_pos]
        r = runner.run(h, tm, members)
        cond = LG.support_condition(r["class_state"], tm_fam)
        row = dict(set=kind, anchor_hgnc_id=anchor["hgnc_id"], anchor_symbol=anchor["symbol"], tested_hgnc_id=h,
                   tested_symbol=gt.symbol.values[tested_pos], term=tm, term_name=onto.name(tm), family=tm_fam,
                   term_size=int(v2.size[tm_col]), n_members=len(members))
        for c in ("P", "A", "L", "G", "S"):
            row[f"state_{c}"] = r["class_state"].get(c, "not measured")
            row[f"p_{c}"] = r["class_p"].get(c, np.nan)
        cd = r["contradiction_detail"] or {}
        row.update(supporting_classes=r["supporting_classes"], n_classes=len(r["supporting_classes"]),
                   contradiction=cond["contradiction"], contradiction_hpa_only=r["contradiction_hpa_only"],
                   contradiction_sources="|".join(cd.get("incompatible_sources", [])),
                   term_compartments="|".join(cd.get("term_compartments", ())),
                   multi_localised=cd.get("multi_localised", False), diag_measured=cond["diag_measured"],
                   diag_support=cond["diag_support"], diag_ok=cond["passes"], strict=cond["strict"],
                   any_support=cond["any_support"], homology_descriptive=r["homology"])
        return row, r

    row, r = one("real", g, term, col, fam, mem)
    out.append(row)
    # matched-gene prediction: first match of M(g) not annotated to the term
    m = next((int(x) for x in base.matches[g] if x != g and v2.A[int(x), col] == 0), None)
    if m is not None:
        out.append(one("matched", m, term, col, fam, mem)[0])
    # decoy prediction: other U genes' top term, same family, size-matched, unrelated, Jaccard < 0.1
    rng = np.random.default_rng([C.fz("seeds", "decoys"), g])
    dc = LG.choose_decoy(term, fam, float(np.log(v2.size[col])), frozenset(mem.tolist()), cands, onto.ancestors, rng,
                         max_jaccard=C.fz("judging", "decoy_max_jaccard"))
    if dc is not None:
        out.append(one("decoy", g, dc.term, int(dc.col), dc.family, np.asarray(sorted(dc.members)))[0])
    return out


def source_rows(runner: SupportRunner, rows: list[dict]) -> pd.DataFrame:
    tabs = []
    for r in rows:
        x = runner.cache[(r["tested_hgnc_id"], r["term"])]["sources"].copy()
        x.insert(0, "set", r["set"])
        x.insert(1, "anchor_symbol", r["anchor_symbol"])
        x.insert(2, "tested_symbol", r["tested_symbol"])
        x.insert(3, "term", r["term"])
        tabs.append(x)
    return pd.concat(tabs, ignore_index=True) if tabs else pd.DataFrame()
