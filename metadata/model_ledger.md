# Model and processing ledger

| Stage | Production model or method | Role |
|---|---|---|
| Title/abstract screening | OpenAI `gpt-4o-mini` | AI-assisted production screening followed by human audit |
| Parsed-text extraction | OpenAI `gpt-5.4-mini` | Candidate structured extraction |
| Figure/table-aware extraction | OpenAI `gpt-5.4`; final rerun provenance `gpt-5.4-2026-03-05` | Candidate multimodal extraction and inter-run triangulation |
| Human audit | Human reviewer with deterministic audit records | Approval, correction, rejection, or deferral of candidate evidence |
| Normalization | Deterministic scripts; no new LLM calls | Controlled vocabulary, unit, matrix, route, direction, and value-scope rules |
| Knowledge-graph processing | Deterministic scripts; no new LLM calls | Processing of extraction-stage candidate triples |
| Cohort freezing and synthesis | Deterministic scripts; no new LLM calls | Read-only cohort construction and quantitative synthesis |

Mistral and TF-IDF/logistic-regression systems were screening benchmark comparators only. They did not contribute final quantitative extraction evidence.

The public cohorts retain extraction model and prompt-rule fields where needed for row-level provenance. Raw model outputs and source-text quotations are excluded from this public release.
