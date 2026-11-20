"""Talk-back agent for one week and one part of the story.

Python classifies the message and writes the reply from the week view.
A language model may only rephrase that reply. If the model is missing,
fails, or adds a number, the plain reply is what the page shows.
"""

from __future__ import annotations

import re
from typing import Any

from invalid_agent.guards.numeric_fidelity import check_narrative

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
    "should ",
)
_MOST = ("majority", "most of", "make up most", "makes up most", "almost all")
_UP = ("going up", "is rising", "is climbing", "rate is up", "keeps climbing")
_CODE = re.compile(r"\bINV-[A-Z0-9]+\b", re.I)
_NUMBER = re.compile(r"\d+(?:\.\d+)?")
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
    """Three short prompts a reader can click. Each one is scored from the view."""
    prompts: list[str] = []
    if view.get("majority") and view.get("majority_phrase"):
        verb = "makes up most of the invalids" if len(view.get("majority_codes") or []) == 1 else "make up most of the invalids"
        prompts.append(f"It looks like {view['majority_phrase']} {verb}")
    elif view.get("top_plain"):
        prompts.append(f"The biggest invalid type is {view['top_plain']}")
    prompts.append("Why is the invalid rate going up?")
    extra = {
        "complaint": "What was promised, and can this file measure it?",
        "data": "What is the invalid rate this week?",
        "charts": "Is there one group we should hold?",
        "logged": "Which tickets are open this week?",
        "notes": "What should the customer be told?",
        "wrap": "What do we recommend this week?",
    }.get(step_id, "What should we remember from this screen?")
    prompts.append(extra)
    # Keep three, and keep them unique so the buttons do not collide.
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
) -> dict[str, Any]:
    """Classify ``message`` and answer from ``view``. No model. No new numbers."""
    text = " ".join(str(message or "").split())
    if not text:
        return {
            "kind": "question",
            "confirmed": False,
            "text": "Type a question, or type what you think the screen is saying. Then I can check it against this week's counts.",
            "bullet": None,
            "log_kind": "",
            "log_key": "",
            "log_text": "",
            "user_text": "",
        }
    kind, body, finding = _classify(text, view, step_id)
    confirmed = kind == "correct"
    key = ticket_key if confirmed else flag_key
    remember = _remember(kind, view)
    lead = {
        "correct": "YEP, YOU GOT IT!",
        "partial": "CLOSE! YOU ARE ON THE RIGHT TRACK.",
        "unsupported": "NOT QUITE. THE FILE DOES NOT SAY THAT.",
        "question": "GOOD QUESTION.",
    }[kind]
    if confirmed:
        log_line = f"We'll log that as Jira ticket {key} to track it and keep it in mind for the root cause."
        bullet = f"We found {finding} -> logged as Jira ticket {key} to resolve going forward"
    else:
        log_line = f"We'll log that as {key} so we do not lose it. It is not a confirmed finding."
        bullet = None
    reply = f"{lead} {body} {log_line} Remember: {remember}"
    return {
        "kind": kind,
        "confirmed": confirmed,
        "text": reply,
        "bullet": bullet,
        "log_kind": "ticket" if confirmed else "flag",
        "log_key": key,
        "log_text": bullet or f"{key}: {finding}",
        "user_text": text,
    }


def reword_reply(base_text: str, llm: Any | None) -> str:
    """Let a model rephrase ``base_text``. Any failure returns ``base_text`` unchanged."""
    if llm is None or getattr(llm, "name", "deterministic") == "deterministic":
        return base_text
    try:
        draft = llm.complete(
            system=(
                "You rewrite one reply for a high school reader. "
                "Keep every number. Keep the ticket or flag id. "
                "Do not add numbers, file paths, or the word fidelity. "
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
    if any(token in lowered for token in _BANNED):
        return False
    if _NUMBER.findall(base) and set(_NUMBER.findall(base)) - set(_NUMBER.findall(cleaned)):
        return False
    if "inv-" not in lowered and "flag" not in lowered:
        return False
    checked = check_narrative(cleaned, {"base": base})
    return bool(checked.ok)


def _classify(text: str, view: dict[str, Any], step_id: str) -> tuple[str, str, str]:
    lowered = text.casefold()
    codes = _mentioned_codes(lowered)
    if codes and (_says_most(lowered) or "biggest" in lowered or "main invalid" in lowered):
        return _code_claim(lowered, codes, view)
    if _asserts_up(lowered) and not _is_question(lowered):
        return _direction_claim(view)
    if _is_question(lowered) or lowered.startswith("it looks like"):
        return "question", _answer_question(lowered, view, step_id), _question_finding(lowered, view, step_id)
    if codes:
        return _code_claim(lowered, codes, view)
    return "question", _answer_question(lowered, view, step_id), _question_finding(lowered, view, step_id)


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
    if says_most and covers and not extra and named_share >= 0.5:
        verb = "makes up" if len(majority) == 1 else "make up"
        body = f"{phrase} really {verb} most of the invalids this week."
        return "correct", body, f"{phrase} {verb} most of the invalids"
    if "biggest" in lowered and codes[0] == str(view.get("top_code") or "") and len(codes) == 1:
        top = str(view.get("top_plain") or codes[0])
        body = f"The biggest invalid type this week is {top}."
        return "correct", body, f"the biggest invalid type is {top}"
    if (says_most and found & set(majority)) or (str(view.get("top_code") or "") in found):
        body = (
            f"You named a real slice. It is not the whole story. "
            f"The slices that make up most of the invalids are {phrase}."
        )
        return "partial", body, f"part of the top slices, not the full set ({phrase})"
    body = (
        f"Those types are not most of the invalids. "
        f"The slices that make up most of them are {phrase}."
    )
    return "unsupported", body, "a claim the counts do not support"


def _direction_claim(view: dict[str, Any]) -> tuple[str, str, str]:
    direction = str(view.get("direction") or "flat")
    sentence = str(view.get("direction_sentence") or "")
    if direction == "up":
        return "correct", sentence, "the invalid rate is higher in the later weeks of this slice"
    if direction == "down":
        return "unsupported", sentence, "a claim that the rate is going up"
    return "partial", sentence, "the rate is not a steady climb"


def _answer_question(lowered: str, view: dict[str, Any], step_id: str) -> str:
    if _asserts_up(lowered) or "invalid rate" in lowered or "going up" in lowered:
        return str(view.get("direction_sentence") or view.get("rate_sentence") or "")
    if "promise" in lowered or "measure" in lowered or "98" in lowered:
        return f"{view.get('promise_sentence', '')} {view.get('measure_sentence', '')}".strip()
    if "ticket" in lowered or "jira" in lowered or "logged" in lowered or "open" in lowered:
        tickets = view.get("tickets") or []
        if not tickets:
            return "No ticket is open in this week's plan yet."
        listed = ", ".join(f"{row['key']} ({row['name']})" for row in tickets[:6])
        return f"This week's open plan tickets are {listed}."
    if "customer" in lowered or "told" in lowered:
        return str((view.get("notes") or {}).get("customer") or view.get("decision") or "")
    if "recommend" in lowered or "wrap" in lowered:
        return str(view.get("decision") or "")
    if "group" in lowered or "hold" in lowered or "cause" in lowered:
        return str(view.get("cause_sentence") or "")
    if "biggest" in lowered or "invalid type" in lowered:
        top = view.get("top_plain")
        if top:
            return f"The biggest invalid type this week is {top}."
        return "This week's slice has no invalids."
    return _step_fact(view, step_id)


def _question_finding(lowered: str, view: dict[str, Any], step_id: str) -> str:
    if _asserts_up(lowered) or "going up" in lowered:
        return "the question of whether the invalid rate is going up"
    if "promise" in lowered:
        return "the question of what was promised"
    if "ticket" in lowered:
        return "the question of which tickets are open"
    if "recommend" in lowered:
        return "the question of what we recommend"
    return f"a question on the {step_id} screen about {view.get('rate_sentence', 'this week')}"


def _step_fact(view: dict[str, Any], step_id: str) -> str:
    if step_id == "complaint":
        return f"{view.get('promise_sentence', '')} {view.get('measure_sentence', '')}".strip()
    if step_id == "logged":
        tickets = view.get("tickets") or []
        if not tickets:
            return "Nothing new is logged this week."
        return "Logged this week: " + ", ".join(row["key"] for row in tickets) + "."
    if step_id == "notes":
        return str(view.get("decision") or "")
    if step_id == "wrap":
        return str(view.get("decision") or "")
    if step_id == "charts":
        return f"{view.get('rule1_sentence', '')} {view.get('cause_sentence', '')}".strip()
    return str(view.get("rate_sentence") or view.get("direction_sentence") or "")


def _remember(kind: str, view: dict[str, Any]) -> str:
    if kind == "correct":
        return "keep this in mind for the root cause."
    if kind == "partial":
        return f"the counts still say this: {view.get('cause_sentence', '')}"
    if kind == "unsupported":
        return "we only keep a claim the counts support."
    rule = str(view.get("rule1_sentence") or "")
    if rule:
        return rule[0].lower() + rule[1:] if rule else "check the counts before you lock a cause."
    return "check the counts before you lock a cause."


def _mentioned_codes(lowered: str) -> list[str]:
    found: list[str] = []
    for match in _CODE.findall(lowered):
        code = match.upper()
        if code not in found:
            found.append(code)
    for code, fragments in _FRAGMENTS:
        if code in found:
            continue
        if any(fragment in lowered for fragment in fragments):
            found.append(code)
    return found


def _says_most(lowered: str) -> bool:
    return any(token in lowered for token in _MOST)


def _asserts_up(lowered: str) -> bool:
    return any(token in lowered for token in _UP)


def _is_question(lowered: str) -> bool:
    stripped = lowered.strip()
    if stripped.endswith("?"):
        return True
    return stripped.startswith(_QUESTION_START)
