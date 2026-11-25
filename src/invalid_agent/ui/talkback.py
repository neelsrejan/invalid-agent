"""Talk-back agent for one week and one part of the story."""

from __future__ import annotations

import re
from typing import Any

from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.llm import ToolCaller
from invalid_agent.ui.plain import code_plain, unexplained_jargon

# Legacy synthetic walk. The JJE pages use AUDIT_WEEKS instead of these six parts.
_STEP_ORDER = ("complaint", "data", "charts", "logged", "notes", "wrap", "done")
LOOKUP_PARTS = frozenset({"complaint", "data"})
AUDIT_WEEKS = frozenset({"eda", "pareto", "responses", "closeout"})
_PART_NAME = {
    "data": "numbers",
    "charts": "charts",
    "logged": "logged",
    "notes": "notes",
}

_QUESTION_START = (
    "why ",
    "what ",
    "how ",
    "which ",
    "when ",
    "where ",
    "who ",
    "do ",
    "does ",
    "did ",
    "is ",
    "are ",
    "can ",
    "could ",
    "would ",
    "should ",
)
_MOST = ("majority", "most of", "make up most", "makes up most", "almost all")
_UP = ("going up", "is rising", "is climbing", "rate is up", "keeps climbing", "increasing")
_DOWN = ("going down", "falling", "dropping", "decreasing")
# Ticket keys are digits (INV-13, Your ticket 1). Invalid types are letters.
_CODE = re.compile(r"\bINV-[A-Z]+\b", re.I)
_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_TICKET_ID = re.compile(r"Your ticket \d+|Flag \d+")
# A parenthetical code, "(INV-NOR)", is one step. A plain word gap stops at the parenthesis.
_GAP = r"(?:[\w'-]+|\([^)]{0,60}\))"
_NEGATION = re.compile(
    rf"(?:\bnot\b|\bnever\b|\bcannot\b|\bcan not\b|n't)"
    rf"(?:\s+{_GAP}){{0,16}}\s+"
    rf"(?:make up|makes up|majority|most|biggest|main)\b"
    rf"|"
    rf"(?:\bnot\b|\bnever\b|\bcannot\b|\bcan not\b|n't)"
    rf"(?:\s+{_GAP}){{0,8}}\s+"
    rf"(?:going up|rising|climbing|increasing|rate is up|going down|falling|dropping|decreasing)\b"
    rf"|"
    rf"(?:\bbiggest\b|\bmost\b|\bmajority\b|\bmain\b)"
    rf"(?:\s+{_GAP}){{0,6}}\s+"
    rf"(?:\bnot\b|\bnever\b|\bcannot\b|n't)\b",
    re.I,
)
# Code names that contain a negation word. Mask them before the negation check.
_NEGATED_NAMES = (
    "not enough sample",
    "no usable result",
    "unable to obtain",
    "used it the wrong way",
    "used the wrong way",
)
_DOUBT = re.compile(
    r"\b(?:neither|(?<!inv-)nor|i doubt|we doubt|doubtful|i disagree|untrue)\b"
    r"|\b(?:i|we)\s+(?:do not|don't|dont)\s+(?:believe|think|agree)\b"
    r"|\bnot true\b"
    r"|\b(?:it'?s|it is|that'?s|that is|is)\s+(?:false|wrong)\b"
    r"|\b(?:false|wrong) that\b|\bhardly\s+(?:the|any|most|main|biggest|majority)\b"
    r"|isn'?t even close|\bno way\b|\bfar from\b|\bunlikely\b|\bskeptical\b|\bquestion whether\b|\bnope\b|\bnah\b"
    r"|\bor not\b|\bi think not\b|\bnot!",
    re.I,
)
_OPENING = ("YEP, YOU GOT IT!", "NOT YET", "NOT QUITE.", "CLOSE!", "GOOD QUESTION.")
_BANNED = (
    "fidelity",
    "traceback",
    "/home",
    "/opt",
    "/agent",
    "api_key",
    "groq_api",
    "model draft",
    "deterministic",
)
_LEADS = ("YEP, YOU GOT IT", "NOT YET", "NOT QUITE", "CLOSE!", "GOOD QUESTION")


_EXCLUSION = re.compile(r"\b(?:not|nor)\s+(inv-[a-z]+)\b", re.I)


def _masked(lowered: str) -> str:
    masked = lowered
    for name in _NEGATED_NAMES:
        masked = masked.replace(name, "codename")
    # "not INV-SW" leaves a code out only when the sentence still names another code.
    # "is not INV-NOR" by itself is a denial, so the "not" has to stay.
    named = {code.upper() for code in _CODE.findall(lowered)}
    excluded = {code.upper() for code in _EXCLUSION.findall(lowered)}
    if excluded and named - excluded:
        masked = _EXCLUSION.sub("exclusion", masked)
    return masked


def _doubts(lowered: str) -> bool:
    return bool(_DOUBT.search(_masked(lowered)))


def _hard_negation(lowered: str) -> bool:
    return bool(_NEGATION.search(_masked(lowered)))


def _negated(lowered: str) -> bool:
    return _hard_negation(lowered) or _doubts(lowered)


def _sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


_FRAGMENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("INV-NOR", ("inv-nor", "no usable result", "unable to obtain")),
    ("INV-MECH", ("inv-mech", "mechanical")),
    ("INV-SW", ("inv-sw", "software abort")),
    ("INV-CAL", ("inv-cal", "calibration")),
    ("INV-USR", ("inv-usr", "used it the wrong way")),
    ("INV-IC", ("inv-ic", "internal-control", "internal control")),
    ("INV-EXT", ("inv-ext", "extraction")),
    ("INV-INH", ("inv-inh", "blocked reaction")),
    ("INV-HEM", ("inv-hem", "sample-quality")),
    ("INV-VOL", ("inv-vol", "not enough sample")),
    ("INV-TMP", ("inv-tmp", "temperature flag")),
)


def example_prompts(view: dict[str, Any], step_id: str) -> list[str]:
    """Three short prompts. A code-share claim is not offered before the charts part."""
    if step_id in AUDIT_WEEKS:
        from invalid_agent.ui.audit import prompts_for

        return prompts_for(step_id, view.get("explore") or {})
    if step_id in LOOKUP_PARTS:
        prompts = [
            "How many complaints are in the dataset?",
            "Which invalid categories are highest to lowest?",
        ]
        if (view.get("explore") or {}).get("manufacturers"):
            prompts.append("Who is the main manufacturer from this week's reports?")
        elif step_id == "data":
            prompts.append("What is the invalid rate this week?")
        week = int(view.get("story_week") or (view.get("explore") or {}).get("week") or 1)
        if step_id == "data" and str(view.get("direction") or "") == "up" and week > 1:
            prompts.append("Why is the invalid rate going up?")
        unique: list[str] = []
        for prompt in prompts:
            if prompt not in unique:
                unique.append(prompt)
        return unique[:3]
    prompts: list[str] = []
    if _seen(step_id, "charts"):
        if view.get("majority") and view.get("majority_phrase"):
            verb = "makes up most of the invalids" if len(view.get("majority_codes") or []) == 1 else "make up most of the invalids"
            prompts.append(f"It looks like {view['majority_phrase']} {verb}")
        elif view.get("top_plain"):
            prompts.append(f"The biggest invalid type is {view['top_plain']}")
    prompts.append("Why is the invalid rate going up?")
    extra = {
        "complaint": "What was promised, and can this file measure it?" if not view.get("fda") else "What is MAUDE?",
        "data": "What is the invalid rate this week?",
        "charts": "Is there one group we should hold?",
        "logged": "Which tickets are open this week?",
        "notes": "What should the customer be told?",
        "wrap": "What do we recommend this week?",
        "done": "What should we remember from this story?",
    }.get(step_id, "What should we remember from this screen?")
    if step_id == "complaint":
        prompts.append("Who made the device?")
    prompts.append(extra)
    unique: list[str] = []
    for prompt in prompts:
        if prompt not in unique:
            unique.append(prompt)
    return unique[:3]


def respond(
    message: str,
    view: dict[str, Any],
    step_id: str,
    *,
    ticket_key: str,
    flag_key: str,
    tool_client: ToolCaller | None = None,
) -> dict[str, Any]:
    raw = str(message or "")
    text = " ".join(raw.split())
    if not text:
        if step_id == "eda":
            return _respond_eda(raw, text, view, None, ticket_key, flag_key)
        return _pack(
            kind="question",
            body="Type a question, or type what you think the screen is saying. Then I can check it against this week's counts.",
            finding="",
            ticket_key=ticket_key,
            flag_key=flag_key,
            user_text="",
        )
    if step_id == "eda":
        return _respond_eda(raw, text, view, tool_client, ticket_key, flag_key)
    kind, body, finding = _classify(text, view, step_id, tool_client)
    bare = step_id in LOOKUP_PARTS | AUDIT_WEEKS and kind in {"question", "hint", "early"}
    return _pack(
        kind=kind,
        body=body,
        finding=finding,
        ticket_key=ticket_key,
        flag_key=flag_key,
        user_text=raw.strip(),
        bare=bare,
    )


def _respond_eda(
    raw: str,
    text: str,
    view: dict[str, Any],
    client: Any | None,
    _ticket_key: str,
    _flag_key: str,
) -> dict[str, Any]:
    from invalid_agent.ui.audit import show_me_fact
    from invalid_agent.ui.week1 import judge_week1

    verdict = judge_week1(text, view, client)
    finding, _sentence = show_me_fact(view, "eda")
    confirmed = bool(verdict.meets_goal)
    return {
        "kind": "correct" if confirmed else "question",
        "confirmed": confirmed,
        "text": verdict.text,
        "bullet": verdict.text if confirmed else None,
        "signature": finding if confirmed else "",
        "log_kind": "insight" if confirmed else "",
        "log_key": "Insight" if confirmed else "",
        "log_text": verdict.text if confirmed else "",
        "user_text": raw.strip(),
    }


def reword_reply(base_text: str, llm: Any | None) -> str:
    """Let a model rephrase ``base_text``. Any failure returns ``base_text`` unchanged."""
    if llm is None or getattr(llm, "name", "deterministic") == "deterministic":
        return base_text
    try:
        draft = llm.complete(
            system=(
                "You rewrite one reply for a high school reader. "
                "Keep the opening verdict (YEP, NOT YET, NOT QUITE, CLOSE, or GOOD QUESTION). "
                "Keep every number. Keep the ticket or flag id if there is one. "
                "Do not add numbers, file paths, or unexplained jargon. "
                "Short sentences. Encouraging. Return only the reply."
            ),
            user=base_text,
            temperature=0.1,
        )
    except Exception:
        return base_text
    if _draft_ok(str(draft or ""), base_text):
        return str(draft).strip()
    return base_text


def _draft_ok(draft: str, base: str) -> bool:
    cleaned = draft.strip()
    if len(cleaned) < 20 or len(cleaned) > 1500:
        return False
    lowered = cleaned.casefold()
    base_lower = base.casefold()
    if any(token in lowered for token in _BANNED):
        return False
    opening = _opening(base)
    if opening and not cleaned.startswith(opening):
        return False
    for lead in _LEADS:
        if lead.casefold() in base_lower and lead.casefold() not in lowered:
            return False
    if _NUMBER.findall(base) != _NUMBER.findall(cleaned):
        return False
    if _negated(base_lower) != _negated(lowered):
        return False
    for token in _TICKET_ID.findall(base):
        if re.search(rf"(?<!\d){re.escape(token)}(?!\d)", cleaned, re.I) is None:
            return False
    if unexplained_jargon(cleaned):
        return False
    if opening in {"NOT QUITE.", "CLOSE!"} and any(
        phrase in lowered for phrase in ("great job", "nailed it", "you got it", "perfect", "excellent", "well done", "awesome", "nice work")
    ):
        return False
    numbers = []
    for raw in _NUMBER.findall(base):
        try:
            numbers.append(float(raw))
        except ValueError:
            continue
    facts = {"numbers": numbers, "ids": _TICKET_ID.findall(base)}
    checked = check_narrative(cleaned, facts)
    return bool(checked.ok)


def _pack(
    *,
    kind: str,
    body: str,
    finding: str,
    ticket_key: str,
    flag_key: str,
    user_text: str,
    bare: bool = False,
) -> dict[str, Any]:
    confirmed = kind == "correct"
    logs_flag = kind in {"partial", "unsupported"}
    key = ticket_key if confirmed else (flag_key if logs_flag else "")
    remember = _remember(kind)
    if kind in {"early", "hint"}:
        lead = ""
        log_line = ""
    elif kind == "correction":
        lead = "NOT QUITE."
        log_line = ""
    else:
        lead = {
            "correct": "YEP, YOU GOT IT!",
            "partial": "CLOSE! YOU ARE ON THE RIGHT TRACK.",
            "unsupported": "NOT QUITE. THE FILE DOES NOT SAY THAT.",
            "question": "GOOD QUESTION.",
        }[kind]
        if confirmed:
            log_line = (
                f"We'll log that as {key} to track it and keep it in mind for the root cause. "
                "On a real team this would go in Jira."
            )
        elif logs_flag:
            log_line = f"We'll log that as {key} so we do not lose it. It is not a confirmed finding."
        else:
            log_line = ""
    bullet = None
    if confirmed:
        bullet = f"We found {finding} -> logged as {key} to resolve going forward. On a real team this would go in Jira."
    if bare:
        reply = body
    else:
        parts = [lead, body, log_line, f"Remember: {remember}"]
        reply = " ".join(part for part in parts if part)
    if confirmed:
        log_kind = "ticket"
    elif logs_flag:
        log_kind = "flag"
    else:
        log_kind = ""
    return {
        "kind": kind,
        "confirmed": confirmed,
        "text": reply,
        "bullet": bullet,
        "signature": finding,
        "log_kind": log_kind,
        "log_key": key,
        "log_text": bullet or (f"{key}: {finding}" if logs_flag else ""),
        "user_text": user_text,
    }


def _seen(step_id: str, first_step: str) -> bool:
    order = _STEP_ORDER
    here = order.index(step_id) if step_id in order else len(order) - 1
    return here >= order.index(first_step)


def _early(first_step: str) -> tuple[str, str, str]:
    part = _PART_NAME.get(first_step, first_step)
    body = f"NOT YET — you'll see that on the {part} part."
    return "early", body, f"an idea to check on the {part} part"


_ASK = re.compile(
    r"\?|\b(?:name|show|tell|list|give|what|how|which|who|whos|why|when|where)\b|\bcan you\b"
)


def _asks_for_facts(lowered: str) -> bool:
    from invalid_agent.ui.explore import match_intent

    later = any(word in lowered for word in ("ticket", "jira", "logged", "recommend"))
    intent = match_intent(lowered)
    if later and intent is None:
        return False
    if _ASK.search(lowered):
        return True
    return intent in {"total", "categories", "manufacturers", "device", "wow"}


def _classify(
    text: str,
    view: dict[str, Any],
    step_id: str,
    tool_client: ToolCaller | None = None,
) -> tuple[str, str, str]:
    lowered = text.casefold()
    if _is_greeting(lowered):
        return "hint", _hello(step_id, view), ""
    if step_id in AUDIT_WEEKS:
        from invalid_agent.ui.audit import goal_statement
        from invalid_agent.ui.explore import answer_message

        stated = goal_statement(text, view, step_id)
        if stated:
            return stated
        return (
            "question",
            answer_message(text, view, tool_client),
            f"a question on the {step_id} page",
        )
    if step_id in LOOKUP_PARTS:
        from invalid_agent.ui.explore import answer_message, match_intent

        stated = _key_statement(lowered, view, step_id)
        if stated:
            return stated
        if _asks_for_facts(lowered):
            glossary = _glossary_answer(lowered)
            if glossary and match_intent(lowered) is None:
                return "question", glossary, _question_finding(lowered, view, step_id)
            return (
                "question",
                answer_message(text, view, tool_client),
                f"a question on the {step_id} screen",
            )
    if step_id == "complaint" and not _is_question(lowered) and not _negated(lowered):
        stated = _key_statement(lowered, view, step_id)
        if stated:
            return stated
        if _category_attempt(lowered):
            sentence = str((view.get("explore") or {}).get("category_sentence") or "")
            if sentence:
                return "hint", sentence, ""
    codes = _mentioned_codes(lowered)
    claims_codes = bool(codes) and (_says_most(lowered) or "biggest" in lowered or "main invalid" in lowered)
    question = _is_question(lowered)
    blocked = question or _negated(lowered)
    if claims_codes and not _seen(step_id, "charts"):
        return _early("charts")
    if claims_codes and question:
        return "question", _answer_question(lowered, view, step_id), "a question about the invalid types"
    if claims_codes and _doubts(lowered):
        return _doubt_reply(lowered, codes, view)
    if claims_codes and _hard_negation(lowered):
        return _negated_code_claim(lowered, codes, view)
    if claims_codes:
        return _code_claim(lowered, codes, view)
    claims_up = _asserts_up(lowered) and not blocked
    claims_down = _asserts_down(lowered) and not claims_up and not blocked
    if (claims_up or claims_down) and not _seen(step_id, "data"):
        return _early("data")
    if claims_up or claims_down:
        return _direction_claim(view, claimed="down" if claims_down else "up")
    body = _answer_question(lowered, view, step_id)
    if question:
        return "question", body, _question_finding(lowered, view, step_id)
    if _doubts(lowered) and (_asserts_up(lowered) or _asserts_down(lowered)) and _seen(step_id, "data"):
        return "hint", str(view.get("direction_sentence") or body), ""
    if _doubts(lowered) and _seen(step_id, "charts"):
        return _doubt_reply(lowered, codes, view)
    stated = _key_statement(lowered, view, step_id)
    if stated:
        return stated
    return "hint", body, ""


def _code_claim(lowered: str, codes: list[str], view: dict[str, Any]) -> tuple[str, str, str]:
    shares: dict[str, float] = {str(key): float(value) for key, value in (view.get("code_shares") or {}).items()}
    majority = [str(code) for code in (view.get("majority_codes") or [])]
    named_share = sum(shares.get(code, 0.0) for code in codes)
    phrase = str(view.get("majority_phrase") or view.get("top_plain") or "the top invalid types")
    if not shares:
        body = "This week's slice has no invalids, so no type makes up most of them."
        return "unsupported", body, "no invalids in this slice"
    says_most = _says_most(lowered)
    found = set(codes)
    covers = bool(majority) and set(majority) <= found
    extra = found - set(majority)
    shown = _sentence_case(phrase)
    if says_most and covers and not extra and named_share >= 0.5:
        verb = "makes up" if len(majority) == 1 else "make up"
        body = f"{shown} really {verb} most of the invalids this week."
        return "correct", body, f"{shown} {verb} most of the invalids"
    top_code = str(view.get("top_code") or "")
    if ("biggest" in lowered or "main invalid" in lowered) and codes == [top_code]:
        top = str(view.get("top_plain") or codes[0])
        body = f"The biggest invalid type this week is {top}."
        return "correct", body, f"the biggest invalid type is {top}"
    if (says_most and found & set(majority)) or (top_code in found):
        body = (
            f"You named a real slice. It is not the whole story. "
            f"The slices that make up most of the invalids are {phrase}."
        )
        return "partial", body, f"part of the top slices, not the full set ({phrase})"
    named = _join([code_plain(code) for code in codes]) or "those types"
    body = f"Those types are not most of the invalids. The slices that make up most of them are {phrase}."
    return "unsupported", body, f"a claim the counts do not support about {named}"


def _majority_line(view: dict[str, Any]) -> tuple[str, str]:
    phrase = _sentence_case(str(view.get("majority_phrase") or view.get("top_plain") or "the top invalid types"))
    count = len(view.get("majority_codes") or [])
    verb = "makes up" if count == 1 else "make up"
    finding = f"{phrase} {verb} most of the invalids"
    body = f"{phrase} really {verb} most of the invalids this week."
    return finding, body


def _doubt_reply(lowered: str, codes: list[str], view: dict[str, Any]) -> tuple[str, str, str]:
    """Doubt never logs. Agree when the doubted set is not the majority; correct it when it is."""
    phrase = _sentence_case(str(view.get("majority_phrase") or view.get("top_plain") or "the top invalid types"))
    count = len(view.get("majority_codes") or [])
    verb = "makes up" if count == 1 else "make up"
    fact = f"{phrase} {verb} most of the invalids this week."
    if codes:
        kind, _body, _finding = _code_claim(lowered, codes, view)
        shares = {str(key): float(value) for key, value in (view.get("code_shares") or {}).items()}
        if kind != "correct" and sum(shares.get(code, 0.0) for code in codes) < 0.5:
            return "hint", f"The counts agree with your doubt. {fact}", ""
    return "correction", f"The counts do not support that. {fact}", "a doubted claim"


def _negated_code_claim(lowered: str, codes: list[str], view: dict[str, Any]) -> tuple[str, str, str]:
    """A statement that denies a claim. Grade it against the counts. Do not call it a question."""
    kind, body, finding = _code_claim(lowered, codes, view)
    shares = {str(key): float(value) for key, value in (view.get("code_shares") or {}).items()}
    named_share = sum(shares.get(code, 0.0) for code in codes)
    # Denying a set the counts already support is a correction, not a new ticket.
    if kind == "correct" or named_share >= 0.5:
        if kind != "correct":
            finding, body = _majority_line(view)
        return "correction", body, finding
    if "biggest" in lowered or "main invalid" in lowered:
        top = str(view.get("top_plain") or "")
        fact = f"The biggest invalid type this week is {top}."
        return "hint", f"The counts agree. {fact}", ""
    finding, fact = _majority_line(view)
    return "hint", f"The counts agree. {fact}", ""


def part_fact(view: dict[str, Any], beat_id: str) -> tuple[str, str]:
    """The key insight for one part: a signature and the sentence that states it."""
    if beat_id in AUDIT_WEEKS:
        from invalid_agent.ui.audit import show_me_fact

        return show_me_fact(view, beat_id)
    if beat_id == "charts":
        if not (view.get("code_shares") or view.get("majority_codes")):
            return (
                "no invalids in this slice",
                "This week's slice has no invalids, so there is no ranking to draw.",
            )
        return _majority_line(view)
    if beat_id == "data":
        return "the invalid rate this week", str(view.get("rate_sentence") or "")
    if beat_id == "complaint":
        from invalid_agent.ui.explore import ensure_explore

        sentence = str(ensure_explore(view).get("category_sentence") or "")
        if not sentence:
            sentence = "The week's counts did not load."
        return "the biggest invalid category so far", sentence
    if beat_id == "logged":
        count = _shown_ticket_count(view)
        sentence = (
            f"This week the plan has {count} follow-up item{'s' if count != 1 else ''}."
            if count
            else "This week the plan has no follow-up items yet."
        )
        return "which tickets are open", sentence
    if beat_id == "notes":
        notes = view.get("notes") or {}
        sentence = str(notes.get("customer") or view.get("decision") or "Tell the customer only what the file supports.")
        return "what the customer should be told", sentence
    sentence = str(view.get("decision") or "Read the recommendation on this wrap-up.")
    return "what we recommend this week", sentence


def _shown_ticket_count(view: dict[str, Any]) -> int:
    """The tickets on this week's table, not the whole four-week plan."""
    tickets = view.get("tickets")
    if isinstance(tickets, list):
        return len(tickets)
    return int(view.get("plan_ticket_count") or 0)


def part_signature(view: dict[str, Any], beat_id: str) -> str:
    return part_fact(view, beat_id)[0]


def accepted_signatures(view: dict[str, Any], beat_id: str) -> set[str]:
    """Findings that count as this part's point, so a typed YEP can unlock Next."""
    found = {part_signature(view, beat_id)}
    if beat_id == "charts":
        top = str(view.get("top_plain") or "")
        if top:
            found.add(f"the biggest invalid type is {top}")
    if beat_id == "data":
        found.update(
            {
                "the invalid rate is higher in the later weeks of this slice",
                "the invalid rate is lower in the later weeks of this slice",
            }
        )
    return found


_WORD_NUMBERS = {
    "no": 0, "none": 0, "zero": 0, "nothing": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_STOP = frozenset(
    "a an the is are was were be been of to in on at for and or we you i it this that these those with "
    "as by from have has had will would should can could do does did our your my so if then than "
    "tell told tells recommend recommends say says note notes customer".split()
)
_NO_WORD = re.compile(r"\b(?:no|not|none|never|nothing|cannot)\b|n't", re.I)


def _count_statement(lowered: str, count: int) -> bool:
    """True when the message gives this week's follow-up count, and nothing else."""
    numbers = {int(n) for n in re.findall(r"(?<![\d.])\d+(?![\d.%])", lowered)}
    numbers |= {value for word, value in _WORD_NUMBERS.items() if re.search(rf"\b{word}\b", lowered)}
    return numbers == {count}


def _norm_words(text: str) -> str:
    return re.sub(r"[^a-z0-9%]+", " ", text.casefold()).strip()


_TELL = re.compile(
    r"^(?:tell|told)\s+(?:the\s+)?customer\s+(?:that\s+)?"
    r"|^(?:the customer (?:was |should be )?told)\s+",
    re.I,
)


def _quotes_fact(lowered: str, body: str) -> bool:
    """The reader pasted one or more sentences that are already on the screen.

    Every substantial sentence in the message must equal a sentence of the
    facts. A correct sentence next to a changed one is not a quote.
    """
    body_pieces = [
        piece
        for sentence in re.split(r"(?<=[.!?])\s+", body)
        if len((piece := _norm_words(sentence)).split()) >= 4
    ]
    if not body_pieces:
        return False
    matched = False
    for raw in re.split(r"(?<=[.!?])\s+", lowered) or [lowered]:
        piece = _norm_words(_TELL.sub("", raw, count=1) if raw.strip() else raw)
        if len(piece.split()) < 4:
            continue
        if piece in body_pieces:
            matched = True
        else:
            return False
    return matched


_TOKEN = re.compile(r"[a-z0-9][a-z0-9%'-]*(?:\.\d+%?)?")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text)


def _negated_stems(tokens: list[str]) -> set[str]:
    """The first content word after each no/not, so "not hold" differs from "hold ... not L-4419"."""
    found: set[str] = set()
    for i, tok in enumerate(tokens):
        if _NO_WORD.fullmatch(tok) or tok.endswith("n't"):
            for nxt in tokens[i + 1:]:
                if nxt not in _STOP and not _NO_WORD.fullmatch(nxt):
                    found.add(nxt[:4])
                    break
    return found


def _same_sentence(lowered: str, body: str) -> bool:
    """The message restates one sentence of the facts.

    Most of its words must be in that sentence, every number or code it gives
    must be in that sentence as written, and each "not" must deny the same word.
    """
    typed = _tokens(lowered)
    words = [w[:4] for w in typed if w not in _STOP and len(w) > 2]
    exact = {w for w in typed if any(ch.isdigit() for ch in w)}
    if len(words) < 2:
        return False
    for sentence in re.split(r"(?<=[.!?])\s+", body.casefold()):
        said = _tokens(sentence)
        known = {w[:4] for w in said}
        share = sum(1 for w in words if w in known) / len(words)
        if share < 0.7 or not exact <= set(said):
            continue
        if _negated_stems(typed) == _negated_stems(said):
            return True
    return False


def _key_statement(lowered: str, view: dict[str, Any], step_id: str) -> tuple[str, str, str] | None:
    """A typed statement of this part's point, not a question and not a denial.

    Each branch checks the fact itself, not a keyword, so a wrong statement
    falls through to the hint and never logs a ticket.
    """
    if _is_question(lowered) or _negated(lowered):
        return None
    finding, body = part_fact(view, step_id)
    if not body:
        return None
    if step_id == "complaint":
        if _complaint_insight(lowered, view):
            return "correct", body, finding
        return None
    if step_id == "data":
        label = str(view.get("rate_label") or "").casefold()
        if (
            label
            and not re.search(r"\b(?:not|never|cannot|no)\b|n't", lowered)
            and ("rate" in lowered or "share" in lowered)
            and re.search(rf"(?<![\d.]){re.escape(label)}", lowered)
        ):
            return "correct", body, finding
    if step_id == "logged" and _seen(step_id, "logged") and re.search(r"\b(?:tickets?|items?)\b", lowered):
        count = _shown_ticket_count(view)
        denies = re.search(r"\b(?:not|never|cannot)\b|n't", lowered) or (
            count != 0 and re.search(r"\b(?:no|none|nothing)\b", lowered)
        )
        if not denies and _count_statement(lowered, count):
            return "correct", body, finding
    if step_id == "notes" and _seen(step_id, "notes") and (
        _quotes_fact(lowered, body) or ("customer" in lowered and _same_sentence(lowered, body))
    ):
        return "correct", body, finding
    if step_id in {"wrap", "done"} and _seen(step_id, "notes") and (
        _quotes_fact(lowered, body) or _same_sentence(lowered, body)
    ):
        return "correct", body, finding
    return None


def _direction_claim(view: dict[str, Any], *, claimed: str = "up") -> tuple[str, str, str]:
    direction = str(view.get("direction") or "flat")
    sentence = str(view.get("direction_sentence") or "")
    if claimed == "down":
        if direction == "down":
            return "correct", sentence, "the invalid rate is lower in the later weeks of this slice"
        if direction == "up":
            return "unsupported", sentence, "a claim that the rate is going down"
        return "partial", sentence, "the rate is not a steady drop"
    if direction == "up":
        return "correct", sentence, "the invalid rate is higher in the later weeks of this slice"
    if direction == "down":
        return "unsupported", sentence, "a claim that the rate is going up"
    return "partial", sentence, "the rate is not a steady climb"


def _answer_question(lowered: str, view: dict[str, Any], step_id: str) -> str:
    glossary = _glossary_answer(lowered)
    if glossary:
        return glossary
    if _is_greeting(lowered):
        return _hello(step_id, view)
    codes = _mentioned_codes(lowered)
    if codes and (_says_most(lowered) or "biggest" in lowered or "main invalid" in lowered):
        if not _seen(step_id, "charts"):
            return "NOT YET — you'll see that on the charts part."
        return _code_question_body(lowered, codes, view)
    if codes and any(token in lowered for token in ("what is", "what does", "what's")):
        return "That means " + _join([code_plain(code) for code in codes]) + "."
    if _asserts_up(lowered) or "going up" in lowered:
        if not _seen(step_id, "data"):
            return "NOT YET — you'll see that on the numbers part."
        return str(view.get("direction_sentence") or view.get("rate_sentence") or "")
    if (
        "what is the invalid rate" in lowered
        or ("invalid rate" in lowered and "this week" in lowered)
        or ("rate" in lowered and "this week" in lowered)
    ):
        if not _seen(step_id, "data"):
            return "NOT YET — you'll see that on the numbers part."
        return str(view.get("rate_sentence") or "")
    if "who made" in lowered or "who makes" in lowered or "manufacturer" in lowered or "made the device" in lowered:
        return _maker_answer(view, step_id)
    if "promise" in lowered or re.search(r"\b98\b", lowered):
        return str(view.get("measure_sentence") or "This file counts the reports we have so far.")
    if any(word in lowered for word in ("ticket", "jira", "logged")):
        if not _seen(step_id, "logged"):
            return "NOT YET — you'll see that on the logged part."
        return _ticket_answer(view)
    if "customer" in lowered or "told" in lowered:
        if not _seen(step_id, "notes"):
            return "NOT YET — you'll see that on the notes part."
        return str((view.get("notes") or {}).get("customer") or view.get("decision") or "")
    if "recommend" in lowered or "wrap" in lowered:
        if not _seen(step_id, "notes"):
            return "NOT YET — you'll see that on the notes part."
        return str(view.get("decision") or "")
    if "group" in lowered or "hold" in lowered or "cause" in lowered or "biggest" in lowered:
        if not _seen(step_id, "charts"):
            return "NOT YET — you'll see that on the charts part."
        if "biggest" in lowered and view.get("top_plain"):
            return f"The biggest invalid type this week is {view['top_plain']}."
        return str(view.get("cause_sentence") or "")
    return _hello(step_id, view)


def _code_question_body(lowered: str, codes: list[str], view: dict[str, Any]) -> str:
    kind, body, _finding = _code_claim(lowered, codes, view)
    phrase = _sentence_case(str(view.get("majority_phrase") or "the top invalid types"))
    negated = _negated(lowered)
    if negated and kind == "correct":
        return f"The counts do not agree with the 'not'. {phrase} do make up most of the invalids."
    if negated and kind != "correct":
        return f"Right to doubt that claim. {body}"
    if kind == "correct":
        return f"Yes. {body}"
    return body


def _glossary_answer(lowered: str) -> str:
    if "maude" in lowered:
        return (
            "MAUDE is the FDA's public database of device problem reports. "
            "It counts reports of problems, not every test that ran."
        )
    if re.search(r"\booi\b", lowered):
        return "OOI means machines that run many nucleic-acid tests at once."
    if re.search(r"\bjje\b", lowered):
        return "JJE means clinical chemistry analyzers, the machines that measure chemicals in blood."
    if "openfda" in lowered:
        return "openFDA means the FDA's public download of device reports."
    if re.search(r"\bivd\b", lowered):
        return "IVD means a lab test run on a sample, not a treatment."
    if "fishbone" in lowered:
        return "A fishbone diagram sorts possible causes into groups."
    if "containment" in lowered:
        return "Containment means stopping the bad units from going out while the team looks."
    if "wilson" in lowered:
        return "A Wilson range is the likely range around the rate. This page calls it the likely range."
    return ""


def _hello(step_id: str, view: dict[str, Any]) -> str:
    screens = {
        "complaint": "You are on complaint understanding. Ask how many complaints are in the data so far, or which categories rank highest to lowest.",
        "data": "You are on the numbers. Ask how many complaints are in the data so far, or what the share is as of this week.",
        "charts": "You are on the charts. Ask which invalid types are the biggest, or whether one group stands out.",
        "logged": "You are on the logged part. Ask which plan tickets are open. A confirmed insight becomes Your ticket, not an INV number.",
        "notes": "You are on the notes. Ask what the customer should be told.",
        "wrap": "You are on the wrap-up. Ask what we recommend this week.",
        "done": "You finished the four weeks. Ask what we recommended, or what is still open.",
    }
    line = screens.get(step_id, "Ask about what is on this screen.")
    if step_id == "data" and view.get("rate_sentence"):
        return f"{line} {view['rate_sentence']}"
    if step_id in {"charts", "wrap"} and view.get("cause_sentence") and _seen(step_id, "charts"):
        return f"{line} {view.get('cause_sentence')}"
    return line


def _maker_answer(view: dict[str, Any], step_id: str) -> str:
    device = str(view.get("device_line") or "The device name is on the complaint.")
    maker = str(view.get("maker_sentence") or "")
    if maker and _seen(step_id, "charts"):
        return f"{device} {maker}"
    return device


def _ticket_answer(view: dict[str, Any]) -> str:
    tickets = view.get("tickets") or []
    if not tickets:
        return "No plan ticket is open in this week's list yet. A confirmed insight is Your ticket 1, not an INV number. On a real team this would go in Jira."
    listed = ", ".join(f"{row['key']} ({row['name']})" for row in tickets[:6])
    return (
        f"This week's plan tickets are {listed}. "
        "A confirmed insight is Your ticket 1, Your ticket 2, and so on. "
        "On a real team this would go in Jira."
    )


def _question_finding(lowered: str, view: dict[str, Any], step_id: str) -> str:
    if "maude" in lowered:
        return "the question of what MAUDE is"
    if "who made" in lowered or "device" in lowered:
        return "the question of who made the device"
    if _asserts_up(lowered) or "going up" in lowered:
        return "the question of whether the invalid rate is going up"
    if "promise" in lowered:
        return "the question of what was promised"
    if "ticket" in lowered:
        return "the question of which tickets are open"
    if "recommend" in lowered:
        return "the question of what we recommend"
    return f"a question on the {step_id} screen"


def _remember(kind: str) -> str:
    if kind == "correct":
        return "these are the first place to look in the next part."
    if kind == "partial":
        return "keep the part that matches the counts, and check the rest on the next part."
    if kind == "unsupported":
        return "we only keep a claim the counts support."
    if kind == "early":
        return "we'll check it when that part is on screen."
    if kind == "correction":
        return "the counts on this screen are the ones to keep."
    return "use the sentence on this screen before you lock a cause."


def _mentioned_codes(lowered: str) -> list[str]:
    found: list[str] = []
    for match in _CODE.findall(lowered):
        code = match.upper()
        if code not in found:
            found.append(code)
    # Fragments name a type only when the reader is talking about invalid types.
    # "not enough sample" is a code name, so the negation check ignores it.
    if not (_says_most(lowered) or "biggest" in lowered or "main invalid" in lowered or "what is" in lowered or "what does" in lowered):
        return found
    for code, fragments in _FRAGMENTS:
        if code in found:
            continue
        if any(fragment in lowered for fragment in fragments):
            found.append(code)
    # "the top two, not INV-SW" names INV-SW only to leave it out.
    denied = {code.upper() for code in re.findall(r"\b(?:not|nor)\s+(inv-[a-z]+)\b", lowered, re.I)}
    if denied and any(code not in denied for code in found):
        found = [code for code in found if code not in denied]
    return found


def _opening(text: str) -> str:
    stripped = text.strip()
    for lead in _OPENING:
        if stripped.startswith(lead):
            return lead
    return ""


def _says_most(lowered: str) -> bool:
    return bool(re.search(r"\bmost\b", lowered)) or any(token in lowered for token in _MOST)


def _asserts_up(lowered: str) -> bool:
    return any(token in lowered for token in _UP)


def _asserts_down(lowered: str) -> bool:
    return any(token in lowered for token in _DOWN)


_TOP_WORD = re.compile(r"\b(?:biggest|largest|top|most (?:common|frequent|reported)|highest|main|leading|number one)\b|#1")
_NOT_TOP = re.compile(
    r"\b(?:smallest|least|lowest|fewest|second|third|fourth|last|bottom|smaller|fewer|less|than|rather|"
    r"instead|neither|nor|without|percent|no longer|used to|ago|will|would|might|maybe|could|no|none|nothing)\b|%"
)
_CODE_FULL = re.compile(r"inv-[a-z0-9]+(?:-[a-z0-9]+)*")
_OF_PAIR = re.compile(r"(\d+(?:\.\d+)?)\s+(?:out\s+)?of\s+(\d+(?:\.\d+)?)")
_NUMBER_TOKEN = re.compile(r"\d+(?:\.\d+)?")


def _fragments_for(code: str) -> tuple[str, ...]:
    for name, words in _FRAGMENTS:
        if name.casefold() == code.casefold():
            return words
    return ()


def _complaint_insight(lowered: str, view: dict[str, Any]) -> bool:
    """The complaint point: the real top category and its count, claimed as the biggest.

    The message must name the top category, say it is the biggest, and give
    "count of total" with no other number, no other category, and no
    smallest, second, "no longer", or percent wording.
    """
    explore = view.get("explore") or {}
    top = str(explore.get("top_code") or "").casefold()
    count = int(explore.get("top_count") or 0)
    total = int(explore.get("invalid_total") or 0)
    week = int(explore.get("week") or view.get("story_week") or 1)
    if not top or count <= 0 or total <= 0:
        return False
    if "?" in lowered or re.search(r",\s*(?:right|isn't it|is it)\s*$", lowered):
        return False
    plain = str(explore.get("top_plain") or "").casefold()
    core = re.sub(r"^(?:a|an|the)\s+", "", plain.split("(")[0].strip())
    own = [fragment for fragment in _fragments_for(top)]
    masked = lowered
    for name in sorted({*_NEGATED_NAMES, plain, core, *own} - {""}, key=len, reverse=True):
        masked = masked.replace(name, "codename")
    if re.search(r"\b(?:not|never|cannot)\b|n't", masked) or _NOT_TOP.search(masked):
        return False
    if not _TOP_WORD.search(masked):
        return False
    codes = set(_CODE_FULL.findall(lowered))
    if codes - {top}:
        return False
    for name, words in _FRAGMENTS:
        if name.casefold() != top and any(word in lowered for word in words):
            return False
    named = (
        top in codes
        or (bool(plain) and plain in lowered)
        or (len(core) > 8 and core in lowered)
        or any(fragment in lowered for fragment in own)
    )
    if not named:
        return False
    pairs = _OF_PAIR.findall(lowered)
    if not pairs or any(pair != (str(count), str(total)) for pair in pairs):
        return False
    allowed = {str(count), str(total), str(week)}
    return all(number in allowed for number in _NUMBER_TOKEN.findall(_CODE_FULL.sub(" ", lowered)))


def _category_attempt(lowered: str) -> bool:
    if not re.search(r"\b(biggest|highest|main|top|largest|most)\b", lowered):
        return False
    if re.search(r"\b(?:categor(?:y|ies)|invalid types?)\b|inv-[a-z0-9]+", lowered):
        return True
    return any(word in lowered for _name, words in _FRAGMENTS for word in words)


def _is_question(lowered: str) -> bool:
    stripped = lowered.strip()
    if "?" in stripped:
        return True
    core = stripped.lstrip("([\"' ")
    return core.startswith(_QUESTION_START)


def _is_greeting(lowered: str) -> bool:
    stripped = lowered.strip(" !.?,")
    return stripped in {"hi", "hello", "hey", "hi there", "hello there"} or stripped.startswith("hello ")


def _join(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"
