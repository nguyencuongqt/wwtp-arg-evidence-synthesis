"""Rerun DL pooled estimates and I2 directly from frozen M1 snapshots.

This script replaces imported 20260626 diagnostic I2/pooled values with
frozen-derived estimates for M1 Results tables A1/A2/A3/C1.

Frozen snapshots do not contain per-effect SEs. The original synthesis used
study-level means with imputed within-study sampling variance. This script
reimplements that method on the frozen rows so every reported I2/pooled value
is reproducible from the frozen cohort snapshot itself.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260629
DATE_TAG = "20260629"

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data"
TABLES = ROOT / "results"
REPORTS = ROOT / "metadata"

REMOVAL_LOG = FROZEN / "m1_axis1_removal_log_reduction_public_v1_20260730.csv"

A1_OLD = TABLES / "m1_results_A1_removal_main_route_gene_forest_20260629.csv"
A2_OLD = TABLES / "m1_results_A2_removal_gene_family_by_route_20260629.csv"
A3_OLD = TABLES / "m1_results_A3_removal_treatment_4group_20260629.csv"
C1_OLD = TABLES / "m1_results_C1_heterogeneity_route_treatment_subgroups_20260629.csv"

A1_NEW = TABLES / "m1_results_A1_removal_main_route_gene_forest_frozen_dl_20260629.csv"
A2_NEW = TABLES / "m1_results_A2_removal_gene_family_by_route_frozen_dl_20260629.csv"
A3_NEW = TABLES / "m1_results_A3_removal_treatment_4group_frozen_dl_20260629.csv"
C1_NEW = TABLES / "m1_results_C1_heterogeneity_route_treatment_subgroups_frozen_dl_20260629.csv"

FROZEN_DL_CELLS = TABLES / "m1_results_frozen_dl_i2_pooled_cells_20260629.csv"
COMPARISON_CSV = TABLES / "m1_results_frozen_dl_vs_import_comparison_20260629.csv"
QC_JSON = REPORTS / "M1_RESULTS_FROZEN_DL_I2_QC_20260629.json"
QC_MD = REPORTS / "M1_RESULTS_FROZEN_DL_I2_QC_20260629.md"

ROUTE_MAIN = "influent_to_final_effluent"
A1_GENES = ["tet", "sul", "bla", "intI1", "erm", "qnr"]
GENE_ORDER = ["tet", "sul", "bla", "intI1", "erm", "qnr", "other"]
TREATMENT_ORDER = ["biological", "disinfection", "membrane", "physicochemical"]


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, **kwargs)


def dl_random_effects(study_df: pd.DataFrame) -> dict[str, float | str]:
    yi = study_df["study_mean"].astype(float).to_numpy()
    n = study_df["study_n_rows"].astype(float).to_numpy()
    if len(yi) < 2:
        return {
            "pooled_mean_dl": np.nan,
            "pooled_ci_low_dl": np.nan,
            "pooled_ci_high_dl": np.nan,
            "i2_percent": np.nan,
            "q": np.nan,
            "tau2_dl": np.nan,
            "variance_imputation": "not_estimated_lt2_studies",
            "imputed_sampling_variance": np.nan,
        }
    within_var = study_df["study_within_sd"].astype(float).to_numpy() ** 2 / np.maximum(n, 1.0)
    positive = within_var[np.isfinite(within_var) & (within_var > 0)]
    if len(positive):
        imputed = float(np.median(positive))
        variance_imputation = "within-study median from frozen rows"
    else:
        imputed = max(float(np.var(yi, ddof=1)) / max(len(yi), 2), 1e-6)
        variance_imputation = "cell-total-variance fallback from frozen rows"
    vi = np.where(np.isfinite(within_var) & (within_var > 0), within_var, imputed)
    vi = np.maximum(vi, 1e-6)
    wi = 1.0 / vi
    fixed = float(np.sum(wi * yi) / np.sum(wi))
    q = float(np.sum(wi * (yi - fixed) ** 2))
    df_q = len(yi) - 1
    c = float(np.sum(wi) - (np.sum(wi**2) / np.sum(wi)))
    tau2 = max(0.0, (q - df_q) / c) if c > 0 and df_q > 0 else 0.0
    rei = 1.0 / (vi + tau2)
    pooled = float(np.sum(rei * yi) / np.sum(rei))
    se = math.sqrt(float(1.0 / np.sum(rei)))
    i2 = max(0.0, (q - df_q) / q) * 100.0 if q > 0 and df_q > 0 else 0.0
    return {
        "pooled_mean_dl": pooled,
        "pooled_ci_low_dl": pooled - 1.96 * se,
        "pooled_ci_high_dl": pooled + 1.96 * se,
        "i2_percent": i2,
        "q": q,
        "tau2_dl": tau2,
        "variance_imputation": variance_imputation,
        "imputed_sampling_variance": imputed,
    }


def study_level(raw: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, grp in raw.groupby(group_cols + ["record_id"], dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        values = pd.to_numeric(grp["analysis_value"], errors="coerce").dropna().astype(float).to_numpy()
        if len(values) == 0:
            continue
        row = {col: val for col, val in zip(group_cols + ["record_id"], keys)}
        row.update(
            {
                "study_mean": float(np.mean(values)),
                "study_median": float(np.median(values)),
                "study_n_rows": int(len(values)),
                "study_within_sd": float(np.std(values, ddof=1)) if len(values) > 1 else np.nan,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_dl(
    raw: pd.DataFrame,
    group_cols: list[str],
    *,
    table_scope: str,
    min_studies_for_dl: int,
) -> pd.DataFrame:
    sl = study_level(raw, group_cols)
    rows = []
    if sl.empty:
        return pd.DataFrame()
    for keys, grp in sl.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        k = int(grp["record_id"].nunique())
        n_rows = int(grp["study_n_rows"].sum())
        row = {
            "table_scope": table_scope,
            "source_cohort_id": "M1_AXIS1_REMOVAL_LOG_REDUCTION",
            "source_cohort_rows": int(len(raw_all)),
            "source_cohort_studies": int(raw_all["record_id"].nunique()),
            "dl_method": "DerSimonian-Laird on frozen snapshot study-level means",
            "effect_input": "analysis_value log10 reduction from frozen snapshot",
            "variance_source": "No per-effect SE in frozen; imputed from frozen within-study dispersion/fallback.",
            "n_studies": k,
            "n_rows": n_rows,
            "study_mean_median": float(np.median(grp["study_mean"].astype(float))),
            "study_mean_iqr_low": float(np.percentile(grp["study_mean"].astype(float), 25)),
            "study_mean_iqr_high": float(np.percentile(grp["study_mean"].astype(float), 75)),
        }
        for c, v in zip(group_cols, keys):
            row[c] = v
        if k >= min_studies_for_dl:
            row["frozen_dl_synthesis_mode"] = f"frozen_dl_ge{min_studies_for_dl}_studies"
            row.update(dl_random_effects(grp))
        else:
            row["frozen_dl_synthesis_mode"] = f"not_estimated_lt{min_studies_for_dl}_studies"
            row.update(
                {
                    "pooled_mean_dl": np.nan,
                    "pooled_ci_low_dl": np.nan,
                    "pooled_ci_high_dl": np.nan,
                    "i2_percent": np.nan,
                    "q": np.nan,
                    "tau2_dl": np.nan,
                    "variance_imputation": f"not_estimated_lt{min_studies_for_dl}_studies",
                    "imputed_sampling_variance": np.nan,
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)


def strip_old_import_cols(df: pd.DataFrame) -> pd.DataFrame:
    drop_patterns = [
        "_from_20260626",
        "i2_source_",
    ]
    drop_cols = [
        c
        for c in df.columns
        if any(pat in c for pat in drop_patterns)
        or c in {"i2_source_note", "i2_reduction_interpretation_from_20260626"}
    ]
    return df.drop(columns=drop_cols, errors="ignore")


def attach_dl(
    base: pd.DataFrame,
    dl: pd.DataFrame,
    keys: list[str],
) -> pd.DataFrame:
    frozen_cols = keys + [
        "n_studies",
        "n_rows",
        "pooled_mean_dl",
        "pooled_ci_low_dl",
        "pooled_ci_high_dl",
        "i2_percent",
        "q",
        "tau2_dl",
        "variance_imputation",
        "imputed_sampling_variance",
        "frozen_dl_synthesis_mode",
        "dl_method",
        "effect_input",
        "variance_source",
    ]
    d = dl[[c for c in frozen_cols if c in dl.columns]].copy()
    rename = {
        "n_studies": "frozen_dl_n_studies",
        "n_rows": "frozen_dl_n_rows",
        "pooled_mean_dl": "pooled_mean_dl_frozen",
        "pooled_ci_low_dl": "pooled_ci_low_dl_frozen",
        "pooled_ci_high_dl": "pooled_ci_high_dl_frozen",
        "i2_percent": "i2_percent_frozen",
        "q": "q_frozen",
        "tau2_dl": "tau2_dl_frozen",
    }
    d = d.rename(columns=rename)
    out = strip_old_import_cols(base).merge(d, on=keys, how="left")
    out["frozen_dl_study_n_match"] = out["n_studies"].astype("Int64").eq(out["frozen_dl_n_studies"].astype("Int64"))
    out["frozen_dl_row_n_match"] = out["n_rows"].astype("Int64").eq(out["frozen_dl_n_rows"].astype("Int64"))
    out["i2_pooled_source"] = np.where(
        out["i2_percent_frozen"].notna() | out["pooled_mean_dl_frozen"].notna(),
        "frozen_snapshot_direct_rerun",
        "not_estimated_by_threshold",
    )
    return out


def compare_import(old: pd.DataFrame, new: pd.DataFrame, keys: list[str], table: str) -> pd.DataFrame:
    old_cols = keys + [
        "n_studies",
        "n_rows",
        "pooled_mean_dl_from_20260626",
        "pooled_ci_low_dl_from_20260626",
        "pooled_ci_high_dl_from_20260626",
        "i2_percent_from_20260626_analysis_clean",
    ]
    old_sub = old[[c for c in old_cols if c in old.columns]].copy()
    old_sub = old_sub[
        old_sub.get("pooled_mean_dl_from_20260626", pd.Series(index=old_sub.index)).notna()
        | old_sub.get("i2_percent_from_20260626_analysis_clean", pd.Series(index=old_sub.index)).notna()
    ]
    new_cols = keys + [
        "pooled_mean_dl_frozen",
        "pooled_ci_low_dl_frozen",
        "pooled_ci_high_dl_frozen",
        "i2_percent_frozen",
        "q_frozen",
        "tau2_dl_frozen",
        "frozen_dl_n_studies",
        "frozen_dl_n_rows",
        "frozen_dl_synthesis_mode",
    ]
    merged = old_sub.merge(new[[c for c in new_cols if c in new.columns]], on=keys, how="left")
    if merged.empty:
        return merged
    merged.insert(0, "table", table)
    merged["pooled_mean_delta_frozen_minus_import"] = (
        merged["pooled_mean_dl_frozen"] - merged["pooled_mean_dl_from_20260626"]
        if "pooled_mean_dl_from_20260626" in merged
        else np.nan
    )
    merged["i2_delta_frozen_minus_import"] = (
        merged["i2_percent_frozen"] - merged["i2_percent_from_20260626_analysis_clean"]
        if "i2_percent_from_20260626_analysis_clean" in merged
        else np.nan
    )
    merged["changed_vs_import"] = (
        merged["pooled_mean_delta_frozen_minus_import"].abs().fillna(0).gt(1e-9)
        | merged["i2_delta_frozen_minus_import"].abs().fillna(0).gt(1e-9)
    )
    return merged


def order_categories(df: pd.DataFrame) -> pd.DataFrame:
    if "gene_family" in df.columns:
        df["gene_family"] = pd.Categorical(df["gene_family"], categories=GENE_ORDER, ordered=True)
    if "technology_supergroup_4group" in df.columns:
        df["technology_supergroup_4group"] = pd.Categorical(
            df["technology_supergroup_4group"], categories=TREATMENT_ORDER, ordered=True
        )
    return df


if __name__ == "__main__":
    TABLES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    raw_all = read_csv(REMOVAL_LOG)
    raw_all["analysis_value"] = pd.to_numeric(raw_all["analysis_value"], errors="coerce")
    raw_all = raw_all[raw_all["analysis_value"].notna()].copy()

    frozen_counts = {
        "M1_AXIS1_REMOVAL_LOG_REDUCTION": {
            "rows": int(len(raw_all)),
            "studies": int(raw_all["record_id"].nunique()),
        }
    }

    # Frozen DL cells.
    a_gene_route = summarize_dl(
        raw_all[raw_all["gene_family"].isin(GENE_ORDER)].copy(),
        ["gene_family", "route"],
        table_scope="A2_gene_family_by_route",
        min_studies_for_dl=10,
    )
    a1_dl = a_gene_route[
        a_gene_route["route"].eq(ROUTE_MAIN) & a_gene_route["gene_family"].isin(A1_GENES)
    ].copy()
    a1_dl["table_scope"] = "A1_main_route_gene_forest"

    a3_raw = raw_all[raw_all["technology_supergroup_4group"].isin(TREATMENT_ORDER)].copy()
    a_treatment = summarize_dl(
        a3_raw,
        ["technology_supergroup_4group"],
        table_scope="A3_treatment_4group",
        min_studies_for_dl=5,
    )

    route_dl = summarize_dl(
        raw_all,
        ["route"],
        table_scope="C1_route",
        min_studies_for_dl=5,
    ).rename(columns={"route": "subgroup"})
    route_dl["subgroup_type"] = "route"
    treatment_c1 = a_treatment.rename(columns={"technology_supergroup_4group": "subgroup"}).copy()
    treatment_c1["subgroup_type"] = "treatment_4group"
    treatment_c1["table_scope"] = "C1_treatment_4group"
    c1_dl = pd.concat([route_dl, treatment_c1], ignore_index=True, sort=False)

    all_dl = pd.concat([a1_dl, a_gene_route, a_treatment, c1_dl], ignore_index=True, sort=False)
    all_dl.to_csv(FROZEN_DL_CELLS, index=False, encoding="utf-8-sig")

    # Updated result tables.
    a1_old = read_csv(A1_OLD)
    a2_old = read_csv(A2_OLD)
    a3_old = read_csv(A3_OLD)
    c1_old = read_csv(C1_OLD)

    a1_new = attach_dl(a1_old, a1_dl, ["gene_family", "route"])
    a2_new = attach_dl(a2_old, a_gene_route, ["gene_family", "route"])
    a3_new = attach_dl(a3_old, a_treatment, ["technology_supergroup_4group"])
    c1_new = attach_dl(c1_old, c1_dl, ["subgroup_type", "subgroup"])

    a1_new = order_categories(a1_new).sort_values(["gene_family"]).reset_index(drop=True)
    a2_new = order_categories(a2_new).reset_index(drop=True)
    a3_new = order_categories(a3_new).sort_values(["technology_supergroup_4group"]).reset_index(drop=True)
    c1_new = c1_new.reset_index(drop=True)

    a1_new.to_csv(A1_NEW, index=False, encoding="utf-8-sig")
    a2_new.to_csv(A2_NEW, index=False, encoding="utf-8-sig")
    a3_new.to_csv(A3_NEW, index=False, encoding="utf-8-sig")
    c1_new.to_csv(C1_NEW, index=False, encoding="utf-8-sig")

    comparisons = [
        compare_import(a1_old, a1_new, ["gene_family", "route"], "A1"),
        compare_import(a2_old, a2_new, ["gene_family", "route"], "A2"),
        compare_import(a3_old, a3_new, ["technology_supergroup_4group"], "A3"),
        compare_import(c1_old, c1_new, ["subgroup_type", "subgroup"], "C1"),
    ]
    comp = pd.concat([c for c in comparisons if c is not None and not c.empty], ignore_index=True, sort=False)
    comp.to_csv(COMPARISON_CSV, index=False, encoding="utf-8-sig")

    updated_tables = {"A1": a1_new, "A2": a2_new, "A3": a3_new, "C1": c1_new}
    n_mismatch_rows = []
    diagnostic_only_cells = []
    for table, df in updated_tables.items():
        has_i2 = df["i2_percent_frozen"].notna() | df["pooled_mean_dl_frozen"].notna()
        mismatch = df[has_i2 & ~(df["frozen_dl_study_n_match"] & df["frozen_dl_row_n_match"])]
        if len(mismatch):
            n_mismatch_rows.append({"table": table, "n_mismatch": int(len(mismatch))})
        diagnostic_only = df[has_i2 & ~df["i2_pooled_source"].eq("frozen_snapshot_direct_rerun")]
        if len(diagnostic_only):
            diagnostic_only_cells.append({"table": table, "n_diagnostic_only": int(len(diagnostic_only))})

    qc = {
        "seed": SEED,
        "frozen_input": str(REMOVAL_LOG),
        "frozen_counts": frozen_counts,
        "method": {
            "model": "DerSimonian-Laird random effects",
            "effect": "study-level mean of frozen analysis_value log10 reduction",
            "variance": "within-study variance / n when available; otherwise median/fallback imputed from frozen cell",
            "thresholds": {
                "A1_A2_gene_route": "DL/I2 estimated for cells with >=10 studies",
                "A3_C1_route_treatment": "DL/I2 estimated for cells with >=5 studies",
            },
        },
        "outputs": {
            "frozen_dl_cells": str(FROZEN_DL_CELLS),
            "A1_updated": str(A1_NEW),
            "A2_updated": str(A2_NEW),
            "A3_updated": str(A3_NEW),
            "C1_updated": str(C1_NEW),
            "comparison": str(COMPARISON_CSV),
            "QC_json": str(QC_JSON),
            "QC_markdown": str(QC_MD),
        },
        "n_mismatch_for_cells_with_i2": n_mismatch_rows,
        "diagnostic_only_cells_remaining": diagnostic_only_cells,
        "comparison_changed_cells": int(comp["changed_vs_import"].sum()) if not comp.empty else 0,
    }
    QC_JSON.write_text(json.dumps(qc, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Frozen DL/I2 Rerun QC",
        "",
        f"Date tag: `{DATE_TAG}`",
        f"Seed: `{SEED}`",
        "",
        "## Method",
        "",
        "- Input: frozen snapshot `M1_AXIS1_REMOVAL_LOG_REDUCTION` only.",
        "- Model: DerSimonian-Laird random effects on study-level mean log10 reduction.",
        "- Variance: frozen snapshot has no per-effect SE; SE is imputed from frozen within-study dispersion, matching the original synthesis machinery.",
        "- Thresholds: A1/A2 gene-route cells use DL/I2 for >=10 studies; A3/C1 route/treatment cells use DL/I2 for >=5 studies.",
        "",
        "## QC",
        "",
        f"- Frozen input rows/studies: **{frozen_counts['M1_AXIS1_REMOVAL_LOG_REDUCTION']['rows']} / {frozen_counts['M1_AXIS1_REMOVAL_LOG_REDUCTION']['studies']}**.",
        f"- Cells with I2/pooled and frozen n mismatch: **{sum(x['n_mismatch'] for x in n_mismatch_rows) if n_mismatch_rows else 0}**.",
        f"- Cells still diagnostic-only: **{sum(x['n_diagnostic_only'] for x in diagnostic_only_cells) if diagnostic_only_cells else 0}**.",
        f"- Cells changed versus old import: **{qc['comparison_changed_cells']}**.",
        "",
        "## Changed Cells Versus Import",
        "",
    ]
    if comp.empty or not comp["changed_vs_import"].any():
        lines.append("- None.")
    else:
        show_cols = [
            "table",
            "gene_family",
            "route",
            "technology_supergroup_4group",
            "subgroup_type",
            "subgroup",
            "pooled_mean_dl_from_20260626",
            "pooled_mean_dl_frozen",
            "pooled_mean_delta_frozen_minus_import",
            "i2_percent_from_20260626_analysis_clean",
            "i2_percent_frozen",
            "i2_delta_frozen_minus_import",
        ]
        changed = comp[comp["changed_vs_import"]].copy()
        lines.append("| table | cell | pooled old | pooled frozen | pooled delta | I2 old | I2 frozen | I2 delta |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        for _, r in changed.iterrows():
            parts = []
            for c in ["gene_family", "route", "technology_supergroup_4group", "subgroup_type", "subgroup"]:
                if c in r.index and pd.notna(r[c]):
                    parts.append(f"{c}={r[c]}")
            cell = "; ".join(parts)
            def fmt(v):
                return "" if pd.isna(v) else f"{float(v):.6f}"
            lines.append(
                f"| {r['table']} | {cell} | {fmt(r.get('pooled_mean_dl_from_20260626'))} | "
                f"{fmt(r.get('pooled_mean_dl_frozen'))} | {fmt(r.get('pooled_mean_delta_frozen_minus_import'))} | "
                f"{fmt(r.get('i2_percent_from_20260626_analysis_clean'))} | {fmt(r.get('i2_percent_frozen'))} | "
                f"{fmt(r.get('i2_delta_frozen_minus_import'))} |"
            )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
        ]
    )
    for k, v in qc["outputs"].items():
        lines.append(f"- `{k}`: `{v}`")
    QC_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(qc, indent=2, ensure_ascii=False))
