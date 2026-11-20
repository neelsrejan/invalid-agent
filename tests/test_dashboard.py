"""The guided walk cannot skip a week, and the talk-back agent is on every part."""

import re
from pathlib import Path

from invalid_agent.ui.plain import unexplained_jargon

ROOT = Path(__file__).resolve().parents[1]


def _visible(app) -> str:
    chunks = []
    for name in ("markdown", "caption", "header", "subheader", "title", "text", "info", "warning", "error", "html"):
        for item in getattr(app, name, []):
            chunks.append(str(getattr(item, "value", "")))
    for button in getattr(app, "button", []):
        chunks.append(str(button.label))
    for metric in getattr(app, "metric", []):
        chunks.append(str(getattr(metric, "label", "")))
        chunks.append(str(getattr(metric, "value", "")))
    return "\n".join(chunks)


def _run_app(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180)
    app.run()
    assert not app.exception, app.exception
    return app


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
    assert any(box.key == "talk_text" for box in app.text_input)

    app.session_state["story_week"] = 4
    app.run()
    assert not app.exception, app.exception
    assert app.session_state["story_week"] == 1
    assert "Week 1 of 4" in _visible(app)

    for expected in ("This week's numbers", "The charts", "What gets logged", "Root-cause notes", "Week wrap-up"):
        app = _click_key(app, "next")
        assert expected in _visible(app)
        assert "Week 1 of 4" in _visible(app)
        assert any(box.key == "talk_text" for box in app.text_input)
    visible = _visible(app)
    assert "What we recommend" in visible
    assert "Open the week-4" not in visible
    assert visible.count("Back") == 1


def test_talkback_answers_and_a_confirmed_insight_carries(monkeypatch):
    app = _run_app(monkeypatch)
    app = _click_key(app, "next")
    app = _click_key(app, "next")
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
    assert "logged as Jira ticket INV-" in confirmed
    bullet = next(line for line in confirmed.splitlines() if "logged as Jira ticket INV-" in line)
    app = _click_key(app, "next")
    assert bullet.strip("- ").strip() in _visible(app) or "logged as Jira ticket INV-" in _visible(app)
    assert "Week 1 insights" in _visible(app)

    for _step in range(2):
        app = _click_key(app, "next")
    assert "Week wrap-up" in _visible(app)
    app = _click_key(app, "next")
    week2 = _visible(app)
    assert "Week 2 of 4" in week2
    assert "Still open from earlier weeks" in week2
    assert "INV-" in week2
    assert unexplained_jargon(week2) == [], unexplained_jargon(week2)


def test_rendered_week_has_no_unexplained_jargon_or_secrets(monkeypatch):
    app = _run_app(monkeypatch)
    for _step in range(6):
        visible = _visible(app)
        assert unexplained_jargon(visible) == [], unexplained_jargon(visible)
        assert "GROQ_API_KEY" not in visible
        assert "api_key" not in visible.casefold()
        assert "/home/" not in visible
        assert "/opt/" not in visible
        assert re.search(r"(?<![\d.])0\.00%", visible) is None
        if _step < 5:
            app = _click_key(app, "next")
    assert "What we recommend" in _visible(app)


def test_case_choice_survives_the_next_part(monkeypatch):
    """Streamlit drops a widget key that was not rendered. The case still sticks."""
    app = _run_app(monkeypatch)
    picker = next(box for box in app.selectbox if box.label == "Which case")
    target = next(option for option in picker.options if str(option).startswith("drift_clear"))
    picker.select(target)
    app.run()
    assert not app.exception, app.exception
    assert app.session_state["scenario_id"] == "drift_clear"
    app = _click_key(app, "next")
    assert "Week 1 of 4" in _visible(app)
    assert "drift" in _visible(app).casefold() or "INS-02" in _visible(app)
    assert app.session_state["scenario_id"] == "drift_clear"
    assert not any(box.label == "Which case" for box in app.selectbox)
