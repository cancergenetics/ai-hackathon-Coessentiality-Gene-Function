# Power simulation for the primary hold-out comparison (freeze-time, annotation only)

|H| = 820, PMID clusters = 709; seed 0; 400 simulations x 1000 cluster-bootstrap replicates; decision = percentile 95% CI of mean paired difference excludes 0.
Outcomes independent between methods given the cluster latent (conservative: real methods share neighbourhoods, which increases concordance and power).

| baseline hit@1 (comparator) | intra-cluster rho | true difference | power |
|---|---|---|---|
| 0.05 | 0.2 | 0.02 | 0.42 |
| 0.05 | 0.2 | 0.04 | 0.91 |
| 0.05 | 0.2 | 0.06 | 1.00 |
| 0.05 | 0.2 | 0.08 | 1.00 |
| 0.05 | 0.5 | 0.02 | 0.51 |
| 0.05 | 0.5 | 0.04 | 0.95 |
| 0.05 | 0.5 | 0.06 | 1.00 |
| 0.05 | 0.5 | 0.08 | 1.00 |
| 0.15 | 0.2 | 0.02 | 0.21 |
| 0.15 | 0.2 | 0.04 | 0.64 |
| 0.15 | 0.2 | 0.06 | 0.93 |
| 0.15 | 0.2 | 0.08 | 1.00 |
| 0.15 | 0.5 | 0.02 | 0.26 |
| 0.15 | 0.5 | 0.04 | 0.73 |
| 0.15 | 0.5 | 0.06 | 0.95 |
| 0.15 | 0.5 | 0.08 | 1.00 |

Minimum simulated difference with power >= 0.80, by (baseline, rho):

- baseline 0.05, rho 0.2: 0.04
- baseline 0.05, rho 0.5: 0.04
- baseline 0.15, rho 0.2: 0.06
- baseline 0.15, rho 0.5: 0.06
