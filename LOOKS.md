# LOOKS.md -- one-look rule for the temporal hold-out H (DESIGN.md v2.2 §3.1, §9)

**Rule.** The hold-out outcomes (hit@1 and every metric computed against T(g)) are looked at **once** for the primary
analysis. Before H is opened, the following must already be committed and logged here: (1) the **ranker choice** (R1/R2/R3,
decided on the LOO benchmark by MRR with the tie rule of §3.1), and (2) the **calibration specification** (§3.7 model, signs,
percentile covariates, support rule). Any further look at H (debugging, a re-run, a secondary analysis, a changed
specification) is a new row, with the reason and what was changed; results from a look that follows a specification change
are reported under both the frozen and the changed rule (DESIGN revision-log rule). Looks that only touch H's *inputs*
(membership, targets, sizing; annotation data, no network outputs) are not outcome looks but are logged if they follow the tag.
Append rows; never edit or delete earlier rows. An agent appends a row **before** it runs the code that opens H and the PI fills
the commit column when committing.

| date | what was looked at | by whom | commit | preceding logged specification |
|---|---|---|---|---|
| PENDING | ranker choice (LOO) + calibration spec — must be logged before opening H | PI / infra agent | — | — (none yet; this row is the specification entry) |
