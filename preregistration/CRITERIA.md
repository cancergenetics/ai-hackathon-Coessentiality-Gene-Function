# CRITERIA.md -- pre-registered uncharacterised genes (U)

Built by `scripts/03_build_preregistration.py` (criteria code: `src/knownness.py`; IDs: `src/hgnc_hub.py`). DESIGN.md v2.1 §1. **Not frozen by this script**: the PI freezes (FREEZE.sha256, tag `preregistration-v1`).
No pairwise / co-essentiality quantity was computed; DepMap was used only for single-gene summaries (mean, SD, NaN fraction, lines < -0.5) and expression single-gene summaries.

## Headline counts

- **|U| = 4,924** (of 19,296 HGNC Approved protein-coding genes)
- **|U ∩ DepMap| = 4,275** (DepMap 26Q3 CRISPRGeneEffect column by Entrez)
- **|U scorable| = 4,271** (DepMap column and >= 1 HGNC UniProt accession mapped uniquely to it by the tool's rule, `external/coessentiality/mvp/src/coessential/data.py::build_uniprot_map`)
- |U ∩ headline stratum (expressed, not chemosensory/epidermal, not tandem)| = 2,439; of which scorable 2,343

## Exact criteria

Universe: HGNC `hgnc_complete_set.txt`, status Approved, locus_group 'protein-coding gene' (19,296).

**D1** (`knownness.d1(gaf, obo, release, acc_map)`; release here: GO goa_human GAF 2026-05-21 / go-basic 2026-07-26): zero informative GO BP/MF terms with evidence in {EXP, IC, IDA, IEP, IGI, IMP, IPI, TAS}.
- rows whose qualifier contains the token NOT are removed first; `contributes_to` rows count; IPI rows count for any non-generic term regardless of the with/from partner;
- aspects P and F only (CC-only does not count); all other evidence codes ignored (HTP/HDA/HMP/HGI/HEP, IEA, ISS/ISO/ISA/ISM/IGC, IBA/IBD/IKR/IRD, RCA, NAS, ND);
- GO ids normalised with the same release's go-basic.obo (alt_id -> primary; obsolete with a single replaced_by -> replacement; unresolvable ids kept as-is);
- gene mapping: GAF column-2 UniProtKB accession (isoform suffix stripped) via HGNC `uniprot_ids` plus Swiss-Prot entries whose HGNC cross-reference names a protein-coding gene; no symbol fallback (identical rule for every release);
- generic terms that do not count (22):

  - GO:0005515: protein binding -- bare 'interacts with something'; dominated by interactome screens
  - GO:0003674: molecular_function root
  - GO:0008150: biological_process root
  - GO:0005575: cellular_component root
  - GO:0005488: binding -- MF high-level grouping term, no specificity
  - GO:0042802: identical protein binding -- self-interaction, no functional content
  - GO:0042803: protein homodimerization activity -- self-interaction, no functional content
  - GO:0046982: protein heterodimerization activity -- generic interaction term (partner unspecified)
  - GO:0019899: enzyme binding -- generic interaction with any enzyme
  - GO:0044877: protein-containing complex binding -- generic interaction term
  - GO:0003824: catalytic activity -- MF high-level grouping term (direct child of root)
  - GO:0043167: ion binding -- MF high-level grouping term
  - GO:0043168: anion binding -- MF high-level grouping term
  - GO:0043169: cation binding -- MF high-level grouping term
  - GO:0097159: organic cyclic compound binding -- MF high-level grouping term
  - GO:1901363: heterocyclic compound binding -- MF high-level grouping term
  - GO:0036094: small molecule binding -- MF high-level grouping term
  - GO:0009987: cellular process -- BP high-level grouping term (direct child of root)
  - GO:0008152: metabolic process -- BP high-level grouping term
  - GO:0065007: biological regulation -- BP high-level grouping term
  - GO:0050789: regulation of biological process -- BP high-level grouping term
  - GO:0050794: regulation of cellular process -- BP high-level grouping term

**D2**: UniProt (Swiss-Prot, 2026_03) annotation score <= 2, max over the gene's reviewed entries (entry -> gene via the entry's HGNC xref, else HGNC uniprot_ids). Genes without a reviewed entry: D2 = False (15 genes).

**D3**: <= 10 focused PubMed records (distinct PMIDs linked to the gene's Entrez id in gene2pubmed (human, 2026-10-29), counting only PMIDs linked to <= 10 distinct human GeneIDs) **or** IDG TDL = Tdark (TCRD 2023 `PharosTCRD_UniProt_Mapping.tsv`; highest TDL over the gene's accessions).

**U = D1 ∩ (D2 ∪ D3)**. No gene is ever removed from U.

## Pre-registered strata (§1.4; reporting only)

- *Family* (exclusive, in this priority): `chemosensory_epidermal` = gene belongs to one of the HGNC gene groups below; `tandem_cluster` = >= 2 Ensembl 116 paralogues (any homology type in the BioMart paralogue export: within_species_paralog, other_paralog, gene_split) whose gene body lies on the same chromosome within 1 Mb (gap between gene bodies <= 1,000,000 bp; Ensembl 116 coordinates, primary chromosomes; gene -> ENSG via HGNC); `other`. Sensitivity: tandem counting only within_species_paralog/gene_split pairs is reported as `tandem_cluster_withinspecies` (it misses most chr19 KZFP and many OR clusters, which Ensembl labels other_paralog).
- HGNC gene groups used for chemosensory/epidermal (exact names found in the universe, from patterns ['^Olfactory receptors, family \\d+$', '^Taste 1 receptors$', '^Taste 2 receptors$', '^Vomeronasal receptors$', '^Trace amine receptors$', '^Keratin associated proteins$', '^Late cornified envelope proteins$', '^Small proline rich proteins$', '^Cornified envelope precursor family$', '^S100 fused type protein family$']):

  - Cornified envelope precursor family
  - Keratin associated proteins
  - Late cornified envelope proteins
  - Olfactory receptors, family 1
  - Olfactory receptors, family 10
  - Olfactory receptors, family 11
  - Olfactory receptors, family 12
  - Olfactory receptors, family 13
  - Olfactory receptors, family 14
  - Olfactory receptors, family 2
  - Olfactory receptors, family 3
  - Olfactory receptors, family 4
  - Olfactory receptors, family 5
  - Olfactory receptors, family 51
  - Olfactory receptors, family 52
  - Olfactory receptors, family 56
  - Olfactory receptors, family 6
  - Olfactory receptors, family 7
  - Olfactory receptors, family 8
  - Olfactory receptors, family 9
  - S100 fused type protein family
  - Small proline rich proteins
  - Taste 1 receptors
  - Taste 2 receptors
  - Trace amine receptors
  - Vomeronasal receptors

- *Expression*: expressed = log2(TPM+1) >= 1.0 in >= 10% of DepMap models with expression data (`OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv`, one default entry per model: 2130 models, 1292 also in CRISPRGeneEffect); genes with no expression column: `no_expression_data` (counted as not expressed in `headline_stratum`).
- *Profile informativeness*: Chronos SD (ddof=0, as in the tool), number/fraction of lines with effect < -0.5 (fraction of non-NaN lines), NaN fraction; SD tertiles computed within U ∩ DepMap (cut points 0.1293, 0.1493); any-dependency = >= 1% of lines < -0.5.
- *Core*: <= 3 focused PMIDs and Tdark.
- *Headline stratum*: expressed & not chemosensory/epidermal & not tandem_cluster.

## Counts by stratum

| stratum | n U | n U ∩ DepMap | n U scorable |
|---|---|---|---|
| all U | 4,924 | 4,275 | 4,271 |
| family = chemosensory_epidermal | 516 | 407 | 407 |
| family = tandem_cluster | 742 | 492 | 488 |
| family = other | 3,666 | 3,376 | 3,376 |
| tandem_cluster (any family; all Ensembl paralogue types, primary) | 1,146 | 813 | 809 |
| tandem_cluster (within_species_paralog/gene_split only; sensitivity) | 680 | 407 | 403 |
| KZFP (C2H2 ZNF group, ZNF/ZSCAN/ZKSCAN/ZFP symbols) | 383 | 374 | 374 |
| KZFP & tandem_cluster | 222 | 217 | 217 |
| expression = expressed | 2,779 | 2,629 | 2,625 |
| expression = not_expressed | 2,092 | 1,643 | 1,643 |
| expression = no_expression_data | 53 | 3 | 3 |
| SD tertile within U = low | 1,425 | 1,425 | 1,425 |
| SD tertile within U = mid | 1,425 | 1,425 | 1,425 |
| SD tertile within U = high | 1,425 | 1,425 | 1,421 |
| any-dependency (>=1% lines < -0.5) | 1,105 | 1,105 | 1,101 |
| tool background (NaN fraction < 0.10) | 3,791 | 3,791 | 3,787 |
| NaN fraction > 0 | 801 | 801 | 801 |
| core (<=3 focused PMIDs & Tdark) | 2,980 | 2,553 | 2,553 |
| headline: expressed & not chemosensory & not tandem | 2,439 | 2,343 | 2,343 |
| headline & scorable & any-dependency | 725 | 725 | 725 |

## Sensitivity sets (D1, D2, D3 alone and overlaps)

| set | n genes | n in DepMap | n scorable | n scorable & expressed |
|---|---|---|---|---|
| D1 | 6,171 | 5,478 | 5,473 | 3,548 |
| D2 | 1,110 | 805 | 805 | 392 |
| D3 | 7,695 | 6,928 | 6,905 | 4,780 |
| D3_pubmed (<=10 focused PMIDs) | 7,511 | 6,780 | 6,757 | 4,670 |
| D3_tdark | 4,492 | 3,944 | 3,944 | 2,457 |
| D1 & D2 | 1,105 | 803 | 803 | 391 |
| D1 & D3 | 4,915 | 4,267 | 4,263 | 2,618 |
| D2 & D3 | 1,100 | 796 | 796 | 384 |
| D1 & D2 & D3 | 1,096 | 795 | 795 | 384 |
| D2 | D3 | 7,705 | 6,937 | 6,914 | 4,788 |
| U = D1 & (D2 | D3) | 4,924 | 4,275 | 4,271 | 2,625 |
| region: D1 only | 1,247 | 1,203 | 1,202 | 923 |
| region: D2 only | 1 | 1 | 1 | 1 |
| region: D3 only | 2,776 | 2,660 | 2,641 | 2,162 |
| region: D1 & D2 only | 9 | 8 | 8 | 7 |
| region: D1 & D3 only | 3,819 | 3,472 | 3,468 | 2,234 |
| region: D2 & D3 only | 4 | 1 | 1 | 0 |
| region: D1 & D2 & D3 | 1,096 | 795 | 795 | 384 |
| region: none | 10,344 | 10,230 | 10,215 | 8,679 |
| U & core | 2,980 | 2,553 | 2,553 | 1,392 |
| D1 & D2 & D3_tdark & <=3 PMIDs (strictest) | 867 | 674 | 674 | 317 |

## Input files (SHA-256)

| file | SHA-256 (config/data_checksums.tsv) | check |
|---|---|---|
| data/raw/hgnc/hgnc_complete_set.txt | `0f2d3f035e0e6583c055a1d9e008f275376a4b66f72af380dfc2ac730272c247` | match |
| data/raw/go/current/goa_human.gaf.gz | `db472faff1785878521693af62646546cea6af4a386609dd01c72c0554a46a30` | match |
| data/raw/go/current/go-basic.obo | `b08d45b268b8c24ccb2513dbbbc7d4df9f6521c099b413f79eb31e06e0fa3bcc` | match |
| data/raw/uniprot/uniprot_human_reviewed.tsv | `7d034c25ec83b2cb3b50fe4e4ca2724aad10d0f3baeb0405ef7f2f0e2c806db6` | match |
| data/raw/ncbi_gene/gene2pubmed_9606.tsv | `ea86631f38e2ef6491f7f85e7e066bcfa8acab458be6ec9615be05f75490b9bd` | match |
| data/raw/tcrd/PharosTCRD_UniProt_Mapping.tsv | `fc10c99fa0ae357b7bb59d0acfee8954763bb4d8031fd9be4efd30e4ccbd0555` | match |
| data/raw/depmap/CRISPRGeneEffect.csv | `1e0c492944a7297c0eda179081a1e81a1cfe41a97628facd7eddbdda1a7504ee` | match |
| data/raw/depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv | `252d1fedc7014953b19ffe5d68151b4df973c8078b12c9e5ccd97e292548d177` | match |
| data/raw/ensembl/ensembl116_human_paralogues.tsv | `003adc6bb6e0f1ad3500aee537a4df99b6d63fafc32ef024835c76f4c9570700` | match |
| data/raw/ensembl/ensembl116_gene_coordinates.tsv | `a80896b35cfdfc0bbb5755b05ac1d123d326a8eba87add554bb3ee2fdd57a1c8` | match |
| results/ids/hgnc_hub.tsv | `cc2ba221575628c9c9d6d8ecb4247a8c0c51d08722ab7a4d62cee477cac5db7b` | derived (hash at build) |
| results/preregistration/pmid_date_cutoffs.tsv | `7a485f1e694ad35d3353d94bc3026062c4603e6c1c92025545707a53bc3aced3` | derived (hash at build) |

Code at build time:

- src/knownness.py: `3fab73f711865ab1267588bda1a3a00e3997492f5e38ed4584abb0d4a4c59e7f`
- src/hgnc_hub.py: `b13b64a1fb72ce34b4bacc94551d718787cbefd19b5e5c69cc89389be665881e`
- scripts/03_build_preregistration.py: `665b152588557b2c61d655f1749991693149926195bdfa7913d886d37873f867`

## Mapping statistics

- accession map: {'n_acc_hgnc': 19204, 'n_acc_multi_gene': 64, 'n_acc_added_from_uniprot_xref': 5}
- D1 current: {'rows': 906445, 'not_rows_removed': 1501, 'rows_bpmf_d1_evidence': 416998, 'rows_primary': 416927, 'terms_primary': 12319, 'rows_alt_id': 0, 'terms_alt_id': 0, 'rows_replaced_by': 53, 'terms_replaced_by': 10, 'rows_obsolete_dropped': 18, 'terms_obsolete_dropped': 7, 'rows_unknown_dropped': 0, 'terms_unknown_dropped': 0, 'rows_unmapped': 9691, 'rows_uniprotkb_unmapped': 1287, 'rows_mapped': 410803, 'genes_with_rows': 16230, 'release': 'GO goa_human GAF 2026-05-21 / go-basic 2026-07-26', 'n_genes_D1': 6171}
- UniProt entries: {'entries': 20431, 'by_hgnc_xref': 19209, 'by_accession': 0, 'unmapped': 1222, 'genes_no_reviewed_entry': 15}
- expression: {'rows': 2314, 'default_model_rows': 2130, 'n_models': 2130, 'n_models_in_crispr': 1292, 'n_gene_columns': 19218}

<!-- BEGIN holdout (written by scripts/04_holdout_sizing.py) -->

## Temporal hold-out H (annotation only; `scripts/04_holdout_sizing.py`)

- |H| = 820; (gene, target) pairs 5,965; |T(g)| median 6 (p25 3, p75 10, max 41); H ∩ U = 0
- preliminary PMID clusters 709 (largest 9); effective n 539 (rho = 1), 650 (rho = 0.5)
- MDE (paired precision@1, 80% power, alpha 0.05 two-sided): psi 0.10: 0.038 (rho 1), 0.035 (rho 0.5), 0.031 (no clustering); psi 0.20: 0.054 (rho 1), 0.049 (rho 0.5), 0.044 (no clustering)
- named controls in H: PEDS1, CCDC32, INTS15, HAPSTR1, SLC25A51, TMEM242, FIRRM, AIRIM, TMEM41B
- details: `results/holdout/holdout_sizing.md`

<!-- END holdout -->
