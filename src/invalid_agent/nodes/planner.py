"""Four-week investigation plan and the risk register.

Dates are computed from the day the synthetic field window ends. A task's
start is never earlier than the end of a task it depends on. Cause-specific
work is an extra task, not a rewrite of the whole plan. Week 2 adds the
lab-director note; that is the Gantt diff the test looks for.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from invalid_agent.artifacts.gantt import write_gantt
from invalid_agent.artifacts.risk_register import render_risk_register
from invalid_agent.case.state import CaseState
from invalid_agent.config import load_settings
from invalid_agent.integrations.jira import make_client

_OWNER = {
    "bad_reagent_lot": "QA",
    "drifting_instrument": "Manufacturing",
    "site_temperature": "Manufacturing",
    "software_version": "R&D",
    "preanalytical_hemolysis": "QA",
    "user_process_error": "QA",
    "measurement_system": "R&D",
    "no_single_cause": "PM",
}


def investigation_start(scenario: dict[str, Any]) -> date:
    if scenario.get("investigation_start"):
        return date.fromisoformat(str(scenario["investigation_start"]))
    origin = date.fromisoformat(str(scenario.get("start_date", "2025-04-01")))
    return origin + timedelta(days=int(scenario.get("horizon_days", 180)))


def _task(
    task_id: str,
    name: str,
    owner: str,
    start: date,
    days: int,
    depends_on: list[str],
    sim_week: int,
) -> dict[str, Any]:
    return {
        "id": task_id,
        "name": name,
        "owner": owner,
        "start": start.isoformat(),
        "end": (start + timedelta(days=days)).isoformat(),
        "depends_on": depends_on,
        "sim_week": sim_week,
        "status": "To Do",
    }


def build_plan(scenario: dict[str, Any], top: dict[str, Any], week: int) -> dict[str, Any]:
    start = investigation_start(scenario)
    cause = str(top.get("cause") or "no_single_cause")
    level = str(top.get("level") or "the leading stratum")
    owner = _OWNER.get(cause, "PM")
    # 28-day window: intake, trace, challenge, contain, recommend.
    tasks = [
        _task("T1", "Confirm rate, interval, and strata", "QA", start, 3, [], 0),
        _task("T2", "Send the holding response to the customer", "Customer Support", start + timedelta(days=3), 3, ["T1"], 0),
        _task("T3", f"Containment decision for {level}", owner, start + timedelta(days=3), 4, ["T1"], 0),
        _task("T4", "Fishbone review across QA, R&D, and Manufacturing", "PM", start + timedelta(days=7), 3, ["T1"], 1),
        _task("T5", f"Trace {cause} for {level}", owner, start + timedelta(days=10), 5, ["T4"], 1),
        _task("T6", "5 Whys on the top branch", "QA", start + timedelta(days=15), 3, ["T5"], 2),
        _task("T7", "Retest the next-best stratum", "R&D", start + timedelta(days=14), 4, ["T4"], 2),
        _task("T8", "Execute containment", owner, start + timedelta(days=18), 6, ["T3", "T6"], 3),
        _task("T9", "Size the cost of the invalids and of the field action", "PM", start + timedelta(days=18), 3, ["T1"], 3),
        _task("T10", "Effectiveness check and recommendation", "PM", start + timedelta(days=26), 2, ["T8"], 4),
    ]
    if week >= 2:
        tasks.append(
            _task(
                "T11",
                "Written update for the lab director",
                "PM",
                start + timedelta(days=14),
                2,
                ["T2"],
                2,
            )
        )
    if week >= 3:
        tasks.append(
            _task(
                "T12",
                "Lane-temperature review against the field rates",
                "Manufacturing",
                start + timedelta(days=21),
                3,
                ["T5"],
                3,
            )
        )
    for task in tasks:
        if task["sim_week"] < week:
            task["status"] = "Done"
        elif task["sim_week"] == week:
            task["status"] = "In Progress"
        else:
            task["status"] = "To Do"
    _assert_dependencies(tasks)
    return {
        "scenario_id": str(scenario.get("id", "scenario")),
        "version": 1 if week < 2 else 2,
        "start": start.isoformat(),
        "horizon_days": 28,
        "top_cause": cause,
        "top_level": level,
        "tasks": tasks,
    }


def _assert_dependencies(tasks: list[dict[str, Any]]) -> None:
    by_id = {task["id"]: task for task in tasks}
    for task in tasks:
        for dep_id in task["depends_on"]:
            dep = by_id[dep_id]
            if task["start"] < dep["end"]:
                raise ValueError(f"{task['id']} starts before {dep_id} ends")


def _risk(
    risk_id: str,
    text: str,
    likelihood: int,
    impact: int,
    owner: str,
    trend: str,
    mitigation: str,
) -> dict[str, Any]:
    return {
        "id": risk_id,
        "risk": text,
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "owner": owner,
        "trend": trend,
        "mitigation": mitigation,
    }


def build_risks(top: dict[str, Any], week: int) -> list[dict[str, Any]]:
    """Week 0 is the opening register. Later weeks move likelihood and add rows."""
    cause = str(top.get("cause") or "no_single_cause")
    level = str(top.get("level") or "a stratum")
    opening = "new" if week == 0 else "stable"
    misread_trend = "new" if week == 0 else ("down" if cause != "no_single_cause" and week >= 2 else "stable")
    misread_l = 3 if week < 2 or cause == "no_single_cause" else 2
    risks = [
        _risk(
            "R1",
            f"A field action hits the wrong stratum instead of {level}.",
            misread_l,
            4,
            "PM",
            misread_trend,
            "Do not quarantine until the stratum clears the evidence bar.",
        ),
        _risk(
            "R2",
            "The customer stops the whole panel rather than the implicated stratum.",
            3,
            5,
            "Customer Support",
            opening if week < 2 else "stable",
            "The holding note names what is still inside the spec.",
        ),
        _risk(
            "R3",
            "The invalid rate stays above the spec for another week of production.",
            4,
            4,
            "QA",
            opening,
            "Containment is a dated task, not a slide.",
        ),
    ]
    if week >= 2:
        risks.append(
            _risk(
                "R4",
                "Release testing passed while the field rate did not, so the cause is disputed.",
                4,
                3,
                "R&D",
                "up",
                "Treat release data as a citation, not as a veto of the field table.",
            )
        )
    if week >= 3:
        risks.append(
            _risk(
                "R5",
                "A shipping-temperature note is a red herring and pulls the team off the leading cause.",
                3,
                3,
                "Manufacturing",
                "new",
                "Compare the excursion lot's rate with the leading stratum before changing the plan.",
            )
        )
        risks.append(
            _risk(
                "R6",
                "Leadership asks for cost before the containment cost is sized.",
                3,
                4,
                "PM",
                "new",
                "Cost task runs in the same week as containment, from the computed invalid count.",
            )
        )
    for risk in risks:
        if risk["score"] != risk["likelihood"] * risk["impact"]:
            raise ValueError(risk["id"])
    return risks


def plan_node(state: CaseState) -> dict[str, Any]:
    scenario = state["scenario"]
    week = int(state.get("week", 0))
    hypotheses = state.get("hypotheses") or []
    top = hypotheses[0] if hypotheses else {"cause": "no_single_cause", "level": None}
    plan = build_plan(scenario, top, week)
    risks = build_risks(top, week)
    settings = load_settings()
    out = Path(state["out_dir"]) if state.get("out_dir") else settings.out_dir
    out.mkdir(parents=True, exist_ok=True)
    register = render_risk_register(risks, week)
    plan_json = json.dumps(plan, indent=2)
    for folder in (out, out / f"week{week}"):
        folder.mkdir(parents=True, exist_ok=True)
        write_gantt(plan, folder / "gantt.html", folder / "gantt.png")
        (folder / "risk_register.md").write_text(register, encoding="utf-8")
        (folder / "plan.json").write_text(plan_json, encoding="utf-8")
    jira = make_client(settings, out / "jira_issues.json").sync(plan)
    return {"plan": plan, "risks": risks, "jira": jira}
