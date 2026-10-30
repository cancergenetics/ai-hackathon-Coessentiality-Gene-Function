
# Methods

The analysis followed DESIGN.md v2.3, frozen at git tag `design-frozen` (commit afed1dd), with every later change logged
in DEVIATIONS.md (summarised at the end of this section, including which rows were logged after the affected result).
All steps were run by scripts in `scripts/`, numbered in execution order (README.md gives the run order). Table 3 defines
the notation.

**Table 3. Notation.**

| Symbol | Meaning |
|---|---|
| U | pre-registered uncharacterised genes (4,924) |
| H | temporal hold-out: genes uncharacterised at t0 (GO 2018-07-02) that gained experimental BP/MF targets since (820; 809 primary) |
| LOO | characterised leave-one-out genes used to choose the ranker |
| D1, D2, D3 | knownness criteria: no experimental BP/MF GO; UniProt annotation score ≤ 2; low focused literature or IDG Tdark |
| N(g), K | the gene's top K = 25 co-essentiality neighbours after exclusions |
| R(g) | split-half reproducibility of N(g) |
| R1, R2, R3 | term rankers: raw neighbour support, hypergeometric, empirical |
| V2; V1, V1′ | primary vocabulary (GO BP + MF); descriptive module labels (GO complexes; plus Complex Portal and MitoCarta) |
| p_cal | calibrated probability that the top term is confirmed, given that the gene gains experimental annotation |
| Σp_cal | sum of p_cal over a gene set (expected conditional confirmations) |
| Tier A / B | pre-specified prioritisation tiers (p_cal ≥ 0.5 / ≥ 0.3 plus conditions) |
| S20; extra30 | secondary list of 20 strong uncalibrated predictions; 30 fill-pool genes outside the top 40 |
| N1, N2, N3 | literature class: function established; partial; none |
| L | blind literature agent |
| definition-artefact flag | UniProt score 5, Complex Portal subunit or experimental GO cellular-component annotation [post-review] |

## Data and versions

Table 1 lists the principal inputs. Every raw file was checksummed (SHA-256) and verified by script before use.
Restricted-licence files were used internally and are not redistributed.

**Table 1. Principal data sources** (URLs, checksums and licences: DATA.md).

| Source | Version | Use |
|---|---|---|
| DepMap CRISPRGeneEffect (Chronos) [DepMap_web; Dempster2021] | Public 26Q3 <!-- src: DATA.md -->; 1,361 lines × 18,434 genes <!-- src: results/assessability/splithalf_runs.md; results/verification/sanity_checks.md --> | co-essentiality |
| DepMap Model, CRISPRConfounders, expression, copy number, mutations [DepMap_web] | 26Q3 <!-- src: DATA.md --> | strata, split halves, artefact flags |
| DEMETER2 RNAi [McFarland2018] | v6 <!-- src: DATA.md --> | robustness only |
| HGNC [Seal2023] | 2026-04-23 <!-- src: DATA.md --> | universe, identifiers |
| GO ontology and human GAF [GO2023] | 2026-07-26 / 2026-05-21 <!-- src: DATA.md --> | D1, vocabularies, targets |
| Archived GO [GO_archive_web] | 2018-07-02 (t0), 2019-07-01 <!-- src: DATA.md --> | temporal hold-out |
| UniProtKB/Swiss-Prot [UniProt2025] | 2026_03 <!-- src: DATA.md --> | D2, identifiers |
| NCBI gene2pubmed [gene2pubmed_web] | 2026-10-29 <!-- src: DATA.md --> | D3, literature cut-off |
| TCRD development levels [Sheils2021] | 2023 <!-- src: DATA.md --> | D3 (Tdark) |
| Ensembl paralogues, coordinates [Dyer2025] | 116 <!-- src: DATA.md --> | exclusions, tandem stratum |
| Orthogonal: BioPlex 3.0 [Huttlin2021], OpenCell [Cho2022], BioGRID [Oughtred2021], STRING v12.5 <!-- src: DATA.md --> [Szklarczyk2025], Human Cell Map [Go2021], ProteomeHD [Kustatscher2019], CCLE proteomics [Nusinow2020], Perturb-seq [Replogle2022], Olivieri screens [Olivieri2020], AlphaFold2 pairs [Burke2023], HPA [Thul2017], MitoCarta3.0 [Rath2021], Complex Portal [Meldal2022], hu.MAP 3.0 [Fischer2025] | DATA.md | support, admission |

Genes were identified by HGNC ID through a hub that joined Entrez (DepMap), UniProt and Ensembl identifiers; symbols were
never join keys. All 18,434 <!-- src: results/ids/hgnc_hub_qc.md --> DepMap columns mapped. A gene was **scorable** if it
had a DepMap column and at least one <!-- src: preregistration/CRITERIA.md --> UniProt accession mapped uniquely to it by
the tool's rule.

## The co-essentiality method

We used zavg_BEF from the ai-hackathon-Coessentiality tool [Coessentiality_tool] at commit 3c684c9
<!-- src: DATA.md -->, unmodified, through its public API and with its published configuration. In brief
(external/coessentiality/docs/explainer/METHOD.md; the description here is intended to allow reimplementation without
the repository), gene profiles were centred and standardised for covariance
estimation. The 20 <!-- src: results/matrices/zavg_full_manifest.json --> strongest cell-line covariance components
were removed and the rest ridge-whitened (ridge 0.1 <!-- src: results/matrices/zavg_full_manifest.json --> × mean
eigenvalue). The method combines three views:

- **F**, the cosine similarity of the cleaned profiles;
- **B**, the row-z-scored overlap of two genes' weighted partner lists, each list being the top 0.25%
  <!-- src: results/matrices/zavg_full_manifest.json --> of background genes (44 genes here
  <!-- src: results/assessability/splithalf_runs.md -->), with the pair itself excluded;
- **E**, the cosine similarity in a 512-dimensional <!-- src: results/matrices/zavg_full_manifest.json --> Laplacian
  eigenmap [Belkin2003] of the partner graph.

Each view was z-scored against 200,000 <!-- src: results/matrices/zavg_full_manifest.json --> fixed random pairs, and
the three z-scores were averaged. Background genes had less than 10%
<!-- src: results/matrices/zavg_full_manifest.json --> missing values (17,525 genes
<!-- src: results/verification/sanity_checks.md -->). The tool's settings had been tuned on hu.MAP 3.0 co-complex pairs
[Fischer2025; Coessentiality_tool]; we tuned nothing. Because hu.MAP 3.0 post-dates t0 and contains complexes with H
genes, this tuning is a route by which post-t0 knowledge could enter zavg_BEF; GLS and Pearson, which were not tuned,
are reported beside it on H for this reason.

**Verification.** We computed one full zavg_BEF matrix, and GLS [Wainberg2021] and Pearson rows for the genes that
needed them. Our GLS and Pearson values matched the tool's on 100,993 <!-- src: results/verification/baseline_rows.md -->
random pairs (maximum absolute difference 2.96 × 10⁻⁷ <!-- src: results/verification/baseline_rows.md -->). With the
tool's own command-line interface we reproduced its published internal-test average precision (Results). All 14
<!-- src: results/verification/sanity_checks.md --> pre-specified sanity checks passed; they covered Chronos sign,
matrix symmetry, median within-complex scores above 3 <!-- src: results/verification/sanity_checks.md --> for seven
<!-- src: results/verification/sanity_checks.md --> reference complexes, and a near-zero mean over random pairs.

## Pre-registration of uncharacterised genes

The universe was the 19,296 <!-- src: preregistration/CRITERIA.md --> HGNC Approved protein-coding genes. A single
function (`src/knownness.py::d1`) applied the criteria to every GO release:

- **D1**: no informative GO biological-process or molecular-function annotation with evidence EXP, IDA, IPI, IMP, IGI,
  IEP, TAS or IC [GO_evidence_web]. The GO guide classes TAS (traceable author statement) and IC (inferred by curator)
  as author or curatorial statements rather than experimental evidence; we counted them deliberately, so that a gene
  with a curated author statement of function was not called uncharacterised, and use "experimental" below for this
  set of codes. NOT-qualified rows were removed and `contributes_to` rows counted. High-throughput,
  electronic, similarity-based, phylogenetic, RCA, NAS and ND codes were ignored, as were cellular-component
  annotations. The 22 <!-- src: preregistration/CRITERIA.md --> generic terms listed in CRITERIA.md (for example
  "protein binding", the roots and high-level grouping terms) did not count.
- **D2**: UniProt annotation score ≤ 2 <!-- src: preregistration/CRITERIA.md --> [UniProtHelp_AnnotationScore], the
  definition of Wainberg et al. [Wainberg2021].
- **D3**: at most 10 <!-- src: preregistration/CRITERIA.md --> PubMed records among those linking at most 10
  <!-- src: preregistration/CRITERIA.md --> human genes, **or** IDG Tdark [Oprea2018; Sheils2021].

The pre-registered set was **U = D1 ∩ (D2 ∪ D3)**, and no gene was ever removed from it. U contained 4,924
<!-- src: preregistration/CRITERIA.md --> genes, of which 4,275 <!-- src: preregistration/CRITERIA.md --> were in
DepMap and 4,271 <!-- src: preregistration/CRITERIA.md --> were scorable. Genes outside U served only for calibration;
no function was proposed for them.

Reporting strata (preregistration/CRITERIA.md) were: **family** (chemosensory/epidermal, from named HGNC groups; tandem
cluster, with at least 2 <!-- src: preregistration/CRITERIA.md --> Ensembl paralogues within 1 Mb
<!-- src: preregistration/CRITERIA.md -->; or other); **expressed** (log2(TPM+1) ≥ 1
<!-- src: preregistration/CRITERIA.md --> in at least 10% <!-- src: preregistration/CRITERIA.md --> of DepMap models,
or in at least 50% <!-- src: DESIGN.md --> of the lines of any lineage with at least 10 <!-- src: DESIGN.md --> lines);
**clean negatives** (log2(TPM+1) < 0.5 <!-- src: DESIGN.md --> in at least 95% <!-- src: DESIGN.md --> of lines);
**profile informativeness** (SD tertile, any dependency) and **low coverage** (outside the tool background); and the
**headline stratum** (expressed, non-chemosensory, non-tandem genes).

U was built from annotation data alone; before the freeze, DepMap was read only for its header and single-gene summaries
(preregistration/PROVENANCE.md). An independent agent, without access to our code, re-derived U and the hold-out set
from the raw files and reproduced both exactly (verify/prereg_verification.md). The list, criteria, design,
configuration, seeds, gate code, tool commit and DepMap file hashes were frozen in `preregistration/FREEZE.sha256` at
commit afed1dd, under the tags `preregistration-v1` and `design-frozen`.

To measure curation lag, an auditor agent with no access to co-essentiality output reviewed a random sample of 50
<!-- src: DESIGN.md --> U genes (seed 0 <!-- src: config/frozen.yaml -->). It searched symbols, previous symbols,
aliases, UniProt and Europe PMC including preprints, and classed each gene N1 (function established), N2 (partial) or N3
(none). Proportions are given with Wilson score intervals [Wilson1927].

## Assessability

Cell lines were split into halves stratified by lineage × screen-library combination (30 lineages
<!-- src: results/assessability/splithalf_runs.md -->), keeping lines from the same patient together, for seeds 0–4
<!-- src: config/frozen.yaml -->, and the tool was refitted on each half (10 fits
<!-- src: results/assessability/splithalf_runs.md -->). Half-neighbour lists N~A~^s^(g) and N~B~^s^(g) were the top 25
<!-- src: DESIGN.md --> genes, after the predictor's exclusions, among genes in the background of both halves and of the
full data. The reproducibility statistic was R(g) = mean~s~ |N~A~^s^(g) ∩ N~B~^s^(g)|/K, and its null analogue
R0(g, m) = mean~s~ |N~A~^s^(g) ∩ N~B~^s^(m)|/K over the first 200 <!-- src: DESIGN.md --> matched genes m (below). A gene was
**assessable** if p = (1 + #{m : R0 ≥ R})/201 <!-- src: DESIGN.md --> was below 0.05 <!-- src: DESIGN.md --> **and** the
gene was expressed. Non-expressed genes were scored anyway, so that calls on clean negatives estimate a false-call rate.
In a sensitivity analysis, extrapolated rank-biased overlap [Webber2010] with persistence 0.9
<!-- src: DEVIATIONS.md --> replaced set overlap. R(g) was computed identically for every gene and was also a calibration
covariate.

## Function predictor and vocabularies

**Vocabularies.** The primary vocabulary, V2, was GO biological process plus molecular function. Membership came from
D1-evidence, non-NOT annotations propagated over is_a and part_of at the release in use. Candidate terms had 5–200
<!-- src: config/frozen.yaml --> annotated scorable genes. Two descriptive module labels supplemented it: V1, GO
complexes under GO:0032991, and V1′, V1 plus Complex Portal and MitoCarta3.0 pathways. Each term belonged to one of eight
<!-- src: config/term_families.tsv --> module families through a fixed, ordered list of GO ancestors
(config/term_families.tsv). When g was scored, IPI rows whose with/from field named g were removed from its neighbours'
memberships.

**Neighbourhood and scores.** N(g) was the top K = 25 <!-- src: config/frozen.yaml --> background genes by zavg_BEF,
excluding g, genes on g's chromosome arm and Ensembl paralogues of g, which removes Cas9 proximity artefacts [Lazar2024]
and paralogue effects. For each term t, S(g, t) = Σ max(z~gj~, 0) over the neighbours j ∈ N(g) annotated to t. Three
rankers were pre-specified: R1, raw S; R2, the hypergeometric p of the neighbour count, with the annotated scorable genes
as background; and R3, an empirical p against matched genes, p~emp~ = (1 + #{m ∈ M(g) ∖ A~t~ : S(m, t) ≥ S(g, t)})/(1 + |M(g) ∖
A~t~|), where A~t~ are the genes annotated to t.

**Matched genes.** M(g) held the 500 <!-- src: config/frozen.yaml --> scorable genes nearest to g in Mahalanobis
distance on mean effect, log SD and missing fraction [Rubin1980; Stuart2010], with background status matched exactly
and g, N(g), same-arm genes and paralogues excluded. The caliper was 0.2 <!-- src: config/frozen.yaml -->, with
nearest-available fallback (seed 0 <!-- src: config/frozen.yaml -->). Among the first five matches, 2.9%
<!-- src: results/verification/matched_lists.md --> fell outside the caliper, and standardised mean differences over
all scorable genes were at most 0.002 <!-- src: results/verification/matched_lists.md --> in absolute value. The first
five <!-- src: config/frozen.yaml --> matches served as the null comparator, the first 200
<!-- src: config/frozen.yaml --> as the assessability null, and all 500 <!-- src: config/frozen.yaml --> as the R3
reference.

**Output.** A term was reportable if at least 2 <!-- src: config/frozen.yaml --> neighbours with z > 0 supported it. The
prediction was the top reportable V2 term, and calibration, tiers and judging all attached to it. Ties in R1 were broken
by ascending GO identifier (a deviation; see below).

**Ranker choice.** The ranker was chosen once, by leave-one-out (LOO) on 3,000
<!-- src: results/verification/baseline_rows.md --> random scorable genes in neither U nor H (seed 0
<!-- src: results/verification/baseline_rows.md -->). Each query's own annotations were removed, and targets with
circular literature (below) were excluded, leaving 2,519 <!-- src: results/calibration/loo_ranker_choice.md --> genes.
The frozen rule took the highest mean reciprocal rank (MRR) of the first correct reportable term, treating differences
below 0.005 <!-- src: config/frozen.yaml --> as ties resolved to R3 and then R1. R1 was chosen and logged with the
calibration specification in LOOKS.md before H was opened. In a label-shuffle control, annotation rows were permuted among
genes of similar annotation count. On a synthetic 300-line × 2,000-gene <!-- src: docs/PIPELINE.md --> matrix with
planted modules, the full pipeline reached strong-module precision@1 of 1.00 <!-- src: docs/PIPELINE.md -->, removed every
proximity call by same-arm exclusion, and gave uniform null p-values (Kolmogorov–Smirnov p = 0.135
<!-- src: docs/PIPELINE.md -->).

## Temporal hold-out, comparators and statistics

**Hold-out set.** t0 was the GO release of 2018-07-02 <!-- src: results/holdout/holdout_sizing.md -->. H contained the
scorable genes that (i) satisfied D1 at t0, under the same function applied to the t0 files; (ii) had at most 10
<!-- src: results/holdout/holdout_sizing.md --> focused PMIDs below the July 2018 cut-off (PMID 29958442
<!-- src: results/holdout/holdout_sizing.md -->); and (iii) had at least one target. UniProt scores at t0 were
unavailable, so D2 was not used. The targets T(g) were the V2 terms propagated from current annotations minus those
propagated from t0 annotations, both in the current ontology, restricted to terms with 5–200
<!-- src: results/holdout/holdout_sizing.md --> annotated genes at t0. H had 820
<!-- src: results/holdout/holdout_sizing.md --> genes and 5,965 <!-- src: results/holdout/holdout_sizing.md -->
gene–target pairs (median 6 <!-- src: results/holdout/holdout_sizing.md --> per gene), and none of its genes was in U.
When H genes were scored, neighbour memberships, the background, the candidate terms and the prior frequencies all came
from t0. The network used 26Q3 data, so the test is temporal in annotation only. Current annotations are about 8
<!-- src: config/frozen.yaml --> years after t0. Because H includes only genes that gained at least one target, p_cal
is the probability of confirmation within roughly that horizon *conditional on the gene gaining experimental BP/MF
annotation*. DESIGN.md §3.7 and the first submitted version of this manuscript described it without this condition;
the conditional reading was introduced after the first round of review, without changing the model.

**Circularity.** Every supporting PMID was searched in Europe PMC, in full text where available, for DepMap and
co-essentiality terms. Of 1,050 <!-- src: results/holdout/circularity_summary.md --> PMIDs, 16
<!-- src: results/holdout/circularity_summary.md --> were flagged; they affected 106
<!-- src: results/holdout/circularity_summary.md --> pairs, and under the primary rule 11
<!-- src: results/holdout_eval/core.md --> genes lost all their targets (9 <!-- src: results/holdout/circularity_summary.md -->
under the fully-circular definition used in one sensitivity analysis). The known case, CCDC32 annotations citing Wainberg et al. [Wainberg2021], was flagged. The
primary analysis excluded flagged annotations from targets and ranked lists; sensitivity analyses varied the rule.

**Endpoint and comparators.** The endpoint was hit@1: the top reportable term is in T(g). The denominator was all primary
H genes, so a gene without a prediction counted as a miss. Every comparator used R1 and the same reportability rule.
Prior-only ranked terms by their t0 frequency. The matched-gene null was the mean, over g's first five matches, of
whether the match's top term was in T(g), skipping matches annotated to T(g). GLS was the same predictor on GLS scores;
it was the key secondary comparison, two-sided and reported by the size of the gene's smallest target.

The primary test was an intersection–union test [Berger1982; BergerHsu1996]: precision@1 of zavg_BEF had to exceed
**both** prior-only **and** the matched-gene null, each paired difference having a 95%
<!-- src: config/frozen.yaml --> cluster-bootstrap percentile confidence interval that excluded 0 [FieldWelsh2007], with no
multiplicity adjustment. BCa intervals [Efron1987] were also reported. Core secondary analyses included MRR, precision@1
on terms of at most 50 <!-- src: config/frozen.yaml --> genes, split-half networks, V1 with and without ETC complex I and
the mitoribosome, and covariate shift between H, U and LOO. A secondary batch (Pearson, homology, hu.MAP 3.0 module
transfer, t0 = 2019-07 <!-- src: config/frozen.yaml -->, K = 10 and 50 <!-- src: config/frozen.yaml -->, reweighting to
U, and others) was reported in full.

**Named controls.** The named controls were SPRING1, PEDS1, CCDC32, INTS15, HAPSTR1, SLC25A51, TEDC1, TEDC2, POU2AF2,
POU2AF3 and TMEM242, with FIRRM, AIRIM and TMEM41B as weaker controls. Nine
<!-- src: results/holdout/holdout_sizing.md --> were in H; the rest had no new term inside the 5–200
<!-- src: results/holdout/holdout_sizing.md --> window. All were reported as a case series, with the rank of the best
true term under a 2–300 <!-- src: config/frozen.yaml --> window, never pooled with the primary.

**Clusters and power.** Clusters were connected components linking H genes that share a supporting PMID or appear in
each other's N(g), fixed once for all comparisons. Confidence intervals came from a paired cluster bootstrap with 10,000
<!-- src: config/frozen.yaml --> replicates (seed 0 <!-- src: config/frozen.yaml -->). Because the largest component
exceeded 20% <!-- src: DEVIATIONS.md --> of H, the primary used PMID-only clusters under a fallback rule logged before H
was opened. With 709 <!-- src: results/holdout/holdout_sizing.md --> PMID-only clusters, the freeze-time effective n was
at least 539 <!-- src: results/holdout/holdout_sizing.md -->, and a simulation gave 80% power for differences of
0.04–0.06 <!-- src: results/holdout/power_sim.md --> in precision@1.

## Calibration

p_cal came from a logistic regression of hit@1 on H with five <!-- src: DESIGN.md --> covariates: top-K mean zavg_BEF
(coefficient ≥ 0), R(g) (≥ 0), neighbourhood annotation coverage (≥ 0), log top-term size (≤ 0) and module family
(unconstrained). Coverage and term size depend on the annotation release, so they entered as within-release percentile
ranks. Out-of-fold H predictions came from 10-fold <!-- src: config/frozen.yaml --> cluster cross-fitting over fold
seeds 0–4 <!-- src: config/frozen.yaml --> [Chernozhukov2018]. We report a reliability diagram (bins of at least 30
<!-- src: config/frozen.yaml --> genes), the Brier score [Brier1950], and the calibration intercept and slope with
confidence intervals [Cox1958; VanCalster2019]. U genes received p_cal from the model fitted on all of H.

p_cal was given only within support: every covariate within H's 5th–95th <!-- src: config/frozen.yaml --> percentiles
and the gene's family represented by at least 30 <!-- src: config/frozen.yaml --> H genes. A gene below support only on
zavg_BEF or R(g) received a boundary upper bound, untiered and summed separately; any other gene outside support received
no p_cal. The C3 headline was Σp_cal, with a percentile confidence interval from 2,000
<!-- src: config/frozen.yaml --> cluster-bootstrap refits. The pre-specified branches were: if the slope interval
excluded 1 or the intercept interval excluded 0, p_cal would be reported with a caveat and no recalibration; if the C2
primary test failed, U predictions would be reported uncalibrated. Neither branch was triggered.

## Hypothesis generation, artefacts and orthogonal evidence

**Ledger.** For every scorable U gene, the predictor was run with current annotations. A machine-written ledger recorded
the top 10 <!-- src: config/frozen.yaml --> partners with their zavg_BEF components, annotations, essentiality and
positions, paralogue and hub flags, and GLS ranks for the top 40 <!-- src: config/frozen.yaml -->. The ledger was written
before any narrative.

**Artefact flags.** Three flags applied to supporting partners: overlapping or adjacent loci (gene bodies within 1 kb
<!-- src: config/frozen.yaml -->, applied strand-agnostically), copy-number co-amplification (r > 0.3
<!-- src: config/frozen.yaml -->) and hub dominance (> 50% <!-- src: config/frozen.yaml --> of S from partners in the top
1% <!-- src: config/frozen.yaml --> of in-degree). If these flags affected half <!-- src: config/frozen.yaml --> or more of
the supporting partners, or the prediction was hub-driven, the gene could not be in Tier A. A top-40 gene was Tier B at
best if it failed lineage leave-out (refit without its most dependent lineage changes the top term), had a TP53-status
flag (Mann–Whitney comparison of TP53-mutant and wild-type lines, BH q < 0.05 <!-- src: DEVIATIONS.md -->
[Benjamini1995]), or failed DEMETER2
replication. Coupling between dependency and the gene's own expression (|ρ| > 0.3 <!-- src: config/frozen.yaml -->), or
transcription-factor enrichment among partners, set the relationship type to (e), programme. Otherwise the type was
assigned by script in a fixed order: (a) subunit, only with physical, co-abundance or structural support; (c)
supplier/client; (b) assembly factor; (d) pathway member, unresolved.

**Orthogonal classes**, all independent of DepMap, were P, physical (BioPlex, OpenCell, BioGRID low-throughput and STRING
experiments as one group; Human Cell Map SAINT separately); A, co-abundance (ProteomeHD; CCLE proteomics, flagged for
its shared lines); L, localisation; G, Perturb-seq with on-target knockdown of at least 30% <!-- src: DESIGN.md -->; and
S, AlphaFold2 pDockQ ≥ 0.23 <!-- src: DESIGN.md -->. Sources that embed DepMap or literature (hu.MAP 3.0, DEMETER2,
Predictomes, STRING text-mining) were never used as support [KimCY2022; Schmid2025]: hu.MAP 3.0 served as a secondary
comparator on H, DEMETER2 as a robustness check, and hu.MAP and Predictomes, after review, only for the novelty check.
HumanNet was not obtained or used.

**Admission.** Sources were admitted before any U prediction existed, on annotation data only (S3 Fig). Pair sources
needed a co-complex odds ratio with a lower 95% bound above 2 <!-- src: DESIGN.md --> on 2,538
<!-- src: results/orthogonal/admission.md --> complexes not derived from hu.MAP. Eleven of twelve
<!-- src: results/orthogonal/admission.md --> sources passed; the Olivieri screens failed (OR 1.87, 95% CI 1.58–2.26
<!-- src: results/orthogonal/admission.md -->), so G support came from Perturb-seq only. Localisation sources needed
agreement with GO cellular component on at least 200 <!-- src: DESIGN.md --> H genes, with a lower Wilson bound above 0.6
<!-- src: DESIGN.md -->. Only HPA passed (0.686, 95% CI 0.639–0.730 <!-- src: results/orthogonal/admission.md -->);
OpenCell, Human Cell Map and MitoCarta failed on coverage alone.

**Support test.** The test was applied to the top-40 candidates and every fill entrant (247 anchors), and to one
matched-gene and one decoy-term prediction per anchor. The called term's members were compared with 1,000
<!-- src: DESIGN.md --> degree-matched member sets, and p-values were combined by Simes within a class and Holm across
classes at α = 0.05 <!-- src: DESIGN.md --> [Simes1986; Holm1979; Aickin1996]. Each class was then called not measured, no support,
supports or contradicts. A missing interaction was never a contradiction; a contradiction needed incompatible
localisation from at least 2 <!-- src: DESIGN.md --> high-reliability sources. Each module family had a pre-specified
diagnostic class. The false-support rate is the fraction of matched and decoy predictions that met the Tier-A support
condition.

## Prioritisation

Tier A required that the gene be assessable and expressed, have p_cal ≥ 0.5 <!-- src: DESIGN.md --> within support, no
artefact exclusion, diagnostic-class support when that class was measured, and no contradiction. Tier B relaxed the
p_cal threshold to 0.3 <!-- src: DESIGN.md --> and/or dropped the diagnostic-support requirement. The top 40
<!-- src: DESIGN.md --> was filled from Tier A, then Tier B, then by p_cal; mitochondrial calls were capped at 6
<!-- src: DESIGN.md --> of the top 20 and 3 <!-- src: DESIGN.md --> reports, because mitochondrial signal dominates
DepMap [Rahman2021]. Thresholds were never relaxed. Because no gene reached Tier A or B, the primary top 40 was the 40
highest p_cal values among expressed, assessable, in-support genes after built-in exclusions and contradictions.

## Literature validation and blinded judging

**Recall probe.** Before any agent saw network output for these genes, a language model without tools stated what it
knew of each top-40, S20 and extra30 gene and of the 50 random U genes, from the symbol and aliases alone, and whether it
recognised the gene.

**Blind literature screen.** A separate agent, L, with no access to predictions or co-essentiality output, searched
Europe PMC (including full text and preprints) and UniProt for each candidate and for the 10 hold-out validation genes,
using the symbol, previous symbols, aliases and accession. It recorded structured evidence items
(claim, source, verbatim span, PMID, evidence level, and whether the evidence was DepMap-derived) and assigned N1–N3.

**Statements and decoys.** Each prediction became a script-written statement containing the V2 term and the V1′ module
label, with no partner names and no relationship type. Each real statement was shown with 3 <!-- src: DESIGN.md -->
decoys, which were other U genes' top terms matched on module family and term size, with member Jaccard < 0.1
<!-- src: DESIGN.md -->, in random slot order (scripts/51_judge_packets.py). Gene names, previous symbols, aliases and
protein names were redacted from L's evidence, and a leak check searched every packet for gene and partner names.

**Judging.** Two independent judges read the packets and scored each statement +1 (directly supported), 0 (not
addressed) or −1 (contradicted) <!-- src: DESIGN.md -->, using only the evidence provided; DepMap-derived support counted
as 0 <!-- src: DESIGN.md -->. The packet instruction credited a match to "the stated process or module, or a
closely equivalent one" <!-- src: scripts/51_judge_packets.py -->, for real and decoy statements alike; this
operationalisation of DESIGN §6.4 was logged in DEVIATIONS.md only after review, and a term-only re-reading of the
judges' justifications is reported beside the primary result (not re-judged blind). Agreement was reported as Cohen's κ
[Cohen1960], and a third judge adjudicated disagreements. Judges were first validated on 10 <!-- src: DESIGN.md --> H genes
with known true terms; validation required at least 7 of 10 <!-- src: DESIGN.md --> real statements supported and at most 3
of 30 <!-- src: DESIGN.md --> decoys. The primary test was an exact one-sided sign-flip test of real minus mean decoy
score over the top 40 (α = 0.05 <!-- src: DESIGN.md -->); S20 and extra30 were tested separately. Judges J1 and J2 were two instances of Claude Sonnet 5.5 and the
adjudicator was Claude Opus 5.5; the recall probe also ran on Claude Opus 5.5 (docs/AGENT_PROMPTS.md, which gives every
blinded-role prompt verbatim). Temperatures and seeds of model calls were not recorded.

## Candidate reports and red-team review

Eight to ten <!-- src: DESIGN.md --> genes received reports: the highest-ranked N2/N3 top-40 genes plus up to 2
<!-- src: DESIGN.md --> N1 rediscovery exemplars, fixed before judging results existed (results/m7/report_selection.md).
For each, a script (scripts/70_report_bundles.py) wrote a machine-generated evidence bundle: identifiers and knownness
criteria, strata, p_cal with its bootstrap interval, the top-10 partners with view-level scores, robustness checks, the
orthogonal evidence matrix with pair-level detail, protein features, the recall-probe answer and a rule-based selection
of dependent and control cell lines. A writer agent then completed a fixed template (reports/TEMPLATE_candidate.md and
TEMPLATE_experiments.md). The template required a plain-language bench summary; a relationship type; falsifying
observations written before the literature and orthogonal sections were read; an unblinded literature search; the
strongest alternative explanation; and a tiered experimental plan with a matched-essentiality control gene and a decision
rule fixed in advance. Every gene-function sentence had to cite an evidence-ledger row with a verbatim span; numbers were
copied from the ledger, not retyped, and the report says "not found in the literature as of" a date rather than
"novel". Overlap with published catalogues [Wainberg2021; Fischer2025; Replogle2022] was at first reported as agreement only;
after review it was quantified systematically (below) and each report gained a "prior prediction" statement.

Each report was then reviewed by an independent red-team agent (Claude Opus 5.5) that had not written it. The reviewer
re-resolved every cited PMID through the Europe PMC API, matched each quoted span against abstract or full text,
recomputed reported numbers from the project files, attacked the hypothesis and the experimental plan, and returned a
verdict with required fixes (reports/redteam/). The writer answered each fix point by point in the report's appendix.

## Post-review exploratory analyses

After the first round of peer review, the referees' requests were run by `scripts/90_revision_analyses.py` (helpers in
`scripts/revision_common.py`) into `results/revision/` (summary in `results/revision/SUMMARY.md`; figure S4 by
`scripts/62_figS4.py`). After the second round, `scripts/92_round2_numbers.py` derived a few further quantities from
U-side and judging files only (A10 below; no H outcome was read). None changes a frozen rule or a pre-specified result.
The analyses that read H outcomes (A3, A4, A7, A8 below) were logged in LOOKS.md; the row was committed together with
the results (b39691d), so the order rests on the agents' record, as for the primary look. All are labelled
[post-review exploratory] in Results.

**Revision history.** The first submitted version read p_cal unconditionally, attributed most of the published-but-uncurated
functions to slow curation, reported the candidate reports' overlap with published catalogues only as agreement, and
carried the full sensitivity analyses and the rediscovery table in the main Results. Round 1 introduced the conditional
reading of p_cal, the definition-artefact analysis (A1) and the catalogue check (A2). Round 2 corrected the
null-adjusted assessability to an excess over the null (A6, A10), restricted the attribution to complex membership to
the selected candidates, added the assumption behind every unconditional figure, and moved the detailed analyses to S1
Text without changing their numbers.

- **A1, entry routes and definition-artefact flags.** Each U gene was classed by entry route (D1 and D2, with or without
  D3; or D3 without D2) and flagged if it had UniProt annotation score 5, was a Complex Portal subunit [Meldal2022] or had
  at least one experimental GO cellular-component annotation (D1 evidence codes, current GAF). CORUM was not available.
  N1 rates were tabulated by route and flag for the random-50 audit and for the candidate sets, with Wilson intervals.
- **A2, novelty overlap.** For each top-40, S20 and report gene, we recorded whether at least one of its ten strongest
  zavg_BEF partners was a hu.MAP 3.0 co-complex member [Fischer2025], a Predictomes pair with SPOC ≥ 0.5 [Schmid2025], a
  significant GLS pair, a co-member of a Wainberg et al. module (any density, and density ≥ 0.5) or listed with an explicit
  function prediction in their Supplementary Data 3 [Wainberg2021], or a Kim et al. network edge or MCL cluster
  co-member [Kim2019]. Symbols of older catalogues were mapped through HGNC previous symbols and aliases. Pan et al.
  [Pan2018], FIREWORKS [Amici2021] and Perturb-seq cluster assignments [Replogle2022] were not obtainable in
  machine-readable form. Downloads and checksums are in `results/revision/external_manifest.tsv`.
- **A3, unconditional reading of p_cal.** Because a top term can be confirmed only if the gene gains annotation, the
  expected number of unconditional confirmations is exactly Σ p_i r_i, where r_i is gene i's probability of gaining new
  experimental BP/MF annotation over the horizon. Using one rate r assumes that (i) the gain rate does not vary with
  p_cal (shown false for signal: the highest quintile gains annotation about twice as often), (ii) the 2018 cohort's
  rate transfers to genes still uncharacterised in 2026 and (iii) p_cal itself transfers to U. The rate at which
  t0-eligible genes gained any target in the 5–200 window (overall, among genes with a reportable top term, and by
  quintile of top-K mean zavg_BEF) was multiplied into the saved bootstrap Σp_cal; intervals combine bootstrap draws
  with Jeffreys-Beta draws of the rate, assuming independence. The survivor-hazard version uses the hazard of 2018
  genes still uncharacterised in 2022 (0.145 over the horizon): 30.5 × 0.145 ≈ 4.4
  <!-- src: results/revision/a10_round2_numbers.tsv -->, beside 4.9 with the 2018-cohort rate; the unconditional
  Poisson-binomial SD is about 2.2 <!-- src: results/revision/numbers_a3.json -->. Annual hazards for a 2022 cohort and
  for the 2018 survivors check stationarity. Assumption (2) as worded in `results/revision/a3_pcal_conditional.md`
  ("independent of whether the top term is right") is superseded by (i)–(iii) here.
- **A4, calibration sensitivity.** Calibration-in-the-large, Brier skill and cluster-bootstrap intervals for the frozen
  model; the frozen model without signalling genes; and sign-constrained one- and two-covariate models (top-K mean
  zavg_BEF alone, plus coverage, plus term size) cross-fitted exactly as in §3.7 and applied to U with covariate support
  only.
- **A5, judging sensitivities.** Term-only scores (the three real statements supported on the module label alone set to
  0; no decoy was affected), an exact slot-permutation test, and a sign-flip test over clusters of genes sharing the real
  statement's V1′ label.
- **A6, null-adjusted assessability.** The clean-negative split-half false-call rate α in each stratum (any
  dependency, or profile-SD tertile) was applied to the N expressed scorable genes of that stratum and the expected
  false calls Nα subtracted from the observed assessable count (Jeffreys-Beta and binomial draws, 100,000, seed 0). If T
  genes carry real signal and are detected with power π, observed = Tπ + (N − T)α, so the difference is T(π − α): the
  excess of calls over the null expectation (named `implied_true` in `a6_assessability_null_adjusted.tsv`), not T. At
  full power T = (observed − Nα)/(1 − α) per stratum, a lower bound on T computed in A10. Both rest on the untested
  assumption that the rates transfer to expressed genes.
- **A7, combination rules on H.** Precision@1 for "homology if it predicts, else zavg_BEF", the reverse, and the oracle
  union, with paired cluster-bootstrap intervals and U-reweighting as in the secondary batch.
- **A8, named-control misses.** For each control, each new term in the t0 vocabulary was classed as circularity-flagged,
  outside the size window, not reportable (fewer than two supporting neighbours annotated at t0) or ranked.
- **A10, round-2 quantities** (`scripts/92_round2_numbers.py`; `results/revision/a10_round2_numbers.tsv` and
  `a10_assessability_excess_and_implied.tsv`). The A6 excess and the full-power lower bound with intervals from the same
  draw scheme; judged support among top-40 genes shared or not shared with the clean-first list; Wilson intervals for
  the N1 accuracy estimate; and the survivor-hazard rescaling in A3. No H outcome was read.

## Reproducibility and AI-agent safeguards

AI agents (Claude Opus 5.5 and Sonnet 5.5 <!-- src: PROMPT.md -->) ran the study under a fixed, human-written goal
(PROMPT.md). Before the freeze, the design went through two review rounds by independent agent reviewers covering prior
work, statistics, data and algorithms, AI-agent failure modes and experimental biology (reviews/). The safeguards were
as follows; where the record is incomplete, we say so.

- **Hash gate.** `gate.check()` verified the freeze file, which covers 10 <!-- src: reviews/audit_order_M4.md --> files,
  and the tag before any pairwise DepMap read. The freeze commit is afed1dd, and the SHA-256 of
  `preregistration/FREEZE.sha256` is 687075e680b8a051e6482de5bb052c903afaf2942ae5a25a34cef79e5965da04
  <!-- src: README.md -->. The repository has no remote, so git tags and commit times are self-reported until deposition.
- **Chronology audit.** `scripts/audit_order.py` was run at milestones M4 and M6 by the milestone analyst agents
  (reviews/audit_order_M4.md, reviews/audit_order_M6.md) and found no ordering violation. Its globs covered the
  prediction ledger from the first commit (the M6 audit ran before the ledger existed), but not the hold-out evaluation,
  the M7 judging or the post-review outputs. During revision the globs were extended to those three directories, and an
  independent agent that produced no results ran the audit on all four (reviews/audit_order_M9.md): no ordering
  violation, no pairwise output before the freeze tag, and the frozen files unchanged.
- **Hidden tool predictions.** The tool's genome-wide predictions were hidden by sparse checkout until the freeze.
- **One-look rule.** LOOKS.md allowed one primary look at H, after the ranker and calibration specification were
  committed. LOOKS.md also records an independent verification re-run of the primary analysis, one exploratory look
  (complementarity) and the post-review exploratory analyses. Only the specification row (commit fa21808) demonstrably
  preceded the primary look (aa381fc), by 31 minutes <!-- src: reviews/audit_order_M9.md -->; the rows for the primary look, the verification re-run, the
  exploratory look and the post-review analyses were each committed together with their results, so for those looks
  "row before run" rests on the agents' record (reviews/audit_order_M9.md).
- **Claim tracing.** Every number in this manuscript's source carries a comment naming its file. A claims table
  generated from these comments, for the main text and S1 Text (`CLAIMS.tsv`, by `scripts/91_claims_from_manuscript.py`),
  replaces the hand-written version, which held only six claims.
- **Agent scopes and prompts.** Blind roles (curation-lag auditor, literature agent L, recall probe, judges, adjudicator)
  were given read and write restrictions in their task prompts, which are reproduced verbatim in docs/AGENT_PROMPTS.md;
  `config/agent_scopes.yaml` is a template rather than an enforced policy, `results/agent_runs.tsv` logs only one agent
  run, and model temperatures and seeds were not recorded, so the agent-only steps are not reproducible in the strict
  sense and blinding can be audited only from the prompts, packet construction (scripts/50–51) and the leak check.
- **Independent re-derivation.** Agents that did not produce key numbers re-derived them (pre-registered list, hold-out
  set, primary hold-out evaluation).

Seeds are in config/seeds.yaml (0–4 <!-- src: config/frozen.yaml -->), and every design parameter is in
config/frozen.yaml, checked by script against DESIGN.md; several scripts hard-code seed 0 rather than reading the seed
file, and the tool's internal random-pair seed is fixed inside the tool. The environment is pinned in
config/requirements.lock.txt (numpy 2.5.4, pandas 3.1.0, scipy 1.18.1, scikit-learn 1.9.1
<!-- src: config/requirements.lock.txt -->); README.md documents the run order, which steps call the gate, runtimes and
the non-portable lines of the lock file. Large matrices are regenerated by script; summaries and per-gene results are
committed.

## Deviations from the frozen design

DESIGN.md was not edited after the tag. Twenty-two changes are logged in DEVIATIONS.md <!-- src: DEVIATIONS.md -->, and
affected results are reported under both rules where both exist. Most were logged before the results they affect were
computed, but four were not: the R1 tie-break (found by the independent verifier after the primary look), the
lineage-restricted expression rule behind the 646 versus 635 assessable count (found after the assessability output),
the pure-p_cal reading of the top-40 fill (decided after the ranked list existed, before any literature step) and the
module-label crediting in the judge instruction (logged retrospectively during manuscript review in commit acdad5a;
the row's date was first written as a later day and corrected in place in commit 090a7d8, so the commit, not the date,
records when it was logged). Row dates in
DEVIATIONS.md are not monotone, and the commits, not the dates, give the order. Thirteen rows fill operational details the
design left open (for example orthogonal admission mechanics, the RBO persistence of 0.9, LOO and hold-out evaluation
details, U scoring and bootstrap mechanics, artefact-flag operationalisation, the transcription-factor list, the fill
iteration, the R1 tie-break, which affects 401 of 820 <!-- src: DEVIATIONS.md --> H genes and whose reverse order
leaves the primary passing, and the judging instruction). Three were interpretations or implementation gaps: the
contradiction rule uses its four named localisation sources regardless of admission; the primary assessable count
applies the design's lineage-restricted expression rule (646 versus 635 <!-- src: results/assessability/summary.md -->);
and, under the low-yield branch, the top-40-only checks are tier caps, so the primary top 40 is pure p_cal order with the
implementing agent's "clean-first" list reported as a sensitivity analysis. Four were real changes or additions: the
PMID-only cluster fallback, set before H was opened after the LOO link graph put 2,491 of 2,519
<!-- src: results/calibration/loo_ranker_choice.md --> genes in one component; the secondary S20 list, defined before
any literature step; the extension of the recall probe to S20 and extra30; and a descriptive HPA tissue stratum that was
not computed because the data were not obtained. Two were errata with no rule change. Judged statements omitted the
relationship type to preserve blinding. DEVIATIONS promised results "under both rules" for the top-40 fill, but only the
pure-p_cal top 40 was judged; the clean-first list shares 20 genes with it
<!-- src: manuscript/figures/source_data/derived_numbers.tsv -->.
