# Protocol and screening records

| File | Content |
|---|---|
| `decision_rules.md` | Project decision rules applied at screening, extraction and synthesis (e.g. Rule 5: full-scale and laboratory/pilot evidence are not pooled) |
| `prompt_title_abstract_screening_v5.md` | Title/abstract screening prompt (v5; the screen used in the review ran with v3, see the note at the top) |
| `prompt_fulltext_screening_v5_2.md` | Full-text screening prompt used in the review |
| `prompt_text_extraction.md` | Text extraction prompt |
| `search_strategy.md` | Search strings for Scopus, Web of Science Core Collection and PubMed (28 April 2026) |
| `prisma_flow.csv` | Study-flow counts (Figure S1) |
| `fulltext_exclusion_reasons.csv` | Exclusion reasons at full-text screening (454) and eligibility re-assessment (19) |
| `title_abstract_screening_decisions_1530.csv` | Model decision (GPT-4o-mini), human decision and final decision for all 1,530 records. Every exclusion is a human decision; records not reviewed by a human retained the model's non-exclusion decision. 335 final decisions differ from the model. |
| `screening_benchmark_gold_and_predictions.csv` | Human labels and model predictions for the 794-record benchmark set |
| `screening_benchmark_metrics.csv` | Benchmark metrics (Table 1) |
| `screening_benchmark_run_manifest.md` | Run identifiers, dates and resource use of the benchmark runs |
| `fulltext_screening_targeted_audit_689.csv` | GPT-5.4-mini full-text decisions against the targeted human audit of 689 records (Table S5) |

The figure- and table-aware extraction prompt is embedded in internal extraction code that is not distributed. The review was not registered in advance.
