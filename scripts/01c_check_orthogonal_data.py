#!/usr/bin/env python3
"""Sanity-check the orthogonal datasets fetched by 01b_fetch_orthogonal_data.sh.

Run as:  python3 -I scripts/01c_check_orthogonal_data.py   (needs pandas, openpyxl, h5py)
Writes results/data_checks/orthogonal_data_checks.md. Reads files only as data (no extraction of archives to disk,
nothing executed). Deliberately does NOT open DepMap files nor external/coessentiality/results/.
For the BioGRID ORCS archive only the screen INDEX (metadata) and the Olivieri 2020 screen are read.
"""
import gzip, io, os, re, sys, tarfile, zipfile
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "results", "data_checks", "orthogonal_data_checks.md")
lines = []


def w(s=""):
    lines.append(s)


def sec(title, path, idtype):
    w(f"\n## {title}\n")
    w(f"- file: `data/raw/{path}`")
    w(f"- identifier type: {idtype}")


def nuniq(*series):
    return len(set(pd.concat(series).dropna().unique()))


def base_up(s):  # strip UniProt isoform suffix
    return s.str.replace(r"-\d+$", "", regex=True)



def read_strict_xlsx(path, sheet="xl/worksheets/sheet1.xml"):
    """Minimal reader for 'strict OOXML' xlsx (pandas/openpyxl cannot open these). First sheet, first row = header."""
    import xml.etree.ElementTree as ET
    z = zipfile.ZipFile(path)
    ns = {"m": "http://purl.oclc.org/ooxml/spreadsheetml/main"}
    ss = []
    for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
        ss.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    rows = []
    for r in ET.fromstring(z.read(sheet)).find("m:sheetData", ns):
        row = {}
        for c in r:
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find("m:v", ns)
            if v is None:
                continue
            row[col] = ss[int(v.text)] if c.get("t") == "s" else (v.text if c.get("t") in ("str", "b", "e") else float(v.text))
        rows.append(row)
    cols = list(rows[0].keys())
    df = pd.DataFrame([[r.get(c) for c in cols] for r in rows[1:]], columns=[rows[0][c] for c in cols])
    return df


# ---------------------------------------------------------------- hu.MAP 3.0
d = "humap3/"
sec("hu.MAP 3.0 complexes", d + "hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv",
    "UniProt accessions (space-separated) + HGNC symbols (space-separated)")
df = pd.read_csv(RAW + "/" + d + "hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv")
up = set(x for s in df.Uniprot_ACCs.dropna() for x in s.split())
gn = set(x for s in df.genenames.dropna() for x in s.split())
sz = df.Uniprot_ACCs.str.split().str.len()
w(f"- rows (complexes): {len(df)}; columns: {list(df.columns)}")
w(f"- ComplexConfidence counts (1=extremely high ... 6=medium): {df.ComplexConfidence.value_counts().sort_index().to_dict()}")
w(f"- distinct UniProt ACCs: {len(up)}; distinct gene symbols: {len(gn)}; complex size median {int(sz.median())}, max {int(sz.max())}")

for f, idt in [("humap3_complex_pairs_20240929.pairsWprob", "UniProt ACC"), ("hu.MAP3.0_complex_pairs_genenames_20240930.pairsWprob", "HGNC symbol")]:
    sec("hu.MAP 3.0 complex pairs (" + idt + ")", d + f, idt + ", 3 tab-separated cols (id1, id2, ML probability), no header")
    df = pd.read_csv(RAW + "/" + d + f, sep="\t", header=None, names=["a", "b", "p"])
    w(f"- rows: {len(df)}; distinct proteins/genes: {nuniq(df.a, df.b)}; probability min/median/max: {df.p.min():.3f}/{df.p.median():.3f}/{df.p.max():.3f}")

f = "humap3_all_ppis_202305.pairsWprob.gz"
sec("hu.MAP 3.0 all pairwise probabilities", d + f, "UniProt ACC, 3 tab-separated cols (id1, id2, ML probability), no header")
df = pd.read_csv(RAW + "/" + d + f, sep="\t", header=None, names=["a", "b", "p"])
w(f"- rows: {len(df)}; distinct UniProt ACCs: {nuniq(df.a, df.b)}; probability min/median/max: {df.p.min():.4f}/{df.p.median():.4f}/{df.p.max():.4f}; pairs with p>=0.5: {(df.p >= 0.5).sum()}")
del df
w("- NOT AVAILABLE: humap3 `nodeTable.txt` URL (linked on the download page) returns HTTP 404; not needed (symbols come with the complex file).")

# ---------------------------------------------------------------- OpenCell
d = "opencell/"
sec("OpenCell protein interactions", d + "opencell-protein-interactions.csv", "gene symbol + Ensembl gene ID (ENSG); interactor UniProt IDs (';'-separated, incl. isoforms)")
df = pd.read_csv(RAW + "/" + d + "opencell-protein-interactions.csv")
w(f"- rows: {len(df)}; columns: {list(df.columns)}")
w(f"- distinct baits (ENSG): {df.target_ensg_id.nunique()}; distinct interactors (ENSG): {df.interactor_ensg_id.nunique()}; union genes: {nuniq(df.target_ensg_id, df.interactor_ensg_id)}")
w(f"- enrichment median {df.enrichment.median():.2f}; pval(-log10) median {df.pval.median():.2f}")
sec("OpenCell localization annotations", d + "opencell-localization-annotations.csv", "gene symbol + ENSG")
df = pd.read_csv(RAW + "/" + d + "opencell-localization-annotations.csv")
cats = pd.concat([df[c].dropna().str.split(";").explode() for c in ["annotations_grade_3", "annotations_grade_2", "annotations_grade_1"]])
w(f"- rows: {len(df)}; columns: {list(df.columns)}; distinct ENSG: {df.ensg_id.nunique()}; distinct localisation categories: {cats.nunique()}")
w(f"- proteins with a grade-3 annotation: {df.annotations_grade_3.notna().sum()}")
sec("OpenCell library metadata", d + "opencell-library-metadata.csv", "Ensembl gene ID (ENSG), symbol")
df = pd.read_csv(RAW + "/" + d + "opencell-library-metadata.csv")
w(f"- rows: {len(df)}; columns ({len(df.columns)}): {list(df.columns)[:14]}...")

# ---------------------------------------------------------------- HPA
sec("Human Protein Atlas subcellular location (HPA v25.1)", "hpa/subcellular_location.tsv.zip", "Ensembl gene ID (ENSG) + gene symbol")
with zipfile.ZipFile(RAW + "/hpa/subcellular_location.tsv.zip") as z:
    df = pd.read_csv(z.open("subcellular_location.tsv"), sep="\t")
w(f"- rows: {len(df)}; columns: {list(df.columns)}")
w(f"- distinct ENSG: {df.Gene.nunique()}; reliability: {df.Reliability.value_counts().to_dict()}")
w(f"- genes with a Main location: {df['Main location'].notna().sum()}")

# ---------------------------------------------------------------- Human Cell Map
d = "humancellmap/"
sec("Human Cell Map preys (NMF / SAFE localisation)", d + "preys-latest.txt", "HGNC symbol + Entrez + HGNC ID + RefSeq + UniProt")
df = pd.read_csv(RAW + "/" + d + "preys-latest.txt", sep="\t")
w(f"- rows: {len(df)}; columns: {list(df.columns)}; distinct symbols: {df.symbol.nunique()}; distinct Entrez: {df.Entrez.nunique()}; distinct UniProt: {df.UniProt.nunique()}")
w(f"- preys with a SAFE localisation other than 'no prediction': {(df['SAFE localization'].fillna('no prediction') != 'no prediction').sum()}; with NMF rank: {df['NMF rank'].notna().sum()}")
sec("Human Cell Map baits", d + "baits-latest.txt", "HGNC symbol + Entrez + HGNC + RefSeq + UniProt")
df = pd.read_csv(RAW + "/" + d + "baits-latest.txt", sep="\t")
w(f"- rows: {len(df)}; distinct bait symbols: {df.symbol.nunique()}; columns: {list(df.columns)}")
sec("Human Cell Map not-significant preys", d + "not-significant-latest.txt", "HGNC symbol (prey)")
df = pd.read_csv(RAW + "/" + d + "not-significant-latest.txt", sep="\t")
w(f"- rows: {len(df)}; columns: {list(df.columns)}")
sec("Human Cell Map SAINTexpress bait-prey table", d + "saint-latest.txt", "bait symbol (Bait), prey RefSeq protein (Prey), prey gene symbol (PreyGene), UniProtID col actually holds RefSeq NP_ ids")
df = pd.read_csv(RAW + "/" + d + "saint-latest.txt", sep="\t", usecols=["Bait", "Prey", "PreyGene", "SaintScore", "BFDR", "UniProtID"], low_memory=False)
w(f"- rows (bait-prey pairs): {len(df)}; baits: {df.Bait.nunique()} (note: bait names can carry suffixes like _target); prey genes: {df.PreyGene.nunique()}")
w(f"- pairs with BFDR<=0.01: {(df.BFDR <= 0.01).sum()}; example UniProtID value: {df.UniProtID.iloc[0]}")
del df

# ---------------------------------------------------------------- HuRI
sec("HuRI / Lit-BM", "huri/ (empty)", "(would be Ensembl gene IDs)")
w("- NOT OBTAINED: interactome-atlas.org apex does not resolve in DNS; www.interactome-atlas.org presents a TLS certificate valid only for the apex (hostname mismatch). Certificate/DNS were not bypassed. HuRI edges are partly recoverable from BioGRID (Luck 2020 as source) and Burke 2023 table (HuRI-derived pairs).")

# ---------------------------------------------------------------- STRING
d = "string/"
info = pd.read_csv(RAW + "/" + d + "9606.protein.info.v12.5.txt.gz", sep="\t")
sec("STRING v12.5 protein.info", d + "9606.protein.info.v12.5.txt.gz", "STRING protein ID (9606.ENSP...) -> preferred symbol")
w(f"- rows: {len(info)}; columns: {list(info.columns)}; distinct preferred_name: {info.preferred_name.nunique()}")
al = pd.read_csv(RAW + "/" + d + "9606.protein.aliases.v12.5.txt.gz", sep="\t")
sec("STRING v12.5 protein.aliases", d + "9606.protein.aliases.v12.5.txt.gz", "STRING protein ID -> alias with source (Ensembl_gene, UniProt_AC, BioMart_HUGO, Entrez ...)")
w(f"- rows: {len(al)}; columns: {list(al.columns)}")
w(f"- top alias sources: {al['source'].value_counts().head(8).to_dict()}")
for f, label in [("9606.protein.links.detailed.v12.5.txt.gz", "links.detailed"), ("9606.protein.physical.links.detailed.v12.5.txt.gz", "physical.links.detailed")]:
    sec("STRING v12.5 protein." + label, d + f, "STRING protein ID (9606.ENSP...); map to genes via info/aliases")
    df = pd.read_csv(RAW + "/" + d + f, sep=" ")
    w(f"- rows (directed, each pair listed twice): {len(df)}; columns: {list(df.columns)}")
    w(f"- distinct proteins: {nuniq(df.protein1, df.protein2)}; combined_score>=700 rows: {(df.combined_score >= 700).sum()}")
    mp = info.set_index("#string_protein_id").preferred_name
    genes = set(mp.reindex(pd.concat([df.protein1, df.protein2]).unique()).dropna())
    w(f"- distinct preferred gene symbols covered: {len(genes)}")
    chans = [c for c in df.columns if c not in ("protein1", "protein2", "combined_score")]
    w("- rows with nonzero channel score: " + ", ".join(f"{c}={(df[c] > 0).sum()}" for c in chans))
    del df

# ---------------------------------------------------------------- BioGRID
f = "biogrid/BIOGRID-ORGANISM-Homo_sapiens-5.0.262.tab3.txt"
sec("BioGRID 5.0.262 (Homo sapiens, TAB3)", f, "Entrez Gene ID, official symbol, BioGRID ID, UniProt (SWISS-PROT/TREMBL) accessions")
cols = ["#BioGRID Interaction ID", "Entrez Gene Interactor A", "Entrez Gene Interactor B", "Official Symbol Interactor A",
        "Official Symbol Interactor B", "Experimental System", "Experimental System Type", "Publication Source",
        "Organism ID Interactor A", "Organism ID Interactor B", "Throughput", "Source Database"]
df = pd.read_csv(RAW + "/" + f, sep="\t", usecols=cols, low_memory=False)
hh = df[(df["Organism ID Interactor A"] == 9606) & (df["Organism ID Interactor B"] == 9606)]
w(f"- rows: {len(df)}; human-human rows: {len(hh)}; Experimental System Type: {hh['Experimental System Type'].value_counts().to_dict()}")
w(f"- distinct human Entrez genes (human-human): {nuniq(hh['Entrez Gene Interactor A'], hh['Entrez Gene Interactor B'])}; distinct symbols: {nuniq(hh['Official Symbol Interactor A'], hh['Official Symbol Interactor B'])}")
ph = hh[hh["Experimental System Type"] == "physical"]
w(f"- physical rows: {len(ph)}; distinct physical gene pairs: {len(set(map(lambda t: tuple(sorted(t)), zip(ph['Entrez Gene Interactor A'], ph['Entrez Gene Interactor B']))))}")
top = hh["Experimental System"].value_counts().head(8).to_dict()
w(f"- top Experimental Systems: {top}")
w("- Note: includes HuRI, BioPlex, OpenCell, hu.MAP-input etc. as sources; treat as non-independent of those. Filter by Experimental System / Publication Source to build independent subsets.")
del df, hh, ph

# ---------------------------------------------------------------- BioGRID ORCS
f = "biogrid_orcs/BIOGRID-ORCS-ALL-homo_sapiens-LATEST.screens.tar.gz"
sec("BioGRID ORCS human screens (release 2.0.18, per archive member names)", f, "per-screen tables keyed by Entrez/BioGRID ID + symbol; INDEX gives screen metadata")
with tarfile.open(RAW + "/" + f) as t:
    names = t.getnames()
    idxn = [n for n in names if "SCREEN_INDEX" in n][0]
    idx = pd.read_csv(io.BytesIO(t.extractfile(idxn).read()), sep="\t", low_memory=False)
    idx.columns = [c.lstrip("#") for c in idx.columns]
    w(f"- members: {len(names)} (1 index + {len(names) - 1} screens); index rows {len(idx)}; archive NOT extracted")
    w(f"- screens by EXPERIMENTAL_SETUP: {idx.EXPERIMENTAL_SETUP.value_counts().head(6).to_dict()}")
    w(f"- screens by LIBRARY_METHODOLOGY: {idx.LIBRARY_METHODOLOGY.value_counts().head(5).to_dict()}")
    chem = idx[idx.EXPERIMENTAL_SETUP.fillna("").str.contains("Drug|Chemical|chemical", regex=True)]
    w(f"- drug/chemical-exposure screens: {len(chem)} from {chem.SOURCE_ID.nunique()} sources; distinct conditions: {chem.CONDITION_NAME.nunique()}")
    big = chem.groupby(["SOURCE_ID", "AUTHOR"]).agg(n_screens=("SCREEN_ID", "size"), n_conditions=("CONDITION_NAME", "nunique"),
                                                       genes=("SCORES_SIZE", "max")).sort_values("n_screens", ascending=False).head(10)
    w("- largest chemical-exposure sources (source, author -> screens, conditions, max genes scored):")
    for (sid, au), r in big.iterrows():
        w(f"  - {sid} {au}: {r.n_screens} screens, {r.n_conditions} conditions, up to {int(r.genes)} genes")
    ol = idx[idx.SOURCE_ID.astype(str) == "32649862"]
    w(f"- Olivieri 2020 (PMID 32649862): {len(ol)} screens in ORCS; cell line {ol.CELL_LINE.unique().tolist()}; score types {ol['SCORE.1_TYPE'].unique().tolist()}")
    if len(ol):
        mem = [n for n in names if re.search(r"SCREEN_%s-" % ol.SCREEN_ID.iloc[0], n)]
        if mem:
            s1 = pd.read_csv(io.BytesIO(t.extractfile(mem[0]).read()), sep="\t", low_memory=False)
            w(f"- example Olivieri screen member {mem[0]}: {len(s1)} rows; columns {list(s1.columns)[:12]}")
    w("- WARNING: archive also contains DepMap/Avana/other essentiality screens (not independent of DepMap); filter by SOURCE before use.")
    del idx

# ---------------------------------------------------------------- Olivieri
d = "olivieri2020/"
sec("Olivieri 2020 (bioRxiv v1) Table S1 screen summary", d + "biorxiv_845446_TableS1_media-1.xlsx", "n/a (screen metadata)")
try:
    v1 = pd.read_excel(RAW + "/" + d + "biorxiv_845446_TableS1_media-1.xlsx", header=None)
except Exception:
    v1 = read_strict_xlsx(RAW + "/" + d + "biorxiv_845446_TableS1_media-1.xlsx")
w(f"- {v1.shape[0]} rows x {v1.shape[1]} cols; header/first row: {v1.iloc[0].dropna().astype(str).tolist()[:12]}")
sec("Olivieri 2020 (bioRxiv v1) Table S2 NormZ", d + "biorxiv_845446_TableS2_NormZ_media-2.xlsx", "gene symbol (RPE1-hTERT TP53-/- Cas9 screens, DrugZ NormZ)")
v = read_strict_xlsx(RAW + "/" + d + "biorxiv_845446_TableS2_NormZ_media-2.xlsx")  # strict-OOXML workbook; sheet name Zscores_28screens
num = v.select_dtypes("number")
gcol = v.columns[0]
w(f"- sheet `Zscores_28screens` (custom strict-OOXML parser): {v.shape[0]} rows x {v.shape[1]} cols; columns: {list(v.columns)}")
w(f"- distinct genes (col `{gcol}`): {v[gcol].nunique()}; numeric screen columns: {num.shape[1]}; NaN fraction {float(num.isna().mean().mean()):.3f}")
w(f"- example gene IDs: {v[gcol].head(4).astype(str).tolist()}; NormZ range {float(num.min().min()):.1f} to {float(num.max().max()):.1f}")

# ---------------------------------------------------------------- Perturb-seq
import h5py
d = "replogle2022_perturbseq/"
for f, lab in [("K562_gwps_normalized_bulk_01.h5ad", "K562 genome-wide"), ("K562_essential_normalized_bulk_01.h5ad", "K562 essential"), ("rpe1_normalized_bulk_01.h5ad", "RPE1 essential")]:
    sec(f"Replogle 2022 Perturb-seq pseudo-bulk, {lab} (z-normalised)", d + f, "obs = perturbed gene (symbol_ENSG-style names, see below); var = measured genes (Ensembl ENSG index, gene_name column)")
    with h5py.File(RAW + "/" + d + f, "r") as h:
        X = h["X"]
        shp = X.attrs.get("shape") if "shape" in X.attrs else X.shape
        obs_idx = h["obs"].attrs["_index"]; var_idx = h["var"].attrs["_index"]
        oi = [s.decode() if isinstance(s, bytes) else s for s in h["obs"][obs_idx][:]]
        vi = [s.decode() if isinstance(s, bytes) else s for s in h["var"][var_idx][:]]
        w(f"- X shape: {tuple(shp)}; obs (perturbations): {len(oi)}; var (measured genes): {len(vi)}")
        w(f"- obs columns: {[k for k in h['obs'].keys()][:12]}; var columns: {[k for k in h['var'].keys()][:12]}")
        w(f"- example obs index: {oi[:3]}; example var index: {vi[:3]}")
        w(f"- layers/other: {list(h.keys())}")
f = "annotated_embedding_coordinates.csv"
sec("Replogle 2022 annotated embedding coordinates", d + f, "perturbation (gene symbol) ")
df = pd.read_csv(RAW + "/" + d + f)
w(f"- rows: {len(df)}; columns: {list(df.columns)}")

# ---------------------------------------------------------------- ProteomeHD
f = "proteomehd/coregulation_scores.zip"
sec("ProteomeHD v1.1 co-regulation scores", f, "UniProt ACCs (';'-separated protein groups incl. isoforms), 2 protein cols + score")
with zipfile.ZipFile(RAW + "/" + f) as z:
    df = pd.read_csv(z.open("coregulation_scores.csv"), usecols=["Protein_1", "Protein_2", "coregulation_score"])
w(f"- rows (pairs): {len(df)}; columns: {list(df.columns)}")
prots = pd.concat([df.Protein_1, df.Protein_2]).unique()
w(f"- distinct protein groups: {len(prots)}; distinct primary accessions (first ACC of each group): {len(set(p.split(';')[0].split('-')[0] for p in prots))}")
w(f"- score min/median/99.5th pct/max: {df.coregulation_score.min():.4f}/{df.coregulation_score.median():.4f}/{df.coregulation_score.quantile(0.995):.4f}/{df.coregulation_score.max():.4f}; pairs >= 0.995 (authors' cut-off): {(df.coregulation_score >= 0.995).sum()}")
del df

# ---------------------------------------------------------------- AF2 pair-level
f = "burke2023_af2/table_AF2_HURI_HuMap_UNIQUE.csv"
sec("Burke et al. 2023 AF2 human PPI predictions", f, "UniProt (id1,id2), gene symbols (Gen.id1/2), ENSG for HuRI pairs")
df = pd.read_csv(RAW + "/" + f, low_memory=False)
w(f"- rows: {len(df)}; columns ({len(df.columns)}): {list(df.columns)[:14]}...")
w(f"- Dataset counts: {df.Dataset.value_counts().to_dict()}; distinct UniProt: {nuniq(df.id1, df.id2)}; pDockQ>0.23 (high-confidence cut): {(df.pDockQ > 0.23).sum()}; pDockQ median {df.pDockQ.median():.3f}")
f = "predictomes2025/20251110_hs_predictome_pair_scores.csv.gz"
sec("Predictomes human proteome-wide pair scores (Schmid 2025 preprint)", f, "UniProt ACC pairs (':'-separated in uniprot_ids), complex_name = UniProtMnemonic__UniProtMnemonic__NNNaa")
df = pd.read_csv(RAW + "/" + f)
ids = df.uniprot_ids.str.split(":", expand=True)
w(f"- rows: {len(df)}; columns: {list(df.columns)}")
w(f"- distinct UniProt ACCs: {nuniq(ids[0], ids[1])}; SPOC>=0.5: {(df.spoc_score >= 0.5).sum()}; SPOC>=0.86 (paper threshold): {(df.spoc_score >= 0.86).sum()}; KIRC>=0.088: {(df.kirc_score >= 0.088).sum()}")
w("- caution: file also carries STRING/BioGRID/IntAct evidence columns (string_db_score, biogrid_detect_count, ...) - drop these when using as an orthogonal structural signal.")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as fh:
    fh.write("# Orthogonal data sanity checks\n\nGenerated by `scripts/01c_check_orthogonal_data.py` (read-only; DepMap files and external/coessentiality/results/ not touched).\n"
             "SHA-256/licence/version per file: `config/data_manifest_orthogonal.tsv`.\n" + "\n".join(lines) + "\n")
print("wrote", OUT)
