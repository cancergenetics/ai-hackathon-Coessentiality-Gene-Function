# Methods

<!-- Draft 1 (scientific writer). Describes DESIGN.md v2.3 (frozen at tag design-frozen, commit afed1dd) plus every
DEVIATIONS.md entry to date. Tense: executed steps (pre-registration, matrices, verification, assessability, source
admission, LOO ranker choice) are in the past tense; steps not yet executed (hold-out evaluation, calibration,
U predictions, support tests, judging, reports) are given as the pre-specified protocol in the present tense and must
be harmonised after execution. No hold-out result is stated. Every number carries a src comment.
[refs_needed: X] marks a citation not yet in references/literature_refs.tsv (see manuscript/refs_needed.md). -->

## Data and versions

Table 1 lists the principal inputs. Every raw file was checksummed (SHA-256) and is verified by script before use.
Restricted-licence files were used internally and are not redistributed.

**Table 1. Principal data sources** (URLs, checksums and licences: DATA.md).

| Source | Version | Use |
|---|---|---|
| DepMap CRISPRGeneEffect (Chronos) [Dempster2021] | Public 26Q3 <!-- src: DATA.md -->; 1,361 lines × 18,434 genes <!-- src: results/assessability/splithalf_runs.md; results/verification/sanity_checks.md --> | co-essentiality |
| DepMap Model, CRISPRConfounders, expression, copy number, mutations | 26Q3 <!-- src: DATA.md --> | strata, split halves, artefact flags |
| DEMETER2 RNAi [McFarland2018] | v6 <!-- src: DATA.md --> | robustness only |
| HGNC [Seal2023] | 2026-04-23 <!-- src: DATA.md --> | universe, identifiers |
| GO ontology and human GAF [GO2023] | 2026-07-26 / 2026-05-21 <!-- src: DATA.md --> | D1, vocabularies, targets |
| Archived GO [GO_archive_web] | 2018-07-02 (t0), 2019-07-01 <!-- src: DATA.md --> | temporal hold-out |
| UniProtKB/Swiss-Prot [UniProt2025] | 2026_03 <!-- src: DATA.md --> | D2, identifiers |
| NCBI gene2pubmed [gene2pubmed_web] | 2026-10-29 <!-- src: DATA.md --> | D3, literature cut-off |
| TCRD development levels [Sheils2021] | 2023 <!-- src: DATA.md --> | D3 (Tdark) |
| Ensembl paralogues, coordinates | 116 <!-- src: DATA.md --> | exclusions, tandem stratum |
| Orthogonal: BioPlex 3.0 [Huttlin2021], OpenCell [Cho2022], BioGRID, STRING v12.5 <!-- src: DATA.md --> [Szklarczyk2025], Human Cell Map [Go2021], ProteomeHD [Kustatscher2019], CCLE proteomics [Nusinow2020], Perturb-seq [Replogle2022], Olivieri screens [Olivieri2020], AlphaFold2 pairs [Burke2023], HPA [Thul2017], MitoCarta3.0 [Rath2021], Complex Portal, hu.MAP 3.0 [Fischer2025] | DATA.md | support, admission |

Genes were identified by HGNC ID through a hub that joins Entrez (DepMap), UniProt and Ensembl identifiers; symbols
were never join keys. All 18,434 <!-- src: results/ids/hgnc_hub_qc.md --> DepMap columns mapped. A gene is **scorable** if it has a
DepMap column and at least one <!-- src: preregistration/CRITERIA.md --> UniProt accession mapped uniquely to it by the tool's rule.

## The co-essentiality method

We used zavg_BEF from the ai-hackathon-Coessentiality tool [Coessentiality_tool] at commit 3c684c9 <!-- src: DATA.md -->,
unmodified, through its public API and with its published configuration. In brief
(external/coessentiality/docs/explainer/METHOD.md), gene profiles are centred and standardised for covariance
estimation. The 20 <!-- src: results/matrices/zavg_full_manifest.json --> strongest cell-line covariance components are removed and the
rest are ridge-whitened (ridge 0.1 <!-- src: results/matrices/zavg_full_manifest.json --> × mean eigenvalue). The method then combines
three views:

- **F**, the cosine similarity of the cleaned profiles;
- **B**, the row-z-scored overlap of two genes' weighted partner lists, each list being the top 0.25% <!-- src: results/matrices/zavg_full_manifest.json -->
  of background genes (44 genes here <!-- src: results/assessability/splithalf_runs.md -->), with the pair itself excluded;
- **E**, the cosine similarity in a 512-dimensional <!-- src: results/matrices/zavg_full_manifest.json --> Laplacian eigenmap of the
  partner graph.

Each view is z-scored against 200,000 <!-- src: results/matrices/zavg_full_manifest.json --> fixed random pairs, and the three z-scores
are averaged. Background genes have less than 10% <!-- src: results/matrices/zavg_full_manifest.json --> missing values
(17,525 genes <!-- src: results/verification/sanity_checks.md -->). The tool's settings were tuned on hu.MAP 3.0 co-complex pairs
[Fischer2025; Coessentiality_tool]. We tuned nothing.

**Verification.** We computed one full zavg_BEF matrix, and GLS [Wainberg2021] and Pearson rows for the genes that
need them. Our GLS and Pearson values matched the tool's on 100,993 <!-- src: results/verification/baseline_rows.md --> random pairs
(maximum absolute difference 2.96 × 10⁻⁷ <!-- src: results/verification/baseline_rows.md -->). With the tool's own CLI we reproduced its
published internal-test average precision: 0.3451, 0.2423, 0.1463 and 0.1341 for zavg_BEF, GLS, Spearman and Pearson,
against 0.345, 0.242, 0.146 and 0.134 <!-- src: results/verification/tool_reproduction.md --> published (tolerance ±0.005 <!-- src: results/verification/tool_reproduction.md -->).
All 14 <!-- src: results/verification/sanity_checks.md --> pre-specified sanity checks passed. They covered Chronos sign, matrix
symmetry, median within-complex scores above 3 <!-- src: results/verification/sanity_checks.md --> for seven <!-- src: results/verification/sanity_checks.md -->
reference complexes, and a near-zero mean over random pairs.

## Pre-registration of uncharacterised genes

The universe was the 19,296 <!-- src: preregistration/CRITERIA.md --> HGNC Approved protein-coding genes. A single function
(`src/knownness.py::d1`) applied the criteria to every GO release:

- **D1**: no informative GO biological-process or molecular-function annotation with evidence EXP, IDA, IPI, IMP,
  IGI, IEP, TAS or IC [GO_evidence_web].
  - NOT-qualified rows are removed and `contributes_to` rows count.
  - High-throughput, electronic, similarity-based, phylogenetic, RCA, NAS and ND codes are ignored, as are
    cellular-component annotations.
  - The 22 <!-- src: preregistration/CRITERIA.md --> generic terms listed in CRITERIA.md do not count. Examples are "protein
    binding", the roots and high-level grouping terms.
- **D2**: UniProt annotation score ≤ 2 <!-- src: preregistration/CRITERIA.md --> [UniProtHelp_AnnotationScore]. This is the
  definition of Wainberg et al. [Wainberg2021].
- **D3**: at most 10 <!-- src: preregistration/CRITERIA.md --> PubMed records among those linking at most 10 <!-- src: preregistration/CRITERIA.md -->
  human genes, **or** IDG Tdark [Oprea2018; Sheils2021].

The pre-registered set is **U = D1 ∩ (D2 ∪ D3)**, and no gene is ever removed from it. U contains 4,924 <!-- src: preregistration/CRITERIA.md -->
genes, of which 4,275 <!-- src: preregistration/CRITERIA.md --> are in DepMap and 4,271 <!-- src: preregistration/CRITERIA.md --> are
scorable. Genes outside U serve only for calibration; no function is proposed for them.

Reporting strata (preregistration/CRITERIA.md) were:

- **Family**: chemosensory/epidermal, from named HGNC groups; tandem cluster, with at least 2 <!-- src: preregistration/CRITERIA.md -->
  Ensembl paralogues within 1 Mb <!-- src: preregistration/CRITERIA.md -->; or other.
- **Expressed**: log2(TPM+1) ≥ 1 <!-- src: preregistration/CRITERIA.md --> in at least 10% <!-- src: preregistration/CRITERIA.md -->
  of DepMap models. Genes expressed in at least 50% <!-- src: DESIGN.md --> of the lines of any lineage with at least 10 <!-- src: DESIGN.md -->
  lines also count as expressed.
- **Clean negatives**: log2(TPM+1) < 0.5 <!-- src: DESIGN.md --> in at least 95% <!-- src: DESIGN.md --> of lines.
- **Profile informativeness** (SD tertile, any-dependency) and **low_coverage** (outside the tool background).
- **Headline stratum**: expressed, non-chemosensory, non-tandem genes.

U was built from annotation data alone; before the freeze, DepMap was read only for its header and single-gene
summaries (preregistration/PROVENANCE.md). An independent agent,
without access to our code, re-derived U and the hold-out set from the raw files and reproduced both exactly
(verify/prereg_verification.md). The list, criteria, design, configuration, seeds, gate code, tool commit and DepMap
file hashes were frozen in `preregistration/FREEZE.sha256` at commit afed1dd, under the tags `preregistration-v1` and
`design-frozen`.

To measure curation lag, an auditor agent with no access to co-essentiality output reviewed a random sample of 50 <!-- src: DESIGN.md -->
U genes (seed 0 <!-- src: config/frozen.yaml -->). It searched symbols, previous symbols, aliases, UniProt and Europe PMC including
preprints, and classed each gene N1 (function established), N2 (partial) or N3 (none).

## Assessability

Cell lines
were split into halves stratified by lineage × screen-library combination (30 lineages <!-- src: results/assessability/splithalf_runs.md -->),
keeping lines from the same patient together. This was done for seeds 0–4 <!-- src: config/frozen.yaml -->, and the tool was refitted on
each half (10 fits <!-- src: results/assessability/splithalf_runs.md -->). Half-neighbour lists N_A^s(g) and N_B^s(g) are the top 25 <!-- src: DESIGN.md -->
genes, after the predictor's exclusions, among genes in the background of both halves and of the full data.

The reproducibility statistic is R(g) = mean_s |N_A^s(g) ∩ N_B^s(g)|/K. Its null analogue is
R0(g, m) = mean_s |N_A^s(g) ∩ N_B^s(m)|/K over the first 200 <!-- src: DESIGN.md --> matched genes m, that is genes with a similar
profile but no shared function. A gene is **assessable** if p = (1 + #{m : R0 ≥ R})/201 <!-- src: DESIGN.md --> is below 0.05 <!-- src: DESIGN.md -->
**and** the gene is expressed. Non-expressed genes are scored anyway: calls on clean negatives estimate a false-call
rate. In a sensitivity analysis, rank-biased overlap [refs_needed: Webber 2010] with persistence 0.9 <!-- src: DEVIATIONS.md -->
replaces set overlap. R(g) is computed identically for every gene and is also a calibration covariate.

## Function predictor and vocabularies

**Vocabularies.** The primary vocabulary, V2, is GO biological process plus molecular function. Membership comes from
D1-evidence, non-NOT annotations propagated over is_a and part_of at the release in use. Candidate terms have
5–200 <!-- src: config/frozen.yaml --> annotated scorable genes. Two descriptive module labels supplement it: V1, GO complexes under
GO:0032991, and V1′, V1 plus Complex Portal and MitoCarta3.0 pathways. Each term belongs to one of eight <!-- src: config/term_families.tsv -->
module families through a fixed, ordered list of GO ancestors (config/term_families.tsv). When g is scored, IPI rows
whose with/from field names g are removed from its neighbours' memberships.

**Neighbourhood and scores.** N(g) is the top K = 25 <!-- src: config/frozen.yaml --> background genes by zavg_BEF. It excludes g,
genes on g's chromosome arm (43 arms <!-- src: results/verification/matched_lists.md -->) and Ensembl paralogues of g, which removes
Cas9 proximity artefacts [Lazar2024] and paralogue effects. For each term t, S(g, t) = Σ max(z_gj, 0) over the
neighbours j ∈ N(g) annotated to t. Three rankers were pre-specified:

- R1, raw S;
- R2, the hypergeometric p of the neighbour count, with the annotated scorable genes as background;
- R3, an empirical p against matched genes:
  p_emp = (1 + #{m ∈ M(g) \ A_t : S(m, t) ≥ S(g, t)})/(1 + |M(g) \ A_t|), where A_t are the genes annotated to t.

**Matched genes.** M(g) holds the 500 <!-- src: config/frozen.yaml --> scorable genes nearest to g in Mahalanobis distance on mean
effect, log SD and missing fraction [refs_needed: matching]. Background status is matched exactly. M(g) excludes g,
N(g), same-arm genes and paralogues. The caliper is 0.2 <!-- src: config/frozen.yaml -->, with nearest-available fallback (seed 0 <!-- src: config/frozen.yaml -->).
Among the first five matches, 2.9% <!-- src: results/verification/matched_lists.md --> fell outside the caliper, and the standardised
mean differences over all scorable genes were at most 0.002 <!-- src: results/verification/matched_lists.md --> in absolute value. The
first five <!-- src: config/frozen.yaml --> matches serve as the null comparator, the first 200 <!-- src: config/frozen.yaml --> as the assessability null, and all 500 <!-- src: config/frozen.yaml --> as the R3
reference.

**Output.** A term is reportable if at least 2 <!-- src: config/frozen.yaml --> neighbours with z > 0 support it. The prediction is the
top reportable V2 term, and calibration, tiers and judging all attach to it.

**Ranker choice.** The ranker was chosen once, by leave-one-out (LOO) on 3,000 <!-- src: results/verification/baseline_rows.md --> random
scorable genes in neither U nor H (seed 0 <!-- src: results/verification/baseline_rows.md -->). Each query's own annotations were removed,
and targets with circular literature (below) were excluded, leaving 2,519 <!-- src: results/calibration/loo_ranker_choice.md --> genes. The
frozen rule takes the highest mean reciprocal rank (MRR) of the first correct reportable term. Differences below 0.005 <!-- src: config/frozen.yaml -->
are ties, resolved to R3 and then R1. R1 was chosen (MRR 0.169 vs 0.140 for R2 and 0.111 for R3 <!-- src: results/calibration/loo_ranker_choice.md -->),
and every circularity variant gave the same choice. The choice was logged with the calibration specification in
LOOKS.md before H was opened.

In a label-shuffle control, annotation rows were permuted among genes of similar annotation count. R1 precision@1 fell
from 0.139 to 0.015 <!-- src: results/calibration/label_shuffle.md -->, below the prior-only level of 0.036 <!-- src: results/calibration/label_shuffle.md -->.

On a synthetic 300-line × 2,000-gene <!-- src: docs/PIPELINE.md --> matrix with planted modules, the full pipeline reached
strong-module precision@1 of 1.00 <!-- src: docs/PIPELINE.md -->, removed every proximity call by same-arm exclusion, and gave
uniform null p-values (KS p = 0.135 <!-- src: docs/PIPELINE.md -->).

## Temporal hold-out, comparators and statistics

**Hold-out set.** t0 is the GO release of 2018-07-02 <!-- src: results/holdout/holdout_sizing.md -->. H contains the scorable genes that
meet three conditions:

1. they satisfied D1 at t0, under the same function applied to the t0 files;
2. they had at most 10 <!-- src: results/holdout/holdout_sizing.md --> focused PMIDs below the July 2018 cut-off (PMID 29958442 <!-- src: results/holdout/holdout_sizing.md -->);
3. they have at least one target.

UniProt scores at t0 were unavailable, so D2 is not used. The targets T(g) are the V2 terms propagated from current
annotations minus those propagated from t0 annotations, both in the current ontology. They are restricted to terms
with 5–200 <!-- src: results/holdout/holdout_sizing.md --> annotated genes at t0. H has 820 <!-- src: results/holdout/holdout_sizing.md --> genes and
5,965 <!-- src: results/holdout/holdout_sizing.md --> gene–target pairs (median 6 <!-- src: results/holdout/holdout_sizing.md --> per gene), and none
of its genes is in U.

When H genes are scored, neighbour memberships, the background, the candidate terms and the prior frequencies all come
from t0. The network uses 26Q3 data, so the test is temporal in annotation only. Current annotations are about 8 <!-- src: config/frozen.yaml -->
years after t0, so p_cal is the probability of confirmation within roughly that horizon.

**Circularity.** Every supporting PMID was searched in Europe PMC, in full text where available, for DepMap and
co-essentiality terms. Of 1,050 <!-- src: results/holdout/circularity_summary.md --> PMIDs, 16 <!-- src: results/holdout/circularity_summary.md --> were
flagged. They affect 106 <!-- src: results/holdout/circularity_summary.md --> pairs, and 9 <!-- src: results/holdout/circularity_summary.md --> genes lose
all their targets. The known case, CCDC32 annotations citing Wainberg et al. [Wainberg2021], was flagged. The primary
analysis excludes flagged annotations; a sensitivity analysis also excludes unscannable ones.

**Endpoint and comparators.** The endpoint is hit@1: the top reportable term is in T(g). The denominator is all H
genes, so a gene without a prediction counts as a miss, and coverage is reported. Every comparator uses R1 and the
same reportability rule:

- **Prior-only** ranks terms by their t0 frequency.
- **Matched-gene null** is the mean, over g's first five matches, of whether the match's top term is in T(g). Matches
  annotated to T(g) are skipped.
- **GLS** is the same predictor on GLS scores. It is the key secondary comparison: two-sided and reported by
  neighbourhood-size stratum.

The primary test is an intersection–union test [refs_needed: Berger 1982]. Precision@1 of zavg_BEF must exceed **both**
prior-only **and** the matched-gene null, each paired difference having a 95% <!-- src: config/frozen.yaml --> cluster-bootstrap percentile
CI that excludes 0 [refs_needed: bootstrap]. BCa intervals are also reported.

Core secondary analyses include MRR, precision@1 on terms of at most 50 <!-- src: config/frozen.yaml --> genes, split-half
networks, V1 with and without ETC complex I and the mitoribosome, and covariate shift between H, U and LOO.

A secondary batch (Pearson, homology, hu.MAP 3.0 module transfer, t0 = 2019-07 <!-- src: config/frozen.yaml -->, K = 10 and 50 <!-- src: config/frozen.yaml -->,
reweighting to U, and others in DESIGN §3.3) is reported all or none.

**Named controls.** The named controls are SPRING1, PEDS1, CCDC32, INTS15, HAPSTR1, SLC25A51, TEDC1, TEDC2, POU2AF2,
POU2AF3 and TMEM242, with FIRRM, AIRIM and TMEM41B as weaker controls. Nine <!-- src: results/holdout/holdout_sizing.md --> are in H; the
rest have no new term inside the 5–200 <!-- src: results/holdout/holdout_sizing.md --> window. All are reported as a case series, with the rank of the best true term
under a 2–300 <!-- src: config/frozen.yaml --> window. The case series is never pooled with the primary.

**Clusters and power.** Clusters are connected components that link H genes sharing a supporting PMID or appearing in
each other's N(g). They are fixed once for all comparisons. CIs come from a paired cluster bootstrap with 10,000 <!-- src: config/frozen.yaml -->
replicates (seed 0 <!-- src: config/frozen.yaml -->). If the largest component exceeds 20% <!-- src: DEVIATIONS.md --> of H, the primary uses
PMID-only clusters (Deviations). If the effective n is below 300 <!-- src: config/frozen.yaml -->, the primary is labelled underpowered.
With 709 <!-- src: results/holdout/holdout_sizing.md --> PMID-only clusters, the effective n is at least 539 <!-- src: results/holdout/holdout_sizing.md -->.
A freeze-time simulation gave 80% power for differences of 0.04–0.06 <!-- src: results/holdout/power_sim.md --> in precision@1.

## Calibration

p_cal comes from a logistic regression of hit@1 on H with five <!-- src: DESIGN.md --> covariates:

- top-K mean zavg_BEF (coefficient ≥ 0);
- R(g) (≥ 0);
- neighbourhood annotation coverage (≥ 0);
- log top-term size (≤ 0);
- module family (unconstrained).

Coverage and term size depend on the annotation release, so they enter as within-release percentile ranks. Out-of-fold
H predictions come from 10-fold <!-- src: config/frozen.yaml --> cluster cross-fitting over fold seeds 0–4 <!-- src: config/frozen.yaml -->.
We report a reliability diagram (bins of at least 30 <!-- src: config/frozen.yaml --> genes), the Brier score [refs_needed: Brier],
and the calibration intercept and slope with CIs [refs_needed: calibration]. U genes get p_cal from the model fitted on
all of H.

p_cal is given only within support, meaning that every covariate lies within H's 5th–95th <!-- src: config/frozen.yaml --> percentiles
and the gene's family has at least 30 <!-- src: config/frozen.yaml --> H genes. A gene below support only on zavg_BEF or R(g) gets a
boundary upper bound, which is untiered and summed separately. Any other gene outside support gets no p_cal.

The C3 headline is Σ p_cal, with a percentile CI from 2,000 <!-- src: config/frozen.yaml --> cluster-bootstrap refits. If the slope CI
excludes 1 or the intercept CI excludes 0, p_cal is still reported, with a caveat and no recalibration. If the C2
primary test fails, U predictions are reported uncalibrated.

## Hypothesis generation, artefacts and orthogonal evidence

**Ledger.** For every scorable U gene, the predictor runs with current annotations. A machine-written ledger records
the top 10 <!-- src: config/frozen.yaml --> partners with zavg_BEF components, their annotations, essentiality and positions, paralogue
and hub flags, and GLS ranks for the top 40 <!-- src: config/frozen.yaml -->. The ledger is written before any narrative.

**Artefact flags.** Three flags apply to supporting partners:

- bidirectional or overlapping loci (TSS < 1 kb <!-- src: config/frozen.yaml -->);
- copy-number co-amplification (r > 0.3 <!-- src: config/frozen.yaml -->);
- hub dominance (> 50% <!-- src: config/frozen.yaml --> of S from partners in the top 1% <!-- src: config/frozen.yaml --> of in-degree).

If any of these flags affects half <!-- src: config/frozen.yaml --> or more of the supporting partners, the gene cannot be in Tier A. A top-40 gene is
Tier B at best if it fails lineage leave-out, has a TP53-status flag, or fails DEMETER2 replication. Coupling between
dependency and the gene's own expression (|ρ| > 0.3 <!-- src: config/frozen.yaml -->), or transcription-factor enrichment among partners,
sets the relationship type to (e), programme. Otherwise the type is assigned by script in a fixed order:

- (a) subunit, only with physical, co-abundance or structural support;
- (c) supplier/client;
- (b) assembly factor;
- (d) pathway member, unresolved.

**Orthogonal classes** are independent of DepMap:

- P, physical: BioPlex, OpenCell, BioGRID low-throughput and STRING experiments, counted as one group; Human Cell Map
  SAINT, counted separately;
- A, co-abundance: ProteomeHD; CCLE proteomics, flagged for its shared lines;
- L, localisation;
- G, Perturb-seq with on-target knockdown of at least 30% <!-- src: DESIGN.md -->;
- S, AlphaFold2 pDockQ ≥ 0.23 <!-- src: DESIGN.md -->.

Sources that embed DepMap or literature (hu.MAP 3.0, DEMETER2, Predictomes, HumanNet, STRING text-mining) are
reported only [KimCY2022; Schmid2025].

**Admission.** Sources were admitted before any U prediction existed, on annotation data only. Pair sources needed a
co-complex odds ratio with a lower 95% bound above 2 <!-- src: DESIGN.md --> on 2,538 <!-- src: results/orthogonal/admission.md --> complexes
that are not derived from hu.MAP. Eleven of twelve <!-- src: results/orthogonal/admission.md --> sources passed. The Olivieri screens
failed (OR 1.87, 95% CI 1.58–2.26 <!-- src: results/orthogonal/admission.md -->), so G support is from Perturb-seq only.

Localisation sources needed agreement with GO cellular component on at least 200 <!-- src: DESIGN.md --> H genes, with a lower Wilson
bound above 0.6 <!-- src: DESIGN.md --> [refs_needed: Wilson]. Only HPA passed (0.686, 95% CI 0.639–0.730 <!-- src: results/orthogonal/admission.md -->).
OpenCell, Human Cell Map and MitoCarta failed on coverage alone.

**Support test.** The test applies to genes with p_cal ≥ 0.3 <!-- src: DESIGN.md -->, to the top 40, and to equal-size matched-gene
and decoy sets. The called term's members are compared with 1,000 <!-- src: DESIGN.md --> degree-matched member sets. p-values are
combined by Simes within a class and Holm across classes at α = 0.05 <!-- src: DESIGN.md --> [refs_needed: Simes; Holm]. Each class is
then called not measured, no support, supports or contradicts. A missing interaction is never a contradiction; a
contradiction needs incompatible localisation from at least 2 <!-- src: DESIGN.md --> high-reliability sources. Each module family has
a pre-specified diagnostic class, for example L or A for mitochondrial terms. The false-support rate on matched and
decoy sets is reported.

## Prioritisation, literature validation and blinded judging

**Tiers.** Tier A requires all of the following:

- the gene is assessable and expressed;
- p_cal ≥ 0.5 <!-- src: DESIGN.md --> within support;
- no artefact exclusion;
- diagnostic-class support when that class is measured;
- no contradiction.

Tier B relaxes the p_cal threshold to 0.3 <!-- src: DESIGN.md --> and/or drops the diagnostic-support requirement. The top 40 <!-- src: DESIGN.md -->
are filled from Tier A, then Tier B, then by p_cal. Because mitochondrial signal dominates DepMap [Rahman2021],
mitochondrial calls are capped at 6 <!-- src: DESIGN.md --> of the top 20 and 3 <!-- src: DESIGN.md --> reports. Thresholds are never relaxed.

**Recall probe and novelty.** Before any agent sees network output for these genes, a tool-less agent states what it
knows of each top-40 gene and of the 50 <!-- src: DESIGN.md --> random U genes. A separate agent, L, has no access to predictions.
It records structured evidence items (claim, source, verbatim span, PMID, evidence level, DepMap-derived or not) and
assigns N1–N3.

**Blinded judging.** Each prediction becomes a script-written statement (V2 term, V1′ label, relationship type; no
partner names). It is shown with 3 <!-- src: DESIGN.md --> decoys, which are other U genes' predictions matched on family and term size
with member Jaccard < 0.1 <!-- src: DESIGN.md -->. Two independent judges read L's evidence, with gene names redacted, and score each
statement +1, 0 or −1 <!-- src: DESIGN.md -->. DepMap-derived support counts as 0 <!-- src: DESIGN.md -->. Agreement is reported as Cohen's κ [refs_needed: Cohen],
and a third judge adjudicates. The primary test is an exact one-sided sign-flip test of real minus mean decoy score
(α = 0.05 <!-- src: DESIGN.md -->).

Judges are first validated on 10 <!-- src: DESIGN.md --> H genes with known true terms. Validation passes if at least 7 of 10 <!-- src: DESIGN.md -->
real statements are supported and at most 3 of 30 <!-- src: DESIGN.md --> decoys are.

**Reports.** Eight to ten <!-- src: DESIGN.md --> genes receive reports: the highest-ranked N2/N3 genes plus up to 2 <!-- src: DESIGN.md --> N1
rediscovery exemplars. Each gives the claim, expected hit probability, strongest alternative and a decisive experiment
with an essentiality-matched control gene, and is red-teamed by an independent agent. Overlap with published
catalogues [Wainberg2021; Fischer2025; Replogle2022] is reported as agreement only.

## Reproducibility and AI-agent safeguards

AI agents (Claude Opus 5.5 and Sonnet 5.5 <!-- src: PROMPT.md -->) ran the study under a fixed, human-written goal (PROMPT.md). Before
the freeze, the design went through two review rounds by independent agent reviewers (reviews/). The safeguards were:

- **Hash gate.** `gate.check()` verifies the freeze file, which covers 10 <!-- src: reviews/audit_order_M4.md --> files, and the tag
  before any pairwise DepMap read.
- **Chronology audit.** Fresh agents run `scripts/audit_order.py` at milestones; the M4 audit found no ordering
  violation (reviews/audit_order_M4.md).
- **Hidden tool predictions.** The tool's genome-wide predictions were hidden by sparse checkout until the freeze.
- **One-look rule.** LOOKS.md allows one look at H.
- **Claim tracing.** CLAIMS.tsv maps each manuscript number to a result file.
- **Agent scopes.** config/agent_scopes.yaml restricts each role's reads and writes. Blind roles run in directories
  that hold only identifiers. results/agent_runs.tsv logs role, model and input hashes. Agents never commit.
- **Independent re-derivation.** Agents that did not produce key numbers re-derive them.

Seeds are in config/seeds.yaml (0–4 <!-- src: config/frozen.yaml -->), and every design parameter is in config/frozen.yaml, which is
checked by script against DESIGN.md. The environment is pinned in config/requirements.lock.txt (numpy 2.5.4, pandas
3.1.0, scipy 1.18.1, scikit-learn 1.9.1 <!-- src: config/requirements.lock.txt -->). Matrices are regenerated by script; summaries are
committed.

## Deviations from the frozen design

DESIGN.md was not edited after the tag. All changes were logged in DEVIATIONS.md before the results they affect were
computed, and affected results are reported under both rules.

1. **Contradiction rule.** The rule uses its four <!-- src: DEVIATIONS.md --> named localisation sources regardless of admission; L-class
   support uses only admitted sources. Otherwise the rule could never fire.
2. **Admission details.** These were set before any prediction existed: 1,000 <!-- src: DEVIATIONS.md --> bootstrap replicates,
   complexes of 2–300 <!-- src: DEVIATIONS.md --> members, direct GO membership, and continuous edges at a mean row percentile
   ≥ 0.95 <!-- src: DEVIATIONS.md -->.
3. **Expressed definition.** The primary count applies the lineage-restricted rule of the DESIGN text, which the
   frozen table predates: 646 vs 635 <!-- src: results/assessability/summary.md --> assessable genes, both reported.
4. **RBO persistence** was set to 0.9 <!-- src: DEVIATIONS.md -->.
5. **HPA tissue stratum.** This descriptive stratum was not computed because the data were not obtained.
6. **Cluster fallback.** This was set before H was opened, after the LOO link graph put 2,491 of 2,519 <!-- src: results/calibration/loo_ranker_choice.md -->
   genes in one component.
7. **LOO details.** Flagged targets were removed from both target sets and ranked lists; the 5–200 <!-- src: DEVIATIONS.md --> window was applied after
   the query's annotations were removed; CIs are gene-level.

<!-- Note to PI: DEVIATIONS.md (2026-10-30, §3.5) quotes "2,484/2,519 ... PMID + N(g) linking"; loo_ranker_choice.md
gives 2,491 for N(g)+PMID and 2,484 for N(g) only. The draft uses the loo_ranker_choice.md figure; DEVIATIONS.md may
need a correction row. -->
