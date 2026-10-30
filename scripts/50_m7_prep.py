#!/usr/bin/env python
"""50_m7_prep.py -- M7 preparation: candidate lists, blinded-judging statements and blind-agent inputs
(DESIGN.md v2.3 §6.2-§6.4; DEVIATIONS.md rows 2026-10-30 "top-40 fill under the low-yield branch" and "secondary
candidate list S20").

Outputs (results/m7/):
  s20.tsv          S20 secondary list (DEVIATIONS S20 row): expressed + assessable (DESIGN) U genes with a prediction
                   and NO p_cal (support_category no_pcal) where EVERY no-p_cal reason is one of: family with < 30 H
                   genes, zmean > P95, R > P95, cov_pct > P95 (high side); no §4.3 exclusion; no §5.3 contradiction
                   (4 named localisation sources, src/support.contradiction, same call as scripts/43); ranked by
                   top-K mean zavg_BEF (zmean) desc, ties by symbol; mitochondrial family <= frozen top-20 cap (6).
  extra30.tsv      §6.4 secondary: 30 U genes from pool = expressed, assessable, in-support p_cal, NOT in the primary
                   top 40 (results/ledger/top40_primary.tsv); 5 equal-count p_cal quantile bins (rank-based, ties by
                   symbol), 6 per bin, numpy default_rng(0).
  hval10.tsv       §6.4 judge validation: 10 H genes (default_rng(0) over H genes sorted by hgnc_id) with >= 1 current
                   target term that is not circularity-flagged (circularity_annotations any_pmid_flagged = False,
                   the M5b primary convention) and lies in the V2 candidate window (current base size 5-200, the
                   vocabulary the decoys come from); real statement = the most specific such target (smallest current
                   base size, ties by GO id).
  statements.tsv   item_id, hgnc_id, slot (A-D), statement. Template: "GENE_X functions in <V2 term name>[; module
                   context: <V1' label name>]"; Complex Portal ", ... variant" suffixes stripped (subunit names); the
                   gene's own identifiers redacted (src/redact.py). No partner names. Relationship type is NOT
                   included (see manifest note). hval10: real = target term name only.
                   Decoys (3 per gene): other U genes' top V2 terms (unique terms of u_predictions), same family, not
                   the real term / an ancestor / a descendant, member-set Jaccard < 0.1 (current V2 base members),
                   random among the 10 closest in |log size| (src/ledger.choose_decoy convention used for the M6 decoy
                   predictions), decoys mutually not nested and with distinct labels; rng default_rng([0, matrix
                   position]). If the real statement has a V1' label, each decoy carries the V1' label of a random
                   donor U gene predicting that decoy term (label present, != the real label, GO labels not nested
                   with the real term/label); if not, decoys carry no label. Slot order: default_rng([0, position, 1]).
  answer_key.tsv   per gene: item_id, hgnc_id, symbol, set, real_slot (JUDGES MUST NEVER READ).
  answer_key_slots.tsv  per slot provenance (term, label, donor, size distance, Jaccard, symbol-like tokens).
  gene_packets/<HGNC_n>.txt  for agent L: hgnc_id, symbol, previous symbols, aliases, UniProt accession(s), cytoband.
  probe_list.tsv   recall probe (top40 ∪ S20 ∪ extra30): hgnc_id, symbol, prev_symbols, alias_symbols; shuffled (seed 0).
  manifest.json    inputs (SHA-256), counts, choices.
Run: .env/bin/python -I scripts/50_m7_prep.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m4_common as C  # noqa: E402

T_START = time.perf_counter()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(C.ROOT))
import m5_common as M5  # noqa: E402
import m5b_common as B  # noqa: E402
import m6_common as M6  # noqa: E402
from src import orthogonal as O  # noqa: E402
from src import redact as RD  # noqa: E402
from src import support as SP  # noqa: E402

log = C.log
ROOT = C.ROOT
OUT = ROOT / "results" / "m7"
PK = OUT / "gene_packets"
OUT.mkdir(parents=True, exist_ok=True)
PK.mkdir(parents=True, exist_ok=True)
SEED = C.fz("seeds", "decoys")                       # 0
N_DECOY = C.fz("judging", "decoys_per_gene")         # 3
MAXJ = C.fz("judging", "decoy_max_jaccard")          # 0.1
N_EXTRA = C.fz("judging", "extra_u_genes_across_pcal_bins")   # 30
N_HVAL = C.fz("judging", "validation_h_genes")       # 10
MITO_CAP = C.fz("tiers", "mito_cap_top20_max_count")  # 6 (= floor(1/3 * 20))
LO, HI = C.fz("vocabulary", "candidate_term_min_genes"), C.fz("vocabulary", "candidate_term_max_genes")
N_S20, N_BINS, N_NEAR = 20, 5, 10
SLOTS = "ABCD"
INPUTS = ["results/ledger/u_predictions.tsv", "results/ledger/u_pcal.tsv", "results/ledger/tiers_all.tsv",
          "results/ledger/u_flags.tsv", "results/ledger/top40_primary.tsv", "results/ledger/support.tsv",
          "results/holdout/H_genes.tsv", "results/holdout/H_targets.tsv",
          "results/holdout/circularity_annotations.tsv", "results/ids/hgnc_hub.tsv", M5.GAF_CUR, M5.OBO_CUR,
          M5.HGNC, M5.UNIPROT, "config/term_families.tsv"]


def as_bool(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


ALLOWED_REASON = re.compile(r"^(family \S+ \(< 30 H genes\)|zmean > P95|R > P95|cov_pct > P95)$")


def reasons(s) -> list[str]:
    return [x.strip() for x in str(s).split(";") if x.strip()]


def clean_label(name) -> str:
    """V1' label for a statement: Complex Portal ', <subunits> variant' suffix stripped (it names subunits)."""
    if not isinstance(name, str) or not name.strip():
        return ""
    return re.sub(r",\s*[^,]*\bvariant\s*$", "", name.strip())


# ============================================================================================ data
base = B.Base()
v2 = B.build_v2(base, M5.GAF_CUR, label="current")
onto, gt = base.onto, base.gt
P = M6.read_tsv("u_predictions.tsv")
PC = M6.read_tsv("u_pcal.tsv")
TA = M6.read_tsv("tiers_all.tsv")
FL = M6.read_tsv("u_flags.tsv")
TOP = M6.read_tsv("top40_primary.tsv")
SUP = M6.read_tsv("support.tsv")
HUB = pd.read_csv(ROOT / "results/ids/hgnc_hub.tsv", sep="\t", dtype=str, keep_default_na=False).set_index("hgnc_id")
HGNC_RAW = pd.read_csv(ROOT / M5.HGNC, sep="\t", dtype=str, keep_default_na=False,
                       usecols=["hgnc_id", "name", "prev_name", "alias_name"]).set_index("hgnc_id")
UP = pd.read_csv(ROOT / M5.UNIPROT, sep="\t", dtype=str, keep_default_na=False,
                 usecols=["Entry", "Protein names", "HGNC"])
UP["hgnc"] = UP.HGNC.str.split(";").map(lambda x: [y.strip() for y in x if y.strip()])
UP = UP.explode("hgnc")
UP_BY = UP.groupby("hgnc")
Pi = P.set_index("hgnc_id")
top_ids = TOP.hgnc_id.tolist()
assert len(top_ids) == 40


def members(term: str) -> frozenset:
    return frozenset(M6.term_members(v2, int(v2.col[term])).tolist())


def redactor_for(h: str) -> RD.Redactor:
    r = HUB.loc[h]
    pn = UP_BY.get_group(h)["Protein names"].tolist() if h in UP_BY.groups else []
    hn = HGNC_RAW.loc[h] if h in HGNC_RAW.index else None
    # HGNC name lists are pipe-separated and quoted (names may contain commas)
    names = [] if hn is None else [hn["name"]] + [s.strip().strip('"') for f in ("prev_name", "alias_name")
                                                   for s in str(hn[f]).split("|") if s.strip().strip('"')]
    return RD.gene_redactor(r["symbol"], r["prev_symbols"], r["alias_symbols"], r["uniprot_ids"], pn, names)


# ============================================================================================ contradiction (S20)
log("loading the four §5.3 localisation sources")
_m = O.mapper()
LOC = [O.LOADERS[n](_m) for n in ("HPA", "OpenCell_loc", "HCM_NMF", "MitoCarta3")]


def contradiction(h: str, term: str) -> dict:
    mem = [gt.hgnc_id.values[j] for j in sorted(members(term)) if gt.hgnc_id.values[j] != h]
    return SP.contradiction(h, mem, LOC)


# check: reproduces the scripts/43 calls on the real top-40 rows
chk = SUP[(SUP.set == "real")].drop_duplicates("tested_hgnc_id")
mism = [r.tested_hgnc_id for r in chk.itertuples()
        if bool(contradiction(r.tested_hgnc_id, r.term)["contradicts"]) != bool(as_bool(pd.Series([r.contradiction]))[0])]
log(f"contradiction check vs support.tsv real rows: {len(chk)} genes, {len(mism)} mismatches")
assert not mism, mism

# ============================================================================================ 1. S20
cand = PC[as_bool(PC.has_prediction) & as_bool(PC.expressed_design) & as_bool(PC.assessable_design)
          & (PC.support_category == "no_pcal")].copy()
cand["reasons_ok"] = [all(ALLOWED_REASON.match(x) for x in reasons(s)) and bool(reasons(s)) for s in cand.support_reason]
cand["reasons_any"] = [any(ALLOWED_REASON.match(x) for x in reasons(s)) for s in cand.support_reason]
cand = cand.merge(FL[["hgnc_id", "excl43"]], on="hgnc_id", how="left")
cand["excl43"] = as_bool(cand.excl43.fillna(False))
cand = cand.merge(P[["hgnc_id", "v1p_label", "v1p_label_name", "top_size"]], on="hgnc_id", how="left")
cand = cand.sort_values(["zmean", "symbol"], ascending=[False, True]).reset_index(drop=True)


def fill_s20(c: pd.DataFrame, cap: int) -> tuple[list, list]:
    sel, log_rows, n_mito = [], [], 0
    for r in c.itertuples():
        st = "selected"
        if r.excl43:
            st = "excl43"
        else:
            cd = contradiction(r.hgnc_id, r.top_term)
            if cd["contradicts"]:
                st = "contradiction:" + "|".join(cd["incompatible_sources"])
            elif r.family == "mitochondrial" and n_mito >= cap:
                st = "mito_cap"
        if st == "selected":
            sel.append(r.Index)
            n_mito += r.family == "mitochondrial"
        log_rows.append(dict(hgnc_id=r.hgnc_id, symbol=r.symbol, status=st))
        if len(sel) == N_S20:
            break
    return sel, log_rows


strict = cand[cand.reasons_ok]
sel, s20_log = fill_s20(strict, MITO_CAP)
S20 = strict.loc[sel].copy()
S20.insert(0, "rank", range(1, len(S20) + 1))
S20 = S20.merge(pd.DataFrame(s20_log)[["hgnc_id", "status"]], on="hgnc_id", how="left")
S20_LOG = pd.DataFrame(s20_log)
s20_cols = ["rank", "hgnc_id", "symbol", "top_term", "top_term_name", "family", "v1p_label", "v1p_label_name", "zmean",
            "R", "cov_pct", "size_pct", "top_size", "support_reason", "excl43", "low_coverage", "sd_tertile_withinU"]
S20[s20_cols].to_csv(OUT / "s20.tsv", sep="\t", index=False, float_format="%.6g")
S20_LOG.to_csv(OUT / "s20_fill_log.tsv", sep="\t", index=False)
# sensitivities (not used downstream): lenient reason reading (>= 1 allowed reason), mito cap 7
sel_len, _ = fill_s20(cand[cand.reasons_any], MITO_CAP)
sel_7, _ = fill_s20(strict, 7)
sens = dict(
    lenient_reasons_list=cand.loc[sel_len, "symbol"].tolist(),
    lenient_minus_primary=sorted(set(cand.loc[sel_len, "symbol"]) - set(S20.symbol)),
    mito_cap7_list=strict.loc[sel_7, "symbol"].tolist(),
    mito_cap7_minus_primary=sorted(set(strict.loc[sel_7, "symbol"]) - set(S20.symbol)))
log(f"S20: {len(S20)} genes (eligible strict {len(strict)}, lenient {int(cand.reasons_any.sum())}); "
    f"mito {int((S20.family == 'mitochondrial').sum())}; skipped: "
    f"{S20_LOG.status.value_counts().to_dict()}")

# ============================================================================================ 2. extra30
pool = TA[as_bool(TA.has_prediction) & as_bool(TA.expressed_design) & as_bool(TA.assessable_design)
          & (TA.support_category == "in_support") & ~TA.hgnc_id.isin(top_ids)].copy()
pool = pool.sort_values(["p_cal", "symbol"]).reset_index(drop=True)
pool["bin"] = pd.qcut(np.arange(len(pool)), N_BINS, labels=False)
rng = np.random.default_rng(SEED)
per_bin = N_EXTRA // N_BINS
ex_rows = []
for b in range(N_BINS):
    sub = pool[pool.bin == b]
    pick = sorted(rng.choice(len(sub), per_bin, replace=False))
    for i in pick:
        ex_rows.append(sub.iloc[i])
EX = pd.DataFrame(ex_rows).reset_index(drop=True)
binr = pool.groupby("bin").p_cal.agg(["min", "max", "size"])
EX["bin_pcal_min"] = EX.bin.map(binr["min"])
EX["bin_pcal_max"] = EX.bin.map(binr["max"])
EX["bin_n"] = EX.bin.map(binr["size"])
EX = EX.merge(P[["hgnc_id", "v1p_label", "v1p_label_name", "top_size"]], on="hgnc_id", how="left")
ex_cols = ["bin", "bin_pcal_min", "bin_pcal_max", "bin_n", "hgnc_id", "symbol", "p_cal", "top_term", "top_term_name",
           "family", "v1p_label", "v1p_label_name", "top_size", "excl43", "contradiction", "zmean"]
EX[ex_cols].to_csv(OUT / "extra30.tsv", sep="\t", index=False, float_format="%.6g")
log(f"extra30: pool {len(pool)}, bins {binr['size'].tolist()}, sampled {len(EX)}")

# ============================================================================================ 3. hval10
HGn = pd.read_csv(ROOT / "results/holdout/H_genes.tsv", sep="\t", dtype=str, keep_default_na=False)
CA = pd.read_csv(ROOT / "results/holdout/circularity_annotations.tsv", sep="\t", dtype={"hgnc_id": str})
TT = pd.read_csv(ROOT / "results/holdout/H_targets.tsv", sep="\t", dtype=str, keep_default_na=False)
TT = TT.merge(CA[["hgnc_id", "go_id", "any_pmid_flagged"]], on=["hgnc_id", "go_id"], how="left", validate="1:1")
assert TT.any_pmid_flagged.notna().all()
TT = TT[~as_bool(TT.any_pmid_flagged)]
TT = TT[TT.go_id.isin(v2.col)]
TT["size_cur"] = [int(v2.size[v2.col[t]]) for t in TT.go_id]
TT = TT[(TT.size_cur >= LO) & (TT.size_cur <= HI)]
TT = TT[TT.hgnc_id.isin(HGn[~as_bool(HGn.in_U)].hgnc_id)]
elig_h = sorted(TT.hgnc_id.unique())
rng = np.random.default_rng(SEED)
hpick = sorted(rng.choice(len(elig_h), N_HVAL, replace=False))
FAMS = B.load_families()
hv = []
for i in hpick:
    h = elig_h[i]
    t = TT[TT.hgnc_id == h].sort_values(["size_cur", "go_id"]).iloc[0]
    hv.append(dict(hgnc_id=h, symbol=HUB.loc[h, "symbol"], n_eligible_targets=int((TT.hgnc_id == h).sum()),
                   real_term=t.go_id, real_term_name=onto.name(t.go_id), size_cur=int(t.size_cur),
                   family=B.family_of(t.go_id, onto, FAMS), term_size_t0=t.term_size_t0,
                   support_evidence=t.support_evidence, support_pmids=t.support_pmids))
HV = pd.DataFrame(hv)
HV.to_csv(OUT / "hval10.tsv", sep="\t", index=False)
log(f"hval10: eligible H genes {len(elig_h)} (of {len(HGn)}); picked {HV.symbol.tolist()}")

# ============================================================================================ 4. statements
cands = M6.decoy_candidates(P, v2)
donors = (P[as_bool(P.has_prediction)][["hgnc_id", "symbol", "top_term", "v1p_label", "v1p_label_name"]]
          .sort_values("hgnc_id").groupby("top_term"))
APPROVED = set(HUB[(HUB.locus_group == "protein-coding gene")].symbol)
PARTNERS = pd.read_csv(ROOT / "results/ledger/u_partners.tsv", sep="\t", dtype=str, keep_default_na=False,
                       usecols=["hgnc_id", "rank", "partner_symbol"])
PARTNERS = PARTNERS[PARTNERS["rank"].astype(int) <= C.fz("predictions", "ledger_partners_per_gene")]
PART_BY = PARTNERS.groupby("hgnc_id").partner_symbol.apply(set).to_dict()


def is_go(x) -> bool:
    return isinstance(x, str) and x.startswith("GO:")


def nested(a: str, b: str) -> bool:
    return is_go(a) and is_go(b) and (a in onto.ancestors(b) or b in onto.ancestors(a))


def statement(term_name: str, label_name: str) -> str:
    s = f"GENE_X functions in {term_name}"
    lab = clean_label(label_name)
    return s + (f"; module context: {lab}" if lab else "")


def pick_decoys(h: str, pos: int, term: str, fam: str, label: str | None) -> list[dict]:
    col = int(v2.col[term])
    mem = members(term)
    lsz = float(np.log(v2.size[col]))
    anc = onto.ancestors(term)
    c = cands[(cands.family == fam) & (cands.term != term)]
    ok = []
    for r in c.itertuples():
        if r.term in anc or term in onto.ancestors(r.term):
            continue
        u = len(mem | r.members)
        jac = len(mem & r.members) / u if u else 0.0
        if jac >= MAXJ:
            continue
        ok.append((r.Index, jac))
    c = c.loc[[i for i, _ in ok]].copy()
    c["jaccard"] = [j for _, j in ok]
    c["d"] = (c.log_size - lsz).abs()
    c = c.sort_values(["d", "term"], kind="mergesort")
    rng = np.random.default_rng([SEED, pos])
    near = c.head(N_NEAR)
    order = [near.index[i] for i in rng.permutation(len(near))] + list(c.index[N_NEAR:])
    out = []
    for i in order:
        r = c.loc[i]
        if any(nested(r.term, o["term"]) for o in out):
            continue
        dn = donors.get_group(r.term)
        if label:
            dn = dn[dn.v1p_label.astype(str).str.len().gt(0) & (dn.v1p_label != label)
                    & ~dn.v1p_label.map(lambda x: nested(x, term) or nested(x, label))
                    & ~dn.v1p_label.isin([o["label"] for o in out])]
        if not len(dn):
            continue
        d = dn.iloc[int(rng.integers(0, len(dn)))]
        out.append(dict(term=r.term, term_name=onto.name(r.term), family=r.family, size=int(v2.size[int(r.col)]),
                        d_logsize=float(r.d), jaccard=float(r.jaccard), near_rank=int(c.index.get_loc(i)) + 1,
                        donor_hgnc_id=d.hgnc_id, donor_symbol=d.symbol,
                        label=d.v1p_label if label else "", label_name=d.v1p_label_name if label else ""))
        if len(out) == N_DECOY:
            break
    return out


genes = ([dict(hgnc_id=h, set="top40", rank_in_set=i + 1) for i, h in enumerate(top_ids)]
         + [dict(hgnc_id=h, set="S20", rank_in_set=i + 1) for i, h in enumerate(S20.hgnc_id)]
         + [dict(hgnc_id=h, set="extra30", rank_in_set=i + 1) for i, h in enumerate(EX.hgnc_id)]
         + [dict(hgnc_id=h, set="hval10", rank_in_set=i + 1) for i, h in enumerate(HV.hgnc_id)])
G = pd.DataFrame(genes)
assert not G.hgnc_id.duplicated().any(), G[G.hgnc_id.duplicated(keep=False)]
item_order = np.random.default_rng(SEED).permutation(len(G))
G["item_id"] = [f"M7-{k + 1:03d}" for k in np.argsort(item_order)]
HVi = HV.set_index("hgnc_id")

st_rows, key_rows, slot_rows = [], [], []
for g in G.itertuples():
    h = g.hgnc_id
    pos = base.pos[h]
    if g.set == "hval10":
        hr = HVi.loc[h]
        term, fam, label, label_name = hr.real_term, hr.family, "", ""
        term_name = hr.real_term_name
    else:
        pr = Pi.loc[h]
        term, fam, term_name = pr.top_term, pr.family, pr.top_term_name
        label = pr.v1p_label if isinstance(pr.v1p_label, str) and pr.v1p_label else ""
        label_name = pr.v1p_label_name if label else ""
    real = dict(term=term, term_name=term_name, family=fam, size=int(v2.size[v2.col[term]]), d_logsize=0.0,
                jaccard=1.0, near_rank=0, donor_hgnc_id=h, donor_symbol=HUB.loc[h, "symbol"], label=label,
                label_name=label_name)
    dec = pick_decoys(h, pos, term, fam, label or None)
    if len(dec) < N_DECOY:
        log(f"WARNING {HUB.loc[h, 'symbol']}: only {len(dec)} decoys")
    allst = [dict(real, is_real=True)] + [dict(d, is_real=False) for d in dec]
    perm = np.random.default_rng([SEED, pos, 1]).permutation(len(allst))
    red = redactor_for(h)
    parts = PART_BY.get(h, set())
    for k, j in enumerate(perm):
        s = allst[j]
        raw = statement(s["term_name"], s["label_name"])
        txt = red.redact(raw)
        toks = sorted({w for w in re.findall(r"[A-Za-z0-9-]+", txt) if w in APPROVED and len(w) >= 3})
        st_rows.append(dict(item_id=g.item_id, hgnc_id=h, slot=SLOTS[k], statement=txt))
        slot_rows.append(dict(item_id=g.item_id, hgnc_id=h, symbol=HUB.loc[h, "symbol"], set=g.set, slot=SLOTS[k],
                              is_real=s["is_real"], **{x: s[x] for x in ("term", "term_name", "family", "size",
                                                                          "d_logsize", "jaccard", "near_rank",
                                                                          "label", "label_name", "donor_hgnc_id",
                                                                          "donor_symbol")},
                              statement=txt, n_redactions=len(red.hits(raw)),
                              symbol_tokens="|".join(toks), partner_tokens="|".join(t for t in toks if t in parts)))
    key_rows.append(dict(item_id=g.item_id, hgnc_id=h, symbol=HUB.loc[h, "symbol"], set=g.set,
                         rank_in_set=g.rank_in_set, n_statements=len(allst),
                         real_slot=SLOTS[int(np.flatnonzero(perm == 0)[0])]))

ST = pd.DataFrame(st_rows).sort_values(["item_id", "slot"])
KEY = pd.DataFrame(key_rows).sort_values("item_id")
SL = pd.DataFrame(slot_rows).sort_values(["item_id", "slot"])
ST.to_csv(OUT / "statements.tsv", sep="\t", index=False)
KEY.to_csv(OUT / "answer_key.tsv", sep="\t", index=False)
SL.to_csv(OUT / "answer_key_slots.tsv", sep="\t", index=False, float_format="%.4g")
leak = ST.statement.str.contains(r"\bGENE_X\b.*\bGENE_X\b", regex=True).sum()
log(f"statements: {len(KEY)} genes, {len(ST)} statements; real-slot counts {KEY.real_slot.value_counts().to_dict()}; "
    f"statements with a redaction beyond the template subject: {int((SL.n_redactions > 0).sum())}; "
    f"with approved-symbol tokens: {int((SL.symbol_tokens != '').sum())}; with top-10 partner tokens: "
    f"{int((SL.partner_tokens != '').sum())}")

# ============================================================================================ 5. packets, probe list
for h in G.hgnc_id:
    r = HUB.loc[h]
    txt = (f"hgnc_id: {h}\nsymbol: {r.symbol}\nprevious_symbols: {r.prev_symbols.replace('|', ', ')}\n"
           f"alias_symbols: {r.alias_symbols.replace('|', ', ')}\nuniprot_accessions: "
           f"{r.uniprot_ids.replace('|', ', ')}\ncytoband: {r.location}\n")
    (PK / f"{h.replace(':', '_')}.txt").write_text(txt)
pr_ids = G[G.set.isin(["top40", "S20", "extra30"])].hgnc_id.tolist()
PR = HUB.loc[pr_ids, ["symbol", "prev_symbols", "alias_symbols"]].reset_index()
PR = PR.iloc[np.random.default_rng(SEED).permutation(len(PR))]
PR.to_csv(OUT / "probe_list.tsv", sep="\t", index=False)
log(f"packets {len(G)}, probe list {len(PR)}")

# ============================================================================================ manifest
counts = dict(top40=len(top_ids), S20=len(S20), extra30=len(EX), hval10=len(HV), genes=len(G), statements=len(ST),
              packets=len(G), probe=len(PR), s20_eligible_strict=int(len(strict)),
              s20_eligible_lenient=int(cand.reasons_any.sum()), s20_mito=int((S20.family == "mitochondrial").sum()),
              extra30_pool=len(pool), hval10_eligible=len(elig_h),
              genes_with_fewer_than_3_decoys=int((KEY.n_statements < N_DECOY + 1).sum()),
              statements_with_symbol_tokens=int((SL.symbol_tokens != "").sum()),
              statements_with_partner_tokens=int((SL.partner_tokens != "").sum()))
notes = dict(
    relationship_type=("Not included in statements: §4.4 types exist only for the M6 clean-first top 40 "
                       "(results/ledger/top40.tsv; 20/40 primary genes) and for none of S20, extra30, hval10 or the "
                       "decoy donors; a type on the real statement only would unblind the real slot. PI decision."),
    s20_reason_reading="strict: every no-p_cal reason in {family < 30 H genes, zmean/R/cov_pct > P95}",
    s20_mito_cap=f"{MITO_CAP} (frozen tiers.mito_cap_top20_max_count = floor(20/3))",
    hval10_window=f"targets restricted to current base size {LO}-{HI} (V2 candidate window) for size matching",
    decoys=f"random among the {N_NEAR} closest |log size| eligible terms (src/ledger.choose_decoy convention)")
C.write_manifest(OUT / "manifest.json", "scripts/50_m7_prep.py", {}, INPUTS, SEED, T_START,
                 extra=dict(counts=counts, notes=notes, s20_sensitivity=sens,
                            outputs=sorted(str(p.relative_to(ROOT)) for p in OUT.glob("*.tsv"))))
log(f"done: {json.dumps(counts)}")
