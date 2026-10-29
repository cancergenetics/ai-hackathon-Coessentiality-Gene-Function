# Independent verification of the M5b temporal hold-out PRIMARY result

Verifier agent, 2026-10-29. LOOKS.md row appended before any H outcome was computed ("independent verification
re-derivation of M5b primary (no spec change)", preceding 7db89d2). Nothing else was edited and nothing was committed.

**Verdict: VERIFIED WITH MINOR DISCREPANCIES (explained).** Every primary number is reproduced exactly: per-gene hit@1
for zavg_BEF, prior-only and the matched null agrees for 809/809 genes. Three top-1 *term labels* differ (none of them a
hit, so no hit changes). All three come from how GAF rows are mapped to genes and are explained below.

## Method

`verify/rederive_holdout.py` was written from DESIGN.md §3.0–§3.3 and §3.5, the LOOKS.md f0922e1 specification row and
the DEVIATIONS.md rows of 2026-10-29/30. It imports only `src/gate.py` (`gate.check()` passes). It does **not** import
scripts/32–34, `scripts/m5b_common.py`, `src/vocab.py` or `src/predictor.py`. I re-implemented each step myself:

- Parsing of the current obo (alt_id, single replaced_by, is_a + part_of closure).
- Parsing of the t0 GAF 2018-07-02 (aspect P/F, D1 codes, NOT and colocalizes_with dropped).
- Mapping each UniProt accession to a gene through the hub.
- The IPI with/from rule with per-query re-propagation and per-query term sizes.
- Chromosome arms parsed from the hub `location` field.
- Ensembl 116 paralogues.
- N(g) as the top 25 background genes.
- R1, with the ≥ 2-partner reportability rule, a 5–200 candidate window and circularity removal (from T(g) and from
  every ranked list).
- The prior-only ranking.
- The matched null: walk M(g), skip matches annotated at t0 to the full T(g), keep the first 5.
- PMID-only clusters by union-find on the supporting PMIDs.
- A paired cluster bootstrap (10,000 replicates, `default_rng(0)`, percentile CIs).

Two inputs were taken as given: T(g) from `results/holdout/H_targets.tsv`, and the matched lists from
`data/derived/matched/matched_lists.npz`.

## Primary numbers (n = 809 primary H genes, 703 PMID-only clusters)

| quantity | re-derived | M5b SUMMARY |
|---|---|---|
| primary H (≥ 1 unflagged target) | 809 / 820 | 809 / 820 |
| precision@1 zavg_BEF | 0.02967 (24 hits) | 0.030 (0.029666) |
| precision@1 prior-only | 0.000 | 0.000 |
| precision@1 matched null | 0.004944 | 0.005 (0.004944) |
| Δ zavg − prior (95% CI) | +0.0297 (+0.0175 to +0.0429) | +0.030 (+0.0177 to +0.0426) |
| Δ zavg − null (95% CI) | +0.0247 (+0.0127 to +0.0379) | +0.025 (+0.0130 to +0.0378) |
| IUT | PASS | PASS |
| zavg coverage | 0.959 (776) | 0.958 (775) |

The CI endpoints differ by ≤ 0.0004. The per-gene inputs and the clusters are identical, so this gap is Monte Carlo
noise between two bootstrap implementations.

## Per-gene agreement with `results/holdout_eval/per_gene_core.tsv`

| field | agreement |
|---|---|
| hit@1, zavg_BEF | 100% (809/809) |
| hit@1, prior-only | 100% |
| top-1 term, prior-only | 100% |
| null hit (per gene) | 100% |
| matched genes used by the null | 100% |
| top-1 term, zavg_BEF | 806/809 (99.6%) |

Other checks that agree:

- N(g) is identical for all 820 H genes, compared with `data/derived/neighbours/full_top100.npz`.
- My paralogue sets match `paralogues_by_matrix_index.npz` for all genes.
- My PMID clusters are identical to `pmid_cluster` in H_genes.tsv.

The three genes whose top-1 zavg_BEF term differs are not hits under either version:

- **TMEM9.** M5b has no reportable term. I report GO:0002478, supported by HLA-A and HLA-DQA1. The cause is that my
  mapping falls back to the GAF symbol when an accession is not found, which recovers HLA-A rows. M5b uses no symbol
  fallback. This one gene also explains the coverage difference (776 vs 775).
- **ADGRG5** (GO:0007268 here, GO:0006813 in M5b) and **SLC35F2** (GO:0034330 here, GO:0051098 in M5b). Here PCDHB11,
  PCDHB6 and NECTIN3 carry t0 annotations. In M5b their annotations are dropped. M5b's accession map
  (`knownness.build_acc_map`) is built from HGNC protein-coding genes only. PCDHB11 is HGNC locus_group "other"
  (a constituent of a complex locus), so its annotations are lost, even though it is a scorable matrix gene.
  - This affects 63 scorable genes that lie outside the universe.
  - DESIGN does not say how accessions map to genes.

Running my script with both of M5b's mapping choices (`--variant universe_only,no_symbol_fallback`) reproduces M5b
exactly:

- top-1 terms agree for 809/809 genes;
- the number of base candidate terms is 5,856, as in their run.log.

## Robustness notes

- **Ties at the top of R1.** In 401 of 820 genes the top S is tied, almost always between a term and its ancestor,
  which share the same supporting neighbours. DESIGN does not fix the R1 tie rule, and M5b uses ascending GO id.
  - Ordering ties by descending GO id instead changes 393 top-1 labels.
  - The result barely moves: precision@1 0.032 (26 hits), Δ prior +0.032 (+0.020 to +0.046), Δ null +0.027
    (+0.015 to +0.040), IUT PASS.
- **Other choices tested, none of which changes any hit:**
  - supporting partners counted only when z > 0;
  - annotations restricted to scorable genes only;
  - ambiguous accessions assigned to every gene they name.

## Files

- `verify/rederive_holdout.py`. Use `--variant` to switch the diagnostic choices and `--debug SYMBOLS` to print one
  gene's ranked terms.
- Per-gene outputs were written to the session scratchpad and are not committed. Re-run the script to regenerate them.
