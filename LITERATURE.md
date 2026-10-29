# LITERATURE.md: co-essentiality for assigning function to uncharacterised human genes

Compiled 2026-10-29 by the literature agent from web searches, Europe PMC abstracts and full texts, Crossref, and live queries of HGNC, QuickGO, UniProt and TCRD.

**How to read this file**
- `[Key]` points to a row in `references/literature_refs.tsv`. Every DOI there was resolved through `api.crossref.org/works/<doi>` on 2026-10-29, and all 123 rows are verified. Web resources and API queries have their own rows.
- **[verified]** means I read the statement in the abstract or full text, or retrieved it from the named database.
- **[unverified]** means it comes from a secondary summary, or I could not confirm it in the primary source.
- Numbers are as reported by the cited source.

**Pre-registration hygiene.** I did not open `external/coessentiality/results/predictions/` or any genome-wide output. I did not run the method, and I computed nothing from DepMap data. The tool's figures below come from its `README.md` and `REPORT.md` [Coessentiality_tool].

---

## Executive summary

1. **The method.** Co-essentiality is now a standard, well-validated way to place genes into complexes and pathways [Pan2018; Boyle2018; Kim2019; Wainberg2021].
   - Its signal is strongly uneven. Two CORUM complexes, ETC complex I and the 55S mitoribosome, supplied about 76% of true-positive pairs at precision 0.5 in raw DepMap correlations [Rahman2021].
   - Copy number, proximity bias from chromosome-arm truncation, paralog buffering and screen dynamics confound it [Kim2019; Lazar2024; Dede2020; Rahman2021].
   - Covariance whitening or PC removal is the single most important correction [Wainberg2021; Gheorghe2022; Hassan2023].
   - zavg_BEF adds second-order and embedding views on top of whitening. Its gains over GLS are concentrated in large complexes; on small complexes its macro-AP equals GLS [Coessentiality_tool].
2. **Precedent for our use.** At least 9 genes formerly named C-orf/TMEM/MCART had their function first proposed or decisively supported by DepMap co-essentiality, between 2018 and 2023 (§2):
   - C12orf49/SPRING1, TMEM189/PEDS1, C15orf57/CCDC32, C7orf26/INTS15, C16orf72/HAPSTR1, MCART1/SLC25A51, C14orf80/TEDC1 and C16orf59/TEDC2, C11orf53/POU2AF2, TMEM242.
   - These are natural positive controls. Several were found at the same time by orthogonal screens, so a hold-out must be built on dated annotation snapshots, not on paper dates.
3. **Defining "uncharacterised".** No single metric is canonical. Defensible, reproducible definitions are:
   - (D1) no experimental GO biological-process or molecular-function annotation in a frozen GO release, ignoring IEA, ISS, IBA, high-throughput codes and bare "protein binding";
   - (D2) UniProt annotation score ≤ 2, the definition Wainberg et al. used. It currently covers 1,706 reviewed human entries in UniProt 2026_03;
   - (D3) a literature-attention criterion: fractional gene2pubmed count, or IDG Tdark. Tdark covers 5,679 of 20,412 TCRD targets.
   - I recommend D1 as primary, plus agreement with D2 or D3, with fixed release dates (§3.4).
4. **Validation.** Guilt-by-association performance is often driven by multifunctionality and node degree, not specific edges [Gillis2011; Gillis2012]. Validation therefore needs:
   - degree- and essentiality-matched null models;
   - a CAFA-style temporal hold-out on archived GO releases [Radivojac2013; Zhou2019];
   - explicit removal of circular evidence.
5. **Circularity is real and documented.**
   - The current experimental GO annotations for CCDC32 cite the co-essentiality paper itself [Wainberg2021].
   - HumanNet v3's GI layer contains DepMap co-essentiality [KimCY2022], and the SPOC classifier behind Predictomes uses DepMap as a feature [Schmid2025].
   - zavg_BEF's hyper-parameters were tuned on hu.MAP 3.0 complexes [Coessentiality_tool].
6. **Orthogonal support.** The most useful data are physical association data (hu.MAP 3.0, BioPlex 3.0, OpenCell, HuRI), localisation (HPA, OpenCell, Human Cell Map), co-abundance (ProteomeHD, CCLE and ProCan proteomics), perturbation phenotypes (genome-wide Perturb-seq, optical pooled screens, chemogenetic screens) and the 2025 proteome-wide structure-predicted interactomes [Zhang2025; Schmid2025b]. STRING text-mining and curated-database channels must be excluded.

---

## 1. Co-essentiality / co-dependency networks for gene function

### 1.1 Data foundations

- **DepMap.** The Cancer Dependency Map began with 501 genome-scale RNAi screens analysed with DEMETER [Tsherniak2017]. It then moved to CRISPR-Cas9 (Avana), first scored with CERES, which corrects the copy-number effect [Meyers2017], and later with Chronos [Dempster2021].
  - Chronos models cell-population dynamics. It reported the "lowest copy number and screen quality bias of evaluated methods" [Dempster2021] [verified].
  - DEMETER2 is a hierarchical Bayesian RNAi model that integrates three RNAi datasets and improves agreement with CRISPR [McFarland2018] [verified]. It is locally available as `depmap_rnai/D2_combined_gene_dep_scores.csv` (DATA.md).
- **Broad–Sanger concordance and batch effects.**
  - Broad and Sanger CRISPR screens agree, and their batch effects are driven mainly by library and assay length [Dempster2019] [abstract-level, via the tool's literature review].
  - Integrating them needs gene-wise correction [Pacini2021]. Sanger's Project Score is an independent CRISPR compendium [Behan2019].
  - Whether 26Q3 `CRISPRGeneEffect` already contains the Sanger screens was not verified here.
- **Release used here.** DepMap 26Q3 `CRISPRGeneEffect` has 1,361 models × 18,434 genes. Per the tool's documentation, it is jointly Chronos-processed with library correction, copy-number correction and chromosome-arm median alignment [Coessentiality_tool].

### 1.2 Founding and key papers

| Paper | Data | Scoring | Key quantitative result | Use for unknown genes |
|---|---|---|---|---|
| Pan et al. 2018 [Pan2018] | Achilles RNAi (501 lines) + CRISPR (342) | Correlation networks + PPI integration | CRISPR recalled 464 CORUM complexes vs 231 for RNAi (200 shared). hu.MAP complexes overlapping CORUM were recalled at 30.7% vs 10% without overlap [verified, full text via WebFetch] | Placed C16orf59 and C14orf80 (now TEDC2 and TEDC1) with δ/ε-tubulin, and C19orf25 with the cytoplasmic NRZ complex; validated by IP-MS and IF |
| Boyle et al. 2018 [Boyle2018] | 436 Avana screens | PCA (olfactory-receptor) correction + Pearson | >1.5 million "co-functional" pairs [verified abstract] | Community detection; gene-level predictions not checked here |
| Kim et al. 2019 [Kim2019] | 276 high-quality Avana screens (BAGEL BF) | Pearson, Bonferroni | "up to 500-fold enrichment for co-functional gene pairs". Strict network: 68,813 edges. Removed same-chromosome pairs within 20 Mb; flagged 270 genes in 30 copy-number "amplification" clusters [verified] | Named DHRS7B, TMEM41A and C12orf49 (SPRING1) as uncharacterised members of an SREBP-maturation cluster |
| Wainberg et al. 2021 [Wainberg2021] (preprint 2019) | Achilles 18Q3, 485 lines | GLS (whitened regression) | Top-partner enrichment, GLS vs PC-corrected Pearson: CORUM ~160× vs ~120×; hu.MAP ~130× vs ~90×. Median p 0.48 vs 0.21 [verified, bioRxiv text] | "Uncharacterised" = UniProt annotation score ≤ 2. Predicted functions for 108 genes (Nature abstract; bioRxiv v2 says 102 genes / 220 predictions). Validated TMEM189 (plasmalogen desaturase) and C15orf57 (AP2 binding, transferrin uptake) |
| Rahman et al. 2021 (FLEX) [Rahman2021] | DepMap 19Q2 (563 lines) | Pearson; FLEX benchmarking | 2 of 1,697 CORUM complexes (ETC I, 55S mitoribosome) contribute ~76% of 3,348 TP pairs at precision 0.5. About 300 screens already capture almost all functional information [verified full text] | Introduced module-level PR (mPR) for functional diversity; GLS gives more diverse coverage |
| Gheorghe & Hart 2022 [Gheorghe2022] | Avana | Factorial comparison | Covariance normalisation is critical. CERES and BF beat Chronos. Pearson after whitening equals OLS. Partial correlation detects "moonlighting" [verified abstract] | Best-practice construction |

### 1.3 Newer methods and resources (2021–2026)

- **FIREWORKS** builds gene-centred co-essentiality networks with bias reduction and user-selected cell-line subsets [Amici2021] [verified abstract]. Its authors then nominated C16orf72/HAPSTR1 (§2) [Amici2022].
- **Webster** uses sparse dictionary learning to model pleiotropy. It "predicted the stoichiometry of an unknown protein complex subunit from fitness data alone" [Pan2022] [verified abstract]. Secondary summaries say this subunit was C7orf26, mapped mostly to the INTS10–13–14 module [unverified in full text].
- **Onion normalisation.** Robust PCA plus "onion" fusion of several normalised layers beats existing DepMap normalisations [Hassan2023] [verified abstract]. The tool's literature review reports a large gain in gene coverage at a fixed number of top edges [Coessentiality_tool]. The paper's figure legend is ambiguous about which layer its gene counts refer to, so I quote no numbers [unverified].
- **Context-defined co-dependency modules.** 145 co-dependency modules from pan-cancer screens, contextualised by mutation, expression and drug data [Chen2023] [verified abstract]. Integrator module #35 contained C7orf26 although it was not annotated as a member [secondary summary of the paper; unverified in full text].
- **BaCoN.** A post-hoc, per-gene-balanced correction of correlation networks; it stacks with Cholesky whitening, and its gains grow with the number of screens [Rohde2025] [verified abstract]. It was benchmarked on gene buffering, not on complexes.
- **Human HAP1 genetic-interaction map** (~4 million gene pairs, ~89,000 interactions). It "complements the DepMap gene co-essentiality network by capturing unique functional information" [Billmann2026] [verified abstract].
  - DepMap subnetworks built from 298 random lines overlap each other at Jaccard ~0.5 (PCC > 0.4) but overlap the HAP1 network weakly.
  - Core-essential genes with uniform effects carry few interactions; selectively essential genes carry more.
  - The paper links 113 low-citation genes to bioprocesses [full text via WebFetch; partly read].
- **datadrivenhypothesis.org** (preprint, not peer-reviewed): pathway-level co-essentiality by canonical correlation of pathway PCs. It reports no formal benchmark, and its only validated hypothesis comes from a separate study [Hirschey2026].
- **zavg_BEF (this project's tool).** Gene-standardised, top-20-PC-filtered, ridge-whitened Chronos profiles, averaged over three z-scored views [Coessentiality_tool]:
  - **F** (direct correlation);
  - **B** (overlap of each gene's top 0.25% neighbours);
  - **E** (cosine in a 512-dimensional Laplacian eigenmap of the kNN graph).

  Benchmarked on hu.MAP 3.0 *train* pairs with complex-disjoint splits [Coessentiality_tool]:

  | Metric | zavg_BEF | GLS |
  |---|---|---|
  | Dev HT-AP | 0.470 | 0.312 |
  | Internal test HT-AP | 0.345 | 0.242 |
  | Internal test macro per-cluster AP | 0.365 | 0.369 |

  - Gains are concentrated in large, dense complexes, and macro per-cluster AP is no better than GLS.
  - 7.2% of olfactory-receptor pairs score above the null 99th percentile, driven by same-chromosome OR clusters, which suggests a residual proximity artefact.
  - These are AI-generated, not human-verified results [Coessentiality_tool README].

### 1.4 Known biases and how they bear on function prediction

1. **Mitochondrial and large-complex dominance.**
   - ETC complex I and the mitoribosome dominate the strongest DepMap correlations. Their variable phenotypes may reflect screen duration and protein stability, not differential dependency [Rahman2021] [verified].
   - Kim et al. likewise note that ETC and mitoribosome clusters dominate [Kim2019].
   - Pooled precision metrics will therefore over-reward predictions into mitochondrial and ribosomal machinery. Report per-term or per-complex (macro) metrics [Rahman2021; Coessentiality_tool].
2. **Copy number and proximity.**
   - CRISPR cutting in amplified regions produces correlated fitness effects among neighbouring genes [Meyers2017; Kim2019].
   - Separately, Cas9 causes chromosome-arm truncations, so knockouts resemble unrelated genes on the same arm ("proximity bias"). The bias is consistent across cell types, labs and modalities [Lazar2024] [verified].
   - Correction methods were benchmarked by Vinceti et al. AC-Chronos was best for joint processing [Vinceti2024] [verified].
   - Wainberg et al. flagged syntenic modules as likely artefacts [Wainberg2021].
   - For uncharacterised genes, **a same-arm or nearby top neighbour is the single most likely false positive.**
3. **Paralog buffering and "never-essential" genes.**
   - Half of constitutively expressed genes are never detected as hits in any CRISPR screen, and these are enriched for paralogs [Dede2020] [verified].
   - Paralogs are less often essential; 13–17% of variable paralog essentiality is attributable to buffering [DeKegel2019] [verified].
   - A gene with a flat profile has no co-essentiality information. Many uncharacterised genes will be uninformative, not negative.
4. **Signal depends on dependency variance.** Genes with variable dependency carry the network signal; uniformly core-essential and never-essential genes carry little [Billmann2026; Pan2018 gene filtering].
5. **Lineage and population structure.** Related cell lines inflate naïve correlations. Whitening and GLS absorb this; Pearson p-values are inflated (median 0.21 vs 0.48) [Wainberg2021]. Lineage-restricted co-dependency carries real context-specific information [Chen2023; Amici2021].
6. **Screen quality, library and assay length.** These effects are gene-specific and driven by library [Rauscher2018; Dempster2019]. FLEX shows that performance saturates at about 300 screens [Rahman2021].
7. **Hub and multifunctional genes.** Broadly essential "hub" genes correlate with many partners. Per-gene balancing (BaCoN, mutual rank, row z-scores) mitigates this [Rohde2025]; zavg_BEF's B view uses row z-scores [Coessentiality_tool].
8. **Score choice.** Chronos underperformed CERES and BF for network construction in one systematic comparison [Gheorghe2022]. This is relevant because 26Q3 offers only Chronos.

### 1.5 Documented ways co-essentiality is used to assign function

1. **Top-neighbour inspection plus wet-lab follow-up:** SPRING1, SLC25A51, HAPSTR1, POU2AF2 (§2).
2. **Module enrichment.** Cluster the network and transfer enriched GO terms to unannotated module members. Wainberg et al. required ≥100-fold enrichment and terms with ≥5 genes [Wainberg2021] [verified bioRxiv].
3. **Integration with physical interaction data.** Intersect co-essential pairs with AP-MS or hu.MAP edges [Pan2018], or use co-essentiality as a classifier feature [Schmid2025].
4. **Context restriction.** Analyse lineage or mutation subsets, as in FIREWORKS and the 145 context modules [Amici2021; Chen2023].
5. **Selective-dependency prioritisation.** Rank strongly selective dependencies by PubMed count, then read their co-dependencies [Zhou2022] (§2).

---

## 2. Success stories: candidate positive controls

### 2.1 Table

**How to read the dates.**
- **HGNC** is the date of the symbol change (`date_symbol_changed`, HGNC REST, 2026-10-29).
- **GO** is the earliest date on any experimental (EXP/IDA/IPI/IMP/IGI/IEP) annotation in today's GOA, from QuickGO. **These GO dates are last-modified dates, not first-entry dates** (§2.3). Both columns were retrieved on 2026-10-29 [QuickGO_HGNC_queries]. Treat them as *upper bounds* on when experimental knowledge entered GO.
- **Role of co-essentiality:**
  - **Primary** = the function was first proposed from DepMap co-essentiality.
  - **Concurrent** = co-essentiality and an independent method arrived in the same period.
  - **Supporting** = co-essentiality corroborated a function found otherwise.
  - **Not shown** = I could not verify any co-essentiality role.

| Gene (former symbol) | Function | Role of co-essentiality and how found | Key papers (year) | HGNC rename | GO exp. (upper bound) |
|---|---|---|---|---|---|
| SPRING1 (C12orf49) | Golgi SREBP-pathway regulator; S1P (MBTPS1) cofactor/maturation | **Primary.** Placed in an SREBP-maturation co-essential cluster [Kim2019]. Then DSPC metabolic co-essentiality map, 35 modules; Golgi, binds MBTPS1, needed for SREBP cleavage [Bayraktar2020]. Concurrent haploid and HAP1 GI screens [Loregger2020; Aregger2020]; S1P maturation cofactor [Xiao2021] | 2019–2021 | 2020-04-29 | 2020-04-23 (Loregger2020) |
| PEDS1 (TMEM189) | Plasmanylethanolamine desaturase (plasmalogen vinyl-ether bond) | **Concurrent.** Top-ranked Wainberg prediction (ether-lipid module) [Wainberg2021, preprint 2019]. Independently via bacterial CarF homology [GallegoGarcia2019] and HAP1 knockout [Werner2020] | 2019–2021 | 2020-05-27 | 2019-10-28 (GallegoGarcia2019) |
| CCDC32 (C15orf57) | AP2/clathrin-mediated endocytosis; AP2 assembly | **Primary.** Wainberg module with AP2 subunits; binds AP2, localises to clathrin-coated pits, needed for transferrin uptake [Wainberg2021]. Later AP-2 assembly biochemistry [Sloan2026]; loss-of-function syndrome [Harel2020] | 2021–2026 | 2017-05-22 (rename preceded function) | 2021-06 IMP (Harel2020); 2023-06 IDA citing Wainberg2021 itself |
| INTS15 (C7orf26) | Integrator subunit (INTS10/13/14 module) | **Primary/concurrent.** Predicted by co-essentiality [Wainberg2021, preprint 2019] and fitness-only modelling [Pan2022]. Clustered with INTS10/13/14 by Perturb-seq; depletion destabilises INTS10 [Replogle2022] [verified]. Co-dependency module #35 [Chen2023]. Confirmed by proteomics plus AlphaFold2 [Offley2023] and structures of INTS10/13/14/15 [Razew2024] | 2019–2024 | 2022-01-07 | 2022-02-15 (hu.MAP 2.0 [Drew2021]) |
| HAPSTR1 (C16orf72) | Stress-response rheostat; binds and is regulated by HUWE1 | **Primary.** Fitness data from 739 lines plus stress transcriptomics nominated it as a central regulator [Amici2022] [verified]. Earlier, as TAPR1, a p53 regulator buffering telomerase inhibition, from a chemogenetic screen [Benslimane2021] [title-level]. Follow-up [Amici2024] | 2021–2024 | 2022-07-04 | 2021-09-08 (IMP, Benslimane2021) |
| SLC25A51 (MCART1) | Mitochondrial NAD⁺ transporter | **Primary.** "Mine gene essentiality data … to identify MCART1 (SLC25A51) as coessential with ETC components" [Kory2020] [verified]. Concurrent [Luongo2020; Girardi2020] | 2020 | symbol 2012 (rename not informative) | 2020-09-15 (Luongo2020) |
| TEDC1 (C14orf80), TEDC2 (C16orf59) | δ/ε-tubulin complex needed for centriole architecture | **Primary/concurrent.** Top CRISPR fitness correlations; IP-MS heterodimer with TUBD1/TUBE1 [Pan2018]. Concurrent CRISPR Hedgehog screen [Breslow2018]. Mechanism [Pudlowski2025] | 2018–2025 | 2017-07-13 | 2025-08-28 (Pudlowski2025): **7-year GO lag** |
| POU2AF2 (C11orf53), POU2AF3 (COLCA2) | Coactivators of POU2F3 (tuft-cell lineage) | **Primary (dependency-driven).** Understudied selective DepMap dependencies ranked by PubMed count; "co-dependencies precalculated by DepMap revealed" POU2F3-dependent SCLC lines [Zhou2022] [verified full text]. Concurrent [Wu2022] (DepMap role not verified) | 2022 | 2022-03-14 / 2022-06-06 | 2022-06-30 (Wu2022) |
| TMEM242 | ATP-synthase c-ring and complex I assembly | **Supporting.** Wainberg prediction (mitochondrial respiration) [Wainberg2021]; Perturb-seq [Replogle2022]; biochemistry [Carroll2021] | 2021–2022 | symbol 2011 | 2021-09-27 (Carroll2021) |
| FIRRM (C1orf112) | FIGNL1 partner; RAD51 filament disassembly; ICL repair | **Not shown.** Found by chemogenetic ICL screens [Mazouzi2023], PICH synthetic-lethal screen [Stok2023], and as "Apolo1" (PLK1) [Xu2021]; FIGNL1 complex [Tischler2024]. A DepMap FIGNL1 co-dependency is widely assumed but not documented in the abstracts I read [unverified] | 2021–2024 | 2023-02-20 | 2023-03-02 (Xu2021) |
| AIRIM (C1orf109) | Late cytoplasmic pre-60S maturation with SPATA5/SPATA5L1/CINP | **Not shown** (CRISPR screen plus ribosome labelling [Ni2022]). SPATA5L1 also a Perturb-seq ribosome-biogenesis hit [Replogle2022] | 2022 | 2023-03-20 | 2022-04-27 (Ni2022) |
| TMEM41B | ER lipid scramblase; autophagosome formation; flavivirus/coronavirus host factor | **Not shown.** Genome-wide autophagy-reporter CRISPR screen [Morita2018]. I found no source documenting DepMap co-essentiality as the discovery route | 2018 | no rename | 2018-08-16 (Morita2018) |

**Negative lessons, kept as exclusion tests.**
- **C19orf52/TIMM29** (TIM22 translocase; [Kang2016; Callegari2016]) and **TMEM261/DMAC1** (complex I assembly; [Stroud2016]) were among Wainberg's "uncharacterised" predictions [Wainberg2021, bioRxiv]. Both had been characterised in 2016.
  - This shows that an annotation-score definition can lag the literature by about 2 years.
  - These genes are useful as "should-have-been-excluded" checks for our definition.
- **PTAR1** (Golgi in Wainberg) has since been linked to vesicle trafficking via its yeast orthologue ECM9 in the HAP1 GI map [Billmann2026]. Its experimental GO annotation is still thin (only HTP/IPI found).
- **DHRS7B and TMEM41A** were flagged as uncharacterised SREBP-cluster genes in 2019 [Kim2019]. QuickGO shows no experimental GO annotation for DHRS7B, and only IPI annotations from high-throughput interactome papers for TMEM41A.
  - So they may still meet our definition.
  - I flag this only as a literature note; nothing about them was looked up in any network output.
- **Zhou et al. 2022** list C3orf38, TMEM164, ZNF511, KCNK13, BEST3, CYB561A3 and C12orf49 as top understudied selective dependencies [Zhou2022]. This is again a literature note, not a prediction.

### 2.2 Use as positive controls (temporal hold-out)

- **Strongest controls:** SPRING1, PEDS1, CCDC32, INTS15, HAPSTR1, SLC25A51, TEDC1/2, POU2AF2/3 and TMEM242.
  - Each was uncharacterised before about 2018 and acquired a specific, experimentally supported function afterwards.
  - For each, the literature records co-essentiality (or DepMap dependency) as a primary or concurrent route.
- **Weaker controls:** FIRRM, AIRIM and TMEM41B, because the co-essentiality route is undocumented.
- **Expected signal strength.** Controls whose partners form large, stable complexes (INTS15–Integrator, TEDC1/2–tubulins, SLC25A51–ETC) should be easiest for zavg_BEF, given its large-complex bias [Coessentiality_tool].
  - Pathway-level functions (SPRING1–SREBP/S1P, HAPSTR1–stress signalling, POU2AF2–lineage TF) test non-complex co-functionality, which zavg_BEF was not tuned for.
- **Possible tuning leakage.** zavg_BEF's hyper-parameters were selected on hu.MAP 3.0 complexes built from Complex Portal 2022_07 [Fischer2025; Coessentiality_tool].
  - Any control whose complex appears in the hu.MAP train positives (for example Integrator, if INTS15 is included) was indirectly "seen" during tuning.
  - Check membership against `humap_train/Train_positive_pairs.txt`, which is an evaluation label file, not prediction output, and report those controls separately.

### 2.3 Annotation-timing pitfalls found while compiling the table

- **QuickGO `date` is a last-modified date.**
  - C19orf25 IPI annotations from 2005 and 2014 papers carry the date 2026-07-25.
  - So "earliest annotation date" from current GOA cannot date knowledge.
  - Use archived GO releases (2004-03-01 to 2026-08-05; [GO_archive_web]) or UniProt previous releases (2010_01 to 2026_02; [UniProt_prev_releases_web]).
- **Circular annotations exist.** CCDC32's IDA annotations cite PMID 33859415, which is Wainberg et al. 2021. A temporal hold-out that counts such annotations as "gold standard" rewards co-essentiality for agreeing with itself.
- **HTP and complex-map annotations.** INTS15's first experimental GO annotation came from hu.MAP 2.0, a high-throughput co-fractionation and AP-MS integration [Drew2021].
  - Decide in advance whether HTP- or IPI-only annotations count as "characterised". GO now has dedicated HTP codes (HDA/HMP/HGI/HEP) [GO_evidence_web].
- **HGNC renames are a cheap, objective proxy.** C#orf → functional symbol (with `prev_symbol` and `date_symbol_changed`) tracks characterisation well for C-orf genes.
  - Renames can precede function (CCDC32 2017, TEDC1/2 2017) or never happen (TMEM41B, SLC25A51).
  - HGNC policy uses C#orf# names for genes of unknown function [Bruford2020; Seal2023].

---

## 3. Defining "uncharacterised" / understudied genes

### 3.1 What the literature shows

- **Attention is concentrated and self-reinforcing.**
  - About 5% of protein-coding genes account for half of all publications, and genes reported by 1991 (16%) received 49% of the 2015 literature [Stoeger2018].
  - Stoeger et al. built fractional per-gene attention from gene2pubmed, each paper contributing 1/n_genes. They predicted publication counts from intrinsic gene features (Spearman 0.64; 0.87 when homolog data are added) [Stoeger2018] [verified via full-text summary].
  - Early-stage research on a gene differs from later research [Stoeger2022].
  - Annotation inequality (Gini) across GO and other resources rose over time, and published disease genes tracked annotation, not molecular evidence [Haynes2018].
  - The "ignorome" is persistent, and the main distinguishing feature of neglected genes is date of discovery [Pandey2014]. See also the commentary in [Edwards2011].
- **Unknome / knownness** [Rocha2023] [verified full text].
  - Knownness is the evidence-weighted sum of a protein's GO annotations: experimental codes 0.8, TAS 0.9, IC 1.0, sequence/phylogeny codes 0.3–0.6, and IEA/ND/NR/IRD/IKR 0.
  - It is aggregated per PANTHER family as the maximum over human and 11 model organisms. Location terms can be excluded.
  - Of 7,515 clusters containing a human protein, about 1,606 score below 2.0.
  - The share of human clusters scoring ≤ 2 fell from 43% to 23% over roughly a decade.
  - The database (build 18 Mar 2026) covers 15,589 families across 143 species [Unknome_web].
  - Caveat: family-level maxima mean a human gene with a well-studied paralog or orthologue counts as "known".
- **"Hidden in plain sight."** About 20% of proteins, even in well-studied organisms, lack informative descriptions. The authors define characterisation by GO-slim biological-process coverage [Wood2019] [verified].
- **Understudied Proteins Initiative.** Calls for agreed metrics of "understudied" and for functional proteomics to link unknown to known proteins [Kustatscher2022] [abstract-level].
- **IDG Tdark** [Oprea2018; Sheils2021; TCRD_web].
  - Tdark means no qualifying drug or small-molecule activity and at least 2 of 3 criteria: Jensen-lab PubMed text-mining score < 5; ≤ 3 GeneRIFs; ≤ 50 antibodies (Antibodypedia).
  - Tbio additionally includes any target with an experimental GO MF/BP *leaf* annotation.
  - TCRD v6.13.4 lists 5,679 Tdark out of 20,412 targets [TCRD_web] [verified, retrieved 2026-10-29].
  - Thresholds have changed between releases [Sheils2021].
- **UniProt annotation score** [UniProtHelp_AnnotationScore; UniProt2025].
  - A heuristic 1–5 measure of annotation *content*, explicitly "not … a measure of the accuracy".
  - Experimental evidence scores higher than predicted. It is the sum over names, comments, features, GO and cross-references.
  - In release 2026_03, reviewed human entries break down as 351 (score 1), 1,355 (score 2), 2,155 (3), 1,906 (4) and 14,664 (5) [UniProtQuery_2026_03].
  - Every success-story gene in §2 now scores 5, so the score moves quickly once a gene is studied.
- **GO evidence codes** [GO2023; GO_evidence_web].
  - Experimental: EXP, IDA, IPI, IMP, IGI, IEP.
  - High-throughput: HTP, HDA, HMP, HGI, HEP.
  - Phylogenetic: IBA etc. The PAN-GO effort now gives integrated function models for ~82% of human protein-coding genes [Feuermann2025], so IBA presence says little about direct knowledge.
  - Computational: ISS etc.
  - Electronic: IEA.
  - ND means no data.
  - Electronic annotations' reliability "rivals" curator non-experimental annotations, and >98% of annotations are uncurated [Skunca2012].
- **PubMed counts (gene2pubmed) pitfalls** [gene2pubmed_web].
  - High-throughput papers link thousands of genes; Stoeger's fractional counting addresses this.
  - Symbol ambiguity and aliases (old C-orf symbols, common-word symbols).
  - Spreadsheet symbol corruption affects about one-fifth of papers with Excel gene lists [Ziemann2016].
  - Disease-association or GWAS mentions are not functional characterisation.

### 3.2 Comparison of candidate metrics

| Metric | Measures | Reproducible/versioned? | Main bias | Fit for us |
|---|---|---|---|---|
| Experimental GO BP/MF annotations (gene-level) | Curated functional knowledge | Yes (dated GO releases since 2004) | Curation lag (TEDC1/2: 7 yr); IPI "protein binding" from HTP interactomes inflates knownness; circular DepMap-derived IDAs | **High.** Directly matches "function unknown"; enables temporal hold-out |
| Unknome knownness (family-level) | Weighted GO evidence over orthologs and paralogs | Yes (builds dated) | Family max hides human-specific ignorance; partly subjective weights | Medium. Good secondary filter for conserved unknowns |
| UniProt annotation score ≤ 2 | Overall entry richness | Per release (previous releases archived) | Heuristic; feature-rich unknowns score high; lags literature (TIMM29, DMAC1 example) | Medium–high. Wainberg precedent allows direct comparison |
| gene2pubmed fractional count | Literature attention | Yes if file dated | HTP papers, aliases, non-functional mentions | Medium. Useful to catch curation lag |
| IDG Tdark | Literature + reagents + drugs | TCRD versions | Includes antibody availability; text-mining score counts any mention | Medium. Externally recognised label |
| HGNC C#orf# / FAM / TMEM / KIAA naming | Nomenclature placeholder | Yes (HGNC history) | Many named genes are unknown and some C-orfs are known | Low as a definition; good as a sanity check |

### 3.3 Selection effects to anticipate

- **Uncharacterised genes are systematically different.** They are less essential on average: mean DepMap dependency for Tdark −0.07 vs −0.17 for Tbio in DepMap 21Q1, from a secondary summary [unverified]. They are also lower-expressed and more often paralog-buffered [Dede2020].
  - Many will therefore have flat CRISPR profiles and no co-essentiality information.
  - The pre-registered list must be defined without DepMap-network information. A *profile-informativeness* eligibility rule (for example a minimum gene-level standard deviation or number of dependent lines, computed on single-gene profiles, not pairs) is defensible only if fixed before any pairwise computation. This is a design decision for the PI.
- **Annotation-based definitions favour genes outside large, well-annotated families**, while knownness by family max favours conserved families [Rocha2023]. Report both.

### 3.4 Recommended operational definitions

**D1, primary: "no experimental functional GO annotation".**
- *Universe.* HGNC protein-coding genes (locus type "gene with protein product") that map to a DepMap 26Q3 gene column.
- *Uncharacterised criterion.* In a single frozen human GOA release (record date and checksum), the gene has **zero** BP or MF annotations with EXP/IDA/IMP/IGI/IEP/TAS/IC evidence, and zero IPI annotations to any term other than "protein binding" (GO:0005515) and its generic children.
  - IEA, ISS/ISO/ISA/ISM, IBA/IRD/IKR, NAS, ND and all HTP codes are ignored.
  - CC-only knowledge does not count as functional.
  - This mirrors the TCRD Tbio rule and the Rocha weights, but is gene-level and stricter on interactions.
- *Pros.* Objective, versioned, directly re-applicable to archived releases (§4.1).
- *Cons.* Curation lag; requires a defined list of "generic binding" terms.

**D2: UniProt annotation score ≤ 2** (reviewed entries, release 2026_03; 1,706 entries).
- *Pros.* Identical to Wainberg et al.'s definition, so results are directly comparable; trivially reproducible.
- *Cons.* Heuristic; lags literature; ignores unreviewed isoforms.

**D3: low literature attention.**
- Fractional gene2pubmed count (each PMID weighted 1/n_genes linked to it; papers linking > 50 genes excluded as high-throughput; date-stamped file) below a pre-set quantile, **or** IDG Tdark in a named TCRD version.
- *Pros.* Catches genes characterised in papers not yet curated into GO.
- *Cons.* Symbol/alias noise; mentions are not function.

**Recommendation**
- Pre-register the set **D1 ∩ (D2 ∪ D3)**: no experimental functional GO annotation, plus either a low UniProt score or low literature attention.
- Report the three single-criterion sets and their overlaps as sensitivity analyses.
- Manually audit a random sample (for example 50 genes), with a recorded reviewer, for false "unknowns" caused by curation lag, such as the TIMM29/DMAC1 pattern.
- Freeze all source versions and checksums in DATA.md before any network computation.

---

## 4. Validation designs and pitfalls for guilt-by-association prediction

### 4.1 Temporal hold-out (CAFA-style)

- **CAFA design.** Predictors are frozen at time t0, and targets are the proteins that gain experimental annotations between t0 and t1 [Radivojac2013; Jiang2016; Zhou2019].
  - Molecular-function and biological-process predictions improved modestly over rounds; cellular component did not. Term-centric prediction remained hard [Zhou2019] [verified].
  - MouseFunc gave an earlier mammalian precedent: 41% precision at 20% recall, with 26% of GO terms reaching > 90% precision [PenaCastillo2008] [verified].
- **Our version.**
  1. Use archived GO (or UniProt) releases. Choose t0 before most DepMap-derived function papers (for example a GO release from late 2018, before the Wainberg preprint) and t1 = the release frozen for the project.
  2. Targets are genes that were "uncharacterised" by D1 at t0 and gained experimental BP/MF annotations by t1.
  3. Remove target annotations whose reference used DepMap co-essentiality (for example CCDC32's IDA from Wainberg 2021, and the papers in §2 marked Primary). Report results with and without them.
- **Caveat.** The DepMap 26Q3 data post-date t0. This is acceptable because the method uses no annotations, but it is not a strict prospective test. More cell lines than were available at t0 could also inflate performance relative to what was possible then.
- **Metrics.** Use per-gene precision at top-k terms, and information-accretion-aware metrics that down-weight trivially predictable general terms (remaining uncertainty and misinformation, Smin) [Clark2013].

### 4.2 Multifunctionality and hub bias

- **Gillis & Pavlidis 2011.** "Knowledge of the degree of multifunctionality alone can produce astonishingly strong performance" as a function predictor. Networks encode multifunctionality through node degree [Gillis2011] [verified].
- **Gillis & Pavlidis 2012.** Functional information is concentrated in "very few interactions", so cross-validated performance often rests on a handful of critical edges [Gillis2012] [verified].
- **EGAD** provides fast GBA AUROCs alongside the matching node-degree-only predictor [Ballouz2017].
- **Implications.**
  - (i) Always report a degree/multifunctionality-only baseline, and a baseline using gene-level essentiality statistics (mean, SD) only.
  - (ii) For each prediction, report the specific supporting edges. A prediction resting on one or two strong edges is typical, not a weakness.
  - (iii) Prefer predictions supported by partners that are *not* hubs.

### 4.3 Circularity and leakage

| Source of circularity | Evidence | Mitigation |
|---|---|---|
| GO annotations derived from co-essentiality papers | CCDC32 IDA cites Wainberg 2021 (QuickGO) | Exclude by reference PMID from gold standards; keep a list of DepMap-derived PMIDs |
| Integrated networks containing DepMap | HumanNet v3 GI layer includes DepMap 20Q4 co-essentiality [KimCY2022] [verified]; SPOC/Predictomes uses DepMap Chronos as a feature [Schmid2025] [verified key-resources table] | Do not use these as "orthogonal" support, or use DepMap-free variants only |
| STRING text-mining and curated-database channels | Text mining reads the literature that defines the answer; curated databases embed GO/KEGG/Reactome [Szklarczyk2023] | Use only the experiments and co-expression channels (and STRING v11 from 2019 for the hold-out) [Szklarczyk2019]; I found no statement that STRING ingests DepMap (not exhaustively checked) |
| Method tuning on hu.MAP 3.0 | zavg_BEF hyper-parameters selected on hu.MAP 3.0 train pairs [Coessentiality_tool] | Treat hu.MAP agreement as partially non-independent; report hu.MAP-supported predictions separately |
| Pair-level evaluation leakage | Performance drops sharply for pairs involving unseen proteins [Park2012] | Gene-disjoint evaluation for any supervised component |

### 4.4 GO term specificity and redundancy

- **Restrict term size and redundancy.**
  - Restrict to terms with roughly 5–200 human genes, both for informativeness and enrichment power. Wainberg used a minimum of 5 [Wainberg2021]; the upper bound is a convention, not a cited standard.
  - Handle the DAG with elim/weight or parent–child methods [Alexa2006; Grossmann2007].
- **Bias in common gold standards.** These standards are themselves functionally biased, for example toward ribosome and other large processes [Myers2006]. Expert-curated, process-balanced standards and per-term reporting are recommended [Myers2006; Rahman2021].
- **Complex membership is the natural target vocabulary** for a co-complex-trained method: Complex Portal, CORUM 4.0 (5,204 complexes, 26% of human protein-coding genes) [Tsitsiridis2023], and GO CC "protein-containing complex" terms. Process-level BP transfer should be a secondary claim.

### 4.5 Enrichment statistics and null models for neighbourhood annotation

- **Hypergeometric/Fisher test of neighbour annotations.**
  - The background must be the scorable universe: genes present in DepMap and annotated in the chosen release. Using the whole genome inflates significance [Timmons2015].
  - Apply BH-FDR across genes × terms [Benjamini1995]. Neighbourhoods overlap, so tests are dependent, and permutation calibration is preferred.
- **Null models.**
  - (a) **Matched-gene null.** Replace the query gene with random genes matched on profile SD, mean effect and NaN fraction, and recompute neighbour enrichment. This controls for "essential genes neighbour essential genes".
  - (b) **Degree-preserving rewiring** of the kNN graph [Maslov2002].
  - (c) **Label permutation** within term-size bins.
  - (d) **Same-arm exclusion control.** Recompute enrichment after dropping neighbours on the same chromosome arm [Lazar2024], or within 20 Mb [Kim2019].
- **Network-size effect.** Bigger networks recover more disease genes; this is not necessarily higher accuracy [Huang2018]. When comparing to orthogonal networks, normalise for size.

---

## 5. Orthogonal datasets to reinforce or downweight predictions

Datasets marked **L** are already on disk (DATA.md).

| Dataset | What it adds | Coverage | Caveats / circularity |
|---|---|---|---|
| **hu.MAP 3.0** [Fischer2025] | Integrated co-complex map from >25,000 MS experiments | >15,000 complexes; ~70% of human proteins; hypotheses for 472 uncharacterised proteins (AlphaFold-supported) [verified] | The tool was tuned on hu.MAP 3.0 train pairs (**L**). Complexes ≤ 30 subunits in the gold standard. Agreement is partly non-independent |
| **BioPlex 3.0** **L** [Huttlin2021] | AP-MS interactions in two cell lines | 293T: 10,128 baits, 118,162 interactions, 14,586 proteins; HCT116: 5,522 IPs [verified] | Overexpressed tagged baits; cell-specific "rewiring". hu.MAP integrates BioPlex, so don't double count |
| **HuRI** [Luck2020] | Binary Y2H interactions | ~53,000 PPIs [verified] | Binary contacts, sparse for complexes; low overlap with AP-MS |
| **OpenCell** [Cho2022] | Endogenous tagging: live-cell localisation + IP-MS in HEK293T | ~1,300 proteins [unverified count] | Localisation is highly informative per the authors, but limited coverage |
| **Human Cell Map (BioID)** [Go2021] | Proximity-based localisation | 192 markers; 4,145 proteins localised in HEK293 [verified] | Proximity ≠ binding; one cell line |
| **HPA subcellular (Cell Atlas)** [Thul2017] | Antibody IF localisation | 12,003 proteins, 30 structures; ~half multi-localised [verified] | Antibody specificity; use reliability tiers |
| **CCLE proteomics** **L** [Nusinow2020] | Protein co-abundance across cancer lines (same lines as DepMap, partly) | 375 lines [verified] | Shared cell lines are not fully independent of DepMap; complex members co-vary strongly |
| **ProCan-DepMapSanger** [Goncalves2022] | Larger cell-line proteomics | 949 lines; 8,498 proteins [verified] | Same caveat; Sanger data access terms not checked |
| **ProteomeHD / ProteomeHD.2** [Kustatscher2019; Fischer2025] | Co-regulation across 294 perturbations (treeClust) | 10,323 proteins [verified] | Captures non-physical co-function; not cell-line based, so more independent of DepMap |
| **Genome-wide Perturb-seq** [Replogle2022; Nadig2025] | Transcriptional phenotype per CRISPRi perturbation; clustering assigns function | K562: 9,866 expressed genes; RPE1 and K562 essential screens (2,057 genes); >2.5M cells [verified] | CRISPRi (orthogonal to Cas9 cutting artefacts). Many weak perturbations: a typical perturbation affects ~45 genes, essentials >500 [Nadig2025]. Same RPE1/K562 context |
| **Optical pooled screens** [Funk2022] | Imaging phenotypes of essential-gene knockouts | 5,072 fitness genes, HeLa; phenotypes for >90% [secondary summary of abstract] | Limited to essential genes |
| **Chemogenetic CRISPR screens** [Olivieri2020] | Gene–drug sensitivity profiles (DNA damage response) | 31 screens, 27 genotoxins, RPE1; 890 genes [verified] | Pathway-specific (DDR); one cell line. FIRRM and HAPSTR1 (TAPR1) were found by such screens [Mazouzi2023; Benslimane2021] |
| **HAP1 genetic-interaction map** [Billmann2026] | Isogenic digenic interactions | ~4M pairs, ~89,000 interactions [verified] | Weak overlap with DepMap, so genuinely complementary |
| **DEMETER2 RNAi** **L** [McFarland2018] | Independent perturbation modality for replicating co-dependency | 3 integrated RNAi datasets [verified]; ~700 lines [unverified] | Seed-based off-target effects; fewer genes are well measured. CRISPR recalls more complexes than RNAi [Pan2018] |
| **STRING v11/v12/v12.5** [Szklarczyk2019; Szklarczyk2023; Szklarczyk2025] | Integrated associations | Genome-wide | Use only the experiments and co-expression channels; exclude text mining and databases (§4.3) |
| **Predicted interactomes** [Burke2023; Zhang2025; Schmid2025; Schmid2025b; Humphreys2021] | Structural plausibility of a predicted partner | Burke: 65,484 pairs modelled, 3,137 high-confidence. Zhang: 200M pairs screened, 17,849 PPIs at ~90% expected precision, 3,631 new. Schmid preprint: ~16,000 PPIs at ~90% precision, >5,000 new [verified] | SPOC/KIRC classifiers use omics features incl. DepMap [Schmid2025], so not orthogonal. Zhang2025 is coevolution/DL-based, so more independent. Humphreys2021 is yeast only (useful for conserved unknowns) |
| **HumanNet v3** [KimCY2022] | Integrated functional network | Genome-wide | **Contains DepMap co-essentiality**: do not use as support |
| **CORUM 4.0 / Complex Portal** [Tsitsiridis2023] | Curated complexes for calibration | 5,204 complexes | Bias toward well-studied complexes |
| **MitoCarta3.0** [Rath2021] | Mitochondrial localisation, to flag the mito-dominance regime | Human mitochondrial proteome | Use to stratify, not to support |
| **Ensembl paralogues** **L** | Flags paralog buffering and paralog-driven correlation | Genome-wide | Paralog pairs can co-correlate by sequence-shared sgRNAs or redundancy |

**How others have combined these data**
- Pan et al. intersected co-essentiality with PPI networks to find complexes of unknown genes [Pan2018].
- hu.MAP 3.0 used ProteomeHD.2 covariation and AlphaFold to support hypotheses [Fischer2025].
- SPOC combines AlphaFold-Multimer structure metrics with omics features [Schmid2025].
- The HAP1 GI study integrated networks with deep-learning fusion (BIONIC) after onion normalisation [secondary summary; unverified].

**Recommended rule of thumb.** For each predicted gene–function pair, record three things separately: (i) physical evidence (AP-MS, BioID, IP-MS, predicted structure); (ii) co-localisation; (iii) an independent perturbation modality (RNAi, CRISPRi Perturb-seq, chemogenetic). Upweight a prediction when ≥ 2 independent classes agree. Downweight it when localisation is incompatible, for example a nuclear prediction for a protein reliably localised to mitochondria in HPA and OpenCell.

---

## 6. Implications for this project's design

1. **Pre-register "uncharacterised" as D1 ∩ (D2 ∪ D3)** (§3.4).
   - Use a frozen GOA file, UniProt 2026_03 and a dated gene2pubmed, with versions and checksums in DATA.md.
   - Publish the three single-criterion sets and their overlaps.
   - Include a manual audit of a random sample for curation lag (TIMM29/DMAC1 pattern).
2. **Fix eligibility rules before any pairwise computation.** Map to DepMap 26Q3 columns, set a NaN threshold, and exclude mtDNA and multi-copy genes. If a profile-informativeness rule is used, compute it on single-gene profiles only. State that genes with flat profiles are "not assessable", not "negative" [Dede2020; Billmann2026].
3. **Calibrate the method on characterised genes first.** Leave-one-gene-out neighbourhood annotation, and per-term and per-complex (macro) precision@k. Compare to GLS and to degree-only and essentiality-only baselines (EGAD-style) [Gillis2011; Ballouz2017; Rahman2021].
4. **Run a CAFA-style temporal hold-out** on archived GO releases (t0 ≈ late 2018). Use the §2 positive controls as a named subset. Exclude, or report separately, annotations whose PMIDs are DepMap-derived [Radivojac2013; Zhou2019]. Do not use QuickGO annotation dates for timing (§2.3).
5. **Use complex membership as the primary vocabulary** (Complex Portal/CORUM, GO CC complexes), because zavg_BEF was trained and benchmarked on co-complex labels. Treat BP/pathway transfer as secondary and lower-confidence [Coessentiality_tool].
6. **Control proximity and copy-number artefacts explicitly.** Flag or drop neighbours on the same chromosome arm (or within 20 Mb), and require the prediction to survive their removal [Lazar2024; Kim2019]. The tool's residual OR-cluster signal makes this mandatory [Coessentiality_tool].
7. **Control mitochondrial and ribosomal dominance.** Stratify predictions by MitoCarta membership and large-complex neighbourhoods. Report enrichment of predicted functions against what the null produces [Rahman2021; Rath2021].
8. **Use matched-gene and degree-preserving null models** for neighbourhood enrichment, with a correct background and BH-FDR. Use DAG-aware term pruning [Maslov2002; Timmons2015; Alexa2006; Grossmann2007].
9. **Report the specific edges behind each prediction** (top partners, their annotations, their hub status). GBA signal sits in few edges [Gillis2012].
10. **Build a circularity blacklist:** HumanNet, SPOC/Predictomes and STRING text-mining/database channels; GO annotations citing co-essentiality papers; and hu.MAP agreement (tuning overlap) flagged as partially dependent [KimCY2022; Schmid2025; Coessentiality_tool].
11. **Score orthogonal support in independent classes** (physical, localisation, other perturbation modality) and pre-specify upweight/downweight rules before seeing predictions (§5).
12. **Replicate with RNAi.** Check whether a CRISPR prediction is reproduced in DEMETER2 co-dependency on shared lines, accepting lower sensitivity [McFarland2018; Pan2018]. This addresses Cas9-specific artefacts.
13. **Run paralog checks.** Flag predictions whose top partner is a paralog (Ensembl 116), and interpret low-variance profiles in light of buffering [DeKegel2019; Dede2020].
14. **Compare against prior catalogues as an external benchmark,** not as evidence: Wainberg's 108 predictions, hu.MAP 3.0's 472 uncharacterised-protein hypotheses, and Perturb-seq function assignments [Wainberg2021; Fischer2025; Replogle2022]. Record agreements and disagreements without tuning to them.
15. **Literature deep-dive protocol for top candidates.**
    - Search current symbols, all HGNC previous symbols, aliases and UniProt accession.
    - Check bioRxiv; preprints are where several functions first appeared (INTS15, HAPSTR1).
    - Classify each hit as functional evidence, high-throughput association or mention [Ziemann2016; Stoeger2018].

---

## Reference keys

Full metadata (authors, year, title, journal, DOI or URL, verification status and notes) is in `references/literature_refs.tsv` (123 rows, all verified on 2026-10-29).

**Co-essentiality and DepMap:** Tsherniak2017, Meyers2017, Dempster2019, Dempster2021, McFarland2018, Pacini2021, Behan2019, Pan2018, Boyle2018, Kim2019, Rauscher2018, Rahman2021, Wainberg2021, Amici2021, Gheorghe2022, Pan2022, Hassan2023, Chen2023, Rohde2025, Billmann2026, Lazar2024, Vinceti2024, DeKegel2019, Dede2020, Hirschey2026, Coessentiality_tool.

**Success stories:** Kory2020, Luongo2020, Girardi2020, Bayraktar2020, Aregger2020, Loregger2020, Xiao2021, GallegoGarcia2019, Werner2020, Harel2020, Sloan2026, Offley2023, Razew2024, Drew2021, Amici2022, Benslimane2021, Amici2024, Wu2022, Zhou2022, Stok2023, Mazouzi2023, Tischler2024, Xu2021, Breslow2018, Pudlowski2025, Stroud2016, Kang2016, Callegari2016, Morita2018, Ni2022, Carroll2021.

**Understudied genes and annotation:** Rocha2023, Stoeger2018, Stoeger2022, Haynes2018, Kustatscher2022, Oprea2018, Sheils2021, Wood2019, Pandey2014, Edwards2011, GO2023, UniProt2025, Feuermann2025, Skunca2012, Seal2023, Bruford2020, Ziemann2016, UniProtHelp_AnnotationScore, UniProtQuery_2026_03, TCRD_web, Unknome_web, GO_evidence_web, GO_archive_web, UniProt_prev_releases_web, gene2pubmed_web, QuickGO_HGNC_queries.

**Validation:** Gillis2011, Gillis2012, Myers2006, PenaCastillo2008, Radivojac2013, Jiang2016, Zhou2019, Clark2013, Ballouz2017, Park2012, Huang2018, Timmons2015, Alexa2006, Grossmann2007, Maslov2002, Benjamini1995.

**Orthogonal data:** Fischer2025, Huttlin2021, Luck2020, Cho2022, Go2021, Thul2017, Nusinow2020, Kustatscher2019, Goncalves2022, Olivieri2020, Funk2022, Replogle2022, Nadig2025, Szklarczyk2019, Szklarczyk2023, Szklarczyk2025, Burke2023, Humphreys2021, Zhang2025, Schmid2025, Schmid2025b, Tsitsiridis2023, Rath2021, KimCY2022.
