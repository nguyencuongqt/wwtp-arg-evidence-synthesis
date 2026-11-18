#!/usr/bin/env python3
"""
01_create_default_dictionaries.py

Create or verify the default normalization dictionaries in dictionaries/.

Does NOT overwrite existing dictionaries unless --overwrite is passed.
Run this once to seed initial dictionaries, then edit them manually.

Usage:
    python 01_create_default_dictionaries.py
    python 01_create_default_dictionaries.py --overwrite
    python 01_create_default_dictionaries.py --dict-dir "../dictionaries"
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logging(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"01_create_dicts_{ts}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)


# ── Dictionary definitions ────────────────────────────────────────────────────

# Each dict: filename → (columns, list of row dicts)
DICT_SPECS: dict[str, tuple[list[str], list[dict]]] = {

    "arg_name_dictionary.csv": (
        ["raw_term", "normalized_arg_name", "arg_class", "target_type", "notes"],
        [
            {"raw_term": "sul1", "normalized_arg_name": "sul1", "arg_class": "sulfonamide resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "sulI", "normalized_arg_name": "sul1", "arg_class": "sulfonamide resistance", "target_type": "ARG", "notes": "Roman numeral variant"},
            {"raw_term": "sul2", "normalized_arg_name": "sul2", "arg_class": "sulfonamide resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "sul3", "normalized_arg_name": "sul3", "arg_class": "sulfonamide resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "tetA", "normalized_arg_name": "tetA", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "tet(A)", "normalized_arg_name": "tetA", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "parenthetical notation"},
            {"raw_term": "tetM", "normalized_arg_name": "tetM", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "tetO", "normalized_arg_name": "tetO", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "tetW", "normalized_arg_name": "tetW", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "tetX", "normalized_arg_name": "tetX", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "tetQ", "normalized_arg_name": "tetQ", "arg_class": "tetracycline resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "ermB", "normalized_arg_name": "ermB", "arg_class": "macrolide-lincosamide-streptogramin resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "ermF", "normalized_arg_name": "ermF", "arg_class": "macrolide-lincosamide-streptogramin resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "blaTEM", "normalized_arg_name": "blaTEM", "arg_class": "beta-lactam resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "blaCTX-M", "normalized_arg_name": "blaCTX-M", "arg_class": "beta-lactam resistance", "target_type": "ARG", "notes": "canonical ESBL"},
            {"raw_term": "blaOXA", "normalized_arg_name": "blaOXA", "arg_class": "beta-lactam resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "blaNDM", "normalized_arg_name": "blaNDM", "arg_class": "carbapenem/beta-lactam resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "blaKPC", "normalized_arg_name": "blaKPC", "arg_class": "carbapenem/beta-lactam resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "qnrS", "normalized_arg_name": "qnrS", "arg_class": "quinolone resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "qnrA", "normalized_arg_name": "qnrA", "arg_class": "quinolone resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "qnrB", "normalized_arg_name": "qnrB", "arg_class": "quinolone resistance", "target_type": "ARG", "notes": "canonical"},
            {"raw_term": "qepA", "normalized_arg_name": "qepA", "arg_class": "quinolone resistance", "target_type": "ARG", "notes": "efflux pump"},
            {"raw_term": "aac(6')-Ib-cr", "normalized_arg_name": "aac(6')-Ib-cr", "arg_class": "aminoglycoside/quinolone resistance", "target_type": "ARG", "notes": "bifunctional"},
            {"raw_term": "mcr-1", "normalized_arg_name": "mcr-1", "arg_class": "colistin resistance", "target_type": "ARG", "notes": "mobile colistin resistance"},
            {"raw_term": "mexF", "normalized_arg_name": "mexF", "arg_class": "multidrug resistance", "target_type": "ARG", "notes": "efflux pump"},
            {"raw_term": "acrB", "normalized_arg_name": "acrB", "arg_class": "multidrug resistance", "target_type": "ARG", "notes": "efflux pump"},
            {"raw_term": "macB", "normalized_arg_name": "macB", "arg_class": "macrolide resistance", "target_type": "ARG", "notes": "efflux pump"},
            {"raw_term": "intI1", "normalized_arg_name": "intI1", "arg_class": "mobile genetic element marker", "target_type": "intI1_marker", "notes": "class 1 integrase"},
            {"raw_term": "int1", "normalized_arg_name": "intI1", "arg_class": "mobile genetic element marker", "target_type": "intI1_marker", "notes": "spelling variant"},
            {"raw_term": "IntI1", "normalized_arg_name": "intI1", "arg_class": "mobile genetic element marker", "target_type": "intI1_marker", "notes": "capitalization variant"},
            {"raw_term": "intI2", "normalized_arg_name": "intI2", "arg_class": "mobile genetic element marker", "target_type": "MGE", "notes": "class 2 integrase"},
            {"raw_term": "resistome", "normalized_arg_name": "resistome", "arg_class": "resistome", "target_type": "resistome", "notes": "metagenomics resistome"},
            {"raw_term": "total ARG", "normalized_arg_name": "total ARG", "arg_class": "resistome", "target_type": "resistome", "notes": "aggregate ARG abundance"},
        ]
    ),

    "matrix_dictionary.csv": (
        ["raw_term", "normalized_matrix", "matrix_group", "notes"],
        [
            {"raw_term": "influent", "normalized_matrix": "influent", "matrix_group": "liquid_influent", "notes": "canonical"},
            {"raw_term": "raw wastewater", "normalized_matrix": "influent", "matrix_group": "liquid_influent", "notes": "synonym"},
            {"raw_term": "secondary effluent", "normalized_matrix": "secondary_effluent", "matrix_group": "liquid_effluent", "notes": "canonical"},
            {"raw_term": "final effluent", "normalized_matrix": "final_effluent", "matrix_group": "liquid_effluent", "notes": "canonical"},
            {"raw_term": "effluent", "normalized_matrix": "final_effluent", "matrix_group": "liquid_effluent", "notes": "ambiguous — assume final if no further info"},
            {"raw_term": "treated effluent", "normalized_matrix": "final_effluent", "matrix_group": "liquid_effluent", "notes": "generic post-treatment"},
            {"raw_term": "tertiary effluent", "normalized_matrix": "tertiary_effluent", "matrix_group": "liquid_effluent", "notes": "after tertiary treatment"},
            {"raw_term": "reclaimed water", "normalized_matrix": "reclaimed_water", "matrix_group": "liquid_reclaimed", "notes": "treated for reuse"},
            {"raw_term": "activated sludge", "normalized_matrix": "activated_sludge", "matrix_group": "sludge_mixed_liquor", "notes": "canonical"},
            {"raw_term": "mixed liquor", "normalized_matrix": "mixed_liquor", "matrix_group": "sludge_mixed_liquor", "notes": "canonical"},
            {"raw_term": "waste activated sludge", "normalized_matrix": "waste_activated_sludge", "matrix_group": "sludge_waste", "notes": "canonical — WAS"},
            {"raw_term": "WAS", "normalized_matrix": "waste_activated_sludge", "matrix_group": "sludge_waste", "notes": "abbreviation"},
            {"raw_term": "sewage sludge", "normalized_matrix": "sewage_sludge", "matrix_group": "sludge_processed", "notes": "canonical"},
            {"raw_term": "sludge", "normalized_matrix": "sewage_sludge", "matrix_group": "sludge_processed", "notes": "generic — assume sewage sludge in WWTP context"},
            {"raw_term": "anaerobic sludge", "normalized_matrix": "anaerobic_sludge", "matrix_group": "sludge_anaerobic", "notes": "canonical"},
            {"raw_term": "digestate", "normalized_matrix": "digestate", "matrix_group": "sludge_processed", "notes": "canonical"},
            {"raw_term": "biosolids", "normalized_matrix": "biosolids", "matrix_group": "sludge_processed", "notes": "canonical"},
            {"raw_term": "bioaerosol", "normalized_matrix": "bioaerosol", "matrix_group": "aerosol", "notes": "canonical"},
            {"raw_term": "receiving water upstream", "normalized_matrix": "receiving_water_upstream", "matrix_group": "receiving_water", "notes": "canonical"},
            {"raw_term": "receiving water downstream", "normalized_matrix": "receiving_water_downstream", "matrix_group": "receiving_water", "notes": "canonical"},
            {"raw_term": "surface water", "normalized_matrix": "receiving_water_downstream", "matrix_group": "receiving_water", "notes": "ambiguous — flag"},
            {"raw_term": "unclear", "normalized_matrix": "unclear", "matrix_group": "unclear", "notes": "cannot determine"},
        ]
    ),

    "treatment_process_dictionary.csv": (
        ["raw_term", "normalized_treatment_process", "treatment_group", "notes"],
        [
            {"raw_term": "activated sludge", "normalized_treatment_process": "activated_sludge", "treatment_group": "secondary_biological_treatment", "notes": "canonical"},
            {"raw_term": "CAS", "normalized_treatment_process": "activated_sludge", "treatment_group": "secondary_biological_treatment", "notes": "conventional activated sludge"},
            {"raw_term": "A2O", "normalized_treatment_process": "A2O", "treatment_group": "secondary_biological_treatment", "notes": "canonical"},
            {"raw_term": "oxidation ditch", "normalized_treatment_process": "oxidation_ditch", "treatment_group": "secondary_biological_treatment", "notes": "canonical"},
            {"raw_term": "SBR", "normalized_treatment_process": "SBR", "treatment_group": "secondary_biological_treatment", "notes": "canonical"},
            {"raw_term": "MBR", "normalized_treatment_process": "MBR", "treatment_group": "membrane_treatment", "notes": "canonical"},
            {"raw_term": "membrane bioreactor", "normalized_treatment_process": "MBR", "treatment_group": "membrane_treatment", "notes": "full description"},
            {"raw_term": "MBBR", "normalized_treatment_process": "MBBR", "treatment_group": "secondary_biological_treatment", "notes": "canonical"},
            {"raw_term": "constructed wetland", "normalized_treatment_process": "constructed_wetland", "treatment_group": "nature_based_treatment", "notes": "canonical"},
            {"raw_term": "CW", "normalized_treatment_process": "constructed_wetland", "treatment_group": "nature_based_treatment", "notes": "abbreviation"},
            {"raw_term": "chlorination", "normalized_treatment_process": "chlorination", "treatment_group": "tertiary_disinfection", "notes": "canonical"},
            {"raw_term": "UV", "normalized_treatment_process": "UV_disinfection", "treatment_group": "tertiary_disinfection", "notes": "canonical"},
            {"raw_term": "ozonation", "normalized_treatment_process": "ozonation", "treatment_group": "tertiary_disinfection", "notes": "canonical"},
            {"raw_term": "advanced oxidation", "normalized_treatment_process": "advanced_oxidation", "treatment_group": "advanced_oxidation", "notes": "AOP"},
            {"raw_term": "AOP", "normalized_treatment_process": "advanced_oxidation", "treatment_group": "advanced_oxidation", "notes": "abbreviation"},
            {"raw_term": "photocatalysis", "normalized_treatment_process": "photocatalysis", "treatment_group": "advanced_oxidation", "notes": "canonical"},
            {"raw_term": "nanofiltration", "normalized_treatment_process": "nanofiltration", "treatment_group": "membrane_treatment", "notes": "canonical"},
            {"raw_term": "NF", "normalized_treatment_process": "nanofiltration", "treatment_group": "membrane_treatment", "notes": "abbreviation"},
            {"raw_term": "reverse osmosis", "normalized_treatment_process": "reverse_osmosis", "treatment_group": "membrane_treatment", "notes": "canonical"},
            {"raw_term": "RO", "normalized_treatment_process": "reverse_osmosis", "treatment_group": "membrane_treatment", "notes": "abbreviation"},
            {"raw_term": "adsorption", "normalized_treatment_process": "adsorption", "treatment_group": "adsorption_treatment", "notes": "canonical"},
            {"raw_term": "biochar", "normalized_treatment_process": "biochar", "treatment_group": "adsorption_treatment", "notes": "canonical"},
            {"raw_term": "activated carbon", "normalized_treatment_process": "activated_carbon", "treatment_group": "adsorption_treatment", "notes": "canonical"},
            {"raw_term": "GAC", "normalized_treatment_process": "activated_carbon", "treatment_group": "adsorption_treatment", "notes": "granular activated carbon"},
            {"raw_term": "anaerobic digestion", "normalized_treatment_process": "anaerobic_digestion", "treatment_group": "anaerobic_digestion", "notes": "canonical"},
            {"raw_term": "AD", "normalized_treatment_process": "anaerobic_digestion", "treatment_group": "anaerobic_digestion", "notes": "abbreviation"},
            {"raw_term": "sludge composting", "normalized_treatment_process": "sludge_composting", "treatment_group": "sludge_treatment", "notes": "canonical"},
            {"raw_term": "thermal hydrolysis", "normalized_treatment_process": "thermal_hydrolysis", "treatment_group": "sludge_treatment", "notes": "canonical"},
            {"raw_term": "sludge dewatering", "normalized_treatment_process": "sludge_dewatering", "treatment_group": "sludge_treatment", "notes": "canonical"},
            {"raw_term": "unclear", "normalized_treatment_process": "unclear", "treatment_group": "unclear", "notes": "cannot determine"},
        ]
    ),

    "wastewater_source_dictionary.csv": (
        ["raw_term", "normalized_wastewater_source_type", "notes"],
        [
            {"raw_term": "municipal", "normalized_wastewater_source_type": "municipal", "notes": "canonical"},
            {"raw_term": "municipal wastewater", "normalized_wastewater_source_type": "municipal", "notes": "full phrase"},
            {"raw_term": "urban wastewater", "normalized_wastewater_source_type": "municipal", "notes": "synonym"},
            {"raw_term": "domestic", "normalized_wastewater_source_type": "domestic", "notes": "canonical"},
            {"raw_term": "domestic wastewater", "normalized_wastewater_source_type": "domestic", "notes": "full phrase"},
            {"raw_term": "hospital", "normalized_wastewater_source_type": "hospital", "notes": "canonical"},
            {"raw_term": "hospital wastewater", "normalized_wastewater_source_type": "hospital", "notes": "full phrase"},
            {"raw_term": "industrial", "normalized_wastewater_source_type": "industrial", "notes": "canonical"},
            {"raw_term": "industrial wastewater", "normalized_wastewater_source_type": "industrial", "notes": "full phrase"},
            {"raw_term": "agricultural", "normalized_wastewater_source_type": "agricultural", "notes": "canonical"},
            {"raw_term": "agricultural wastewater", "normalized_wastewater_source_type": "agricultural", "notes": "full phrase"},
            {"raw_term": "livestock", "normalized_wastewater_source_type": "livestock", "notes": "canonical"},
            {"raw_term": "animal husbandry", "normalized_wastewater_source_type": "livestock", "notes": "synonym"},
            {"raw_term": "swine", "normalized_wastewater_source_type": "livestock", "notes": "pig farming"},
            {"raw_term": "aquaculture", "normalized_wastewater_source_type": "aquaculture", "notes": "canonical"},
            {"raw_term": "fish farm", "normalized_wastewater_source_type": "aquaculture", "notes": "specific type"},
            {"raw_term": "mixed", "normalized_wastewater_source_type": "mixed", "notes": "canonical"},
            {"raw_term": "unclear", "normalized_wastewater_source_type": "unclear", "notes": "canonical"},
            {"raw_term": "unknown", "normalized_wastewater_source_type": "unclear", "notes": "not reported"},
            {"raw_term": "not reported", "normalized_wastewater_source_type": "unclear", "notes": "not reported"},
        ]
    ),

    "unit_dictionary.csv": (
        ["raw_unit", "normalized_unit", "unit_family", "convertible_to", "conversion_rule", "notes"],
        [
            {"raw_unit": "copies/mL", "normalized_unit": "copies_per_mL", "unit_family": "absolute_abundance_liquid", "convertible_to": "copies_per_L", "conversion_rule": "multiply by 1000", "notes": "most common liquid unit"},
            {"raw_unit": "copies/L", "normalized_unit": "copies_per_L", "unit_family": "absolute_abundance_liquid", "convertible_to": "copies_per_mL", "conversion_rule": "divide by 1000", "notes": "per liter"},
            {"raw_unit": "copies/m3", "normalized_unit": "copies_per_m3", "unit_family": "absolute_abundance_air", "convertible_to": "", "conversion_rule": "", "notes": "air/bioaerosol"},
            {"raw_unit": "copies/g", "normalized_unit": "copies_per_g", "unit_family": "absolute_abundance_solid", "convertible_to": "", "conversion_rule": "", "notes": "per gram — wet weight assumed unless stated"},
            {"raw_unit": "copies/g dry weight", "normalized_unit": "copies_per_g_dw", "unit_family": "absolute_abundance_solid", "convertible_to": "", "conversion_rule": "", "notes": "per gram dry weight — not interchangeable with ww"},
            {"raw_unit": "copies/g DW", "normalized_unit": "copies_per_g_dw", "unit_family": "absolute_abundance_solid", "convertible_to": "", "conversion_rule": "", "notes": "dry weight abbreviation"},
            {"raw_unit": "copies/g TS", "normalized_unit": "copies_per_g_ts", "unit_family": "absolute_abundance_solid", "convertible_to": "", "conversion_rule": "", "notes": "total solids basis"},
            {"raw_unit": "copies/g VS", "normalized_unit": "copies_per_g_vs", "unit_family": "absolute_abundance_solid", "convertible_to": "", "conversion_rule": "", "notes": "volatile solids basis"},
            {"raw_unit": "log copies/mL", "normalized_unit": "log_copies_per_mL", "unit_family": "log_abundance", "convertible_to": "", "conversion_rule": "", "notes": "log10-transformed"},
            {"raw_unit": "log copies/g", "normalized_unit": "log_copies_per_g", "unit_family": "log_abundance", "convertible_to": "", "conversion_rule": "", "notes": "log10-transformed solid"},
            {"raw_unit": "relative abundance", "normalized_unit": "relative_abundance", "unit_family": "relative_abundance_metagenomic", "convertible_to": "", "conversion_rule": "", "notes": "metagenomics"},
            {"raw_unit": "relative abundance/16S", "normalized_unit": "relative_abundance_16S", "unit_family": "relative_abundance_16S", "convertible_to": "", "conversion_rule": "", "notes": "normalized to 16S"},
            {"raw_unit": "copies/16S rRNA gene", "normalized_unit": "copies_per_16S", "unit_family": "relative_abundance_16S", "convertible_to": "", "conversion_rule": "", "notes": "per 16S copy"},
            {"raw_unit": "TPM", "normalized_unit": "TPM", "unit_family": "relative_abundance_metagenomic", "convertible_to": "", "conversion_rule": "", "notes": "transcripts per million"},
            {"raw_unit": "RPKM", "normalized_unit": "RPKM", "unit_family": "relative_abundance_metagenomic", "convertible_to": "", "conversion_rule": "", "notes": "reads per kilobase per million"},
            {"raw_unit": "removal percent", "normalized_unit": "percent_removal", "unit_family": "removal_percent", "convertible_to": "", "conversion_rule": "", "notes": "removal efficiency"},
            {"raw_unit": "% removal", "normalized_unit": "percent_removal", "unit_family": "removal_percent", "convertible_to": "", "conversion_rule": "", "notes": "abbreviation"},
            {"raw_unit": "log reduction", "normalized_unit": "log_reduction", "unit_family": "log_reduction", "convertible_to": "", "conversion_rule": "", "notes": "LRV"},
            {"raw_unit": "LRV", "normalized_unit": "log_reduction", "unit_family": "log_reduction", "convertible_to": "", "conversion_rule": "", "notes": "log reduction value"},
            {"raw_unit": "not reported", "normalized_unit": "not_reported", "unit_family": "unclear", "convertible_to": "", "conversion_rule": "", "notes": "unit not reported"},
            {"raw_unit": "unclear", "normalized_unit": "unclear", "unit_family": "unclear", "convertible_to": "", "conversion_rule": "", "notes": "cannot determine"},
        ]
    ),

    "outcome_dictionary.csv": (
        ["raw_outcome_type", "normalized_outcome_type", "outcome_group", "notes"],
        [
            {"raw_outcome_type": "removal_efficiency", "normalized_outcome_type": "removal_efficiency", "outcome_group": "quantitative_removal", "notes": "canonical"},
            {"raw_outcome_type": "removal efficiency", "normalized_outcome_type": "removal_efficiency", "outcome_group": "quantitative_removal", "notes": "space variant"},
            {"raw_outcome_type": "log_reduction", "normalized_outcome_type": "log_reduction", "outcome_group": "quantitative_removal", "notes": "canonical"},
            {"raw_outcome_type": "log reduction", "normalized_outcome_type": "log_reduction", "outcome_group": "quantitative_removal", "notes": "space variant"},
            {"raw_outcome_type": "reduction", "normalized_outcome_type": "reduction", "outcome_group": "quantitative_removal", "notes": "general reduction"},
            {"raw_outcome_type": "persistence", "normalized_outcome_type": "persistence", "outcome_group": "qualitative_outcome", "notes": "canonical"},
            {"raw_outcome_type": "enrichment", "normalized_outcome_type": "enrichment", "outcome_group": "qualitative_outcome", "notes": "canonical"},
            {"raw_outcome_type": "no_significant_change", "normalized_outcome_type": "no_significant_change", "outcome_group": "qualitative_outcome", "notes": "canonical"},
            {"raw_outcome_type": "no significant change", "normalized_outcome_type": "no_significant_change", "outcome_group": "qualitative_outcome", "notes": "space variant"},
            {"raw_outcome_type": "occurrence_only", "normalized_outcome_type": "occurrence_only", "outcome_group": "occurrence", "notes": "canonical"},
            {"raw_outcome_type": "occurrence only", "normalized_outcome_type": "occurrence_only", "outcome_group": "occurrence", "notes": "space variant"},
            {"raw_outcome_type": "detection_non_detection", "normalized_outcome_type": "detection_non_detection", "outcome_group": "occurrence", "notes": "canonical"},
            {"raw_outcome_type": "unclear", "normalized_outcome_type": "unclear", "outcome_group": "unclear", "notes": "canonical"},
        ]
    ),

    "predicate_dictionary.csv": (
        ["raw_predicate", "normalized_predicate", "relation_group", "allowed_evidence_strength", "notes"],
        [
            {"raw_predicate": "detected_in", "normalized_predicate": "detected_in", "relation_group": "occurrence", "allowed_evidence_strength": "direct_measurement|statistical_association", "notes": "canonical"},
            {"raw_predicate": "measured_in", "normalized_predicate": "measured_in", "relation_group": "quantification", "allowed_evidence_strength": "direct_measurement", "notes": "canonical"},
            {"raw_predicate": "reduced_by", "normalized_predicate": "reduced_by", "relation_group": "treatment_outcome", "allowed_evidence_strength": "direct_measurement|reported_calculation", "notes": "canonical"},
            {"raw_predicate": "removed_by", "normalized_predicate": "removed_by", "relation_group": "treatment_outcome", "allowed_evidence_strength": "direct_measurement|reported_calculation", "notes": "canonical"},
            {"raw_predicate": "persists_after", "normalized_predicate": "persists_after", "relation_group": "treatment_outcome", "allowed_evidence_strength": "direct_measurement|reported_calculation", "notes": "canonical"},
            {"raw_predicate": "enriched_after", "normalized_predicate": "enriched_after", "relation_group": "treatment_outcome", "allowed_evidence_strength": "direct_measurement|reported_calculation", "notes": "canonical"},
            {"raw_predicate": "associated_with", "normalized_predicate": "associated_with", "relation_group": "association", "allowed_evidence_strength": "statistical_association|correlation|author_interpretation", "notes": "canonical"},
            {"raw_predicate": "correlates_with", "normalized_predicate": "correlates_with", "relation_group": "association", "allowed_evidence_strength": "correlation|statistical_association", "notes": "canonical"},
            {"raw_predicate": "co_occurs_with", "normalized_predicate": "co_occurs_with", "relation_group": "co_occurrence", "allowed_evidence_strength": "direct_measurement|statistical_association", "notes": "canonical"},
            {"raw_predicate": "treated_by", "normalized_predicate": "treated_by", "relation_group": "treatment_process", "allowed_evidence_strength": "direct_measurement", "notes": "canonical"},
            {"raw_predicate": "sampled_from", "normalized_predicate": "sampled_from", "relation_group": "sampling", "allowed_evidence_strength": "direct_measurement", "notes": "canonical"},
            {"raw_predicate": "derived_from", "normalized_predicate": "derived_from", "relation_group": "provenance", "allowed_evidence_strength": "direct_measurement", "notes": "canonical"},
            {"raw_predicate": "normalized_by", "normalized_predicate": "normalized_by", "relation_group": "normalization", "allowed_evidence_strength": "direct_measurement", "notes": "canonical"},
            {"raw_predicate": "quantified_by", "normalized_predicate": "quantified_by", "relation_group": "method", "allowed_evidence_strength": "direct_measurement", "notes": "canonical"},
            {"raw_predicate": "linked_to_effluent_discharge", "normalized_predicate": "linked_to_effluent_discharge", "relation_group": "environmental_link", "allowed_evidence_strength": "direct_measurement|statistical_association", "notes": "canonical"},
            {"raw_predicate": "supported_by_evidence", "normalized_predicate": "supported_by_evidence", "relation_group": "evidence", "allowed_evidence_strength": "direct_measurement|reported_calculation", "notes": "use sparingly"},
        ]
    ),
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create default normalization dictionaries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dict-dir", default="../dictionaries",
                        help="Directory to write dictionary CSVs.")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing dictionary files.")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir)

    logger.info("=" * 60)
    logger.info("01_create_default_dictionaries START")
    logger.info("=" * 60)

    dict_dir = Path(args.dict_dir).resolve()
    dict_dir.mkdir(parents=True, exist_ok=True)

    n_created = n_skipped = 0

    for filename, (columns, rows) in DICT_SPECS.items():
        path = dict_dir / filename
        if path.exists() and not args.overwrite:
            logger.info(f"  [SKIP] {filename} — already exists. Use --overwrite to replace.")
            n_skipped += 1
            continue
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        logger.info(f"  [OK]   {filename} ({len(df)} entries)")
        n_created += 1

    logger.info("-" * 40)
    logger.info(f"Created : {n_created}")
    logger.info(f"Skipped : {n_skipped}")
    logger.info(f"Dict dir: {dict_dir}")
    logger.info("=" * 60)
    logger.info("01_create_default_dictionaries COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
