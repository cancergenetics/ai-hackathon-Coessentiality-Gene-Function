# EXPLORATORY (post hoc; not pre-specified)

Exploratory complementarity analysis on the temporal hold-out H (scripts/36; LOOKS.md row dated 2026-10-29). The primary analysis (M5b, 7db89d2) is unchanged. Nothing here is a confirmatory test; p-values and CIs are descriptive, uncorrected, and chosen after seeing the primary results (homology 0.218 and PPI 0.049 hit@1 vs zavg_BEF 0.030). Primary H n = 809; same genes, targets, circularity exclusion, R1 and >= 2-partner reportability as scripts/32-33 (per-gene hit@1 of zavg_BEF, GLS, prior-only, homology and PPI reproduce the saved outputs exactly). Gene-level bootstrap CIs: 10,000 replicates, seed 0; PMID-only cluster CIs (the primary cluster rule) given alongside where noted.

## 1. Per-gene hit@1 agreement (2x2) and union

### zavg_BEF vs homology baseline

| | homology baseline hit | homology baseline miss | total |
|---|---|---|---|
| zavg_BEF hit | 9 | 15 | 24 |
| zavg_BEF miss | 167 | 618 | 785 |
| total | 176 | 633 | 809 |

Discordant: zavg-only 15, homology baseline-only 167; McNemar exact p = 1.2e-33. Union hit rate (zavg_BEF OR homology baseline) = 0.236 (gene-bootstrap 0.206-0.266; cluster 0.202-0.272) vs zavg_BEF 0.030 and homology baseline 0.218; gain of the union over the better single method = +0.019 (15 genes).

### zavg_BEF vs hu.MAP PPI transfer

| | hu.MAP PPI transfer hit | hu.MAP PPI transfer miss | total |
|---|---|---|---|
| zavg_BEF hit | 8 | 16 | 24 |
| zavg_BEF miss | 32 | 753 | 785 |
| total | 40 | 769 | 809 |

Discordant: zavg-only 16, hu.MAP PPI transfer-only 32; McNemar exact p = 0.0293. Union hit rate (zavg_BEF OR hu.MAP PPI transfer) = 0.069 (gene-bootstrap 0.052-0.088; cluster 0.051-0.088) vs zavg_BEF 0.030 and hu.MAP PPI transfer 0.049; gain of the union over the better single method = +0.020 (16 genes).

## 2. zavg_BEF precision@1 in genes the baselines cannot cover

| subset | n | zavg_BEF p@1 | gene-bootstrap 95% CI | cluster 95% CI | hits | homology p@1 | PPI p@1 |
|---|---|---|---|---|---|---|---|
| homology makes no prediction (no t0 IEA/ISS/IBA candidate term) | 348 | 0.014 | 0.003-0.029 | 0.003-0.028 | 5 | 0.000 | 0.040 |
| homology makes a prediction | 461 | 0.041 | 0.024-0.059 | 0.022-0.062 | 19 | 0.382 | 0.056 |
| no hu.MAP coverage: no scorable hu.MAP partner | 81 | 0.000 | 0.000-0.000 | 0.000-0.000 | 0 | 0.210 | 0.000 |
| no hu.MAP coverage: no reportable PPI prediction (< 2 supporting partners) | 94 | 0.000 | 0.000-0.000 | 0.000-0.000 | 0 | 0.234 | 0.000 |
| hu.MAP covered (>= 1 partner) | 728 | 0.033 | 0.021-0.047 | 0.020-0.048 | 24 | 0.218 | 0.055 |
| neither homology prediction nor hu.MAP partner | 38 | 0.000 | 0.000-0.000 | 0.000-0.000 | 0 | 0.000 | 0.000 |
| all primary H | 809 | 0.030 | 0.019-0.042 | 0.018-0.043 | 24 | 0.218 | 0.049 |

Note: genes with no hu.MAP coverage or no homology prediction are a selected subset (e.g. poorly studied genes), so these rates are not comparable to the full-H rate without that caveat.

## 3. hit@k (any target term among the top k reportable terms)

Denominator = all primary H genes (a gene with no reportable list scores 0); homology and prior-only lists are complete rankings of candidate terms, the others are limited to reportable terms (>= 2 supporting partners). Gene-bootstrap 95% CIs.

| method | hit@1 | hit@3 | hit@5 | coverage (>= 1 term) |
|---|---|---|---|---|
| zavg_BEF | 0.030 (0.019-0.042) | 0.053 (0.038-0.069) | 0.067 (0.049-0.085) | 0.958 |
| GLS | 0.023 (0.014-0.035) | 0.036 (0.023-0.049) | 0.041 (0.027-0.056) | 0.927 |
| homology | 0.218 (0.189-0.247) | 0.299 (0.267-0.331) | 0.344 (0.311-0.377) | 1.000 |
| PPI (hu.MAP) | 0.049 (0.035-0.066) | 0.079 (0.062-0.099) | 0.094 (0.074-0.115) | 0.884 |
| prior-only | 0.000 (0.000-0.000) | 0.042 (0.028-0.057) | 0.069 (0.052-0.088) | 1.000 |

## 4. precision@1 by out-of-fold p_cal bin and by signal quintile (already reported in M5b; cited, not recomputed)

Source: results/holdout_eval/reliability_oof.tsv (decile bins of p_cal_oof) and signal_quintiles.tsv (quintiles of top-K mean zavg).

| p_cal_oof bin | n | p range | mean predicted | observed p@1 | Wilson 95% CI |
|---|---|---|---|---|---|
| 0 | 78 | 0.000-0.000 | 0.000 | 0.000 | 0.000-0.047 |
| 1 | 77 | 0.000-0.006 | 0.003 | 0.000 | 0.000-0.048 |
| 2 | 78 | 0.006-0.008 | 0.007 | 0.000 | 0.000-0.047 |
| 3 | 77 | 0.008-0.010 | 0.009 | 0.000 | 0.000-0.048 |
| 4 | 77 | 0.010-0.013 | 0.011 | 0.000 | 0.000-0.048 |
| 5 | 78 | 0.013-0.016 | 0.014 | 0.013 | 0.002-0.069 |
| 6 | 77 | 0.016-0.021 | 0.019 | 0.026 | 0.007-0.090 |
| 7 | 78 | 0.021-0.034 | 0.026 | 0.077 | 0.036-0.158 |
| 8 | 77 | 0.034-0.075 | 0.051 | 0.078 | 0.036-0.160 |
| 9 | 78 | 0.077-0.533 | 0.170 | 0.115 | 0.062-0.205 |

Quintiles of top-K mean zavg (all columns as saved):

| quintile | n | zmean_min | zmean_max | p1_zavg | p1_zavg_lo | p1_zavg_hi | p1_prior | p1_prior_lo | p1_prior_hi | p1_null | p1_null_lo | p1_null_hi | p1_gls | p1_gls_lo | p1_gls_hi | d_prior | d_prior_lo | d_prior_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 162 | 2.736 | 3.742 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.005 | 0.001 | 0.010 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Q2 | 162 | 3.742 | 3.921 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.002 | 0.000 | 0.006 | 0.006 | 0.000 | 0.019 | 0.000 | 0.000 | 0.000 |
| Q3 | 161 | 3.921 | 4.207 | 0.012 | 0.000 | 0.032 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 | 0.004 | 0.012 | 0.000 | 0.032 | 0.012 | 0.000 | 0.032 |
| Q4 | 162 | 4.207 | 5.366 | 0.019 | 0.000 | 0.042 | 0.000 | 0.000 | 0.000 | 0.009 | 0.001 | 0.019 | 0.025 | 0.006 | 0.050 | 0.019 | 0.000 | 0.042 |
| Q5 | 162 | 5.379 | 15.545 | 0.117 | 0.067 | 0.174 | 0.000 | 0.000 | 0.000 | 0.007 | 0.002 | 0.014 | 0.074 | 0.031 | 0.124 | 0.117 | 0.067 | 0.174 |
