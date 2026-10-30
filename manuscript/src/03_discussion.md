# Discussion

We asked how far co-essentiality can be trusted as a source of function for uncharacterised human genes, under rules
fixed before any network quantity was computed. Three answers emerge. The signal is real and specific: on genes that
were uncharacterised in 2018, the method beat a profile-matched null (the prior-only arm was degenerate at rank 1), and
in blinded judging its top predictions matched the literature far more often than decoy statements. Its absolute
accuracy is low and its reach is narrow: at most one pre-registered gene in eight is assessable, and once the
reproducibility test's false-call rate is allowed for, the calls exceed the null by one gene in twenty, implying at
least one in fifteen with real signal under an untested assumption; no in-support calibrated probability exceeds
0.141; and transfer from homology or interaction partners is more accurate. And the most confident predictions point
mainly to functions that are already published, and usually already linked by earlier co-essentiality or interaction
catalogues, which says as much about how "uncharacterised" is defined as about the method.

## Co-essentiality as calibrated, complementary evidence

The primary result is modest in size. A precision@1 of 0.030 <!-- src: results/holdout_eval/SUMMARY.md --> means that
about one gene in 33 of the hold-out receives, as its single top term, a term that curators later annotated with
experimental evidence. Reweighted to the covariate distribution of U it is 0.012 <!-- src: results/holdout_eval/SUMMARY.md -->,
about one gene in 83. Accuracy rose steeply with signal strength, to 0.117
<!-- src: results/holdout_eval/fig_signal_quintiles.tsv --> in the top quintile, and was much higher for complex
membership (0.182 <!-- src: results/holdout_eval/SUMMARY.md -->) than for the broad process terms that dominate GO, so the
low headline is partly a property of the pre-registered endpoint. Both observations agree with earlier evidence that
co-essentiality is strongest for stable complexes and strong dependencies [Pan2018; Wainberg2021; Rahman2021]. zavg_BEF
did not differ detectably from GLS or from plain Pearson correlation, so these are statements about co-essentiality, not
about one tool. The homology baseline was seven times more accurate (0.218 <!-- src: results/holdout_eval/SUMMARY.md -->),
and module transfer from hu.MAP 3.0 partners also did better (0.049 <!-- src: results/holdout_eval/SUMMARY.md -->),
although hu.MAP was built after t0 and was favoured by the comparison. Used where homology makes no prediction,
co-essentiality raised precision from 0.218 to 0.224 <!-- src: results/revision/a7_combination_rules.tsv --> [post-review
exploratory]; the oracle union, which credits either method, bounds the gain at 0.236
<!-- src: results/holdout_eval/exploratory_complementarity.md -->. It is a complementary line of evidence, best weighed
alongside homology and physical interaction data, not a stand-alone annotator.

What the study adds is a calibration, with two qualifications. The pre-specified logistic model was not detectably
miscalibrated out of fold (slope 0.82, 95% CI 0.51–1.13; c-statistic 0.855
<!-- src: results/holdout_eval/calibration.md -->), but it rests on 24 events at 3.4 per parameter, its Brier score barely
improves on a constant <!-- src: results/revision/a4_calibration_models.tsv -->, one family coefficient reflects
separation, and simpler models calibrate comparably (S4D Fig), so the data cannot say whether the frozen model is
over-parameterised. And p_cal is conditional: it estimates the chance
that the top term is confirmed if the gene is annotated at all, which happened for about one eligible gene in six over
eight years <!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->. The catalogue's headline of about 30
confirmations among 2,583 calibrated top terms <!-- src: results/ledger/pcal_summary.json --> therefore corresponds to
about five confirmations if the 2018 cohort's annotation rate applies to U
<!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json --> [post-review
exploratory]. A model fitted on characterised
genes, the usual leave-one-out set-up, overstated even the conditional probability about threefold
<!-- src: results/holdout_eval/SUMMARY.md -->. Leave-one-out accuracy on well-annotated genes is therefore an optimistic
guide to performance on genes that are only now being studied, a point that CAFA-style evaluations have made for other
predictors [Radivojac2013; Jiang2016; Zhou2019]. The pre-specified tier thresholds (0.3 and 0.5) could not be reached by
construction with a 3% hit rate and covariates bounded by the hold-out; a design lesson is to set such thresholds from a
pilot of the attainable range, or relative to the base rate.

## Published functions, uncurated or invisible to the definition

Two independent agents, using different gene samples, found that a large share of database-"uncharacterised" genes
already have published functions: 42% (29–56%) of a random sample of the pre-registered list
<!-- src: results/audit/curation_lag_audit.md -->, the only estimate of prevalence, and 59 of the 90 candidate genes in
the blinded literature screen <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->, which were selected on
p_cal or signal and estimate nothing about prevalence. Among the primary top 40, 31 genes were N1
<!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv -->, and 16 of the 18 supported predictions were for
N1 genes <!-- src: results/m7/judge/analysis_main.md -->.

Part of this, and most of it among top candidates, is not slow curation but a property of our definition. U combined the absence of experimental GO process
and function evidence with either a low UniProt annotation score or low focused literature, following Wainberg et al.'s
UniProt criterion [Wainberg2021] only in part. The literature criterion counted papers about at most ten genes and the
GO criterion ignored cellular component, so genes studied mainly in multi-gene papers entered U: 3,819 genes came in
through the literature criterion alone <!-- src: results/revision/a1_flag_counts.tsv -->. In the random sample, 56% of
such literature-route genes were N1 against 13% of genes with a low UniProt score
<!-- src: results/revision/a1_N1_rates_by_route_and_flag.tsv -->. There, 13 of the 21 N1 genes rest on evidence from 2021
or later, which is curation lag in the usual sense; of the 8 with older evidence, 6 carry a definition-artefact flag,
mostly a UniProt score of 5, and none is a Complex Portal subunit <!-- src: results/revision/a1_U_entry_flags.tsv -->.
Among the top 40, by contrast, 30 genes carry a flag and 13 are Complex Portal subunits
<!-- src: results/revision/a1_flag_counts.tsv -->, so complex membership matters mainly for the selected candidates.
Electronic and phylogenetic
annotation now covers most human genes [Feuermann2025], although its reliability varies by evidence source
[Skunca2012], and experimental curation lags. A stricter definition (UniProt score ≤ 2, or exclusion of genes with
experimental cellular-component or Complex Portal membership) would have given a smaller and more genuinely
uncharacterised list, at the cost of some genes that are truly unstudied.

This shapes how co-essentiality results should be read. Blinded literature concordance shows that the method's best
predictions recover real, published biology without access to it. But a high-ranking prediction for an
"uncharacterised" gene is more likely a rediscovery than a discovery, and most of our top predictions had been anticipated:
34 of the top 40 genes had a co-essential or physical link in earlier catalogues, and Wainberg et al. had already
predicted functions for three of our report genes <!-- src: results/revision/a2_novelty_overlap.tsv -->. Novelty claims
therefore require both a literature screen and a catalogue check first. The closed-book recall probe adds a warning for
AI-assisted work: a language model "recognised" most N1 genes (43 of 59 among candidates
<!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->), so an unblinded model judging its own predictions
would have rewarded prior knowledge. Within N1 genes, support was higher in the top 40 than in extra30 (16 of 31 against
1 of 11 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->), which suggests that the ranking reflects
the correctness of the predicted function and not only the fame of the gene; this rests on one exploratory test with 11
N1 genes in extra30 and should be confirmed.

## The calibration-support gap

The pre-specified support rule withheld p_cal from every prediction in five machinery families and from the strongest
signals <!-- src: results/ledger/pcal_summary.json -->, because the hold-out held too few such genes to calibrate them.
This is the domain in which co-essentiality is most reliable. The secondary S20 list, defined before any literature step
to avoid misrepresenting the method, made the cost visible: 19 of 20 strong but uncalibrated predictions were supported
<!-- src: results/m7/judge/analysis_main.md -->, nearly all for Commander, complex I and Elongator genes that are N1 and
already in earlier catalogues. The gap is a property of honest calibration on a small hold-out, not of the method; a
larger hold-out, pooled families or a hierarchical model could close it, at the price of new assumptions that should
themselves be pre-specified.

## Context, direction, vocabulary and circularity

Two reports show that the "gene functions in module M" vocabulary is too coarse for some of the method's signal.
PLEKHH3 tracks PTEN and PLEKHA1 in fitness *gains* on knockout <!-- src: reports/PLEKHH3.md (§0) -->, which suggests a
brake on PI3K/AKT signalling rather than a requirement for it; a GO-term hit cannot encode that direction, and PLEKHH3 is
the one report gene without a precedent in the catalogues we checked. C5orf34's centriolar co-dependency exists only in
TP53-mutant lines <!-- src: reports/C5orf34.md (§5) -->, and the method's genome-wide summary hides that condition.
Context-specific co-dependency is known to carry real information [Chen2023; Amici2021]; it should become part of the
prediction rather than a caveat discovered afterwards. RBM34 illustrates the converse problem: the module was right, but
the term that carried the probability, "transcription elongation", reflects how its RNA polymerase I partners happen to
be annotated <!-- src: reports/RBM34.md (§0) -->. The named controls INTS15 and TMEM41B fail for a related reason: their
networks were right, but the terms curators later added were not carried by their neighbours at t0
<!-- src: results/revision/a8_control_target_reasons.tsv -->.

Annotation also feeds back on itself. For most named controls the experimental annotations added since 2018 cite DepMap
or co-essentiality papers <!-- src: results/holdout_eval/controls_case_series.tsv -->, and 16 of 1,050 supporting PMIDs
in the hold-out were flagged this way <!-- src: results/holdout/circularity_summary.md -->. Integrated interaction
resources also embed DepMap [KimCY2022; Schmid2025], so hu.MAP 3.0, Predictomes and STRING text-mining were not used as
independent support. Excluding flagged evidence made no material difference here (precision@1 0.030–0.032 across
sensitivities <!-- src: results/holdout_eval/SUMMARY.md -->), but as co-essentiality-derived annotations enter GO,
benchmarks that do not track evidence provenance will increasingly reward the method for agreeing with itself.

## What the AI-agent safeguards caught, and what they did not

Several safeguards changed the result rather than merely documenting it. Independent re-derivation of the
pre-registered list exposed a mismatch between two implementations of the generic-term list (7 versus 22 terms)
<!-- src: reviews/retro_M3.md -->; an independent verifier reproduced hit@1 for 809 of 809 hold-out genes
<!-- src: verify/holdout_verification.md --> and found an unspecified tie-break affecting 401 of 820 genes
<!-- src: DEVIATIONS.md -->; the PI overrode a top-40 fill that ranked genes with p_cal near zero above flagged genes
with p_cal ≥ 0.06 <!-- src: DEVIATIONS.md -->; and red-team review changed every report, prompting the TP53-stratified
refit for C5orf34 and downgrading the paralogue claim for BICRAL
<!-- src: reports/redteam/BICRAL.md; reports/redteam/C5orf34.md -->. No packet leaked a gene or partner name
<!-- src: results/m7/judge/leak_check.tsv -->. The gaps were exposed by peer review: the module-label crediting rule and
three other deviations were logged only after the results they affect existed, the agent-run log is sparse, the
role-scope file is a template, and the agents' novelty statements had not been checked against earlier catalogues. Of
22 logged deviations, 13 filled operational details the design had left open <!-- src: DEVIATIONS.md -->; a full dry
run of the pipeline before the freeze would have prevented most of them.

## Limitations

The study used a single DepMap release (26Q3), on which the tool's hyper-parameters were also set, so we cannot say how
the predictions would change with other releases, other screen libraries or non-cancer cells. The tool was tuned on hu.MAP
3.0 co-complex pairs, which post-date t0; parity with untuned Pearson correlation suggests this did not help it on H.
GO is incomplete and lags the literature, so a "miss" on the hold-out is often an annotation not yet made, and p_cal
estimates the probability of curation, given that curation occurs, within about eight years, rather than of biological
truth. The hold-out genes had stronger signal than U genes, and reweighting to U lowered precision@1 to 0.012
<!-- src: results/holdout_eval/SUMMARY.md -->. Confidence intervals use PMID-only clusters; complex-mates in H that share
no paper are treated as independent, and we did not run a leave-one-module-out sensitivity on H. Judging used two
instances of one language model and an adjudicator from the same model family as the agents that ran the study; their
very high agreement (κ = 0.975 <!-- src: results/m7/judge/analysis_main.md -->) reflects shared training and shared
evidence rather than independent assessment, all evidence came from a single retrieval agent, the decoys were other
genes' terms rather than the gene's own alternatives, and no human expert scored the packets. The judging rule credited
matches to the module label as well as to the term; on terms alone the top 40 has 16 rather than 18 supported
statements <!-- src: results/revision/a5_judging_sensitivity.tsv -->. The literature agent's search was incomplete in at
least one case (CCDC71L). The novelty check covered the catalogues we could obtain; Pan et al., FIREWORKS and the
Perturb-seq clusters were not checked. Orthogonal support separated real from decoy predictions only weakly, and DEMETER2
replication failed for most genes, a check that was never validated on positive controls. The DepMap-only controls for
the two most novel report observations (lineage-adjusted and PTEN-null-excluded correlations for PLEKHH3; centriole-module
coherence in TP53-wild-type lines for C5orf34) were not run. Twenty-two deviations from
the frozen design are logged <!-- src: DEVIATIONS.md -->. Finally, no prediction was tested at the bench: the reports
specify decisive experiments, with matched-essentiality controls and decision rules, but these remain proposals.

## Future work

Four extensions follow directly. First, repeating the temporal design on later DepMap releases and annotation snapshots
would test whether p_cal remains calibrated and would enlarge the hold-out enough to calibrate the machinery families;
the same design applies unchanged to Perturb-seq, interaction maps and AlphaFold-based predictors, and a joint evaluation
would show what each adds to homology. Second, prediction targets should include direction (co-advantage versus
co-dependency) and context (lineage, TP53 status), which the reports show carry information that GO terms cannot
express. Third, definitions of "uncharacterised" should exclude genes with experimental cellular-component or curated
complex membership, or report them separately. Fourth, the most decisive next step is experimental: the reports each name
a first experiment and a pre-registered decision rule, and PLEKHH3, the only report gene without precedent, together
with the TP53 condition for C5orf34, offers the clearest test, once the DepMap-only controls above have been run, of whether co-essentiality can identify genuinely new
functions rather than recover known ones.
