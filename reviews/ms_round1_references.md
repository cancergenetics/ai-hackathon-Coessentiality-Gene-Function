# Round 1 reference verification

Scope: all 100 numbered references of manuscript/manuscript.md. Method: every DOI resolved against the Crossref API (first author, year, title, journal, volume/issue, pages/article number compared programmatically; authorship order compared for all listed authors); ambiguous records cross-checked in Europe PMC; no Crossref update-to record of type retraction/correction was found (refs 2 and 51 only carry a "new_version" preprint relation). Six references have no DOI (web resources) and were checked for URL resolution only. Nothing else in the repository was edited.

## Summary

- References checked: 100 (94 with DOI, 6 web resources).
- Metadata mismatches requiring a fix: **1** (ref 54, Fischer 2025 pages).
- Cosmetic / no action: Crossref markup differences (refs 31, 54 title, 59, 72, 79), print-vs-online year (refs 12, 13, 41, 65, 67, 69, 72, 73, 81, 82).
- Cited-but-missing: 0. Listed-but-never-cited: 0. In-text numbers 1-100 all used; first-appearance order is strictly sequential (no skipped or out-of-order first citation); ranges and lists in text resolve to the right entries.
- Citation-claim spot-check: 49 citation uses checked across Introduction, Results, Discussion and Methods (Table 2): 44 supported (several only via full text), 4 partial or weak ([37], [62,63], [84], [98,99]), 1 not verifiable from open text ([52]); none clearly wrong. [37] is the only mis-fitting attribution.

## Table 1. Reference-by-reference check

| n | key | status | problem |
|---|---|---|---|
| 1 | Stoeger2018 | OK |  |
| 2 | Stoeger2022 | OK |  |
| 3 | Pandey2014 | OK |  |
| 4 | Edwards2011 | OK |  |
| 5 | Haynes2018 | OK |  |
| 6 | Wood2019 | OK |  |
| 7 | Kustatscher2022 | OK |  |
| 8 | Oprea2018 | OK |  |
| 9 | Rocha2023 | OK |  |
| 10 | GO2023 | OK | Consortium byline ("The Gene Ontology Consortium, Aleksander SA...") matches PubMed; Crossref has no personal-author field for first entry. Volume/pages/article number iyad031 match. |
| 11 | UniProtHelp_AnnotationScore | OK (web) | No DOI (UniProt help page); URL returns HTTP 200 on 2026-10-30; cannot be verified against a bibliographic record. |
| 12 | UniProt2025 | OK | Consortium byline matches PubMed; online 2024, print 2025 (53(D1)); list year = print year. |
| 13 | Sheils2021 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 14 | Kang2016 | OK |  |
| 15 | Callegari2016 | OK |  |
| 16 | Stroud2016 | OK |  |
| 17 | Tsherniak2017 | OK |  |
| 18 | Meyers2017 | OK |  |
| 19 | Dempster2021 | OK |  |
| 20 | Pan2018 | OK |  |
| 21 | Boyle2018 | OK |  |
| 22 | Kim2019 | OK |  |
| 23 | Wainberg2021 | OK |  |
| 24 | Kory2020 | OK |  |
| 25 | Luongo2020 | OK |  |
| 26 | Girardi2020 | OK |  |
| 27 | Bayraktar2020 | OK |  |
| 28 | Loregger2020 | OK |  |
| 29 | Aregger2020 | OK |  |
| 30 | GallegoGarcia2019 | OK |  |
| 31 | Werner2020 | OK | Title matches (Crossref adds <i> markup around TMEM189 only). |
| 32 | Amici2022 | OK |  |
| 33 | Pan2022 | OK |  |
| 34 | Offley2023 | OK |  |
| 35 | Gheorghe2022 | OK |  |
| 36 | Hassan2023 | OK |  |
| 37 | Rohde2025 | OK |  |
| 38 | Coessentiality_tool | OK (web) | No DOI (GitHub repository (commit-pinned)); URL returns HTTP 200 on 2026-10-30; cannot be verified against a bibliographic record. |
| 39 | Simmons2011 | OK |  |
| 40 | Nosek2018 | OK |  |
| 41 | KimCY2022 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 42 | Schmid2025 | OK |  |
| 43 | Gillis2011 | OK |  |
| 44 | Gillis2012 | OK |  |
| 45 | Rahman2021 | OK |  |
| 46 | Radivojac2013 | OK |  |
| 47 | Jiang2016 | OK |  |
| 48 | Zhou2019 | OK |  |
| 49 | GO_archive_web | OK (web) | No DOI (GO release archive); URL returns HTTP 200 on 2026-10-30; cannot be verified against a bibliographic record. |
| 50 | Dede2020 | OK |  |
| 51 | DeKegel2019 | OK |  |
| 52 | Billmann2026 | OK |  |
| 53 | Lazar2024 | OK |  |
| 54 | Fischer2025 | FLAG | Pages "21(7):8" wrong form: Crossref carries only publisher article-number "8" (no page range); PubMed/Europe PMC (PMID 40425816) gives 21(7):911-943. Replace with "21(7):911-943". Authors/year/title/journal/volume/issue/DOI otherwise match. |
| 55 | McFarland2018 | OK |  |
| 56 | Golden2017 | OK |  |
| 57 | Shui2023 | OK |  |
| 58 | Alpsoy2018 | OK |  |
| 59 | Talkish2014 | OK | Title matches (Crossref adds <i> markup around species name only). |
| 60 | Bournonville2025 | OK |  |
| 61 | Lambrus2016 | OK |  |
| 62 | Feuermann2025 | OK |  |
| 63 | Skunca2012 | OK |  |
| 64 | Chen2023 | OK |  |
| 65 | Amici2021 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 66 | DepMap_web | OK (web) | No DOI (DepMap portal); URL returns HTTP 200 on 2026-10-30; cannot be verified against a bibliographic record. |
| 67 | Seal2023 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 68 | gene2pubmed_web | OK (web) | No DOI (NCBI FTP file); URL returns HTTP 200 on 2026-10-30; cannot be verified against a bibliographic record. |
| 69 | Dyer2025 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 70 | Huttlin2021 | OK |  |
| 71 | Cho2022 | OK |  |
| 72 | Oughtred2021 | OK | Title matches (Crossref small-caps markup only). Crossref issued year 2020 (online) vs print 2021; list uses print year, consistent with vol 30. |
| 73 | Szklarczyk2025 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 74 | Go2021 | OK |  |
| 75 | Kustatscher2019 | OK |  |
| 76 | Nusinow2020 | OK |  |
| 77 | Replogle2022 | OK |  |
| 78 | Olivieri2020 | OK |  |
| 79 | Burke2023 | OK | Matches (Crossref HTML-escapes "&"). |
| 80 | Thul2017 | OK |  |
| 81 | Rath2021 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 82 | Meldal2022 | OK | Matches; Crossref online year is one year earlier than print year used in list (volume/pages agree with print issue). |
| 83 | Belkin2003 | OK |  |
| 84 | GO_evidence_web | OK (web) | No DOI (GO evidence-code guide); URL returns HTTP 200 on 2026-10-30; cannot be verified against a bibliographic record. |
| 85 | Wilson1927 | OK |  |
| 86 | Webber2010 | OK |  |
| 87 | Rubin1980 | OK |  |
| 88 | Stuart2010 | OK |  |
| 89 | Berger1982 | OK |  |
| 90 | BergerHsu1996 | OK |  |
| 91 | FieldWelsh2007 | OK |  |
| 92 | Efron1987 | OK |  |
| 93 | Chernozhukov2018 | OK |  |
| 94 | Brier1950 | OK |  |
| 95 | Cox1958 | OK | Matches; Crossref issue "3-4" = list "(3-4)". |
| 96 | VanCalster2019 | OK | Crossref lacks author names; Europe PMC (PMID 31842878) confirms Van Calster B first author, BMC Med 17(1):230, 2019. |
| 97 | Benjamini1995 | OK |  |
| 98 | Simes1986 | OK |  |
| 99 | Aickin1996 | OK |  |
| 100 | Cohen1960 | OK |  |

## Table 2. Citation-claim spot-check

Abstracts read via Europe PMC; where the abstract was silent, open-access full text (PMC BioC) or the local tool report was searched.

| # | section | claim as written (condensed) | refs | verdict | evidence / problem |
|---|---|---|---|---|---|
| 1 | Intro | Research attention is concentrated and self-reinforcing; small minority of genes ~half of publications; genes studied today were studied first | [1-4] | Supported | Stoeger 2018 full text: 5% of genes account for half of publications; genes reported by 1991 account for 49% of 2015 literature. [2], [3] abstracts support persistence/skew. |
| 2 | Intro | Annotation resources inherit this imbalance | [5] | Supported | Haynes 2018 abstract: inequality across annotation resources. |
| 3 | Intro | ~20% of proteins in well-studied organisms lack informative description | [6] | Supported | Wood 2019 abstract states this almost verbatim. |
| 4 | Intro | Calls for agreed measures of 'understudied' and systematic data | [7-9] | Supported | [9] abstract (Unknome ranking); [8] IDG/TDL; [7] abstract not retrievable, title consistent. |
| 5 | Intro | UniProt annotation score; IDG Tdark as measures of knownness | [11,12],[8,13] | Supported (minor) | [8] full text defines Tdark; [13] Pharos/TCRD abstract. [12] (UniProt 2025) abstract does not mention annotation score; [11] help page carries it. |
| 6 | Intro | Lists of 'uncharacterised' genes contain genes whose function is already published | [14-16] | Supported | [14],[15] abstracts: TIM29 identified as TIM22 subunit in 2016; [16] complex I accessory subunits. Examples, not a general proof. |
| 7 | Intro | DepMap with copy-number and screen-dynamics correction | [17-19] | Supported | [18] CERES copy-number abstract; [19] Chronos abstract (proliferation dynamics, copy-number bias). |
| 8 | Intro | Co-essential genes tend to act in same complex/pathway | [20-23] | Supported | Abstracts of all four state this. |
| 9 | Intro | C12orf49/SPRING1 in SREBP processing via co-essentiality | [22,27-29] | Supported | [27] abstract (coessentiality map identifies C12orf49), [28] SPRING/SREBP, [29] LUR1; [22] full text lists C12orf49 as uncharacterised in SREBP cluster. |
| 10 | Intro | TMEM189/PEDS1 plasmalogen desaturase and C15orf57/CCDC32 AP-2 | [23,30,31] | Supported | [23] abstract names both; [30],[31] abstracts show TMEM189 desaturase. |
| 11 | Intro | C16orf72/HAPSTR1 in stress signalling | [32] | Supported | Abstract. |
| 12 | Intro | C14orf80, C16orf59 (TEDC1/2) with delta/epsilon-tubulin from co-essentiality | [20] | Supported (full text) | Pan 2018 full text: C16orf59 and C14orf80 form a heterodimer binding delta/epsilon tubulins; not in abstract. |
| 13 | Intro | C7orf26/INTS15 as Integrator subunit | [33,34] | Supported (full text) | [33] full text: C7orf26 loading with INTS10/13/14; [34] abstract: INTS15 additional subunit. Names C7orf26 and INTS15 are synonyms but [34] uses only INTS15. |
| 14 | Intro | Network construction improved: covariance whitening and GLS | [23,35] | Supported | [35] abstract: covariance normalisation critical; [23] introduces GLS. |
| 15 | Intro | Dimensionality reduction and normalisation | [33,36] | Supported | [36] abstract (autoencoder/PCA/onion); [33] sparse dictionary learning is a looser fit. |
| 16 | Intro | Per-gene balancing improves co-essentiality networks | [37] | WEAK | BaCoN abstract concerns prediction of gene buffering from expression-versus-fitness correlation networks, not co-essentiality network construction for function; reword or cite as a related balancing idea. |
| 17 | Intro | Tool ranked co-complex pairs better than GLS on held-out pairs | [38] | Supported (non-peer-reviewed) | Local clone external/coessentiality/REPORT.md reports delta AP vs GLS +0.103/+0.175-0.193 with CI above 0. |
| 18 | Intro | Pre-registration as guard against analytic flexibility | [39,40] | Supported | Simmons 2011 and Nosek 2018 titles/topics. |
| 19 | Intro | Integrated networks used as 'independent' support already contain DepMap data | [41,42] | Supported (full text) | HumanNet v3 table: co-essentiality links from ~800 CRISPR profiles; SPOC/Predictomes features include DepMap co-dependency. Not visible in abstracts. |
| 20 | Intro | GBA performance reflects degree and multifunctionality | [43,44] | Supported | Both abstracts. |
| 21 | Intro | ETC complex I + mitoribosome ~76% of true-positive pairs at precision 0.5 | [45] | Supported | Rahman 2021 full text: ~76% of 3,348 TP pairs at precision 0.5 (CORUM standard). |
| 22 | Intro | CAFA time-delayed evaluation design; archived GO | [46-48],[49] | Supported | CAFA abstracts; GO archive URL resolves. |
| 23 | Intro | Genes less often essential, not expressed, buffered by paralogues | [50,51] | Supported | [50],[51] abstracts (never-essentials enriched for paralogs; paralogs less frequently essential). |
| 24 | Intro | Flat knockout profile carries no network information | [52] | Not verifiable from abstract | Billmann 2026 abstract says the HAP1 GI network complements DepMap co-essentiality, but does not state this point. Logically true; citation loose. |
| 25 | Intro | Cas9 chromosome-arm truncation and amplicon artefacts | [18,22,53] | Supported | [53] abstract (proximity bias, arm truncation); [18] CERES copy-number artefact; [22] full text flags amplification-artefact clusters. |
| 26 | Results | hu.MAP 3.0 partner transfer (0.049); built after t0 | [54] | Supported | Abstract; 2025 publication post-dates 2018. |
| 27 | Results | DEMETER2 RNAi replication check | [55] | Supported | Abstract. |
| 28 | Results | ANKRD52 is PP6 regulatory subunit dephosphorylating AGO2 | [56] | Supported | Abstract: AGO2 dephosphorylated by ANKRD52-PPP6C. |
| 29 | Results | AGO2-ANKRD52 co-dependency in DepMap already reported | [57] | Supported (full text only) | Shui 2023 full text: DepMap 21Q2 AGO2 vs ANKRD52/PPP6C co-dependency (Fig S5C); absent from abstract. Suggest citing 'Fig S5C'. |
| 30 | Results | BICRAL partners SMARCD1 and BRD9 define GBAF/ncBAF, placed biochemically in 2018 | [58] | Supported | Alpsoy 2018 abstract: GLTSCR1/GLTSCR1L (BICRAL) GBAF with BRD9 and BAF subunits. |
| 31 | Results | RBM34 orthologue Nop12 is a 60S maturation factor | [59] | Supported | Talkish 2014 abstract: Nop12 role in 27SA3/ITS2 pre-rRNA processing. |
| 32 | Results | A-C linker proteins CCDC77, MIIP, TBC1D31 | [60] | Supported (minor) | Abstract names CCDC77, WDR67 (= TBC1D31 alias) and MIIP; use one symbol or give the alias. |
| 33 | Results | Centriolar phenotype masked by p53-dependent arrest | [61] | Supported | Lambrus 2016 abstract: p53-dependent arrest after centrosome loss. |
| 34 | Discussion | Co-essentiality strongest for stable complexes and strong dependencies | [20,23,45] | Supported | Consistent with the three papers. |
| 35 | Discussion | LOO accuracy optimistic; CAFA-style evaluations made this point | [46-48] | Supported | CAFA time-delayed vs LOO evaluation. |
| 36 | Discussion | Definition of 'uncharacterised' as recommended | [8,23] | Supported | [23] full text: annotation score <=2; [8] defines Tdark. |
| 37 | Discussion | Electronic and phylogenetic annotation now covers most human genes | [62,63] | Partial | [62] Feuermann 2025 supports coverage; [63] Skunca 2012 evaluates quality (reliability) of electronic annotation, not coverage. |
| 38 | Discussion | Context-specific co-dependency carries information | [64,65] | Supported | Chen 2023 and FIREWORKS abstracts. |
| 39 | Methods | D2 = UniProt annotation score <=2, definition of Wainberg | [11],[23] | Supported | Wainberg full text: 'UniProt annotation score ... of <=2'. |
| 40 | Methods | D1 evidence code list (EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC) | [84] | Partial | Guide defines the codes, but classes TAS (author statement) and IC (curator statement) as non-experimental; text elsewhere says 'experimental' evidence. Clarify that TAS/IC are deliberately counted. |
| 41 | Methods | Extrapolated rank-biased overlap | [86] | Supported | Webber 2010 introduces RBO with extrapolation. |
| 42 | Methods | Mahalanobis matching | [87,88] | Supported | Rubin 1980 title; Stuart 2010 matching review. |
| 43 | Methods | Intersection-union test | [89,90] | Supported | Berger 1982; Berger and Hsu 1996. |
| 44 | Methods | Cluster bootstrap; BCa intervals | [91],[92] | Supported | Field and Welsh 2007; Efron 1987. |
| 45 | Methods | Cross-fitting | [93] | Supported | Chernozhukov 2018 (DML). |
| 46 | Methods | Brier score; calibration intercept and slope | [94],[95,96] | Supported | Brier 1950; Cox 1958 (logistic recalibration); Van Calster 2019. |
| 47 | Methods | Simes within class, Holm across classes | [98,99] | Partial | Simes 1986 fine; Aickin and Gensler 1996 compares Bonferroni vs Holm (secondary source). Holm (1979) is the primary reference and is not cited. |
| 48 | Methods | Cas9 proximity artefacts removed by excluding same-arm genes | [53] | Supported | Abstract describes proximity bias within chromosome arm. |
| 49 | Methods | Cohen's kappa; Laplacian eigenmap; BH q | [100],[83],[97] | Supported | Standard primary references. |

## Recommended edits

1. Ref 54: change "21(7):8" to "21(7):911-943".
2. Intro, "per-gene balancing [37]": BaCoN addresses gene buffering; reword or drop.
3. Discussion "[62,63]": split coverage ([62]) from annotation quality ([63]).
4. Methods D1 evidence codes: state that TAS and IC are deliberately included although the cited guide does not class them as experimental.
5. Methods "Holm": consider adding Holm 1979 as the primary reference.
6. Results ANKRD52: add "(Fig S5C)" to the [57] citation; BICRAL/TBC1D31: give WDR67 alias or keep one symbol.

