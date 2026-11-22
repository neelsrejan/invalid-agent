"""The four-week audit keeps the agent box, and Next stays locked until the goal."""

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
    for box in list(getattr(app, "selectbox", [])) + list(getattr(app, "radio", [])):
        chunks.append(str(box.label))
        chunks.extend(str(option) for option in (box.options or []))
    for box in list(getattr(app, "text_input", [])) + list(getattr(app, "toggle", [])):
        chunks.append(str(box.label))
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


def _click_key(app, key: str):
    matches = [button for button in app.button if button.key == key]
    assert matches, f"missing button {key}; have {[(button.key, button.label) for button in app.button]}"
    matches[0].click()
    app.run()
    assert not app.exception, app.exception
    return app


def test_week_one_boots_with_the_agent_and_a_locked_next(monkeypatch):
    app = _run_app(monkeypatch)
    visible = _visible(app)
    assert "Week 1 of 4" in visible
    assert "Who is over 1%" in visible
    assert "how many complaints are in the dataset" in visible
    assert "Your question or insight" in visible
    assert "98%" not in visible
    assert "2%" not in visible
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    _lint_each(app)


def test_show_me_unlocks_next_and_a_question_does_not(monkeypatch):
    app = _run_app(monkeypatch)
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    app = box.set_value("how many complaints are in the dataset").run()
    button = next(item for item in app.button if item.label == "Tell the agent")
    button.click()
    app.run()
    assert not app.exception, app.exception
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    assert "GOOD QUESTION" not in _visible(app)
    app = _click_key(app, "show-me")
    visible = _visible(app)
    assert "Insight:" in visible
    nxt = next(button for button in app.button if button.key == "next")
    assert not nxt.disabled


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


def test_a_question_clears_the_box_and_later_weeks_render(monkeypatch):
    app = _run_app(monkeypatch)
    app.session_state["story_week"] = 4
    app.run()
    assert not app.exception, app.exception
    assert "Week 1 of 4" in _visible(app)
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    app = box.set_value("how many complaints are in the dataset").run()
    button = next(item for item in app.button if item.label == "Tell the agent")
    button.click()
    app.run()
    assert not app.exception, app.exception
    box = next(item for item in app.text_input if item.label == "Your question or insight")
    assert not str(getattr(box, "value", "") or "").strip()
    nxt = next(button for button in app.button if button.key == "next")
    assert nxt.disabled
    app = _click_key(app, "show-me")
    assert _visible(app).count("Insight:") == 1
    app.session_state["done_parts"] = []
    app.run()
    app = _click_key(app, "show-me")
    assert _visible(app).count("Insight:") == 1
    for title in (
        "Causes that get under 1%",
        "What the companies say",
        "Does the plan get under 1%",
    ):
        app = _click_key(app, "next")
        visible = _visible(app)
        assert title in visible
        assert "Things to notice" in visible
        assert "Your question or insight" in visible
        assert "Show me" in visible
        nxt = next(button for button in app.button if button.key == "next")
        assert nxt.disabled
        app = _click_key(app, "show-me")
        nxt = next(button for button in app.button if button.key == "next")
        assert not nxt.disabled


def test_a_failed_deck_does_not_print_the_exception(monkeypatch):
    def boom(_path, _facts):
        raise RuntimeError("postgres://secret-host/db password=hunter2")

    monkeypatch.setattr("invalid_agent.artifacts.deck.write_deck", boom)
    app = _run_app(monkeypatch)
    app.session_state["story_week"] = 4
    app.session_state["unlocked_week"] = 4
    app.run()
    assert not app.exception, app.exception
    app = _click_key(app, "prepare-deck")
    visible = _visible(app)
    assert "did not build" in visible
    assert "hunter2" not in visible
    assert "postgres://" not in visible
