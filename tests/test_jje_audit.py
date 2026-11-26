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
    assert INVALID_LABELS["program or algorithm execution failure"] == "INV-SW"
    assert primary_invalid_code(["Program or Algorithm Execution Failure"]) == "INV-SW"


def test_company_table_and_cause_sets_use_the_recomputed_file():
    frame = _frame()
    table = company_table(frame)
    by_name = {row["name"]: row for row in table}
    assert by_name["Roche"]["invalid"] == 81 and by_name["Roche"]["total"] == 2249
    assert by_name["Siemens"]["invalid"] == 13 and by_name["Siemens"]["total"] == 485
    assert by_name["Abbott Labs"]["invalid"] == 10 and by_name["Abbott Labs"]["total"] == 748
    assert by_name["Beckman"]["over"] is False and by_name["Beckman"]["enough"] is True
    assert by_name["Ortho"]["total"] == 64
    assert by_name["Biomerieux Italia"]["invalid"] == 1
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
        "pareto": "Roche needs INV-MECH and INV-NOR, Abbott Labs needs INV-MECH or INV-SW (tied at 4), and Siemens needs INV-MECH and INV-USR to get under 1%.",
        "responses": "Roche INV-MECH is Machine, Roche INV-NOR is Material, Abbott Labs INV-MECH is Machine, Siemens INV-MECH is Machine, and Siemens INV-USR is Man.",
        "closeout": "Roche gets under 1%, Abbott Labs gets under 1%, and Siemens gets under 1%.",
    }
    for week, step in enumerate(WEEKS, start=1):
        view = _view(week)
        finding, sentence = part_fact(view, step)
        assert sentence == expectations[step], sentence
        reply = respond(sentence, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert reply["confirmed"] is False
        assert not reply["text"].startswith("YEP")
        assert "GOOD QUESTION" not in reply["text"]
        assert "I can look up" not in reply["text"]
        asked = respond("which companies are over 1%", view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert asked["confirmed"] is False


def test_guard_rejects_company_swap_on_new_tools():
    from invalid_agent.ui import explore

    view = _view(2)
    facts = view["explore"]

    class Swap:
        def select_tools(self, text, specs):
            return [{"name": "threshold_flags", "arguments": {}}]

        def phrase(self, text, results):
            return "Siemens is at 3.60% (81 of 2249), Roche is at 2.68% (13 of 485), Abbott Labs 1.34% (10 of 748)."

    template = explore._sentence_for(explore.run_tool("threshold_flags", {}, facts), facts, view)
    assert explore._answer_with_client("x", facts, view, Swap()) == template

    class Foreign:
        def select_tools(self, text, specs):
            return [{"name": "company_causes", "arguments": {"company": "Roche"}}]

        def phrase(self, text, results):
            return "Siemens needs INV-MECH (53) and INV-NOR (15)."

    cause = explore._sentence_for(explore.run_tool("company_causes", {"company": "Roche"}, facts), facts, view)
    assert explore._answer_with_client("x", facts, view, Foreign()) == cause


def test_goal_claims_reject_wrong_companies_codes_branches_and_numbers():
    bad = {
        "eda": (
            "Roche, Abbott Labs, Siemens, and Beckman are over 1%.",
            "Roche, Abbott Labs, and Siemens are over 10%",
            "Roche, Abbott Labs, and Siemens are over 1.5%",
            "Roche, Abbott Labs, and Siemens are under 1%, everyone else over 1%",
            "Roche 99 of 2250, Abbott Labs 10 of 748, Siemens 13 of 485 are over 1%",
            "Roche, Abbott Labs, and Siemens are over 1% except Siemens",
            "Roche and Siemens are over 1%",
        ),
        "pareto": (
            "Roche needs INV-MECH, Abbott Labs needs INV-NOR, and Siemens needs INV-USR to get under 1%.",
            "Roche needs INV-MECH and INV-NOR and INV-CAL and INV-SW, Abbott Labs needs INV-MECH, Siemens needs INV-MECH and INV-USR to get under 1%",
            "Roche INV-MECH INV-NOR Abbott Labs INV-MECH Siemens INV-MECH INV-USR under 10%",
        ),
        "responses": (
            "Roche INV-MECH is Machine, Roche INV-NOR is Material, Abbott Labs INV-MECH is Machine, Siemens INV-MECH is Man, and Siemens INV-USR is Machine.",
        ),
        "closeout": (
            "Roche gets under 1%, Abbott Labs gets under 1%, and Siemens stays over 1%",
            "Roche and Abbott Labs get under 1%",
        ),
    }
    for week, step in enumerate(WEEKS, start=1):
        view = _view(week)
        for text in bad[step]:
            reply = respond(text, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
            assert reply["confirmed"] is False, (step, text)


def test_week_one_does_not_say_a_later_weeks_finding():
    view = _view(1)
    for text in ("which causes bring Roche under 1%", "what is the projected invalid share after the fix"):
        reply = respond(text, view, "eda", ticket_key="Your ticket 1", flag_key="Flag 1")
        assert "0.58" not in reply["text"], text
        assert "INV-NOR (15)" not in reply["text"], text
        assert reply["confirmed"] is False


def test_phrased_reply_cannot_add_a_company_to_the_flags():
    from invalid_agent.ui.explore import answer_message

    class Stub:
        def __init__(self, tool, phrased):
            self.tool, self.phrased = tool, phrased

        def select_tools(self, text, specs):
            return [{"name": self.tool, "arguments": {}}]

        def phrase(self, text, results):
            return self.phrased

    for tool, view, phrased in (
        ("threshold_flags", _view(1), "Roche, Abbott Labs, Siemens and Beckman are over 1%."),
        ("threshold_flags", _view(1), "Only Ortho is over 1%."),
        ("capa_outlook", _view(4), "Siemens stays over 1% after the fix."),
    ):
        assert answer_message("q", view, Stub(tool, phrased)) != phrased, phrased


def test_db_shaped_rows_without_invalid_code_still_count_roche():
    records = []
    for row in _records():
        bare = dict(row)
        bare.pop("invalid_code", None)
        bare.pop("is_invalid_type", None)
        records.append(bare)
    scenario = load_scenario(ROOT / "cases" / "openfda_jje.yaml")
    frame = frame_from_reports(records, scenario)
    by_name = {row["name"]: row for row in company_table(frame)}
    assert by_name["Roche"]["invalid"] == 81 and by_name["Roche"]["total"] == 2249


def test_a_missing_problem_table_uses_the_cached_extract(monkeypatch, caplog):
    import logging

    from invalid_agent.data import frame as frame_mod

    def missing(_code, _start, _end):
        raise RuntimeError('relation "maude_problem" does not exist')

    monkeypatch.setattr(frame_mod, "_query_case_rows", missing)
    monkeypatch.setattr("invalid_agent.data.cache.read_rows", lambda *_args, **_kwargs: [])
    scenario = load_scenario(ROOT / "cases" / "openfda_jje.yaml")
    with caplog.at_level(logging.WARNING):
        built = frame_mod.load_openfda_frame(scenario)
    assert "cached JJE extract" in caplog.text
    assert "no product_problems" in caplog.text
    assert len(built) == 4221
