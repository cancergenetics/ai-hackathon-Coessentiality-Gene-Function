# Circularity query -- summary

`scripts/05_circularity_query.py`; Europe PMC REST search (2026-10-29; cached under `data/cache/europepmc/`). Query per PMID: `EXT_ID:<pmid> AND SRC:MED AND (DepMap OR "co-essential*" OR coessential* OR codependen* OR "co-dependen*" OR "Project Achilles")`. Default field-less search = title, abstract, keywords and, when the article's full text is in Europe PMC (inEPMC=Y), the full text.

- supporting PMIDs queried: 1,050; found in Europe PMC: 1,050
- **full text searchable (inEPMC=Y): 753 / 1,050 (71.7%)**; open access: 474
- **PMIDs flagged: 16 / 1,050 (1.5%)**; among full-text-searchable PMIDs 2.1%, among abstract-only PMIDs 0.0%
- matched terms among flagged PMIDs: DepMap 13, "co-essential*" 2, coessential* 2, codependen* 4, "co-dependen*" 0, "Project Achilles" 3
- (gene, target) pairs with >= 1 flagged supporting PMID: 106 / 5,965 (1.8%); all supporting PMIDs flagged: 65
- H genes with >= 1 flagged target: 16 / 820; H genes whose every target is fully circular (would leave H if flagged annotations are excluded): 9
- (gene, target) pairs whose supporting PMIDs are all full-text searchable: 4,128 / 5,965; with no PMID (GO_REF/Reactome only, not queryable): 48
- per-PMID validation of the batched query (spec form, one query per PMID): 55 PMIDs (systematic sample + all flagged + Wainberg 2021), disagreements: 0 []

## Known-answer check: CCDC32 / Wainberg et al. 2021 (PMID 33859415)

- PMID 33859415 among supporting PMIDs: True; flagged: True
- CCDC32 supporting PMIDs: [32307552, 33859415]; flags: 32307552=False, 33859415=True
- CCDC32 targets: GO:0030100 regulation of endocytosis (any flagged True); GO:0048259 regulation of receptor-mediated endocytosis (any flagged True); GO:0060322 head development (any flagged False); GO:0060627 regulation of vesicle-mediated transport (any flagged True); GO:2000369 regulation of clathrin-dependent endocytosis (any flagged True)
- CCDC32 targets citing PMID 33859415: 4; all flagged: True
- **check PASS**

## Named controls

| symbol | targets | targets with flagged PMID | supporting PMIDs (flag) |
|---|---|---|---|
| SPRING1 | not in H | | |
| PEDS1 | 6 | 0 | 31604315 (-, abstract only), 32209662 (-) |
| CCDC32 | 5 | 4 | 32307552 (-), 33859415 (FLAG) |
| INTS15 | 5 | 0 | 36920904 (-), 38570683 (-) |
| HAPSTR1 | 2 | 0 | 33660365 (-) |
| SLC25A51 | 19 | 18 | 32906142 (-), 33087354 (FLAG), 33262325 (FLAG) |
| TEDC1 | not in H | | |
| TEDC2 | not in H | | |
| POU2AF2 | not in H | | |
| POU2AF3 | not in H | | |
| TMEM242 | 2 | 0 | 33753518 (-) |
| FIRRM | 15 | 14 | 34260926 (-), 37256941 (-), 37347663 (-, abstract only), 37515771 (-, abstract only), 37556550 (FLAG), 38286805 (FLAG) |
| AIRIM | 3 | 0 | 35354024 (-), 38554706 (-) |
| TMEM41B | 15 | 0 | 30093494 (-), 30126924 (-), 30933966 (-), 33850023 (-), 33929485 (-), 34015269 (-, abstract only), 34043740 (-) |

Direct query on PMID 33859415 (spec form): flagged = True.
