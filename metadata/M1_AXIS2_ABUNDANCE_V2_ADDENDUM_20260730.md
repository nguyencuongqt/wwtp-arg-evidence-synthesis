# Axis 2 liquid-abundance correction addendum

**Effective date:** 2026-07-30  
**Execution prompt:** `QC_D2_EXECUTION_20260730`

`m1_axis2_abundance_liquid_copies_ml_frozen_v2_20260730.csv` supersedes
`m1_axis2_abundance_liquid_copies_ml_frozen_v1_20260627.csv` for all M1
Axis 2 liquid-abundance analyses. Version 2 corrects a Step 08 unit-handling
error in which 89 measurements already converted from copies/L to copies/mL
during deterministic normalization were converted a second time during log10
cohort construction, producing a -3 log10 offset. Cohort eligibility and
membership are unchanged; only the affected `analysis_log10_value` cells are
corrected. Version 1 remains archived unmodified with its original checksum
for auditability. All other frozen M1 cohorts remain unchanged.

The corrected 89-row set is defined by `final_unit == copies_per_mL`,
`conversion_applied == Yes`, and a stored value equal to
`log10(normalized_value) - 3`. Twenty-seven rows included in the initial
116-row QC candidate set were confirmed as correctly handled per-litre values
with `conversion_applied == No` and were not changed.

