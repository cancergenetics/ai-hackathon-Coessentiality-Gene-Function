"""Independent re-derivation of U (DESIGN.md §1.2) and the temporal hold-out H (§3.0, §3.2.2).

Written from the spec and raw files only (does NOT import src/knownness.py, src/hgnc_hub.py or scripts/02-05).
Run: ./.env/bin/python -I verify/rederive_prereg.py   (from the project root)
Outputs (all under verify/): rederived_U.tsv, rederived_H_genes.tsv, rederived_H_targets.tsv, rederive_summary.json
"""
import gzip
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verify"
RAW = ROOT / "data" / "raw"

D1_CODES = {"EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC"}
GENERIC7 = {"GO:0005515", "GO:0005488", "GO:0042802", "GO:0042803",
            "GO:0003674", "GO:0008150", "GO:0005575"}
# The longer list documented in preregistration/CRITERIA.md (used only for the requested comparison)
GENERIC22 = GENERIC7 | {"GO:0046982", "GO:0019899", "GO:0044877", "GO:0003824", "GO:0043167", "GO:0043168",
                        "GO:0043169", "GO:0097159", "GO:1901363", "GO:0036094", "GO:0009987", "GO:0008152",
                        "GO:0065007", "GO:0050789", "GO:0050794"}
TDL_RANK = {"Tdark": 0, "Tbio": 1, "Tchem": 2, "Tclin": 3}


# ---------------------------------------------------------------- readers
def read_hgnc():
    rows = []
    with open(RAW / "hgnc" / "hgnc_complete_set.txt", encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in fh:
            f = line.rstrip("\n").split("\t")
            f += [""] * (len(hdr) - len(f))
            rows.append({k: f[ix[k]].strip().strip('"') for k in
                         ("hgnc_id", "symbol", "status", "locus_group", "entrez_id", "uniprot_ids")})
    return rows


def read_obo(path):
    terms = {}
    cur = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("["):
                cur = {"alt": [], "isa": [], "partof": [], "obs": False, "repl": [], "ns": None, "name": ""} \
                    if line == "[Term]" else None
                continue
            if cur is None or ": " not in line:
                continue
            k, v = line.split(": ", 1)
            if k == "id":
                terms[v] = cur
                cur["id"] = v
            elif k == "name":
                cur["name"] = v
            elif k == "namespace":
                cur["ns"] = v
            elif k == "alt_id":
                cur["alt"].append(v)
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
    alt = {a: t for t, d in terms.items() for a in d["alt"]}
    return terms, alt


def resolver(terms, alt):
    """Map a GO id to a live primary id of this obo, or None (obsolete without single replacement / unknown)."""
    cache = {}

    def res(g):
        if g in cache:
            return cache[g]
        x = alt.get(g, g)
        out = None
        for _ in range(5):
            d = terms.get(x)
            if d is None:
                break
            if not d["obs"]:
                out = x
                break
            if len(d["repl"]) == 1:
                x = alt.get(d["repl"][0], d["repl"][0])
                continue
            break
        cache[g] = out
        return out
    return res


def ancestors_fn(terms):
    cache = {}

    def anc(t):
        if t in cache:
            return cache[t]
        seen = {t}
        stack = [t]
        while stack:
            x = stack.pop()
            d = terms.get(x)
            if not d:
                continue
            for p in d["isa"] + d["partof"]:
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        cache[t] = frozenset(seen)
        return cache[t]
    return anc


def read_gaf_d1rows(path):
    """Yield (acc, go, evidence, qualifier, aspect, reference) for UniProtKB BP/MF rows with D1 codes, NOT removed.
    Also returns counts."""
    out = []
    n = {"rows": 0, "not": 0, "nonuniprot": 0}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("!"):
                continue
            f = line.rstrip("\n").split("\t")
            n["rows"] += 1
            qual = [q.strip().upper() for q in f[3].split("|") if q.strip()]
            if "NOT" in qual:
                n["not"] += 1
                continue
            if f[8] not in ("P", "F") or f[6] not in D1_CODES:
                continue
            if f[0] != "UniProtKB":
                n["nonuniprot"] += 1
                continue
            if "COLOCALIZES_WITH" in qual:
                continue
            acc = f[1].split("-")[0]
            out.append((acc, f[4], f[6], f[3], f[8], f[5], f[2]))
    return out, n


# ---------------------------------------------------------------- build
def main():
    hg = read_hgnc()
    univ = [r for r in hg if r["status"] == "Approved" and r["locus_group"] == "protein-coding gene"]
    U_ids = [r["hgnc_id"] for r in univ]
    info = {r["hgnc_id"]: r for r in univ}
    print("universe", len(univ))

    # accession -> genes (HGNC uniprot_ids), plus Swiss-Prot entries whose HGNC xref names a universe gene
    acc2g = defaultdict(set)
    for r in univ:
        for a in r["uniprot_ids"].split("|"):
            if a:
                acc2g[a].add(r["hgnc_id"])
    acc2g_hgnc_only = {a: set(s) for a, s in acc2g.items()}

    # UniProt reviewed
    up_entries = []
    with open(RAW / "uniprot" / "uniprot_human_reviewed.tsv", encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in fh:
            f = line.rstrip("\n").split("\t")
            hx = [h.strip() for h in f[ix["HGNC"]].split(";") if h.strip()]
            up_entries.append((f[ix["Entry"]], float(f[ix["Annotation"]]) if f[ix["Annotation"]] else None, hx))
    n_added = 0
    for acc, sc, hx in up_entries:
        for h in hx:
            if h in info and h not in acc2g[acc]:
                acc2g[acc].add(h)
                n_added += 1
    print("accessions added from UniProt HGNC xref:", n_added)

    # ---- D1 (current)
    obo_cur, alt_cur = read_obo(RAW / "go" / "current" / "go-basic.obo")
    res_cur = resolver(obo_cur, alt_cur)
    rows_cur, ncur = read_gaf_d1rows(RAW / "go" / "current" / "goa_human.gaf.gz")
    print("current GAF", ncur, "d1 rows", len(rows_cur))

    def d1_terms(rows, res, a2g):
        """gene -> {resolved GO id: [rows]} for D1-evidence rows."""
        g2t = defaultdict(lambda: defaultdict(list))
        unm = 0
        for row in rows:
            gs = a2g.get(row[0])
            if not gs:
                unm += 1
                continue
            t = res(row[1])
            if t is None:
                continue
            for g in gs:
                g2t[g][t].append(row)
        return g2t, unm

    g2t_cur, unm_cur = d1_terms(rows_cur, res_cur, acc2g)
    g2t_cur_h, _ = d1_terms(rows_cur, res_cur, acc2g_hgnc_only)
    print("current unmapped d1 rows", unm_cur)

    def d1(g2t, generic, ids):
        return {g: not any(t not in generic for t in g2t.get(g, {})) for g in ids}

    D1 = d1(g2t_cur, GENERIC7, U_ids)
    D1_22 = d1(g2t_cur, GENERIC22, U_ids)
    D1_hgnconly = d1(g2t_cur_h, GENERIC7, U_ids)

    # ---- D2
    g_score = {}
    for acc, sc, hx in up_entries:
        gs = [h for h in hx if h in info] or list(acc2g_hgnc_only.get(acc, []))
        for g in gs:
            if sc is not None:
                g_score[g] = max(g_score.get(g, -1), sc)
    D2 = {g: (g in g_score and g_score[g] <= 2) for g in U_ids}

    # ---- D3
    pm2genes = defaultdict(set)
    gene2pm = defaultdict(set)
    with open(RAW / "ncbi_gene" / "gene2pubmed_9606.tsv") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            tax, gid, pm = line.rstrip("\n").split("\t")[:3]
            if tax != "9606":
                continue
            pm2genes[pm].add(gid)
            gene2pm[gid].add(pm)
    focused = {pm for pm, s in pm2genes.items() if len(s) <= 10}
    tdl = {}
    with open(RAW / "tcrd" / "PharosTCRD_UniProt_Mapping.tsv") as fh:
        fh.readline()
        for line in fh:
            f = line.rstrip("\n").split("\t")
            tdl[f[0]] = f[2]
    g_tdl, g_anytdark = {}, {}
    g_accs = defaultdict(set)
    for a, s in acc2g.items():
        for g in s:
            g_accs[g].add(a)
    for g in U_ids:
        ts = [tdl[a] for a in g_accs[g] if a in tdl]
        g_tdl[g] = max(ts, key=TDL_RANK.get) if ts else ""
        g_anytdark[g] = "Tdark" in ts
    npm_foc = {g: len(gene2pm.get(info[g]["entrez_id"], set()) & focused) for g in U_ids}
    npm_all = {g: len(gene2pm.get(info[g]["entrez_id"], set())) for g in U_ids}
    D3pm = {g: npm_foc[g] <= 10 for g in U_ids}
    D3td = {g: g_tdl[g] == "Tdark" for g in U_ids}
    D3 = {g: D3pm[g] or D3td[g] for g in U_ids}

    U = {g for g in U_ids if D1[g] and (D2[g] or D3[g])}
    U22 = {g for g in U_ids if D1_22[g] and (D2[g] or D3[g])}
    U_anytd = {g for g in U_ids if D1[g] and (D2[g] or D3pm[g] or g_anytdark[g])}
    U_hgnconly = {g for g in U_ids if D1_hgnconly[g] and (D2[g] or D3[g])}

    # ---- DepMap (header only) + scorable (tool rule: accession maps uniquely, among DepMap Entrez ids, to gene)
    with open(RAW / "depmap" / "CRISPRGeneEffect.csv") as fh:
        cols = fh.readline().rstrip("\n").split(",")[1:]
    dep_entrez = {}
    for c in cols:
        c = c.strip().strip('"')
        if c.endswith(")") and " (" in c:
            dep_entrez[c.rsplit(" (", 1)[1][:-1]] = c
    cand = defaultdict(set)  # tool rule uses all HGNC rows with entrez & uniprot
    for r in hg:
        if r["entrez_id"] and r["uniprot_ids"]:
            for a in r["uniprot_ids"].split("|"):
                if a:
                    cand[a].add(r["entrez_id"])
    in_dep = {g: info[g]["entrez_id"] in dep_entrez for g in U_ids}
    scorable = {}
    for g in U_ids:
        e = info[g]["entrez_id"]
        ok = False
        if e in dep_entrez:
            for a in info[g]["uniprot_ids"].split("|"):
                if a and [x for x in cand[a] if x in dep_entrez] == [e]:
                    ok = True
        scorable[g] = ok
    n_scorable = sum(scorable.values())
    print("|U|", len(U), "|U&DepMap|", sum(in_dep[g] for g in U), "|U scorable|", sum(scorable[g] for g in U))

    # ---- H
    obo_t0, alt_t0 = read_obo(RAW / "go" / "archive" / "2018-07-02" / "go-basic.obo")
    res_t0 = resolver(obo_t0, alt_t0)
    rows_t0, nt0 = read_gaf_d1rows(RAW / "go" / "archive" / "2018-07-02" / "goa_human.gaf.gz")
    g2t_t0own, _ = d1_terms(rows_t0, res_t0, acc2g)          # D1 at t0: t0 obo
    D1_t0 = d1(g2t_t0own, GENERIC7, U_ids)
    D1_t0_22 = d1(g2t_t0own, GENERIC22, U_ids)
    cutoff = None
    with open(ROOT / "results" / "preregistration" / "pmid_date_cutoffs.tsv") as fh:
        fh.readline()
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if f[0].startswith("2018-07"):
                cutoff = int(f[1])
    print("PMID cut-off", cutoff)
    npm_t0 = {g: sum(1 for p in gene2pm.get(info[g]["entrez_id"], set()) & focused if int(p) < cutoff)
              for g in U_ids}

    # membership: current rows / t0 rows both resolved into the CURRENT obo, propagated with current obo
    anc = ancestors_fn(obo_cur)
    g2t_t0cur, _ = d1_terms(rows_t0, res_cur, acc2g)
    n_obs_drop = sum(1 for r in rows_t0 if res_cur(r[1]) is None)

    def propagate(g2t):
        out = {}
        for g, ts in g2t.items():
            s = set()
            for t in ts:
                s |= anc(t)
            out[g] = {t for t in s if obo_cur.get(t, {}).get("ns") in ("biological_process", "molecular_function")}
        return out
    prop_cur = propagate(g2t_cur)
    prop_t0 = propagate(g2t_t0cur)
    size_t0 = defaultdict(int)
    for g, s in prop_t0.items():
        if scorable.get(g):
            for t in s:
                size_t0[t] += 1
    cands = {g for g in U_ids if scorable[g] and D1_t0[g] and npm_t0[g] <= 10}
    H_targets = {}
    for g in cands:
        T = {t for t in prop_cur.get(g, set()) - prop_t0.get(g, set())
             if t not in GENERIC7 and 5 <= size_t0.get(t, 0) <= 200}
        if T:
            H_targets[g] = T
    # alt: generic direct annotations NOT propagated, generic22 removed from targets
    def strip(g2t, generic):
        return {g: {t: r for t, r in ts.items() if t not in generic} for g, ts in g2t.items()}
    prop_cur_ng = propagate(strip(g2t_cur, GENERIC7))
    prop_t0_ng = propagate(strip(g2t_t0cur, GENERIC7))

    print("|H|", len(H_targets), "targets", sum(len(v) for v in H_targets.values()))

    # ---- write
    OUT.mkdir(exist_ok=True)
    with open(OUT / "rederived_U.tsv", "w") as fh:
        fh.write("hgnc_id\tsymbol\tentrez_id\tD1\tn_inf\tD1_22\tD2\tannotation_score\tD3\tn_pubmed_focused"
                 "\tn_pubmed_all\ttdl\tany_tdark\tin_U\tin_U22\tin_depmap\tscorable\tD1_t0\tn_pm_focused_t0\n")
        for g in U_ids:
            fh.write("\t".join(map(str, [g, info[g]["symbol"], info[g]["entrez_id"], D1[g],
                                          sum(1 for t in g2t_cur.get(g, {}) if t not in GENERIC7), D1_22[g],
                                          D2[g], g_score.get(g, ""), D3[g], npm_foc[g], npm_all[g], g_tdl[g],
                                          g_anytdark[g], g in U, g in U22, in_dep[g], scorable[g], D1_t0[g],
                                          npm_t0[g]])) + "\n")
    with open(OUT / "rederived_H_targets.tsv", "w") as fh:
        fh.write("hgnc_id\tsymbol\tgo_id\tterm_size_t0\n")
        for g in sorted(H_targets):
            for t in sorted(H_targets[g]):
                fh.write(f"{g}\t{info[g]['symbol']}\t{t}\t{size_t0[t]}\n")

    # ---- compare with produced files
    def read_tsv(p):
        with open(p) as fh:
            hdr = fh.readline().rstrip("\n").split("\t")
            return [dict(zip(hdr, l.rstrip("\n").split("\t"))) for l in fh]
    pU = {r["hgnc_id"]: r for r in read_tsv(ROOT / "preregistration" / "uncharacterised_genes.tsv")}
    pHg = {r["hgnc_id"]: r for r in read_tsv(ROOT / "results" / "holdout" / "H_genes.tsv")}
    pHt = defaultdict(set)
    for r in read_tsv(ROOT / "results" / "holdout" / "H_targets.tsv"):
        pHt[r["hgnc_id"]].add(r["go_id"])

    def diag_U(g):
        return dict(sym=info[g]["symbol"], D1=D1[g], D1_22=D1_22[g], D1_hgnconly=D1_hgnconly[g], D2=D2[g],
                    score=g_score.get(g), D3pm=D3pm[g], npm=npm_foc[g], tdl=g_tdl[g], anytdark=g_anytdark[g],
                    inf_terms=sorted(t for t in g2t_cur.get(g, {}) if t not in GENERIC7)[:5],
                    produced=pU.get(g, {}) and {k: pU[g][k] for k in ("D1", "n_d1_terms_informative", "D2",
                                                                      "annotation_score", "D3", "n_pubmed_focused", "tdl")})
    summ = {
        "universe": len(U_ids), "U": len(U), "U_depmap": sum(in_dep[g] for g in U),
        "U_scorable": sum(scorable[g] for g in U), "n_scorable_universe": n_scorable,
        "D1": sum(D1.values()), "D1_22": sum(D1_22.values()), "D2": sum(D2.values()), "D3": sum(D3.values()),
        "D3_pubmed": sum(D3pm.values()), "D3_tdark": sum(D3td.values()),
        "U22": len(U22), "U7_minus_U22": len(U - U22), "U22_minus_U7": len(U22 - U),
        "U_anytdark": len(U_anytd), "U_hgnconly_map": len(U_hgnconly),
        "produced_U": len(pU), "U_minus_produced": sorted(U - set(pU)), "produced_minus_U": sorted(set(pU) - U),
        "U22_minus_produced": sorted(U22 - set(pU)), "produced_minus_U22": sorted(set(pU) - U22),
        "D1_t0": sum(D1_t0.values()), "D1_t0_22": sum(D1_t0_22.values()), "H_candidates": len(cands),
        "H": len(H_targets), "H_pairs": sum(len(v) for v in H_targets.values()),
        "t0_rows_obsolete_dropped_currentobo": n_obs_drop,
        "produced_H": len(pHg), "produced_H_pairs": sum(len(v) for v in pHt.values()),
        "H_minus_produced": sorted(set(H_targets) - set(pHg)), "produced_minus_H": sorted(set(pHg) - set(H_targets)),
        "H_and_U": len(set(H_targets) & U),
    }
    common = set(H_targets) & set(pHt)
    pair_mine = {(g, t) for g in common for t in H_targets[g]}
    pair_prod = {(g, t) for g in common for t in pHt[g]}
    summ["pairs_common_genes_mine_only"] = len(pair_mine - pair_prod)
    summ["pairs_common_genes_prod_only"] = len(pair_prod - pair_mine)
    summ["genes_with_identical_targets"] = sum(1 for g in common if H_targets[g] == pHt[g])
    summ["examples_pair_mine_only"] = sorted(pair_mine - pair_prod)[:15]
    summ["examples_pair_prod_only"] = sorted(pair_prod - pair_mine)[:15]
    summ["diag_U"] = {g: diag_U(g) for g in sorted((U ^ set(pU)))[:40]}
    summ["diag_U22"] = {g: diag_U(g) for g in sorted((U22 ^ set(pU)))[:40]}

    # H diagnostics for set differences
    def diag_H(g):
        mineT = H_targets.get(g, set())
        rawT = {t for t in prop_cur.get(g, set()) - prop_t0.get(g, set()) if t not in GENERIC7}
        ngT = {t for t in prop_cur_ng.get(g, set()) - prop_t0_ng.get(g, set()) if t not in GENERIC22}
        return dict(sym=info[g]["symbol"], scorable=scorable[g], D1_t0=D1_t0[g], D1_t0_22=D1_t0_22[g],
                    npm_t0=npm_t0[g], n_mine_targets=len(mineT), n_prod_targets=len(pHt.get(g, ())),
                    new_terms_sizes=sorted((t, size_t0.get(t, 0)) for t in rawT)[:8],
                    new_terms_nogeneric_prop=sorted((t, size_t0.get(t, 0)) for t in ngT)[:8],
                    t0_inf_terms=sorted(t for t in g2t_t0own.get(g, {}) if t not in GENERIC7)[:5],
                    prod_targets=sorted(pHt.get(g, ()))[:8])
    summ["diag_H"] = {g: diag_H(g) for g in (summ["H_minus_produced"] + summ["produced_minus_H"])[:40]}

    # ---- evidence samples (seed 0)
    rng = random.Random(0)
    Us = sorted(U)
    nonU = sorted(set(U_ids) - U)
    samp = {"U": rng.sample(Us, 10), "nonU": rng.sample(nonU, 10)}
    ev = {}
    for k, gs in samp.items():
        for g in gs:
            rows = []
            for t, rr in sorted(g2t_cur.get(g, {}).items()):
                for r in rr[:2]:
                    rows.append(dict(go=t, name=obo_cur[t]["name"], generic=t in GENERIC7, acc=r[0], ev=r[2],
                                     qual=r[3], aspect=r[4], ref=r[5]))
            ev[g] = dict(set=k, sym=info[g]["symbol"], D1=D1[g], D2=D2[g], score=g_score.get(g), D3=D3[g],
                         npm=npm_foc[g], tdl=g_tdl[g], inU_produced=g in pU,
                         n_inf=sum(1 for t in g2t_cur.get(g, {}) if t not in GENERIC7),
                         rows=[x for x in rows if not x["generic"]][:4] + [x for x in rows if x["generic"]][:3])
    summ["evidence_samples"] = ev

    # ---- 22-term variant (what the produced files claim to use): U22 counts, per-gene column agreement, H22
    summ["U22_depmap"] = sum(in_dep[g] for g in U22)
    summ["U22_scorable"] = sum(scorable[g] for g in U22)
    mism = defaultdict(list)
    for g in U22 & set(pU):
        p = pU[g]
        chk = {"D2": (str(D2[g]), p["D2"]), "D3": (str(D3[g]), p["D3"]),
               "n_pubmed_focused": (str(npm_foc[g]), p["n_pubmed_focused"]),
               "n_pubmed_all": (str(npm_all[g]), p["n_pubmed_all"]), "tdl": (g_tdl[g], p["tdl"]),
               "annotation_score": ("" if g not in g_score else str(int(g_score[g])), p["annotation_score"]),
               "in_depmap": (str(in_dep[g]), p["in_depmap"]), "scorable": (str(scorable[g]), p["scorable"])}
        for k, (a, b) in chk.items():
            if a != b:
                mism[k].append((g, info[g]["symbol"], a, b))
    summ["U22_column_mismatches"] = {k: v[:20] for k, v in mism.items()}
    summ["U22_column_mismatch_counts"] = {k: len(v) for k, v in mism.items()}
    cands22 = {g for g in U_ids if scorable[g] and D1_t0_22[g] and npm_t0[g] <= 10}
    H22 = {}
    for g in cands22:
        T = {t for t in prop_cur.get(g, set()) - prop_t0.get(g, set())
             if t not in GENERIC22 and 5 <= size_t0.get(t, 0) <= 200}
        if T:
            H22[g] = T
    summ["H22_candidates"] = len(cands22)
    summ["H22"] = len(H22)
    summ["H22_pairs"] = sum(len(v) for v in H22.values())
    summ["H22_minus_produced"] = sorted(set(H22) - set(pHg))
    summ["produced_minus_H22"] = sorted(set(pHg) - set(H22))
    summ["H22_pairs_symdiff"] = len({(g, t) for g in H22 for t in H22[g]} ^ {(g, t) for g in pHt for t in pHt[g]})
    summ["H22_and_U22"] = len(set(H22) & U22)
    # per-gene H columns
    hm = defaultdict(list)
    for g in set(H22) & set(pHg):
        p = pHg[g]
        for k, a in (("n_pubmed_focused_before_cutoff", str(npm_t0[g])), ("n_targets", str(len(H22[g])))):
            if a != p[k]:
                hm[k].append((g, a, p[k]))
    summ["H22_column_mismatch_counts"] = {k: len(v) for k, v in hm.items()}
    # term sizes vs produced
    psz = {}
    for r in read_tsv(ROOT / "results" / "holdout" / "H_targets.tsv"):
        psz[r["go_id"]] = int(r["term_size_t0"])
    summ["term_size_mismatches"] = sorted((t, size_t0.get(t, 0), s) for t, s in psz.items()
                                          if size_t0.get(t, 0) != s)[:20]
    summ["n_term_size_mismatches"] = sum(1 for t, s in psz.items() if size_t0.get(t, 0) != s)
    with open(OUT / "rederive_summary.json", "w") as fh:
        json.dump(summ, fh, indent=1, default=str)
    for k, v in summ.items():
        if not isinstance(v, (dict, list)):
            print(k, v)
        elif isinstance(v, list):
            print(k, len(v), v[:30])


if __name__ == "__main__":
    sys.exit(main())
