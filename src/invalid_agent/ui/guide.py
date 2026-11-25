"""Step catalog for the guided demo.

Plain-language copy lives here so a test can lock the order without
starting Streamlit. Nothing in this module computes a rate.

The walk is four weeks. Each week is one page. The page does not offer a way to jump ahead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GuideStep:
    id: str
    short: str
    title: str
    next_label: str
    needs_case: bool = True
    question_ids: tuple[str, ...] = ()
    match_case: bool = True


GUIDE_STEPS: tuple[GuideStep, ...] = (
    GuideStep(
        id="eda",
        short="Companies",
        title="Who is over 1%",
        next_label="See the returned complaint detail",
    ),
    GuideStep(
        id="pareto",
        short="Causes",
        title="Causes that get under 1%",
        next_label="See the company responses",
    ),
    GuideStep(
        id="responses",
        short="Responses",
        title="What the companies say",
        next_label="See the close-out",
    ),
    GuideStep(
        id="closeout",
        short="Close-out",
        title="Does the plan get under 1%",
        next_label="Finish the story",
    ),
)

BEATS = GUIDE_STEPS

AUDIENCES: tuple[tuple[str, str], ...] = (
    ("customer", "Customer"),
    ("internal", "Internal team"),
    ("leadership", "Leadership"),
)

def progress_label(week: int, beat: int) -> str:
    del beat
    return f"Week {int(week)} of 4"


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
