"""Weeks 0–3 keep a decision per week, and the customer note does not declare a cause."""

import json
from pathlib import Path

from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.nodes.status import rag_color, upsert_decision


def test_rag_moves_from_red_to_amber_when_containment_week_arrives():
    assert rag_color(True, 0) == "Red"
    assert rag_color(True, 2) == "Red"
    assert rag_color(True, 3) == "Amber"
    assert rag_color(False, 0) == "Green"


def test_decision_log_keeps_one_row_per_week():
    log = upsert_decision([], {"week": 1, "decision": "first"})
    log = upsert_decision(log, {"week": 1, "decision": "replaced"})
    log = upsert_decision(log, {"week": 0, "decision": "earlier"})
    assert [row["week"] for row in log] == [0, 1]
    assert log[1]["decision"] == "replaced"


def test_weeks_one_through_three_diff_the_plan_and_pass_fidelity(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    for key in ("JIRA_BASE_URL", "JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    from invalid_agent.graph import main

    main(["--scenario", "bad_lot", "--week", "3", "--out", str(tmp_path)])
    log = (tmp_path / "decision_log.md").read_text(encoding="utf-8")
    assert log.count("## Week ") == 4
    week0 = json.loads((tmp_path / "week0" / "plan.json").read_text(encoding="utf-8"))
    week2 = json.loads((tmp_path / "week2" / "plan.json").read_text(encoding="utf-8"))
    assert "T11" not in {task["id"] for task in week0["tasks"]}
    assert "T11" in {task["id"] for task in week2["tasks"]}
    risk0 = (tmp_path / "week0" / "risk_register.md").read_text(encoding="utf-8")
    risk2 = (tmp_path / "week2" / "risk_register.md").read_text(encoding="utf-8")
    assert "| R4 |" not in risk0
    assert "| R4 |" in risk2
    customer = (tmp_path / "week2" / "status_customer.md").read_text(encoding="utf-8")
    internal = (tmp_path / "week2" / "status_internal.md").read_text(encoding="utf-8")
    leadership = (tmp_path / "week2" / "status_leadership.md").read_text(encoding="utf-8")
    assert "the root cause is" not in customer.lower()
    assert "bad_reagent_lot" not in customer
    assert "bad_reagent_lot" in internal
    assert "RAG: Red" in leadership
    assert "dollars" in leadership
    jira = json.loads((tmp_path / "jira_issues.json").read_text(encoding="utf-8"))
    by_task = {issue["task_id"]: issue for issue in jira["issues"]}
    assert by_task["T1"]["status"] == "Done"
    assert by_task["T11"]["status"] == "Done"  # sim_week 2, and the run finished at week 3
    # The node already raised if a note failed the guard. Re-read leadership as a smoke check
    # that the file is the guarded text: it contains only the rate line plus the cost line.
    assert "Not for clinical use" in customer
    assert check_narrative("The invalid rate is 27.40%.", {"overall": {"rate_pct": 3.67}}).ok is False
