# Independent verification of U (DESIGN §1.2) and temporal hold-out H (§3.0, §3.2.2)

Verifier code: `verify/rederive_prereg.py` (written from DESIGN.md and the raw files; `src/knownness.py`,
`src/hgnc_hub.py` and `scripts/02–05` were **not** read or imported until after the numbers below were produced;
they were then read only to diagnose one residual discrepancy). Outputs: `verify/rederived_U.tsv`,
`verify/rederived_H_targets.tsv`, `verify/rederive_summary.json`, `verify/rederive_stdout.txt`.
No co-essentiality output was opened; DepMap was read for its header line only. Runtime ~15 s.

**Verdict: VERIFIED WITH MINOR DISCREPANCIES (explained)** — under the generic-term list that CRITERIA.md documents
(22 terms; DESIGN §1.2 says "full list in code"), U and H are reproduced exactly, gene for gene and target for target.
Under the minimal 7-term list (4 named terms + 3 roots), U loses 17 genes and H loses 1 gene; all are explained by
the extra generic terms. One non-U gene (TECPR2) differs in universe-level D1 due to obsolete-term handling.

## Implementation (independent choices)

- Universe: HGNC Approved, locus_group "protein-coding gene" → **19,296**.
- Gene mapping of GAF rows: column-2 UniProtKB accession (isoform suffix stripped) → HGNC `uniprot_ids` of universe
  genes, plus Swiss-Prot entries whose HGNC xref names a universe gene (5 accessions added). No symbol fallback
  (HGNC-only mapping gives 4,908 vs 4,907 — immaterial).
- D1: non-NOT rows (token NOT, case-insensitive), aspect P/F, evidence {EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC},
  `contributes_to` kept, GO ids resolved with the same release's go-basic (alt_id → primary; obsolete with single
  replaced_by → replacement; otherwise dropped). D1 = no non-generic term.
- D2: max annotation score over reviewed entries (entry → gene via HGNC xref, else accession) ≤ 2; no entry → False.
- D3: PMIDs linked to ≤ 10 distinct human GeneIDs in gene2pubmed; ≤ 10 such PMIDs per gene, **or** highest TCRD TDL
  over the gene's accessions = Tdark ("any accession Tdark" variant: 4,908, +1).
- DepMap: Entrez parsed from the CRISPRGeneEffect header. Scorable: in DepMap and ≥ 1 HGNC accession whose candidate
  Entrez ids (all HGNC rows) restricted to DepMap columns are exactly this gene (tool `build_uniprot_map` rule).
- H: D1 on t0 GAF (2018-07-02) with the t0 obo; ≤ 10 focused PMIDs with PMID < 29958442 (2018-07 cut-off; genes-per-PMID
  from the full file); scorable. Membership: D1-evidence non-NOT BP/MF rows (generic rows included) resolved into the
  **current** obo (3,977 t0 rows on obsolete terms dropped), propagated over is_a + part_of. T(g) = current − t0
  propagated terms, minus generic terms, with 5 ≤ (# scorable genes annotated at t0) ≤ 200.

## Headline numbers

| quantity | mine, 7-term list | mine, 22-term list | produced files |
|---|---|---|---|
| D1 (universe) | 6,148 | 6,172 | 6,171 (CRITERIA) |
| D2 / D3 / D3_pubmed / D3_tdark | 1,110 / 7,695 / 7,511 / 4,492 | same | 1,110 / 7,695 / 7,511 / 4,492 |
| **\|U\|** | **4,907** | **4,924** | **4,924** |
| \|U ∩ DepMap\| | 4,259 | 4,275 | 4,275 |
| \|U scorable\| | 4,259 | 4,271 | 4,271 |
| D1 at t0 (universe) | 6,771 | 6,793 | 6,793 |
| H candidates (scorable, D1_t0, ≤ 10 PMIDs < cut-off) | 5,040 | 5,051 | 5,051 |
| **\|H\|** | **819** | **820** | **820** |
| **total (gene, target) pairs** | **5,946** | **5,965** | **5,965** |
| H ∩ U | 0 | 0 | 0 |

## Set differences vs produced files

**22-term list:** U symmetric difference 0; H symmetric difference 0; (gene, target) pair symmetric difference 0;
term_size_t0 mismatches 0 (all target terms); per-gene mismatches in D2, annotation_score, D3, n_pubmed_focused,
n_pubmed_all, tdl, in_depmap, scorable over all 4,924 U genes: 0; n_pubmed_focused_before_cutoff and n_targets
over all 820 H genes: 0.

**7-term list (requested comparison): 17 U genes differ**, all in produced U but not in mine (U7 ⊂ U22, U7 \ U22 = ∅).
Each has exactly one non-generic D1 term under the 7-term list, and that term is on the 22-term list:

| gene | the only "informative" D1 term under 7-term list |
|---|---|
| LUC7L2, SCNM1, HDHD2, WDR70, KRT79, PHLDB3, GOLGA7B, H2AC11, H2AC13, H2AC15, H2AC16, H2AC17 | GO:0019899 enzyme binding |
| KCTD2, TEPSIN, WDR47, MB21D2 | GO:0044877 protein-containing complex binding |
| RALGAPB | GO:0046982 protein heterodimerization activity |

Of the 17: 16 in DepMap, 12 scorable (the 4 non-scorable are H2AC histone-cluster genes sharing accessions).
**H, 7-term list:** 1 gene differs — AKIRIN2 (HGNC:21407; 19 targets) is in produced H but not mine, because its only
t0 D1 term was GO:0019899 enzyme binding (not D1 at t0 under the 7-term list). All 819 common genes have identical
target sets.

**Residual (not affecting U or H):** universe D1 under the 22-term list is 6,172 vs 6,171. Diagnosis (after reading
`src/knownness.py::d1_annotations`): in D1 their "normalise" mode keeps unresolvable (obsolete, no single
replaced_by) GO ids as informative, whereas I drop them. TECPR2's only D1 term in the current GAF is obsolete → D1 True
(mine) vs False (theirs). TECPR2 fails D2 and D3, so it is outside U either way. Spec is silent on this case.

## Evidence samples (seed 0; `random.Random(0).sample`)

D1-deciding rows from the current GAF (D1-evidence, non-NOT, BP/MF; up to 4 informative + 3 generic rows shown).
"prod U" = gene present in `preregistration/uncharacterised_genes.tsv`. All 20 agree with the produced file.

| set | gene | D1 (n informative) | D2 (score) | D3 (focused PMIDs, TDL) | prod U | deciding rows |
|---|---|---|---|---|---|---|
| U | MRFAP1L1 | True (0) | False (5) | True (1, Tdark) | True | GO:0005515 IPI PMID:16189514 [generic]; GO:0005515 IPI PMID:16407074 [generic]; GO:0042802 IPI PMID:25416956 [generic] |
| U | COMMD10 | True (0) | False (5) | True (9, Tbio) | True | GO:0005515 IPI PMID:15799966 [generic] |
| U | MRPL9 | True (0) | False (4) | True (2, Tdark) | True | GO:0005515 IPI PMID:25416956, PMID:32296183 [generic] |
| U | NTN5 | True (0) | False (3) | True (1, Tdark) | True | no D1-evidence BP/MF rows |
| U | TRIM64B | True (0) | True (2) | True (0, Tdark) | True | no D1-evidence BP/MF rows |
| U | BNIP5 | True (0) | True (2) | True (1, Tdark) | True | GO:0005515 IPI PMID:32296183 [generic] |
| U | CCDC85A | True (0) | False (3) | True (1, Tdark) | True | GO:0005515 IPI PMID:32296183 [generic] |
| U | ARHGAP36 | True (0) | False (4) | True (8, Tbio) | True | no D1-evidence BP/MF rows |
| U | CT47A5 | True (0) | False (4) | True (0, Tdark) | True | no D1-evidence BP/MF rows |
| U | PHYKPL | True (0) | False (5) | True (2, Tbio) | True | GO:0005515 IPI PMID:21044950, PMID:25416956 [generic]; GO:0042802 IPI PMID:16189514 [generic] |
| non-U | EXOC4 | False (1) | False (5) | False (58, Tbio) | False | GO:0016241 regulation of macroautophagy TAS PMID:21241894 |
| non-U | MORF4L2 | False (2) | False (5) | False (20, Tbio) | False | GO:0051726 regulation of cell cycle IMP PMID:27153538; GO:1905168 IDA PMID:27153538 |
| non-U | RBFOX3 | True (0) | False (4) | False (143, Tbio) | False | no D1-evidence BP/MF rows (excluded by D2 ∪ D3) |
| non-U | TRPV6 | False (5) | False (5) | False (222, Tchem) | False | GO:0005262 calcium channel activity IDA PMID:11097838; GO:0005516 calmodulin binding IDA PMID:11278579; GO:0006816 IDA PMID:23612980 |
| non-U | IL17RE | True (0) | False (5) | False (13, Tbio) | False | GO:0005515 IPI PMID:21993848 [generic] (excluded by D2 ∪ D3) |
| non-U | CACNB2 | False (10) | False (5) | False (74, Tbio) | False | GO:0005245 IDA PMID:1309651; GO:0008331 IDA contributes_to PMID:1309651; GO:0007528 TAS PMID:8494331 |
| non-U | SMAD9 | False (5) | False (5) | False (100, Tbio) | False | GO:0000978 TAS PMID:25534700; GO:0001649 osteoblast differentiation IDA PMID:34948289; GO:0030509 BMP signaling TAS PMID:19018011 |
| non-U | UBE2G1 | False (6) | False (5) | False (41, Tbio) | False | GO:0004842 ubiquitin-protein transferase activity IDA PMID:20061386; GO:0031625 IPI PMID:11439185 |
| non-U | ELK1 | False (9) | False (5) | False (498, Tbio) | False | GO:0000981 DNA-binding TF activity IDA PMID:10799319; GO:0001228 IDA PMID:12750007 |
| non-U | ATF7 | False (9) | False (5) | False (35, Tbio) | False | GO:0000122 IDA PMID:8288576; GO:0001223 transcription coactivator binding IDA PMID:17264123 |

## Notes for the PI

- DESIGN §1.2 names only 4 generic terms + roots and defers to "full list in code"; the produced build uses 22 terms
  (CRITERIA.md lists them with rationale). The choice moves 17 genes into U (≈0.35%) and 1 gene into H. It should be
  frozen explicitly (it is, via CRITERIA.md and the hash of src/knownness.py).
- Obsolete-term handling in D1 (keep-as-informative vs drop) is not stated in DESIGN; it changes one non-U gene today
  but could matter for archive releases if reused (at t0 the produced and my D1 counts agree exactly, 6,793).
