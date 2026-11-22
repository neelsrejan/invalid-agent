"""JJE audit weeks on the frozen public extract."""

from pathlib import Path

import pandas as pd

from invalid_agent.data.mapping import INVALID_LABELS, primary_invalid_code
from invalid_agent.data.frame import frame_from_reports
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.audit import cause_set_for, company_table, flagged_companies
from invalid_agent.ui.story import build_week_view
from invalid_agent.ui.talkback import part_fact, respond

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "openfda_jje.csv"
WEEKS = ("eda", "pareto", "responses", "closeout")
ASKS = (
    "how many complaints are in the dataset",
    "which companies are over 1%",
    "name the biggest invalid category for roche",
    "which companies have too few reports to judge",
)


def _records() -> list[dict]:
    raw = pd.read_csv(FIXTURE, dtype=str).fillna("")
    records = []
    for row in raw.to_dict(orient="records"):
        labels = [part.strip() for part in str(row["product_problems"]).split("|") if part.strip()]
        assert primary_invalid_code(labels) == str(row["invalid_code"])
        row["product_problems"] = labels
        records.append(row)
    return records


def _frame() -> pd.DataFrame:
    scenario = load_scenario(ROOT / "cases" / "openfda_jje.yaml")
    return frame_from_reports(_records(), scenario)


def _view(week: int = 1) -> dict:
    scenario = load_scenario(ROOT / "cases" / "openfda_jje.yaml")
    return build_week_view(scenario, _frame(), week)


def test_label_map_includes_the_missing_phrases():
    assert INVALID_LABELS["program or algorithm execution problem"] == "INV-SW"
    assert INVALID_LABELS["failure to obtain sample"] == "INV-NOR"


def test_company_table_and_cause_sets_use_the_recomputed_file():
    frame = _frame()
    table = company_table(frame)
    by_name = {row["name"]: row for row in table}
    assert by_name["Roche"]["invalid"] == 81 and by_name["Roche"]["total"] == 2250
    assert by_name["Siemens"]["invalid"] == 13 and by_name["Siemens"]["total"] == 485
    assert by_name["Abbott Labs"]["invalid"] == 10 and by_name["Abbott Labs"]["total"] == 748
    assert by_name["Beckman"]["over"] is False and by_name["Beckman"]["enough"] is True
    assert by_name["Ortho"]["note"] == "too few reports to judge"
    assert by_name["The Binding Site"]["total"] == 3
    assert [row["name"] for row in flagged_companies(table)] == ["Roche", "Abbott Labs", "Siemens"]
    roche = cause_set_for(frame, "Roche", table)
    assert [cause["code"] for cause in roche["causes"]] == ["INV-MECH", "INV-NOR"]
    assert roche["projected"] < 0.01
    abbott = cause_set_for(frame, "Abbott Labs", table)
    assert [cause["code"] for cause in abbott["causes"]] == ["INV-MECH"]
    siemens = cause_set_for(frame, "Siemens", table)
    assert [cause["code"] for cause in siemens["causes"]] == ["INV-MECH", "INV-USR"]
    week1 = _view(1)
    week4 = _view(4)
    assert week1["explore"]["total"] == week4["explore"]["total"] == 4221
    assert "product_problems" not in (week1["explore"]["preview"][0] if week1["explore"]["preview"] else {})


def test_neel_phrases_answer_on_every_week_and_do_not_unlock():
    for week, step in enumerate(WEEKS, start=1):
        view = _view(week)
        for text in ASKS:
            reply = respond(text, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
            assert reply["confirmed"] is False, (step, text)
            assert "can't answer" not in reply["text"]
            assert "GOOD QUESTION" not in reply["text"]
            assert "NOT QUITE" not in reply["text"]
            assert "charts part" not in reply["text"]
        counted = respond(ASKS[0], view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert "4221" in counted["text"]


def test_goal_claim_unlocks_and_show_me_logs_the_same_fact():
    expectations = {
        "eda": "Roche, Abbott Labs, and Siemens are over 1%.",
        "pareto": "Roche needs INV-MECH and INV-NOR, Abbott Labs needs INV-MECH, and Siemens needs INV-MECH and INV-USR to get under 1%.",
        "responses": "Roche INV-MECH is Machine, Roche INV-NOR is Material, Abbott Labs INV-MECH is Machine, Siemens INV-MECH is Machine, and Siemens INV-USR is Man.",
        "closeout": "Roche gets under 1%, Abbott Labs gets under 1%, and Siemens gets under 1%.",
    }
    for week, step in enumerate(WEEKS, start=1):
        view = _view(week)
        finding, sentence = part_fact(view, step)
        assert sentence == expectations[step], sentence
        reply = respond(sentence, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert reply["confirmed"] is True, step
        assert reply["text"].startswith("YEP")
        asked = respond("which companies are over 1%", view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert asked["confirmed"] is False
