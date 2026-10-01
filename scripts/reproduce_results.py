"""Reproduce the quantitative results of the manuscript from the public v4 datasets.

Run from the repository root:

    python scripts/reproduce_results.py

Outputs are written to results/. Every summary is computed from data/ and audit/ only;
no model calls are made. Study-level summaries use the median of each study's values;
DerSimonian-Laird (DL) random-effects estimates are reported only where the pre-specified
minimum number of studies is met (10 for gene-family cells, 5 for route and treatment cells).
Sampling variances are imputed from within-study dispersion, so DL estimates are
heterogeneity diagnostics rather than precision-weighted effects. Bootstrap confidence
intervals for medians use 2,000 resamples drawn from a single random stream (seed 20260626),
so the run is deterministic. Because the stream is shared, the interval for the same cell can
differ slightly between tables; the intervals reported in the manuscript are those in
removal_main_route_by_gene_family.csv (gene families) and removal_by_route.csv (routes).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AUDIT = ROOT / "audit"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

FAM = ["tet", "sul", "bla", "intI1", "erm", "qnr"]
ROUTES = ["influent_to_final_effluent", "influent_to_secondary_effluent", "secondary_effluent_to_final_effluent"]
TREAT = ["biological", "disinfection", "membrane", "physicochemical"]
MATRICES = ["influent", "secondary_effluent", "final_effluent"]
rng = np.random.default_rng(20260626)


def boot(values, n=2000):
    values = np.asarray(values)
    if len(values) < 2:
        return (np.nan, np.nan)
    medians = [np.median(rng.choice(values, len(values))) for _ in range(n)]
    return tuple(np.percentile(medians, [2.5, 97.5]))


def dl(group, col="analysis_value"):
    s = group.groupby("record_id")[col].agg(["mean", "count", "std"])
    yi = s["mean"].values
    n = s["count"].values.astype(float)
    wv = (s["std"].values ** 2) / np.maximum(n, 1)
    pos = wv[np.isfinite(wv) & (wv > 0)]
    imp = float(np.median(pos)) if len(pos) else max(np.var(yi, ddof=1) / max(len(yi), 2), 1e-6)
    vi = np.maximum(np.where(np.isfinite(wv) & (wv > 0), wv, imp), 1e-6)
    wi = 1 / vi
    fx = (wi * yi).sum() / wi.sum()
    q = (wi * (yi - fx) ** 2).sum()
    df = len(yi) - 1
    c = wi.sum() - (wi ** 2).sum() / wi.sum()
    t2 = max(0, (q - df) / c) if c > 0 and df > 0 else 0
    re = 1 / (vi + t2)
    p = (re * yi).sum() / re.sum()
    se = math.sqrt(1 / re.sum())
    i2 = max(0, (q - df) / q) * 100 if q > 0 and df > 0 else 0
    return dict(dl=p, dl_ci_low=p - 1.96 * se, dl_ci_high=p + 1.96 * se, i2_percent=i2)


def cell(group, threshold, col="analysis_value"):
    s = group.groupby("record_id")[col].median()
    if len(s) == 0:
        return None
    d = dict(studies=len(s), rows=len(group), median=s.median(), iqr_low=s.quantile(0.25), iqr_high=s.quantile(0.75),
             min=s.min(), max=s.max())
    d["bootstrap_ci_low"], d["bootstrap_ci_high"] = boot(s.values)
    if len(s) >= threshold:
        d.update(dl(group, col))
    return d


def meta_hksj(group):
    """DL estimate with Hartung-Knapp-Sidik-Jonkman 95% CI and 95% prediction interval (post hoc, five-study threshold)."""
    s = group.groupby("record_id")["analysis_value"].agg(["mean", "count", "std"])
    yi = s["mean"].values
    n = s["count"].values.astype(float)
    k = len(yi)
    wv = (s["std"].values ** 2) / np.maximum(n, 1)
    pos = wv[np.isfinite(wv) & (wv > 0)]
    imp = float(np.median(pos)) if len(pos) else max(np.var(yi, ddof=1) / max(k, 2), 1e-6)
    vi = np.maximum(np.where(np.isfinite(wv) & (wv > 0), wv, imp), 1e-6)
    wi = 1 / vi
    fx = (wi * yi).sum() / wi.sum()
    q = (wi * (yi - fx) ** 2).sum()
    df = k - 1
    c = wi.sum() - (wi ** 2).sum() / wi.sum()
    t2 = max(0, (q - df) / c) if c > 0 else 0
    w = 1 / (vi + t2)
    mu = (w * yi).sum() / w.sum()
    se = math.sqrt(1 / w.sum())
    seh = math.sqrt((w * (yi - mu) ** 2).sum() / df / w.sum())
    th = stats.t.ppf(0.975, df)
    pi = stats.t.ppf(0.975, k - 2) * math.sqrt(t2 + se ** 2)
    return dict(studies=k, median=group.groupby("record_id")["analysis_value"].median().median(), dl=mu,
                dl_ci_low=mu - 1.96 * se, dl_ci_high=mu + 1.96 * se, hksj_ci_low=mu - th * seh, hksj_ci_high=mu + th * seh,
                prediction_low=mu - pi, prediction_high=mu + pi, i2_percent=max(0, (q - df) / q) * 100 if q > 0 else 0)


def table(cells: dict, keys: list[str]) -> pd.DataFrame:
    rows = []
    for name, value in cells.items():
        if value is None:
            continue
        rows.append({**dict(zip(keys, name.split("|"))), **value})
    return pd.DataFrame(rows).round(4)


def clean(o):
    """Convert numpy types to JSON types and NaN to null."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if math.isnan(float(o)) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    return o


def main() -> None:
    R_all = pd.read_csv(DATA / "removal_log10_reduction_v4.csv", low_memory=False)
    P_all = pd.read_csv(DATA / "removal_percent_v4.csv", low_memory=False)
    A = pd.read_csv(DATA / "abundance_liquid_v4.csv", low_memory=False)
    X = pd.read_csv(DATA / "removal_route_layer_v4.csv", low_memory=False)
    crit = pd.read_csv(AUDIT / "critical_appraisal" / "critical_concern_outcomes.csv")

    tier1 = lambda d: d[d.analysis_tier.str.startswith("Tier 1")]
    R = tier1(R_all)
    P = tier1(P_all)
    R_t2 = R_all[~R_all.analysis_tier.str.startswith("Tier 1")]
    res: dict = {}

    # Removal (primary analysis: full-scale, Tier 1). Order matters for the bootstrap stream.
    main_route = R[R.route == "influent_to_final_effluent"]
    res["family_main_route"] = {f: cell(main_route[main_route.gene_family == f], 10) for f in FAM}
    res["family_by_route"] = {f"{f}|{r}": cell(R[(R.gene_family == f) & (R.route == r)], 10) for f in FAM for r in ROUTES}
    res["route"] = {r: cell(R[R.route == r], 5) for r in ROUTES}
    res["treatment"] = {t: cell(R[R.technology_supergroup_4group == t], 5) for t in TREAT}
    res["treatment_by_family"] = {f"{t}|{f}": cell(R[(R.technology_supergroup_4group == t) & (R.gene_family == f)], 10)
                                  for t in TREAT for f in FAM}
    res["percent_removal"] = dict(rows=len(P), studies=P.record_id.nunique(), rows_ge95=int((P.analysis_value >= 95).sum()),
                                  rows_ge99=int((P.analysis_value >= 99).sum()))

    # Risk-of-bias sensitivity: exclude outcomes linked to units at critical concern.
    excluded = set(crit.outcome_id)
    Rs = R[~R.outcome_id.isin(excluded)]
    res["rob_sensitivity"] = dict(
        excluded_outcomes=int(R.outcome_id.isin(excluded).sum()), rows=len(Rs), studies=Rs.record_id.nunique(),
        primary=cell(R[R.route == "influent_to_final_effluent"], 5),
        restricted=cell(Rs[Rs.route == "influent_to_final_effluent"], 5),
        family_restricted={f: cell(Rs[(Rs.route == "influent_to_final_effluent") & (Rs.gene_family == f)], 10) for f in FAM},
        treatment_primary={t: cell(R[R.technology_supergroup_4group == t], 5) for t in TREAT},
        treatment_restricted={t: cell(Rs[Rs.technology_supergroup_4group == t], 5) for t in TREAT})

    # Tier 2 (laboratory, bench or pilot), reported separately and descriptively.
    res["tier2"] = dict(rows=len(R_t2), studies=R_t2.record_id.nunique(),
                        route={r: cell(R_t2[R_t2.route == r], 999) for r in ROUTES},
                        treatment={t: cell(R_t2[R_t2.technology_supergroup_4group == t], 999) for t in TREAT})

    # All tiers pooled (sensitivity row in the route/treatment heterogeneity table).
    res["all_tiers_pooled"] = dict(rows=len(R_all), studies=R_all.record_id.nunique(),
                                   main_route=cell(R_all[R_all.route == "influent_to_final_effluent"], 5),
                                   route={r: cell(R_all[R_all.route == r], 5) for r in ROUTES[1:]},
                                   family_main_route={f: cell(R_all[(R_all.route == "influent_to_final_effluent") & (R_all.gene_family == f)], 10) for f in FAM})

    # Liquid abundance (log10 copies/mL-equivalent), six families in three matrices.
    L = A[A.gene_family.isin(FAM) & A.matrix_bucket.isin(MATRICES)]
    res["abundance_all_scales"] = {f"{f}|{m}": cell(L[(L.gene_family == f) & (L.matrix_bucket == m)], 999, "analysis_log10_value")
                                   for f in FAM for m in MATRICES}
    FS = tier1(L)
    res["abundance_full_scale"] = {f"{f}|{m}": cell(FS[(FS.gene_family == f) & (FS.matrix_bucket == m)], 999, "analysis_log10_value")
                                   for f in FAM for m in MATRICES}
    res["abundance_rows"] = dict(total_rows=len(A), total_studies=A.record_id.nunique(), summary_rows=len(L),
                                 full_scale_summary_rows=len(FS), full_scale_summary_studies=FS.record_id.nunique())

    # Route layer coverage.
    valid = X[X.valid_for_removal_synthesis == "Yes"]
    res["route_layer"] = dict(rows=len(X), studies=X.record_id.nunique(), valid_rows=len(valid),
                              valid_studies=valid.record_id.nunique(),
                              valid_studies_with_treatment_category=int(valid[valid.technology_supergroup_4group.isin(TREAT)].record_id.nunique()))

    # Influent characterization coverage in the 136-study quantitative core.
    S = pd.read_csv(DATA / "study_characteristics_quantitative_core_v4.csv")
    res["influent_quality_coverage"] = {v: dict(studies_with_data=int((S[f"{v}_status"] != "not_reported").sum()), denominator=len(S))
                                        for v in ["COD", "BOD", "TN", "NH4", "TP", "TSS", "pH"]}

    # Verification status of the synthesis datasets.
    res["verification_status"] = {name: d.verification_status.value_counts().to_dict()
                                  for name, d in [("log10_reduction_full_scale", R), ("percent_removal", P), ("liquid_abundance", A),
                                                  ("abundance_summaries", L)]}

    # Post hoc sensitivity: family-level pooling with a five-study threshold (main route, full-scale).
    rows = []
    for f in FAM:
        g = main_route[main_route.gene_family == f]
        k = g.record_id.nunique()
        r = meta_hksj(g) if k >= 5 else dict(studies=k, median=g.groupby("record_id")["analysis_value"].median().median())
        rows.append(dict(gene_family=f, pooled_in_primary_analysis="Yes" if k >= 10 else "No", **r))
    pd.DataFrame(rows).round(3).to_csv(OUT / "sensitivity_five_study_threshold.csv", index=False)

    # Percent removal by route and gene family (descriptive; bounded scale).
    pr = []
    for (r, f), g in P.groupby(["route", "gene_family"]):
        s = g.groupby("record_id")["analysis_value"].median()
        pr.append(dict(route=r, gene_family=f, studies=len(s), rows=len(g), median=s.median(), iqr_low=s.quantile(0.25),
                       iqr_high=s.quantile(0.75), min=s.min(), max=s.max(),
                       synthesis_mode="descriptive only" if len(s) >= 5 else "listed only"))
    pd.DataFrame(pr).round(4).to_csv(OUT / "percent_removal_by_route_and_gene_family.csv", index=False)

    # Write tables.
    rob = pd.DataFrame([dict(analysis="primary (all full-scale outcomes)", **res["rob_sensitivity"]["primary"]),
                        dict(analysis="restricted (outcomes from units at critical concern excluded)", **res["rob_sensitivity"]["restricted"])])
    rob.round(4).to_csv(OUT / "critical_appraisal_sensitivity_main_route.csv", index=False)
    table({f: v for f, v in res["rob_sensitivity"]["family_restricted"].items()}, ["gene_family"]).to_csv(
        OUT / "critical_appraisal_sensitivity_by_gene_family.csv", index=False)
    table(res["rob_sensitivity"]["treatment_primary"], ["treatment_category"]).assign(analysis="primary").to_csv(
        OUT / "critical_appraisal_sensitivity_by_treatment_primary.csv", index=False)
    table(res["rob_sensitivity"]["treatment_restricted"], ["treatment_category"]).assign(analysis="restricted").to_csv(
        OUT / "critical_appraisal_sensitivity_by_treatment_restricted.csv", index=False)
    table(res["tier2"]["treatment"], ["treatment_category"]).to_csv(OUT / "removal_tier2_by_treatment_category.csv", index=False)
    at = {"influent_to_final_effluent": res["all_tiers_pooled"]["main_route"], **res["all_tiers_pooled"]["route"]}
    table(at, ["route"]).to_csv(OUT / "removal_all_tiers_pooled_by_route.csv", index=False)
    table(res["family_main_route"], ["gene_family"]).to_csv(OUT / "removal_main_route_by_gene_family.csv", index=False)
    table(res["family_by_route"], ["gene_family", "route"]).to_csv(OUT / "removal_gene_family_by_route.csv", index=False)
    table(res["route"], ["route"]).to_csv(OUT / "removal_by_route.csv", index=False)
    table(res["treatment"], ["treatment_category"]).to_csv(OUT / "removal_by_treatment_category.csv", index=False)
    table(res["treatment_by_family"], ["treatment_category", "gene_family"]).to_csv(OUT / "removal_treatment_category_by_gene_family.csv", index=False)
    table(res["tier2"]["route"], ["route"]).to_csv(OUT / "removal_tier2_by_route.csv", index=False)
    table(res["abundance_full_scale"], ["gene_family", "matrix"]).to_csv(OUT / "abundance_full_scale_by_family_and_matrix.csv", index=False)
    table(res["abundance_all_scales"], ["gene_family", "matrix"]).to_csv(OUT / "abundance_all_scales_by_family_and_matrix.csv", index=False)
    with open(OUT / "results_summary.json", "w") as fh:
        json.dump(clean(res), fh, indent=1)
    rs = res["route"]["influent_to_final_effluent"]
    print(f"Influent -> final effluent (full-scale): median {rs['median']:.2f} log10 "
          f"(bootstrap 95% CI {rs['bootstrap_ci_low']:.2f}-{rs['bootstrap_ci_high']:.2f}), {rs['studies']} studies; "
          f"DL {rs['dl']:.2f} ({rs['dl_ci_low']:.2f}-{rs['dl_ci_high']:.2f}), I2 {rs['i2_percent']:.1f}%")
    print("Results written to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
