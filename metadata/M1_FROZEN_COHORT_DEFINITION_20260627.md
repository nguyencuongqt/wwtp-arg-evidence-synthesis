# M1 Frozen Cohort Definition

Freeze date: **2026-06-27**
Version: **v1.0**

Guardrail: these are read-only snapshot artifacts. They are frozen copies for M1 manuscript tables/figures and traceable provenance; normalized source tables and prior analysis cohorts are not modified.

Freeze integrity: every row-level snapshot carries `snapshot_read_only = Yes`, and the folder includes `M1_FROZEN_COHORT_SHA256_MANIFEST_20260627.tsv` for checksum verification. On the current Google Drive mount, Windows file read-only attributes may not persist; the checksum manifest is the stable audit lock.

## Frozen Cohorts

| cohort_id | rows | studies | snapshot CSV | provenance QC |
|---|---:|---:|---|---|
| `M1_AXIS1_REMOVAL_CROSS_STAGE_ROUTE` | 295 | 73 | `m1_axis1_removal_cross_stage_route_frozen_v1_20260627.csv` | record_id 100.0%; DOI 100.0% |
| `M1_AXIS1_REMOVAL_LOG_REDUCTION` | 185 | 45 | `m1_axis1_removal_log_reduction_frozen_v1_20260627.csv` | record_id 100.0%; DOI 100.0% |
| `M1_AXIS1_REMOVAL_PERCENT` | 95 | 28 | `m1_axis1_removal_percent_frozen_v1_20260627.csv` | record_id 100.0%; DOI 100.0% |
| `M1_AXIS2_ABUNDANCE_LIQUID_COPIES_ML` | 1127 | 109 | `m1_axis2_abundance_liquid_copies_ml_frozen_v1_20260627.csv` | record_id 100.0%; DOI 100.0% |
| `M1_AXIS2_ABUNDANCE_OTHER_QUANT_TRACKS` | 1104 | 93 | `m1_axis2_abundance_other_quant_tracks_frozen_v1_20260627.csv` | record_id 100.0%; DOI 100.0% |
| `M1_AXIS2_OCCURRENCE_DETECTION_ROW_LEVEL` | 5301 | 371 | `m1_axis2_occurrence_detection_row_level_frozen_v1_20260627.csv` | record_id 100.0%; DOI 100.0% |

## Axis 1 — Removal

### M1_AXIS1_REMOVAL_CROSS_STAGE_ROUTE

Frozen count: **295 rows / 73 studies**.

Filter chain:

1. Source: `outcomes_normalized.csv` plus treatment-rescued analysis-clean cohort.
2. Keep ARG/MGE target-specific quantitative removal outcomes with parsed cross-stage route transitions.
3. Include log-reduction and percent-removal rows that form the M1 route-removal evidence layer.
4. Start from `removal_cross_stage_analysis_cohort_treatment_rescued_20260626.csv` (**273 rows / 69 studies**).
5. Re-include the audited `REMOVAL_295_TO_273_LOSS_AUDIT_20260626.csv` rows (**22 rows / 8 studies**) to preserve the broader M1 cross-stage route cohort definition.
6. Join DOI/title/year/journal from `final_study_metadata.csv` by `record_id`.

Note: the 273-row cohort remains the analysis-clean subset used for strict valid before-after removal synthesis; the 295-row frozen route cohort is the M1 traceable route-removal evidence layer.

### M1_AXIS1_REMOVAL_LOG_REDUCTION

Frozen count: **185 rows / 45 studies**.

Filter chain:

1. Start from the frozen route-removal evidence layer.
2. Keep `outcome_unit_family == log_reduction`.
3. Include the 178 analysis-clean log-reduction rows.
4. Add 7 audited log-loss rows from the 295-to-273 audit that are non-negative route-removal/decrease rows.
5. Exclude 2 audited negative log rows marked as negative-log enrichment/removal-pool exclusion.
6. Retain `gene_family`, `route`, and rescued/collapsed `technology_supergroup_4group` for downstream M1 summaries.

### M1_AXIS1_REMOVAL_PERCENT

Frozen count: **95 rows / 28 studies**.

Filter chain:

1. Start from the analysis-clean treatment-rescued removal cohort.
2. Keep `outcome_unit_family == removal_percent`.
3. Keep percent-removal as a separate bounded scale; do not pool with log reduction.
4. Join DOI/title/year/journal from `final_study_metadata.csv` by `record_id`.

## Axis 2 — Abundance/Occurrence

### M1_AXIS2_ABUNDANCE_LIQUID_COPIES_ML

Frozen count: **1,127 rows / 109 studies**.

Filter chain:

1. Source: `abundance_axis2_clean_cohort_20260626.csv` derived from `arg_measurements_normalized.csv`.
2. Keep quantified detections already selected into the abundance clean cohort.
3. Keep `target_cohort == gene_mge`.
4. Keep `unit_track == liquid_absolute_log10_copies_per_mL_equivalent`.
5. Keep `usable_for_log10_abundance_synthesis == Yes`.
6. Do not interpret matrix medians as removal; this is an abundance landscape track.
7. Join DOI/title/year/journal from `final_study_metadata.csv` by `record_id`.

### M1_AXIS2_ABUNDANCE_OTHER_QUANT_TRACKS

Frozen count: **1,104 rows / 93 studies**.

Filter chain:

1. Source: `abundance_axis2_clean_cohort_20260626.csv`.
2. Keep `target_cohort == gene_mge`.
3. Exclude the liquid copies/mL-equivalent main track.
4. Keep remaining quantitative tracks separate: relative abundance/16S, metagenomic relative abundance, solid absolute abundance, and concentration tracks.
5. Do not pool these tracks with the liquid copies/mL track.

### M1_AXIS2_OCCURRENCE_DETECTION_ROW_LEVEL

Frozen count: **5,301 reported-detection rows / 371 studies**.

Filter chain:

1. Source: `arg_measurements_normalized.csv`.
2. Keep `detection_status in {detected_quantified, detected_not_quantified}`.
3. Keep `target_scope in {gene_specific, mge_marker}`.
4. Add `gene_family` and `matrix_bucket` for qualitative occurrence landscape summaries.
5. Join DOI/title/year/journal from `final_study_metadata.csv` by `record_id`.
6. No prevalence denominator; do not interpret as occurrence prevalence.

Aggregate landscape companion: `m1_axis2_occurrence_detection_landscape_aggregate_summary_frozen_v1_20260627.csv` preserves the 534 gene × matrix summary rows used in the abundance synthesis report.

## Use Rule

All future M1 tables/figures should use these frozen counts and file paths. Do not silently re-count from normalized sources unless a new frozen version is explicitly created.
