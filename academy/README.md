# invalid-agent Academy

Static course for sessions 1–9. Open it from any browser. Quizzes, progress, and videos have no backend and no paid service.

Session 1’s narration is the reference pack (project file, config, tests, CI). Sessions 2–9 follow each tag’s `docs/sessions/session-N/LOGIC_TRACE.md`. Code on screen is the `session-N` tag, not today’s `main`.

Speech is edge-tts only, voice `en-US-AndrewNeural`. The renderer will not fall back to another engine.

## Study

Published site: GitHub Pages from the `gh-pages` branch (videos live there, not in `main`).

Locally, after a render:

```bash
python3 academy/scripts/publish_pages.sh
python3 -m http.server -d academy/build/pages 8765
```

Pass a quiz at 80% (7 of 8) to unlock the next session. Progress stays in `localStorage`. Export copies a checksummed code (`IA1.…`) you can paste on another computer.

## Rebuild

```bash
pip install -r academy/requirements.txt
python3 academy/scripts/render_all.py          # git-archive each tag, then MP4s
python3 academy/scripts/verify_videos.py       # ffprobe, edge-tts only, under 100 MB
python3 academy/scripts/build_site.py
```

Snapshots under `academy/snapshots/` and MP4s under `academy/build/` are gitignored so `main` stays light.

## One-time Pages setting

If the live site is not already on, in the repo: Settings → Pages → Build and deployment → Deploy from a branch → branch `gh-pages` → folder `/` → Save. The URL is `https://neelsrejan.github.io/invalid-agent/`.

The dashboard link is `streamlitUrl` in `academy/site/js/site-config.js` (`https://invalid-agent-lwycv4pt4vd4emwhuiqde3.streamlit.app/`). Jira points at `https://neelsrejan.atlassian.net/jira/projects` (project key `INV`).

Quiz letters live in `academy/content/bank.py` for rebuilds. The pages only get a salted SHA-256 of the correct choice, and the explanation is base64 until you submit.
