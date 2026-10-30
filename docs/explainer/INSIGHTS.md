# Key insights

**The main point:** for the biologist, most genes that databases call "uncharacterised" are either invisible to
cancer-cell CRISPR screens or already have a published function. Where co-essentiality does say something, it is
specific but rarely the exact answer, and simple homology does far better. For the methodologist, every number that
looked encouraging shrank once someone asked what it was conditional on, or applied the negative control's error rate
back to it.

A ranked half-page summary comes first. Below it, insights are grouped and ranked within each group by how general
and how surprising they are. Each links to
where it arose. "Shown" means measured in this project; "believed" means a likely explanation that was not tested.
Insight labels (Bio-, Meth-, Eng-) are not the project's milestone (M1–M9) or referee-item (M1, S1…) names. Terms are
defined in [JOURNEY.md](JOURNEY.md#words-used-below) and the [METHOD.md glossary](METHOD.md#glossary).

## The insights in half a page

Ranked by how much they should change what a reader does. Details and sources follow below.

**For biologists**
1. **Co-essentiality rarely names the exact function, and homology does far better.** On 809 genes annotated after
   2018, its top GO term was right for 3.0%, against 21.8% for the gene's own electronic/phylogenetic annotations
   ([Bio-1](#ins-bio-1)).
2. **"Uncharacterised" in databases often means "uncurated".** 42% of a random 50 already had a published function
   ([Bio-2](#ins-bio-2)).
3. **Most uncharacterised genes are invisible to CRISPR co-essentiality.** 646 of 4,924 (13%) pass the usable-signal
   rule; at least ~322 (6.5%) carry real signal ([Bio-3](#ins-bio-3)).
4. **The most confident calls are mostly rediscoveries.** 18/40 top predictions were literature-supported, but 31/40
   genes already had a published function and 34/40 had a prior catalogue link ([Bio-4](#ins-bio-4)).

**For methodologists**
1. **Leave-one-out flatters.** Accuracy on known genes was about five times that on genes annotated after 2018 (13.9% vs
   3.0%) ([Meth-1](#ins-meth-1)).
2. **A hold-out of later-annotated genes gives conditional probabilities.** Expected confirmations fell from 30.5 to
   about 4.9 once this was accounted for ([Meth-2](#ins-meth-2)).
3. **Apply the negative control's error rate back to every count.** About 400 of 646 "usable signal" calls were expected
   under the null ([Meth-3](#ins-meth-3)).
4. **Benchmark against the annotation the database already has.** The homology baseline beat co-essentiality sevenfold
   ([Meth-4](#ins-meth-4)).

## 1. Scientific and domain insights

<a id="ins-bio-1"></a>
**Bio-1. On genuinely new annotations, co-essentiality is specific but weak, and homology is far stronger.** *Shown.* For
809 genes annotated after 2018, the top predicted GO term was right for 3.0%, against 0.5% for matched genes. Ranking
the gene's own 2018 electronic/phylogenetic terms gave 21.8%. The signal sits in the strongest-dependency fifth of genes
(11.7%) and in complex membership (18.2%). It is complementary: 15 of its 24 hits were missed by homology. As a
fallback where homology is silent, it adds +0.6 points (21.8% → 22.4%).
→ [TP5](JOURNEY.md#tp-5).

<a id="ins-bio-2"></a>
**Bio-2. "Uncharacterised" in databases often means "uncurated", not "unknown".** *Shown.* In a random 50 of 4,924 genes
with no experimental GO process/function annotation and low annotation or literature counts, 42% (29–56%) already had
an experimentally established function. The rate was 56% for genes that entered through the literature-attention
route (few focused papers or IDG Tdark) without a low UniProt score, against 13% for genes with a low UniProt annotation
score. *Believed:* counting only papers about ≤ 10
genes misses complex subunits characterised in multi-subunit papers (288 of the genes are Complex Portal subunits).
This extends the knownness critiques of Stoeger 2018 (doi:10.1371/journal.pbio.2006643) and Haynes 2018
(doi:10.1038/s41598-018-19333-x) to the definitions used in function-prediction studies.
→ [TP1](JOURNEY.md#tp-1), [TP8](JOURNEY.md#tp-8).

<a id="ins-bio-3"></a>
**Bio-3. Most uncharacterised genes carry no co-essentiality information.** *Shown.* 646 of 4,924 (13%) passed the
reproducibility-plus-expression rule. Non-expressed control genes passed the reproducibility test at 13% (27% with any
dependency), so the 646 assessable calls exceed the null expectation by only about 241. Under an untested assumption,
at least about 322 genes (6.5%) carry real signal. The pipeline still writes flagged predictions for the others, and
about 82% of the summed calibrated probability comes from them (derived for this explainer). Chemosensory/epidermal family genes: 2 of 516.
→ [TP3](JOURNEY.md#tp-3).

<a id="ins-bio-4"></a>
**Bio-4. The most confident co-essentiality calls are mostly rediscoveries.** *Shown.* Blinded judges supported 18 of the
top 40 predictions against 3/120 decoys, but 31 of the 40 genes already had published function. 34/40 had a link with a
top partner in earlier catalogues, and 9 of 10 deep-dive genes had a published co-essential relationship (3 were
explicit Wainberg 2021 predictions, doi:10.1038/s41588-021-00840-z). Of the ten deep-dive genes, only PLEKHH3 (a co-advantage
partner of PTEN and PLEKHA1) had no prior; 6 of the top 40 had no prior in any resource checked. → [TP7](JOURNEY.md#tp-7), [TP8](JOURNEY.md#tp-8).

<a id="ins-bio-5"></a>
**Bio-5. A better co-complex score did not give better function predictions.** *Shown.* zavg_BEF leads GLS by +0.10 in average precision (AP) on
the tool's co-complex benchmark, but on the hold-out it tied GLS (+0.006, CI −0.005 to +0.017) and Pearson (+0.002).
*Believed:* the bottleneck is GO-term assignment and the scarcity of strongly dependent new genes, not pair scoring.
→ [TP5](JOURNEY.md#tp-5).

<a id="ins-bio-6"></a>
**Bio-6. DepMap-derived annotations are rare in GO overall but concentrated in the famous success stories.** *Shown.* Only
1.8% of hold-out targets cite a paper that used DepMap, and removing them moved precision@1 from 0.032 to 0.030. But
they were most of the targets of SLC25A51 (18/19), FIRRM (14/15) and CCDC32 (4/5), so these stories cannot serve as
independent validation. → [TP2](JOURNEY.md#tp-2).

<a id="ins-bio-7"></a>
**Bio-7. Where co-essentiality is strongest, it cannot be calibrated.** *Shown.* Mitochondrial, DNA-repair, ribosome,
nuclear-RNA and centrosome terms each had fewer than 30 hold-out genes, and the strongest signals lay beyond the
hold-out's range. These predictions therefore got no calibrated probability. The uncalibrated top 20 from these families
were supported 19/20 by judges, but all 20 had earlier catalogue links. At the other end, signalling/lineage terms were
right for 0 of 111 hold-out genes. This fits the mitochondrial dominance of co-essentiality signal reported by Rahman
2021 (doi:10.15252/msb.202010013). → [TP6](JOURNEY.md#tp-6).

## 2. Methodological insights

These generalise to other guilt-by-association or function-prediction studies.

<a id="ins-meth-1"></a>
**Meth-1. Leave-one-out accuracy was about five times the accuracy on newly annotated genes.** *Shown.* The same predictor scored precision@1
0.139 on 2,519 known genes with their own annotations hidden, and 0.030 on genes annotated after 2018. A calibration
fitted on the known genes predicted 0.089 on the hold-out, where 0.031 was observed. *Believed:* part of the gap is that
known genes are more essential and better connected (standardised differences of 0.1–0.5 between the two gene sets), as the multifunctionality
argument of Gillis & Pavlidis predicts (2011, doi:10.1371/journal.pone.0017258; 2012, doi:10.1371/journal.pcbi.1002444).
The CAFA-style temporal hold-out (Radivojac 2013, doi:10.1038/nmeth.2340) is the test that matters.
→ [TP2](JOURNEY.md#tp-2), [TP5](JOURNEY.md#tp-5).

<a id="ins-meth-2"></a>
**Meth-2. A hold-out built from genes that later got annotated yields conditional probabilities.** *Shown.* Calibrating on
such genes estimates P(correct | the gene is annotated later). Only 16% of eligible 2018 genes gained annotation, so the
expected number of confirmed predictions fell from 30.5 to about 4.9 once this was accounted for. Any CAFA-style
calibration should state its conditioning. → [TP8](JOURNEY.md#tp-8).

<a id="ins-meth-3"></a>
**Meth-3. Apply the negative control's false-call rate back to every count.** *Shown.* The split-half reproducibility test
was nominally a 5% test but passed 13–27% of non-expressed control genes. Counting assessable genes without subtracting
expected false calls hid that about 400 of the 646 calls were expected under the null alone. → [TP3](JOURNEY.md#tp-3).

<a id="ins-meth-4"></a>
**Meth-4. Benchmark against the annotation the database already has.** *Shown.* The trivial "homology" baseline (rank the
gene's own electronic and phylogenetic GO terms at the start date) beat co-essentiality sevenfold on the hold-out.
*Believed:* curators often confirm experimentally what electronic annotation already suggested, so this baseline is hard
to beat for any new-function predictor. → [TP5](JOURNEY.md#tp-5).

<a id="ins-meth-5"></a>
**Meth-5. Fix the novelty baseline before choosing candidates.** *Shown.* A blind literature screen judged novelty from
papers. Only after ten reports were written did a check against earlier co-essentiality catalogues show that 9 of the 10
genes had a published co-essential link. → [TP8](JOURNEY.md#tp-8).

<a id="ins-meth-6"></a>
**Meth-6. Decoys and a known-gene validation set turn literature support into a test, but the scoring rule is part of the
endpoint.** *Shown.* Three decoys per gene gave an interpretable false-support rate (3/120), and judge validation
(9/10 vs 1/30) showed the judges could discriminate. A rule crediting module-label matches existed only in the judge
prompt. It changed the headline from 16/40 to 18/40, and it helped only real statements, because every supported decoy
was supported on its term. Agreement between two instances of one model (κ 0.975) is not validity.
→ [TP7](JOURNEY.md#tp-7).

<a id="ins-meth-7"></a>
**Meth-7. Validate a check on known positives and decoys before it can promote or demote.** *Shown.* Robustness checks
failed 221 of 269 candidates. The orthogonal-evidence rule supported 32% of real, 28% of matched-gene and 22% of decoy
predictions. Neither had been tried on known positives first, and neither ended up deciding anything.
→ [TP6](JOURNEY.md#tp-6), [appendix](JOURNEY.md#appendix).

<a id="ins-meth-9"></a>
**Meth-9. A ranking from a thin calibration is fragile.** *Shown.* The calibration rested on 24 correct calls. Simpler
post-review models were equally well calibrated but shared only 7–14 of the top 40 genes with the frozen model. Report
the expected count, not a ranked list, as the primary output. → [TP8](JOURNEY.md#tp-8).

## 3. Lower-ranked observations

True and measured, but narrower or less actionable than the ones above.

<a id="ins-bio-8"></a>
**Bio-8. CRISPR co-dependencies of candidate genes rarely replicate in RNAi.** *Shown, with a caveat.* For 182 of 204
measured candidates, the mean correlation with their CRISPR partners in DEMETER2 RNAi data was not above the 95th
percentile of random partner sets. *Believed:* this reflects RNAi noise and partial knockdown as much as CRISPR
artefacts; the check was never run on known positives, so it cannot separate the two. → [TP6](JOURNEY.md#tp-6).

<a id="ins-meth-8"></a>
**Meth-8. Set thresholds and power assumptions from the achievable range.** *Shown.* Tiers required p_cal ≥ 0.5 or 0.3
when the base rate was 3% and the maximum p_cal was 0.141. The power simulation assumed null precision of 0.05–0.15,
where 0.000–0.005 was observed. A dry run of the scoring and calibration on known genes before the freeze would have
shown both. → [TP6](JOURNEY.md#tp-6).

<a id="ins-meth-10"></a>
**Meth-10. The simplest ranker can win and still need guarding.** *Shown.* A summed neighbour score beat hypergeometric and
matched-gene p-values by a pre-declared rule (MRR 0.169 vs 0.140 vs 0.111). But its top terms were broad (median 131
genes), and its top score was tied in 401/820 genes, mostly between a term and its parent. Specify tie-breaks, and
report the most specific term alongside. → [TP4](JOURNEY.md#tp-4).

## 4. Engineering details for reproduction

<a id="ins-eng-1"></a>
**Eng-1. Make "no look" rules mechanisms.** The gene list and design are covered by `preregistration/FREEZE.sha256`;
`src/gate.py::gate.check()` refuses pairwise computation unless the hash and tag match. The tool's precomputed
predictions were hidden by sparse checkout (`scripts/verify_sparse.sh`), and `scripts/audit_order.py` checks that no
pairwise output predates the tag (PASS at all three chronology audits: after the census, after the predictions and at the end). → [TP1](JOURNEY.md#tp-1).

<a id="ins-eng-2"></a>
**Eng-2. Git order is the only proof of "specified before".** The hold-out specification preceded the look by 31 minutes.
But several rows marked "set before computing" were committed in the same commit as, or after, the results they
governed, so their order cannot be shown (see [DISCREPANCIES.md](DISCREPANCIES.md)). Commit specification files
separately, before the run. → [TP5](JOURNEY.md#tp-5).

<a id="ins-eng-3"></a>
**Eng-3. Write an executable spec for every operational detail.** 22 post-freeze deviation entries, about 13 of them
filling unspecified details (tie-breaks, fill order, covariate release, TF list, bootstrap mechanics). See
[DEVIATIONS.md](../../DEVIATIONS.md) and [reviews/retro_M7.md](../../reviews/retro_M7.md) §3.

<a id="ins-eng-4"></a>
**Eng-4. R1 tie-break = ascending GO id.** Descending order changes 393 labels; precision@1 0.032 vs 0.030.
→ [TP4](JOURNEY.md#tp-4).

<a id="ins-eng-5"></a>
**Eng-5. Expressed-gene definition.** The frozen list's `expressed` column predates the lineage-restricted clause in
DESIGN §1.4, giving 635 vs 646 assessable genes. Both are reported. → [TP3](JOURNEY.md#tp-3).

<a id="ins-eng-6"></a>
**Eng-6. One implementation per definition.** A 7-term vs 22-term "generic binding" GO list changed 17 genes in the
uncharacterised list. The independent re-derivation found it, and the 22-term list in `src/knownness.py` is the frozen
one ([preregistration/PROVENANCE.md](../../preregistration/PROVENANCE.md)).

<a id="ins-eng-7"></a>
**Eng-7. Cluster bootstrap fallback.** Linking hold-out genes by shared papers *or* shared neighbours made one cluster of
63.5% of genes; the primary CIs use paper-only clusters (709 clusters; logged before the look)
([results/holdout_eval/SUMMARY.md](../../results/holdout_eval/SUMMARY.md)).

<a id="ins-eng-8"></a>
**Eng-8. Circularity detection depends on full text.** The Europe PMC query searched full text for 71.7% of supporting
papers. No abstract-only paper was flagged, so circularity is a lower bound
([results/holdout/circularity_summary.md](../../results/holdout/circularity_summary.md)).

<a id="ins-eng-9"></a>
**Eng-9. IPI leakage rule.** When scoring gene g, drop protein-interaction annotations (evidence IPI) whose "with/from"
field names g. Otherwise a neighbour's annotation can encode the interaction with g itself
([src/vocab.py](../../src/vocab.py)).

<a id="ins-eng-10"></a>
**Eng-10. Reproduce the tool before using it.** zavg_BEF internal-test average precision (AP) 0.3451 vs published 0.345; GLS and Pearson rows
match the tool to < 3e-7; 14/14 sign and orientation checks
([results/verification/](../../results/verification/)).

<a id="ins-eng-11"></a>
**Eng-11. Literature agents need symbol hygiene.** Searches must cover previous symbols and aliases and exclude
collisions (for example STOML3 alias SRO, GPR152 alias PGR5). Catalogues from 2019 use old symbols: INAFM1 = PRR24,
BICRAL = GLTSCR1L ([docs/AGENT_PROMPTS.md](../AGENT_PROMPTS.md)).

<a id="ins-eng-12"></a>
**Eng-12. Monotone demotions.** Make demotions monotone in iterative fills (once demoted, never re-promoted when the set of
genes over which Benjamini–Hochberg false-discovery control is applied changes), or the fill can cycle
([DEVIATIONS.md](../../DEVIATIONS.md)).

<a id="ins-eng-13"></a>
**Eng-13. Record keeping.** Use git UTC times; agent-written dates in the record are inconsistent (some say 31 October).
Enforce the agent-run log: `results/agent_runs.tsv` has 1 row. Checkpoint before long agent runs: the usage-limit stop
left unreviewed edits (`379827f`).
