# A3. p_cal is conditional on annotation [exploratory, post-review]

p_cal estimates P(top term confirmed | the gene receives >= 1 new experimental BP/MF annotation in the 5–200 window over ~7.9 years), because H requires >= 1 target. An unconditional expectation is approximately Σp_cal × r, where r = P(gene gains such an annotation).

Assumptions: (1) r estimated on t0-eligible genes (2018-07) applies to U genes over a similar horizon (stationary curation; PAN-GO and similar efforts may change it); (2) gaining annotation is independent of whether the top term is right, conditional on the p_cal covariates. This is VIOLATED for top-K mean zavg: the gain rate is ~0.13-0.14 in quintiles 1-4 and 0.25 in quintile 5 (table below), so a signal-adjusted rescaling (quintile-specific rate per U gene) is also reported; (3) U genes are survivors that stayed uncharacterised to 2026, so the 2018 cohort rate is likely optimistic for them (the 2022-cohort and 2018-survivor hazards are reported as checks); (4) the interval combines bootstrap parameter uncertainty in Σp_cal with binomial uncertainty in r assuming independence; it is an interval for an expectation, not a prediction interval.

| rate | k | n | p | wilson_lo | wilson_hi | horizon_years | annual_hazard | p_over_7p88y_constant_hazard | note |
|---|---|---|---|---|---|---|---|---|---|
| any new target (/H/ / t0-eligible) | 820 | 5051 | 0.1623 | 0.1524 | 0.1728 | 7.88 | 0.02247 | 0.1623 | holdout_sizing.md definition |
| primary H (non-circular target) / t0-eligible | 809 | 5051 | 0.1602 | 0.1503 | 0.1705 | 7.88 | 0.02214 | 0.1602 |  |
| H fit set (primary H with prediction) / t0-eligible with prediction | 775 | 4822 | 0.1607 | 0.1506 | 0.1714 | 7.88 | 0.02223 | 0.1607 | matches the conditioning set of p_cal (PRIMARY scaling) |
| any new target among t0-eligible with prediction | 786 | 4822 | 0.163 | 0.1528 | 0.1737 | 7.88 | 0.02257 | 0.163 |  |
| 2022 cohort: any new target / 2022-eligible | 376 | 4555 | 0.08255 | 0.0749 | 0.09089 | 3.89 | 0.02218 | 0.1604 | t0 = GO 2022-07-01, cut-off PMID 2022-07-01 |
| survivors: eligible in 2018 AND still eligible in 2022 -> new target after 2022 | 310 | 4171 | 0.07432 | 0.06675 | 0.08268 | 3.89 | 0.01988 | 0.145 | genes that stayed uncharacterised 2018->2022 (U-like survivors); gain 2022->now |

| q | sum | count | rate | lo | hi |
|---|---|---|---|---|---|
| Q1 | 130 | 965 | 0.1347 | 0.1146 | 0.1577 |
| Q2 | 139 | 964 | 0.1442 | 0.1234 | 0.1678 |
| Q3 | 125 | 964 | 0.1297 | 0.1099 | 0.1524 |
| Q4 | 136 | 964 | 0.1411 | 0.1205 | 0.1645 |
| Q5 | 245 | 965 | 0.2539 | 0.2274 | 0.2823 |
