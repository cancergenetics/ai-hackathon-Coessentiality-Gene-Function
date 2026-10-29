#!/usr/bin/env bash
# 01b_fetch_orthogonal_data.sh -- fetch + checksum ORTHOGONAL datasets (idempotent).
#
# Each source goes into its own directory data/raw/<source>/ (git-ignored). Existing non-empty files are never
# re-downloaded or overwritten. Downloaded files are untrusted data: this script never executes or extracts
# them (the only exception: `unzip -p` of ONE named member of the BioGRID organism zip, written to a plain file).
# Files > 3 GB are skipped (recorded as SKIP rows). No logins/accounts; anything needing a login/captcha is SKIP.
# At the end it (re)writes config/data_manifest_orthogonal.tsv with SHA-256 + size of every file on disk.
#
# Registry columns (|-separated):  action | file(rel. data/raw) | source | url | version | licence | md5-or-member | notes
#   action GET  = download url -> file ; verify md5 if given;  "member:NAME" = url is a zip, keep only member NAME
#   action SKIP = not downloaded (recorded in manifest with the reason in notes)
#   action FAIL = attempted and failed at the time of writing (retried here; recorded as failed if it still fails)
set -uo pipefail
cd "$(dirname "$0")/.."
RAW=data/raw
MANIFEST=config/data_manifest_orthogonal.tsv
MAXBYTES=$((3*1024*1024*1024))
UA='Mozilla/5.0'
mkdir -p "$RAW" config

REGISTRY=$(cat <<'REG'
GET|humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv|hu.MAP 3.0 (Drew et al.; humap3.proteincomplexes.org)|https://humap3.proteincomplexes.org/static/downloads/humap3/hu.MAP3.0_complexes_wConfidenceScores_total15326_wGenenames_20240922.csv|hu.MAP 3.0, file stamp 2024-09-22|CC0 (+BY requested) per humap3 download page|-|15,326 complexes; cols HuMap3_ID,ComplexConfidence(1-6),Uniprot_ACCs,genenames
GET|humap3/humap3_complex_pairs_20240929.pairsWprob|hu.MAP 3.0|https://humap3.proteincomplexes.org/static/downloads/humap3/humap3_complex_pairs_20240929.pairsWprob|hu.MAP 3.0, file stamp 2024-09-29|CC0 (+BY requested) per humap3 download page|-|pairs inside complexes w/ ML probability; UniProt ACCs, tab-separated, no header
GET|humap3/hu.MAP3.0_complex_pairs_genenames_20240930.pairsWprob|hu.MAP 3.0|https://humap3.proteincomplexes.org/static/downloads/humap3/hu.MAP3.0_complex_pairs_genenames_20240930.pairsWprob|hu.MAP 3.0, file stamp 2024-09-30|CC0 (+BY requested) per humap3 download page|-|as above, gene symbols
GET|humap3/humap3_all_ppis_202305.pairsWprob.gz|hu.MAP 3.0|https://humap3.proteincomplexes.org/static/downloads/humap3/humap3_all_ppis_202305.pairsWprob.gz|hu.MAP 3.0, file stamp 2023-05 (server Last-Modified 2024-09-30)|CC0 (+BY requested) per humap3 download page|-|ALL pairwise ML interaction probabilities (UniProt); NOTE hu.MAP training uses BioPlex/Hein/CORUM-style evidence: not independent of BioPlex
SKIP|humap3/nodeTable.txt|hu.MAP 3.0|https://humap3.proteincomplexes.org/static/downloads/nodeTable.txt|n/a|CC0 (+BY requested) per humap3 download page|-|link on download page returns HTTP 404 (not needed: symbols are in the complex files)
GET|opencell/opencell-protein-interactions.csv|OpenCell (Cho et al. 2022 Science)|https://opencell.czbiohub.org/data/datasets/opencell-protein-interactions.csv|OpenCell processed datasets, server Last-Modified 2022-03-07|CC BY-SA 4.0 per AWS Open Data registry entry czb-opencell; download page itself states no licence (treat as unverified for derived tables)|-|IP-MS significant interactions (HEK293T), Ensembl/UniProt/symbol columns
GET|opencell/opencell-localization-annotations.csv|OpenCell|https://opencell.czbiohub.org/data/datasets/opencell-localization-annotations.csv|OpenCell processed datasets, 2022-03-07|as above|-|manual localisation categories, grades 1-3
GET|opencell/opencell-library-metadata.csv|OpenCell|https://opencell.czbiohub.org/data/datasets/opencell-library-metadata.csv|OpenCell processed datasets, 2022-03-07|as above|-|1,310 tagged lines; Ensembl gene IDs (ID mapping)
GET|hpa/subcellular_location.tsv.zip|Human Protein Atlas|https://www.proteinatlas.org/download/tsv/subcellular_location.tsv.zip|HPA v25.1 (download page text; server Last-Modified 2025-11-06)|CC BY 4.0 for copyrightable parts (proteinatlas.org/about/licence); third-party constraints possible|-|zip contains subcellular_location.tsv; Ensembl gene IDs + symbols
GET|humancellmap/baits-latest.txt|Human Cell Map / BioID (Go et al. 2021 Nature)|https://humancellmap.org/resources/downloads/baits-latest.txt|Cell Map v1 (latest == v1; Last-Modified 2025-10-14)|CC BY 4.0 per humancellmap.org download page|-|profiled baits
GET|humancellmap/preys-latest.txt|Human Cell Map|https://humancellmap.org/resources/downloads/preys-latest.txt|Cell Map v1 (2025-10-14)|CC BY 4.0 per humancellmap.org download page|-|significant preys with NMF localisation predictions (incl. SAFE/NMF columns)
GET|humancellmap/not-significant-latest.txt|Human Cell Map|https://humancellmap.org/resources/downloads/not-significant-latest.txt|Cell Map v1 (2025-10-14)|CC BY 4.0 per humancellmap.org download page|-|detected but not significant preys
GET|humancellmap/saint-latest.txt|Human Cell Map|https://humancellmap.org/resources/downloads/saint-latest.txt|Cell Map v1 (2025-10-14)|CC BY 4.0 per humancellmap.org download page|-|SAINTexpress bait-prey table (interaction data)
GET|huri/HuRI.tsv|HuRI (Luck et al. 2020 Nature)|https://www.interactome-atlas.org/data/HuRI.tsv|HuRI (HI-III-20)|CC BY 4.0 expected (Nature OA paper); site terms unverified|-|Ensembl gene ID pairs. FAILED at time of writing: apex host interactome-atlas.org does not resolve in DNS; www.interactome-atlas.org serves a TLS cert for the apex only (name mismatch). Not bypassed (no -k / DNS override). Retry later; HuRI edges are also inside BioGRID (Luck 2020 source).
GET|huri/Lit-BM.tsv|HuRI / Lit-BM (Luck et al. 2020)|https://www.interactome-atlas.org/data/Lit-BM.tsv|Lit-BM-17|as above|-|same failure as HuRI.tsv
GET|string/9606.protein.links.detailed.v12.5.txt.gz|STRING|https://stringdb-downloads.org/download/protein.links.detailed.v12.5/9606.protein.links.detailed.v12.5.txt.gz|STRING v12.5 (Last-Modified 2026-08-01)|CC BY 4.0 (string-db.org/cgi/access)|-|per-channel subscores: neighborhood, fusion, cooccurence, coexpression, experimental, database, textmining, combined_score; ENSP ids (9606.ENSP...). Exclude textmining/database/coexpression channels downstream
GET|string/9606.protein.physical.links.detailed.v12.5.txt.gz|STRING|https://stringdb-downloads.org/download/protein.physical.links.detailed.v12.5/9606.protein.physical.links.detailed.v12.5.txt.gz|STRING v12.5 (2026-08-01)|CC BY 4.0|-|physical subnetwork with experimental/database/textmining subscores
GET|string/9606.protein.info.v12.5.txt.gz|STRING|https://stringdb-downloads.org/download/protein.info.v12.5/9606.protein.info.v12.5.txt.gz|STRING v12.5 (server file Last-Modified 2023-05-31)|CC BY 4.0|-|ENSP -> preferred symbol, size, annotation
GET|string/9606.protein.aliases.v12.5.txt.gz|STRING|https://stringdb-downloads.org/download/protein.aliases.v12.5/9606.protein.aliases.v12.5.txt.gz|STRING v12.5 (server file Last-Modified 2023-05-31)|CC BY 4.0|-|ENSP -> aliases incl. Ensembl gene, UniProt, Entrez, HGNC
GET|biogrid/BIOGRID-ORGANISM-Homo_sapiens-5.0.262.tab3.txt|BioGRID|https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/BIOGRID-5.0.262/BIOGRID-ORGANISM-5.0.262.tab3.zip|BioGRID 5.0.262 (released 2026-09-29)|MIT licence (downloads.thebiogrid.org); cite Stark 2006 / Oughtred|member:BIOGRID-ORGANISM-Homo_sapiens-5.0.262.tab3.txt|TAB3, Homo sapiens only (organism zip deleted after member extraction; zip sha256 in sidecar .zip.sha256). Contains physical AND genetic interactions; includes HuRI/BioPlex/OpenCell-derived rows, so not independent of those sets
GET|biogrid_orcs/BIOGRID-ORCS-ALL-homo_sapiens-LATEST.screens.tar.gz|BioGRID ORCS (CRISPR screens, curated gene-level scores)|https://downloads.thebiogrid.org/Download/BioGRID-ORCS/Latest-Release/BIOGRID-ORCS-ALL-homo_sapiens-LATEST.screens.tar.gz|BioGRID ORCS 2.0.18 (index file name; 'Latest-Release' as of 2026-10-29; 1952 human screens)|MIT licence (downloads.thebiogrid.org); each screen retains its original publication terms|-|NOT extracted (untrusted tar). Contains the Cell version of Olivieri 2020 (PMID 32649862: 31 screens, 17,382 genes, Z-scores) plus 484 drug-exposure screens (e.g. Lau 2020 PMID 32028983: 27 screens up to 20.7k genes; Vervoort 2021; Ramaker 2021; Kwanten 2023), but ALSO DepMap/Avana-derived and other essentiality screens: exclude those from any orthogonal use
GET|olivieri2020/biorxiv_845446_TableS1_media-1.xlsx|Olivieri et al. 2020 Cell, bioRxiv preprint 10.1101/845446v1 (RPE1-hTERT TP53-/- genotoxin CRISPR screens)|https://www.biorxiv.org/content/biorxiv/early/2019/11/18/845446/DC1/embed/media-1.xlsx?download=true|bioRxiv v1, 2019-11-18 (preprint; may differ slightly from Cell version)|CC BY-NC-ND 4.0 (bioRxiv): non-commercial, NO derivatives, do not redistribute|-|Table S1: screen summary (28 screens)
GET|olivieri2020/biorxiv_845446_TableS2_NormZ_media-2.xlsx|Olivieri et al. 2020, bioRxiv preprint|https://www.biorxiv.org/content/biorxiv/early/2019/11/18/845446/DC2/embed/media-2.xlsx?download=true|bioRxiv v1, 2019-11-18|CC BY-NC-ND 4.0 (bioRxiv): non-commercial, NO derivatives, do not redistribute|-|Table S2: DrugZ NormZ per gene per screen (sheet Zscores_28screens). Cell-version supplement (PMC7384976, mmc2) is behind a reCAPTCHA/proof-of-work wall: not fetched. Preprint has 28 screens vs 31 in Cell
GET|replogle2022_perturbseq/K562_gwps_normalized_bulk_01.h5ad|Replogle et al. 2022 Cell, genome-wide Perturb-seq (figshare+ 20029387)|https://ndownloader.figshare.com/files/35773217|figshare+ article 20029387 v1 (2022-06-09)|CC BY 4.0 (figshare+ record)|a3dfaa94ea8724217f5ecb1e14a5f0c8|K562 genome-wide (~9.8k perturbations x ~8k genes) pseudo-bulk mean expression, z-normalised (normalized_bulk). h5ad (HDF5)
GET|replogle2022_perturbseq/K562_essential_normalized_bulk_01.h5ad|Replogle et al. 2022|https://ndownloader.figshare.com/files/35780870|figshare+ 20029387 v1|CC BY 4.0 (figshare+ record)|30496767641cd2e660ee6ecb5baee132|K562 essential-gene screen pseudo-bulk, z-normalised
GET|replogle2022_perturbseq/rpe1_normalized_bulk_01.h5ad|Replogle et al. 2022|https://ndownloader.figshare.com/files/35775512|figshare+ 20029387 v1|CC BY 4.0 (figshare+ record)|6f1e7d6a09e2f869759e3c4526b7f171|RPE1 essential-gene screen pseudo-bulk, z-normalised
GET|replogle2022_perturbseq/annotated_embedding_coordinates.csv|Replogle et al. 2022 (figshare+ 21632564, commonly requested supplemental files)|https://ndownloader.figshare.com/files/38349302|figshare+ 21632564 v1 (2022-11-29)|CC0 (figshare+ record)|fb848d4223f03d9486ff45bf26a3049b|perturbation embedding coordinates + cluster annotation
SKIP|replogle2022_perturbseq/K562_gwps_normalized_singlecell_01.h5ad|Replogle et al. 2022|https://ndownloader.figshare.com/files/35774440|figshare+ 20029387|CC BY 4.0|-|SKIPPED: 65.8 GB single-cell matrix (> 3 GB). Same for K562_gwps_raw_singlecell (65.8 GB), K562/RPE1 *_singlecell (8.7-10.7 GB); raw_bulk files also exist (not needed)
SKIP|replogle2022_perturbseq/anderson-darling_pvalues_BH.csv.gz|Replogle et al. 2022|https://ndownloader.figshare.com/files/38349308|figshare+ 21632564|CC0|-|SKIPPED by choice: 488 MB, not requested (transcriptome-wide AD p-values); clustered_mean_gene_expression_figs2-4.csv.gz (38 MB, file 38349305) also available
GET|proteomehd/coregulation_scores.zip|ProteomeHD (Kustatscher et al. 2019 Nat Biotechnol)|https://ftp.pride.ebi.ac.uk/pride/data/archive/2019/11/PXD008888/coregulation_scores.zip|PRIDE PXD008888 (2019-11), ProteomeHD v1.1|unverified (PRIDE open data; no licence stated on file; GitHub repo Rappsilber-Laboratory/ProteomeHD has no LICENSE file)|-|zip (194 MB) with coregulation_scores.csv (treeClust+TOM scores, ~12.6M UniProt pairs). Not extracted
SKIP|proteomehd/ProteomeHD_v1_1.7z|ProteomeHD|https://raw.githubusercontent.com/Rappsilber-Laboratory/ProteomeHD/master/Data/ProteomeHD_v1_1.7z|GitHub master (2019-11-05)|unverified|-|SKIPPED: protein-level SILAC ratio matrix (9 MB, 7z, no 7z tool installed); not needed for pair scores
GET|burke2023_af2/table_AF2_HURI_HuMap_UNIQUE.csv|Burke et al. 2023 NSMB, AlphaFold2 human PPI predictions (archive.bioinfo.se/huintaf2)|https://archive.bioinfo.se/huintaf2/table_AF2_HURI_HuMap_UNIQUE.csv|Burke et al. 2023 (table dated 2021-11-20); SciLifeLab figshare 10.17044/scilifelab.16945039|CC BY 4.0 (figshare record 16945039 and paper)|-|65,484 pairs (HuRI + hu.MAP 2) with pDockQ, plDDT, IF_plDDT; UniProt IDs + gene symbols + ENSG for HuRI pairs. Pair set is pre-selected from HuRI/hu.MAP, not proteome-wide
GET|predictomes2025/20251110_hs_predictome_pair_scores.csv.gz|Predictomes human proteome screen (Schmid et al. 2025 bioRxiv 10.1101/2025.11.10.687652; predictomes.org/downloads)|https://predictomes-hsbps-dataset.s3.us-east-1.amazonaws.com/20251110_hs_predictome_pair_scores.csv.gz|file stamp 2025-11-10|CC BY 4.0 per predictomes.org/downloads|-|SPOC scores for ~1.6M human pairs (AlphaFold-Multimer, KIRC-prefiltered); preprint, not yet peer-reviewed. Note KIRC prefilter uses non-orthogonal features (coexpression, STRING-type evidence)
SKIP|predictomes2025/hs_predictomes_top_16k_export.tar|Predictomes|https://predictomes-hsbps-dataset.s3.us-east-1.amazonaws.com/hs_predictomes_top_16k_export.tar|2025-11|CC BY 4.0|-|SKIPPED: 53.2 GB (> 3 GB) structure models for top 16k pairs; full set 4.32 TB in 100 tars
REG
)

log() { echo "[$(date +%H:%M:%S)] $*" >&2; }
fsize() { wc -c < "$1" | tr -d ' '; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }

remote_len() {  # content-length after redirects, or empty
  curl -sIL -m 40 -A "$UA" "$1" | tr -d '\r' | awk 'tolower($1)=="content-length:"{l=$2} END{print l}'
}

download() {  # url dest
  local url=$1 dest=$2 part="$2.part" try
  for try in 1 2 3; do
    if curl -fsSL --retry 2 -m 3600 -A "$UA" -o "$part" "$url"; then mv "$part" "$dest"; return 0; fi
    rm -f "$part"; sleep $((try*5))
  done
  return 1
}

while IFS='|' read -r action file source url version licence md5 notes; do
  [ -z "$action" ] && continue
  [ "$action" = SKIP ] && { log "SKIP  $file (recorded only)"; continue; }
  dest="$RAW/$file"; mkdir -p "$(dirname "$dest")"
  if [ -s "$dest" ]; then log "have  $file"; continue; fi
  len=$(remote_len "$url")
  if [ -n "$len" ] && [ "$len" -gt "$MAXBYTES" ] 2>/dev/null; then log "SKIP  $file: $len bytes > 3 GB"; continue; fi
  log "get   $file  (${len:-?} bytes)"
  case "$md5" in
    member:*)
      member=${md5#member:}; zipf="$dest.zip.download"
      if download "$url" "$zipf"; then
        sha "$zipf" > "$dest.zip.sha256"
        unzip -p "$zipf" "$member" > "$dest.part" && mv "$dest.part" "$dest" || { log "FAIL unzip member $member"; rm -f "$dest.part"; }
        rm -f "$zipf"
      else log "FAIL  $file ($url)"; fi ;;
    *)
      if download "$url" "$dest"; then
        if [ "$md5" != "-" ]; then
          got=$(md5 -q "$dest" 2>/dev/null || md5sum "$dest" | cut -d' ' -f1)
          [ "$got" = "$md5" ] || { log "MD5 MISMATCH $file expected $md5 got $got"; mv "$dest" "$dest.md5mismatch"; }
        fi
      else log "FAIL  $file ($url)"; fi ;;
  esac
  case "$file" in olivieri2020/*) sleep 20;; esac   # bioRxiv rate-limits (HTTP 429)
done <<< "$REGISTRY"

# ---- manifest -------------------------------------------------------------------------------------------------
{
  printf 'file\tsource\turl\tversion\tsha256\tsize_bytes\tlicence\tnotes\n'
  while IFS='|' read -r action file source url version licence md5 notes; do
    [ -z "$action" ] && continue
    dest="$RAW/$file"
    if [ -s "$dest" ]; then
      s=$(sha "$dest"); n=$(fsize "$dest"); extra=""
      [ -s "$dest.zip.sha256" ] && extra=" [organism zip sha256 $(cat "$dest.zip.sha256"), deleted after extraction]"
      printf 'data/raw/%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s\n' "$file" "$source" "$url" "$version" "$s" "$n" "$licence" "$notes" "$extra"
    else
      st="NOT DOWNLOADED"; [ "$action" = SKIP ] || st="NOT DOWNLOADED (download failed/blocked)"
      printf 'data/raw/%s\t%s\t%s\t%s\t\t\t%s\t%s: %s\n' "$file" "$source" "$url" "$version" "$licence" "$st" "$notes"
    fi
  done <<< "$REGISTRY"
} > "$MANIFEST"
log "manifest written: $MANIFEST"
