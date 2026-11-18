"""Reject narrative numbers that are not in the computed facts.

Identifiers such as ``L-4419``, ``2.4.0``, and a lot of four or more digits
are removed before the scan when that string appears in the facts. A lot
named ``12`` is removed only in ``lot 12`` or ``model 12``, so a fabricated
``12%`` is still rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_NUMBER = re.compile(r"(?<![A-Za-z0-9._-])(\d+(?:\.\d+)?)")
_DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
_YEAR = re.compile(r"\b(20\d{2})\b")
_PURE_DIGITS = re.compile(r"^\d+$")
_VERSION_ID = re.compile(r"^\d+(?:\.\d+){2,}$")
# Claims about the rate. A lot that "stayed inside the spec" is not one of these.
_NOT_EXCEED = re.compile(
    r"\b(?:does not exceed|do not exceed|doesn't exceed|does not break)\b"
    r".{0,60}?\b(?:spec|specification|cap)\b"
    r"|"
    r"\b(?:invalid[- ]type share|invalid rate|overall rate)\b"
    r".{0,60}?\b(?:within the spec|inside the spec|meets the spec|below the spec|not above the spec)\b"
    r"|"
    r"\b(?:do not|does not|don't|doesn't|cannot|can't)\b"
    r".{0,120}?\b(?:exceeds?|above|over)\b"
    r".{0,60}?\b(?:spec|specification|cap)\b",
    re.IGNORECASE | re.DOTALL,
)
_EXCEED = re.compile(
    r"\b(?:exceeds?|above|over|breaks|outside) the spec(?:ification)?\b",
    re.IGNORECASE,
)


@dataclass
class FidelityResult:
    ok: bool
    unknown: list[float] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "unknown": self.unknown, "claims": self.claims}


def _walk_numbers(obj: Any, found: set[float]) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        value = float(obj)
        found.add(value)
        found.add(round(value, 2))
        found.add(round(value, 4))
        if 0.0 < abs(value) <= 1.0:
            found.add(round(value * 100.0, 2))
            found.add(round(value * 100.0, 1))
        return
    if isinstance(obj, dict):
        for item in obj.values():
            _walk_numbers(item, found)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _walk_numbers(item, found)


def _collect_strings(obj: Any, found: set[str]) -> None:
    if isinstance(obj, str):
        if len(obj) >= 2:
            found.add(obj)
        return
    if isinstance(obj, dict):
        for item in obj.values():
            _collect_strings(item, found)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _collect_strings(item, found)


def _maskable(token: str) -> bool:
    """Which fact strings may be removed before the number scan.

    A lot named ``12`` must not erase a fabricated ``12%``. Bare ids are
    masked only when they are four or more digits, a dotted version such as
    ``2.4.0``, or any id that contains a letter. Short numeric ids are masked
    only in ``lot <id>`` or ``model <id>`` context.
    """
    if _PURE_DIGITS.fullmatch(token):
        return len(token) >= 4
    if _VERSION_ID.fullmatch(token):
        return True
    return any(character.isalpha() for character in token)


def _mask_tokens(raw: set[str]) -> list[str]:
    tokens: list[str] = []
    for text in raw:
        if _maskable(text):
            tokens.append(text)
        if _PURE_DIGITS.fullmatch(text):
            for label in ("lot ", "Lot ", "model ", "Model ", "reagent_lot "):
                tokens.append(label + text)
            tokens.append(f":{text}:")
    return tokens


def _years_in_range(raw_strings: set[str]) -> set[float]:
    """Every calendar year from the earliest to the latest year written in the facts.

    A date window of 2022-01-01 through 2024-12-31 makes 2022, 2023, and 2024
    labels, so a sentence can name 2024 without the guard calling it a rate.
    """
    found: set[int] = set()
    for text in raw_strings:
        for match in _YEAR.finditer(text):
            found.add(int(match.group(1)))
    if not found:
        return set()
    return {float(year) for year in range(min(found), max(found) + 1)}


def allowed_numbers(facts: Any) -> set[float]:
    found: set[float] = set()
    _walk_numbers(facts, found)
    raw_strings: set[str] = set()
    _collect_strings(facts, raw_strings)
    found.update(_years_in_range(raw_strings))
    return found


def _atol(value: float) -> float:
    # Counts (14400 vs 14400.4) get half a unit. Rates printed to two
    # decimals get 0.03, so 3.67 matches 3.67 and 3.70, and 3.72 does not.
    if abs(value) >= 50:
        return 0.51
    return 0.03


def _rate_and_spec(facts: Any) -> tuple[float, float] | None:
    if not isinstance(facts, dict):
        return None
    overall = facts.get("overall")
    if not isinstance(overall, dict):
        return None
    rate = overall.get("rate")
    spec = overall.get("spec_invalid_rate")
    if rate is None and overall.get("rate_pct") is not None and overall.get("spec_pct") is not None:
        rate = float(overall["rate_pct"]) / 100.0
        spec = float(overall["spec_pct"]) / 100.0
    if rate is None or spec is None:
        return None
    return float(rate), float(spec)


def spec_claim_errors(text: str, facts: Any) -> list[str]:
    """Reject a sentence that says the rate is inside or outside the spec when the numbers disagree.

    The comparison is rate versus the spec number. A share above 2% must not
    be described as not exceeding the spec, even when that spec is not estimable
    from reported events.
    """
    pair = _rate_and_spec(facts)
    if pair is None:
        return []
    rate, spec = pair
    above = rate > spec
    errors: list[str] = []
    if _NOT_EXCEED.search(text) and above:
        errors.append("text says the rate does not exceed the spec, but the rate is above the spec")
    stripped = _NOT_EXCEED.sub(" ", text)
    if _EXCEED.search(stripped) and not above:
        errors.append("text says the rate exceeds the spec, but the rate is not above the spec")
    return errors


def check_narrative(text: str, facts: Any) -> FidelityResult:
    """Return ok=False when any remaining number is not near a fact, or a spec claim disagrees."""
    raw_strings: set[str] = set()
    _collect_strings(facts, raw_strings)
    masked = _DATE.sub(" ", text)
    for identifier in sorted(_mask_tokens(raw_strings), key=len, reverse=True):
        masked = masked.replace(identifier, " ")
    allowed = allowed_numbers(facts)
    unknown: list[float] = []
    for match in _NUMBER.finditer(masked):
        value = float(match.group(1))
        if any(abs(value - candidate) <= _atol(value) for candidate in allowed):
            continue
        unknown.append(value)
    claims = spec_claim_errors(text, facts)
    return FidelityResult(ok=not unknown and not claims, unknown=unknown, claims=claims)
