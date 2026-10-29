# LESSONS.md — process rules for running this project efficiently

One line per rule, with evidence. Pruned at each milestone.

1. Check the user's machine for already-provided data before trying public portals: DepMap portal is behind bot verification and figshare stops at 24Q4, but the exact 26Q3 files (checksums matching the tool's DATA.md) were in sibling project folders. (M0, saved ~hours / avoided using a different release than the tool was tuned on.)
2. In zsh, `echo ====` fails (`=` expansion); use `echo '----'` as separators in shell commands. (M0, one wasted call.)
3. Never open the tool's precomputed `results/predictions/` before the gene list is pre-registered — it is network output. (M0, pre-registration hygiene.)
