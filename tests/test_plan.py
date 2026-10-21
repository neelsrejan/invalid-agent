"""The plan honors dependencies, and week 2 moves the Gantt and the register."""

from datetime import date
from pathlib import Path

from invalid_agent.nodes.planner import build_plan, build_risks
from invalid_agent.sim.generate import load_scenario

ROOT = Path(__file__).resolve().parents[1]


def _top():
    return {"cause": "bad_reagent_lot", "level": "L-4419", "category": "Material"}


def test_dependencies_start_when_the_predecessor_ends():
    scenario = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    plan = build_plan(scenario, _top(), week=0)
    by_id = {task["id"]: task for task in plan["tasks"]}
    horizon_end = date.fromisoformat(plan["start"]).toordinal() + plan["horizon_days"]
    assert date.fromisoformat(plan["tasks"][-1]["end"]).toordinal() <= horizon_end
    for task in plan["tasks"]:
        for dep in task["depends_on"]:
            assert task["start"] >= by_id[dep]["end"]
    assert "T11" not in by_id


def test_week_two_adds_the_lab_director_task_and_moves_risk():
    scenario = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    early = build_plan(scenario, _top(), week=0)
    later = build_plan(scenario, _top(), week=2)
    early_ids = {task["id"] for task in early["tasks"]}
    later_ids = {task["id"] for task in later["tasks"]}
    assert later_ids - early_ids == {"T11"}
    assert later["version"] == 2
    week0 = {risk["id"]: risk for risk in build_risks(_top(), 0)}
    week2 = {risk["id"]: risk for risk in build_risks(_top(), 2)}
    assert week0["R1"]["trend"] == "new"
    assert week2["R1"]["trend"] == "down"
    assert week2["R1"]["score"] == week2["R1"]["likelihood"] * week2["R1"]["impact"]
    assert week2["R4"]["trend"] == "up"
    assert "R4" not in week0


def test_gantt_files_and_register(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    monkeypatch.delenv("JIRA_TOKEN", raising=False)
    from invalid_agent.graph import main

    main(["--scenario", "bad_lot", "--week", "0", "--out", str(tmp_path)])
    html = (tmp_path / "gantt.html").read_text(encoding="utf-8")
    assert "Confirm rate, interval, and strata" in html
    png = (tmp_path / "gantt.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    register = (tmp_path / "risk_register.md").read_text(encoding="utf-8")
    assert "likelihood × impact" in register
    jira = (tmp_path / "jira_issues.json").read_text(encoding="utf-8")
    assert '"mode": "dry-run"' in jira
    assert "SIM-1" in jira
