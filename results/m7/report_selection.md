# Deep-dive report selection (DESIGN §6.5) — fixed BEFORE blinded judging results exist

Rule: highest-ranked primary top-40 genes with novelty class N2/N3 (agent L), plus up to 2 N1 rediscovery exemplars,
8–10 genes, mitochondrial-family calls ≤ 3 (none of the selected genes is mitochondrial-family).

| rank | gene | L class | predicted V2 term |
|---|---|---|---|
| 4 | TRAPPC5 | N2 | Golgi vesicle transport |
| 5 | RBM34 | N2 | DNA-templated transcription elongation |
| 12 | PLEKHH3 | N3 | regulation of PI3K/AKT signal transduction |
| 16 | CCDC71L | N2 | epigenetic regulation of gene expression |
| 21 | TM2D2 | N2 | response to ER stress |
| 28 | TM2D1 | N2 | response to ER stress |
| 31 | C5orf34 | N2 | regulation of organelle assembly |
| 33 | BICRAL | N2 | transcription coregulator binding |
| 37 | INAFM1 | N3 | polyubiquitin modification-dependent protein binding |
| 1 | ANKRD52 | N1 | regulatory ncRNA-mediated gene silencing (rediscovery exemplar; highest-ranked N1) |

Sources: results/ledger/top40_primary.tsv; results/m7/L/index_batch_*.tsv. Only one N1 exemplar is used so the total
stays within 10. TM2D1 and TM2D2 (and the N1 gene CHIC2, rank 25) share one predicted module and will be
cross-referenced. S20 genes (17/20 N1) are reported in a rediscovery table, not as reports.
