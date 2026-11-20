"""Drop cached package modules when their files changed or live outside this tree.

Streamlit re-executes the page and keeps imported modules. A deploy can
replace a file on disk while the process still holds the previous module.
The page calls ``ensure_checkout`` before it imports the package, then
``note_imports`` after those imports succeed.
"""

from __future__ import annotations

import ast
import struct
import sys
import threading
from pathlib import Path

_LOCK = threading.Lock()
_STAMPS: dict[str, float] = {}
_NOTED = False  # True once note_imports has run in this process
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


def _public_names(path: Path) -> set[str] | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found = [node.name]
        elif isinstance(node, ast.Assign):
            found = [target.id for target in node.targets if isinstance(target, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            found = [node.target.id]
        else:
            found = []
        names.update(name for name in found if not name.startswith("_"))
    return names


def _missing_exported_name(module: object, path: Path) -> bool:
    """The file on disk defines a public name this loaded module does not have."""
    names = _public_names(path)
    if names is None:
        return True
    return any(not hasattr(module, name) for name in names)


def _pyc_predates_source(module: object, path: Path) -> bool:
    """The bytecode this module was loaded from records an older source time.

    A bytecode file that another process rewrote is not enough on its own: its
    file time can be newer while this process still holds the previous module.
    The timestamp stored inside the bytecode is the source time it was built
    from. A missing bytecode file means the module is old only before the
    first ``note_imports``. After that, a missing file does not drop a module
    that already has every public name.
    """
    cached = getattr(module, "__cached__", None)
    if not cached:
        # No bytecode path at all (python -B). Before the first note_imports,
        # an unstamped module is from the previous release.
        return not _NOTED
    try:
        header = Path(str(cached)).read_bytes()[:16]
        source_mtime = int(path.stat().st_mtime)
    except OSError:
        # The recorded .pyc is missing. Same rule: evict only before the first stamp.
        return not _NOTED
    if len(header) < 16:
        return True
    flags = struct.unpack("<I", header[4:8])[0]
    if flags & 0x1:
        return False
    built_for = struct.unpack("<I", header[8:12])[0]
    return source_mtime > built_for


def _stale(name: str, module: object, src: Path) -> bool:
    path = _source_path(module)
    if path is None:
        return False
    if _outside_src(path, src):
        return True
    stamp = _STAMPS.get(name)
    if stamp is None:
        return _missing_exported_name(module, path) or _pyc_predates_source(module, path)
    try:
        return path.stat().st_mtime > float(stamp) + 1e-6
    except OSError:
        return True


def ensure_checkout(src: Path) -> bool:
    """Evict ``invalid_agent`` modules whose files moved on or off this source tree.

    A module is evicted when its file is outside ``src``, when that file is
    newer than the mtime recorded by ``note_imports``, or when this process has
    no stamp for it and the loaded module is missing a name the file defines,
    was loaded from older bytecode, or has no readable bytecode yet and
    ``note_imports`` has not run. One stale module drops
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
    global _NOTED
    with _LOCK:
        _NOTED = True
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
