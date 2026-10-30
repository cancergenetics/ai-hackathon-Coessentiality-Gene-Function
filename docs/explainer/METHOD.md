# The method: predicting functions of uncharacterised genes from co-essentiality, with honest confidence

**In one sentence:** to propose functions for human genes that databases call "uncharacterised", the method takes a
gene list frozen in advance plus DepMap CRISPR knockout screens, and returns for each gene one predicted Gene Ontology
(GO) function, a calibrated probability that curators will later confirm it, and labels that say when not to trust it.

**In three sentences:** each gene's 25 strongest co-essential partners (genes whose knockout hurts the same cancer cell
lines) are found with a published scoring tool, the GO term carried by the most strongly linked partners becomes the
prediction, and genes whose partner list does not reproduce in two halves of the cell lines are flagged and kept off
the shortlist (a prediction is still written for them). How
much to trust a prediction is learned from the future, not the past: a calibration model is fitted on 809 genes that
were uncharacterised in 2018 and gained experimental annotations afterwards, after removing annotations from papers
that themselves used DepMap. The top predictions are then checked against independent interaction and localisation data,
and against the literature by blinded judges who also see three decoy statements per gene.

> **Key numbers (honest version)**
>
> | Measure | Value |
> |---|---|
> | Genes pre-registered as uncharacterised | **4,924** of 19,296 (4,271 measurable in DepMap) |
> | Genes with a usable, reproducible signal | **646** pass the rule (13%); allowing for false passes, at least **~322** (6.5%) carry real signal *[post-review estimate, untested assumption]* |
> | Accuracy on genes annotated after 2018 (top term right) | **3.0%** (95% CI 1.8–4.3%), vs 0.5% for matched genes; no better than the older GLS score (2.3%) and far below homology (**21.8%**) |
> | Highest calibrated probability for any gene | **0.141**, so no gene reached the pre-set confidence tiers (0.3, 0.5) |
> | Expected confirmed predictions | **~4.9** (2.2–8.1) over 2,583 calibrated genes; 30.5 if every gene were later annotated *[post-review]*. About 82% of this comes from genes that fail the usable-signal rule: over the 269 assessable genes it is **~0.9** (5.5 if every gene were annotated) *[derived for this explainer, not in the manuscript]* |
> | Blinded literature check of the top 40 | **18/40** supported vs 3/120 decoys (p = 0.0002); 16/40 on the GO term alone |
> | Novelty of the top 40 | **31/40** already had a published function; 34/40 had a link in earlier catalogues *[post-review]* |
>
> *This project, including this page, was produced by AI agents and has not been verified by a human.*

## Contents

- [How it differs from the standard approach](#differs)
- [The pipeline at a glance](#pipeline)
- [The seven steps](#steps)
- [Worked example: ANKRD52, plus the TMEM242 hold-out control](#worked-example)
- [Pseudocode and where each step lives in the code](#code)
- [Results and how strong the evidence is](#results)
- [Limitations, assumptions and when not to use it](#limitations)
- [Glossary](#glossary)

<a id="differs"></a>
## How it differs from the standard approach

**The standard approach** to predicting function from CRISPR screens is *guilt by association*. Score every pair of
genes by how similar their knockout profiles are across cell lines (a plain correlation, or GLS, a correlation after
correcting for related cell lines; Wainberg 2021, doi:10.1038/s41588-021-00840-z). Then give an uncharacterised gene the
function that is over-represented among its top partners. Accuracy is usually measured by *leave-one-out*: hide a
well-studied gene's annotations, predict them from its neighbours, and count hits. Success is often illustrated with a
few genes whose function was first proposed from co-essentiality and later confirmed.

**This method keeps the guilt-by-association core and changes what surrounds it.**

| | Standard approach | This method | Why it matters here (evidence) |
|---|---|---|---|
| Which genes | Chosen during analysis | Frozen list, defined from annotation databases before any gene–gene score ([Step 1](#step-1)) | Results cannot be tuned to the gene list; the list is checkable by hash |
| Pair score | Correlation or GLS | The published zavg_BEF tool, used unchanged ([Step 2](#step-2)) | Required by the brief. On function prediction it tied GLS (+0.006, CI −0.005 to +0.017) |
| When to abstain | Rarely | Every gene gets a top term, but genes whose partner list does not reproduce in split halves, or that are not expressed, are flagged and kept off the shortlist ([Step 3](#step-3)) | 0% accuracy in the two weakest fifths of hold-out genes by partner strength (the gate itself was not tested on the hold-out) |
| Artefacts | Often ignored | Same-chromosome-arm genes and paralogues removed from partner lists ([Step 4](#step-4)) | Removes CRISPR-cutting and copy-number look-alikes (Lazar 2024); shown on synthetic data, no measurable effect on the hold-out (3.3% without vs 3.0% with) |
| How accuracy is measured | Leave-one-out on known genes | Genes uncharacterised in 2018 and annotated since, with DepMap-citing annotations removed ([Step 5](#step-5)) | Leave-one-out gave 13.9% top-term accuracy; the 2018 hold-out gave 3.0% |
| Confidence | A rank or a p-value | A calibrated probability, p_cal, fitted on the hold-out ([Step 5](#step-5)) | A calibration fitted on known genes predicted 8.9% where 3.1% was observed |
| Literature check | Searches with the prediction in mind | Evidence collected blind, judged against three decoys per gene ([Step 7](#step-7)) | Judges' false-support rate is measurable (3/120); a language model "recognised" 43 of 59 published functions from the name alone |

**Why this matters.** Each change exists because a looser version overstated what co-essentiality can do. Leave-one-out
on well-studied genes made the method look about five times more accurate than it was on genuinely new annotations.
Most of the celebrated co-essentiality success stories turned out to be circular as validation, because their new GO
annotations cite papers that used DepMap (18 of 19 targets for SLC25A51, 14 of 15 for FIRRM). The pipeline writes a top
term for 4,137 genes, but at most about 650 carry a reproducible signal, so the usable-signal flag decides which genes
may enter the shortlist. The
result is a smaller, less exciting, but honest claim: co-essentiality gives specific, low-accuracy predictions for a
minority of strongly dependent genes. How each change came about is told in [JOURNEY.md](JOURNEY.md).

<a id="pipeline"></a>
## The pipeline at a glance

<!-- widget:pipeline -->
![Pipeline: input (19,296 genes, DepMap 26Q3, GO) → Step 1 pre-register (4,924 genes, 4,271 scorable) → Step 2 score co-essentiality → Step 3 usable signal (646 pass, at least about 322 real) → Step 4 assign a GO term (4,137 genes) → Step 5 calibrate on the 2018 hold-out (3.0% vs 0.5% null; max p_cal 0.141) → Step 6 prioritise (245 eligible → top 40) → Step 7 blinded literature check (18/40 vs 3/120 decoys) → output](figures/pipeline.svg)

*Steps 3 to 6 attach labels to every scorable gene rather than discarding genes: a prediction is written for all 4,137
genes with a reportable term, but only expressed, assessable genes with a calibrated probability can enter the top 40.
PNG version: [figures/pipeline.png](figures/pipeline.png).*

<a id="steps"></a>
## The seven steps

Each step says what it does, why it is needed, what goes wrong without it, which turning point in the project's history
shaped it, where the idea came from, and where the code is. Terms are defined in the [glossary](#glossary).

<a id="step-1"></a>
### Step 1. Pre-register the uncharacterised genes

**What it does.** Before any gene-to-gene co-essentiality score exists, it defines "uncharacterised" from annotation
databases only, applies the rule to all 19,296 human protein-coding genes, and freezes the resulting list with a
cryptographic hash. A gene is in the list **U** if:

- **D1**: it has no informative GO biological-process or molecular-function annotation backed by experimental or
  curator evidence (codes EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC). Generic terms such as "protein binding" do not count;
- **and** either **D2**, a UniProt annotation score of 2 or less (out of 5), **or D3**, at most 10 "focused" PubMed papers
  (papers that list at most 10 human genes) or IDG target class "Tdark" (the Illuminating the Druggable Genome class for
  proteins with almost no literature or functional annotation).

This gives **4,924 genes**, of which **4,271** have a DepMap profile the tool can score. An independent agent rebuilt the
list from the raw files with its own code and got the same genes. Every script that touches pairwise DepMap data first
calls a gate that refuses to run unless the frozen hash and git tag match.

**Why it is needed.** If the gene list is chosen after seeing the network, it can drift towards genes where the network
looks informative, and every later count is biased. The same rule (D1) also defines the hold-out genes of
[Step 5](#step-5) at the 2018 GO release, so the hold-out resembles the target genes by construction.

**What goes wrong without it.** The benefit is that results are checkable, not a measured gain in accuracy: a
chronology audit confirmed that no pairwise output predates the freeze. The step also exposed a cost of database
definitions. In a random 50 of the 4,924 genes, a literature audit found that **42%** (95% CI 29–56%) already had an
experimentally established function ("curation lag"). Genes that entered through the literature-attention route (D3:
few focused papers or Tdark) without a low UniProt score were N1 (function established) in 56% of cases (19/34), against
13% (2/16) for genes with a low UniProt score *[post-review]*. Counting only
"focused" papers makes protein-complex subunits, which are usually described in multi-subunit papers, look unstudied
(288 listed genes are Complex Portal subunits). No gene was removed after the freeze; the caveat travels with every
result.

**Shaped by:** [TP1](JOURNEY.md#tp-1), with the entry-route analysis from [TP8](JOURNEY.md#tp-8).
**Ideas from:** knownness measures and research-attention bias (Stoeger 2018, doi:10.1371/journal.pbio.2006643; Haynes
2018, doi:10.1038/s41598-018-19333-x; Unknome, Rocha 2023, doi:10.1371/journal.pbio.3002222; IDG Tdark, Oprea 2018,
doi:10.1038/nrd.2018.14); the UniProt score ≤ 2 threshold follows Wainberg 2021.
**Code:** `scripts/02_gene_knownness_table.py`, `scripts/03_build_preregistration.py`, `src/knownness.py` (`d1`, `d2`,
`d3`, `combine_u`), `src/gate.py` (`check`); outputs in `preregistration/`.

<a id="step-2"></a>
### Step 2. Score co-essentiality with the published tool (read-only)

**What it does.** It runs the co-essentiality tool zavg_BEF (github.com/cancergenetics/ai-hackathon-Coessentiality,
commit 3c684c9) unchanged, at its published settings, on DepMap 26Q3 (1,361 cell lines). The tool gives every gene pair
one score from three views of the knockout profiles, each put on a common scale against random gene pairs and averaged:

- **F**, how similar the two cleaned profiles are (cleaning removes the 20 strongest screen-wide patterns, a regularised
  form of the GLS whitening of Wainberg 2021);
- **B**, how much the two genes' top-44 partner lists overlap;
- **E**, how close the two genes sit in a 512-dimensional map of the whole partner network.

Higher means the two genes are needed by the same cell lines beyond what screen-wide patterns explain. The tool, its
design and its own validation are explained in its repository
([docs/explainer/METHOD.md](https://github.com/cancergenetics/ai-hackathon-Coessentiality/blob/main/docs/explainer/METHOD.md));
this project did not modify or tune it.

**Why it is needed.** The partner list is the only evidence the method uses. Every later step reads the full gene × gene
score matrix (18k × 18k) or its top-ranked rows.

**What goes wrong without it.** Not much, for this purpose. Before use, the project reproduced the tool's published
benchmark (average precision 0.3451 against 0.345 published), matched its GLS and Pearson baselines to within 3 × 10⁻⁷,
and passed 14 of 14 sign and orientation checks. On the 2018 hold-out, zavg_BEF predicted functions no better than GLS
(+0.006, 95% CI −0.005 to +0.017) or plain Pearson correlation (+0.002). The tool's large lead in finding protein-complex
pairs did not become a lead in predicting GO function. *Believed, not tested:* the bottleneck is the step from partners
to a GO term, and the scarcity of strongly dependent new genes.

**Shaped by:** no turning point; the brief fixed the tool ([JOURNEY.md](JOURNEY.md)).
**Ideas from:** the tool (zavg_BEF), building on co-essentiality as evidence of shared function (Pan 2018,
doi:10.1016/j.cels.2018.04.011; Kim 2019, doi:10.26508/lsa.201800278; Wainberg 2021).
**Code:** `scripts/00_get_tool.sh`, `scripts/10_full_matrix.py`, `scripts/11_reproduce_tool.py`,
`scripts/12_sanity_checks.py`, `scripts/16_baseline_rows.py`, `src/coess_matrix.py` (`fit_model`,
`write_tool_matrices`); the tool itself in `external/coessentiality/` (read-only).

<a id="step-3"></a>
### Step 3. Decide whether the gene has a usable signal

**What it does.** It asks whether a gene's partner list is stable enough to read, and labels the gene "assessable" or
not. It does not stop the later steps: every scorable gene still gets a top term (Step 4) and, if in calibration support,
a p_cal (Step 5); the label decides whether the gene can enter the shortlist (Step 6). The cell lines are split into two
halves five times (balanced by tissue and screening library, with lines from the same patient kept together), and the
tool is refitted on each half. Each half gives a top-25 partner list, built with the exclusions of [Step 4](#step-4).

- **R(g)**, the split-half reproducibility: the overlap of the two half-lists, as a fraction of 25, averaged over the
  five splits.
- **Null:** the same overlap computed between the gene's half-A list and the half-B lists of 200 *matched genes* (genes
  with similar mean effect, spread and missing data). The empirical p is (1 + number of matched genes with overlap ≥ R) /
  201.
- **Assessable** means p < 0.05 **and** the gene is expressed (log2(TPM+1) ≥ 1, TPM being transcripts per million, in at least
  10% of DepMap models, or in at least half the lines of one lineage). Non-expressed genes are scored anyway, as a negative control.

**Why it is needed.** Many uncharacterised genes are barely expressed or never essential, so their knockout profiles
are flat noise and their "top partners" are arbitrary. Even among expressed genes, about half are never hits in any
CRISPR screen, often because a paralogue buffers their loss (Dede 2020, doi:10.1186/s13059-020-02173-2). Such genes
should be labelled "no usable signal" rather than given a confident-looking shortlist place.

**What goes wrong without it.** *Not tested directly:* the hold-out was never split by this gate, so there is no
accuracy figure for assessable versus non-assessable genes. The evidence is indirect. On the hold-out, accuracy was
**0** in the two weakest fifths of genes by partner strength (mean score of the 25 neighbours) and **11.7%** (6.7–17.4%)
in the strongest fifth; the gate correlates with partner strength but is not the same thing. Only 2 of 516
chemosensory/epidermal-family genes passed.
The step has a known weakness: non-expressed control genes passed the reproducibility test **13%** of the time (27%
among those with any dependency), against a nominal 5%. Applying those false-pass rates back, the 646 assessable calls
exceed the null expectation by about 241 (168–306), which at full power implies **at least ~322** genes (6.5%, 242–388)
with real signal, under the untested assumption that the controls' false-pass rates apply to expressed genes
*[post-review]*. (The manuscript quotes 243 and 324 for the 635 calls under the frozen list's expression column; see
[DISCREPANCIES B13](DISCREPANCIES.md#b13).) In the calibration model of [Step 5](#step-5), R(g) received zero weight once
partner strength was known; so assessability works as a gate, not as a confidence score. The gate matters for how
headline numbers are read: about 82% of the summed p_cal comes from genes that fail it (Step 5).

**Shaped by:** [TP3](JOURNEY.md#tp-3), with the null-adjusted reading from [TP8](JOURNEY.md#tp-8).
**Ideas from:** the round-1 statistics reviewer's demand for a true cross-gene null rather than a quantile; matching on
profile covariates (Rubin 1980; Stuart 2010).
**Code:** `scripts/13_matched_lists.py`, `scripts/14_splithalf.py`, `scripts/15_assessability.py`, `src/splithalf.py`
(`split_halves`, `half_neighbours`, `reproducibility`, `assessable`, `expression_strata`), `src/predictor.py`
(`match_genes`).

<a id="step-4"></a>
### Step 4. Assign a candidate function

**What it does.** It turns the partner list into one GO term.

1. **Neighbours N(g):** the 25 highest-scoring partners, after removing genes outside the tool's well-measured
   background, genes on the **same chromosome arm** and **Ensembl paralogues**.
2. **Vocabulary V2:** GO biological-process and molecular-function terms with 5–200 annotated genes, where a gene
   counts as a member only through experimental or curator evidence (propagated up the GO hierarchy). An
   interaction-based annotation (evidence IPI) of a neighbour is dropped if it names the query gene, so the gene cannot
   vote for itself through a neighbour.
3. **Term score:** S(g, t) = sum of max(zavg_BEF, 0) over neighbours annotated to term t. Each such neighbour is a
   **supporting partner**.
4. **Reportable:** a term needs **at least 2 supporting partners**. The prediction is the top reportable term
   (ties broken by GO identifier; the most specific term among the top five is reported alongside).

**Why it is needed.** Partners are evidence about a module; curators annotate GO terms. Some rule has to turn many
partners with many annotations into one testable claim. The same-arm and paralogue exclusions exist because CRISPR
cutting can delete large parts of a chromosome arm, and copy-number changes move neighbouring genes together, so genes
near each other can look co-essential for reasons unrelated to function (Lazar 2024, doi:10.1038/s41588-024-01758-y);
paralogues can share guide RNAs or compensate for each other.

**What goes wrong without it.**
- **Choice of ranker.** Three rankers were declared before any data: R1 (the summed score above), R2 (hypergeometric
  over-representation) and R3 (comparison with matched genes). A fixed rule chose R1 on 2,519 well-studied genes:
  mean reciprocal rank 0.169, against 0.140, 0.111 and 0.073 for frequency alone. Shuffling annotations among genes
  collapsed top-term accuracy from 13.9% to 1.5%, so the signal comes from the network, not from term popularity.
- **Broad terms.** The worry that a sum favours large terms was partly right: R1's top terms had a median of about 131
  annotated genes, against 35 for R2. This is the multifunctionality bias of Gillis & Pavlidis (2011,
  doi:10.1371/journal.pone.0017258).
- **Ties.** The top score was tied in 401 of 820 hold-out genes, usually between a term and its parent. Reversing the
  tie order changed 393 labels but left accuracy almost unchanged (3.2% instead of 3.0%).
- **Exclusions.** In the project's synthetic test, genes sharing a "chromosome-arm" artefact called their artefact term
  first 100% of the time without the exclusion and 0% with it. On the real hold-out, dropping the exclusions changed
  accuracy little (3.3% instead of 3.0%), so the guard costs nothing measurable; it can, however, discard a true partner
  (see TARBP2 in the [worked example](#worked-example)).
- **"≥ 2 partners" barely filters.** On synthetic null data every gene still had a reportable term. Confidence has to
  come from [Step 5](#step-5).

**Shaped by:** [TP4](JOURNEY.md#tp-4).
**Ideas from:** neighbour-voting guilt by association (Pan 2018; Wainberg 2021); multifunctionality and edge-dependence
critiques (Gillis & Pavlidis 2011; 2012, doi:10.1371/journal.pcbi.1002444); chromosome-arm proximity artefacts (Lazar 2024).
**Code:** `scripts/30_loo_ranker_choice.py`, `scripts/31_label_shuffle.py`, `scripts/40_u_predictions.py`,
`src/neighbours.py` (`top_k`), `src/vocab.py` (`build_v2`, IPI rule), `src/predictor.py` (`term_scores`, `score_table`,
`top_terms`, `most_specific`).

<a id="step-5"></a>
### Step 5. Calibrate confidence on a temporal hold-out

**What it does.** It measures accuracy, and learns a probability, on genes whose function was discovered *after* the
annotations used to predict it.

- **Hold-out H:** freeze GO at **2 July 2018**. Take genes that met rule D1 then, had at most 10 focused papers by then,
  and gained experimental GO terms since: **820 genes**, 5,965 new (gene, term) targets. Predict each gene's function from
  its neighbours' **2018** annotations and score the top term against the terms it received later. (The co-essentiality
  network is from 2026 data, so only the annotations are rolled back.)
- **Circularity filter:** every paper behind a target annotation was searched in Europe PMC full text for DepMap or
  co-essentiality terms; flagged annotations were removed (106 targets; 809 genes remain).
- **Comparators:** a frequency-only ranking ("prior-only"), a matched-gene null (the same predictor run from five genes
  with similar profiles), GLS, Pearson, homology (the gene's own 2018 electronic and phylogenetic annotations) and
  protein-interaction transfer from hu.MAP 3.0.
- **Calibration:** a logistic regression, with signs fixed in advance, of "top term later confirmed" on four covariates
  (mean score of the 25 neighbours, R(g), the share of neighbours with any annotation, and the size of the top term) plus
  the term's family. It is fitted on the 775 hold-out genes with a prediction and checked by cross-fitting over clusters
  of genes that share papers. Applied to U, it gives **p_cal**, but only for genes whose covariates lie inside the
  hold-out's 5th–95th percentiles and whose term family has at least 30 hold-out genes ("in support").

The specification was written to [LOOKS.md](../../LOOKS.md) 31 minutes before the hold-out was opened, once.

**Why it is needed.** Leave-one-out tests well-studied, multifunctional genes, which are easy to predict from network
position alone and unlike the genes the method is for. A temporal split reproduces the real situation: predict now,
be checked later.

**What goes wrong without it.**
- Leave-one-out gave top-term accuracy **13.9%**; the hold-out gave **3.0%**. Part of this gap reflects different genes,
  not only leakage (open question; [DISCREPANCIES C4](DISCREPANCIES.md#c4)).
- A calibration fitted on leave-one-out genes predicted a mean probability of **0.089** on the hold-out, where **0.031**
  was observed.
- Without the circularity filter, the named success stories would count as validation. The filter removed only 1.8% of
  targets overall (accuracy 3.2% → 3.0%), but most targets of exactly those genes. Of 14 named controls, only TMEM242
  ranked its true term first, and only in the descriptive case series ([worked example](#we-tmem242)).
- **p_cal is conditional.** Every hold-out gene *did* gain annotation, so p_cal estimates P(top term confirmed | the gene
  is annotated later). Only 16% of eligible 2018 genes gained annotation in about 8 years, so the expected number of
  confirmations among the 2,583 calibrated genes is about **4.9** (2.2–8.1), not 30.5 *[post-review]*.
- **Most of that comes from genes without a usable signal.** Of the 30.5, only 5.49 (2.81–8.64) comes from the 269
  expressed, assessable genes in support (`results/ledger/pcal_summary.json`); the other 82% comes from genes that fail
  Step 3. Rescaled by the same 16.1% annotation rate (775/4,822), the 269 assessable genes are expected to yield about
  **0.9** (roughly 0.45–1.4, ignoring uncertainty in the rate) confirmed top terms *[derived for this explainer; the
  manuscript does not state it; [DISCREPANCIES B19](DISCREPANCIES.md#b19)]*.
- The model rests on **24 correct calls**. Out-of-fold calibration slope 0.82 (0.51–1.13); c-statistic 0.86 (the chance
  that a randomly chosen correct call gets a higher probability than a randomly chosen wrong one); Brier skill only 2%
  (the Brier score, the mean squared error of the probabilities, is only 2% better than always predicting the base
  rate): not detectably off, but thin. Simpler models calibrate as well but share only 7–14 of the top 40
  genes with it *[post-review]*.

**Shaped by:** [TP2](JOURNEY.md#tp-2), [TP5](JOURNEY.md#tp-5) and [TP8](JOURNEY.md#tp-8).
**Ideas from:** the CAFA time-split design (Radivojac 2013, doi:10.1038/nmeth.2340; Zhou 2019,
doi:10.1186/s13059-019-1835-8); logistic calibration and its checks (Cox 1958; Van Calster 2019,
doi:10.1186/s12916-019-1466-7); cluster bootstrap (Field & Welsh 2007); intersection–union test (Berger 1982).
**Code:** `scripts/04_holdout_sizing.py`, `scripts/05_circularity_query.py`, `scripts/32_holdout_core.py`,
`scripts/33_holdout_secondary.py`, `scripts/34_calibration_fit.py`, `scripts/41_pcal.py`, `src/calibration.py`
(`MonotoneLogistic`, `cross_fit`, `support_mask`, `p_cal`), `src/metrics.py`, `src/ledger.py` (`pcal_from_model`,
`support_category`).

<a id="step-6"></a>
### Step 6. Add orthogonal evidence and prioritise

**What it does.** It ranks candidates and attaches independent evidence and warnings to each.

- **Orthogonal evidence:** data that never saw DepMap, in five classes: physical interaction (BioPlex, OpenCell,
  BioGRID low-throughput, STRING experiments; Human Cell Map), protein co-abundance (ProteomeHD, CCLE proteomics),
  localisation (Human Protein Atlas), Perturb-seq and AlphaFold2 pair models. Sources were admitted only if they
  recovered known complexes before any prediction existed (11 of 12 pair sources passed). For a prediction, each source
  tests whether the gene is closer to the predicted term's members than 1,000 degree-matched random member sets; p-values
  are combined within a class (Simes) and across classes (Holm, α = 0.05).
- **Artefact flags:** overlapping loci, copy-number co-amplification and hub-driven scores; a prediction with flags on
  half or more of its supporting partners is excluded from the top.
- **Prioritisation:** the design promised tiers (Tier A: p_cal ≥ 0.5 plus orthogonal support; Tier B: p_cal ≥ 0.3).
  No gene reached either, so a pre-written "low-yield" branch applied: the **top 40 is the 40 highest p_cal values**
  among expressed, assessable, in-support genes (269), after artefact exclusions and one contradiction (245 remain),
  with mitochondrial calls capped at 6 of the top 20.
- **Labels, not demotions:** top-40-only checks (refit without the most dependent lineage, replication in DEMETER2 RNAi
  data, TP53 dependence) are shown next to each gene.
- **A separate list (S20):** the 20 strongest predictions that cannot be calibrated (machinery families with fewer than
  30 hold-out genes, or signals beyond the hold-out's range), kept apart from the calibrated top 40.

**Why it is needed.** p_cal is one number from one data type. Independent data can catch artefacts, and a reader needs
to know which predictions rest on hubs, neighbouring loci or a single tissue.

**What goes wrong without it, and what went wrong with it.** The checks were never validated on known positives before
they could demote genes, and they did not separate signal from noise. Orthogonal support passed **32%** of real
predictions, **28%** of matched-gene predictions and **22%** of decoy-term predictions (247 each); in the top 40,
62.5% vs 47.5% vs 25%. The robustness checks failed 221 of 269 candidates, 182 of 204 of them on RNAi replication. Using
them as demotions (an agent's "clean-first" fill) would have produced a top 40 sharing only 20 genes with the p_cal
order. Without the separate S20 list, the best-established co-essentiality signals (mitochondria, DNA repair, ribosome,
nuclear RNA, centrosome) would be invisible, because the calibration's support rule excludes them; judges later supported
19 of those 20, all with earlier catalogue links (Rahman 2021, doi:10.15252/msb.202010013, documents this mitochondrial
dominance).

**Shaped by:** [TP6](JOURNEY.md#tp-6).
**Ideas from:** independent evidence classes, each source admitted only if it recovered 2,538 known complexes not
derived from hu.MAP (design choice, DESIGN §5); Simes 1986 and Holm 1979 for combining tests; mitochondrial bias in screens (Rahman
2021).
**Code:** `scripts/20_source_admission.py`, `scripts/42_artefact_flags.py`, `scripts/43_orthogonal_support.py`,
`scripts/44_tiers_top40.py`, `scripts/46_top40_primary.py`, `src/support.py` (`source_test`, `support_test`, `simes`,
`holm`), `src/orthogonal.py`, `src/ledger.py` (`exclusion_43`, `tier_of`, `fill_top`).

<a id="step-7"></a>
### Step 7. Check the literature blind

**What it does.** It asks whether published evidence supports each top prediction, in a way that measures how easily
"supported" is said.

1. **Recall probe:** before anything else, a language model without tools says what it knows about each gene. This
   measures how much a model "already knows".
2. **Blind literature screen:** a separate agent with no access to predictions or co-essentiality output searches the
   literature and writes an evidence table with verbatim quotes, and classes each gene N1 (function established), N2
   (partial) or N3 (none).
3. **Statements and decoys:** each prediction becomes a script-written statement (GO term plus a module label). It is
   shown with **three decoys**, the top terms of other genes matched on term family and size, in random order. Gene names
   are redacted from the evidence; a leak check found none.
4. **Judge validation:** on 10 hold-out genes with known answers, the judges had to support at least 7 of 10 real
   statements and at most 3 of 30 decoys. They scored 9/10 and 1/30.
5. **Judging:** two independent judges score every statement +1 (supported), 0 (not addressed) or −1 (contradicted); an
   adjudicator resolves disagreements. The test is a one-sided sign-flip test of real minus mean decoy score over the top
   40.

**Why it is needed.** An agent that knows the prediction and then searches will find support. A model may also simply
remember gene functions: the recall probe "recognised" 43 of 59 genes with an established function. Decoys turn
literature support into a test with a measurable false-support rate.

**What goes wrong without it.** Without decoys there is no way to tell real support from leniency; with them, judges
supported **18 of 40** real statements against **3 of 120** decoys (p = 0.0002). Without the novelty classes the 18 would
read as discoveries; **16 of the 18** were N1 genes whose function was already published. The judging rule itself
mattered: the judge prompt credited a match to "the stated process *or module*", a choice that was not logged before
judging. Counting the GO term only gives **16/40** (p = 7 × 10⁻⁴) *[logged retrospectively]*. Agreement between the two
judges (κ = 0.975) shows that two instances of one model agree, not that they are right.

**Shaped by:** [TP7](JOURNEY.md#tp-7), with the scoring-rule and novelty corrections from [TP8](JOURNEY.md#tp-8).
**Ideas from:** blinded assessment with decoys (design choice of this project, DESIGN §6.2–6.4); Cohen's κ (Cohen 1960);
symbol hygiene for literature agents (previous symbols and aliases).
**Code:** `scripts/50_m7_prep.py`, `scripts/51_judge_packets.py`, `scripts/52_judge_analysis.py`, `src/redact.py`,
`src/metrics.py` (`sign_flip_test`, `cohens_kappa`); agent prompts verbatim in [docs/AGENT_PROMPTS.md](../AGENT_PROMPTS.md).

<a id="worked-example"></a>
## Worked example: ANKRD52 through all seven steps

**ANKRD52** came out **rank 1 of the primary top 40**. Its predicted function, microRNA-mediated gene silencing, had
already been published, so the reader can watch the method recover an answer that is known to be right. Every number
below was recomputed by [worked_example.py](worked_example.py), which calls the pipeline's own functions; 159 of 159
values matched the committed results (details and all tables:
[worked_example_notes.md](worked_example_notes.md), [worked_example_output/](worked_example_output/)). The notes number
their sections 0–7 by pipeline stage; the mapping to the seven method steps is given in each panel title below.

<!-- worked:start -->

### Step 1 · Pre-registration: why ANKRD52 counts as "uncharacterised"

ANKRD52 has three experimental GO rows, all "protein binding" (evidence IPI). That term is generic, so it has **0
informative terms: D1 is true**. Its UniProt annotation score is 3, so **D2 is false**. It has **6 focused papers** (62
in total), so **D3 is true**. It entered U through D1 + D3.

**This is a curation-lag case.** A 2017 study (PMID 28114302) showed that the ANKRD52–PPP6C phosphatase removes
phosphates from AGO2 and that this cycle is needed for microRNA silencing. GO never recorded it with an experimental
code. The blind literature agent later classed ANKRD52 as N1 (function established), and co-essentiality catalogues
had already linked it to the microRNA machinery (Kim 2019; Wainberg 2021). The example is a validation, not a discovery.

### Step 2 · Co-essentiality scores

ANKRD52 has a value in all **1,361** cell lines (mean gene effect −0.243, SD 0.231; 12.4% of lines below −0.5): a weak,
selective dependency. The method uses the *pattern* of these values. Across all genes, ANKRD52's zavg_BEF scores have
median −0.09 and 99.9th percentile 5.4; its strongest partners score far above that.

| rank | partner | zavg_BEF | z_B | z_E | z_F |
|---|---|---|---|---|---|
| 1 | AGO2 | 25.76 | 43.28 | 20.59 | 13.41 |
| 2 | XPO5 | 24.40 | 42.90 | 20.19 | 10.11 |
| 3 | DICER1 | 23.69 | 41.51 | 19.84 | 9.70 |
| 8 | PPP6C | 13.62 | 20.85 | 11.76 | 8.25 |

![ANKRD52 gene-effect profile plotted against AGO2 (Pearson r = 0.37, its top partner) and against PPP6C (r = 0.28, its known biochemical partner)](figures/we_profile.png)

### Step 3 · Usable signal

Over five split halves, ANKRD52's two top-25 lists shared 10, 10, 13, 13 and 13 genes: **R = 0.472**. AGO2, XPO5,
DICER1, DROSHA, DGCR8, TNRC6A/B, CNOT9 and PPP6R1 were shared in every split. Against its 200 matched genes the mean null
overlap was 0.0037 (maximum 0.20), so none reached R: **p = 1/201 = 0.005**. ANKRD52 is expressed (median log2(TPM+1)
3.94), so it is **assessable**. Context: only 646 of 4,924 genes pass, and 13% of non-expressed controls pass the p-value
part.

![Histogram of the null split-half overlaps for ANKRD52's 200 matched genes, nearly all near 0, with ANKRD52's own reproducibility R = 0.472 far to the right (p = 1/201)](figures/we_assessability.png)

### Step 4 · Candidate function

**Neighbours.** Two same-arm genes (ANKRD52 is on 12q) and three paralogues were removed. One of them, **TARBP2**
(score 13.42, would have ranked 9th), is a Dicer cofactor: the artefact guard threw away a true partner. The 25th
neighbour scores 4.52; the mean over the 25, **10.68**, is reused in Step 5.

![Bar chart of ANKRD52's 25 neighbours by zavg_BEF; the eight annotated to the predicted term (AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8, TNRC6B, DDX6) are highlighted; a side panel shows the five excluded genes, led by TARBP2 (same arm)](figures/we_neighbours.png)

**Terms.** 22 of 25 neighbours carry at least one annotation; 238 terms get S > 0 and 45 are reportable. Ranks 3 and 4
are tied (a parent and child term with the same five supporting partners), a live case of the tie problem of Step 4.

| rank | GO term | S | supporting partners |
|---|---|---|---|
| **1** | **regulatory ncRNA-mediated gene silencing (GO:0031047)** | **158.11** | **8** |
| 2 | post-transcriptional gene silencing | 115.69 | 6 |
| 3 | regulatory ncRNA-mediated post-transcriptional gene silencing | 92.00 | 5 |
| 4 | miRNA-mediated post-transcriptional gene silencing | 92.00 | 5 |
| 5 | miRNA processing | 91.87 | 4 |

S = 25.76 + 24.40 + 23.69 + 22.37 + 21.00 + 20.05 + 16.27 + 4.57 = 158.11 (AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8,
TNRC6B, DDX6). ANKRD52's biochemical home, the PP6 phosphatase (PPP6C, PPP6R1, PPP6R3 and PTPA are all neighbours),
ranks only 37th (*phosphoprotein phosphatase activity*, S = 24.9), because few PP6 members carry experimental GO terms.
The GO vote follows the best-annotated partners.

![Top GO terms for ANKRD52 ranked by term score S; regulatory ncRNA-mediated gene silencing leads with S = 158 from 8 partners](figures/we_term_scores.png)

### Step 5 · Calibrated probability

| covariate | ANKRD52 | hold-out 5th–95th percentile | coefficient |
|---|---|---|---|
| mean score of the 25 neighbours | 10.68 | 3.33–10.99 | +0.285 |
| R(g) | 0.472 | 0–0.546 | 0 (shrunk to its bound) |
| annotated-neighbour share, as a percentile | 0.859 | 0.075–0.894 | +1.704 |
| top-term size, as a percentile | 0.172 | 0.049–0.950 | 0 (shrunk) |

logit = −6.3155 + 0.28504 × 10.682 + 1.70378 × 0.8591 = −1.807, so **p_cal = 0.141**: the **highest of the 2,583
calibrated genes**, yet below Tier B (0.30). On the hold-out, genes in the top probability decile (mean 0.170) were
confirmed 11.5% of the time (6.2–20.5%). Read p_cal as "about a one-in-seven chance that this exact GO term is
experimentally annotated within about 8 years, *if* the gene is annotated at all".

![Left: hold-out reliability by decile, observed confirmation rate against predicted probability, with ANKRD52's p_cal of 0.141 marked; right: histogram of p_cal over the 2,583 calibrated genes, with ANKRD52 the highest](figures/we_calibration.png)

### Step 6 · Orthogonal evidence and rank

Tested against the 62 genes annotated to the predicted term: physical interaction p = 0.565 (its physical edges go to
PP6 subunits and TNRC6B), co-abundance p = 0.028, localisation p = 0.021, Perturb-seq and structure not measured. Holm
needs the smallest class p ≤ 0.05/3 = 0.0167, so **no class is called "supports"**, and there is no contradiction. The
same test gave a matched gene (MTA2) co-abundance and localisation support, and gave a decoy term nothing. ANKRD52 passed
the top-40-only checks that could be run (lineage leave-out, no expression coupling, no TP53 effect; RNAi not measured).
It is **rank 1 of 245 eligible genes**.

![Per-class orthogonal evidence for ANKRD52's prediction compared with a matched gene and a decoy term; no class reaches the Holm threshold for ANKRD52](figures/we_support.png)

### Step 7 · Blind literature check

The literature agent found 11 items (7 functional) and classed ANKRD52 **N1**. In its judging packet (J071) the judges saw four
statements with the gene name redacted:

| slot | statement | real? | judge 1 | judge 2 |
|---|---|---|---|---|
| A | modulation of chemical synaptic transmission | decoy | 0 | 0 |
| B | deacylase activity | decoy | 0 | 0 |
| **C** | **regulatory ncRNA-mediated gene silencing; RISC complex** | **real** | **+1** | **+1** |
| D | dicarboxylic acid metabolic process | decoy | 0 | 0 |

Both judges cited the AGO2-dephosphorylation evidence. Real minus mean decoy score: **d = 1**. Over the top 40, 18
genes were supported like this, most of them, like ANKRD52, rediscoveries.

<a id="we-tmem242"></a>
### Hold-out control · TMEM242 (how the method was validated)

**TMEM242** shows the hold-out logic. In 2018 it had no informative GO term. Its 25 neighbours are dominated by ATP
synthase subunits (ATP5F1A/B/C/D/E, ATP5PB/PD/PF/PO and others) plus TMEM70, OXA1L and STOML2 (mean score 13.05,
R = 0.67). In 2021 one paper (PMID 33753518, not flagged as DepMap-derived) gave it five terms, including
*mitochondrion organization* and three ATP-synthase-assembly terms.

| analysis | term window | top term from 2018 annotations | later received? |
|---|---|---|---|
| named-control case series (descriptive) | 2–300 genes | mitochondrion organization (S = 272, 18 partners) | **yes, rank 1 of 77** |
| **primary hold-out endpoint (pre-registered)** | 5–200 genes | generation of precursor metabolites and energy | **no**; the in-window later terms ranked 49 and 50 |

Stated plainly: **TMEM242 is a miss on the pre-registered primary endpoint and a hit only in the descriptive case
series.** The term it received has 204 annotated genes, just above the 200-gene ceiling, and the specific assembly
terms had too few annotated neighbours in 2018. Its out-of-fold p_cal was 0.28. It is the only one of 14 named controls
whose true term ranked first, and that only under the wider window.

![TMEM242's 2018 term ranking under the 2–300 window: mitochondrion organization, a term it received after 2018, ranks first; the remaining top-10 terms were not received](figures/we_holdout_tmem242.png)

<!-- worked:end -->

<a id="code"></a>
## Pseudocode and where each step lives in the code

```text
# Step 1  (before the freeze; annotation data only)
U = {g in HGNC protein-coding : D1(g, GO_now) and (D2(g) or D3(g))}       # 4,924 genes
freeze(U, design, config) -> FREEZE.sha256 + git tag; gate.check() guards every later pairwise script

# Step 2  (tool, read-only)
Z = zavg_BEF(DepMap_26Q3)                       # gene x gene score; mean of z-scored F, B, E

# Step 3
for g in scorable(U):
    N_A[s], N_B[s] = top25(tool(half_A[s]), g), top25(tool(half_B[s]), g)   for s in 0..4
    R[g]  = mean_s |N_A[s] ∩ N_B[s]| / 25
    R0[m] = mean_s |N_A[s](g) ∩ N_B[s](m)| / 25   for 200 matched genes m
    p[g]  = (1 + #{m : R0[m] >= R[g]}) / 201
    assessable[g] = p[g] < 0.05 and expressed[g]

# Step 4
N(g) = top 25 of Z[g, :] excluding self, non-background, same chromosome arm, paralogues
S(g, t) = sum_{j in N(g), j annotated to t} max(Z[g, j], 0)             # V2 terms, 5-200 genes, IPI rule
top_term(g) = argmax_t S(g, t) over terms with >= 2 supporting partners  # ties: ascending GO id

# Step 5  (one look at H)
H = genes with D1 at GO 2018-07-02, <= 10 focused papers, new experimental terms since; drop DepMap-citing annotations
rerun Steps 3-4 for H with 2018 annotations; hit[g] = top_term(g) in new_terms(g)
model = sign-constrained logistic(hit ~ mean Z of N(g) + R + coverage_pct + size_pct + family), cluster cross-fitted
p_cal(g in U) = model(g) if covariates within H's 5th-95th percentiles and family has >= 30 H genes else none

# Step 6
support(g) = Holm over classes(Simes over sources(empirical p vs 1,000 degree-matched member sets))
pool  = U genes that are expressed, assessable, in support, without artefact exclusion or contradiction
top40 = pool sorted by p_cal (tiers A/B first if any; mitochondrial <= 6 of top 20); checks attached as labels

# Step 7
for g in top40 (+ S20, extra30, 10 validation genes): evidence(g) = blind_literature_agent(g)  # N1/N2/N3
packet(g) = shuffle([statement(top_term(g))] + 3 decoys); redact names; judges J1, J2 (+ adjudicator)
test: one-sided sign-flip on d(g) = score(real) - mean(score(decoys))
```

| Step | Scripts (`scripts/`) | Modules (`src/`) | Main outputs |
|---|---|---|---|
| 1 Pre-register | `02_gene_knownness_table.py`, `03_build_preregistration.py` | `knownness.py`, `gate.py` | `preregistration/uncharacterised_genes.tsv`, `FREEZE.sha256` |
| 2 Score | `00_get_tool.sh`, `10_full_matrix.py`, `11_reproduce_tool.py`, `12_sanity_checks.py`, `16_baseline_rows.py` | `coess_matrix.py` (+ tool in `external/coessentiality/`) | `data/derived/matrices/zavg_full/`, `results/verification/` |
| 3 Usable signal | `13_matched_lists.py`, `14_splithalf.py`, `15_assessability.py` | `splithalf.py`, `predictor.py` (`match_genes`) | `results/assessability/assessability_U.tsv` |
| 4 Assign function | `30_loo_ranker_choice.py`, `31_label_shuffle.py`, `40_u_predictions.py` | `neighbours.py`, `vocab.py`, `predictor.py` | `results/ledger/u_predictions.tsv`, `u_partners.tsv` |
| 5 Calibrate | `04_holdout_sizing.py`, `05_circularity_query.py`, `32_holdout_core.py`, `33_holdout_secondary.py`, `34_calibration_fit.py`, `41_pcal.py` | `calibration.py`, `metrics.py`, `ledger.py` | `results/holdout_eval/`, `results/calibration/model_H.json`, `results/ledger/u_pcal.tsv` |
| 6 Prioritise | `20_source_admission.py`, `42_artefact_flags.py`, `43_orthogonal_support.py`, `44_tiers_top40.py`, `46_top40_primary.py` | `support.py`, `orthogonal.py`, `ledger.py` | `results/ledger/support.tsv`, `top40_primary.tsv` |
| 7 Literature | `50_m7_prep.py`, `51_judge_packets.py`, `52_judge_analysis.py` | `redact.py`, `metrics.py` | `results/m7/judge/analysis_main.md` |

Run order, runtimes and the gate are in the repository [README](../../README.md#run-order); module details in
[docs/PIPELINE.md](../PIPELINE.md).

<a id="results"></a>
## Results and how strong the evidence is

**What was evaluated.** Four claims, fixed in the frozen design: how many pre-registered genes carry a usable signal
(C1); top-term accuracy on the 2018 hold-out against nulls (C2, the primary test); calibrated predictions for the
pre-registered genes (C3); and blinded literature support for the top 40 (C4). Labels: *pre-specified* (frozen design),
*deviation* (a logged change), *exploratory* (post hoc, before review), *post-review* (requested by referee agents after
the first manuscript draft; no frozen rule changed).

| Evaluation | Compared with | Outcome (95% CI) | Status |
|---|---|---|---|
| Tool reproduction | Published average precision 0.345 | 0.3451 | Pre-specified check |
| Ranker choice (2,519 known genes) | R2, R3, frequency only | MRR 0.169 vs 0.140, 0.111, 0.073 | Pre-specified rule |
| **C1** usable signal | Non-expressed controls (false-pass rate 13%) | 646 of 4,924 (13.1%); excess over null ~241 (168–306); at least ~322 (242–388) real | Count pre-specified; adjustment post-review |
| **C2** top-term accuracy, 809 hold-out genes | Prior-only 0.000; matched-gene null 0.005 (0.003–0.008) | **0.030 (0.018–0.043)**; vs null +0.025 (+0.013 to +0.038); passes; re-derived independently (809/809 genes) | Pre-specified primary |
| C2 vs other scores | GLS 0.023; Pearson 0.027 | zavg_BEF − GLS +0.006 (−0.005 to +0.017) | Pre-specified secondary |
| C2 vs other evidence | Homology 0.218 (0.184–0.253); hu.MAP transfer 0.049 (0.034–0.066) | Co-essentiality far below both | Pre-specified secondary |
| C2 by subgroup | — | Strongest-signal fifth 0.117 (0.067–0.174); complex membership 0.182 (0.093–0.286); reweighted to resemble U 0.012 (0.007–0.019) | Pre-specified secondary |
| Combination with homology | Homology alone 0.218 | "Homology, else co-essentiality" 0.224 (+0.006, +0.001 to +0.012); 15 of 24 co-essentiality hits missed by homology | Exploratory / post-review |
| Calibration (out of fold) | Perfect calibration (slope 1) | Slope 0.82 (0.51–1.13), c 0.855, Brier skill 0.021; 24 events | Pre-specified; "thin" reading post-review |
| **C3** calibrated catalogue | Tier thresholds 0.3 / 0.5 | Max p_cal 0.141; no tiered gene; Σp_cal 30.5 (13.8–49.7) conditional, ~4.9 (2.2–8.1) unconditional; over the 269 assessable genes 5.5 conditional, ~0.9 unconditional (derived here) | Pre-specified; unconditional post-review |
| Orthogonal support | Matched-gene and decoy predictions | 0.32 vs 0.28 vs 0.22 (247 each) | Pre-specified |
| **C4** blinded literature, top 40 | 3 decoys per gene | **18/40 vs 3/120**, sign-flip p = 0.0002; term only 16/40, p = 7 × 10⁻⁴ | Pre-specified; scoring rule logged retrospectively |
| C4 secondary sets | — | S20 (20 strong uncalibrated predictions) 19/20 vs 2/60 decoys; extra30 (30 lower-p_cal genes from the shortlist pool) 1/30 | S20 a deviation; extra30 pre-specified |
| Novelty | Earlier catalogues | 31/40 N1; 34/40 prior link; 9/10 report genes with a published co-essential link (3 explicit Wainberg 2021 predictions) | Post-review |

**How strong is the evidence?** The primary test (C2) is the strongest result: specified 31 minutes before a single look,
re-derived by an independent agent, robust in all 10 split-half networks and every circularity variant. But the effect is
small (24 correct genes out of 809), and the comparison that matters most for a user, homology, is lost sevenfold. The
literature result (C4) is significant but easy: decoys are other genes' terms, so a gene with any literature can win on
topic alone, and judges were two instances of one model. The calibration is formally adequate but rests on 24 events, and
the top-40 ranking it produces is fragile. Nothing was validated at the bench, and no human has checked any result.

<a id="limitations"></a>
## Limitations, assumptions and when not to use it

**Assumptions.**
- GO experimental annotation is a fair proxy for "function established". It is not: 42% of a random sample of
  "uncharacterised" genes already had published function.
- Genes annotated after 2018 behave like today's uncharacterised genes. The hold-out genes have stronger signal than U
  (reweighting to U drops accuracy from 3.0% to 1.2%), and p_cal is conditional on later annotation.
- The 2026 DepMap network carries no post-2018 knowledge about the hold-out genes. Only annotations were rolled back; the
  tool's settings were tuned on hu.MAP 3.0, built after 2018. Parity with untuned Pearson bounds this leak but does not
  measure it.
- Non-expressed genes estimate the false-pass rate of Step 3 for expressed genes (untested).

**What was not validated.**
- No prediction was tested experimentally; the ten candidate reports propose experiments only.
- The orthogonal-support rule and the top-40 robustness checks were never validated on known positives.
- Within-gene decoys (the gene's own lower-ranked terms) were not run, so the judging does not show that the *top* term
  beats the gene's other candidates.
- Judges' validity rests on 10 validation genes and the decoy rate; heterogeneous judges (other models, human curators)
  were not used.
- Novelty against Pan 2018, FIREWORKS and Perturb-seq clusters could not be checked; prior-knowledge counts are lower
  bounds.
- Temperatures and seeds of model calls were not recorded; the agent-run log has one row.

**When not to use it.**
- **As a general annotator.** Use homology or interaction-based transfer first; co-essentiality adds a few distinct correct
  calls (+0.6 points) where homology is silent.
- **For genes without a usable signal** (not assessable, not expressed, chemosensory or epidermal families): the method
  about 87% of the pre-registered genes fail the usable-signal rule. Their predictions are still written and some carry a
  p_cal, but they are flagged and should not be read as evidence.
- **Reading p_cal as the chance that the biology is right.** It is the chance that this exact GO term is curated with
  experimental evidence, given that the gene is annotated at all.
- **Expecting novelty.** Check earlier co-essentiality catalogues (Wainberg 2021; Kim 2019) before calling a prediction new.
- **For machinery genes** (mitochondria, ribosome, DNA repair, nuclear RNA, centrosome): they have no calibrated
  probability; use the separate, uncalibrated S20-style list and treat it as descriptive.
- **Without checking neighbouring-gene and paralogue artefacts** if the exclusions in Step 4 are removed.

<a id="glossary"></a>
## Glossary

- **AP (average precision).** The area under a precision–recall curve; the tool's own benchmark measure for finding
  co-complex pairs.
- **Assessable.** A gene whose top-25 partner list reproduces across split halves (p < 0.05 against matched genes) and
  that is expressed. See [Step 3](#step-3).
- **Background (BG).** Genes with less than 10% missing DepMap values (17,525 genes); only these can be neighbours.
- **Brier score, Brier skill.** The mean squared error of predicted probabilities; skill is the fractional improvement
  over always predicting the base rate.
- **c-statistic.** The chance that a randomly chosen correct call gets a higher predicted probability than a randomly
  chosen wrong one (0.5 = no discrimination).
- **Calibration, calibrated.** Probabilities are calibrated if, among predictions given 0.1, about 10% come true.
- **Calibration support ("in support").** A gene whose covariates lie within the hold-out's 5th–95th percentiles and
  whose term family has at least 30 hold-out genes; only these get a p_cal (2,583 genes).
- **Chronos gene effect.** DepMap's estimate of how much knocking out a gene slows a cell line's growth: 0 no effect,
  about −1 a typical essential gene (Dempster 2021, doi:10.1186/s13059-021-02540-7).
- **Circularity filter.** Removal of hold-out target annotations whose supporting papers mention DepMap or
  co-essentiality in full text.
- **Clean negative.** A gene not expressed (log2(TPM+1) < 0.5) in at least 95% of cell lines; used as a negative control.
- **Cluster bootstrap.** Confidence intervals from resampling clusters of genes that share supporting papers, so that
  related genes are not counted as independent.
- **Co-essentiality.** Two genes are co-essential when their knockout profiles across cell lines rise and fall together,
  which often means shared function.
- **Coverage.** The share of a gene's 25 neighbours with at least one annotation; enters calibration as a percentile.
- **Curation lag.** A function is published but not (yet) recorded in GO with experimental evidence.
- **D1, D2, D3.** The three knownness criteria of [Step 1](#step-1).
- **Decoy.** Another gene's predicted term, matched on family and size, shown to judges (or tested for orthogonal support)
  as a negative control.
- **DepMap.** The Cancer Dependency Map; release 26Q3 has 1,361 cell lines and 18,434 genes.
- **Evidence codes.** GO annotation provenance: experimental (EXP, IDA, IPI, IMP, IGI, IEP), curator/author (TAS, IC),
  electronic (IEA), similarity (ISS), phylogenetic (IBA) and others.
- **Expressed.** log2(TPM+1) ≥ 1 in at least 10% of DepMap models or in at least half the lines of one lineage.
- **extra30.** 30 further genes from the top-40 pool, six per p_cal fifth, judged as a secondary set.
- **GLS.** Generalised least squares correlation: a profile correlation after removing the correlation between related
  cell lines (Wainberg 2021).
- **GO; BP, MF, CC.** Gene Ontology; biological process, molecular function, cellular component.
- **H (hold-out).** 820 genes uncharacterised in GO on 2 July 2018 that gained experimental terms since (809 after the
  circularity filter).
- **Homology baseline.** Ranking the gene's own 2018 electronic, similarity and phylogenetic GO terms.
- **hu.MAP 3.0.** A protein-complex atlas from proteomics (Fischer 2025, doi:10.1038/s44320-025-00121-5); used as a comparator, never as support.
- **Intersection–union test.** The primary test passes only if the method beats both nulls.
- **IPI rule.** An interaction-based annotation of a neighbour is ignored if its partner field names the query gene.
- **κ (kappa).** Cohen's chance-corrected agreement between two judges.
- **Leave-one-out (LOO).** Hide a known gene's annotations and predict them from its neighbours; here used only to choose
  the ranker.
- **Matched gene.** A gene with similar mean effect, spread and missing data, used as a null.
- **MRR.** Mean reciprocal rank of the first correct term.
- **N(g), neighbours.** The 25 highest-scoring partners of gene g after exclusions.
- **N1, N2, N3.** Literature classes: function established, partial evidence, none.
- **Orthogonal evidence.** Data independent of DepMap: physical interaction (P), co-abundance (A), localisation (L),
  Perturb-seq (G), structure (S).
- **p_cal.** Calibrated probability that a gene's top GO term will be confirmed with experimental evidence within about
  8 years, given that the gene gains new experimental annotation.
- **Paralogue.** A gene related by duplication (Ensembl); excluded from neighbour lists.
- **Precision@1.** The fraction of genes whose single top term was later received.
- **Prior-only.** A ranking by term frequency alone; a null comparator.
- **R(g), R0.** Split-half reproducibility of a gene's partner list, and its null analogue against matched genes.
- **R1, R2, R3.** Candidate term rankers: summed score, hypergeometric p, matched-gene empirical p. R1 was chosen.
- **Reportable.** A term with at least 2 supporting partners.
- **S(g, t), term score.** Sum of positive zavg_BEF scores of neighbours annotated to term t.
- **S20.** The 20 strongest predictions without a p_cal, judged separately.
- **Same-arm exclusion.** Removal of neighbours on the same chromosome arm, against CRISPR-cutting and copy-number
  artefacts.
- **Scorable.** Has a DepMap profile the tool can score (4,271 of the 4,924 genes).
- **Sign-flip test.** A permutation test of whether real-minus-decoy differences are centred above zero.
- **Simes, Holm.** Methods to combine p-values within a class and to correct across classes.
- **Split halves.** Two random halves of the cell lines, balanced by lineage and screening library.
- **Supporting partner.** A neighbour annotated to the term, with a positive score.
- **Σp_cal.** Sum of p_cal over genes: the expected number of confirmations.
- **Tdark.** The Illuminating the Druggable Genome (IDG) class for proteins with almost no literature or annotation.
- **Temporal hold-out.** Predict from annotations frozen at an earlier date and score against annotations added later.
- **Tier A / B.** Pre-set confidence tiers (p_cal ≥ 0.5 plus orthogonal support / p_cal ≥ 0.3); empty in this study.
- **TPM.** Transcripts per million, a unit of gene expression; log2(TPM+1) is its log scale.
- **Top-K mean zavg.** The mean zavg_BEF of a gene's 25 neighbours; the main calibration covariate.
- **U.** The 4,924 pre-registered uncharacterised genes.
- **V2; V1, V1′.** Prediction vocabulary (GO BP + MF); descriptive module labels (GO complexes; plus Complex Portal and
  MitoCarta).
- **zavg_BEF; z_B, z_E, z_F.** The tool's co-essentiality score, the mean of its three z-scored views (shared neighbours,
  graph embedding, first-order similarity).
