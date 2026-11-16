#!/usr/bin/env python3
"""Build the static academy pages. Quiz keys are salted hashes, not letters."""
from __future__ import annotations

import base64
import hashlib
import html
import json
import random
import sys
from collections import Counter
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[2]
ACADEMY = ROOT / "academy"
SITE = ACADEMY / "site"
sys.path.insert(0, str(ACADEMY))
sys.path.insert(0, str(ACADEMY / "content"))

from bank import QUIZZES  # noqa: E402
from course import SESSIONS  # noqa: E402
from pin import PIN_SHORT, PIN_TAG, assert_tag  # noqa: E402
from quiz_checks import assert_guessers, assert_uniform_options  # noqa: E402

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


def clip_overview(spec: dict) -> str:
    overview = spec.get("overview") or ""
    if isinstance(overview, dict):
        overview = overview.get("say") or overview.get("text") or ""
    text = " ".join(str(overview).split())
    if len(text) < 40:
        raise SystemExit("clip is missing an architecture overview")
    return text


def load_clips(session: int) -> list[dict]:
    folder = ACADEMY / "narration" / f"session-{session}"
    clips = []
    for script in sorted(folder.glob("*.yaml")):
        spec = yaml.safe_load(script.read_text())
        raw = str(spec["file"]).replace("\\", "/")
        path = repo_path(raw, session) if "snapshots/" in raw else raw
        spans = []
        for segment in spec.get("segments") or []:
            start_s, end_s = str(segment["lines"]).split("-", 1)
            spans.append((int(start_s), int(end_s)))
        if not spans:
            raise SystemExit(f"{script.name} has no line ranges")
        line_start = min(start for start, _end in spans)
        line_end = max(end for _start, end in spans)
        seconds = clip_seconds(session, script.stem)
        clips.append(
            {
                "stem": script.stem,
                "title": spec.get("title") or script.stem,
                "overview": clip_overview(spec),
                "path": path,
                "seconds": seconds,
                "src": f"videos/session-{session}/{script.stem}.mp4",
                "blob": f"{REPO}/blob/{PIN_TAG}/{path}#L{line_start}-L{line_end}",
            }
        )
    if not clips:
        raise SystemExit(f"no narration yaml for session {session}")
    return clips


def clip_seconds(session: int, stem: str):
    """Durations are committed so a rebuild matches without the MP4s present."""
    manifest = ACADEMY / "content" / "durations.json"
    key = f"session-{session}/{stem}"
    if manifest.exists():
        data = json.loads(manifest.read_text())
        if key in data:
            return data[key]
    sidecar = ACADEMY / "build" / "videos" / f"session-{session}" / f"{stem}.json"
    if sidecar.exists():
        return json.loads(sidecar.read_text()).get("seconds")
    return None


def clock(seconds: float | None) -> str:
    if seconds is None:
        return "duration after render"
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def published_choices(q: dict, salt: str) -> tuple[dict[str, str], str]:
    """Shuffle the four texts with a fixed seed and relabel them a–d.

    The letter in bank.py is only the authoring key. The page letter is the
    one assigned here, and that is what gets hashed.
    """
    correct_text = q["choices"][q["correct"]]
    texts = [q["choices"][key] for key in "abcd"]
    random.Random(salt).shuffle(texts)
    labeled = {letter: texts[i] for i, letter in enumerate("abcd")}
    published = next(letter for letter, text in labeled.items() if text == correct_text)
    return labeled, published


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
            labeled, published = published_choices(q, salt)
            built.append(
                {
                    "id": qid,
                    "prompt": q["prompt"],
                    "choices": [{"id": key, "text": labeled[key]} for key in "abcd"],
                    "salt": salt,
                    "answerHash": answer_hash(salt, published),
                    "explain": b64(q["why"]),
                }
            )
        payload[str(session)] = {"passMark": 0.8, "questions": built}
    return payload


def graded_items(payload: dict) -> list[dict]:
    """Questions as the page shows them, with the letter the hash actually accepts."""
    items = []
    for session, pack in payload.items():
        for question in pack["questions"]:
            winner = None
            for choice in question["choices"]:
                if answer_hash(question["salt"], choice["id"]) == question["answerHash"]:
                    if winner is not None:
                        raise SystemExit(f"{question['id']} hashes to two letters")
                    winner = choice
            if winner is None:
                raise SystemExit(f"{question['id']} hash matches no choice")
            items.append(
                {
                    "session": int(session),
                    "prompt": question["prompt"],
                    "choices": question["choices"],
                    "correct": winner["id"],
                }
            )
    return items


def nav(active: int) -> str:
    by_id = {s["id"]: s for s in SESSIONS}
    parts = [
        '<a class="brand" href="index.html"><div class="mark">ia</div><div><strong>invalid-agent</strong><span>Academy</span></div></a>',
        f'<a class="item{" active" if active == 0 else ""}" href="index.html">Home</a>',
        f'<a class="item{" active" if active == -1 else ""}" href="architecture.html">Architecture</a>',
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


def page(title: str, body: str, *, session: int, page_name: str, active: int | None = None) -> str:
    nav_active = session if active is None else active
    lock = ""
    if session > 1:
        lock = f"""
<script>
(function () {{
  var session = {session};
  var ok = false;
  try {{
    var raw = localStorage.getItem("ia-academy-progress-v2");
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
{nav(nav_active)}
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
<p class="kicker">Field-quality simulation · nine sessions · synthetic data</p>
<h1>Learn the invalid-agent, session by session.</h1>
<p class="lede">A customer complaint on a fictional molecular panel, narrated against the code that investigates it. Rates are computed in Python. The model, when one is connected, only narrates. The pages, the quizzes, and the videos are static files.</p>
<div class="progress-row">
  <div class="ring" data-progress style="--p:0"><span id="ring-label">0/9</span></div>
  <div>
    <strong id="progress-label">0 of 9 sessions passed</strong>
    <div class="bar" data-progress style="--p:0"><i></i></div>
    <p class="note" id="progress-detail">Pass a quiz at 80% or better (7 of 8) to open the next session. Retries are unlimited.</p>
    <p class="note" id="lock-note"></p>
  </div>
</div>
<div class="cards">
  <a class="link-card" id="link-github" href="{REPO}"><div class="label">Repository</div><strong>GitHub</strong><p>neelsrejan/invalid-agent. Clips cite <code>{PIN_TAG}</code> ({PIN_SHORT}).</p></a>
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
<p class="note">Practice notes stay on a branch you create. Do not merge them into main.</p>
</div>
<p class="note">The system map is on the <a href="architecture.html">architecture</a> page. Each session is a short summary, an architecture note before each clip, and a quiz on the boundaries.</p>
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
<textarea id="import-code" rows="3" placeholder="IA2...."></textarea>
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
<div class="overview"><h4>Architecture</h4><p>{html.escape(clip['overview'])}</p></div>
<video controls preload="metadata" src="{html.escape(clip['src'])}">
<a href="{html.escape(clip['src'])}">Download clip {i}</a>
</video>
<p class="meta">{clock(clip['seconds'])} · Andrew · <a href="{html.escape(clip['blob'])}">{html.escape(clip['path'])}</a> at <code>{PIN_TAG}</code> (<code>{PIN_SHORT}</code>)</p>
</article>"""
        )
    files = []
    seen = set()
    for clip in clips:
        if clip["path"] in seen:
            continue
        seen.add(clip["path"])
        files.append(f'<li><a href="{html.escape(clip["blob"])}"><code>{html.escape(clip["path"])}</code></a></li>')
    trace = md(session["trace"])
    practice = md(session["practice"])
    tree = f"{REPO}/tree/{PIN_TAG}"
    trace_blob = f"{REPO}/blob/{PIN_TAG}/docs/sessions/session-{n}/LOGIC_TRACE.md"
    lock = ""
    if n > 1:
        lock = f"""
<div class="lock-screen">
  <div class="panel">
    <h2>This session is locked</h2>
    <p>Pass Session {n - 1} at 80% or better (7 of 8) to open the videos and this quiz. Retries on the earlier quiz are unlimited. If you already passed it on another computer, import that progress code from the home page.</p>
    <p><a class="button" href="session-{n - 1}.html">Go to Session {n - 1}</a> <a class="button secondary" href="index.html">Home</a></p>
  </div>
</div>"""
    return f"""
<p class="kicker">Week {session['week']} · Session {n}</p>
<h1>{html.escape(session['title'])}</h1>
<p class="lede">{html.escape(session['blurb'])}</p>
<p class="note">Ticket {html.escape(session['ticket'])} · about {html.escape(session['minutes'])} minutes · artifact: {html.escape(session['artifact'])}</p>
{lock}
<div class="lesson">
<h2>Read first</h2>
<ul>{reads}</ul>
<h2>Watch in this order</h2>
<p class="note">Read the architecture note, then play the clip. The note says what the file is for. The video opens on that note, then walks a few ranges. Line numbers match <code>{PIN_TAG}</code> (<code>{PIN_SHORT}</code>).</p>
{''.join(clip_html)}
<h2>How this session connects</h2>
<div class="prose">{trace}</div>
<p class="note">The build diary is <a href="{html.escape(trace_blob)}">LOGIC_TRACE.md</a> at <code>{PIN_TAG}</code>. The clips walk that same commit, not whatever main is today.</p>
<h2>Code on main</h2>
<p><a href="{tree}">Browse the repository</a></p>
<ul>{''.join(files)}</ul>
<h2>Practice</h2>
<div class="prose">{practice}</div>
<h2>Quiz</h2>
<p class="note">Eight questions on architecture and design. 7 of 8 to pass. Explanations show after you submit. The salted hash is a self-study speed bump, not protection.</p>
<div id="quiz"></div>
</div>
"""


def write_answer_key(payload: dict) -> None:
    """Author key for the letters the built site actually grades. Not copied to Pages."""
    lines = [
        "# Academy quiz letters",
        "",
        "These are the letters after `build_site.py` shuffles each question.",
        "The salted hash on the page is a self-study speed bump, not protection.",
        "Reading this file, or trying all four choices, bypasses it.",
        "The prose quizzes in `docs/sessions/` are a separate set and are not these letters.",
        "",
    ]
    for session in range(1, 10):
        lines.append(f"## Session {session}")
        lines.append("")
        for index, question in enumerate(payload[str(session)]["questions"], 1):
            winner = next(
                choice
                for choice in question["choices"]
                if answer_hash(question["salt"], choice["id"]) == question["answerHash"]
            )
            lines.append(f"{index}. **{winner['id'].upper()}.** {winner['text']}")
            lines.append("")
    (ACADEMY / "content" / "QUIZ_ANSWERS.md").write_text("\n".join(lines))


def architecture_body() -> str:
    stages = [
        ("Scenario YAML", "The cause, the calendar, and the injections. The printed invalid rate is not stored here."),
        ("Seeded generator", "One seed produces one field file. The same YAML always yields the same rows."),
        ("Metrics in Python", "Rate, Wilson interval, chi-square, p-chart, Pareto, hypothesis score, cost, and the projection are code."),
        ("One case graph", "Triage once, then plan, the quality record, and a status note until the requested week. Week 4 continues into close-out."),
        ("Numeric-fidelity guard", "Prose may be rewritten. A number that is not already in the facts is rejected, and the template replaces that draft."),
        ("Optional narrator", "The default backend is deterministic. Local Ollama uses Llama 3.1 8B. Hosted Streamlit stays rules-only, because Community Cloud has no Ollama."),
        ("Artifacts", "Memo, fishbone, 5 Whys, 8D/CAPA, Gantt, risk register, three audience notes, the Streamlit page, and a seven-slide deck."),
        ("Optional Jira", "All three secrets, or a JSON file of SIM keys and no socket. That file is not the build backlog in docs/jira/backlog.json."),
    ]
    cards = "".join(
        f'<article class="stage"><strong>{html.escape(title)}</strong><p>{html.escape(text)}</p></article>'
        for title, text in stages
    )
    return f"""
<p class="kicker">How a case moves</p>
<h1>Architecture</h1>
<p class="lede">A simulated field-quality investigation. The language model does not calculate. The dataframe is not stored on the graph state. Each node regenerates it from the scenario seed.</p>
<div class="stages">
{cards}
</div>
<h2>What stays out</h2>
<div class="panel">
<ul>
<li>The panel, the customers, and the field file are synthetic. This is not a medical device and not for clinical use.</li>
<li>No agent swarm, no fine-tune, and no vector database. The status color is red, amber, or green. It is not retrieval.</li>
<li>The projection clears the leading stratum on a copy of the same file. It is not observed follow-up, and the walkthrough file does not turn green.</li>
<li>The build board is project INV. The investigation dry-run uses SIM keys. Those are different files.</li>
</ul>
</div>
<h2>Where to look</h2>
<div class="cards">
  <a class="link-card" href="{REPO}/tree/{PIN_TAG}"><div class="label">Repository</div><strong>GitHub</strong><p>The clips cite <code>{PIN_TAG}</code> ({PIN_SHORT}).</p></a>
  <a class="link-card" href="https://neelsrejan.atlassian.net/jira/projects"><div class="label">Jira Cloud</div><strong>Project INV</strong><p>Import docs/jira/backlog.json. The build board is not the investigation sync.</p></a>
  <a class="link-card" href="https://invalid-agent-lwycv4pt4vd4emwhuiqde3.streamlit.app/"><div class="label">Dashboard</div><strong>Streamlit</strong><p>The hosted rules-only dashboard. Community Cloud does not run Ollama.</p></a>
</div>
"""


def main() -> None:
    assert_tag()
    if len(QUIZZES) != 9:
        raise SystemExit("expected 9 quizzes")
    payload = quiz_payload()
    blob = json.dumps(payload, ensure_ascii=False, indent=2)
    for forbidden in ('"correct"', '"answer":', "Qwen", "qwen"):
        if forbidden in blob:
            raise SystemExit(f"quiz payload contains {forbidden}")
    items = graded_items(payload)
    assert_uniform_options(items)
    expected = assert_guessers(items)
    letters: Counter = Counter(item["correct"] for item in items)
    n = len(items)
    for letter, count in sorted(letters.items()):
        if count / n > 0.40:
            raise SystemExit(f"letter {letter} is {count}/{n} answers, over 40%")
        print(f"letter {letter}: {count}/{n}")
    for name, by_session in expected.items():
        bits = " ".join(f"s{session}={by_session[session]:.1%}" for session in range(1, 10))
        print(f"guesser {name}: {bits}")
    # Spot-check session 1 question 1 against the shuffled letter, not a fixed "a".
    sample = payload["1"]["questions"][0]
    _labeled, published = published_choices(QUIZZES[1][0], sample["salt"])
    if answer_hash(sample["salt"], published) != sample["answerHash"]:
        raise SystemExit("hash mismatch on session 1 question 1")
    write_answer_key(payload)
    (SITE / "js").mkdir(parents=True, exist_ok=True)
    (SITE / "js" / "quiz-data.js").write_text("window.QUIZZES = " + blob + ";\n")
    (SITE / "index.html").write_text(page("invalid-agent Academy", home_body(), session=0, page_name="home"))
    (SITE / "architecture.html").write_text(
        page("Architecture · invalid-agent Academy", architecture_body(), session=0, page_name="architecture", active=-1)
    )
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
