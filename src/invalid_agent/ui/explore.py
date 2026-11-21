"""Lookups over the rows visible as of one story week.

Every number comes from that slice. A later week is not counted.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from invalid_agent.metrics.pareto import pareto
from invalid_agent.ui.plain import code_plain, format_percent

_BLANK = {"", "UNREPORTED", "NAN", "NONE", "NAT"}


def report_total(frame: pd.DataFrame) -> int:
    return int(len(frame))


def invalid_total(frame: pd.DataFrame) -> int:
    if frame.empty or "invalid" not in frame.columns:
        return 0
    return int(frame["invalid"].astype(bool).sum())


def category_ranking(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Invalid categories, highest count first. Share is of the invalid rows."""
    ranked: list[dict[str, Any]] = []
    if frame.empty or "invalid" not in frame.columns:
        return ranked
    for row in pareto(frame):
        ranked.append(
            {
                "code": str(row["code"]),
                "plain": code_plain(str(row["code"])),
                "count": int(row["count"]),
                "share": float(row["share"]),
            }
        )
    return ranked


def manufacturer_ranking(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Named manufacturers, highest report count first. Share is of all visible rows."""
    if frame.empty or "manufacturer" not in frame.columns:
        return []
    names = frame["manufacturer"].fillna("").astype(str).str.strip()
    names = names[~names.str.upper().isin(_BLANK)]
    total = report_total(frame)
    if total == 0 or names.empty:
        return []
    ranked: list[dict[str, Any]] = []
    for name, count in names.value_counts().items():
        ranked.append({"name": str(name), "count": int(count), "share": int(count) / total})
    return ranked


def week_over_week(frame: pd.DataFrame, week: int) -> dict[str, int] | None:
    """Compare the rows visible as of this week with the rows visible as of the week before."""
    current = int(week)
    if current < 2:
        return None
    from invalid_agent.ui.story import slice_through_story_week

    now = slice_through_story_week(frame, current)
    then = slice_through_story_week(frame, current - 1)
    return {
        "reports_now": report_total(now),
        "reports_then": report_total(then),
        "invalid_now": invalid_total(now),
        "invalid_then": invalid_total(then),
    }


def explore_facts(
    frame: pd.DataFrame,
    week: int,
    *,
    product_code: str = "",
    device: str = "",
    estimable: bool = True,
) -> dict[str, Any]:
    """Facts the agent may say for this week. Later rows are not in the counts."""
    from invalid_agent.ui.story import slice_through_story_week

    current = min(4, max(1, int(week)))
    visible = slice_through_story_week(frame, current)
    categories = category_ranking(visible)
    makers = manufacturer_ranking(visible)
    total = report_total(visible)
    invalid = invalid_total(visible)
    top = categories[0] if categories else {}
    return {
        "week": current,
        "total": total,
        "invalid_total": invalid,
        "invalid_share": (invalid / total) if total else 0.0,
        "categories": categories,
        "manufacturers": makers,
        "top_code": str(top.get("code") or ""),
        "top_plain": str(top.get("plain") or ""),
        "top_count": int(top.get("count") or 0),
        "product_code": str(product_code or "").strip(),
        "device": str(device or "").strip() or "the device",
        "estimable": bool(estimable),
        "noun": "runs" if estimable else "complaints",
        "change": week_over_week(frame, current),
        "category_sentence": _category_sentence(current, top, invalid),
    }


def _category_sentence(week: int, top: dict[str, Any], invalid: int) -> str:
    if not top:
        return f"As of week {week}, there are no invalid categories so far."
    return (
        f"As of week {week}, the biggest invalid category so far is {top['plain']} "
        f"({int(top['count'])} of {int(invalid)})."
    )


def match_intent(text: str) -> str | None:
    """Pick a lookup from the question. None when the words are not a lookup."""
    lowered = " ".join(str(text or "").casefold().split())
    if not lowered:
        return None
    if re.search(r"\bmanufactur", lowered) or "who report" in lowered:
        return "manufacturers"
    if re.search(r"\b(categor|invalid types?|highest to lowest|high to low|ranked)\b", lowered):
        return "categories"
    if re.search(r"week over week|last week|previous week|from week", lowered):
        return "wow"
    if re.search(r"how many|how much|number of|count of", lowered) and re.search(
        r"complaint|report|dataset|data set|\brows\b|\bruns?\b", lowered
    ):
        return "total"
    if re.search(r"product code|supposed to do|\bdevice\b", lowered):
        return "device"
    if "invalid rate" in lowered or ("share" in lowered and "report" in lowered):
        return "rate"
    if "going up" in lowered or "going down" in lowered or re.search(
        r"\brate\b.{0,40}\b(up|down|higher|lower)\b", lowered
    ):
        return "direction"
    return None


def answer_for(intent: str, view: dict[str, Any]) -> str:
    """One short answer. The numbers are the week facts, never a guess."""
    facts = view.get("explore") or {}
    week = int(facts.get("week") or view.get("story_week") or 1)
    if intent == "device":
        return _with_lead(_device_answer(facts, view), facts, intent)
    if intent == "rate":
        sentence = str(view.get("rate_sentence") or "").strip()
        if sentence:
            return sentence
        if facts:
            return _total_answer(facts)
        return honest_menu(week)
    if intent == "direction":
        sentence = str(view.get("direction_sentence") or "").strip()
        prefix = f"As of week {week} there is no earlier week to compare. " if week < 2 else ""
        if sentence:
            return (prefix + sentence).strip()
        return honest_menu(week)
    if not facts:
        return honest_menu(week)
    if intent == "total":
        return _with_lead(_total_answer(facts), facts, intent)
    if intent == "categories":
        return _category_answer(facts)
    if intent == "manufacturers":
        return _maker_answer(facts)
    if intent == "wow":
        return _change_answer(facts)
    return honest_menu(week)


def honest_menu(week: int) -> str:
    return (
        f"I can look up, as of week {int(week)}, how many complaints are in the data so far, "
        "which invalid categories rank highest to lowest, who the main manufacturer is, "
        "and the device. Once a second week is in, I can also say what changed. "
        "I can't answer that from this file."
    )


def _total_answer(facts: dict[str, Any]) -> str:
    week = int(facts["week"])
    total = int(facts["total"])
    invalid = int(facts["invalid_total"])
    noun = str(facts.get("noun") or "reports")
    share = format_percent(float(facts.get("invalid_share") or 0.0))
    return (
        f"As of week {week} there are {total} {noun} so far. "
        f"{invalid} of them are an invalid type ({share})."
    )


def _category_answer(facts: dict[str, Any]) -> str:
    week = int(facts["week"])
    rows = list(facts.get("categories") or [])
    if not rows:
        return f"As of week {week}, there are no invalid categories so far."
    listed = "; ".join(
        f"{row['plain']} {int(row['count'])} ({format_percent(float(row['share']))})" for row in rows
    )
    return f"As of week {week}, invalid categories from highest to lowest: {listed}."


def _maker_answer(facts: dict[str, Any]) -> str:
    week = int(facts["week"])
    rows = list(facts.get("manufacturers") or [])
    if not rows:
        return f"This file does not name a manufacturer. The device is {facts.get('device') or 'the device'}."
    listed = ", ".join(
        f"{row['name']} {int(row['count'])} ({format_percent(float(row['share']))})" for row in rows[:3]
    )
    return f"As of week {week}, manufacturers with the most reports so far: {listed}."


def _change_answer(facts: dict[str, Any]) -> str:
    week = int(facts["week"])
    change = facts.get("change")
    if not change:
        return f"As of week {week} there is no earlier week to compare. New data arrives as we go week by week."
    added = int(change["reports_now"]) - int(change["reports_then"])
    return (
        f"As of week {week} there are {int(change['reports_now'])} reports. "
        f"As of week {week - 1} there were {int(change['reports_then'])}. "
        f"That is {added} more. "
        f"Invalid reports went from {int(change['invalid_then'])} to {int(change['invalid_now'])}."
    )


def _device_answer(facts: dict[str, Any], view: dict[str, Any]) -> str:
    device = str(facts.get("device") or "").strip()
    if not device:
        line = str(view.get("device_line") or "")
        device = line.replace("Device:", "").strip(" .") or "the device"
    code = str(facts.get("product_code") or "").strip()
    if code:
        return f"The device is {device}. The product code is {code}."
    return f"The device is {device}."


def _with_lead(text: str, facts: dict[str, Any], intent: str) -> str:
    if intent not in {"total", "device"}:
        return text
    plain = str(facts.get("top_plain") or "").strip()
    if not plain:
        return text
    lead = f"{plain[:1].upper()}{plain[1:]} is the biggest category so far."
    if facts.get("manufacturers"):
        lead += " Want to see who reports it most?"
    return f"{text} {lead}"
