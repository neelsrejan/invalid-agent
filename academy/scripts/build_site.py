#!/usr/bin/env python3
"""Build the static academy pages. Quiz keys are salted hashes, not letters."""
from __future__ import annotations

import base64
import hashlib
import html
import json
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[2]
ACADEMY = ROOT / "academy"
SITE = ACADEMY / "site"
sys.path.insert(0, str(ACADEMY / "content"))

from bank import QUIZZES  # noqa: E402
from course import SESSIONS  # noqa: E402

REPO = "https://github.com/neelsrejan/invalid-agent"
MD = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"], output_format="html5")


def md(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def salt_for(session: int, qid: str) -> str:
    return hashlib.sha256(f"ia-quiz|{session}|{qid}|v1".encode()).hexdigest()[:16]


def answer_hash(salt: str, choice: str) -> str:
    return hashlib.sha256(f"{salt}|{choice}".encode()).hexdigest()


def b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def repo_path(file_field: str, session: int) -> str:
    marker = f"snapshots/session-{session}/"
    text = file_field.replace("\\", "/")
    idx = text.find(marker)
    if idx >= 0:
        return text[idx + len(marker) :]
    return Path(text).name


def load_clips(session: int) -> list[dict]:
    folder = ACADEMY / "narration" / f"session-{session}"
    clips = []
    for script in sorted(folder.glob("*.yaml")):
        spec = yaml.safe_load(script.read_text())
        path = repo_path(spec["file"], session)
        sidecar = ACADEMY / "build" / "videos" / f"session-{session}" / f"{script.stem}.json"
        seconds = None
        if sidecar.exists():
            seconds = json.loads(sidecar.read_text()).get("seconds")
        clips.append(
            {
                "stem": script.stem,
                "title": spec.get("title") or script.stem,
                "path": path,
                "seconds": seconds,
                "src": f"videos/session-{session}/{script.stem}.mp4",
                "blob": f"{REPO}/blob/session-{session}/{path}",
            }
        )
    if not clips:
        raise SystemExit(f"no narration yaml for session {session}")
    return clips


def clock(seconds: float | None) -> str:
    if seconds is None:
        return "duration after render"
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def quiz_payload() -> dict:
    payload = {}
    for session, questions in QUIZZES.items():
        if not 6 <= len(questions) <= 8:
            raise SystemExit(f"session {session} has {len(questions)} questions")
        built = []
        for i, q in enumerate(questions, 1):
            choices = q["choices"]
            if set(choices) != {"a", "b", "c", "d"}:
                raise SystemExit(f"session {session} q{i} choices {set(choices)}")
            if q["correct"] not in choices:
                raise SystemExit(f"session {session} q{i} missing correct")
            qid = f"s{session}q{i}"
            salt = salt_for(session, qid)
            built.append(
                {
                    "id": qid,
                    "prompt": q["prompt"],
                    "choices": [{"id": key, "text": choices[key]} for key in "abcd"],
                    "salt": salt,
                    "answerHash": answer_hash(salt, q["correct"]),
                    "explain": b64(q["explain"]),
                }
            )
        payload[str(session)] = {"passMark": 0.8, "questions": built}
    return payload


def nav(active: int) -> str:
    by_id = {s["id"]: s for s in SESSIONS}
    parts = [
        '<a class="brand" href="index.html"><div class="mark">ia</div><div><strong>invalid-agent</strong><span>Academy</span></div></a>',
        f'<a class="item{" active" if active == 0 else ""}" href="index.html">Home</a>',
    ]
    for week, ids in ((1, (1, 2, 3)), (2, (4, 5, 6)), (3, (7, 8, 9))):
        parts.append(f'<div class="week">Week {week}</div>')
        for n in ids:
            title = html.escape(by_id[n]["title"])
            active_cls = " active" if n == active else ""
            parts.append(
                f'<a class="item{active_cls}" data-session="{n}" href="session-{n}.html">'
                f'<i class="dot"></i>S{n} · {title}</a>'
            )
    parts.append('<div class="nav-foot" id="nav-progress">Progress stays in this browser</div>')
    return "\n".join(parts)


def page(title: str, body: str, *, session: int, page_name: str) -> str:
    lock = ""
    if session > 1:
        lock = f"""
<script>
(function () {{
  var session = {session};
  var ok = false;
  try {{
    var raw = localStorage.getItem("ia-academy-progress-v1");
    var data = raw ? JSON.parse(raw) : null;
    var prev = data && data.sessions && data.sessions[String(session - 1)];
    ok = !!(prev && prev.passed);
  }} catch (e) {{ ok = false; }}
  if (!ok) document.documentElement.classList.add("is-locked");
}})();
</script>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="css/academy.css">
{lock}
</head>
<body data-page="{page_name}" data-session="{session}">
<div class="app">
<aside class="nav">
{nav(session)}
</aside>
<main class="main">
{body}
</main>
</div>
<script src="js/site-config.js"></script>
<script src="js/quiz-data.js"></script>
<script src="js/academy.js"></script>
</body>
</html>
"""


def home_body() -> str:
    cards = []
    for s in SESSIONS:
        cards.append(
            f"""<a class="session-card" data-session="{s['id']}" href="session-{s['id']}.html">
<div class="num">{s['id']:02d}</div>
<div><h3>{html.escape(s['title'])}</h3>
<div class="meta">Week {s['week']} · {html.escape(s['minutes'])} min · {html.escape(s['artifact'])}</div></div>
<div class="pill">Open</div>
</a>"""
        )
    return f"""
<p class="kicker">Field-quality PM · nine git tags</p>
<h1>Learn the invalid-agent, session by session.</h1>
<p class="lede">A simulated investigation, narrated against the code that built it. The language model does not do the arithmetic. You can study this from a locked-down work browser: the pages, the quizzes, and the videos are static files.</p>
<div class="progress-row">
  <div class="ring" data-progress style="--p:0"><span id="ring-label">0/9</span></div>
  <div>
    <strong id="progress-label">0 of 9 sessions passed</strong>
    <div class="bar" data-progress style="--p:0"><i></i></div>
    <p class="note" id="progress-detail">Pass a quiz at 80% or better to open the next session. Retries are unlimited.</p>
    <p class="note" id="lock-note"></p>
  </div>
</div>
<div class="cards">
  <a class="link-card" id="link-github" href="{REPO}"><div class="label">Repository</div><strong>GitHub</strong><p>neelsrejan/invalid-agent. Each session links to its tag.</p></a>
  <a class="link-card" id="link-jira" href="https://neelsrejan.atlassian.net/jira/projects"><div class="label">Jira Cloud</div><strong>Project INV</strong><p>Import docs/jira/backlog.json. The build board is not the investigation sync.</p></a>
  <a class="link-card" id="link-streamlit" href="https://invalid-agent-lwycv4pt4vd4emwhuiqde3.streamlit.app/"><div class="label">Dashboard</div><strong>Streamlit</strong><p>The hosted rules-only dashboard. Community Cloud does not run Ollama.</p></a>
</div>
<h2>How to run it locally</h2>
<div class="panel">
<p>The default path needs no key and no model. Deterministic templates plus the numbers Python already computed.</p>
<pre>python -m pip install -e ".[dev]"
python -m pytest
python -m invalid_agent.graph --scenario bad_lot --week 4
streamlit run streamlit_app.py</pre>
<p>When you want a local model, Ollama serves Meta Llama 3.1 8B. The smaller tag for a laptop demo is Llama 3.2 1B. Hosted Streamlit Community Cloud stays rules-only, because Cloud has no Ollama.</p>
<pre>ollama pull llama3.1:8b
LLM_BACKEND=ollama LLM_MODEL=llama3.1:8b python -m invalid_agent.graph --scenario bad_lot --week 0

ollama pull llama3.2:1b
LLM_MODEL=llama3.2:1b</pre>
<p class="note">Practice edits stay on a branch you create from the session tag. Do not merge them into main.</p>
</div>
<h2>Sessions</h2>
<div class="session-grid">
{''.join(cards)}
</div>
<h2>Move progress between computers</h2>
<div class="panel">
<p>Quiz scores live in this browser's localStorage. Export a code, and paste it on the other machine. The code is a checksummed copy of your scores, not an account.</p>
<div class="row">
  <button type="button" id="export-btn">Export progress</button>
  <button type="button" class="secondary" id="reset-btn">Clear this browser</button>
</div>
<textarea id="export-code" rows="3" readonly placeholder="Your code appears here"></textarea>
<label for="import-code">Paste a code from your other computer</label>
<textarea id="import-code" rows="3" placeholder="IA1...."></textarea>
<div class="row"><button type="button" id="import-btn">Import progress</button></div>
<p class="note" id="transfer-msg"></p>
</div>
"""


def session_body(session: dict, clips: list[dict]) -> str:
    n = session["id"]
    reads = "".join(f"<li>{html.escape(item)}</li>" for item in session["read"])
    clip_html = []
    for i, clip in enumerate(clips, 1):
        clip_html.append(
            f"""<article class="clip">
<h3>{i}. {html.escape(clip['title'])}</h3>
<video controls preload="metadata" src="{html.escape(clip['src'])}">
<a href="{html.escape(clip['src'])}">Download clip {i}</a>
</video>
<p class="meta">{clock(clip['seconds'])} · Andrew · <a href="{html.escape(clip['blob'])}">{html.escape(clip['path'])}</a> at <code>session-{n}</code></p>
</article>"""
        )
    files = []
    seen = set()
    for clip in clips:
        if clip["path"] in seen:
            continue
        seen.add(clip["path"])
        files.append(f'<li><a href="{html.escape(clip["blob"])}"><code>{html.escape(clip["path"])}</code></a></li>')
    trace_path = ROOT / "docs" / "sessions" / f"session-{n}" / "LOGIC_TRACE.md"
    trace = md(trace_path.read_text())
    practice = md(session["practice"])
    tree = f"{REPO}/tree/session-{n}"
    trace_blob = f"{REPO}/blob/session-{n}/docs/sessions/session-{n}/LOGIC_TRACE.md"
    return f"""
<p class="kicker">Week {session['week']} · Session {n} · tag session-{n}</p>
<h1>{html.escape(session['title'])}</h1>
<p class="lede">{html.escape(session['blurb'])}</p>
<p class="note">Ticket {html.escape(session['ticket'])} · about {html.escape(session['minutes'])} minutes · artifact: {html.escape(session['artifact'])}</p>
<div class="lock-screen">
  <div class="panel">
    <h2>This session is locked</h2>
    <p>Pass Session {n - 1} at 80% or better to open the videos, the logic trace, the practice task, and this quiz. Retries on the earlier quiz are unlimited. If you already passed it on another computer, import that progress code from the home page.</p>
    <p><a class="button" href="session-{n - 1}.html">Go to Session {n - 1}</a> <a class="button secondary" href="index.html">Home</a></p>
  </div>
</div>
<div class="lesson">
<h2>Read first</h2>
<ul>{reads}</ul>
<h2>Watch in this order</h2>
<p class="note">Pause whenever you want. The line numbers match tag <code>session-{n}</code>, not whatever main looks like today.</p>
{''.join(clip_html)}
<h2>Logic trace</h2>
<p class="note"><a href="{html.escape(trace_blob)}">LOGIC_TRACE.md at session-{n}</a></p>
<div class="prose">{trace}</div>
<h2>Code at this tag</h2>
<p><a href="{tree}">Browse the whole tree for session-{n}</a></p>
<ul>{''.join(files)}</ul>
<h2>Practice, on a private branch</h2>
<div class="prose">{practice}</div>
<h2>Quiz</h2>
<p class="note">Eight questions. 80% to pass, which means 7 of 8. Explanations show after you submit. The answer key is not stored as letters in this page.</p>
<div id="quiz"></div>
</div>
"""


def main() -> None:
    if len(QUIZZES) != 9:
        raise SystemExit("expected 9 quizzes")
    payload = quiz_payload()
    blob = json.dumps(payload, ensure_ascii=False, indent=2)
    for forbidden in ('"correct"', '"answer":', "Qwen", "qwen"):
        if forbidden in blob:
            raise SystemExit(f"quiz payload contains {forbidden}")
    # The correct letter must not appear as its own field. Spot-check a hash.
    sample = payload["1"]["questions"][0]
    if answer_hash(sample["salt"], "a") != sample["answerHash"]:
        raise SystemExit("hash mismatch on session 1 question 1")
    (SITE / "js").mkdir(parents=True, exist_ok=True)
    (SITE / "js" / "quiz-data.js").write_text("window.QUIZZES = " + blob + ";\n")
    (SITE / "index.html").write_text(page("invalid-agent Academy", home_body(), session=0, page_name="home"))
    (SITE / ".nojekyll").write_text("")
    for session in SESSIONS:
        clips = load_clips(session["id"])
        body = session_body(session, clips)
        (SITE / f"session-{session['id']}.html").write_text(
            page(f"Session {session['id']} · {session['title']}", body, session=session["id"], page_name="session")
        )
        print(f"session {session['id']}: {len(clips)} clips")
    print("wrote", SITE)


if __name__ == "__main__":
    main()
