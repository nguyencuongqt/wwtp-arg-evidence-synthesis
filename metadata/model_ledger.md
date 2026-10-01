# Processing ledger

| Stage | Method | Who decided |
|---|---|---|
| Title/abstract screening | OpenAI `gpt-4o-mini` (temperature 0, 15 May 2026) proposed candidate decisions for 1,530 records | Human review of risk-flagged, uncertain and 794 benchmark records; every exclusion (346) was a human decision |
| Screening benchmark | `gpt-5.4-mini`, `mistral-small-2603` (open-weight) and a TF-IDF/logistic-regression baseline on the 794-record human-labelled set | Comparison only; did not change any decision |
| Full-text screening | OpenAI `gpt-5.4-mini`, prompt v5.2 (28 May 2026) proposed candidate decisions for 1,167 articles | Targeted human audit of 689 records, including all 403 model exclusions; the human decision was final |
| Eligibility re-assessment | — | 95 studies re-assessed against the full text by X.C.N. and T.U. (94 independently by both) |
| Text extraction | OpenAI `gpt-5.4-mini` produced candidate study metadata, measurements and outcomes with evidence quotations | Human extraction audit of 4,014 high-priority rows |
| Figure- and table-aware extraction | OpenAI `gpt-5.4` (final rerun `gpt-5.4-2026-03-05`) for 307 records, extracted twice and compared value by value | Disagreements and high-risk rows checked by a human reviewer |
| Targeted re-extraction | OpenAI vision model re-extracted under-captured sludge and sample-matrix rows (984 candidate rows); model version not recorded per row | Rows audited by a human reviewer in batches before use |
| Final value audit | — | 491 values verified against the source articles by X.C.N.; blinded re-check of 100 values by T.U. |
| Critical appraisal | — | 64 removal units appraised independently by X.C.N. and T.U. and jointly reconciled |
| Normalization, dataset definition and statistics | Deterministic scripts; no model calls | — |

Candidate data from the models never entered an analysis without passing the human checks above. Screening and text-extraction prompts are provided in `protocol/`.
