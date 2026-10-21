"""Likelihood × impact risk register. Score is the product, not a feeling."""

from __future__ import annotations

from typing import Any


def render_risk_register(risks: list[dict[str, Any]], week: int) -> str:
    lines = [
        "# Risk register",
        "",
        "**Simulation. Synthetic data. Not for clinical use.**",
        "",
        f"Investigation week {week}. Score = likelihood × impact, each on a 1–5 scale.",
        "",
        "| ID | Risk | L | I | Score | Owner | Trend | Mitigation |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for risk in risks:
        lines.append(
            "| {id} | {risk} | {likelihood} | {impact} | {score} | {owner} | {trend} | {mitigation} |".format(
                **risk
            )
        )
    lines.append("")
    return "\n".join(lines)
