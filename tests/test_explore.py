"""Week-visible lookups answer from the rows in hand, and not from a later week."""

import pandas as pd

from invalid_agent.sim.generate import generate, load_scenario
from invalid_agent.ui.explore import (
    category_ranking,
    explore_facts,
    invalid_total,
    manufacturer_ranking,
    report_total,
    week_over_week,
)
from invalid_agent.ui.story import slice_through_story_week
from invalid_agent.ui.talkback import example_prompts, respond

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1] / "scenarios" / "bad_lot.yaml"


def _span() -> pd.DataFrame:
    start = pd.Timestamp("2025-01-01")
    middle = start + pd.Timedelta(days=40)
    end = start + pd.Timedelta(days=100)
    rows = []
    for index in range(10):
        rows.append(
            {
                "date": start,
                "invalid": index < 5,
                "invalid_code": "INV-MECH" if index < 4 else ("INV-IC" if index == 4 else ""),
                "manufacturer": "Acme" if index < 6 else "Other",
            }
        )
    for _index in range(10):
        rows.append(
            {
                "date": middle,
                "invalid": True,
                "invalid_code": "INV-VOL",
                "manufacturer": "Other",
            }
        )
    for _index in range(80):
        rows.append(
            {
                "date": end,
                "invalid": True,
                "invalid_code": "INV-SW",
                "manufacturer": "FutureCo",
            }
        )
    return pd.DataFrame(rows)


def test_counts_ranking_and_manufacturer_use_only_the_visible_rows():
    frame = _span()
    visible = slice_through_story_week(frame, 1)
    assert report_total(visible) == 10
    assert invalid_total(visible) == 5
    assert report_total(visible) < report_total(frame)
    ranking = category_ranking(visible)
    codes = visible.loc[visible["invalid"].astype(bool), "invalid_code"].astype(str).value_counts()
    assert ranking[0]["code"] == str(codes.index[0])
    assert ranking[0]["count"] == int(codes.iloc[0])
    assert [row["code"] for row in ranking] == ["INV-MECH", "INV-IC"]
    assert ranking[0]["count"] == 4
    makers = manufacturer_ranking(visible)
    assert makers[0]["name"] == "Acme"
    assert makers[0]["count"] == 6
    assert makers[0]["share"] == 0.6
    assert all(row["name"] != "FutureCo" for row in makers)
    assert week_over_week(frame, 1) is None
    change = week_over_week(frame, 2)
    assert change is not None
    assert change["reports_then"] == 10
    assert change["reports_now"] == 20
    assert change["reports_now"] < report_total(frame)


def test_neel_prompts_return_the_week_one_numbers_and_do_not_unlock():
    frame = _span()
    facts = explore_facts(frame, 1, product_code="OOI", device="Multiplex", estimable=False)
    view = {
        "story_week": 1,
        "explore": facts,
        "fda": True,
        "direction": "flat",
        "direction_sentence": "The rate is not steadily going up.",
        "rate_sentence": "The share of reports this week is 50.00% (5 of 10).",
        "device_line": "Device: Multiplex.",
    }
    count = respond(
        "How many complaints are in the dataset",
        view,
        "complaint",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert count["confirmed"] is False
    assert not count["text"].startswith("YEP")
    assert "10" in count["text"]
    assert "100" not in count["text"]
    assert "FutureCo" not in count["text"]
    assert "80" not in count["text"]
    maker = respond(
        "Who is the main manufacturer from this weeks reports",
        view,
        "data",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert maker["confirmed"] is False
    assert "Acme" in maker["text"]
    assert "6" in maker["text"]
    assert "FutureCo" not in maker["text"]
    ranked = respond(
        "Which invalid categories are highest to lowest?",
        view,
        "complaint",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert ranked["confirmed"] is False
    assert ranked["text"].index("INV-MECH") < ranked["text"].index("INV-IC")
    assert "INV-SW" not in ranked["text"]
    insight = respond(
        facts["category_sentence"],
        view,
        "complaint",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert insight["confirmed"] is True
    assert insight["text"].startswith("YEP")
    prompts = " ".join(example_prompts(view, "complaint"))
    assert "going up" not in prompts
    assert "How many complaints" in prompts


def test_bad_lot_week_one_explore_does_not_count_the_rest_of_the_file():
    scenario = load_scenario(ROOT)
    frame = generate(scenario)
    facts = explore_facts(frame, 1, device=str(scenario.get("device") or ""), estimable=True)
    visible = slice_through_story_week(frame, 1)
    assert facts["total"] == len(visible)
    assert facts["total"] < len(frame)
    assert facts["change"] is None
    assert "quarter" not in facts["category_sentence"]
    assert "subset" not in facts["category_sentence"]
