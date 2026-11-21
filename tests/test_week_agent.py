"""Week 1 complaint and numbers, on the real OOI extract, binned by received date."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "openfda_ooi.csv"

# Measured from tests/fixtures/openfda_ooi.csv with weeks binned on date_received.
WEEK_TOTALS = {
    1: {"reports": 775, "invalid": 42, "top_code": "INV-MECH", "top_count": 38, "maker": "ABBOTT MOLECULAR", "maker_count": 540},
    2: {"reports": 972, "invalid": 73, "top_code": "INV-MECH", "top_count": 39, "maker": "ABBOTT MOLECULAR", "maker_count": 603},
    3: {"reports": 1146, "invalid": 73, "top_code": "INV-MECH", "top_count": 39, "maker": "ABBOTT MOLECULAR", "maker_count": 656},
    4: {"reports": 1422, "invalid": 97, "top_code": "INV-NOR", "top_count": 50, "maker": "ABBOTT MOLECULAR", "maker_count": 717},
}
PROMPTS = (
    "name the biggest invalid category so far",
    "How many complaints are in the dataset?",
    "How many complaints are in the dataset",
    "Who is the main manufacturer from this weeks reports",
    "which invalid categories are highest to lowest",
    "whos the main manufacturer",
)


def _records():
    frame = pd.read_csv(FIXTURE, dtype=str).fillna("")
    rows = []
    for record in frame.to_dict(orient="records"):
        code = str(record["invalid_code"] or "")
        rows.append(
            {
                "mdr_report_key": record["mdr_report_key"],
                "product_code": "OOI",
                "date_received": record["date_received"],
                "date_of_event": record["date_of_event"] or None,
                "manufacturer_name": record["manufacturer_name"],
                "invalid_code": code,
                "is_invalid_type": bool(code),
            }
        )
    return rows


def _ooi_frame():
    from invalid_agent.data.frame import frame_from_reports
    from invalid_agent.sim.generate import load_scenario

    scenario = load_scenario(ROOT / "cases" / "openfda_ooi.yaml")
    return scenario, frame_from_reports(_records(), scenario)


def _week_view(week: int):
    from invalid_agent.ui.story import build_week_view

    scenario, frame = _ooi_frame()
    return build_week_view(scenario, frame, week)


def _talk(view, text, step):
    from invalid_agent.ui.talkback import respond

    return respond(text, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")


def test_received_date_week_totals_and_no_future_rows():
    from invalid_agent.ui.explore import explore_facts
    from invalid_agent.ui.story import slice_through_story_week

    scenario, frame = _ooi_frame()
    assert set(frame["date_basis"]) == {"date_received"}
    early_event = frame["date_of_event"].notna() & (frame["date_of_event"] < "2022-01-01")
    late_received = frame["date"] >= "2023-01-01"
    leaked = frame.loc[early_event & late_received, "run_id"]
    assert not leaked.empty
    week1 = slice_through_story_week(frame, 1)
    assert set(leaked).isdisjoint(set(week1["run_id"]))
    assert week1["date"].max() < pd.Timestamp("2023-01-01")
    for week, expected in WEEK_TOTALS.items():
        facts = explore_facts(frame, week, product_code="OOI", device=scenario["device"], estimable=False)
        assert facts["total"] == expected["reports"]
        assert facts["invalid_total"] == expected["invalid"]
        assert facts["top_code"] == expected["top_code"]
        assert facts["top_count"] == expected["top_count"]
        assert facts["manufacturers"][0]["name"] == expected["maker"]
        assert facts["manufacturers"][0]["count"] == expected["maker_count"]
        assert facts["total"] <= WEEK_TOTALS[4]["reports"]


def test_neel_prompts_answer_on_both_parts_without_unlocking():
    view = _week_view(1)
    expected = WEEK_TOTALS[1]
    for step in ("complaint", "data"):
        for text in PROMPTS:
            reply = _talk(view, text, step)
            body = reply["text"]
            assert reply["confirmed"] is False, text
            assert "can't answer" not in body, text
            assert "charts part" not in body, text
            assert "GOOD QUESTION" not in body, text
            assert "Remember:" not in body, text
            if "biggest" in text or "categor" in text:
                assert expected["top_code"] in body, text
                assert str(expected["top_count"]) in body, text
            elif "how many" in text.casefold():
                assert str(expected["reports"]) in body, text
                assert str(expected["invalid"]) in body, text
                assert str(WEEK_TOTALS[4]["reports"]) not in body, text
            else:
                assert expected["maker"] in body, text
                assert str(expected["maker_count"]) in body, text


def test_missing_explore_still_answers_and_show_me_logs_the_fact():
    from invalid_agent.ui.talkback import part_fact

    view = _week_view(1)
    view.pop("explore")
    expected = WEEK_TOTALS[1]
    for step in ("complaint", "data"):
        named = _talk(view, "name the biggest invalid category so far", step)
        counted = _talk(view, "How many complaints are in the dataset?", step)
        assert expected["top_code"] in named["text"]
        assert "charts part" not in named["text"]
        assert str(expected["reports"]) in counted["text"]
        assert "can't answer" not in counted["text"]
        assert named["confirmed"] is False
    finding, sentence = part_fact(view, "complaint")
    assert finding == "the biggest invalid category so far"
    assert "Name the biggest invalid category so far." not in sentence
    assert "38 of 42" in sentence
    assert "INV-MECH" in sentence


def test_category_claim_unlocks_and_the_bad_claims_do_not():
    view = _week_view(1)
    good = _talk(view, "INV-MECH is the biggest invalid category with 38 of 42", "complaint")
    assert good["confirmed"] is True
    assert good["text"].startswith("YEP")
    for text in (
        "INV-MECH is the smallest invalid category with 38 of 42",
        "INV-MECH first showed up in week 1 at 38 of 42",
        "INV-MECH is the biggest invalid category with 38 of 42?",
        "name the biggest invalid category so far",
    ):
        reply = _talk(view, text, "complaint")
        assert not reply["confirmed"], text
        assert not reply["text"].startswith("YEP"), text


def test_a_phrased_reply_with_a_wrong_number_is_replaced():
    view = _week_view(1)

    class _Client:
        def select_tools(self, message, tools):
            assert any(spec["name"] == "report_total" for spec in tools)
            return [{"name": "report_total", "arguments": {}}]

        def phrase(self, message, results):
            assert results[0]["data"]["total"] == 775
            return "There are 999 complaints so far."

    reply = _talk_with(view, "How many complaints are in the dataset?", _Client())
    assert "999" not in reply["text"]
    assert "775" in reply["text"]
    assert reply["confirmed"] is False


def _talk_with(view, text, client):
    from invalid_agent.ui.talkback import respond

    return respond(text, view, "complaint", ticket_key="Your ticket 1", flag_key="Flag 1", tool_client=client)


def test_filtered_count_uses_the_named_manufacturer():
    from invalid_agent.ui.explore import answer_message

    view = _week_view(1)
    text = answer_message("How many reports does ABBOTT MOLECULAR have?", view, None)
    assert "540" in text
    assert "ABBOTT MOLECULAR" in text
    assert "can't answer" not in text


def _visible(app) -> str:
    chunks = []
    for name in ("markdown", "caption", "header", "subheader", "title", "text", "info", "warning", "error"):
        for item in getattr(app, name, []):
            chunks.append(str(getattr(item, "value", "")))
    for button in app.button:
        chunks.append(str(button.label))
    return "\n".join(chunks)


def _ask(app, text):
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    app = box.set_value(text).run()
    assert not app.exception, app.exception
    button = next(item for item in app.button if item.label == "Tell the agent")
    button.click()
    app.run()
    assert not app.exception, app.exception
    return app


def _ooi_app(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.setenv("MANUFACTURER_DISPLAY", "real")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    _scenario, frame = _ooi_frame()
    monkeypatch.setattr("invalid_agent.data.frame.load_openfda_frame", lambda scenario: frame)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180)
    app.session_state["scenario_id"] = "openfda_ooi"
    app.run()
    assert not app.exception, app.exception
    return app


def test_live_prompts_on_the_ooi_pages(monkeypatch):
    app = _ooi_app(monkeypatch)
    for beat, title in ((0, "Complaint understanding"), (1, "This week's numbers")):
        app.session_state["beat"] = beat
        app.session_state["done_parts"] = []
        app.run()
        assert title in _visible(app)
        for text in PROMPTS:
            app = _ask(app, text)
            visible = _visible(app)
            assert "can't answer" not in visible, text
            assert "charts part" not in visible, text
            assert "GOOD QUESTION" not in visible, text
            assert "Remember:" not in visible, text
            if "biggest" in text or "categor" in text:
                assert "INV-MECH" in visible, text
                assert "38" in visible, text
            elif "how many" in text.casefold():
                assert "775" in visible, text
            else:
                assert "ABBOTT MOLECULAR" in visible, text
                assert "540" in visible, text
            nxt = next(button for button in app.button if button.key == "next")
            assert nxt.disabled, text
    app.session_state["beat"] = 0
    app.session_state["done_parts"] = []
    app.run()
    app = _ask(app, "INV-MECH is the biggest invalid category with 38 of 42")
    assert "YEP, YOU GOT IT!" in _visible(app)
    nxt = next(button for button in app.button if button.key == "next")
    assert not nxt.disabled


def test_show_me_logs_the_ooi_category_not_the_goal(monkeypatch):
    app = _ooi_app(monkeypatch)
    button = next(item for item in app.button if item.key == "show-me")
    button.click()
    app.run()
    assert not app.exception, app.exception
    visible = _visible(app)
    assert "38 of 42" in visible
    assert "INV-MECH" in visible
    assert "Name the biggest invalid category so far." not in visible
    nxt = next(item for item in app.button if item.key == "next")
    assert not nxt.disabled
