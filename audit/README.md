# Human audit and critical-appraisal records

All decisions in this folder were made by the authors: X.C.N. (Xuan Cuong Nguyen) and T.U. (Tatsuya Unno).

| File | Content |
|---|---|
| `eligibility_reassessment_95_studies.csv` | Full-text eligibility re-assessment of the 95 studies that contributed quantitative data without an earlier individual audit. 94 were assessed independently by both reviewers (three-category agreement 87.2%, Cohen's κ = 0.80); disagreements were resolved by X.C.N. One study (R0451) was assessed by X.C.N. 19 studies were excluded. |
| `final_value_audit_491_values.csv` | Every value that entered a reported synthesis without an earlier individual check (84 removal and 407 abundance values), verified against the source article by X.C.N. 231 were retained (225 confirmed, 6 corrected); 260 were removed, with the reason recorded. Three retained values belong to studies later excluded at the eligibility re-assessment, so 228 of the retained values appear in the final datasets. Page locators are given for verification. |
| `final_value_audit_second_reviewer_100.csv` | Blinded re-check of a stratified random sample of 100 of these values by T.U. Excluding the 10 rows marked as duplicates, agreement was 66.7% (κ = 0.52) for categories and 73.3% (κ = 0.49) for keep versus remove. Among these 90 rows there were 30 disagreements (rows marked `disagree`; a further 9 disagreements fall in the excluded duplicate rows). The authors reviewed all disagreements and retained the first reviewer's decision in every case. In one duplicate pair (UC013/UC065) the reviewers kept opposite copies of the same value; this is recorded as agreement. |
| `critical_appraisal/critical_appraisal_unit_summary_64_units.csv` | Final outcome-specific critical appraisal of 64 removal units (five domains and overall judgement), independently assessed by X.C.N. and T.U. and jointly reconciled on 13 September 2026 (formerly Supplementary Data S1). |
| `critical_appraisal/critical_appraisal_domain_decisions_64_units.csv` | Domain-level judgements of each reviewer, reconciliation and source locators (formerly Supplementary Data S1). |
| `critical_appraisal/appraisal_units_in_final_dataset_v4.csv` | Which appraisal units contribute to the final full-scale primary dataset (44 of 64: 1 low concern, 38 some concerns, 5 critical concern). |
| `critical_appraisal/critical_concern_outcomes.csv` | The 22 valid outcomes linked to units at critical concern; input to the sensitivity analysis. |

The sensitivity analysis itself (formerly Supplementary Data S2) is regenerated on the final dataset by `scripts/reproduce_results.py`; see `results/critical_appraisal_sensitivity_*.csv`.

Run `python scripts/audit_agreement.py` to reproduce the agreement statistics.
