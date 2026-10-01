# Data (final version v4, fixed 30 September 2026)

| File | Rows / studies | Content |
|---|---:|---|
| `removal_log10_reduction_v4.csv` | 164 / 37 | Log10 reductions; 126 rows / 30 studies from full-scale systems form the primary analysis |
| `removal_percent_v4.csv` | 59 / 19 | Percent removal (bounded scale, analysed separately; all full-scale) |
| `abundance_liquid_v4.csv` | 779 / 86 | Liquid absolute abundance, log10 copies/mL-equivalent |
| `removal_route_layer_v4.csv` | 295 / 70 | Route-defined removal records; 280 rows / 68 studies valid for removal synthesis |
| `reported_detection_aggregate.csv` | 534 | Reported detections by gene family and matrix (descriptive layer from all studies judged eligible at full-text screening; not prevalence) |
| `reported_detection_by_family_and_matrix.csv` | 42 | The same layer summarized by gene family and matrix (Table S22; 5,301 reported detections from 371 studies) |
| `study_characteristics_quantitative_core_v4.csv` | 136 | Characteristics of the 136-study quantitative core (Table S18) |
| `metadata_coverage_v4.csv` | 14 | Reporting coverage of influent quality (136-study core) and operating conditions (264 candidate removal studies; audit made before the eligibility re-assessment) (Table S15) |
| `change_log_v3_to_v4.csv` | 453 | Every row removed, corrected or added relative to the previous public datasets (v1.2.0), with the reason |

## Columns added in v4

- `system_scale`, `analysis_tier`: full-scale or field-scale systems are Tier 1 (primary analysis); laboratory, bench and pilot systems are Tier 2 (reported separately).
- `eligibility_reassessment`: outcome of the eligibility re-assessment for studies that were re-assessed against the full text.
- `final_value_audit`: decision in the final value audit (`Correct` or `Corrected`) for values audited at that stage; other rows were verified at the earlier extraction audit or are outside the summaries used for synthesis.
- `verification_status`: `human-verified (extraction audit)`, `human-verified (final value audit)`, `human-verified (corrected by the authors against the source)`, `two-run agreement, not individually human-checked`, or `single extraction run, not individually human-checked`. Every row of the removal datasets and every row used in the influent, secondary-effluent and final-effluent abundance summaries is human-verified.
- `unit_plausibility_flag` (abundance): three influent values above 10^10 copies/mL confirmed as printed in the source articles but with unresolved unit plausibility; retained as reported.

`analysis_value` (removal) and `analysis_log10_value` (abundance) are the values used in the analyses. `extraction_model` and `prompt_rule_version` record how the candidate value was first extracted; they do not indicate who verified it.

One Tier 2 row (`O_004540`, sludge route) is flagged `valid_for_removal_synthesis = No` and does not enter any summary.

## Other columns

- `inter_run_agreement`: for figure- and table-aware rows, whether the two independent extraction runs agreed (`consensus`), or the value came from one run only (`legacy_only_rescued`, `rerun_only`); empty for text-extracted rows.
- `rescued_*`, `technology_supergroup_4group`: treatment category assigned by deterministic rules from the reported treatment train.
- `extraction_model`: model that produced the candidate value; `not recorded` where the row came from a targeted re-extraction of sludge and sample-matrix rows whose model field was not stored. Every such row was checked by a human reviewer.
- `target_group` (abundance): ARG/MGE target class used to select rows for the liquid-abundance track.
