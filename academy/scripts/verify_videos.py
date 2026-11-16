#!/usr/bin/env python3
"""Confirm every academy MP4 is one edge-tts voice, playable, and under 100 MB."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO_ROOT = ROOT / "academy" / "build" / "videos"
# Sibling academies land between about half a minute and two minutes:
# an architecture card, then a few ranges, not a line-by-line reading.
MIN_S, MAX_S = 25.0, 180.0


def probe(path: Path) -> dict:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def main() -> None:
    scripts = sorted(VIDEO_ROOT.glob("session-*/*.mp4"))
    expected = []
    narration = ROOT / "academy" / "narration"
    for n in range(1, 10):
        folder = narration / f"session-{n}"
        yamls = sorted(folder.glob("*.yaml"))
        if len(yamls) != 2:
            print(f"{folder} should hold 2 clips, found {len(yamls)}", file=sys.stderr)
            sys.exit(1)
        for script in yamls:
            expected.append(VIDEO_ROOT / f"session-{n}" / f"{script.stem}.mp4")
    missing = [path for path in expected if not path.is_file()]
    extra = [path for path in scripts if path not in expected]
    if missing or extra:
        print("missing:", ", ".join(str(p) for p in missing), file=sys.stderr)
        print("extra:", ", ".join(str(p) for p in extra), file=sys.stderr)
        sys.exit(1)
    files = expected
    rows = []
    bad = False
    for path in files:
        info = probe(path)
        dur = float(info["format"]["duration"])
        size = int(info["format"]["size"])
        kinds = {(s.get("codec_type"), s.get("codec_name")) for s in info["streams"]}
        side = json.loads(path.with_suffix(".json").read_text())
        engines = side.get("engines") or [side.get("engine")]
        problems = []
        if engines != ["edge-tts"]:
            problems.append(f"tts {engines}")
        if side.get("voice") != "en-US-AndrewNeural":
            problems.append(f"voice {side.get('voice')}")
        if ("video", "h264") not in kinds or ("audio", "aac") not in kinds:
            problems.append(f"streams {kinds}")
        if size >= 100 * 1024 * 1024:
            problems.append(f"size {size}")
        if not (MIN_S <= dur <= MAX_S):
            problems.append(f"duration {dur:.1f}s outside {MIN_S:.0f}-{MAX_S:.0f}")
        flag = "OK" if not problems else "FAIL " + "; ".join(problems)
        if problems:
            bad = True
        m, s = divmod(int(round(dur)), 60)
        rows.append((path.relative_to(VIDEO_ROOT).as_posix(), f"{m}:{s:02d}", f"{size/1e6:.1f} MB", flag))
        print(f"{rows[-1][0]:48} {rows[-1][1]:>6} {rows[-1][2]:>10}  {flag}")
    print(f"\n{len(rows)} videos")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
