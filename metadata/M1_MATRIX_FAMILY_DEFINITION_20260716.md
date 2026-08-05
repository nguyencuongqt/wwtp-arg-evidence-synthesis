# M1 matrix family definition

## Freeze status

- Definition freeze date: 2026-07-16
- Cohort freeze date: 2026-06-27
- Selection label: **PRE-SPECIFIED RELATIVE TO COHORT FREEZING**
- Registration status: not pre-registered in the study protocol
- Status: additive definition artifact; no frozen cohort file was altered

## Approved selection rule (verbatim)

Selection rule — label: PRE-SPECIFIED RELATIVE TO COHORT FREEZING
(not pre-registered in the study protocol).

Six named priority gene families (tet, sul, bla, intI1, erm, qnr) were
hard-coded as the PRIORITY_FAMILIES constant in the normalization code
prior to cohort freezing (2026-06-27). Normalized targets not matching a
priority family were collapsed deterministically into an `other` residual
bucket. The matrix covers the six named priority families; `other` is
excluded because it is a residual aggregate, not a gene family.

Table 10 applied this pre-existing constant to the already-frozen cohorts,
so family selection was not conditioned on the frozen results.

## Frozen matrix family set and evidence availability

Counts describe evidence availability in the existing frozen outputs. Axis 1 is the main influent-to-final-effluent removal route; Axis 2 is final-effluent liquid abundance.

| Family | Deterministic vocabulary/mapping condition | Axis 1 studies | Axis 1 rows | Axis 2 studies | Axis 2 rows |
|---|---|---:|---:|---:|---:|
| tet | target starts with `tet`, or normalized ARG class contains tetracycline | 11 | 18 | 14 | 66 |
| sul | target starts with `sul`, or normalized ARG class contains sulfonamide | 10 | 16 | 20 | 61 |
| bla | target starts with `bla`, or normalized ARG class contains beta-lactam or carbapenem | 13 | 22 | 19 | 50 |
| intI1 | target/name/class matches an `intI1` spelling or class-1-integron pattern | 7 | 8 | 17 | 42 |
| erm | target starts with `erm`, or normalized ARG class contains macrolide or lincosamide | 8 | 11 | 7 | 12 |
| qnr | target starts with `qnr`, or normalized ARG class contains quinolone | 2 | 2 | 9 | 22 |

## Exclusions and efflux/multidrug disposition

- `other` is excluded from the matrix because it is the deterministic residual aggregate for normalized targets that do not match a named priority family.
- `mexF` is assigned to `other`: it has one study/one row in the frozen Axis 1 percent-removal cohort and three studies/five rows in Axis 2 final-effluent liquid abundance.
- `acrB` is assigned to `other`: it was extracted and normalized, but the exact target does not occur in the frozen cohorts.
- `macB` is assigned to `erm` because its normalized macrolide-resistance class meets the `erm` family class condition: it has one study/one row in Axis 2 final-effluent liquid abundance and no main-route Axis 1 display.
- These dispositions are deterministic applications of the frozen mapping logic, not additional matrix families.

## Matrix dimensions

The six-family matrix is organized as an evidence-availability framework across:

1. removal evidence;
2. residual-burden evidence;
3. reported-detection breadth;
4. mobility/class context; and
5. uncertainty and evidence limitations.

## Scope and interpretation

This matrix supports evidence-availability synthesis and monitoring prioritization. It does not establish biological risk, clinical risk, environmental prevalence, or a ranking of intrinsic hazard. Absence or sparsity in a matrix cell indicates limited eligible evidence under the frozen cohort definitions, not confirmed absence in wastewater systems.

## Provenance

- Frozen cohort definition: `08_quantitative_synthesis/frozen_cohorts/M1_20260627/M1_FROZEN_COHORT_DEFINITION_20260627.md`
- Axis 1 family evidence source: `08_quantitative_synthesis/tables/m1_results_A1_removal_main_route_gene_forest_frozen_dl_20260629.csv`
- Axis 2 family evidence source: `08_quantitative_synthesis/tables/m1_results_B1_abundance_liquid_gene_family_by_matrix_20260629.csv`
- Removal family-collapsing implementation: `08_quantitative_synthesis/scripts/01_removal_meta_analysis.py`
- Abundance family-collapsing implementation: `08_quantitative_synthesis/scripts/03_abundance_synthesis_axis2.py`
- Upstream target vocabulary: `06_data_normalization/dictionaries/arg_name_dictionary.csv`
- Table 10 manuscript source: `11_manuscript/manuscript_1_quantitative_review/09_submission/01_sources/MAIN_MANUSCRIPT.md`

The approved rule uses “normalization code” as its frozen wording. For implementation-level provenance, the named-family collapsing constant and logic are located in the two quantitative-synthesis scripts listed above; the upstream normalization dictionary supplies target vocabulary/class assignments.

## Companion CSV integrity

- File: `M1_MATRIX_FAMILY_DEFINITION_20260716.csv`
- Bytes: 2796
- SHA-256: `52a9cccb91c8aec9661d6e996796b2e9a840a28aac887ddfc674404bc2383e11`
- Manifest: `M1_FROZEN_COHORT_SHA256_MANIFEST_20260627.tsv`
