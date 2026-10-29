# Retrospective M0–M3 (fresh-process reviewer)

## 1. What should we stop doing?

1. **Monolithic freeze commit.** `afed1dd` bundles 65 files and 116k added lines: list, DESIGN v2.3, 11 src modules, 99 tests, hold-out tables and verification. LESSONS 4 asked for narrow commits, yet the tag points at a commit nobody can review as "the freeze". Tag a small commit; commit pipeline code separately.
2. **Committing bulky duplicate derived tables.** `verify/rederived_U.tsv` (19k lines), `rederived_H_targets.tsv`, `circularity_annotations.tsv` (same keys as `H_targets.tsv`), `hgnc_hub.tsv` (45k lines). Store script, hash and diff summary instead.
3. **Two implementations of one definition.** `scripts/02_gene_knownness_table.py` and `src/knownness.py::d1()` diverged (HTP/TAS handling), (round2_ai §2.2), and the re-derivation found a 7- vs 22-term generic-binding list mismatch (PROVENANCE step 4).
4. **Late-stage tree maintenance.** RESEARCH_TREE was stale mid-M2 ("~2.1–2.6k", "v1 in round 1") against DESIGN's 5.2k (round2_ai §2.3).
5. **Full-DESIGN re-review plus 30 KB disposition tables.** `round1_disposition.md` (30 KB) and `round2_disposition.md` (31 KB) are about 3x any single review. Round 2 reviews were half the length (about 6 KB vs about 12 KB) and all said "minor". Give round 2 a diff plus item IDs; track adoption in a ledger.
6. **Governance scaffolding ahead of use.** `agent_scopes.yaml` (153 lines), the empty `DEVIATIONS.md`, `LOOKS.md` with a PENDING row, and `CLAIMS.tsv` all exist before any result. Verify in M4 that each is actually consumed; add no more.
7. **Setting the last spec edits at the freeze.** DESIGN v2.3 (206 changed lines) was never reviewed on its own; it went in with the code. Review the last spec edit before tagging.
8. **Lessons that are not lessons.** LESSONS 2 (zsh `=`) and 3 (hygiene duplicates D0) are noise.

## 2. What worked well

- **Role-specific parallel reviewers.** Round 1 (`3e6b162`) found non-overlapping must-fixes: assessability null, calibration shift, circularity, templates. Review rounds took about 12 and about 8 minutes (commits 20:06 → 20:18 → 20:31). Stopping at 2 of the 3 allowed rounds, once all reviewers said "minor", was right.
- **Disposition check on the text, not the revision log.** It found 7 (round 1) and 32 (round 2) real gaps, including frozen-rule changes (O1–O4).
- **Independent re-derivation** (`verify/prereg_verification.md`) reproduced U (4,924) and H (820/5,965) exactly, and exposed a definition discrepancy.
- **Honest provenance.** PROVENANCE.md logs every look at |U|, the pre-freeze DepMap reads (single-gene marginals only), and the chronology. The mechanisms are real: `gate.py`, `verify_sparse.sh`, `audit_order.py`.
- **Annotation-only work parallel to review** (M1 knownness table, hold-out sizing, power sim, toy tests), so the freeze cost minutes after round 2.

## 3. Proposed pruned LESSONS.md (10 rules)

1. Look on the user's machine for provided data before public portals; match checksums to the tool's DATA.md. (M0: 26Q3 found, hours saved)
2. Make "blind" and "no-look" rules mechanisms with a log: sparse checkout, `gate.check()`, an allow-listed reader, LOOKS/PROVENANCE. (round2_ai §1; `verify_sparse.sh`)
3. Commit with explicit paths, one logical change per commit; keep the tagged freeze commit small. (v2.1 swept in WIP; `afed1dd` 65 files)
4. Use 5–6 role-specific parallel reviewers, at most 2 rounds, stop when all say "minor". (`3e6b162`, `ba26d17`)
5. Run an item-by-item disposition by a cheap agent against the document text, never the revision log. (7 and 32 gaps found)
6. Keep one implementation per frozen definition, and have an independent agent re-derive it from raw files. (`knownness.py` vs script 02; 7 vs 22 terms)
7. Do annotation-only builds in parallel with design review; only DepMap pairwise steps wait for the freeze. (M2: freeze right after round 2)
8. Update RESEARCH_TREE at every DESIGN version; a stale tree misleads reviewers. (round2_ai §2.3)
9. Commit scripts, hashes and summaries, not duplicate derived tables. (`afed1dd`: 116k lines)
10. Give later review rounds a diff and ID'd items, not the whole document. (round-2 reviews were short, disposition 31 KB)
