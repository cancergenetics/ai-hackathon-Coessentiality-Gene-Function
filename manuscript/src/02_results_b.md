
## C4: blinded literature concordance supports the top predictions, mostly as rediscovery of published function

**Candidate sets.** Four gene sets entered the literature step (Fig 5A). The primary set is the top 40 by p_cal. S20
holds the 20 strongest predictions that have no p_cal, because their family has fewer than 30 H genes or their signal
exceeds H's 95th percentile <!-- src: results/m7/s20.tsv -->; it was defined before any literature step and is analysed
separately [deviation]. Extra30 holds 30 further fill-pool genes, six in each p_cal quintile (p_cal 6 × 10⁻⁸ to 0.099)
<!-- src: results/m7/extra30.tsv --> [pre-specified secondary]. Ten H genes whose "real" statement is a known current
target term served only to validate the judges <!-- src: results/m7/hval10.tsv --> [pre-specified]. Judged statements
contained the predicted GO term and the descriptive module label but not the relationship type, which existed for no
decoy donor and would have marked the real slot [deviation]. The judge instruction credited a match to "the stated
process or module", so a module-label match counted as support; this was entered in DEVIATIONS.md only after the result
[deviation, logged after the result], and term-only results are reported beside the primary ones (Methods).

**Recall probe and blind literature screen [pre-specified; extended].** Before any agent saw network output for these
genes, a closed-book language model "recognised" 43 of 59 N1 candidates but 1 of 7 N3 candidates
<!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv --> (Fig 5D; S1 Text). A language model therefore
already knows most published-but-uncurated functions, which is why the judges saw only evidence retrieved by a separate
agent, L, under a redacted gene name. Agent L, with no access to co-essentiality output or to our predictions, recorded
887 evidence items with verbatim spans for the 100 genes
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Among the 90 U candidates, 59 were N1, 24 N2 and 7
N3 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->; in the primary top 40 the split was 31 N1, 7
N2 and 2 N3, and in S20 17 N1 and 3 N2 <!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv --> (Fig 5C).
These sets were selected on p_cal or signal and do not estimate a prevalence, but the highest-ranked predictions are
concentrated in genes whose function is already published but not yet in GO experimental annotation: 78% of the top 40
and 85% of S20 <!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv -->. [Post-review exploratory] The
definition artefacts described under C1 are concentrated here: 37 of the top 40 and all 20 S20 genes entered U through
the literature criterion alone, and 30 of the top 40 and all of S20 carry a definition-artefact flag (13 and 17 are
Complex Portal subunits) <!-- src: results/revision/a1_flag_counts.tsv -->.

**Judges [pre-specified].** On the 10 H validation genes, adjudicated scores supported 9 of 10 real statements and 1 of
30 decoys <!-- src: results/m7/judge/analysis_hval.md -->, meeting the acceptance rule (at least 7 of 10 real, at most 3
of 30 decoys) at the first attempt. Over the 360 main statements the two judges, two instances of one model (Methods),
agreed with κ = 0.975, with 2 disagreements, both resolved by the adjudicator <!-- src: results/m7/judge/analysis_main.md -->.
This is between-instance reproducibility, not validity, which rests on the validation set and the low decoy support
rate. No packet leaked a gene or partner name <!-- src: results/m7/judge/leak_check.tsv -->.

**Primary blinded test: top 40 [pre-specified; scoring operationalised, see above].** Each gene's packet held the real
statement and three decoys in random order; the decoys were top terms of other U genes, matched on family and term size
<!-- src: results/m7/answer_key_slots.tsv -->. Judges supported 18 of 40 real statements (45%, Wilson 95% CI 31–60%),
left 20 unaddressed and scored 2 as contradicted <!-- src: results/m7/judge/analysis_main.md -->, both on direction (S1
Text). They supported 3 of 120 decoys (2.5%) <!-- src: results/m7/judge/analysis_main.md -->. The mean of real minus
mean decoy score was 0.375; with 20 non-zero differences, the exact one-sided sign-flip p was 2.2 × 10⁻⁴
<!-- src: results/m7/judge/analysis_main.md -->, so the primary test passes (Fig 5A). [Post-review exploratory] Counting
support for the GO term only, which is what p_cal estimates, 16 of 40 real statements were supported (sign-flip p = 7.1
× 10⁻⁴); every supported decoy was supported on its term
<!-- src: results/revision/a5_judging_sensitivity.tsv; results/revision/a5_plus1_basis.tsv -->. Slot-permutation and
module-clustered tests gave the same conclusion (S1 Text). The test is nonetheless easy: decoys are other genes' terms,
so for a gene with literature the real statement can win on topic alone; within-gene decoys (the gene's own
lower-ranked terms) would test whether the *top* prediction is preferred, and were not run. Support fell with rank: 12
of 20 for ranks 1–20 and 6 of 20 for ranks 21–40
<!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv --> (Fig 5B).

**Secondary sets [S20: deviation; extra30: pre-specified].** These sets were analysed separately and never pooled with
the primary test. In S20, judges supported 19 of 20 real statements and 2 of 60 decoys (sign-flip p = 1.9 × 10⁻⁶)
<!-- src: results/m7/judge/analysis_main.md -->; 15 of the 20 carry a Commander, complex I/OXPHOS or Elongator module
label <!-- src: results/m7/s20.tsv -->, the machinery modules that the calibration support rule excludes. In extra30,
judges supported 1 of 30 real statements and 1 of 90 decoys (p = 0.5) <!-- src: results/m7/judge/analysis_main.md -->.
Literature support therefore rose with p_cal across the fill pool (Fig 5B): 18 of 40 in the top 40 against 1 of 30 in
extra30 (one-sided Fisher p = 5.6 × 10⁻⁵) [exploratory; post hoc, unadjusted]
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Literature support is a different and more
lenient endpoint than p_cal, which estimates curation of the exact GO term with experimental evidence: the 18 (or 16)
supported statements sit beside a summed p_cal of 2.50 for the top 40
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv --> if every gene were annotated, or about 0.4–0.6
unconditionally (signal-adjusted 0.64, 0.32–1.02)
<!-- src: results/revision/a3_gain_rate_by_signal_quintile.tsv; results/revision/numbers_a3.json --> [post-review
exploratory]. The gap measures how much more often "the literature reports the gene in this process or module" holds
than "curators annotate this exact term".

**Support by novelty class [pre-specified reporting].** The support is mostly rediscovery. In the top 40, judges
supported 16 of 31 N1, 2 of 7 N2 and 0 of 2 N3 genes <!-- src: results/m7/judge/analysis_main.md --> (Fig 5C); in S20,
17 of 17 N1 and 2 of 3 N2 genes <!-- src: results/m7/judge/analysis_main.md -->. Of the 37 supported top-40 and S20
genes, 33 are N1, and the recall probe recognised 35 <!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->
(Table A in S1 Text). Among top-40 genes with published function, selected on p_cal, the predicted function matched the
published one for 16 of 31 (52%, Wilson 95% CI 35–68%); on the GO term alone it matched for 14 of 31 (45%), because
YPEL5 and DPCD are N1 genes supported on the module label only <!-- src: results/revision/a10_round2_numbers.tsv -->.
This is a curation-independent estimate of accuracy within that selected group, on a lenient endpoint. In extra30 the
corresponding count was 1 of 11 N1 genes <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv --> (one-sided
Fisher p = 0.014 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->) [exploratory; post hoc,
unadjusted]. This suggests that higher-ranked predictions match published function more often, and not only because
their genes are better studied; it rests on one uncorrected test with 11 extra30 genes. [Post-review exploratory] In
the top 40, judged support was 17 of 30 for genes with a definition-artefact flag and 1 of 10 for genes without
<!-- src: results/revision/a1_judged_support_by_flag.tsv -->. Only four supported genes are N2: TRAPPC5 and BICRAL in the
top 40, NDUFB2 and MED9 in S20 <!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->. No N3 prediction
could be checked against the literature by construction.

**Overlap with earlier catalogues [post-review exploratory].** For each candidate we asked whether the relationship
between the gene and at least one of its ten strongest partners had already been published (S9 Table; S4B Fig). Of the
primary top 40, 19 have a significant GLS pair and 22 share a tight module in the 2021 co-essentiality atlas
[Wainberg2021], 17 share a hu.MAP 3.0 complex with a top-10 partner and 20 have a Predictomes AlphaFold pair (SPOC ≥
0.5) <!-- src: results/revision/a2_novelty_overlap.tsv; manuscript/figures/source_data/FigS4_derived_numbers.tsv -->.
Overall, 27 of the top 40 have a prior in a co-essentiality catalogue and 34 in any resource we obtained; only 6 have
none, and all 20 S20 genes have a prior <!-- src: results/revision/a2_novelty_overlap.tsv -->. Wainberg et al. listed
explicit function predictions for three of our top-40 genes, CCDC71L, C5orf34 and INAFM1
<!-- src: results/revision/a2_novelty_overlap.tsv -->, all of which became candidate reports. These flags record that the
link was published, not that the same function was assigned; Pan et al. [Pan2018], FIREWORKS [Amici2021] and
Perturb-seq clusters [Replogle2022] could not be checked, so the counts are lower bounds on prior knowledge.

## Ten candidate reports: three rediscoveries, one partial rediscovery and five hypotheses, four of them previously proposed

The ten report genes were fixed before any judging result existed <!-- src: results/m7/report_selection.md -->: the
nine highest-ranked N2 and N3 genes of the primary top 40 and one N1 rediscovery exemplar, ANKRD52, the top-ranked gene
overall. Each report was written from a machine-generated evidence bundle, attacked by an independent red-team agent,
and revised (S1–S10 Reports); all ten red-team verdicts were "accept with revisions"
<!-- src: reports/redteam/ANKRD52.md; reports/redteam/TRAPPC5.md; reports/redteam/RBM34.md; reports/redteam/PLEKHH3.md; reports/redteam/CCDC71L.md; reports/redteam/TM2D2.md; reports/redteam/TM2D1.md; reports/redteam/C5orf34.md; reports/redteam/BICRAL.md; reports/redteam/INAFM1.md -->.
Nine of the ten genes had a prior co-essential or physical link in earlier catalogues; only PLEKHH3 had none
<!-- src: results/revision/a2_novelty_overlap.tsv -->. Table 2 summarises the reports, S10 Table gives the decisive
experiments, and S1 Text gives the full narrative.

**Rediscoveries.** ANKRD52, BICRAL and TRAPPC5 recovered published biology blind. ANKRD52 is the regulatory subunit of
the phosphatase PP6, which dephosphorylates Argonaute 2 to sustain microRNA silencing [Golden2017]; its
co-essentiality neighbourhood is the miRNA biogenesis and silencing machinery, and the AGO2–ANKRD52 co-dependency had
itself been reported [Shui2023]. BICRAL's two strongest partners, SMARCD1 and BRD9, are the defining subunits of the
non-canonical BAF (GBAF/ncBAF) complex in which it was placed biochemically in 2018 [Alpsoy2018]. TRAPPC5 is a known
TRAPP core subunit. RBM34 is a partial rediscovery: its partners are RNA polymerase I subunits and large-subunit
pre-rRNA assembly factors, consistent with its yeast orthologue Nop12, a 60S maturation factor [Talkish2014], and with a
pre-ribosome module of Wainberg et al., while the predicted term "DNA-templated transcription elongation" reflects how
the Pol I subunits are annotated <!-- src: reports/RBM34.md (§0) -->.

**PLEKHH3.** The one hypothesis without precedent in any catalogue we checked rests on a fitness co-advantage rather
than on shared essentiality. PLEKHH3's two strongest correlates among all 18,433 genes are PLEKHA1 (TAPP1) and PTEN
(r = 0.424 and 0.400), followed by TSC2, TSC1 and DDIT4, while the pathway's accelerator PIK3CA runs the other way
(r = −0.186) <!-- src: reports/PLEKHH3.md (§0) -->. PTEN and PLEKHA1, like PLEKHH3 itself, are genes whose loss helps
cells grow (mean Chronos effects +0.377, +0.219 and +0.087) <!-- src: reports/PLEKHH3.md (§0, §3) -->. The two
partners are themselves correlated (r 0.453), but each keeps a partial correlation with PLEKHH3 given the other (0.257
and 0.298) <!-- src: reports/PLEKHH3.md (§0) -->. The report predicts that PLEKHH3 restrains PI3K/AKT output with the
PI(3,4)P₂ arm, a direction that a "function in a module" vocabulary cannot express. For now this is a low-amplitude
co-advantage signal not yet controlled for lineage: the co-dependency is absent in lymphoid lines, and the checks that
need only DepMap data (lineage-adjusted partial correlations and an analysis excluding PTEN-null lines) were not run.

**C5orf34.** C5orf34 co-depends exclusively on centriole-duplication genes, including the recently described A–C linker
proteins CCDC77, MIIP and TBC1D31 (alias WDR67) [Bournonville2025], and Wainberg et al. had already predicted a
centriole function for it <!-- src: results/revision/a2_novelty_overlap.tsv -->. A red-team-prompted refit showed that
the centriolar neighbourhood survives in the 902 TP53-mutant lines and collapses in the 459 wild-type lines, whereas
three random 459-line refits retain it <!-- src: reports/C5orf34.md (§5) -->. The signal is second-order, from
partner-list overlap rather than direct correlation (S1 Text). The TP53 dependence could reflect a centriolar phenotype
masked by p53-dependent arrest [Lambrus2016], a p53-context dependency unrelated to centrioles, or p53 arrest
homogenising the dependency of the whole module. The DepMap-only check that would address the last explanation, the
coherence of the centriole module itself in TP53-wild-type lines, was not run, so the TP53 condition is an observation
to be tested, not an established property of C5orf34.

**The other hypotheses** are weak or anticipated, as the reports state up front. CCDC71L's Polycomb-dominated
neighbourhood exists only after bias correction, and Wainberg et al. had predicted an H3K27-methyltransferase function
for it <!-- src: reports/CCDC71L.md (§0) -->. TM2D1 and TM2D2 form one co-dependency module with AUP1, JOSD1, STUB1 and
CHIC2, whose "ER stress" label rests on two partners and which was already in Wainberg et al.'s modules
<!-- src: reports/TM2D1.md (§0); reports/TM2D2.md (§0) -->. INAFM1, the weakest, is dependency-flat (4 of 1,361 lines
below −0.5) <!-- src: reports/INAFM1.md (§0) -->, and a related ubiquitination function had been predicted before
<!-- src: results/revision/a2_novelty_overlap.tsv -->. None of the seven reports that are not rediscoveries was supported
by the blinded judges, as expected for genes with partial or no literature.

**Table 2. The ten candidate reports.** Rank and p_cal in the primary top 40; relationship type: a, stable subunit;
b, assembly or maturation factor; d, pathway member, type unresolved. Orthogonal classes that support the predicted term
after Holm correction: P, physical; A, co-abundance; L, localisation; G, Perturb-seq. L class: agent L's novelty class;
judged: blinded, adjudicated verdict. Prior: earlier catalogue evidence for the gene's co-essential or physical link
[post-review]. DEMETER2 non-replication is not listed as a caveat, because the check was never validated (S1 Text).
Decisive experiments: S10 Table.

| Gene (rank; p_cal) | Predicted function; type | Key co-essential partners | Evidence: physical; other orthogonal; L class; judged | Prior in catalogues | Main caveat | Status |
|---|---|---|---|---|---|---|
| ANKRD52 (1; 0.141) | Regulatory ncRNA-mediated gene silencing; d (PP6 subunit acting on AGO2) | AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8; PPP6C | none (physical data point to PP6); none; N1; supported | Wainberg module and GLS pairs; Kim edge; hu.MAP; Predictomes | Published mechanism and co-dependency; AGO2 loss near-neutral | rediscovery |
| TRAPPC5 (4; 0.114) | Golgi vesicle transport; a (TRAPP subunit) | TRAPPC3, TRAPPC1, TRAPPC11, TRAPPC4, TRAPPC2L, TRAPPC13, TRAPPC8 | P; A, L, G; N2; supported | Wainberg module; Kim edge; hu.MAP; Predictomes | Membership in UniProt and Complex Portal; TRAPPIII leaning untested against other core subunits; TP53 flag | rediscovery |
| RBM34 (5; 0.103) | DNA-templated transcription elongation (label from Pol I subunits); script a, evidence favours b | WDR89, DDX31, PWP1, RPF1, CEBPZ, POLR1E/G/H, TCOF1 | P; A, L; N2; unaddressed | Wainberg pre-ribosome module; Predictomes (PWP1) | Term is a vocabulary artefact; Nop12 orthology implies the module; TP53 flag | partial rediscovery |
| PLEKHH3 (12; 0.076) | Regulation of PI3K/AKT signal transduction, as a negative regulator; d | PLEKHA1, PTEN, PTPN13; TSC2, TSC1, DDIT4 | none; none; N3; unaddressed | none found | Low-amplitude co-advantage, not yet controlled for lineage or PTEN-null lines; PTEN and PLEKHA1 correlated (r 0.45), about two effective partners; absent in lymphoid lines | hypothesis (no precedent found) |
| CCDC71L (16; 0.064) | Epigenetic regulation of gene expression; d | SUZ12, EED, BMI1, RING1, CBX4, CBX8, PHC3, MTF2; SMCHD1, LRIF1 | none; none; N2; unaddressed | Wainberg function prediction (H3K27 methyltransferase), module and GLS pair | Exists only after bias correction; very basic protein; lineage leave-out changes the term; HP1 not co-dependent | hypothesis (predicted before) |
| TM2D2 (21; 0.050) | Response to ER stress (tied with ERAD); d | TM2D1, JOSD1, AUP1, STUB1, CHIC2 | none; none; N2; unaddressed | Wainberg module and GLS pairs | Term rests on two partners; no co-variation with HRD1–SEL1L–UBE2G2 or UPR genes | hypothesis (with TM2D1; link published) |
| TM2D1 (28; 0.045) | Response to ER stress (tied with ERAD); d | TM2D2, AUP1, JOSD1, STUB1, CHIC2 | none; none; N2; unaddressed | Wainberg module and GLS pairs; hu.MAP; Predictomes | Same module as TM2D2 (one observation); STUB1 only raw rank 234; GLS gives a different top term | hypothesis (with TM2D2) |
| C5orf34 (31; 0.044) | Regulation of organelle assembly (centriole duplication); b | SPICE1, CEP135, CEP295, WRAP73, PPP1R35, CEP120, CCDC77, MIIP, TBC1D31 | none; none; N2; unaddressed | Wainberg function prediction (centriole elongation) | TP53-mutant lines only, module coherence in wild-type lines untested; second-order signal (raw r with SPICE1 0.06); GLS gives a different term; TP53 flag | hypothesis (function predicted before; TP53 condition untested) |
| BICRAL (33; 0.041) | Transcription coregulator binding (GBAF complex); a (weight from literature) | SMARCD1, BRD9, CTBP1, SMARCA4, CREBBP | none; A, L (near-tautological); N2; supported | Wainberg module and GLS pairs; hu.MAP; Predictomes | Membership published in 2018; paralogue-specificity downgraded; lineage leave-out changes the term | rediscovery |
| INAFM1 (37; 0.037) | Polyubiquitin modification-dependent protein binding; d | label from RAD23B, VCP, UBQLN1; strongest NFE2L1, NGLY1, DDI2 | none; none; N3; unaddressed | Wainberg function prediction (K63-ubiquitination), module and GLS pairs | Dependency-flat (4 of 1,361 lines < −0.5); NRF1 axis weakly attached; lineage leave-out changes the term | hypothesis (predicted before; weakest) |

<!-- src: rank, p_cal, orthogonal classes and flags from manuscript/figures/source_data/Fig4_top40_primary.tsv
(results/ledger/top40_primary.tsv); judged verdicts from results/m7/judge/analysis_main_genes.tsv and, for packet-level
scores, results/m7/judge/scores/ADJ_main2.tsv; L classes from results/m7/report_selection.md; prior-catalogue column
from results/revision/a2_novelty_overlap.tsv; partners and caveats from §0, §1 and §4 of reports/ANKRD52.md,
reports/TRAPPC5.md, reports/RBM34.md, reports/PLEKHH3.md, reports/CCDC71L.md, reports/TM2D2.md, reports/TM2D1.md,
reports/C5orf34.md, reports/BICRAL.md and reports/INAFM1.md (post-red-team, post-review versions). -->
