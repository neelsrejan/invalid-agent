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
            assert "Week-4 close-out" in _visible(app)
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
