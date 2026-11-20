"""Step catalog for the guided demo.

Plain-language copy lives here so a test can lock the order without
starting Streamlit. Nothing in this module computes a rate.
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
    needs_case: bool = False
    question_ids: tuple[str, ...] = ()
    match_case: bool = True


GUIDE_STEPS: tuple[GuideStep, ...] = (
    GuideStep(
        id="complaint",
        short="Complaint",
        title="The complaint",
        doing=(
            "The agent starts from the complaint. It states the promise the customer was sold "
            "and the limit of the file in front of it."
        ),
        why=(
            "The charts only mean something once you know what invalid was supposed to mean. "
            "Validity was promised at 98% or better, so the invalid rate has to stay at or below 2%. "
            "On public MAUDE reports that 2% cap is not estimable, because the file has no count of successful runs."
        ),
        look=(
            "Read the promise and the banner. This is screen 1 of 10. "
            "Next comes the case, the control chart, the Pareto, the strata, the projection, "
            "the week's writing, the audience notes, the Jira tickets, and the week-4 pitch. "
            "Free explore, in the header, opens the full panel at any time."
        ),
        next_label="Choose a case",
    ),
    GuideStep(
        id="case",
        short="Case",
        title="Choose the case",
        doing=(
            "The agent loads one case file: the complaint, the device, the window, "
            "and the columns it is allowed to break on."
        ),
        why=(
            "OOI and JJE are real openFDA MAUDE extracts in Neon. "
            "The other files are synthetic so CI can run with no database. "
            "The complaint on this screen is the one the rest of the walk investigates."
        ),
        look=(
            "Read the complaint for the case you selected. "
            "The buttons are the cases this page is offering. "
            "The hosted demo offers the two MAUDE product codes, OOI and JJE. "
            "A full list appears only when this run also has other case files."
        ),
        next_label="Investigate this case",
    ),
    GuideStep(
        id="chart",
        short="Control chart",
        title="The control chart",
        doing=(
            "The agent asks Python for the weekly invalid rate, the Wilson interval, and a p-chart. "
            "Western Electric rule 1 marks a point outside the control limits. "
            "The model is asked only for wording, and only when rules-only is off."
        ),
        why=(
            "The first question is whether the rate is a stable process or whether some weeks leave the limits. "
            "The measurements stay on this file when the investigation week changes. "
            "The week changes what the team has been told and the color of the status note."
        ),
        look=(
            "Red marks are rule 1. The tiles are the rate, the interval, the escalate-or-hold call, "
            "and the RAG color for the week you selected."
        ),
        next_label="See where invalids concentrate",
        needs_case=True,
        question_ids=("ooi_share", "jje_weeks"),
    ),
    GuideStep(
        id="pareto",
        short="Pareto",
        title="Where invalids concentrate",
        doing=(
            "The agent ranks invalid types by count and cumulative share. "
            "Python builds the Pareto."
        ),
        why=(
            "A high overall rate can be one failure mode or a pile of small ones. "
            "The Pareto says which codes dominate before anyone argues about a lot or a manufacturer."
        ),
        look=(
            "The bars are counts. The line is the cumulative share. "
            "The largest bar is the code to read first. The root-cause call is the next step."
        ),
        next_label="Test the slices",
        needs_case=True,
        question_ids=("ooi_types",),
    ),
    GuideStep(
        id="strata",
        short="Strata",
        title="Strata and root cause",
        doing=(
            "The agent breaks the same file by one column at a time and scores each slice against the complement. "
            "A slice becomes the leading cause only when it clears the evidence bar: "
            "enough rows, enough extra invalids, enough lift, and a chi-square result inside the gate."
        ),
        why=(
            "The loudest complaint is not yet a cause. A one-off at 100% is not yet a cause. "
            "The ranker can stop at no single cause, and the agent has to leave it there."
        ),
        look=(
            "Pick a break. The table is n, k, and the rate. "
            "The sentence under it is the ranker's call for the whole file."
        ),
        next_label="Project containment",
        needs_case=True,
        question_ids=("jje_manufacturer",),
    ),
    GuideStep(
        id="projection",
        short="Before / after",
        title="Before and after",
        doing=(
            "The agent asks what the rate would be if the leading stratum's invalids were cleared on this same file. "
            "Python copies the table, clears that slice, and recomputes. The case file stays as it was."
        ),
        why=(
            "Leadership will ask what containment returns. "
            "The honest answer is a projection. The record stays open until a later file replaces it."
        ),
        look=(
            "The chart is before and after. The caption is the effectiveness label, "
            "including that this is not observed follow-up. "
            "When no slice cleared the bar, there is no removal to draw."
        ),
        next_label="Read this week's writing",
        needs_case=True,
    ),
    GuideStep(
        id="artifacts",
        short="Artifacts",
        title="This week's artifacts",
        doing=(
            "The agent writes the week's quality record from facts Python already stored: "
            "a triage memo, a fishbone, 5 Whys, an 8D/CAPA, and the plan with its risks. "
            "A model may phrase the memo and the notes when rules-only is off. "
            "A number that was not in the facts is rejected, and the template replaces that draft."
        ),
        why=(
            "The work product is the record, not only the chart. "
            "Each record answers a different question, so one of them is on screen at a time."
        ),
        look=(
            "Open one record. The plan table is the same plan as the Gantt file in the week folder. "
            "Change the week to see the plan and the decision move."
        ),
        next_label="Read the status notes",
        needs_case=True,
    ),
    GuideStep(
        id="notes",
        short="Status notes",
        title="Status notes",
        doing=(
            "The agent writes three notes from one set of facts: customer, internal, and leadership. "
            "The customer note leaves the cause unconfirmed. "
            "Leadership leads with RAG, cost, and the ask."
        ),
        why=(
            "The same rate has to be safe to send to a lab director and useful to the people who can approve containment. "
            "The color is a rule about the rate and the week."
        ),
        look=(
            "Choose an audience. Then walk Week 0 through Week 4. "
            "The decision line is what the agent logged that week."
        ),
        next_label="Open the Jira tickets",
        needs_case=True,
    ),
    GuideStep(
        id="jira",
        short="Jira",
        title="Jira tickets",
        doing=(
            "The agent reads the INV tickets for this case. "
            "With Jira credentials it links the live issues. Without them it shows the dry-run record. "
            "Creating a ticket stays on the owner's machine. This page only reads."
        ),
        why=(
            "The investigation is unfinished if the work is missing from the tracker the team already uses. "
            "The tickets are the plan."
        ),
        look=(
            "The table is the issues returned for this run. "
            "Live keys link to the Jira site. The project key is INV."
        ),
        next_label="Read the management pitch",
        needs_case=True,
    ),
    GuideStep(
        id="pitch",
        short="Pitch",
        title="The management pitch",
        doing=(
            "At week 4 the agent closes the loop: a recommendation, an effectiveness check, and a seven-slide deck. "
            "The effectiveness number is the projection from the earlier step. "
            "The prose has to say it is not observed follow-up."
        ),
        why=(
            "This is the meeting. Contain the leading stratum, or widen the pull. "
            "A projected rate is a projection."
        ),
        look=(
            "On an earlier week, open week 4. The pitch is the close-out. "
            "The deck file is written beside it. "
            "Look around on your own when you want every control on one page."
        ),
        next_label="Look around on your own",
        needs_case=True,
        question_ids=("ooi_share", "jje_manufacturer", "ooi_types", "jje_weeks"),
        match_case=False,
    ),
)

ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("triage", "Triage memo"),
    ("fishbone", "Fishbone"),
    ("five_whys", "5 Whys"),
    ("capa", "8D / CAPA"),
    ("plan", "Plan and risks"),
)

AUDIENCES: tuple[tuple[str, str], ...] = (
    ("customer", "Customer"),
    ("internal", "Internal"),
    ("leadership", "Leadership"),
)

SUGGESTED_CASE_IDS: tuple[str, ...] = ("openfda_ooi", "openfda_jje", "bad_lot")


def progress_label(index: int) -> str:
    return f"Step {index + 1} of {len(GUIDE_STEPS)}"


def rag_label(updates: dict[str, Any] | None) -> str:
    """RAG is read off the leadership note, the same strings status.py writes."""
    leadership = str((updates or {}).get("leadership") or "")
    if "RAG: Amber" in leadership:
        return "Amber"
    if "RAG: Green" in leadership:
        return "Green"
    return "Red"


def cause_sentence(top: dict[str, Any] | None) -> str:
    """One sentence from the ranker. The model does not choose the cause."""
    top = top or {}
    cause = str(top.get("cause") or "no_single_cause")
    summary = str(top.get("summary") or "").strip()
    if cause == "no_single_cause":
        lead = "The ranker stopped at no single cause."
        return f"{lead} {summary}".strip()
    level = top.get("level") or "the leading slice"
    lead = f"Python ranked this. The leading call is {cause} on {level}."
    if summary:
        return f"{lead} {summary}"
    return lead


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
    """Suggested MAUDE questions for this step.

    When ``match_case`` is set, a question tied to a product code is kept
    only for that case. The pitch lists every suggested question.
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
