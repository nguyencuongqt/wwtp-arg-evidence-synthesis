# Dataset definitions (v4, fixed 30 September 2026)

The v4 datasets were derived from the previous public datasets (v1.2.0: log10 reduction 181 rows, percent removal 95 rows, liquid abundance 1,125 rows, route layer 295 rows) in two steps, both based on human decisions:

1. **Eligibility re-assessment.** Rows from the 19 studies excluded at the re-assessment were removed (`audit/eligibility_reassessment_95_studies.csv`).
2. **Final value audit.** Values that entered a reported synthesis without an earlier individual check were verified against the source article. Only values confirmed or corrected by the reviewer were retained; six values were replaced by the reviewer's corrected value (`audit/final_value_audit_491_values.csv`).

| Dataset | Previous public | Removed (eligibility) | Removed (value audit) | Corrected | v4 |
|---|---:|---:|---:|---:|---:|
| Log10 reduction | 181 | 4 | 19 | 0 | 158 rows / 37 studies |
| Percent removal | 95 | 0 | 36 | 0 | 59 / 19 |
| Liquid abundance | 1,125 | 145 | 201 | 6 | 779 / 86 |
| Route layer | 295 | 6 | — | — | 289 / 70 (274 / 68 valid) |

Analysis rules:
- Primary removal and abundance summaries use full-scale or field-scale systems (Tier 1). Two system-scale labels were corrected after checking the full text (R0170 and R0988, laboratory scale).
- Each study contributes one value per cell (median of its rows). DerSimonian–Laird estimates are reported only for cells with at least 10 studies (gene-family cells) or 5 studies (route and treatment cells).
- Percent removal is analysed separately from log10 reduction. Abundance values are cross-study and non-paired.
- Values below detection limits were excluded without substitution.

Every removed or corrected row is listed in `data/change_log_v3_to_v4.csv`.
