#!/usr/bin/env python3
"""Assemble manuscript parts (keyed citations) into manuscript.md with numbered citations and a PLOS-style
reference list. Metadata: Crossref records fetched by scripts/78_crossref_metadata.py (old_meta.tsv, new_meta.tsv); fallback to the TSV."""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "manuscript"
parts = sorted((S / "src").glob("*.md"))
text = "".join(p.read_text() for p in parts)

tsv = {}
with open(ROOT / "references/literature_refs.tsv") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        tsv[r["key"]] = r
meta = {}
for fn in ("old_meta.tsv", "new_meta.tsv"):
    for line in (ROOT / "references" / fn).read_text().splitlines():
        k, *rest = line.split("\t")
        meta[k] = rest  # authors, year, title, journal, vol, issue, page, doi
EXTRA = {"DepMap_web": dict(authors="Broad Institute", year="2026",
                            title="DepMap Public 26Q3 (CRISPRGeneEffect and companion files)",
                            journal="DepMap portal", doi_or_pmid="https://depmap.org/portal/")}
keys = set(tsv) | set(meta) | set(EXTRA)

body, _, _ = text.partition("<!-- REFERENCES -->")
pat = re.compile(r"\[([A-Za-z][A-Za-z0-9_]*(?:;\s*[A-Za-z][A-Za-z0-9_]*)*)\]")
order = []
def scan(m):
    ks = [k.strip() for k in m.group(1).split(";")]
    if all(k in keys for k in ks):
        for k in ks:
            if k not in order:
                order.append(k)
# strip HTML comments before scanning so commented keys never count
for m in pat.finditer(re.sub(r"<!--.*?-->", "", text, flags=re.S)):
    scan(m)
num = {k: i + 1 for i, k in enumerate(order)}

def compress(ns):
    ns = sorted(set(ns)); out = []; i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(str(ns[i]) if j == i else (f"{ns[i]},{ns[j]}" if j == i + 1 else f"{ns[i]}–{ns[j]}"))
        i = j + 1
    return ",".join(out)

def repl(m):
    ks = [k.strip() for k in m.group(1).split(";")]
    if all(k in keys for k in ks):
        return "[" + compress([num[k] for k in ks]) + "]"
    return m.group(0)

# replace outside HTML comments only
chunks = re.split(r"(<!--.*?-->)", text, flags=re.S)
text = "".join(c if c.startswith("<!--") else pat.sub(repl, c) for c in chunks)
unknown = sorted({k for m in pat.finditer(re.sub(r"<!--.*?-->", "", text, flags=re.S))
                  for k in [x.strip() for x in m.group(1).split(";")] if k[0].isupper() and k not in keys})

def fix_name(n):
    fam, _, ini = n.rpartition(" ")
    if fam.isupper():
        fam = fam.title()
    return f"{fam} {ini}".strip()

def fmt(k):
    if k in meta and len(meta[k]) == 8:
        au, yr, ti, jo, vol, iss, pg, doi = meta[k]
        names = [fix_name(a) for a in au.split(";") if a and not a.lower().startswith("on behalf")]
        auth = ", ".join(names[:6]) + (", et al." if len(names) > 6 else "")
        if not jo:
            jo = tsv.get(k, {}).get("journal", "Preprint")
        loc = f"{yr}"
        if vol:
            loc += f";{vol}"
            if iss:
                loc += f"({iss})"
            if pg:
                loc += f":{pg}"
        elif pg:
            loc += f":{pg}"
        ti = ti.rstrip(".")
        if ti.isupper():
            ti = ti.capitalize()
        if jo.isupper():
            jo = jo.title()
        a_end = "" if auth.endswith(".") else "."
        t_end = "" if ti[-1] in "?!" else "."
        return f"{auth}{a_end} {ti}{t_end} {jo}. {loc}. doi:{doi}"
    r = tsv.get(k) or EXTRA[k]
    url = r["doi_or_pmid"]
    if url.startswith("doi:"):
        return f"{r['authors']}. {r['title']}. {r['journal']}. {r['year']}. {url}"
    acc = "Accessed 2026-10-30" if k == "DepMap_web" else "Accessed 2026-10-29"
    return f"{r['authors']}. {r['title']} [Internet]. {r['journal']}; {r['year']}. Available from: {url}. {acc}."

refs = "\n".join(f"{num[k]}. {fmt(k)}" for k in order)
text = text.replace("<!-- REFERENCES -->", refs)
(ROOT / "manuscript/manuscript.md").write_text(text)
(S / "cited_keys.txt").write_text("\n".join(order) + "\n")
print("cited", len(order), "unknown-looking keys:", unknown)
