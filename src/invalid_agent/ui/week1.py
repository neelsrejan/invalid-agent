from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from invalid_agent.config import WEEK1_GROQ_FALLBACK, load_settings
from invalid_agent.ui.audit import short_name, show_me_fact

_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", re.I)
_N_OF_M = re.compile(r"(\d[\d,]*)\s*(?:of|/|out of)\s*(\d[\d,]*)", re.I)

RUBRIC = (
    "You answer from the table only. Python already computed every count. "
    "The week goal is met only when the user names the companies that are over 1% "
    "invalid and have enough reports, N >= 100. "
    "A company marked too few reports to judge is not flagged. "
    "A question does not meet the goal. Answer it from the table. "
    "Write the reply in your own words, then one JSON object on its own line: "
    '{"meets_goal": false, "reason": "short", "companies": []}. '
    "companies lists the firms the user treated as over the line. "
    "Do not write YEP, CLOSE, NOT QUITE, GOOD QUESTION, Remember, or Jira. "
    "Do not praise the user. Do not invent a percent or a count."
)


@dataclass(frozen=True)
class Week1Verdict:
    text: str
    meets_goal: bool
    reason: str
    companies: tuple[str, ...]


def judge_week1(message: str, view: dict[str, Any], client: Any | None) -> Week1Verdict:
    facts = view.get("explore") or {}
    if client is None:
        return _python(message, facts, "no model")
    raw = _complete(client, message, facts)
    if raw is None:
        fallback = _fallback_client(client)
        if fallback is not None:
            raw = _complete(fallback, message, facts)
    if not raw:
        return _python(message, facts, "model down")
    parsed = _parse(raw)
    if parsed is None:
        return _python(message, facts, "unparsed")
    prose, payload = parsed
    return _guard(message, facts, prose, payload)


def compact_table(facts: dict[str, Any]) -> str:
    lines: list[str] = []
    if facts.get("total") is not None:
        lines.append(f"file reports: {int(facts['total'])}")
    if facts.get("invalid_total") is not None:
        lines.append(f"file invalid: {int(facts['invalid_total'])}")
    lines.append("company | invalid | total | rate | note")
    for row in facts.get("companies") or []:
        rate = f"{float(row['share']) * 100:.2f}%"
        if row.get("over"):
            note = "flagged"
        elif not row.get("enough"):
            note = "too few reports to judge"
        else:
            note = "not flagged"
        lines.append(
            f"{row['name']} | {int(row['invalid'])} | {int(row['total'])} | {rate} | {note}"
        )
    flagged = ", ".join(str(row["name"]) for row in facts.get("flagged") or []) or "none"
    lines.append("flagged: " + flagged)
    return "\n".join(lines)


def python_sentence(message: str, facts: dict[str, Any]) -> str:
    if not str(message or "").strip():
        return "Type a question, or type what you think the screen is saying."
    from invalid_agent.ui.explore import match_intent, threshold_sentence, total_answer

    intent = match_intent(message) if facts else None
    if intent == "total" and "total" in facts:
        return total_answer(facts)
    if intent == "threshold" and facts.get("companies"):
        return threshold_sentence(facts)
    _finding, sentence = show_me_fact({"explore": facts}, "eda")
    return sentence or "The company table did not load."


def prose_numbers_match(prose: str, facts: dict[str, Any]) -> bool:
    shares = {"1", "1.0", "1.00"}
    pairs: set[tuple[int, int]] = set()
    for row in facts.get("companies") or []:
        pct = float(row["share"]) * 100
        shares.add(f"{pct:.2f}")
        shares.add(f"{pct:.1f}")
        pairs.add((int(row["invalid"]), int(row["total"])))
    if facts.get("total") is not None and facts.get("invalid_total") is not None:
        pairs.add((int(facts["invalid_total"]), int(facts["total"])))
        if facts.get("invalid_share") is not None:
            pct = float(facts["invalid_share"]) * 100
            shares.add(f"{pct:.2f}")
            shares.add(f"{pct:.1f}")
    if any(value not in shares for value in _PCT.findall(prose)):
        return False
    for left, right in _N_OF_M.findall(prose):
        pair = (int(left.replace(",", "")), int(right.replace(",", "")))
        if pair not in pairs:
            return False
    return True


def _python(message: str, facts: dict[str, Any], reason: str) -> Week1Verdict:
    return Week1Verdict(python_sentence(message, facts), False, reason, ())


def _user_prompt(message: str, facts: dict[str, Any]) -> str:
    return f"Table:\n{compact_table(facts)}\n\nUser:\n{message}"


def _effort(client: Any) -> str:
    model = str(getattr(client, "model", "") or "")
    if model.startswith("openai/"):
        return "low"
    return "none"


def _complete(client: Any, message: str, facts: dict[str, Any]) -> str | None:
    try:
        text = client.complete(
            system=RUBRIC,
            user=_user_prompt(message, facts),
            temperature=0,
            reasoning_effort=_effort(client),
        )
    except TypeError:
        raise
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
            prose = text[:start].strip()
            prose = re.sub(r"```(?:json)?\s*$", "", prose).strip()
            if not prose:
                prose = str(payload.get("reply") or payload.get("text") or "").strip()
            if not prose:
                return None
            return prose, payload
        start = text.rfind("{", 0, start)
    return None


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().casefold() == "true"
    return False


def _as_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names = []
    for item in value:
        text = str(item or "").strip()
        if text:
            names.append(text)
    return names


def _resolve(names: list[str], official: list[str]) -> tuple[list[str], bool]:
    by_fold = {name.casefold(): name for name in official}
    resolved: list[str] = []
    ok = True
    for raw in names:
        hit = by_fold.get(raw.casefold())
        if hit is None:
            hit = by_fold.get(short_name(raw).casefold())
        if hit is None:
            ok = False
            continue
        resolved.append(hit)
    return resolved, ok


def _guard(
    message: str,
    facts: dict[str, Any],
    prose: str,
    payload: dict[str, Any],
) -> Week1Verdict:
    meets = _as_bool(payload.get("meets_goal"))
    reason = str(payload.get("reason") or "").strip()
    official = [str(row["name"]) for row in facts.get("companies") or []]
    resolved, mapped = _resolve(_as_names(payload.get("companies")), official)
    flagged = {str(row["name"]) for row in facts.get("flagged") or []}
    if not prose_numbers_match(prose, facts):
        return Week1Verdict(python_sentence(message, facts), False, "invented number", tuple(resolved))
    if meets and (not mapped or set(resolved) != flagged or not flagged):
        meets = False
    return Week1Verdict(prose, meets, reason, tuple(dict.fromkeys(resolved)))
