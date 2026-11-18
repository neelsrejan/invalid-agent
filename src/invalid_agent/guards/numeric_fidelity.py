"""Reject narrative numbers that are not in the computed facts.

Identifiers such as ``L-4419`` and ``2.4.0`` are removed before the scan
when that exact string appears in the facts, so a lot id is not mistaken
for a rate and is also not a free pass for some other number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_NUMBER = re.compile(r"(?<![A-Za-z0-9._-])(\d+(?:\.\d+)?)")
_DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
# Claims about the rate. A lot that "stayed inside the spec" is not one of these.
_NOT_EXCEED = re.compile(
    r"\b(?:does not exceed|do not exceed|doesn't exceed|does not break)\b"
    r".{0,60}?\b(?:spec|specification|cap)\b"
    r"|"
    r"\b(?:invalid[- ]type share|invalid rate|overall rate)\b"
    r".{0,60}?\b(?:within the spec|inside the spec|meets the spec|below the spec)\b",
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


def _identifiers(obj: Any, found: set[str]) -> None:
    if isinstance(obj, str):
        if len(obj) >= 2:
            found.add(obj)
        return
    if isinstance(obj, dict):
        for item in obj.values():
            _identifiers(item, found)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _identifiers(item, found)


def allowed_numbers(facts: Any) -> set[float]:
    found: set[float] = set()
    _walk_numbers(facts, found)
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
    identifiers: set[str] = set()
    _identifiers(facts, identifiers)
    masked = _DATE.sub(" ", text)
    for identifier in sorted(identifiers, key=len, reverse=True):
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
