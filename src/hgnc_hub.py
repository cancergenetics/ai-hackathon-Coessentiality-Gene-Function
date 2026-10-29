"""hgnc_hub.py -- identifier hub keyed on hgnc_id (DESIGN.md v2 §2.1).

One row per HGNC *Approved* record (all locus groups; ``in_universe`` marks the protein-coding universe):
hgnc_id, symbol, locus_group, prev_symbols, alias_symbols, entrez_id, uniprot_ids, ensembl_gene_id,
depmap_column (CRISPRGeneEffect.csv column whose Entrez equals the gene's Entrez; header line only),
depmap_symbol_differs, tool_mapped_uniprot (HGNC accessions the co-essentiality tool maps uniquely to this gene's
DepMap column, rule of external/coessentiality/mvp/src/coessential/data.py::build_uniprot_map), tool_ambiguous_uniprot,
scorable (depmap_column present AND >= 1 tool-mapped accession), Ensembl 116 coordinates (by ENSG), and collision flags:
  symbol_collides_prev_alias -- the approved symbol is also a previous symbol or alias of another Approved gene;
  prev_alias_ambiguous       -- one of the gene's previous symbols / aliases is the approved symbol, previous symbol
                                or alias of another Approved gene (symbol lookups through it are ambiguous);
  uniprot_shared             -- one of its UniProt accessions is listed by another Approved gene;
  entrez_duplicated / ensembl_duplicated.
Symbols are never used for joins when an ID exists; the flags say where a symbol-only lookup would be unsafe.

Run: .env/bin/python -I src/hgnc_hub.py   (writes results/ids/hgnc_hub.tsv and results/ids/hgnc_hub_qc.md)
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT_TSV = os.path.join(ROOT, "results", "ids", "hgnc_hub.tsv")
OUT_QC = os.path.join(ROOT, "results", "ids", "hgnc_hub_qc.md")
PRIMARY_CHROMS = [str(i) for i in range(1, 23)] + ["X", "Y", "MT"]


def _split(s, sep="|"):
    if not isinstance(s, str) or not s:
        return []
    return [x.strip() for x in s.split(sep) if x.strip()]


def parse_depmap_column(col: str):
    m = re.match(r"^(.*) \((\d+)\)$", col.strip().strip('"'))
    return (m.group(1), m.group(2)) if m else (None, None)


def depmap_header(path: str) -> list[str]:
    with open(path) as f:
        return f.readline().rstrip("\n").split(",")[1:]  # header ONLY


def tool_uniprot_map(hgnc_approved: pd.DataFrame, depmap_cols: list[str]) -> pd.DataFrame:
    """Re-implementation of the tool's deterministic UniProt -> DepMap column rule (data.py, steps 1-4):
    accession -> Entrez ids of all Approved HGNC rows listing it -> intersect with DepMap Entrez ->
    exactly one: 'mapped'; none: 'not_in_depmap'; several: 'ambiguous'. (Rows lacking entrez_id are dropped first,
    as the tool's ``dropna`` on [entrez_id, uniprot_ids] does.)"""
    m = hgnc_approved[["entrez_id", "uniprot_ids"]].dropna().copy()
    m["uniprot"] = m.uniprot_ids.str.split("|")
    m = m.explode("uniprot")
    cand = m.groupby("uniprot").entrez_id.apply(lambda s: sorted(set(s)))
    ent2col = {}
    for c in depmap_cols:
        _, e = parse_depmap_column(c)
        if e:
            ent2col[e] = c
    rows = []
    for u, c in cand.items():
        indep = [e for e in c if e in ent2col]
        st = "not_in_depmap" if not indep else ("ambiguous" if len(indep) > 1 else "mapped")
        rows.append(dict(uniprot=u, status=st, entrez=indep[0] if st == "mapped" else "",
                         column=ent2col[indep[0]] if st == "mapped" else "",
                         candidates_in_depmap="|".join(indep)))
    return pd.DataFrame(rows)


def build_hub(hgnc_path: str, depmap_path: str, ens_coord_path: str | None = None) -> tuple[pd.DataFrame, dict]:
    h = pd.read_csv(hgnc_path, sep="\t", dtype=str, low_memory=False)
    ap = h[h.status == "Approved"].reset_index(drop=True)
    qc = {"hgnc_approved": len(ap), "hgnc_protein_coding": int((ap.locus_group == "protein-coding gene").sum())}
    hub = pd.DataFrame({
        "hgnc_id": ap.hgnc_id, "symbol": ap.symbol, "locus_group": ap.locus_group, "locus_type": ap.locus_type,
        "location": ap.location.fillna(""),
        "prev_symbols": ap.prev_symbol.fillna(""), "alias_symbols": ap.alias_symbol.fillna(""),
        "entrez_id": ap.entrez_id.fillna(""), "uniprot_ids": ap.uniprot_ids.fillna(""),
        "ensembl_gene_id": ap.ensembl_gene_id.fillna(""), "gene_group": ap.gene_group.fillna(""),
        "gene_group_id": ap.gene_group_id.fillna(""),
    })
    hub["in_universe"] = hub.locus_group == "protein-coding gene"

    # ---------------------------------------------------------------- DepMap (Entrez)
    cols = depmap_header(depmap_path)
    ent2col, sym_of_col, n_unparsed = {}, {}, 0
    for c in cols:
        s, e = parse_depmap_column(c)
        if e is None:
            n_unparsed += 1
            continue
        ent2col[e] = c
        sym_of_col[c] = s
    hub["depmap_column"] = hub.entrez_id.map(ent2col).fillna("")
    hub["depmap_symbol_differs"] = [(c != "" and sym_of_col.get(c) != s) for c, s in
                                    zip(hub.depmap_column, hub.symbol)]
    hub_ent = set(hub.entrez_id[hub.entrez_id != ""])
    qc.update(depmap_columns=len(cols), depmap_unparsed=n_unparsed,
              depmap_columns_mapped=int(sum(e in hub_ent for e in ent2col)),
              depmap_columns_unmapped=sorted(c for e, c in ent2col.items() if e not in hub_ent),
              depmap_universe_genes=int((hub.in_universe & (hub.depmap_column != "")).sum()),
              depmap_nonuniverse_genes=int((~hub.in_universe & (hub.depmap_column != "")).sum()),
              depmap_symbol_differs=int(hub.depmap_symbol_differs.sum()))

    # ---------------------------------------------------------------- tool UniProt mapping -> scorable
    um = tool_uniprot_map(ap, cols)
    mapped = um[um.status == "mapped"].groupby("column").uniprot.apply(lambda s: "|".join(sorted(s)))
    hub["tool_mapped_uniprot"] = hub.depmap_column.map(mapped).fillna("")
    amb = set(um.uniprot[um.status == "ambiguous"])
    hub["tool_ambiguous_uniprot"] = hub.uniprot_ids.map(lambda s: "|".join(a for a in _split(s) if a in amb))
    hub["scorable"] = (hub.depmap_column != "") & (hub.tool_mapped_uniprot != "")
    qc.update(tool_accessions=len(um), **{f"tool_acc_{k}": int(v) for k, v in um.status.value_counts().items()},
              scorable_universe=int((hub.scorable & hub.in_universe).sum()),
              depmap_universe_not_scorable=int((hub.in_universe & (hub.depmap_column != "") & ~hub.scorable).sum()))

    # ---------------------------------------------------------------- collisions
    owners = defaultdict(set)  # token -> hgnc ids using it as approved / prev / alias
    for hid, s, p, a in zip(hub.hgnc_id, hub.symbol, hub.prev_symbols, hub.alias_symbols):
        for t in [s] + _split(p) + _split(a):
            owners[t.upper()].add(hid)
    approved = defaultdict(set)
    for hid, s in zip(hub.hgnc_id, hub.symbol):
        approved[s.upper()].add(hid)
    hub["symbol_collides_prev_alias"] = [len(owners[s.upper()] - {hid}) > 0 for hid, s in zip(hub.hgnc_id,
                                                                                               hub.symbol)]
    hub["prev_alias_ambiguous"] = [any(len(owners[t.upper()] - {hid}) > 0 for t in _split(p) + _split(a))
                                   for hid, p, a in zip(hub.hgnc_id, hub.prev_symbols, hub.alias_symbols)]
    acc_owner = defaultdict(set)
    for hid, u in zip(hub.hgnc_id, hub.uniprot_ids):
        for a in _split(u):
            acc_owner[a].add(hid)
    hub["uniprot_shared"] = [any(len(acc_owner[a]) > 1 for a in _split(u)) for u in hub.uniprot_ids]
    ent = hub.entrez_id[hub.entrez_id != ""]
    hub["entrez_duplicated"] = hub.entrez_id.isin(set(ent[ent.duplicated()]))
    ens = hub.ensembl_gene_id[hub.ensembl_gene_id != ""]
    hub["ensembl_duplicated"] = hub.ensembl_gene_id.isin(set(ens[ens.duplicated()]))
    u = hub[hub.in_universe]
    for c in ["symbol_collides_prev_alias", "prev_alias_ambiguous", "uniprot_shared", "entrez_duplicated",
              "ensembl_duplicated"]:
        qc[f"universe_{c}"] = int(u[c].sum())
    qc.update(universe_no_entrez=int((u.entrez_id == "").sum()), universe_no_uniprot=int((u.uniprot_ids == "").sum()),
              universe_no_ensembl=int((u.ensembl_gene_id == "").sum()),
              universe_multi_uniprot=int(u.uniprot_ids.str.contains(r"\|").sum()))

    # ---------------------------------------------------------------- Ensembl 116 coordinates (by ENSG)
    if ens_coord_path:
        ec = pd.read_csv(ens_coord_path, sep="\t", dtype=str)
        ec.columns = ["ensg", "ens_name", "ens_entrez", "chrom", "start", "end"]
        ec = ec[ec.chrom.isin(PRIMARY_CHROMS)].drop_duplicates("ensg")
        ec = ec.set_index("ensg")
        hub["ens_chrom"] = hub.ensembl_gene_id.map(ec.chrom).fillna("")
        hub["ens_start"] = pd.to_numeric(hub.ensembl_gene_id.map(ec.start), errors="coerce").astype("Int64")
        hub["ens_end"] = pd.to_numeric(hub.ensembl_gene_id.map(ec.end), errors="coerce").astype("Int64")
        qc["universe_ensg_with_ens116_coords"] = int((u.ensembl_gene_id.map(lambda x: x in ec.index)).sum())
        qc["universe_ensg_without_ens116_coords"] = int(((u.ensembl_gene_id != "") &
                                                         ~u.ensembl_gene_id.map(lambda x: x in ec.index)).sum())
    return hub, qc


def write_qc(qc: dict, path: str) -> None:
    lines = ["# HGNC identifier hub -- mapping QC", "",
             "Generated by `src/hgnc_hub.py` from HGNC `hgnc_complete_set.txt` (Approved records), the DepMap 26Q3 "
             "`CRISPRGeneEffect.csv` header (line 1 only; no values) and Ensembl 116 gene coordinates. Join keys: "
             "Entrez (DepMap), UniProt (tool rule), ENSG (Ensembl). Symbols are never join keys.", "",
             "| quantity | value |", "|---|---|"]
    for k, v in qc.items():
        if isinstance(v, list):
            v = f"{len(v)}: " + ", ".join(v[:80]) + (" ..." if len(v) > 80 else "")
        lines.append(f"| {k} | {v} |")
    lines += ["", "Definitions: `scorable` = DepMap column (Entrez match) and >= 1 HGNC UniProt accession that the "
              "tool's rule maps uniquely to that column (status 'mapped'); accessions listed by several genes that are "
              "all in DepMap are 'ambiguous' and not scored by the tool. `tool_acc_*` count accessions by status. "
              "`depmap_columns_unmapped` are DepMap columns whose Entrez is not an Approved HGNC Entrez id."]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
    hub, qc = build_hub(os.path.join(RAW, "hgnc", "hgnc_complete_set.txt"),
                        os.path.join(RAW, "depmap", "CRISPRGeneEffect.csv"),
                        os.path.join(RAW, "ensembl", "ensembl116_gene_coordinates.tsv"))
    assert hub.hgnc_id.is_unique
    hub.to_csv(OUT_TSV, sep="\t", index=False)
    write_qc(qc, OUT_QC)
    print(f"wrote {OUT_TSV} ({len(hub)} rows); QC -> {OUT_QC}")
    for k, v in qc.items():
        print(k, len(v) if isinstance(v, list) else v)


if __name__ == "__main__":
    sys.exit(main())
