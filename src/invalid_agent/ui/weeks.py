from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from invalid_agent.config import WEEK1_GROQ_FALLBACK, load_settings
from invalid_agent.ui.audit import show_me_fact
from invalid_agent.ui.plain import code_plain
from invalid_agent.ui.week1 import _mentions, _pair_names_its_company, _segments

_CODE = re.compile(r"\binv-[a-z]+\b", re.I)
_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", re.I)
_N_OF_M = re.compile(r"(\d[\d,]*)\s*(?:of|/|out of)\s*(\d[\d,]*)", re.I)
_NOT = re.compile(r"n't|\b(?:not|no|neither)\b|(?<!inv-)\bnor\b", re.I)
_COMPLETE_TIMEOUT = 15.0

_PARETO_RUBRIC = (
    "You answer from the table only. Python already computed every count. "
    "The week goal is met only when the user names, for every flagged company, "
    "the codes that bring that company under 1%. "
    "When the table marks a tie, any one of the tied codes fills that slot. "
    "An extra code, or a company that is not flagged, does not meet the goal. "
    "A question does not meet the goal. Answer it from the table. "
    "Write the reply in your own words, then one JSON object on its own line: "
    '{"meets_goal": false, "reason": "short", "companies": []}. '
    "Do not write YEP, CLOSE, NOT QUITE, GOOD QUESTION, Remember, or Jira. "
    "Do not praise the user. Do not invent a percent or a count."
)
_RESPONSE_RUBRIC = (
    "You answer from the table only. Python already computed every issue. "
    "The week goal is met only when the user covers every company and issue code, "
    "and the branch, the simulated note, and the ticket agree with that row. "
    "A question does not meet the goal. Answer it from the table. "
    "Write the reply in your own words, then one JSON object on its own line: "
    '{"meets_goal": false, "reason": "short", "companies": []}. '
    "Do not write YEP, CLOSE, NOT QUITE, GOOD QUESTION, Remember, or Jira. "
    "Do not praise the user. Do not invent a percent or a count."
)
_CLOSE_RUBRIC = (
    "You answer from the table only. Python already computed every close-out. "
    "The week goal is met only when the user covers every flagged company and "
    "the root cause, the corrective action, and the public statement agree with that row. "
    "A question does not meet the goal. Answer it from the table. "
    "Write the reply in your own words, then one JSON object on its own line: "
    '{"meets_goal": false, "reason": "short", "companies": []}. '
    "Do not write YEP, CLOSE, NOT QUITE, GOOD QUESTION, Remember, or Jira. "
    "Do not praise the user. Do not invent a percent or a count."
)
_CLAIM = re.compile(
    r">\s*1\b|\btoo\b(?!\s+few)|\b(?:under|below|over|above|exceeds?|flagged|also)\b|\b(?:more|greater) than\b",
    re.I,
)
_EXTRA = re.compile(r"\btoo\b(?!\s+few)|\b(?:flagged|also)\b|\bin the set\b", re.I)


@dataclass(frozen=True)
class WeekVerdict:
    text: str
    meets_goal: bool
    reason: str
    companies: tuple[str, ...]


def judge_week(message: str, view: dict[str, Any], client: Any | None, step_id: str) -> WeekVerdict:
    facts = view.get("explore") or {}
    if step_id not in {"pareto", "responses", "closeout"}:
        return _python(message, facts, step_id, "no week")
    if client is None:
        return _python(message, facts, step_id, "no model")
    raw = _complete(client, message, facts, step_id)
    if raw is None:
        fallback = _fallback_client(client)
        if fallback is not None:
            raw = _complete(fallback, message, facts, step_id)
    if not raw:
        return _python(message, facts, step_id, "model down")
    parsed = _parse(raw)
    if parsed is None:
        return _python(message, facts, step_id, "unparsed")
    prose, payload = parsed
    return _guard(message, facts, step_id, prose, payload)


def compact_table(facts: dict[str, Any], step_id: str) -> str:
    if step_id == "pareto":
        return _pareto_table(facts)
    if step_id == "responses":
        return _response_table(facts)
    return _close_table(facts)


def python_sentence(message: str, facts: dict[str, Any], step_id: str) -> str:
    if not str(message or "").strip():
        return "Type a question, or type what you think the screen is saying."
    from invalid_agent.ui.explore import match_intent, threshold_sentence, total_answer

    intent = match_intent(message) if facts else None
    if intent == "total" and "total" in facts:
        return total_answer(facts)
    if intent == "threshold" and facts.get("companies"):
        return threshold_sentence(facts)
    _finding, sentence = show_me_fact({"explore": facts}, step_id)
    return sentence or "The table did not load."


def _pareto_table(facts: dict[str, Any]) -> str:
    lines = ["company | code | count | in the set that gets under 1%"]
    for bundle in facts.get("cause_sets") or []:
        chosen = {str(cause["code"]) for cause in bundle.get("causes") or []}
        tied = {str(code) for code in bundle.get("tied") or []}
        for row in bundle.get("pareto") or []:
            code = str(row["code"])
            mark = "tie" if code in tied else ("yes" if code in chosen else "no")
            lines.append(f"{bundle['name']} | {code} | {int(row['count'])} | {mark}")
        projected = float(bundle.get("projected") or 0) * 100
        lines.append(f"{bundle['name']} projected {projected:.2f}%")
    return "\n".join(lines)


def _response_table(facts: dict[str, Any]) -> str:
    lines = ["company | code | branch | ticket | note"]
    for issue in facts.get("issues") or []:
        lines.append(
            f"{issue['company']} | {issue['code']} | {issue['branch']} | {issue['ticket']} | {issue['testimonial']}"
        )
    return "\n".join(lines)


def _close_table(facts: dict[str, Any]) -> str:
    lines = ["company | causes | share | projected | statement"]
    for row in facts.get("closeouts") or []:
        share = float(row["share"]) * 100
        projected = float(row["projected"]) * 100
        causes = ", ".join(str(code) for code in row.get("causes") or [])
        lines.append(
            f"{row['company']} | {causes} | {share:.2f}% | {projected:.2f}% | {row['statement']}"
        )
    return "\n".join(lines)


def _python(message: str, facts: dict[str, Any], step_id: str, reason: str) -> WeekVerdict:
    return WeekVerdict(python_sentence(message, facts, step_id), False, reason, ())


def _rows(facts: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in facts.get("companies") or [] if str(row.get("name") or "").strip()]


def _runs(message: str, rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    runs: dict[str, list[str]] = {}
    current: str | None = None
    for part in _segments(message):
        names = list(dict.fromkeys(name for _start, _end, name in _mentions(part, rows)))
        if len(names) > 1:
            for name in names:
                runs.setdefault(name, []).append(part)
            current = names[-1]
            continue
        if len(names) == 1:
            current = names[0]
        if current is None:
            continue
        runs.setdefault(current, []).append(part)
    return runs


def _known_codes(facts: dict[str, Any]) -> set[str]:
    found: set[str] = set()
    for bundle in facts.get("cause_sets") or []:
        for row in bundle.get("pareto") or []:
            found.add(str(row["code"]))
        for cause in bundle.get("causes") or []:
            found.add(str(cause["code"]))
        for code in bundle.get("tied") or []:
            found.add(str(code))
    for issue in facts.get("issues") or []:
        found.add(str(issue["code"]))
    for row in facts.get("closeouts") or []:
        for code in row.get("causes") or []:
            found.add(str(code))
    return {code for code in found if code}


def _stamp(message: str, codes: set[str]) -> str:
    pairs: list[tuple[str, str]] = []
    for code in codes:
        plain = code_plain(code).casefold()
        core = re.sub(r"^(?:a|an|the)\s+", "", plain.split("(")[0].strip())
        for phrase in (plain, core):
            if phrase:
                pairs.append((phrase, code))
    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    text = str(message or "")
    for phrase, code in pairs:
        text = re.sub(re.escape(phrase), code, text, flags=re.I)
    return text


def _stands(parts: list[str], name: str, rows: list[dict[str, Any]]) -> bool:
    mentioned = [part for part in parts if any(hit == name for _start, _end, hit in _mentions(part, rows))]
    return any(_NOT.search(part) is None for part in mentioned)


def _claimed_codes(parts: list[str]) -> set[str]:
    found: set[str] = set()
    for part in parts:
        if _NOT.search(part):
            continue
        found.update(code.upper() for code in _CODE.findall(part))
    return found


def _code_gap(
    runs: dict[str, list[str]], groups: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    wrong: list[str] = []
    required: set[str] = set()
    for group in groups:
        name = str(group["name"])
        required.add(name)
        parts = runs.get(name) or []
        claimed = _claimed_codes(parts)
        causes = {str(code).upper() for code in group["causes"]}
        tied = {str(code).upper() for code in group.get("tied") or []}
        if tied:
            ok = bool(claimed & tied) and (causes - tied) <= claimed
        else:
            ok = bool(causes) and causes <= claimed
        if not _stands(parts, name, rows) or not ok:
            missing.append(name)
        if claimed - causes - tied:
            wrong.append(name)
    for name, parts in runs.items():
        if name in required:
            continue
        if _claimed_codes(parts):
            wrong.append(name)
            continue
        for part in parts:
            if not any(hit == name for _start, _end, hit in _mentions(part, rows)):
                continue
            if _NOT.search(part):
                continue
            if _EXTRA.search(part):
                wrong.append(name)
                break
    return missing, wrong


def _pareto_groups(facts: dict[str, Any]) -> list[dict[str, Any]]:
    groups = []
    for bundle in facts.get("cause_sets") or []:
        groups.append(
            {
                "name": bundle["name"],
                "causes": [cause["code"] for cause in bundle.get("causes") or []],
                "tied": list(bundle.get("tied") or []),
            }
        )
    return groups


def _issue_groups(facts: dict[str, Any]) -> list[dict[str, Any]]:
    by_company: dict[str, list[str]] = {}
    for issue in facts.get("issues") or []:
        by_company.setdefault(str(issue["company"]), []).append(str(issue["code"]))
    return [{"name": name, "causes": codes, "tied": []} for name, codes in by_company.items()]


def _company_gap(runs: dict[str, list[str]], required: set[str], rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    wrong: list[str] = []
    for row in rows:
        name = str(row["name"])
        parts = runs.get(name) or []
        if name in required and not _stands(parts, name, rows):
            missing.append(name)
        if name in required:
            continue
        for part in parts:
            if not any(hit == name for _start, _end, hit in _mentions(part, rows)):
                continue
            if _NOT.search(part):
                continue
            if _CLAIM.search(part):
                wrong.append(name)
                break
    return missing, wrong


def _gap_line(step_id: str) -> str:
    if step_id == "pareto":
        return "That doesn't match the cause sets that get each company under 1% yet. Check the charts."
    if step_id == "responses":
        return "That doesn't match the companies and issue codes yet. Check the notes."
    return "That doesn't match the companies in the close-out yet. Check the statements."


def _shares(facts: dict[str, Any]) -> set[str]:
    shares = {"1", "1.0", "1.00"}

    def add(value: Any) -> None:
        if value is None:
            return
        pct = float(value) * 100
        shares.add(f"{pct:.2f}")
        shares.add(f"{pct:.1f}")

    for row in facts.get("companies") or []:
        add(row.get("share"))
    if facts.get("invalid_share") is not None:
        add(facts.get("invalid_share"))
    for bundle in facts.get("cause_sets") or []:
        add(bundle.get("projected"))
    for row in facts.get("closeouts") or []:
        add(row.get("share"))
        add(row.get("projected"))
    return shares


def _pairs(facts: dict[str, Any]) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    if facts.get("total") is not None and facts.get("invalid_total") is not None:
        pairs.add((int(facts["invalid_total"]), int(facts["total"])))
    for row in facts.get("companies") or []:
        pairs.add((int(row["invalid"]), int(row["total"])))
    for bundle in facts.get("cause_sets") or []:
        invalid = int(bundle.get("invalid") or 0)
        total = int(bundle.get("total") or 0)
        for row in list(bundle.get("pareto") or []) + list(bundle.get("causes") or []):
            count = int(row["count"])
            pairs.add((count, invalid))
            pairs.add((count, total))
    return pairs


def _numbers_ok(prose: str, facts: dict[str, Any]) -> bool:
    if any(value not in _shares(facts) for value in _PCT.findall(prose)):
        return False
    rows = _rows(facts)
    pairs = _pairs(facts)
    for match in _N_OF_M.finditer(prose):
        total = int(match.group(2).replace(",", ""))
        pair = (int(match.group(1).replace(",", "")), total)
        if total < 100 and not _pair_names_its_company(prose, match.start(), total, rows):
            continue
        if pair not in pairs:
            return False
    return True


def _guard(
    message: str,
    facts: dict[str, Any],
    step_id: str,
    prose: str,
    payload: dict[str, Any],
) -> WeekVerdict:
    meets = payload.get("meets_goal") is True or str(payload.get("meets_goal")).strip().casefold() == "true"
    reason = str(payload.get("reason") or "").strip()
    if not _numbers_ok(prose, facts):
        return WeekVerdict(python_sentence(message, facts, step_id), False, "invented number", ())
    if not meets:
        return WeekVerdict(prose, False, reason, ())
    rows = _rows(facts)
    stamped = _stamp(message, _known_codes(facts))
    runs = _runs(stamped, rows)
    if step_id == "closeout":
        required = {str(row["company"]) for row in facts.get("closeouts") or []}
        missing, wrong = _company_gap(runs, required, rows)
        ready = bool(required)
    else:
        groups = _pareto_groups(facts) if step_id == "pareto" else _issue_groups(facts)
        missing, wrong = _code_gap(runs, groups, rows)
        ready = bool(groups)
    if not ready or missing or wrong:
        return WeekVerdict(_gap_line(step_id), False, "entity set", ())
    return WeekVerdict(prose, True, reason, tuple(str(row["name"]) for row in rows if str(row["name"]) in runs))


def _user_prompt(message: str, facts: dict[str, Any], step_id: str) -> str:
    return f"Table:\n{compact_table(facts, step_id)}\n\nUser:\n{message}"


def _rubric(step_id: str) -> str:
    return {"pareto": _PARETO_RUBRIC, "responses": _RESPONSE_RUBRIC, "closeout": _CLOSE_RUBRIC}[step_id]


def _effort(client: Any) -> str:
    model = str(getattr(client, "model", "") or "")
    if model.startswith("openai/"):
        return "low"
    return "none"


def _complete(client: Any, message: str, facts: dict[str, Any], step_id: str) -> str | None:
    try:
        text = client.complete(
            system=_rubric(step_id),
            user=_user_prompt(message, facts, step_id),
            temperature=0,
            reasoning_effort=_effort(client),
            timeout=_COMPLETE_TIMEOUT,
        )
    except Exception:
        return None
    return str(text or "")


def _fallback_client(client: Any) -> Any | None:
    model = str(getattr(client, "model", "") or "")
    if model == WEEK1_GROQ_FALLBACK:
        return None
    settings = load_settings()
    if not settings.groq_api_key:
        return None
    from invalid_agent.llm import GroqLLM

    try:
        return GroqLLM(settings.groq_api_key, WEEK1_GROQ_FALLBACK)
    except Exception:
        return None


def _parse(raw: str) -> tuple[str, dict[str, Any]] | None:
    text = re.sub(r"<think>.*?</think>", "", str(raw or ""), flags=re.DOTALL).strip()
    decoder = json.JSONDecoder()
    start = text.rfind("{")
    while start >= 0:
        try:
            payload, _end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            start = text.rfind("{", 0, start)
            continue
        if isinstance(payload, dict) and "meets_goal" in payload:
            prose = re.sub(r"```(?:json)?\s*$", "", text[:start]).strip()
            if not prose:
                prose = str(payload.get("reply") or payload.get("text") or "").strip()
            if not prose:
                return None
            return prose, payload
        start = text.rfind("{", 0, start)
    return None
