"""Independent re-derivation of the M5b temporal hold-out PRIMARY result (verifier; no spec change).

Written from DESIGN.md v2.3 §3.0-§3.3, §3.5, the LOOKS.md f0922e1 spec row and DEVIATIONS.md rows of 2026-10-29/30.
Does NOT import scripts/32-34, scripts/m5b_common.py, src/vocab.py or src/predictor.py. Imports only src/gate.py.

Usage: ./.env/bin/python -I verify/rederive_holdout.py [--variant NAME ...]
Writes verify/holdout_rederived_per_gene.tsv and verify/holdout_rederived_summary.json (primary variant), and prints
comparisons against results/holdout_eval/per_gene_core.tsv.

Implementation choices where the specification is silent (each can be toggled by a variant for diagnosis):
- GAF row -> gene: UniProtKB accession unique in the hub's uniprot_ids; else GAF symbol = unique current HGNC symbol;
  else unique previous symbol. Ambiguous accessions dropped.
- Members: any matrix gene can be a term member (so non-scorable background neighbours can count in S); term sizes
  (candidate window, prior) count scorable genes only.
- GO ids: alt_id -> primary; obsolete -> single replaced_by, else dropped. Rows with aspect P/F; NOT dropped;
  colocalizes_with dropped; contributes_to kept. Propagation over is_a + part_of (current obo), kept terms in BP/MF.
- IPI rule: when query q is scored, every row with evidence IPI whose with/from contains one of q's UniProt
  accessions (hub + accessions of GAF rows mapped to q; isoform suffix stripped) is dropped; per-query term sizes,
  membership, S and prior use the reduced annotation.
- N(q): top 25 background genes by zavg, excluding q, NaN, genes sharing any chromosome arm with q (location parsed,
  "X.. and Y.." = both arms), Ensembl paralogues (all homology types in the Ensembl 116 paralogue file).
- R1: S desc; ties -> more supporting partners, then GO id asc. Reportable = >= 2 annotated neighbours.
- Prior: per-query t0 size desc, ties GO id asc; same candidate set; no reportability rule.
- Circularity: (gene, term) pairs with any flagged PMID removed from T(g) and from all ranked lists for g.
- Null: walk M(g) in order, skip m annotated at t0 (base, propagated) to any term of the FULL T(g); first 5 kept.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import gate  # noqa: E402

D1_CODES = {"EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC"}
K = 25
LO, HI = 5, 200
N_BOOT = 10_000


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- ontology
def parse_obo(path):
    terms = {}
    cur = None
    with open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("["):
                cur = {"alt": [], "isa": [], "partof": [], "obs": False, "repl": [], "ns": None} if line == "[Term]" else None
                if cur is not None:
                    cur["_new"] = True
                continue
            if cur is None or not line:
                continue
            k, _, v = line.partition(": ")
            if k == "id":
                cur["id"] = v
                terms[v] = cur
            elif k == "name":
                cur["name"] = v
            elif k == "alt_id":
                cur["alt"].append(v)
            elif k == "namespace":
                cur["ns"] = v
            elif k == "is_a":
                cur["isa"].append(v.split()[0])
            elif k == "relationship":
                p = v.split()
                if p[0] == "part_of":
                    cur["partof"].append(p[1])
            elif k == "is_obsolete" and v.strip() == "true":
                cur["obs"] = True
            elif k == "replaced_by":
                cur["repl"].append(v.split()[0])
    alt = {}
    for t, d in terms.items():
        for a in d["alt"]:
            alt[a] = t
    return terms, alt


def resolve(go, terms, alt):
    go = alt.get(go, go)
    d = terms.get(go)
    if d is None:
        return None
    if d["obs"]:
        if len(d["repl"]) == 1:
            r = alt.get(d["repl"][0], d["repl"][0])
            if r in terms and not terms[r]["obs"]:
                return r
        return None
    return go


def ancestors_fn(terms):
    memo = {}

    def anc(t):
        if t in memo:
            return memo[t]
        out = {t}
        for p in terms[t]["isa"] + terms[t]["partof"]:
            if p in terms:
                out |= anc(p)
        memo[t] = frozenset(out)
        return memo[t]

    sys.setrecursionlimit(100000)
    return anc


# ---------------------------------------------------------------- arms / paralogues
ARM_RE = re.compile(r"^(\d{1,2}|X|Y)([pq])")


def parse_arms(loc):
    if not isinstance(loc, str) or not loc:
        return frozenset()
    out = set()
    for part in loc.split(" and "):
        part = part.strip()
        m = ARM_RE.match(part)
        if m:
            out.add(m.group(1) + m.group(2))
            # ranges such as 3p21.1-p14.3: all bands seen in this problem stay on the same arm; check anyway
            for seg in part.split("-")[1:]:
                m2 = re.match(r"^(\d{1,2}|X|Y)?([pq])", seg)
                if m2:
                    out.add(m.group(1) + m2.group(2))
    return frozenset(out)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="primary",
                    help="primary | members_scorable_only | nbr_scorable_only | arm_first_only | no_ipi_rule | "
                         "sizes_base | ties_goid | null_skip_none | prior_size_asc")
    ap.add_argument("--no-boot", action="store_true")
    ap.add_argument("--debug", default="", help="comma-separated symbols: print their top-ranked terms and exit")
    ap.add_argument("--outdir", default=str(ROOT / "verify" / "_out"), help="where per-gene tables are written")
    args = ap.parse_args()
    V = args.variant
    VS = set(V.split(","))
    g_info = gate.check()
    log("gate OK", g_info.get("tag_commit", ""))

    genes = pd.read_csv(ROOT / "data/derived/matrices/zavg_full/genes.tsv", sep="\t")
    genes["scorable"] = genes["scorable"].astype(str) == "True"
    n = len(genes)
    hgnc2idx = dict(zip(genes.hgnc_id, genes.matrix_index))
    scorable = genes.scorable.to_numpy()
    bg = genes.bg.to_numpy() == 1
    hub = pd.read_csv(ROOT / "results/ids/hgnc_hub.tsv", sep="\t", dtype=str)
    hubm = hub.set_index("hgnc_id")

    # arms
    arms = [parse_arms(hubm.location.get(h)) for h in genes.hgnc_id]
    if "arm_first_only" in VS:
        arms = []
        for h in genes.hgnc_id:
            loc = hubm.location.get(h)
            a = parse_arms(loc.split(" and ")[0]) if isinstance(loc, str) else frozenset()
            arms.append(a)
    arm_of = defaultdict(set)
    for i, a in enumerate(arms):
        for x in a:
            arm_of[x].add(i)
    log("genes without arm:", sum(1 for a in arms if not a))

    # paralogues (Ensembl 116 file -> hub ENSG -> matrix index)
    ens2idx = defaultdict(set)
    for h, e in zip(hub.hgnc_id, hub.ensembl_gene_id):
        if isinstance(e, str) and h in hgnc2idx:
            ens2idx[e].add(hgnc2idx[h])
    par = defaultdict(set)
    pf = pd.read_csv(ROOT / "data/raw/ensembl/ensembl116_human_paralogues.tsv", sep="\t", dtype=str,
                     usecols=[0, 2])
    pf.columns = ["a", "b"]
    for a, b in zip(pf.a, pf.b):
        if isinstance(b, str):
            for i in ens2idx.get(a, ()):
                for j in ens2idx.get(b, ()):
                    if i != j:
                        par[i].add(j)
                        par[j].add(i)
    # cross-check with the shared paralogue table (diagnostic only)
    z = np.load(ROOT / "data/derived/paralogues_by_matrix_index.npz")
    ptr, ids = z["ptr"], z["ids"]
    npar_diff = sum(1 for i in range(n) if set(ids[ptr[i]:ptr[i + 1]].tolist()) != par.get(i, set()))
    log("paralogue sets differing from shared npz:", npar_diff)

    # ontology
    terms, alt = parse_obo(ROOT / "data/raw/go/current/go-basic.obo")
    anc = ancestors_fn(terms)
    ns_ok = {t for t, d in terms.items() if d["ns"] in ("biological_process", "molecular_function")}

    # accession -> gene
    acc2h = defaultdict(set)
    hub_map = hub[hub.in_universe.astype(str) == "True"] if "universe_only" in VS else hub
    for h, u in zip(hub_map.hgnc_id, hub_map.uniprot_ids):
        if isinstance(u, str):
            for a in u.split("|"):
                acc2h[a.strip()].add(h)
    sym2h = defaultdict(set)
    prev2h = defaultdict(set)
    for h, s, p in zip(hub.hgnc_id, hub.symbol, hub.prev_symbols):
        sym2h[s].add(h)
        if isinstance(p, str):
            for x in re.split(r"[|,]", p):
                if x.strip():
                    prev2h[x.strip()].add(h)

    # t0 GAF
    rows = []  # (gene_idx, go, is_ipi, frozenset(with accessions))
    stats = defaultdict(int)
    gene_accs = defaultdict(set)
    for h, u in zip(hub.hgnc_id, hub.uniprot_ids):
        if isinstance(u, str) and h in hgnc2idx:
            gene_accs[hgnc2idx[h]].update(x.strip() for x in u.split("|"))
    with gzip.open(ROOT / "data/raw/go/archive/2018-07-02/goa_human.gaf.gz", "rt") as fh:
        for line in fh:
            if line.startswith("!"):
                continue
            f = line.rstrip("\n").split("\t")
            if f[0] != "UniProtKB" or f[8] not in ("P", "F"):
                continue
            q = f[3].lower()
            if "not" in q.split("|") or "colocalizes_with" in q:
                continue
            if f[6] not in D1_CODES:
                continue
            stats["rows_d1_PF"] += 1
            acc = f[1].split("-")[0]
            hs = acc2h.get(acc, set())
            if len(hs) > 1 and "acc_all" in VS:
                for h in hs:
                    if h in hgnc2idx:
                        go = resolve(f[4], terms, alt)
                        if go is not None:
                            gi = hgnc2idx[h]
                            gene_accs[gi].add(acc)
                            wf = frozenset(x.split(":", 1)[1].split("-")[0] for x in re.split(r"[|,]", f[7])
                                           if x.startswith("UniProtKB:")) if f[6] == "IPI" else frozenset()
                            rows.append((gi, go, f[6] == "IPI", wf))
                stats["ambiguous_acc_assigned_all"] += 1
                continue
            if len(hs) != 1 and "no_symbol_fallback" in VS:
                stats["unmapped_or_ambiguous"] += 1
                continue
            if len(hs) != 1:
                if len(hs) > 1:
                    stats["ambiguous_acc"] += 1
                    continue
                hs = sym2h.get(f[2], set())
                if len(hs) != 1:
                    hs = prev2h.get(f[2], set())
                if len(hs) != 1:
                    stats["unmapped"] += 1
                    continue
                stats["mapped_by_symbol"] += 1
            h = next(iter(hs))
            if h not in hgnc2idx:
                stats["not_in_matrix"] += 1
                continue
            gi = hgnc2idx[h]
            go = resolve(f[4], terms, alt)
            if go is None:
                stats["obsolete_dropped"] += 1
                continue
            gene_accs[gi].add(acc)
            wf = frozenset(x.split(":", 1)[1].split("-")[0] for x in re.split(r"[|,]", f[7])
                           if x.startswith("UniProtKB:")) if f[6] == "IPI" else frozenset()
            rows.append((gi, go, f[6] == "IPI", wf))
    log("GAF stats:", dict(stats), "rows kept:", len(rows))

    if "members_scorable_only" in VS:
        rows = [r for r in rows if scorable[r[0]]]

    rows_by_gene = defaultdict(list)
    for r in rows:
        rows_by_gene[r[0]].append(r)
    # accession -> list of (gene, row index within gene) for IPI rows
    ipi_by_acc = defaultdict(list)
    for gi, rl in rows_by_gene.items():
        for k, r in enumerate(rl):
            if r[2]:
                for a in r[3]:
                    ipi_by_acc[a].append((gi, k))

    def propagate(rl, drop=frozenset()):
        out = set()
        for k, r in enumerate(rl):
            if k in drop:
                continue
            out |= anc(r[1])
        return frozenset(out & ns_ok)

    mem = {gi: propagate(rl) for gi, rl in rows_by_gene.items()}
    base_size = defaultdict(int)
    for gi, ts in mem.items():
        if scorable[gi]:
            for t in ts:
                base_size[t] += 1
    n_annot_scorable = sum(1 for gi, ts in mem.items() if scorable[gi] and ts)
    base_cands = {t for t, s in base_size.items() if LO <= s <= HI}
    log("annotated scorable genes at t0:", n_annot_scorable, "base candidates:", len(base_cands),
        "terms with >=1 member:", len(base_size))

    def query_annotation(q):
        """Returns (membership override dict gi -> termset, per-query size dict) after the IPI rule for q."""
        if "no_ipi_rule" in VS:
            return {}, base_size
        drops = defaultdict(set)
        for a in gene_accs.get(q, ()):
            for gi, k in ipi_by_acc.get(a, ()):
                drops[gi].add(k)
        if not drops:
            return {}, base_size
        override = {}
        size = dict(base_size)
        for gi, ks in drops.items():
            new = propagate(rows_by_gene[gi], frozenset(ks))
            override[gi] = new
            if scorable[gi] and "sizes_base" not in VS:
                for t in mem[gi] - new:
                    size[t] -= 1
        return override, size

    Z = np.load(ROOT / "data/derived/matrices/zavg_full/zavg_BEF.npy", mmap_mode="r")
    nb_ok = bg & scorable if "nbr_scorable_only" in VS else bg

    nbr_cache = {}

    def neighbours(q):
        if q in nbr_cache:
            return nbr_cache[q]
        r = np.array(Z[q], dtype=np.float64)
        r[~np.isfinite(r)] = -np.inf
        r[~nb_ok] = -np.inf
        r[q] = -np.inf
        excl = set(par.get(q, ()))
        for a in arms[q]:
            excl |= arm_of[a]
        if excl:
            r[list(excl)] = -np.inf
        o = np.argsort(-r, kind="stable")[:K]
        assert np.all(np.isfinite(r[o]))
        nbr_cache[q] = (o, r[o])
        return nbr_cache[q]

    rank_cache = {}

    def ranked(q, dbg=False):
        """R1 ranked reportable candidate list and prior list for query q (no circularity removal yet)."""
        if q in rank_cache:
            return rank_cache[q]
        override, size = query_annotation(q)
        nb, zz = neighbours(q)
        S = defaultdict(float)
        sup = defaultdict(int)
        for j, zj in zip(nb, zz):
            ts = override.get(j, mem.get(j, frozenset()))
            for t in ts:
                S[t] += max(zj, 0.0)
                if zj > 0 or "sup_zpos" not in VS:
                    sup[t] += 1
        cand = {t for t, s in size.items() if LO <= s <= HI}
        rep = [t for t in S if t in cand and sup[t] >= 2]
        if "ties_goid_desc" in VS:
            rep.sort(key=lambda t: t, reverse=True)
            rep.sort(key=lambda t: (-S[t], -sup[t]))
        elif "ties_goid" in VS:
            rep.sort(key=lambda t: (-S[t], t))
        else:
            rep.sort(key=lambda t: (-S[t], -sup[t], t))
        if "prior_size_asc" in VS:
            prior = sorted(cand, key=lambda t: (-size[t], -int(t[3:])))
        else:
            prior = sorted(cand, key=lambda t: (-size[t], t))
        if dbg:
            for t in rep[:8]:
                log(genes.symbol[q], t, terms[t].get("name", ""), round(S[t], 4), sup[t], size[t])
            members = {t: [genes.symbol[j] for j in nb if t in override.get(j, mem.get(j, frozenset()))] for t in rep[:3]}
            log(members)
        out = {"r1": rep, "S": {t: S[t] for t in rep[:5]}, "prior": prior[:200], "size": size,
               "tie_top": len(rep) > 1 and abs(S[rep[0]] - S[rep[1]]) < 1e-9}
        rank_cache[q] = out
        return out

    def first_not(lst, excl):
        for t in lst:
            if t not in excl:
                return t
        return None

    # H, targets, circularity
    Hg = pd.read_csv(ROOT / "results/holdout/H_genes.tsv", sep="\t")
    Ht = pd.read_csv(ROOT / "results/holdout/H_targets.tsv", sep="\t", dtype={"support_pmids": str})
    ca = pd.read_csv(ROOT / "results/holdout/circularity_annotations.tsv", sep="\t")
    flagged = set(zip(ca.hgnc_id[ca.any_pmid_flagged], ca.go_id[ca.any_pmid_flagged]))
    T_full = Ht.groupby("hgnc_id").go_id.apply(set).to_dict()
    log("|H| =", len(Hg), "pairs =", len(Ht), "flagged pairs =", len(flagged))

    # PMID-only clusters over all H genes (union-find on shared supporting PMIDs)
    parent = {h: h for h in Hg.hgnc_id}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pm2g = defaultdict(set)
    for h, p in zip(Ht.hgnc_id, Ht.support_pmids):
        if isinstance(p, str):
            for x in re.split(r"[|;,]", p):
                if x.strip():
                    pm2g[x.strip()].add(h)
    for gs in pm2g.values():
        gs = list(gs)
        for x in gs[1:]:
            ra, rb = find(gs[0]), find(x)
            if ra != rb:
                parent[ra] = rb
    clus = {h: find(h) for h in Hg.hgnc_id}

    M = np.load(ROOT / "data/derived/matched/matched_lists.npz")
    mrow = {int(q): i for i, q in enumerate(M["queries"])}
    Mids = M["ids"]

    if args.debug:
        for sy in args.debug.split(","):
            ranked(int(genes.index[genes.symbol == sy][0]), dbg=True)
        return
    recs = []
    for h in Hg.hgnc_id:
        q = hgnc2idx[h]
        Tf = T_full.get(h, set())
        fl = {t for t in Tf if (h, t) in flagged}
        T = Tf - fl
        rk = ranked(q)
        top = first_not(rk["r1"], fl)
        ptop = first_not(rk["prior"], fl)
        # matched null
        used, skipped, nh = [], 0, []
        for m in Mids[mrow[q]]:
            m = int(m)
            if "null_skip_none" not in VS and (mem.get(m, frozenset()) & Tf):
                skipped += 1
                continue
            used.append(m)
            mt = first_not(ranked(m)["r1"], fl)
            nh.append(1.0 if (mt is not None and mt in T) else 0.0)
            if len(used) == 5:
                break
        recs.append(dict(hgnc_id=h, symbol=genes.symbol[q], n_T=len(T), n_flag=len(fl),
                         top1_zavg=top or "", hit1_zavg=int(top in T) if top else 0,
                         S_top=rk["S"].get(top, np.nan) if top else np.nan, tie_top=rk["tie_top"],
                         top1_prior=ptop or "", hit1_prior=int(ptop in T) if ptop else 0,
                         hit1_null=float(np.mean(nh)), null_matches=";".join(genes.hgnc_id[u] for u in used),
                         null_skipped=skipped, cluster=clus[h],
                         nbrs=";".join(genes.symbol[j] for j in neighbours(q)[0])))
    R = pd.DataFrame(recs)
    P = R[R.n_T > 0].reset_index(drop=True)
    log("primary H:", len(P), "of", len(R))
    res = {"variant": V, "n_H": len(R), "n_primary": len(P), "coverage_zavg": float((P.top1_zavg != "").mean()),
           "p1_zavg": float(P.hit1_zavg.mean()), "p1_prior": float(P.hit1_prior.mean()),
           "p1_null": float(P.hit1_null.mean()), "n_hits_zavg": int(P.hit1_zavg.sum()),
           "n_tie_top": int(R.tie_top.sum())}
    res["d_prior"] = res["p1_zavg"] - res["p1_prior"]
    res["d_null"] = res["p1_zavg"] - res["p1_null"]

    # cross-check clusters with H_genes.tsv pmid_cluster
    lab = dict(zip(Hg.hgnc_id, Hg.pmid_cluster))
    same = pd.crosstab(pd.Series([clus[h] for h in Hg.hgnc_id]), pd.Series([lab[h] for h in Hg.hgnc_id]))
    res["clusters_identical_to_H_genes_pmid_cluster"] = bool(((same > 0).sum(axis=1) == 1).all()
                                                             and ((same > 0).sum(axis=0) == 1).all())
    res["n_clusters_primary"] = int(P.cluster.nunique())

    if not args.no_boot:
        cl = P.cluster.astype("category").cat.codes.to_numpy()
        nc = cl.max() + 1
        da = P.hit1_zavg.to_numpy() - P.hit1_prior.to_numpy()
        dn = P.hit1_zavg.to_numpy() - P.hit1_null.to_numpy()
        sa = np.bincount(cl, weights=da, minlength=nc)
        sn = np.bincount(cl, weights=dn, minlength=nc)
        cnt = np.bincount(cl, minlength=nc).astype(float)
        rng = np.random.default_rng(0)
        ba, bn = np.empty(N_BOOT), np.empty(N_BOOT)
        for b in range(N_BOOT):
            w = np.bincount(rng.integers(0, nc, nc), minlength=nc)
            den = w @ cnt
            ba[b] = (w @ sa) / den
            bn[b] = (w @ sn) / den
        res["ci_d_prior"] = [float(x) for x in np.percentile(ba, [2.5, 97.5])]
        res["ci_d_null"] = [float(x) for x in np.percentile(bn, [2.5, 97.5])]
        res["IUT_pass"] = bool(res["ci_d_prior"][0] > 0 and res["ci_d_null"][0] > 0)

    # compare with the M5b per-gene table
    theirs = pd.read_csv(ROOT / "results/holdout_eval/per_gene_core.tsv", sep="\t", dtype={"top1_zavg": str})
    C = P.merge(theirs[["hgnc_id", "hit1_zavg", "top1_zavg", "hit1_prior", "top1_prior", "hit1_null",
                        "null_matches"]], on="hgnc_id", suffixes=("", "_m5b"), how="outer", indicator=True)
    res["merge"] = C._merge.value_counts().to_dict()
    C = C[C._merge == "both"].copy()
    C["top1_zavg_m5b"] = C.top1_zavg_m5b.fillna("")
    C["top1_prior_m5b"] = C.top1_prior_m5b.fillna("")
    res["agree_hit1_zavg"] = float((C.hit1_zavg == C.hit1_zavg_m5b).mean())
    res["agree_top1_zavg"] = float((C.top1_zavg == C.top1_zavg_m5b).mean())
    res["agree_hit1_prior"] = float((C.hit1_prior == C.hit1_prior_m5b).mean())
    res["agree_top1_prior"] = float((C.top1_prior == C.top1_prior_m5b).mean())
    res["agree_hit1_null"] = float((np.abs(C.hit1_null - C.hit1_null_m5b) < 1e-9).mean())
    res["agree_null_matches"] = float((C.null_matches.fillna("") == C.null_matches_m5b.fillna("")).mean())
    disc = C[(C.hit1_zavg != C.hit1_zavg_m5b) | (C.top1_zavg != C.top1_zavg_m5b)]
    res["n_discordant_top1_zavg"] = int(len(disc))
    res["discordant_hit1_zavg"] = C[C.hit1_zavg != C.hit1_zavg_m5b][["symbol", "hit1_zavg", "hit1_zavg_m5b",
                                                                       "top1_zavg", "top1_zavg_m5b"]].to_dict("records")
    log(json.dumps({k: v for k, v in res.items() if k != "discordant_hit1_zavg"}, indent=1, default=str))
    log("discordant hit@1 genes:", res["discordant_hit1_zavg"])
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    tag = "" if V == "primary" else "_" + V.replace(",", "+")
    R.to_csv(out / f"holdout_rederived_per_gene{tag}.tsv", sep="\t", index=False)
    disc.to_csv(out / f"holdout_discordant_top1{tag}.tsv", sep="\t", index=False)
    (out / f"holdout_rederived_summary{tag}.json").write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
