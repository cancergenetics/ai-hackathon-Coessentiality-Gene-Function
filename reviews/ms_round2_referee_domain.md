# Referee 1, round 2 (functional genomics / CRISPR screens / protein complexes)

**Recommendation: minor revision**

## Round-1 MUST items

- **M1 (the definition confounds curation lag):** largely addressed, but the new text overclaims (N1 below). The C1 paragraph, S4A Fig, Table 2 flags, the new title and the Discussion heading are what I asked for.
- **M2 (generic co-essentiality; hu.MAP leakage):** addressed. Having no DOI for a third-party tool is acceptable, given the Methods description.
- **M3 (calibration):** addressed well. Events per parameter, Brier skill, separation and S4D Fig are all reported, and the wording is now modest.
- **M4 (novelty against catalogues):** addressed. S9 Table, S4B Fig, the report bullets and the Wainberg Supp. Data 3 finding are convincing, and the counts are labelled as lower bounds.
- **M9 text items:** addressed. **Authorship:** still placeholders.

Declined SHOULD items are acceptable as limitations, except the DepMap-only candidate controls, which touch no hold-out data.

## New problems

**N1. The curation-lag decomposition now over-attributes to complex membership.** I checked `results/revision/a1_U_entry_flags.tsv` and `a1_N1_rates_by_route_and_flag.tsv`.
- In the random 50, none of the genes is a Complex Portal subunit, and none of the 21 N1 genes has an experimental GO complex term. The N1 genes include GNG8, SEPTIN1 and B3GAT2.
- The broad flag is driven by UniProt score 5 and by *any* experimental CC term, including localisation-only annotations. With the flag restricted to complex terms, the contrast is 10/18 vs 11/32 (p = 0.23).
- 13 of the 21 N1 genes rest on evidence from 2021 or later (lag in the usual sense). At most 8 are "invisible to the definition".

Yet three passages attribute the lag to the definition or to complexes:
- Results C1: "Much of what we call curation lag is therefore a gap created by the pre-registered definition … often for complex membership".
- Discussion: "Much of this is not slow curation".
- Author summary: "members of large complexes".

Complex membership dominates only among the *selected* candidates (13/40 and 17/20 Complex Portal subunits).

**N2. Residual overstatement.**
- The C2 heading still says "beats both nulls", although the prior-only arm is conceded to be degenerate.
- The Author summary says one gene in four "has been little studied", which the audit contradicts (42% N1; 2,248 genes with UniProt score ≥ 4).
- "Five independent hypotheses": four of the five were already proposed or linked by Wainberg et al.

**N3. DEMETER2 inconsistency.** Results and Limitations say a DEMETER2 flag "should not be read as evidence against a prediction". Table 3 nevertheless lists DEMETER2 as a *main caveat* for RBM34, TM2D2 and C5orf34.

**N4. Revision narration in Results** (e.g. "our first draft read it unconditionally"). The [post-review exploratory] label is enough; the history belongs in Methods.

## Assessment

The paper is now an accurate and useful evaluation standard (low accuracy, no tool effect, little gain over homology, fragile calibration, mostly anticipated rediscovery). What remains is wording and length.

## Length

Results run to about 8.9k words, with a 37-row Table 2. I propose cutting them to about 5.5k words:

1. **Tool reproduction:** reduce to two sentences and move the rest to S1 Text (about −250 words).
2. **C1:** reduce Strata to one sentence plus Fig 1C, and move the RBO sensitivity to S Text (about −250).
3. **C2:** robustness becomes one sentence plus an S Table. Calibration becomes about 250 words, with separation, the bootstrap and the simpler models moved to S Text and S4D Fig. Named controls become about 150 words (about −900 in all).
4. **C3:** move "Other sensitivities", clean-negative false calls, artefact flags, the orthogonal-support detail and the top-40 checks (DEMETER2, clean-first list) to S Text, each with a one-sentence summary (about −900).
5. **C4:** cut the recall probe to two sentences, merge judge validation with agreement, move the module-crediting mechanics to Methods, and move Table 2 to an S Table (about −600).
6. **Candidate reports:** about 700 words, covering the rediscoveries in brief plus PLEKHH3 and C5orf34. Table 3, S10 Table and S Reports carry the rest (about −800).
7. **Discussion:** halve the AI-safeguards section, and merge "Circularity" into "Context, direction and vocabulary".

## Required changes (no hold-out looks needed)

### MUST

1. **Results C1:** replace "Much of what we call curation lag … often for complex membership" with:

   "In the random sample, 13 of 21 N1 genes rest on evidence from 2021 or later (curation lag in the usual sense). The other 8 rest on older evidence; 6 of these are flagged, mostly by UniProt score 5. None is a Complex Portal subunit. Literature-route genes were N1 more often (19/34 vs 2/16). Among selected candidates, definition artefacts dominate (30/40 and 20/20 flagged; 13 and 17 Complex Portal subunits)."

   Also report the complex-restricted flag (165 U genes; 10/18 vs 11/32), and state that the broad flag counts localisation-only CC annotations.
2. **The same correction elsewhere:**
   - Discussion: "Much of this is not slow curation" becomes "Part of this, and most of it among top candidates, is".
   - Author summary and Abstract conclusion: "misses complex subunits" becomes "misses genes studied mainly in multi-gene papers, including, among our top candidates, many complex subunits".
3. **C2 heading:** change to "co-essentiality beats a matched-gene null on a temporal hold-out, with low absolute accuracy".
4. **Author summary:** change "has been little studied" to "was classed as little studied by our literature criterion; many such genes in fact have published functions".
5. **Placeholders:** complete the authorship, corresponding-author, oversight, CRediT, funding and deposit-DOI placeholders.

### SHOULD

1. Cut the Results as proposed, moving Table 2 to Supporting Information.
2. Change the candidate heading to "… and five hypotheses, four of them previously proposed".
3. Run the DepMap-only checks: PLEKHH3 lineage-adjusted partial correlations with PTEN-null lines excluded, and the coherence of the C5orf34 centriole module in the TP53-wild-type lines. If they are not run, the Abstract should call PLEKHH3 "a low-amplitude co-advantage signal not yet controlled for lineage", and the TP53 condition should not be called "what is new".
4. Remove DEMETER2 from the Table 3 caveats, or mark it "(unvalidated check)".
5. Move the revision narration to Methods.
