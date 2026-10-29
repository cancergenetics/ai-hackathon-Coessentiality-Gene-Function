#!/usr/bin/env bash
# 01a_fetch_annotation_data.sh -- idempotent download of gene-annotation datasets.
# Each source goes to its own directory data/raw/<source>/ (git-ignored). Existing files are never overwritten.
# Downloaded files are untrusted data: this script only downloads, gunzips-to-stdout (NCBI filter) and hashes them.
# Response headers (minus cookies) are saved to data/raw/<source>/_headers/<file>.headers.txt (Last-Modified, X-UniProt-Release...).
# Not fetched (see config/data_manifest_annotation.tsv notes): CORUM (TLS cert of mips.helmholtz-muenchen.de not trusted by
# system CA store, unreachable without disabling verification), Pharos/TCRD full SQL dump (7.4 GB, not needed).
# Checksums/manifest/sanity checks: scripts/01b_check_annotation_data.py
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=data/raw
UA="predicting_gene_function-data-fetch (research; contact via repo owner)"

fetch() {  # fetch <url> <dest>
  local url="$1" dest="$2"
  if [[ -s "$dest" ]]; then echo "[skip] $dest exists"; return 0; fi
  mkdir -p "$(dirname "$dest")" "$(dirname "$dest")/_headers"
  local hdr; hdr="$(dirname "$dest")/_headers/$(basename "$dest").headers.txt"
  echo "[get ] $url -> $dest"
  curl -fsSL --retry 3 --retry-delay 5 -A "$UA" -D "$hdr.tmp" -o "$dest.part" "$url"
  grep -vi '^set-cookie' "$hdr.tmp" | tr -d '\r' > "$hdr"; rm -f "$hdr.tmp"
  mv "$dest.part" "$dest"
}

# ---------- 1. Gene Ontology: current ----------
fetch https://current.geneontology.org/ontology/go-basic.obo        $RAW/go/current/go-basic.obo
fetch https://current.geneontology.org/annotations/goa_human.gaf.gz $RAW/go/current/goa_human.gaf.gz

# ---------- 1b. Gene Ontology: archived releases closest to 2018-07-01, 2019-07-01, 2020-07-01, 2022-07-01 ----------
# Release dirs listed at https://release.geneontology.org/ ; 2018-07-01 and 2020-07-01 do not exist (404).
# Nearest: 2018-07-02, 2019-07-01, 2020-07-16 (also 2020-06-01 = nearest release ON/BEFORE the 2020-07-01 cutoff), 2022-07-01.
for d in 2018-07-02 2019-07-01 2020-06-01 2020-07-16 2022-07-01; do
  fetch https://release.geneontology.org/$d/ontology/go-basic.obo        $RAW/go/archive/$d/go-basic.obo
  fetch https://release.geneontology.org/$d/annotations/goa_human.gaf.gz $RAW/go/archive/$d/goa_human.gaf.gz
done

# ---------- 2. NCBI Gene ----------
fetch https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz $RAW/ncbi_gene/Homo_sapiens.gene_info.gz
fetch https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz                              $RAW/ncbi_gene/gene2pubmed.gz
# derived (smaller) file: header + tax_id 9606 rows only (original kept; its checksum is in the manifest)
if [[ ! -s $RAW/ncbi_gene/gene2pubmed_9606.tsv ]]; then
  gunzip -c $RAW/ncbi_gene/gene2pubmed.gz | awk -F'\t' 'NR==1 || $1=="9606"' > $RAW/ncbi_gene/gene2pubmed_9606.tsv.part
  mv $RAW/ncbi_gene/gene2pubmed_9606.tsv.part $RAW/ncbi_gene/gene2pubmed_9606.tsv
fi

# ---------- 3. UniProt human reviewed (Swiss-Prot), TSV via REST ----------
UPFIELDS="accession,id,gene_names,gene_primary,protein_name,annotation_score,protein_existence,length,cc_function,cc_subcellular_location,go_id,go_p,go_f,go_c,keyword,ft_domain,xref_pfam,xref_interpro,cc_similarity,xref_geneid,xref_hgnc,lit_pubmed_id,date_modified,version"
fetch "https://rest.uniprot.org/uniprotkb/stream?query=organism_id:9606+AND+reviewed:true&format=tsv&fields=${UPFIELDS}" \
      $RAW/uniprot/uniprot_human_reviewed.tsv
# NB: a re-run after a new UniProt release would give different content; the file is intentionally not overwritten.

# ---------- 4. Unknome (Rocha et al. 2023 PLoS Biol; unknome.mrc-lmb.cam.ac.uk, release 18 Mar 2026) ----------
fetch https://unknome.mrc-lmb.cam.ac.uk/download/prot_tsv_gz/18_Mar_2026/  $RAW/unknome/unknome_protein_table_18_Mar_2026.tsv.gz
fetch https://unknome.mrc-lmb.cam.ac.uk/download/clust_tsv_gz/18_Mar_2026/ $RAW/unknome/unknome_cluster_table_18_Mar_2026.tsv.gz

# ---------- 5. IDG / TCRD target development level (UNM TCRD downloads; Pharos site itself is not scriptable) ----------
fetch https://unmtid-dbs.net/download/TCRD/PharosTCRD_UniProt_Mapping.tsv $RAW/tcrd/PharosTCRD_UniProt_Mapping.tsv
fetch https://unmtid-dbs.net/download/TCRD/latest.README                  $RAW/tcrd/latest.README
fetch https://unmtid-dbs.net/download/TCRD/README                         $RAW/tcrd/README

# ---------- 6. Reactome ----------
fetch https://reactome.org/download/current/UniProt2Reactome_All_Levels.txt $RAW/reactome/UniProt2Reactome_All_Levels.txt

# ---------- checksums ----------
echo; echo "SHA-256 (data files only):"
find $RAW/go $RAW/ncbi_gene $RAW/uniprot $RAW/unknome $RAW/tcrd $RAW/reactome -type f -not -path '*/_headers/*' | sort | xargs shasum -a 256
