# Template A: per-candidate report (`reports/<GENE>.md`)

Fill every `{{placeholder}}`. Rules (DESIGN §6.5, §9):
- Numbers are copied from `results/ledger/*.tsv` by script; do not retype them.
- Prose may only (a) paraphrase a ledger row or (b) cite a key that appears in the evidence ledger (§12) with verified = Y.
- Any gene-function sentence without a ledger row or an evidence-ledger key fails the lint.
- Write "not found in the literature as of {{search_date}}", never "novel".
- Write §9 (falsifying observations) before reading §7 (literature) and §6 (orthogonal evidence).

## Definitions used in this template

**Relationship type (DESIGN §4.4).** How the gene g relates to its predicted module M.

| Code | Type | Claim allowed |
|---|---|---|
| a | Stable subunit | Only with physical, co-abundance or structural support. |
| b | Assembly or maturation factor | "Required for assembly or maturation of M". |
| c | Supplier or client | Transporter, enzyme, or substrate of an import or insertion machinery that co-varies with M. |
| d | Pathway member | "Acts in pathway M". |
| e | Lineage or transcriptional programme | Regulatory co-dependency; not a function call. Assigned when g's dependency tracks its own expression, or partners are enriched for TFs or lineage markers. |

Without type-(a) support the claim reads "functions in / supports module M".

**Novelty class (DESIGN §1.5, §6.3).** Assigned by agent L, blind to our prediction, with the search date recorded.

| Class | Meaning |
|---|---|
| N1 | Function established in the literature (rediscovery; curation lag). Reported as validation, never dropped. |
| N2 | Partial or indirect evidence (function related or the complex known; prediction goes beyond it). |
| N3 | No functional literature found. Novelty claims are made only for N3, and for N2 where the prediction goes beyond what is known. |

---

## 1. Header
- Symbol: {{symbol}} | HGNC ID: {{hgnc_id}} | previous symbols / aliases: {{prev_aliases}} | UniProt: {{uniprot}} | band: {{band}}
- D1 / D2 / D3 values: {{d1}} / {{d2}} / {{d3}} | curation-lag audit flag: {{audit_flag}}
- Stratum (§1.4): family {{family}}; expression {{expressed_or_not}}; informativeness tertile {{sd_tertile}}; core {{core_yes_no}}
- Hypothesis (one sentence): {{gene}} {{functions in / supports / is an assembly factor of / supplies}} {{module_term}}.
- Relationship type: {{a|b|c|d|e}} ({{one-line justification}})
- Novelty class: {{N1|N2|N3}} (search date {{search_date}})
- LLM-recall-probe flag (§6.2): {{known / not known}}; probe answer logged at `{{probe_path}}`; matches network top term: {{yes/no}}
  (if "known", the prediction is not independent of background knowledge)
- Calibrated probability p_cal: {{p_cal}} [95% CI {{lo}}–{{hi}}]; calibration family: {{mitochondrial | large machinery (>30 subunits) | other}}; covariates inside H's 5th–95th percentile: {{yes/no}}
- Tier: {{A|B|filled by p_cal}}; rank in top 40: {{rank}}

## 2. The protein
- Domains (InterPro): {{domains}}; TM / signal peptide / MTS: {{features}}; AlphaFold pLDDT: {{plddt}}; deepest orthologue: {{orthologue}}
- Class H (homology) evidence: {{h_evidence}}
- Source keys: {{keys}} (all must appear in §12)

## 3. Dependency profile
- Mean / SD of Chronos effect: {{mean}} / {{sd}}; fraction of lines < −0.5: {{frac}}; common-essential or selective: {{status}}; NaN fraction: {{nan}}
- Expression across lines (log2(TPM+1) ≥ 1 in {{pct}}% of lines); dependency-vs-expression scatter: `{{fig_dep_vs_expr}}`
- Lineage enrichment: {{lineage}}
- Split-half assessability: R(g) = {{R}}; null 95th percentile = {{R0_95}}; assessable: {{yes/no}}
- Figure 1 (profile panel): `{{fig_profile}}`

## 4. Neighbourhood
- Top-10 partners table: partner | zavg_BEF | z_B / z_E / z_F | GLS rank | partner function and essentiality | chromosome and distance | paralogue or shared-guide flag | hu.MAP-train membership
- Figure 2 (neighbourhood network): `{{fig_network}}`
- Top 3 terms: term | S | p_emp | hypergeometric p (descriptive) | leave-one-partner-out stability
- Second-ranked term: {{term2}}

## 5. Robustness (pass / fail)

| Check | Result | Note |
|---|---|---|
| Same-arm and paralogue removal (built in) | {{pass/fail}} | |
| Bidirectional-promoter / overlapping / readthrough partners | {{pass/fail}} | |
| Copy-number co-amplification | {{pass/fail}} | |
| Hub-driven call (>50% of S from top-1% in-degree) | {{pass/fail}} | |
| Lineage leave-out | {{pass/fail}} | |
| K = 10 / 50 | {{pass/fail}} | |
| Dependency vs own expression; TF / lineage-marker enrichment | {{pass/fail}} | |
| TP53 / p53-axis correlation | {{pass/fail}} | |
| DEMETER2 replication | {{pass/fail}} | |
| Shared-sgRNA and per-guide check | not possible (guide maps / guide-level data not available) | recorded |

## 6. Orthogonal evidence matrix (four states: not measured / no support / supports / contradicts)

| Class | Dataset | State | Pair-level detail | Empirical p (Holm) | Diagnostic for this module family? |
|---|---|---|---|---|---|
| P physical | {{}} | {{}} | {{}} | {{}} | {{}} |
| A co-abundance | {{}} | {{}} | {{}} | {{}} | {{}} |
| L localisation | {{}} | {{}} | {{}} | {{}} | {{}} |
| G perturbation phenotype | {{}} | {{}} | {{}} | {{}} | {{}} |
| S structure | {{}} | {{}} | {{}} | {{}} | {{}} |
| H homology | {{}} | {{}} | {{}} | reported only | {{}} |

Reported but not counted: hu.MAP 3.0, DEMETER2, Predictomes. Absence of an interaction is never a contradiction.

## 7. Literature (blinded step, then synthesis)
- Blinded summary of agent L's evidence items, with evidence level (functional / high-throughput / mention) and DepMap-derived yes/no
- Blinded verdicts: real statement {{+1/0/−1}}; decoys {{+1/0/−1}}, {{}}, {{}}; judges {{J1}}, {{J2}}, adjudicator {{J3 or n/a}}
- Unblinded synthesis (every sentence carries an evidence-ledger key): {{text}}
- Closest prior publication and what co-essentiality adds beyond it: {{text}}
- Prior prediction lists containing this gene (Wainberg 2021, hu.MAP 3.0, Replogle 2022, Predictomes): {{yes/no, which}}
- Post-freeze (after 2026-10-29) papers confirming the prediction (counted separately): {{list}}

## 8. Alternative explanations
- For each artefact in §5: the evidence against it.
- Strongest competing biological hypothesis (for example supplier rather than subunit): {{text}}; experiment that separates it: {{ref to Template B}}

## 9. Falsifying observations (written before §6 and §7 were read)
1. {{observation}}
2. {{observation}}

## 10. Experiments
See `reports/{{GENE}}_experiments.md` (Template B).

## 11. Novelty and external benchmarks
Agreement with prior catalogues (Wainberg 2021, hu.MAP 3.0, Replogle 2022, Predictomes); what is new here: {{text}}.

## 12. Evidence ledger
Every claim in this report that is not a ledger row from `results/ledger/*.tsv` has a row here. Unverified rows must be deleted before submission.

| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| {{claim}} | {{results/ledger/....tsv row id | PMID | DOI}} | "{{verbatim span from abstract or full text}}" (text read: {{abstract | full text}}) | {{Y/N}} |

## 13. Red-team review
Written by a separate agent that argues the artefact explanation (hub, mitochondrial or ribosomal dominance, proximity, lineage, multifunctional partners, curation lag). Appended unedited.
- Reviewer / model / date: {{}}
- Review text: {{unedited}}
- Lint result (claims without a verified source): {{pass/fail, list}}
- PI response (separate, below the review): {{}}
