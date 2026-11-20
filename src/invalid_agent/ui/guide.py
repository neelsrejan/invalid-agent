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
        look="Ticket numbers start at INV-1. Open tickets carry into the next week.",
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

ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("triage", "Triage memo"),
    ("fishbone", "Fishbone"),
    ("five_whys", "5 Whys"),
    ("capa", "8D / CAPA"),
    ("plan", "Plan and risks"),
)

AUDIENCES: tuple[tuple[str, str], ...] = (
    ("customer", "Customer"),
    ("internal", "Internal team"),
    ("leadership", "Leadership"),
)

SUGGESTED_CASE_IDS: tuple[str, ...] = ("openfda_ooi", "openfda_jje", "bad_lot")


def progress_label(week: int, beat: int) -> str:
    return f"Week {int(week)} of 4 — Part {int(beat) + 1} of {len(GUIDE_STEPS)}"


def rag_label(updates: dict[str, Any] | None) -> str:
    """RAG is read off the leadership note, the same strings status.py writes."""
    leadership = str((updates or {}).get("leadership") or "")
    if "RAG: Amber" in leadership:
        return "Amber"
    if "RAG: Green" in leadership:
        return "Green"
    return "Red"


def cause_sentence(top: dict[str, Any] | None) -> str:
    """One plain sentence from the ranker. The model does not choose the cause."""
    top = top or {}
    cause = str(top.get("cause") or "no_single_cause")
    if cause == "no_single_cause":
        return "No single group stands out yet. We will not pretend we know the cause."
    level = top.get("level") or "the leading group"
    lift = top.get("lift")
    try:
        ratio = None if lift is None else float(lift)
    except (TypeError, ValueError):
        ratio = None
    if ratio is None or ratio != ratio or ratio in {float("inf"), float("-inf")}:
        ratio_line = "The other rows had no invalids, so we do not quote how many times higher this group is."
    else:
        ratio_line = f"Its invalid share is about {ratio:.1f} times the share in the other rows."
    return f"The strongest group is {level}. {ratio_line}"


def decision_for_week(log: list[dict[str, Any]] | None, week: int) -> str:
    for entry in log or []:
        try:
            entry_week = int(entry.get("week", -1))
        except (TypeError, ValueError):
            continue
        if entry_week == int(week):
            return str(entry.get("decision") or "")
    return ""


def arrivals(scenario: dict[str, Any], week: int) -> str:
    """Who spoke this week. Injections are citations, not scores."""
    found: list[str] = []
    for item in scenario.get("injections") or []:
        try:
            item_week = int(item.get("week", -1))
        except (TypeError, ValueError):
            continue
        if item_week != int(week):
            continue
        source = str(item.get("source") or "update")
        audience = str(item.get("audience") or "").strip()
        found.append(f"{source} ({audience})" if audience else source)
    if not found:
        return ""
    return "What arrived this week: " + "; ".join(found) + "."


def stratum_label(column: str, scenario: dict[str, Any]) -> str:
    labels = scenario.get("strata_labels") or {}
    if column in labels:
        return str(labels[column])
    return column.replace("_", " ")


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
