"""The guided walk cannot skip a week, and the talk-back agent is on every part."""

import re
from pathlib import Path

from invalid_agent.ui.plain import unexplained_jargon

ROOT = Path(__file__).resolve().parents[1]


def _chunks(app) -> list[str]:
    chunks = []
    for name in ("markdown", "caption", "header", "subheader", "title", "text", "info", "warning", "error", "html"):
        for item in getattr(app, name, []):
            chunks.append(str(getattr(item, "value", "")))
    for button in list(getattr(app, "button", [])) + list(getattr(app, "download_button", [])):
        chunks.append(str(button.label))
    for metric in getattr(app, "metric", []):
        chunks.append(str(getattr(metric, "label", "")))
        chunks.append(str(getattr(metric, "value", "")))
    for frame in getattr(app, "dataframe", []):
        chunks.append(str(getattr(frame, "value", "")))
    for box in list(getattr(app, "selectbox", [])) + list(getattr(app, "radio", [])):
        chunks.append(str(box.label))
        chunks.extend(str(option) for option in (box.options or []))
    for box in list(getattr(app, "text_input", [])) + list(getattr(app, "toggle", [])):
        chunks.append(str(box.label))
    for item in getattr(app, "expander", []):
        chunks.append(str(item.label))
    return [chunk for chunk in chunks if chunk]


def _visible(app) -> str:
    return "\n".join(_chunks(app))


def _explained(text: str) -> set[str]:
    from invalid_agent.ui.plain import JARGON_RULES, _readable

    readable = _readable(text)
    lowered = readable.casefold()
    found: set[str] = set()
    for pattern, glosses in JARGON_RULES:
        if pattern.search(readable) and glosses and any(gloss in lowered for gloss in glosses):
            found.add(pattern.pattern)
    return found


def _lint_each(app) -> None:
    """A term must be explained the first time it shows. Later mentions can stay short."""
    known: set[str] = set()
    for chunk in _chunks(app):
        bare = [hit for hit in unexplained_jargon(chunk) if hit not in known]
        assert bare == [], chunk
        known |= _explained(chunk)


def _run_app(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180)
    app.run()
    assert not app.exception, app.exception
    return app


def _advance(app):
    """Finish the part with Show me when Next is still locked, then go forward."""
    show = [button for button in app.button if button.key == "show-me"]
    if show and not getattr(show[0], "disabled", False):
        show[0].click()
        app.run()
        assert not app.exception, app.exception
    return _click_key(app, "next")


def _click_key(app, key: str):
    matches = [button for button in app.button if button.key == key]
    assert matches, f"missing button {key}; have {[(button.key, button.label) for button in app.button]}"
    matches[0].click()
    app.run()
    assert not app.exception, app.exception
    return app


def _click_label(app, label: str):
    matches = [button for button in app.button if button.label == label]
    assert matches, f"missing button {label!r}; have {[button.label for button in app.button]}"
    matches[0].click()
    app.run()
    assert not app.exception, app.exception
    return app


def test_next_stays_locked_until_the_part_is_done(monkeypatch):
    app = _run_app(monkeypatch)
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    assert "Show me" in _visible(app)
    beat = app.session_state["beat"]
    assert app.session_state["beat"] == beat
    assert app.session_state["story_week"] == 1
    app = _click_key(app, "show-me")
    visible = _visible(app)
    assert "No confirmed insight yet" not in visible
    assert "Insight:" in visible
    assert "98%" in visible
    assert "We found what was promised" not in visible
    nxt = next(button for button in app.button if button.key == "next")
    assert not nxt.disabled
    app = _click_key(app, "next")
    assert app.session_state["beat"] == beat + 1

    for _part in range(4):
        app = _advance(app)
    assert "Week wrap-up" in _visible(app)
    start = next(button for button in app.button if button.key == "next")
    assert start.label == "Start week 2"
    assert start.disabled
    assert app.session_state["story_week"] == 1
    assert "Week 2 of 4" not in _visible(app)
    app = _click_key(app, "show-me")
    app = _click_key(app, "next")
    assert app.session_state["story_week"] == 2
    assert "Week 2 of 4" in _visible(app)


def test_show_me_on_week_two_logs_that_weeks_insight(monkeypatch):
    app = _run_app(monkeypatch)
    app.session_state["unlocked_week"] = 2
    app.session_state["story_week"] = 2
    app.session_state["beat"] = 0
    app.session_state["done_parts"] = [f"1:{step}" for step in ("complaint", "data", "charts", "logged", "notes", "wrap")]
    app.session_state["open_items"] = [
        {
            "week": 1,
            "key": "Your ticket 1",
            "text": "The promise is that at least 98% of tests are valid.",
            "kind": "ticket",
            "signature": "what was promised",
        }
    ]
    app.session_state["insight_serial"] = 1
    app.run()
    assert not app.exception, app.exception
    assert "Week 2 of 4" in _visible(app)
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    app = _click_key(app, "show-me")
    visible = _visible(app)
    assert "Week 2 insights" in visible
    assert "No confirmed insight yet" not in visible
    assert "Insight:" in visible
    assert "Your ticket 2" not in visible
    assert "We found what was promised" not in visible
    nxt = next(button for button in app.button if button.key == "next")
    assert not nxt.disabled


def test_a_flag_shows_in_the_week_insights_without_a_doubled_label(monkeypatch):
    app = _run_app(monkeypatch)
    app = _advance(app)
    app = _advance(app)
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    box.set_value("INV-SW makes up the majority of the invalids").run()
    app = _click_label(app, "Tell the agent")
    visible = _visible(app)
    assert "Flag 1" in visible
    assert "We'll log that as Flag 1" in visible
    assert "No confirmed insight yet" not in visible
    assert "(Flag)" in visible
    assert "Flag 1: Flag 1" not in visible
    assert "Flag 1** (Flag): Flag 1" not in visible


def test_cannot_skip_weeks_and_every_part_has_a_wrap_up(monkeypatch):
    app = _run_app(monkeypatch)
    visible = _visible(app)
    assert "Not for clinical use" in visible
    assert "Week 1 of 4" in visible
    assert "The complaint" in visible
    assert "Northlake Health" in visible
    assert not any(button.label == "Week 2" for button in app.button)
    assert not any(button.label == "Week 0" for button in app.button)
    assert not any(button.label == "Week 4" for button in app.button)
    # One Back, one Next. The talk-back box is on the first screen.
    assert sum(1 for button in app.button if button.key == "back") == 1
    assert sum(1 for button in app.button if button.key == "next") == 1
    assert any(box.label == "Your question or insight" for box in app.text_input)

    app.session_state["story_week"] = 4
    app.run()
    assert not app.exception, app.exception
    assert app.session_state["story_week"] == 1
    assert "Week 1 of 4" in _visible(app)

    for expected in ("This week's numbers", "The charts", "What gets logged", "Root-cause notes", "Week wrap-up"):
        app = _advance(app)
        assert expected in _visible(app)
        assert "Week 1 of 4" in _visible(app)
        assert any(box.label == "Your question or insight" for box in app.text_input)
    visible = _visible(app)
    assert "What we recommend" in visible
    assert "Open the week-4" not in visible
    assert visible.count("Back") == 1


def test_talkback_answers_and_a_confirmed_insight_carries(monkeypatch):
    app = _run_app(monkeypatch)
    app = _advance(app)
    app = _advance(app)
    assert "The charts" in _visible(app)
    before = _visible(app)
    count_line = re.search(r"This chart counts \d+ weeks far above the usual rate\.", before)
    assert count_line, before
    why = next(button for button in app.button if button.label == "Why is the invalid rate going up?")
    why.click()
    app.run()
    assert not app.exception, app.exception
    answered = _visible(app)
    assert "GOOD QUESTION." in answered
    assert count_line.group(0) in answered
    assert answered.count(count_line.group(0)) >= 2
    assert "Fidelity" not in answered
    assert "model draft" not in answered.casefold()
    assert "/dashboard/" not in answered
    assert "GROQ_API_KEY" not in answered

    insight = next(
        button
        for button in app.button
        if button.label.startswith("It looks like") or button.label.startswith("The biggest invalid type")
    )
    insight.click()
    app.run()
    assert not app.exception, app.exception
    confirmed = _visible(app)
    assert "YEP, YOU GOT IT!" in confirmed
    assert "Week 1 insights" in confirmed
    assert "Your ticket 1" in confirmed
    assert "INV-13" not in confirmed
    assert confirmed.count("keep it in mind for the root cause") == 1
    bullet = next(line for line in confirmed.splitlines() if "logged as Your ticket 1" in line)
    app = _click_key(app, "next")
    assert bullet.strip("- ").strip() in _visible(app) or "logged as Your ticket 1" in _visible(app)
    assert "Week 1 insights" in _visible(app)

    for _step in range(2):
        app = _advance(app)
    assert "Week wrap-up" in _visible(app)
    app = _advance(app)
    week2 = _visible(app)
    assert "Week 2 of 4" in week2
    assert "Still open from earlier weeks" in week2
    assert "Your ticket 1" in week2
    _lint_each(app)


def test_rendered_week_has_no_unexplained_jargon_or_secrets(monkeypatch):
    app = _run_app(monkeypatch)
    for _step in range(6):
        _lint_each(app)
        visible = _visible(app)
        assert "GROQ_API_KEY" not in visible
        assert "api_key" not in visible.casefold()
        assert "/home/" not in visible
        assert "/opt/" not in visible
        assert re.search(r"(?<![\d.])0\.00%", visible) is None
        if _step < 5:
            app = _advance(app)
    assert "What we recommend" in _visible(app)


def test_the_same_insight_is_not_logged_twice(monkeypatch):
    app = _run_app(monkeypatch)
    app = _advance(app)
    app = _advance(app)
    insight = next(button for button in app.button if button.label.startswith("It looks like") or button.label.startswith("The biggest invalid type"))
    insight.click()
    app.run()
    app = _click_label(app, "Tell the agent")
    first = _visible(app)
    insight = next(button for button in app.button if button.label.startswith("It looks like") or button.label.startswith("The biggest invalid type"))
    insight.click()
    app.run()
    app = _click_label(app, "Tell the agent")
    visible = _visible(app)
    assert "Your ticket 1" in visible
    assert "Your ticket 2" not in visible
    assert visible.count("We found") == first.count("We found")


def test_show_me_through_week_one_leaves_week_two_with_no_carried_items(monkeypatch):
    app = _run_app(monkeypatch)
    for _part in range(6):
        app = _advance(app)
    assert app.session_state["story_week"] == 2
    carried = [
        item
        for item in app.session_state["open_items"]
        if int(item["week"]) < 2 and item.get("kind") in {"ticket", "flag"}
    ]
    assert carried == []
    week_one = [item for item in app.session_state["open_items"] if int(item["week"]) == 1]
    assert len(week_one) == 6
    assert all(item["kind"] == "insight" and str(item["text"]).strip() for item in week_one)
    assert all("what was promised" not in str(item["text"]).casefold() for item in week_one)
    visible = _visible(app)
    assert "Still open from earlier weeks" not in visible
    assert "We found what was promised" not in visible


def test_a_typed_insight_unlocks_next_on_the_numbers_and_the_charts(monkeypatch):
    app = _run_app(monkeypatch)
    app = _advance(app)
    assert "This week's numbers" in _visible(app)
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    visible = _visible(app)
    rate = re.search(r"The invalid rate this week is [\d.]+%", visible)
    assert rate, visible
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    box.set_value(rate.group(0)).run()
    app = _click_label(app, "Tell the agent")
    assert "YEP, YOU GOT IT!" in _visible(app)
    nxt = next(button for button in app.button if button.key == "next")
    assert not nxt.disabled
    app = _click_key(app, "next")
    assert "The charts" in _visible(app)
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    claim = next(
        button.label
        for button in app.button
        if button.label.startswith("It looks like") or button.label.startswith("The biggest invalid type")
    )
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    box.set_value(claim).run()
    app = _click_label(app, "Tell the agent")
    visible = _visible(app)
    assert "YEP, YOU GOT IT!" in visible
    nxt = next(button for button in app.button if button.key == "next")
    assert not nxt.disabled


def test_a_typed_insight_unlocks_next_on_every_part(monkeypatch):
    app = _run_app(monkeypatch)
    steps = (
        ("The complaint", "The promise is at least 98% valid tests"),
        ("This week's numbers", None),
        ("The charts", None),
        ("What gets logged", None),
        ("Root-cause notes", "Tell the customer we have not confirmed a cause"),
        ("Week wrap-up", "We opened the case"),
    )
    for title, typed in steps:
        visible = _visible(app)
        assert title in visible
        nxt = next(button for button in app.button if button.key == "next")
        assert nxt.disabled
        if title == "This week's numbers":
            rate = re.search(r"The invalid rate this week is [\d.]+%", visible)
            assert rate, visible
            typed = rate.group(0)
        if title == "What gets logged":
            typed = f"The plan has {len(app.dataframe[0].value)} follow-up items"
        if title == "The charts":
            typed = next(
                button.label
                for button in app.button
                if button.label.startswith("It looks like") or button.label.startswith("The biggest invalid type")
            )
        box = next(item for item in app.text_input if item.label == "Your question or insight")
        box.set_value(typed).run()
        app = _click_label(app, "Tell the agent")
        assert "YEP, YOU GOT IT!" in _visible(app), title
        nxt = next(button for button in app.button if button.key == "next")
        assert not nxt.disabled, title
        if title != "Week wrap-up":
            app = _click_key(app, "next")


def test_sending_a_question_clears_the_box(monkeypatch):
    app = _run_app(monkeypatch)
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    box.set_value("What is MAUDE?").run()
    assert not app.exception, app.exception
    app = _click_label(app, "Tell the agent")
    visible = _visible(app)
    assert "public database of device problem reports" in visible
    said = next(line for line in visible.splitlines() if "You said" in line)
    assert "What is MAUDE?" in said
    assert "public database" not in said
    shown = next(item for item in app.text_input if item.label == "Your question or insight")
    assert (shown.value or "") == ""
    assert "Flag 1" not in visible


def test_a_failed_load_does_not_print_the_exception(monkeypatch):
    import streamlit as st

    def boom(_scenario):
        raise RuntimeError("postgres://secret-host/db password=hunter2")

    st.cache_data.clear()
    monkeypatch.setattr("invalid_agent.data.frame.load_frame", boom)
    app = _run_app(monkeypatch)
    visible = _visible(app)
    assert "does not show a connection string" in visible
    assert "hunter2" not in visible
    assert "postgres://" not in visible
    assert "RuntimeError" not in visible


def test_a_failed_deck_does_not_print_the_exception(monkeypatch):
    def boom(_path, _facts):
        raise RuntimeError("postgres://secret-host/db password=hunter2")

    monkeypatch.setattr("invalid_agent.artifacts.deck.write_deck", boom)
    app = _run_app(monkeypatch)
    app.session_state["unlocked_week"] = 4
    app.session_state["story_week"] = 4
    app.session_state["beat"] = 5
    app.run()
    assert not app.exception, app.exception
    app = _click_key(app, "prepare-deck")
    visible = _visible(app)
    assert "The slide file did not build" in visible
    assert "hunter2" not in visible
    assert "postgres://" not in visible
    assert "RuntimeError" not in visible


def test_case_choice_survives_the_next_part(monkeypatch):
    """Streamlit drops a widget key that was not rendered. The case still sticks."""
    app = _run_app(monkeypatch)
    picker = next(box for box in app.selectbox if box.label == "Which case")
    target = next(option for option in picker.options if str(option).startswith("drift_clear"))
    picker.select(target)
    app.run()
    assert not app.exception, app.exception
    assert app.session_state["scenario_id"] == "drift_clear"
    app = _advance(app)
    assert "Week 1 of 4" in _visible(app)
    assert "drift" in _visible(app).casefold() or "INS-02" in _visible(app)
    assert app.session_state["scenario_id"] == "drift_clear"
    assert not any(box.label == "Which case" for box in app.selectbox)
