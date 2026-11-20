"""Week slices, ticket numbers, and plain sentences stay inside the facts."""

import math
import re

import pandas as pd

from invalid_agent.metrics.hypotheses import rank_hypotheses
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.plain import PUBLIC_BANNER, unexplained_jargon
from invalid_agent.ui.story import beat_lines, build_week_view, slice_through_story_week

ROOT_SCENARIO = __import__("pathlib").Path(__file__).resolve().parents[1] / "scenarios" / "bad_lot.yaml"


def _toy_frame() -> pd.DataFrame:
    rows = []
    for index in range(200):
        rows.append(
            {
                "date": "2025-04-01",
                "invalid": True,
                "invalid_code": "INV-NOR" if index < 150 else "INV-MECH",
                "manufacturer": "ABBOTT",
                "reagent_lot": "UNREPORTED",
            }
        )
    for _index in range(200):
        rows.append(
            {
                "date": "2025-04-01",
                "invalid": False,
                "invalid_code": "",
                "manufacturer": "OTHER",
                "reagent_lot": "UNREPORTED",
            }
        )
    return pd.DataFrame(rows)


def _toy_scenario() -> dict:
    return {
        "id": "toy",
        "title": "Toy case",
        "device": "Toy device",
        "start_date": "2025-04-01",
        "horizon_days": 30,
        "spec_invalid_rate": 0.02,
        "promised_validity": 0.98,
        "cost_per_invalid_usd": 85,
        "complaint": "A toy complaint about invalids.",
        "strata_columns": ["manufacturer", "reagent_lot"],
        "strata_labels": {"manufacturer": "Company", "reagent_lot": "Reported lot"},
        "injections": [],
        "denominator": "synthetic_runs",
    }


def test_zero_complement_does_not_store_an_infinite_ratio():
    ranked = rank_hypotheses(_toy_frame(), 0.02)
    assert ranked[0]["cause"] != "no_single_cause"
    assert ranked[0]["lift"] is None or math.isfinite(float(ranked[0]["lift"]))
    assert "inf" not in str(ranked[0]["summary"]).casefold()


def test_week_slices_grow_and_week_four_is_the_whole_file():
    scenario = load_scenario(ROOT_SCENARIO)
    from invalid_agent.sim.generate import generate

    frame = generate(scenario)
    first = slice_through_story_week(frame, 1)
    last = slice_through_story_week(frame, 4)
    assert len(first) < len(last)
    assert len(last) == len(frame)
    early = build_week_view(scenario, frame, 1)
    full = build_week_view(scenario, frame, 4)
    assert early["n"] < full["n"]
    assert "first quarter" in early["window_sentence"]
    assert "would have arrived first" in early["window_sentence"]
    one_day = _toy_frame()
    one_view = build_week_view(_toy_scenario(), one_day, 1)
    assert "whole file" in one_view["window_sentence"]
    assert "first quarter" not in one_view["window_sentence"]
    assert "whole date range" in full["window_sentence"]
    assert early["call_label"] in {"Watch", "Look harder"}
    assert "kept the leading read" not in early["decision"]
    assert "kept the leading read" not in full["decision"]
    assert early["glossary"] == ""


def test_break_follows_the_ranker_and_skips_unreported():
    view = build_week_view(_toy_scenario(), _toy_frame(), 1)
    assert view["default_break"] == "manufacturer"
    assert view["level"] == "ABBOTT"
    lot_rows = view["breaks"]["reagent_lot"]["rows"]
    assert lot_rows == []
    assert view["breaks"]["reagent_lot"]["unreported_n"] == 400
    assert "UNREPORTED" not in str(lot_rows)
    assert re.search(r"(?<![\d.])0\.00%", view["projection_sentence"]) is None
    assert " to 0%" in view["projection_sentence"]
    assert "not a real repair" in view["projection_sentence"]
    assert view["tickets"][0]["key"] == "INV-1"
    names = " ".join(row["name"] for row in view["tickets"])
    assert "Retest" not in names


def test_week_two_names_the_recheck_and_keeps_inv_1():
    scenario = load_scenario(ROOT_SCENARIO)
    from invalid_agent.sim.generate import generate

    view = build_week_view(scenario, generate(scenario), 2)
    keys = [row["key"] for row in view["tickets"]]
    assert keys[0] == "INV-1"
    assert keys == sorted(keys, key=lambda key: int(key.split("-")[1]))
    assert any(row["name"] == "Check the next-best group again" for row in view["tickets"])
    assert "kept the leading read" not in view["decision"]
    assert view["call_label"] != "Hold"
    assert all("Retest" not in row["name"] for row in view["tickets"])


def test_every_week_has_a_wrap_up_body_and_no_bare_jargon():
    scenario = load_scenario(ROOT_SCENARIO)
    from invalid_agent.sim.generate import generate

    frame = generate(scenario)
    for week in (1, 2, 3, 4):
        view = build_week_view(scenario, frame, week)
        for beat in ("complaint", "data", "charts", "logged", "notes", "wrap"):
            text = "\n".join(beat_lines(view, beat))
            assert unexplained_jargon(text) == [], unexplained_jargon(text)
        data = "\n".join(beat_lines(view, "data"))
        charts = "\n".join(beat_lines(view, "charts"))
        assert "This chart" not in data
        assert "This chart" in charts
        wrap = "\n".join(beat_lines(view, "wrap"))
        assert "What we recommend" in wrap
        assert "Open the week-4" not in wrap
        assert "0.00%" not in wrap
    assert unexplained_jargon(PUBLIC_BANNER) == []
    assert unexplained_jargon("What is MAUDE?") == []
    assert unexplained_jargon("(FDA product code OOI)") == []
    assert unexplained_jargon("OOI showed up again.") != []


def test_the_public_banner_is_the_only_maude_explanation():
    from invalid_agent.ui.plain import PUBLIC_BANNER, gloss_once, gloss_seen_for_banner, plain_case_label

    seen = gloss_seen_for_banner(True)
    case = gloss_once(
        f"Case: {plain_case_label('OOI nucleic-acid systems, invalid-type share of MAUDE reports')}. Week 1.",
        seen,
    )
    device = gloss_once("Device: Multiplex / nucleic acid amplification systems (FDA product code OOI).", seen)
    blob = "\n".join((PUBLIC_BANNER, case, device))
    assert blob.casefold().count("public database of device problem reports") == 1
    assert blob.casefold().count("machines that run many nucleic-acid tests") == 1
    assert "OOI means" not in blob


def test_hosted_case_files_explain_maude_ooi_and_jje():
    import yaml

    from invalid_agent.ui.plain import with_gloss

    root = __import__("pathlib").Path(__file__).resolve().parents[1] / "cases"
    for name in ("openfda_ooi.yaml", "openfda_jje.yaml"):
        data = yaml.safe_load((root / name).read_text())
        assert unexplained_jargon(str(data["device"])) == [], data["device"]
        shown = with_gloss(str(data["complaint"]))
        assert unexplained_jargon(shown) == [], shown
    from invalid_agent.ui.talkback import example_prompts

    fda_view = {"fda": True, "majority": False}
    for prompt in example_prompts(fda_view, "complaint"):
        assert unexplained_jargon(prompt) == [], prompt


def test_chart_text_uses_plain_labels():
    from invalid_agent.artifacts.charts import p_chart_figure, pareto_figure

    view = build_week_view(_toy_scenario(), _toy_frame(), 1)
    weekly = p_chart_figure(
        view["chart"],
        title="Weekly share of reports",
        y_title="Share of reports (%)",
        series_name="Share of reports",
    )
    ranking = pareto_figure(view["pareto"], count_title="Reports")
    for figure in (weekly, ranking):
        blob = _figure_text(figure)
        assert unexplained_jargon(blob) == [], unexplained_jargon(blob)
        assert "UCL" not in blob
        assert "Cumulative" not in blob
    assert "no usable result (INV-NOR)" in _figure_text(ranking)


def _figure_text(figure) -> str:
    layout = figure.layout
    parts = [str(layout.title.text or ""), str(layout.yaxis.title.text or "")]
    y2 = getattr(layout, "yaxis2", None)
    if y2 is not None and y2.title is not None:
        parts.append(str(y2.title.text or ""))
    for trace in figure.data:
        parts.append(str(trace.name or ""))
        parts.append(str(getattr(trace, "hovertemplate", "") or ""))
        values = getattr(trace, "x", None) or []
        parts.extend(str(value) for value in values)
    return "\n".join(parts)
