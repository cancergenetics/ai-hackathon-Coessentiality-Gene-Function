# external/ (placeholder — not distributed)

Everything here is git-ignored except this file.

## `external/coessentiality/` — the co-essentiality tool (used read-only, never modified)

`scripts/00_get_tool.sh` clones <https://github.com/cancergenetics/ai-hackathon-Coessentiality> and checks out commit
`3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf`. Until the pre-registration tag existed, the tool's precomputed genome-wide
predictions (`results/predictions/`) were hidden by sparse checkout (`scripts/verify_sparse.sh`). The tool's `mvp/`
package is installed in editable mode into the project environment (see `README.md`, environment setup).
