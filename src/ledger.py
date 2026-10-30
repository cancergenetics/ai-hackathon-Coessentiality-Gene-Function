"""ledger.py -- M6 hypothesis-generation rules for U genes (DESIGN.md v2.3 §3.7 support, §4.3, §4.4, §5.4, §6.1).

Pure functions (no file I/O, no DepMap reads); the numbered scripts 40-45 pass DataFrames / arrays.
Operational details not fixed by DESIGN are logged in DEVIATIONS.md (rows dated 2026-10-29, "M6").

* ``pcal_from_model`` / ``support_category`` -- p_cal from the frozen all-H fit (results/calibration/model_H.json) and the
  §3.7 support rule (in support / boundary upper bound / no p_cal).
* ``locus_flags``, ``in_degree``, ``hub_genes``, ``hub_share``, ``pearson_pairwise`` -- §4.3 artefact flags.
* ``bh``, ``fisher_enrichment`` -- multiplicity and TF enrichment.
* ``DIAGNOSTIC``, ``support_condition`` -- §5.4 diagnostic class by family and the Tier-A support condition.
* ``tier_of`` / ``fill_top`` -- §6.1 tiers, the fill rule and the mitochondrial cap.
* ``relationship_type`` -- §4.4 script precedence e -> a -> c -> b -> d (unresolved).
* ``choose_decoy`` -- §6.4-style decoy term (family + size matched, not related, Jaccard < 0.1).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import fisher_exact

CONT = ("zmean", "R", "cov_pct", "size_pct")
BOUNDARY_COVS = ("zmean", "R")          # below the 5th percentile only on these -> upper bound


# ================================================================================================ p_cal
def design_row(x: dict, model: dict) -> np.ndarray:
    """Covariate vector in model['covariates'] order: continuous covariates, then family dummies
    ('fam_<family>' = 1 if the top-term family is that family; 'fam_rare' = 1 if the family is not kept)."""
    fam = x["family"]
    kept = set(model["families_kept"])
    out = []
    for c in model["covariates"]:
        if c.startswith("fam_"):
            f = c[4:]
            out.append(1.0 if (f == "rare" and fam not in kept) or (f != "rare" and fam == f) else 0.0)
        else:
            out.append(float(x[c]))
    return np.asarray(out, float)


def pcal_from_model(df: pd.DataFrame, model: dict) -> np.ndarray:
    """p = expit(w0 + sum_j w_j (x_j - mu_j) / sd_j) with the standardised all-H fit; NaN when a covariate is NaN."""
    st = model["standardised"]
    w, mu, sd = np.asarray(st["w"], float), np.asarray(st["mu"], float), np.asarray(st["sd"], float)
    out = np.full(len(df), np.nan)
    for i, (_, r) in enumerate(df.iterrows()):
        if not isinstance(r.get("family"), str) or not r["family"]:
            continue
        x = design_row(r, model)
        if np.isfinite(x).all():
            out[i] = float(expit(w[0] + np.sum(w[1:] * (x - mu) / sd)))
    return out


def support_category(x: dict, bounds: dict, families_kept) -> str:
    """'in_support' | 'upper_bound' | 'no_pcal' (§3.7; model_H.json support.rule)."""
    if not isinstance(x.get("family"), str) or x["family"] not in set(families_kept):
        return "no_pcal"
    vals = {c: float(x[c]) for c in CONT}
    if not all(np.isfinite(v) for v in vals.values()):
        return "no_pcal"
    inside = {c: bounds[c][0] <= vals[c] <= bounds[c][1] for c in CONT}
    if all(inside.values()):
        return "in_support"
    below = {c: vals[c] < bounds[c][0] for c in CONT}
    if all(inside[c] for c in CONT if c not in BOUNDARY_COVS) and \
            all(inside[c] or below[c] for c in BOUNDARY_COVS) and any(below[c] for c in BOUNDARY_COVS):
        return "upper_bound"
    return "no_pcal"


# ================================================================================================ §4.3 flags
def interval_gap(a, b) -> float:
    """Gap in bp between two (chrom, start, end) intervals (0 if overlapping); inf on different chromosomes or
    missing coordinates."""
    if a is None or b is None or a[0] != b[0] or any(pd.isna(v) for v in (*a[1:], *b[1:])):
        return math.inf
    return float(max(0.0, max(a[1], b[1]) - min(a[2], b[2])))


def locus_flags(g_coord, partner_coords: dict, window: float = 1000.0, readthrough=()) -> dict:
    """{partner: flagged}: partner gene body overlapping or within ``window`` bp (gap < window) of g's or another
    partner's gene body (strand-agnostic; DEVIATIONS 2026-10-29), or partner in ``readthrough``."""
    out = {}
    keys = list(partner_coords)
    for j in keys:
        c = partner_coords[j]
        f = j in set(readthrough) or interval_gap(g_coord, c) < window
        if not f:
            f = any(interval_gap(c, partner_coords[k]) < window for k in keys if k != j)
        out[j] = bool(f)
    return out


def in_degree(ids: np.ndarray, rows_mask: np.ndarray, G: int) -> np.ndarray:
    """Number of query rows (rows_mask True) whose neighbour list contains each gene."""
    I = np.asarray(ids)[np.asarray(rows_mask, bool)]
    I = I[I >= 0]
    return np.bincount(I.ravel(), minlength=G)


def hub_genes(indeg: np.ndarray, eligible: np.ndarray, top_fraction: float = 0.01) -> np.ndarray:
    """Boolean G mask: eligible genes whose in-degree is >= that of the ceil(top_fraction x n_eligible)-th largest
    (ties at the threshold included)."""
    e = np.asarray(eligible, bool)
    k = max(1, int(math.ceil(top_fraction * e.sum())))
    thr = np.sort(indeg[e])[::-1][k - 1]
    return e & (indeg >= thr) & (indeg > 0)


def hub_share(weights, is_hub) -> float:
    """Fraction of S (sum of positive weights of supporting partners) from hub partners."""
    w = np.clip(np.asarray(weights, float), 0, None)
    h = np.asarray(is_hub, bool)
    return float(w[h].sum() / w.sum()) if w.sum() > 0 else np.nan


def pearson_pairwise(x, Y, min_n: int = 20) -> np.ndarray:
    """Pearson r of vector x (n) with each column of Y (n x m) over pairwise-complete entries; NaN if < min_n."""
    x = np.asarray(x, float)
    Y = np.asarray(Y, float)
    if Y.ndim == 1:
        Y = Y[:, None]
    out = np.full(Y.shape[1], np.nan)
    for k in range(Y.shape[1]):
        ok = np.isfinite(x) & np.isfinite(Y[:, k])
        if ok.sum() < min_n:
            continue
        a, b = x[ok] - x[ok].mean(), Y[ok, k] - Y[ok, k].mean()
        d = np.sqrt((a * a).sum() * (b * b).sum())
        out[k] = float((a * b).sum() / d) if d > 0 else np.nan
    return out


def exclusion_43(flag_matrix: pd.DataFrame, hub_driven: bool, frac: float = 0.5) -> tuple[bool, float]:
    """Not-Tier-A exclusion: fraction of supporting partners carrying any flag (columns of ``flag_matrix``,
    rows = supporting partners) >= frac, or hub-driven. Returns (excluded, flagged fraction)."""
    if len(flag_matrix) == 0:
        return bool(hub_driven), np.nan
    f = float(flag_matrix.any(axis=1).mean())
    return bool(f >= frac or hub_driven), f


# ================================================================================================ statistics
def bh(p) -> np.ndarray:
    """Benjamini-Hochberg q-values (NaN kept as NaN)."""
    p = np.asarray(p, float)
    q = np.full(len(p), np.nan)
    ok = np.isfinite(p)
    if not ok.any():
        return q
    pv = p[ok]
    o = np.argsort(pv)
    n = len(pv)
    r = pv[o] * n / np.arange(1, n + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    qq = np.empty(n)
    qq[o] = np.minimum(r, 1.0)
    q[ok] = qq
    return q


def fisher_enrichment(partners, hits: set, background) -> dict:
    """One-sided (greater) Fisher test of hits among partners vs the rest of background. Returns a, b, c, d, OR
    (Haldane-corrected when a cell is 0), p."""
    P = set(partners)
    Bg = set(background) - P
    a = len(P & hits)
    b = len(P) - a
    c = len(Bg & hits)
    d = len(Bg) - c
    p = fisher_exact([[a, b], [c, d]], alternative="greater")[1]
    orr = (a * d) / (b * c) if min(a, b, c, d) > 0 else ((a + .5) * (d + .5)) / ((b + .5) * (c + .5))
    return dict(a=a, b=b, c=c, d=d, OR=float(orr), p=float(p))


# ================================================================================================ §5.4 / §6.1
DIAGNOSTIC = {
    "mitochondrial": ("L", "A"),
    "nuclear_RNA_machinery": ("G", "L"),
    "ribosome_biogenesis_translation": ("G", "L"),
    "DNA_replication_repair": ("G", "L"),
    "ER_Golgi_secretory_lipid": ("L",),
    "centrosome_cilia_mitosis": ("L", "P"),
    "signalling_lineage": ("P",),
    "other": ("P", "A", "L", "G", "S"),
}


def support_condition(class_state: dict, family: str) -> dict:
    """Tier-A orthogonal condition (§5.3-§5.4): diagnostic-class support when a diagnostic class is measured, and no
    contradiction. ``class_state``: {class: 'not measured'|'no support'|'supports'|'contradicts'}."""
    diag = DIAGNOSTIC.get(family, DIAGNOSTIC["other"])
    measured = [c for c in diag if class_state.get(c, "not measured") != "not measured"]
    diag_support = any(class_state.get(c) == "supports" for c in diag)
    contra = class_state.get("L") == "contradicts"
    any_support = any(v == "supports" for v in class_state.values())
    return dict(diag_measured=bool(measured), diag_support=diag_support, contradiction=contra,
                any_support=any_support,
                passes=bool((diag_support or not measured) and not contra),
                strict=bool(diag_support and not contra))


def tier_of(r: dict, pa: float = 0.5, pb: float = 0.3) -> str:
    """'A' | 'B' | '' from the §6.1 conditions in ``r``: scorable, expressed, assessable, in_support (p_cal in
    support), p_cal, excl43 (§4.3 exclusion incl. top-40 demotions), diag_ok (diagnostic support or none measured),
    diag_support (strict), contradiction, low_coverage_excluded."""
    base = (r["scorable"] and r["expressed"] and r["assessable"] and r["in_support"] and not r["excl43"]
            and not r["contradiction"] and not r.get("low_coverage_excluded", False))
    if not base or not np.isfinite(r["p_cal"]):
        return ""
    if r["p_cal"] >= pa and r["diag_ok"] and not r.get("demote_A", False):
        return "A"
    if r["p_cal"] >= pb:
        return "B"
    return ""


def fill_top(df: pd.DataFrame, n: int = 40, cap_top: int = 20, cap_max: int = 6,
             mito: str = "mitochondrial") -> pd.DataFrame:
    """Order: tier A, tier B, clean fill, other fill (column ``group`` 0-3), each by p_cal desc, n_classes desc,
    symbol; mitochondrial-family genes beyond ``cap_max`` within the first ``cap_top`` positions are deferred (next
    eligible substitutes). Returns the first n rows with ``rank`` and ``mito_deferred``."""
    d = df.sort_values(["group", "p_cal", "n_classes", "symbol"], ascending=[True, False, False, True],
                       kind="mergesort").reset_index(drop=True)
    chosen, deferred = [], []
    n_m = 0
    for i, r in d.iterrows():
        if len(chosen) < cap_top:
            if r["family"] == mito and n_m >= cap_max:
                deferred.append(i)
                continue
            n_m += r["family"] == mito
            chosen.append(i)
        else:
            break
    rest = [i for i in d.index if i not in set(chosen)]          # includes deferred, in order
    order = chosen + rest
    out = d.loc[order[:n]].copy()
    out["mito_deferred"] = [i in set(deferred) for i in order[:n]]
    out["rank"] = np.arange(1, len(out) + 1)
    return out.reset_index(drop=True)


# ================================================================================================ §4.4 type
def relationship_type(coupling: bool, tf_flag: bool, class_state: dict, enzyme_or_transporter: bool,
                      multipass: bool, complex_like_partners: bool, assembly_label: bool) -> tuple[str, str]:
    """Script precedence e -> a -> c -> b -> d (§4.4); returns (type letter, reason)."""
    if coupling or tf_flag:
        return "e", "coupling" if coupling else "TF enrichment"
    if any(class_state.get(c) == "supports" for c in ("P", "A", "S")):
        return "a", "P/A/S support"
    if enzyme_or_transporter or (multipass and not complex_like_partners):
        return "c", "enzyme/transporter" if enzyme_or_transporter else "multi-pass membrane, no complex-like partners"
    if assembly_label:
        return "b", "assembly term"
    return "d", "type unresolved"


# ================================================================================================ decoys
def choose_decoy(term: str, family: str, log_size: float, members: set, cands: pd.DataFrame, ancestors,
                 rng: np.random.Generator, n_near: int = 10, max_jaccard: float = 0.1):
    """Decoy term for a prediction: candidates (columns term, family, log_size, members) of the same family, not the
    term, an ancestor or a descendant, member Jaccard < max_jaccard; random pick among the n_near closest in
    |log size|. Returns the row (Series) or None."""
    anc = ancestors(term)
    c = cands[(cands.family == family) & (cands.term != term)]
    ok = []
    for r in c.itertuples():
        if r.term in anc or term in ancestors(r.term):
            continue
        u = len(members | r.members)
        if u and len(members & r.members) / u >= max_jaccard:
            continue
        ok.append(r.Index)
    if not ok:
        return None
    c = c.loc[ok].copy()
    c["d"] = (c.log_size - log_size).abs()
    c = c.sort_values(["d", "term"], kind="mergesort").head(n_near)
    return c.iloc[int(rng.integers(0, len(c)))]
