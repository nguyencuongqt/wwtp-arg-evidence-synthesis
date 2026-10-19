# Supplementary Data S2 — Risk-of-bias sensitivity analysis

## Scope

This analysis uses the final v4 log10-reduction dataset after the eligibility and value audits and the author-confirmed R0328 endpoint correction. The primary analysis is restricted to full-scale systems (Tier 1). Outcomes linked to appraisal units judged Critical concern / insufficient reporting were excluded one outcome at a time; studies were not removed wholesale.

## Dataset counts

- Final log10 dataset: 164 outcomes from 37 studies (all scales).
- Primary full-scale dataset: 126 outcomes from 30 studies.
- Critical outcomes in the appraisal source: 22 overall; 16 intersect the primary full-scale dataset and are listed in `Supplementary_Data_S2_excluded_outcomes.csv`.
- Restricted full-scale dataset: 110 outcomes from 25 studies.
- Main influent-to-final-effluent route: 66 outcomes / 20 studies before restriction and 57 / 18 after restriction.

## Principal sensitivity result

For influent-to-final-effluent removal, the median of study-level medians was 2.3025 log10 before and after restriction (reported as 2.30 in the manuscript). The DerSimonian–Laird diagnostic changed from 2.3990 (95% CI 1.8355–2.9626; I² 98.3969%) to 2.4429 (95% CI 1.8263–3.0594; I² 98.5640%). The estimate therefore changed little, while heterogeneity remained very high.

For the main-route gene-family analysis, bla remained the only family meeting the prespecified ten-study pooling threshold (12 studies / 21 outcomes to 11 / 20; median 2.37 to 2.30 log10; DL 2.3075 to 2.2950). tet and sul remained descriptive. For treatment categories, biological treatment changed from 12 studies / 29 outcomes (median 1.875; DL 1.6107) to 10 / 20 (median 1.470; DL 1.5301); disinfection changed from 14 / 65 (median 2.000; DL 1.9632) to 13 / 64 (median 2.000; DL 1.9609). Membrane and physicochemical categories remained below the pooling threshold.

## Files

- `Supplementary_Data_S2_excluded_outcomes.csv`: the 16 critical-concern outcomes removed from the primary full-scale dataset, joined to the final v4 values.
- `Supplementary_Data_S2_full_vs_restricted_comparison.csv`: harmonized comparison of study counts, outcome counts, medians, pooled diagnostics, and I² for the route, gene-family and treatment cells.
- The remaining CSVs reproduce the primary/restricted route, gene-family, and treatment result tables from the repository.

Pooled DerSimonian–Laird values and I² use the manuscript's imputed-variance procedure and should be read as heterogeneity diagnostics, not precision-complete treatment effects. Full appraisal decisions and the complete reproducibility code are in the repository's `audit/critical_appraisal/` and `scripts/reproduce_results.py`.
