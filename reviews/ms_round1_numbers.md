# Manuscript number verification, round 1

Subject: `manuscript/manuscript.md` (v1 assembly, 403 `<!-- src: ... -->` tags).
Tool: `verify/check_manuscript_numbers.py` (extraction plus screening). The semantic check (is the value in the
cited file the same quantity as the one in the sentence) was done by reading each cited source file and comparing it with
the sentence. Read-only: nothing else in the repository was edited.

## 1. How the check was done

1. The script splits the text (Abstract through Methods, legends, supporting-information list; References skipped) into
   sentences and table cells and extracts every number, including number words from two to fifty and values written
   as `x × 10⁻ⁿ`. Citation brackets, figure/table labels, dates, version strings and identifiers such as C1, N1, R1, V1 are masked.
   A number is attached to the first src tag that follows it in the same sentence. For tables 2 and 3 the trailing
   comment block supplies the tag.
2. Each tagged number is searched in the cited file(s), allowing rounding to the manuscript's precision, percent and
   fraction forms, and the 10⁻ⁿ form. Wildcards and bare file names (`J1_main3.tsv`) are resolved. Every cited path resolves and is tracked in git.
3. All 49 numbers that the screening could not find were looked at by hand. In addition, the cited sources were read for the
   quantities behind the Abstract, every Results paragraph, Tables 2 and 3, the Discussion and Methods. Table 2 was compared row by row
   with `Table2_rediscovery.tsv` (37 of 37 rows agree on gene, rank, term, p_cal or zavg, L class and probe call). Table 3 was compared
   with `Fig4_top40_primary.tsv`, `analysis_main_genes.tsv` and `report_selection.md`.
4. Limits: a screening hit proves only that the value occurs in the file. For the 457 decimals and numbers of 100 or more, I
   confirmed the quantity in context. Small integers and number words (447 of them) were confirmed against the source
   tables or by recounting from the source rows. Nothing was re-derived from raw data; this check tests the
   manuscript against the committed result files, not the result files themselves.

## 2. Summary counts

| quantity | count |
|---|---|
| sentences or table cells containing numbers | 441 |
| tagged numeric tokens checked | 953 (888 digits, 65 number words) |
| matched the cited source (value and quantity) | 948 |
| mismatched | 5 (2 internal-consistency problems, 3 tag attributions; section 3) |
| screening misses (49) resolved by hand | 46 matches (rounding of CI ends, row counts, definitions), 3 attribution issues |
| untagged numeric tokens (excluding bare years) | 191 (145 digits, 46 words) |
| untagged tokens that need a tag | 13 tokens in 6 places (section 4) |
| untagged tokens where a tag is optional or unnecessary | 178 (restatements of a tagged number in legends and Methods, frozen design parameters, structural counts such as "three views", "four claims") |
| value in a tag's file differs from the manuscript value | 0 |

Untagged tokens by section: Results 41 digits and 17 words; Methods 24 and 8; figure legends 73 and 6; Discussion 3 and 6;
Introduction 0 and 5; Table legends and Supporting information 4 and 1; Abstract 0 and 1; Author summary 0 and 1; Data and code availability 0 and 1.

Overall: no number in the manuscript disagrees with the file it cites. The problems are one wrong count in
Methods that contradicts the Results, one comparison made on unequal bases, three imprecise citations, and a set of numbers with no tag.

## 3. Discrepancies

| # | location | text value | source value | file | severity |
|---|---|---|---|---|---|
| 1 | Methods > Temporal hold-out > Circularity (line 945): "affected 106 pairs, and 9 genes lost all their targets" | 9 genes lose all targets | 11 genes lose every target under the primary rule (820 to 809 primary genes). 9 is the count for the "fully circular" definition only (sensitivity row n = 811) | `results/holdout/circularity_summary.md` says 9; `results/holdout_eval/core.md` and `SUMMARY.md` say 11 | moderate. Contradicts Results line 223 to 225 (820 genes, 106 pairs removed, 809 left). The two source files disagree with each other, so the text should say 11 (primary) or state the definition |
| 2 | Results > C1 (line 185): "A rank-biased-overlap version ... gave 704 assessable genes; the two statistics agree closely" | 704 compared implicitly with 646 | 704 is the RBO count on the frozen expression column, to be compared with 635. No RBO count is given for the 646 (design-expression) definition | `results/assessability/summary.md` ("Assessable (RBO): 704 vs 635") | low to moderate. Unequal comparison basis. Write "704 versus 635 on the same expression column" |
| 3 | Results > C3 (line 348): "within about eight years" | 8 years | not in the tagged file | tag `results/ledger/pcal_summary.json`; horizon is in `config/frozen.yaml` (calibration.horizon_years) and `results/ledger/M6_SUMMARY.md` | low. Citation only |
| 4 | Results > C1 (line 188): "any dependency (≥ 1% of lines below −0.5)" | 1%, −0.5 | definition absent from the tagged TSV | tag `Fig1c_assessable_by_stratum.tsv`; definition in `preregistration/CRITERIA.md` ("any-dependency = >= 1% of lines < -0.5") | low. Citation only. The 427 of 1,105 and 219 of 3,170 do match the TSV |
| 5 | Table 3 trailing comment and line 468/504 | tag lists `reports/<GENE>.md` | placeholder, not a path. For WDR7 (packet J040) the cited J1 file scores 0 on every slot; the supporting score comes from judge 2 and `ADJ_main2.tsv` | `results/m7/judge/scores/J1_main2.tsv`, `ADJ_main2.tsv` | low. Citation precision; add the ADJ file and the real report paths |

Statement about the paper's own process (Methods > Reproducibility, line 1109), not a number: "CLAIMS.tsv maps manuscript
numbers to result files, and every number in this manuscript's source carries a comment naming its file." `CLAIMS.tsv` holds 6 claims
(C001 to C006), and 191 numbers are untagged (section 4). Reword, or add the missing tags and claims.

Source-to-source observations (no manuscript error):
- `Fig5b_support_vs_pcal.tsv` gives 5.50 × 10⁻⁸ as the minimum extra30 p_cal bin edge, while `extra30.tsv` has 6.38 × 10⁻⁸ as the minimum gene value. Both round to "6 × 10⁻⁸".
- Mean R(g) of H is 0.078 (all 820 genes, `summary.md`, used in the text) and 0.076 (809 primary genes, `core.md`).
- `M6_SUMMARY.md` labels the clean-first list "top 40" with Σp_cal 2.04. The manuscript correctly assigns 2.04 to the clean-first sensitivity list and 2.50 to the primary top 40.

## 4. Untagged numbers

Needs a tag (13 tokens in 6 places):

| location | text | judgement and suggested source |
|---|---|---|
| Results > Ten candidate reports (line 585) | PLEKHH3: "all 18,433 genes", r = 0.424 and 0.400, PIK3CA r = −0.186 | data values with no tag in their sentence (the next sentence's tag covers the Chronos means). Tag: `reports/PLEKHH3.md` (§0). Values verified there |
| Results > C2 (line 279) | "(top-K mean 5.4–15.5)" | same file as the preceding tag; move the tag to the end of the sentence. Value verified in `fig_signal_quintiles.tsv` (5.379 to 15.545) |
| Fig 2 legend (C) | "Q1 2.7–3.7 to Q5 5.4–15.5" | Q1 range appears nowhere else in tagged text. Verified in `fig_signal_quintiles.tsv` (2.736 to 3.742). Tag the legend |
| S2 Fig legend (A) | "other scorable genes (n = 10,303)" | new number, no tag anywhere. Verified in `FigS2a_R_by_set.tsv` (10,303; equals 18,394 − 4,271 − 820 − 3,000) |
| Results > C1 (line 202) | "(13.1%)" for 153 of 1,167 | derived percentage after the tag. Value correct (`summary.md`, 0.131) |
| Results > C3 (line 348) | "about 1.2% per gene" | derived: 30.49 / 2,583 = 1.18%. Correct; tag optional |

Tag optional or not needed:
- Figure and table legends (most of the 79 tokens): restate tagged values (809, 10,000 replicates, 2,583, 269, 708, 247, 2,000, 2,538, 4,271, 820, 3,000, 0.3, 0.5, 30, 200) or design parameters, and all agree with the tagged text. A single source-data pointer per legend, which they already carry, is sufficient.
- Frozen design parameters stated in Results or Methods without a tag: thresholds 0.3 and 0.5, "< 10 Tier A", "≥ 100 assessable", "underpowered threshold 300", acceptance rule "7 of 10 / 3 of 30", 10-fold, K = 25, "five covariates" in the formula text. These match `config/frozen.yaml` and DESIGN.md (checked), so a `config/frozen.yaml` tag would be tidy but is not needed.
- Structural counts and names: "three views", "four claims", "three points", "ten reports", "seven non-rediscovery reports", "two review rounds" (reviews/round1_* and round2_* exist), "Claude Opus 5.5". Verified or not data.
- Restatements in the same paragraph of a number tagged earlier (646, 50 genes, 247 anchors in Methods, "18 supported", "2 N3 genes").
- Derived plain-language ratios: "one gene in 33" (1 / 0.030), "one in eight" (646 / 4,924), "seven times" (0.218 / 0.030 = 7.3), "roughly threefold" (0.089 / 0.031 = 2.9). All correct.
- Introduction: "a small minority of genes accounts for half of all publications" has no tag but carries citations [1–4]; qualitative.

## 5. Internal consistency (same quantity across sections)

| quantity | locations compared | result |
|---|---|---|
| U = 4,924 (of 19,296); 4,275 in DepMap; 4,271 scorable | Author summary, Results C1, Methods, S1 Table legend, S2 Fig legend | agree |
| 646 assessable (13.1% of U) vs 635 (12.9%) | Abstract, Results C1, C3, Discussion ("one in eight"), Methods deviations | agree; 635 always labelled as the frozen-column value |
| H = 820; primary 809; 24 hits; precision@1 0.030 (0.018–0.043) | Abstract, Results C2, Discussion, Fig 2 legend, Methods | agree (see discrepancy 1 for the "9 genes" in Methods) |
| prior-only 0.000, matched null 0.005, GLS 0.023, homology 0.218, hu.MAP 0.049 | Abstract, Results, Discussion | agree |
| calibration slope 0.82, c-statistic 0.855, Brier 0.0294, base rate 3.1% | Abstract, Results, Discussion | agree |
| Σp_cal 30.5 (13.8–49.7) over 2,583; max p_cal 0.141; 5.5 over 269; 1.0 over 133 | Abstract, Results C3, Discussion, Fig 3 legend, Table 3 | agree |
| top-40 Σp_cal 2.50 (primary) vs 2.04 (clean-first) | Results C3 and C4 | agree; not mixed up |
| judged 18 of 40 vs 3 of 120 decoys, p = 2.2 × 10⁻⁴ (Abstract "0.0002") | Abstract, Results C4, Discussion, Limitations (16 on terms alone) | agree |
| N1 31 of 40; 59/24/7 of 90; 69 of 100; audit 21/13/16 of 50 (42%, 29–56%) | Abstract, Results C1 and C4, Discussion, Fig 1D and Fig 5 sources | agree |
| recall probe 52 of 90 (22/19/11) and 24 of 50; 43 of 59 N1 | Results C1 and C4, Discussion | agree |
| 37 supported genes in top 40 and S20; 33 N1; 4 N2; 35 recognised | Results C4, Table 2 | agree (Table 2 has 37 rows, 18 + 19) |
| κ = 0.975 (360 statements), κ = 0.931 (40) | Results C4, Limitations | agree |
| 21 deviations (12 / 3 / 4 / 2) | Discussion, Limitations, Methods | agree |
| tie-break affects 401 of 820; reverse order 0.032 | Results C2, Discussion, Methods | agree |
| 14 controls, 9 in H | Results C2, Methods | agree |

## 6. Verified against the source, by theme (no discrepancy)

Tool reproduction (0.3451, 0.2423, 0.1463, 0.1341; 14 of 14 checks; 4.06 to 16.90; 2.96 × 10⁻⁷). Ranker choice (MRR 0.169, 0.140,
0.111, 0.073; shuffle 0.139 to 0.015 vs 0.036). Census and strata (every fraction in `Fig1c_assessable_by_stratum.tsv`; 2/516, 46/742, 598/3,666,
427/1,105, 219/3,170, 437/138/71 of 1,425, 13/297, 31/484; 153/1,167; 27.2%; 9.7%; Spearman 0.991). Hold-out (all CIs in
`SUMMARY.md` and `core.md`; split-half range 0.025 to 0.038; V1 0.182; quintiles 0 / 0 / 0.012 / 0.019 / 0.117; GLS strata; SMDs; U-reweighting;
LOO-fitted model 0.089 vs 0.031). Calibration table (deciles, 775 genes, coefficients, support bounds). Complementarity (9/15/167, 0.236, 0.014 on 348, 0.067 and 0.069).
Catalogue (all counts in `pcal_summary.json`, `M6_SUMMARY.md`, `derived_numbers.tsv`). Clean negatives and false-support rates. Judging (every
count, p-value, Wilson interval, class split in `analysis_main.md`, `analysis_hval.md`, `Fig5_derived_numbers.tsv`, `Fig5b/c/d`). Reports (r values
0.424, 0.400, −0.186, +0.377, +0.219, +0.087; 902 and 459 lines; INAFM1 r 0.12 to 0.21 and 4 of 1,361; BICRA 0.53 vs BICRAL 0.27; STUB1 raw rank 234; PxVxL 223 to 227).
Methods parameters (all against `config/frozen.yaml`, `zavg_full_manifest.json`, `CRITERIA.md`, `admission.md`, `holdout_sizing.md`, `power_sim.md`, `PIPELINE.md`, `DATA.md`, `requirements.lock.txt`).
