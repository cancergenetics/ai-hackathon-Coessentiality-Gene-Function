# M5b core results on the temporal hold-out H (scripts/32)

Generated 2026-10-29T22:46:13 (runtime 297.2 s). Gate tag `preregistration-v1`. Ranker R1; bootstrap 10,000 replicates, seed 0; CIs 95% percentile (BCa in comparisons_core.tsv).

## H

H genes 820; (gene, target) pairs 5965; flagged 106 (fully circular 65); unscannable 48. Primary H (>= 1 non-flagged target): **809** (11 genes lose every target). Target pairs whose term is not a t0 V2 column: 0.

Clusters (all 820 H genes): PMID-only {'n_clusters': 709, 'largest': 9, 'largest_frac': 0.01097560975609756, 'singletons': 644}; PMID+N(g) {'n_clusters': 214, 'largest': 521, 'largest_frac': 0.6353658536585366, 'singletons': 171}. Largest PMID+N(g) component fraction 0.635 vs fallback threshold 0.2 -> **primary clusters: PMID-only (fallback)** (sensitivity: PMID+N(g)).

## Primary test (intersection-union)

| method | precision@1 | 95% CI | MRR | 95% CI | coverage | precision@1 (≤50) | n (≤50) |
|---|---|---|---|---|---|---|---|
| zavg_BEF (R1) | 0.030 | 0.018–0.043 | 0.048 | 0.035–0.062 | 0.958 | 0.029 (0.017–0.044) | 649 |
| prior-only | 0.000 | 0.000–0.000 | 0.038 | 0.032–0.045 | 1.000 | 0.000 (0.000–0.000) | 649 |
| matched-gene null | 0.005 | 0.003–0.008 | 0.010 | 0.008–0.013 | 0.966 | 0.003 (0.001–0.005) | 649 |
| GLS (R1) | 0.023 | 0.013–0.035 | 0.032 | 0.021–0.045 | 0.927 | 0.018 (0.008–0.030) | 649 |

| comparison | clusters | difference | 95% percentile CI | BCa CI | design effect | CI excludes 0 |
|---|---|---|---|---|---|---|
| precision@1 zavg - prior | PMID-only (fallback) | +0.0297 | +0.0177 to +0.0426 | +0.0189 to +0.0445 | 1.12 | True |
| precision@1 zavg - prior | PMID+N(g) | +0.0297 | +0.0105 to +0.0382 | +0.0157 to +0.0474 | 1.26 | True |
| precision@1 zavg - null | PMID-only (fallback) | +0.0247 | +0.0130 to +0.0378 | +0.0142 to +0.0398 | 1.12 | True |
| precision@1 zavg - null | PMID+N(g) | +0.0247 | +0.0055 to +0.0331 | +0.0103 to +0.0428 | 1.31 | True |
| precision@1 zavg - GLS (two-sided) | PMID-only (fallback) | +0.0062 | -0.0050 to +0.0173 | -0.0049 to +0.0175 | 0.90 | False |
| precision@1 zavg - GLS, smallest-target-size stratum <= 50 | PMID-only (fallback) | +0.0108 | -0.0016 to +0.0240 | -0.0016 to +0.0243 | 0.88 | False |
| precision@1 zavg - GLS, smallest-target-size stratum > 50 | PMID-only (fallback) | -0.0125 | -0.0325 to +0.0000 | -0.0424 to +0.0000 | 1.02 | False |
| precision@1 zavg - GLS, smallest-target-size stratum 21-50 | PMID-only (fallback) | +0.0252 | +0.0000 to +0.0579 | +0.0081 to +0.0684 | 0.98 | False |
| precision@1 zavg - GLS, smallest-target-size stratum 5-20 | PMID-only (fallback) | +0.0075 | -0.0075 to +0.0223 | -0.0073 to +0.0226 | 0.87 | False |
| precision@1 zavg - GLS, smallest-target-size stratum 51-200 | PMID-only (fallback) | -0.0125 | -0.0325 to +0.0000 | -0.0424 to +0.0000 | 1.02 | False |
| MRR zavg - prior | PMID-only (fallback) | +0.0099 | -0.0040 to +0.0251 | -0.0030 to +0.0265 | 1.14 | False |
| MRR zavg - null | PMID-only (fallback) | +0.0380 | +0.0251 to +0.0519 | +0.0265 to +0.0539 | 1.14 | True |
| MRR zavg - gls | PMID-only (fallback) | +0.0161 | +0.0052 to +0.0274 | +0.0057 to +0.0280 | 0.92 | True |
| precision@1 (terms <= 50) zavg - prior | PMID-only (fallback) | +0.0293 | +0.0167 to +0.0436 | +0.0175 to +0.0454 | 1.10 | True |
| precision@1 (terms <= 50) zavg - null | PMID-only (fallback) | +0.0265 | +0.0140 to +0.0407 | +0.0149 to +0.0422 | 1.06 | True |
| precision@1 (terms <= 50) zavg - gls | PMID-only (fallback) | +0.0108 | +0.0015 to +0.0213 | +0.0016 to +0.0222 | 1.00 | True |

**Primary IUT: PASS** (both percentile CIs > 0: True; BCa: True). Effective n = |H| / design effect: prior 719, null 722 -> not underpowered (rule < 300).

Key secondary: GLS precision@1 0.023; zavg - GLS +0.0062 (-0.0050 to +0.0173); GLS ≥ zavg: False.

## Top-1 term size (t0 annotated scorable genes)

| method | n | p10 | Q1 | median | Q3 | p90 | mean | fraction ≤ 50 |
|---|---|---|---|---|---|---|---|---|
| zavg | 775 | 46 | 84 | 132 | 176 | 196 | 127.1 | 0.125 |
| prior | 809 | 200 | 200 | 200 | 200 | 200 | 200.0 | 0.000 |
| null (pooled matches) | 3908 | 49 | 82 | 132 | 174 | 195 | 126.8 | 0.111 |
| gls | 750 | 59 | 102 | 140 | 178 | 196 | 134.3 | 0.072 |

## Split-half networks (half-specific N(g))

| seed | half | precision@1 | 95% CI | − prior | 95% CI | − matched null | 95% CI |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0.032 | 0.020–0.045 | +0.032 | +0.020 to +0.045 | +0.025 | +0.013 to +0.038 |
| 0 | 1 | 0.030 | 0.018–0.042 | +0.030 | +0.018 to +0.042 | +0.025 | +0.013 to +0.038 |
| 1 | 0 | 0.031 | 0.019–0.044 | +0.031 | +0.019 to +0.044 | +0.026 | +0.014 to +0.039 |
| 1 | 1 | 0.033 | 0.021–0.047 | +0.033 | +0.021 to +0.047 | +0.028 | +0.015 to +0.042 |
| 2 | 0 | 0.038 | 0.025–0.053 | +0.038 | +0.025 to +0.053 | +0.033 | +0.019 to +0.048 |
| 2 | 1 | 0.027 | 0.016–0.039 | +0.027 | +0.016 to +0.039 | +0.024 | +0.013 to +0.036 |
| 3 | 0 | 0.038 | 0.025–0.053 | +0.038 | +0.025 to +0.053 | +0.032 | +0.018 to +0.047 |
| 3 | 1 | 0.033 | 0.021–0.047 | +0.033 | +0.021 to +0.047 | +0.028 | +0.016 to +0.041 |
| 4 | 0 | 0.025 | 0.014–0.036 | +0.025 | +0.014 to +0.036 | +0.018 | +0.007 to +0.029 |
| 4 | 1 | 0.027 | 0.016–0.039 | +0.027 | +0.016 to +0.039 | +0.023 | +0.012 to +0.035 |

## Circularity sensitivity

| analysis | n | zavg | prior | null | − prior (CI) | − null (CI) | IUT |
|---|---|---|---|---|---|---|---|
| primary: flagged excluded (targets + lists) | 809 | 0.030 | 0.000 | 0.005 | +0.030 (+0.018 to +0.043) | +0.025 (+0.013 to +0.038) | pass |
| flagged + unscannable excluded | 800 | 0.030 | 0.000 | 0.005 | +0.030 (+0.018 to +0.043) | +0.025 (+0.013 to +0.038) | pass |
| fully circular only excluded | 811 | 0.031 | 0.000 | 0.005 | +0.031 (+0.019 to +0.044) | +0.026 (+0.014 to +0.039) | pass |
| flagged removed from targets only | 809 | 0.030 | 0.000 | 0.005 | +0.030 (+0.018 to +0.043) | +0.025 (+0.013 to +0.038) | pass |
| no circularity exclusion | 820 | 0.032 | 0.000 | 0.005 | +0.032 (+0.020 to +0.045) | +0.027 (+0.014 to +0.040) | pass |

## V1 (GO CC complexes, t0)

V1 target pairs 184 (flagged 6); ETC-I/mitoribosome terms 3; hu.MAP-train genes 1119.

| analysis | n | zavg (CI) | prior | null | − prior (CI) | − null (CI) |
|---|---|---|---|---|---|---|
| V1 all complexes | 77 | 0.182 (0.093–0.286) | 0.013 | 0.005 | +0.169 (+0.074 to +0.278) | +0.177 (+0.086 to +0.283) |
| V1 without ETC complex I and mitoribosome | 77 | 0.182 (0.093–0.286) | 0.013 | 0.005 | +0.169 (+0.074 to +0.278) | +0.177 (+0.086 to +0.283) |
| V1, hu.MAP-train members | 10 | 0.200 (0.000–0.545) | 0.000 | 0.000 | +0.200 (+0.000 to +0.545) | +0.200 (+0.000 to +0.545) |
| V1, not hu.MAP-train members | 67 | 0.179 (0.091–0.288) | 0.015 | 0.006 | +0.164 (+0.072 to +0.276) | +0.173 (+0.085 to +0.283) |
| V1 without ETC-I/mitoribosome, hu.MAP-train members | 10 | 0.200 (0.000–0.545) | 0.000 | 0.000 | +0.200 (+0.000 to +0.545) | +0.200 (+0.000 to +0.545) |
| V1 without ETC-I/mitoribosome, not hu.MAP-train members | 67 | 0.179 (0.091–0.288) | 0.015 | 0.006 | +0.164 (+0.072 to +0.276) | +0.173 (+0.085 to +0.283) |

## Named-control case series (window 2–300; descriptive, never pooled)

| control | weak | in H | targets (flagged) | reportable terms | rank of best true term | best true term | top-1 term | top V1′ label |
|---|---|---|---|---|---|---|---|---|
| SPRING1 | False | False | 1 (1) | 89 | — |  | GO:0019216 regulation of lipid metabolic process | GO:0032936 SREBP-SCAP complex |
| PEDS1 | False | True | 6 (0) | 79 | 7 | GO:0008611 ether lipid biosynthetic process | GO:0006644 phospholipid metabolic process |  |
| CCDC32 | False | True | 5 (4) | 86 | — |  | GO:0006897 endocytosis | GO:0030117 membrane coat |
| INTS15 | False | True | 8 (0) | 21 | — |  | GO:0016073 snRNA metabolic process | CP:CPX-26393 Integrator-PP2A complex |
| HAPSTR1 | False | True | 5 (3) | 61 | — |  | GO:0004842 ubiquitin-protein transferase activity | GO:0008180 COP9 signalosome |
| SLC25A51 | False | True | 23 (20) | 24 | — |  | GO:0007005 mitochondrion organization | MitoCarta: OXPHOS |
| TEDC1 | False | False | 1 (1) | 87 | — |  | GO:0007098 centrosome cycle | GO:0120099 procentriole replication complex |
| TEDC2 | False | False | 1 (1) | 80 | — |  | GO:0007098 centrosome cycle | GO:0120099 procentriole replication complex |
| POU2AF2 | False | False | 1 (1) | 23 | — |  | GO:0008270 zinc ion binding |  |
| POU2AF3 | False | False | 1 (1) | 16 | — |  | GO:0000978 RNA polymerase II cis-regulatory region sequence-specific DNA binding | CP:CPX-5646 Kinetochore CCAN complex |
| TMEM242 | False | True | 5 (0) | 77 | 1 | GO:0007005 mitochondrion organization | GO:0007005 mitochondrion organization | MitoCarta: OXPHOS |
| FIRRM | True | True | 18 (17) | 54 | — |  | GO:0006302 double-strand break repair | CP:CPX-478 ERCC1-XPF endonuclease complex |
| AIRIM | True | True | 4 (0) | 125 | 89 | GO:0006260 DNA replication | GO:0006487 protein N-linked glycosylation | GO:1904949 ATPase complex |
| TMEM41B | True | True | 16 (0) | 70 | — |  | GO:0034976 response to endoplasmic reticulum stress | GO:0140534 endoplasmic reticulum protein-containing complex |

## Covariate shift (SMD)

| covariate | mean H | mean U | mean LOO | SMD H−U | SMD H−LOO | SMD U−LOO |
|---|---|---|---|---|---|---|
| mean_effect | -0.09225 | -0.05711 | -0.1627 | -0.146 | +0.210 | +0.320 |
| sd | 0.1587 | 0.1504 | 0.1737 | +0.161 | -0.212 | -0.347 |
| nan_fraction | 0.03542 | 0.07774 | 0.01677 | -0.220 | +0.137 | +0.352 |
| topK_mean_zavg | 4.945 | 4.426 | 5.468 | +0.253 | -0.203 | -0.443 |
| R | 0.07607 | 0.04101 | 0.112 | +0.228 | -0.186 | -0.404 |
| coverage_pct | 0.4753 | 0.4099 | 0.5339 | +0.247 | -0.209 | -0.453 |
| coverage_raw | 0.6906 | 0.6954 | 0.7519 | -0.041 | -0.504 | -0.474 |

Coverage enters as within-release percentile (H at t0, U and LOO at current); raw shown for reference.

## Precision@1 by signal quintile (top-K mean zavg within H)

| quintile | n | zavg range | zavg | prior | null | GLS | zavg − prior (CI) |
|---|---|---|---|---|---|---|---|
| Q1 | 162 | 2.74–3.74 | 0.000 (0.000–0.000) | 0.000 | 0.005 | 0.000 | +0.000 (+0.000 to +0.000) |
| Q2 | 162 | 3.74–3.92 | 0.000 (0.000–0.000) | 0.000 | 0.002 | 0.006 | +0.000 (+0.000 to +0.000) |
| Q3 | 161 | 3.92–4.21 | 0.012 (0.000–0.032) | 0.000 | 0.001 | 0.012 | +0.012 (+0.000 to +0.032) |
| Q4 | 162 | 4.21–5.37 | 0.019 (0.000–0.042) | 0.000 | 0.009 | 0.025 | +0.019 (+0.000 to +0.042) |
| Q5 | 162 | 5.38–15.54 | 0.117 (0.067–0.174) | 0.000 | 0.007 | 0.074 | +0.117 (+0.067 to +0.174) |

## Notes

- Matched null: first 5 matches not annotated at t0 to any term of the full T(g) (before circularity exclusion, so the same matches serve every sensitivity); matches skipped: median 0, max 4. Each match is scored like an H query (loo=False, IPI rule for that match) and its list is compared with T(g) after g's flagged terms are dropped.
- ≤ 50 analysis: ranked lists and targets restricted to terms with ≤ 50 annotated scorable genes at t0 (g's per-query size); genes without such a target dropped (160).
- GLS strata: smallest primary-target size at t0 (the gene's true complex/module size; review round 1 item 8).
- Split halves: half top-60 lists restricted to BG_A ∩ BG_B ∩ BG_full, first 25 (scripts/15 rule); matched null and prior recomputed on each half network; clusters fixed (full-data).
- V1: same rules as V2 on GO CC terms under GO:0032991 (rows citing hu.MAP papers dropped); targets = current − t0 V1 terms of H genes with t0 size 5–200; flagged targets excluded; ETC-I = GO:0045271, mitoribosome = GO:0005761 and descendants removed from targets and lists; hu.MAP-train = gene in the tool's positive training pairs.
- Controls: targets = current − t0 V2 terms with t0 size 2–300, flagged excluded; ranked at t0 with window 2–300; V1′ (current: V1 ∪ Complex Portal ∪ MitoCarta3.0 pathways, window 2–300, own annotations removed) top reportable label.
