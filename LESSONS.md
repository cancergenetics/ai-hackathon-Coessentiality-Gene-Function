# LESSONS.md — process rules for running this project efficiently

One line per rule, with evidence. Pruned at each milestone (M3 pruning: reviews/retro_M3.md).

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
