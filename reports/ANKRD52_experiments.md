# ANKRD52 — experiment plan (Template B)

Companion to `reports/ANKRD52.md` (N1 rediscovery exemplar). Evidence keys (A*, L*, T*) refer to Appendix A of that report; every key is verified. Cell lines, effects, media and copy number come from `reports/data/ANKRD52/bundle.md` §10; values marked † are recomputed in `results/m7/scratch_reports_trappc5/`.

Because the module assignment is already published [A1], the plan is not designed to re-prove it. It is designed to test the one statement our data add (`reports/ANKRD52.md` §7 (ii)): that ANKRD52's **fitness** requirement across cancer lines is mediated by the AGO2 phospho-cycle rather than by PP6's other substrates.

## 1. Context

- Gene: **ANKRD52** | hypothesis: ANKRD52 acts in regulatory ncRNA-mediated gene silencing (miRNA pathway), as the substrate-targeting subunit of the PP6 holoenzyme that dephosphorylates AGO2; its proliferation dependency in DepMap lines is mediated by that arm of PP6 rather than by PP6's Aurora A / MEK / PAK1 substrates. | relationship type: **d** (pathway member; explicitly *not* a RISC subunit) | novelty class: **N1**
- LLM-recall-probe flag: **known** for the protein's identity (PP6-ARS-C) but the probe did not state the predicted module | calibrated probability p_cal **0.1410** [0.065–0.244] (family other) | tier: none (p_cal fill, rank 1 of the primary top 40)
- Strongest alternative explanation: ANKRD52's dependency is PP6-general (mediated by Aurora A [A20], MEK [A18] or PAK1 [A14]), and the miRNA-machinery co-dependency is a correlate rather than the cause; a second, locus-level alternative is that the DepMap signal reflects destruction of the circular intronic RNA ci-ankrd52 [A17] rather than of the protein.
- **Decisive experiment (one sentence):** in two ANKRD52-dependent lines carrying a homozygous knock-in of non-phosphorylatable AGO2 (S824–S834→A, the 5XA allele whose expression rescued silencing in ANKRD52-null cells [A22]) versus isogenic wild-type AGO2 lines, deplete ANKRD52 with a degron and measure competitive growth, miRNA-reporter silencing and the transcriptome — if the fitness requirement runs through the AGO2 phospho-cycle, AGO2-5XA rescues the growth defect; if ANKRD52's dependency is PP6-general, it does not, while the reporter defect is still rescued.
- Falsifying observation (Template A §9.2): AGO2-5XA fails to rescue the proliferation defect of ANKRD52 loss while rescuing the silencing defect — refuting the added claim and leaving the module assignment correct but unable to explain the dependency that produced it.

## 2. Cell lines (selection rule)

Rule: Chronos ≤ −0.5 for g and ≤ −0.3 for the rank-1 partner (AGO2); g expressed (log2(TPM+1) ≥ 2); locus not amplified; best ScreenNNMD; TP53-mutant preferred; line 2 from another lineage. Funnel: 1361 lines → 169 (g ≤ −0.5) → 53 (+AGO2 ≤ −0.3) → 48 (+expression) → 48 (+not amplified). The funnel is narrow because ANKRD52 is a weak, selective dependency (mean −0.243; < −0.5 in only 12.4% of lines) and AGO2 is barely essential anywhere (mean −0.090; < −0.5 in 1.8% of lines) †.

| Role | ModelID | Name | Lineage / disease | g effect | AGO2 effect | g expr (log2 TPM+1) | g CN | TP53 | ScreenNNMD | Medium |
|---|---|---|---|---|---|---|---|---|---|---|
| Dependent D1 | ACH-000127 | SLR 20 | Bladder/urinary tract / urothelial carcinoma | −0.69 | −0.50 | 4.08 | 1.04 | mutant | −14.05 | RPMI + 10% FBS (MF-001-001) |
| Dependent D2 | ACH-000215 | LN382 | CNS/brain / adult-type diffuse glioma | −0.54 | −0.33 | 4.51 | 1.05 | mutant | −13.19 | DMEM + 10% FBS (MF-002-001) |
| Control C (expresses g, does not depend on it) | ACH-000026 | 253J-BV | Bladder/urinary tract / urothelial carcinoma (same lineage as D1) | +0.15 | −0.07 | 5.04 | — (NaN) | WT | −3.60 | DMEM + 10% FBS (MF-002-001) |

Next qualifying lines by the same rule if D1/D2 prove intractable: ACH-000243 (DAN-G, pancreas, −0.72 / −0.30), ACH-002677 (U-2946, lymphoid, −0.74 / −0.30), ACH-003177 (NRH-UPS1, soft tissue, −0.70 / −0.32), ACH-000788 (A2058, melanoma, −0.57 / −0.32). Substitutions must be recorded.

Important caveat for interpretation (not a deviation): **HCT116**, the line in which the mechanism was discovered [A23], has ANKRD52 −0.08 and AGO2 −0.08 †, i.e. it is a non-dependent line. The reporter phenotype and the fitness phenotype are therefore separable experiments in separable contexts; HCT116 is retained as the *reporter* context (where the published assay is validated) and D1/D2 as the *fitness* context.

- Common-essential genes: ANKRD52 is not common-essential, so acute depletion is used for timing control rather than out of necessity. A non-cancer context (RPE1-hTERT TP53⁻/⁻ with dTAG or AID2) is run in parallel for the reporter arm.
- **Baseline medium:** each line's own DepMap screen medium (table above). Interferon-γ stimulation (relevant to [A10]) and any stress condition are separate arms, never the baseline.
- **Essential-gene confound control (required):** degron depletion of ANKRD52 time-matched to AGO2 and PPP6C depletion, compared with a matched-essentiality control gene from an unrelated module: **MRPS35** (small mitoribosomal subunit; mitochondrial translation, unrelated to miRNA silencing), Chronos −0.671 in D1 and −0.534 in D2 against ANKRD52's −0.685 and −0.539 (max |Δ| 0.014 across the two lines; genome-wide mean −0.500 vs ANKRD52 −0.243) †. Every pathway readout must move beyond MRPS35's at matched growth inhibition.

## 3. Reagents

- **sgRNAs:** 3 independent guides per target (ANKRD52, PPP6C, AGO2, MRPS35), 2 non-targeting guides, AAVS1 cutting control. **Sequences are not listed:** the project holds no CRISPR library file and DepMap guide maps are unavailable (DESIGN §4.3, "not possible (recorded)"), so per-guide effects cannot be quoted; guides are taken from a published genome-wide library and concordance is established within the experiment.
- **Sequence-level off-target check (required):** genome-wide mismatch search for every guide (Cas-OFFinder or CRISPOR, GRCh38) with the acceptance rule fixed in advance — no perfect-match or 1-mismatch site in another protein-coding gene and specifically none in PPP6C, PPP6R1/2/3, ANKRD28, ANKRD44 (the close paralogues; ANKRD28/44 share extensive sequence identity with ANKRD52 [A8], so paralogue cross-targeting is the leading off-target risk here), AGO1/2/3 or MRPS35. Tool and output recorded with the result.
- **ANKRD52 guides must avoid the ci-ankrd52 intron.** Because the locus also encodes a functional circular intronic RNA [A17], guides are placed in coding exons outside the ci-ankrd52-generating intron, and the primary depletion modality is a **degron on the endogenous protein** (dTAG or AID2 knock-in), which leaves the RNA intact — this is what separates alternative 2 in Template A §8.
- **CRISPRi:** not required for copy number (g CN 1.04 / 1.05) but retained as a modality check.
- **Guide-resistant cDNA:** full-length ANKRD52 (1076 aa) with silent PAM/seed changes; an ankyrin-repeat-surface mutant series for Tier 3 (substrate-recognition hypothesis from [L4], [A9]).
- **AGO2 alleles:** homozygous knock-in of AGO2 5XA (S824–S834 serine/threonine → alanine) and, as a second allele, AGO2 S828A — both shown to rescue reporter silencing in ANKRD52-null cells [A22]; isogenic wild-type AGO2 re-knock-in as the matched control.
- **Antibodies / detection:** anti-AGO2 with **Phos-tag** electrophoresis (the published assay for the AGO2 phospho-shift [A3]); anti-PPP6C, anti-PPP6R1; endogenous HaloTag/mNeonGreen knock-in for ANKRD52 (no validated ANKRD52 antibody is established in the retrieved literature); markers for P-bodies (DDX6, EDC4) and nucleus/mitochondria (the three localisation sources disagree: HPA mitochondria+nucleoplasm, OpenCell cytoplasmic, Human Cell Map microtubule cytoskeleton — bundle §7).
- **Reporters:** the published miR-19 EGFP reporter with eight imperfect sites plus the site-less control [A23], and an endogenous let-7 target panel.

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of ANKRD52 with AGO2, PPP6C, PPP6R1 (ipTM/pDockQ) | days | Confident interface with PP6 subunits; weak/transient with AGO2 | No interface at all | **yes** | Predicted: high-confidence ANKRD52–PPP6R interfaces (Predictomes SPOC 0.974–0.997 †) and a weak ANKRD52–AGO2 score (0.329 †), consistent with enzyme–substrate rather than co-complex |
| 1 | Competitive growth (GFP mix), 3 guides plus guide-resistant cDNA rescue, D1/D2 vs 253J-BV | 2–3 wk | Dropout in D1/D2, none in the control line; rescued | No dropout, or no rescue (off-target, paralogue cross-targeting, or ci-ankrd52 effect) | **yes** | Modest, real effect expected: ~1.5–2-fold depletion of guide+ cells by day 21 in D1/D2 (Chronos −0.69/−0.54), none in 253J-BV (+0.15). Underpowered designs will miss this — ≥ 6 replicates and a 28-day window |
| 1 | **Essential-gene confound control:** degron depletion of ANKRD52 time-matched to AGO2 and PPP6C depletion, vs MRPS35 at matched growth inhibition | 2–4 wk | Phospho-AGO2 and reporter de-repression change beyond MRPS35's | Same as MRPS35 (general sickness) | **yes** | At 40–50% growth inhibition: Phos-tag p-AGO2 fraction up ≥ 2-fold within 24–48 h of degron addition [A3]; MRPS35 depletion leaves it unchanged |
| 1 | Localisation with markers (HaloTag knock-in) | 2–4 wk | Cytoplasmic with PP6 subunits and partial P-body overlap | Exclusively mitochondrial (as HPA's main call suggests) | **yes** | Resolves the three-way source disagreement (bundle §7); a strictly mitochondrial pool would argue against both PP6 and RISC-adjacent function |
| 1 | **Module-specific readout after depletion** (see §5) | 2–4 wk | Phenocopies AGO2 phospho-cycle inactivation: reporter de-repressed, p-AGO2 accumulated, miRNA levels unchanged [A4] | Reporter unchanged | **yes** | ≥ 1.5-fold EGFP de-repression for the eight-site reporter and none for the site-less control [A23]; small-RNA-seq shows unchanged mature miRNA abundance [A4] |
| 1 | Partner protein levels after ANKRD52 depletion (and the reverse) | 2 wk | PP6 subunits (PPP6C, PPP6R1) may co-destabilise (ANKRD52 is a PP6 subunit); AGO2 levels unchanged, only its phospho-state shifts | AGO2 protein destabilised | **yes** | Distinguishes the two memberships: co-destabilisation with PP6 (type a *for PP6*), phospho-shift only for AGO2 (type d for the predicted module) |
| 2 | IP-MS / TurboID of tagged ANKRD52 vs an unrelated tagged control | 1–2 mo | PP6 subunits enriched (SAINT); AGO1/AGO2 recovered sub-stoichiometrically and RNA-independently [A5] | Neither PP6 nor AGO recovered | **yes** | Quantifies the predicted asymmetry that the P class already shows (bundle §6): stoichiometric PP6, transient AGO2 |
| 2 | **Decisive: AGO2-5XA epistasis** — degron depletion of ANKRD52 in AGO2-5XA vs AGO2-WT isogenic D1/D2 | 1–2 mo | 5XA rescues the growth defect (the fitness requirement runs through the phospho-cycle) | 5XA rescues the reporter but not growth (PP6-general dependency) | **yes** | Competitive-growth rescue ≥ 70% of the non-targeting control in 5XA lines, < 20% in WT lines; reporter rescued in both [A22] |
| 2 | Arrayed CRISPRi Perturb-seq with partners (AGO2, DICER1, DROSHA, XPO5, TNRC6A, PPP6C) | 2 mo | ANKRD52's signature clusters with the miRNA-pathway perturbations rather than with PP6's other substrates | Clusters with PPP6C only, or is distinct | **yes** — this is the one G-class gap: ANKRD52 was **not perturbed** in any of the three Perturb-seq datasets (bundle §6), so this fills a "not measured" cell of the orthogonal matrix | Transcriptional signature correlation with AGO2 and DICER1 perturbations > with MRPS35; derepression of conserved miRNA-target sets |
| 3 | Ankyrin-repeat interface mutants fail to rescue; in vitro reconstitution of PP6c–PP6R–ANKRD52 dephosphorylating p-AGO2 | 6–12 mo | Substrate-recognition surface required; reconstituted holoenzyme dephosphorylates p-AGO2 S824–S834 | Mutants rescue; no activity on p-AGO2 in vitro | optional | Would convert the published cell-based mechanism [A1] into direct enzymology, which the retrieved literature does not contain |

Type-specific row (relationship type **d**, pathway member): Template B defines extra rows for types b, c and e only. For type d the pathway claim is carried by the Tier-1 module readout and the Tier-2 epistasis and Perturb-seq rows above.

## 5. Module readouts

The predicted module (GO:0031047 regulatory ncRNA-mediated gene silencing) is not one of the named rows of Template B §5, so the "Other" row applies.

| Module | Readouts |
|---|---|
| Other — regulatory ncRNA-mediated gene silencing / miRNA pathway | (i) miRNA-activity reporter: EGFP with eight imperfect miR-19 sites vs a site-less control, the assay that identified this gene [A23] (PMID:28114302, ledger rows A23/A6); (ii) **Phos-tag western for phospho-AGO2**, where "Deficiency of ANKRD52 or PPP6C in multiple human cell lines similarly led to accumulation of phosphorylated AGO2" [A3] (same PMID, ledger row A3); (iii) small-RNA-seq to show mature miRNA abundance is unchanged [A4], separating silencing competence from biogenesis; (iv) RNA-seq overlap with the AGO2-null upregulated gene set; (v) for the physiological arm, IFN-γ-pathway and SOCS1 readouts [A10] |

**Chosen readout:** Phos-tag p-AGO2 fraction (primary, fastest and most specific) with the miR-19 EGFP reporter (primary functional) and small-RNA-seq (specificity control), all against MRPS35 at matched growth inhibition.

## 6. Experiment that separates the alternative explanation

- **Alternative A (strongest):** the dependency is PP6-general — mediated by Aurora A [A20], MEK [A18] or PAK1 [A14] — and the miRNA-pathway co-dependency is correlative.
  **Experiment:** the Tier-2 AGO2-5XA epistasis above, plus parallel measurement of Aurora A T-loop phosphorylation, MEK and PAK1 phosphorylation after ANKRD52 degron depletion.
  **Readout if the prediction is right:** AGO2-5XA rescues growth; Aurora A / MEK / PAK1 phospho-states are little changed by ANKRD52 loss (they are PP6R/ANKRD28-dependent rather than ANKRD52-dependent).
  **Readout if the alternative is right:** growth is not rescued by AGO2-5XA, and one of the other substrates shows an ANKRD52-dependent phospho-shift of comparable size.
- **Alternative B (locus-level):** the DepMap signal reflects loss of the circular intronic RNA ci-ankrd52 [A17] rather than of the protein.
  **Experiment:** degron depletion of the ANKRD52 protein (RNA intact) compared with exonic CRISPR cutting, and, conversely, antisense knockdown of ci-ankrd52 with the protein intact.
  **Readout if the prediction is right:** degron depletion reproduces both the growth and the p-AGO2 phenotype; ci-ankrd52 knockdown alone does neither.
  **Readout if the alternative is right:** only cutting (not degron) produces the fitness defect, and ci-ankrd52 knockdown reproduces it.

## 7. Decision rule (fixed in advance)

- **Supported:** dropout in D1/D2 rescued by guide-resistant cDNA **AND** module-specific readout concordant (p-AGO2 accumulation and reporter de-repression beyond MRPS35 at matched growth inhibition) **AND** localisation compatible (a cytoplasmic/nuclear pool coexisting with PP6 subunits) **AND** Tier-2 physical or epistatic support (PP6 subunits plus sub-stoichiometric AGO2 by IP-MS, or AGO2-5XA epistasis).
- **Refuted:** a dropout that is not rescued, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else — reported as such. The most likely ambiguous outcome here is "module assignment confirmed, fitness mechanism not" (reporter rescued by AGO2-5XA, growth not), which would keep relationship type **d** for the module while attributing the dependency to PP6's wider substrate set.

## 8. Evidence ledger

All rows verified as described in `reports/ANKRD52.md` Appendix A (Europe PMC resolution + verbatim span match; `results/m7/scratch_reports_trappc5/verify.py`).

| Claim | Source | Verbatim span | Verified |
|---|---|---|---|
| The miR-19 EGFP reporter assay reports on this module (and its site-less control) | PMID:28114302 / 10.1038/nature21025 | "Enhanced green fluorescent protein (EGFP) transcripts with or without a 3' untranslated region (UTR) harboring eight imperfectly complementary binding sites for miR-19, an abundant miRNA, were expressed in the stably diploid cell line HCT116" (full text) | Y |
| Phos-tag p-AGO2 accumulation is the direct readout of ANKRD52/PPP6C loss | PMID:28114302 | "Deficiency of ANKRD52 or PPP6C in multiple human cell lines similarly led to accumulation of phosphorylated AGO2" (full text) | Y |
| Mature miRNA abundance is unchanged — the specificity control | PMID:28114302 | "The steady-state abundance of representative miRNAs was not decreased" (full text) | Y |
| Non-phosphorylatable AGO2 alleles rescue silencing in ANKRD52-null cells (basis of the decisive experiment) | PMID:28114302 | "expression of AGO25XA or AGO2S828A, but not wild-type AGO2, rescued repression of the miR-19 EGFP reporter in ANKRD52" (full text) | Y |
| The AGO2 interaction is RNA-independent (IP-MS design) | PMID:28114302 | "AGO2 and ANKRD52-PPP6C interacted in an RNA-independent manner" (full text) | Y |
| ANKRD28/44/52 are extensively similar — paralogue off-target risk | PMID:18186651 / 10.1021/bi7022877 | "Mass spectrometry identified coprecipitating proteins as PP6 catalytic subunit and three ankyrin repeat proteins (Ankrd28, Ankrd44, and Ankrd52)." (abstract) | Y |
| PP6's regulatory subunits determine substrate specificity (interface-mutant rationale) | PMID:18186651 | "We propose that the SAPS and ankyrin repeat regulatory subunits determine the function and specificity of PP6." (abstract) | Y |
| PP6 has other substrates — Aurora A (alternative-explanation arm) | PMID:21187329 / 10.1083/jcb.201008106 | "We find that the protein phosphatase 6 (PP6) holoenzyme is the major T-loop phosphatase for Aurora A, an essential mitotic kinase." (abstract) | Y |
| PP6 has other substrates — MEK (alternative-explanation arm) | PMID:33789117 / 10.1016/j.celrep.2021.108928 | "we identify PPP6C, a phosphatase frequently mutated or downregulated in melanoma, as a major MEK phosphatase in cells exhibiting oncogenic ERK pathway activation" (abstract) | Y |
| PP6/ANKRD52 also acts on PAK1 (alternative-explanation arm) | PMID:33096142 / 10.1016/j.bbamcr.2020.118891 | "Knockdown of ANKRD52 or PP6c resulted in upregulated PAK1 phosphorylation." (abstract) | Y |
| The locus encodes a functional circular intronic RNA (guide placement and degron rationale) | PMID:24035497 / 10.1016/j.molcel.2013.08.017 | "One abundant such RNA, ci-ankrd52, largely accumulates to its sites of transcription, associates with elongation Pol II machinery, and acts as a positive regulator of Pol II transcription." (abstract) | Y |
| Physiological (IFN-γ/SOCS1) readout arm | PMID:34853298 / 10.1038/s41467-021-27331-3 | "Genetic inactivation of the machinery or re-introduction of ANKRD52 frequent patient mutations dampens the JAK-STAT-interferon-γ signaling and antigen presentation in cancer cells, largely by abolishing miR-155-targeted silencing of suppressor of cytokine signaling 1 (SOCS1)." (abstract) | Y |
| Cell lines, effects, expression, CN, TP53 status, screen quality, media | `reports/data/ANKRD52/bundle.md` §10 (DepMap `CRISPRGeneEffect.csv`, `Model.csv`, `OmicsExpression…`, `OmicsCNGeneWGS.csv`, `CRISPRConfounders.csv`) | machine-generated table; not retyped | Y |
| MRPS35 as the matched-essentiality control; HCT116 non-dependence | `results/m7/scratch_reports_trappc5/{ctrl2.py,lines.py}` outputs † | ANKRD52 [−0.685, −0.539] vs MRPS35 [−0.671, −0.534], max \|Δ\| 0.014; HCT116: ANKRD52 −0.08, AGO2 −0.08 | Y |

## 9. Red-team review

**pending** — separate agent; to be appended unedited.

- Reviewer / model / date: pending
- Review text: pending
- PI response: pending
