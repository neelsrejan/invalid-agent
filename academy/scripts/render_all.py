#!/usr/bin/env python3
"""Materialize session tags and render any narration YAML that has no MP4 yet."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACADEMY = ROOT / "academy"
sys.path.insert(0, str(ACADEMY))

from render_walkthrough import render  # noqa: E402


def materialize(sessions: range) -> None:
    snap = ACADEMY / "snapshots"
    snap.mkdir(parents=True, exist_ok=True)
    for n in sessions:
        dest = snap / f"session-{n}"
        marker = dest / "pyproject.toml"
        if marker.exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        print(f"extracting tag session-{n}")
        archive = subprocess.check_output(["git", "archive", f"session-{n}"], cwd=ROOT)
        subprocess.run(["tar", "-x", "-C", str(dest)], input=archive, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=int, action="append", dest="sessions")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    wanted = args.sessions or list(range(1, 10))
    materialize(wanted)
    out_root = ACADEMY / "build" / "videos"
    for n in wanted:
        folder = ACADEMY / "narration" / f"session-{n}"
        scripts = sorted(folder.glob("*.yaml"))
        if not scripts:
            raise SystemExit(f"no narration in {folder}")
        for script in scripts:
            dest = out_root / f"session-{n}" / f"{script.stem}.mp4"
            if dest.exists() and dest.stat().st_size > 100_000 and not args.force:
                print(f"keep {dest}")
                continue
            last = None
            for attempt in range(1, 4):
                try:
                    render(script, dest)
                    last = None
                    break
                except Exception as exc:  # noqa: BLE001 — retry a flaky speech call
                    last = exc
                    print(f"retry {attempt} for {script.name}: {exc}", file=sys.stderr)
                    dest.unlink(missing_ok=True)
                    dest.with_suffix(".json").unlink(missing_ok=True)
            if last is not None:
                raise SystemExit(f"failed {script}: {last}")


if __name__ == "__main__":
    main()
