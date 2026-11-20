"""Invalid Bot dashboard.

The guided walk is Week 1 through Week 4. Each week is complaint, numbers,
charts, what gets logged, root-cause notes, and a wrap-up. The next week
unlocks only after the wrap-up. Python computes every number. A language
model, when one is on, may only rephrase the talk-back reply.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pandas as pd
import streamlit as st

from invalid_agent.artifacts.charts import before_after_figure, p_chart_figure, pareto_figure
from invalid_agent.config import find_repo_root, load_settings
from invalid_agent.data.frame import DataUnavailable, load_frame
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.guide import AUDIENCES, GUIDE_STEPS, progress_label
from invalid_agent.ui.plain import PRACTICE_BANNER, PUBLIC_BANNER, plain_case_label, with_gloss
from invalid_agent.ui.story import beat_lines, build_week_view
from invalid_agent.ui.talkback import example_prompts, respond, reword_reply

ROOT = find_repo_root()

# Widget keys Streamlit drops when the widget is not on the current screen.
# Re-assigning them before any widget is created keeps the value.
_KEPT_KEYS = (
    "scenario_id",
    "story_week",
    "beat",
    "unlocked_week",
    "finished",
    "locked_case",
    "stratum",
    "stratum_for_week",
    "audience",
    "rules_only",
    "week_insights",
    "open_items",
    "insight_serial",
    "flag_serial",
    "last_reply",
    "talk_text",
    "deck_bytes",
)


def _apply_streamlit_secrets() -> None:
    """Copy Streamlit secrets into the environment. Existing env vars win."""
    try:
        secrets = st.secrets
    except Exception:
        return
    names = (
        "OPENFDA_API_KEY",
        "DATABASE_URL",
        "DATABASE_URL_READONLY",
        "DEMO_READONLY_PASSWORD",
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "LLM_BACKEND",
        "LLM_MODEL",
        "DATA_BACKEND",
        "JIRA_BASE_URL",
        "JIRA_EMAIL",
        "JIRA_API_TOKEN",
        "JIRA_PROJECT_KEY",
        "OLLAMA_HOST",
        "MANUFACTURER_DISPLAY",
    )
    for name in names:
        try:
            value = secrets[name]
        except Exception:
            continue
        if value and not os.environ.get(name):
            os.environ[name] = str(value)


def _scenarios(public: bool) -> list[Path]:
    synthetic = sorted((ROOT / "scenarios").glob("*.yaml"))
    hosted = [ROOT / "cases" / "openfda_ooi.yaml", ROOT / "cases" / "openfda_jje.yaml"]
    hosted = [path for path in hosted if path.is_file()]
    if public:
        return hosted
    return synthetic + hosted


def _init_state(ids: list[str]) -> None:
    for key in _KEPT_KEYS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
    if st.session_state.get("scenario_id") not in ids:
        st.session_state.scenario_id = ids[0]
    if "story_week" not in st.session_state:
        st.session_state.story_week = 1
    if "beat" not in st.session_state:
        st.session_state.beat = 0
    if "unlocked_week" not in st.session_state:
        st.session_state.unlocked_week = 1
    if "finished" not in st.session_state:
        st.session_state.finished = False
    if not isinstance(st.session_state.get("week_insights"), dict):
        st.session_state.week_insights = {1: [], 2: [], 3: [], 4: []}
    for week in (1, 2, 3, 4):
        st.session_state.week_insights.setdefault(week, [])
    if not isinstance(st.session_state.get("open_items"), list):
        st.session_state.open_items = []
    if "insight_serial" not in st.session_state:
        st.session_state.insight_serial = 0
    if "flag_serial" not in st.session_state:
        st.session_state.flag_serial = 0
    if "audience" not in st.session_state:
        st.session_state.audience = "customer"
    st.session_state.unlocked_week = min(4, max(1, int(st.session_state.unlocked_week)))
    st.session_state.story_week = min(
        st.session_state.unlocked_week,
        max(1, int(st.session_state.story_week)),
    )
    st.session_state.beat = min(len(GUIDE_STEPS) - 1, max(0, int(st.session_state.beat)))
    current = st.session_state.scenario_id
    previous = st.session_state.get("locked_case")
    if previous and previous != current:
        st.session_state.story_week = 1
        st.session_state.beat = 0
        st.session_state.unlocked_week = 1
        st.session_state.finished = False
        st.session_state.week_insights = {1: [], 2: [], 3: [], 4: []}
        st.session_state.open_items = []
        st.session_state.insight_serial = 0
        st.session_state.flag_serial = 0
        st.session_state.last_reply = None
        st.session_state.stratum_for_week = None
        st.session_state.deck_bytes = None
    st.session_state.locked_case = current


def _page_chrome(banner: str) -> None:
    st.set_page_config(page_title="Invalid Bot", layout="wide")
    st.markdown(
        """
        <style>
          header[data-testid="stHeader"] { position: static !important; }
          [data-testid="stToolbar"] { position: static !important; }
          .block-container { padding-top: 1.4rem !important; padding-bottom: 2.5rem; }
          div[data-testid="stMetric"] { position: static !important; top: auto !important; }
          div[data-testid="stHorizontalBlock"] { position: static !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    safe = (
        banner.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    st.html(
        '<div style="background:#0B3A5B;color:#FFFFFF;padding:16px 18px;'
        'border-radius:6px;margin-top:8px;">'
        '<p style="margin:0;color:#FFFFFF;font-size:16px;line-height:1.5;'
        "font-family:sans-serif;font-weight:500;white-space:normal;\">"
        f"{safe}</p></div>"
    )
    st.title("Invalid Bot")
    st.caption(
        "The promise is at least 98% valid tests, so invalid results stay at or below 2%. "
        "Python does every count. A language model, if one is on, only rephrases words."
    )


def _backend_caption(rules_only: bool) -> None:
    if rules_only:
        st.caption("Fixed wording is on. Python still does the math. No language model is called.")
    else:
        st.caption(
            "Groq (a free language-model host) may rephrase a reply. "
            "Python still computes every number. If the model fails, you still get the plain reply."
        )


@st.cache_data(show_spinner=False)
def _week_view(scenario_path: str, story_week: int) -> dict:
    scenario = load_scenario(scenario_path)
    frame = load_frame(scenario)
    return build_week_view(scenario, frame, story_week)


def _talk_llm(rules_only: bool):
    if rules_only:
        return None
    try:
        from invalid_agent.llm import get_llm

        llm = get_llm()
    except Exception:
        return None
    if getattr(llm, "name", "deterministic") == "deterministic":
        return None
    return llm


def _apply_talk(message: str, view: dict, beat_id: str, week: int, rules_only: bool) -> None:
    plan_count = int(view.get("plan_ticket_count") or 0)
    ticket_key = f"INV-{plan_count + int(st.session_state.insight_serial) + 1}"
    flag_key = f"Flag {int(st.session_state.flag_serial) + 1}"
    reply = respond(message, view, beat_id, ticket_key=ticket_key, flag_key=flag_key)
    if reply["log_kind"] == "ticket" and reply.get("bullet"):
        st.session_state.insight_serial = int(st.session_state.insight_serial) + 1
        st.session_state.week_insights.setdefault(week, []).append(reply["bullet"])
        st.session_state.open_items.append(
            {"week": week, "key": reply["log_key"], "text": reply["bullet"], "kind": "ticket"}
        )
    elif reply["log_kind"] == "flag":
        st.session_state.flag_serial = int(st.session_state.flag_serial) + 1
        st.session_state.open_items.append(
            {"week": week, "key": reply["log_key"], "text": reply["log_text"], "kind": "flag"}
        )
    shown = reword_reply(reply["text"], _talk_llm(rules_only))
    st.session_state.last_reply = {
        "week": week,
        "beat": beat_id,
        "user_text": reply.get("user_text") or "",
        "text": shown,
    }


def _render_lines(lines: list[str]) -> None:
    for line in lines:
        if line.startswith("### "):
            st.subheader(line[4:])
        else:
            st.markdown(line)


def _render_carried(week: int) -> None:
    if week <= 1:
        return
    carried = [item for item in st.session_state.open_items if int(item["week"]) < week]
    if not carried:
        return
    st.subheader("Still open from earlier weeks")
    for item in carried:
        st.markdown(f"- {item['key']}: {item['text']}")


def _render_insights(week: int) -> None:
    st.subheader(f"Week {week} insights")
    bullets = list(st.session_state.week_insights.get(week) or [])
    if not bullets:
        st.markdown("No confirmed insight yet. Tell the agent what you see. A confirmed insight will land here.")
        return
    for bullet in bullets:
        st.markdown(f"- {bullet}")


def _render_talk(view: dict, beat_id: str, week: int, rules_only: bool) -> None:
    st.subheader("Talk to the agent")
    st.caption("Type a question, or type what you think is going on. The reply uses this week's counts.")
    st.text_input("Your question or insight", key="talk_text")
    if st.button("Tell the agent", key="talk-send"):
        _apply_talk(str(st.session_state.get("talk_text") or ""), view, beat_id, week, rules_only)
        st.rerun()
    prompts = example_prompts(view, beat_id if beat_id != "done" else "wrap")
    st.caption("Or try one of these.")
    for index, prompt in enumerate(prompts):
        if st.button(prompt, key=f"ex-{beat_id}-{index}"):
            _apply_talk(prompt, view, beat_id, week, rules_only)
            st.rerun()
    last = st.session_state.get("last_reply") or {}
    if last and int(last.get("week") or 0) == week and str(last.get("beat") or "") == beat_id:
        if last.get("user_text"):
            st.markdown("**You said.** " + with_gloss(str(last["user_text"])))
        st.markdown(str(last.get("text") or ""))


def _render_metrics(view: dict) -> None:
    label = "Invalid rate" if view["estimable"] else "Share of reports"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label, view["rate_label"])
    c2.metric("Count", view["count_label"])
    c3.metric("Likely range", view["range_label"])
    c4.metric("This week's call", view["call_label"])


def _render_charts(view: dict, week: int) -> None:
    st.plotly_chart(p_chart_figure(view["chart"], title="Weekly invalid rate"), width="stretch")
    if view["pareto"]:
        st.plotly_chart(pareto_figure(view["pareto"]), width="stretch")
    else:
        st.info("This week's slice has no invalids, so there is no ranking to draw.")
    breaks = view["breaks"]
    columns = list(breaks)
    if not columns:
        return
    if st.session_state.get("stratum_for_week") != week or st.session_state.get("stratum") not in columns:
        st.session_state.stratum = view["default_break"] or columns[0]
        st.session_state.stratum_for_week = week
    st.selectbox(
        "Break the file by",
        columns,
        key="stratum",
        format_func=lambda column: breaks[column]["label"],
    )
    chosen = breaks[st.session_state.stratum]
    rows = chosen["rows"]
    if rows:
        st.dataframe(pd.DataFrame(rows)[["level", "n", "k", "rate_label"]], width="stretch", hide_index=True)
    else:
        st.info("Every row in this break is blank, so there is nothing to rank. A blank is not a cause.")


def _render_tickets(view: dict) -> None:
    rows = view["tickets"]
    if not rows:
        st.info("This week has no plan ticket yet.")
        return
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _render_notes(view: dict) -> None:
    st.radio(
        "Who is this note for?",
        [value for value, _label in AUDIENCES],
        key="audience",
        horizontal=True,
        format_func=lambda value: dict(AUDIENCES)[value],
    )
    st.markdown(view["notes"][st.session_state.audience])


def _render_wrap_chart(view: dict) -> None:
    if view.get("projection_applied") and view.get("after_chart"):
        st.plotly_chart(before_after_figure(view["chart"], view["after_chart"]), width="stretch")


def _offer_deck(view: dict, scenario: dict) -> None:
    if int(view["story_week"]) < 4:
        return
    st.caption("The seven-slide deck is exec_deck.pptx. It uses the same numbers as this wrap-up.")
    if st.button("Prepare the slide file", key="prepare-deck"):
        st.session_state.deck_bytes = _deck_bytes(view, scenario)
        st.rerun()
    payload = st.session_state.get("deck_bytes")
    if payload:
        st.download_button(
            "Download the deck",
            data=payload,
            file_name="exec_deck.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            key="download-deck",
        )


def _deck_bytes(view: dict, scenario: dict) -> bytes | None:
    from invalid_agent.artifacts.deck import write_deck

    facts = {
        "scenario_id": str(scenario.get("id") or "case"),
        "device": str(scenario.get("device") or "device"),
        "banner": "Practice data. Not for clinical use. Not a medical device.",
        "rate_pct": float(view["rate"]) * 100.0,
        "k": int(view["k"]),
        "n": int(view["n"]),
        "ci_low_pct": float(view["ci_low"]) * 100.0,
        "ci_high_pct": float(view["ci_high"]) * 100.0,
        "spec_pct": float(scenario.get("spec_invalid_rate", 0.02)) * 100.0,
        "promised_pct": float(scenario.get("promised_validity", 0.98)) * 100.0,
        "cause": str(view.get("cause") or "no_single_cause"),
        "level": str(view.get("level") or "the leading group"),
        "category": "Leading group" if view.get("single") else "Unresolved",
        "recommendation": str(view.get("decision") or ""),
        "after_pct": float(view.get("after_rate") or 0.0) * 100.0,
        "label": str(view.get("projection_sentence") or ""),
        "single": bool(view.get("single")),
        "cost": int(view.get("cost") or 0),
        "unit": int(view.get("unit") or 0),
        "d7": str(view.get("decision") or ""),
        "chart": view.get("chart"),
    }
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "exec_deck.pptx"
            write_deck(path, facts)
            return path.read_bytes()
    except Exception:
        return None


def _nav(week: int, beat: int, finished: bool) -> None:
    back, forward = st.columns(2)
    with back:
        if st.button("Back", key="back", disabled=beat == 0 and week == 1 and not finished):
            if finished:
                st.session_state.finished = False
            elif beat > 0:
                st.session_state.beat = beat - 1
            elif week > 1:
                st.session_state.story_week = week - 1
                st.session_state.beat = len(GUIDE_STEPS) - 1
            st.rerun()
    with forward:
        if finished:
            return
        step = GUIDE_STEPS[beat]
        if beat < len(GUIDE_STEPS) - 1:
            label = step.next_label
        elif week < 4:
            label = f"Start week {week + 1}"
        else:
            label = "Finish the story"
        if st.button(label, key="next", type="primary"):
            if beat < len(GUIDE_STEPS) - 1:
                st.session_state.beat = beat + 1
            elif week < 4:
                st.session_state.story_week = week + 1
                st.session_state.beat = 0
                st.session_state.unlocked_week = max(int(st.session_state.unlocked_week), week + 1)
            else:
                st.session_state.finished = True
            st.rerun()


def _render_case_picker(rows: list[tuple[Path, dict, str]]) -> None:
    ids = [str(scenario.get("id")) for _path, scenario, _label in rows]
    labels = {str(scenario.get("id")): label for _path, scenario, label in rows}
    st.selectbox(
        "Which case",
        ids,
        key="scenario_id",
        format_func=lambda case_id: plain_case_label(labels.get(case_id, case_id)),
    )


def _render_guided(rows: list[tuple[Path, dict, str]], rules_only: bool) -> None:
    by_id = {str(scenario.get("id")): (path, scenario) for path, scenario, _label in rows}
    scenario_path, scenario = by_id[st.session_state.scenario_id]
    week = int(st.session_state.story_week)
    beat = int(st.session_state.beat)
    finished = bool(st.session_state.finished)
    try:
        view = _week_view(str(scenario_path), week)
    except DataUnavailable:
        st.error(
            "The public report table is not connected, so this case cannot load. "
            "Pick a practice case. This page does not show a connection string."
        )
        st.stop()

    if finished:
        st.subheader("You finished the four weeks")
        st.markdown(
            "You walked week 1 through week 4. "
            "Open tickets and flags from earlier weeks are still listed above the wrap-up if you go back."
        )
        _render_carried(week)
        _render_talk(view, "done", week, rules_only)
        _render_insights(week)
        _nav(week, beat, True)
        return

    step = GUIDE_STEPS[beat]
    trail = []
    for position, item in enumerate(GUIDE_STEPS):
        label = item.short
        if position == beat:
            label = f"**{label}**"
        trail.append(label)
    st.caption(" · ".join(trail))
    st.subheader(f"{progress_label(week, beat)} — {step.title}")
    st.markdown(f"**What the agent is doing.** {step.doing}")
    st.markdown(f"**Why.** {step.why}")
    st.markdown(f"**What to look at.** {step.look}")
    if week == 1 and beat == 0:
        _render_case_picker(rows)
        view = _week_view(str(by_id[st.session_state.scenario_id][0]), week)
        scenario = by_id[st.session_state.scenario_id][1]
    _render_carried(week)
    _render_lines(beat_lines(view, step.id))
    if step.id == "data":
        _render_metrics(view)
    elif step.id == "charts":
        _render_charts(view, week)
    elif step.id == "logged":
        _render_tickets(view)
    elif step.id == "notes":
        _render_notes(view)
    elif step.id == "wrap":
        _render_wrap_chart(view)
        _offer_deck(view, scenario)
    _render_talk(view, step.id, week, rules_only)
    _render_insights(week)
    _nav(week, beat, False)


def main() -> None:
    from invalid_agent.config import load_dotenv

    load_dotenv()
    _apply_streamlit_secrets()
    settings = load_settings()
    public = settings.data_backend == "openfda"
    _page_chrome(PUBLIC_BANNER if public else PRACTICE_BANNER)

    files = _scenarios(public)
    if not files:
        st.error("No case files were found.")
        st.stop()
    rows = []
    for path in files:
        scenario = load_scenario(path)
        rows.append((path, scenario, f"{scenario.get('id')} — {scenario.get('title', '')}"))
    _init_state([str(scenario.get("id")) for _path, scenario, _label in rows])
    if "rules_only" not in st.session_state:
        st.session_state.rules_only = settings.rules_only
    st.toggle(
        "Use fixed wording",
        key="rules_only",
        help="On: the reply is the plain sentence from the counts. Off: a language model may rephrase it.",
    )
    rules_only = bool(st.session_state.rules_only)
    _backend_caption(rules_only)
    _render_guided(rows, rules_only)


main()
