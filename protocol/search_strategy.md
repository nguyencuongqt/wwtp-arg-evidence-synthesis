# Search strategy

Search date: 28 April 2026. Databases: Scopus, Web of Science Core Collection and PubMed. Limits: English-language journal articles published 2001–2026. Raw retrieval counts are given in `prisma_flow.csv`.

## Scopus

```text
TITLE-ABS-KEY (
  (
    "antibiotic resistance gene*" OR "antimicrobial resistance gene*" OR
    "antibiotic resistant gene*" OR ARGs OR ARG OR resistome OR
    "mobile genetic element*" OR MGE*
  )
  AND
  (
    "wastewater treatment plant*" OR WWTP* OR "sewage treatment plant*" OR
    "water reclamation plant*" OR "water resource recovery facilit*" OR WRRF OR
    "municipal wastewater" OR "urban wastewater" OR "biological treatment plant*"
  )
  AND
  (
    remov* OR reduc* OR persistence OR persistent OR fate OR attenuation OR
    elimination OR inactivation OR enrichment OR enrich* OR
    "log reduction" OR "removal efficiency"
  )
)
AND PUBYEAR > 2000
AND LIMIT-TO (DOCTYPE, "ar")
AND LIMIT-TO (LANGUAGE, "English")
```

## Web of Science Core Collection

```text
(
  "antibiotic resistance gene" OR "antibiotic resistance genes" OR
  "antimicrobial resistance gene" OR "antimicrobial resistance genes" OR
  "antibiotic resistant gene" OR "antibiotic resistant genes" OR
  ARG OR ARGs OR resistome OR
  "mobile genetic element" OR "mobile genetic elements" OR MGE OR MGEs
)
AND
(
  "wastewater treatment plant" OR "wastewater treatment plants" OR
  WWTP OR WWTPs OR "sewage treatment plant" OR "sewage treatment plants" OR
  "water reclamation plant" OR "water reclamation plants" OR
  "water resource recovery facility" OR "water resource recovery facilities" OR
  WRRF OR WRRFs OR "municipal wastewater" OR "urban wastewater" OR
  "biological treatment plant" OR "biological treatment plants"
)
AND
(
  removal OR remove OR removed OR removing OR reduction OR reduce OR
  reduced OR reducing OR persistence OR persistent OR fate OR attenuation OR
  elimination OR inactivation OR enrichment OR enrich OR enriched OR
  "log reduction" OR "removal efficiency"
)
```

## PubMed

```text
(
  "antibiotic resistance gene"[Title/Abstract] OR
  "antibiotic resistance genes"[Title/Abstract] OR
  "antimicrobial resistance gene"[Title/Abstract] OR
  "antimicrobial resistance genes"[Title/Abstract] OR
  "antibiotic resistant gene"[Title/Abstract] OR
  "antibiotic resistant genes"[Title/Abstract] OR
  ARG[Title/Abstract] OR ARGs[Title/Abstract] OR
  resistome[Title/Abstract] OR
  "mobile genetic element"[Title/Abstract] OR
  "mobile genetic elements"[Title/Abstract] OR
  MGE[Title/Abstract] OR MGEs[Title/Abstract]
)
AND
(
  "wastewater treatment plant"[Title/Abstract] OR
  "wastewater treatment plants"[Title/Abstract] OR
  WWTP[Title/Abstract] OR WWTPs[Title/Abstract] OR
  "sewage treatment plant"[Title/Abstract] OR
  "sewage treatment plants"[Title/Abstract] OR
  "water reclamation plant"[Title/Abstract] OR
  "water reclamation plants"[Title/Abstract] OR
  "water resource recovery facility"[Title/Abstract] OR
  "water resource recovery facilities"[Title/Abstract] OR
  WRRF[Title/Abstract] OR WRRFs[Title/Abstract] OR
  "municipal wastewater"[Title/Abstract] OR
  "urban wastewater"[Title/Abstract] OR
  "biological treatment plant"[Title/Abstract] OR
  "biological treatment plants"[Title/Abstract]
)
AND
(
  removal[Title/Abstract] OR remove[Title/Abstract] OR
  removed[Title/Abstract] OR removing[Title/Abstract] OR
  reduction[Title/Abstract] OR reduce[Title/Abstract] OR
  reduced[Title/Abstract] OR reducing[Title/Abstract] OR
  persistence[Title/Abstract] OR persistent[Title/Abstract] OR
  fate[Title/Abstract] OR attenuation[Title/Abstract] OR
  elimination[Title/Abstract] OR inactivation[Title/Abstract] OR
  enrichment[Title/Abstract] OR enrich[Title/Abstract] OR
  enriched[Title/Abstract] OR
  "log reduction"[Title/Abstract] OR
  "removal efficiency"[Title/Abstract]
)
AND english[Language]
AND journal article[Publication Type]
AND ("2001/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
```

In Web of Science, the language, document-type and publication-year limits were applied with the database refinement filters.
