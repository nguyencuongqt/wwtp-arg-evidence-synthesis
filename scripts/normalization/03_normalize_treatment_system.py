#!/usr/bin/env python3
"""
03_normalize_treatment_system.py

Normalize treatment process names and assign treatment_group.

Reads:   05_data_extraction/final_extracted/final_treatment_system.csv
Saves:   06_data_normalization/normalized_tables/treatment_system_normalized.csv

Usage:
    python 03_normalize_treatment_system.py
    python 03_normalize_treatment_system.py --overwrite
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         normalize_column, save_output, setup_logging)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Normalize treatment system data.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted/final_treatment_system.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/treatment_system_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "03_normalize_treatment_system")

    logger.info("=" * 60)
    logger.info("03_normalize_treatment_system START")
    logger.info("=" * 60)

    output_path = Path(args.output).resolve()
    check_overwrite(output_path, args.overwrite, logger)

    df = load_input(Path(args.input).resolve(), logger)
    if df is None:
        sys.exit(1)

    dict_dir = Path(args.dict_dir).resolve()
    tp_map = load_dictionary(
        dict_dir / "treatment_process_dictionary.csv", "raw_term", logger
    )

    unmapped: list[str] = []

    if "treatment_process" in df.columns:
        df["raw_treatment_process"] = df["treatment_process"]
        df = normalize_column(
            df, "raw_treatment_process", "normalized_treatment_process",
            tp_map, "normalized_treatment_process", unmapped, logger
        )
        # Add treatment_group from dictionary
        df["treatment_group"] = df["raw_treatment_process"].apply(
            lambda v: tp_map.get(str(v).strip().lower(), {}).get("treatment_group", "unclear")
        )
    else:
        logger.warning("Column 'treatment_process' missing — skipping.")

    # Save unmapped
    if unmapped:
        import pandas as pd
        qa_dir = output_path.parent.parent / "qa_reports"
        qa_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"unmapped_term": list(set(unmapped)),
                      "source_table": "treatment_system",
                      "dictionary": "treatment_process_dictionary"}).to_csv(
            qa_dir / "unmapped_treatment_process.csv", index=False, encoding="utf-8-sig"
        )
        logger.info(f"Unmapped treatment process terms: {len(set(unmapped))}")

    save_output(df, output_path, logger)
    logger.info("03_normalize_treatment_system COMPLETE")


if __name__ == "__main__":
    main()
