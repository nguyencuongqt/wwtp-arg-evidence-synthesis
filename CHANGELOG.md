# Changelog

## v1.3.0 (1 October 2026) — final datasets

Replaces all preliminary content of v1.0.0–v1.2.0.

- **Data (v4, fixed 30 September 2026).** Eligibility re-assessment of 95 studies (19 excluded) and a final value audit of 491 values (231 retained, 6 of them corrected; 260 removed) were applied to the previous public datasets. Log10 reduction: 164 rows / 37 studies (126 rows / 30 studies full-scale); percent removal: 59 / 19; liquid abundance: 779 / 86; route layer: 295 / 70 (280 / 68 valid). For R0328, values reported after secondary sedimentation were reassigned to the influent-to-secondary-effluent route and the values after reverse osmosis, the final treatment unit, were added from the source. Every removed, corrected or added row is listed in `data/change_log_v3_to_v4.csv`.
- **Analysis.** Primary removal and abundance summaries use full-scale (Tier 1) systems only; laboratory, bench and pilot systems (Tier 2) are reported separately. `scripts/reproduce_results.py` replaces the earlier scripts and regenerates all reported values.
- **Audit records.** New `audit/` folder with the human decision records for eligibility, the final value audit, the second-reviewer check and the critical appraisal (previously distributed as Supplementary Data S1–S2). The critical-appraisal sensitivity analysis was recomputed on the final dataset.
- **Protocol.** PRISMA counts and exclusion reasons updated (694 eligible studies; 473 exclusions after full-text screening and eligibility re-assessment); final title/abstract decisions now reflect the reconciled human audit (346 exclusions, all human decisions).
- **Metadata.** Authors, title and citation updated; the processing ledger lists the screening, extraction and audit steps and who decided each. Screening prompts and decision rules added to `protocol/`.

## v1.2.0 (13 September 2026), v1.1.0 (20 August 2026), v1.0.0 (5 August 2026)

Preliminary releases based on the June–August 2026 dataset versions (v1.1.0 and v1.2.0 were distributed as archive packages and are not separate commits in this history). Superseded.
