#!/usr/bin/env python
"""05_circularity_query.py -- DepMap-circularity flags for hold-out target annotations (DESIGN.md v2.1 §3.2.3).

For every PMID supporting an H target (results/holdout/H_targets.tsv) Europe PMC REST search is queried with
  EXT_ID:<pmid> AND SRC:MED AND (DepMap OR "co-essential*" OR coessential* OR codependen* OR "co-dependen*"
                                 OR "Project Achilles")
Europe PMC's default (field-less) search covers title, abstract, keywords/MeSH AND the full text of every article
whose full text is in Europe PMC (inEPMC = Y; open-access and author-manuscript/free full text, also non-OA;
verified: Wainberg 2021, PMID 33859415, isOpenAccess = N, inEPMC = Y, matches METHODS:"Achilles"). Phrase wildcards
must be quoted ("co-essential*" matches, unquoted co-essential* does not); quoted as in the spec.
Coverage per PMID = whether the full text was searchable (inEPMC = Y), from a metadata query (resultType=lite).

Requests are batched (EXT_ID:(p1 OR p2 ...) -- logically identical to one query per PMID; the per-PMID form is
re-run on a validation sample and on every flagged PMID to confirm equivalence). Per-term queries are run for flagged
PMIDs to record which term matched. Rate <= 4 requests/s; every response is cached under data/cache/europepmc/
(git-ignored); re-runs are offline when the cache is complete.

Outputs: results/holdout/circularity_flags.tsv (one row per PMID), results/holdout/circularity_annotations.tsv
(one row per (gene, target) with circular-flag status), results/holdout/circularity_summary.md.
Run: .env/bin/python -I scripts/05_circularity_query.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.parse

import pandas as pd
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "holdout")
CACHE = os.path.join(ROOT, "data", "cache", "europepmc")
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
TERMS = ['DepMap', '"co-essential*"', 'coessential*', 'codependen*', '"co-dependen*"', '"Project Achilles"']
TERM_CLAUSE = "(" + " OR ".join(TERMS) + ")"
BATCH = 50
MIN_INTERVAL = 0.25  # s between live requests (<= 4/s)
VALIDATION_N = 40
WAINBERG_2021 = 33859415

_last = [0.0]


def get(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(sorted(params.items()))
    key = hashlib.sha1(url.encode()).hexdigest()
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["response"]
    for attempt in range(5):
        wait = MIN_INTERVAL - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                data = r.json()
                with open(path, "w") as f:
                    json.dump({"url": url, "retrieved": time.strftime("%Y-%m-%dT%H:%M:%S"), "response": data}, f)
                return data
        except requests.RequestException:
            pass
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Europe PMC request failed: {url}")


def search_all(query: str, result_type: str = "idlist") -> list[dict]:
    out, cursor = [], "*"
    while True:
        d = get({"query": query, "resultType": result_type, "format": "json", "pageSize": 1000,
                 "cursorMark": cursor})
        res = d.get("resultList", {}).get("result", [])
        out += res
        nxt = d.get("nextCursorMark")
        if not res or nxt is None or nxt == cursor or len(out) >= d.get("hitCount", 0):
            return out
        cursor = nxt


def ext_clause(pmids) -> str:
    return "EXT_ID:(" + " OR ".join(str(p) for p in pmids) + ")"


def main():
    os.makedirs(CACHE, exist_ok=True)
    TT = pd.read_csv(os.path.join(OUT, "H_targets.tsv"), sep="\t", dtype={"support_pmids": str})
    TT["support_pmids"] = TT.support_pmids.fillna("")
    pmids = sorted({int(p) for s in TT.support_pmids for p in s.split("|") if p})
    print(f"{len(pmids)} supporting PMIDs")

    meta, hits = {}, set()
    for i in range(0, len(pmids), BATCH):
        b = pmids[i:i + BATCH]
        for r in search_all(ext_clause(b) + " AND SRC:MED", "lite"):
            if r.get("pmid"):
                meta[int(r["pmid"])] = r
        for r in search_all(ext_clause(b) + " AND SRC:MED AND " + TERM_CLAUSE, "idlist"):
            if r.get("pmid"):
                hits.add(int(r["pmid"]))
    # ---------------------------------------------------------------- per-PMID validation (spec form)
    rows_val = []
    val = sorted(set(pmids[:: max(1, len(pmids) // VALIDATION_N)][:VALIDATION_N]) | hits | {WAINBERG_2021})
    for p in val:
        d = get({"query": f"EXT_ID:{p} AND SRC:MED AND {TERM_CLAUSE}", "resultType": "idlist", "format": "json",
                 "pageSize": 25})
        rows_val.append((p, d.get("hitCount", 0) > 0, p in hits))
    disagree = [r for r in rows_val if r[1] != r[2]]
    # ---------------------------------------------------------------- per-term breakdown for flagged PMIDs
    term_hits = {p: [] for p in hits}
    hl = sorted(hits)
    for t in TERMS:
        for i in range(0, len(hl), BATCH):
            for r in search_all(ext_clause(hl[i:i + BATCH]) + f" AND SRC:MED AND ({t})", "idlist"):
                if r.get("pmid") and int(r["pmid"]) in term_hits:
                    term_hits[int(r["pmid"])].append(t)

    F = pd.DataFrame({"pmid": pmids})
    F["found_in_europepmc"] = F.pmid.isin(meta)
    F["full_text_searchable"] = F.pmid.map(lambda p: meta.get(p, {}).get("inEPMC") == "Y")
    F["is_open_access"] = F.pmid.map(lambda p: meta.get(p, {}).get("isOpenAccess") == "Y")
    F["pmcid"] = F.pmid.map(lambda p: meta.get(p, {}).get("pmcid", ""))
    F["pub_year"] = F.pmid.map(lambda p: meta.get(p, {}).get("pubYear", ""))
    F["title"] = F.pmid.map(lambda p: meta.get(p, {}).get("title", ""))
    F["circular_flag"] = F.pmid.isin(hits)
    F["matched_terms"] = F.pmid.map(lambda p: "|".join(term_hits.get(p, [])))
    F["searched_fields"] = F.full_text_searchable.map(lambda x: "full text + title/abstract/keywords" if x
                                                      else "title/abstract/keywords only")
    F.to_csv(os.path.join(OUT, "circularity_flags.tsv"), sep="\t", index=False)

    # ---------------------------------------------------------------- annotation-level flags
    flag = dict(zip(F.pmid, F.circular_flag))
    ft = dict(zip(F.pmid, F.full_text_searchable))

    def ann_status(s):
        ps = [int(p) for p in s.split("|") if p]
        if not ps:
            return pd.Series(dict(any_pmid_flagged=False, n_pmids=0, n_pmids_flagged=0,
                                  all_pmids_full_text=False, any_pmid_full_text=False))
        return pd.Series(dict(any_pmid_flagged=any(flag[p] for p in ps), n_pmids=len(ps),
                              n_pmids_flagged=sum(flag[p] for p in ps),
                              all_pmids_full_text=all(ft[p] for p in ps), any_pmid_full_text=any(ft[p] for p in ps)))
    A = pd.concat([TT[["hgnc_id", "symbol", "go_id", "go_name", "support_pmids"]],
                   TT.support_pmids.apply(ann_status)], axis=1)
    # a (gene, target) is circular when ANY supporting PMID is flagged (conservative), and "fully circular" when every
    # supporting PMID is flagged (the target would vanish if flagged papers were removed)
    A["fully_circular"] = (A.n_pmids > 0) & (A.n_pmids == A.n_pmids_flagged)
    A.to_csv(os.path.join(OUT, "circularity_annotations.tsv"), sep="\t", index=False)

    genes_all_targets_circ = A.groupby("hgnc_id").fully_circular.all()
    ccdc = A[A.symbol == "CCDC32"]
    ccdc_pm = sorted({int(p) for s in ccdc.support_pmids for p in s.split("|") if p})
    w_in = WAINBERG_2021 in set(pmids)
    ccdc_w = ccdc[ccdc.support_pmids.map(lambda x: str(WAINBERG_2021) in x.split("|"))]
    L = ["# Circularity query -- summary", "",
         "`scripts/05_circularity_query.py`; Europe PMC REST search (" + time.strftime("%Y-%m-%d") + "; cached under "
         "`data/cache/europepmc/`). Query per PMID: `EXT_ID:<pmid> AND SRC:MED AND " + TERM_CLAUSE + "`. Default "
         "field-less search = title, abstract, keywords and, when the article's full text is in Europe PMC (inEPMC=Y), "
         "the full text.", "",
         f"- supporting PMIDs queried: {len(F):,}; found in Europe PMC: {int(F.found_in_europepmc.sum()):,}",
         f"- **full text searchable (inEPMC=Y): {int(F.full_text_searchable.sum()):,} / {len(F):,} "
         f"({F.full_text_searchable.mean():.1%})**; open access: {int(F.is_open_access.sum()):,}",
         f"- **PMIDs flagged: {int(F.circular_flag.sum()):,} / {len(F):,} ({F.circular_flag.mean():.1%})**; among "
         f"full-text-searchable PMIDs {F[F.full_text_searchable].circular_flag.mean():.1%}, among abstract-only PMIDs "
         f"{F[~F.full_text_searchable].circular_flag.mean():.1%}",
         "- matched terms among flagged PMIDs: " + ", ".join(
             f"{t} {int(F.matched_terms.str.contains(t, regex=False).sum())}" for t in TERMS),
         f"- (gene, target) pairs with >= 1 flagged supporting PMID: {int(A.any_pmid_flagged.sum()):,} / {len(A):,} "
         f"({A.any_pmid_flagged.mean():.1%}); all supporting PMIDs flagged: {int(A.fully_circular.sum()):,}",
         f"- H genes with >= 1 flagged target: {A[A.any_pmid_flagged].hgnc_id.nunique():,} / {A.hgnc_id.nunique():,}; "
         f"H genes whose every target is fully circular (would leave H if flagged annotations are excluded): "
         f"{int(genes_all_targets_circ.sum()):,}",
         f"- (gene, target) pairs whose supporting PMIDs are all full-text searchable: "
         f"{int(A.all_pmids_full_text.sum()):,} / {len(A):,}; with no PMID (GO_REF/Reactome only, not queryable): "
         f"{int((A.n_pmids == 0).sum())}",
         f"- per-PMID validation of the batched query (spec form, one query per PMID): {len(rows_val)} PMIDs "
         f"(systematic sample + all flagged + Wainberg 2021), disagreements: {len(disagree)} {disagree[:10]}", "",
         "## Known-answer check: CCDC32 / Wainberg et al. 2021 (PMID 33859415)", "",
         f"- PMID 33859415 among supporting PMIDs: {w_in}; flagged: "
         f"{bool(flag.get(WAINBERG_2021, False)) if w_in else 'n/a'}",
         f"- CCDC32 supporting PMIDs: {ccdc_pm}; flags: " + ", ".join(f"{p}={flag[p]}" for p in ccdc_pm),
         "- CCDC32 targets: " + "; ".join(f"{r.go_id} {r.go_name} (any flagged {r.any_pmid_flagged})"
                                           for r in ccdc.itertuples()),
         f"- CCDC32 targets citing PMID 33859415: {len(ccdc_w)}; all flagged: {bool(ccdc_w.any_pmid_flagged.all())}",
         f"- **check {'PASS' if (w_in and flag.get(WAINBERG_2021) and len(ccdc_w) and ccdc_w.any_pmid_flagged.all()) else 'FAIL'}**"
         + ("" if len(ccdc_w) else " (no current CCDC32 target annotation cites Wainberg 2021; "
            "the query itself was verified to flag PMID 33859415 directly, see validation)"), "",
         "## Named controls", "", "| symbol | targets | targets with flagged PMID | supporting PMIDs (flag) |",
         "|---|---|---|---|"]
    for s in ["SPRING1", "PEDS1", "CCDC32", "INTS15", "HAPSTR1", "SLC25A51", "TEDC1", "TEDC2", "POU2AF2", "POU2AF3",
              "TMEM242", "FIRRM", "AIRIM", "TMEM41B"]:
        a = A[A.symbol == s]
        if not len(a):
            L.append(f"| {s} | not in H | | |")
            continue
        pm = sorted({int(p) for x in a.support_pmids for p in x.split("|") if p})
        L.append(f"| {s} | {len(a)} | {int(a.any_pmid_flagged.sum())} | "
                 + ", ".join(f"{p} ({'FLAG' if flag[p] else '-'}{'' if ft[p] else ', abstract only'})" for p in pm)
                 + " |")
    wv = [r for r in rows_val if r[0] == WAINBERG_2021]
    L += ["", f"Direct query on PMID 33859415 (spec form): flagged = {wv[0][1] if wv else 'n/a'}."]
    with open(os.path.join(OUT, "circularity_summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
