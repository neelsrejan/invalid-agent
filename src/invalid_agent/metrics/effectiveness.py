"""Projected rate if the leading stratum is removed.

This is a counterfactual on the same file. It is not observed follow-up
after a field action. Callers have to say that in the label.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from invalid_agent.metrics.hypotheses import with_bands
from invalid_agent.metrics.rates import overall_rate


def project_without_leading_stratum(df: pd.DataFrame, hypothesis: dict[str, Any]) -> tuple[pd.DataFrame, bool]:
    """Return a copy with that stratum's invalids cleared, and whether a change was applied."""
    framed = with_bands(df.copy())
    column = hypothesis.get("column")
    level = hypothesis.get("level")
    if not column or level is None or column not in framed.columns:
        return framed, False
    mask = framed[column].astype(str) == str(level)
    if not bool(mask.any()):
        return framed, False
    framed.loc[mask, "invalid"] = False
    if "invalid_code" in framed.columns:
        framed.loc[mask, "invalid_code"] = ""
    return framed, True


def projection_summary(df: pd.DataFrame, hypothesis: dict[str, Any], spec: float, promised: float = 0.98) -> dict[str, Any]:
    projected, applied = project_without_leading_stratum(df, hypothesis)
    before = overall_rate(df, spec, promised)
    after = overall_rate(projected, spec, promised)
    return {
        "applied": applied,
        "before": before,
        "after": after,
        "label": "Projected if the leading stratum is removed. Not observed follow-up.",
        "frame": projected,
    }
