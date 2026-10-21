"""Templates the deterministic backend fills, and the prompt the model sees.

Templates may only interpolate values that already live on ``facts``.
The fidelity guard checks the result either way.
"""

from __future__ import annotations

import json
from typing import Any

SYSTEM_PROMPT = (
    "You are drafting a field-quality note for a simulation. "
    "It is not for clinical use. Use only numbers that appear in FACTS. "
    "Do not invent rates, intervals, counts, costs, or dates. "
    "Do not state a root cause as confirmed if FACTS says it is a hypothesis. "
    "Write plain sentences a program manager can send."
)


def prompt_for(task: str, facts: dict[str, Any]) -> str:
    return (
        f"TASK: {task}\n"
        "Write the artifact described by TASK. Quote numbers exactly as they appear in FACTS.\n"
        "FACTS:\n"
        + json.dumps(facts, indent=2, default=str)
    )


def render(task: str, facts: dict[str, Any]) -> str:
    renderer = TEMPLATES[task]
    return renderer(facts)


def _pct(facts_overall: dict[str, Any], key: str) -> str:
    return f"{facts_overall[key]:.2f}%"


def triage_memo(facts: dict[str, Any]) -> str:
    overall = facts["overall"]
    decision = "Escalate" if facts["escalate"] else "Do not escalate"
    lines = [
        "# Week-0 triage memo",
        "",
        "**Simulation. Synthetic data. Not for clinical use.**",
        "",
        f"Scenario `{facts['scenario_id']}` · {facts['device']} · investigation week {facts['week']}.",
        "",
        "## Decision",
        "",
        (
            f"Invalid rate **{_pct(overall, 'rate_pct')}** "
            f"({overall['k']} of {overall['n']}), "
            f"Wilson 95% CI **{_pct(overall, 'ci_low_pct')}–{_pct(overall, 'ci_high_pct')}**. "
            f"Promised validity **{_pct(overall, 'promised_pct')}**, "
            f"so the invalid rate must stay at or below **{_pct(overall, 'spec_pct')}**."
        ),
        "",
        f"**{decision}.** Severity: {facts['severity']}.",
        "",
        "## Complaint",
        "",
        facts["complaint"].strip(),
        "",
        "## Where the invalids concentrate",
        "",
    ]
    for label, key in (
        ("Lot", "reagent_lot"),
        ("Instrument", "instrument"),
        ("Site", "site"),
        ("Software", "software_version"),
    ):
        rows = facts["strata"][key]
        rendered = ", ".join(
            f"{row['level']} {_pct(row, 'rate_pct')} (n={row['n']}, k={row['k']})" for row in rows
        )
        lines.append(f"- {label}: {rendered}")
    head = facts["pareto"]
    if head:
        pareto_text = ", ".join(f"{row['code']} {_pct(row, 'share_pct')}" for row in head)
        lines.append(f"- Invalid-code Pareto (head): {pareto_text}")
    spc = facts["spc"]
    lines.append(
        f"- Weekly p-chart p-bar {_pct(spc, 'p_bar_pct')}. "
        f"Western Electric rule 1 points: {spc['rule1_count']} "
        f"(any rule: {spc['violation_count']})."
    )
    lines.extend(["", "## Initial hypotheses", ""])
    lines.append(
        "These are ranked from the strata (lift, excess invalids, chi-square). "
        "They are not a confirmed root cause. "
        "A cause that does not clear that bar is left off this list on purpose."
    )
    lines.append("")
    for index, item in enumerate(facts["hypotheses"], start=1):
        lines.append(f"{index}. {item['prose']}")
        if item.get("evidence_ids"):
            lines.append(f"   Evidence: {', '.join(item['evidence_ids'])}.")
    lines.extend(
        [
            "",
            "## What the numbers are",
            "",
            "Every figure above was computed in Python (Wilson interval, strata, p-chart, Pareto). "
            "A language model, if one is configured, is only allowed to phrase them. "
            "A figure that is not in the computed set is rejected.",
            "",
        ]
    )
    return "\n".join(lines)


TEMPLATES = {
    "triage": triage_memo,
}
