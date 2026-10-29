# Round 1 review — biology and experimental follow-up (DESIGN.md v1)

Reviewer: cell biology / functional genomics. Read PROMPT, DESIGN v1, LITERATURE §1.4/§2/§5/§6, tool METHOD.md. No
results opened.

## Assessment

The design is statistically careful. Biologically, it has three gaps.

1. **The vocabulary is too narrow for the questions biologists ask.** A complex-first vocabulary (V1) suits zavg_BEF.
   But most of the project's own positive controls are not stable subunits:
   - SLC25A51 is a transporter that is co-essential with the ETC;
   - TMEM242 is an assembly factor;
   - SPRING1 is a pathway cofactor, and PEDS1 a pathway enzyme;
   - POU2AF2/3 are lineage coactivators.

   Scored only as "member of complex X", these calls are half-right. Suppliers and assembly factors get mislabelled as
   subunits, which is the field's commonest over-claim.
2. **The design has no model of which genes co-essentiality can reach.** Pooled growth screens in cancer lines cannot
   see:
   - genes that are not expressed in those lines (tissue-restricted, testis, neuronal, ciliary);
   - secreted and other non-cell-autonomous functions, which neighbouring cells complement in the pool;
   - redundant paralogs;
   - most signalling genes outside lineage-driver contexts.

   Split-half reproducibility (§4.2) does not catch profiles that are *reproducibly* artefactual, such as a
   non-expressed gene carrying a proximity signal.
3. **The orthogonal-evidence rules are the same for every prediction type, and they treat "not measured" as "not
   supported".**
   - Localisation is decisive for mitochondrial and nuclear machinery.
   - Chemogenomics is diagnostic only for DNA repair.
   - AP-MS rarely recovers assembly factors or multi-pass membrane proteins.

   As a result, "≥1 class supports" favours abundant, soluble proteins.

§6 describes the reports and experiments in one sentence each. I give templates for both below.

## Concrete changes

**1. (MUST) Add a pre-specified relationship type to every prediction.**
- Each prediction says how g relates to its module M: (a) stable subunit; (b) assembly/maturation factor; (c) supplier
  or client (transporter, enzyme, substrate of import/insertion machinery); (d) pathway member; (e) lineage or
  transcriptional programme.
- Type (a) may be claimed only with physical, co-abundance or structural support. Otherwise the claim reads "functions
  in/supports M".
- In §3, also score a module-level vocabulary V1′: complexes merged with their assembly factors (Complex Portal + GO CC +
  MitoCarta pathways). Report precision at both levels.
- Why: the controls show that co-essentiality finds the module reliably, and the structural role much less reliably.

**2. (MUST) Pre-register expression and reachability annotations for U, and use non-expressed genes as a negative
control.**
- Annotate each U gene with:
  - the fraction of screened lines with log2(TPM+1) ≥ 1 (`OmicsExpressionTPMLogp1…`, already on disk);
  - HPA/GTEx tissue-enriched or testis-enriched status;
  - secreted status (signal peptide, no TM) and TM count;
  - ciliary status (CiliaCarta).
- Genes expressed in < 10% of lines are "not assessable — not expressed".
- Their neighbourhoods are still computed, as a negative-control distribution. A confident call for a gene that cannot
  have a phenotype is a false positive by construction. This is the most biologically grounded false-positive rate the
  project can measure.
- Report assessability by category. The unreachable fraction of the dark genome is itself a result.

**3. (MUST) Add three artefact checks to §4.3.**
- **(f) Shared guides and overlapping loci.**
  - Flag pairs that share sgRNA target sequences. This needs the DepMap guide maps (`AvanaGuideMap`/`KYGuideMap`), which
    must be fetched.
  - Also flag readthrough or overlapping transcripts, and bidirectional promoters (TSSs < 1 kb apart on opposite
    strands).
  - Paralog flags miss shared guides.
- **(g) Regulatory co-dependency.**
  - Test whether g's dependency is explained by its own expression.
  - Test whether the top partners are enriched for transcription factors or lineage markers.
  - If either holds, relabel the prediction as type (e), not a function call.
- **(h) The p53 / Cas9-toxicity axis.** Correlate g's profile with TP53 status and with TP53/CDKN1A/USP28 dependency.
- **Copy number.** Add copy number (`OmicsCNGene`) so that co-amplified neighbours beyond the same arm are caught.

**4. (MUST) Make orthogonal evidence four-state and specific to the module family.**
- Each class records one of: not measured / no support / supports / contradicts.
- Only "contradicts" downweights a prediction.
- Absence of an interaction in AP-MS or BioID is **never** a contradiction.
- A contradiction requires incompatible localisation from ≥ 2 high-reliability sources (HPA Enhanced/Supported,
  OpenCell, Human Cell Map). Multi-localised proteins are exempt.
- Tier A requires support from a class that is *diagnostic* for the module family, whenever that class was measured.
  The diagnostic classes are pre-specified below.

| Module family | Diagnostic | Useful | Weak |
|---|---|---|---|
| Mitochondrial (OXPHOS, mitoribosome, import, Fe–S, CoQ) | Localisation (MitoCarta, MTS, HPA, Cell Map); co-abundance | Perturb-seq; BioPlex | Chemogenomics |
| Nuclear RNA machinery (splicing, Integrator, Pol II) | Perturb-seq profile (essential screens); nuclear localisation | Co-abundance; OpenCell | Chemogenomics |
| Ribosome biogenesis / translation | Perturb-seq; nucleolar localisation | Co-abundance | — |
| DNA replication / repair | Chemogenomics (Olivieri; ORCS); nuclear localisation | BioGRID LTP | Perturb-seq |
| ER/Golgi, secretory, lipid | ER/Golgi localisation; HAP1 GI map | Perturb-seq UPR (low specificity) | BioPlex (membrane under-recovery) |
| Centrosome / cilia / mitosis | Localisation; optical pooled screens | BioID | Co-abundance |
| Signalling / lineage TF | Lineage-restricted co-dependency; physical (OpenCell, LTP) | DEMETER2 | K562 Perturb-seq |

- Perturb-seq counts only if g was perturbed with significant on-target knockdown.
- For bidirectional-promoter pairs, CRISPRi is not orthogonal (see 3f).

**5. (MUST) Calibrate by module family and cap mitochondrial dominance.**
- Fit the §3.4 confidence model separately for (i) mitochondrial, (ii) large cytosolic/nuclear machinery (> 30
  subunits), and (iii) the rest. Alternatively, use family as a covariate.
- Why: pooled calibration lends mitochondrial precision to non-mitochondrial calls.
- Pre-specify that at most ⅓ of the top 20 are OXPHOS/mitoribosome calls.
- Why: OXPHOS dependency varies with medium and screen duration. Many supplier genes (type c; SLC25A51 is the template)
  therefore co-vary with the ETC.

**6. (SHOULD) Add homology and human genetics as evidence classes independent of DepMap.**
- (H) Orthologue experimental function in yeast, worm, fly and mouse (Alliance/PANTHER, IBA). PTAR1→ECM9 shows the
  value.
- (M) Mendelian phenotype (OMIM/ClinVar). Mitochondrial disease, ciliopathy and DNA-repair syndromes are strongly
  diagnostic.
- Both are reported only; neither is used to select U.

**7. (SHOULD) Add guide-level and modality robustness checks to §4.3.**
- The partner correlation must persist for each sgRNA separately (DepMap guide-level LFC).
- DEMETER2 replication is in LITERATURE §6.12 but missing from DESIGN. Add it, with a pre-specified threshold.

**8. (SHOULD) Screen the top 40 for curation lag before any report is written.** Run a quick alias and preprint
search. Report already-characterised genes as a curation-lag result (the TIMM29/DMAC1 lesson). Blinded judging then runs
on the remaining genes.

**9. (MUST) Adopt Template A** for `reports/<GENE>.md`. Each report has two figures: the profile panel and the
neighbourhood network.

**10. (MUST) Adopt Template B**, with expected outcomes stated for both "right" and "wrong", and cell lines chosen by
rule.

**11. (COULD) Use CCLE metabolomics as descriptive support for type (c) calls.** Correlate g's dependency or
expression with metabolite levels (the SLC25A51→NAD⁺ pattern).

---

## Template A — per-candidate report

1. **Header.**
   - Symbol, aliases, UniProt, band.
   - D1/D2/D3 values and audit flag.
   - One-sentence hypothesis with relationship type (a–e).
   - Calibrated probability, naming the calibration family used.
   - Tier.
2. **The protein.**
   - Domains (InterPro), TM/signal/MTS features, AlphaFold pLDDT, deepest orthologue.
   - Class H and class M evidence.
3. **Dependency profile.**
   - Mean and SD effect; fraction of lines < −0.5; common-essential or selective status; NaN fraction.
   - Expression across lines, with a dependency-vs-expression scatter.
   - Lineage enrichment.
   - Split-half assessability.
4. **Neighbourhood.**
   - Top 10 partners. For each: zavg_BEF, z_B/z_E/z_F, GLS rank, partner function and essentiality, chromosome and
     distance, paralog or guide-sharing flags, hu.MAP-train membership.
   - Network figure.
   - Top 3 terms with S, q and leave-one-partner-out stability.
5. **Robustness.** A pass/fail table: arm removal, lineage leave-out, K = 10/50, per-guide check, DEMETER2, p53 axis,
   copy number.
6. **Orthogonal matrix.** For each of classes P/A/L/G/S/H/M: dataset, whether measured, result, pair-level details,
   whether the class is diagnostic for this family.
7. **Literature.**
   - Blinded summary with evidence level (functional / high-throughput / mention).
   - Verdicts on the prediction and on the decoy.
   - Unblinded synthesis, with verified citations.
8. **Alternative explanations.** Each artefact and the evidence against it. The best competing biological hypothesis
   (for example, supplier rather than subunit).
9. **Falsifying observations.** One or two.
10. **Experiments** (Template B).
11. **Novelty.** Agreement with prior catalogues (Wainberg, hu.MAP 3.0, Perturb-seq), and what is new here.

## Template B — experiment tiers

**Cell lines (rule).**
- Two dependent lines:
  - Chronos ≤ −0.5 for g and ≤ −0.3 for the top partner;
  - g expressed (log2(TPM+1) ≥ 2);
  - g's locus not amplified;
  - high screen quality;
  - preferably TP53-null.
- One control line that expresses g but does not depend on it, from the same lineage where possible.
- For common-essential genes: RPE1-hTERT TP53⁻/⁻ or HEK293T, with a degron or CRISPRi.

**Reagents.**
- 3 sgRNAs with concordant DepMap guide-level effects, 2 non-targeting guides and an AAVS1 cutting control.
- CRISPRi guides if the locus is amplified.
- Guide-resistant cDNA (ORFeome).
- A validated antibody, or an endogenous HaloTag/mNG knock-in.
- Antibodies for the partners and organelle markers.

| Tier | Experiment | Time | If right | If wrong |
|---|---|---|---|---|
| 0 | AF-Multimer of g with the top 3 partners (ipTM/pDockQ) | days | Confident, conserved interface | No interface (does not exclude types b–e) |
| 1 | Competitive growth (GFP mix), 3 guides plus rescue, dependent vs control lines | 2–3 wk | Dropout only in dependent lines; rescued | No dropout, or no rescue (off-target or proximity) |
| 1 | Localisation with markers | 2–4 wk | Module's compartment | Incompatible compartment |
| 1 | Module-specific readout after KO | 2–4 wk | Phenocopies partner KO | Normal |
| 1 | Partner protein levels after g KO (and the reverse) | 2 wk | Co-destabilisation (types a/b) | Stable (favours c/d) |
| 2 | IP-MS / TurboID of tagged g vs an unrelated tagged control | 1–2 mo | Partners enriched (SAINT) | Absent, or another module appears |
| 2 | BN-PAGE / SEC co-migration | 1 mo | Co-migrates; KO stalls assembly | Separate |
| 2 | Double KO with partner (epistasis) | 1–2 mo | No extra defect | Additive or synergistic (parallel pathways) |
| 2 | Arrayed CRISPRi Perturb-seq with partners | 2 mo | Signatures cluster | Distinct |
| 3 | Interface mutants fail to rescue; reconstitution, activity or structure | 6–12 mo | Interface or activity required | Mutants rescue |

**Readout menu.**

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

**Decision rule.**
- **Supported:** ≥ 2 of the 3 Tier-1 experiments are concordant, *and* there is physical or epistatic support at Tier 2.
- **Refuted:** a dropout that is not rescued, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else. Report it as such and propose an alternative relationship type.
