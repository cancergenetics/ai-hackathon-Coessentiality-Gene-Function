# Red-team review: reports/TM2D2.md (including the shared module analysis in §12 and the M-ledger)

- Reviewer: adversarial reviewer agent (role `red_team`), model Claude Opus 5.5
- Date: 2026-10-30
- Scope: Appendix A.1 (M1–M83) and A.2 (Q1–Q43); numbers against `reports/data/TM2D2/bundle.md`, `reports/data/TM2D_module/{module.md,CHIC2_bundle.md}`, `results/m7/scratch_reports_tm2d/{lines_out,ctrl_out}.txt`, `results/ledger/M6_SUMMARY.md`, `results/holdout_eval/SUMMARY.md`; the hypothesis; the Part 2 plan.
- Independence: I did not write the report. PMIDs were resolved through the Europe PMC REST API. Correlations and own-locus copy-number tests were recomputed from `data/raw/depmap/` (`reports/redteam/tm2d_rt_corr.py`, `tm2d_rt_cn.py`).

---

## 1. Ledger spot-check (28 rows)

| # | Row | Check | Result |
|---|---|---|---|
| 1 | M15–M18 TM2D3: ER protein; ATF4/HSPA5/DDIT3; ER swelling; ER-stress sensitivity | **PMID 40449487 exists**: Gabillard-Lefort C et al., *Am J Hum Genet* 2025, "Bi-allelic variants in TM2D3 cause a severe syndromic neurodevelopmental disorder associated with endoplasmic reticulum and mitochondrial abnormalities", DOI 10.1016/j.ajhg.2025.05.004; all four spans are in the abstract | **PASS** |
| 2 | M26 LoF in TM2D1/2/3 associated with CN-LOH in cis | **PMID 42156563 exists**: Tang D, Kamitaki N, … Loh P-R, *Nat Genet* 2026, DOI 10.1038/s41588-026-02592-0; span is in the full text | **PASS on the span**. The paper also says the CN-LOH events "may generate a proliferative advantage via dysregulation of NOTCH1". §0 states "*selected for*" without this hedge and without the Notch mechanism the authors propose. |
| 3 | M27 TM2D1 penetrance 27% | same | **PASS** |
| 4 | M28 TM2D3 CN-LOH locus | PMID 32581363 | **PASS on the span**. §7.3's "(TM2D3 was the first such locus [M28])" is not in the source, which lists six loci. |
| 5 | M24, M25 phagocytosis screen; TM2D2/3 KO clear Aβ poorly | PMID 30397336 / PMC6719718 full text | **PASS** |
| 6 | M5–M12 Salazar 2021 (fly family, orthology, co-IP/MS, IMPC lethality) | PMID 34905536 | **PASS** |
| 7 | M13, M14 TM2D3 activates Notch1; surface Notch1/2 reduced | PMID 38016980 | **PASS** |
| 8 | M19, M20 P155L LOAD; abolishes rescue | PMID 27764101 | **PASS** |
| 9 | M21–M23 almondex Notch distribution; NICD rescue | PMIDs 31782145, 18331889 | **PASS** |
| 10 | M29–M31 AUP1 (HRD1–SEL1L; ER + LD; UBE2G2) | PMIDs 21857022, 34879065 | **PASS** |
| 11 | M33 Aup1 knockdown raises ER-stress genes (zebrafish) | PMID 40484276 | **PASS** (cross-species, labelled as such) |
| 12 | M34, M35 JOSD1 membrane DUB; protective at the plasma membrane | PMIDs 23625928, 39284830 (hepatic proteotoxicity) | **PASS** |
| 13 | M36 CHIP in ER quality control | PMID 11146634 | **PASS** |
| 14 | M37, M38 STUB1–CHIC2 complex | PMIDs 36108743, 40796662 | **PASS** |
| 15 | M39, M40 CHIC2 attenuates CHIP (preprint) | DOI 10.1101/2023.07.17.549407 | **PASS** (preprint, not peer-reviewed; should be marked as such) |
| 16 | Q5 Daphnia TM2D2 KO | PMID 42248690 (*Genome Res* 2026) | **PASS** |
| 17 | M45, M50, M51 hu.MAP / Predictomes rows | project files | **PASS** |
| 18 | M53–M56 module table, 103 edges, 6 physical | `module.md` | **PASS** |
| 19 | M61–M64, M78 raw r rows | recomputed independently | **PASS**: TM2D2–JOSD1 0.22, TM2D2–AUP1 0.27, TM2D2–UBE2G2/SEL1L/SYVN1 −0.02/0.03/0.01, STUB1–CHIC2 0.34 |
| 20 | M76 NOTCH1/PSEN1/NCSTN means | `lines_out.txt` | **PASS** (numbers right; inference wrong, see §3.4) |
| 21 | Q9–Q16 term, p_cal, tie, LOPO, DEMETER2 fail, GLS same, lineage, TP53 | bundle | **PASS** |
| 22 | Q21–Q24 YD-8, ETCC-016, SNU-46, MAPAC/LXF | bundle | **PASS** |
| 23 | Q31 MEN1 control (−0.91/−0.66; r 0.049) | `ctrl_out.txt` | **PASS** |
| 24 | Q32/M83 effects in chosen lines | `lines_out.txt` | **PASS** |
| 25 | Q2–Q4, Q40 topology | UniProt Q9BX73 | **PASS** |
| 26 | Q25 recall probe | file | **PASS** |
| 27 | Q26–Q29 judging | judge files | **PASS** |
| 28 | M65–M70 calibration/hold-out facts | summaries | **PASS** |

All PMIDs and DOIs resolve, and all spans are present. The failures are interpretive: the "first such locus" over-reading (M28), the dropped NOTCH1 hedge (M26), and a preprint that is not labelled as one (M39/M40).

## 2. Numbers

- **Confirmed:**
  - TM2D1/2/3 against UBE2G2, SEL1L and SYVN1: |r| ≤ 0.03.
  - AUP1 against the same core: 0.25–0.39.
  - TM2D trio: r 0.41–0.51.
  - TM2D2–JOSD1: 0.22. TM2D1–JOSD1: 0.17.
  - Mean/SD −0.227/0.228, fraction < −0.5 0.0977, R(g) 0.272, p_cal 0.0503 (0.016–0.098).
  - The chosen lines follow the bundle's rule.
- **Selective reporting in §12.4.** The section gives the TM2D–AUP1 and TM2D–JOSD1 raw r values but leaves out the STUB1 and CHIC2 values: TM2D2–STUB1 0.20 (genome-wide raw rank 39), TM2D1–STUB1 0.10 (rank 234), TM2D2–CHIC2 0.14 (rank 252), TM2D1–CHIC2 0.09. It also omits that the partners hardly co-vary with each other: JOSD1–AUP1 0.07, AUP1–STUB1 0.12, JOSD1–STUB1 0.13.

## 3. Attack on the hypothesis

1. **Paralogue artefact.** TM2D1–TM2D2 zavg_BEF is 31.7 (raw 0.51), and TM2D2–TM2D3 raw r is 0.51. The built-in exclusion stops the paralogue from carrying the term. But two of the top-40 slots, plus CHIC2's ranks 2–4, all describe one TM2D-complex observation. The report says this, yet the top-40 statistics still count the observation twice. Paralogue guide cross-cutting is said to be "not available locally"; the Avana guide map is public, so this check can be done.
2. **Hub-driven partners.** Ruled out. Partner in-degrees are JOSD1 39, AUP1 46 and STUB1 57, against TM2D2's own 62; hub share is 0. STUB1 is a promiscuous E3 ligase biologically, but it is not a network hub here.
3. **Copy number and lineage.** Ruled out. I tested own-locus copy number (8p11.22 is often lost; YD-8 CN 0.61): Spearman ρ(TM2D2 effect, CN) = 0.015 (p 0.6), and dependent lines have median CN 0.98, so there is no CYCLOPS effect. Partner copy number has r ≤ 0.05. Lineage leave-out (Head and Neck) is retained.
4. **Over-reading of "response to ER stress".**
   - The term rests on two partners, LOPO 0/2.
   - It is tied with ERAD, which the report itself considers least likely.
   - DEMETER2 fails (mean partner r −0.039).
   - TM2D2 has no raw co-dependency with any UPR sensor or effector: HSPA5 0.00, ERN1 −0.05, ATF6 −0.03, EIF2AK3 −0.03, XBP1 −0.09, ATF4 −0.03, DDIT3 0.02.
   - The only support is by analogy to TM2D3's ER phenotype (M16).

   The honest label is "shared dependency with membrane ubiquitin/quality-control proteins". "ER stress" should be a hypothesis to test, not the module name.
5. **Notch dismissed with the wrong statistic.** Mean effects of NOTCH1, PSEN1 and NCSTN say nothing about co-dependency. The correct test gives TM2D2 against NOTCH1/2, PSEN1/2, NCSTN, APH1A, PSENEN and ADAM10 of |r| ≤ 0.09. Notch is therefore equally unsupported by DepMap. Meanwhile M26, the strongest human genetic data on loss of all three genes, explicitly points to NOTCH1. The competing hypothesis deserves equal weight.
6. **Weak raw Pearson.** JOSD1, the rank-1 partner, has raw r 0.22 for TM2D2 and 0.17 for TM2D1. The zavg_BEF transform amplifies these weak links (z_B 29–31). That is acceptable for the method, but §0 should not present JOSD1, AUP1 and STUB1 as equally firm.
7. **Missing literature.** Michellod et al. 2003 (PMID 14595834, almondex) was downloaded to `texts/` but not cited. Otherwise the TM2D3/almondex, Notch and Alzheimer's literature (M13–M25) is adequately covered.
8. **Experiments.**
   - **The decision rule contradicts the decisive experiment.** "Refuted" covers only non-rescue or wrong localisation. A clean null on the UPR panel or tunicamycin beyond MEN1, which §1 and §9 call refuting, would be scored "ambiguous". That makes the hypothesis effectively unfalsifiable by its own decisive test.
   - In ETCC-016, AUP1 is not a dependency (−0.05), so the AUP1 arm is not growth-matched there.
   - The SNU-46 control shows positive TM2D1/TM2D3 effects (+0.41/+0.38).
   - Guide sequences and off-target checks are pending.
   - The UPR readout at day 4–5 after CRISPRi may be too early or too late for a protein with no expected acute UPR role. A time course (day 3/5/7) is needed.

## 4. Verdict: ACCEPT WITH REVISIONS

The ledger and numbers are accurate, the weaknesses are mostly disclosed, and the module analysis is careful. The remaining problems are the ER-stress framing and the decision rule.

**Required fixes**
1. Make a null UPR/tunicamycin result beyond MEN1 a **refutation** in Part 2 §7, in both reports. Add a UPR time course, and run the paralogue off-target check with the public Avana guide map.
2. In §12.4 and §0, report raw r and genome-wide rank for STUB1 and CHIC2 (TM2D1–STUB1 0.10, rank 234) and the near-zero partner–partner correlations. Add TM2D2's null correlations with UPR genes. Rename the claim to "membrane-protein quality-control co-dependency; ER stress tentative".
3. Replace the mean-effect Notch dismissal with correlations, and cite M26's NOTCH1 interpretation and its "suggesting" hedge. Remove "first such locus" (M28), mark M39/M40 as a preprint, and count TM2D1/TM2D2 as one observation in module-level statistics.
