# Deterministic normalization workflow

This directory contains the rule-based Python scripts and controlled-vocabulary dictionaries used to normalize the candidate extraction tables before the final datasets were defined. The workflow makes no model calls. It preserves raw fields, maps terms through explicit dictionaries, separates incompatible unit families, records allowed unit conversions, and writes quality-control flags and reports.

The scripts are archived in their production form. Their default paths reproduce the internal project layout and therefore point to intermediate extraction tables that are not redistributed because some contain publisher-derived text. Each processing script accepts command-line paths for the input table, dictionaries, output table and log directory. The public final datasets in `data/` are the downstream, human-audited products used by `../reproduce_results.py`.

## Contents

- `01_create_default_dictionaries.py` creates the initial controlled vocabularies.
- `02_normalize_study_metadata.py` through `08_normalize_kg_triples.py` normalize each extraction table.
- `09_create_normalization_qa_reports.py` compiles mapping coverage and quality-control reports.
- `_norm_utils.py` contains the shared mapping, unit, scope and provenance rules.
- `dictionaries/` contains the final dictionaries used by the workflow. Superseded dictionary backups are excluded.

## Execution order

Run the scripts from this directory in numeric order. Supply the corresponding intermediate extraction file to each script when using a layout different from the original project. For example:

```bash
python 06_normalize_measurements.py \
  --input /path/to/candidate_measurements.csv \
  --dict-dir dictionaries \
  --output /path/to/arg_measurements_normalized.csv \
  --log-dir /path/to/logs \
  --overwrite
```

The normalization inputs are outside the public release. The scripts and dictionaries contain no publisher text, evidence quotations or article images.
