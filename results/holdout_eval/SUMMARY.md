# M5b — the single pre-registered look at the temporal hold-out H: SUMMARY

Scripts 32–35 (one execution each unless noted in LOOKS.md); specification: LOOKS.md row 47631ed (ranker R1, §3.7 calibration spec, cluster fallback), DEVIATIONS.md. All CIs are 95% paired cluster-bootstrap percentile intervals (10,000 replicates, seed 0) unless stated; BCa intervals are in comparisons_core.tsv.

## Verdicts

1. **Primary IUT (C2): PASS.** precision@1 zavg_BEF 0.030 vs prior-only 0.000 (Δ +0.030, +0.018 to +0.043) and vs matched-gene null 0.005 (Δ +0.025, +0.013 to +0.038); clusters: PMID-only (fallback); BCa verdict PASS. Effective n 719 / 722 (not underpowered; rule < 300).
2. **GLS (key secondary, two-sided):** GLS precision@1 0.023; zavg − GLS +0.006 (-0.005 to +0.017) — CI includes 0 (no detectable difference); GLS ≥ zavg_BEF (point estimate): False.
3. **Calibration (§3.7, out-of-fold):** slope 0.819 (Wald 0.512 to 1.127; bootstrap 0.593 to 1.090), intercept -0.006 (Wald -0.437 to +0.426; bootstrap -0.534 to +0.442), Brier 0.0294 (0.0198 to 0.0412), c-statistic 0.855. Poor-calibration rule met: False (Wald; bootstrap False).

**Decision branches (DESIGN §0):**

- C2 primary PASSES -> calibrated claims for U are permitted (p_cal from the pre-specified model).
- Calibration branch: slope 95% CI includes 1 and intercept 95% CI includes 0 (Wald) -> calibration not poor; p_cal reported without the poor-calibration caveat.
- GLS < zavg_BEF on H (point estimate): the 'GLS ≥ zavg' branch does not apply.
- Tier-A (< 10) and assessable-count (< 100) branches are decided at M6/M7 (C1: 646 assessable, so the < 100 branch does not hold).

## H

|H| = 820 genes, 5965 (gene, target) pairs; circularity-flagged pairs 106 (fully circular 65), unscannable 48; primary H = **809** genes (11 lose every target). Clusters: PMID-only 709 (largest 9); PMID+N(g) 214 (largest 521, 63.5% of H) → primary = **PMID-only (fallback)**.

## Core metrics

| method | precision@1 (CI) | MRR (CI) | coverage | precision@1, terms ≤ 50 (CI; n) |
|---|---|---|---|---|
| zavg_BEF (R1) | 0.030 (0.018–0.043) | 0.048 (0.035–0.062) | 0.958 | 0.029 (0.017–0.044; 649) |
| prior-only | 0.000 (0.000–0.000) | 0.038 (0.032–0.045) | 1.000 | 0.000 (0.000–0.000; 649) |
| matched-gene null | 0.005 (0.003–0.008) | 0.010 (0.008–0.013) | 0.966 | 0.003 (0.001–0.005; 649) |
| GLS (R1) | 0.023 (0.013–0.035) | 0.032 (0.021–0.045) | 0.927 | 0.018 (0.008–0.030; 649) |

| comparison | clusters | Δ | 95% CI | BCa |
|---|---|---|---|---|
| precision@1 zavg - prior | PMID-only (fallback) | +0.030 | +0.018 to +0.043 | +0.019 to +0.045 |
| precision@1 zavg - prior | PMID+N(g) | +0.030 | +0.011 to +0.038 | +0.016 to +0.047 |
| precision@1 zavg - null | PMID-only (fallback) | +0.025 | +0.013 to +0.038 | +0.014 to +0.040 |
| precision@1 zavg - null | PMID+N(g) | +0.025 | +0.006 to +0.033 | +0.010 to +0.043 |
| precision@1 zavg - GLS (two-sided) | PMID-only (fallback) | +0.006 | -0.005 to +0.017 | -0.005 to +0.018 |
| precision@1 zavg - GLS, smallest-target-size stratum <= 50 | PMID-only (fallback) | +0.011 | -0.002 to +0.024 | -0.002 to +0.024 |
| precision@1 zavg - GLS, smallest-target-size stratum > 50 | PMID-only (fallback) | -0.013 | -0.032 to +0.000 | -0.042 to +0.000 |
| precision@1 zavg - GLS, smallest-target-size stratum 21-50 | PMID-only (fallback) | +0.025 | +0.000 to +0.058 | +0.008 to +0.068 |
| precision@1 zavg - GLS, smallest-target-size stratum 5-20 | PMID-only (fallback) | +0.008 | -0.007 to +0.022 | -0.007 to +0.023 |
| precision@1 zavg - GLS, smallest-target-size stratum 51-200 | PMID-only (fallback) | -0.013 | -0.032 to +0.000 | -0.042 to +0.000 |
| MRR zavg - prior | PMID-only (fallback) | +0.010 | -0.004 to +0.025 | -0.003 to +0.026 |
| MRR zavg - null | PMID-only (fallback) | +0.038 | +0.025 to +0.052 | +0.026 to +0.054 |
| MRR zavg - gls | PMID-only (fallback) | +0.016 | +0.005 to +0.027 | +0.006 to +0.028 |
| precision@1 (terms <= 50) zavg - prior | PMID-only (fallback) | +0.029 | +0.017 to +0.044 | +0.017 to +0.045 |
| precision@1 (terms <= 50) zavg - null | PMID-only (fallback) | +0.027 | +0.014 to +0.041 | +0.015 to +0.042 |
| precision@1 (terms <= 50) zavg - gls | PMID-only (fallback) | +0.011 | +0.002 to +0.021 | +0.002 to +0.022 |

Top-1 term size (t0 annotated scorable genes): zavg median 132 (IQR 84–176), ≤ 50: 0.13; prior median 200 (IQR 200–200), ≤ 50: 0.00; null (pooled matches) median 132 (IQR 82–174), ≤ 50: 0.11; gls median 140 (IQR 102–178), ≤ 50: 0.07.

## Split-half networks

precision@1 range 0.025–0.038 over 10 half networks; both primary differences exclude 0 in 10/10.

| seed/half | precision@1 (CI) | − prior (CI) | − null (CI) |
|---|---|---|---|
| 0/0 | 0.032 (0.020–0.045) | +0.032 (+0.020 to +0.045) | +0.025 (+0.013 to +0.038) |
| 0/1 | 0.030 (0.018–0.042) | +0.030 (+0.018 to +0.042) | +0.025 (+0.013 to +0.038) |
| 1/0 | 0.031 (0.019–0.044) | +0.031 (+0.019 to +0.044) | +0.026 (+0.014 to +0.039) |
| 1/1 | 0.033 (0.021–0.047) | +0.033 (+0.021 to +0.047) | +0.028 (+0.015 to +0.042) |
| 2/0 | 0.038 (0.025–0.053) | +0.038 (+0.025 to +0.053) | +0.033 (+0.019 to +0.048) |
| 2/1 | 0.027 (0.016–0.039) | +0.027 (+0.016 to +0.039) | +0.024 (+0.013 to +0.036) |
| 3/0 | 0.038 (0.025–0.053) | +0.038 (+0.025 to +0.053) | +0.032 (+0.018 to +0.047) |
| 3/1 | 0.033 (0.021–0.047) | +0.033 (+0.021 to +0.047) | +0.028 (+0.016 to +0.041) |
| 4/0 | 0.025 (0.014–0.036) | +0.025 (+0.014 to +0.036) | +0.018 (+0.007 to +0.029) |
| 4/1 | 0.027 (0.016–0.039) | +0.027 (+0.016 to +0.039) | +0.023 (+0.012 to +0.035) |

## Circularity sensitivity

| analysis | n | zavg | − prior (CI) | − null (CI) | IUT |
|---|---|---|---|---|---|
| primary: flagged excluded (targets + lists) | 809 | 0.030 | +0.030 (+0.018 to +0.043) | +0.025 (+0.013 to +0.038) | pass |
| flagged + unscannable excluded | 800 | 0.030 | +0.030 (+0.018 to +0.043) | +0.025 (+0.013 to +0.038) | pass |
| fully circular only excluded | 811 | 0.031 | +0.031 (+0.019 to +0.044) | +0.026 (+0.014 to +0.039) | pass |
| flagged removed from targets only | 809 | 0.030 | +0.030 (+0.018 to +0.043) | +0.025 (+0.013 to +0.038) | pass |
| no circularity exclusion | 820 | 0.032 | +0.032 (+0.020 to +0.045) | +0.027 (+0.014 to +0.040) | pass |

## V1 (GO CC complexes)

| analysis | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) |
|---|---|---|---|---|---|---|
| V1 all complexes | 77 | 0.182 (0.093–0.286) | 0.013 | 0.005 | +0.169 (+0.074 to +0.278) | +0.177 (+0.086 to +0.283) |
| V1 without ETC complex I and mitoribosome | 77 | 0.182 (0.093–0.286) | 0.013 | 0.005 | +0.169 (+0.074 to +0.278) | +0.177 (+0.086 to +0.283) |
| V1, hu.MAP-train members | 10 | 0.200 (0.000–0.545) | 0.000 | 0.000 | +0.200 (+0.000 to +0.545) | +0.200 (+0.000 to +0.545) |
| V1, not hu.MAP-train members | 67 | 0.179 (0.091–0.288) | 0.015 | 0.006 | +0.164 (+0.072 to +0.276) | +0.173 (+0.085 to +0.283) |
| V1 without ETC-I/mitoribosome, hu.MAP-train members | 10 | 0.200 (0.000–0.545) | 0.000 | 0.000 | +0.200 (+0.000 to +0.545) | +0.200 (+0.000 to +0.545) |
| V1 without ETC-I/mitoribosome, not hu.MAP-train members | 67 | 0.179 (0.091–0.288) | 0.015 | 0.006 | +0.164 (+0.072 to +0.276) | +0.173 (+0.085 to +0.283) |

## Named controls (window 2–300; descriptive)

| control | in H | targets (flagged) | rank of best true term / reportable | top-1 term | top V1′ label |
|---|---|---|---|---|---|
| SPRING1 | False | 1 (1) | — / 89 | GO:0019216 regulation of lipid metabolic process | GO:0032936 SREBP-SCAP complex |
| PEDS1 | True | 6 (0) | 7 / 79 | GO:0006644 phospholipid metabolic process |  |
| CCDC32 | True | 5 (4) | — / 86 | GO:0006897 endocytosis | GO:0030117 membrane coat |
| INTS15 | True | 8 (0) | — / 21 | GO:0016073 snRNA metabolic process | CP:CPX-26393 Integrator-PP2A complex |
| HAPSTR1 | True | 5 (3) | — / 61 | GO:0004842 ubiquitin-protein transferase activity | GO:0008180 COP9 signalosome |
| SLC25A51 | True | 23 (20) | — / 24 | GO:0007005 mitochondrion organization | MitoCarta: OXPHOS |
| TEDC1 | False | 1 (1) | — / 87 | GO:0007098 centrosome cycle | GO:0120099 procentriole replication complex |
| TEDC2 | False | 1 (1) | — / 80 | GO:0007098 centrosome cycle | GO:0120099 procentriole replication complex |
| POU2AF2 | False | 1 (1) | — / 23 | GO:0008270 zinc ion binding |  |
| POU2AF3 | False | 1 (1) | — / 16 | GO:0000978 RNA polymerase II cis-regulatory region sequence-specific DNA binding | CP:CPX-5646 Kinetochore CCAN complex |
| TMEM242 | True | 5 (0) | 1 / 77 | GO:0007005 mitochondrion organization | MitoCarta: OXPHOS |
| FIRRM (weak) | True | 18 (17) | — / 54 | GO:0006302 double-strand break repair | CP:CPX-478 ERCC1-XPF endonuclease complex |
| AIRIM (weak) | True | 4 (0) | 89 / 125 | GO:0006487 protein N-linked glycosylation | GO:1904949 ATPase complex |
| TMEM41B (weak) | True | 16 (0) | — / 70 | GO:0034976 response to endoplasmic reticulum stress | GO:0140534 endoplasmic reticulum protein-containing complex |

## Covariate shift and signal quintiles

| covariate | SMD H−U | SMD H−LOO | SMD U−LOO |
|---|---|---|---|
| mean_effect | -0.146 | +0.210 | +0.320 |
| sd | +0.161 | -0.212 | -0.346 |
| nan_fraction | -0.220 | +0.138 | +0.352 |
| topK_mean_zavg | +0.253 | -0.203 | -0.443 |
| R | +0.228 | -0.186 | -0.404 |
| coverage_pct | +0.247 | -0.209 | -0.453 |
| coverage_raw | -0.041 | -0.504 | -0.474 |

| quintile (zavg range) | n | zavg (CI) | prior | null | GLS | zavg − prior (CI) |
|---|---|---|---|---|---|---|
| Q1 (2.74–3.74) | 162 | 0.000 (0.000–0.000) | 0.000 | 0.005 | 0.000 | +0.000 (+0.000 to +0.000) |
| Q2 (3.74–3.92) | 162 | 0.000 (0.000–0.000) | 0.000 | 0.002 | 0.006 | +0.000 (+0.000 to +0.000) |
| Q3 (3.92–4.21) | 161 | 0.012 (0.000–0.032) | 0.000 | 0.001 | 0.012 | +0.012 (+0.000 to +0.032) |
| Q4 (4.21–5.37) | 162 | 0.019 (0.000–0.042) | 0.000 | 0.009 | 0.025 | +0.019 (+0.000 to +0.042) |
| Q5 (5.38–15.54) | 162 | 0.117 (0.067–0.174) | 0.000 | 0.007 | 0.074 | +0.117 (+0.067 to +0.174) |

## Secondary batch (reported all or none)

| comparator | precision@1 (CI) | coverage | zavg − comparator (CI) |
|---|---|---|---|
| Pearson (R1) | 0.027 (0.016–0.040) | 0.910 | +0.002 (-0.009 to +0.014) |
| Homology baseline (t0 IEA/ISS/IBA, then frequency) | 0.218 (0.184–0.253) | 0.570 | -0.188 (-0.225 to -0.153) |
| PPI module transfer (hu.MAP 3.0 top-25) | 0.049 (0.034–0.066) | 0.884 | -0.020 (-0.037 to -0.004) |

| variant | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) | IUT |
|---|---|---|---|---|---|---|---|
| t0 = 2019-07 (H rebuilt) | 649 | 0.028 (0.016–0.041) | 0.008 | 0.006 | +0.020 (+0.005 to +0.036) | +0.022 (+0.010 to +0.036) | pass |
| PMID-dated targets (all supporting PMIDs ≥ 2018-07 cut-off) | 475 | 0.034 (0.017–0.053) | 0.000 | 0.005 | +0.034 (+0.017 to +0.053) | +0.028 (+0.012 to +0.047) | pass |
| K = 10 | 809 | 0.028 (0.017–0.041) | 0.000 | 0.003 | +0.028 (+0.017 to +0.041) | +0.025 (+0.014 to +0.037) | pass |
| K = 50 | 809 | 0.033 (0.021–0.046) | 0.000 | 0.007 | +0.033 (+0.021 to +0.046) | +0.027 (+0.014 to +0.040) | pass |
| No same-arm / paralogue exclusion | 809 | 0.033 (0.021–0.046) | 0.000 | 0.005 | +0.033 (+0.021 to +0.046) | +0.029 (+0.017 to +0.042) | pass |
| U-reweighted (inverse-odds, trimmed 1/99) | 809 | 0.012 (0.007–0.019) | 0.000 | 0.004 | +0.012 (+0.007 to +0.019) | +0.008 (+0.002 to +0.015) | pass |

U-reweighting: 3301 U-eligible of 4271 scorable U genes; ESS 656; weighted zavg − GLS +0.001 (-0.008 to +0.009).
LOO-fitted calibration on H: mean p 0.089 vs observed 0.031; Brier 0.0397; intercept -1.394 (-1.835 to -0.953); slope 0.839 (0.576 to 1.102).

## Calibration model for U

Fitted on 775 H genes with a top term (34 without). Families with ≥ 30 H genes: ER_Golgi_secretory_lipid, other, signalling_lineage (reference other). Coefficients: zmean +0.2850; R +0.0000; cov_pct +1.7038; size_pct +0.0000; fam_ER_Golgi_secretory_lipid -0.1934; fam_signalling_lineage -11.8593; fam_rare +1.2437; intercept -6.3155. Saved to results/calibration/model_H.json.

## Files

core.md, secondary.md, calibration.md; methods_core.tsv, comparisons_core.tsv, per_gene_core.tsv, splithalf.tsv, circularity_sensitivity.tsv, v1.tsv, controls_case_series.tsv, covariate_smd.tsv, signal_quintiles.tsv, top1_size.tsv, secondary.tsv, reliability_oof.tsv, loo_fitted_reliability.tsv, calibration_oof.tsv, fig_*.tsv; figures manuscript/figures/m5b_{precision_by_method,reliability,controls,signal_quintiles}.{png,svg}.
