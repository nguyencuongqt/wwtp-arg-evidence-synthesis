"""Reproduce the human-audit agreement statistics reported in the manuscript.

Run from the repository root:

    python scripts/audit_agreement.py

Inputs are the human decision records in audit/:
- eligibility_reassessment_95_studies.csv: 94 studies assessed independently by X.C.N. and T.U.
  (one further study, R0451, was assessed by X.C.N. only);
- final_value_audit_491_values.csv: first-reviewer (X.C.N.) decisions on the 491 values that entered a
  reported synthesis without an earlier individual check;
- final_value_audit_second_reviewer_100.csv: blinded re-check of a stratified random sample of 100 of those
  values by the second reviewer (T.U.).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
KEEP = {"Correct", "Corrected"}


def kappa(a: pd.Series, b: pd.Series) -> float:
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = (a.values == b.values).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return c - h, c + h


def main() -> None:
    el = pd.read_csv(AUDIT / "eligibility_reassessment_95_studies.csv")
    both = el[el.reviewer_TU_decision != "not assessed"]
    inc = lambda s: s.where(s == "Exclude", "Include")
    print(f"Eligibility re-assessment: {len(el)} studies; {len(both)} assessed by both reviewers")
    print(f"  three-category agreement (core, supporting, exclude) {(both.reviewer_XCN_decision == both.reviewer_TU_decision).mean():.1%}, "
          f"Cohen's kappa {kappa(both.reviewer_XCN_decision, both.reviewer_TU_decision):.2f}")
    print(f"  include/exclude agreement {(inc(both.reviewer_XCN_decision) == inc(both.reviewer_TU_decision)).mean():.1%}, "
          f"Cohen's kappa {kappa(inc(both.reviewer_XCN_decision), inc(both.reviewer_TU_decision)):.2f}")
    print(f"  excluded after reconciliation: {(el.final_decision == 'Exclude').sum()}")

    va = pd.read_csv(AUDIT / "final_value_audit_491_values.csv")
    kept = va.decision.isin(KEEP).sum()
    ctx = (~va.decision.isin(KEEP)).sum()
    corr = (va.decision == "Corrected").sum()
    lo, hi = wilson(ctx, len(va))
    lo2, hi2 = wilson(corr, len(va))
    print(f"Final value audit: {len(va)} values; retained {kept} ({(va.decision == 'Correct').sum()} confirmed, {corr} corrected)")
    print(f"  unusable {ctx} ({ctx / len(va):.1%}; Wilson 95% CI {lo:.1%}-{hi:.1%}); corrected {corr / len(va):.1%} ({lo2:.1%}-{hi2:.1%})")
    print("  " + "; ".join(f"{k}: {v}" for k, v in va.decision.value_counts().items()))

    sc = pd.read_csv(AUDIT / "final_value_audit_second_reviewer_100.csv")
    nd = sc[sc.first_reviewer_XCN != "Duplicate row"].copy()
    # In one duplicate pair the reviewers kept opposite copies of the same value; this row counts as agreement.
    second = nd.second_reviewer_TU.where(~nd.agreement.str.startswith("agree"), nd.first_reviewer_XCN)
    print(f"Second-reviewer check: {len(sc)} values; {len(nd)} after excluding rows marked as duplicates")
    print(f"  category agreement {(nd.first_reviewer_XCN == second).mean():.1%}, kappa {kappa(nd.first_reviewer_XCN, second):.2f}")
    b1, b2 = nd.first_reviewer_XCN.isin(KEEP).map({True: "keep", False: "remove"}), second.isin(KEEP).map({True: "keep", False: "remove"})
    print(f"  keep/remove agreement {(b1 == b2).mean():.1%}, kappa {kappa(b1, b2):.2f}")
    print(f"  second reviewer agreed on {((b1 == 'keep') & (b2 == 'keep')).sum()} of {(b1 == 'keep').sum()} kept and "
          f"{((b1 == 'remove') & (b2 == 'remove')).sum()} of {(b1 == 'remove').sum()} removed values")


if __name__ == "__main__":
    main()
