# Fact check of docs/explainer_v2/README.md and figures

Checked independently against the result files (not only NOTES.md): `results/holdout_eval/SUMMARY.md`, `calibration.md`,
`fig_precision_by_method.tsv`; `results/revision/SUMMARY.md` (A1-A8), `a10_*.tsv`; `results/ledger/M6_SUMMARY.md`,
`pcal_summary.json`, `top40_primary.tsv`; `results/m7/judge/analysis_main.md`, `analysis_hval.md`; `results/assessability/summary.md`;
`results/audit/curation_lag_audit.md`; `results/calibration/loo_ranker_choice.md`, `label_shuffle.md`;
`results/holdout/circularity_summary.md`; `docs/explainer/worked_example_output/`; `docs/explainer/JOURNEY.md`, `METHOD.md`,
`DISCREPANCIES.md`, `journey_data.json`; `manuscript/manuscript.md`; `git log`; `PROMPT.md`; `preregistration/CRITERIA.md`.
References: all 17 DOIs resolved on Crossref; title, first author, journal and year match the citation in every case.

Verdicts: OK = matches source. IMPRECISE = number right but wording over- or under-states, or a label hides a caveat.
WRONG = contradicts a source. UNSOURCED = no source found.

## Summary of problems (WRONG and the most important IMPRECISE)

| ID | Verdict | One line |
|---|---|---|
| W1 | WRONG | Section 6, item 5 headline: "Most 'new' predictions had been made before". The source counts prior *links to a partner*, not prior function predictions; only 3 of 40 were explicit predictions. |
| W2 | WRONG | Figure (e) shades "overnight run" 23:11 to 03:57 and NOTES calls it the "no-commit" gap. The git gap is 23:11 to 04:55 (5.7 h). 03:57 is a sleep-blind timer estimate, not a commit time or a measured start. |
| I1 | IMPRECISE | "Confidence numbers are trustworthy" / "Is the stated confidence honest? yes": rests on equal means (near-trivial) and 24 events; slope CI 0.51-1.13, Brier skill 2%; the referee-approved wording is "not detectably miscalibrated". |
| I2 | IMPRECISE | "About 320 genes ... 1 in 15 carry a real signal" is a lower bound under an untested assumption ("at least"). |
| I3 | IMPRECISE | Step 4 lists "how broad the term is" as one of four inputs; its fitted weight is 0 (so is R). |
| I4 | IMPRECISE | "Support tracked confidence": the uncalibrated S20 list got 19/20; support fell with rank within the top 40 but the claim needs the S20 caveat. |
| I5 | IMPRECISE | Caveat "independent-data ... checks never validated on known positives": sources were admitted on annotation data before any prediction (S3 Fig); only the robustness (DEMETER2) check is stated as unvalidated in the paper. |
| I6 | IMPRECISE | "Testing on well-studied genes overstates accuracy about five-fold": the gap mixes leakage and a different gene population (DISCREPANCIES C4, untested). |

## Full table

### Opening, sections 1-2

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| Para 1 | Gene list fixed before any analysis | afed1dd 21:00; hash gate; PROVENANCE | OK | |
| Para 1 | Judges saw decoys; method beats chance, rarely names exact function, far worse than related sequences, most best predictions already known | 3.0% vs 0.5%; homology 21.8%; 31/40 N1 | OK | |
| S1 | "about one gene in four (4,924 of 19,296)" | 25.5% | OK | |
| S1 | "...and little focused literature" | U = D1 and (D2 or D3); 1,105 genes enter via low UniProt score regardless of paper count (A1); Tdark also counts | IMPRECISE | "...and either a low UniProt score or little focused literature" |
| S1 | Stoeger 2018; Haynes 2018 for unequal attention / annotation bias | Titles match ("ignored genes"; "annotation bias") | OK | |
| S1 | Tsherniak 2017 DepMap; Dempster 2021 measures growth loss | Crossref OK (Chronos) | OK | |
| S1 | 1,361 cell lines | worked_example.json n_lines_total 1361 | OK | |
| S2 | Pan 2018; Kim 2019; Wainberg 2021 for co-essentiality | Titles match | OK | |
| S2 | Gillis & Pavlidis 2011, 2012: well-studied genes easy to predict so LOO flatters | 2011 = multifunctional genes drive guilt-by-association; 2012 = performance rests on few edges. "Well-studied" is a paraphrase | IMPRECISE | "multifunctional, well-annotated genes are easy to predict" |
| S2 | "famous success stories often confirmed by papers that used DepMap" | SLC25A51 18/19, FIRRM 14/15, CCDC32 4/5 targets flagged | OK | |
| S2 | Nosek 2018 pre-registration; Radivojac 2013 CAFA time-split | Titles match | OK | |
| S2 | "checked whether a stated confidence of 10% is right about 10% of the time" | Calibration done on H; see I1 for strength | OK | |

### Section 3, steps 1-5 and ANKRD52

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| Step 1 | No informative experimental GO; "protein binding" does not count | CRITERIA D1; GO:0005515 generic | OK | |
| Step 1 | "either a low UniProt score or few focused papers (papers about 10 genes or fewer)" | D2 score <= 2; D3 <= 10 focused PMIDs (papers linked to <= 10 genes) **or Tdark** | IMPRECISE | Add "or the IDG 'dark' class" (NOTES admits the omission) |
| Step 1 | 4,924 genes; hash; scripts refuse to run; independent re-derivation matched | CRITERIA; PROVENANCE line 18-19, 32 | OK | |
| Step 1 | ANKRD52: only "protein binding"; 6 of 62 papers focused | step0: n_pubmed_focused 6, n_pubmed_all 62, 3 IPI rows protein binding, UniProt score 3 | OK | |
| Step 1 | ANKRD52 function already worked out in 2017 (Golden 2017) and "the database had never recorded it" | METHOD worked example (PMID 28114302); D1 shows no informative GO | OK | Golden DOI/title resolve |
| Step 2 | Tool "from the same lab" | PROMPT.md only gives the GitHub URL (cancergenetics); no statement about "the same lab" | UNSOURCED | Drop "from the same lab" or say whose lab |
| Step 2 | Three views: cleaned-profile similarity, partner-list overlap, network-map closeness | METHOD Step 2: F, B, E | OK | |
| Step 2 | Reproduced published benchmark | AP 0.3451 vs 0.345 | OK | |
| Step 2 | Same-arm and paralogue exclusions; Lazar 2024 | Title matches (arm-scale truncation) | OK | |
| Step 2 | ANKRD52 top partners AGO2, XPO5, DICER1, DROSHA, TNRC6A, DGCR8, TNRC6B; eighth PPP6C | step2_neighbours_top25.tsv ranks 1-8 | OK | |
| Step 2 | TARBP2 discarded (same arm, Dicer helper) | rank_without_exclusions 9; arm 12q | OK | (DUSP6 also removed, irrelevant) |
| Step 3 | Five splits; 200 look-alike genes; pass if beat them and expressed; failures flagged, cannot enter shortlist | assessability summary; JOURNEY | OK | |
| Step 3 | Look-alikes "similarly strong, variable profiles" | matched on mean effect, spread, missing data | OK | |
| Step 3 | Dede 2020 for paralogue buffering | Title matches | OK | |
| Step 3 | ANKRD52 halves shared about 12 of 25, look-alikes almost none | 10,10,13,13,13 = 11.8; null mean 0.0037 x 25 = 0.09 | OK | |
| Step 3 | "Only 646 of 4,924 (13%) passed" | 646 (13.1%) DESIGN-expressed; 635 (12.9%) frozen column | OK | Fine print says which |
| Step 3 | Non-expressed genes passed 13% vs planned 5% | clean negatives 153/1,167 = 13.1% (all non-expressed 12.6%) | OK | |
| Step 3 | "about 320 genes, roughly 1 in 15 of the list, carry a real signal" | 322 (242-388) = 6.5% **at least**, assumes clean-negative false-call rate applies to expressed genes | IMPRECISE (I2) | "at least about 320 ... under an untested assumption" (also section 6 item 2: "Only about 1 in 15") |
| Step 4 | Partners vote; sum of scores; >= 2 supporting partners; simplest of 3 pre-declared rankers won | R1 MRR 0.1688 vs 0.1403 vs 0.1108 | OK | |
| Step 4 | Four inputs: partner strength, annotated-partner share, term breadth, kind | model_H.json: zmean +0.285, cov_pct +1.70, **size_pct 0.000, R 0.000**, family terms | IMPRECISE (I3) | "mainly partner strength, share of partners annotated, and term family; term size got zero weight" |
| Step 4 | Fitted on 2018 test set; calibrated | Fitted on 775 H genes (24 hits) | OK | |
| Step 4 | 2,583 genes get a confidence | pcal_summary in_support 2583 | OK | |
| Step 4 | Usual-way confidence promised about 3x too much | 0.089 vs 0.031 = 2.9x | OK | |
| Step 4 | ANKRD52: 8 partners vote; ncRNA-mediated gene silencing | S 158.1, n_sup 8 (AGO2...TNRC6B, DDX6) | OK | |
| Step 4 | Confidence 0.14, about 1 in 7, highest of 2,583 | 0.14102; max_p_cal | OK | |
| Step 4 | Definition: curators record exact term from experiments within ~8 years if gene gets any annotation | M6 "~8 years"; A3 conditional | OK | |
| Step 4 | PP6 phosphatase ranks 37th because few PP6 members have experimental GO terms | METHOD: 37th, S = 24.9, explanation as stated | OK | |
| Step 5 | GO rolled back to 2 July 2018; 809 genes | H t0 2018-07-02; 820 -> 809 | OK | |
| Step 5 | SLC25A51 18/19, FIRRM 14/15 from DepMap-citing papers | circularity_summary.md | OK | |
| Step 5 | Written down 31 minutes before data opened, "once" | fa21808 22:19:48 -> aa381fc 22:50:36 = 30 min 48 s. Primary look once (LOOKS rule); later logged exploratory analyses touched H outcomes (70864b2, b39691d: a3, a4, a7, a8) | IMPRECISE | "the pre-registered look at the data was taken once; later exploratory analyses on it were logged separately" |
| Step 5 | Two judges, gene name hidden, real + three decoys "of similar type and size" | Decoys: same family, similar term size, no ancestor overlap. Relationship "types" were deliberately dropped (JOURNEY appendix) | IMPRECISE | "similar family and size" |
| Step 5 | Judges validated on known genes first | hval 9/10 vs 1/30, passed | OK | |
| Step 5 | Independent data: interaction, co-abundance, localisation, Perturb-seq, structure | classes P, A, L, G, S | OK | |
| Step 5 | ANKRD52: both judges real +1, decoys 0; already published (Golden 2017); Kim 2019, Wainberg 2021 earlier links | step7_judging.tsv J071; a2_novelty_overlap: Wainberg modules/pairs, Kim edge/cluster all True | OK | |

### Figures (a)-(c)

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| Fig a | 19,296; 4,924; 4,271; 646; 40; 18; "16 already published"; about 320 | All match | OK | |
| Fig a | "Measured in the CRISPR screens" 4,271 | 4,271 = scorable (DepMap column and unique tool mapping); 4,275 are in DepMap | IMPRECISE | "Measurable by the tool in the screens" |
| Fig a | "Top 40 by calibrated confidence" | top40_primary.tsv = pure p_cal order after exclusions (PI overrode clean-first); pool is 269 assessable calibrated genes | OK | |
| Fig b | 4,924; 25 partners; 1,361 lines; halves; "function most partners share" | "Most partners share" is really highest summed score with >= 2 partners | IMPRECISE | "best-scoring shared function" |
| Fig c panel 1 | "Only 6 papers focused on it" | 6 | OK | |
| Fig c panel 2 | Blue = gene-silencing machinery (7 bars), PPP6C grey | Panel 4 says "8 of 25 partners vote"; the 8th (DDX6) is below rank 13 and not drawn | IMPRECISE | Note "(8th, DDX6, not shown)" |
| Fig c panel 3 | 12 vs ~0 | 0.472 x 25 = 11.8; 0.0037 x 25 = 0.09 | OK | |
| Fig c panel 4 | confidence 0.14 (1 in 7); 0.3 = pre-set bar; highest of 2,583 | OK (tier B 0.3; tier A 0.5 also existed) | OK | |
| Fig c panel 5 | Real two checks, three decoys with no support; terms synaptic, deacylase, dicarboxylic acid | J071 | OK | |

### Section 5 scorecard and figure (d)

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| S5 header | "confidence numbers are trustworthy but low" | See I1 | IMPRECISE (I1) | "not detectably miscalibrated, but rests on 24 correct calls" |
| Test 1 | 3% (about 1 in 30) vs 0.5%; 809 genes | 0.0297 (0.018-0.043); 24/809; null 0.0049 | OK | |
| Test 1 | GLS 2.3% | 0.0235; delta +0.006 (-0.005 to +0.017) | OK | "no better" is fair (CI includes 0) |
| Test 1 | Tool's lead on protein-complex partners did not carry over to function | METHOD Step 2 / JOURNEY TP5 | OK | |
| Test 1 | Homology 22% (about 1 in 5) | 0.2176 (176/809) | OK | Understates: homology predicts for only 461/809 genes (57%) |
| Test 1 | Homology = gene's own computer-inferred 2018 GO terms | IEA/ISS/IBA terms ranked | OK | Add: strength may partly reflect later curators confirming electronic terms (DISCREPANCIES C5, untested) |
| Test 1 | Strongest fifth 12% (11.7); weakest two fifths never; complex membership 18% | Q5 0.117; Q1,Q2 0.000; V1 0.182 (77 genes) | OK | |
| Test 2 | Predicted and observed agree (3.1% each) | Mean OOF 0.031 vs 0.031. Slope 0.82 (0.51-1.13), Brier skill 2%, c 0.855 inflated by quasi-separation (family coefficient -11.86) | IMPRECISE (I1) | Say agreement of the mean is expected from a fitted intercept; discrimination evidence is thin |
| Test 2 | Known-gene model promised 8.9% | 0.089 vs 0.031 | OK | |
| Test 2 | Highest 0.14; no gene reached 0.3 or 0.5 | 0.141; 0 and 0 | OK | |
| Test 2 | ~30 confirmations if all annotated; ~5 of 2,583; 1 in 6 gain annotation in 8 years | 30.5 (13.8-49.7); 4.90 (2.23-8.05); 775/4,822 = 0.161 | OK | |
| Test 3 | 18/40 (45%) vs 3/120 (2.5%) | analysis_main | OK | |
| Test 3 | Validation 9/10 vs 1/30 | hval | OK | Adjudicated value; commit message of 1eb08ea says 0/30 (DISCREPANCIES A5) |
| Test 3 | 16 of 18 already published | N1 real supported 16 (31 N1 genes) | OK | |
| Test 3 | "Support tracked confidence: among 30 lower-confidence genes only one" | extra30 1/30 OK; manuscript: ranks 1-20 12/20, 21-40 6/20. But S20 (uncalibrated) 19/20, so support follows signal strength, not p_cal as such | IMPRECISE (I4) | "Support fell with rank and was 1/30 in lower-ranked genes; the uncalibrated strong-signal list got 19/20" |
| Test 3 | Independent-data 32% vs 28% vs 22% (247 each) | 0.320/0.279/0.223 | OK | |
| Fig d1 | 0.5, 2.3, 3.0, 21.8 | tsv 0.0049, 0.0235, 0.0297, 0.2176 | OK | |
| Fig d1 | Label "Homology (sequence similarity)" | Baseline = own IEA/ISS/IBA terms (electronic, similarity and phylogenetic) | IMPRECISE | "Homology (inferred GO terms)" |
| Fig d2 | 8.9 / 3.1 and 3.1 / 3.1 titled "Is the stated confidence honest?" | Values correct; second pair is an out-of-fold mean | IMPRECISE (I1) | Retitle "Average predicted vs observed hit rate" |
| Fig d3 | 18/40, 16 already published, 3/120 | Correct. Bar 16/40 = 40% is genes already published among all 40 | OK | |

### Section 6 insights

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| 6.1 | Random 50: 42% experimentally established function | 21/50, CI 29.4-55.8; borderline sensitivity 38-46% | OK | |
| 6.1 | 288 listed genes are curated complex subunits; mechanism of focused-paper count | A1: 288 Complex Portal subunits | OK | |
| 6.2 | About 1 in 15; 2 of 516 passed | 6.5% lower bound (I2). 2/516 is driven by the expression requirement (only 7 of 407 scorable chemosensory/epidermal genes are expressed); 88 had p < 0.05 | IMPRECISE | "at least 1 in 15"; "mostly because they are not expressed in these cell lines" |
| 6.3 | Homology beats co-essentiality about 7 to 1 | 21.8/3.0 = 7.3 | OK | |
| 6.3 | 15 of 24 co-essentiality hits missed by homology | 176 + 24 - 191 = 9 shared, so 15 | OK | |
| 6.3 | Co-essentiality where homology silent adds 0.6 points | 0.224 vs 0.218; +0.006 (+0.001 to +0.012) | OK | |
| 6.4 | 14% vs 3% "overstates accuracy about five-fold" | 0.1385 (2,519 genes) vs 0.030 = 4.6x. Gap includes population difference (SMD table), not just leakage (DISCREPANCIES C4) | IMPRECISE (I6) | "is about five-fold higher; part is leakage, part is different genes" |
| 6.5 | "Most 'new' predictions had been made before" | A2 note: overlap flags "do not check that the resource assigned the same function"; only Wainberg SD3 is explicit, 3/40 | **WRONG (W1)** | "Most top genes already had a published link to a top partner (34 of 40); only 3 of 40 were explicit earlier predictions" |
| 6.5 | 34 of 40 prior link; 3 of 10 explicit in Wainberg 2021; only PLEKHH3 no precedent | a2: 34/40; CCDC71L, C5orf34, INAFM1; PLEKHH3 | OK | |
| 6.5 | PLEKHH3 possible PI3K/AKT brake, linked to PTEN | reports/PLEKHH3.md | OK | |

### Section 7 (AI process)

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| Intro | Six moments; about 15 hours, 29-30 Oct | 19:39 -> 10:26 = 14 h 47 | OK | |
| Fig e | Six points at 20:18, 21:00, 21:55, 22:50, 04:55, 07:47 | Commits 3e6b162, afed1dd, 0e76668, aa381fc, c4eadf5, 3f3a65b match to the second | OK | |
| Fig e / NOTES | Shaded "overnight run" 23:11-03:57 | Git: last commit 23:11:36, next 04:55:05. 03:57 = completion minus perf_counter runtime (excludes sleep, B12) | **WRONG (W2)** | Shade 23:11-04:55 labelled "no commits (machine asleep by the PI's account)" |
| Fig e | Usage-limit pause 08:16-09:16 not drawn | 379827f | IMPRECISE | Optional |
| Card 1 | Test on future; reviewers noted DepMap-based confirmations; literature review flagged LOO bias | Time-split already primary in DESIGN v1 (20:06, literature review); 3e6b162 (20:18) hardened it (A1) | IMPRECISE | Say "time-split proposed by the literature review at 20:06, hardened by round-1 review at 20:18" |
| Card 2 | Five measures incl. Stoeger, Oprea, Unknome | JOURNEY TP1 | OK | |
| Card 2 | "So the method now combines them" | Final rule uses GO, UniProt score, focused papers, Tdark; Unknome not in the rule | IMPRECISE | "combines four of them" |
| Card 2 | 16 min after freeze audit found 42%; no gene removed | afed1dd 21:00:14, b2b3a53 21:16:24 | OK | |
| Card 3 | First rule a quantile; statistics reviewer said cut-off not a test | round1_statistics item 11 | OK | |
| Card 3 | "That control later revealed the 13% leak" | 13% measured in the same M4 run (0e76668); referee later applied it to expressed genes (DISCREPANCIES A7) | IMPRECISE | "That control showed a 13% false-pass rate" |
| Card 4 | Three rankers, fixed contest; test opened once; 3%; independent re-derivation | 809/809 agreement (8e7e47f) | OK | See Step 5 note on "once" |
| Card 5 | Checks: leave out most dependent cancer type, RNAi; failed 221 of 269 | DESIGN: lineage leave-out = remove most dependent lineage; TP53 check also; 221 demoted of 269 | OK | Add TP53 |
| Card 5 | "ranks by confidence alone, failed checks as labels" | top40_primary.tsv = p_cal order; clean-first list kept as sensitivity | OK | |
| Card 5 | Machinery list, "where co-essentiality is strongest (Rahman 2021)" | Rahman 2021 documents a mitochondrial bias in screen benchmarking, not ribosome/DNA repair | IMPRECISE | "mitochondrial modules dominate benchmarks (Rahman 2021)" |
| Card 6 | Two referees, four problems; 30 -> about 5; title wording | JOURNEY TP8; manuscript title | OK | |
| Who did what | PI = Claude Opus 5.5; sub-agents Opus 5.5 / Sonnet 5.5; about 60 by estimate; log not kept | agent_runs.tsv one row; PROMPT | OK | |
| Who did what | Human supplied DepMap files; restarted run after usage-limit pause; "no scientific direction" | JOURNEY: human "had the files on the machine; PI found them"; restart and "no direction" are the PI's account, unverifiable (A8) | IMPRECISE | "According to the PI's account, ... (no transcript to check)" |
| Circles | Reviews found dozens of fixes (7 then 32) | JOURNEY | OK | |
| Circles | "Details left open at the freeze ... needed 22 logged changes" | 22 = all post-freeze deviation entries; about 13 filled unspecified details; file has 23 rows | IMPRECISE | "22 logged deviations, about 13 of them filling unspecified details" |
| Circles | Ten reports before catalogue check; nine corrected | 9/10 | OK | |

### Section 8 fine print and caveats

| Location | Claim | Source value | Verdict | Fix |
|---|---|---|---|---|
| Table | 4,924/19,296; 4,271 "measurable in DepMap" | 4,271 scorable (4,275 in DepMap) | IMPRECISE | "scorable" |
| Table | 21/50 = 42% (29-56%) | OK | OK | |
| Table | 646 (13.1%); excess 241 (168-306); implied 322 (242-388), 6.5%; manuscript 243, ~320 (6.6%) on 635 | a10 any_dependency rows: 240.8, 321.8 (242.5-388.1); 635: 243.2, 324.3, 6.59% | OK | The sd_tertile stratifier gives 269 / 323; README picks the lower pair without saying |
| Table | Non-expressed passing 13% (27% any dependency) | Clean negatives 13.1%; any_dependency=True 27.2% | IMPRECISE | "clean-negative (non-expressed) genes" |
| Table | 820 / 809; 106 of 5,965 | OK | OK | |
| Table | 3.0 (1.8-4.3), 24 | OK | OK | |
| Table | 0.5 (0.3-0.8); 0.0 | OK | OK | |
| Table | GLS +0.6 (-0.5 to +1.7); Pearson 2.7 | OK | OK | |
| Table | Homology 21.8 (18.4-25.3); hu.MAP 4.9 | OK | OK | |
| Table | 11.7 (6.7-17.4); 18.2 (9.3-28.6); 1.2 (0.7-1.9) | OK | OK | |
| Table | 22.4% (+0.6, +0.1 to +1.2) | 181/809 = 0.224 | OK | |
| Table | LOO 13.9% on 2,519 | 0.1385 | OK | |
| Table | Slope 0.82 (0.51-1.13); c 0.86; skill about 2%; 24 | 0.819; 0.855; 0.021 | OK | |
| Table | Promised 8.9, observed 3.1 | OK | OK | |
| Table | 0.141; 0 genes >= 0.3 | OK | OK | |
| Table | 30.5 (13.8-49.7); ~4.9 (2.2-8.1) | OK | OK | |
| Table | 18/40 vs 3/120 p = 0.0002; 16/40 p = 7e-4 | 0.000217; 0.000713 | OK | |
| Table | 31/40; 34/40; 6/40 | OK | OK | |
| Table | S20 19/20 all with earlier links; 1/30 | S20 any prior 20/20; 19/20 supported | OK | |
| Table | 32/28/22 (247) | OK | OK | |
| Caveats | Thin: 24 calls; simpler models share 7-14 of top 40 | 7, 14, 8 | OK | |
| Caveats | 82% of expected confirmations from failing genes; about one for 269 | 1 - 5.49/30.49 = 82%; 5.49 x 0.161 = 0.88 | OK | Marked as derived (B19) |
| Caveats | Reweighted accuracy about 1% | 0.012 | OK | |
| Caveats | Network from 2026; tool tuned on post-2018 atlas; Pearson matched | C6 (hu.MAP 3.0); Pearson +0.002 | OK | |
| Caveats | Module-label rule moved 16 to 18; same model judges; within-gene decoys not tried | manuscript | OK | |
| Caveats | Independent-data and robustness checks never validated on known positives | Manuscript only says DEMETER2 never validated on positives. Pair sources were admitted on annotation data (co-complex OR, S3 Fig) before predictions; Olivieri failed | IMPRECISE (I5) | "the final support rule and the robustness checks were never validated on known positives" |
| Caveats | Leak rate measured on non-expressed genes, assumed for expressed | A6 note "bound, not an estimate" | OK | |
| Caveats | No bench test, no human check | Manuscript; header disclaimer | OK | |
| When not to use | Fail the check about 87% of list | 100 - 13.1 | OK | |
| When not to use | Machinery genes have no calibrated confidence | families < 30 H genes | OK | |

### References and attributions (Crossref)

All 17 DOIs resolve and match author, year, journal and title idea: Dede 2020 (paralogue buffering), Dempster 2021 (Chronos),
Gillis & Pavlidis 2011 (multifunctional genes) and 2012 (guilt by association as exception), Golden 2017 (Argonaute
phosphorylation cycle), Haynes 2018 (annotation bias), Kim 2019 (functional interaction network), Lazar 2024 (arm-scale
truncations), Nosek 2018 (preregistration), Oprea 2018 (druggable genome), Pan 2018 (complex membership), Radivojac 2013
(CAFA), Rahman 2021 (mitochondrial bias), Rocha 2023 (Unknome), Stoeger 2018 (ignored genes), Tsherniak 2017 (Dependency
Map), Wainberg 2021 (co-essential module atlas). Attribution issues: Gillis & Pavlidis paraphrase and Rahman 2021 scope (above).
Tool commit 3c684c9 matches worked_example.json.

## Counts

About 120 claims checked. WRONG 2; IMPRECISE 31 (6 flagged as I1-I6 above); UNSOURCED 1; rest OK.
