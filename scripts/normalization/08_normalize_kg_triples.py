#!/usr/bin/env python3
"""
08_normalize_kg_triples.py

Normalize KG triple data: subject, predicate, object, subject_type,
object_type, polarity, evidence_strength.
Validates predicates against predicate_dictionary.
Preserves: record_id, evidence_quote, confidence, human_validation_status.

Reads:   05_data_extraction/final_extracted/final_kg_triples.csv
Saves:   06_data_normalization/normalized_tables/kg_triples_normalized.csv

Usage:
    python 08_normalize_kg_triples.py
    python 08_normalize_kg_triples.py --overwrite
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import (check_overwrite, load_dictionary, load_input,
                         normalize_column, save_output, setup_logging)

# ── Controlled vocabularies ────────────────────────────────────────────────────

VALID_POLARITY = {"positive", "negative", "absence_like", "unknown"}

VALID_EVIDENCE_STRENGTH = {
    "direct_measurement",
    "author_reported",
    "inferred_from_data",
    "inferred_uncertain",
    "model_output",
    "unclear",
}

# Columns that must be preserved (warn if missing)
REQUIRED_PROVENANCE_COLS = {"record_id", "evidence_quote", "confidence", "human_validation_status"}


def normalize_controlled_value(raw: str, valid_set: set[str]) -> tuple[str, str]:
    """Return (normalized, was_mapped). Case-insensitive match against valid_set."""
    v = str(raw).strip()
    if v in valid_set:
        return v, "Yes"
    v_lower = v.lower()
    for valid in valid_set:
        if v_lower == valid.lower():
            return valid, "Yes"
    return v if v else "unclear", "No"


def normalize_subject_object(raw: str, arg_map: dict, mat_map: dict, tp_map: dict) -> str:
    """
    Attempt best-effort normalization of subject/object values.
    Tries ARG names, matrices, treatment processes in sequence.
    Returns the first successful match, or the raw value if none found.
    """
    v = str(raw).strip()
    v_lower = v.lower()

    # Try ARG name dictionary
    if v_lower in arg_map:
        return str(arg_map[v_lower].get("normalized_arg_name", v)).strip()

    # Try matrix dictionary
    if v_lower in mat_map:
        return str(mat_map[v_lower].get("normalized_matrix", v)).strip()

    # Try treatment process dictionary
    if v_lower in tp_map:
        return str(tp_map[v_lower].get("normalized_treatment_process", v)).strip()

    return v  # return as-is


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Normalize KG triple data.")
    parser.add_argument("--input",
                        default="../../05_data_extraction/final_extracted/final_kg_triples.csv")
    parser.add_argument("--dict-dir", default="../dictionaries")
    parser.add_argument("--output",
                        default="../normalized_tables/kg_triples_normalized.csv")
    parser.add_argument("--log-dir", default="../logs")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    logger = setup_logging(log_dir, "08_normalize_kg_triples")

    logger.info("=" * 60)
    logger.info("08_normalize_kg_triples START")
    logger.info("=" * 60)

    output_path = Path(args.output).resolve()
    check_overwrite(output_path, args.overwrite, logger)

    df = load_input(Path(args.input).resolve(), logger)
    if df is None:
        sys.exit(1)

    # Warn on missing provenance columns
    for col in REQUIRED_PROVENANCE_COLS:
        if col not in df.columns:
            logger.warning(f"Provenance column missing: '{col}' — triples may lack traceable evidence.")

    dict_dir = Path(args.dict_dir).resolve()
    arg_map = load_dictionary(dict_dir / "arg_name_dictionary.csv", "raw_term", logger)
    mat_map = load_dictionary(dict_dir / "matrix_dictionary.csv", "raw_term", logger)
    tp_map = load_dictionary(dict_dir / "treatment_process_dictionary.csv", "raw_term", logger)
    pred_map = load_dictionary(dict_dir / "predicate_dictionary.csv", "raw_predicate", logger)

    unmapped_all: list[str] = []

    # Normalize subject
    if "subject" in df.columns:
        df["raw_subject"] = df["subject"]
        df["normalized_subject"] = df["raw_subject"].apply(
            lambda v: normalize_subject_object(v, arg_map, mat_map, tp_map)
        )
        n_changed = (df["normalized_subject"] != df["raw_subject"]).sum()
        logger.info(f"  subject: {n_changed} values normalized")

    # Normalize predicate via dictionary
    if "predicate" in df.columns:
        df["raw_predicate"] = df["predicate"]
        df = normalize_column(df, "raw_predicate", "normalized_predicate",
                              pred_map, "normalized_predicate", unmapped_all, logger)
        df["predicate_relation_group"] = df["raw_predicate"].apply(
            lambda v: pred_map.get(str(v).strip().lower(), {}).get("relation_group", "")
        )
        df["allowed_evidence_strength"] = df["raw_predicate"].apply(
            lambda v: pred_map.get(str(v).strip().lower(), {}).get("allowed_evidence_strength", "")
        )
        # Flag predicates that don't match any known predicate
        invalid_preds = df[df["normalized_predicate_mapped"] == "No"]["raw_predicate"].unique()
        if len(invalid_preds) > 0:
            logger.warning(f"Unrecognized predicates: {list(invalid_preds)}")

    # Normalize object
    if "object" in df.columns:
        df["raw_object"] = df["object"]
        df["normalized_object"] = df["raw_object"].apply(
            lambda v: normalize_subject_object(v, arg_map, mat_map, tp_map)
        )
        n_changed = (df["normalized_object"] != df["raw_object"]).sum()
        logger.info(f"  object: {n_changed} values normalized")

    # Normalize subject_type (keep as-is but record)
    if "subject_type" in df.columns:
        df["raw_subject_type"] = df["subject_type"]

    # Normalize object_type (keep as-is but record)
    if "object_type" in df.columns:
        df["raw_object_type"] = df["object_type"]

    # Normalize polarity
    if "polarity" in df.columns:
        df["raw_polarity"] = df["polarity"]
        norm_vals, mapped_flags = [], []
        for raw in df["raw_polarity"]:
            norm, mapped = normalize_controlled_value(str(raw), VALID_POLARITY)
            norm_vals.append(norm)
            mapped_flags.append("Yes" if mapped else "No")
            if not mapped and str(raw).strip() not in ("", "unclear", "unknown"):
                unmapped_all.append(str(raw).strip())
        df["normalized_polarity"] = norm_vals
        df["normalized_polarity_mapped"] = mapped_flags
    else:
        logger.warning("Column 'polarity' missing — skipping.")

    # Normalize evidence_strength
    if "evidence_strength" in df.columns:
        df["raw_evidence_strength"] = df["evidence_strength"]
        norm_vals, mapped_flags = [], []
        for raw in df["raw_evidence_strength"]:
            norm, mapped = normalize_controlled_value(str(raw), VALID_EVIDENCE_STRENGTH)
            norm_vals.append(norm)
            mapped_flags.append("Yes" if mapped else "No")
            if not mapped and str(raw).strip() not in ("", "unclear"):
                unmapped_all.append(str(raw).strip())
        df["normalized_evidence_strength"] = norm_vals
        df["normalized_evidence_strength_mapped"] = mapped_flags
    else:
        logger.warning("Column 'evidence_strength' missing — skipping.")

    # Flag triples missing critical provenance fields
    missing_flags = []
    for _, row in df.iterrows():
        missing = []
        for col in REQUIRED_PROVENANCE_COLS:
            if col in df.columns and str(row.get(col, "")).strip() in ("", "nan", "None"):
                missing.append(col)
        missing_flags.append("|".join(missing) if missing else "")
    df["missing_provenance"] = missing_flags

    n_missing = sum(1 for m in missing_flags if m)
    if n_missing:
        logger.warning(f"{n_missing} triples have missing provenance fields.")

    # Save unmapped terms
    if unmapped_all:
        qa_dir = output_path.parent.parent / "qa_reports"
        qa_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({
            "unmapped_term": list(set(unmapped_all)),
            "source_table": "kg_triples",
            "dictionary": "multiple",
        }).to_csv(qa_dir / "unmapped_kg_triples.csv", index=False, encoding="utf-8-sig")
        logger.info(f"Unmapped terms: {len(set(unmapped_all))}")

    save_output(df, output_path, logger)
    logger.info("08_normalize_kg_triples COMPLETE")


if __name__ == "__main__":
    main()
