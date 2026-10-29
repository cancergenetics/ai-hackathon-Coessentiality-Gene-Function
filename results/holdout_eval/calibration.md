# M5b calibration on H (§3.7; scripts/34)

Generated 2026-10-29T22:49:20.
Fit set: 775 primary H genes with a top reportable term (34 without; no p_cal). Hit rate 0.031. Families with ≥ 30 H genes: ['ER_Golgi_secretory_lipid', 'other', 'signalling_lineage'] (reference other); counts {'other': 552, 'signalling_lineage': 111, 'ER_Golgi_secretory_lipid': 44, 'ribosome_biogenesis_translation': 19, 'nuclear_RNA_machinery': 16, 'DNA_replication_repair': 13, 'centrosome_cilia_mitosis': 10, 'mitochondrial': 10}.

## Out-of-fold performance (10-fold cluster cross-fitting, fold seeds 0–4, averaged)

- Mean out-of-fold p 0.031 vs observed 0.031; Brier 0.0294 (95% cluster-bootstrap CI 0.0198 to 0.0412; constant-rate reference 0.0300); c-statistic 0.855.
- Calibration intercept -0.006 (Wald 95% CI -0.437 to +0.426; cluster bootstrap -0.534 to +0.442).
- Calibration slope 0.819 (Wald 95% CI 0.512 to 1.127; cluster bootstrap 0.593 to 1.090).
- Poor calibration (§0 rule): Wald False; bootstrap False.

| bin | n | p range | mean predicted | observed | Wilson 95% CI |
|---|---|---|---|---|---|
| 0 | 78 | 0.000–0.000 | 0.000 | 0.000 | 0.000–0.047 |
| 1 | 77 | 0.000–0.006 | 0.003 | 0.000 | 0.000–0.048 |
| 2 | 78 | 0.006–0.008 | 0.007 | 0.000 | 0.000–0.047 |
| 3 | 77 | 0.008–0.010 | 0.009 | 0.000 | 0.000–0.048 |
| 4 | 77 | 0.010–0.013 | 0.011 | 0.000 | 0.000–0.048 |
| 5 | 78 | 0.013–0.016 | 0.014 | 0.013 | 0.002–0.069 |
| 6 | 77 | 0.016–0.021 | 0.019 | 0.026 | 0.007–0.090 |
| 7 | 78 | 0.021–0.034 | 0.026 | 0.077 | 0.036–0.158 |
| 8 | 77 | 0.034–0.075 | 0.051 | 0.078 | 0.036–0.160 |
| 9 | 78 | 0.077–0.533 | 0.170 | 0.115 | 0.062–0.205 |

## Model fitted on all H (for U; results/calibration/model_H.json)

| term | coefficient (original scale) | sign constraint |
|---|---|---|
| intercept | -6.3155 | free |
| zmean | +0.2850 | ≥ 0 |
| R | +0.0000 | ≥ 0 |
| cov_pct | +1.7038 | ≥ 0 |
| size_pct | +0.0000 | ≤ 0 |
| fam_ER_Golgi_secretory_lipid | -0.1934 | free |
| fam_signalling_lineage | -11.8593 | free |
| fam_rare | +1.2437 | free |

Support bounds (H 5th–95th percentiles): zmean 3.333–10.99; R 0–0.5464; cov_pct 0.07508–0.894; size_pct 0.04932–0.9498

## Decision branches (DESIGN §0)

- C2 primary PASSES -> calibrated claims for U are permitted (p_cal from the pre-specified model).
- Calibration branch: slope 95% CI includes 1 and intercept 95% CI includes 0 (Wald) -> calibration not poor; p_cal reported without the poor-calibration caveat.
- GLS < zavg_BEF on H (point estimate): the 'GLS ≥ zavg' branch does not apply.
- Tier-A (< 10) and assessable-count (< 100) branches are decided at M6/M7 (C1: 646 assessable, so the < 100 branch does not hold).
