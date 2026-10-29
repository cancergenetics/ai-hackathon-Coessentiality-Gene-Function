# M5b secondary batch on H (scripts/33; reported all or none)

Generated 2026-10-29T22:49:11 (runtime 175.8 s). Primary H n = 809; clusters as scripts/32; bootstrap 10,000 replicates, seed 0.

## Comparator methods (same predictor, R1, ≥ 2 partners)

| method | precision@1 (CI) | coverage | MRR | zavg − method (95% CI) | BCa |
|---|---|---|---|---|---|
| Pearson (R1) | 0.027 (0.016–0.040) | 0.910 | 0.039 | +0.002 (-0.009 to +0.014) | -0.009 to +0.014 |
| Homology baseline (t0 IEA/ISS/IBA, then frequency) | 0.218 (0.184–0.253) | 0.570 | 0.274 | -0.188 (-0.225 to -0.153) | -0.227 to -0.154 |
| PPI module transfer (hu.MAP 3.0 top-25) | 0.049 (0.034–0.066) | 0.884 | 0.073 | -0.020 (-0.037 to -0.004) | -0.037 to -0.004 |

zavg_BEF precision@1 = 0.030. hu.MAP: 728 of 809 H genes have ≥ 1 partner (724 ≥ 2); homology terms for 461 genes.

## Variants of the primary analysis

| variant | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) | IUT |
|---|---|---|---|---|---|---|---|
| t0 = 2019-07 (H rebuilt) | 649 | 0.028 (0.016–0.041) | 0.008 | 0.006 | +0.020 (+0.005 to +0.036) | +0.022 (+0.010 to +0.036) | pass |
| PMID-dated targets (all supporting PMIDs ≥ 2018-07 cut-off) | 475 | 0.034 (0.017–0.053) | 0.000 | 0.005 | +0.034 (+0.017 to +0.053) | +0.028 (+0.012 to +0.047) | pass |
| K = 10 | 809 | 0.028 (0.017–0.041) | 0.000 | 0.003 | +0.028 (+0.017 to +0.041) | +0.025 (+0.014 to +0.037) | pass |
| K = 50 | 809 | 0.033 (0.021–0.046) | 0.000 | 0.007 | +0.033 (+0.021 to +0.046) | +0.027 (+0.014 to +0.040) | pass |
| No same-arm / paralogue exclusion | 809 | 0.033 (0.021–0.046) | 0.000 | 0.005 | +0.033 (+0.021 to +0.046) | +0.029 (+0.017 to +0.042) | pass |
| U-reweighted (inverse-odds, trimmed 1/99) | 809 | 0.012 (0.007–0.019) | 0.000 | 0.004 | +0.012 (+0.007 to +0.019) | +0.008 (+0.002 to +0.015) | pass |

t0 = 2019-07: |H| = 660, primary 649 (98 flagged pairs), clusters PMID-only (fallback) {'PMID-only': {'n_clusters': 583, 'largest': 8, 'largest_frac': 0.012121212121212121, 'singletons': 537}, 'PMID+N(g)': {'n_clusters': 223, 'largest': 338, 'largest_frac': 0.5121212121212121, 'singletons': 178}}. U-reweighting: U-eligible 3301 of 4271 scorable U genes; weights 0.183–12.285, effective sample size 656; weighted GLS precision@1 0.012, zavg − GLS +0.001 (-0.008 to +0.009).

## LOO-fitted calibration evaluated on H

Model §3.7 fitted on 2479 LOO genes with a prediction (hit rate 0.141); applied to 775 H genes with a prediction: mean predicted 0.089 vs observed 0.031; Brier 0.0397 (constant-rate reference 0.0300); calibration intercept -1.394 (-1.835 to -0.953); slope 0.839 (0.576 to 1.102).

| bin | n | p range | mean predicted | observed | Wilson 95% CI |
|---|---|---|---|---|---|
| 0 | 78 | 0.009–0.016 | 0.013 | 0.000 | 0.000–0.047 |
| 1 | 77 | 0.016–0.020 | 0.018 | 0.000 | 0.000–0.048 |
| 2 | 78 | 0.020–0.024 | 0.022 | 0.000 | 0.000–0.047 |
| 3 | 77 | 0.024–0.029 | 0.026 | 0.000 | 0.000–0.048 |
| 4 | 77 | 0.029–0.036 | 0.032 | 0.000 | 0.000–0.048 |
| 5 | 78 | 0.036–0.046 | 0.041 | 0.013 | 0.002–0.069 |
| 6 | 77 | 0.046–0.060 | 0.052 | 0.026 | 0.007–0.090 |
| 7 | 78 | 0.060–0.101 | 0.077 | 0.051 | 0.020–0.125 |
| 8 | 77 | 0.101–0.223 | 0.153 | 0.091 | 0.045–0.176 |
| 9 | 78 | 0.226–0.868 | 0.454 | 0.128 | 0.071–0.220 |

Notes: comparator CIs are paired cluster bootstraps of zavg − method (two-sided). PPI module transfer uses hu.MAP 3.0, which post-dates t0 (favours the comparator). U complementarity of the PPI comparator requires U predictions and is deferred to M6.
