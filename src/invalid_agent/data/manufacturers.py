"""Display names for manufacturers.

openFDA MAUDE is public. The default is the reported firm name.
``MANUFACTURER_DISPLAY=anonymized`` still maps those names to Manufacturer A,
B, C when someone wants the page without firm names. The stored table always
keeps the reported name.
"""

from __future__ import annotations

from typing import Iterable

from invalid_agent.config import Settings, load_settings


def display_labels(names: Iterable[str]) -> dict[str, str]:
    """Map sorted unique names to Manufacturer A, Manufacturer B, ..."""
    unique = sorted({str(name).strip() for name in names if str(name).strip() and str(name).strip() != "UNREPORTED"})
    labels: dict[str, str] = {}
    for index, name in enumerate(unique):
        if index < 26:
            suffix = chr(ord("A") + index)
        else:
            suffix = str(index + 1)
        labels[name] = f"Manufacturer {suffix}"
    return labels


def anonymized(settings: Settings | None = None) -> bool:
    settings = settings or load_settings()
    return settings.manufacturer_display != "real"


def relabel(name: str, labels: dict[str, str], *, enabled: bool) -> str:
    text = str(name)
    if not enabled:
        return text
    return labels.get(text, text)
