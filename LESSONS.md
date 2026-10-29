# LESSONS.md — process rules for running this project efficiently

One line per rule, with evidence. Pruned at each milestone.

1. Check the user's machine for already-provided data before trying public portals: DepMap portal is behind bot verification and figshare stops at 24Q4, but the exact 26Q3 files (checksums matching the tool's DATA.md) were in sibling project folders. (M0, saved ~hours / avoided using a different release than the tool was tuned on.)
2. In zsh, `echo ====` fails (`=` expansion); use `echo '----'` as separators in shell commands. (M0, one wasted call.)
3. Never open the tool's precomputed `results/predictions/` before the gene list is pre-registered — it is network output. (M0, pre-registration hygiene.)
4. While agents are writing, commit with explicit paths, never `git add -A`: the v2.1 commit swept in other agents' work-in-progress files. (M2)
5. Six parallel role-specific reviewers in round 1 found largely non-overlapping must-fixes (assessability null, calibration shift, term-size bias, circularity, templates) in ~5–7 min each — cheap relative to the errors prevented. (M2)
6. Have a cheap editor agent produce an item-by-item disposition table; it surfaced 7 must-fix items the PI's revision had silently missed. (M2)
7. Build annotation-only artefacts (gene list, hold-out sizing, circularity flags, toy-tested pipeline) in parallel with design review; only the DepMap pairwise step must wait for the freeze. (M2)
