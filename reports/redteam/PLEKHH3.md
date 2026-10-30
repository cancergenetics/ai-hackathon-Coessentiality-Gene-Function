# Red-team review — reports/PLEKHH3.md

Reviewer role: `red_team` (adversarial, did not write the report). Date: 2026-10-30.
Scope: `reports/PLEKHH3.md` (Parts I and II, Appendix A). The report was not edited.

**Method.** Every PMID/DOI in Appendix A and in the Part II ledger was re-resolved through the Europe PMC REST API by the reviewer, independently of the authors' `verify.py` (fresh `fullTextXML` / `resultType=core` fetches; markup stripped, whitespace collapsed, spans matched as substrings). Numbers were recomputed from `data/raw/depmap/CRISPRGeneEffect.csv`, `OmicsSomaticMutationsMatrixDamaging.csv`, `OmicsSomaticMutationsMatrixHotspot.csv`, `Model.csv`, `data/raw/humap3/*`, `data/raw/predictomes2025/*`, `data/raw/string/*`, `data/raw/bioplex/*`, `data/derived/neighbours/full_top100.npz`, `data/derived/paralogues_by_matrix_index.npz` and `results/ledger/*`. UniProt Q7Z736 was re-fetched from `rest.uniprot.org`.

---

## 1. Ledger spot-check (20 entries checked; 19 Appendix-A rows + the Part II rows)

**Result: no failures.** All 19 Appendix-A keys (A-P1…A-P19) and all seven rows of the Part II ledger resolve to a real record, and every quoted span is present verbatim in the cited article after the declared normalisation. A-P4, A-P5, A-P6 and A-P13 match only after subscript markup is stripped — which the rows themselves declare ("subscript markup removed"). Checked in detail:

- **A-P1 / A-P2 (PMID 14516276)** — both spans in the abstract; the record is the TAPP1/PTPL1 paper and the "first PDZ domain" wording (including the source's own typo "though") is reproduced exactly. The report's use of it to motivate the fourth-ranked GO term (PDZ domain binding) is legitimate.
- **A-P3 (PMID 21204784)** — "function as negative regulators of the insulin and PI3K signalling pathways" is verbatim; this is the knock-in genetics the direction claim rests on. Supports the claim as worded.
- **A-P4 (PMC5678281)** and **A-P6 (PMC6400549)** — PTEN as a PI(3,4)P₂ 3-phosphatase, both verbatim. Correctly used to justify controlling PTEN status in the lipid readout rather than to claim anything about PLEKHH3.
- **A-P7 / A-P8 (PMC9547923)** — PLEKHH2/β-arrestin1/FERM and "promoted the activity of the PI3K/AKT pathway" both verbatim. Crucially, the report states the direction conflict explicitly ("PLEKHH2 is reported as a *positive* regulator … whereas the co-essentiality direction for PLEKHH3 is negative"). That is the correct reading and is to the report's credit.
- **A-P9 (PMID 35348689)** — verbatim, and the report correctly refuses to assert MAX-1/PLEKHH3 orthology ("no orthology assignment … was verified here, and none is claimed"). A weaker report would have claimed it.
- **A-P11, A-P12, A-P13** — fusion case report, segregating truncating variant and bioinformatic nomination, all verbatim, all correctly labelled "mention" and explicitly "not counted".

**Independent literature sweep (reviewer).** Europe PMC `"PLEKHH3"` = 97 records; `"PLEKHH3" AND (PI3K OR AKT OR PTEN OR phosphoinositide)` = 30, every one an omics/association mention; `SRC:PPR` = 3, none functional. The N3 class and the statement that no functional study of PLEKHH3 exists are **upheld**. Agent L's search for this gene, unlike the CCDC71L one, appears complete.

---

## 2. Recheck of numbers

All of the following were reproduced exactly.

| Claim in report | Reviewer value | Verdict |
|---|---|---|
| Mean Chronos **+0.087** / SD 0.160, median +0.078, min −0.533, 2/1,361 < −0.5, NaN 0 | +0.087 / 0.160 / 2 (0.0015) / 0 NaN | ✔ |
| **r(PLEKHH3, PTEN) = 0.400**, **r(PLEKHA1) = 0.424**, TSC1 0.240, TSC2 0.246, DDIT4 0.193, PTPN13 0.117 | 0.400 / 0.424 / 0.240 / 0.246 / 0.193 / 0.117 | ✔ |
| Partner means PTEN +0.377, PLEKHA1 +0.219, DDIT4 +0.039, TSC1 +0.002, PTPN13 +0.006, TSC2 −0.118, FOXO3 −0.271 | identical to 3 d.p. | ✔ |
| **Within PTEN-WT r = 0.390 (n = 1,215); within PTEN-damaging-mutant r = 0.354 (n = 146)** | 0.390 / 1,215 and 0.354 / 146, using default-entry rows of `OmicsSomaticMutationsMatrixDamaging.csv` | ✔ |
| PLEKHH1 r = 0.049, PLEKHH2 r = −0.123; 0 paralogues in the project list | 0.049 / −0.123; `paralogues_by_matrix_index.npz` returns an empty list for index 11610 | ✔ |
| Top-10 partners and zavg_BEF (PLEKHA1 24.40 … ZNF608 7.55) | identical from `full_top100.npz` row 11610 | ✔ |
| Supporting partners = PLEKHA1, PTEN, PTPN13; PTEN hub-flagged; CN r −0.03 / −0.00 / 0.02 | identical in `u_flag_partners.tsv` (PTEN `hub_flag` True, `any_flag` True) | ✔ |
| Terms: S 56.363 / 44.012 / 44.012, sizes 172 / 49 / 185, LOPO 0/3 | identical in `u_top5.tsv` | ✔ |
| p_cal 0.0757 [0.030–0.127], rank 12, no demotion, R 0.264, RBO 0.560, hub share 0.35 | identical in `top40_primary.tsv` / `bundle.md` | ✔ |
| SLC30A5 −0.555 (JURKAT) / −0.663 (PANFR0034), mean +0.013, SD 0.174 | −0.555 / −0.663 / +0.013 / 0.174 | ✔ |
| JURKAT g = −0.51, PANFR0034 −0.53, LP-1 +0.27; PLEKHA1 +0.14 / +0.20 / −0.01 | −0.506 / −0.533 / +0.272; +0.138 / +0.198 / −0.010 | ✔ |
| **JURKAT carries 2 damaging PTEN mutations, 0 hotspot; PANFR0034 and LP-1 carry none** | exactly so (damaging 2 / 0 / 0; hotspot 0 / 0 / 0) | ✔ |
| hu.MAP 3.0: 8 complexes, all receptor/membrane; 01062.1 = PTPRD+TGFBR2+g (conf 1); 09249.1 = BMPR1A+ACVR2B+g; 11149.1 = 32 subunits | 8 complexes, all receptor clusters; all three descriptions exact | ✔ |
| Predictomes: **134** scored pairs; **no pair with PTEN, PLEKHA1 or PTPN13** | 134 pairs; zero pairs with any of the three | ✔ |
| Top KIRC: TGFBR2 0.696, SKAP1 0.634, MAPK4 0.618, EFNB2 0.618 | exactly these | ✔ |
| BioPlex3 degree 46 incl. ACVR2B, TGFBR2, AMHR2, FLRT1; STRING-exp degree 6 (CCNF, CDC123, EFNB2, SKAP1, SOX2, TGFBR2) | confirmed; STRING-exp = exactly those 6 at experimental score ≥ 400 (EFNB2 509, TGFBR2 487, CDC123 457, SOX2 457, CCNF 457, SKAP1 433; next is SEMA3C at 380) | ✔ |
| UniProt: 793 aa, score 3.0, PH 95–199, MyTH4 237–399, FERM 404–754, signal-peptide keyword present | all exact — and note it is a **sequence feature `Signal 1–18`**, not merely a keyword | ✔ (see §3.6) |

**Errors found (two, both in the "reported but not counted" paragraph of §6):**

1. **The Predictomes SPOC list is wrong because it is ranked by the wrong column.** The report writes: "the highest KIRC scores are receptor-ligand-like (TGFBR2 0.696, SKAP1 0.634, MAPK4 0.618, EFNB2 0.618) with **low SPOC except MAPK4 (0.556), EFNB2 (0.429), BTNL9 (0.486)**". Those three values are individually correct, but they are not the high-SPOC pairs. Ranked by SPOC, PLEKHH3's top pairs are **GPRC5B 0.617, RFXANK 0.569, TMEM9B 0.557**, then MAPK4 0.556, KCNE3 0.551, SOX2 0.532, TMED7 0.515, UBXN6 0.510, PTGES3 0.510 — four pairs above MAPK4 are omitted. RFXANK is additionally a BioPlex interactor of PLEKHH3 (HCT116 network, pInt 0.798), so that pair is reproducible across two sources and is the single most interesting structural hit for this gene.
2. **A relevant positive is omitted.** The report says there is no Predictomes pair with PTEN/PLEKHA1/PTPN13 (true), but does not mention **PLEKHH3–PTGES3, SPOC 0.510**, where PTGES3 is a rank-21 co-dependency partner (z 5.36) in g's own N(g). It is the only Predictomes pair linking g to anything in its co-essentiality neighbourhood and should be reported.

**One labelling caveat (pipeline, not report).** §4 calls GO:0051896 "the **most specific term in the top 5**" — faithfully copied from `bundle.md`, which implements DESIGN §3.1's definition ("ancestors of a ranked descendant dropped"). But GO:0051896 has 172 members while GO:0030165 in the same top 5 has 48. Add half a clause so a reader does not take "most specific" to mean "smallest".

---

## 3. Attacks

### 3.1 Co-advantage interpretation — I tried to break it and failed; the report is *under*-claiming

The obvious attack on a co-advantage signal is that it is generic: lines in which deleting any growth brake helps will show correlated positive effects across all brakes, producing a "pathway" that is really just a proliferation covariate. **This attack does not work here, and the evidence that refutes it is not in the report.**

Correlations of PLEKHH3's profile with classic tumour suppressors across all 1,361 lines:

| specific to PI3K/mTOR | r | generic suppressors | r |
|---|---|---|---|
| PLEKHA1 | **0.424** | NF2 | 0.172 |
| PTEN | **0.400** | NF1 | 0.127 |
| TSC2 | 0.246 | RB1 | 0.053 |
| TSC1 | 0.240 | APC | 0.021 |
| NPRL2 (GATOR1) | 0.204 | TP53 | **0.014** |
| DDIT4 | 0.193 | ARID1A | 0.015 |
| DEPDC5 (GATOR1) | 0.187 | SMAD4 | −0.049 |
| PTPN13 | 0.117 | CDKN2A | −0.051 |
| | | **PIK3CA** | **−0.186** |

Two things follow. First, **PLEKHA1 and PTEN are the #1 and #2 correlates of PLEKHH3 among all 18,433 genes in the matrix** — not merely high-ranking, the top two. Second, the signal is confined to the PI3K/mTOR brake set and is absent for TP53, RB1, APC, CDKN2A and SMAD4, while the pathway's *accelerator* PIK3CA runs in the opposite direction (−0.186), exactly as a brake should. A generic proliferation covariate cannot produce that pattern. This is the strongest single argument the report has and it appears nowhere in it; §3 reports only the six partner correlations.

This does not dispose of the type-e reading (see 3.4) — a *PI3K-pathway-specific* state covariate remains consistent with everything above — but it does dispose of the lazy version of it, and it should be in §3 and §8.

### 3.2 Hub PTEN and LOPO 0/3 — real, but the right diagnosis is non-independence, not hub-ness

The report treats the hub share of 0.35 and LOPO 0/3 as separate worries. They are the same worry, and it can be quantified: **r(PTEN, PLEKHA1) = 0.453**. The three supporting partners are not three independent observations.

Partial correlations (reviewer recomputation):

- r(PLEKHH3, PTEN | PLEKHA1) = **0.257**
- r(PLEKHH3, PLEKHA1 | PTEN) = **0.298**

Both survive, so neither partner is a pass-through of the other and the module is not a single-gene artefact — but the effective support is roughly **two** partners, not three, and the LOPO 0/3 result is the arithmetic consequence of two correlated partners carrying a term that needs ≥ 2 supporting partners to be reportable at all. Stating it this way is both more honest and less alarming than "loses its rank if any one of them is removed".

Separately: the §4.3 built-in exclusion fires when ≥ half of the supporting partners are flagged. With 1 of 3 flagged (PTEN, hub), this prediction is **one flag away from exclusion**. `bundle.md` line 127 records "flagged: PTEN" explicitly. §5 should say so.

### 3.3 LOPO fragility vs lineage robustness — and the pre-registered check tests the wrong lineage

The report's §5 note ("Robustness to *line* resampling … is not robustness to *partner* resampling, and only the former is a pre-registered check") is exactly right and is the best sentence in the report. I can sharpen it in the report's favour and against it simultaneously.

**Against:** the pre-registered lineage leave-out removes Myeloid, because DEVIATIONS 2026-10-29 defines the removed lineage as the one with the lowest mean effect of g. For a gene whose effect is centred at +0.087, "lowest mean effect" picks the least growth-advantaged lineage, which has no particular relationship to where the *correlation* lives. The check as run is close to uninformative.

**In favour:** a proper influence jackknife passes easily. Removing each lineage with n ≥ 20 in turn changes r(PLEKHH3, PTEN) by at most **−0.024** (Bone, n = 59) and r(PLEKHH3, PLEKHA1) by at most **−0.028** (Bone). Lineage-demeaning every profile leaves r(PTEN) = **0.380** and r(PLEKHA1) = **0.392**. The call is far more lineage-robust than the pre-registered check demonstrates. **Report the jackknife and the demeaned correlations instead of leaning on the single pre-registered removal.**

### 3.4 Type-e regulatory co-dependency — the right leading alternative, but the discriminator has a hole

The report is correct that type e is the leading alternative and that the designed discriminator (pAKT output at matched growth effect) is the right one. The hole is in "matched":

> "At growth effect matched within ±15%: ≥ 1.5-fold change in pAKT-S473/total AKT … SLC30A5-depleted cells within ±1.2-fold"

The decisive measurement is to be made in the two added **PTEN-wild-type signalling backgrounds**, where the report itself says "the growth read-out in them is expected to be near zero — which is the point". If PLEKHH3 depletion has no fitness effect in those lines, "growth effect matched within ±15%" is undefined there, and SLC30A5's matching (−0.555 / −0.663, measured in JURKAT and PANFR0034) does not transfer: SLC30A5's genome-wide mean is +0.013, so it is a *selectively* essential gene whose effect in an arbitrary PTEN-WT line is unknown. The matched-essentiality control has to be re-derived in whichever lines are actually used, and the decision rule needs a second branch for the zero-growth-effect case (e.g. matching on a titrated CRISPRi knockdown depth rather than on growth). As written, the required confound control is not executable in the backgrounds where the decisive readout is taken.

### 3.5 Cell-line choice — the report's most serious weakness, and worse than it states

The report already flags that the rule had to be relaxed, that JURKAT is PTEN-deficient, and that PANFR0034's screen quality is poor (NNMD −1.71). All true. But the decisive fact is missing: **within-lineage, the predicted co-dependency does not exist in the lineage the chosen lines come from.**

Within-lineage correlations (lineages with n ≥ 60):

| lineage | n | r(PLEKHH3, PTEN) | r(PLEKHH3, PLEKHA1) |
|---|---|---|---|
| Skin | 75 | 0.550 | 0.510 |
| CNS/Brain | 133 | 0.518 | 0.455 |
| Ovary/Fallopian Tube | 62 | 0.465 | 0.409 |
| Lung | 126 | 0.458 | 0.367 |
| Breast | 67 | 0.451 | 0.627 |
| Pancreas | 71 | 0.446 | 0.136 |
| Esophagus/Stomach | 96 | 0.444 | 0.145 |
| Head and Neck | 77 | 0.379 | 0.437 |
| Bowel | 85 | 0.261 | 0.022 |
| **Lymphoid** | **97** | **−0.037** | **+0.020** |

The co-dependency is present in essentially every solid lineage and **absent in Lymphoid**. The rule-selected primary line **JURKAT is Lymphoid** — and PTEN-damaged — and the rule-selected non-dependent control **LP-1 is Lymphoid** as well. Two of the three named lines are drawn from the one lineage in which the predicted relationship does not hold. The report's remedy ("the specific models are to be fixed from the DepMap tables at execution time") leaves the decisive experiment with no named background at all, which is also the one place where a pre-registration is most needed.

**Fix:** name the PTEN-wild-type backgrounds now, using the report's own stated criteria plus one more — lineage in which r(PLEKHH3, PTEN) > 0.4 — which points at CNS/Brain, Skin, Lung, Breast and Ovary. Demote JURKAT from "dependent line" to what the data say it is: a negative-lineage, PTEN-null control that should show the *smallest* signalling effect if the hypothesis is right.

### 3.6 The UniProt signal peptide is a topology problem the plan does not test

§2 notes the signal-peptide keyword as "an unusual combination … worth checking experimentally". It is stronger than a keyword: UniProt Q7Z736 carries an actual sequence feature **`Signal 1–18`**. If that annotation is real, the PH (95–199), MyTH4 and FERM domains are lumenal/extracytosolic and *cannot* read cytosolic PI(3,4)P₂ — which would invalidate the mechanism, not merely the refinement. The §7 decision rule mentions "exclusively lumenal/secreted" under "Refuted", but every Tier-1 and Tier-2 arm (membrane recruitment, biosensor co-timing, recombinant PH lipid binding) presupposes cytosolic topology, and none tests it. Add a cheap topology assay at step 0 — protease-protection of the endogenous knock-in, or N-glycosylation-site scanning — alongside the PH-domain alignment that is already step 0. It costs days and gates two months of work.

### 3.7 Missing supportive evidence inside the project's own data

§4 stops at the top 10 partners. At K = 25 the neighbourhood also contains **AKT1S1 (PRAS40, rank 11, z 7.13)** and **GRB10 (rank 19, z 5.51)** — two further direct brakes/substrates of the AKT–mTORC1 axis. AKT1S1 is literally the protein whose phosphorylation (pPRAS40-T246) the Part II readout proposes to measure. Together with NPRL2 and DEPDC5 (§3.1 above), the pathway coherence of the neighbourhood is materially stronger than the "seven of the top ten" statement in §4. Include them.

### 3.8 AP-MS stickiness

Lower risk than for the companion report: a BioPlex degree of 46 dominated by single-pass receptors is a normal profile for a membrane-proximal FERM bait, not a basic-patch artefact, and the report does not over-read it. Two gaps: the Tier-2 bait control is only "an unrelated tagged control" — for a 793-aa membrane-associated FERM protein this must be a membrane-localised control of comparable size, not a soluble one; and the plan should state whether TurboID or AP-MS is primary, since the receptor-heavy prior from BioPlex came from AP-MS and a proximity method would not be comparable to it.

### 3.9 Weak experiments

- Tier 1 competitive growth is correctly demoted to "control, not endpoint" (§1), with a clear statement that a null does not refute. Good.
- Tier 2 drug-interaction grid: "≥ 2-fold IC50 shift" from a gene whose mean effect is +0.087 is optimistic and unpowered; state the expected effect size or make the arm contingent.
- The PH-domain point mutant is undefined ("the specific residue number … is not asserted here"). This is honest, but it means the specificity control for the lipid-binding arm, the Tier-3 rescue experiment and the §7 "Ambiguous → type c" branch all depend on an alignment that has not been done. Do the alignment before the plan is costed.

---

## 4. Verdict

**ACCEPT WITH REVISIONS.**

Every number I could recompute matched to three decimal places, the ledger is clean, the N3 novelty claim survives an independent literature sweep, and the report is candid about the three things that actually threaten it (LOPO 0/3, hub PTEN, near-zero fitness amplitude). My attacks mostly *strengthened* the biological call — the co-advantage signal is specific to the PI3K/mTOR brake set rather than generic, and is robust to lineage removal and lineage-demeaning — while exposing one genuine defect that the report does not see: the decisive experiment is specified in the one lineage where the predicted relationship is absent.

### Required fixes (in order)

1. **Re-specify the decisive experiment's cell lines, and name them.** Within-lineage r(PLEKHH3, PTEN) is −0.037 in Lymphoid (n = 97) and 0.45–0.55 in CNS/Brain, Skin, Lung, Breast and Ovary. JURKAT (primary "dependent" line, PTEN-damaged) and LP-1 (control) are both Lymphoid. Name PTEN-wild-type solid-lineage backgrounds now, add "lineage r > 0.4" to the selection rule, re-derive the matched-essentiality control in those lines, and add a decision branch for the case where PLEKHH3 loss has no fitness effect there (matching on knockdown depth, not on growth).
2. **Add the specificity and robustness evidence that is missing, and re-frame LOPO.** PTEN and PLEKHA1 are g's #1 and #2 correlates among 18,433 genes; the signal is confined to the PI3K/mTOR brakes (TSC1/2 0.24, NPRL2 0.20, DEPDC5 0.19, DDIT4 0.19) and absent for TP53 0.014 / RB1 0.053 / APC 0.021 / CDKN2A −0.051, with r(PIK3CA) = −0.186. Report the lineage jackknife (max |Δr| 0.028) and lineage-demeaned r (0.380 / 0.392) in place of the uninformative pre-registered Myeloid removal. Report r(PTEN, PLEKHA1) = 0.453 and the partial correlations (0.257 / 0.298) so LOPO 0/3 reads as "≈ 2 effective partners", and note that the §4.3 exclusion is one flag away from firing.
3. **Correct §6 and close two gaps in Part II.** PLEKHH3's highest SPOC pairs are GPRC5B 0.617, RFXANK 0.569 and TMEM9B 0.557 — not MAPK4/EFNB2/BTNL9, which are the KIRC-ranked set; RFXANK is also a BioPlex interactor, and PLEKHH3–PTGES3 (SPOC 0.510) links g to a rank-21 co-dependency partner and should be reported. Add AKT1S1 (rank 11) and GRB10 (rank 19) to the §4 neighbourhood narrative. Add a topology test for the `Signal 1–18` sequence feature at step 0, before any lipid-binding or membrane-recruitment arm is run.
