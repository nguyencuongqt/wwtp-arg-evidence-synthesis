#!/usr/bin/env python3
"""
07_normalize_outcomes.py

Normalize outcome data: target_name, matrix_before/after, treatment_process,
outcome_type, reported_outcome_unit, and paired_data_status.
Generates quality flags for removal synthesis eligibility.

Reads:   05_data_extraction/final_extracted_human_audited_20260616/final_v3_20260624_id_normalized/final_outcomes_v3_id_normalized_pairing_cleaned_matrixlabel_backfilled_20260624.csv
Saves:   06_data_normalization/normalized_tables/outcomes_normalized.csv

Usage:
    python 07_normalize_outcomes.py
    python 07_normalize_outcomes.py --overwrite
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         add_directional_change_resolution, add_processing_stream,
                         add_log_reduction_harmonization,
                         add_matrix_transition_type, add_outcome_matrix_context,
                         add_target_scope_columns,
                         infer_legacy_outcome_value_scope,
                         normalize_column,
                         normalize_unit_column, save_output, setup_logging)

# ── Valid controlled vocabularies ──────────────────────────────────────────────

VALID_PAIRED_STATUS = {
    "valid_spatial_pair",
    "valid_before_after_pair",
    "valid_treatment_control_pair",
    "temporal_pair_unclear",
    "cross_study_comparison",
    "unpaired",
    "unclear",
}

# Outcome types that should have valid pairing
REMOVAL_OUTCOME_TYPES = {"removal_efficiency", "log_reduction", "reduction"}

# Outcome types that are valid for removal synthesis
SYNTHESIS_ELIGIBLE_TYPES = {"removal_efficiency", "log_reduction", "reduction"}

# Pairing statuses that support removal synthesis
VALID_PAIRING_FOR_SYNTHESIS = {
    "valid_spatial_pair",
    "valid_before_after_pair",
    "valid_treatment_control_pair",
}


def normalize_paired_status(raw: str) -> tuple[str, str]:
    """Return (normalized_status, was_mapped)."""
    v = str(raw).strip()
    if v in VALID_PAIRED_STATUS:
        return v, "Yes"
    v_lower = v.lower()
    for valid in VALID_PAIRED_STATUS:
        if v_lower == valid.lower():
            return valid, "Yes"
    return v if v else "unclear", "No"


def compute_outcome_flags(
    normalized_outcome_type: str,
    normalized_paired_status: str,
    reported_by_author: str,
) -> tuple[str, str, str]:
    """
    Return (valid_for_removal_synthesis, pairing_quality_flag, needs_human_check).
    """
    is_removal_type = normalized_outcome_type in SYNTHESIS_ELIGIBLE_TYPES
    has_valid_pairing = normalized_paired_status in VALID_PAIRING_FOR_SYNTHESIS
    is_cross_study = normalized_paired_status == "cross_study_comparison"

    # Valid for removal synthesis: correct type + valid spatial/temporal pairing + not cross-study
    if is_removal_type and has_valid_pairing and not is_cross_study:
        valid = "Yes"
    elif is_removal_type and reported_by_author == "Yes":
        # Author-reported removals are flagged but kept
        valid = "Yes_author_reported"
    else:
        valid = "No"

    # Pairing quality flag
    if is_removal_type and normalized_paired_status in ("unclear", "unpaired", "temporal_pair_unclear"):
        pairing_flag = "needs_human_check"
    elif is_cross_study:
        pairing_flag = "not_valid_for_removal_calculation"
    else:
        pairing_flag = "ok"

    # needs_human_check
    if pairing_flag == "needs_human_check" or normalized_outcome_type == "unclear":
        needs_check = "Yes"
    else:
        needs_check = "No"

    return valid, pairing_flag, needs_check


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Normalize outcome data.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted_human_audited_20260616/final_v3_20260624_id_normalized/final_outcomes_v3_id_normalized_pairing_cleaned_matrixlabel_backfilled_20260624.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/outcomes_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "07_normalize_outcomes")

    logger.info("=" * 60)
    logger.info("07_normalize_outcomes START")
    logger.info("=" * 60)

    output_path = Path(args.output).resolve()
    check_overwrite(output_path, args.overwrite, logger)

    df = load_input(Path(args.input).resolve(), logger)
    if df is None:
        sys.exit(1)

    dict_dir = Path(args.dict_dir).resolve()
    arg_map = load_dictionary(dict_dir / "arg_name_dictionary.csv", "raw_term", logger)
    mat_map = load_dictionary(dict_dir / "matrix_dictionary.csv", "raw_term", logger)
    tp_map = load_dictionary(dict_dir / "treatment_process_dictionary.csv", "raw_term", logger)
    unit_map = load_dictionary(dict_dir / "unit_dictionary.csv", "raw_unit", logger)
    outcome_map = load_dictionary(dict_dir / "outcome_dictionary.csv", "raw_outcome_type", logger)

    unmapped_all: list[str] = []

    # Normalize target_name
    if "target_name" in df.columns:
        df["raw_target_name"] = df["target_name"]
        df = normalize_column(df, "raw_target_name", "normalized_target_name",
                              arg_map, "normalized_arg_name", unmapped_all, logger)
        df["normalized_arg_class"] = df["raw_target_name"].apply(
            lambda v: arg_map.get(str(v).strip().lower(), {}).get("arg_class", "")
        )
        df["normalized_target_type"] = df["raw_target_name"].apply(
            lambda v: arg_map.get(str(v).strip().lower(), {}).get("target_type", "Unclear")
        )
        df = add_target_scope_columns(df)

    # Normalize matrix_before
    if "matrix_before" in df.columns:
        df["raw_matrix_before"] = df["matrix_before"]
        df = normalize_column(df, "raw_matrix_before", "normalized_matrix_before",
                              mat_map, "normalized_matrix", unmapped_all, logger)
        df["matrix_before_group"] = df["raw_matrix_before"].apply(
            lambda v: mat_map.get(str(v).strip().lower(), {}).get("matrix_group", "unclear")
        )

    # Normalize matrix_after
    if "matrix_after" in df.columns:
        df["raw_matrix_after"] = df["matrix_after"]
        df = normalize_column(df, "raw_matrix_after", "normalized_matrix_after",
                              mat_map, "normalized_matrix", unmapped_all, logger)
        df["matrix_after_group"] = df["raw_matrix_after"].apply(
            lambda v: mat_map.get(str(v).strip().lower(), {}).get("matrix_group", "unclear")
        )
        df = add_outcome_matrix_context(df, mat_map)

    # Normalize treatment_process
    if "treatment_process" in df.columns:
        df["raw_treatment_process"] = df["treatment_process"]
        df = normalize_column(df, "raw_treatment_process", "normalized_treatment_process",
                              tp_map, "normalized_treatment_process", unmapped_all, logger)
        df["treatment_group"] = df["raw_treatment_process"].apply(
            lambda v: tp_map.get(str(v).strip().lower(), {}).get("treatment_group", "unclear")
        )

    if "matrix_before" in df.columns and "matrix_after" in df.columns:
        df = add_matrix_transition_type(df, mat_map)

    # Normalize outcome_type
    if "outcome_type" in df.columns:
        df["raw_outcome_type"] = df["outcome_type"]
        df = normalize_column(df, "raw_outcome_type", "normalized_outcome_type",
                              outcome_map, "normalized_outcome_type", unmapped_all, logger)
        df["outcome_group"] = df["raw_outcome_type"].apply(
            lambda v: outcome_map.get(str(v).strip().lower(), {}).get("outcome_group", "unclear")
        )

    # Normalize reported_outcome_unit
    if "reported_outcome_unit" in df.columns:
        df["raw_reported_outcome_unit"] = df["reported_outcome_unit"]
        df = normalize_unit_column(df, "raw_reported_outcome_unit", "normalized_outcome_unit",
                                   unit_map, "normalized_unit", unmapped_all,
                                   logger, context="outcome")
        df["outcome_unit_family"] = df["raw_reported_outcome_unit_pre_normalized"].apply(
            lambda v: unit_map.get(str(v).strip().lower(), {}).get("unit_family", "unclear")
        )

    df = add_log_reduction_harmonization(df)

    # Normalize paired_data_status
    if "paired_data_status" in df.columns:
        df["raw_paired_data_status"] = df["paired_data_status"]
        norm_statuses, status_mapped = [], []
        for raw in df["raw_paired_data_status"]:
            norm, mapped = normalize_paired_status(str(raw))
            norm_statuses.append(norm)
            status_mapped.append("Yes" if mapped else "No")
            if not mapped and str(raw).strip() not in ("", "unclear"):
                unmapped_all.append(str(raw).strip())
        df["normalized_paired_data_status"] = norm_statuses
        df["normalized_paired_data_status_mapped"] = status_mapped
    else:
        df["normalized_paired_data_status"] = "unclear"
        df["normalized_paired_data_status_mapped"] = "No"
        logger.warning("Column 'paired_data_status' missing — defaulting to 'unclear'.")

    # reported_by_author column (preserve or default)
    if "reported_by_author" not in df.columns:
        df["reported_by_author"] = ""

    # Compute outcome quality flags
    valid_list, flag_list, check_list = [], [], []
    for _, row in df.iterrows():
        norm_ot = str(row.get("normalized_outcome_type", "")).strip()
        norm_ps = str(row.get("normalized_paired_data_status", "unclear")).strip()
        rep_by_auth = str(row.get("reported_by_author", "")).strip()
        valid, flag, check = compute_outcome_flags(norm_ot, norm_ps, rep_by_auth)
        valid_list.append(valid)
        flag_list.append(flag)
        check_list.append(check)

    df["valid_for_removal_synthesis"] = valid_list
    df["pairing_quality_flag"] = flag_list
    df["needs_human_check"] = check_list

    # Summary stats
    n_valid = sum(1 for v in valid_list if v.startswith("Yes"))
    n_check = check_list.count("Yes")
    logger.info(f"Valid for removal synthesis: {n_valid}/{len(df)}")
    logger.info(f"Needs human check: {n_check}/{len(df)}")

    # Save unmapped terms
    if unmapped_all:
        qa_dir = output_path.parent.parent / "qa_reports"
        qa_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({
            "unmapped_term": list(set(unmapped_all)),
            "source_table": "outcomes",
            "dictionary": "multiple",
        }).to_csv(qa_dir / "unmapped_outcomes.csv", index=False, encoding="utf-8-sig")
        logger.info(f"Unmapped terms: {len(set(unmapped_all))}")

    df = infer_legacy_outcome_value_scope(df)
    df = add_processing_stream(df)
    df = add_directional_change_resolution(df)
    save_output(df, output_path, logger)
    logger.info("07_normalize_outcomes COMPLETE")


if __name__ == "__main__":
    main()
