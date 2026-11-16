# invalid-agent Academy

Static course for sessions 1–9. Quizzes, progress, and videos have no backend and no paid service.

Each clip opens with an architecture card, then a short walk through a few ranges of the file on `main`. Speech is edge-tts only, voice `en-US-AndrewNeural`. The renderer will not fall back to another engine.

Quizzes are about boundaries and tradeoffs. They do not ask for syntax or a line number. Pass at 80% (7 of 8) to unlock the next session. Progress stays in `localStorage` under `ia-academy-progress-v2`. Export copies a checksummed code (`IA2.…`). Older `IA1` codes are not imported.

## Study

Published site: GitHub Pages from the `gh-pages` branch (videos live there, not in `main`). The URL is `https://neelsrejan.github.io/invalid-agent/`.

Locally, after a render:

```bash
python3 academy/scripts/emit_narration.py
python3 academy/scripts/render_all.py
python3 academy/scripts/verify_videos.py
python3 academy/scripts/build_site.py
python3 -m http.server -d academy/site 8765
```

Copy `academy/build/videos` to `academy/site/videos` when you want the clips to play from that server. `academy/site/videos/` is gitignored.

## Rebuild

```bash
pip install -r academy/requirements.txt
python3 academy/scripts/emit_narration.py
python3 academy/scripts/render_all.py
python3 academy/scripts/verify_videos.py
python3 academy/scripts/build_site.py
```

Snapshots under `academy/snapshots/` and MP4s under `academy/build/` stay out of `main`. Clip durations live in `academy/content/durations.json`, so `build_site.py` can rebuild the HTML without the video files. CI runs that script and fails if `academy/site/` or `academy/content/QUIZ_ANSWERS.md` drift.

## Pages

Settings → Pages → Deploy from a branch → `gh-pages` → folder `/`. Do not change that source. `academy/scripts/publish_pages.sh --push` replaces the site and the videos on `gh-pages`.

The dashboard link is `streamlitUrl` in `academy/site/js/site-config.js` (`https://invalid-agent-lwycv4pt4vd4emwhuiqde3.streamlit.app/`). Jira points at `https://neelsrejan.atlassian.net/jira/projects` (project key `INV`).

`academy/content/bank.py` is the authoring copy. The build shuffles the four choices and writes a salted SHA-256 of the published letter. That hash is a self-study speed bump, not protection. The prose quizzes in `docs/sessions/` are a different set.
