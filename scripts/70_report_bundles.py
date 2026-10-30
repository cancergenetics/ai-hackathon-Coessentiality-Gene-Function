#!/usr/bin/env python
"""70_report_bundles.py -- M7 deep-dive evidence bundles (DESIGN.md v2.3 §4.1, §4.3-§4.4, §5, §6.5; Templates A/B).

For each gene of results/m7/report_selection.md writes reports/data/<SYMBOL>/:
  bundle.md        machine-generated facts only (no interpretation): identifiers, D1-D3, strata, p_cal (+ cluster-
                   bootstrap 95% interval from data/derived/ledger/pcal_boot.npz), calibration family and support
                   category, V2 term, top-5 terms, V1' label, dependency profile, expression, split-half
                   assessability, top-10 partner table, robustness table, orthogonal evidence matrix with pair-level
                   detail, localisation calls per source, protein features, LLM-recall-probe answer, and the
                   Template-B DepMap cell-line selection.
  fig_profile.png  (a) g's Chronos effect vs its rank-1 partner across lines, (b) g's effect vs own expression.
  fig_network.png  g, its top-10 partners and zavg_BEF >= 3 edges among them; node colour = annotated to the
                   predicted V2 term; edge style = orthogonal physical support (admitted P sources).
plus reports/data/TM2D_module/ (TM2D1, TM2D2, CHIC2 joint module figure + module.md + CHIC2 bundle).

Every number is read from results/ledger/*, results/assessability/*, results/m7/recall_probe_90.tsv or recomputed
from the raw DepMap / orthogonal files with the project's loaders. Values recomputed here (and not in the ledger) are
marked "(recomputed here)": K = 10/50 top terms, leave-one-partner-out stability, p_emp of the top terms, GLS ranks for
genes outside top40.tsv, pair-level orthogonal scores, cell-line selection. Sanity checks assert that the re-scored
K = 25 top term equals u_predictions.tsv and that recomputed GLS ranks equal top40_partners_gls.tsv where present.

Rules fixed here (descriptive; not in DESIGN):
  * common-essential = Chronos < -0.5 in >= 90% of lines (data-defined, as scripts/12 A1).
  * lineage enrichment = lineages (Model.csv OncotreeLineage) with >= 10 lines, ranked by mean effect of g;
    two-sided Mann-Whitney vs all other lines (descriptive).
  * cell-line rule (Template B §2): dependent = g <= -0.5, rank-1 partner <= -0.3, g log2(TPM+1) >= 2, g not
    amplified (OmicsCNGeneWGS relative CN < 1.5; NaN CN allowed, listed); ranked TP53-mutant first (proxy for
    TP53-null: damaging or hotspot mutation), then ScreenNNMD ascending (CRISPRConfounders), then g effect; the second
    chosen line is the best-ranked line of a different lineage when one qualifies. If < 2 lines qualify the partner
    criterion is relaxed, then g <= -0.3 (labelled). Control = g >= -0.2, log2(TPM+1) >= 2, not amplified, same lineage
    as chosen line 1 (else line 2, else any), ranked by expression descending. Baseline medium = Model.csv OnboardedMedia.
Run: .env/bin/python -I scripts/70_report_bundles.py
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()
DEP = "data/raw/depmap/"
DATA = (C.EFFECT_CSV, DEP + "Model.csv", DEP + "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
        DEP + "OmicsCNGeneWGS.csv", DEP + "OmicsSomaticMutationsMatrixDamaging.csv",
        DEP + "OmicsSomaticMutationsMatrixHotspot.csv", DEP + "CRISPRConfounders.csv")
gate = C.gate_check(data_files=DATA)
C.log("gate OK")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.stats import mannwhitneyu, pearsonr, rankdata, spearmanr  # noqa: E402

import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import coess_matrix as cm  # noqa: E402
from src import ledger as LG  # noqa: E402
from src import neighbours as nbm  # noqa: E402
from src import orthogonal as og  # noqa: E402
from src import vocab  # noqa: E402
from src.neighbours import Neighbours  # noqa: E402

log = C.log
ROOT = C.ROOT
OUTD = ROOT / "reports" / "data"
CACHE = C.DERIVED / "reports"
CACHE.mkdir(parents=True, exist_ok=True)
K = B.K
fmt = M6.fmt
MODULE = ("TM2D1", "TM2D2", "CHIC2")
OKABE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
GREY = "#BDBDBD"
C_G, C_IN, C_OUT = "#E69F00", "#0072B2", "#D9D9D9"

# ============================================================================================ selection
sel_txt = (ROOT / "results/m7/report_selection.md").read_text()
SEL = []
for line in sel_txt.splitlines():
    m = re.match(r"^\|\s*(\d+)\s*\|\s*([A-Za-z0-9\-]+)\s*\|\s*(N\d)\s*\|", line)
    if m:
        SEL.append(dict(rank=int(m.group(1)), symbol=m.group(2), L=m.group(3)))
GENES = [s["symbol"] for s in SEL]
LCLASS = {s["symbol"]: s["L"] for s in SEL}
assert len(GENES) == 10, GENES
log(f"genes: {GENES}")

# ============================================================================================ ledger tables
rd = M6.read_tsv
P = rd("u_predictions.tsv")
PC = rd("u_pcal.tsv")
T40 = rd("top40_primary.tsv")
T40C = rd("top40.tsv")
PART = rd("u_partners.tsv")
TOP5 = rd("u_top5.tsv")
FL = rd("u_flags.tsv")
FLP = rd("u_flag_partners.tsv")
ST = rd("support.tsv")
SS = rd("support_sources.tsv")
CHK = rd("checks_all_evaluated.tsv")
GLSL = rd("top40_partners_gls.tsv")
ASS = pd.read_csv(ROOT / M6.ASSESS, sep="\t", dtype={"hgnc_id": str})
U = pd.read_csv(ROOT / M6.U_TSV, sep="\t", dtype=str, keep_default_na=False)
HUB = pd.read_csv(ROOT / C.HUB_TSV, sep="\t", dtype=str, keep_default_na=False)
PROBE = pd.read_csv(ROOT / "results/m7/recall_probe_90.tsv", sep="\t", dtype=str, keep_default_na=False)
AUDIT = pd.read_csv(ROOT / "results/audit/curation_lag_audit.tsv", sep="\t", dtype=str, keep_default_na=False)
UP = pd.read_csv(ROOT / M5.UNIPROT, sep="\t", dtype=str, keep_default_na=False)
UP["hgnc"] = UP.HGNC.str.split(";").map(lambda x: [y for y in x if y])
UPX = UP.explode("hgnc")
PB = np.load(C.DERIVED / "ledger/pcal_boot.npz", allow_pickle=True)
PB_IDX = {h: i for i, h in enumerate(PB["hgnc_id"])}
PB_BOOT = PB["boot"][PB["ok"].astype(bool)]

sym2h = dict(zip(P.symbol, P.hgnc_id))
ALL = list(GENES) + [g for g in MODULE if g not in GENES]
HIDS = [sym2h[s] for s in ALL]

# ============================================================================================ base, V2, effect
base = B.Base()
gt, G = base.gt, base.G
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
effect = C.load_effect()
E = effect.values
lines = np.asarray(effect.index)
assert list(effect.columns) == list(gt.gene.values)
MODEL = pd.read_csv(ROOT / DEP / "Model.csv", dtype=str, keep_default_na=False).set_index("ModelID")
lin_of = MODEL.OncotreeLineage.reindex(lines).replace("", np.nan).fillna("unknown").values
CONF = pd.read_csv(ROOT / DEP / "CRISPRConfounders.csv", index_col=0)
ZM = np.load(ROOT / "data/derived/matrices/zavg_full/zavg_BEF.npy", mmap_mode="r")
assert ZM.shape == (G, G)
pos = {s: base.pos[sym2h[s]] for s in ALL}


def pos_of_h(h):
    return base.pos.get(h)


def ce_flag(j):
    e = E[:, j]
    e = e[np.isfinite(e)]
    return bool(len(e) and (e < -0.5).mean() >= 0.9)


# ------------------------------------------------------------------------------------------ omics columns
def header(path):
    return pd.read_csv(ROOT / path, nrows=0).columns


def gene_cols(path, positions):
    """Default-entry omics values (ModelID x matrix positions; Entrez match) -- as scripts/44."""
    h = header(path)
    ent = M6.entrez_of_col(h)
    col_of = {}
    for c, x in zip(h, ent):
        if isinstance(x, str) and x not in col_of:
            col_of[x] = c
    want = {}
    for p_, e in zip(positions, M6.entrez_of_col(gt.gene.values[list(positions)])):
        if e in col_of:
            want[p_] = col_of[e]
    meta = [c for c in ("ModelID", "IsDefaultEntryForModel") if c in h]
    df = pd.read_csv(ROOT / path, usecols=meta + sorted(set(want.values())))
    if "IsDefaultEntryForModel" in df.columns:
        df = df[df.IsDefaultEntryForModel.astype(str).isin(["Yes", "True", "true", "1"])]
    df = df.drop_duplicates("ModelID").set_index("ModelID")
    return pd.DataFrame({p_: df[c] for p_, c in want.items()}, index=df.index)


part_by = {h: PART[PART.hgnc_id == h].sort_values("rank") for h in HIDS}
top1 = {h: base.pos[part_by[h].iloc[0].partner_hgnc_id] for h in HIDS}
EXPR = gene_cols(DEP + "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv",
                 sorted({pos[s] for s in ALL} | set(top1.values())))
CN, cn_rows = M6.omics_by_position(pd.DataFrame(), gt, cache="cn_wgs")
CNdf = pd.DataFrame(CN[:, sorted({pos[s] for s in ALL})], index=cn_rows, columns=sorted({pos[s] for s in ALL}))
tp53_pos = int(np.flatnonzero(gt.symbol.values == "TP53")[0])
mm = pd.concat([gene_cols(f, [tp53_pos])[tp53_pos] for f in (DEP + "OmicsSomaticMutationsMatrixDamaging.csv",
                                                              DEP + "OmicsSomaticMutationsMatrixHotspot.csv")], axis=1)
TP53_MUT = (mm.fillna(0) > 0).any(axis=1)
log(f"omics loaded: expression {EXPR.shape}, CN {CNdf.shape}, TP53 {int(TP53_MUT.sum())}/{len(TP53_MUT)} mutant")

# ============================================================================================ rescoring (K, LOPO)
def score(nb, queries):
    sc = vocab.score_queries(v2, nb, base.matches, np.asarray(sorted(queries)), loo=False)
    return sc


qpos = [pos[s] for s in ALL]
sc25 = score(base.nb, qpos)
r25 = sc25.ranked("R1")
for s in ALL:
    h = sym2h[s]
    assert v2.terms[r25[pos[s]][0]] == P.set_index("hgnc_id").loc[h].top_term, s
log("K = 25 rescoring reproduces u_predictions top terms")
tab25 = sc25.table
topK = {}
for k in (10, 50):
    rk = score(base.nb_k(k), qpos).ranked("R1")
    topK[k] = {g: (v2.terms[rk[g][0]] if rk.get(g) else "") for g in qpos}


def p_emp_of(g, term):
    t = tab25[(tab25["query"] == g) & (tab25.term == v2.col[term])]
    return float(t.p_emp.iloc[0]) if len(t) else np.nan


def lopo(g, terms):
    """Leave-one-partner-out (recomputed here): for each of the top-3 terms, drop each of its supporting partners
    from N(g) (K = 25, no refill), re-score g; count drops after which the term keeps its R1 rank."""
    r0 = r25[g]
    out = {}
    cache = {}
    for t in terms:
        col = v2.col[t]
        sup = [j for j, _ in M6.supporting(v2, g, col, base.ids100[g, :K], base.z100[g, :K])]
        kept = 0
        for j in sup:
            if j not in cache:
                I, Z = base.nb.ids.copy(), base.nb.z.copy()
                k_ = np.flatnonzero(I[g] == j)
                I[g, k_], Z[g, k_] = -1, np.nan
                rr = score(Neighbours(rows=np.arange(G), ids=I, z=Z, K=K), [g]).ranked("R1").get(g, [])
                cache[j] = rr
            rr = cache[j]
            kept += int(col in rr and rr.index(col) == r0.index(col))
        out[t] = (kept, len(sup))
    return out


# ============================================================================================ GLS ranks
gls_file = CACHE / "gls_report_rows.npz"
cols_bg = np.flatnonzero(base.bg)
if gls_file.exists() and list(np.load(gls_file)["rows"]) == qpos:
    GL = np.load(gls_file)["gls"]
else:
    GL, _ = cm.gls_rows(effect.to_numpy(), np.asarray(qpos), cols_bg, out_path=None, log=log)
    GL = np.asarray(GL)
    np.savez_compressed(gls_file, rows=np.asarray(qpos), gls=GL)
src_rows = B.RowSource(GL, {g: i for i, g in enumerate(qpos)}, cols_bg, G)
nbg = nbm.top_k(src_rows, K, rows=np.asarray(qpos), bg=base.bg, arm=base.arm, paralogues=base.par)
scg = score(B.padded(G, np.asarray(qpos), nbg.ids, nbg.z, K), qpos).ranked("R1")
GLS_RANK, GLS_TOP = {}, {}
for i, g in enumerate(qpos):
    full = np.full(G, -np.inf)
    full[cols_bg] = np.asarray(GL[i], float)
    ex = nbm.exclusion_mask(np.array([g]), G, base.bg, base.arm, base.par)[0]
    full[ex | ~np.isfinite(full)] = -np.inf
    lst = scg.get(g, [])
    GLS_TOP[g] = v2.terms[lst[0]] if lst else ""
    h = gt.hgnc_id.values[g]
    for x in part_by[h].itertuples():
        v = full[base.pos[x.partner_hgnc_id]]
        GLS_RANK[(h, x.partner_symbol)] = int((full > v).sum() + 1) if np.isfinite(v) else np.nan
    led = GLSL[GLSL.hgnc_id == h]
    for x in led.itertuples():
        assert GLS_RANK[(h, x.partner_symbol)] == int(x.gls_rank), (h, x.partner_symbol)
log("GLS ranks computed (match top40_partners_gls.tsv where present)")

# ============================================================================================ orthogonal sources
t0 = time.perf_counter()
MAP = og.mapper()
SRC = {}
for n in ("BioPlex3", "OpenCell_PPI", "BioGRID_LTP", "STRING_exp", "HCM_SAINT", "ProteomeHD", "CCLE_proteomics",
          "PerturbSeq_K562_GW", "PerturbSeq_K562_essential", "PerturbSeq_RPE1_essential", "Burke2023_AF2", "HPA",
          "OpenCell_loc", "HCM_NMF", "MitoCarta3", "huMAP3_NI"):
    SRC[n] = og.LOADERS[n](MAP)
log(f"orthogonal sources loaded in {time.perf_counter() - t0:.0f} s")
PHYS = ("BioPlex3", "OpenCell_PPI", "BioGRID_LTP", "STRING_exp", "HCM_SAINT")
CONT = ("ProteomeHD", "CCLE_proteomics", "PerturbSeq_K562_GW", "PerturbSeq_K562_essential", "PerturbSeq_RPE1_essential")
burke = pd.read_csv(ROOT / "data/raw/burke2023_af2/table_AF2_HURI_HuMap_UNIQUE.csv",
                    usecols=["id1", "id2", "pDockQ", "Dataset"], dtype={"id1": str, "id2": str})
burke["a"], burke["b"] = burke.id1.map(MAP.from_acc), burke.id2.map(MAP.from_acc)
burke["pDockQ"] = pd.to_numeric(burke.pDockQ, errors="coerce")
burke = burke.dropna(subset=["a", "b"])
PDQ = float(og.fz("orthogonal", "pdockq_min"))


def edge(src, a, b):
    s = SRC[src]
    i, j = s.index.get(a), s.index.get(b)
    if i is None or j is None:
        return None                     # not measured
    return bool(s.adj[i, j])


def phys_any(a, b):
    v = [edge(n, a, b) for n in PHYS]
    return any(x is True for x in v), all(x is None for x in v)


def cont_row(src, a):
    s = SRC[src]
    i = s.index.get(a)
    if i is None:
        return None
    row = np.asarray(s.mat[i], float).copy()
    row[i] = np.nan
    fin = np.isfinite(row)
    pct = np.full(len(row), np.nan)
    if fin.sum():
        pct[fin] = rankdata(row[fin]) / fin.sum()
    return row, pct


def pair_cont(src, a, b):
    r = cont_row(src, a)
    if r is None:
        return "n.m. (g)"
    j = SRC[src].index.get(b)
    if j is None:
        return "n.m."
    v, p_ = r[0][j], r[1][j]
    return "NaN" if not np.isfinite(v) else f"{v:.2f} ({100 * p_:.0f}%)"


def burke_pair(a, b):
    d = burke[((burke.a == a) & (burke.b == b)) | ((burke.a == b) & (burke.b == a))]
    return "n.m." if not len(d) else f"{d.pDockQ.max():.3f}"


def sym(h):
    return MAP.symbol.get(h, h)


# ============================================================================================ helpers
def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else str(v).replace("|", "/")
                                     for v in r) + " |")
    return "\n".join(out)


def yn(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n.m."
    return "yes" if bool(x) else "no"


def nz(x, empty="—"):
    """Display value: NaN / None / '' -> empty."""
    if x is None or (isinstance(x, float) and np.isnan(x)) or str(x).strip() in ("", "nan"):
        return empty
    return str(x)


def as_bool(x):
    return str(x).strip().lower() in ("true", "1", "yes")


def term_name(t):
    try:
        return base.onto.name(t)
    except Exception:  # noqa: BLE001
        return ""


def bh_over_primary(col):
    v = pd.to_numeric(T40[col], errors="coerce").values
    return dict(zip(T40.hgnc_id, LG.bh(v)))


TFQ, TP53Q = bh_over_primary("tf_p"), bh_over_primary("tp53_p")
TF_OR, TF_QMAX = C.fz("artefacts", "tf_enrichment_fisher_or_min"), C.fz("artefacts", "tf_enrichment_q_max")
TP53_QMAX = C.fz("artefacts", "tp53_mannwhitney_q")


def lineage_stats(e):
    s = pd.DataFrame(dict(lin=lin_of, e=e)).dropna()
    g = s.groupby("lin").e.agg(["mean", "size"])
    g = g[(g["size"] >= 10) & (g.index != "unknown")].sort_values("mean")
    rows = []
    for lin, r in g.head(3).iterrows():
        inn, out = s.e[s.lin == lin], s.e[s.lin != lin]
        rows.append(dict(lineage=lin, n=int(r["size"]), mean=r["mean"], median=float(inn.median()),
                         p=float(mannwhitneyu(inn, out, alternative="two-sided").pvalue)))
    return rows, g


def prot(h):
    u = UPX[UPX.hgnc == h]
    if not len(u):
        return None
    u = u.iloc[0]
    kw = [k.strip() for k in u.Keywords.split(";")]
    loc = u["Subcellular location [CC]"]
    return dict(entry=u.Entry, name=u["Protein names"], length=u.Length, pfam=u.Pfam.strip(";"),
                interpro=u.InterPro.strip(";"), domain_ft=u["Domain [FT]"], keywords=kw,
                tm="Transmembrane" in kw, signal="Signal" in kw, transit="Transit peptide" in kw,
                multipass="Multi-pass membrane protein" in loc, singlepass="Single-pass" in loc,
                loc_cc=loc, simil=u["Sequence similarities"], function=u["Function [CC]"],
                existence=u["Protein existence"], annot=u.Annotation)


# raw localisation rows
import zipfile  # noqa: E402

with zipfile.ZipFile(ROOT / "data/raw/hpa/subcellular_location.tsv.zip") as z:
    HPA_RAW = pd.read_csv(z.open("subcellular_location.tsv"), sep="\t", dtype=str, keep_default_na=False)
OC_LOC = pd.read_csv(ROOT / "data/raw/opencell/opencell-localization-annotations.csv", dtype=str, keep_default_na=False)
HCM_PREY = pd.read_csv(ROOT / "data/raw/humancellmap/preys-latest.txt", sep="\t", dtype=str, keep_default_na=False)
HCM_BAIT = pd.read_csv(ROOT / "data/raw/humancellmap/baits-latest.txt", sep="\t", dtype=str, keep_default_na=False)


def comp_str(src, h, hr=False):
    s = SRC[src]
    c = (s.comp_hr if hr else s.comp).get(h)
    return ", ".join(sorted(c)) if c else "—"


# ============================================================================================ cell lines
def choose_lines(g, j):
    eg = pd.Series(E[:, g], index=lines)
    ej = pd.Series(E[:, j], index=lines)
    ex = EXPR[g].reindex(lines) if g in EXPR.columns else pd.Series(np.nan, index=lines)
    cn = CNdf[g].reindex(lines) if g in CNdf.columns else pd.Series(np.nan, index=lines)
    df = pd.DataFrame(dict(g_effect=eg, partner_effect=ej, g_expr=ex, g_CN=cn))
    df["TP53_mut"] = pd.Series(lines, index=lines).map(TP53_MUT)
    df["NNMD"] = CONF.ScreenNNMD.reindex(lines).values
    df["ROCAUC"] = CONF.ScreenROCAUC.reindex(lines).values
    df["name"] = MODEL.CellLineName.reindex(lines).values
    df["lineage"] = MODEL.OncotreeLineage.reindex(lines).values
    df["disease"] = MODEL.OncotreePrimaryDisease.reindex(lines).values
    df["medium"] = [f"{a_} ({b_})" if a_ else b_ for a_, b_ in zip(MODEL.FormulationID.reindex(lines).fillna("").values,
                                                                   MODEL.OnboardedMedia.reindex(lines).fillna("").values)]
    notamp = ~(df.g_CN >= 1.5)
    expr_ok = df.g_expr >= 2
    counts = dict(n_lines=len(df), g_le_m0p5=int((df.g_effect <= -0.5).sum()),
                  plus_partner_le_m0p3=int(((df.g_effect <= -0.5) & (df.partner_effect <= -0.3)).sum()),
                  plus_expr_ge2=int(((df.g_effect <= -0.5) & (df.partner_effect <= -0.3) & expr_ok).sum()),
                  plus_not_amplified=int(((df.g_effect <= -0.5) & (df.partner_effect <= -0.3) & expr_ok &
                                          notamp).sum()))
    tiers = [("rule (g <= -0.5, partner <= -0.3)", (df.g_effect <= -0.5) & (df.partner_effect <= -0.3)),
             ("relaxed: partner criterion dropped (g <= -0.5)", df.g_effect <= -0.5),
             ("relaxed: g <= -0.3, partner criterion dropped", df.g_effect <= -0.3)]
    used, cand = None, None
    for lab, m in tiers:
        c = df[m & expr_ok & notamp].copy()
        if len(c) >= 2:
            used, cand = lab, c
            break
    if cand is None:
        used, cand = tiers[-1][0] + " (fewer than 2 lines)", df[tiers[-1][1] & expr_ok & notamp].copy()
    cand["tp53_key"] = np.where(cand.TP53_mut == True, 0, np.where(cand.TP53_mut == False, 1, 2))  # noqa: E712
    cand = cand.sort_values(["tp53_key", "NNMD", "g_effect"], na_position="last")
    chosen = []
    if len(cand):
        chosen.append(cand.index[0])
        other = cand[cand.lineage != cand.lineage.iloc[0]]
        if len(other):
            chosen.append(other.index[0])
        elif len(cand) > 1:
            chosen.append(cand.index[1])
    ctrl_pool = df[(df.g_effect >= -0.2) & expr_ok & notamp].copy()
    ctrl, ctrl_rule = None, ""
    for k, cid in enumerate(chosen):
        c = ctrl_pool[ctrl_pool.lineage == df.loc[cid, "lineage"]].sort_values("g_expr", ascending=False)
        if len(c):
            ctrl, ctrl_rule = c.index[0], f"same lineage as chosen line {k + 1}"
            break
    if ctrl is None and len(ctrl_pool):
        ctrl, ctrl_rule = ctrl_pool.sort_values("g_expr", ascending=False).index[0], "any lineage (none in chosen lineages)"
    return df, cand, chosen, ctrl, ctrl_rule, used, counts


def line_table(df, ids):
    t = df.loc[list(ids)].copy()
    t.insert(0, "ModelID", t.index)
    t["TP53"] = t.TP53_mut.map({True: "mut", False: "WT"}).fillna("n.a.")
    out = t[["ModelID", "name", "lineage", "disease", "g_effect", "partner_effect", "g_expr", "g_CN", "TP53", "NNMD",
             "ROCAUC", "medium"]].copy()
    for c in ("g_effect", "partner_effect", "g_expr", "g_CN", "NNMD", "ROCAUC"):
        out[c] = out[c].map(lambda v: fmt(v, 2))
    return out


# ============================================================================================ figures
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "font.family": "sans-serif"})


def lineage_colours(g):
    _, lg = lineage_stats(E[:, g])
    top = list(lg.index[:5])
    return {l: OKABE[i] for i, l in enumerate(top)}


def fig_profile(s, g, j, jsym, sel, path):
    cmap = lineage_colours(g)
    eg, ej = E[:, g], E[:, j]
    ex = EXPR[g].reindex(lines).values if g in EXPR.columns else np.full(len(lines), np.nan)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.4))
    for k, (x, y, xl) in enumerate(((ej, eg, f"{jsym} Chronos effect (rank-1 partner)"),
                                    (ex, eg, f"{s} expression, log2(TPM+1)"))):
        a = ax[k]
        ok = np.isfinite(x) & np.isfinite(y)
        rest = ok & ~np.isin(lin_of, list(cmap))
        a.scatter(x[rest], y[rest], s=7, c=GREY, alpha=0.6, lw=0, label="other lineages", rasterized=True)
        for lin, c in cmap.items():
            m = ok & (lin_of == lin)
            a.scatter(x[m], y[m], s=14, c=c, alpha=0.9, lw=0.3, edgecolors="white",
                      label=f"{lin} (n={int(m.sum())})")
        a.axhline(-0.5, ls="--", lw=0.8, c="#555555")
        if k == 0:
            a.axvline(-0.3, ls=":", lw=0.8, c="#555555")
            r, _ = pearsonr(x[ok], y[ok])
            rho = spearmanr(x[ok], y[ok]).correlation
            a.set_title(f"(a) {s} vs {jsym}: Pearson r = {r:.2f}, Spearman ρ = {rho:.2f}, n = {ok.sum()}", fontsize=9,
                        loc="left")
        else:
            a.axvline(2, ls=":", lw=0.8, c="#555555")
            rho = spearmanr(x[ok], y[ok]).correlation if ok.sum() > 2 else np.nan
            a.set_title(f"(b) {s} effect vs own expression: Spearman ρ = {rho:.2f}, n = {ok.sum()}", fontsize=9,
                        loc="left")
        for tag, mid, mk in sel:
            i = np.flatnonzero(lines == mid)
            if len(i) and ok[i[0]]:
                a.scatter(x[i], y[i], s=70, facecolors="none", edgecolors="black", lw=1.1, marker=mk)
                a.annotate(tag, (x[i[0]], y[i[0]]), xytext=(4, 4), textcoords="offset points", fontsize=7)
        a.set_xlabel(xl)
        a.set_ylabel(f"{s} Chronos effect")
    h, l_ = ax[0].get_legend_handles_labels()
    h += [Line2D([], [], ls="none", marker="o", mfc="none", mec="black", label="chosen dependent line (D1, D2)"),
          Line2D([], [], ls="none", marker="s", mfc="none", mec="black", label="control line (C)")]
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, -0.02))
    fig.text(0.5, 0.955, "coloured: the 5 lineages with the lowest mean effect of " + s +
             " (>= 10 lines); dashed: effect -0.5; dotted: partner -0.3 / expression 2", ha="center", fontsize=7.5,
             color="#444444")
    fig.tight_layout(rect=(0, 0.1, 1, 0.94))
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def zpair(a, b):
    return float(np.nanmean([ZM[a, b], ZM[b, a]]))


def network_graph(nodes, centre_set, in_term):
    Gx = nx.Graph()
    for n in nodes:
        Gx.add_node(n)
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            z = zpair(a, b)
            if np.isfinite(z) and z >= 3:
                pa, _ = phys_any(gt.hgnc_id.values[a], gt.hgnc_id.values[b])
                Gx.add_edge(a, b, z=z, phys=pa)
    return Gx


def draw_net(ax, Gx, layout, centres, in_term, zmax):
    for a, b, d in Gx.edges(data=True):
        (x1, y1), (x2, y2) = layout[a], layout[b]
        f = min(1.0, (d["z"] - 3) / max(zmax - 3, 1e-6))
        w = 0.5 + 3.5 * f
        if d["phys"]:
            ax.plot([x1, x2], [y1, y2], c="#000000", lw=max(w, 1.6), ls="-", zorder=2, solid_capstyle="round")
        else:
            ax.plot([x1, x2], [y1, y2], c="#7F7F7F", lw=w, ls=(0, (3, 2)), zorder=1, alpha=0.35 + 0.5 * f)
    for n in Gx.nodes:
        x, y = layout[n]
        is_c = n in centres
        col = C_G if is_c else (C_IN if n in in_term else C_OUT)
        ax.scatter([x], [y], s=900 if is_c else 520, c=col, edgecolors="black", linewidths=1.2 if is_c else 0.6,
                   marker="D" if is_c else "o", zorder=3)
        ax.text(x, y - (0.17 if is_c else 0.12), gt.symbol.values[n], ha="center", va="top", fontsize=8.5,
                fontweight="bold" if is_c else "normal", zorder=4,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
    ax.set_axis_off()


def legend_net(ax, term_lbl, zmax):
    h = [Line2D([], [], ls="none", marker="D", mfc=C_G, mec="black", ms=10, label="query gene"),
         Line2D([], [], ls="none", marker="o", mfc=C_IN, mec="black", ms=9, label=f"annotated to {term_lbl}"),
         Line2D([], [], ls="none", marker="o", mfc=C_OUT, mec="black", ms=9, label="not annotated to the term"),
         Line2D([], [], c="black", lw=2, label="edge with physical support (BioPlex/OpenCell/BioGRID-LTP/STRING-exp/HCM)"),
         Line2D([], [], c="#7F7F7F", lw=2, ls=(0, (3, 2)), label="no physical support (or pair not measured)"),
         Line2D([], [], c="#7F7F7F", lw=0.5, alpha=0.4, label="zavg_BEF = 3 (width and opacity scale with z)"),
         Line2D([], [], c="#7F7F7F", lw=4.0, alpha=0.85, label=f"zavg_BEF >= {zmax:.0f}")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, frameon=False, fontsize=7.5)


def fig_network(s, g, h, term, path):
    ptn = [base.pos[x] for x in part_by[h].partner_hgnc_id]
    nodes = [g] + ptn
    members = set(M6.term_members(v2, v2.col[term]).tolist())
    in_term = {n for n in ptn if n in members}
    Gx = network_graph(nodes, {g}, in_term)
    ang = np.pi / 2 - 2 * np.pi * np.arange(len(ptn)) / len(ptn)
    lay = {g: (0.0, 0.0)}
    lay.update({n: (np.cos(a), np.sin(a)) for n, a in zip(ptn, ang)})
    zmax = max([d["z"] for *_, d in Gx.edges(data=True)] + [4])
    fig, ax = plt.subplots(figsize=(7.2, 7.6))
    draw_net(ax, Gx, lay, {g}, in_term, zmax)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.25)
    ax.set_title(f"{s}: top-10 co-essentiality partners (K = 25 list, ranks clockwise from top)\n"
                 f"predicted V2 term: {term_name(term)} ({term}); edges: zavg_BEF >= 3", fontsize=9)
    legend_net(ax, "the predicted term", zmax)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return Gx, in_term


# ============================================================================================ bundle
Pi = P.set_index("hgnc_id")
PCi = PC.set_index("hgnc_id")
T40i = T40.set_index("hgnc_id")
CHKi = CHK.set_index("hgnc_id")
ASSi = ASS.set_index("hgnc_id")
Ui = U.set_index("hgnc_id")
HUBi = HUB.set_index("hgnc_id")
FLi = FL.set_index("hgnc_id")
SUMMARY = {}


def bundle(s, outdir: Path):
    h = sym2h[s]
    g = pos[s]
    p, pc, u, hb = Pi.loc[h], PCi.loc[h], Ui.loc[h], HUBi.loc[h]
    t40 = T40i.loc[h] if h in T40i.index else None
    ck = CHKi.loc[h] if h in CHKi.index else None
    a = ASSi.loc[h]
    fl = FLi.loc[h]
    term = p.top_term
    col = v2.col[term]
    members = set(M6.term_members(v2, col).tolist()) - {g}
    mem_h = {gt.hgnc_id.values[j] for j in members}
    parts = part_by[h]
    j1 = top1[h]
    j1s = gt.symbol.values[j1]
    L = []
    w = L.append
    w(f"# Evidence bundle: {s}\n")
    w("Machine-generated by `scripts/70_report_bundles.py` (facts only; no interpretation). Sources: results/ledger/*, "
      "results/assessability/assessability_U.tsv, preregistration/uncharacterised_genes.tsv, results/m7/recall_probe_90.tsv, "
      "raw DepMap / orthogonal files via src/orthogonal.py. Values marked † are recomputed here (not ledger rows).\n")

    # ---------------------------------------------------------------- 1 identifiers
    w("## 1. Identifiers and strata\n")
    rows = [("Symbol", s), ("HGNC ID", h), ("Previous symbols", hb.prev_symbols or "—"),
            ("Alias symbols", hb.alias_symbols or "—"), ("UniProt", u.uniprot_ids), ("Ensembl", u.ensembl_gene_id),
            ("Entrez", u.entrez_id), ("Cytogenetic band", u.location), ("DepMap column", u.depmap_column),
            ("Matrix index", g), ("Locus type", hb.locus_type),
            ("D1 (no informative GO BP/MF/CC)", u.D1), ("D2 (UniProt annotation score ≤ threshold)",
                                                       f"{u.D2} (annotation score {u.annotation_score})"),
            ("D3 (PubMed / Tdark)", f"{u.D3} (D3_pubmed {u.D3_pubmed}, D3_tdark {u.D3_tdark}; focused PMIDs "
                                    f"{u.n_pubmed_focused}, all PMIDs {u.n_pubmed_all}; TDL {u.tdl})"),
            ("Curation-lag audit (results/audit)", ("in audit sample, class " + AUDIT[AUDIT.hgnc_id == h]["class"].iloc[0])
             if (AUDIT.hgnc_id == h).any() else "not in the audit sample"),
            ("Family stratum", u.family_stratum), ("Expression stratum", u.expression_stratum),
            ("Expressed (DESIGN incl. lineage-restricted)", a.expressed_design),
            ("Lineage-restricted expression", a.lineage_restricted),
            ("Informativeness (SD) tertile within U", u.sd_tertile_withinU), ("Core", u.core),
            ("Headline stratum", u.headline_stratum), ("Tool background", u.tool_background),
            ("low_coverage", a.low_coverage), ("Paralogues in matrix (n)", p.n_paralogues),
            ("hu.MAP-train gene (positive training pairs)", p.humap_train),
            ("In-degree in K-NN graph / hub", f"{p.in_degree} / {p.hub}"),
            ("Novelty class (agent L; results/m7/report_selection.md)", LCLASS.get(s, "— (module cross-reference)"))]
    w(md_table(pd.DataFrame(rows, columns=["field", "value"])) + "\n")

    # ---------------------------------------------------------------- 2 prediction
    w("## 2. Prediction and calibration\n")
    ci = "—"
    if h in PB_IDX:
        b = PB_BOOT[:, PB_IDX[h]]
        b = b[np.isfinite(b)]
        ci = f"{np.percentile(b, 2.5):.3f}–{np.percentile(b, 97.5):.3f} (cluster bootstrap, {len(b)} refits)"
    pe = p_emp_of(g, term)
    ty_row = T40C[T40C.hgnc_id == h]
    tfq = TFQ.get(h, np.nan)
    tff = bool(np.isfinite(tfq) and ck is not None and float(ck.tf_OR) > TF_OR and tfq < TF_QMAX)
    sr = ST[(ST.set == "real") & (ST.anchor_hgnc_id == h)].iloc[0]
    cs = {c: sr[f"state_{c}"] for c in "PALGS"}
    pi = prot(h) or {}
    enz = "(EC " in str(pi.get("name", ""))
    trans = any(k.lower() in ("transport", "ion transport", "sugar transport", "amino-acid transport", "lipid transport",
                              "protein transport", "mrna transport", "electron transport") for k in pi.get("keywords", []))
    v1pc = isinstance(p.v1p_label, str) and (p.v1p_label.startswith("CP:") or p.v1p_label.startswith("GO:"))
    cl = bool(v1pc and float(p.v1p_label_n_sup or 0) >= 3)
    asm = "assembly" in f"{p.top_term_name} {p.v1p_label_name}".lower()
    ty, why = LG.relationship_type(as_bool(ck.coupling_flag) if ck is not None else False, tff, cs, enz or trans,
                                   bool(pi.get("multipass")), cl, asm)
    rows = [("Predicted V2 term (R1 top, K = 25)", f"{term} {p.top_term_name}"),
            ("S / supporting partners / term size (current V2)", f"{fmt(p.top_S)} / {p.top_n_sup} / {int(p.top_size)}"),
            ("Hypergeometric p (descriptive)", fmt(p.top_p_hyper, 4)), ("p_emp (matched-gene null) †", fmt(pe, 4)),
            ("Most specific term in top 5", f"{p.most_specific_top5} {p.most_specific_top5_name}"),
            ("V1 label (GO CC complex)", f"{nz(p.v1_label)} {nz(p.v1_label_name, '')}".strip()),
            ("V1′ label", f"{nz(p.v1p_label)} {nz(p.v1p_label_name, '')} (supporting partners {p.v1p_label_n_sup})"),
            ("Term family (calibration family)", p.family), ("p_cal", fmt(pc.p_cal, 4)), ("p_cal 95% interval", ci),
            ("Support category / reason", f"{pc.support_category} {nz(pc.support_reason, '')}".strip()),
            ("Covariates: top-K mean zavg / R / coverage pct / size pct",
             f"{fmt(p.zmean)} / {fmt(p.R)} / {fmt(pc.cov_pct)} / {fmt(pc.size_pct)}"),
            ("Rank in primary top 40", t40["rank"] if t40 is not None else "—"),
            ("Tier", (t40.tier if t40 is not None and isinstance(t40.tier, str) and t40.tier else "none (p_cal fill)")),
            ("Top-40-only labels (demotion)", f"demoted {ck.demoted} {nz(ck.demotion_reason, '')}".strip() if ck is not None else "—"),
            ("Relationship type (script rule e→a→c→b→d, §4.4) †", f"{ty} ({why})"),
            ("Relationship type in top40.tsv (clean-first list)",
             f"{ty_row.relationship_type.iloc[0]} ({ty_row.relationship_reason.iloc[0]})" if len(ty_row) else "gene not in top40.tsv"),
            ("Type inputs", f"coupling {ck.coupling_flag if ck is not None else '—'}; TF flag {tff}; P/A/S states "
                            f"{cs['P']}/{cs['A']}/{cs['S']}; EC or transport keyword {enz or trans}; multi-pass "
                            f"{bool(pi.get('multipass'))}; complex-like V1′ {cl}; assembly label {asm}")]
    w(md_table(pd.DataFrame(rows, columns=["field", "value"])) + "\n")
    w("Top-5 terms (R1; u_top5.tsv; p_emp and leave-one-partner-out recomputed †):\n")
    t5 = TOP5[TOP5.hgnc_id == h].sort_values("rank")
    lp = lopo(g, list(t5.term[:3]))
    t5o = pd.DataFrame(dict(rank=t5["rank"], term=t5.term, name=t5.term_name, S=t5.S.map(fmt), n_sup=t5.n_sup,
                            size=t5["size"], p_hyper=t5.p_hyper.map(lambda v: fmt(v, 4)),
                            p_emp=[fmt(p_emp_of(g, t), 4) for t in t5.term], family=t5.family,
                            LOPO_rank_kept=[f"{lp[t][0]}/{lp[t][1]}" if t in lp else "" for t in t5.term]))
    w(md_table(t5o) + "\n")
    w("LOPO_rank_kept = number of single supporting-partner removals (from N(g), no refill) after which the term keeps "
      "its R1 rank / number of supporting partners.\n")

    # ---------------------------------------------------------------- 3 dependency / expression
    w("## 3. Dependency profile and expression\n")
    e = E[:, g]
    fin = np.isfinite(e)
    lin_rows, _ = lineage_stats(e)
    ex = EXPR[g].reindex(lines) if g in EXPR.columns else pd.Series(np.nan, index=lines)
    exa = EXPR[g].dropna() if g in EXPR.columns else pd.Series(dtype=float)
    ok = fin & ex.notna().values
    rho = spearmanr(e[ok], ex.values[ok]).correlation if ok.sum() > 2 else np.nan
    rows = [("Lines in tool matrix / with value", f"{len(e)} / {int(fin.sum())}"),
            ("NaN fraction", fmt(1 - fin.mean(), 4)), ("Mean / SD Chronos", f"{fmt(np.nanmean(e))} / {fmt(np.nanstd(e))}"),
            ("Median / 5th percentile / min", f"{fmt(np.nanmedian(e))} / {fmt(np.nanpercentile(e, 5))} / {fmt(np.nanmin(e))}"),
            ("Fraction of lines < −0.5 (n)", f"{fmt((e[fin] < -0.5).mean(), 4)} ({int((e[fin] < -0.5).sum())})"),
            ("Common-essential (< −0.5 in ≥ 90% of lines)", yn(ce_flag(g))),
            ("Expression lines (default entry)", len(exa)),
            ("Fraction lines log2(TPM+1) ≥ 1 / ≥ 2", f"{fmt((exa >= 1).mean(), 3)} / {fmt((exa >= 2).mean(), 3)}"),
            ("Median log2(TPM+1)", fmt(exa.median(), 2)),
            ("Spearman ρ(effect, own expression), n †", f"{fmt(rho)} (n = {int(ok.sum())})"),
            ("Ledger coupling ρ / flag (abs ρ > 0.3)", f"{fmt(ck.coupling_rho) if ck is not None else '—'} / "
                                                    f"{ck.coupling_flag if ck is not None else '—'}"),
            ("Split-half R(g) (seeds 0–4, K = 25)", fmt(a.R)), ("R0 mean / max over 200 matches", f"{fmt(a.R0_mean)} / {fmt(a.R0_max)}"),
            ("#R0 ≥ R; empirical p", f"{a.n_R0_ge_R}; {fmt(a.p, 4)}"), ("RBO R / p", f"{fmt(a.R_rbo)} / {fmt(a.p_rbo, 4)}"),
            ("Assessable (DESIGN)", a.assessable_design)]
    w(md_table(pd.DataFrame(rows, columns=["field", "value"])) + "\n")
    w("Lineage enrichment (lineages with ≥ 10 lines, lowest mean effect; Mann–Whitney vs other lines, descriptive):\n")
    w(md_table(pd.DataFrame([dict(lineage=r["lineage"], n=r["n"], mean=fmt(r["mean"]), median=fmt(r["median"]),
                                  MW_p=fmt(r["p"], 4)) for r in lin_rows])) + "\n")

    # ---------------------------------------------------------------- 4 partners
    w("## 4. Top-10 partners (u_partners.tsv; GLS rank in g's GLS row after §3.1 exclusions)\n")
    flp = FLP[FLP.hgnc_id == h].set_index("partner_hgnc_id")
    rows = []
    for x in parts.itertuples():
        j = base.pos[x.partner_hgnc_id]
        fr = flp.loc[x.partner_hgnc_id] if x.partner_hgnc_id in flp.index else None
        ann = nz(x.partner_top_annotations, "")
        ann = "; ".join(ann.split("|")[:2])
        rows.append(dict(rank=x.rank, partner=x.partner_symbol, zavg_BEF=fmt(x.zavg_BEF, 2),
                         z_B_E_F=f"{fmt(x.z_B, 1)}/{fmt(x.z_E, 1)}/{fmt(x.z_F, 1)}",
                         GLS_rank=GLS_RANK.get((h, x.partner_symbol), np.nan),
                         in_term=("yes" if j in members else "no"),
                         partner_mean_eff=fmt(x.partner_mean_effect, 2),
                         frac_lt_m05=fmt(x.partner_frac_lines_lt_m0p5, 3), CE=yn(ce_flag(j)),
                         band=x.partner_location,
                         same_chr_dist=(f"yes, {int(float(x.distance_bp)):,} bp" if as_bool(x.same_chromosome) and
                                        str(x.distance_bp) not in ("", "nan") else ("yes" if as_bool(x.same_chromosome) else "no")),
                         paralogue=("g" if as_bool(x.paralogue_of_g) else ("other partner" if as_bool(x.paralogue_of_other_partner) else "no")),
                         hub=f"{x.partner_in_degree}{' HUB' if as_bool(x.partner_hub) else ''}",
                         locus_CN=(f"locus {yn(fr.locus_flag)}; CN r {fmt(fr.cn_r, 2)}" if fr is not None else "not supporting"),
                         huMAP_train=f"{yn(as_bool(x.partner_humap_train))}/pair {yn(as_bool(x.pair_humap_train))}",
                         in_U=yn(as_bool(x.partner_in_U)), top_annotations=ann[:90]))
    w(md_table(pd.DataFrame(rows)) + "\n")
    w("in_term = partner annotated (current V2, propagated) to the predicted term; CE = common-essential; locus/CN "
      "evaluated for supporting partners only (u_flag_partners.tsv); hub = in-degree in the K = 25 graph (HUB = top 1%); "
      "huMAP_train = partner gene / g–partner pair in hu.MAP training positives.\n")

    # ---------------------------------------------------------------- 5 robustness
    w("## 5. Robustness (§4.3; ledger rows unless marked †)\n")
    same_chr = int(sum(as_bool(x) for x in parts.same_chromosome))
    rows = [("Same-arm and paralogue exclusion", "built in", f"g arm {p.arm}; top-10 partners on g's chromosome: {same_chr}"),
            ("Locus (bidirectional/overlapping/readthrough, strand-agnostic)", f"{fl.n_locus}/{fl.n_supporting} supporting partners flagged", ""),
            ("CN co-amplification (r(g effect, partner CN) > 0.3)", f"{fl.n_cn}/{fl.n_cn_measured} flagged",
             "; ".join(f"{r.partner_symbol} r={fmt(r.cn_r, 2)}" for r in flp.itertuples())),
            ("Hub-driven (> 50% of S from hub partners)", f"{fl.hub_driven} (hub share {fmt(fl.hub_share, 2)}; hub partners {fl.n_hub})", ""),
            ("§4.3 built-in exclusion (≥ half of supporting partners flagged or hub-driven)", f"{fl.excl43}", f"flagged: {nz(fl.flagged_partners)}")]
    if ck is not None:
        rows += [("Lineage leave-out", "retained" if as_bool(ck.leaveout_retained) else "NOT retained",
                  f"removed {ck.lineage} ({ck.lineage_removed_lines} lines; mean effect {fmt(ck.lineage_mean_effect)}); "
                  f"top term after refit {ck.leaveout_top_term} {term_name(ck.leaveout_top_term)}; N(g) overlap "
                  f"{fmt(ck.leaveout_nb_overlap, 2)}"),
                 ("Dependency–expression coupling (abs ρ > 0.3)", "flag" if as_bool(ck.coupling_flag) else "no flag",
                  f"ρ = {fmt(ck.coupling_rho)}, n = {ck.coupling_n}"),
                 ("TF enrichment of N(g) (OR > 3, BH q < 0.05 over primary top 40)", "flag" if tff else "no flag",
                  f"TFs in N(g) {ck.tf_in_N}; OR {fmt(ck.tf_OR, 2)}; p {fmt(ck.tf_p, 4)}; q {fmt(tfq, 4)}"),
                 ("TP53 status (Mann–Whitney, BH q < 0.05 over primary top 40)",
                  "flag" if np.isfinite(TP53Q.get(h, np.nan)) and TP53Q[h] < TP53_QMAX else "no flag",
                  f"mut {ck.tp53_n_mut} / WT {ck.tp53_n_wt}; p {fmt(ck.tp53_p, 4)}; q {fmt(TP53Q.get(h, np.nan), 4)}; "
                  f"median diff (mut − WT) {fmt(ck.tp53_median_diff)}"),
                 ("DEMETER2 replication (mean partner r ≥ 95th pct of random sets)",
                  ("not measured" if not as_bool(ck.d2_measured) else ("replicated" if as_bool(ck.d2_replicated) else "NOT replicated")),
                  f"partners in D2 {ck.d2_n_partners}; mean r {fmt(ck.d2_mean_r)}; null 95th pct {fmt(ck.d2_null_p95)}")]
    for k in (10, 50):
        tk = topK[k][g]
        rows.append((f"K = {k} top term †", "same" if tk == term else "different", f"{tk} {term_name(tk)}"))
    rows.append(("GLS network top term (K = 25, §3.1 exclusions) †", "same" if GLS_TOP[g] == term else "different",
                 f"{GLS_TOP[g]} {term_name(GLS_TOP[g])}"))
    rows.append(("Shared-sgRNA / per-guide check", "not possible", "guide-level data not available (recorded)"))
    w(md_table(pd.DataFrame(rows, columns=["check", "result", "detail"])) + "\n")

    # ---------------------------------------------------------------- 6 orthogonal
    w("## 6. Orthogonal evidence (§5; support.tsv / support_sources.tsv, real prediction)\n")
    rows = []
    for c in "PALGS":
        rows.append(dict(cls=c, state=sr[f"state_{c}"], class_p=fmt(sr[f"p_{c}"], 4)))
    w(md_table(pd.DataFrame(rows)) + "\n")
    w(f"Class p = Simes within class; Holm across measured classes (α = 0.05) decides 'supports'. Supporting classes: "
      f"{nz(sr.supporting_classes, 'none')}; diagnostic class measured / supports: {sr.diag_measured} / {sr.diag_support}; "
      f"contradiction: {sr.contradiction} (sources: {nz(sr.contradiction_sources)}; HPA-only: {sr.contradiction_hpa_only}); "
      f"term compartments: {nz(sr.term_compartments)}; g multi-localised: {sr.multi_localised}; homology (IBA/ISO to "
      f"term, reported only): {nz(sr.homology_descriptive, 'no IBA/ISO annotation for g')}; "
      f"members tested: {sr.n_members}.\n")
    ss = SS[(SS.set == "real") & (SS.anchor_symbol == s) & (SS.tested_symbol == s)]
    w(md_table(pd.DataFrame(dict(source=ss.source, cls=ss.cls, kind=ss.kind, measured=ss.measured,
                                 members_measured=ss.n_measured, stat=ss.stat.map(lambda v: fmt(v, 3)),
                                 null_mean=ss.null_mean.map(lambda v: fmt(v, 3)), p=ss.p.map(lambda v: fmt(v, 4)),
                                 note=ss.note))) + "\n")
    w("Pair-level detail with the top-10 partners † (binary: Y edge / N measured, no edge / n.m. not measured; "
      "continuous: score (row percentile in g's row); Burke: max pDockQ of the modelled pair, edge ≥ 0.23; hu.MAP 3.0 "
      "is not independent, reported only):\n")
    rows = []
    for x in parts.itertuples():
        b_ = x.partner_hgnc_id
        r = dict(partner=x.partner_symbol)
        for n, lab in (("BioPlex3", "BioPlex"), ("OpenCell_PPI", "OpenCell"), ("BioGRID_LTP", "BioGRID-LTP"),
                       ("STRING_exp", "STRING-exp"), ("HCM_SAINT", "HCM-SAINT"), ("huMAP3_NI", "huMAP3(NI)")):
            v = edge(n, h, b_)
            r[lab] = "n.m." if v is None else ("Y" if v else "N")
        for n, lab in (("ProteomeHD", "ProteomeHD"), ("CCLE_proteomics", "CCLE-prot r"),
                       ("PerturbSeq_K562_GW", "PS K562-GW r"), ("PerturbSeq_K562_essential", "PS K562-ess r"),
                       ("PerturbSeq_RPE1_essential", "PS RPE1 r")):
            r[lab] = pair_cont(n, h, b_)
        r["Burke pDockQ"] = burke_pair(h, b_)
        rows.append(r)
    w(md_table(pd.DataFrame(rows)) + "\n")
    w("g's physical edges per source (all interactors; * = annotated to the predicted term; † recomputed):\n")
    rows = []
    for n in PHYS + ("huMAP3_NI",):
        S_ = SRC[n]
        i = S_.index.get(h)
        if i is None:
            rows.append(dict(source=n, measured="no", degree="", term_members="", interactors=""))
            continue
        nbr = [S_.genes[k] for k in S_.adj[i].indices]
        mem = [sym(x) for x in nbr if x in mem_h]
        lst = sorted((sym(x) + ("*" if x in mem_h else "") for x in nbr), key=lambda z: (not z.endswith("*"), z))
        rows.append(dict(source=n, measured="yes", degree=len(nbr), term_members=len(mem),
                         interactors=", ".join(lst[:40]) + (" …" if len(lst) > 40 else "")))
    w(md_table(pd.DataFrame(rows)) + "\n")
    bk = burke[(burke.a == h) | (burke.b == h)].copy()
    if len(bk):
        bk["other"] = np.where(bk.a == h, bk.b, bk.a)
        bk = bk.sort_values("pDockQ", ascending=False).drop_duplicates("other")
        hi_ = bk[bk.pDockQ >= PDQ]
        w(f"Burke 2023 AF2: {len(bk)} modelled pairs with g; {len(hi_)} with pDockQ ≥ {PDQ}: " +
          (", ".join(f"{sym(o)}{'*' if o in mem_h else ''} ({v:.3f})" for o, v in zip(hi_.other, hi_.pDockQ)) or "none") + "\n")
    else:
        w("Burke 2023 AF2: g not modelled.\n")
    rows = []
    for n in CONT:
        r = cont_row(n, h)
        if r is None:
            rows.append(dict(source=n, g_measured="no", top_partners_by_score=""))
            continue
        v, pct = r
        o = np.argsort(-np.nan_to_num(v, nan=-np.inf))[:8]
        rows.append(dict(source=n, g_measured="yes", top_partners_by_score=", ".join(
            f"{sym(SRC[n].genes[k])}{'*' if SRC[n].genes[k] in mem_h else ''} ({v[k]:.2f})" for k in o if np.isfinite(v[k]))))
    w("Continuous sources: g's 8 highest-scoring genes († ; * = annotated to the predicted term):\n")
    w(md_table(pd.DataFrame(rows)) + "\n")

    # ---------------------------------------------------------------- 7 localisation
    w("## 7. Localisation calls per source\n")
    hr = HPA_RAW[HPA_RAW.Gene == u.ensembl_gene_id]
    oc = OC_LOC[OC_LOC.ensg_id == u.ensembl_gene_id]
    hp = HCM_PREY[HCM_PREY.HGNC == h]
    hbt = HCM_BAIT[HCM_BAIT.HGNC == h] if "HGNC" in HCM_BAIT.columns else HCM_BAIT.iloc[0:0]
    mc = SRC["MitoCarta3"]
    rows = [("HPA v25.1 (admitted L source)",
             (f"reliability {hr.Reliability.iloc[0]}; main: {hr['Main location'].iloc[0] or '—'}; additional: "
              f"{hr['Additional location'].iloc[0] or '—'}; Enhanced: {hr.Enhanced.iloc[0] or '—'}; Supported: "
              f"{hr.Supported.iloc[0] or '—'}; Approved: {hr.Approved.iloc[0] or '—'}; Uncertain: {hr.Uncertain.iloc[0] or '—'}")
             if len(hr) else "not in HPA", f"{comp_str('HPA', h)} (high-reliability: {comp_str('HPA', h, True)})"),
            ("OpenCell (contradiction rule only)",
             (f"grade 3: {oc.annotations_grade_3.iloc[0] or '—'}; grade 2: {oc.annotations_grade_2.iloc[0] or '—'}; "
              f"grade 1: {oc.annotations_grade_1.iloc[0] or '—'}") if len(oc) else "not tagged", comp_str("OpenCell_loc", h)),
            ("Human Cell Map (contradiction rule only)",
             (f"prey; NMF rank {hp['NMF rank'].iloc[0]}; NMF ('MMF localization'): {hp['MMF localization'].iloc[0]}; "
              f"SAFE: {hp['SAFE localization'].iloc[0]}" if len(hp) else "not a prey") +
             ("; also a BioID bait" if len(hbt) else "; not a bait"), comp_str("HCM_NMF", h)),
            ("MitoCarta3.0", "listed" if h in mc.comp else ("assessed, not listed" if h in set(mc.meta["assessed"])
                                                             else "not in MitoCarta table"), comp_str("MitoCarta3", h))]
    w(md_table(pd.DataFrame(rows, columns=["source", "raw call", "common-vocabulary compartments"])) + "\n")

    # ---------------------------------------------------------------- 8 protein
    w("## 8. Protein features (UniProt reviewed TSV)\n")
    if pi:
        rows = [("Entry / existence / annotation", f"{pi['entry']} / {pi['existence']} / {pi['annot']}"),
                ("Protein names", pi["name"]), ("Length (aa)", pi["length"]), ("Pfam", pi["pfam"] or "—"),
                ("InterPro", pi["interpro"] or "—"), ("Domain [FT]", pi["domain_ft"] or "—"),
                ("Transmembrane keyword / multi-pass / single-pass", f"{yn(pi['tm'])} / {yn(pi['multipass'])} / {yn(pi['singlepass'])}"),
                ("Signal peptide keyword / transit peptide keyword", f"{yn(pi['signal'])} / {yn(pi['transit'])}"),
                ("Subcellular location [CC]", pi["loc_cc"] or "—"), ("Sequence similarities", pi["simil"] or "—"),
                ("Keywords", "; ".join(pi["keywords"])), ("Function [CC] (verbatim, UniProt)", pi["function"] or "—")]
        w(md_table(pd.DataFrame(rows, columns=["field", "value"])) + "\n")
    else:
        w("No reviewed UniProt entry mapped to this HGNC ID.\n")

    # ---------------------------------------------------------------- 9 recall probe
    w("## 9. LLM recall probe (results/m7/recall_probe_90.tsv)\n")
    pr_ = PROBE[PROBE.hgnc_id == h]
    if len(pr_):
        w(f"- recognised: **{pr_.recognised.iloc[0]}**; confidence: {pr_.confidence.iloc[0]}\n"
          f"- recalled function (verbatim): \"{pr_.recalled_function.iloc[0]}\"\n")
    else:
        w("- not probed\n")

    # ---------------------------------------------------------------- 10 cell lines
    w("## 10. DepMap cell-line selection (Template B §2 rule; † recomputed)\n")
    df, cand, chosen, ctrl, ctrl_rule, used, counts = choose_lines(g, j1)
    w(f"Rank-1 partner used for the partner criterion: **{j1s}**. Criterion applied: {used}.\n")
    w("Funnel: " + "; ".join(f"{k} {v}" for k, v in counts.items()) + ". Not amplified = OmicsCNGeneWGS relative CN < 1.5 "
      "(NaN CN allowed). Ranking: TP53 mutant (damaging/hotspot; proxy for TP53-null) first, then ScreenNNMD ascending "
      "(better screen), then g effect; line 2 = best line of another lineage when available.\n")
    if chosen:
        w("Chosen dependent lines:\n")
        w(md_table(line_table(df, chosen)) + "\n")
    else:
        w("No dependent line meets the rule or its relaxations.\n")
    w(f"Top candidates (up to 10):\n")
    w(md_table(line_table(df, cand.index[:10])) + "\n" if len(cand) else "none\n")
    if ctrl is not None:
        w(f"Non-dependent expressing control (g ≥ −0.2, log2(TPM+1) ≥ 2, not amplified; {ctrl_rule}; highest expression):\n")
        w(md_table(line_table(df, [ctrl])) + "\n")
    else:
        w("No control line found.\n")
    sel = [(f"D{k + 1}", mid, "o") for k, mid in enumerate(chosen)] + ([("C", ctrl, "s")] if ctrl is not None else [])

    # ---------------------------------------------------------------- figures
    w("## 11. Figures\n")
    w("- `fig_profile.png`: (a) g's Chronos effect vs the rank-1 partner across lines (5 most dependent lineages coloured); "
      "(b) g's effect vs own expression; chosen lines circled (D1, D2), control squared (C).\n"
      "- `fig_network.png`: g, its top-10 partners and zavg_BEF ≥ 3 edges among them; node colour = annotated to the "
      "predicted term; solid black edge = physical support in an admitted P source.\n")
    fig_profile(s, g, j1, j1s, sel, outdir / "fig_profile.png")
    Gx, in_term = fig_network(s, g, h, term, outdir / "fig_network.png")
    w(f"Network edges among the 11 nodes (zavg_BEF ≥ 3, mean of both directions †): {Gx.number_of_edges()}; with physical "
      f"support: {sum(d['phys'] for *_, d in Gx.edges(data=True))} (" +
      ", ".join(f"{gt.symbol.values[a]}–{gt.symbol.values[b]}" for a, b, d in Gx.edges(data=True) if d["phys"]) + ").\n")
    (outdir / "bundle.md").write_text("\n".join(L))
    SUMMARY[s] = dict(term=p.top_term_name, partners=list(parts.partner_symbol[:3]),
                      classes=nz(sr.supporting_classes, "none"), type=ty, p_cal=pc.p_cal,
                      flags=[n for n, f in (("leaveout_fail", ck is not None and not as_bool(ck.leaveout_retained)),
                                            ("D2_not_replicated", ck is not None and as_bool(ck.d2_flag)),
                                            ("TP53", np.isfinite(TP53Q.get(h, np.nan)) and TP53Q[h] < TP53_QMAX),
                                            ("coupling", ck is not None and as_bool(ck.coupling_flag)),
                                            ("TF", tff), ("K10_diff", topK[10][g] != term), ("K50_diff", topK[50][g] != term),
                                            ("CE", ce_flag(g)), ("probe_recognised", len(pr_) and pr_.recognised.iloc[0] == "yes"))
                             if f])
    log(f"{s}: bundle written")


# ============================================================================================ TM2D module
def module(outdir: Path):
    hs = [sym2h[s] for s in MODULE]
    gs = [pos[s] for s in MODULE]
    ptn = []
    for h in hs:
        for x in part_by[h].partner_hgnc_id:
            j = base.pos[x]
            if j not in gs and j not in ptn:
                ptn.append(j)
    nodes = gs + ptn
    term = Pi.loc[hs[0]].top_term
    members = set(M6.term_members(v2, v2.col[term]).tolist())
    in_term = {n for n in nodes if n in members}
    Gx = network_graph(nodes, set(gs), in_term)
    zmax = max([d["z"] for *_, d in Gx.edges(data=True)] + [4])
    # deterministic layout: the three genes on an inner triangle; partners on an outer circle, ordered by the
    # circular mean angle of the genes whose top-10 list contains them (shared partners sit between those genes)
    core_ang = {n: np.pi / 2 + 2 * np.pi * k / 3 for k, n in enumerate(gs)}
    lay = {n: (0.38 * np.cos(a_), 0.38 * np.sin(a_)) for n, a_ in core_ang.items()}
    plists = {g_: set(base.pos[x] for x in part_by[h_].partner_hgnc_id) for g_, h_ in zip(gs, hs)}
    key = []
    for n in ptn:
        angs = [core_ang[g_] for g_ in gs if n in plists[g_]]
        key.append((float(np.angle(np.mean(np.exp(1j * np.array(angs))))) % (2 * np.pi), -zpair(n, gs[0]), n))
    key.sort()
    for k, (_, _, n) in enumerate(key):
        a_ = key[0][0] + 2 * np.pi * k / len(key)
        lay[n] = (np.cos(a_), np.sin(a_))
    fig, ax = plt.subplots(1, 2, figsize=(14, 7.6), gridspec_kw=dict(width_ratios=[1.55, 1]))
    draw_net(ax[0], Gx, lay, set(gs), in_term, zmax)
    ax[0].set_xlim(-1.3, 1.3)
    ax[0].set_ylim(-1.3, 1.25)
    ax[0].set_title("(a) TM2D1, TM2D2, CHIC2 and the union of their top-10 partners; edges zavg_BEF ≥ 3\n"
                    f"blue = annotated to {term_name(term)} ({term})", fontsize=9, loc="left")
    legend_net(ax[0], term_name(term), zmax)
    shared = [n for n in ptn if sum(n in set(base.pos[x] for x in part_by[h].partner_hgnc_id) for h in hs) >= 2]
    hm = gs + shared
    Mz = np.array([[zpair(a, b) if a != b else np.nan for b in hm] for a in hm])
    im = ax[1].imshow(Mz, cmap="viridis", vmin=0, vmax=np.nanmax(Mz))
    lbl = [gt.symbol.values[n] for n in hm]
    ax[1].set_xticks(range(len(hm)), lbl, rotation=60, ha="right", fontsize=8)
    ax[1].set_yticks(range(len(hm)), lbl, fontsize=8)
    for i in range(len(hm)):
        for k in range(len(hm)):
            if np.isfinite(Mz[i, k]):
                ax[1].text(k, i, f"{Mz[i, k]:.0f}", ha="center", va="center", fontsize=6.5,
                           color="white" if Mz[i, k] < 0.6 * np.nanmax(Mz) else "black")
    ax[1].spines[:].set_visible(False)
    ax[1].set_title("(b) zavg_BEF among the three genes and partners shared by ≥ 2 of them", fontsize=9, loc="left")
    fig.colorbar(im, ax=ax[1], fraction=0.046, pad=0.04, label="zavg_BEF")
    fig.tight_layout()
    fig.savefig(outdir / "fig_module.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    # module.md
    L = ["# TM2D module: TM2D1, TM2D2, CHIC2\n",
         "Machine-generated by `scripts/70_report_bundles.py` (facts only). CHIC2's full bundle: `CHIC2_bundle.md`.\n",
         "## Predictions\n"]
    rows = []
    for s, h in zip(MODULE, hs):
        p, t = Pi.loc[h], T40i.loc[h] if h in T40i.index else None
        rows.append(dict(gene=s, rank_primary=t["rank"] if t is not None else "—", L_class=LCLASS.get(s, "N1 (selection note)"),
                         term=f"{p.top_term} {p.top_term_name}", p_cal=fmt(PCi.loc[h].p_cal, 4),
                         V1p=f"{nz(p.v1p_label)} {nz(p.v1p_label_name, '')}".strip(), band=p.location,
                         mean_effect=fmt(p.mean_effect), frac_lt_m05=fmt(p.frac_lines_lt_m0p5, 3)))
    L.append(md_table(pd.DataFrame(rows)) + "\n")
    L.append("## Pairwise among the three genes († recomputed; rank = position in the other gene's K = 100 neighbour list)\n")
    rows = []
    for i, (sa, a) in enumerate(zip(MODULE, gs)):
        for sb, b in list(zip(MODULE, gs))[i + 1:]:
            ra = np.flatnonzero(base.ids100[a] == b)
            rb = np.flatnonzero(base.ids100[b] == a)
            ha, hb_ = gt.hgnc_id.values[a], gt.hgnc_id.values[b]
            para = b in set(np.asarray(base.par.get(a, []), dtype=np.int64).tolist())
            same_arm = base.arm[a] == base.arm[b]
            miss = "excluded (paralogue)" if para else ("excluded (same arm)" if same_arm else ">100")
            r = dict(pair=f"{sa}–{sb}", zavg_BEF=fmt(zpair(a, b), 2),
                     rank_b_in_a=int(ra[0]) + 1 if len(ra) else miss, rank_a_in_b=int(rb[0]) + 1 if len(rb) else miss)
            for n in PHYS + ("huMAP3_NI",):
                v = edge(n, ha, hb_)
                r[n] = "n.m." if v is None else ("Y" if v else "N")
            for n in CONT:
                r[n] = pair_cont(n, ha, hb_)
            r["Burke"] = burke_pair(ha, hb_)
            rows.append(r)
    L.append(md_table(pd.DataFrame(rows)) + "\n")
    L.append("## Partners shared by ≥ 2 of the three genes (top-10 lists)\n")
    rows = []
    for n in shared:
        hn = gt.hgnc_id.values[n]
        r = dict(partner=gt.symbol.values[n], in_term=yn(n in members))
        for s, h in zip(MODULE, hs):
            q = part_by[h][part_by[h].partner_hgnc_id == hn]
            r[s] = f"#{q['rank'].iloc[0]} z={fmt(q.zavg_BEF.iloc[0], 1)}" if len(q) else "—"
        rows.append(r)
    L.append(md_table(pd.DataFrame(rows)) + "\n" if rows else "none\n")
    L.append(f"Network: {len(nodes)} nodes, {Gx.number_of_edges()} edges (zavg_BEF ≥ 3), "
             f"{sum(d['phys'] for *_, d in Gx.edges(data=True))} with physical support: " +
             ", ".join(f"{gt.symbol.values[a]}–{gt.symbol.values[b]}" for a, b, d in Gx.edges(data=True) if d["phys"]) + ".\n")
    L.append("Figure: `fig_module.png`.\n")
    (outdir / "module.md").write_text("\n".join(L))
    log("TM2D module written")


# ============================================================================================ run
for s in GENES:
    d = OUTD / s
    d.mkdir(parents=True, exist_ok=True)
    bundle(s, d)
md = OUTD / "TM2D_module"
md.mkdir(parents=True, exist_ok=True)
tmp = md / "_chic2"
tmp.mkdir(exist_ok=True)
bundle("CHIC2", tmp)
for f in ("bundle.md", "fig_profile.png", "fig_network.png"):
    (tmp / f).rename(md / f"CHIC2_{f}")
tmp.rmdir()
module(md)
SUM = pd.DataFrame([dict(gene=s, **v) for s, v in SUMMARY.items()])
SUM["partners"] = SUM.partners.map(", ".join)
SUM["flags"] = SUM["flags"].map(lambda x: ", ".join(x) if x else "")
SUM.to_csv(OUTD / "bundle_summary.tsv", sep="\t", index=False, float_format="%.4g")
C.write_manifest(OUTD / "70_manifest.json", "scripts/70_report_bundles.py", gate,
                 ["results/m7/report_selection.md", *[f"results/ledger/{x}" for x in (
                     "u_predictions.tsv", "u_pcal.tsv", "top40_primary.tsv", "top40.tsv", "u_partners.tsv",
                     "u_top5.tsv", "u_flags.tsv", "u_flag_partners.tsv", "support.tsv", "support_sources.tsv",
                     "checks_all_evaluated.tsv", "top40_partners_gls.tsv")], M6.ASSESS, M6.U_TSV,
                  "results/m7/recall_probe_90.tsv", *DATA], seed=0, t0=T_START, extra=dict(genes=ALL))
log(f"done in {time.perf_counter() - T_START:.0f} s")
