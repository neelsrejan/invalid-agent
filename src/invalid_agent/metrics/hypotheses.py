"""Rank root-cause hypotheses from strata. No language model.

A cause is allowed into the ranking only when three gates all pass:

- the stratum has at least ``min_n`` runs and at least ``min_excess`` extra invalids
  versus the complement rate
- the rate ratio (lift) is at least ``min_lift``
- a 2×2 chi-square test has p < ``alpha``

If the top two passing causes are within ``close_call_ratio`` of each other, the
call is ``no_single_cause``. A loud stakeholder sentence cannot create a score;
this function never reads injections.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd
from scipy import stats

from invalid_agent.metrics.rates import overall_rate, stratified_rates
from invalid_agent.metrics.spc import p_chart

CAUSE_CATEGORY = {
    "bad_reagent_lot": "Material",
    "drifting_instrument": "Machine",
    "site_temperature": "Environment",
    "software_version": "Method",
    "preanalytical_hemolysis": "Material",
    "user_process_error": "Man",
    "no_single_cause": "Unresolved",
}

_COLUMN_CAUSE = (
    ("reagent_lot", "bad_reagent_lot"),
    ("instrument", "drifting_instrument"),
    ("software_version", "software_version"),
    ("operator", "user_process_error"),
    ("temp_band", "site_temperature"),
    ("hil_band", "preanalytical_hemolysis"),
)

MIN_N = 80
MIN_LIFT = 1.8
MIN_EXCESS = 15.0
ALPHA = 0.01
CLOSE_CALL_RATIO = 0.80
TEMP_EXCURSION_C = 30.0
HIL_CUTOFF = 100.0


def with_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Add temperature and hemolysis bands used as strata. Does not copy first."""
    out = df
    out["temp_band"] = [
        "excursion" if float(value) >= TEMP_EXCURSION_C else "controlled" for value in out["shipping_temp_c"]
    ]
    out["hil_band"] = ["high" if float(value) >= HIL_CUTOFF else "typical" for value in out["hemolysis_index"]]
    return out


def _best_level(df: pd.DataFrame, column: str) -> dict[str, Any] | None:
    if column not in df.columns:
        return None
    invalid = df["invalid"].astype(bool)
    best: dict[str, Any] | None = None
    for level, sub in df.groupby(column, dropna=False):
        n = int(len(sub))
        if n < MIN_N:
            continue
        k = int(invalid.loc[sub.index].sum())
        complement = df.loc[df[column] != level]
        cn = int(len(complement))
        if cn < MIN_N:
            continue
        ck = int(invalid.loc[complement.index].sum())
        rate = k / n
        complement_rate = ck / cn if cn else 0.0
        if rate <= complement_rate:
            continue
        table = [[k, n - k], [ck, cn - ck]]
        _chi2, p_value, _dof, _expected = stats.chi2_contingency(table)
        lift = rate / complement_rate if complement_rate > 0 else math.inf
        excess = k - complement_rate * n
        if p_value >= ALPHA or lift < MIN_LIFT or excess < MIN_EXCESS:
            score = 0.0
        else:
            score = (lift - 1.0) * math.log1p(excess) * (-math.log10(max(float(p_value), 1e-300)))
        if score <= 0.0:
            continue
        row = {
            "column": column,
            "level": str(level),
            "n": n,
            "k": k,
            "rate": rate,
            "complement_n": cn,
            "complement_k": ck,
            "complement_rate": complement_rate,
            "lift": lift,
            "p_value": float(p_value),
            "excess": excess,
            "score": float(score),
            "evidence_ids": [
                f"metric:{column}:{level}:rate",
                f"metric:{column}:{level}:lift",
                f"metric:overall:rate",
            ],
        }
        if best is None or row["score"] > best["score"]:
            best = row
    return best


def rank_hypotheses(df: pd.DataFrame, spec_invalid_rate: float = 0.02) -> list[dict[str, Any]]:
    """Highest score first. Index 0 is the call, including a possible no-single-cause call."""
    framed = with_bands(df.copy())
    found: list[dict[str, Any]] = []
    for column, cause in _COLUMN_CAUSE:
        best = _best_level(framed, column)
        if best is None:
            continue
        best["cause"] = cause
        best["category"] = CAUSE_CATEGORY[cause]
        best["summary"] = (
            f"{best['level']} {cause.replace('_', ' ')} rate is above the complement "
            f"with lift {best['lift']:.2f}"
        )
        found.append(best)
    found.sort(key=lambda row: (-row["score"], row["cause"]))
    if not found:
        return [_unresolved(framed, spec_invalid_rate, "No stratum cleared the evidence bar.")]
    if len(found) >= 2 and found[1]["score"] >= CLOSE_CALL_RATIO * found[0]["score"]:
        unresolved = _unresolved(
            framed,
            spec_invalid_rate,
            "Two causes cleared the evidence bar with similar scores, so this is not a single-cause call.",
        )
        unresolved["contenders"] = [found[0]["cause"], found[1]["cause"]]
        return [unresolved, *found]
    return found


def _unresolved(df: pd.DataFrame, spec_invalid_rate: float, summary: str) -> dict[str, Any]:
    overall = overall_rate(df, spec_invalid_rate)
    return {
        "cause": "no_single_cause",
        "category": "Unresolved",
        "column": None,
        "level": None,
        "n": overall["n"],
        "k": overall["k"],
        "rate": overall["rate"],
        "complement_rate": None,
        "lift": None,
        "p_value": None,
        "excess": None,
        "score": 0.0,
        "summary": summary,
        "evidence_ids": ["metric:overall:rate", "metric:overall:ci", "metric:overall:spec"],
        "contenders": [],
    }


def evidence_catalog(df: pd.DataFrame, spec_invalid_rate: float = 0.02, promised_validity: float = 0.98) -> dict[str, str]:
    """Id → sentence. A 5 Whys citation has to be one of these keys."""
    framed = with_bands(df.copy())
    overall = overall_rate(framed, spec_invalid_rate, promised_validity)
    catalog = {
        "metric:overall:rate": (
            f"Overall invalid rate {overall['rate'] * 100:.2f}% "
            f"({overall['k']} of {overall['n']})."
        ),
        "metric:overall:ci": (
            f"Wilson 95% CI {overall['ci_low'] * 100:.2f}% to {overall['ci_high'] * 100:.2f}%."
        ),
        "metric:overall:spec": (
            f"Spec is an invalid rate at or below {spec_invalid_rate * 100:.2f}% "
            f"(promised validity at least {promised_validity * 100:.2f}%)."
        ),
    }
    for column in ("reagent_lot", "instrument", "site", "software_version", "operator", "temp_band", "hil_band"):
        for row in stratified_rates(framed, column):
            catalog[f"metric:{column}:{row['level']}:rate"] = (
                f"{column} {row['level']} invalid rate {row['rate'] * 100:.2f}% ({row['k']} of {row['n']})."
            )
            catalog[f"metric:{column}:{row['level']}:n"] = f"{column} {row['level']} has {row['n']} runs."
    chart = p_chart(framed)
    rule1 = sum(1 for hit in chart["violations"] if hit["rule"] == 1)
    catalog["spc:rule1"] = f"Western Electric rule 1 fired on {rule1} weekly points."
    catalog["spc:p_bar"] = f"Pooled weekly invalid rate (p-bar) is {chart['p_bar'] * 100:.2f}%."
    return catalog
