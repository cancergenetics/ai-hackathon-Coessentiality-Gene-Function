#!/usr/bin/env python
"""06_check_term_families.py -- verify config/term_families.tsv (DESIGN.md v2.2 §3.0) against the current GO.

Checks: every go_id exists in data/raw/go/current/go-basic.obo, is not obsolete, is BP or MF (V2 = BP + MF), the
listed name equals the obo name, no id is listed twice, family order is 1..7 in the fixed order. Then reports, per
family, how many candidate V2 terms (BP/MF, 5-200 annotated scorable genes at the current release, D1 evidence codes,
generic terms removed; same rules as src/knownness.py / scripts/04_holdout_sizing.py) fall under it with
"first match wins" assignment, how many fall under >= 2 families (before first-match), and how many fall to
"other". Annotation-only: no DepMap values (scorable = results/ids/hgnc_hub.tsv).

Output: results/config_checks/term_families_check.md. Exit status 1 if any ID check fails.
Run: .env/bin/python -I scripts/06_check_term_families.py
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import knownness as kn  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw")
TSV = os.path.join(ROOT, "config", "term_families.tsv")
OUT = os.path.join(ROOT, "results", "config_checks", "term_families_check.md")
FAMILIES = ["mitochondrial", "nuclear_RNA_machinery", "ribosome_biogenesis_translation", "DNA_replication_repair",
            "ER_Golgi_secretory_lipid", "centrosome_cilia_mitosis", "signalling_lineage"]
LO, HI = 5, 200
NS_OK = ("biological_process", "molecular_function")


def verify_ids(fam: pd.DataFrame, onto) -> list[str]:
    """Return a list of problems (empty = all good)."""
    prob = []
    if list(fam.columns) != ["order", "family", "go_id", "go_name"]:
        prob.append(f"unexpected columns {list(fam.columns)}")
    seen = Counter(fam.go_id)
    for t, n in seen.items():
        if n > 1:
            prob.append(f"{t} listed {n} times")
    order = fam.drop_duplicates("family").sort_values("order").family.tolist()
    if order != FAMILIES:
        prob.append(f"family order {order} != {FAMILIES}")
    for r in fam.itertuples():
        t = onto.terms.get(r.go_id)
        if t is None:
            prob.append(f"{r.go_id}: not in obo (alt_id? {onto.alt.get(r.go_id)})")
        elif t["obsolete"]:
            prob.append(f"{r.go_id}: obsolete ({t['name']})")
        elif t["namespace"] not in NS_OK:
            prob.append(f"{r.go_id}: namespace {t['namespace']} not BP/MF")
        elif t["name"] != r.go_name:
            prob.append(f"{r.go_id}: name mismatch (file {r.go_name!r} vs obo {t['name']!r})")
        if kn.GENERIC and r.go_id in kn.GENERIC:
            prob.append(f"{r.go_id}: is a GENERIC term in src/knownness.py")
    return prob


def assign(term: str, onto, fam_ids: dict) -> tuple[list[str], str]:
    """(all matching families in fixed order, first match or 'other')."""
    anc = onto.ancestors(term)
    hits = [f for f in FAMILIES if any(i in anc for i in fam_ids[f])]
    return hits, (hits[0] if hits else "other")


def main() -> int:
    fam = pd.read_csv(TSV, sep="\t", dtype=str)
    onto = kn.GoOntology.from_obo(os.path.join(RAW, "go", "current", "go-basic.obo"), "current")
    problems = verify_ids(fam, onto)
    fam_ids = {f: sorted(fam[fam.family == f].go_id) for f in FAMILIES}

    # candidate terms at the current release
    pc = kn.load_hgnc_pc(os.path.join(RAW, "hgnc", "hgnc_complete_set.txt"))
    up = pd.read_csv(os.path.join(RAW, "uniprot", "uniprot_human_reviewed.tsv"), sep="\t", dtype=str,
                     keep_default_na=False)
    acc_map, _ = kn.build_acc_map(pc, up)
    hub = pd.read_csv(os.path.join(ROOT, "results", "ids", "hgnc_hub.tsv"), sep="\t", dtype=str, keep_default_na=False)
    scorable = set(hub.hgnc_id[hub.scorable == "True"])
    ann, _ = kn.d1_annotations(os.path.join(RAW, "go", "current", "goa_human.gaf.gz"), onto, acc_map,
                               resolve_mode="strict")
    prop = kn.propagate_annotations(ann, onto)
    inf_genes = set(ann[~ann.go_id.isin(kn.GENERIC)].hgnc_id) & scorable  # background: >= 1 informative annotation
    sizes = kn.term_sizes(prop, inf_genes)
    cand = [t for t, n in sizes.items() if LO <= n <= HI and t not in kn.GENERIC and t in onto.terms
            and not onto.terms[t]["obsolete"] and onto.namespace(t) in NS_OK]

    first, multi, per_id = Counter(), Counter(), Counter()
    n_multi, combos, other_examples = 0, Counter(), []
    for t in cand:
        hits, f = assign(t, onto, fam_ids)
        first[f] += 1
        for fid in (i for ff in FAMILIES for i in fam_ids[ff] if i in onto.ancestors(t)):
            per_id[fid] += 1
        if len(hits) > 1:
            n_multi += 1
            combos[" + ".join(hits)] += 1
        for h in hits:
            multi[h] += 1
    for t in sorted(cand, key=lambda x: -sizes[x]):
        if not assign(t, onto, fam_ids)[0]:
            other_examples.append(t)
        if len(other_examples) >= 15:
            break

    L = ["# term_families.tsv check", "",
         f"Generated by `scripts/06_check_term_families.py`. Obo: `{onto.release}`; GAF: current goa_human (D1 evidence "
         f"codes, generic terms removed); candidate terms = BP/MF terms with {LO}-{HI} annotated scorable genes "
         f"(background = scorable genes with >= 1 informative annotation: {len(inf_genes):,}).", "",
         "## ID verification", ""]
    L.append(f"- {len(fam)} rows, {fam.family.nunique()} families, {fam.go_id.nunique()} distinct IDs.")
    if problems:
        L += ["- **FAILED**:"] + [f"  - {p}" for p in problems]
    else:
        L.append("- All IDs exist in go-basic.obo, are not obsolete, are BP/MF, names match the obo, no duplicates, "
                 "family order is fixed order 1-7. **PASS**")
    L += ["", f"## Candidate terms by family ({len(cand):,} candidate V2 terms)", "",
          "| order | family | root IDs | candidate terms (first match wins) | candidate terms under family (any match) |",
          "|---|---|---|---|---|"]
    for i, f in enumerate(FAMILIES, 1):
        L.append(f"| {i} | {f} | {len(fam_ids[f])} | {first[f]} | {multi[f]} |")
    L.append(f"| 8 | other (fallback) | 0 | {first['other']} | - |")
    L += ["", f"Candidate terms falling under >= 2 families (resolved by first match): **{n_multi}** "
          f"({n_multi / max(len(cand), 1):.1%}).", "", "| family combination | n terms |", "|---|---|"]
    for k, v in combos.most_common(15):
        L.append(f"| {k} | {v} |")
    L += ["", "## Candidate terms per root ID (descendant-or-self)", "", "| family | go_id | go_name | n candidate terms |",
          "|---|---|---|---|"]
    for r in fam.itertuples():
        L.append(f"| {r.family} | {r.go_id} | {r.go_name} | {per_id[r.go_id]} |")
    L += ["", "## Largest candidate terms assigned to 'other' (for review; 15 shown)", "",
          "| go_id | name | namespace | genes |", "|---|---|---|---|"]
    for t in other_examples:
        L.append(f"| {t} | {onto.name(t)} | {onto.namespace(t)} | {int(sizes[t])} |")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L[:30]))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
