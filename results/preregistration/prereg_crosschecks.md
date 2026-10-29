# Pre-registration cross-checks

- annotation_score identical to feature table: 19296/19296
- TDL identical: 19296/19296
- n_pubmed_focused identical: 19296/19296
- genes with >=1 low-throughput experimental informative BP/MF term in the feature table but D1=True (expected only where the feature table's current-GAF symbol fallback mapped a row): 0 []
- genes D1=False only because of TAS/IC (no EXP/IDA/IPI/IMP/IGI/IEP informative term): 1157
- diagnostic: D1-eligible UniProtKB rows with unmapped accession 1287; a symbol fallback would map 0 informative rows and flip D1 for 0 genes (). Not applied (accession-only mapping for every release); these genes are flagged `d1_symbol_fallback_would_flip`.

- D1 genes: 6171; D2: 1110; D3: 7695; U: 4924
- U genes in DepMap but not scorable: 4 ['H2AC11', 'H2AC15', 'H2AC16', 'H2AC17']
- U genes in DepMap with NaN fraction >= 0.10 (outside the tool background): 484
- U genes without expression column: 53
- Known common essentials (sign check; mean Chronos): RPL3 -2.51, PCNA -2.97, POLR2B -2.34, SNRPD1 -2.92
- KZFP tandem check: fraction of U KZFPs on chr19 flagged tandem = 172/215
- Olfactory receptor tandem check (all universe ORs): 351/419
