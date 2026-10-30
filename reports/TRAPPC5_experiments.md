# TRAPPC5 — experiment plan (Template B)

Companion to `reports/TRAPPC5.md`. Evidence keys (T*, L*, P*) refer to Appendix A of that report; every key is verified. Cell lines, effects, media and copy number come from `reports/data/TRAPPC5/bundle.md` §10; values marked † are recomputed in `results/m7/scratch_reports_trappc5/`.

## 1. Context

- Gene: **TRAPPC5** | hypothesis: TRAPPC5 is a core subunit of the TRAPP tethering complexes required for Golgi vesicle transport, and its proliferation requirement in human cells tracks the TRAPPIII-specific arm (TRAPPC8/C11/C12/C13) rather than the TRAPPII arm (TRAPPC9/C10). | relationship type: **a** (stable subunit) | novelty class: **N2**
- LLM-recall-probe flag: **known** (a tool-less model already names TRAPP and Rab1) | calibrated probability p_cal **0.1140** [0.000–0.274] (family ER_Golgi_secretory_lipid) | tier: none (p_cal fill, rank 4 of the primary top 40)
- Strongest alternative explanation: the TRAPPIII-leaning co-dependency reflects the *arms'* own differential essentiality (TRAPPC9 mean −0.145, TRAPPC10 −0.029 †, both dispensable), or TRAPPC5 loss destabilising the whole core, rather than route-specific usage of TRAPPC5.
- **Decisive experiment (one sentence):** in two dependent lines, deplete TRAPPC5 acutely with a degron and measure, in the same cells and at matched growth inhibition against a matched-essentiality control gene, (i) Rab1-dependent ER→Golgi RUSH cargo delivery and (ii) Rab11-dependent post-Golgi delivery, alongside TRAPPC8 (TRAPPIII) and TRAPPC9 (TRAPPII) depletion — TRAPPC5 loss should phenocopy TRAPPC8 on the Rab1 arm and exceed TRAPPC9 on the Rab11 arm only if TRAPPC5 is shared, as the structure says [T4, T26], while the *dependency* is carried by TRAPPIII.
- Falsifying observation (Template A §9.3): TRAPPC5 depletion impairs Rab11-dependent transport at least as much as Rab1-dependent transport **and** TRAPPC9 co-depletion is epistatic to TRAPPC5 — refuting the TRAPPIII-leaning refinement (the only part of the call not already in UniProt/hu.MAP).

## 2. Cell lines (selection rule)

Rule: Chronos ≤ −0.5 for g and ≤ −0.3 for the rank-1 partner (TRAPPC3); g expressed (log2(TPM+1) ≥ 2); locus not amplified (relative CN < 1.5); best screen quality (ScreenNNMD); TP53-mutant preferred; line 2 from another lineage. Funnel: 1361 lines → 1168 (g ≤ −0.5) → 1168 (+partner) → 1102 (+expression) → 1082 (+not amplified).

| Role | ModelID | Name | Lineage / disease | g effect | TRAPPC3 effect | g expr (log2 TPM+1) | g CN | TP53 | ScreenNNMD | Medium |
|---|---|---|---|---|---|---|---|---|---|---|
| Dependent D1 | ACH-002877 | MSKPCa16 | Prostate / prostate adenocarcinoma | −0.62 | −1.76 | 3.48 | 1.02 | mutant | −24.24 | Prostate Organoid Media:NSA (1:1) (MF-031-007) |
| Dependent D2 | ACH-001852 | HKGZ-CC | Biliary tract / IPN of the bile duct | −0.98 | −1.93 | 5.95 | 1.10 | mutant | −17.33 | RPMI + 10% FBS (MF-001-001) |
| Control C (expresses g, does not depend on it) | ACH-000956 | 22Rv1 | Prostate / prostate adenocarcinoma (same lineage as D1) | −0.01 | −0.77 | 4.49 | 0.96 | mutant | −4.29 | RPMI + 10% FBS (MF-001-001) |

Practical note (recorded, not a deviation): both chosen dependent lines are organoid-derived/low-passage models; MSKPCa16 requires organoid medium. If either proves intractable for degron knock-in, the next qualifying lines by the same rule are ACH-003723 (HCM-WCMC-0673-C56-B, ovary, −0.98 / −1.68), ACH-001664 (SNU-638, gastric, −0.72 / −2.57) and ACH-000973 (639-V, bladder, −0.73 / −1.65). Lines must not be swapped for convenience without recording the substitution.

- Common-essential genes: TRAPPC5 is **not** common-essential (< −0.5 in 85.8% of lines, not ≥ 90%), but it is a dependency in most lines, so the degron/CRISPRi route is used anyway: RPE1-hTERT TP53⁻/⁻ or HEK293T with a dTAG or AID2 knock-in is run as a third, non-cancer context. Controls for the strong partners used as comparators (TRAPPC3, TRAPPC8 are common-essential): guide-resistant cDNA rescue, two non-targeting guides, and a control essential gene.
- **Baseline medium:** each line's own DepMap screen medium (above). Any sensitising condition (nocodazole washout, Brefeldin A challenge, starvation-induced autophagy) is a separate arm, never the baseline.
- **Essential-gene confound control (required):** hypomorphic/acute depletion of TRAPPC5 time-matched to TRAPPC8 and TRAPPC9 depletion, compared with a matched-essentiality control gene from an unrelated module: **NDUFAF8** (complex I assembly factor; mitochondrial module, unrelated to Golgi traffic) with Chronos −0.676 in D1 and −0.941 in D2 versus TRAPPC5's −0.620 and −0.983 (max |Δ| 0.055 across the two lines; genome-wide mean −0.630 vs TRAPPC5 −0.724) †. Every module readout must move beyond what NDUFAF8 depletion produces at the same growth inhibition.

## 3. Reagents

- **sgRNAs:** 3 independent guides per target (TRAPPC5, TRAPPC8, TRAPPC9, NDUFAF8), 2 non-targeting guides, AAVS1 cutting control. **Sequences are not listed here:** the project holds no CRISPR library file and DepMap guide maps are unavailable (DESIGN §4.3 "not possible (recorded)"), so per-guide DepMap effects cannot be quoted. Guides are to be taken from a published genome-wide library (e.g. Brunello/Avana sets distributed with the screens) and concordance across the three guides is established within the experiment itself.
- **Sequence-level off-target check (required):** genome-wide mismatch search for every guide before use (Cas-OFFinder or CRISPOR against GRCh38); acceptance rule fixed in advance — no perfect-match or 1-mismatch site in any other protein-coding gene and, specifically, none in TRAPPC3, TRAPPC8, TRAPPC9, TRAPPC11 or NDUFAF8. Tool and output table to be recorded with the result.
- **CRISPRi guides if the locus is amplified:** not needed (g CN 1.02 / 1.10 in D1 / D2); CRISPRi is nonetheless the backup modality if cutting toxicity confounds the 19p13.2 locus.
- **Guide-resistant cDNA:** TRAPPC5 ORF (188 aa) with silent PAM/seed mutations for all three guides, expressed from a weak promoter; an interface mutant series for Tier 3 is designed on the TRAPPC3b–TRAPPC5–TRAPPC8 contact reported in the TRAPPIII structure [T4, T5].
- **Endogenous tagging:** HaloTag or mNeonGreen knock-in at the TRAPPC5 locus plus a degron (dTAG/AID2), since validated TRAPPC5 antibodies are not established in the retrieved literature; TRAPP partners are followed with antibodies against TRAPPC3, TRAPPC8 and TRAPPC11.
- **Markers:** GM130/giantin (cis-Golgi), TGN46 (TGN), ERGIC-53 (ERGIC), calnexin (ER), LAMP1 (lysosome); RUSH reporters Str-KDEL_ST-SBP-EGFP (Golgi cargo) and Str-KDEL_TNF-SBP-mCherry (plasma-membrane cargo) [T18].

## 4. Experiment tiers

| Tier | Experiment | Time | If right | If wrong | Selected? | Expected readout (specific) |
|---|---|---|---|---|---|---|
| 0 | AF-Multimer of TRAPPC5 with TRAPPC3, TRAPPC1, TRAPPC11 (ipTM/pDockQ) | days | Confident, conserved interface | No interface (does not exclude types b–e) | **yes** | TRAPPC3–TRAPPC5 should reproduce the existing Burke-2023 pDockQ 0.680 (bundle §6) and the structural contact [T4]; TRAPPC11 is predicted **not** to contact TRAPPC5 directly (the arm attaches via TRAPPC3b/TRAPPC5 density [T5]) — a direct C5–C11 interface would be a surprise |
| 1 | Competitive growth (GFP mix), 3 guides plus guide-resistant cDNA rescue, D1/D2 vs control line C | 2–3 wk | Dropout in D1 and D2, none in 22Rv1; rescued by cDNA | No dropout, or no rescue (off-target or proximity) | **yes** | ~2–4-fold depletion of guide+ cells by day 21 in D1/D2 (Chronos −0.62/−0.98), ≤ 1.2-fold in 22Rv1 (−0.01); rescue restores to within 20% of non-targeting |
| 1 | **Essential-gene confound control:** degron depletion of TRAPPC5 time-matched to TRAPPC8 and TRAPPC9 depletion, vs NDUFAF8 at matched growth inhibition | 2–4 wk | Golgi/RUSH readout changes beyond NDUFAF8's at equal growth effect | Same change as NDUFAF8 (general sickness) | **yes** | At 50% growth inhibition: RUSH ER→Golgi t½ prolonged ≥ 2-fold after TRAPPC5 or TRAPPC8 loss, < 1.2-fold after NDUFAF8 loss |
| 1 | Localisation with markers (HaloTag knock-in) | 2–4 wk | cis-Golgi/ERGIC with ER pool, matching [L3] and HPA "Vesicles" | Incompatible compartment (e.g. nucleolus, mitochondria) | **yes** | ≥ 60% Pearson overlap with GM130/ERGIC-53 after cycloheximide chase; no MitoTracker overlap (MitoCarta: assessed, not listed) |
| 1 | **Module-specific readout after depletion** (decisive; see §5) | 2–4 wk | Phenocopies TRAPPC8/TRAPPC3 depletion on the Rab1 arm | Normal transport | **yes** | See §5 and §6 |
| 1 | Partner protein levels after TRAPPC5 depletion (and the reverse) | 2 wk | Co-destabilisation of TRAPPC3/C1/C4 (types a/b) | Partners stable (favours c/d) | **yes** | ≥ 40% reduction of steady-state TRAPPC3 and TRAPPC8 by western 48 h after degron addition; TRAPPC5 reciprocally lost after TRAPPC3 depletion |
| 2 | IP-MS / TurboID of tagged TRAPPC5 vs an unrelated tagged control | 1–2 mo | TRAPP subunits enriched (SAINT) | Absent, or another module appears | **yes** | All of TRAPPC1/2L/3/4/6A/6B plus both arms recovered; stoichiometric ratio of TRAPPC8-arm to TRAPPC9-arm peptides quantified — the key number for the TRAPPIII-vs-TRAPPII claim |
| 2 | BN-PAGE / SEC co-migration | 1 mo | TRAPPC5 co-migrates with both TRAPPII and TRAPPIII species; depletion stalls assembly | Separate species | **yes** | Two resolvable high-MW species (TRAPPC9/C10-containing and TRAPPC8/C11-containing); after TRAPPC5 degron both collapse to a sub-core peak |
| 2 | Double KO with partner (epistasis) | 1–2 mo | TRAPPC5 + TRAPPC8 no extra defect (same pathway); TRAPPC5 + TRAPPC9 additive | Additive with TRAPPC8 (parallel pathways) | **yes** | Growth and RUSH defects: TRAPPC5∧TRAPPC8 ≈ TRAPPC8 alone; TRAPPC5∧TRAPPC9 > either alone |
| 2 | Arrayed CRISPRi Perturb-seq with partners | 2 mo | Signatures cluster with TRAPP subunits | Distinct | no (deferred; the three Perturb-seq datasets already support the G class, bundle §6) | — |
| 3 | Interface mutants fail to rescue; reconstitution | 6–12 mo | The TRAPPC3b/TRAPPC5 interface [T4, T5] is required for rescue and for arm recruitment | Mutants rescue fully | optional | Interface-mutant cDNA rescues growth but not TRAPPC8-arm recruitment → separates core assembly from arm recruitment |

Type-specific rows: the relationship type here is **a** (stable subunit); Template B defines extra rows only for types b, c and e, so no type-specific row is added. The subunit claim is instead carried by the Tier-2 BN-PAGE/SEC and IP-MS rows, which are the evidence the type-a claim requires.

## 5. Module readouts

The predicted module (GO:0048193 Golgi vesicle transport) is not one of the named rows of Template B §5, so the "Other" row applies.

| Module | Readouts |
|---|---|
| Other — Golgi vesicle transport / TRAPP | (i) RUSH synchronised ER→Golgi and Golgi→plasma-membrane cargo release, where "Biotin addition causes a synchronous release of the reporter from the hook" [T18] (PMID:22406856, ledger row T18); (ii) Golgi morphology (GM130/TGN46 fragmentation); (iii) glycosylation of LAMP2 and ICAM-1, the assay that reported the ER–Golgi defect in TRAPPC11 patient cells [T17] (PMID:38564972, ledger row T17); (iv) Rab1 and Rab11 activation (GTP loading) measured separately, since the two TRAPP subtypes differ in substrate [T9] |

**Chosen readout:** RUSH ER→Golgi cargo t½ (primary), with LAMP2/ICAM-1 glycosylation shift and separate Rab1/Rab11 activation as secondary, all measured against NDUFAF8 at matched growth inhibition.

## 6. Experiment that separates the alternative explanation

- **Alternative:** the TRAPPIII-leaning co-dependency is a by-product of the TRAPPII arm being dispensable for proliferation in these lines (or of TRAPPC5 loss destabilising the core wholesale), not of route-specific TRAPPC5 usage.
- **Experiment:** (a) quantitative IP-MS of tagged TRAPPC5 measuring the ratio of TRAPPC8/C11-arm to TRAPPC9/C10-arm peptides recovered (does TRAPPC5 actually sit in both complexes in these lines?); (b) epistasis of acute TRAPPC5 depletion with TRAPPC8 vs TRAPPC9 knockout for growth and for the two RUSH arms; (c) Rab1-GTP and Rab11-GTP loading after each depletion.
- **Readout if the prediction is right:** TRAPPC5 is recovered in both assemblies at comparable stoichiometry, but only the Rab1/TRAPPIII arm readouts (ER→Golgi RUSH, Rab1-GTP) collapse on depletion; TRAPPC5∧TRAPPC8 double loss is epistatic while TRAPPC5∧TRAPPC9 is additive.
- **Readout if the alternative is right:** TRAPPC5 depletion impairs Rab1- and Rab11-dependent transport equally (shared-core behaviour with no route preference), or both arms disassemble identically — in which case the co-essentiality asymmetry is explained by the arms' own dispensability and the refinement in `reports/TRAPPC5.md` §7 must be withdrawn.

## 7. Decision rule (fixed in advance)

- **Supported:** dropout in D1/D2 rescued by guide-resistant cDNA **AND** RUSH/glycosylation readout changed beyond NDUFAF8 at matched growth inhibition **AND** localisation compatible (cis-Golgi/ERGIC/ER) **AND** Tier-2 physical or epistatic support (TRAPP subunits recovered by IP-MS, or TRAPPC8 epistasis).
- **Refuted:** a dropout that is not rescued, or incompatible localisation in both dependent lines.
- **Ambiguous:** anything else — reported as such, with an alternative relationship type proposed (most plausibly **b**, an assembly/stability factor for the core, if partners destabilise without a route-specific transport defect).

## 8. Evidence ledger

All rows verified as described in `reports/TRAPPC5.md` Appendix A (Europe PMC resolution + verbatim span match; `results/m7/scratch_reports_trappc5/verify.py`).

| Claim | Source | Verbatim span | Verified |
|---|---|---|---|
| RUSH is a validated synchronised secretory-traffic assay | PMID:22406856 / 10.1038/nmeth.1928 | "Biotin addition causes a synchronous release of the reporter from the hook." (abstract) | Y |
| LAMP2/ICAM-1 glycosylation and ER–Golgi transport assays report on TRAPP-complex loss | PMID:38564972 / 10.1016/j.ymgme.2024.108469 | "membrane trafficking assays in our patient showed defective abnormal endoplasmic reticulum-Golgi transport as well as decreased expression of LAMP2, and ICAM-1 glycoproteins" (abstract) | Y |
| The two metazoan TRAPP complexes differ in Rab substrate, so Rab1 and Rab11 readouts discriminate them | PMID:29273580 / 10.1083/jcb.201705068 | "both activate Rab1, whereas one, TRAPPII, also activates Rab11" (abstract) | Y |
| TRAPPC5 sits at the TRAPPC3b position where the TRAPPC8 arm attaches (interface-mutant design) | PMID:34018214 / 10.15252/embj.2020107608 | "TRAPPC8 is linked to density formed by the connection of the first two α‐helices of TRAPPC3b and TRAPPC5" (full text) | Y |
| TRAPPC5 is part of the core shared by TRAPPII and TRAPPIII (basis for the stoichiometry experiment) | PMID:42738849 / 10.3390/cells15171555 | "Both of these complexes share a conserved common core of subunits (TRAPPC1, TRAPPC2, TRAPPC2L, TRAPPC3, TRAPPC4, TRAPPC5, and TRAPPC6A/B)" (full text) | Y |
| TRAPPC13 loss reduces Rab1a/Rab1b activity (Rab-activation readout is informative for arm subunits) | PMID:28536105 / 10.1242/jcs.199521 | "TRAPPC13 depletion reduces Rab1a and Rab1b activity, impairs autophagy" (abstract) | Y |
| Cell lines, effects, expression, CN, TP53 status, screen quality and media | `reports/data/TRAPPC5/bundle.md` §10 (DepMap `CRISPRGeneEffect.csv`, `Model.csv`, `OmicsExpression…`, `OmicsCNGeneWGS.csv`, `CRISPRConfounders.csv`) | machine-generated table; not retyped | Y |
| NDUFAF8 as the matched-essentiality control (effects in D1/D2) | `results/m7/scratch_reports_trappc5/ctrl2.py` output † | TRAPPC5 [−0.620, −0.983] vs NDUFAF8 [−0.676, −0.941], max \|Δ\| 0.055 | Y |

## 9. Red-team review

**pending** — separate agent; to be appended unedited.

- Reviewer / model / date: pending
- Review text: pending
- PI response: pending
