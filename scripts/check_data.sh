#!/usr/bin/env bash
# Verify SHA-256 of every raw dataset listed in config/data_checksums.tsv
set -euo pipefail
cd "$(dirname "$0")/.."
shasum -a 256 -c config/data_checksums.tsv
