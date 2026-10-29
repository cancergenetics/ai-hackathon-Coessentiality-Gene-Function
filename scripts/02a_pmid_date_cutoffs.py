#!/usr/bin/env python
"""02a_pmid_date_cutoffs.py -- determine PMID-number cut-offs used as a *date proxy* for "published before <date>".

PubMed IDs are assigned (approximately) sequentially when a citation enters PubMed, so a PMID threshold approximates
an Entrez-date (EDAT) cut-off. For each cut-off date D we query NCBI E-utilities esearch for all PMIDs with
EDAT == D, D+1, D+2 (pooled = "on/after" window) and EDAT == D-3 .. D-1 ("before" window). Some records carry an old
EDAT but a much newer PMID (back-filled / re-indexed records) or vice versa, so we use a robust rule:

    cutoff_pmid(D) = 1st percentile of the PMIDs with EDAT in [D, D+2]

A gene2pubmed PMID p is counted as "before D" iff p < cutoff_pmid(D). This is an APPROXIMATION of the EDAT (not the
publication date); diagnostics (fraction of the before-window PMIDs >= cut-off, fraction of the after-window PMIDs
< cut-off) are written next to each cut-off.

Run (needs network; ~30 small esearch requests, <= 3 req/s as NCBI asks without an API key):
    .env/bin/python -I scripts/02a_pmid_date_cutoffs.py
Writes:
    results/preregistration/pmid_date_cutoffs.tsv       (one row per cut-off date)
    results/preregistration/pmid_date_cutoffs_days.tsv  (per-day PMID quantiles for the queried days)
"""
import datetime as dt
import json
import os
import time
import urllib.parse
import urllib.request

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "preregistration")
# 2019-07-01 and 2020-06-01 are the requested cut-offs (= archived GO releases used for temporal hold-outs);
# 2018-07-01 and 2022-07-01 added for symmetry with the other archived GO releases.
CUTOFFS = ["2018-07-01", "2019-07-01", "2020-06-01", "2022-07-01"]
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def esearch_edat(day: dt.date) -> tuple[int, list[int]]:
    term = f'{day:%Y/%m/%d}[EDAT]'
    url = ESEARCH + "?" + urllib.parse.urlencode(dict(db="pubmed", term=term, retmax=10000, retmode="json",
                                                       tool="predicting_gene_function_prereg"))
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                res = json.load(r)["esearchresult"]
            break
        except Exception:  # transient NCBI errors
            time.sleep(2 + 2 * attempt)
    else:
        raise RuntimeError(f"esearch failed for {term}")
    count = int(res["count"])
    ids = [int(i) for i in res["idlist"]]
    if count > len(ids):
        raise RuntimeError(f"{term}: {count} hits > retmax {len(ids)}")
    time.sleep(0.4)
    return count, ids


def main():
    os.makedirs(OUT, exist_ok=True)
    query_date = dt.date.today().isoformat()
    day_rows, cut_rows = [], []
    for c in CUTOFFS:
        d0 = dt.date.fromisoformat(c)
        before, after = [], []
        for off in range(-3, 3):
            day = d0 + dt.timedelta(days=off)
            n, ids = esearch_edat(day)
            (after if off >= 0 else before).extend(ids)
            q = np.percentile(ids, [1, 5, 50, 95, 99]).astype(int) if ids else [None] * 5
            day_rows.append([c, day.isoformat(), n, *(q if ids else ["NA"] * 5), min(ids, default="NA"),
                             max(ids, default="NA")])
        after, before = np.array(after), np.array(before)
        cut = int(np.percentile(after, 1))
        cut_rows.append([c, cut, len(before), len(after), f"{(before >= cut).mean():.4f}",
                         f"{(after < cut).mean():.4f}", int(np.median(before)), int(np.median(after)), query_date])
        print(c, cut)
    with open(os.path.join(OUT, "pmid_date_cutoffs_days.tsv"), "w") as f:
        f.write("cutoff_date\tedat_day\tn_pmids\tp01\tp05\tp50\tp95\tp99\tmin\tmax\n")
        for r in day_rows:
            f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(OUT, "pmid_date_cutoffs.tsv"), "w") as f:
        f.write("cutoff_date\tcutoff_pmid\tn_pmids_edat_3d_before\tn_pmids_edat_3d_onafter\t"
                "frac_before_window_ge_cutoff\tfrac_onafter_window_lt_cutoff\tmedian_pmid_before\t"
                "median_pmid_onafter\tquery_date\n")
        for r in cut_rows:
            f.write("\t".join(map(str, r)) + "\n")


if __name__ == "__main__":
    main()
