"""Immutable commit the Academy clips and line links were recorded against.

Tag academy-v2 names this SHA. Later commits on main do not move it.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

PIN_TAG = "academy-v2"
PIN_SHA = "d057d3ead8f9320fb738110924317b6f5bcc021c"
PIN_SHORT = PIN_SHA[:7]

ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def assert_tag() -> None:
    """Refuse to continue if the tag is missing or has been moved."""
    try:
        got = _git("rev-parse", f"{PIN_TAG}^{{}}").strip()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"tag {PIN_TAG} is missing. It must point at {PIN_SHA}."
        ) from exc
    if got != PIN_SHA:
        raise SystemExit(f"tag {PIN_TAG} points at {got}, not {PIN_SHA}")


def pinned_text(path: str) -> str:
    """File bytes as stored at the pinned commit, not the working tree."""
    assert_tag()
    try:
        return _git("show", f"{PIN_SHA}:{path}")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"{PIN_TAG} has no {path}") from exc


def first_line(path: str, lines: str) -> str:
    start = int(str(lines).split("-", 1)[0])
    rows = pinned_text(path).splitlines()
    if start < 1 or start > len(rows):
        raise SystemExit(f"{path} line {start} is outside 1..{len(rows)} at {PIN_TAG}")
    return rows[start - 1]
