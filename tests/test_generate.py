"""The bad-lot scenario is repeatable and the injected lot is the one that moves."""

from pathlib import Path

import pandas as pd

from invalid_agent.sim.generate import generate, load_scenario, summarize
from invalid_agent.sim.openfda import build_query, fetch_event_count
from invalid_agent.sim.seeds import COMPLAINT_THEMES

ROOT = Path(__file__).resolve().parents[1]
BAD_LOT = ROOT / "scenarios" / "bad_lot.yaml"


def test_bad_lot_exceeds_spec_and_the_named_lot_is_the_outlier():
    scenario = load_scenario(BAD_LOT)
    df = generate(scenario)
    assert len(df) == 180 * 80
    invalid_rate = df["invalid"].mean()
    assert invalid_rate > scenario["spec_invalid_rate"]
    by_lot = df.groupby("reagent_lot")["invalid"].mean()
    assert by_lot["L-4419"] > 0.10
    others = by_lot.drop(labels=["L-4419"])
    assert by_lot["L-4419"] > 5 * others.max()
    text = summarize(df, scenario)
    assert "EXCEEDS SPEC" in text
    assert "L-4419" in text
    assert "Synthetic data. Not for clinical use." in text


def test_generation_is_repeatable():
    scenario = load_scenario(BAD_LOT)
    first = generate(scenario)
    second = generate(scenario)
    pd.testing.assert_frame_equal(first, second)


def test_complaint_themes_are_local_and_openfda_is_not_required(monkeypatch):
    assert len(COMPLAINT_THEMES) >= 4

    def explode(*_args, **_kwargs):
        raise OSError("no network in this test")

    monkeypatch.setattr("invalid_agent.sim.openfda.urlopen", explode)
    assert fetch_event_count("should-not-be-sent") is None
    url, params = build_query("")
    assert url.startswith("https://api.fda.gov/")
    assert "api_key" not in params
    _url, keyed = build_query("optional-key")
    assert keyed["api_key"] == "optional-key"
