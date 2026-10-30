## C4: blinded literature judging supports the top predictions, mostly as rediscovery of uncurated function

<!-- Draft 1 (results writer). Covers M7: recall probe, blind literature screen, judge validation, blinded judging, the
rediscovery table. Deep-dive reports are NOT summarised here (placeholder below, for the PI). Labels as in
03_results_C1_C3.md: [pre-specified] = DESIGN.md v2.3 §6; [deviation] = DEVIATIONS.md row dated before the literature
step; [descriptive, this draft] = computed by scripts/61_figure5.py from committed M7 files
(manuscript/figures/source_data/Fig5_derived_numbers.tsv), not a pre-specified test. Figure 5 and Table 2 source data:
manuscript/figures/source_data/Fig5*_*.tsv, Table2_rediscovery.tsv. -->

**Candidate sets.** Four gene sets entered the literature step (Fig. 5a). The primary set is the top 40 by p_cal
[pre-specified fill; deviation in its reading, see C3]. Two sets are secondary. S20 holds the 20 strongest predictions
that have no p_cal, because their family has fewer than 30 H genes or their signal exceeds H's 95th percentile
<!-- src: results/m7/s20.tsv -->. S20 was defined after M6 but before any literature step, and is analysed separately
[deviation]. Extra30 holds 30 further genes from the fill pool, six in each p_cal quintile (p_cal 6 × 10⁻⁸ to 0.099)
<!-- src: results/m7/extra30.tsv --> [pre-specified secondary]. The fourth set, 10 H genes whose "real" statement is a
known current target term, served only to validate the judges <!-- src: results/m7/hval10.tsv --> [pre-specified].
Judged statements contained the V2 term and the V1′ module label only. The relationship type was dropped for every
statement, because types existed for none of the decoy donors and would have marked the real slot [deviation].

**Closed-book recall probe [pre-specified; extended to S20 and extra30].** Before any agent saw network output for
these genes, a fresh language model without tools stated what it knew of each gene from its symbol and aliases. It
"recognised" 52 of the 90 <!-- src: results/m7/recall_probe_90.tsv --> candidates: 22 of 40 in the top 40, 19 of 20 in
S20 and 11 of 30 in extra30 <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Recognition followed
the literature class assigned later by agent L (Fig. 5d). It recognised 43 of 59 N1, 8 of 24 N2 and 1 of 7 N3
candidates <!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->. The random 50 U genes showed the same
pattern: 18 of 21 N1, 3 of 13 N2 and 3 of 16 N3 <!-- src: manuscript/figures/source_data/Fig5d_recall_probe.tsv -->.
A language model therefore already knows most published-but-uncurated functions. This is why the judges saw only
evidence that agent L had retrieved, under a redacted gene name, and were told not to use their own knowledge.

**Blind literature screen: curation lag among candidates [pre-specified; extended to S20, extra30 and the H
validation genes].** Agent L had no access to co-essentiality output or to our predictions. For the 100 genes it
recorded 887 evidence items, each with a verbatim span. Of these, 518 were focused functional studies and 4 were
flagged as DepMap-derived <!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Among the 90 U
candidates, 59 were N1 (direct functional evidence), 24 N2 (partial) and 7 N3 (none)
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. In the primary top 40 the split was 31 N1, 7 N2
and 2 N3. In S20 it was 17 N1 and 3 N2, and in extra30 11 N1, 14 N2 and 5 N3
<!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv --> (Fig. 5c). For comparison, the random 50 U genes
had 21 N1, 13 N2 and 16 N3 <!-- src: results/audit/curation_lag_audit.md -->. A different auditor classed that sample,
so the comparison is descriptive. All 10 H validation genes were N1, as expected
<!-- src: results/m7/judge/analysis_hval_genes.tsv -->. Our highest-ranked predictions are thus concentrated in genes
whose function is already published but not yet in GO experimental annotation: 78% of the top 40 and 85% of S20
<!-- src: manuscript/figures/source_data/Fig5c_novelty_class.tsv -->.

**Judge validation [pre-specified].** On the 10 H genes, adjudicated scores supported 9 of 10 real statements and 1
of 30 decoys <!-- src: results/m7/judge/analysis_hval.md -->. This meets the acceptance rule (at least 7 of 10 real, at
most 3 of 30 decoys) at the first attempt, so no revision was needed. Agreement between the two judges was κ = 0.931
over 40 statements, with one disagreement <!-- src: results/m7/judge/analysis_hval.md -->. The adjudicator scored that
statement, a decoy, as supported. It is the single supported decoy
<!-- src: results/m7/judge/scores/ADJ_hval.tsv -->.

**Primary blinded test: top 40 [pre-specified].** Each gene's packet held the real statement and three decoys in
random order. The decoys were top terms of other U genes, matched on family and term size
<!-- src: results/m7/answer_key_slots.tsv -->. Judges supported 18 of 40 real statements (45%, Wilson 95% CI 31–60%),
left 20 unaddressed and scored 2 as contradicted <!-- src: results/m7/judge/analysis_main.md -->
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. They supported 3 of 120 decoys (2.5%)
<!-- src: results/m7/judge/analysis_main.md -->. The mean of real minus mean decoy score was 0.375. With 20 non-zero
differences, the exact one-sided sign-flip p was 2.2 × 10⁻⁴ <!-- src: results/m7/judge/analysis_main.md -->, so the
primary test passes (Fig. 5a). The two contradicted statements were for TLNRD1 and KDF1. Both are N1 genes <!-- src: results/m7/judge/analysis_main_genes.tsv -->, and in both
the evidence showed regulation in the opposite direction. TLNRD1 promotes rather than inhibits cell migration, and
KDF1 inhibits rather than activates NF-κB signalling <!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->.
Support fell with rank. It was 12 of 20 for ranks 1–20 (p_cal 0.055–0.141) and 6 of 20 for ranks 21–40 (p_cal
0.036–0.050) <!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv --> (Fig. 5b).

**Secondary sets [S20: deviation; extra30: pre-specified].** These sets were analysed separately and never pooled with
the primary test. In S20, judges supported 19 of 20 real statements and 2 of 60 decoys (sign-flip p = 1.9 × 10⁻⁶)
<!-- src: results/m7/judge/analysis_main.md -->. In S20, 15 of the 20 carry a Commander, complex I/OXPHOS or Elongator
module label <!-- src: results/m7/s20.tsv --> (Table 2). These are the well-established machinery modules that the
calibration support rule excludes. In extra30, judges supported 1 of 30 real statements and 1 of 90 decoys (p = 0.5)
<!-- src: results/m7/judge/analysis_main.md -->. Across the five extra30 quintiles, support was 0 of 6 in the four
lowest and 1 of 6 in the highest <!-- src: manuscript/figures/source_data/Fig5b_support_vs_pcal.tsv -->. Literature
support therefore rose with p_cal across the fill pool (Fig. 5b). The top 40 had 18 of 40 supported against 1 of 30
in extra30 (one-sided Fisher p = 5.6 × 10⁻⁵) [descriptive, this draft]
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Literature support is a different endpoint from
p_cal, which estimates future GO experimental annotation. The summed p_cal of the top 40 (2.50) <!-- src:
manuscript/figures/source_data/Fig5_derived_numbers.tsv --> should therefore not be compared directly with the 18
supported statements.

**Support by novelty class [pre-specified reporting].** The support is mostly rediscovery. In the top 40, judges
supported 16 of 31 N1, 2 of 7 N2 and 0 of 2 N3 genes <!-- src: results/m7/judge/analysis_main.md --> (Fig. 5c). In
S20 they supported 17 of 17 N1 and 2 of 3 N2 genes <!-- src: results/m7/judge/analysis_main.md -->. Of the 37
supported top-40 and S20 genes, 33 are N1, and the recall probe recognised 35
<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->. Being known is not enough, however. Among N1 genes
only, support was 16 of 31 in the top 40 and 1 of 11 in extra30 (one-sided Fisher p = 0.014) [descriptive, this draft]
<!-- src: manuscript/figures/source_data/Fig5_derived_numbers.tsv -->. Higher-ranked predictions match the published
function more often, not merely more studied genes. Only four supported genes are N2: TRAPPC5 and BICRAL in the top
40, NDUFB2 and MED9 in S20 <!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv -->. For these, agent L classed the published
evidence as partial. No N3 prediction could be checked
against the literature by construction, and the top 40 contains only 2 N3 genes.

**Agreement and adjudication [pre-specified].** Over the 360 main statements the judges agreed with κ = 0.975, with 2
disagreements and none left unresolved <!-- src: results/m7/judge/analysis_main.md -->. Both disagreements involved
real statements, for WDR7 (S20) and DPCD (top 40). The adjudicator resolved both as supported because the evidence
matched the module label, not the V2 term <!-- src: results/m7/judge/scores/ADJ_main2.tsv -->
<!-- src: results/m7/judge/scores/ADJ_main3.tsv -->. The judging rule credits a match to "the stated process or module"
<!-- src: scripts/51_judge_packets.py --> and applied equally to decoys. Still, three supported real statements rest on
the module label alone: YPEL5 (GID/CTLH complex; Wnt not shown), DPCD (R2TP/PAQosome; transcription elongation not
shown) and WDR7 (V-ATPase/RAVE; iron homeostasis not shown) <!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->. For
DDX19A, support for "cell population proliferation" came from cancer cell-line proliferation studies
<!-- src: results/m7/judge/scores/J1_main2.tsv, J1_main3.tsv (packets J045, J048, J088, J098, J040, J095) -->. Counting only term-level support, the top 40 has 16 supported real
statements <!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv --> [descriptive, this draft]. The judges'
packets contained no gene-symbol or partner-name leaks <!-- src: results/m7/judge/leak_check.tsv -->.

**Table 2. Top-40 and S20 predictions judged supported by the literature (blinded, adjudicated).** p_cal for the top
40; uncalibrated top-K mean zavg_BEF for S20. L class, agent L's novelty class. Probe, recognised by the closed-book
recall probe. Basis: whether judges cited the V2 term (term) or only the V1′ module label (module).

| Set, rank | Gene | Predicted V2 term | V1′ module label | p_cal / zavg | L class | Probe | Basis |
|---|---|---|---|---|---|---|---|
| top 40, 1 | ANKRD52 | regulatory ncRNA-mediated gene silencing | RISC complex | 0.141 | N1 | yes | term |
| top 40, 3 | CNOT10 | regulation of RNA stability | CCR4-NOT deadenylase complex | 0.116 | N1 | yes | term |
| top 40, 4 | TRAPPC5 | Golgi vesicle transport | TRAPP III complex | 0.114 | N2 | yes | term |
| top 40, 6 | SSR4 | protein N-linked glycosylation | ER protein-containing complex | 0.091 | N1 | yes | term |
| top 40, 7 | CNOT11 | regulation of RNA stability | CCR4-NOT deadenylase complex | 0.080 | N1 | yes | term |
| top 40, 8 | MED31 | DNA-templated transcription initiation | RNA Pol II transcription regulator complex | 0.079 | N1 | yes | term |
| top 40, 9 | YPEL5 | positive regulation of Wnt signaling pathway | GID E3 ubiquitin ligase complex | 0.078 | N1 | yes | module |
| top 40, 10 | TMEM208 | establishment of protein localization to membrane | ER protein-containing complex | 0.078 | N1 | yes | term |
| top 40, 11 | PHC3 | epigenetic regulation of gene expression | PcG protein complex | 0.077 | N1 | yes | term |
| top 40, 15 | TMED7 | Golgi vesicle transport | cytoplasmic ubiquitin ligase complex | 0.064 | N1 | yes | term |
| top 40, 18 | MGA | epigenetic regulation of gene expression | chromatin silencing complex | 0.059 | N1 | yes | term |
| top 40, 20 | TMEM209 | nucleus organization | nuclear pore complex | 0.055 | N1 | no | term |
| top 40, 26 | PSMD13 | regulation of proteasomal protein catabolic process | proteasome complex | 0.047 | N1 | yes | term |
| top 40, 27 | COA4 | cytochrome complex assembly | MitoCarta: OXPHOS | 0.046 | N1 | yes | term |
| top 40, 30 | GRIPAP1 | vesicle-mediated transport to the plasma membrane | vesicle tethering complex | 0.044 | N1 | yes | term |
| top 40, 33 | BICRAL | transcription coregulator binding | GBAF (SWI/SNF) complex | 0.041 | N2 | yes | term |
| top 40, 38 | DDX19A | cell population proliferation | ER protein-containing complex | 0.036 | N1 | yes | term (generic) |
| top 40, 40 | DPCD | DNA-templated transcription elongation | PAQosome co-chaperone complex | 0.036 | N1 | no | module (adjudicated) |
| S20, 1 | COMMD3 | endosomal transport | Commander complex | 18.5 | N1 | yes | term |
| S20, 2 | COMMD2 | endosomal transport | Commander complex | 17.0 | N1 | yes | term |
| S20, 3 | NDUFB10 | NADH dehydrogenase activity | MitoCarta: OXPHOS | 16.7 | N1 | yes | term |
| S20, 4 | COMMD4 | endosomal transport | Commander complex | 16.4 | N1 | yes | term |
| S20, 5 | NDUFB2 | NADH dehydrogenase activity | respiratory chain complex I | 16.3 | N2 | yes | term |
| S20, 6 | NDUFA2 | NADH dehydrogenase activity | respiratory chain complex I | 16.3 | N1 | yes | term |
| S20, 7 | COMMD8 | endosomal transport | Commander complex | 16.3 | N1 | yes | term |
| S20, 8 | TADA2B | acyltransferase activity (non-amino-acyl groups) | SAGA complex, KAT2A variant | 16.2 | N1 | yes | term |
| S20, 9 | NDUFA11 | NADH dehydrogenase activity | MitoCarta: OXPHOS | 16.0 | N1 | yes | term |
| S20, 10 | COMMD10 | endosomal transport | Commander complex | 15.9 | N1 | yes | term |
| S20, 11 | WDR7 | intracellular iron ion homeostasis | proton-transporting two-sector ATPase complex | 15.8 | N1 | yes | module (adjudicated) |
| S20, 12 | WASHC3 | endosomal transport | Commander complex | 15.6 | N1 | yes | term |
| S20, 14 | CTU2 | tRNA metabolic process | Elongator holoenzyme complex | 15.5 | N1 | yes | term |
| S20, 15 | NDUFB4 | NADH dehydrogenase activity | MitoCarta: OXPHOS | 15.5 | N1 | yes | term |
| S20, 16 | ELP5 | tRNA metabolic process | Elongator holoenzyme complex | 15.2 | N1 | yes | term |
| S20, 17 | ELP6 | tRNA metabolic process | Elongator holoenzyme complex | 15.0 | N1 | yes | term |
| S20, 18 | UNC50 | Golgi organization | vesicle tethering complex | 14.9 | N1 | yes | term |
| S20, 19 | MED9 | regulation of transcription initiation by RNA Pol II | RNA Pol II transcription regulator complex | 14.8 | N2 | yes | term |
| S20, 20 | NUP43 | nucleocytoplasmic transport | nuclear pore complex | 14.8 | N1 | yes | term |

<!-- src: manuscript/figures/source_data/Table2_rediscovery.tsv (scripts/61_figure5.py: analysis_main_genes.tsv,
answer_key_slots.tsv, top40_primary.tsv, s20.tsv, L/index_batch_*.tsv, recall_probe_90.tsv); Basis column read from the
judges' justifications in results/m7/judge/scores/J1_main*.tsv, J2_main*.tsv and ADJ_main*.tsv. Complex labels
shortened (full names in the source TSV). -->

Unsupported top-40 genes: 20 unaddressed and 2 contradicted (TLNRD1, KDF1); S20: NR2C2AP unaddressed
<!-- src: results/m7/judge/analysis_main_genes.tsv -->.

**Deep-dive candidates (see Reports).** [PI to fill. The 10 report genes were fixed before judging results existed
<!-- src: results/m7/report_selection.md -->: the highest-ranked N2/N3 top-40 genes (TRAPPC5, RBM34, PLEKHH3, CCDC71L,
TM2D2, TM2D1, C5orf34, BICRAL, INAFM1) and one N1 rediscovery exemplar (ANKRD52). Of these, only TRAPPC5, BICRAL and
ANKRD52 were judged supported <!-- src: results/m7/judge/analysis_main_genes.tsv -->; the others remain hypotheses
with no direct published support. Summarise the decisive experiment and strongest alternative per gene from reports/.]

<!-- Notes for the PI:
1. The recall probe and L screen were run on S20 and extra30 (and L on hval10) in addition to the DESIGN §6.2/§6.3
   scope (top 40 + random 50); labelled "extended". No DEVIATIONS row covers the extra30 probe/screen explicitly; the
   S20 row says S20 goes through the same probe/screen/judging. Consider a one-line DEVIATIONS entry for extra30.
2. "Term (generic)" for DDX19A and the three "module" rows are my reading of the judges' justification lines, not a
   pre-specified category. A term-only re-analysis of the sign-flip test is not computed; if wanted, it needs a
   pre-declared rule and would itself be post hoc (LOOKS.md).
3. The random-50 N-classes (curation-lag auditor) and the candidate N-classes (agent L) come from different agents
   with similar instructions; Fig. 5c/d label them separately.
4. Fisher tests (top 40 vs extra30, overall and within N1) are descriptive, from scripts/61_figure5.py.
5. The "78% / 85%" N1 shares: 31/40 and 17/20. -->
