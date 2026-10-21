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


def test_streamlit_app_renders_the_banner():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=120)
    app.run()
    assert not app.exception
    blob = " ".join(str(getattr(item, "value", "")) for item in app.markdown)
    assert "Not for clinical use" in blob
    assert app.metric
