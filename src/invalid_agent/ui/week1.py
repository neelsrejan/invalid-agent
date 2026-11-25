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
    rows = [row for row in facts.get("companies") or [] if str(row.get("name") or "").strip()]
    for match in _N_OF_M.finditer(prose):
        total = int(match.group(2).replace(",", ""))
        pair = (int(match.group(1).replace(",", "")), total)
        if total < 100 and not _pair_names_its_company(prose, match.start(), total, rows):
            continue
        if pair not in pairs:
            return False
    return True


def _pair_names_its_company(prose: str, index: int, total: int, rows: list[dict[str, Any]]) -> bool:
    start = prose.rfind(".", 0, index)
    start = 0 if start < 0 else start + 1
    end = prose.find(".", index)
    end = len(prose) if end < 0 else end
    owners = [row for row in rows if int(row["total"]) == total]
    return bool(owners and _mentions(prose[start:end], owners))


def _python(message: str, facts: dict[str, Any], reason: str) -> Week1Verdict:
    return Week1Verdict(python_sentence(message, facts), False, reason, ())


def _user_prompt(message: str, facts: dict[str, Any]) -> str:
    return f"Table:\n{compact_table(facts)}\n\nUser:\n{message}"


def _effort(client: Any) -> str:
    model = str(getattr(client, "model", "") or "")
    if model.startswith("openai/"):
        return "low"
    return "none"


_COMPLETE_TIMEOUT = 15.0
_SKIP_TOKEN = frozenset({"the", "labs", "lab", "inc", "ltd", "corp", "corporation", "company"})
_CLAUSE_SPLIT = re.compile(r"[.;!?]|\bbut\b", re.I)
_NEGATED = re.compile(r"\b(?:under|below|not|less than|fine|ok|okay)\b", re.I)
_CLAIMS_OVER = re.compile(r"\b(?:over|above)\s+(?:the\s+)?1\b|\bflagged\b", re.I)


def _complete(client: Any, message: str, facts: dict[str, Any]) -> str | None:
    try:
        text = client.complete(
            system=RUBRIC,
            user=_user_prompt(message, facts),
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


def _aliases(name: str) -> list[str]:
    folded = " ".join(name.casefold().split())
    found = {folded}
    if folded.startswith("the "):
        found.add(folded[4:])
    tokens = [token for token in re.findall(r"[a-z0-9]+", folded) if token not in _SKIP_TOKEN]
    for token in tokens:
        if len(token) >= 4 and short_name(token).casefold() == folded:
            found.add(token)
    words = folded.split()
    for index in range(len(words) - 1):
        phrase = " ".join(words[index : index + 2])
        if short_name(phrase).casefold() == folded:
            found.add(phrase)
    return sorted(found, key=len, reverse=True)


def _bounded(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start else " "
    after = text[end] if end < len(text) else " "
    return not before.isalnum() and not after.isalnum()


def _mentions(message: str, rows: list[dict[str, Any]]) -> list[tuple[int, int, str]]:
    lowered = " ".join(str(message or "").casefold().split())
    patterns: list[tuple[str, str]] = []
    for row in rows:
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        for alias in _aliases(name):
            patterns.append((alias, name))
    patterns.sort(key=lambda item: len(item[0]), reverse=True)
    hits: list[tuple[int, int, str]] = []
    cursor = 0
    while cursor < len(lowered):
        found: tuple[int, int, str] | None = None
        for alias, name in patterns:
            end = cursor + len(alias)
            if lowered.startswith(alias, cursor) and _bounded(lowered, cursor, end):
                found = (cursor, end, name)
                break
        if found is None:
            cursor += 1
            continue
        hits.append(found)
        cursor = found[1]
    return hits


def _clauses(message: str) -> list[str]:
    return [part.strip() for part in _CLAUSE_SPLIT.split(str(message or "")) if part.strip()]


def _claimed_over(name: str, clauses: list[str], row: dict[str, Any]) -> bool:
    owners = [row]
    for clause in clauses:
        if not _mentions(clause, owners):
            continue
        if _NEGATED.search(clause):
            continue
        if _CLAIMS_OVER.search(clause):
            return True
    return False


def _name_gap(message: str, facts: dict[str, Any]) -> tuple[list[str], list[str]]:
    rows = [row for row in facts.get("companies") or [] if str(row.get("name") or "").strip()]
    named = {hit[2] for hit in _mentions(message, rows)}
    missing = [str(row["name"]) for row in facts.get("flagged") or [] if str(row["name"]) not in named]
    clauses = _clauses(message)
    wrong: list[str] = []
    flagged = {str(row["name"]) for row in facts.get("flagged") or []}
    for row in rows:
        name = str(row["name"])
        if name in flagged or name not in named:
            continue
        if _claimed_over(name, clauses, row):
            wrong.append(name)
    return missing, wrong


def _listed(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _name_line(missing: list[str], wrong: list[str]) -> str:
    parts: list[str] = []
    if missing:
        verb = "is" if len(missing) == 1 else "are"
        parts.append(f"{_listed(missing)} {verb} missing from the flagged companies.")
    if wrong:
        verb = "is" if len(wrong) == 1 else "are"
        parts.append(f"{_listed(wrong)} {verb} not a flagged company.")
    return " ".join(parts)


def _guard(
    message: str,
    facts: dict[str, Any],
    prose: str,
    payload: dict[str, Any],
) -> Week1Verdict:
    meets = _as_bool(payload.get("meets_goal"))
    reason = str(payload.get("reason") or "").strip()
    official = [str(row["name"]) for row in facts.get("companies") or []]
    resolved, _mapped = _resolve(_as_names(payload.get("companies")), official)
    names = tuple(dict.fromkeys(resolved))
    if not prose_numbers_match(prose, facts):
        return Week1Verdict(python_sentence(message, facts), False, "invented number", names)
    flagged = [str(row["name"]) for row in facts.get("flagged") or []]
    if not meets:
        return Week1Verdict(prose, False, reason, names)
    if not flagged:
        return Week1Verdict(python_sentence(message, facts), False, "company set", names)
    missing, wrong = _name_gap(message, facts)
    if missing or wrong:
        return Week1Verdict(_name_line(missing, wrong), False, "company set", names)
    return Week1Verdict(prose, True, reason, names)
