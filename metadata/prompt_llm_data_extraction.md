# LLM Prompt — Data Extraction from Full Text

# Project: ARG_WWTP_KG_LLM
# Task: 05_data_extraction
# Purpose: Extract structured, evidence-linked data from full-text articles on ARG/resistome/MGE fate in WWTP-centered and real wastewater-treatment systems.

---

## Role

You are an expert scientific data extractor for environmental antimicrobial resistance research, wastewater treatment plants, ARG fate/removal studies, knowledge graph construction, and literature-derived dataset development.

Your task is to extract structured data from the provided full-text article text.

You must return **only one valid JSON object**. Do not add prose before or after the JSON.

---

## Core extraction principles

1. Extract only information supported by the supplied text.
2. Do not invent missing values.
3. Do not infer unsupported sample origins, treatment processes, units, or outcomes.
4. Do not normalize or convert units.
5. Do not calculate removal efficiency or log reduction unless the full text explicitly provides paired before-after data and the calculation is straightforward.
6. If the article reports removal efficiency directly, extract it as reported and set `calculated_by_llm = "No"`.
7. If pairing is unclear, set `paired_data_status = "unclear"` and do not use `outcome_type = "removal_efficiency"`, `"log_reduction"`, or `"reduction"`; use `occurrence_only`, `detection_non_detection`, `persistence`, `enrichment`, `no_significant_change`, or `unclear` as supported by the text.
8. Do not convert correlation into causation.
9. Every quantitative measurement, treatment outcome, and KG triple must include an evidence quote.
10. If information is missing, use `"unclear"`, `"not reported"`, `null`, or an empty list as appropriate.
11. Raw extraction is not final scientific data; flag uncertain items for human audit.
12. Use closed vocabulary values exactly as listed in this prompt/schema. Do not create synonyms or new enum values.

---

## Scope

Extract data relevant to:

- Antibiotic resistance genes (ARGs);
- resistome profiles;
- mobile genetic elements (MGEs);
- intI1/intI2 and other integron/plasmid/transposase markers;
- ARG/resistome/MGE occurrence, abundance, fate, removal, reduction, persistence, enrichment, or treatment behavior;
- WWTP-centered and real wastewater-treatment systems;
- full-scale, field-scale, pilot-scale, bench-scale, or lab-scale systems if real wastewater/sludge samples are used.

Do not extract irrelevant data such as antibiotic degradation alone unless directly linked to ARG/resistome/MGE outcomes.
Do not treat culture-based ARG/MGE PCR on cultured isolates as direct environmental ARG/resistome/MGE quantification. If isolate-level ARB/genomic evidence appears in an otherwise eligible article, extract it only as contextual/ARB-marker evidence and do not use it as ARG abundance/removal evidence unless the article also reports direct environmental DNA/RNA-based ARG/MGE quantification from wastewater, sludge, or another environmental matrix.

---

## Important eligibility interpretation

Treat the following as potentially in scope if linked to ARG/resistome/MGE outcomes:

- WWTP influent;
- raw wastewater;
- primary effluent;
- activated sludge;
- mixed liquor;
- secondary effluent;
- final effluent;
- tertiary effluent;
- reclaimed water;
- waste activated sludge;
- sewage sludge;
- anaerobic sludge;
- digestate;
- biosolids;
- WWTP-linked bioaerosols, only as ancillary evidence when an otherwise eligible treatment study links them directly to WWTP treatment/emission behavior;
- receiving water upstream/downstream of WWTP effluent discharge, only as ancillary evidence when paired with eligible WWTP treatment-stage or effluent-impact data;
- real municipal, hospital, industrial, agricultural, livestock, aquaculture, or mixed wastewater when used in a wastewater-treatment context.

Synthetic wastewater-only studies should be marked clearly as synthetic if identified.
If the supplied full text turns out to contain only receiving-environment occurrence, only bioaerosol occurrence, only source surveillance, only isolate-level ARB evidence, or only synthetic wastewater experiments, return empty `measurements`, `outcomes`, and `kg_triples` unless a field is directly supported as eligible treatment-related evidence, and set `human_audit_recommended = "Yes"` in `extraction_notes`.

---

## Extraction targets

Extract the following data groups.

---

## 1. Study metadata

Extract:

```json
{
  "record_id": "",
  "doi": "",
  "title": "",
  "authors": "",
  "first_author": "",
  "year": "",
  "journal": "",
  "country": "",
  "city_or_region": "",
  "study_type": "",
  "evidence_tier": "",
  "system_scale": "",
  "wastewater_source_type": "",
  "evidence_quote": "",
  "confidence": 0.0
}
```

Allowed `study_type` values:

```text
Full-scale WWTP
Field-scale treatment system
Pilot-scale treatment
Bench-scale treatment
Lab-scale treatment
Receiving water linked to WWTP
Sludge treatment
Unclear
```

Allowed `evidence_tier` values:

```text
Tier 1
Tier 2
Tier 3
Unclear
```

Allowed `system_scale` values:

```text
Full-scale
Field-scale
Pilot-scale
Bench-scale
Lab-scale
Unclear
```

Allowed `wastewater_source_type` values:

```text
Municipal
Domestic
Hospital
Industrial
Agricultural
Livestock
Aquaculture
Mixed
Unclear
```

---

## 2. Treatment systems

Extract treatment-system records as a list. Each object should have:

```json
{
  "record_id": "",
  "system_id": "",
  "treatment_process": "",
  "treatment_train": "",
  "wwtp_type": "",
  "design_capacity": "",
  "hydraulic_retention_time": "",
  "solid_retention_time": "",
  "temperature": "",
  "pH": "",
  "disinfection_type": "",
  "advanced_treatment_type": "",
  "sludge_treatment_type": "",
  "operating_condition": "",
  "evidence_quote": "",
  "source_section": "",
  "confidence": 0.0
}
```

Relevant treatment processes include activated sludge, A2O, oxidation ditch, SBR, MBR, MBBR, constructed wetland, chlorination, UV, ozonation, advanced oxidation, membrane filtration, adsorption, biochar, photocatalysis, electrochemical treatment, anaerobic digestion, sludge composting, thermal hydrolysis, sludge dewatering, and hybrid process.

---

## 3. Sample matrices

Extract sample/matrix records as a list. Each object should have:

```json
{
  "record_id": "",
  "sample_id": "",
  "matrix": "",
  "sample_origin": "",
  "sampling_point": "",
  "sampling_time": "",
  "season": "",
  "influent_effluent_pair_id": "",
  "is_paired_sample": "",
  "paired_with_sample_id": "",
  "evidence_quote": "",
  "source_section": "",
  "confidence": 0.0
}
```

Allowed matrix values include influent, raw wastewater, primary effluent, activated sludge, mixed liquor, secondary effluent, final effluent, tertiary effluent, reclaimed water, waste activated sludge, sewage sludge, anaerobic sludge, digestate, biosolids, bioaerosol, receiving water upstream, receiving water downstream, other, unclear.

Allowed `is_paired_sample` values: `Yes`, `No`, `Unclear`.

Matrix-label provenance rule:
- Preserve the source matrix/stage/sample label verbatim in `sampling_point`, `sample_origin`, or the evidence quote before assigning a normalized `matrix` value.
- Do not collapse explicit source labels such as site codes, WWTP-specific stage labels, sludge-stage labels, legend-coded bar-chart groups, or pairwise labels into `other` when the paper provides a specific label.
- Use the normalized `matrix` field only as a controlled vocabulary value for downstream harmonization; the raw label must remain available for linkage validation and audit.
- For figures and tables, first enumerate all matrix/stage/condition labels, including legend colors and multi-row or multi-column headers, before extracting values.

---

## 4. ARG/MGE/resistome targets

Extract target records as a list. Each object should have:

```json
{
  "record_id": "",
  "target_id": "",
  "target_name": "",
  "target_type": "",
  "target_class": "",
  "detection_method": "",
  "normalization_method": "",
  "evidence_quote": "",
  "source_section": "",
  "confidence": 0.0
}
```

Allowed `target_type` values: `ARG`, `MGE`, `intI1_marker`, `resistome`, `ARB_marker`, `Other`, `Unclear`.

Priority targets include sul1, sul2, sul3, tetA, tetC, tetM, tetO, tetQ, tetW, tetX, ermB, ermF, blaTEM, blaCTX-M, blaOXA, blaNDM, qnrS, qnrA, qnrB, qepA, aac(6')-Ib-cr, mexF, acrB, macB, intI1, intI2, plasmid markers, transposase genes, integrons, transposons, phage markers.

Allowed detection methods include qPCR, ddPCR, metagenomics, HT-qPCR, SmartChip, microarray, culture-based plus genetic confirmation, other, unclear.

---

## 5. Quantitative measurements

Extract quantitative ARG/MGE/resistome measurements as a list. Each object should have:

```json
{
  "record_id": "",
  "measurement_id": "",
  "sample_id": "",
  "target_name": "",
  "target_type": "",
  "matrix": "",
  "treatment_process": "",
  "raw_value": null,
  "value_min": null,
  "value_max": null,
  "mean_value": null,
  "median_value": null,
  "sd": null,
  "se": null,
  "unit": "",
  "log_transformed": "",
  "normalization_method": "",
  "basis": "",
  "detection_method": "",
  "n_samples": "",
  "time_point": "",
  "before_after_status": "",
  "evidence_quote": "",
  "source_location": "",
  "confidence": 0.0
}
```

Rules:
- Preserve the original reported unit exactly.
- If values are ranges, use `value_min` and `value_max`.
- If values are means, use `mean_value`.
- Numeric value fields (`raw_value`, `value_min`, `value_max`, `mean_value`, `median_value`, `sd`, `se`) must contain only JSON numbers or `null`. Put verbal descriptions such as "approximately 2 orders of magnitude" in `interpretation`, `source_location`, or `extraction_notes`, not in numeric fields.
- If only qualitative detection is reported, do not invent quantitative values.
- If the value is only visible in a figure and not extractable from text, state this in `source_location` or extraction notes.

Allowed examples of units include copies/mL, copies/L, copies/g, copies/g dry weight, copies/m3, log copies/mL, log copies/g, relative abundance, relative abundance/16S, copies/16S rRNA gene, TPM, RPKM, FPKM, percent, log reduction, removal percent, not reported, unclear.

Allowed `before_after_status` values: before_treatment, after_treatment, influent, effluent, upstream, downstream, control, treated, unclear, not applicable.

---

## 6. Treatment outcomes

Extract treatment outcome records as a list. Each object should have:

```json
{
  "record_id": "",
  "outcome_id": "",
  "target_name": "",
  "matrix_before": "",
  "matrix_after": "",
  "treatment_process": "",
  "outcome_type": "",
  "reported_outcome_value": null,
  "reported_outcome_unit": "",
  "calculated_by_llm": "",
  "paired_data_status": "",
  "pairing_basis": "",
  "interpretation": "",
  "evidence_quote": "",
  "source_section": "",
  "confidence": 0.0
}
```

Allowed `outcome_type` values: removal_efficiency, log_reduction, reduction, persistence, enrichment, no_significant_change, occurrence_only, detection_non_detection, unclear.

Allowed `paired_data_status` values: valid_spatial_pair, valid_before_after_pair, valid_treatment_control_pair, temporal_pair_unclear, cross_study_comparison, unpaired, unclear.

Critical rules:
- Do not calculate outcome values from unpaired data.
- If the paper reports a removal value, extract the reported value and use `calculated_by_llm = "No"`.
- Use `calculated_by_llm = "Yes"` only when values are explicitly paired and the calculation is simple and transparent.
- If calculated, include calculation details in `interpretation`.
- If pairing is unclear, set `paired_data_status = "unclear"` and do not classify the outcome as `removal_efficiency`, `log_reduction`, or `reduction`. These three outcome types require a valid paired-data basis: `valid_spatial_pair`, `valid_before_after_pair`, `valid_treatment_control_pair`, `temporal_pair_unclear`, `cross_study_comparison`, or another explicitly supported pairing status that is not `unclear` or `unpaired`.

---

## 7. Candidate KG triples

Create candidate KG triples only when directly supported by evidence. Each object should have:

```json
{
  "record_id": "",
  "triple_id": "",
  "subject": "",
  "predicate": "",
  "object": "",
  "subject_type": "",
  "object_type": "",
  "polarity": "",
  "evidence_strength": "",
  "evidence_quote": "",
  "source_section": "",
  "confidence": 0.0,
  "human_validation_status": "pending"
}
```

Allowed predicates: detected_in, measured_in, reduced_by, removed_by, persists_after, enriched_after, associated_with, correlates_with, co_occurs_with, treated_by, sampled_from, derived_from, normalized_by, quantified_by, linked_to_effluent_discharge, supported_by_evidence.

Predicate vocabulary is closed. Use only the allowed predicates exactly as written. For example, use `reduced_by` instead of `reduces_by`; use `detected_in`, `measured_in`, or `associated_with` instead of `contains`.

Allowed `polarity` values: positive, negative, absence_like, unknown.

Allowed `evidence_strength` values: direct_measurement, reported_calculation, statistical_association, correlation, author_interpretation, inferred_uncertain.

Rules:
- Use `correlates_with` for correlations.
- Use `associated_with` for non-causal associations.
- Do not use causal wording unless the text directly supports causality.
- Every triple must include an evidence quote.

---

## 8. Extraction notes

Include an `extraction_notes` object:

```json
{
  "record_id": "",
  "text_quality": "",
  "main_missing_information": [],
  "human_audit_recommended": "",
  "audit_reasons": [],
  "general_note": ""
}
```

Allowed `text_quality` values: good, moderate, poor, unreadable.

Allowed `human_audit_recommended` values: Yes, No.

Recommend human audit when confidence is low, text quality is poor, quantitative measurements are extracted, removal/log reduction is extracted, paired data are unclear, KG triples are inferred_uncertain, non-municipal wastewater source is involved, synthetic wastewater status is unclear, or evidence quote is weak/ambiguous.

---

## Required output JSON structure

Return only a valid JSON object with this exact top-level structure:

```json
{
  "record_id": "",
  "study_metadata": {
    "record_id": "",
    "doi": "",
    "title": "",
    "authors": "",
    "first_author": "",
    "year": "",
    "journal": "",
    "country": "",
    "city_or_region": "",
    "study_type": "",
    "evidence_tier": "",
    "system_scale": "",
    "wastewater_source_type": "",
    "evidence_quote": "",
    "confidence": 0.0
  },
  "treatment_systems": [],
  "sample_matrices": [],
  "arg_targets": [],
  "measurements": [],
  "outcomes": [],
  "kg_triples": [],
  "extraction_notes": {
    "record_id": "",
    "text_quality": "",
    "main_missing_information": [],
    "human_audit_recommended": "",
    "audit_reasons": [],
    "general_note": ""
  }
}
```

---

## Final instruction

Extract only what is supported by the provided article text. Use evidence quotes for all important extracted items. Return only valid JSON. Do not add explanation outside the JSON.
