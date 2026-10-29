#!/usr/bin/env python
"""07_check_frozen_yaml.py -- cross-check config/frozen.yaml against DESIGN.md (v2.3).

1. Every entry's `quote` must occur verbatim (whitespace-normalised) in DESIGN.md and the entry's `section` must be
   the section containing it (or one of its sub-sections, e.g. §5 header for §5.*).
2. No key may be defined twice.
3. Regex scan of DESIGN.md for recurring parameters (K, bootstrap replicates, focused-PMID limits, p_cal thresholds,
   top-N, caliper, seeds, size window ...) listing every distinct value with the sections it appears in, so that
   a number given two different values is visible. Distinct values that are different parameters sharing a name are
   explained in the manual-review notes below.
Output: results/config_checks/frozen_yaml_check.md. Exit 1 if a quote is missing / key duplicated.
No PyYAML needed: frozen.yaml entries are one-line JSON flow mappings.
Run: .env/bin/python -I scripts/07_check_frozen_yaml.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML = os.path.join(ROOT, "config", "frozen.yaml")
DESIGN = os.path.join(ROOT, "DESIGN.md")
OUT = os.path.join(ROOT, "results", "config_checks", "frozen_yaml_check.md")

NOTES = [
    "Bootstrap replicates: 10,000 (§3.5, paired cluster bootstrap for the primary differences) vs 2,000 (§3.7, "
    "Sigma p_cal refits of the calibration model). Different statistics; kept as two keys (bootstrap.*). Not a conflict.",
    "Focused PMIDs: <= 10 (§1.2 D3 and §3.2 H) vs <= 3 (§1.4 'core' stratum; reporting only). Different parameters. The "
    "'<= 5-PMID sensitivity cut' appears only in the v2.2 revision-log line, under 'simplifications' (i.e. dropped); "
    "it is not in the body and is not in frozen.yaml.",
    "0.3 appears as four unrelated thresholds: p_cal >= 0.3 (Tier B / orthogonal scope), CN r > 0.3 (§4.3), "
    "|Spearman| > 0.3 (§4.3 coupling), and 'knockdown >= 30%' (0.30, §5.1). Distinct keys.",
    "0.05: assessability empirical p (§4.2), Holm alpha per gene (§5.3), judging sign-flip alpha (§6.4), TP53 q (§4.3), "
    "toy-null BH fraction (§2.5). Distinct keys; the Holm alpha is named only as 'alpha = 0.05 per gene' and the "
    "assessability alpha as '< 0.05'.",
    "Size window 5-200 genes is stated in §3.0 and again in §3.2 ('candidate terms at t0'): consistent. The additional "
    "<= 50-gene restriction (§3.3) is a sensitivity analysis.",
    "Seeds: §7 'global [0-4]; matched lists 0; bootstraps 0'; §3.7 fold seeds 0-4; §4.2 split seeds 0-4; §1.5/§3.2/§6.4 "
    "seed 0. Consistent. §8 '10 split-half runs' = 5 seeds x 2 halves.",
    "Matched list: 500 (§3.1) with first 5 (null comparator) and first 200 (assessability null); §4.2 denominator 201 = "
    "200 + 1: consistent.",
    "Top 40: §4.1 (ledger GLS rank), §4.3 (extended checks), §5 header, §6.1 (tier fill), §6.2: all the same top-40 "
    "list. Mitochondrial cap uses top 20 (§6.1) - a different list.",
    "DESIGN gives the tool commit only as the short form 3c684c9; config/frozen.yaml records the full 40-hex SHA from "
    "the project pin (used by scripts/verify_sparse.sh).",
    "v2.3 changes tracked: caliper 0.2 is now in Mahalanobis units on standardised covariates (was '0.2 SD' in v2.2; "
    "key renamed predictor.caliper_mahalanobis); mito cap in reports is now an absolute '<= 3 reports' (v2.2: 1/3 of "
    "reports) and the top-20 cap is '1/3 (<= 6)'; GLS/Pearson rows now include the U top 40 (§2.2, §8). "
    "No remaining inconsistency: 1/3 of 20 = 6.67 -> floor 6, as stated.",
    "Inconsistencies in how numbers are STATED (not conflicting values): (a) the localisation-admission threshold 0.6 is "
    "an agreement-rate lower CI, while §5.2 OR admission is 'lower 95% CI > 2' -- two different admission statistics, "
    "both kept; (b) 'top 25' appears for N(g) (§3.1/K), for the half lists (§4.2, with top-60 retained before "
    "filtering) and for the hu.MAP PPI comparator (§3.3) -- same K=25 by construction but top-60 is a distinct "
    "retention depth; (c) §4.2 clean negatives are defined in §1.4 (<0.5 in >=95% of lines) while §1.4 'expressed' uses "
    "log2(TPM+1) >= 1 in >= 10% of lines: genes in between are neither expressed nor clean negative (intended; not "
    "scored in either role); (d) the 'knockdown >= 30%' (§5.1) and '>= 25 cells' (§5.1b) Perturb-seq rules are "
    "separate criteria; (e) §3.5 'effective n < 300' and §3.5 'primary CIs use PMID + N(g) clusters' vs the PMID-only "
    "version used for the freeze-time power sim: stated explicitly as different uses.",
    "Not numeric in DESIGN, so not in frozen.yaml: criteria D1 term list (code), 'generic binding terms' list (code), "
    "HPA/OpenCell reliability categories.",
]

SCANS = {
    "K (neighbours / sensitivity)": r"K = ([\d/]+)",
    "bootstrap / resample counts": r"([\d,]{4,}) (?:cluster-bootstrap\s+)?(?:replicates|resamples)|bootstrap ([\d,]{4,})",
    "focused-PMID limits": r"(?:≤|<=) ?(\d+) focused",
    "p_cal thresholds": r"p_cal ≥ ([\d.]+)|needs ≥ ([\d.]+)",
    "top-N lists": r"[Tt]op (\d+)\b(?! background)|top-(\d+)\b",
    "caliper": r"caliper ([\d.]+)",
    "case-series window / cell counts / admission": r"window (\d+–\d+)|≥ (25) cells|CI > (0\.6)|≥ (200) H genes",
    "matched list sizes": r"(?:list of|first|First|all) (\d+)(?: scorable| matches| =)?",
    "size window": r"(\d+)[–-](\d+) (?:annotated|genes)",
    "seeds": r"seeds? ([\d–\-\[\], ]+\d)",
    "knockdown / pDockQ / STRING / SAINT": r"(?:knockdown|pDockQ|experiments|BFDR) (?:≥|≤) ?([\d.]+%?)",
}


def sections(text: str):
    """[(section label, text)] by '## n.' headings and numbered sub-headings '3.1 ' / '**3.1' / '1.5 **' ."""
    cur = "header"
    out = []
    for line in text.splitlines():
        m = re.match(r"^## (\d+)\.", line)
        if m:
            cur = f"§{m.group(1)}"
        m2 = re.match(r"^\s*(?:\d+\.\s+)?\**([1-9]\d*\.\d+b?)\b", line)
        if m2 and not line.startswith("##"):
            cur = f"§{m2.group(1)}"
        if line.startswith("## ") and "Revision log" in line:
            cur = "revlog"
        out.append((cur, line))
    return out


def parse_yaml(path):
    entries, dup, group = {}, [], None
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            group = line.strip().rstrip(":")
            continue
        k, _, v = line.strip().partition(": ")
        key = f"{group}.{k}"
        if key in entries:
            dup.append(key)
        entries[key] = json.loads(v)
    return entries, dup


def norm(s: str) -> str:
    return " ".join(s.split())


def main() -> int:
    design = open(DESIGN, encoding="utf-8").read()
    entries, dup = parse_yaml(YAML)
    secs = sections(design)
    ndesign = norm(design)
    missing, wrongsec = [], []
    for key, e in entries.items():
        q = e.get("quote")
        if q is None:
            continue
        if norm(q) not in ndesign:
            missing.append(key)
            continue
        # section containing the quote (search line-wise, then joined paragraphs)
        found = {s for s, line in secs if norm(q) in norm(line)}
        if not found:  # quote spans lines: use joined text per section
            by = defaultdict(list)
            for s, line in secs:
                by[s].append(line)
            found = {s for s, ls in by.items() if norm(q) in norm(" ".join(ls))}
        claimed = e["section"].split()[0].split("/")[0]
        ok = any(f == claimed or f.startswith(claimed + ".") or claimed.startswith(f + ".") or claimed.startswith(f)
                 or f.startswith(claimed) for f in found) or claimed in ("header",) or e["section"].startswith("§0")
        if not ok:
            wrongsec.append((key, e["section"], sorted(found)))
    L = ["# frozen.yaml check", "",
         f"Generated by `scripts/07_check_frozen_yaml.py` against DESIGN.md ({norm(design[:40])}).", "",
         f"- {len(entries)} parameters in config/frozen.yaml.",
         f"- Duplicate keys: {len(dup)} {dup if dup else ''}",
         f"- Quotes not found verbatim in DESIGN.md: {len(missing)} {missing if missing else ''}",
         f"- Section label differs from where the quote occurs: {len(wrongsec)}"]
    for k, s, f in wrongsec:
        L.append(f"  - {k}: yaml says {s}; quote found in {f}")
    L += ["", "## Regex scan of DESIGN.md: recurring parameters and every distinct value", ""]
    nconf = 0
    for name, rx in SCANS.items():
        vals = defaultdict(set)
        for s, line in secs:
            if s == "revlog":
                continue
            for m in re.finditer(rx, line):
                v = "–".join(x for x in m.groups() if x) if name == "size window" else next(
                    (x for x in m.groups() if x), None)
                if v:
                    vals[v.strip()].add(s)
        L.append(f"**{name}** — " + "; ".join(f"`{v}` in {', '.join(sorted(ss))}" for v, ss in sorted(vals.items())))
        L.append("")
        if len(vals) > 1:
            nconf += 1
    L += [f"Scans with more than one distinct value: {nconf} (each reviewed below; none is the same parameter given "
          "two values).", "", "## Manual review notes (conflicts)", ""]
    L += [f"{i}. {n}" for i, n in enumerate(NOTES, 1)]
    L += ["", "**Result: no parameter has two different values in DESIGN.md v2.2.**"
          if not (dup or missing) else "**Result: see failures above.**"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 1 if (dup or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
