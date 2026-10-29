"""Toy tests with hand-worked answers for src/knownness.py, src/hgnc_hub.py and the statistics / helpers in
scripts/03_build_preregistration.py and scripts/04_holdout_sizing.py.

Run: .env/bin/python -I -m pytest -q tests/test_prereg_modules.py
"""
import importlib.util
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import hgnc_hub, knownness as kn  # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s03 = _load("s03", "scripts/03_build_preregistration.py")
s04 = _load("s04", "scripts/04_holdout_sizing.py")

# ------------------------------------------------------------------------------------------------ toy ontology
# BP: root 8150 <- 1 <- 2 ; 3 part_of 1 ; 4 obsolete replaced_by 2 ; 5 obsolete (consider 3, no replaced_by)
#     alt_id GO:0000099 -> GO:0000002 ; 6 obsolete replaced_by 4 (chain -> 2)
# MF: root 3674 <- binding 5488 <- protein binding 5515 ; 10 is_a 3674 ; 11 is_a 10
TOY_OBO = """format-version: 1.2
data-version: releases/2099-01-01

[Term]
id: GO:0008150
name: biological_process
namespace: biological_process

[Term]
id: GO:0000001
name: proc one
namespace: biological_process
is_a: GO:0008150 ! biological_process

[Term]
id: GO:0000002
name: proc two
namespace: biological_process
alt_id: GO:0000099
is_a: GO:0000001 ! proc one

[Term]
id: GO:0000003
name: proc three
namespace: biological_process
relationship: part_of GO:0000001 ! proc one

[Term]
id: GO:0000004
name: obsolete proc four
namespace: biological_process
is_obsolete: true
replaced_by: GO:0000002

[Term]
id: GO:0000005
name: obsolete proc five
namespace: biological_process
is_obsolete: true
consider: GO:0000003

[Term]
id: GO:0000006
name: obsolete proc six
namespace: biological_process
is_obsolete: true
replaced_by: GO:0000004

[Term]
id: GO:0000007
name: proc seven regulates one
namespace: biological_process
is_a: GO:0008150
relationship: regulates GO:0000001

[Term]
id: GO:0003674
name: molecular_function
namespace: molecular_function

[Term]
id: GO:0005488
name: binding
namespace: molecular_function
is_a: GO:0003674

[Term]
id: GO:0005515
name: protein binding
namespace: molecular_function
is_a: GO:0005488

[Term]
id: GO:0000010
name: func ten
namespace: molecular_function
is_a: GO:0003674

[Term]
id: GO:0000011
name: func eleven
namespace: molecular_function
is_a: GO:0000010

[Term]
id: GO:0005575
name: cellular_component
namespace: cellular_component

[Term]
id: GO:0000100
name: comp hundred
namespace: cellular_component
is_a: GO:0005575

[Typedef]
id: part_of
name: part of
"""


def gl(acc, qual, go, ev, aspect, ref="PMID:1", db="UniProtKB"):
    return "\t".join([db, acc, "SYM", qual, go, ref, ev, "", aspect, "n", "", "protein", "taxon:9606", "20200101",
                      "UniProt", "", ""])


@pytest.fixture(scope="module")
def onto():
    return kn.GoOntology.from_obo(TOY_OBO)


ACC = {"P1": {"G1"}, "P2": {"G2"}, "P3": {"G3"}, "P4": {"G4"}, "P5": {"G5"}, "P6": {"G6"}, "P7": {"G7"},
       "P8": {"G8"}, "P9": {"G9", "G10"}}


# ===================================================================================== ontology resolution
def test_resolve_and_ancestors(onto):
    assert onto.release == "releases/2099-01-01"
    assert onto.resolve("GO:0000002") == ("GO:0000002", "primary")
    assert onto.resolve("GO:0000099") == ("GO:0000002", "alt_id")
    assert onto.resolve("GO:0000004") == ("GO:0000002", "replaced_by")
    assert onto.resolve("GO:0000006") == ("GO:0000002", "replaced_by")  # chain 6 -> 4 -> 2
    assert onto.resolve("GO:0000005") == (None, "obsolete_dropped")    # consider is not followed
    assert onto.resolve("GO:9999999") == (None, "unknown_dropped")
    assert onto.ancestors("GO:0000002") == {"GO:0000002", "GO:0000001", "GO:0008150"}
    assert onto.ancestors("GO:0000003") == {"GO:0000003", "GO:0000001", "GO:0008150"}  # part_of followed
    assert onto.ancestors("GO:0000007") == {"GO:0000007", "GO:0008150"}  # regulates NOT followed
    assert onto.namespace("GO:0000011") == "molecular_function"


# ===================================================================================== D1
TOY_GAF = "\n".join([
    "!gaf-version: 2.2",
    gl("P1", "involved_in", "GO:0000001", "IMP", "P"),          # G1: informative EXP-class -> known
    gl("P2", "involved_in", "GO:0000001", "TAS", "P"),          # G2: TAS counts -> known
    gl("P3", "involved_in", "GO:0000001", "HMP", "P"),          # G3: HTP code ignored
    gl("P3", "enables", "GO:0000010", "IEA", "F"),              #     IEA ignored
    gl("P3", "enables", "GO:0000010", "ISS", "F"),              #     ISS ignored
    gl("P3", "enables", "GO:0000010", "IBA", "F"),              #     IBA ignored
    gl("P3", "enables", "GO:0000010", "NAS", "F"),              #     NAS ignored -> G3 is D1
    gl("P4", "enables", "GO:0005515", "IPI", "F"),              # G4: protein binding only (generic)
    gl("P4", "enables", "GO:0005488", "IDA", "F"),              #     binding (generic)
    gl("P4", "located_in", "GO:0000100", "IDA", "C"),           #     CC only -> G4 is D1
    gl("P5", "NOT|enables", "GO:0000010", "IDA", "F"),          # G5: NOT (GAF 2.2) -> excluded
    gl("P5", "NOT", "GO:0000001", "IMP", "P"),                  #     NOT (GAF 2.1) -> excluded -> D1
    gl("P6", "contributes_to", "GO:0000011", "IDA", "F"),       # G6: contributes_to counts -> known
    gl("P7", "involved_in", "GO:0000099", "IGI", "P"),          # G7: alt id -> GO:0000002 informative -> known
    gl("P8-2", "enables", "GO:0000010", "IC", "F"),             # G8: isoform accession + IC -> known
    gl("P9", "enables", "GO:0000010", "EXP", "F"),              # G9 & G10 share accession -> both known
    gl("PX", "enables", "GO:0000010", "IDA", "F"),              # unmapped accession
])


def test_d1_flags(onto):
    universe = [f"G{i}" for i in range(1, 12)]  # G11 has no rows -> D1
    pg, ann, st = kn.d1(TOY_GAF, onto, "toy", ACC, universe=universe)
    d1 = pg.D1.to_dict()
    assert d1 == {"G1": False, "G2": False, "G3": True, "G4": True, "G5": True, "G6": False, "G7": False,
                  "G8": False, "G9": False, "G10": False, "G11": True}
    assert pg.at["G4", "n_d1_terms_generic"] == 2 and pg.at["G4", "n_d1_terms_informative"] == 0
    assert pg.at["G7", "d1_terms"] == "GO:0000002"
    assert st["not_rows_removed"] == 2
    assert st["rows_unmapped"] == 1
    assert st["rows_alt_id"] == 1


def test_d1_same_function_any_release(onto):
    """t0 call uses the same code path; a GAF 2.1 file (NOT without relation) behaves identically."""
    g21 = TOY_GAF.replace("!gaf-version: 2.2", "!gaf-version: 2.1").replace("NOT|enables", "NOT")
    a, _, _ = kn.d1(TOY_GAF, onto, "r1", ACC, universe=["G1", "G5"])
    b, _, _ = kn.d1(g21, onto, "r0", ACC, universe=["G1", "G5"])
    assert a.D1.tolist() == b.D1.tolist() == [False, True]
    assert set(a.release) == {"r1"} and set(b.release) == {"r0"}


def test_generic_list_contains_design_terms():
    for t in ["GO:0005515", "GO:0005488", "GO:0042802", "GO:0042803", "GO:0003674", "GO:0008150", "GO:0005575"]:
        assert t in kn.GENERIC
    assert kn.D1_EVIDENCE == {"EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC"}


# ===================================================================================== propagation / targets
def test_strict_mapping_and_propagation(onto):
    gaf = "\n".join([
        gl("P1", "involved_in", "GO:0000004", "IMP", "P"),   # obsolete -> replaced_by GO:0000002
        gl("P1", "involved_in", "GO:0000005", "IMP", "P"),   # obsolete, no replacement -> dropped
        gl("P2", "involved_in", "GO:0000099", "IDA", "P"),   # alt id -> GO:0000002
        gl("P2", "involved_in", "GO:0000003", "IDA", "P"),
    ])
    ann, st = kn.d1_annotations(gaf, onto, ACC, resolve_mode="strict")
    assert st["rows_obsolete_dropped"] == 1 and st["terms_obsolete_dropped"] == 1
    assert st["rows_replaced_by"] == 1 and st["rows_alt_id"] == 1
    prop = kn.propagate_annotations(ann, onto)
    assert prop["G1"] == {"GO:0000002", "GO:0000001", "GO:0008150"}
    assert prop["G2"] == {"GO:0000002", "GO:0000003", "GO:0000001", "GO:0008150"}


def test_target_set_difference(onto):
    cur = {"G1": frozenset({"GO:0000002", "GO:0000001", "GO:0008150", "GO:0000011", "GO:0000010", "GO:0003674",
                            "GO:0005515", "GO:0005488"}),
           "G2": frozenset({"GO:0000001", "GO:0008150"})}
    t0 = {"G1": frozenset({"GO:0000001", "GO:0008150"}), "G2": frozenset({"GO:0000001", "GO:0008150"})}
    sizes = pd.Series({"GO:0000002": 10, "GO:0000001": 50, "GO:0000011": 3, "GO:0000010": 300,
                       "GO:0005515": 100, "GO:0005488": 100, "GO:0008150": 1000, "GO:0003674": 1000})
    T = kn.target_sets(cur, t0, ["G1", "G2", "G3"], sizes, 5, 200, onto=onto)
    # G1: new = {2, 11, 10, 3674, 5515, 5488}; generic removed -> {2, 11, 10}; size window -> {2}
    assert T["G1"] == {"GO:0000002"}
    assert T["G2"] == set() and T["G3"] == set()
    # window edges inclusive
    T2 = kn.target_sets(cur, t0, ["G1"], sizes, 3, 300, onto=onto)
    assert T2["G1"] == {"GO:0000002", "GO:0000011", "GO:0000010"}


def test_term_sizes_and_supporting_rows(onto):
    prop = {"A": frozenset({"x", "y"}), "B": frozenset({"x"}), "C": frozenset({"y"})}
    s = kn.term_sizes(prop, ["A", "B"])
    assert s["x"] == 2 and s["y"] == 1
    ann = pd.DataFrame({"hgnc_id": ["G1", "G1", "G2"], "go_id": ["GO:0000002", "GO:0000003", "GO:0000002"],
                        "reference": ["PMID:5|GO_REF:1", "PMID:7", "PMID:9"]})
    sup = kn.supporting_rows(ann, onto, "G1", "GO:0000001")
    assert len(sup) == 2
    assert kn.pmids_from_refs(sup.reference) == [5, 7]
    assert len(kn.supporting_rows(ann, onto, "G1", "GO:0000003")) == 1


# ===================================================================================== PMIDs / D2 / D3
def test_pmid_cutoff_logic():
    # PMID 100 linked to 11 genes (not focused); 200 to gene 1 only; 300 to genes 1,2; 400 to gene 1
    rows = [(9606, g, 100) for g in range(1, 12)] + [(9606, 1, 200), (9606, 1, 300), (9606, 2, 300),
                                                     (9606, 1, 400), (9606, 1, 400)]
    g2p = pd.DataFrame(rows, columns=["tax_id", "GeneID", "PubMed_ID"])
    c = kn.focused_pmid_counts(g2p, max_genes=10)
    assert c[1] == 3 and c[2] == 1 and 3 not in c.index
    c = kn.focused_pmid_counts(g2p, max_genes=10, pmid_lt=300)       # strictly below the cut-off
    assert c[1] == 1 and 2 not in c.index
    c = kn.focused_pmid_counts(g2p, max_genes=10, pmid_lt=301)
    assert c[1] == 2 and c[2] == 1
    c = kn.focused_pmid_counts(g2p, max_genes=None)
    assert c[1] == 4 and c[3] == 1


def test_d2_d3_and_u():
    pc = pd.DataFrame({"hgnc_id": ["H1", "H2", "H3", "H4"], "entrez_id": ["1", "2", "3", "4"],
                       "uniprot_ids": ["Q1", "Q2", "Q3|Q3b", None]})
    up = pd.DataFrame({"Entry": ["Q1", "Q2", "Q3", "Q3b"], "HGNC": ["H1;", "", "H3;", "H3;"],
                       "Annotation": ["2", "3", "5", "1"]})
    d2, st = kn.d2(up, pc)
    assert d2.D2.tolist() == [True, False, False, False]          # H3 max(5,1)=5; H4 no entry -> False
    assert st["by_accession"] == 1 and st["genes_no_reviewed_entry"] == 1
    g2p = pd.DataFrame([(9606, 1, p) for p in range(11)] + [(9606, 2, 999)], columns=["tax_id", "GeneID",
                                                                                      "PubMed_ID"])
    tc = pd.DataFrame({"UniProt_accession": ["Q1", "Q2", "Q3", "Q3b"], "TDL": ["Tbio", "Tdark", "Tdark", "Tchem"]})
    acc = {"Q1": {"H1"}, "Q2": {"H2"}, "Q3": {"H3"}, "Q3b": {"H3"}}
    d3 = kn.d3(g2p, tc, pc, acc)
    assert d3.n_pubmed_focused.tolist() == [11, 1, 0, 0]
    assert d3.tdl.tolist() == ["Tbio", "Tdark", "Tchem", ""]
    assert d3.D3.tolist() == [False, True, True, True]
    u = kn.combine_u(pd.Series([True, True, False, True]), d2.D2.reset_index(drop=True),
                     d3.D3.reset_index(drop=True))
    assert u.tolist() == [True, True, False, True]


# ===================================================================================== ID hub / scorable
def test_tool_uniprot_map():
    hg = pd.DataFrame({"entrez_id": ["1", "2", "3", "4", None], "uniprot_ids": ["A", "B|S", "S", "C", "D"]})
    cols = ["G1 (1)", "G2 (2)", "G3 (3)"]
    m = hgnc_hub.tool_uniprot_map(hg, cols).set_index("uniprot")
    assert m.at["A", "status"] == "mapped" and m.at["A", "column"] == "G1 (1)"
    assert m.at["S", "status"] == "ambiguous"        # shared by two DepMap genes
    assert m.at["C", "status"] == "not_in_depmap"
    assert "D" not in m.index                        # no Entrez -> dropped as in the tool


def test_build_hub_scorable(tmp_path):
    h = tmp_path / "hgnc.txt"
    h.write_text("\t".join(["hgnc_id", "symbol", "locus_group", "locus_type", "status", "location", "prev_symbol",
                            "alias_symbol", "entrez_id", "uniprot_ids", "ensembl_gene_id", "gene_group",
                            "gene_group_id"]) + "\n" +
                 "HGNC:1\tAAA\tprotein-coding gene\tgene\tApproved\t1p\tOLD1\tBBB\t1\tA\tENSG1\t\t\n"
                 "HGNC:2\tBBB\tprotein-coding gene\tgene\tApproved\t1p\t\t\t2\tS\tENSG2\t\t\n"
                 "HGNC:3\tCCC\tprotein-coding gene\tgene\tApproved\t1p\t\t\t3\tS\tENSG3\t\t\n"
                 "HGNC:4\tDDD\tprotein-coding gene\tgene\tApproved\t1p\t\t\t4\t\tENSG4\t\t\n")
    d = tmp_path / "dep.csv"
    d.write_text("ModelID,AAA (1),BBB (2),CCC (3),XDD (4)\nACH-1,0,0,0,0\n")
    hub, qc = hgnc_hub.build_hub(str(h), str(d))
    hub = hub.set_index("symbol")
    assert hub.scorable.to_dict() == {"AAA": True, "BBB": False, "CCC": False, "DDD": False}
    assert hub.at["DDD", "depmap_symbol_differs"]
    assert hub.at["BBB", "symbol_collides_prev_alias"]   # BBB is an alias of AAA
    assert hub.at["AAA", "prev_alias_ambiguous"]
    assert hub.at["BBB", "uniprot_shared"] and not hub.at["AAA", "uniprot_shared"]


# ===================================================================================== strata helpers
def test_tandem_counts(tmp_path):
    par = tmp_path / "par.tsv"
    par.write_text("Gene stable ID\tGene name\tHuman paralogue gene stable ID\tn\tp1\tp2\ttype\tlca\n"
                   "ENSG01\ta\tENSG02\tb\t1\t1\twithin_species_paralog\tx\n"
                   "ENSG01\ta\tENSG03\tc\t1\t1\tother_paralog\tx\n"
                   "ENSG01\ta\tENSG04\td\t1\t1\twithin_species_paralog\tx\n"
                   "ENSG02\tb\tENSG01\ta\t1\t1\twithin_species_paralog\tx\n[success]\n")
    co = tmp_path / "co.tsv"
    co.write_text("Gene stable ID\tGene name\tNCBI\tChromosome/scaffold name\tGene start (bp)\tGene end (bp)\n"
                  "ENSG01\ta\t\t19\t1000000\t1010000\n"
                  "ENSG02\tb\t\t19\t2010000\t2020000\n"   # gap 1,000,000 -> within (inclusive)
                  "ENSG03\tc\t\t19\t1500000\t1600000\n"
                  "ENSG04\td\t\t1\t1000000\t1010000\n")    # other chromosome
    ens = pd.Series(["ENSG01", "ENSG02", "ENSG05"])
    assert s03.tandem_counts(ens, str(par), str(co), None).tolist() == [2, 1, 0]
    assert s03.tandem_counts(ens, str(par), str(co), ("within_species_paralog",)).tolist() == [1, 1, 0]


def test_chemo_groups():
    f, used = s03.chemo_groups(pd.Series(["Olfactory receptors, family 2", "Keratin associated proteins|X",
                                          "Olfactomedin domain containing ", "Late cornified envelope proteins", ""]))
    assert f.tolist() == [True, True, False, True, False]
    assert used == ["Keratin associated proteins", "Late cornified envelope proteins",
                    "Olfactory receptors, family 2"]


# ===================================================================================== hold-out statistics
def test_mde_inverts_connor():
    for n, psi in [(820, 0.1), (300, 0.2), (539, 0.2)]:
        d = s04.mde(n, psi)
        assert math.isclose(s04.connor_n(d, psi), n, rel_tol=1e-6)
    # textbook value: psi=0.2, delta=0.1, alpha .05 two-sided, power .8 -> n ~ 155 (Connor 1987)
    assert 150 < s04.connor_n(0.1, 0.2) < 160
    assert s04.mde(1000, 0.1) < s04.mde(100, 0.1)


def test_clusters_and_design_effect():
    cl = s04.clusters_from_pmids({"a": {1}, "b": {1, 2}, "c": {2}, "d": {3}, "e": set()})
    assert cl["a"] == cl["b"] == cl["c"] and len({cl["a"], cl["d"], cl["e"]}) == 3
    deff, ne = s04.design_effect([3, 1, 1], 1.0)        # m_w = 11/5 = 2.2 -> deff 2.2, n_eff 5/2.2
    assert math.isclose(deff, 2.2) and math.isclose(ne, 5 / 2.2)
    assert s04.design_effect([1, 1, 1], 1.0) == (1.0, 3.0)
    assert math.isclose(s04.design_effect([3, 1, 1], 0.0)[1], 5.0)
