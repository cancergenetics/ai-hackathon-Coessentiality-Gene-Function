# Manuscript number verification, round 2

Subject: `manuscript/manuscript.md` at HEAD 0cde51b (v2) and `REPORT.md`. Auditor: independent agent (did not produce results).
Tool: `./.env/bin/python -I verify/check_manuscript_numbers.py` (read-only). Nothing in the manuscript, REPORT.md or sources was edited.

## 1. Counts

| quantity | round 1 | round 2 |
|---|---|---|
| sentences or table cells with numbers | 441 | 556 |
| tagged numeric tokens | 953 | 1,260 |
| screening hit (value occurs in a cited file) | 904 | 1,178 |
| screening miss, resolved by hand | 49 | 82 (56 sentences; 49 digits, 20 number words, 10 percentages, 3 years) |
| tagged tokens whose cited path does not resolve | 0 | 0 |
| untagged numeric tokens (years excluded) | 191 | 249 (Figure legends 88, Methods 76, Results 55, Discussion 21, others 9) |

Manual confirmation (value and quantity, read from the source file, not only a screening hit):
- all 82 screening misses: 81 confirmed (rounding of CI ends, derived counts, counts living in a sibling file, number words, years, definitions); 1 is a true rounding mismatch (item A1 below);
- every number in the Abstract, Author summary, Table 3, Table 4 and the Discussion;
- every number in Results C1 to C4 and the Methods sections on data, hold-out, calibration, orthogonal admission, judging and deviations (checked against `results/`, `manuscript/figures/source_data/`, `reports/*.md`, `DEVIATIONS.md`, `LOOKS.md`);
- Table 2 against `Table2_rediscovery.tsv` (37 rows: 18 top-40 and 19 S20; 33 N1, 4 N2, 35 recognised by the probe; ranks and p_cal reproduce `top40_primary.tsv`);
- Table 3 ranks and p_cal for the ten genes against `top40_primary.tsv` (1, 4, 5, 12, 16, 21, 28, 31, 33, 37; 0.141 ... 0.037 all agree), L classes against `report_selection.md`, orthogonal classes and TP53/DEMETER2/leave-out flags against `top40_primary.tsv`, prior-catalogue column against `a2_novelty_overlap.tsv` (9 of 10; PLEKHH3 none), partner correlations (PLEKHH3 0.424, 0.400, -0.186, 0.453, 0.257, 0.298, +0.377, +0.219, +0.087; C5orf34 902/459, z 23.8 and 2.4, r 0.06; INAFM1 4 of 1,361, r 0.12-0.21; BICRAL 0.53 vs 0.27; CCDC71L HP1 -0.105 to -0.010; TM2D1 STUB1 rank 234) against `reports/*.md`;
- Table 4: U 4,924; H 820 / 809; K = 25; all agree.

Round-1 findings are fixed in v2: the 9 vs 11 circularity count is now explained (11 under the primary rule, 9 fully circular; `core.md`, `circularity_summary.md`); the RBO count is compared on the same column (704 vs 635); the horizon, any-dependency and Table 3 tags now name real files.

Internal consistency: every quantity that appears more than once is identical wherever it appears (646 / 13.1%; 635 / 12.9%; 243 / 4.9%; 4,271; 809 / 820 / 775; 24 events; 0.030 / 0.012 / 0.182 / 0.218 / 0.049; slope 0.82 (0.51-1.13); 30.5 (13.8-49.7); 2,583; 4.9 (2.2-8.1); 0.40; 2.50; 18 / 16 of 40; 3 of 120; 31 N1; 34 and 27 of 40 priors; 59 of 90; 42% (29-56%); the 22 / 13 / 12 deviation counts; p_cal range 0.036-0.141; 5,965 pairs; 106 pairs; 11 genes; 10 report genes; 269 pool; 9 of 14 controls in H). Deviation classes add up: 13 + 3 + 4 + 2 = 22 = rows 7-28 of `DEVIATIONS.md`.

## 2. Mismatches (text vs source)

| # | location | text value | source value | file | severity |
|---|---|---|---|---|---|
| A1 | `manuscript.md` line 259 (Results C1, definition-artefact paragraph) | "2 of 16 (13%, 4-36%)" | Wilson lower bound 0.03498 = 3.5%, which rounds to 3%, not 4% (upper 0.360) | `results/revision/a1_N1_rates_by_route_and_flag.tsv` (also `numbers_a1.json`: 0.035) | trivial. Write 3-36% (or 3.5-36%) |
| A2 | line 400 (Results, Complementarity) and line 857 (Discussion) | oracle union 0.236 (0.206-0.266) | 0.206-0.266 is the gene-level bootstrap in `exploratory_complementarity.md`; the same quantity under the cluster bootstrap used for every other interval on the page is 0.202-0.272 (and +0.019, +0.010 to +0.028 vs homology) | `results/holdout_eval/exploratory_complementarity.md` section 1; `results/revision/a7_combination_rules.tsv` | low. Basis of the interval unlabelled and inconsistent with the neighbouring 0.224 (cluster CI). Either say "gene-level bootstrap" or quote 0.202-0.272 |
| A3 | line 847 (Discussion) | 0.012 "about one gene in 80" | 1 / 0.012 = 83 (1 / 0.030 = 33 is right) | `results/holdout_eval/SUMMARY.md` | trivial wording |
| A4 | line 1426, Methods > Reproducibility, "Chronology audit" bullet | "Its globs do not cover the hold-out and ledger outputs" | `results/ledger/` was in the glob set from the first commit (afed1dd); the M6 audit ran before the ledger existed (reviews/audit_order_M6.md: "prediction ledger: none"). Only `results/holdout_eval/`, `results/m7/` and `results/revision/` were uncovered. The same bullet's "no audit was committed for the final milestone" is superseded by `reviews/audit_order_M9.md` and the extended globs | `scripts/audit_order.py`; `reviews/audit_order_M6.md` | low (statement about process, not a number). Reword after M9 |
| R1 | `REPORT.md` section 5 | "23+ logged deviations after the freeze" | 22 rows (manuscript Discussion, Methods and `DEVIATIONS.md` rows 7-28) | `DEVIATIONS.md` | low. Replace by 22 |
| R2 | `REPORT.md` header | "2026-10-29 -> 2026-10-31" | last commit 0cde51b is 2026-10-30T09:36Z; no commit dated 10-31. The same later date appears in `DEVIATIONS.md` (row "2026-10-31", judge instruction), `reports/CCDC71L.md`, `reports/PLEKHH3.md` ("corrected 2026-10-31") | `git log` | low. Date anomaly; the manuscript already says row dates are not monotone |
| R3 | `REPORT.md` section 1, M4 | "Tool reproduces its published HT-AP exactly" | reproduced within +/-0.005; differences 0.0001-0.0003 (0.3451 vs 0.345 etc.) | `results/verification/tool_reproduction.md` | trivial. "within tolerance" |

No other REPORT.md number disagrees with the manuscript or sources (646 / 13.1%, 243 (173-306) / 4.9%, 809, 0.030 (0.018-0.043), 0.000 / 0.005, +0.006, 0.218, 0.049, +0.006, 0.117, slope 0.82 (0.51-1.13), c 0.86, 24 events, 0.141, 4,137, 0.32 / 0.28 / 0.22, 18/40 vs 3/120, p = 0.0002, 16/40 and 7e-4, 19/20, 1/30, 42%, 59/90, 56% vs 13%, 34/40, 9/10, 11 reviewers and 2 disposition checks, 809/809).

## 3. Source-to-source observations (no manuscript error)

- `a8` lists 2 new SPRING1 terms in the t0 vocabulary, `controls_case_series.tsv` lists 1 target in the 2-300 window; the manuscript quotes 1 ("single new term") and cites the latter. Different windows; consistent.
- `a3_annotation_gain_rates.tsv` is the cited file but the unconditional expectation 4.90 (2.23-8.05) is in `numbers_a3.json` and `SUMMARY.md`, which the tag also names. The manuscript prints 8.1 for 8.05 (two-decimal source); fine.
- `S2 Fig` legend: other scorable genes 10,303; `baseline_rows.md` frame is 13,240 protein-coding scorable genes outside U and H, less 3,000 LOO = 10,240. The 63 difference is probably non-protein-coding scorable genes; not verifiable from committed files, so left as a query.
- `S4A` Wilson interval for D1 and D2 route 4-36% vs 3.5-36%: see A1.
- Commit message 1eb08ea says judge validation "0/30 decoys"; the adjudicated analysis (`analysis_hval.md`) and the manuscript say 1 of 30. The manuscript is right.
- The 82 screening misses were dominated by derived or rewritten forms (95% CI labels, "five", "two to three", "2018", percentages of fractions), which the tool cannot match.
