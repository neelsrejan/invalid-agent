"""On-disk extract cache. Repeat runs, tests, and the dashboard do not call openFDA."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from invalid_agent.config import load_settings


def cache_root() -> Path:
    import os

    override = os.environ.get("INVALID_AGENT_CACHE", "").strip()
    if override:
        return Path(override)
    return load_settings().repo_root / "data" / "cache" / "openfda"


def case_paths(case_id: str, root: Path | None = None) -> tuple[Path, Path]:
    folder = root or cache_root()
    return folder / f"{case_id}.jsonl", folder / f"{case_id}.meta.json"


def read_meta(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_case(case_id: str, rows: list[dict[str, Any]], meta: dict[str, Any], root: Path | None = None) -> Path:
    folder = root or cache_root()
    folder.mkdir(parents=True, exist_ok=True)
    jsonl, meta_path = case_paths(case_id, folder)
    with jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":"), default=str))
            handle.write("\n")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return jsonl


def read_rows(case_id: str, root: Path | None = None) -> list[dict[str, Any]]:
    jsonl, _meta = case_paths(case_id, root or cache_root())
    if not jsonl.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def is_complete(case_id: str, root: Path | None = None) -> bool:
    _jsonl, meta_path = case_paths(case_id, root or cache_root())
    meta = read_meta(meta_path)
    return bool(meta and meta.get("complete"))
