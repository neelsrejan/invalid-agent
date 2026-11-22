"""Lookups over the rows visible as of one story week.

Every number comes from that slice. A later week is not counted.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import pandas as pd

from invalid_agent.llm import ToolCaller
from invalid_agent.metrics.pareto import pareto
from invalid_agent.ui.plain import code_plain, format_percent

_BLANK = {"", "UNREPORTED", "NAN", "NONE", "NAT"}
_LOG = logging.getLogger(__name__)


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
    whole: bool = False,
) -> dict[str, Any]:
    """Facts the agent may say for this week. Later rows are not in the counts."""
    from invalid_agent.ui.audit import attach
    from invalid_agent.ui.story import slice_through_story_week

    current = min(4, max(1, int(week)))
    visible = frame if whole else slice_through_story_week(frame, current)
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
        "rows": _slim_rows(visible),
        **attach(visible),
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
    if re.search(r"over 1|above 1|too few|which companies", lowered):
        return "threshold"
    if re.search(r"root cause|fishbone|co-reported|co reported|testimonial", lowered):
        return "issue"
    if re.search(r"\bcapa\b|projected|plan get|plan gets", lowered):
        return "outlook"
    if re.search(r"under 1|below 1", lowered) and re.search(
        r"cause|fix|bring|company|roche|siemens|abbott|beckman", lowered
    ):
        return "causes"
    if re.search(r"biggest invalid|invalid categor", lowered) and re.search(
        r"\bfor\b|roche|siemens|abbott|beckman|ortho|binding", lowered
    ):
        return "causes"
    if re.search(r"\bmanufactur", lowered) or "who report" in lowered:
        return "manufacturers"
    if re.search(r"\bcategor(?:y|ies)\b|\binvalid types?\b|\b(?:highest to lowest|high to low|ranked)\b", lowered):
        return "categories"
    if re.search(r"week over week|last week|previous week|from week", lowered):
        return "wow"
    if re.search(r"how many|how much|number of|count of", lowered) and re.search(
        r"complaint|report|dataset|data set|\brows\b|\bruns?\b|\binvalids?\b", lowered
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
        return capabilities_menu(week)
    if intent == "direction":
        sentence = str(view.get("direction_sentence") or "").strip()
        prefix = f"As of week {week} there is no earlier week to compare. " if week < 2 else ""
        if sentence:
            return (prefix + sentence).strip()
        return capabilities_menu(week)
    if not facts or "total" not in facts:
        return counts_did_not_load()
    if intent == "total":
        return _with_lead(_total_answer(facts), facts, intent)
    if intent == "categories":
        return _category_answer(facts)
    if intent == "manufacturers":
        return _maker_answer(facts)
    if intent == "wow":
        return _change_answer(facts)
    return capabilities_menu(week)


def capabilities_menu(week: int) -> str:
    return (
        f"I can look up, as of week {int(week)}, how many complaints are in the data so far, "
        "which invalid categories rank highest to lowest, who the main manufacturer is, "
        "and the device. Once a second week is in, I can also say what changed."
    )


def counts_did_not_load() -> str:
    return "The week's counts did not load."


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
        if facts.get("rebuilt"):
            return "The week's manufacturer list did not load."
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


def _slim_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    count = len(frame)
    makers = frame["manufacturer"] if "manufacturer" in frame.columns else [""] * count
    flags = frame["invalid"] if "invalid" in frame.columns else [False] * count
    codes = frame["invalid_code"] if "invalid_code" in frame.columns else [""] * count
    rows: list[dict[str, Any]] = []
    for maker, flag, code in zip(list(makers), list(flags), list(codes)):
        rows.append(
            {
                "manufacturer": str(maker or ""),
                "invalid": bool(flag),
                "invalid_code": str(code or ""),
            }
        )
    return rows


def ensure_explore(view: dict[str, Any]) -> dict[str, Any]:
    current = view.get("explore")
    if isinstance(current, dict) and (current.get("category_sentence") or "total" in current):
        return current
    rebuilt = rebuild_explore(view)
    if rebuilt:
        view["explore"] = rebuilt
        return rebuilt
    if isinstance(current, dict):
        return current
    return {}


def rebuild_explore(view: dict[str, Any]) -> dict[str, Any] | None:
    if "n" not in view or "k" not in view:
        return None
    week = int(view.get("story_week") or 1)
    total = int(view["n"])
    invalid = int(view["k"])
    categories: list[dict[str, Any]] = []
    for row in view.get("pareto") or []:
        if not isinstance(row, dict) or not row.get("code"):
            continue
        categories.append(
            {
                "code": str(row["code"]),
                "plain": str(row.get("plain") or code_plain(str(row["code"]))),
                "count": int(row.get("count") or 0),
                "share": float(row.get("share") or 0.0),
            }
        )
    top = categories[0] if categories else {}
    if not top and view.get("top_code"):
        top = {
            "code": str(view.get("top_code") or ""),
            "plain": str(view.get("top_plain") or code_plain(str(view.get("top_code") or ""))),
            "count": int(view.get("k") or 0),
            "share": 1.0 if invalid else 0.0,
        }
        categories = [top]
    device_line = str(view.get("device_line") or "")
    device = device_line.replace("Device:", "").strip(" .") or "the device"
    estimable = bool(view.get("estimable"))
    return {
        "week": week,
        "total": total,
        "invalid_total": invalid,
        "invalid_share": (invalid / total) if total else 0.0,
        "categories": categories,
        "manufacturers": [],
        "top_code": str(top.get("code") or ""),
        "top_plain": str(top.get("plain") or ""),
        "top_count": int(top.get("count") or 0),
        "product_code": "",
        "device": device,
        "estimable": estimable,
        "noun": "runs" if estimable else "complaints",
        "change": None,
        "category_sentence": _category_sentence(week, top, invalid),
        "rows": [],
        "rebuilt": True,
    }


def tool_specs() -> list[dict[str, Any]]:
    empty = {"type": "object", "properties": {}, "additionalProperties": False}
    filtered = {
        "type": "object",
        "properties": {
            "manufacturer": {"type": "string"},
            "category": {"type": "string"},
        },
        "additionalProperties": False,
    }
    return [
        {"name": "report_total", "description": "Count the reports visible as of this week.", "parameters": empty},
        {"name": "invalid_summary", "description": "Count invalid-type reports and their share.", "parameters": empty},
        {"name": "category_ranking", "description": "Rank invalid categories from highest to lowest.", "parameters": empty},
        {"name": "manufacturer_ranking", "description": "Rank manufacturers by report count.", "parameters": empty},
        {"name": "device_info", "description": "Name the device and the product code.", "parameters": empty},
        {"name": "week_change", "description": "Compare this week with the previous week.", "parameters": empty},
        {
            "name": "filtered_count",
            "description": "Count reports for one manufacturer or one invalid category code.",
            "parameters": filtered,
        },
        {"name": "company_shares", "description": "List each company's reports, invalids, and share.", "parameters": empty},
        {"name": "threshold_flags", "description": "List companies over 1% and companies with too few reports.", "parameters": empty},
        {
            "name": "company_causes",
            "description": "Pareto and the smallest cause set that brings one company under 1%.",
            "parameters": {
                "type": "object",
                "properties": {"company": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        {
            "name": "issue_response",
            "description": "Simulated company note, ticket, and likely cause branch for one issue.",
            "parameters": {
                "type": "object",
                "properties": {"company": {"type": "string"}, "category": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        {"name": "capa_outlook", "description": "Projected share after the cause set, against the 1% line.", "parameters": empty},
    ]


def run_tool(name: str, arguments: dict[str, Any] | None, facts: dict[str, Any]) -> dict[str, Any]:
    args = arguments or {}
    if name == "report_total":
        data: dict[str, Any] = {"week": facts["week"], "total": facts["total"], "noun": facts.get("noun")}
    elif name == "invalid_summary":
        data = {
            "week": facts["week"],
            "total": facts["total"],
            "invalid_total": facts["invalid_total"],
            "invalid_share": facts["invalid_share"],
        }
    elif name == "category_ranking":
        data = {
            "week": facts["week"],
            "categories": facts.get("categories") or [],
            "top_code": facts.get("top_code"),
            "top_count": facts.get("top_count"),
            "invalid_total": facts.get("invalid_total"),
        }
    elif name == "manufacturer_ranking":
        data = {"week": facts["week"], "manufacturers": list(facts.get("manufacturers") or [])[:5]}
    elif name == "device_info":
        data = {"device": facts.get("device"), "product_code": facts.get("product_code")}
    elif name == "week_change":
        data = {"week": facts["week"], "change": facts.get("change")}
    elif name == "filtered_count":
        data = _filtered_data(facts, args)
    elif name == "company_shares":
        data = {"companies": facts.get("companies") or []}
    elif name == "threshold_flags":
        data = {"flagged": facts.get("flagged") or [], "small": facts.get("small") or []}
    elif name == "company_causes":
        data = _cause_payload(facts, args)
    elif name == "issue_response":
        data = _issue_payload(facts, args)
    elif name == "capa_outlook":
        data = {"closeouts": facts.get("closeouts") or []}
    else:
        raise KeyError(name)
    return {"name": name, "data": data}


def answer_message(text: str, view: dict[str, Any], client: ToolCaller | None = None) -> str:
    facts = ensure_explore(view)
    if client is not None and facts and "total" in facts:
        try:
            answered = _answer_with_client(text, facts, view, client)
            if answered:
                return answered
        except Exception:
            _LOG.exception("week lookup failed")
    if not facts or "total" not in facts:
        return _answer_without_facts(text, view)
    return _answer_router(text, facts, view)


def _answer_without_facts(text: str, view: dict[str, Any]) -> str:
    intent = match_intent(text)
    if intent == "device":
        return _device_answer({}, view)
    if intent == "rate":
        sentence = str(view.get("rate_sentence") or "").strip()
        if sentence:
            return sentence
    if intent == "direction":
        sentence = str(view.get("direction_sentence") or "").strip()
        if sentence:
            week = int(view.get("story_week") or 1)
            prefix = f"As of week {week} there is no earlier week to compare. " if week < 2 else ""
            return (prefix + sentence).strip()
    if intent in {"total", "categories", "manufacturers", "wow"}:
        return counts_did_not_load()
    week = int(view.get("story_week") or 1)
    return capabilities_menu(week)


def _answer_router(text: str, facts: dict[str, Any], view: dict[str, Any]) -> str:
    chosen = _specific_filter(text, facts)
    if chosen:
        return _sentence_for(run_tool("filtered_count", chosen, facts), facts, view)
    intent = match_intent(text)
    if intent == "threshold":
        return _sentence_for(run_tool("threshold_flags", {}, facts), facts, view)
    if intent == "causes":
        return _sentence_for(run_tool("company_causes", {"company": _named_company(text, facts)}, facts), facts, view)
    if intent == "issue":
        return _sentence_for(run_tool("issue_response", {"company": _named_company(text, facts)}, facts), facts, view)
    if intent == "outlook":
        return _sentence_for(run_tool("capa_outlook", {}, facts), facts, view)
    if not intent:
        return capabilities_menu(int(facts["week"]))
    return answer_for(intent, view)


def _answer_with_client(text: str, facts: dict[str, Any], view: dict[str, Any], client: ToolCaller) -> str:
    calls = client.select_tools(text, tool_specs())
    if not isinstance(calls, list) or not calls:
        return ""
    results: list[dict[str, Any]] = []
    for call in calls:
        if not isinstance(call, dict):
            return ""
        name = str(call.get("name") or "")
        arguments = call.get("arguments") if isinstance(call.get("arguments"), dict) else {}
        try:
            results.append(run_tool(name, arguments, facts))
        except KeyError:
            return ""
    template = " ".join(_sentence_for(result, facts, view) for result in results).strip()
    if not template:
        return capabilities_menu(int(facts["week"]))
    try:
        phrased = str(client.phrase(text, results) or "").strip()
    except Exception:
        return template
    if not phrased or _unknown_number(phrased, results, template) or _unknown_label(phrased, results, template, facts):
        return template
    return phrased


def _specific_filter(text: str, facts: dict[str, Any]) -> dict[str, str] | None:
    lowered = " ".join(str(text or "").casefold().split())
    if not re.search(r"how many|how much|number of|count of", lowered):
        return None
    for row in facts.get("manufacturers") or []:
        name = str(row.get("name") or "")
        if name and name.casefold() in lowered:
            return {"manufacturer": name}
    for row in facts.get("categories") or []:
        code = str(row.get("code") or "")
        if code and code.casefold() in lowered:
            return {"category": code}
    return None


def _filtered_data(facts: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    rows = list(facts.get("rows") or [])
    maker = str(args.get("manufacturer") or "").strip()
    category = str(args.get("category") or "").strip()
    if not rows:
        return {"loaded": False, "week": facts.get("week")}
    matched = rows
    if maker:
        needle = maker.casefold()
        matched = [row for row in matched if needle in str(row.get("manufacturer") or "").casefold()]
    if category:
        needle = category.casefold()
        matched = [row for row in matched if str(row.get("invalid_code") or "").casefold() == needle]
    invalid = sum(1 for row in matched if row.get("invalid"))
    return {
        "loaded": True,
        "week": facts.get("week"),
        "count": len(matched),
        "invalid": invalid,
        "manufacturer": maker,
        "category": category,
    }


def _sentence_for(result: dict[str, Any], facts: dict[str, Any], view: dict[str, Any]) -> str:
    name = str(result.get("name") or "")
    if name in {"report_total", "invalid_summary"}:
        return _with_lead(_total_answer(facts), facts, "total")
    if name == "category_ranking":
        return _category_answer(facts)
    if name == "manufacturer_ranking":
        return _maker_answer(facts)
    if name == "device_info":
        return _device_answer(facts, view)
    if name == "week_change":
        return _change_answer(facts)
    if name == "filtered_count":
        data = result.get("data") or {}
        if not data.get("loaded"):
            return counts_did_not_load()
        who = str(data.get("manufacturer") or data.get("category") or "that filter")
        return (
            f"As of week {int(data.get('week') or facts['week'])}, {who} has {int(data['count'])} reports so far. "
            f"{int(data['invalid'])} of them are an invalid type."
        )
    if name == "company_shares":
        return _company_sentence(facts.get("companies") or [])
    if name == "threshold_flags":
        return _threshold_sentence(facts)
    if name == "company_causes":
        return _cause_sentence(result.get("data") or {})
    if name == "issue_response":
        return _issue_sentence(result.get("data") or {})
    if name == "capa_outlook":
        return _capa_sentence(facts.get("closeouts") or [])
    return ""


def _named_company(text: str, facts: dict[str, Any]) -> str:
    lowered = " ".join(str(text or "").casefold().split())
    for row in facts.get("companies") or []:
        name = str(row.get("name") or "")
        if name and name.casefold() in lowered:
            return name
    return ""


def _cause_payload(facts: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    wanted = short_company(str(args.get("company") or ""), facts)
    bundles = facts.get("cause_sets") or []
    if wanted:
        for bundle in bundles:
            if str(bundle.get("name") or "").casefold() == wanted.casefold():
                return bundle
    return {"name": wanted, "causes": [], "missing": True}


def _issue_payload(facts: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    wanted = short_company(str(args.get("company") or ""), facts).casefold()
    category = str(args.get("category") or "").casefold()
    issues = facts.get("issues") or []
    for issue in issues:
        if wanted and str(issue.get("company") or "").casefold() != wanted:
            continue
        if category and category not in str(issue.get("code") or "").casefold() and category not in str(issue.get("plain") or "").casefold():
            continue
        return issue
    return {"missing": True, "company": wanted}


def short_company(name: str, facts: dict[str, Any]) -> str:
    from invalid_agent.ui.audit import short_name

    if not name:
        return ""
    label = short_name(name)
    for row in facts.get("companies") or []:
        if str(row.get("name") or "").casefold() == label.casefold():
            return str(row["name"])
    return label


def _company_sentence(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "The company table did not load."
    listed = ", ".join(
        f"{row['name']} {int(row['invalid'])} of {int(row['total'])} ({float(row['share']) * 100:.2f}%)"
        for row in rows[:8]
    )
    return f"Invalid share of field problem reports: {listed}."


def _threshold_sentence(facts: dict[str, Any]) -> str:
    flagged = facts.get("flagged") or []
    small = facts.get("small") or []
    if not facts.get("companies"):
        return "The company table did not load."
    over = ", ".join(
        f"{row['name']} {float(row['share']) * 100:.2f}% ({int(row['invalid'])} of {int(row['total'])})"
        for row in flagged
    ) or "none"
    few = ", ".join(f"{row['name']} ({int(row['total'])} reports)" for row in small[:6]) or "none"
    return f"Over 1% with enough reports: {over}. Too few reports to judge: {few}."


def _cause_sentence(data: dict[str, Any]) -> str:
    if data.get("missing") or not data.get("causes"):
        name = data.get("name") or "That company"
        return f"{name} has no cause set on this page."
    causes = ", ".join(f"{cause['code']} ({int(cause['count'])})" for cause in data["causes"])
    projected = float(data.get("projected") or 0.0) * 100
    return (
        f"{data['name']}: the smallest cause set that gets under 1% is {causes}. "
        f"The projected invalid share of field problem reports is {projected:.2f}%."
    )


def _issue_sentence(data: dict[str, Any]) -> str:
    if data.get("missing") or not data.get("testimonial"):
        return "That issue is not on this page."
    others = ", ".join(data.get("co_reported") or []) or "no other label"
    return f"{data['testimonial']} Co-reported labels: {others}. Likely branch: {data['branch']}."


def _capa_sentence(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No close-out is on this page."
    parts = [
        f"{row['company']} moves from {float(row['share']) * 100:.2f}% to {float(row['projected']) * 100:.2f}%"
        for row in rows
    ]
    return "Projected invalid share of field problem reports after the fix: " + "; ".join(parts) + "."


def _unknown_number(phrased: str, results: list[dict[str, Any]], template: str) -> bool:
    allowed = _number_tokens(results) | _number_tokens(template)
    return any(token not in allowed for token in _number_tokens(phrased))


_INV_CODE = re.compile(r"inv-[a-z0-9]+(?:-[a-z0-9]+)*", re.I)


def _unknown_label(
    phrased: str,
    results: list[dict[str, Any]],
    template: str,
    facts: dict[str, Any],
) -> bool:
    """True when the phrasing names a category or manufacturer the tools did not support."""
    allowed_codes = _codes_in(results) | _codes_in(template)
    said_codes = _codes_in(phrased)
    if said_codes - allowed_codes:
        return True
    allowed_makers = _makers_in(results) | _makers_mentioned(template, facts)
    if _makers_mentioned(phrased, facts) - allowed_makers:
        return True
    lowered = phrased.casefold()
    for result in results:
        name = str(result.get("name") or "")
        data = result.get("data") or {}
        if name == "category_ranking":
            top = str(data.get("top_code") or facts.get("top_code") or "")
            if top and not _refers_to(lowered, top, facts):
                return True
        if name == "manufacturer_ranking":
            makers = list(data.get("manufacturers") or facts.get("manufacturers") or [])
            top = str((makers[0] or {}).get("name") or "") if makers else ""
            if top and top.casefold() not in lowered:
                return True
    return False


def _codes_in(value: Any) -> set[str]:
    return {token.casefold() for token in _INV_CODE.findall(_text_of(value))}


def _makers_in(results: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for result in results:
        data = result.get("data") or {}
        for row in data.get("manufacturers") or []:
            name = str(row.get("name") or "").strip()
            if name:
                found.add(name.casefold())
        name = str(data.get("manufacturer") or "").strip()
        if name:
            found.add(name.casefold())
    return found


def _makers_mentioned(text: str, facts: dict[str, Any]) -> set[str]:
    lowered = str(text or "").casefold()
    found: set[str] = set()
    for row in facts.get("manufacturers") or []:
        name = str(row.get("name") or "").strip()
        if name and name.casefold() in lowered:
            found.add(name.casefold())
    return found


def _refers_to(lowered: str, code: str, facts: dict[str, Any]) -> bool:
    token = str(code or "").casefold()
    if token and token in lowered:
        return True
    for row in facts.get("categories") or []:
        if str(row.get("code") or "").casefold() != token:
            continue
        plain = str(row.get("plain") or "").casefold()
        if plain and plain in lowered:
            return True
        core = re.sub(r"^(?:a|an|the)\s+", "", plain.split("(")[0].strip())
        if len(core) > 8 and core in lowered:
            return True
    return False


def _text_of(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_text_of(child) for child in value.values())
    if isinstance(value, list):
        return " ".join(_text_of(child) for child in value)
    return ""


def _number_tokens(value: Any) -> set[str]:
    found: set[str] = set()

    def add(token: str) -> None:
        found.add(token)
        if "." in token:
            found.add(token.rstrip("0").rstrip("."))

    def walk(item: Any) -> None:
        if isinstance(item, bool) or item is None:
            return
        if isinstance(item, int):
            add(str(item))
            return
        if isinstance(item, float):
            add(f"{item:.4f}")
            if 0.0 <= item <= 1.0:
                pct = item * 100.0
                add(f"{pct:.2f}")
                add(f"{pct:.1f}")
                add(f"{pct:.0f}")
            return
        if isinstance(item, str):
            for token in re.findall(r"\d+(?:\.\d+)?", item):
                add(token)
            return
        if isinstance(item, dict):
            for child in item.values():
                walk(child)
            return
        if isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return found
