# Evidence for surveillance of antibiotic resistance genes in treated wastewater

Reproducibility package for the manuscript:

> Nguyen, X. C. & Unno, T. *What the evidence supports for surveillance of antibiotic resistance genes in treated wastewater: a human-verified, large language model-assisted synthesis.* (submitted to *Water Research X*)

Release **v1.3.0** contains the final v4 datasets, human audit and critical-appraisal records, and code that regenerates every quantitative result reported in the manuscript and its Supplementary Information. The final data include the author-confirmed R0328 endpoint correction checked on 2 October 2026. All earlier releases (v1.0.0–v1.2.0) were based on preliminary datasets and are superseded; see `CHANGELOG.md`.

The main branch also provides ready-to-submit **Data S1–S2** bundles in `supplementary_data/`. They mirror the appraisal, mapping and sensitivity inputs/results already archived in v1.3.0; Data S2 is restricted to the 16 critical-concern outcomes that intersect the final full-scale dataset. The v1.3.0 tag and archived release are unchanged.

## Contents

| Folder | What it contains |
|---|---|
| `data/` | Final analysis datasets (log10 reduction, percent removal, liquid abundance, route layer), the reported-detection aggregate, characteristics of the 136-study quantitative core, and a row-level change log from the previous public version |
| `audit/` | Human decision records: eligibility re-assessment of 95 studies, final value audit of 491 values, blinded second-reviewer check of 100 values, and the critical appraisal of 64 removal units with its sensitivity input |
| `protocol/` | Search strategy, decision rules, screening and extraction prompts, PRISMA flow counts, exclusion reasons, final title/abstract screening decisions, screening benchmark and full-text screening audit |
| `scripts/` | `reproduce_results.py` (all quantitative results), `audit_agreement.py` (agreement statistics), checksum and release-validation tools |
| `results/` | Outputs of `reproduce_results.py` |
| `metadata/` | Processing ledger, dataset definitions, SHA-256 checksums |
| `supplementary_data/` | Water Research X Data S1–S2 bundles and expanded machine-readable files |

## Who decided what

Large language models (OpenAI GPT-4o-mini, GPT-5.4-mini and GPT-5.4), called through the OpenAI API from Python scripts, generated **candidate** screening decisions and **candidate** extracted data only. mistral-small-2603 and a TF-IDF/logistic-regression baseline were run only as screening benchmark comparators and did not change any decision. Every exclusion at title/abstract and full-text screening was a human decision, every study contributing data to the synthesis was confirmed eligible by a reviewer, and every value audit decision and every critical-appraisal judgement was made by the authors (X.C.N. and T.U.), as recorded in `audit/` and `protocol/`. Model versions, run dates, settings and prompts are listed in `metadata/model_ledger.md` and `protocol/`. Normalization, dataset definition and statistics are deterministic and require no model calls.

## Reproduce the results

Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/reproduce_results.py
python scripts/audit_agreement.py
```

`reproduce_results.py` prints the main estimate (influent to final effluent, full-scale plants: median 2.30 log10, bootstrap 95% CI 1.46–3.00, 20 studies; DerSimonian–Laird 2.40, I² 98.4%) and writes all summary tables to `results/`.

## Verify integrity

The checksum manifest normalizes text-file line endings before hashing, so the same release verifies on Windows, macOS and Linux.

```bash
python scripts/verify_checksums.py
python scripts/validate_public_release.py
```

## What is not included

Publisher PDFs, titles, abstracts, evidence quotations and internal working files are not redistributed. The critical-appraisal records include the reviewers' short reconciliation rationales with page locators. Each row carries a record identifier and DOI; the DOI-linked articles remain the authoritative source.

## Citation

Nguyen, X. C. & Unno, T. Reproducibility package for traceable synthesis of antibiotic resistance gene burdens across wastewater treatment systems. Zenodo (2026). https://doi.org/10.5281/zenodo.21818085

## License

Code: MIT License. Data compilations and documentation: CC BY 4.0. See `LICENSE`.
