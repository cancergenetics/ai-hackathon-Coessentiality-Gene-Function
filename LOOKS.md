# LOOKS.md -- one-look rule for the temporal hold-out H (DESIGN.md v2.2 §3.1, §9)

**Rule.** The hold-out outcomes (hit@1 and every metric computed against T(g)) are looked at **once** for the primary
analysis. Before H is opened, the following must already be committed and logged here: (1) the **ranker choice** (R1/R2/R3,
decided on the LOO benchmark by MRR with the tie rule of §3.1), and (2) the **calibration specification** (§3.7 model, signs,
percentile covariates, support rule). Any further look at H (debugging, a re-run, a secondary analysis, a changed
specification) is a new row, with the reason and what was changed; results from a look that follows a specification change
are reported under both the frozen and the changed rule (DESIGN revision-log rule). Looks that only touch H's *inputs*
(membership, targets, sizing; annotation data, no network outputs) are not outcome looks but are logged if they follow the tag.
Append rows; never edit or delete earlier rows. An agent appends a row **before** it runs the code that opens H and the PI fills
the commit column when committing.

| date | what was looked at | by whom | commit | preceding logged specification |
|---|---|---|---|---|
| 2026-10-30 | SPECIFICATION ENTRY (no H outcome looked at). Ranker = **R1 (raw S)**, chosen on LOO by the frozen MRR rule (R1 0.169, R2 0.140, R3 0.111; ΔR1−R2 = 0.029, CI 0.023–0.035; results/calibration/loo_ranker_choice.md). Calibration = DESIGN §3.7 exactly as frozen (logistic hit@1 ~ top-K mean zavg (≥0, raw) + R(g) (≥0, raw) + neighbourhood annotation coverage (≥0, within-release percentile) + log top-term size (≤0, within-release percentile) + module family (unconstrained); 10-fold cluster cross-fitting, fold seeds 0–4; support 5th–95th pct + family ≥30 H genes; boundary upper-bound branch; Σp_cal CI by 2,000 cluster-bootstrap refits, seed 0). Cluster fallback (DEVIATIONS 2026-10-30, set before opening H): if the largest PMID+N(g) component holds > 20% of H genes, primary CIs use PMID-only clusters; both reported. | PI | f0922e1 | DESIGN v2.3 §3.1, §3.5, §3.7 |
| 2026-10-29 | M5b primary look at H (core + secondary batch, scripts 32–35) | M5b agent | 7db89d2 | f0922e1 spec row |
| 2026-10-29 | independent verification re-derivation of M5b primary (no spec change) | verifier agent | d8959e8 | 7db89d2 |
| 2026-10-29 | EXPLORATORY post hoc look at H: complementarity of zavg_BEF with homology and PPI baselines; hit@k | exploratory agent | 4eb041c | 7db89d2 (primary already reported; no spec change) |
| 2026-10-30 | EXPLORATORY POST-REVIEW analyses on H, no spec change (manuscript round-1 referee requests; scripts/90_revision_analyses.py → results/revision/): annotation-gain rate among t0-eligible genes for p_cal rescaling; simpler calibration models (top-K mean zavg only; zavg + coverage) cross-fitted on H; deployable homology-else-zavg_BEF (and zavg-else-homology) precision@1 with cluster-bootstrap CIs and U-reweighting; named-control misses (INTS15, TMEM41B, others) | revision-analyses agent | feb6172 | 7db89d2 (primary already reported; no spec change) |
