#!/usr/bin/env python3
"""
02_normalize_study_metadata.py

Normalize study metadata fields using controlled vocabulary.

Normalizes:
  - wastewater_source_type (via wastewater_source_dictionary.csv)
  - study_type (rule-based)
  - evidence_tier (rule-based)
  - system_scale (rule-based)
  - country (basic capitalization normalization)

Reads:
  05_data_extraction/final_extracted/final_study_metadata.csv

Saves:
  06_data_normalization/normalized_tables/study_metadata_normalized.csv

Usage:
    python 02_normalize_study_metadata.py
    python 02_normalize_study_metadata.py --overwrite
"""

import argparse
import sys
from pathlib import Path

# Allow importing sibling _norm_utils
sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         normalize_column, save_output, setup_logging)

# ── Controlled vocabulary for rule-based fields ────────────────────────────────

VALID_STUDY_TYPE = {
    "Full-scale WWTP", "Field-scale treatment system", "Pilot-scale treatment",
    "Bench-scale treatment", "Lab-scale treatment",
    "Receiving water linked to WWTP", "Sludge treatment", "Unclear",
}
VALID_TIER = {"Tier 1", "Tier 2", "Tier 3", "Unclear"}
VALID_SCALE = {"Full-scale", "Field-scale", "Pilot-scale", "Bench-scale", "Lab-scale", "Unclear"}


def normalize_controlled(val: str, valid_set: set[str]) -> tuple[str, str]:
    """Return (normalized_value, mapped_flag)."""
    v = str(val).strip()
    if v in valid_set:
        return v, "Yes"
    # Case-insensitive match
    for valid in valid_set:
        if v.lower() == valid.lower():
            return valid, "Yes"
    return v if v else "Unclear", "No"


def normalize_country(raw: str) -> str:
    """Basic country normalization — title case, strip whitespace."""
    return str(raw).strip().title() if raw.strip() else ""


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize study metadata.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted/final_study_metadata.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/study_metadata_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "02_normalize_study_metadata")

    logger.info("=" * 60)
    logger.info("02_normalize_study_metadata START")
    logger.info("=" * 60)

    output_path = Path(args.output).resolve()
    check_overwrite(output_path, args.overwrite, logger)

    df = load_input(Path(args.input).resolve(), logger)
    if df is None:
        sys.exit(1)

    dict_dir = Path(args.dict_dir).resolve()
    ww_map = load_dictionary(
        dict_dir / "wastewater_source_dictionary.csv",
        "raw_term", logger
    )

    unmapped: list[str] = []

    # Wastewater source type
    if "wastewater_source_type" in df.columns:
        df["raw_wastewater_source_type"] = df["wastewater_source_type"]
        df = normalize_column(
            df, "raw_wastewater_source_type", "normalized_wastewater_source_type",
            ww_map, "normalized_wastewater_source_type", unmapped, logger
        )
    else:
        logger.warning("Column 'wastewater_source_type' missing — skipping.")

    # study_type, evidence_tier, system_scale — rule-based
    for col, valid_set, norm_col in [
        ("study_type",   VALID_STUDY_TYPE, "normalized_study_type"),
        ("evidence_tier", VALID_TIER,      "normalized_evidence_tier"),
        ("system_scale", VALID_SCALE,      "normalized_system_scale"),
    ]:
        if col in df.columns:
            df[f"raw_{col}"] = df[col]
            df[norm_col], df[f"{norm_col}_mapped"] = zip(
                *df[f"raw_{col}"].apply(lambda v: normalize_controlled(v, valid_set))
            )
        else:
            logger.warning(f"Column '{col}' missing — skipping.")

    # Country
    if "country" in df.columns:
        df["normalized_country"] = df["country"].apply(normalize_country)

    # Save unmapped terms to QA
    if unmapped:
        qa_dir = Path(args.output).parent.parent / "qa_reports"
        qa_dir.mkdir(parents=True, exist_ok=True)
        import pandas as pd
        pd.DataFrame({"unmapped_term": list(set(unmapped)),
                      "source_table": "study_metadata",
                      "dictionary": "wastewater_source_dictionary"}).to_csv(
            qa_dir / "unmapped_study_metadata.csv", index=False, encoding="utf-8-sig"
        )
        logger.info(f"Unmapped terms: {len(set(unmapped))} → qa_reports/unmapped_study_metadata.csv")

    save_output(df, output_path, logger)
    logger.info("=" * 60)
    logger.info("02_normalize_study_metadata COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
