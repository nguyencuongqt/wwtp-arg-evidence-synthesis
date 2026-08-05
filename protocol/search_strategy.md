# Search strategy

Search date: 28 April 2026. Filters were English-language journal articles published from 2001 onward. Counts are reported in `prisma_flow.csv`.

## Scopus

```text
TITLE-ABS-KEY (("antibiotic resistance gene*" OR "antimicrobial resistance gene*" OR "antibiotic resistant gene*" OR ARGs OR ARG OR resistome OR "mobile genetic element*" OR MGE*) AND ("wastewater treatment plant*" OR WWTP* OR "sewage treatment plant*" OR "water reclamation plant*" OR "water resource recovery facilit*" OR WRRF OR "municipal wastewater" OR "urban wastewater" OR "biological treatment plant*") AND (remov* OR reduc* OR persistence OR persistent OR fate OR attenuation OR elimination OR inactivation OR enrichment OR enrich* OR "log reduction" OR "removal efficiency")) AND PUBYEAR > 2000 AND LIMIT-TO (DOCTYPE, "ar") AND LIMIT-TO (LANGUAGE, "English")
```

## Web of Science Core Collection

Topic search combining the same three concept groups: ARG/MGE terminology; WWTP and real-wastewater treatment terminology; and removal, persistence, fate, attenuation, inactivation, or enrichment terminology. Filters: Article; English; 2001-2026.

## PubMed

Title/Abstract search combining the same ARG/MGE, WWTP, and fate/removal concept groups. Filters: English; Journal Article; publication dates 2001-01-01 to 2026-12-31.

The complete expanded Web of Science and PubMed Boolean expressions are documented in the submitted Supplementary Methods. This repository records the reproducibility boundary without redistributing database exports.
