# Curation-lag audit of the random 50-gene U sample (DESIGN.md 1.5)

Auditor: role `audit`, model claude-sonnet-5-5, run 2026-10-29. Input: `results/audit/random50_U_sample.tsv` (SHA-256 ba8ab742...4432).
No co-essentiality output, `data/derived/`, `external/` or other `results/` file was read. Per-gene evidence, verbatim spans, search terms and collision notes: `curation_lag_audit.tsv`.

## Classes
N1 = function established by direct experimental evidence in a focused study; N2 = partial/indirect (localisation, interaction, phenotype without mechanism, dedicated expression/phylogeny study, high-throughput experimental mention); N3 = no functional literature (signature-list or GWAS-table mentions only, or nothing).

| Class | n | % of 50 |
|---|---|---|
| N1 established | 21 | 42% |
| N2 partial | 13 | 26% |
| N3 none | 16 | 32% |

**N1 rate (expected curation-lag rediscovery rate): 21/50 = 42.0%, 95% Wilson CI 29.4% to 55.8%.**

Sensitivity to the three borderline calls (ARL14 and SPATA46 are N1 but could be argued N2; MRTO4 is N2 but could be argued N1):
strict (ARL14, SPATA46 to N2) 19/50 = 38% (25.9% to 51.8%); lenient (MRTO4 to N1) 22/50 = 44% (31.2% to 57.7%); both directions 23/50 = 46% (33.0% to 59.6%).
The call that U genes are "unknown" is therefore wrong for roughly 40% of a random draw, so in a prediction benchmark roughly 4 in 10 "novel" hypotheses may be rediscoveries.

N1 genes (21): B3GAT2, ERG28, SEPTIN1, NUDT8, TAF7L, ZKSCAN5, TSHZ2, CNTNAP4, STOML3, GNG8, ARL14, GIMAP1, SRBD1, NOL10, TYW2, JHY, SPATA46, CNPY1, PRRC1, LRRCC1, SELENOM.
N2 genes (13): RWDD2B, PAGE3, HHLA1, KRT84, PTX4, MRTO4, GPR152, CEP95, TMEM130, ARMCX6, C8orf48, DBNDD1, RIMBP3.
N3 genes (16): OR51D1, OR51S1, DEFB113, C12orf56, ZNF883, GLB1L, SLC66A3, GAGE12G, FOXD4L6, SPANXN5, ZNF705D, TMEM191B, C16orf86, PRR23C, C18orf63, KIAA2012.

## Patterns
- **Recent characterisation not yet reflected in annotation.** 13 of 21 N1 genes have key evidence from 2021 or later: ERG28 (2022), GNG8 (2021), SRBD1 (two 2025 papers; the live UniProt entry already cites them), JHY (2026), NOL10 (2023, 2026), CNPY1 (2025-26 mouse, 2011 zebrafish), STOML3 (2017-2025), PRRC1 (2021), ZKSCAN5 (2022, 2024, 2025), TSHZ2 (2021), TAF7L (2022-2024), ARL14 (2024), SELENOM (2024-25). Whether these terms are already in GO could not be checked here (GO was off-limits); the D1 flag implies they are not.
- **Old but never converted into GO.** B3GAT2 (crystal structure and enzymology, 2006), TYW2 (2009, 2012), LRRCC1 (2008), GIMAP1 (2010), CNTNAP4 (2014), NUDT8 (2019), SEPTIN1 (2011, 2019) have had direct functional evidence for 7 to 17 years. These are the clearest lag cases; the D2/D3 criteria (low annotation score, few focused PMIDs) did not exclude them.
- **Evidence often comes from orthologues or model organisms**: ERG28 (yeast/plant plus human KO), CNPY1 (zebrafish, mouse), GIMAP1, GNG8, CNTNAP4, TAF7L, NUDT8, SPATA46 (mouse/rat). Human-specific function is partly inferred; this inflates N1 relative to a human-only reading.
- **Cancer-biomarker bias in N2.** KRT84, C8orf48, DBNDD1, TMEM130, CEP95/CCDC45, MRTO4 have correlative cancer/prognosis papers that do not define function.
- **N3 is dominated by paralogue families and orphans**: 9 of 16 (OR51D1, OR51S1, DEFB113, GAGE12G, FOXD4L6, SPANXN5, ZNF705D, ZNF883, PRR23C) are multi-copy/tandem or chemosensory-like family members, where family-level papers cannot be attributed to a member; the remaining 7 are C-orf/KIAA/TMEM/SLC/GLB1L-type orphans. These are the genes where a co-essentiality prediction is least likely to be a rediscovery.
- **Symbol collisions were frequent** and handled by excluding the colliding papers: STOML3 alias SRO (strontium oxide, >1500 hits), GPR152 alias PGR5 (plant photosynthesis), ARL14 previous symbol ARF7 (plant auxin factor), CEP95 (GPS circular error probable), LRRCC1/CLERC (surname Clerc), SELENOM/SEPM (particulate matter, SepM), KRT84/Hb-4, PAGE3 (polyacrylamide gel electrophoresis), TAF7L/CT40 (CT imaging), B3GAT2/GlcAT-S (Drosophila), ZNF883 (lncRNA of the same name).

## Method and limits
- Searches: Europe PMC REST (MEDLINE, preprints, agriculture, patents) with title/abstract OR-queries over the current symbol, all previous symbols and aliases (FLJ/DKFZp/MGC/OTTHUMG clone names not queried), then targeted follow-up queries for genes with noisy or empty results. The UniProt accession was used for UniProt REST entry text (FUNCTION, SUBCELLULAR LOCATION); UniProt returned HTTP 500 for Q5H9L4, Q9C0A0 and Q8WWX9. WebSearch and PubMed web pages were not used, and full-text-only mentions were not searched, so N3 calls (and CEP95, which likely has full-text centrosome-proteomics support) are lower bounds on the literature.
- Every verbatim span was machine-checked against the retrieved abstract (or UniProt text for CEP95); only papers whose records were returned by Europe PMC are cited, and "title only" marks papers whose abstract was not read.
- Classes are one auditor's judgement and were not independently double-scored; the borderline genes are flagged in the TSV summary column.
