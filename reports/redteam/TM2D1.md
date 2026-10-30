# Red-team review: reports/TM2D1.md

- Reviewer: adversarial reviewer agent (role `red_team`), model Claude Opus 5.5
- Date: 2026-10-30
- Scope: the TM2D1 T-ledger (Appendix A.2) and the shared M-ledger it cites (in `reports/TM2D2.md` A.1); numbers checked against `reports/data/TM2D1/bundle.md`, `reports/data/TM2D_module/*`, `results/m7/scratch_reports_tm2d/*_out.txt`, `results/ledger/M6_SUMMARY.md`, `results/holdout_eval/SUMMARY.md`; the hypothesis; the Part 2 plan.
- Independence: I did not write the report. PMIDs were resolved again through the Europe PMC REST API (`EXT_ID:` queries). Raw Chronos correlations and own-locus copy-number tests were recomputed from `data/raw/depmap/CRISPRGeneEffect.csv` and `OmicsCNGeneWGS.csv`. Scripts: `reports/redteam/tm2d_rt_corr.py` and `reports/redteam/tm2d_rt_cn.py`.

---

## 1. Ledger spot-check (29 rows)

| # | Row | Check | Result |
|---|---|---|---|
| 1 | M15 TM2D3 is an ER protein | PMID 40449487 is in Europe PMC (Gabillard-Lefort et al., *Am J Hum Genet* 2025, DOI 10.1016/j.ajhg.2025.05.004); span is in the abstract | **PASS** |
| 2 | M16 ATF4/HSPA5/DDIT3 dysregulated | same abstract | **PASS** |
| 3 | M18 "exacerbated ER-stress sensitivity" | same abstract | **PASS** |
| 4 | M26 LoF in all three TM2D genes associated with CN-LOH in cis | PMID 42156563 is in Europe PMC (Tang, Kamitaki, Mukamel, … Loh, *Nat Genet* 2026, "Patterns and drivers of 43,617 mosaic chromosomal alterations in blood", DOI 10.1038/s41588-026-02592-0); span is in the full text | **PASS on the span**. The same sentence goes on to propose that these CN-LOH events act "via dysregulation of NOTCH1". The report leaves this out (see §3.4). |
| 5 | M27 TM2D1 LoF penetrance 27% (17–39%) | same full text | **PASS** |
| 6 | M28 TM2D3 is a monogenic CN-LOH locus | PMID 32581363 (Loh 2020 *Nature*) | **PASS**. However, `reports/TM2D2.md` §7.3 says TM2D3 was "the first such locus". The source lists TM2D3 as one of six loci and does not say "first". This is an over-reading. |
| 7 | M1–M3 BBP family of three; binds Aβ; sensitises cells to Aβ toxicity | PMID 11278849 | **PASS** |
| 8 | M4 BBP not coupled to G proteins | PMID 12836168 | **PASS** |
| 9 | M5, M6 fly TM2D knockouts share a phenotype; triple null no worse | PMID 34905536 | **PASS** |
| 10 | M8 / T34 orthology TM2D1 = *bisc* | 34905536 full text | **PASS** |
| 11 | M12 IMPC Tm2d1/2/3 recessive embryonic lethal | 34905536 full text (context names all three MGI pages) | **PASS** |
| 12 | M24 TM2D1/2/3 among strongest phagocytosis regulators | PMID 30397336 / PMC6719718 | **PASS** |
| 13 | M29 AUP1 binds HRD1–SEL1L; needed for ERAD | PMID 21857022 | **PASS** |
| 14 | M33 Aup1 knockdown raises ER-stress genes (zebrafish) | PMID 40484276 (the preceding sentence is about overexpression; "opposite effects" refers to it) | **PASS** |
| 15 | M37, M38 STUB1–CHIC2 complex | PMIDs 36108743, 40796662 | **PASS** |
| 16 | M61/M62 raw r rows | `lines_out.txt`; recomputed by me: TM2D1–TM2D2 0.51, TM2D1–AUP1 0.24, AUP1–UBE2G2/SEL1L/SYVN1 0.39/0.25/0.34 | **PASS** |
| 17 | M77 UBE2G2/SEL1L/SYVN1 means −0.321/−0.055/−0.458 | `lines_out.txt` | **PASS** |
| 18 | T6 TM2D1 overexpression drives HCC proliferation | PMID 33948373 (*Am J Cancer Res* 2021, no DOI) | **PASS** |
| 19 | T7 TM2D1 reverses sevoflurane/propofol effects | PMID 38920064 | **PASS** |
| 20 | T11–T14 S 34.612, tie with ERAD, LOPO 0/2 | bundle §2 | **PASS** |
| 21 | T15 GLS top term "lymphocyte activation" | bundle §5 | **PASS** |
| 22 | T16 DEMETER2 not measured (0 partners) | bundle | **PASS** |
| 23 | T19/T20 CCLE proteomics TM2D3 0.63, APP 0.59, AUP1 0.41 (97%) | bundle | **PASS** |
| 24 | T23–T25 lines MAPAC-HS-77, LXF-289, PANFR0344_T1 | bundle; `lines_out.txt` | **PASS** |
| 25 | T26 recall-probe text | `recall_probe_90.tsv` | **PASS on the span**. The probe's content is wrong: it calls almondex TM2D1's fly homologue, but almondex is the TM2D3 orthologue (M8). The report quotes the probe without flagging the error. |
| 26 | T27–T30 blinded judging 0/0 | judge files | **PASS** |
| 27 | T32 PCM1 control (−0.54/−0.74; r −0.018) | `ctrl_out.txt` | **PASS** |
| 28 | T33/M83 module effects in the chosen lines | `lines_out.txt` | **PASS** (every value matches the report's text) |
| 29 | M65–M70 p_cal meaning, precision@1 0.030, slope 0.819, false-support 0.223 | M6_SUMMARY / holdout SUMMARY | **PASS** |

`verify_result.json` lists 170 rows, all `ok`. I found no fabricated PMID, DOI or span. The failures are wording problems only: "first such locus" (M28), the omitted NOTCH1 interpretation (M26), and the unflagged recall-probe error (T26).

## 2. Numbers

- Correlations: TM2D1/2/3 against UBE2G2, SEL1L and SYVN1 all have |r| ≤ 0.03, and AUP1 against them ranges 0.25–0.39. Both are **confirmed**.
- Mean, SD, fraction < −0.5, split-half R, p_cal and its CI all match bundle §2–3.
- Cell lines follow the bundle's rule (TM2D1 ≤ −0.5, JOSD1 ≤ −0.3).
- **What the report does not show.** I recomputed TM2D1's raw genome-wide co-dependency ranks (Pearson, 1,361 lines):

| partner | network rank (zavg_BEF) | raw r | raw genome-wide rank |
|---|---|---|---|
| AUP1 | 2 | 0.24 | 3 |
| JOSD1 | 1 | 0.17 | 19 |
| **STUB1** | 3 | **0.10** | **234** |
| **CHIC2** | 6 | 0.095 | 333 |
| **ZDHHC6** | 5 | 0.06 | 1,379 |

  STUB1 is one of the only two term-supporting partners. In raw co-dependency it is rank 234, and it is GLS rank 127. The report mentions the GLS rank (§5) but never gives the raw r of 0.10, and it describes the STUB1 link as if it were as strong as the AUP1 link.

## 3. Attack on the hypothesis

1. **Paralogue / one observation.** TM2D1–TM2D2 zavg_BEF is 31.7 (raw r 0.51), and their top-10 lists share eight partners. The report says this correctly. But TM2D1 and TM2D2 still occupy two top-40 slots and two blinded-judging rows. Guide cross-cutting is described as "not checkable". The Avana guide map is public, so this check is feasible and has simply not been done.
2. **The "module" is a star, not a module.** The partners barely co-vary with each other: JOSD1–AUP1 0.07, JOSD1–STUB1 0.13, AUP1–STUB1 0.12. The only real partner–partner pair is STUB1–CHIC2 at 0.34. The bench summary's phrase "module with AUP1, JOSD1, STUB1" is stronger than the data.
3. **"Response to ER stress" is an over-reading.**
   - The term rests on two partners and has LOPO 0/2.
   - It is tied with ERAD, and the report itself argues ERAD is unlikely.
   - It changes under GLS.
   - TM2D1 shows no co-dependency with any UPR gene: HSPA5 0.01, ERN1 −0.08, ATF6 −0.06, EIF2AK3 −0.03, XBP1 0.02, ATF4 −0.02, DDIT3 −0.02. It also shows none with the ERAD core.
   - The rank-3 term ("regulation of kinase activity", LOPO 2/3) is more robust. The raw top partners (CRKL, GRB2, NCKAP1, PKN2, SSR2) point to signalling and the translocon rather than the UPR.
4. **Notch is dismissed with the wrong statistic.** The report rules out Notch using *mean* effects of NOTCH1, PSEN1 and NCSTN. The right test is correlation. I computed them: TM2D1 against NOTCH1/2, PSEN1/2, NCSTN, APH1A, PSENEN and ADAM10 gives |r| ≤ 0.08. So the cancer-line data support neither Notch nor the UPR. Meanwhile, the newest human genetics (M26) itself interprets TM2D loss through NOTCH1.
5. **Hub, copy-number and lineage artefacts.**
   - Hub: not a factor (in-degrees 39–60; hub share 0).
   - Partner copy number: no effect.
   - Own-locus copy number, which I tested: Spearman ρ(effect, CN) = −0.09. The dependent lines have median CN 1.04, so there is no CYCLOPS-type effect.
   - Lineage: leave-out passes.
6. **Weak raw signal.** The rank-1 partner JOSD1 has a raw Pearson r of only 0.17. DEMETER2 cannot test the call at all (0 partners), so no second perturbation technology replicates it.
7. **Literature.** TM2D3/almondex (M13–M23), the AD variant P155L (M19) and BBP–Aβ (M1–M3) are covered. Missing: the NOTCH1 interpretation in M26, and Michellod et al. 2003 (PMID 14595834, almondex). That paper was downloaded to `texts/` but never cited.
8. **Experiments.**
   - The decision rule (Part 2 §7) contradicts the stated decisive experiment. "Refuted" lists only non-rescue or wrong localisation, so a null UPR result counts as "ambiguous", even though Template A §9 and Part 2 §1 call it refuting.
   - AUP1 is barely a dependency in either chosen line (−0.11, −0.20), so its value as a positive control is weak.
   - The control line PANFR0344_T1 is an organoid grown in OPAC medium, which cannot be run in parallel with 2D lines in CRISPRi time courses.
   - Guide sequences and off-target checks are pending.

## 4. Verdict: ACCEPT WITH REVISIONS

The ledger is sound, and the report is honest about most of its weaknesses. For TM2D1 the ER-stress call is weaker than for TM2D2, and it is not independent of TM2D2.

**Required fixes**
1. Report raw r and genome-wide rank for every top-10 partner. In particular, give STUB1 (0.10, rank 234) in §4 and §0, and state that the term rests on one raw-robust partner (AUP1). Downgrade the label to "membrane protein quality control (tentative)". Add the null correlations with UPR genes.
2. Fix the decision rule so that a null UPR/tunicamycin result beyond PCM1 counts as **refuted**. Replace PANFR0344_T1 with a 2D non-dependent line. Run the off-target check for the paralogue guides using the public Avana guide map.
3. Replace the mean-effect Notch dismissal with correlations (|r| ≤ 0.08), and cite M26's NOTCH1 interpretation. Flag the recall-probe orthology error (almondex = TM2D3). Count TM2D1/TM2D2 as one observation in module-level claims.
