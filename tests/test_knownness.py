"""Toy-data unit tests for scripts/02_gene_knownness_table.py (GAF parsing / evidence filtering / gene mapping,
focused-PMID counting, symbol patterns). Every expected value is worked out by hand in the comments.

Run: .env/bin/python -I -m pytest -q tests/test_knownness.py
"""
import importlib.util
import io
import os

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("kn", os.path.join(ROOT, "scripts", "02_gene_knownness_table.py"))
kn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kn)


def gaf_line(acc, sym, qual, go, ev, aspect, db="UniProtKB"):
    cols = [db, acc, sym, qual, go, "PMID:1", ev, "", aspect, "name", "", "protein", "taxon:9606", "20200101",
            "UniProt", "", ""]
    return "\t".join(cols)


# Genes: G1 (acc P1), G2 (acc P2 and P2b), G3 (no accession in map -> symbol fallback "SYM3"), G4 (shares P4 w/ G5)
TOY_GAF = "\n".join([
    "!gaf-version: 2.2",
    "!a comment line",
    # G1: exp BP x2 distinct terms (one duplicated with another code), MF protein binding (uninformative),
    #     MF informative IDA, NOT-qualified MF (must be ignored), IBA BP, IEA MF, ND for BP
    gaf_line("P1", "SYM1", "involved_in", "GO:0000001", "IMP", "P"),
    gaf_line("P1", "SYM1", "involved_in", "GO:0000001", "IDA", "P"),        # same term -> still 1 distinct
    gaf_line("P1", "SYM1", "involved_in", "GO:0000002", "HMP", "P"),        # HTP exp term
    gaf_line("P1", "SYM1", "enables", "GO:0005515", "IPI", "F"),            # protein binding -> uninformative
    gaf_line("P1", "SYM1", "enables", "GO:0000010", "IDA", "F"),
    gaf_line("P1", "SYM1", "NOT|enables", "GO:0000011", "IDA", "F"),        # NOT -> excluded
    gaf_line("P1", "SYM1", "involved_in", "GO:0000003", "IBA", "P"),
    gaf_line("P1", "SYM1", "enables", "GO:0000012", "IEA", "F"),
    gaf_line("P1", "SYM1", "involved_in", "GO:0008150", "ND", "P"),
    gaf_line("P1", "SYM1", "located_in", "GO:0000100", "IDA", "C"),
    # G2 via isoform accession P2-2 and via secondary accession P2b; alt id GO:9999999 -> GO:0000020
    gaf_line("P2-2", "SYM2", "enables", "GO:0000020", "EXP", "F"),
    gaf_line("P2b", "SYM2", "enables", "GO:9999999", "IGI", "F"),           # alt_id of GO:0000020 -> same term
    gaf_line("P2", "SYM2", "involved_in", "GO:0000021", "TAS", "P"),        # comp class
    gaf_line("P2", "SYM2", "enables", "GO:0042802", "IPI", "F"),            # identical protein binding -> uninf.
    # G3: accession unknown, symbol fallback (UniProtKB rows only)
    gaf_line("Q999", "SYM3", "involved_in", "GO:0000030", "IDA", "P"),
    gaf_line("URS0001", "SYM3", "involved_in", "GO:0000031", "IDA", "P", db="RNAcentral"),  # no fallback
    # GAF 2.1 style: empty qualifier and bare NOT
    gaf_line("P4", "SYM4", "", "GO:0000040", "IDA", "P"),
    gaf_line("P4", "SYM4", "NOT", "GO:0000041", "IDA", "P"),
    gaf_line("P4", "SYM4", "contributes_to", "GO:0000042", "IPI", "F"),
])

ACC_MAP = {"P1": {"G1"}, "P2": {"G2"}, "P2b": {"G2"}, "P4": {"G4", "G5"}}
SYM_MAP = {"SYM1": {"G1"}, "SYM2": {"G2"}, "SYM3": {"G3"}, "SYM4": {"G4"}}
ALT = {"GO:9999999": "GO:0000020"}


@pytest.fixture(scope="module")
def mapped():
    gaf = kn.read_gaf(io.StringIO(TOY_GAF))
    assert len(gaf) == 19  # comment lines skipped
    g, st = kn.prepare_gaf(gaf, ALT)
    assert st["n_not_rows_removed"] == 2
    assert st["n_alt_id_normalised"] == 1
    m, ms = kn.map_gaf_to_genes(g, ACC_MAP, SYM_MAP)
    return m, ms


def test_evidence_classes():
    assert kn.evidence_class("IPI") == "exp" and kn.evidence_class("HDA") == "exp"
    assert kn.evidence_class("IBA") == "phylo" and kn.evidence_class("IKR") == "phylo"
    assert kn.evidence_class("TAS") == "comp" and kn.evidence_class("ISO") == "comp"
    assert kn.evidence_class("IEA") == "iea" and kn.evidence_class("ND") == "nd"
    assert kn.evidence_class("XYZ") == "other"


def test_not_detection():
    q = pd.Series(["", "NOT", "NOT|enables", "not|contributes_to", "enables", "colocalizes_with", "NOTE"])
    assert kn.is_not_qualified(q).tolist() == [False, True, True, True, False, False, False]


def test_mapping(mapped):
    m, ms = mapped
    # 17 non-NOT rows; 16 UniProtKB rows; 1 via symbol (Q999 -> SYM3); RNAcentral row unmapped
    assert ms["rows"] == 17
    assert ms["rows_by_symbol"] == 1
    assert ms["rows_unmapped"] == 1
    assert ms["rows_by_accession"] == 15
    # shared accession P4 -> both G4 and G5
    assert set(m.loc[m.go_id == "GO:0000040", "hgnc_id"]) == {"G4", "G5"}
    # isoform suffix stripped
    assert "G2" in set(m.loc[m.acc == "P2-2", "hgnc_id"])
    # without symbol map (archived mode) the Q999 row is unmapped
    g, _ = kn.prepare_gaf(kn.read_gaf(io.StringIO(TOY_GAF)), ALT)
    _, ms2 = kn.map_gaf_to_genes(g, ACC_MAP, None)
    assert ms2["rows_unmapped"] == 2 and ms2["rows_by_symbol"] == 0


def test_go_features(mapped):
    m, _ = mapped
    f = kn.go_features(m)
    g1 = f.loc["G1"]
    assert g1.n_exp_BP == 2                     # GO:1, GO:2 (duplicate GO:1 counted once)
    assert g1.n_exp_MF_informative == 1         # GO:10 only (protein binding excluded, NOT excluded)
    assert g1.n_exp_CC == 1
    assert g1.n_exp_informative_BPMF == 3       # GO:1, GO:2, GO:10
    assert g1.n_exp_informative_BPMF_lowthroughput == 2  # HMP term GO:2 dropped
    assert g1.n_exp_BPMF_all_terms == 4         # + protein binding
    assert g1.n_ibas_BPMF == 1
    assert g1.n_IEA == 1
    assert g1.n_any_BPMF_nonIEA == 4            # GO:1, 2, 10, 3 (IBA); IEA/ND/uninformative excluded
    assert bool(g1.has_ND_BP) and not bool(g1.has_ND_MF)
    assert g1.nrows_P_exp == 3 and g1.nrows_F_exp == 2 and g1.nrows_P_nd == 1
    g2 = f.loc["G2"]
    assert g2.n_exp_MF_informative == 1         # GO:20 via EXP and via alt id (IGI) -> 1 term; 42802 excluded
    assert g2.n_comp_BPMF == 1 and g2.n_exp_informative_BPMF == 1
    assert f.loc["G3"].n_exp_informative_BPMF == 1
    assert f.loc["G4"].n_exp_informative_BPMF == 2  # GO:40 + GO:42 (contributes_to kept; NOT GO:41 dropped)
    assert f.loc["G5"].n_exp_informative_BPMF == 2
    s = kn.exp_informative_bpmf(m)
    assert s.to_dict() == {"G1": 3, "G2": 1, "G3": 1, "G4": 2, "G5": 2}


def test_parse_obo(tmp_path):
    p = tmp_path / "t.obo"
    p.write_text("format-version: 1.2\n\n[Term]\nid: GO:0000020\nname: x\nnamespace: molecular_function\n"
                 "alt_id: GO:9999999\n\n[Typedef]\nid: part_of\nalt_id: GO:1\n\n[Term]\nid: GO:0000021\n"
                 "namespace: biological_process\n")
    alt, ns = kn.parse_obo(str(p))
    assert alt == {"GO:9999999": "GO:0000020"}
    assert ns == {"GO:0000020": "molecular_function", "GO:0000021": "biological_process"}


# ------------------------------------------------------------------------------------------------ PubMed
def toy_g2p():
    rows = []
    # PMID 100: 11 genes (1..11) -> not focused at <=10, not at <=3
    rows += [(g, 100) for g in range(1, 12)]
    # PMID 200: 10 genes (1..10) -> focused at <=10, not at <=3
    rows += [(g, 200) for g in range(1, 11)]
    # PMID 300: 3 genes (1, 2, 3) -> focused at both
    rows += [(g, 300) for g in (1, 2, 3)]
    # PMID 50: gene 1 alone, duplicated row -> counted once
    rows += [(1, 50), (1, 50)]
    # PMID 400: gene 2 alone (late PMID)
    rows += [(2, 400)]
    return pd.DataFrame(rows, columns=["GeneID", "PubMed_ID"]).assign(tax_id=9606)


def test_pubmed_counts():
    d = toy_g2p()
    allc = kn.pubmed_counts(d)
    assert allc[1] == 4 and allc[2] == 4 and allc[11] == 1
    f10 = kn.pubmed_counts(d, max_genes=10)
    assert f10[1] == 3            # 50, 200, 300
    assert f10[2] == 3            # 200, 300, 400
    assert f10[4] == 1            # 200
    assert 11 not in f10.index    # only in PMID 100 (11 genes)
    f3 = kn.pubmed_counts(d, max_genes=3)
    assert f3[1] == 2 and f3[2] == 2 and f3[3] == 1 and 4 not in f3.index
    # PMID cut-off: < 300 -> gene 1: 50, 200 ; gene 2: 200 ; gene-count per PMID still from full table
    fb = kn.pubmed_counts(d, max_genes=10, pmid_lt=300)
    assert fb[1] == 2 and fb[2] == 1 and fb[3] == 1
    # boundary: PMID equal to cut-off is NOT "before"
    assert kn.pubmed_counts(d, max_genes=10, pmid_lt=50).get(1, 0) == 0


# ------------------------------------------------------------------------------------- symbols / UniProt text
@pytest.mark.parametrize("sym,expect", [
    ("C1orf112", ("orf", True)), ("CXorf38", ("orf", True)), ("C17orf75", ("orf", True)),
    ("FAM210A", ("FAM", True)), ("KIAA1328", ("KIAA", True)), ("TMEM14B", ("TMEM", True)),
    ("CCDC88A", ("CCDC", True)), ("ANKRD11", ("domain:ANKRD", False)), ("TP53", ("", False)),
    ("CCDC", ("", False)), ("FAMIN", ("", False)),
])
def test_symbol_pattern(sym, expect):
    assert kn.symbol_pattern(sym) == expect


def test_clean_function_text():
    s = "FUNCTION: Binds DNA (PubMed:123, PubMed:456). {ECO:0000269|PubMed:123}."
    assert kn.clean_function_text(s) == "Binds DNA"
    assert kn.clean_function_text("") == "" and kn.clean_function_text(float("nan")) == ""
