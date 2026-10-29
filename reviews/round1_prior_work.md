# Round 1 review: prior work (LITERATURE.md and DESIGN.md v1)

I read PROMPT.md, DESIGN.md, LITERATURE.md and the refs table. I did not open `external/coessentiality/results/` and ran no analysis. Spot checks used Europe PMC, PMC, bioRxiv, HGNC REST and web search.

## 1. Assessment

LITERATURE.md is thorough and mostly accurate. Of 16 claims checked, 13 are correct as stated, including all 12 HGNC rename dates, Rahman FLEX numbers (76% / 3,348 / ~300 screens), Kim 2019 (276 screens, 500-fold, 68,813 edges, 20 Mb filter), Pan 2018 (464 vs 231; 30.7% vs 10%), hu.MAP 3.0 (472 hypotheses), Stoeger (5%; 16% / 49%), Dede 2020 and Kory 2020. Three need correction (section 2).

The design is strong on pre-registration, circularity and nulls. Its weaknesses are: (a) tuning leakage into the V1 calibration, (b) selection bias in the temporal hold-out, (c) no test that co-essentiality adds anything beyond physical maps and earlier prediction lists, and (d) no policy for predictions that are already published.

**Closest prior work.** Wainberg 2021 (Nat Genet; bioRxiv 827071, 2019) is the direct predecessor: GLS, 485 lines, UniProt score ≤ 2, 108 genes, 2 validated. Also close: Kim 2019 and Pan 2018 (networks, named uncharacterised genes), Replogle 2022 Perturb-seq (function calls for C7orf26, TMEM242, SPATA5L1, CCDC86, ZNF236), hu.MAP 3.0 (472 hypotheses, 2025), Billmann 2026 (HAP1 GI map "complementing" DepMap), and single-gene DepMap discoveries (Zhou 2022, Bayraktar 2020, Amici 2022, Pan 2022). I found no systematic, calibrated, pre-registered co-essentiality re-annotation after Wainberg. That is a search result, not proof; the literature agent should run one dedicated Europe PMC / bioRxiv sweep (2022 to Oct 2026) and log it.

**Defensible contribution**: (1) dated pre-registered list; (2) temporal hold-out with calibrated confidence and an explicit "not assessable" class; (3) 1,361 models and a new scorer; (4) a prospective audit of 1 to 7-year-old prediction lists; (5) blinded literature test against decoys.

## 2. LITERATURE.md errata

| # | Claim | Source says | Fix |
|---|---|---|---|
| E1 | §2 INTS15: "depletion destabilises INTS10 [Replogle2022] [verified]" | Replogle only clustered C7orf26 perturbation phenotypes with Integrator (cluster 37). INTS10/13/14 stoichiometry and INTS10 loss in KO 293T cells are Pan 2022 (Webster) | Re-attribute to [Pan2022]. Upgrade the §1.3 Webster/C7orf26 statement from [unverified] |
| E2 | Wainberg 108 in the "Nature abstract"; "bioRxiv v2 says 102 / 220" | Nature Genetics 2021 (53:638). bioRxiv **v1** (Nov 2019, title "almanac") says 102 genes, ~220 predictions. v2 not checked | Fix journal; attribute 102 / 220 to v1; note title change |
| E3 | Negative lessons: TIMM29 and DMAC1 were Wainberg "uncharacterised" predictions to be excluded | The preprint lists C19orf52 and TMEM261 and cites Kang 2016 and Stroud 2016 as support, so the authors knew. The names TIMM29/DMAC1 do not appear in the text I read | Keep as a lesson on annotation-score lag; do not imply Wainberg treated them as novel |
| E4 | TEDC1/2: "7-year GO lag" (GO date 2025-08-28) | The GO date is last-modified (§2.3 says so). Pudlowski: eLife 11 Mar 2025 | Say "up to 7 years" |
| E5 | Rahman: "2 of 1,697 CORUM complexes" | 1,697 is the effective standard after contribution-diversity reduction (from 2,916) | Add that qualifier |
| E6 | Billmann: "113 low-citation genes linked to bioprocesses" | Not found in abstract or supplement page (File S12 lists genes; HEATR6 example). PTAR1/ECM9 is confirmed | Mark [unverified] or count from File S12 |

Also note for the table: Pan 2018 (16 May 2018) already placed TEDC1/2 and C19orf25, before the design's t0 (see change 5).

Gap to add to §1.4: the tool README plus a late-2025 DepMap forum thread report that newly added, sparsely screened genes dominate top co-dependencies. This supports a minimum screened-line rule on single-gene profiles.

## 3. Design changes

**Must**

1. **Remove tuning leakage from V1 (§3).** zavg_BEF was tuned on hu.MAP 3.0 train pairs, which derive from Complex Portal 2022_07. So "Complex Portal (current)" and GO CC complexes are also partly seen, not only hu.MAP. Evaluate V1 on complex-disjoint held-out complexes (the tool's own dev/test splits), or report seen vs unseen separately. The primary criterion must use unseen complexes. DESIGN §3 flags hu.MAP only.
2. **Show added value over existing evidence.** On the same hold-out, add a PPI-only guilt-by-association comparator (hu.MAP 3.0, BioPlex, STRING experiments) and a Wainberg-style module-transfer comparator. Report which U predictions have no physical support, i.e. depend on co-essentiality alone. Without this, the paper cannot claim more than hu.MAP 3.0's 472 hypotheses.
3. **Use earlier prediction lists as a prospective audit.** Wainberg's 108, hu.MAP's 472, Replogle's and Kim's named genes are 1 to 7 years old. Record what has since been experimentally shown (circularity blacklist applied). This gives a field-wide hit rate independent of our method. Compute their overlap with U before viewing any prediction (published tables only, so no breach), and flag overlapping genes "previously proposed".
4. **Adopt a novelty policy** (section 4).
5. **Fix hold-out timing.** (a) Per-annotation dating: count a term as acquired only if its supporting PMID postdates t0; a release diff also picks up curation backlog of old papers. (b) t0 = 2018-07-02 follows Pan 2018. Move t0 before May 2018 or drop TEDC1/2 and C19orf25 from the named controls.
6. **Build the circularity blacklist by text scan.** For every supporting PMID of a hold-out annotation, scan the full text (Europe PMC) for DepMap / Achilles / Avana / Chronos / co-essential. Kory 2020 cites DepMap in the abstract; others use it quietly. Report with and without.
7. **State and measure selection bias in H.** Genes characterised after 2018 are enriched for informative CRISPR profiles, and several were found through CRISPR or DepMap. Calibrating on H overstates precision for U, where many profiles are flat. Report H performance by assessability bin (§4.2 rule), apply the confidence model only within the covered range, and report the assessable fraction of U.
8. **Report V1 with ETC-I and the 55S mitoribosome removed** (Rahman 2021) as well as macro-averages. §4.3(c) stratifies U, but §3 does not stratify the benchmark.

**Should**

9. Add Unknome knownness (Rocha 2023) as a sensitivity set and "conserved unknown" tag (LITERATURE §3.3 recommends it; DESIGN §1 omits it). Report overlap of U with Unknome, Tdark and Wood 2019. Consider the neXtProt / HPP uPE1 list as a comparator after verifying its definition.
10. Treat the D3 threshold (≤ 10 focused records) and the 95th-percentile assessability cut as sensitivity analyses. Add a minimum screened-line count for single-gene profiles.
11. Repeat the novelty search for all Tier A and B genes at submission (symbols, previous symbols, aliases, UniProt; Europe PMC and bioRxiv), not only for the top 20 before analysis. Papers after the freeze date (2026-10-29) that confirm a prediction are genuine prospective validation; count them separately.
12. Add to LITERATURE.md: shinyDepMap (Shimada 2020), the lncRNA co-essential-module paper (PMC9191893), the DepMap portal co-dependency tool, coessentiality.net; say how this paper differs.

**Could**

13. Add a degree-preserving rewiring null on the kNN graph (LITERATURE §4.5b).
14. Use CORUM 4.0 as a second complex standard if the licence permits.
15. Compare at matched K against Wainberg's published GLS top-partner enrichment, since the tool's README reports macro per-cluster AP equal to GLS.

## 4. Novelty risk: predictions already published

1. Classify every Tier A and B prediction as N0 (function established), N1 (partly known, or related complex known) or N2 (absent from the literature). The blinded literature agents assign this, with the search date recorded.
2. Never drop N0 predictions. Report them as rediscoveries. Because the list is dated and frozen, they are time-stamped validation that the method finds true functions in genes called uncharacterised. The headline is a rediscovery rate with CI, beside the decoy support rate, then the N2 list.
3. Separate three kinds of "already published": curation lag (known, absent from GO; measured by the 50-gene audit), earlier prediction lists, and experimental papers.
4. Write "not found in the literature as of <date>", never "novel", before the check. Preprints and post-freeze papers get their own column.
5. Each per-candidate report states the novelty class, the closest prior publication, and what co-essentiality adds beyond it.
