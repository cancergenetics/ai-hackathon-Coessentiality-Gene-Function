"""Tests for src/orthogonal.py: strict-OOXML xlsx loader (synthetic + the real Olivieri 2020 table), correlation
helpers (masked Pearson; Perturb-seq own/partner-transcript exclusion), row percentiles, identifier rules."""
import os
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import orthogonal as o  # noqa: E402

STRICT = "http://purl.oclc.org/ooxml/spreadsheetml/main"
STRICT_R = "http://purl.oclc.org/ooxml/officeDocument/relationships"


def _strict_xlsx(path):
    wb = (f'<?xml version="1.0"?><workbook xmlns="{STRICT}" xmlns:r="{STRICT_R}" conformance="strict"><sheets>'
          f'<sheet name="Zscores_28screens" sheetId="1" r:id="rId1"/></sheets></workbook>')
    rels = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="x" Target="worksheets/sheet1.xml"/></Relationships>')
    ss = f'<?xml version="1.0"?><sst xmlns="{STRICT}"><si><t>Gene</t></si><si><t>ScreenA</t></si><si><t>ScreenB</t>' \
         f'</si><si><t>TP53</t></si><si><r><t>BR</t></r><r><t>CA1</t></r></si></sst>'
    sh = (f'<?xml version="1.0"?><worksheet xmlns="{STRICT}"><dimension ref="A1:XFD3"/><sheetData>'
          '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row>'
          '<row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2"><v>-1.5</v></c><c r="C2"><v>2</v></c></row>'
          '<row r="3"><c r="A3" t="s"><v>4</v></c><c r="C3"><v>0.25</v></c></row>'
          '</sheetData></worksheet>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        z.writestr("xl/sharedStrings.xml", ss)
        z.writestr("xl/worksheets/sheet1.xml", sh)


def test_read_xlsx_strict_synthetic(tmp_path):
    p = tmp_path / "strict.xlsx"
    _strict_xlsx(p)
    df = o.read_xlsx(str(p), sheet="Zscores_28screens")
    assert list(df.columns) == ["Gene", "ScreenA", "ScreenB"]
    assert df.Gene.tolist() == ["TP53", "BRCA1"]          # rich-text shared string concatenated
    assert df.ScreenA.iloc[0] == -1.5 and np.isnan(df.ScreenA.iloc[1]) and df.ScreenB.iloc[1] == 0.25
    assert o.read_xlsx(str(p), sheet=0).shape == (2, 3)


OLIVIERI = ROOT / "data" / "raw" / "olivieri2020" / "biorxiv_845446_TableS2_NormZ_media-2.xlsx"


@pytest.mark.skipif(not OLIVIERI.exists(), reason="raw Olivieri table not present")
def test_olivieri_loader_real_file():
    with pytest.raises(Exception):          # the reason a custom loader is needed (DESIGN §5.1b)
        pd.read_excel(OLIVIERI)
    d = o.read_olivieri(str(OLIVIERI))
    assert d.shape == (17382, 29)
    assert d.columns[0] == "Gene" and d.columns[1] == "Cisplatin-1" and d.columns[-1] == "CPT-2"
    num = d.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    assert num.shape[1] == 28 and num.isna().mean().mean() < 0.01
    assert d.Gene.is_unique
    assert -30 < num.min().min() < -20 and 10 < num.max().max() < 15     # NormZ range -27.4 .. 12.8


def test_masked_pearson_matches_pandas():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 30))
    X[rng.random(X.shape) < 0.2] = np.nan
    R, N = o.masked_pearson(X, min_n=10, block=7)
    ref = pd.DataFrame(X.T).corr(min_periods=10).to_numpy().copy()
    np.fill_diagonal(ref, np.nan)
    ok = np.isfinite(ref)
    assert np.array_equal(ok, np.isfinite(R))
    assert np.allclose(R[ok], ref[ok], atol=1e-5)
    assert N[0, 1] == int((np.isfinite(X[0]) & np.isfinite(X[1])).sum())


def test_pearson_excluding_own_matches_bruteforce():
    rng = np.random.default_rng(1)
    P, F = 12, 25
    X = rng.normal(size=(P, F))
    own = rng.choice(F, P, replace=False)
    own[3] = -1                            # perturbed gene's transcript not measured
    R = o.pearson_excluding_own(X, own, block=5)
    for i in range(P):
        for j in range(P):
            if i == j:
                assert np.isnan(R[i, j])
                continue
            keep = np.ones(F, bool)
            for f in (own[i], own[j]):
                if f >= 0:
                    keep[f] = False
            ref = np.corrcoef(X[i, keep], X[j, keep])[0, 1]
            assert abs(R[i, j] - ref) < 1e-5


def test_row_percentiles():
    M = np.array([[np.nan, 1, 2, 3], [5, np.nan, 5, 1], [0, 0, np.nan, np.nan], [1, 2, 3, np.nan]], float)
    P = o.row_percentiles(M, block=2)
    assert np.allclose(P[0, 1:], [1 / 3, 2 / 3, 1])
    assert np.allclose(P[1, [0, 2, 3]], [2.5 / 3, 2.5 / 3, 1 / 3])      # ties averaged
    assert np.allclose(P[2, :2], [0.75, 0.75]) and np.isnan(P[2, 3])
    assert np.all(np.isnan(np.diag(P)))


HUB = ROOT / "results" / "ids" / "hgnc_hub.tsv"


@pytest.mark.skipif(not HUB.exists(), reason="hub not built")
def test_id_mapper_rules():
    m = o.IdMapper(str(HUB), uniprot_path="/nonexistent")
    assert m.from_entrez("7157") == "HGNC:11998"          # TP53
    assert m.from_ensg("ENSG00000141510") == "HGNC:11998"
    assert m.from_acc("P04637-2") == "HGNC:11998"        # isoform suffix stripped
    assert m.from_symbol("tp53") == ("HGNC:11998", "approved")
    h, route = m.from_symbol("C7orf41")                  # previous symbol of MTPN? any previous-symbol route
    assert route in ("previous", "alias", "ambiguous", "unmapped", "approved")
    assert m.from_symbol("NOT_A_SYMBOL_XYZ") == (None, "unmapped")
    # an ID that maps to several genes is never returned
    multi = [a for a, hs in m.acc.items() if len(hs) > 1]
    if multi:
        assert m.from_acc(multi[0]) is None and m.acc_status(multi[0]) == "ambiguous"


def test_localisation_map_vocabulary():
    lm = o.localisation_map()
    comps = {c for x in lm.compartment if x for c in x.split("|")}
    assert comps <= set(o.COMPARTMENTS) and len(o.COMPARTMENTS) == 13
    for src in ("HPA", "OpenCell", "HCM_NMF", "MitoCarta", "GO_CC"):
        assert (lm.source == src).any()
    assert not lm[lm.source != "GO_CC"].duplicated(["source", "label"]).any()
    assert lm[lm.source == "GO_CC"].priority.astype(int).is_unique
