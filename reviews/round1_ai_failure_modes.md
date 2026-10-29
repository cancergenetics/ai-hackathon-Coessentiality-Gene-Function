# Review round 1: AI-agent failure modes

Reviewer scope: how LLM agents running DESIGN.md v1 are likely to go wrong, and what to add. Read: PROMPT, DESIGN, LESSONS, RESEARCH_TREE, LITERATURE (skimmed), and the earlier project's LESSONS and REPORT. No DepMap data was touched.

## Assessment

DESIGN §9 lists the right headings but each is one line, and several are not yet mechanisms. The statistical core (fixed K, frozen predictor, matched-gene and prior-only nulls, temporal hold-out) is algorithmic, which is the best defence against agent storytelling. The weakest points are the following.

- **Knowledge leakage.** Everything after the algorithmic prediction (interpretation, literature judging, candidate reports) is done by LLMs that may already know the gene.
- **Gate integrity.** The pre-registration gate is enforced by the same agent that could edit it, and the tool's `results/predictions/` still sits in the working tree.
- **Blinding.** The judge step leaks through gene symbols, partner names, statement style, and unequal decoy plausibility.
- **Citations.** Citation checking covers existence, not whether the paper supports the claim.
- **Lessons not carried over.** The earlier project's hard-won lessons (power simulation before gates, one-look rule, verifiers that re-implement from raw files, macro and per-cluster reporting) are absent from DESIGN §9.

## Numbered changes

### A. Pre-registration and gate integrity

1. **MUST: Make the freeze tamper-evident and physically enforced.**
   - Before freeze, remove `external/coessentiality/results/predictions/` (sparse-checkout exclusion or `chmod 000`; restore only after the tag). Instructions to "not open" it are not a mechanism.
   - Create an annotated git tag `prereg-v1` and record the hash of `uncharacterised_genes.tsv` and `CRITERIA.md` in RESEARCH_TREE.md.
   - Add `scripts/audit_order.py`, run by a fresh agent at M4 and M9. It checks that no DepMap-derived artefact (matrix hash, `results/` outputs) has a commit or mtime earlier than the tag, and that the guard module (`prereg_guard.py`) is unchanged since the tag.
   - Why: the same agent writes both the gate and the code that checks it.

2. **MUST: Pre-specify what happens when a gate fails, and what happens when the lists come out the wrong size.**
   - Tier A needs calibrated P ≥ 0.5. If calibration never reaches that, the temptation will be to lower it. Fix the fallback now (for example, "Tier A empty; all predictions exploratory; the paper is a calibration and negative-result paper").
   - Do the same for the hold-out criterion (§3 primary success criterion), for |U| too large or small, and for "too few scorable U genes".
   - Fix the cap on the number of calibrated-P bins and the minimum n per bin.

3. **MUST: Run a power simulation before freezing the hold-out gate, and write a one-look rule.**
   - Sources are LESSONS 3 and 8 of the earlier project, where a CI gate had P(pass) ≤ 0.22.
   - Simulate with the real |H|, plausible precision@1 and the term-cluster correlation structure.
   - The hold-out and U predictions are each computed once, after code freeze. Code or bug fixes after a look are allowed only with a LOOKS.md entry (date, command, commit, reason), and both versions are reported.
   - Bootstrap over complexes or term-clusters, not only over genes. Genes in one complex are not independent (earlier project: effective n of about 8 clusters).

4. **SHOULD: Add `config/frozen.yaml` plus a pytest that fails on drift.**
   - It records SHA-256 of `metrics.py`, `predictor.py`, the term filters and the thresholds (K, 5–300, 95th percentile, tier cuts).
   - Every results JSON embeds the code commit and the frozen-config hash. Any edit goes through DEVIATIONS.md with both results reported. This blocks metric drift mechanically.

### B. Knowledge leakage and story-telling

5. **MUST: Machine-generated prediction ledger before any narrative.**
   - A script writes `results/predictions/U_predictions.tsv` (top term, S, p, calibrated P, top-10 partners, flags, tier), hashed and committed.
   - Candidate reports are generated from a fixed template that quotes this ledger. LLM prose may only (a) paraphrase table rows or (b) cite a verified source (see 10).
   - Any sentence of the form "gene X is known/likely to…" without a ledger row or a source key fails the lint.

6. **MUST: Closed-book recall probe.**
   - Before any agent sees network output for a gene, a fresh tool-less agent gets only the HGNC symbol, ID and prior symbols. It writes its recalled function and a 0–3 confidence into `results/probe/<gene>.json` (timestamped).
   - It is run for the 50-gene audit sample and all Tier A/B genes.
   - Report the fraction where the recalled function matches the network top term. Mark such genes "LLM-recognisable": the match is not independent evidence, and it may signal curation lag.
   - Also use the probe to check how "uncharacterised" U really is to the model.

7. **MUST: Fixed-schema evidence table and adversarial review for every candidate report.**
   - The table has fixed columns: the top term, the second-ranked term, supporting edges, hub and degree status, same-arm and paralog flags, lineage dependence, and each orthogonal class (pass, fail, not covered).
   - Require a "what would falsify this" paragraph written before the orthogonal and literature sections are read.
   - A separate red-team agent argues the artefact explanation (hub, mitochondrial or ribosomal dominance, proximity, lineage, multifunctional partners). Its output is appended unedited.

8. **SHOULD: Remove the cherry-picking route.**
   - "Top 20 go to deep-dives" must be fixed by rule (tier, then calibrated P, seeded tie-breaks) before any literature look.
   - Never recompute pipeline precision from the literature-supported subset. Publish the full U prediction table, including non-supported and contradicted cases, with denominators.
   - The named positive-control list (§3.2) is selected from success stories. Label it illustrative, not evidence of accuracy. The primary metric is algorithmic H.

### C. Literature step: hallucination and blinding

9. **MUST: Script-resolved identifiers.**
   - Build `results/identifiers/U_ids.tsv` from HGNC: HGNC ID, current symbol, previous symbols, aliases, Entrez ID, UniProt, Ensembl.
   - Search uses IDs via gene2pubmed and symbols. Flag any alias that is a common word or collides with another approved symbol or alias, and require a manual disambiguation note.
   - Without this, renamed or ambiguous symbols will produce wrong-gene literature in both directions.

10. **MUST: Claim-level citation verification, not just existence checks.**
    - Agents cite only keys from `references.bib`, generated by script from PubMed or Crossref records (PMID or DOI to metadata). Agents never type references by hand.
    - A verifier agent receives each (claim, key) pair plus the fetched abstract or full text and returns a verbatim supporting span or "unsupported". Unsupported claims are deleted.
    - Lint the manuscript: every `\cite` resolves, and every gene-function sentence has a key.
    - Record which text (abstract or full text) was actually read, because many papers on obscure genes are paywalled.

11. **MUST: Harden the blinded judging protocol.**
    - L writes a structured evidence list (verbatim quote, PMID, year, evidence type: functional, high-throughput, or mention), not free narrative. Items without a fetched source are dropped.
    - Redaction: a script replaces all of the gene's symbols, aliases and previous names in L's items with "GENE", and the judge has no tools.
    - Statements are generated by script from the term label and definition in one template (same length and tense). They contain no partner names and are never written by an LLM, so there is no style leak.
    - Use at least 3 decoys per real prediction, assigned with seeded random positions. Match the decoy on compartment and on term size and information content. Exclude decoys whose term gene-set overlaps the real term or contains the gene's own top partners, since such a decoy could be true.
    - Pre-specify the test (paired exact or permutation over decoys) and state that n ≈ 20 gives low power, so the result is descriptive.
    - Exclude co-essentiality-derived papers (blacklist) from L's evidence items.

12. **MUST: Validate the blinded pipeline on known answers before the real run.**
    - Take about 6 characterised genes outside U with well-established functions, plus decoys. L and J must score the true statement "supported" and decoys "not supported".
    - The pipeline is accepted only if the decoy false-support rate is at most 1/6 and the true-support rate at least 4/6 (fix the cut-offs now).
    - Use two judges, different models where possible (Opus and Sonnet), and report agreement (kappa).
    - Run L in a directory containing only the ID file, with no `results/`.

### D. Silent data bugs

13. **MUST: ID-mapping contract and tests.**
    - DepMap columns are "SYMBOL (Entrez)". Map by Entrez ID, then HGNC ID, never by symbol string.
    - Report loss counts per dataset (GO, UniProt, hu.MAP, Complex Portal, BioPlex, orthogonal sets).
    - Add a toy test with known renames (for example C12orf49 to SPRING1 and several others), many-to-many UniProt-to-gene cases, and a check that U genes absent from DepMap are labelled "not scorable" and not dropped.
    - Hash the gene and model ordering of every matrix and assert equality across the matrices that are compared.

14. **MUST: Sign and orientation assertions on real data, using characterised genes only.**
    - Chronos: more negative means more dependent. Assert that mean effect is below −1 for ribosomal and proteasome genes and about 0 for olfactory receptors.
    - Assert that matrix orientation is models × genes and that rows are aligned to `Model.csv` before any lineage use.
    - After PC removal and whitening, assert top partners of RPL genes are ribosomal, and that the self-pair is excluded from top-K.
    - Also include a label-shuffle negative control (permute cell-line rows, so AP falls to chance), a tie-handling check, and a K off-by-one unit test with a known answer.

15. **SHOULD: Single metrics module and numbers by script.**
    - All AUPRC, precision@k and enrichment code lives in one tested `metrics.py` with known-answer toy cases (hand-computed hypergeometric values).
    - Manuscript numbers are inserted from `results/report/tables.md` tokens. A lint fails if the manuscript has an untokenised number from the results.

### E. Sub-agent verification, context, cost

16. **MUST: Claims ledger and independent re-derivation.**
    - Maintain `CLAIMS.tsv` with columns: claim, value, source file and hash, producer, verifier, status. The PI accepts numbers only when the status is verified.
    - Verifiers get the spec and raw inputs, never the producer's code (earlier LESSONS 6), and sweep neighbouring configs (K = 10, 25, 50).
    - Every agent returns artefact paths and SHA-256s, not just prose. Re-derive at least: the hold-out set H and its size, the prior-only baseline, the hold-out precision@1 CI, and the Tier A list.
    - Reviewers and verifiers receive "compute no label metrics" instructions (earlier LESSONS 1).

17. **SHOULD: Task sizing and a duplicate-work guard.**
    - Each agent task has one deliverable, a time or tool-call cap (for example, 40 searches per literature dive), and a checkpoint line written to RESEARCH_TREE.md.
    - Add a Makefile or DAG, with `scripts/INDEX.tsv` (script, inputs, outputs). Agents consult it before writing a new script.
    - Deep-dives run as 20 independent, template-bound tasks in parallel, not one long chain.
    - Use Sonnet for mechanical steps and Opus for judging and red-teaming, with a token budget per milestone logged in the tree.

18. **SHOULD: Adopt the earlier project's rules in DESIGN §9 explicitly.**
    - Report macro per-term or per-complex precision, and results without the ten largest terms and complexes (ribosome, proteasome, respiratory chain) next to every headline (earlier LESSONS 5).
    - Pilot any added model on one fold, with a stop if |Δ| < 0.005 (earlier LESSONS 7). Set PYTHONHASHSEED and commit canonical split files (earlier LESSONS 2).
    - Update the tree in the same commit as each result (earlier LESSONS 9).

19. **COULD: Scope-creep lint.**
    - A script scans the manuscript and reports for gene symbols that are not in U, and fails where a function is asserted for a non-U gene, to uphold "no function is proposed outside U". Partners and cited known genes are allowlisted.

20. **COULD: Retrospective prompt.**
    - At each milestone, a fresh agent is asked what to stop doing and what worked well (PROMPT requirement), and it must also name any step where an agent's output was relied on without verification.
