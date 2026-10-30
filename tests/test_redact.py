"""Tests for src/redact.py (gene-name redaction for blinded judging, DESIGN §6.4)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import redact as RD  # noqa: E402

X = RD.PLACEHOLDER


def test_orf_case_and_spelled_out():
    r = RD.gene_redactor("C8orf33", alias_symbols="FLJ20989")
    assert r.redact("C8ORF33 and c8orf33 and C8orf33") == f"{X} and {X} and {X}"
    assert r.redact("C8orf33-deficient cells") == f"{X}-deficient cells"
    assert r.redact("chromosome 8 open reading frame 33 (C8-orf33)") == f"{X} ({X})"
    assert r.redact("Chromosome 8 open-reading frame 33") == X
    assert r.redact("C8orf330 and C18orf33") == "C8orf330 and C18orf33"   # other genes untouched


def test_paralogues_not_redacted():
    r = RD.gene_redactor("TMEM120B")
    assert r.redact("TMEM120A and TMEM120B") == f"TMEM120A and {X}"
    assert r.redact("TMEM-120B, Tmem120b, TMEM120 B") == f"{X}, {X}, TMEM120 B"
    r = RD.gene_redactor("SLC25A51")
    assert r.redact("SLC25A5 vs SLC25A51 vs SLC25A510") == f"SLC25A5 vs {X} vs SLC25A510"
    r = RD.gene_redactor("SLC25A5")
    assert r.redact("SLC25A5 vs SLC25A51") == f"{X} vs SLC25A51"
    r = RD.gene_redactor("TBC1D9")
    assert r.redact("TBC1D9B binds TBC1D9") == f"TBC1D9B binds {X}"


def test_hyphen_variants():
    r = RD.gene_redactor("HLA-DRB1")
    for s in ("HLA-DRB1", "HLA DRB1", "HLADRB1", "HLA‐DRB1", "hla-drb1", "HLA_DRB1", "HLA-DRB-1"):
        assert r.redact(f"the {s} allele") == f"the {X} allele", s
    assert r.redact("HLA-DRB10") == "HLA-DRB10"


def test_word_boundaries_and_possessive():
    r = RD.gene_redactor("MED31", alias_symbols=["SOH1"])
    assert r.redact("MED31's role; pMED31; MED310; xMED31") == f"{X}'s role; pMED31; MED310; xMED31"
    assert r.redact("(MED31)/SOH1, Soh1") == f"({X})/{X}, {X}"


def test_short_alpha_alias_case_sensitive_and_too_short_skipped():
    r = RD.gene_redactor("PHC3", alias_symbols=["SET", "HPH3", "EDR3", "P3"])
    assert r.redact("a set of genes; SET binds") == f"a set of genes; {X} binds"
    assert "P3" in r.skipped
    assert r.redact("P3 phase") == "P3 phase"


def test_accessions_and_isoforms():
    r = RD.gene_redactor("ANKRD52", uniprot_ids="Q8NB46")
    assert r.redact("UniProt Q8NB46, isoform Q8NB46-2; Q8NB467") == f"UniProt {X}, isoform {X}; Q8NB467"


def test_protein_names_longest_first():
    pn = ("Serine/threonine-protein phosphatase 6 regulatory ankyrin repeat subunit C (PP6-ARS-C) "
          "(Serine/threonine-protein phosphatase 6 regulatory subunit ARS-C) (Ankyrin repeat domain-containing "
          "protein 52)")
    names = RD.parse_uniprot_protein_names(pn)
    assert names == ["Serine/threonine-protein phosphatase 6 regulatory ankyrin repeat subunit C", "PP6-ARS-C",
                     "Serine/threonine-protein phosphatase 6 regulatory subunit ARS-C",
                     "Ankyrin repeat domain-containing protein 52"]
    r = RD.gene_redactor("ANKRD52", protein_names=pn, hgnc_names="ankyrin repeat domain 52")
    t = "ankyrin repeat domain containing protein 52 (ANKRD52), also called PP6-ARS-C; ankyrin repeat domain 52"
    assert r.redact(t) == f"{X} ({X}), also called {X}; {X}"
    # the regulatory subunit name is redacted as one unit, not leaving fragments
    assert r.redact("Serine/threonine-protein phosphatase 6 regulatory subunit ARS-C binds PP6") == f"{X} binds PP6"


def test_uniprot_name_parsing_ec_and_generic():
    assert RD.parse_uniprot_protein_names("Uncharacterized protein C6orf47 (Protein G4)") == [
        "Uncharacterized protein C6orf47", "Protein G4"]
    assert RD.parse_uniprot_protein_names("Some enzyme (EC 1.2.3.4) (Alt (nested) name)") == [
        "Some enzyme", "Alt (nested) name"]
    assert RD.parse_uniprot_protein_names("Uncharacterized protein") == []


def test_statement_template_redaction():
    r = RD.gene_redactor("YIPF6")
    s = "YIPF6 functions in retrograde vesicle-mediated transport, Golgi to endoplasmic reticulum"
    assert r.redact(s) == f"{X} functions in retrograde vesicle-mediated transport, Golgi to endoplasmic reticulum"
    assert r.hits("yipf6 and YIPF-6") == ["yipf6", "YIPF-6"]
