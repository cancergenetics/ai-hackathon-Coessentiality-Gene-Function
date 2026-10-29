# Round 2 review: biology, experiments, prior work (DESIGN v2.1)

## 1. Round-1 must-fixes

| Item | Status |
|---|---|
| Relationship types, V1′ | Adopted; no assignment rule for b/c/d (C1). |
| Reachability, negative control | Adopted; control purity and lineage-restricted genes unhandled (C2). |
| Artefact checks | Structure adopted; pass/fail thresholds unset (C3). Shared-sgRNA/per-guide recorded as not possible; acceptable. |
| Four-state, family rules | Adopted; family mapping, "other" family, MitoCarta, vocabulary gaps (C4). |
| Mito cap | Partial (C5). |
| Templates | Adopted; rigorous but not yet bench-ready (section 2). |
| Novelty policy | Adopted; report-selection rule missing (C6). |
| Circularity | Adopted; two gaps (C7). |
| PPI comparator | Adopted (§3.3); refinements (C8). |
| Temporal timing | Adopted-modified (PMID-dated targets as sensitivity; TEDC1/2 as caveated controls). Acceptable if both versions are reported side by side, primary rule unchanged. |
| LITERATURE E1–E6 | All applied correctly. |

Deferred items (2022–2026 prior-work sweep, shinyDepMap etc., experimental audit of earlier lists) do not block freeze. The sweep must be logged before the paper says no calibrated pre-registered predecessor exists.

## 2. Changes

**C1. Type assignment (§4.4).** Script-applied order: (e) if the expression/TF/lineage flag fires; (a) only with P/A/S support; (c) if g has transporter/enzyme domains, or ≥ 4 TM helices and no complex-like partners; (b) if not a stable subunit but in an assembly term or MitoCarta assembly pathway; else (d), "type unresolved". State in DESIGN and Template A §1 that p_cal covers the module term only, never the type, and tell judges (§6.4).

**C2. Negative control.**
- Clean negatives: log2(TPM+1) < 0.5 in ≥ 95% of lines. Report the false-call rate by informativeness tertile; non-expressed genes are mostly flat, so an unstratified rate flatters.
- Add "lineage-restricted expressed" (≥ 50% of lines in any lineage with ≥ 10 lines). It is assessable and typed (e) if flagged; the 10%-of-lines rule otherwise discards real tissue-specific dependencies.
- Record HPA tissue/testis-enriched and TM/secreted status as descriptive strata.

**C3. Fix §4.3 flag thresholds at freeze (CRITERIA.md).** Numeric pass/fail for CN co-amplification, g-effect vs own expression, TF/lineage enrichment (TF list and test), TP53 axis, hub and DEMETER2. Tier A depends on them, and §7 says all thresholds are fixed.

**C4. §5.**
- Freeze a term → module-family mapping file. Add an "other" family (metabolism, transport, peroxisome, chromatin, proteostasis, cell cycle). Tier A there requires ≥ 1 supporting class when any is measured.
- Add MitoCarta3.0 membership and sub-compartment to class L. It is currently only vocabulary, not evidence.
- Add peroxisome, lipid droplet and nuclear envelope to the compartment vocabulary. Define "multi-localised" (≥ 2 compartments in any admitted source).
- State how localisation sources pass §5.2; a co-complex odds ratio does not apply. Agreement with GO CC on held-out genes would.

**C5. Mito cap.** Keep ≤ ⅓ OXPHOS/mitoribosome in the top 20. Add: all mitochondrial-family calls ≤ ½ of the top 20 and ≤ 3 of the 8–10 reports (type-(c) suppliers co-vary with the ETC without being OXPHOS).

**C6. Report selection (§6.5).** Take the 8–10 from the top 40 in order, N2/N3 only, plus at most 2 N1 genes as labelled rediscovery case studies. Other N1 genes go in the rediscovery table with rate and CI.

**C7. Circularity (§3.2.3).** Add a citation flag (PMIDs citing Wainberg 2021, Kim 2019, Pan 2018 or 2022, via Europe PMC). Report the fraction of PMIDs with scannable full text: unscannable are unflagged in the primary analysis and excluded in a sensitivity run.

**C8. PPI comparator.** Add one line reporting the fraction of Tier A/B whose class P state is "no support" or "not measured"; coverage alone does not show a call rests on co-essentiality alone. Use BioPlex 2.0 (pre-t0) where obtainable; note post-t0 hu.MAP 3.0 favours the comparator (conservative).

## 3. Template fitness for an experimental biologist

**Template A.**
- Add a "Section 0" bench summary: the claim in plain words; confidence as expected hit probability; the strongest reason to doubt; the recommended first experiment with time and cost; the caveat that this is cancer-line essentiality, not necessarily organismal function.
- Add the C1 statement that p_cal covers the module only.
- Move ledger and red-team to an appendix.

**Template B.**
- **Essential-gene confound.** Readouts after KO of an essential gene are confounded by dying cells. Require acute or hypomorphic depletion (inducible CRISPR, CRISPRi, degron), time-matched to partner depletion, with a matched-essentiality control gene from an unrelated module. Otherwise "phenocopies partner" is not specific.
- **Common-essential genes** have no non-dependent control line. State the controls instead: rescue, non-targeting guides, control essential gene.
- **Medium.** Use the DepMap screen medium. OXPHOS dependency is medium-dependent, so galactose is a sensitised condition, not the baseline.
- **Type-specific rows**, since the tier table is subunit-centric:
  - (b) assembly intermediates by BN-PAGE and pulse-chase;
  - (c) uptake or metabolite measurement, and bypass or supplementation rescue;
  - (e) ChIP or reporter.
- **Readout menu.** Add an "other" row: an assay taken from a ledger-verified paper for the module's top term.
- **Guides.** Add a sequence-level off-target check of the guides against partner and neighbouring loci, replacing the unavailable per-guide DepMap check.
- **Decision rule.** "≥ 2 of the 3 Tier-1" is ambiguous (four rows), and the dropout row only confirms dependency. Rewrite: Supported = dropout rescued, and module-specific readout concordant, and localisation compatible, and Tier-2 physical or epistatic support. Refuted = unrescued dropout, or incompatible localisation (endogenous tag) in both dependent lines.

## 4. New problems

None beyond the above.

## Verdict

**READY AFTER MINOR CHANGES** (C1–C8 and the template edits in section 3).
