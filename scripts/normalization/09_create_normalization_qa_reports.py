#!/usr/bin/env python3
"""
09_create_normalization_qa_reports.py

Aggregate all QA outputs from normalization scripts 02–08.
Creates:
  - qa_reports/unmapped_terms_report.csv     (all unmapped terms combined)
  - qa_reports/normalization_quality_report.csv (per-table coverage stats)
  - logs/data_normalization_summary.md        (human-readable summary)

Reads:
  06_data_normalization/qa_reports/unmapped_*.csv
  06_data_normalization/normalized_tables/*.csv

Usage:
    python 09_create_normalization_qa_reports.py
    python 09_create_normalization_qa_reports.py --overwrite
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _norm_utils import setup_logging

# ── Configuration ──────────────────────────────────────────────────────────────

# Table → (normalized CSV, [columns to check for coverage])
TABLE_CONFIGS = {
    "study_metadata": (
        "study_metadata_normalized.csv",
        ["normalized_wastewater_source_type", "normalized_study_type",
         "normalized_evidence_tier", "normalized_system_scale"],
    ),
    "treatment_system": (
        "treatment_system_normalized.csv",
        ["normalized_treatment_process", "treatment_group"],
    ),
    "sample_matrix": (
        "sample_matrix_normalized.csv",
        ["normalized_matrix", "matrix_group"],
    ),
    "arg_targets": (
        "arg_targets_normalized.csv",
        ["normalized_target_name", "normalized_arg_class", "normalized_target_type"],
    ),
    "arg_measurements": (
        "arg_measurements_normalized.csv",
        ["normalized_target_name", "normalized_unit", "unit_family", "final_unit"],
    ),
    "outcomes": (
        "outcomes_normalized.csv",
        ["normalized_outcome_type", "normalized_paired_data_status",
         "valid_for_removal_synthesis", "needs_human_check"],
    ),
    "kg_triples": (
        "kg_triples_normalized.csv",
        ["normalized_predicate", "normalized_polarity", "normalized_evidence_strength"],
    ),
}


# ── Helper functions ───────────────────────────────────────────────────────────

def load_table(tables_dir: Path, filename: str, logger) -> pd.DataFrame | None:
    path = tables_dir / filename
    if not path.exists():
        logger.warning(f"[SKIP] Normalized table not found: {filename}")
        return None
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        logger.info(f"Loaded: {filename} ({len(df)} rows)")
        return df
    except Exception as exc:
        logger.error(f"Could not load {filename}: {exc}")
        return None


def compute_table_coverage(table_name: str, df: pd.DataFrame,
                           cols_to_check: list[str]) -> dict:
    """Return coverage stats for a normalized table."""
    row = {
        "table_name": table_name,
        "total_rows": len(df),
    }
    for col in cols_to_check:
        if col in df.columns:
            mapped_col = f"{col}_mapped"
            if mapped_col in df.columns:
                n_mapped = (df[mapped_col] == "Yes").sum()
                row[f"{col}_mapped_pct"] = (
                    f"{n_mapped}/{len(df)} ({100*n_mapped/len(df):.1f}%)"
                    if len(df) > 0 else "0/0"
                )
            n_filled = (df[col].str.strip() != "").sum()
            row[f"{col}_filled_pct"] = (
                f"{n_filled}/{len(df)} ({100*n_filled/len(df):.1f}%)"
                if len(df) > 0 else "0/0"
            )
    return row


def distribution_table(df: pd.DataFrame, col: str, top_n: int = 15) -> str:
    """Return a markdown table of value counts for a column."""
    if col not in df.columns or df.empty:
        return "_column not available_"
    counts = df[col].value_counts().head(top_n)
    if counts.empty:
        return "_no data_"
    lines = ["| Value | Count |", "| --- | --- |"]
    for val, cnt in counts.items():
        lines.append(f"| {val} | {cnt} |")
    return "\n".join(lines)


def md_section(title: str, content: str, level: int = 2) -> str:
    prefix = "#" * level
    return f"\n{prefix} {title}\n\n{content}\n"


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Create normalization QA reports.")
    parser.add_argument("--norm-dir", default="..",
                        help="Root of 06_data_normalization/")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    norm_dir = Path(args.norm_dir).resolve()
    tables_dir = norm_dir / "normalized_tables"
    qa_dir = norm_dir / "qa_reports"
    log_dir = norm_dir / "logs"

    qa_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(log_dir, "09_create_normalization_qa_reports")

    logger.info("=" * 60)
    logger.info("09_create_normalization_qa_reports START")
    logger.info("=" * 60)

    # ── 1. Aggregate unmapped terms ────────────────────────────────────────────
    unmapped_files = list(qa_dir.glob("unmapped_*.csv"))
    all_unmapped: list[pd.DataFrame] = []
    for f in unmapped_files:
        try:
            tmp = pd.read_csv(f, dtype=str).fillna("")
            all_unmapped.append(tmp)
            logger.info(f"Found unmapped file: {f.name} ({len(tmp)} rows)")
        except Exception as exc:
            logger.warning(f"Could not load {f.name}: {exc}")

    unmapped_report_path = qa_dir / "unmapped_terms_report.csv"
    if unmapped_report_path.exists() and not args.overwrite:
        logger.error(f"Output exists: {unmapped_report_path}. Use --overwrite.")
        sys.exit(1)

    if all_unmapped:
        df_unmapped = pd.concat(all_unmapped, ignore_index=True)
        df_unmapped = df_unmapped.drop_duplicates(subset=["unmapped_term", "source_table"])
        df_unmapped = df_unmapped.sort_values(["source_table", "unmapped_term"])
        df_unmapped.to_csv(unmapped_report_path, index=False, encoding="utf-8-sig")
        logger.info(f"Unmapped terms report: {len(df_unmapped)} unique terms")
    else:
        logger.info("No unmapped term files found — skipping unmapped_terms_report.csv")
        df_unmapped = pd.DataFrame(columns=["unmapped_term", "source_table", "dictionary"])

    # ── 2. Quality report per table ────────────────────────────────────────────
    quality_rows: list[dict] = []
    loaded_tables: dict[str, pd.DataFrame] = {}

    for table_name, (filename, cols_to_check) in TABLE_CONFIGS.items():
        df = load_table(tables_dir, filename, logger)
        if df is not None:
            loaded_tables[table_name] = df
            row = compute_table_coverage(table_name, df, cols_to_check)
            quality_rows.append(row)

    quality_path = qa_dir / "normalization_quality_report.csv"
    if quality_path.exists() and not args.overwrite:
        logger.error(f"Output exists: {quality_path}. Use --overwrite.")
        sys.exit(1)

    df_quality = pd.DataFrame(quality_rows)
    df_quality.to_csv(quality_path, index=False, encoding="utf-8-sig")
    logger.info(f"Quality report: {len(df_quality)} tables")

    # ── 3. Markdown summary ────────────────────────────────────────────────────
    summary_path = log_dir / "data_normalization_summary.md"
    if summary_path.exists() and not args.overwrite:
        logger.error(f"Output exists: {summary_path}. Use --overwrite.")
        sys.exit(1)

    md_parts = ["# Data Normalization Summary — 06_data_normalization\n"]

    # 3a. Row counts
    row_counts_lines = ["| Table | Rows |", "| --- | --- |"]
    for table_name, df in loaded_tables.items():
        row_counts_lines.append(f"| {table_name} | {len(df)} |")
    md_parts.append(md_section("Row Counts", "\n".join(row_counts_lines)))

    # 3b. Unmapped terms summary
    if not df_unmapped.empty:
        by_source = df_unmapped.groupby("source_table").size().reset_index(name="unmapped_count")
        lines = ["| Source Table | Unmapped Terms |", "| --- | --- |"]
        for _, r in by_source.iterrows():
            lines.append(f"| {r['source_table']} | {r['unmapped_count']} |")
        md_parts.append(md_section("Unmapped Terms by Table", "\n".join(lines)))
    else:
        md_parts.append(md_section("Unmapped Terms", "_No unmapped terms found._"))

    # 3c. Matrix distribution
    if "sample_matrix" in loaded_tables:
        col = "normalized_matrix" if "normalized_matrix" in loaded_tables["sample_matrix"].columns else "matrix_group"
        md_parts.append(md_section("Matrix Distribution", distribution_table(loaded_tables["sample_matrix"], col)))

    # 3d. Treatment process distribution
    if "treatment_system" in loaded_tables:
        md_parts.append(md_section(
            "Treatment Group Distribution",
            distribution_table(loaded_tables["treatment_system"], "treatment_group"),
        ))

    # 3e. ARG class distribution
    if "arg_targets" in loaded_tables:
        md_parts.append(md_section(
            "ARG Class Distribution",
            distribution_table(loaded_tables["arg_targets"], "normalized_arg_class"),
        ))

    # 3f. Unit family distribution
    if "arg_measurements" in loaded_tables:
        md_parts.append(md_section(
            "Unit Family Distribution (Measurements)",
            distribution_table(loaded_tables["arg_measurements"], "unit_family"),
        ))

    # 3g. Outcome synthesis eligibility
    if "outcomes" in loaded_tables:
        df_out = loaded_tables["outcomes"]
        total = len(df_out)
        if "valid_for_removal_synthesis" in df_out.columns:
            n_yes = df_out["valid_for_removal_synthesis"].str.startswith("Yes").sum()
            n_no = (df_out["valid_for_removal_synthesis"] == "No").sum()
            synth_lines = [
                f"- Valid for removal synthesis (Yes/Yes_author_reported): **{n_yes}** / {total}",
                f"- Not valid: **{n_no}** / {total}",
            ]
        else:
            synth_lines = ["_valid_for_removal_synthesis column not found_"]
        if "needs_human_check" in df_out.columns:
            n_check = (df_out["needs_human_check"] == "Yes").sum()
            synth_lines.append(f"- Needs human check: **{n_check}** / {total}")
        md_parts.append(md_section("Outcome Synthesis Eligibility", "\n".join(synth_lines)))

    # 3h. KG triple provenance
    if "kg_triples" in loaded_tables:
        df_kg = loaded_tables["kg_triples"]
        total = len(df_kg)
        if "missing_provenance" in df_kg.columns:
            n_missing = (df_kg["missing_provenance"].str.strip() != "").sum()
            prov_lines = [
                f"- Total triples: **{total}**",
                f"- Triples with missing provenance fields: **{n_missing}**",
            ]
        else:
            prov_lines = [f"- Total triples: **{total}**"]
        md_parts.append(md_section("KG Triple Provenance Check", "\n".join(prov_lines)))

    summary_text = "".join(md_parts)
    summary_path.write_text(summary_text, encoding="utf-8")
    logger.info(f"Summary written: {summary_path.name}")

    logger.info("09_create_normalization_qa_reports COMPLETE")


if __name__ == "__main__":
    main()
