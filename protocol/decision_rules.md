# General Decision Rulebook

## Purpose
This file records project-wide rules for screening, extraction, normalization, KG construction, and ML-readiness decisions.

## Rule 1 — Scope priority
The project scope document (eligibility criteria summarized in the manuscript Methods and Text S2) has the highest priority.

## Rule 2 — Conservative screening
If title/abstract evidence is insufficient but potentially relevant, classify as `Maybe`, not `Exclude`.

## Rule 3 — Do not exclude solely by wastewater source
Hospital, industrial, agricultural, livestock, aquaculture, and mixed wastewater studies are not automatically excluded if they use real wastewater/sludge and evaluate ARG/resistome/MGE fate/removal in a treatment context.

## Rule 4 — Exclude synthetic-only studies
Synthetic/artificial wastewater-only studies are excluded unless they also use real WWTP-derived or other real wastewater/sludge matrices.

## Rule 5 — Separate evidence tiers
Tier 1 and Tier 2 evidence must be retained separately. Do not pool full-scale and lab/pilot evidence without stratification.

## Rule 6 — No unsupported LLM labels
LLM-generated decisions, labels, and triples are provisional until validated by rule-based checks and/or human audit.

## Rule 7 — Unit separation
Absolute abundance, relative abundance, normalized abundance, detection status, removal percentage, and log reduction are separate outcome types.

## Rule 8 — Paired-data rule
Calculate removal percentage or log reduction only when before/after values are comparable and paired by system, matrix, target, unit, and sampling/experimental condition.

## Rule 9 — Triple provenance
Every KG triple must include DOI or stable source ID, evidence span/table/figure, extraction method, confidence, and validation status.

## Rule 10 — ML labels
ML labels must be derived only from validated extracted data. Do not use raw LLM-inferred labels for training.

## Rule 11 — Spiked real wastewater/sludge studies
Studies that use a real wastewater or sludge matrix as the base (e.g., real activated sludge, real WWTP effluent, real municipal wastewater) but add exogenous substances such as antibiotics, microplastics, disinfectants, nanoparticles, or other stressors to evaluate ARG response are classified as **Include_Supporting (Tier 2)**.

The addition of spiked substances does not change the base matrix classification and does not trigger `E11_Synthetic_only`. Set `synthetic_wastewater_flag = No` when the base matrix is confirmed real, even if substances are added.

At the human audit stage, record the spike in `auditor_notes` using this format:
> "Real [matrix] base; spiked with [substance] at [concentration]. Flag for sensitivity analysis at synthesis stage if concentrations are above environmental range."

At the synthesis stage, spiked Tier 2 studies should be analyzed separately from naturalistic Tier 2 studies when spike concentrations exceed environmentally relevant ranges, or when the research question requires ecological representativeness.
