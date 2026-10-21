"""One case graph: triage, then plan, RCA, and a status note, looping by week.

Week 4 continues into close-out and the exec deck.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from langgraph.graph import END, StateGraph

from invalid_agent.case.state import CaseState
from invalid_agent.config import load_settings
from invalid_agent.nodes.closeout import closeout_node
from invalid_agent.nodes.planner import plan_node
from invalid_agent.nodes.rca import rca_node
from invalid_agent.nodes.status import status_node
from invalid_agent.nodes.triage import triage_node
from invalid_agent.sim.generate import load_scenario


def advance_week(state: CaseState) -> dict[str, int]:
    """Move the investigation forward one week and re-enter the planner."""
    return {"week": int(state["week"]) + 1}


def route_after_status(state: CaseState) -> str:
    """Stop at the requested week. Week 4 continues into close-out."""
    target = int(state.get("target_week", state["week"]))
    if int(state["week"]) >= target:
        if int(state["week"]) >= 4:
            return "closeout"
        return "end"
    return "advance"


def build_graph():
    """Triage once, then plan → RCA → status, repeating until target_week."""
    graph = StateGraph(CaseState)
    graph.add_node("triage", triage_node)
    graph.add_node("plan", plan_node)
    graph.add_node("rca", rca_node)
    graph.add_node("status", status_node)
    graph.add_node("advance", advance_week)
    graph.add_node("closeout", closeout_node)
    graph.set_entry_point("triage")
    graph.add_edge("triage", "plan")
    graph.add_edge("plan", "rca")
    graph.add_edge("rca", "status")
    graph.add_conditional_edges(
        "status",
        route_after_status,
        {"advance": "advance", "end": END, "closeout": "closeout"},
    )
    graph.add_edge("advance", "plan")
    graph.add_edge("closeout", END)
    return graph.compile()


def resolve_scenario(name: str, root: Path) -> Path:
    candidate = Path(name)
    if candidate.is_file():
        return candidate
    in_folder = root / "scenarios" / name
    if in_folder.is_file():
        return in_folder
    with_suffix = in_folder.with_suffix(".yaml")
    if with_suffix.is_file():
        return with_suffix
    raise SystemExit(f"scenario not found: {name}")


def initial_state(
    scenario: dict[str, Any],
    week: int,
    out_dir: Path | None = None,
    target_week: int | None = None,
) -> CaseState:
    state: CaseState = {
        "scenario_id": str(scenario.get("id", "scenario")),
        "scenario": scenario,
        "week": week,
        "target_week": week if target_week is None else target_week,
        "decision_log": [],
        "risks": [],
        "status_updates": {},
        "jira": {},
    }
    if out_dir is not None:
        state["out_dir"] = str(out_dir)
    return state


def run_case(scenario_name: str, week: int, out_dir: Path | None = None) -> dict[str, Any]:
    if week < 0 or week > 4:
        raise SystemExit("week must be 0 through 4")
    settings = load_settings()
    path = resolve_scenario(scenario_name, settings.repo_root)
    scenario = load_scenario(path)
    destination = out_dir or settings.out_dir
    destination.mkdir(parents=True, exist_ok=True)
    app = build_graph()
    result = app.invoke(
        initial_state(scenario, 0, destination, target_week=week),
        config={"recursion_limit": 80},
    )
    memo_path = destination / "week0_triage.md"
    memo_path.write_text(result["triage_markdown"], encoding="utf-8")
    (destination / "week0_fidelity.json").write_text(
        json.dumps(result["fidelity"], indent=2),
        encoding="utf-8",
    )
    (destination / "fishbone.md").write_text(result["fishbone"]["markdown"], encoding="utf-8")
    (destination / "five_whys.md").write_text(result["five_whys"]["markdown"], encoding="utf-8")
    (destination / "capa8d.md").write_text(result["capa"]["markdown"], encoding="utf-8")
    result["memo_path"] = str(memo_path)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Invalid Bot case graph.")
    parser.add_argument("--scenario", required=True, help="Scenario id or YAML path, e.g. bad_lot")
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--out", default="", help="Output directory. Default: ./out")
    args = parser.parse_args(argv)
    result = run_case(args.scenario, args.week, Path(args.out) if args.out else None)
    print(f"Wrote {result['memo_path']}")
    if result.get("deck_path"):
        print(f"Wrote {result['deck_path']}")
    print(f"Escalate: {result['triage_memo']['escalate']}  severity: {result['triage_memo']['severity']}")
    print("Simulation. Synthetic data. Not for clinical use.")


if __name__ == "__main__":
    main()
