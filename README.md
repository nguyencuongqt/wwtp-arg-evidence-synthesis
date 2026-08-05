# Residual ARG burden after wastewater treatment

Minimal reproducibility and traceability package for the manuscript:

> *Residual antibiotic resistance gene burden after wastewater treatment: a traceable, knowledge-graph-based evidence synthesis for environmental AMR surveillance*

This repository contains the minimum public-safe data and code needed to verify the manuscript's principal numerical claims. It intentionally does not duplicate the manuscript, Supplementary Information, formatted tables, or publication figures.

## Contents

- `data/`: sanitized, analysis-ready frozen cohorts
- `scripts/`: deterministic analysis and integrity-checking code
- `results/`: compact machine-readable outputs used to verify reported values
- `metadata/`: cohort definitions, model/prompt provenance, and release checksums
- `protocol/`: search strategy, PRISMA counts, exclusions, and aggregate screening benchmark

Publisher PDFs, abstracts, copied source text, evidence quotations, internal audit notes, QC drafts, superseded files, and manuscript submission files are excluded.

## Reproducibility boundary

The row-level public cohorts retain record IDs, DOI links, quantitative values, normalized units, analysis classifications, and version fields needed to reproduce the synthesis. Evidence quotations and publisher-controlled article content are not redistributed. DOI-linked source documents remain the authoritative primary sources.

The production extraction evidence was OpenAI-only. Non-OpenAI systems were used only as screening benchmark comparators and did not contribute final extracted quantitative evidence.

## Installation

Python 3.12 is recommended.

```bash
conda env create -f environment.yml
conda activate arg-wwtp-m1
```

Alternatively:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproduce the principal summaries

Run from the repository root:

```bash
python scripts/15_rerun_frozen_dl_i2.py
python scripts/15_regenerate_axis2_v2_outputs_20260730.py
```

The first command regenerates the DerSimonian-Laird removal and heterogeneity outputs from the public 185-row log-reduction cohort. The second regenerates the corrected Axis 2 family-by-matrix abundance summary from the public 1,127-row cohort.

## Verify integrity and public safety

```bash
python scripts/verify_checksums.py
python scripts/validate_public_release.py
```

## Data limitations

The reported-detection layer is supplied as an aggregate table because tested-negative denominators were not consistently available and the manuscript interprets these data as reporting support, not prevalence. No risk ranking or causal technology ranking can be derived from this package.

## Citation and archival DOI

Use `CITATION.cff` to cite this repository. A permanent archival DOI can be added after creating a versioned Zenodo release.

## License

Code is released under the MIT License. Original data compilations and documentation are released under CC BY 4.0. Third-party source material is excluded; see `LICENSE`.
