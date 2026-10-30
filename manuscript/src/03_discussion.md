
# Discussion

We asked how far co-essentiality can be trusted as a source of function for uncharacterised human genes, under rules
fixed before any network quantity was computed. Three answers emerge. The signal is real and specific: on genes that
were uncharacterised in 2018, the method beat a prior-only predictor and a profile-matched null, and in blinded judging
its top predictions were supported far more often than decoy statements. Its absolute accuracy is low, and its reach is
narrow: one pre-registered gene in eight is assessable, no calibrated probability exceeds 0.141, and transfer from
homology or interaction partners is more accurate. And the most confident predictions point mainly to functions that
are already published but not curated, which says as much about the state of annotation as about the method.

## Co-essentiality as calibrated, complementary evidence

The primary result is modest in size. A precision@1 of 0.030 <!-- src: results/holdout_eval/SUMMARY.md --> means that
about one gene in 33 receives, as its single top term, a term that curators later annotated with experimental evidence.
Accuracy rose steeply with signal strength, to 0.117 <!-- src: results/holdout_eval/fig_signal_quintiles.tsv --> in the
top quintile, and was much higher for complex membership (0.182 <!-- src: results/holdout_eval/SUMMARY.md -->) than for
the broad process terms that dominate GO. Both observations agree with earlier evidence that co-essentiality is
strongest for stable complexes and strong dependencies [Pan2018; Wainberg2021; Rahman2021]. The homology baseline was
seven times more accurate (0.218 <!-- src: results/holdout_eval/SUMMARY.md -->), and module transfer from hu.MAP 3.0
partners also did better (0.049 <!-- src: results/holdout_eval/SUMMARY.md -->), although hu.MAP was built after t0
and was favoured by the comparison. The exploratory union analysis gives the practical reading: co-essentiality was right
for 15 hold-out genes on which homology was wrong, so adding it raised precision from homology's 0.218 to 0.236
<!-- src: results/holdout_eval/exploratory_complementarity.md -->. It is a complementary line of evidence, best weighed
alongside homology and physical interaction data, not a stand-alone annotator.

What the study adds is calibration. The pre-specified logistic model transferred out of fold with slope 0.82 and
c-statistic 0.855 <!-- src: results/holdout_eval/calibration.md -->, so a reported p_cal can be read as a probability
of later confirmation. A model fitted on characterised genes, the usual leave-one-out set-up, overstated that probability
about threefold <!-- src: results/holdout_eval/SUMMARY.md -->. Leave-one-out accuracy on well-annotated genes is
therefore an optimistic guide to performance on genes that are only now being studied, a point that CAFA-style
evaluations have made for other predictors [Radivojac2013; Jiang2016; Zhou2019]. The calibrated catalogue is sobering
but usable: about 30 confirmations are expected among 2,583 calibrated top terms
<!-- src: results/ledger/pcal_summary.json -->, and a reader can see which predictions carry most of that expectation.

## Curation lag is a central finding

Two independent agents, using different gene samples, found that a large share of database-"uncharacterised" genes
already have published functions: 42% (29–56%) of a random sample of the pre-registered list
<!-- src: results/audit/curation_lag_audit.md --> and 69 of 100 candidate and validation genes in the blinded literature
screen <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Among the primary top 40, 31 genes were
N1 <!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv -->, and 16 of the 18 supported predictions were for
N1 genes <!-- src: results/m7/judge/analysis_main.md -->. Our definition of "uncharacterised" combined the absence of
experimental GO evidence with low UniProt annotation or low literature attention, as recommended [Wainberg2021;
Oprea2018], and it still admitted hundreds of genes with established functions. Much of the recent literature that
established those functions dates from 2021 or later <!-- src: results/audit/curation_lag_audit.md -->, so the lag is
partly simple delay; electronic and phylogenetic annotation now covers most human genes [Feuermann2025; Skunca2012], but
experimental curation has not kept pace.

Curation lag shapes how co-essentiality results should be read. Our blinded judging shows that the method's best
predictions recover real, published biology without access to it, a stringent form of validation. But it also means
that a high-ranking prediction for an "uncharacterised" gene is more likely a rediscovery than a discovery, and that
novelty claims require a literature screen first. The closed-book recall probe adds a warning for AI-assisted work: a
language model "recognised" most N1 genes (43 of 59 among candidates <!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->),
so an unblinded model judging its own predictions would have rewarded prior knowledge. Within N1 genes, however, support
still fell with p_cal (16 of 31 in the top 40 against 1 of 11 in extra30
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->), so the ranking reflects the correctness of the
predicted function, not merely the fame of the gene.

## The calibration-support gap

The pre-specified support rule withheld p_cal from every prediction in five machinery families and from the strongest
signals <!-- src: results/ledger/pcal_summary.json -->, because the hold-out held too few such genes to calibrate them.
This is the domain in which co-essentiality is most reliable. The secondary S20 list, defined before any literature step
to avoid misrepresenting the method, made the cost visible: 19 of 20 strong but uncalibrated predictions were supported
<!-- src: results/m7/judge/analysis_main.md -->, nearly all for Commander, complex I and Elongator genes that are N1. The
gap is a property of honest calibration on a small hold-out, not of the method; a larger hold-out, pooled families or a
hierarchical model could close it, at the price of new assumptions that should themselves be pre-specified.

## Context, direction and vocabulary

Two reports show that the "gene functions in module M" vocabulary is too coarse for some of the method's signal.
PLEKHH3 tracks PTEN and PLEKHA1 in fitness *gains* on knockout <!-- src: reports/PLEKHH3.md (§0) -->, which suggests a
brake on PI3K/AKT signalling rather than a requirement for it; a GO-term hit cannot encode that direction. C5orf34's
centriolar co-dependency exists only in TP53-mutant lines <!-- src: reports/C5orf34.md (§5) -->, and the method's
genome-wide summary hides that condition. Context-specific co-dependency is known to carry real information [Chen2023;
Amici2021]; it should become part of the prediction rather than a caveat discovered afterwards. RBM34 illustrates the
converse problem: the module was right, but the term that carried the probability, "transcription elongation", reflects
how its RNA polymerase I partners happen to be annotated <!-- src: reports/RBM34.md (§0) -->.

## Circularity in annotation

Our attempts to use known successes as positive controls largely failed for a reason that matters beyond this study.
For most named controls, the experimental annotations added since 2018 cite DepMap or co-essentiality papers
<!-- src: results/holdout_eval/controls_case_series.tsv -->; 16 of 1,050 supporting PMIDs in the hold-out were flagged
this way <!-- src: results/holdout/circularity_summary.md -->. Integrated interaction resources also embed DepMap
[KimCY2022; Schmid2025], so we treated hu.MAP 3.0, Predictomes, HumanNet and STRING text-mining as non-independent and
reported them only. As co-essentiality-derived annotations
enter GO, future benchmarks that do not track evidence provenance will increasingly reward the method for agreeing with
itself. Excluding flagged evidence made no material difference here (precision@1 0.030–0.032 across sensitivities
<!-- src: results/holdout_eval/SUMMARY.md -->), but the issue will grow.

## What the AI-agent safeguards caught

The study was run by language-model agents, and several safeguards changed the result rather than merely documenting
it. An independent agent re-derived the pre-registered list and the hold-out from raw files and reproduced both exactly,
after an earlier re-derivation had exposed a mismatch between two implementations of the generic-term list (7 versus 22
terms) <!-- src: reviews/retro_M3.md -->. An independent verifier reproduced hit@1 for 809 of 809 hold-out genes
<!-- src: verify/holdout_verification.md --> and found that the design had never specified a tie-break, which affected
401 of 820 genes <!-- src: DEVIATIONS.md -->. The PI overrode an implementing agent's fill of the top 40 that ranked
genes with p_cal near zero above flagged genes with p_cal ≥ 0.06 and retained two genes that carried exclusions
<!-- src: DEVIATIONS.md -->. Red-team review of the ten reports found no fabricated citation but changed every report: it
led to the TP53-stratified refit for C5orf34, exposed an error in the recall-probe answer for TM2D1 (the fly gene
*almondex* is the TM2D3 orthologue), showed that the blinded search for CCDC71L had missed its most relevant paper, and
downgraded the paralogue claim for BICRAL <!-- src: reports/redteam/*.md -->. Blinding held: no packet leaked a gene or
partner name <!-- src: results/m7/judge/leak_check.tsv -->, and the judges were validated on known genes before they saw
any candidate. Of 21 deviations from the frozen design, 12 filled operational details the design had left open
<!-- src: reviews/retro_M7.md -->; a full dry run of the pipeline before the freeze would have prevented most of them.

## Limitations

The study used a single DepMap release (26Q3), on which the tool's hyper-parameters were also set, so we cannot say how
the predictions would change with other releases, other screen libraries or non-cancer cells. GO is incomplete and
lags the literature, so a "miss" on the hold-out is often an annotation not yet made, and p_cal estimates the probability
of curation within about eight years rather than of biological truth. The hold-out genes had stronger signal than U
genes, and reweighting to U lowered precision@1 to 0.012 <!-- src: results/holdout_eval/SUMMARY.md -->. Judging used
two language-model judges and an adjudicator from the same model family as the agents that ran the study; their very
high agreement (κ = 0.975 <!-- src: results/m7/judge/analysis_main.md -->) partly reflects shared training rather than
independent assessment, and no human expert scored the packets. The judging rule credited matches to the module label
as well as to the term; on terms alone the top 40 has 16 rather than 18 supported statements
<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->. The literature agent's search was incomplete in at
least one case (CCDC71L). Orthogonal support separated real from decoy predictions only weakly, and DEMETER2 replication
failed for most genes, a check that was never validated on positive controls. Twenty-one deviations from the frozen
design are logged, three of them interpretations and four real changes or additions (S20, the cluster fallback, the
recall-probe scope and a dropped descriptive stratum) <!-- src: reviews/retro_M7.md -->. Finally, no prediction was tested
at the bench: the reports specify decisive experiments, with matched-essentiality controls and decision rules, but these
remain proposals.

## Future work

Three extensions follow directly. First, repeating the temporal design on later DepMap releases and annotation snapshots
would test whether p_cal remains calibrated and would enlarge the hold-out enough to calibrate the machinery families.
Second, prediction targets should include direction (co-advantage versus co-dependency) and context (lineage, TP53
status), which the reports show carry information that GO terms cannot express. Third, the most decisive next step is
experimental: the seven non-rediscovery reports each name a first experiment and a pre-registered decision rule, and
PLEKHH3, C5orf34 and CCDC71L offer the clearest tests of whether co-essentiality can identify genuinely new functions
rather than recover known ones.
