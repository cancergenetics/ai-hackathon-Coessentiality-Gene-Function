# DATA.md — datasets used

All raw files live under `data/raw/<source>/` (git-ignored; never committed). Checksums (SHA-256) are in
`config/data_checksums.tsv`; verify with `scripts/check_data.sh`. Each row below names source, version, checksum, licence.
Any dataset added later must be added here **and** to `config/data_checksums.tsv` in the same commit.

## Method (tool)

| Item | Source | Version | Checksum | Licence |
|---|---|---|---|---|
| Co-essentiality tool (`zavg_BEF`, package `coessential` in `mvp/`) | https://github.com/cancergenetics/ai-hackathon-Coessentiality | git commit `3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf` | git commit hash | see repository (no LICENSE file at this commit; used read-only, never modified, not redistributed) |

Fetched by `scripts/00_get_tool.sh` into `external/coessentiality/` (git-ignored).

## User-provided data (copied from the user's local project folders on 2026-10-29)

These files were provided by the user (same files the tool's authors used); their SHA-256 values match those recorded in the
tool repository's `DATA.md`. DepMap files carry no version stamp; release 26Q3 is as stated by the user/tool.

| File | Source | Version | SHA-256 | Licence |
|---|---|---|---|---|
| depmap/CRISPRGeneEffect.csv | DepMap Portal (Broad) | Public 26Q3 (user-stated) | 1e0c492944a7297c0eda179081a1e81a1cfe41a97628facd7eddbdda1a7504ee | CC BY 4.0 |
| depmap/Model.csv | DepMap Portal | 26Q3 | 65eb1895800e71a963a3ab56e5d08c8d006cb0d9e7aa68f7e34a3810a2a3cbc7 | CC BY 4.0 |
| depmap/ModelCondition.csv | DepMap Portal | 26Q3 | a1edda78cd60718e5c99690ce8ab80315b65ddc9346643338d2c1c774fc51326 | CC BY 4.0 |
| depmap/CRISPRConfounders.csv | DepMap Portal | 26Q3 | 0e098325d53403d7852f3a773477d20a508a9bf29f43e10fe28bf0f550b35779 | CC BY 4.0 |
| depmap/OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv | DepMap Portal | 26Q3 | 252d1fedc7014953b19ffe5d68151b4df973c8078b12c9e5ccd97e292548d177 | CC BY 4.0 |
| depmap/OmicsProfiles.csv | DepMap Portal | 26Q3 | 4241e537f0b23139c0e525b4d78fb53ee65c5507771a33e2cd5debd78f7179ea | CC BY 4.0 |
| depmap_rnai/D2_combined_gene_dep_scores.csv | DepMap Portal, DEMETER2 (McFarland et al. 2018) | v6 (user-stated) | 6bfe7b24ef191debccd502b7dfe61c4b0763caba3e02c6c14e521c8226bb98a7 | CC BY 4.0 |
| hgnc/hgnc_complete_set.txt | HGNC, genenames.org | download date unknown (user-provided; file dated 2026-04-23) | 0f2d3f035e0e6583c055a1d9e008f275376a4b66f72af380dfc2ac730272c247 | CC0 |
| bioplex/BioPlex_293T_Network_10K_Dec_2019.tsv | BioPlex 3.0 (Huttlin et al. 2021) | Dec 2019 | 5a98def087fc77c7bf07aac79e2553fd64ea1a27a7d0c4617870476f3f120833 | BioPlex terms (free for research; unverified) |
| bioplex/BioPlex_HCT116_Network_5.5K_Dec_2019.tsv | BioPlex 3.0 | Dec 2019 | b37be6de6fe15e948151ab9480cfcb88a6795780cf7a4059b386b07f3c1e760d | as above |
| ccle_proteomics/protein_quant_current_normalized.xlsx | CCLE proteomics (Nusinow et al. 2020, Cell) | as published | a0ec29ad609d309d884852c268e3382ea6b38bca171af2cf59e4f38a518d21ff | per publisher / DepMap terms (unverified) |
| ensembl/ensembl116_human_paralogues.tsv | Ensembl BioMart | Ensembl 116 | 003adc6bb6e0f1ad3500aee537a4df99b6d63fafc32ef024835c76f4c9570700 | Ensembl: no restrictions |
| ensembl/ensembl116_gene_coordinates.tsv | Ensembl BioMart | Ensembl 116 | a80896b35cfdfc0bbb5755b05ac1d123d326a8eba87add554bb3ee2fdd57a1c8 | Ensembl: no restrictions |
| humap_train/Train_positive_pairs.txt | hu.MAP 3.0 train split (Fischer et al. 2025), from the tool authors | hu.MAP 3.0 (user-stated) | 77276dbac8ca108cac4a9c196b0d26bfac3912b616d9647b44adacdc88092fc9 | CC BY 4.0 per paper (file licence unverified) |
| humap_train/Train_negative_pairs.txt | as above | as above | c37e27dfe12ddfcecc34e084719a4f8b2aaf47e106455e3da46d7199aed836f3 | as above |

## Downloaded public data

(added as acquired; see `scripts/01_fetch_public_data.*`)
