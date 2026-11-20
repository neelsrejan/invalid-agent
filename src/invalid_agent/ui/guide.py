"""Step catalog for the guided demo.

Plain-language copy lives here so a test can lock the order without
starting Streamlit. Nothing in this module computes a rate.

The walk is four weeks. Each week has the same six parts, in order.
The page does not offer a way to jump to a later week.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GuideStep:
    id: str
    short: str
    title: str
    doing: str
    why: str
    look: str
    next_label: str
    needs_case: bool = True
    question_ids: tuple[str, ...] = ()
    match_case: bool = True


GUIDE_STEPS: tuple[GuideStep, ...] = (
    GuideStep(
        id="complaint",
        short="Complaint",
        title="The complaint",
        doing="The agent reads what came in this week and restates the promise.",
        why="The numbers only make sense after you know what 'invalid' was supposed to mean.",
        look="Read the promise, the device, and what arrived. The case list is on week 1.",
        next_label="See this week's numbers",
        needs_case=True,
    ),
    GuideStep(
        id="data",
        short="Data",
        title="This week's numbers",
        doing="Python counts the invalids in this week's slice of the file. The model does not do the math.",
        why="Each week adds the next part of the date range. Week 4 is the whole file.",
        look="Read the rate, the count, the likely range, and whether the later weeks sit higher.",
        next_label="See the charts",
    ),
    GuideStep(
        id="charts",
        short="Charts",
        title="The charts",
        doing="Python draws the weekly rate and the ranking of invalid types from the same counts as the number screen.",
        why="A picture should match the sentence. Both use one count of weeks that sit far above the usual rate.",
        look="The red marks, the biggest bars, and the leading group all come from this week's slice.",
        next_label="See what gets logged",
        question_ids=("ooi_share", "jje_weeks"),
    ),
    GuideStep(
        id="logged",
        short="Logged",
        title="What gets logged",
        doing="The agent lists the tickets for this week. A confirmed insight becomes the next ticket.",
        why="A finding that is not written down gets lost before the next week.",
        look="Plan tickets start at INV-1. Your own findings are Your ticket 1, then Your ticket 2.",
        next_label="Read the notes",
    ),
    GuideStep(
        id="notes",
        short="Notes",
        title="Root-cause notes",
        doing="The agent writes three notes from the same counts: customer, team, and leadership.",
        why="The lab can hear the rate. The team can hear the leading group. Leadership can hear the cost.",
        look="Pick who the note is for. The cause sentence stays the same.",
        next_label="Read the week wrap-up",
    ),
    GuideStep(
        id="wrap",
        short="Wrap-up",
        title="Week wrap-up",
        doing="The agent writes this week's recommendation in full, including the what-if on the same file.",
        why="The pitch is part of every week. It is not a button that jumps to the last week.",
        look="Read what came in, what the counts say, and what we recommend. Then the next week unlocks.",
        next_label="Start the next week",
        question_ids=("ooi_share", "jje_manufacturer", "ooi_types", "jje_weeks"),
        match_case=False,
    ),
)

BEATS = GUIDE_STEPS

AUDIENCES: tuple[tuple[str, str], ...] = (
    ("customer", "Customer"),
    ("internal", "Internal team"),
    ("leadership", "Leadership"),
)

def progress_label(week: int, beat: int) -> str:
    return f"Week {int(week)} of 4 — Part {int(beat) + 1} of {len(GUIDE_STEPS)}"


def questions_for(
    step: GuideStep,
    product_code: str | None,
    catalog: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    """Suggested questions for this step.

    When ``match_case`` is set, a question tied to a product code is kept
    only for that case. The wrap-up lists every suggested question.
    The guided page does not run these against a second calculator.
    """
    code = (product_code or "").strip().upper()
    by_id = {str(item["id"]): item for item in catalog}
    chosen: list[dict[str, Any]] = []
    for question_id in step.question_ids:
        item = by_id.get(question_id)
        if item is None:
            continue
        params_code = str((item.get("params") or {}).get("product_code") or "").upper()
        if step.match_case and params_code and params_code != code:
            continue
        chosen.append(item)
    return chosen
