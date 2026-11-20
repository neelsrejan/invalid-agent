"""Drop cached package modules when their files changed or live outside this tree.

Streamlit re-executes the page and keeps imported modules. A deploy can
replace a file on disk while the process still holds the previous module.
The page calls ``ensure_checkout`` before it imports the package, then
``note_imports`` after those imports succeed.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

_LOCK = threading.Lock()
_STAMPS: dict[str, float] = {}
# This module holds the stamps. Evicting it would forget them on the next rerun.
_SELF = "invalid_agent.fresh"


def _ours(name: str) -> bool:
    return name == "invalid_agent" or name.startswith("invalid_agent.")


def _source_path(module: object) -> Path | None:
    raw = getattr(module, "__file__", None)
    if not raw:
        return None
    path = Path(str(raw)).resolve()
    if path.suffix == ".pyc":
        sibling = path.with_suffix(".py")
        if sibling.is_file():
            return sibling
    return path


def _outside_src(path: Path, src: Path) -> bool:
    try:
        path.resolve().relative_to(src.resolve())
    except ValueError:
        return True
    return False


def _stale(name: str, module: object, src: Path) -> bool:
    path = _source_path(module)
    if path is None:
        return False
    if _outside_src(path, src):
        return True
    stamp = _STAMPS.get(name)
    if stamp is None:
        return False
    try:
        return path.stat().st_mtime > float(stamp) + 1e-6
    except OSError:
        return True


def ensure_checkout(src: Path) -> bool:
    """Evict ``invalid_agent`` modules whose files moved on or off this source tree.

    A module is evicted when its file is outside ``src``, or when that file is
    newer than the mtime recorded by ``note_imports``. One stale module drops
    the rest of the package so the next import is one consistent tree.
    Returns True when anything was evicted.
    """
    with _LOCK:
        checkout = src.resolve()
        stale = [
            name
            for name, module in list(sys.modules.items())
            if _ours(name) and name != _SELF and _stale(name, module, checkout)
        ]
        if not stale:
            return False
        for name in list(sys.modules):
            if _ours(name) and name != _SELF:
                del sys.modules[name]
        for name in list(_STAMPS):
            if name != _SELF:
                _STAMPS.pop(name, None)
        return True


def note_imports() -> None:
    """Record the mtime of each ``invalid_agent`` module now in memory."""
    with _LOCK:
        for name, module in list(sys.modules.items()):
            if not _ours(name):
                continue
            path = _source_path(module)
            if path is None or not path.is_file():
                continue
            try:
                _STAMPS[name] = path.stat().st_mtime
            except OSError:
                continue
