#!/usr/bin/env python3
"""
06_normalize_measurements.py

Normalize ARG measurement data: target names, matrix, treatment process,
units, and unit families. Apply simple within-family unit conversions only.

Keeps raw values alongside normalized values.
Creates unit_compatibility_report.csv.

Reads:   05_data_extraction/final_extracted_human_audited_20260616/final_v3_20260624_id_normalized/final_arg_measurements_v3_id_normalized_matrixlabel_backfilled_20260624.csv
Saves:   06_data_normalization/normalized_tables/arg_measurements_normalized.csv
         06_data_normalization/qa_reports/unit_compatibility_report.csv

Usage:
    python 06_normalize_measurements.py
    python 06_normalize_measurements.py --overwrite
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         add_processing_stream, add_target_scope_columns,
                         add_measurement_matrix_context,
                         add_detection_status_columns,
                         infer_legacy_value_scope,
                         normalize_column,
                         normalize_unit_column, save_output, setup_logging)

# ── Allowed simple unit conversions (within same family) ─────────────────────
# (from_normalized_unit, to_normalized_unit): (multiply_factor, note)
UNIT_CONVERSIONS: dict[tuple[str, str], tuple[float, str]] = {
    ("copies_per_mL", "copies_per_L"): (1000.0, "copies/mL × 1000 → copies/L"),
    ("copies_per_L", "copies_per_mL"): (1e-3, "copies/L ÷ 1000 → copies/mL"),
}

# Target unit for within-family standardization of liquid abundance
LIQUID_STANDARD_UNIT = "copies_per_mL"


def normalize_numeric_value(val: str) -> float | None:
    """Try to parse a string as float; return None on failure."""
    try:
        return float(str(val).strip().replace(",", ""))
    except (ValueError, TypeError):
        return None


def apply_unit_conversion(
    raw_value: float | None, raw_unit: str, norm_unit: str
) -> tuple[float | None, str, str, str]:
    """
    Return (normalized_value, normalized_unit_out, conversion_applied, conversion_note).
    Only converts copies/L ↔ copies/mL. All other units pass through unchanged.
    """
    if raw_value is None:
        return None, norm_unit, "No", ""

    key = (norm_unit, LIQUID_STANDARD_UNIT)
    if key in UNIT_CONVERSIONS and norm_unit != LIQUID_STANDARD_UNIT:
        factor, note = UNIT_CONVERSIONS[key]
        return raw_value * factor, LIQUID_STANDARD_UNIT, "Yes", note

    return raw_value, norm_unit, "No", ""


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Normalize ARG measurement data.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted_human_audited_20260616/final_v3_20260624_id_normalized/final_arg_measurements_v3_id_normalized_matrixlabel_backfilled_20260624.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/arg_measurements_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "06_normalize_measurements")

    logger.info("=" * 60)
    logger.info("06_normalize_measurements START")
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

    unmapped_all: list[str] = []

    # Target name
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

    # Matrix
    if "matrix" in df.columns:
        df["raw_matrix"] = df["matrix"]
        df = normalize_column(df, "raw_matrix", "normalized_matrix",
                              mat_map, "normalized_matrix", unmapped_all, logger)
        df["matrix_group"] = df["raw_matrix"].apply(
            lambda v: mat_map.get(str(v).strip().lower(), {}).get("matrix_group", "unclear")
        )
        df = add_measurement_matrix_context(df, mat_map)

    # Treatment process
    if "treatment_process" in df.columns:
        df["raw_treatment_process"] = df["treatment_process"]
        df = normalize_column(df, "raw_treatment_process", "normalized_treatment_process",
                              tp_map, "normalized_treatment_process", unmapped_all, logger)
        df["treatment_group"] = df["raw_treatment_process"].apply(
            lambda v: tp_map.get(str(v).strip().lower(), {}).get("treatment_group", "unclear")
        )

    # Unit normalization
    unit_compat_rows: list[dict] = []
    if "unit" in df.columns:
        df["raw_unit"] = df["unit"]
        df = normalize_unit_column(df, "raw_unit", "normalized_unit",
                                   unit_map, "normalized_unit", unmapped_all,
                                   logger, context="measurement")
        df["unit_family"] = df["raw_unit_pre_normalized"].apply(
            lambda v: unit_map.get(str(v).strip().lower(), {}).get("unit_family", "unclear")
        )

        # Apply simple liquid unit conversion
        norm_values, conv_applied, conv_notes, final_units = [], [], [], []
        for _, row in df.iterrows():
            raw_val = None
            for vc in ["raw_value", "mean_value", "median_value"]:
                if vc in row and str(row[vc]).strip() not in ("", "nan", "None"):
                    raw_val = normalize_numeric_value(str(row[vc]))
                    if raw_val is not None:
                        break

            if str(row.get("raw_unit_pre_normalization_note", "")).strip():
                norm_val = raw_val
                final_unit = str(row.get("normalized_unit", ""))
                conv = "No"
                note = "unit name pre-normalized only; numeric value not converted"
            else:
                norm_val, final_unit, conv, note = apply_unit_conversion(
                    raw_val, str(row.get("raw_unit", "")), str(row.get("normalized_unit", ""))
                )
            norm_values.append(norm_val)
            conv_applied.append(conv)
            conv_notes.append(note)
            final_units.append(final_unit)
            unit_route = str(row.get("raw_unit_pre_normalization_route", "")).strip()
            numeric_status = (
                "needs_multiplier_scale_handling"
                if unit_route == "unit_contains_multiplier"
                else "not_flagged_for_multiplier_handling"
            )
            synthesis_eligible = "No" if unit_route == "unit_contains_multiplier" else "Not_assessed"
            synthesis_exclusion = (
                "unit contains multiplier/scale (x10^n, ×10^n, or 10^-n); "
                "numeric multiplier must be applied before synthesis"
                if unit_route == "unit_contains_multiplier"
                else ""
            )

            unit_compat_rows.append({
                "record_id": row.get("record_id", ""),
                "measurement_id": row.get("measurement_id", ""),
                "target_name": row.get("target_name", ""),
                "raw_unit": row.get("raw_unit", ""),
                "raw_unit_pre_normalized": row.get("raw_unit_pre_normalized", ""),
                "raw_unit_pre_normalization_note": row.get("raw_unit_pre_normalization_note", ""),
                "raw_unit_pre_normalization_route": row.get("raw_unit_pre_normalization_route", ""),
                "normalized_unit": row.get("normalized_unit", ""),
                "unit_family": row.get("unit_family", ""),
                "conversion_applied": conv,
                "conversion_note": note,
                "numeric_handling_status": numeric_status,
                "quantitative_synthesis_eligible": synthesis_eligible,
                "quantitative_synthesis_exclusion_reason": synthesis_exclusion,
            })

        df["normalized_value"] = norm_values
        df["conversion_applied"] = conv_applied
        df["conversion_note"] = conv_notes
        df["final_unit"] = final_units
        df["numeric_handling_status"] = df["raw_unit_pre_normalization_route"].apply(
            lambda v: "needs_multiplier_scale_handling"
            if str(v).strip() == "unit_contains_multiplier"
            else "not_flagged_for_multiplier_handling"
        )
        df["quantitative_synthesis_eligible"] = df["raw_unit_pre_normalization_route"].apply(
            lambda v: "No" if str(v).strip() == "unit_contains_multiplier" else "Not_assessed"
        )
        df["quantitative_synthesis_exclusion_reason"] = df["raw_unit_pre_normalization_route"].apply(
            lambda v: (
                "unit contains multiplier/scale (x10^n, ×10^n, or 10^-n); "
                "numeric multiplier must be applied before synthesis"
            )
            if str(v).strip() == "unit_contains_multiplier"
            else ""
        )
    else:
        logger.warning("Column 'unit' missing — skipping unit normalization.")

    df = add_detection_status_columns(df)

    # Save unit compatibility report
    qa_dir = output_path.parent.parent / "qa_reports"
    qa_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(unit_compat_rows).to_csv(
        qa_dir / "unit_compatibility_report.csv", index=False, encoding="utf-8-sig"
    )
    logger.info(f"Unit compatibility report: {len(unit_compat_rows)} rows")

    # Save unmapped
    if unmapped_all:
        pd.DataFrame({"unmapped_term": list(set(unmapped_all)),
                      "source_table": "arg_measurements",
                      "dictionary": "multiple"}).to_csv(
            qa_dir / "unmapped_measurements.csv", index=False, encoding="utf-8-sig"
        )
        logger.info(f"Unmapped terms: {len(set(unmapped_all))}")

    df = infer_legacy_value_scope(df)
    df = add_processing_stream(df)
    save_output(df, output_path, logger)
    logger.info("06_normalize_measurements COMPLETE")


if __name__ == "__main__":
    main()
