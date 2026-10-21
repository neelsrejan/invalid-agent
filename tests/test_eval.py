"""The evidence ranker and the keyword ranker disagree where the YAML says they should."""

from pathlib import Path

from evals.run_eval import keyword_cause, scenario_paths, score_scenario
from invalid_agent.sim.generate import load_scenario

ROOT = Path(__file__).resolve().parents[1]


def test_every_scenario_matches_its_expected_call():
    misses = []
    for path in scenario_paths(ROOT):
        row = score_scenario(load_scenario(path))
        if not row["top1"] or not row["top3"]:
            misses.append(f"{row['id']} evidence={row['evidence']} expect={row['expect']}")
    assert misses == []
    assert len(scenario_paths(ROOT)) >= 15


def test_keyword_ranker_takes_the_herring_and_misses_a_silent_complaint():
    herring = load_scenario(ROOT / "scenarios" / "herring_software.yaml")
    assert keyword_cause(herring) == "software_version"
    scored = score_scenario(herring)
    assert scored["evidence"] == "bad_reagent_lot"
    assert scored["keyword_hit"] is False

    quiet = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    assert keyword_cause(quiet) == "no_single_cause"
    assert score_scenario(quiet)["evidence"] == "bad_reagent_lot"


def test_weak_lot_stays_below_the_bar():
    row = score_scenario(load_scenario(ROOT / "scenarios" / "weak_lot.yaml"))
    assert row["below_bar"] is True
    assert row["evidence"] == "no_single_cause"
    assert row["keyword"] == "bad_reagent_lot"
    assert row["top1"] is True
