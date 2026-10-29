#!/usr/bin/env bash
# verify_sparse.sh -- DESIGN.md v2.2 §1.6/§9: until git tag preregistration-v1 exists, the tool clone's
# results/predictions/ must stay hidden (sparse checkout). Also asserts the tool clone is pristine and pinned.
#
# Exit 0 only if ALL hold:
#   1. NOT (external/coessentiality/results/predictions exists in the working tree AND tag preregistration-v1 is absent)
#   2. `git status --porcelain` in the tool clone is empty (no modifications, no untracked files)
#   3. tool clone HEAD == 3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf
# Overrides (for tests): REPO_ROOT, TOOL_DIR, TOOL_COMMIT, TAG.
# Run: bash scripts/verify_sparse.sh
set -u
REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TOOL_DIR="${TOOL_DIR:-$REPO_ROOT/external/coessentiality}"
TOOL_COMMIT="${TOOL_COMMIT:-3c684c972f1e5c3ead722b4b3e2c508fa3cb5ddf}"
TAG="${TAG:-preregistration-v1}"
fail=0
say() { echo "verify_sparse: $*"; }

# 1. predictions hidden until the tag exists
if git -C "$REPO_ROOT" rev-parse --verify --quiet "refs/tags/${TAG}^{commit}" >/dev/null 2>&1; then
  have_tag=1; say "tag ${TAG} exists"
else
  have_tag=0; say "tag ${TAG} does not exist"
fi
if [ -e "$TOOL_DIR/results/predictions" ]; then
  if [ "$have_tag" -eq 0 ]; then
    say "FAIL: $TOOL_DIR/results/predictions exists in the working tree before tag ${TAG}"; fail=1
  else
    say "note: results/predictions present, allowed because tag ${TAG} exists"
  fi
else
  say "OK: results/predictions not in working tree"
fi

# 2./3. tool clone pristine and pinned
if ! git -C "$TOOL_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  say "FAIL: $TOOL_DIR is not a git clone"; fail=1
else
  st="$(git -C "$TOOL_DIR" status --porcelain 2>&1)"
  if [ -n "$st" ]; then
    say "FAIL: tool clone has modifications:"; echo "$st" | head -20; fail=1
  else
    say "OK: tool clone clean (git status --porcelain empty)"
  fi
  head="$(git -C "$TOOL_DIR" rev-parse HEAD 2>/dev/null)"
  if [ "$head" != "$TOOL_COMMIT" ]; then
    say "FAIL: tool clone HEAD ${head:-<none>} != $TOOL_COMMIT"; fail=1
  else
    say "OK: tool clone HEAD == $TOOL_COMMIT"
  fi
fi
[ "$fail" -eq 0 ] && say "PASS" || say "FAILED"
exit "$fail"
