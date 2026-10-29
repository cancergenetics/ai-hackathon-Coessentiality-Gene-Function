# Template B: experiment plan (`reports/<GENE>_experiments.md`)

Rules (DESIGN §6.5): one decisive, falsifiable experiment per candidate; expected readouts stated for both "right" and "wrong"; cell lines chosen by rule, not by convenience; essential-gene confound control, DepMap screen medium as baseline, and a sequence-level guide off-target check are required. Relationship types (a–e) and novelty classes (N1/N2/N3) are defined in `reports/TEMPLATE_candidate.md`.

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
- Common-essential genes: RPE1-hTERT TP53⁻/⁻ or HEK293T, with a degron or CRISPRi: {{yes/no}}. Controls for common-essential genes: guide-resistant cDNA rescue, non-targeting guides and a control essential gene (matched essentiality, unrelated module): {{rescue / non-targeting / control essential gene}}
- Baseline medium: the DepMap screen medium of the chosen lines ({{medium}}). Galactose (or any other changed carbon source) is a sensitised condition, not the baseline; if used, it is a separate arm.
- Essential-gene confound control (required, see Tier 1): acute or hypomorphic depletion (degron or CRISPRi titration) time-matched to partner depletion, with a matched-essentiality control gene from an unrelated module: {{control gene, its Chronos effect, its module}}

## 3. Reagents
- 3 sgRNAs: {{sequences}}; 2 non-targeting guides; AAVS1 cutting control. Per-guide DepMap effects are not available locally; guides are chosen from published libraries and checked for concordance in the experiment itself.
- Sequence-level off-target check of every guide (genome-wide mismatch search; no perfect or 1-mismatch site in another gene or in the partner's locus; result and tool: {{}})
- CRISPRi guides if the locus is amplified: {{yes/no}}
- Guide-resistant cDNA (ORFeome): {{clone}}
- Validated antibody, or endogenous HaloTag/mNG knock-in: {{}}
- Antibodies for partners and organelle markers: {{}}

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of g with the top 3 partners (ipTM/pDockQ) | days | Confident, conserved interface | No interface (does not exclude types b–e) | {{}} | {{}} |
| 1 | Competitive growth (GFP mix), 3 guides plus rescue, dependent vs control lines | 2–3 wk | Dropout only in dependent lines; rescued | No dropout, or no rescue (off-target or proximity) | {{}} | {{}} |
| 1 | Essential-gene confound control: acute or hypomorphic depletion of g time-matched to partner depletion, vs a matched-essentiality control gene from an unrelated module | 2–4 wk | Module readout changes beyond the control gene's at matched growth effect | Same change as the control gene (general sickness, not module function) | {{}} | {{}} |
| 1 | Localisation with markers | 2–4 wk | Module's compartment | Incompatible compartment | {{}} | {{}} |
| 1 | Module-specific readout after KO | 2–4 wk | Phenocopies partner KO | Normal | {{}} | {{}} |
| 1 | Partner protein levels after g KO (and the reverse) | 2 wk | Co-destabilisation (types a/b) | Stable (favours c/d) | {{}} | {{}} |
| 2 | IP-MS / TurboID of tagged g vs unrelated tagged control | 1–2 mo | Partners enriched (SAINT) | Absent, or another module appears | {{}} | {{}} |
| 2 | BN-PAGE / SEC co-migration | 1 mo | Co-migrates; KO stalls assembly | Separate | {{}} | {{}} |
| 2 | Double KO with partner (epistasis) | 1–2 mo | No extra defect | Additive or synergistic (parallel pathways) | {{}} | {{}} |
| 2 | Arrayed CRISPRi Perturb-seq with partners | 2 mo | Signatures cluster | Distinct | {{}} | {{}} |
| 3 | Interface mutants fail to rescue; reconstitution, activity or structure | 6–12 mo | Interface or activity required | Mutants rescue | {{}} | {{}} |

Type-specific rows (add the row for the relationship type; delete the others):

| Type | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| b | BN-PAGE of the module's complex and pulse-chase of its subunits after g KO | 1–2 mo | Intermediates accumulate; subunit turnover or assembly kinetics altered | Complex assembles normally | {{}} | {{}} |
| c | Uptake or metabolite assay (labelled substrate or targeted metabolomics) and bypass rescue (supplement the product or bypass the step) | 1–2 mo | Substrate/metabolite defect rescued by bypass | No defect, or no rescue | {{}} | {{}} |
| e | ChIP (or CUT&RUN) and reporter assay at the partner/programme targets | 1–2 mo | g occupies the targets; reporter depends on g | No occupancy; reporter unchanged | {{}} | {{}} |

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
| Other (module not listed) | {{readout}}; source: {{ledger-verified paper (PMID/DOI, Evidence ledger row id) showing the assay reports on this module}} |

Chosen readout: {{}}

## 6. Experiment that separates the alternative explanation
- Alternative: {{text}} | experiment: {{text}} | readout if prediction right: {{}} | readout if alternative right: {{}}

## 7. Decision rule (fixed in advance)
- **Supported:** dropout rescued AND module-specific readout concordant AND localisation compatible AND Tier-2 physical or epistatic support.
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
