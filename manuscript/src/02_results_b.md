
## C4: blinded literature concordance supports the top predictions, mostly as rediscovery of published function

**Candidate sets.** Four gene sets entered the literature step (Fig 5A). The primary set is the top 40 by p_cal. Two
sets are secondary. S20 holds the 20 strongest predictions that have no p_cal, because their family has fewer than 30 H
genes or their signal exceeds H's 95th percentile <!-- src: results/m7/s20.tsv -->; it was defined after the U
predictions but before any literature step, and is analysed separately [deviation]. Extra30 holds 30 further genes from
the fill pool, six in each p_cal quintile (p_cal 6 × 10⁻⁸ to 0.099) <!-- src: results/m7/extra30.tsv -->
[pre-specified secondary]. The fourth set, 10 H genes whose "real" statement is a known current target term, served only
to validate the judges <!-- src: results/m7/hval10.tsv --> [pre-specified]. Judged statements contained the predicted GO
term and the descriptive module label only; the relationship type was dropped for every statement, because types
existed for none of the decoy donors and would have marked the real slot [deviation]. This makes statements less
falsifiable and easier to support. The judge instruction also credited a match to "the stated process or module",
so a match to the module label alone counted as support; this operationalisation was not logged before judging and was
entered in DEVIATIONS.md retrospectively [deviation, logged after the result], so we report term-only results beside
the primary ones.

**Closed-book recall probe [pre-specified; extended to S20 and extra30].** Before any agent saw network output for
these genes, a fresh language model without tools stated what it knew of each gene from its symbol and aliases. It
"recognised" 52 of the 90 <!-- src: results/m7/recall_probe_90.tsv --> candidates: 22 of 40 in the top 40, 19 of 20 in
S20 and 11 of 30 in extra30 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Recognition followed
the literature class assigned later by the literature agent L (Fig 5D): 43 of 59 N1, 8 of 24 N2 and 1 of 7 N3
candidates <!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->, as in the random 50 U genes (18 of 21 N1,
3 of 13 N2 and 3 of 16 N3 <!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->). A language model
therefore already knows most published-but-uncurated functions. This is why the judges saw only evidence that agent L
had retrieved, under a redacted gene name, and were told not to use their own knowledge.

**Blind literature screen: curation lag among candidates [pre-specified; extended].** Agent L had no access to
co-essentiality output or to our predictions. For the 100 genes it recorded 887 evidence items, each with a verbatim
span; 518 were focused functional studies and 4 were flagged as DepMap-derived
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Among the 90 U candidates, 59 were N1 (direct
functional evidence), 24 N2 (partial) and 7 N3 (none) <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->.
In the primary top 40 the split was 31 N1, 7 N2 and 2 N3; in S20 17 N1 and 3 N2; and in extra30 11 N1, 14 N2 and 5 N3
<!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv --> (Fig 5C). Including the 10 H validation genes, all
N1 as expected <!-- src: results/m7/judge/analysis_hval_genes.tsv -->, agent L classed 69 of 100 genes as N1
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->; the 10 H genes are N1 by construction, so the
relevant count is 59 of the 90 U candidates
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->, which were selected on p_cal or signal and therefore do not estimate a
prevalence. For comparison, the random 50 U genes had 21 N1,
13 N2 and 16 N3 <!-- src: results/audit/curation_lag_audit.md --> (a different auditor; descriptive comparison). Our
highest-ranked predictions are thus concentrated in genes whose function is already published but not yet in GO
experimental annotation: 78% of the top 40 and 85% of S20 <!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv -->.
[Post-review exploratory] The definition artefacts described under C1 are concentrated here: 37 of the top 40 and all
20 S20 genes entered U through the literature criterion alone, and 30 of the top 40 and all of S20 carry a
definition-artefact flag (13 and 17 are Complex Portal subunits) <!-- src: results/revision/a1_flag_counts.tsv -->.
Across the 90 candidates, 58 of 80 D3-only genes were N1 against 1 of 10 genes with a low UniProt score
<!-- src: results/revision/a1_N1_rates_by_route_and_flag.tsv -->.

**Judge validation [pre-specified].** On the 10 H genes, adjudicated scores supported 9 of 10 real statements and 1 of
30 decoys <!-- src: results/m7/judge/analysis_hval.md -->, meeting the acceptance rule (at least 7 of 10 real, at most 3
of 30 decoys) at the first attempt. Between-instance agreement of the two judges was κ = 0.931 over 40 statements, with one
disagreement <!-- src: results/m7/judge/analysis_hval.md -->, which the adjudicator resolved as supported; it is the
single supported decoy <!-- src: results/m7/judge/scores/ADJ_hval.tsv -->.

**Primary blinded test: top 40 [pre-specified; scoring operationalised, see above].** Each gene's packet held the real statement and three decoys in random
order; the decoys were top terms of other U genes, matched on family and term size
<!-- src: results/m7/answer_key_slots.tsv -->. Judges supported 18 of 40 real statements (45%, Wilson 95% CI 31–60%),
left 20 unaddressed and scored 2 as contradicted <!-- src: results/m7/judge/analysis_main.md -->
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. They supported 3 of 120 decoys (2.5%)
<!-- src: results/m7/judge/analysis_main.md -->. The mean of real minus mean decoy score was 0.375; with 20 non-zero
differences, the exact one-sided sign-flip p was 2.2 × 10⁻⁴ <!-- src: results/m7/judge/analysis_main.md -->, so the
primary test passes (Fig 5A). [Post-review exploratory] Counting support for the GO term only, which is what p_cal
estimates, 16 of 40 real statements were supported (sign-flip p = 7.1 × 10⁻⁴); all six supported decoys across the
sets were supported on the term <!-- src: results/revision/a5_judging_sensitivity.tsv; results/revision/a5_plus1_basis.tsv -->,
so module crediting helped only real statements. An exact slot-permutation test, which uses the exchangeability of
slots directly, gave p = 2.3 × 10⁻⁷ (term-only 2.6 × 10⁻⁶), and averaging the differences within clusters of genes that
share a module label, because complex-mates share literature, gave p = 0.0022 over 17 non-zero clusters (term-only
0.0058) <!-- src: results/revision/a5_judging_sensitivity.tsv -->. The conclusion does not depend on module crediting
or on gene-level independence. The test is nonetheless easy: decoys are other genes' terms, so for a gene with
literature the real statement can win on topic alone; within-gene decoys (the gene's own lower-ranked terms) would test
whether the *top* prediction is preferred, and were not run. The two contradicted statements, for the N1 genes TLNRD1 and KDF1
<!-- src: results/m7/judge/analysis_main_genes.tsv -->, failed on direction: TLNRD1 promotes rather than inhibits cell
migration, and KDF1 inhibits rather than activates NF-κB signalling
<!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv, J2_main2.tsv, J2_main3.tsv, ADJ_main2.tsv, ADJ_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->. Support
fell with rank: 12 of 20 for ranks 1–20 (p_cal 0.055–0.141) and 6 of 20 for ranks 21–40 (p_cal 0.036–0.050)
<!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv --> (Fig 5B).

**Secondary sets [S20: deviation; extra30: pre-specified].** These sets were analysed separately and never pooled with
the primary test. In S20, judges supported 19 of 20 real statements and 2 of 60 decoys (sign-flip p = 1.9 × 10⁻⁶)
<!-- src: results/m7/judge/analysis_main.md -->; 15 of the 20 carry a Commander, complex I/OXPHOS or Elongator module
label <!-- src: results/m7/s20.tsv --> (Table 2), the well-established machinery modules that the calibration support
rule excludes. In extra30, judges supported 1 of 30 real statements and 1 of 90 decoys (p = 0.5)
<!-- src: results/m7/judge/analysis_main.md -->; support was 0 of 6 in each of the four lowest p_cal quintiles and 1 of 6
in the highest <!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv -->. Literature support therefore rose
with p_cal across the fill pool (Fig 5B): 18 of 40 in the top 40 against 1 of 30 in extra30 (one-sided Fisher p = 5.6 ×
10⁻⁵) [exploratory; post hoc, unadjusted] <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. The
two extra30 genes whose p_cal exceeds the top-40 minimum, MARF1 (0.099, contradiction) and TMEM60 (0.037, built-in
artefact exclusion), were excluded from the top 40 <!-- src: results/m7/extra30.tsv -->, which is why the highest
extra30 bin overlaps the top-40 range. Literature support is a different and more lenient endpoint than p_cal, which
estimates curation of the exact GO term with experimental evidence: the 18 (or 16) supported statements sit beside a
summed p_cal of 2.50 for the top 40 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->, or about 0.4
unconditionally <!-- src: results/revision/a3_annotation_gain_rates.tsv; results/revision/numbers_a3.json -->. The gap measures how much more often
"the literature reports the gene in this process or module" holds than "curators annotate this exact term".

**Support by novelty class [pre-specified reporting].** The support is mostly rediscovery. In the top 40, judges
supported 16 of 31 N1, 2 of 7 N2 and 0 of 2 N3 genes <!-- src: results/m7/judge/analysis_main.md --> (Fig 5C); in S20,
17 of 17 N1 and 2 of 3 N2 genes <!-- src: results/m7/judge/analysis_main.md -->. Of the 37 supported top-40 and S20
genes, 33 are N1, and the recall probe recognised 35 <!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->.
Among N1 genes, whose function is published, the predicted function matched the published one for 16 of 31 in the top
40 and 1 of 11 in extra30 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. This is a direct,
curation-independent estimate of accuracy among genes with literature (52% in the top 40
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->), with the caveat that literature concordance is
lenient. The contrast (one-sided Fisher p = 0.014 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->)
[exploratory; post hoc, unadjusted, with only 11 N1 genes in extra30] suggests that higher-ranked predictions match published function more often, and not only because
their genes are better studied, but it rests on one uncorrected test. [Post-review exploratory] In the top 40, judged
support was 17 of 30 for genes with a definition-artefact flag and 1 of 10 for genes without
<!-- src: results/revision/a1_judged_support_by_flag.tsv -->, so the judged successes are concentrated among complex
subunits and other genes with published function that the definition missed. Only four supported
genes are N2: TRAPPC5 and BICRAL in the top 40, NDUFB2 and MED9 in S20
<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->. No N3 prediction could be checked against the
literature by construction, and the top 40 contains only 2 N3 genes.

**Agreement and adjudication [pre-specified].** Over the 360 main statements the two judges, two instances of the same
model (Claude Sonnet 5.5; adjudicator Claude Opus 5.5; docs/AGENT_PROMPTS.md), agreed with κ = 0.975, with 2
disagreements and none left unresolved <!-- src: results/m7/judge/analysis_main.md -->. This is between-instance
reproducibility, not validity: the judges read identical evidence tables under one rubric and scored most statements
0. Validity rests on the validation set (9 of 10 real, 1 of 30 decoys <!-- src: results/m7/judge/analysis_hval.md -->) and
the low decoy support rate. Both disagreements involved real
statements, for WDR7 (S20) and DPCD (top 40); the adjudicator resolved both as supported because the evidence matched
the module label, not the GO term <!-- src: results/m7/judge/scores/ADJ_main2.tsv -->
<!-- src: results/m7/judge/scores/ADJ_main3.tsv -->. The judging rule credits a match to "the stated process or module"
<!-- src: scripts/51_judge_packets.py --> and applied equally to decoys. Still, three supported real statements rest on
the module label alone: YPEL5 (GID/CTLH complex; Wnt not shown), DPCD (R2TP/PAQosome; transcription elongation not
shown) and WDR7 (V-ATPase/RAVE; iron homeostasis not shown)
<!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv, J2_main2.tsv, J2_main3.tsv, ADJ_main2.tsv, ADJ_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->, and for
DDX19A, support for "cell population proliferation" came from cancer cell-line proliferation studies. Counting only
term-level support, the top 40 has 16 supported real statements
<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv; results/revision/a5_judging_sensitivity.tsv --> (see
above). The judges' packets contained no
gene-symbol or partner-name leaks <!-- src: results/m7/judge/leak_check.tsv -->.

**Overlap with earlier catalogues [post-review exploratory].** The reports compared their predictions with published
catalogues only as "agreement", so we quantified, for each candidate, whether the relationship between the gene and at
least one of its ten strongest partners had already been published (S9 Table; S4B Fig). Of the primary top 40, 17 share
a hu.MAP 3.0 complex with a top-10 partner, 20 have a Predictomes AlphaFold pair (SPOC ≥ 0.5), 19 have a significant GLS
pair and 22 share a tight module in the 2021 co-essentiality atlas [Wainberg2021], and 9 have an edge or cluster in the
2019 network [Kim2019] <!-- src: results/revision/a2_novelty_overlap.tsv; manuscript/figures/source_data/FigS4_derived_numbers.tsv -->.
Overall, 27 of the top 40 have a prior in a co-essentiality catalogue and 34 in any resource we obtained; only 6
(PLEKHH3, LGALS9B, FBXL18, SASH3, DDX19A and DPCD) have none <!-- src: results/revision/a2_novelty_overlap.tsv -->. All
20 S20 genes have a prior <!-- src: results/revision/a2_novelty_overlap.tsv -->. Wainberg et al. listed explicit function
predictions for three of our top-40 genes, CCDC71L, C5orf34 and INAFM1 <!-- src: results/revision/a2_novelty_overlap.tsv -->,
all of which became candidate reports. These flags record that the co-essential or physical link was published, not that
the same function was assigned; Pan et al. [Pan2018], FIREWORKS [Amici2021] and Perturb-seq clusters [Replogle2022]
could not be checked because no machine-readable gene-level table was obtainable. The counts are therefore lower bounds on
prior knowledge.

**Table 2. Top-40 and S20 predictions judged supported by the literature (blinded, adjudicated).**

| Set, rank | Gene | Predicted GO term | Module label | p_cal | zavg | UniProt score; CP | L class | Probe | Basis |
|---|---|---|---|---|---|---|---|---|---|
| top 40, 1 | ANKRD52 | regulatory ncRNA-mediated gene silencing | RISC complex | 0.141 | – | 3; – | N1 | yes | term |
| top 40, 3 | CNOT10 | regulation of RNA stability | CCR4-NOT deadenylase complex | 0.116 | – | 5; CP | N1 | yes | term |
| top 40, 4 | TRAPPC5 | Golgi vesicle transport | TRAPP III complex | 0.114 | – | 4; CP | N2 | yes | term |
| top 40, 6 | SSR4 | protein N-linked glycosylation | ER protein-containing complex | 0.091 | – | 5; CP | N1 | yes | term |
| top 40, 7 | CNOT11 | regulation of RNA stability | CCR4-NOT deadenylase complex | 0.080 | – | 4; CP | N1 | yes | term |
| top 40, 8 | MED31 | DNA-templated transcription initiation | RNA Pol II transcription regulator complex | 0.079 | – | 5; CP | N1 | yes | term |
| top 40, 9 | YPEL5 | positive regulation of Wnt signaling pathway | GID E3 ubiquitin ligase complex | 0.078 | – | 5; CP | N1 | yes | module |
| top 40, 10 | TMEM208 | establishment of protein localization to membrane | ER protein-containing complex | 0.078 | – | 5; – | N1 | yes | term |
| top 40, 11 | PHC3 | epigenetic regulation of gene expression | PcG protein complex | 0.077 | – | 5; CP | N1 | yes | term |
| top 40, 15 | TMED7 | Golgi vesicle transport | cytoplasmic ubiquitin ligase complex | 0.064 | – | 5; – | N1 | yes | term |
| top 40, 18 | MGA | epigenetic regulation of gene expression | chromatin silencing complex | 0.059 | – | 5; CP | N1 | yes | term |
| top 40, 20 | TMEM209 | nucleus organization | nuclear pore complex | 0.055 | – | 5; – | N1 | no | term |
| top 40, 26 | PSMD13 | regulation of proteasomal protein catabolic process | proteasome complex | 0.047 | – | 5; CP | N1 | yes | term |
| top 40, 27 | COA4 | cytochrome complex assembly | MitoCarta: OXPHOS | 0.046 | – | 4; – | N1 | yes | term |
| top 40, 30 | GRIPAP1 | vesicle-mediated transport to the plasma membrane | vesicle tethering complex | 0.044 | – | 5; – | N1 | yes | term |
| top 40, 33 | BICRAL | transcription coregulator binding | GBAF (SWI/SNF) complex | 0.041 | – | 5; CP | N2 | yes | term |
| top 40, 38 | DDX19A | cell population proliferation | ER protein-containing complex | 0.036 | – | 5; – | N1 | yes | term (generic) |
| top 40, 40 | DPCD | DNA-templated transcription elongation | PAQosome co-chaperone complex | 0.036 | – | 3; – | N1 | no | module (adjudicated) |
| S20, 1 | COMMD3 | endosomal transport | Commander complex | – | 18.5 | 5; CP | N1 | yes | term |
| S20, 2 | COMMD2 | endosomal transport | Commander complex | – | 17.0 | 5; CP | N1 | yes | term |
| S20, 3 | NDUFB10 | NADH dehydrogenase activity | MitoCarta: OXPHOS | – | 16.7 | 5; CP | N1 | yes | term |
| S20, 4 | COMMD4 | endosomal transport | Commander complex | – | 16.4 | 5; CP | N1 | yes | term |
| S20, 5 | NDUFB2 | NADH dehydrogenase activity | respiratory chain complex I | – | 16.3 | 4; CP | N2 | yes | term |
| S20, 6 | NDUFA2 | NADH dehydrogenase activity | respiratory chain complex I | – | 16.3 | 5; CP | N1 | yes | term |
| S20, 7 | COMMD8 | endosomal transport | Commander complex | – | 16.3 | 5; CP | N1 | yes | term |
| S20, 8 | TADA2B | acyltransferase activity (non-amino-acyl groups) | SAGA complex, KAT2A variant | – | 16.2 | 5; CP | N1 | yes | term |
| S20, 9 | NDUFA11 | NADH dehydrogenase activity | MitoCarta: OXPHOS | – | 16.0 | 5; CP | N1 | yes | term |
| S20, 10 | COMMD10 | endosomal transport | Commander complex | – | 15.9 | 5; CP | N1 | yes | term |
| S20, 11 | WDR7 | intracellular iron ion homeostasis | proton-transporting two-sector ATPase complex | – | 15.8 | 3; CP | N1 | yes | module (adjudicated) |
| S20, 12 | WASHC3 | endosomal transport | Commander complex | – | 15.6 | 5; CP | N1 | yes | term |
| S20, 14 | CTU2 | tRNA metabolic process | Elongator holoenzyme complex | – | 15.5 | 5; – | N1 | yes | term |
| S20, 15 | NDUFB4 | NADH dehydrogenase activity | MitoCarta: OXPHOS | – | 15.5 | 4; CP | N1 | yes | term |
| S20, 16 | ELP5 | tRNA metabolic process | Elongator holoenzyme complex | – | 15.2 | 5; CP | N1 | yes | term |
| S20, 17 | ELP6 | tRNA metabolic process | Elongator holoenzyme complex | – | 15.0 | 5; CP | N1 | yes | term |
| S20, 18 | UNC50 | Golgi organization | vesicle tethering complex | – | 14.9 | 5; – | N1 | yes | term |
| S20, 19 | MED9 | regulation of transcription initiation by RNA Pol II | RNA Pol II transcription regulator complex | – | 14.8 | 4; CP | N2 | yes | term |
| S20, 20 | NUP43 | nucleocytoplasmic transport | nuclear pore complex | – | 14.8 | 5; CP | N1 | yes | term |

<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv (scripts/61_figure5.py: analysis_main_genes.tsv,
answer_key_slots.tsv, top40_primary.tsv, s20.tsv, L/index_batch_*.tsv, recall_probe_90.tsv); Basis column read from the
judges' justifications in results/m7/judge/scores/J1_main*.tsv, J2_main*.tsv and ADJ_main*.tsv. Complex labels
shortened (full names in the source TSV). UniProt
annotation score and Complex Portal subunit (CP) from results/revision/a1_U_entry_flags.tsv [post-review]. -->

Unsupported top-40 genes: 20 unaddressed and 2 contradicted (TLNRD1, KDF1); in S20, NR2C2AP was unaddressed
<!-- src: results/m7/judge/analysis_main_genes.tsv -->.

## Ten candidate reports: three rediscoveries, one partial rediscovery and five independent hypotheses

The ten report genes were fixed before any judging result existed <!-- src: results/m7/report_selection.md -->: the
nine highest-ranked N2 and N3 genes of the primary top 40 and one N1 rediscovery exemplar, ANKRD52, the top-ranked gene
overall. Each report was written from a machine-generated evidence bundle, attacked by an independent red-team agent,
and revised (S1–S10 Reports). All ten red-team verdicts were "accept with revisions"
<!-- src: reports/redteam/ANKRD52.md; reports/redteam/TRAPPC5.md; reports/redteam/RBM34.md; reports/redteam/PLEKHH3.md; reports/redteam/CCDC71L.md; reports/redteam/TM2D2.md; reports/redteam/TM2D1.md; reports/redteam/C5orf34.md; reports/redteam/BICRAL.md; reports/redteam/INAFM1.md -->.
No fabricated citation was found among roughly 300 verbatim evidence spans checked
<!-- src: RESEARCH_TREE.md (M7b status summary); reviews/retro_M7.md -->, but every review found numeric or framing
problems that changed the reports. After peer review, each report gained a statement of what earlier catalogues had
already published [post-review]: nine of the ten genes had a prior co-essential or physical link, and only PLEKHH3 had
none <!-- src: results/revision/a2_novelty_overlap.tsv -->. Table 3 summarises the outcome; S10 Table gives the decisive
experiments. Three points stand out.

First, three reports are rediscoveries in which co-essentiality recovered published biology blind, and one is a partial
rediscovery. ANKRD52 is the regulatory subunit of the phosphatase PP6, which dephosphorylates Argonaute 2 to sustain
microRNA silencing [Golden2017]; its co-essentiality neighbourhood is the miRNA biogenesis and silencing machinery
(AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8) with PPP6C further down <!-- src: reports/ANKRD52.md (§4) -->, and the
AGO2–ANKRD52 co-dependency in DepMap had itself been reported (Fig S5C of [Shui2023]). Because AGO2 loss is near-neutral
while ANKRD52 loss is not, and PP6 has other substrates, the prior favours failure of the proposed AGO2 phospho-mutant
rescue of fitness. BICRAL's two strongest partners, SMARCD1 and BRD9, are the defining subunits of the non-canonical BAF
(GBAF/ncBAF) complex in which it was placed biochemically in 2018 [Alpsoy2018]; an earlier draft's "paralogue-specific
requirement" was downgraded after red-team review because the paralogue BICRA tracks the same axis about twice as
strongly (r 0.53 versus 0.27) <!-- src: reports/BICRAL.md (§0) -->. TRAPPC5 is a known TRAPP core subunit; the only
unrecorded element, a dependency that follows the TRAPPIII arm (TRAPPC8/11/12/13), is one-sided because the
TRAPPII-specific subunits have no recoverable co-essentiality structure <!-- src: reports/TRAPPC5.md (§0, §4) -->, and we
have not tested whether the other core subunits (TRAPPC1/3/4) share the same leaning, in which case it would be a
property of TRAPP in cancer lines rather than of TRAPPC5. RBM34 is the partial rediscovery: its partners are RNA
polymerase I subunits and large-subunit pre-rRNA assembly factors, consistent with its yeast orthologue Nop12, a 60S
maturation factor [Talkish2014], and Wainberg et al. had placed it in a pre-ribosome module
<!-- src: results/revision/a2_novelty_overlap.tsv -->, while the predicted term "DNA-templated transcription elongation"
is an artefact of the vocabulary — the Pol I subunits carry the elongation annotation <!-- src: reports/RBM34.md (§0) -->.

Second, the five remaining hypotheses (TM2D1 and TM2D2 count as one) differ in novelty. Only PLEKHH3 has no precedent in
any catalogue we checked <!-- src: results/revision/a2_novelty_overlap.tsv -->, and it rests on a fitness co-advantage
rather than on shared essentiality. PLEKHH3's two strongest correlates among all 18,433 genes are PLEKHA1 (TAPP1) and
PTEN (r = 0.424 and 0.400), followed by TSC2, TSC1 and DDIT4, while the pathway's accelerator PIK3CA runs the other way
(r = −0.186) <!-- src: reports/PLEKHH3.md (§0) -->. PTEN and PLEKHA1, like PLEKHH3 itself, are genes whose loss helps
cells grow (mean Chronos effects +0.377, +0.219 and +0.087) <!-- src: reports/PLEKHH3.md (§0, §3) -->. The two partners
are themselves correlated (r 0.453), but each keeps a partial correlation with PLEKHH3 given the other (0.257 and
0.298), and the co-dependency is absent in lymphoid lines <!-- src: reports/PLEKHH3.md (§0) -->. The report therefore
predicts that PLEKHH3 restrains PI3K/AKT output with the PI(3,4)P₂ arm, a direction that a "function in a module"
vocabulary cannot express; lineage-adjusted partial correlations and an analysis excluding PTEN-null lines are still to
be done. C5orf34 co-depends exclusively on centriole-duplication genes, including the recently described A–C linker
proteins CCDC77, MIIP and TBC1D31 (alias WDR67) [Bournonville2025], but Wainberg et al. had already predicted a
centriole function for it <!-- src: results/revision/a2_novelty_overlap.tsv -->. What is new is the condition: a
red-team-prompted refit showed that the centriolar neighbourhood survives in the 902 TP53-mutant lines and collapses in
the 459 wild-type lines, whereas three random 459-line refits retain it <!-- src: reports/C5orf34.md (§5) -->. The signal
is second-order — it comes from partner-list overlap (B-view z 23.8 with SPICE1) rather than direct correlation (F-view z
2.4; raw r with SPICE1 0.06), and GLS gives a different top term <!-- src: reports/C5orf34.md (§0, §4, §5) -->. The
co-dependency is therefore conditional on TP53 status, consistent with a centriolar phenotype masked by p53-dependent
arrest [Lambrus2016], with a p53-context dependency unrelated to centrioles, or with p53 arrest homogenising the
dependency of the whole module; whether the centriole module itself loses coherence in TP53-wild-type lines has not yet
been tested, and the experimental plan requires an isogenic TP53 arm.

Third, the other hypotheses are weak or not new, as the reports state up front. CCDC71L's Polycomb-dominated
neighbourhood exists only after bias correction, the protein's high basic charge makes non-specific chromatin
association the prior <!-- src: reports/CCDC71L.md (§0) -->, and Wainberg et al. had predicted an H3K27-methyltransferase
function from a module with 8 of our top 10 partners <!-- src: reports/CCDC71L.md (§0) -->. Its proposed IP-MS against a
PxVxL mutant tests HP1 binding, a refinement suggested by structural and hu.MAP data; the HP1 proteins themselves are not
co-dependent with CCDC71L (r −0.105 to −0.010) <!-- src: reports/CCDC71L.md (§3) -->, so that experiment tests the
interaction-derived hypothesis, and a Polycomb readout (H2AK119ub and H3K27me3 at Polycomb targets) is needed to test the
co-essentiality one (S10 Table). TM2D1 and TM2D2 form a single observation: a co-dependency star with AUP1, JOSD1, STUB1
and CHIC2 whose "ER stress" label rests on two partners and which shows no co-variation with the core ERAD machinery or
UPR genes <!-- src: reports/TM2D1.md (§0); reports/TM2D2.md (§0) -->; the shared dependency was already in Wainberg et
al.'s modules <!-- src: results/revision/a2_novelty_overlap.tsv -->. INAFM1, the weakest, is dependency-flat (4 of 1,361
lines below −0.5), its predicted term rests on partners with near-zero raw correlation, its strongest partners (NFE2L1,
NGLY1, DDI2, the NRF1-activation axis) form one correlated axis to which it attaches weakly (r 0.12–0.21)
<!-- src: reports/INAFM1.md (§0) -->, and Wainberg et al. had predicted a related ubiquitination function
<!-- src: results/revision/a2_novelty_overlap.tsv -->. Of the seven reports that are not rediscoveries, only RBM34 has
admitted orthogonal support for its term, and none was supported by the blinded judges, as expected for genes with
partial or no literature.

**Table 3. The ten candidate reports.** Rank and p_cal in the primary top 40; relationship type: a, stable subunit;
b, assembly or maturation factor; d, pathway member, type unresolved. Orthogonal classes that support the predicted term
after Holm correction: P, physical; A, co-abundance; L, localisation; G, Perturb-seq. L class: agent L's novelty class;
judged: blinded, adjudicated verdict. Prior: earlier catalogue evidence for the gene's co-essential or physical link
[post-review]. Decisive experiments: S10 Table.

| Gene (rank; p_cal) | Predicted function; type | Key co-essential partners | Evidence: physical; other orthogonal; L class; judged | Prior in catalogues | Main caveat | Status |
|---|---|---|---|---|---|---|
| ANKRD52 (1; 0.141) | Regulatory ncRNA-mediated gene silencing; d (PP6 subunit acting on AGO2) | AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8; PPP6C | none (physical data point to PP6); none; N1; supported | Wainberg module and GLS pairs; Kim edge; hu.MAP; Predictomes | Published mechanism and co-dependency; AGO2 loss near-neutral | rediscovery |
| TRAPPC5 (4; 0.114) | Golgi vesicle transport; a (TRAPP subunit) | TRAPPC3, TRAPPC1, TRAPPC11, TRAPPC4, TRAPPC2L, TRAPPC13, TRAPPC8 | P; A, L, G; N2; supported | Wainberg module; Kim edge; hu.MAP; Predictomes | Membership in UniProt and Complex Portal; TRAPPIII leaning untested against other core subunits; TP53 flag | rediscovery |
| RBM34 (5; 0.103) | DNA-templated transcription elongation (label from Pol I subunits); script a, evidence favours b | WDR89, DDX31, PWP1, RPF1, CEBPZ, POLR1E/G/H, TCOF1 | P; A, L; N2; unaddressed | Wainberg pre-ribosome module; Predictomes (PWP1) | Term is a vocabulary artefact; Nop12 orthology implies the module; DEMETER2 and TP53 flags | partial rediscovery |
| PLEKHH3 (12; 0.076) | Regulation of PI3K/AKT signal transduction, as a negative regulator; d | PLEKHA1, PTEN, PTPN13; TSC2, TSC1, DDIT4 | none; none; N3; unaddressed | none found | Low-amplitude co-advantage; PTEN and PLEKHA1 correlated (r 0.45), about two effective partners; absent in lymphoid lines | hypothesis (new) |
| CCDC71L (16; 0.064) | Epigenetic regulation of gene expression; d | SUZ12, EED, BMI1, RING1, CBX4, CBX8, PHC3, MTF2; SMCHD1, LRIF1 | none; none; N2; unaddressed | Wainberg function prediction (H3K27 methyltransferase), module and GLS pair | Exists only after bias correction; very basic protein; lineage leave-out changes the term; HP1 not co-dependent | hypothesis (predicted before) |
| TM2D2 (21; 0.050) | Response to ER stress (tied with ERAD); d | TM2D1, JOSD1, AUP1, STUB1, CHIC2 | none; none; N2; unaddressed | Wainberg module and GLS pairs | Term rests on two partners; no co-variation with HRD1–SEL1L–UBE2G2 or UPR genes; DEMETER2 non-replication | hypothesis (with TM2D1; link published) |
| TM2D1 (28; 0.045) | Response to ER stress (tied with ERAD); d | TM2D2, AUP1, JOSD1, STUB1, CHIC2 | none; none; N2; unaddressed | Wainberg module and GLS pairs; hu.MAP; Predictomes | Same module as TM2D2 (one observation); STUB1 only raw rank 234; GLS gives a different top term | hypothesis (with TM2D2) |
| C5orf34 (31; 0.044) | Regulation of organelle assembly (centriole duplication); b | SPICE1, CEP135, CEP295, WRAP73, PPP1R35, CEP120, CCDC77, MIIP, TBC1D31 | none; none; N2; unaddressed | Wainberg function prediction (centriole elongation) | TP53-mutant lines only; second-order signal (raw r with SPICE1 0.06); GLS gives a different term; DEMETER2 and TP53 flags | hypothesis (function predicted before; TP53 condition new) |
| BICRAL (33; 0.041) | Transcription coregulator binding (GBAF complex); a (weight from literature) | SMARCD1, BRD9, CTBP1, SMARCA4, CREBBP | none; A, L (near-tautological); N2; supported | Wainberg module and GLS pairs; hu.MAP; Predictomes | Membership published in 2018; paralogue-specificity downgraded; lineage leave-out changes the term | rediscovery |
| INAFM1 (37; 0.037) | Polyubiquitin modification-dependent protein binding; d | label from RAD23B, VCP, UBQLN1; strongest NFE2L1, NGLY1, DDI2 | none; none; N3; unaddressed | Wainberg function prediction (K63-ubiquitination), module and GLS pairs | Dependency-flat (4 of 1,361 lines < −0.5); NRF1 axis weakly attached; lineage leave-out changes the term | hypothesis (predicted before; weakest) |

<!-- src: rank, p_cal, orthogonal classes and flags from manuscript/figures/source_data/Fig4_top40_primary.tsv
(results/ledger/top40_primary.tsv); judged verdicts from results/m7/judge/analysis_main_genes.tsv and, for packet-level
scores, results/m7/judge/scores/ADJ_main2.tsv; L classes from results/m7/report_selection.md; prior-catalogue column
from results/revision/a2_novelty_overlap.tsv; partners and caveats from §0, §1 and §4 of reports/ANKRD52.md,
reports/TRAPPC5.md, reports/RBM34.md, reports/PLEKHH3.md, reports/CCDC71L.md, reports/TM2D2.md, reports/TM2D1.md,
reports/C5orf34.md, reports/BICRAL.md and reports/INAFM1.md (post-red-team, post-review versions). -->
