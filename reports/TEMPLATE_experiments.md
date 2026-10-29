# Template B: experiment plan (`reports/<GENE>_experiments.md`)

Rules (DESIGN §6.5): one decisive, falsifiable experiment per candidate; expected readouts stated for both "right" and "wrong"; cell lines chosen by rule, not by convenience. Relationship types (a–e) and novelty classes (N1/N2/N3) are defined in `reports/TEMPLATE_candidate.md`.

## 1. Context
- Gene: {{symbol}} | hypothesis: {{one sentence}} | relationship type: {{a|b|c|d|e}} | novelty class: {{N1|N2|N3}}
- LLM-recall-probe flag: {{known / not known}} | calibrated probability: {{p_cal}} (calibration family {{family}}) | tier: {{A|B}}
- Strongest alternative explanation: {{text}}
- Decisive experiment (one sentence): {{text}}
- Falsifying observation (copied from Template A §9): {{text}}

## 2. Cell lines (selection rule)
- Two dependent lines: Chronos ≤ −0.5 for g and ≤ −0.3 for the top partner; g expressed (log2(TPM+1) ≥ 2); g's locus not amplified; high screen quality; preferably TP53-null.
  Chosen: {{ModelID, name, g effect, partner effect, expression, CN, TP53 status}} ×2
- One control line that expresses g but does not depend on it, same lineage where possible: {{ModelID, name, g effect, expression}}
- Common-essential genes: RPE1-hTERT TP53⁻/⁻ or HEK293T, with a degron or CRISPRi: {{yes/no}}

## 3. Reagents
- 3 sgRNAs: {{sequences}}; 2 non-targeting guides; AAVS1 cutting control. Per-guide DepMap effects are not available locally; guides are chosen from published libraries and checked for concordance in the experiment itself.
- CRISPRi guides if the locus is amplified: {{yes/no}}
- Guide-resistant cDNA (ORFeome): {{clone}}
- Validated antibody, or endogenous HaloTag/mNG knock-in: {{}}
- Antibodies for partners and organelle markers: {{}}

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of g with the top 3 partners (ipTM/pDockQ) | days | Confident, conserved interface | No interface (does not exclude types b–e) | {{}} | {{}} |
| 1 | Competitive growth (GFP mix), 3 guides plus rescue, dependent vs control lines | 2–3 wk | Dropout only in dependent lines; rescued | No dropout, or no rescue (off-target or proximity) | {{}} | {{}} |
| 1 | Localisation with markers | 2–4 wk | Module's compartment | Incompatible compartment | {{}} | {{}} |
| 1 | Module-specific readout after KO | 2–4 wk | Phenocopies partner KO | Normal | {{}} | {{}} |
| 1 | Partner protein levels after g KO (and the reverse) | 2 wk | Co-destabilisation (types a/b) | Stable (favours c/d) | {{}} | {{}} |
| 2 | IP-MS / TurboID of tagged g vs unrelated tagged control | 1–2 mo | Partners enriched (SAINT) | Absent, or another module appears | {{}} | {{}} |
| 2 | BN-PAGE / SEC co-migration | 1 mo | Co-migrates; KO stalls assembly | Separate | {{}} | {{}} |
| 2 | Double KO with partner (epistasis) | 1–2 mo | No extra defect | Additive or synergistic (parallel pathways) | {{}} | {{}} |
| 2 | Arrayed CRISPRi Perturb-seq with partners | 2 mo | Signatures cluster | Distinct | {{}} | {{}} |
| 3 | Interface mutants fail to rescue; reconstitution, activity or structure | 6–12 mo | Interface or activity required | Mutants rescue | {{}} | {{}} |

## 5. Module readouts (pick the row matching the module)

| Module | Readouts |
|---|---|
| OXPHOS | OCR, galactose growth, BN-PAGE |
| Mitoribosome | ³⁵S mitochondrial translation |
| Ribosome biogenesis | Polysomes, pre-rRNA northern |
| Integrator / splicing | snRNA readthrough, reporter RT-PCR |
| DNA repair | Olaparib, MMC and cisplatin sensitivity; RAD51/γH2AX foci |
| SREBP | Cleavage western, LDL uptake |
| Endocytosis | Transferrin uptake |
| Centrosome | Centriole counts |

Chosen readout: {{}}

## 6. Experiment that separates the alternative explanation
- Alternative: {{text}} | experiment: {{text}} | readout if prediction right: {{}} | readout if alternative right: {{}}

## 7. Decision rule (fixed in advance)
- **Supported:** ≥ 2 of the 3 Tier-1 experiments are concordant, and there is physical or epistatic support at Tier 2.
- **Refuted:** a dropout that is not rescued, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else. Report it as such and propose an alternative relationship type.

## 8. Evidence ledger
| Claim | Source file or PMID/DOI | Verbatim span | Verified (Y/N) |
|---|---|---|---|
| {{claim, e.g. assay validated for this module}} | {{PMID | DOI | ledger row}} | "{{verbatim span}}" | {{Y/N}} |

## 9. Red-team review
Separate agent; asks what would make the experiment uninformative (off-target guides, proximity effects, lineage dependence, rescue failure, assay insensitivity). Appended unedited.
- Reviewer / model / date: {{}}
- Review text: {{unedited}}
- PI response (separate): {{}}
