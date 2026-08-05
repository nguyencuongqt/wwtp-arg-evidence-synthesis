"""Regenerate the M1 Axis 2 B1 table from the corrected frozen v2 cohort."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260629
RNG = np.random.default_rng(SEED)
ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "data/m1_axis2_abundance_liquid_public_v2_20260730.csv"
OUT = ROOT / "results/m1_results_B1_abundance_liquid_gene_family_by_matrix_v2_20260730.csv"
GENE_ORDER = ["tet", "sul", "bla", "intI1", "erm", "qnr", "other"]
MATRIX_ORDER = ["influent", "secondary_effluent", "final_effluent", "sludge"]


def bootstrap_ci(values: np.ndarray, n_boot: int = 5000) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return math.nan, math.nan
    if len(values) == 1:
        return float(values[0]), float(values[0])
    idx = RNG.integers(0, len(values), size=(n_boot, len(values)))
    boot = np.median(values[idx], axis=1)
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def main() -> None:
    abundance = pd.read_csv(COHORT)
    abundance["analysis_log10_value"] = pd.to_numeric(
        abundance["analysis_log10_value"], errors="coerce"
    )
    scoped = abundance[abundance["matrix_bucket"].isin(MATRIX_ORDER)].copy()
    rows: list[dict[str, object]] = []
    for (family, matrix, unit_track), group in scoped.groupby(
        ["gene_family", "matrix_bucket", "unit_track"], dropna=False
    ):
        study_values = (
            group.dropna(subset=["analysis_log10_value"])
            .groupby("record_id")["analysis_log10_value"]
            .median()
            .astype(float)
            .to_numpy()
        )
        raw_values = group["analysis_log10_value"].dropna().astype(float).to_numpy()
        ci_low, ci_high = bootstrap_ci(study_values)
        rows.append(
            {
                "gene_family": family,
                "matrix_bucket": matrix,
                "unit_track": unit_track,
                "source_cohort_id": "M1_AXIS2_ABUNDANCE_LIQUID_COPIES_ML_V2_20260730",
                "source_cohort_rows": len(abundance),
                "source_cohort_studies": abundance["record_id"].nunique(),
                "analysis_scope_rows": len(scoped),
                "analysis_scope_studies": scoped["record_id"].nunique(),
                "n_studies": len(study_values),
                "n_rows": len(raw_values),
                "median_log10_study_level": np.median(study_values),
                "iqr_low_log10_study_level": np.percentile(study_values, 25),
                "iqr_high_log10_study_level": np.percentile(study_values, 75),
                "min_study_level": np.min(study_values),
                "max_study_level": np.max(study_values),
                "bootstrap_median_log10_ci_low": ci_low,
                "bootstrap_median_log10_ci_high": ci_high,
                "display_unit": "log10 copies/mL equivalent",
                "descriptive_synthesis_mode": (
                    "median_iqr_bootstrap_ci"
                    if len(study_values) >= 5
                    else "list_or_descriptive_lt_min_studies"
                ),
                "abundance_interpretation_note": (
                    "Cross-study abundance landscape; not paired removal."
                ),
            }
        )
    out = pd.DataFrame(rows)
    out["gene_family"] = pd.Categorical(out["gene_family"], GENE_ORDER, ordered=True)
    out["matrix_bucket"] = pd.Categorical(
        out["matrix_bucket"], MATRIX_ORDER, ordered=True
    )
    out = out.sort_values(["gene_family", "matrix_bucket"]).reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(OUT)


if __name__ == "__main__":
    main()
