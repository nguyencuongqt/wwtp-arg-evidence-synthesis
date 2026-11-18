#!/usr/bin/env python3
"""
04_normalize_sample_matrix.py

Normalize sample matrix terms to controlled vocabulary.

Reads:   05_data_extraction/final_extracted/final_sample_matrix.csv
Saves:   06_data_normalization/normalized_tables/sample_matrix_normalized.csv

Usage:
    python 04_normalize_sample_matrix.py
    python 04_normalize_sample_matrix.py --overwrite
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         normalize_column, save_output, setup_logging)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Normalize sample matrix data.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted/final_sample_matrix.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/sample_matrix_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "04_normalize_sample_matrix")

    logger.info("=" * 60)
    logger.info("04_normalize_sample_matrix START")
    logger.info("=" * 60)

    output_path = Path(args.output).resolve()
    check_overwrite(output_path, args.overwrite, logger)

    df = load_input(Path(args.input).resolve(), logger)
    if df is None:
        sys.exit(1)

    dict_dir = Path(args.dict_dir).resolve()
    mat_map = load_dictionary(dict_dir / "matrix_dictionary.csv", "raw_term", logger)

    unmapped: list[str] = []

    if "matrix" in df.columns:
        df["raw_matrix"] = df["matrix"]
        df = normalize_column(
            df, "raw_matrix", "normalized_matrix",
            mat_map, "normalized_matrix", unmapped, logger
        )
        # Add matrix_group
        df["matrix_group"] = df["raw_matrix"].apply(
            lambda v: mat_map.get(str(v).strip().lower(), {}).get("matrix_group", "unclear")
        )
    else:
        logger.warning("Column 'matrix' missing — skipping.")

    # Normalize sample_origin if present
    if "sample_origin" in df.columns:
        df["raw_sample_origin"] = df["sample_origin"]
        df = normalize_column(
            df, "raw_sample_origin", "normalized_sample_origin",
            mat_map, "normalized_matrix", unmapped, logger
        )

    # Save unmapped
    if unmapped:
        import pandas as pd
        qa_dir = output_path.parent.parent / "qa_reports"
        qa_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"unmapped_term": list(set(unmapped)),
                      "source_table": "sample_matrix",
                      "dictionary": "matrix_dictionary"}).to_csv(
            qa_dir / "unmapped_matrix.csv", index=False, encoding="utf-8-sig"
        )
        logger.info(f"Unmapped matrix terms: {len(set(unmapped))}")

    save_output(df, output_path, logger)
    logger.info("04_normalize_sample_matrix COMPLETE")


if __name__ == "__main__":
    main()
