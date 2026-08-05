# M1 Axis 2 v2 correction changelog

**Date:** 2026-07-30  
**Execution prompt:** `QC_D2_EXECUTION_20260730`  
**Corrected QC basis:** `QC_D2_CORRECTED_89ROW_BLASTRADIUS_20260730.md`

## Step 2 — code correction

- Updated `08_quantitative_synthesis/scripts/03_abundance_synthesis_axis2.py`.
- `classify_unit_track()` now checks `final_unit` before source-oriented unit
  fields.
- Rows already standardized to `copies_per_mL` in Step 06 are no longer
  subjected to another -3 log10 conversion.
- Rows retained as `copies_per_L` with `conversion_applied == No` continue to
  receive the required litre-to-millilitre conversion in Step 08.
- Verification against v1 changed exactly 89 rows, each by +3.0 log10, and
  left the remaining 1,038 rows numerically unchanged.

## Step 3 — frozen successor

- Created `m1_axis2_abundance_liquid_copies_ml_frozen_v2_20260730.csv`.
- Rows: 1,127 in v1 and v2.
- Studies: 109 in v1 and v2.
- Fieldwise comparison: exactly 89 `analysis_log10_value` cells changed;
  zero cells in all other columns changed.
- The original v1 cohort and original frozen-cohort definition were not
  modified.
- Added `M1_AXIS2_ABUNDANCE_V2_ADDENDUM_20260730.md`.
- Added successor checksum manifest
  `M1_AXIS2_V2_SHA256_MANIFEST_20260730.tsv`.

## Failed serialization attempt retained

The first v2 serialization attempt used pandas and changed textual
representations of unrelated floating-point and LOD/LOQ fields. It failed the
cell-invariance acceptance criterion and was moved, not deleted, to:

`superseded_20260730/FAILED_pandas_reserialized_m1_axis2_abundance_liquid_copies_ml_frozen_v2_20260730.csv`

The active v2 was regenerated with field-preserving CSV replacement and
passed strict cell-level comparison.

## SHA-256 ledger

| File | SHA-256 |
|---|---|
| `03_abundance_synthesis_axis2.py` | `5a4ffcd2d7efea777116d6137ba3946fc59d6d61f5f396f968464aa2ba337779` |
| `m1_axis2_abundance_liquid_copies_ml_frozen_v1_20260627.csv` | `fd854cad6e49527df7a1bd36fb467e14c26311c2de0b0e3874f6a7859af2045f` |
| `m1_axis2_abundance_liquid_copies_ml_frozen_v2_20260730.csv` | `08b6cfb974e859f4dbbe07462a7bb6807e0cd919d4544494ceb808d5f9f7fc52` |
| `M1_FROZEN_COHORT_DEFINITION_20260627.md` | `a031ae448103fdbd4b825497f2fa0f2973f56850cf7f52fe37ee86aa8b3490b8` |
| `M1_AXIS2_ABUNDANCE_V2_ADDENDUM_20260730.md` | `c0ea3b648c49fe37563520645bf538d36b3220ae70abb8b663da19ee1c7b783c` |
| Failed pandas serialization retained in `superseded_20260730/` | `f96ce4412025c82ddfe865ead3e6ba9bad0ab79cc2c56c0f03323d2c9618960e` |

## Gate status

Steps 2 and 3 passed. Downstream regeneration and manuscript propagation have
not yet been performed. Table 6/S17 and Abstract/Highlights remain gated
pending explicit sorted-value evidence for final-effluent sul, erm, and qnr.

