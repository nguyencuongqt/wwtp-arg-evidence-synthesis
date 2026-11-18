#!/usr/bin/env python3
"""
05_normalize_arg_targets.py

Normalize ARG/MGE target names, ARG class, and target_type.

Reads:   05_data_extraction/final_extracted/final_arg_targets.csv
Saves:   06_data_normalization/normalized_tables/arg_targets_normalized.csv

Usage:
    python 05_normalize_arg_targets.py
    python 05_normalize_arg_targets.py --overwrite
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         add_target_scope_columns, normalize_column,
                         save_output, setup_logging)

VALID_TARGET_TYPE = {
    "ARG", "MGE", "intI1_marker", "resistome", "ARB_marker", "Other", "Unclear"
}

VALID_DETECTION_METHOD = {
    "qPCR", "ddPCR", "metagenomics", "HT-qPCR", "SmartChip",
    "microarray", "culture-based plus genetic confirmation", "other", "unclear"
}


def normalize_target_type(raw: str, arg_map: dict) -> str:
    v = str(raw).strip()
    if v in VALID_TARGET_TYPE:
        return v
    row = arg_map.get(v.lower(), {})
    tt = row.get("target_type", "")
    return tt if tt in VALID_TARGET_TYPE else v or "Unclear"


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Normalize ARG/MGE target data.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted/final_arg_targets.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/arg_targets_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "05_normalize_arg_targets")

    logger.info("=" * 60)
    logger.info("05_normalize_arg_targets START")
    logger.info("=" * 60)

    output_path = Path(args.output).resolve()
    check_overwrite(output_path, args.overwrite, logger)

    df = load_input(Path(args.input).resolve(), logger)
    if df is None:
        sys.exit(1)

    dict_dir = Path(args.dict_dir).resolve()
    arg_map = load_dictionary(dict_dir / "arg_name_dictionary.csv", "raw_term", logger)

    unmapped: list[str] = []

    # Normalize target_name
    if "target_name" in df.columns:
        df["raw_target_name"] = df["target_name"]
        df = normalize_column(
            df, "raw_target_name", "normalized_target_name",
            arg_map, "normalized_arg_name", unmapped, logger
        )
        # Pull arg_class from dictionary
        df["normalized_arg_class"] = df["raw_target_name"].apply(
            lambda v: arg_map.get(str(v).strip().lower(), {}).get("arg_class", "")
        )
        # Normalize target_type
        if "target_type" in df.columns:
            df["raw_target_type"] = df["target_type"]
            df["normalized_target_type"] = df["raw_target_name"].apply(
                lambda v: normalize_target_type(v, arg_map)
            )
        else:
            df["normalized_target_type"] = df["raw_target_name"].apply(
                lambda v: arg_map.get(str(v).strip().lower(), {}).get("target_type", "Unclear")
            )
        df = add_target_scope_columns(df)
    else:
        logger.warning("Column 'target_name' missing — skipping.")

    # Save unmapped
    if unmapped:
        import pandas as pd
        qa_dir = output_path.parent.parent / "qa_reports"
        qa_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"unmapped_term": list(set(unmapped)),
                      "source_table": "arg_targets",
                      "dictionary": "arg_name_dictionary"}).to_csv(
            qa_dir / "unmapped_arg_targets.csv", index=False, encoding="utf-8-sig"
        )
        logger.info(f"Unmapped ARG target terms: {len(set(unmapped))}")

    save_output(df, output_path, logger)
    logger.info("05_normalize_arg_targets COMPLETE")


if __name__ == "__main__":
    main()
