"""The projection is a lower rate, and the Streamlit app renders the banner."""

from pathlib import Path

from invalid_agent.metrics.effectiveness import projection_summary
from invalid_agent.metrics.hypotheses import rank_hypotheses
from invalid_agent.sim.generate import generate, load_scenario

ROOT = Path(__file__).resolve().parents[1]


def test_removing_the_bad_lot_drops_the_rate():
    scenario = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    df = generate(scenario)
    top = rank_hypotheses(df, scenario["spec_invalid_rate"])[0]
    summary = projection_summary(df, top, scenario["spec_invalid_rate"], scenario["promised_validity"])
    assert summary["applied"] is True
    assert summary["after"]["rate"] < summary["before"]["rate"]
    assert "Not observed" in summary["label"]


def _visible(app) -> str:
    chunks = []
    for name in ("markdown", "caption", "header", "subheader", "title", "text", "info", "warning", "error", "html"):
        for item in getattr(app, name, []):
            chunks.append(str(getattr(item, "value", "")))
    return "\n".join(chunks)


def _click(app, label: str):
    matches = [button for button in app.button if button.label == label]
    assert matches, f"missing button {label!r}; have {[button.label for button in app.button]}"
    matches[0].click()
    app.run()
    assert not app.exception, app.exception
    return app


def test_guided_walk_then_free_explore(monkeypatch):
    from streamlit.testing.v1 import AppTest

    from invalid_agent.ui.guide import GUIDE_STEPS

    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180)
    app.run()
    assert not app.exception, app.exception
    visible = _visible(app)
    assert "Not for clinical use" in visible
    assert "Step 1 of 10" in visible
    assert "The complaint" in visible
    assert not app.metric
    assert not any(box.label == "Break by" for box in app.selectbox)

    for step in GUIDE_STEPS:
        visible = _visible(app)
        assert step.title in visible
        assert f"Step {GUIDE_STEPS.index(step) + 1} of 10" in visible
        if step.id == "case":
            assert "Northlake Health" in visible
            app = _click(app, "Back")
            assert "The complaint" in _visible(app)
            app = _click(app, GUIDE_STEPS[0].next_label)
            assert "Choose the case" in _visible(app)
        if step.id == "chart":
            assert app.metric
            assert "Western Electric" in visible
        if step.id == "strata":
            assert "L-4419" in visible
        if step.id == "projection":
            assert "Projected if the leading stratum is removed" in visible
        if step.id == "artifacts":
            assert "Week-0 triage memo" in visible
            app = _click(app, "Fishbone")
            assert "# Fishbone" in _visible(app)
        if step.id == "notes":
            assert "Customer update" in visible
            app = _click(app, "Leadership")
            assert "Leadership update" in _visible(app)
        if step.id == "jira":
            assert "dry-run" in visible
            assert "INV" in visible
        if step.id == "pitch":
            assert "week 4" in visible
            app = _click(app, "Open the week-4 pitch")
            pitched = _visible(app)
            assert "Week-4 close-out" in pitched
            assert pitched.count("Contain L-4419. Do not extend") == 1
            assert "The seven-slide deck is exec_deck.pptx." in pitched
            assert "/dashboard/" not in pitched
        app = _click(app, step.next_label)

    visible = _visible(app)
    assert "Ask the MAUDE table" in visible
    assert "Free explore shows every control on this page." in visible
    assert any(box.label == "Break by" for box in app.selectbox)
    assert any(slider.label == "Investigation week" for slider in app.slider)
    explore = next(toggle for toggle in app.toggle if toggle.label == "Free explore")
    assert explore.value is True

    app = _click(app, "Return to the guided steps")
    visible = _visible(app)
    assert "Step 10 of 10" in visible
    assert "The management pitch" in visible
    explore = next(toggle for toggle in app.toggle if toggle.label == "Free explore")
    assert explore.value is False


def _run_app(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180)
    app.run()
    assert not app.exception, app.exception
    return app


def _toggle(app, label: str, value: bool):
    control = next(item for item in app.toggle if item.label == label)
    control.set_value(value)
    app.run()
    assert not app.exception, app.exception
    return app


def test_case_and_week_persist_across_steps_and_free_explore(monkeypatch):
    """A case and week chosen off the default survive later steps and Free explore.

    Streamlit drops a widget key when that widget is not rendered. The page
    has to keep scenario_label and week anyway.
    """
    app = _run_app(monkeypatch)
    app = _click(app, "Choose a case")
    cases = next(item for item in app.selectbox if item.label == "All cases")
    target = next(option for option in cases.options if str(option).startswith("drift_clear"))
    cases.select(target)
    app.run()
    assert not app.exception, app.exception
    assert str(app.session_state["scenario_label"]).startswith("drift_clear")

    app = _click(app, "Investigate this case")
    assert "Case drift_clear · week 0" in _visible(app)
    app = _click(app, "Week 2")
    assert "Case drift_clear · week 2" in _visible(app)
    assert app.session_state["week"] == 2

    app = _click(app, "See where invalids concentrate")
    app = _click(app, "Test the slices")
    assert "Step 5 of 10" in _visible(app)
    assert "Case drift_clear · week 2" in _visible(app)
    assert str(app.session_state["scenario_label"]).startswith("drift_clear")
    assert app.session_state["week"] == 2

    app = _toggle(app, "Free explore", True)
    scenario = next(item for item in app.selectbox if item.label == "Scenario")
    week = next(item for item in app.slider if item.label == "Investigation week")
    assert str(scenario.value).startswith("drift_clear")
    assert week.value == 2
    week.set_value(3)
    app.run()
    assert not app.exception, app.exception
    assert app.session_state["week"] == 3
    assert str(app.session_state["scenario_label"]).startswith("drift_clear")

    app = _toggle(app, "Free explore", False)
    visible = _visible(app)
    assert "Step 5 of 10" in visible
    assert "Case drift_clear · week 3" in visible
    assert str(app.session_state["scenario_label"]).startswith("drift_clear")
    assert app.session_state["week"] == 3
