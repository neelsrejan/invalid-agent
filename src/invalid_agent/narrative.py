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


def _banner(facts: dict[str, Any]) -> str:
    return str(facts.get("banner") or "Simulation. Synthetic data. Not for clinical use.")


def _rate_sentence(facts: dict[str, Any]) -> str:
    overall = facts["overall"]
    if facts.get("spec_estimable", True) is False:
        return (
            f"Invalid-type share of reported events **{_pct(overall, 'rate_pct')}** "
            f"({overall['k']} of {overall['n']} reports), "
            f"Wilson 95% CI **{_pct(overall, 'ci_low_pct')}–{_pct(overall, 'ci_high_pct')}**. "
            f"Promised validity **{_pct(overall, 'promised_pct')}** would cap a run-level invalid rate at "
            f"**{_pct(overall, 'spec_pct')}**. That cap is not estimable here: the denominator is "
            "device-event reports, not test runs."
        )
    return (
        f"Invalid rate **{_pct(overall, 'rate_pct')}** "
        f"({overall['k']} of {overall['n']}), "
        f"Wilson 95% CI **{_pct(overall, 'ci_low_pct')}–{_pct(overall, 'ci_high_pct')}**. "
        f"Promised validity **{_pct(overall, 'promised_pct')}**, "
        f"so the invalid rate must stay at or below **{_pct(overall, 'spec_pct')}**."
    )


def triage_memo(facts: dict[str, Any]) -> str:
    overall = facts["overall"]
    decision = "Escalate" if facts["escalate"] else "Do not escalate"
    lines = [
        "# Week-0 triage memo",
        "",
        f"**{_banner(facts)}**",
        "",
        f"Scenario `{facts['scenario_id']}` · {facts['device']} · investigation week {facts['week']}.",
        "",
        "## Decision",
        "",
        _rate_sentence(facts),
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
    order = facts.get("strata_order") or [
        {"column": "reagent_lot", "label": "Lot"},
        {"column": "instrument", "label": "Instrument"},
        {"column": "site", "label": "Site"},
        {"column": "software_version", "label": "Software"},
    ]
    for item in order:
        label = item["label"]
        key = item["column"]
        rows = facts["strata"].get(key) or []
        if not rows:
            continue
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


def _status_header(facts: dict[str, Any], title: str) -> list[str]:
    overall = facts["overall"]
    if facts.get("spec_estimable", True) is False:
        rate_line = (
            f"Invalid-type share of reported events {overall['rate_pct']:.2f}% "
            f"({overall['k']} of {overall['n']} reports), "
            f"Wilson 95% CI {overall['ci_low_pct']:.2f}–{overall['ci_high_pct']:.2f}%. "
            f"Promised validity {overall['promised_pct']:.2f}% would cap a run-level invalid rate at {overall['spec_pct']:.2f}%. "
            "That cap is not estimable from reported events."
        )
    else:
        rate_line = (
            f"Invalid rate {overall['rate_pct']:.2f}% ({overall['k']} of {overall['n']}), "
            f"Wilson 95% CI {overall['ci_low_pct']:.2f}–{overall['ci_high_pct']:.2f}%. "
            f"Promised validity {overall['promised_pct']:.2f}%, so the invalid rate must stay at or below {overall['spec_pct']:.2f}%."
        )
    return [
        f"# {title}",
        "",
        f"**{_banner(facts)}**",
        "",
        f"Investigation week {facts['week']}. RAG: {facts['rag']}.",
        "",
        rate_line,
        "",
    ]


def status_customer(facts: dict[str, Any]) -> str:
    lines = _status_header(facts, "Customer update")
    lines.extend(
        [
            facts["customer_action"],
            "",
            "This note does not state a confirmed cause. We will write again when the next week's evidence is in.",
            "",
        ]
    )
    return "\n".join(lines)


def status_internal(facts: dict[str, Any]) -> str:
    lines = _status_header(facts, "Internal update")
    hypo = facts["hypothesis"]
    lines.append(
        f"Leading hypothesis: {hypo['category']} / {hypo['cause']} / {hypo['level']}. "
        "This is a ranking, not a confirmed cause."
    )
    lines.append("")
    if hypo.get("prose"):
        lines.append(hypo["prose"])
        lines.append("")
    lines.append("Evidence: " + ", ".join(hypo.get("evidence_ids") or []) + ".")
    lines.append("")
    lines.append(f"Plan version {facts['plan_version']}. Tasks in progress are marked on the Jira dry-run.")
    lines.append("")
    if facts.get("injection_texts"):
        lines.append("Stakeholder notes in scope:")
        lines.append("")
        for text in facts["injection_texts"]:
            lines.append(f"- {text}")
        lines.append("")
    return "\n".join(lines)


def status_leadership(facts: dict[str, Any]) -> str:
    lines = _status_header(facts, "Leadership update")
    cost = facts["cost"]
    lines.extend(
        [
            (
                f"Cost of invalids in the field file: {cost['total_usd']} dollars "
                f"({cost['k']} invalids at {cost['unit_usd']} dollars)."
            ),
            "",
            facts["ask"],
            "",
            "The ask is a decision on containment scope. It is not a request to close the CAPA.",
            "",
        ]
    )
    if facts.get("cost_basis"):
        lines.extend([str(facts["cost_basis"]), ""])
    return "\n".join(lines)


def data_answer(facts: dict[str, Any]) -> str:
    head = facts["head"]
    lines = [
        "# Data answer",
        "",
        f"**{_banner(facts) if facts.get('banner') else 'Public openFDA MAUDE device-event reports. Not for clinical use.'}**",
        "",
        facts["denominator_note"],
        "",
        (
            f"Product code {facts['product_code']} from {facts['date_from']} to {facts['date_to']}. "
            f"Template {facts['template_id']}."
        ),
        "",
        (
            f"Leading figure: {head['k']} of {head['n']} "
            f"({head['rate'] * 100:.2f}%), "
            f"Wilson 95% CI {head['ci_low'] * 100:.2f}%–{head['ci_high'] * 100:.2f}%."
        ),
        (
            f"Stated run-level promise: invalid cap {facts['spec_invalid_rate'] * 100:.2f}% "
            f"(validity at least {facts['promised_validity'] * 100:.2f}%). "
            "Not estimable from reported events."
        ),
        "",
    ]
    shown = 0
    for row in facts.get("rows") or []:
        if "level" not in row:
            continue
        lines.append(
            f"- {row['level']}: {row['k']} of {row['n']} ({row['rate'] * 100:.2f}%)."
        )
        shown += 1
        if shown == 5:
            break
    spc = facts.get("spc") or {}
    if spc:
        lines.append(
            f"Weekly points: {spc['points']}. Western Electric rule 1 count: {spc['rule1_count']} "
            f"(any rule: {spc['violation_count']}). Pooled share {spc['p_bar'] * 100:.2f}%."
        )
    lines.append("")
    lines.append("Python computed every figure above. The model only chose a vetted template and may phrase this note.")
    lines.append("")
    return "\n".join(lines)


TEMPLATES = {
    "triage": triage_memo,
    "status_customer": status_customer,
    "status_internal": status_internal,
    "status_leadership": status_leadership,
    "data_answer": data_answer,
}
