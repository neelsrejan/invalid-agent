"""One week of the guided story, computed in Python.

Story weeks are 1, 2, 3, and 4. Week 1 shows the first quarter of the
file's dates, week 4 shows the whole file. The page does not offer a
week switcher. Every number in the returned view comes from that slice.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from invalid_agent.metrics.effectiveness import projection_summary
from invalid_agent.metrics.hypotheses import rank_hypotheses, with_bands
from invalid_agent.metrics.pareto import pareto
from invalid_agent.metrics.rates import overall_rate, stratified_rates
from invalid_agent.metrics.spc import p_chart
from invalid_agent.nodes.planner import build_plan
from invalid_agent.ui.plain import (
    cause_plain,
    code_plain,
    format_percent,
    plain_case_label,
    with_gloss,
)

STORY_WEEKS: tuple[int, ...] = (1, 2, 3, 4)
_BLANK_LEVELS = {"", "UNREPORTED", "NAN", "NONE"}


def slice_through_story_week(frame: pd.DataFrame, story_week: int) -> pd.DataFrame:
    """Rows from the start of the file through the end of story week ``story_week``."""
    week = min(4, max(1, int(story_week)))
    if frame.empty or "date" not in frame.columns:
        out = frame.copy()
        out.attrs = dict(getattr(frame, "attrs", {}) or {})
        return out
    dates = pd.to_datetime(frame["date"], errors="coerce")
    valid = dates.notna()
    if not bool(valid.any()):
        out = frame.copy()
        out.attrs = dict(getattr(frame, "attrs", {}) or {})
        return out
    start = dates[valid].min()
    end = dates[valid].max()
    if start == end or week >= 4:
        out = frame.loc[valid].copy()
    else:
        cutoff = start + (end - start) * (week / 4.0)
        out = frame.loc[valid & (dates <= cutoff)].copy()
        if out.empty:
            out = frame.loc[valid].copy()
    out.attrs = dict(getattr(frame, "attrs", {}) or {})
    return out


def build_week_view(scenario: dict[str, Any], frame: pd.DataFrame, story_week: int) -> dict[str, Any]:
    """Facts, sentences, and tickets for one story week. No model."""
    week = min(4, max(1, int(story_week)))
    sliced = slice_through_story_week(frame, week)
    estimable = _estimable(scenario, sliced)
    framed = with_bands(sliced.copy())
    framed.attrs["spec_estimable"] = estimable
    spec = float(scenario.get("spec_invalid_rate", 0.02))
    promised = float(scenario.get("promised_validity", 0.98))
    overall = overall_rate(framed, spec, promised, spec_estimable=estimable)
    chart = _plain_chart(p_chart(framed))
    rule1_count = sum(1 for hit in chart["violations"] if int(hit["rule"]) == 1)
    direction, early, late = _direction(chart["points"])
    codes = _code_facts(pareto(framed))
    hypotheses = rank_hypotheses(framed, spec)
    top = hypotheses[0] if hypotheses else {}
    single = str(top.get("cause") or "no_single_cause") != "no_single_cause"
    level = _clean_level(top.get("level"), single)
    ratio = top.get("lift")
    if ratio is not None:
        try:
            ratio = float(ratio)
        except (TypeError, ValueError):
            ratio = None
        if ratio is not None and not math.isfinite(ratio):
            ratio = None
    cause_sentence = _cause_sentence(single, level, ratio, cause_plain(str(top.get("cause") or "")))
    summary = projection_summary(framed, top if single else {}, spec, promised, spec_estimable=estimable)
    after_chart = _plain_chart(p_chart(summary["frame"])) if summary["applied"] else None
    projection_sentence = _projection_sentence(
        applied=bool(summary["applied"]),
        before=float(summary["before"]["rate"]),
        after=float(summary["after"]["rate"]),
        level=level,
        estimable=estimable,
    )
    breaks = _breaks(framed, scenario, str(top.get("column") or ""))
    default_break = _default_break(breaks, str(top.get("column") or ""))
    tickets, plan_count = _tickets(scenario, top, level, week)
    rate_label = format_percent(float(overall["rate"]))
    range_label = f"{format_percent(float(overall['ci_low']))} to {format_percent(float(overall['ci_high']))}"
    count_label = f"{int(overall['k'])} of {int(overall['n'])}"
    noun = "share of reports" if not estimable else "invalid rate"
    rate_sentence = f"The {noun} this week is {rate_label} ({count_label})."
    rule1_sentence = f"This chart counts {rule1_count} weeks far above the usual rate."
    direction_sentence = _direction_sentence(direction, early, late, rule1_sentence)
    promise_sentence = (
        "The promise is that at least 98% of tests are valid, so invalid results stay at or below 2%."
    )
    measure_sentence = (
        "This file counts test runs, so we can compare the invalid rate with the 2% cap."
        if estimable
        else (
            "This file counts problem reports, not successful tests. "
            "We cannot measure the 2% cap from it. "
            "The number on screen is the share of reports that are an invalid type."
        )
    )
    decision = _decision(week, level, single)
    unit = int(scenario.get("cost_per_invalid_usd", 85))
    cost = int(overall["k"]) * unit
    arrivals_text = _arrivals(scenario, week)
    complaint = with_gloss(str(scenario.get("complaint") or "").strip())
    device_line = _device_line(scenario)
    case_line = f"Case: {plain_case_label(str(scenario.get('title') or scenario.get('id') or 'case'))}. Week {week}."
    call_label = "Look harder" if (bool(overall["exceeds_spec"]) if estimable else single) else "Hold"
    notes = _notes(
        rate_sentence=rate_sentence,
        cause_sentence=cause_sentence,
        decision=decision,
        cost=cost,
        unit=unit,
        k=int(overall["k"]),
        estimable=estimable,
    )
    view = {
        "story_week": week,
        "estimable": estimable,
        "n": int(overall["n"]),
        "k": int(overall["k"]),
        "rate": float(overall["rate"]),
        "ci_low": float(overall["ci_low"]),
        "ci_high": float(overall["ci_high"]),
        "rate_label": rate_label,
        "range_label": range_label,
        "count_label": count_label,
        "rate_sentence": rate_sentence,
        "call_label": call_label,
        "rule1_count": int(rule1_count),
        "rule1_sentence": rule1_sentence,
        "direction": direction,
        "direction_sentence": direction_sentence,
        "early_label": format_percent(early),
        "late_label": format_percent(late),
        "chart": chart,
        "after_chart": after_chart,
        "projection_applied": bool(summary["applied"]),
        "before_rate": float(summary["before"]["rate"]),
        "after_rate": float(summary["after"]["rate"]),
        "projection_sentence": projection_sentence,
        "pareto": codes["rows"],
        "code_shares": codes["shares"],
        "majority": codes["majority"],
        "majority_codes": codes["majority_codes"],
        "majority_phrase": codes["majority_phrase"],
        "top_code": codes["top_code"],
        "top_plain": codes["top_plain"],
        "single": single,
        "level": level,
        "cause": str(top.get("cause") or "no_single_cause"),
        "ratio": None if ratio is None else round(float(ratio), 2),
        "cause_sentence": cause_sentence,
        "breaks": breaks,
        "default_break": default_break,
        "tickets": tickets,
        "plan_ticket_count": plan_count,
        "promise_sentence": promise_sentence,
        "measure_sentence": measure_sentence,
        "decision": decision,
        "complaint": complaint,
        "arrivals": arrivals_text,
        "device_line": device_line,
        "case_line": case_line,
        "glossary": (
            "MAUDE is the FDA's public database of device problem reports. "
            "OOI means machines that run many nucleic-acid tests at once. "
            "JJE means clinical chemistry analyzers, the machines that measure chemicals in blood."
        ),
        "notes": notes,
        "cost": cost,
        "unit": unit,
        "window_sentence": _window_sentence(week),
    }
    return _jsonify(view)


def beat_lines(view: dict[str, Any], beat_id: str) -> list[str]:
    """The sentences for one part of the week. The page prints these and nothing wordier."""
    week = int(view["story_week"])
    if beat_id == "complaint":
        lines = [
            view["case_line"],
            view["promise_sentence"],
            view["measure_sentence"],
            view["device_line"],
            view["glossary"] if week == 1 else "",
            "### The complaint",
            view["complaint"],
            view["arrivals"] or "Nothing new came in this week. The original complaint still stands.",
            "Next you will see the count for this week.",
        ]
    elif beat_id == "data":
        lines = [
            view["case_line"],
            view["window_sentence"],
            view["rate_sentence"],
            f"The likely range is {view['range_label']}. That is a 95% range. The model did not pick it.",
            f"This week's call is {view['call_label']}.",
            view["direction_sentence"],
            view["measure_sentence"],
        ]
    elif beat_id == "charts":
        lines = [
            view["case_line"],
            view["window_sentence"],
            "The bars rank the biggest invalid types first. The line adds them up.",
            view["rule1_sentence"],
            "The red marks on the chart are those weeks.",
            view["direction_sentence"],
            view["cause_sentence"],
            _unreported_line(view),
        ]
    elif beat_id == "logged":
        lines = [
            view["case_line"],
            "Jira is the ticket list the team already uses. This page reads the plan. It does not create a live ticket.",
            _ticket_lines(view),
            "A confirmed insight from the box below is added as the next ticket and carried into the next week.",
        ]
    elif beat_id == "notes":
        lines = [
            view["case_line"],
            view["cause_sentence"],
            view["decision"],
            "The customer note does not claim we know the cause. The team note names the leading group. The leadership note adds the planning cost.",
        ]
    elif beat_id == "wrap":
        lines = [
            view["case_line"],
            "### What came in",
            view["arrivals"] or "Nothing new came in this week. The original complaint still stands.",
            "### What the counts say",
            view["rate_sentence"],
            view["direction_sentence"],
            view["cause_sentence"],
            "### What we recommend",
            view["decision"],
            view["projection_sentence"],
            (
                "This is the last week. The recommendation above is the pitch. It is written out here."
                if week >= 4
                else "Finish this page to unlock the next week. You cannot skip ahead."
            ),
        ]
    else:
        lines = [view["case_line"]]
    return [line for line in lines if str(line).strip()]


def _estimable(scenario: dict[str, Any], frame: pd.DataFrame) -> bool:
    if scenario.get("denominator") == "reported_events":
        return False
    return bool(frame.attrs.get("spec_estimable", True))


def _plain_chart(chart: dict[str, Any]) -> dict[str, Any]:
    points = []
    for point in chart.get("points") or []:
        points.append(
            {
                "period": str(point.get("period")),
                "n": int(point["n"]),
                "k": int(point["k"]),
                "p": float(point["p"]),
                "lcl": float(point.get("lcl") or 0.0),
                "ucl": float(point.get("ucl") or 0.0),
                "p_bar": float(point.get("p_bar") or chart.get("p_bar") or 0.0),
            }
        )
    violations = []
    for hit in chart.get("violations") or []:
        violations.append(
            {
                "index": int(hit["index"]),
                "rule": int(hit["rule"]),
                "period": str(hit.get("period") or ""),
                "side": str(hit.get("side") or ""),
            }
        )
    return {"p_bar": float(chart.get("p_bar") or 0.0), "points": points, "violations": violations}


def _direction(points: list[dict[str, Any]]) -> tuple[str, float, float]:
    if not points:
        return "flat", 0.0, 0.0
    third = max(1, len(points) // 3)
    early = sum(float(point["p"]) for point in points[:third]) / third
    late = sum(float(point["p"]) for point in points[-third:]) / third
    if late > early * 1.25 and (late - early) >= 0.005:
        return "up", early, late
    if early > late * 1.25 and (early - late) >= 0.005:
        return "down", early, late
    return "flat", early, late


def _direction_sentence(direction: str, early: float, late: float, rule1_sentence: str) -> str:
    early_label = format_percent(early)
    late_label = format_percent(late)
    if direction == "up":
        head = f"The later weeks in this slice are higher ({late_label}) than the early weeks ({early_label})."
    elif direction == "down":
        head = (
            f"The later weeks in this slice are lower ({late_label}) than the early weeks ({early_label}). "
            "The rate is not going up."
        )
    else:
        head = (
            f"The later weeks in this slice ({late_label}) are about the same as the early weeks ({early_label}). "
            "The rate is not steadily going up."
        )
    return f"{head} {rule1_sentence}"


def _code_facts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    plain_rows = []
    shares: dict[str, float] = {}
    for row in rows:
        code = str(row["code"])
        share = float(row["share"])
        shares[code] = share
        plain_rows.append(
            {
                "code": code,
                "plain": code_plain(code),
                "count": int(row["count"]),
                "share": share,
                "cumulative_share": float(row["cumulative_share"]),
            }
        )
    majority_codes: list[str] = []
    running = 0.0
    for row in plain_rows:
        majority_codes.append(row["code"])
        running += row["share"]
        if running >= 0.5:
            break
    phrase = _join_plain([code_plain(code) for code in majority_codes])
    return {
        "rows": plain_rows,
        "shares": shares,
        "majority": bool(majority_codes),
        "majority_codes": majority_codes,
        "majority_phrase": phrase,
        "top_code": plain_rows[0]["code"] if plain_rows else "",
        "top_plain": plain_rows[0]["plain"] if plain_rows else "",
    }


def _join_plain(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _cause_sentence(single: bool, level: str, ratio: float | None, cause: str) -> str:
    if not single:
        return "No single group stands out yet. We will not pretend we know the cause."
    if ratio is None:
        ratio_line = "The other rows had no invalids, so we do not quote how many times higher this group is."
    else:
        ratio_line = f"Its invalid share is about {ratio:.1f} times the share in the other rows."
    return f"The strongest group is {level} ({cause}). {ratio_line}"


def _projection_sentence(*, applied: bool, before: float, after: float, level: str, estimable: bool) -> str:
    noun = "share of reports" if not estimable else "invalid rate"
    if not applied:
        return (
            "No single group stood out enough to remove. "
            "There is no what-if number this week. "
            "We are not hiding a zero. There is nothing to take out."
        )
    before_label = format_percent(before)
    after_label = format_percent(after)
    sentence = (
        f"If we pretend the invalids in {level} never happened, "
        f"the {noun} on this file goes from {before_label} to {after_label}."
    )
    if after <= 0.0:
        sentence += (
            " The what-if is 0% because every invalid in this file sits in that group. "
            "Pretending those rows were fine leaves no invalids. "
            "That is not a real repair. Nobody has rerun the tests."
        )
    elif after < 0.0001:
        sentence += " The what-if is under 0.01%. That is a pretend cleanup of this same file, not a new test."
    else:
        sentence += " This is a pretend cleanup of this same file. It is not a new test, and it is not proof the problem is gone."
    return sentence


def _breaks(frame: pd.DataFrame, scenario: dict[str, Any], hypothesis_column: str) -> dict[str, Any]:
    labels = dict(scenario.get("strata_labels") or {})
    columns = [str(column) for column in (scenario.get("strata_columns") or [])]
    if not columns:
        columns = [column for column in ("reagent_lot", "instrument", "site", "software_version", "manufacturer") if column in frame.columns]
    if hypothesis_column and hypothesis_column not in columns and hypothesis_column in frame.columns:
        columns.append(hypothesis_column)
    found: dict[str, Any] = {}
    for column in columns:
        if column not in frame.columns:
            continue
        shown, hidden_n, hidden_k = _split_blank(stratified_rates(frame, column))
        found[column] = {
            "column": column,
            "label": str(labels.get(column) or column.replace("_", " ")),
            "rows": [
                {
                    "level": str(row["level"]),
                    "n": int(row["n"]),
                    "k": int(row["k"]),
                    "rate_label": format_percent(float(row["rate"])),
                }
                for row in shown
            ],
            "unreported_n": int(hidden_n),
            "unreported_k": int(hidden_k),
        }
    return found


def _split_blank(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    shown = []
    hidden_n = 0
    hidden_k = 0
    for row in rows:
        if str(row.get("level") or "").strip().upper() in _BLANK_LEVELS:
            hidden_n += int(row["n"])
            hidden_k += int(row["k"])
        else:
            shown.append(row)
    return shown, hidden_n, hidden_k


def _default_break(breaks: dict[str, Any], hypothesis_column: str) -> str:
    if hypothesis_column in breaks and breaks[hypothesis_column]["rows"]:
        return hypothesis_column
    best = ""
    best_rows = -1
    for column, payload in breaks.items():
        count = len(payload["rows"])
        if count > best_rows:
            best = column
            best_rows = count
    if best:
        return best
    return next(iter(breaks), "")


def _ticket_lines(view: dict[str, Any]) -> str:
    rows = view.get("tickets") or []
    if not rows:
        return "No plan ticket is in progress this week."
    return " ".join(
        f"{row['key']} — {row['name']} ({row['status']}, {row['owner']})." for row in rows
    )


def _unreported_line(view: dict[str, Any]) -> str:
    breaks = view.get("breaks") or {}
    hidden = sum(int(payload.get("unreported_n") or 0) for payload in breaks.values())
    if hidden <= 0:
        return "Rows with a blank lot or a blank name are left out of the ranking. A blank is not a cause."
    return (
        "Some rows have no lot, brand, or company name. "
        "Those blanks are left out of the table and out of the ranking. "
        "A blank is not a cause."
    )


def _tickets(
    scenario: dict[str, Any],
    top: dict[str, Any],
    level: str,
    story_week: int,
) -> tuple[list[dict[str, str]], int]:
    cleaned = dict(top)
    cleaned["level"] = level
    cleaned["cause"] = str(top.get("cause") or "no_single_cause")
    full = build_plan(scenario, cleaned, week=4)
    current = build_plan(scenario, cleaned, week=story_week)
    keys = {str(task["id"]): f"INV-{index}" for index, task in enumerate(full["tasks"], start=1)}
    shown: list[dict[str, str]] = []
    for task in current["tasks"]:
        slot = 1 if int(task["sim_week"]) <= 1 else int(task["sim_week"])
        if slot > story_week or task["status"] == "To Do":
            continue
        shown.append(
            {
                "key": keys[str(task["id"])],
                "name": _plain_task_name(str(task["name"])),
                "owner": str(task["owner"]),
                "status": str(task["status"]),
            }
        )
    return shown, len(full["tasks"])


def _plain_task_name(name: str) -> str:
    text = name.replace("Retest the next-best stratum", "Check the next-best group again")
    text = text.replace("Retest", "Check again")
    text = text.replace("strata", "groups")
    text = text.replace("stratum", "group")
    text = text.replace("5 Whys on the top branch", "Ask why five times on the top cause")
    text = text.replace("run denominator", "count of tests that were run")
    for key, phrase in (
        ("bad_reagent_lot", "a bad reagent lot"),
        ("drifting_instrument", "an instrument that is drifting"),
        ("site_temperature", "site temperature"),
        ("software_version", "a software version"),
        ("preanalytical_hemolysis", "a sample-quality problem"),
        ("user_process_error", "how people ran the test"),
        ("reported_manufacturer", "the company that made the device"),
        ("reported_brand", "the brand name"),
        ("no_single_cause", "no single cause"),
    ):
        text = text.replace(key, phrase)
    return text


def _decision(week: int, level: str, single: bool) -> str:
    who = level if single else "no single group"
    if week <= 1:
        return f"We opened the case. The leading read is {who}."
    if week == 2:
        return "We kept the leading read. New notes are clues. They do not outvote the counts."
    if week == 3:
        return "We did not switch the cause onto a side note. Any hold stays on the leading group, not the whole product."
    if single:
        return f"We recommend holding {level}. We do not hold every group on this file."
    return "We do not hold one group. No group stood out enough. We keep the case open and ask for a wider look."


def _notes(
    *,
    rate_sentence: str,
    cause_sentence: str,
    decision: str,
    cost: int,
    unit: int,
    k: int,
    estimable: bool,
) -> dict[str, str]:
    share_note = (
        ""
        if estimable
        else " Do not quote this number as a test-run rate. It is a share of problem reports."
    )
    return {
        "customer": (
            f"Hello. {rate_sentence}{share_note} We have not confirmed a cause. {decision} "
            "We are not asking you to stop every test."
        ),
        "internal": (
            f"Team note. {rate_sentence} {cause_sentence} {decision} "
            "A new note from a person does not get its own score. The counts do."
        ),
        "leadership": (
            f"Leadership note. {rate_sentence} {cause_sentence} {decision} "
            f"The planning cost is ${cost} ({k} invalids at ${unit} each). "
            "That dollar figure is a planning assumption, not an invoice."
        ),
    }


_WHO_SPOKE = {
    "customer": "a customer",
    "qa": "quality checks (QA), from the internal team",
    "r&d": "the research team (R&D), from the internal team",
    "manufacturing": "the manufacturing team",
    "management": "management",
}


def _arrivals(scenario: dict[str, Any], story_week: int) -> str:
    weeks = (0, 1) if story_week == 1 else (int(story_week),)
    parts: list[str] = []
    for item in scenario.get("injections") or []:
        try:
            item_week = int(item.get("week", -1))
        except (TypeError, ValueError):
            continue
        if item_week not in weeks:
            continue
        source = str(item.get("source") or "update").strip()
        who = _WHO_SPOKE.get(source.casefold(), source)
        if who not in parts:
            parts.append(who)
    if not parts:
        return ""
    return with_gloss("What came in this week: " + "; ".join(parts) + ".")


def _device_line(scenario: dict[str, Any]) -> str:
    device = str(scenario.get("device") or "the device")
    code = str(scenario.get("product_code") or "").upper()
    if code == "OOI":
        return (
            f"Device: {device}. "
            "OOI means machines that run many nucleic-acid tests at once."
        )
    if code == "JJE":
        return (
            f"Device: {device}. "
            "JJE means clinical chemistry analyzers, the machines that measure chemicals in blood."
        )
    return f"Device: {device}."


def _window_sentence(week: int) -> str:
    if week >= 4:
        return "Week 4 uses the whole date range in the file."
    part = {1: "the first quarter", 2: "the first half", 3: "the first three quarters"}[week]
    return f"Week {week} uses {part} of the date range. Later dates are not in this week's numbers."


def _clean_level(level: Any, single: bool) -> str:
    text = str(level or "").strip()
    if not single or text.lower() in {"", "none", "nan"}:
        return "the leading group"
    return text


def _jsonify(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonify(item) for item in value]
    if isinstance(value, bool) or value is None:
        return value
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            value = value.item()
        except Exception:
            return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return float(value)
    if isinstance(value, int):
        return int(value)
    return value
