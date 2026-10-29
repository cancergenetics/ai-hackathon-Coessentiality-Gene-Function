#!/usr/bin/env python
"""01b_check_annotation_data.py -- checksum, document and sanity-check the annotation datasets fetched by
01a_fetch_annotation_data.sh.  Reads downloaded files as plain text only (never executes anything).

Run:  .env/bin/python -I scripts/01b_check_annotation_data.py
Writes:
  config/data_manifest_annotation.tsv       (file, source, url, version, sha256, size_bytes, licence, notes)
  results/data_checks/annotation_data_checks.md
"""
import collections
import csv
import gzip
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
MANIFEST = os.path.join(ROOT, "config", "data_manifest_annotation.tsv")
REPORT = os.path.join(ROOT, "results", "data_checks", "annotation_data_checks.md")

CC4 = "CC BY 4.0"
GO_LIC = "CC BY 4.0 (https://geneontology.org/docs/go-citation-policy/)"
NCBI_LIC = ("NCBI data: no copyright restriction on the NCBI-produced data, but submitters may claim rights "
            "(https://www.ncbi.nlm.nih.gov/home/about/policies/); treat as public domain-ish")
UP_LIC = "CC BY 4.0 (https://www.uniprot.org/help/license)"
UNK_LIC = "CC BY 4.0 (https://unknome.mrc-lmb.cam.ac.uk/download/)"
TCRD_LIC = ("TCRD: CC BY-SA 4.0 per TCRD README, BUT incorporates third-party sources with varied licences "
            "(TCRDv6_DataSourcesLicenses.xlsx at unmtid-dbs.net/download/TCRD/)")
REACT_LIC = "CC BY 4.0 (https://reactome.org/license)"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def headers_of(rel):
    d, b = os.path.split(os.path.join(RAW, rel))
    p = os.path.join(d, "_headers", b + ".headers.txt")
    out = {}
    if os.path.exists(p):
        for line in open(p, errors="replace"):
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip().lower()] = v.strip()
    return out


def opener(path):
    if path.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", errors="replace")
    return open(path, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- per-type checks
def check_obo(path):
    n_term = n_obs = 0
    ns = collections.Counter()
    ver = None
    cur_ns = None
    in_term = False
    obs = False
    for line in opener(path):
        line = line.rstrip("\n")
        if ver is None and line.startswith("data-version:"):
            ver = line.split(":", 1)[1].strip()
        if line.startswith("["):
            if in_term:
                n_obs += obs
                ns[cur_ns] += 1
            in_term = line == "[Term]"
            n_term += in_term
            obs, cur_ns = False, None
        elif in_term:
            if line.startswith("namespace:"):
                cur_ns = line.split(":", 1)[1].strip()
            elif line.startswith("is_obsolete: true"):
                obs = True
    if in_term:
        n_obs += obs
        ns[cur_ns] += 1
    return ver, [f"[Term] stanzas: {n_term:,} (obsolete: {n_obs:,})",
                 "namespaces: " + ", ".join(f"{k}={v:,}" for k, v in ns.most_common())]


def check_gaf(path):
    ids, syms, taxa = set(), set(), collections.Counter()
    ev = collections.Counter()
    aspects = collections.Counter()
    n = 0
    hdr = []
    maxdate = ""
    for line in opener(path):
        if line.startswith("!"):
            hdr.append(line.rstrip("\n"))
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) < 15:
            continue
        n += 1
        ids.add(f[1])
        syms.add(f[2])
        taxa[f[12]] += 1
        ev[f[6]] += 1
        aspects[f[8]] += 1
        maxdate = max(maxdate, f[13])
    gver = next((h for h in hdr if h.lower().startswith("!gaf-version")), "").replace("!gaf-version:", "").strip()
    gdate = next((h.split(":", 1)[1].strip() for h in hdr if h.lower().startswith(("!date-generated", "!date generated"))), "")
    lines = [f"header lines: {len(hdr)}; gaf-version {gver or 'n/a'}; header date-generated: {gdate or 'n/a'}",
             f"annotation rows: {n:,}; unique UniProt accessions (col2): {len(ids):,}; unique symbols (col3): {len(syms):,}",
             "taxon (col13) values: " + ", ".join(f"{k}={v:,}" for k, v in taxa.most_common(4)),
             "aspects: " + ", ".join(f"{k}={v:,}" for k, v in sorted(aspects.items())),
             "top evidence codes: " + ", ".join(f"{k}={v:,}" for k, v in ev.most_common(6)),
             f"max annotation date (col14): {maxdate}"]
    return gdate or maxdate, lines


def check_gene_info(path):
    n = 0
    taxa = collections.Counter()
    types = collections.Counter()
    ids = set()
    hdr = None
    for line in opener(path):
        if line.startswith("#"):
            hdr = line.strip()
            continue
        f = line.split("\t")
        n += 1
        taxa[f[0]] += 1
        ids.add(f[1])
        types[f[9]] += 1
    return None, [f"header: {hdr}", f"rows: {n:,}; unique GeneIDs: {len(ids):,}",
                  "tax_id: " + ", ".join(f"{k}={v:,}" for k, v in taxa.most_common(3)),
                  "type_of_gene: " + ", ".join(f"{k}={v:,}" for k, v in types.most_common(6))]


def check_gene2pubmed(path):
    n = 0
    taxa = collections.Counter()
    genes_h, pmids_h = set(), set()
    hdr = None
    for line in opener(path):
        if line.startswith("#"):
            hdr = line.strip()
            continue
        f = line.rstrip("\n").split("\t")
        n += 1
        taxa[f[0]] += 1
        if f[0] == "9606":
            genes_h.add(f[1])
            pmids_h.add(f[2])
    return None, [f"header: {hdr}", f"rows (excl. header): {n:,}; distinct tax_ids: {len(taxa):,}",
                  f"tax_id 9606 rows: {taxa.get('9606', 0):,}; human GeneIDs with >=1 PMID: {len(genes_h):,}; "
                  f"distinct human PMIDs: {len(pmids_h):,}"]


def check_uniprot(path):
    rdr = csv.reader(opener(path), delimiter="\t")
    hdr = next(rdr)
    rows = list(rdr)
    col = {h: i for i, h in enumerate(hdr)}
    acc = {r[0] for r in rows}
    out = [f"columns ({len(hdr)}): {' | '.join(hdr)}", f"rows: {len(rows):,}; unique accessions: {len(acc):,}"]
    for name in ("Protein existence", "Annotation"):
        k = next((h for h in hdr if h.startswith(name)), None)
        if k:
            c = collections.Counter(r[col[k]] for r in rows)
            out.append(f"{k}: " + ", ".join(f"{a}={b:,}" for a, b in sorted(c.items())))
    for name in ("Gene Names (primary)", "Gene Names (primary)".replace(" (primary)", " (primary)"), "Function [CC]",
                 "Gene Ontology IDs", "PubMed ID", "Pfam", "GeneID", "HGNC"):
        if name in col:
            out.append(f"non-empty '{name}': {sum(1 for r in rows if r[col[name]].strip()):,}")
    gp = next((h for h in hdr if h.startswith("Gene Names (primary)")), None)
    if gp:
        out.append(f"unique primary gene symbols: {len({r[col[gp]] for r in rows if r[col[gp]]}):,}")
    return None, out


def check_tsv_generic(path, label, key=None):
    rdr = csv.reader(opener(path), delimiter="\t")
    hdr = next(rdr)
    n = 0
    cnt = collections.Counter()
    ids = set()
    ki = hdr.index(key) if key and key in hdr else None
    for r in rdr:
        n += 1
        if ki is not None and len(r) > ki:
            cnt[r[ki]] += 1
        ids.add(r[0])
    out = [f"columns ({len(hdr)}): {' | '.join(hdr[:40])}", f"data rows: {n:,}; unique values in col 1: {len(ids):,}"]
    if ki is not None:
        out.append(f"{key}: " + ", ".join(f"{a}={b:,}" for a, b in cnt.most_common(8)))
    return None, out


def check_unknome_protein(path):
    rdr = csv.reader(opener(path), delimiter="\t")
    hdr = next(rdr)
    n = 0
    cnt = collections.Counter()
    human = 0
    sp = next((i for i, h in enumerate(hdr) if "species" in h.lower() or "taxon" in h.lower() or "organism" in h.lower()), None)
    for r in rdr:
        n += 1
        if sp is not None and len(r) > sp:
            cnt[r[sp]] += 1
    out = [f"columns ({len(hdr)}): {' | '.join(hdr)}", f"data rows: {n:,}"]
    if sp is not None:
        out.append(f"species column '{hdr[sp]}': {len(cnt)} distinct; top: " + ", ".join(f"{a}={b:,}" for a, b in cnt.most_common(5)))
        hs = [(k, v) for k, v in cnt.items() if "sapiens" in k.lower() or k in ("9606", "HUMAN")]
        out.append(f"human rows: {hs}")
    return None, out


def check_reactome(path):
    n = 0
    sp = collections.Counter()
    ids = set()
    for line in opener(path):
        f = line.rstrip("\n").split("\t")
        if len(f) < 6:
            continue
        n += 1
        sp[f[5]] += 1
        if f[5] == "Homo sapiens":
            ids.add(f[0])
    return None, [f"rows: {n:,}; Homo sapiens rows: {sp.get('Homo sapiens', 0):,}; unique human UniProt IDs: {len(ids):,}",
                  f"species count: {len(sp)}"]


def check_text(path):
    return None, [f"{sum(1 for _ in opener(path)):,} lines"]


# ---------------------------------------------------------------- file registry
FILES = []


def add(rel, source, url, lic, fn, notes="", version_hint=None):
    FILES.append(dict(rel=rel, source=source, url=url, lic=lic, fn=fn, notes=notes, vh=version_hint))


add("go/current/go-basic.obo", "Gene Ontology", "https://current.geneontology.org/ontology/go-basic.obo", GO_LIC, check_obo,
    "current ontology; version = header data-version")
add("go/current/goa_human.gaf.gz", "GOA human (GO Consortium / EBI GOA)", "https://current.geneontology.org/annotations/goa_human.gaf.gz",
    GO_LIC, check_gaf, "current annotations; note GAF generation date can lag the ontology release")
for d in ("2018-07-02", "2019-07-01", "2020-06-01", "2020-07-16", "2022-07-01"):
    tgt = {"2018-07-02": "2018-07-01 (nearest; 2018-07-01 dir does not exist)",
           "2019-07-01": "2019-07-01 (exact)",
           "2020-06-01": "2020-07-01 (nearest release on/before the cutoff; 2020-07-01 dir does not exist)",
           "2020-07-16": "2020-07-01 (nearest overall; post-cutoff by 15 days; 2020-07-01 dir does not exist)",
           "2022-07-01": "2022-07-01 (exact)"}[d]
    add(f"go/archive/{d}/go-basic.obo", "Gene Ontology (archived release)", f"https://release.geneontology.org/{d}/ontology/go-basic.obo",
        GO_LIC, check_obo, f"archived release {d}; target cutoff {tgt}")
    add(f"go/archive/{d}/goa_human.gaf.gz", "GOA human (archived GO release)", f"https://release.geneontology.org/{d}/annotations/goa_human.gaf.gz",
        GO_LIC, check_gaf, f"archived release {d}; target cutoff {tgt}")
add("ncbi_gene/Homo_sapiens.gene_info.gz", "NCBI Gene", "https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz",
    NCBI_LIC, check_gene_info, "version = HTTP Last-Modified")
add("ncbi_gene/gene2pubmed.gz", "NCBI Gene", "https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz", NCBI_LIC, check_gene2pubmed,
    "ALL taxa (original, unfiltered); version = HTTP Last-Modified")
add("ncbi_gene/gene2pubmed_9606.tsv", "NCBI Gene (derived)", "derived from ncbi_gene/gene2pubmed.gz by 01a_fetch_annotation_data.sh (awk: header + tax_id==9606)",
    NCBI_LIC, check_gene2pubmed, "derived, filtered to tax_id 9606; parent checksum = gene2pubmed.gz row above")
UPFIELDS = "accession,id,gene_names,gene_primary,protein_name,annotation_score,protein_existence,length,cc_function,cc_subcellular_location,go_id,go_p,go_f,go_c,keyword,ft_domain,xref_pfam,xref_interpro,cc_similarity,xref_geneid,xref_hgnc,lit_pubmed_id,date_modified,version"
add("uniprot/uniprot_human_reviewed.tsv", "UniProtKB/Swiss-Prot", "https://rest.uniprot.org/uniprotkb/stream?query=organism_id:9606+AND+reviewed:true&format=tsv&fields=" + UPFIELDS,
    UP_LIC, check_uniprot, "version = X-UniProt-Release / X-UniProt-Release-Date response headers")
add("unknome/unknome_protein_table_18_Mar_2026.tsv.gz", "Unknome (Rocha et al. 2023 PLoS Biol 21:e3002222)",
    "https://unknome.mrc-lmb.cam.ac.uk/download/prot_tsv_gz/18_Mar_2026/", UNK_LIC, check_unknome_protein,
    "protein summary, all species; release 18 Mar 2026")
add("unknome/unknome_cluster_table_18_Mar_2026.tsv.gz", "Unknome (Rocha et al. 2023 PLoS Biol 21:e3002222)",
    "https://unknome.mrc-lmb.cam.ac.uk/download/clust_tsv_gz/18_Mar_2026/", UNK_LIC, lambda p: check_tsv_generic(p, "cluster"),
    "cluster (knownness score) summary; release 18 Mar 2026")
add("tcrd/PharosTCRD_UniProt_Mapping.tsv", "IDG / TCRD (Pharos) TDL", "https://unmtid-dbs.net/download/TCRD/PharosTCRD_UniProt_Mapping.tsv",
    TCRD_LIC, lambda p: check_tsv_generic(p, "tcrd", "TDL"),
    "UniProt->TDL; file dated 2023-07-11 (TCRD v6.13.x; latest.README says v6.13.4, 2022-09-08). Older than the live Pharos site; version=HTTP Last-Modified")
add("tcrd/latest.README", "IDG / TCRD", "https://unmtid-dbs.net/download/TCRD/latest.README", TCRD_LIC, check_text, "release notes")
add("tcrd/README", "IDG / TCRD", "https://unmtid-dbs.net/download/TCRD/README", TCRD_LIC, check_text, "download-dir README (licence statement)")
add("reactome/UniProt2Reactome_All_Levels.txt", "Reactome", "https://reactome.org/download/current/UniProt2Reactome_All_Levels.txt", REACT_LIC,
    check_reactome, "version = HTTP Last-Modified of /download/current/ (Reactome release number not in file)")


def main():
    rows, sections = [], []
    for e in FILES:
        path = os.path.join(RAW, e["rel"])
        if not os.path.exists(path):
            sections.append(f"### {e['rel']}\n\nMISSING (not downloaded)\n")
            continue
        h = headers_of(e["rel"])
        sz = os.path.getsize(path)
        digest = sha256(path)
        ver, lines = e["fn"](path)
        parts = []
        if ver:
            parts.append(ver)
        if "x-uniprot-release" in h:
            parts.append(f"UniProt release {h['x-uniprot-release']} ({h.get('x-uniprot-release-date', '')})")
        if "last-modified" in h and not parts:
            parts.append("Last-Modified " + h["last-modified"])
        elif "last-modified" in h:
            parts.append("HTTP Last-Modified " + h["last-modified"])
        if e["rel"].startswith("go/") and "archive" in e["rel"] and e["rel"].endswith(".gz"):
            parts.insert(0, "GO release " + e["rel"].split("/")[2])
        if e["rel"].endswith("goa_human.gaf.gz") and "current" in e["rel"]:
            parts.insert(0, "GAF header date-generated " + (ver or ""))
        version = "; ".join(parts) or "n/a"
        if e["rel"].startswith("unknome"):
            version = "Unknome DB build 18 Mar 2026"
        if e["rel"] == "ncbi_gene/gene2pubmed_9606.tsv":
            version = "derived from gene2pubmed.gz (see parent)"
        rows.append([e["rel"].join(["data/raw/", ""]), e["source"], e["url"], version, digest, sz, e["lic"], e["notes"]])
        sections.append(f"### data/raw/{e['rel']}\n\n- size: {sz:,} bytes; sha256 `{digest}`\n- version: {version}\n" +
                        "\n".join(f"- {l}" for l in lines) + "\n")
        print("done", e["rel"], file=sys.stderr)

    # attempted-but-unavailable sources
    unavailable = [
        ["(none)", "CORUM 5.x", "https://mips.helmholtz-muenchen.de/corum/", "NOT DOWNLOADED", "", "", "CC BY-NC 4.0 historically (unverified)",
         "TLS certificate of mips.helmholtz-muenchen.de not trusted by system CA store (curl 'unknown CA'); download page appears to be JS-driven. Not fetched; certificate verification deliberately not disabled. Retry manually from a browser."],
        ["(none)", "Pharos/TCRD full SQL dump (latest.sql.gz)", "https://unmtid-dbs.net/download/TCRD/latest.sql.gz", "NOT DOWNLOADED", "", 7400000000, TCRD_LIC,
         "7.4 GB MySQL dump (2023-07-11); not needed because TDL-per-UniProt TSV obtained. Pharos web/GraphQL (pharos-api.ncats.io) was not queried; live TDLs may be newer than the 2023 TSV."],
    ]
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["file", "source", "url", "version", "sha256", "size_bytes", "licence", "notes"])
        w.writerows(rows + unavailable)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("# Annotation data sanity checks\n\nGenerated by `scripts/01b_check_annotation_data.py`. "
                "Line/row counts, headers, and number of human genes/proteins per file.\n\n")
        f.write("\n".join(sections))
        f.write("\n### Not downloaded\n\n" + "\n".join(f"- {u[1]}: {u[7]}" for u in unavailable) + "\n")


if __name__ == "__main__":
    main()
