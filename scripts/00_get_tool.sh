#!/usr/bin/env bash
# Fetch the co-essentiality tool at the pinned commit (read-only use; never modified).
set -euo pipefail
cd "$(dirname "$0")/.."
TOOL_COMMIT=3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf
if [ ! -d external/coessentiality ]; then
  git clone https://github.com/cancergenetics/ai-hackathon-Coessentiality external/coessentiality
fi
git -C external/coessentiality checkout -q "$TOOL_COMMIT"
test -z "$(git -C external/coessentiality status --porcelain)" || { echo "tool checkout modified!"; exit 1; }
echo "tool at $(git -C external/coessentiality rev-parse HEAD)"
