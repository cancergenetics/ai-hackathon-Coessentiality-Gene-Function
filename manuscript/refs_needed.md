# References needed (not in references/literature_refs.tsv)

Each row is a claim in the drafts that needs a citation. Placeholders in the drafts read `[refs_needed: <tag>]`.
None of these has been looked up or verified. Add verified rows to `references/literature_refs.tsv` and replace the
placeholders with the new keys.

| Placeholder tag | Draft / section | Claim to be supported | Suggested source (verify before use) |
|---|---|---|---|
| Webber 2010 | 02_methods, Assessability | Rank-biased overlap (RBO) as a similarity measure for top-weighted ranked lists; extrapolated RBO (eq. 32) used with persistence p = 0.9 | Webber, Moffat & Zobel, "A similarity measure for indefinite rankings", ACM TOIS 2010 |
| matching | 02_methods, Matched genes | Mahalanobis-distance nearest-neighbour matching with a caliper, and standardised mean differences as balance diagnostics | e.g. Rubin 1980 (Biometrics) or Stuart 2010 (Stat Sci) review of matching methods |
| Berger 1982 | 02_methods, Endpoint and comparators | The intersection–union test: reject a union of nulls only if each component test rejects at level α, with no multiplicity adjustment | Berger 1982 (Technometrics), or Berger & Hsu 1996 (Stat Sci) |
| bootstrap | 02_methods, Endpoint and comparators | Percentile and BCa bootstrap confidence intervals; cluster (block) resampling of dependent units | Efron 1987 (JASA, BCa); Efron & Tibshirani 1993; a cluster-bootstrap reference, e.g. Field & Welsh 2007 |
| Brier | 02_methods, Calibration | Brier score as a proper scoring rule for probabilistic predictions | Brier 1950 (Monthly Weather Review) |
| calibration | 02_methods, Calibration | Calibration intercept and slope (logistic recalibration) and reliability diagrams for assessing calibration | Cox 1958 (Biometrika); Van Calster et al. 2019 (BMC Med) |
| Wilson | 02_methods, Admission | Wilson score interval for a binomial proportion | Wilson 1927 (JASA) |
| Simes; Holm | 02_methods, Support test | Simes combination of p-values within an evidence class; Holm step-down across classes | Simes 1986 (Biometrika); Holm 1979 (Scand J Stat) |
| Cohen | 02_methods, Blinded judging | Cohen's κ for agreement between two judges | Cohen 1960 (Educ Psychol Meas) |
| (none placed) | 01_introduction, "Pre-registration" paragraph | Undisclosed analytic flexibility inflates apparent effects, and pre-registration guards against it | e.g. Nosek et al. 2018 (PNAS) "The preregistration revolution"; Simmons et al. 2011 (Psychol Sci) |
| (none placed) | 02_methods, Data | Citations for the DepMap 26Q3 release itself (DepMap portal / figshare DOI), Complex Portal, BioGRID and Ensembl 116 | DepMap 26Q3 figshare record; Meldal et al. (Complex Portal, NAR); Oughtred et al. 2021 (BioGRID, Protein Sci); Ensembl 2025/2026 NAR paper |
| (none placed) | 02_methods, Calibration | Cross-fitting (sample splitting for out-of-fold predictions) | Chernozhukov et al. 2018 (Econometrics J), optional |
| (none placed) | 02_methods, Hold-out power | Connor 1987 McNemar sample-size approximation used in results/holdout/holdout_sizing.md (only needed if the MDE formula is quoted) | Connor 1987 (Biometrics) |
| (none placed) | 02_methods, co-essentiality method | Laplacian eigenmaps (the E view), if the method description is expanded | Belkin & Niyogi 2003 (Neural Comput) |

## Status (2026-10-30, manuscript assembly)

All rows above were resolved in `manuscript/manuscript.md` with references verified against Crossref (and PubMed where
indexed) and added to `references/literature_refs.tsv` (verified_yes_no = yes): Webber2010; Rubin1980, Stuart2010;
Berger1982, BergerHsu1996; Efron1987, FieldWelsh2007; Brier1950; Cox1958, VanCalster2019; Wilson1927; Simes1986,
Aickin1996 (for Holm's procedure: Holm 1979 has no Crossref/PubMed record); Cohen1960; Nosek2018, Simmons2011;
DepMap_web, Meldal2022, Oughtred2021, Dyer2025; Chernozhukov2018; Belkin2003. Connor 1987 was not needed (no MDE
formula is quoted). The suggested Berger 1982 DOI (…10487759) resolved to a different paper and was replaced by
10.1080/00401706.1982.10487790.
