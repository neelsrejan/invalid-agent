"""RAG status notes for three audiences, plus the decision log.

Customer copy does not state a cause as fact. Internal copy names the
hypothesis and the evidence ids. Leadership copy leads with RAG, cost,
and the ask. All three go through the numeric-fidelity guard.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from invalid_agent.case.state import CaseState
from invalid_agent.config import load_settings
from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.llm import get_llm, narrate
from invalid_agent.nodes.rca import index_injections


def rag_color(exceeds_spec: bool, week: int) -> str:
    if not exceeds_spec:
        return "Green"
    if week >= 3:
        return "Amber"
    return "Red"


def _pct(value: float) -> float:
    return round(float(value) * 100.0, 2)


def _customer_action(week: int) -> str:
    actions = {
        0: "We are checking the rate against the commitment. No panel-wide stop is requested today.",
        1: "One lot is under review. Please keep running the other lots that are still in your inventory.",
        2: "The written note your lab director asked for is in this week's plan. The review is still limited to one lot.",
        3: "Containment is in progress on the lot under review. Lots that stayed inside the spec are not in the hold.",
        4: "A recommendation is being prepared. This note still does not state a confirmed cause.",
    }
    return actions.get(week, actions[4])


def _ask(week: int) -> str:
    if week >= 3:
        return "Ask: approve containment on the leading stratum, and do not approve a panel-wide stop."
    if week >= 2:
        return "Ask: approve the lab-director note and hold a panel-wide stop until the field table is challenged."
    return "Ask: approve the investigation plan and a holding response. No field action beyond the review yet."


def _decision(week: int, top: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    cause = str(top.get("cause") or "no_single_cause")
    level = str(top.get("level") or "no single stratum")
    if week == 0:
        text = f"Escalate and open the plan. Leading hypothesis is {cause} on {level}."
    elif week == 1:
        text = "Keep the leading hypothesis. The new QA note is a citation. It does not get its own score."
    elif week == 2:
        text = "Keep the field ranking after release testing was reported as a pass. Add the lab-director note to the plan."
    elif week == 3:
        text = "Do not switch the cause onto the shipping note. Execute containment on the leading stratum and size the cost."
    else:
        text = "Prepare the recommendation from the leading hypothesis and the effectiveness check."
    return {
        "week": week,
        "decision": text,
        "evidence_ids": list(top.get("evidence_ids") or ["metric:overall:rate"]),
        "plan_version": int(plan.get("version", 1)),
        "cause": cause,
        "level": level,
    }


def upsert_decision(log: list[dict[str, Any]], entry: dict[str, Any]) -> list[dict[str, Any]]:
    kept = [row for row in log if int(row["week"]) != int(entry["week"])]
    kept.append(entry)
    kept.sort(key=lambda row: int(row["week"]))
    return kept


def render_decision_log(log: list[dict[str, Any]]) -> str:
    lines = [
        "# Decision log",
        "",
        "**Simulation. Synthetic data. Not for clinical use.**",
        "",
    ]
    for entry in log:
        lines.append(f"## Week {entry['week']}")
        lines.append("")
        lines.append(entry["decision"])
        lines.append("")
        lines.append("Evidence: " + ", ".join(entry.get("evidence_ids") or []) + ".")
        lines.append("")
        lines.append(f"Plan version {entry['plan_version']}.")
        lines.append("")
    return "\n".join(lines)


def build_status_facts(state: CaseState) -> dict[str, Any]:
    scenario = state["scenario"]
    week = int(state["week"])
    overall = state["metrics"]["overall"]
    top = (state.get("hypotheses") or [{}])[0]
    plan = state.get("plan") or {"version": 1}
    unit = int(scenario.get("cost_per_invalid_usd", 85))
    invalids = int(overall["k"])
    injections = index_injections(scenario, week)
    return {
        "week": week,
        "rag": rag_color(bool(overall["exceeds_spec"]), week),
        "overall": {
            "n": int(overall["n"]),
            "k": invalids,
            "rate": overall["rate"],
            "rate_pct": _pct(overall["rate"]),
            "ci_low": overall["ci_low"],
            "ci_high": overall["ci_high"],
            "ci_low_pct": _pct(overall["ci_low"]),
            "ci_high_pct": _pct(overall["ci_high"]),
            "spec_invalid_rate": overall["spec_invalid_rate"],
            "promised_validity": overall["promised_validity"],
            "spec_pct": _pct(overall["spec_invalid_rate"]),
            "promised_pct": _pct(overall["promised_validity"]),
            "confidence": overall.get("confidence", 0.95),
            "exceeds_spec": overall["exceeds_spec"],
        },
        "hypothesis": {
            "cause": str(top.get("cause") or "no_single_cause"),
            "category": str(top.get("category") or "Unresolved"),
            "level": str(top.get("level") or "none"),
            "prose": str(top.get("summary") or ""),
            "evidence_ids": list(top.get("evidence_ids") or []),
            "lift": None if top.get("lift") is None else round(float(top["lift"]), 2),
            "rate_pct": None if top.get("rate") is None else _pct(top["rate"]),
        },
        "plan_version": int(plan.get("version", 1)),
        "customer_action": _customer_action(week),
        "ask": _ask(week),
        "injection_texts": list(injections.values()),
        "cost": {"k": invalids, "unit_usd": unit, "total_usd": invalids * unit},
        "structure": [0, 1, 2, 3, 4, 5],
    }


def status_node(state: CaseState) -> dict[str, Any]:
    facts = build_status_facts(state)
    llm = get_llm()
    updates: dict[str, str] = {}
    fidelity: dict[str, Any] = {}
    for audience, task in (
        ("customer", "status_customer"),
        ("internal", "status_internal"),
        ("leadership", "status_leadership"),
    ):
        prose, record = narrate(task, facts, llm)
        checked = check_narrative(prose, facts)
        if not checked.ok:
            raise RuntimeError(f"{audience} status failed the fidelity guard: {checked.unknown}")
        updates[audience] = prose
        fidelity[audience] = record
    entry = _decision(int(state["week"]), (state.get("hypotheses") or [{}])[0], state.get("plan") or {})
    log = upsert_decision(list(state.get("decision_log") or []), entry)
    _write(state, updates, log)
    return {
        "status_updates": updates,
        "status_fidelity": fidelity,
        "decision_log": log,
    }


def _write(state: CaseState, updates: dict[str, str], log: list[dict[str, Any]]) -> None:
    settings = load_settings()
    out = Path(state["out_dir"]) if state.get("out_dir") else settings.out_dir
    week = int(state["week"])
    folders = [out, out / f"week{week}"]
    log_text = render_decision_log(log)
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        for audience, prose in updates.items():
            (folder / f"status_{audience}.md").write_text(prose, encoding="utf-8")
        (folder / "decision_log.md").write_text(log_text, encoding="utf-8")
