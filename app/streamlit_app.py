"""Invalid Bot dashboard.

The guided walk is Week 1 through Week 4. Each week is complaint, numbers,
charts, what gets logged, root-cause notes, and a wrap-up. The next week
unlocks only after the wrap-up. Python computes every number. A language
model, when one is on, may only rephrase the talk-back reply.
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
_SRC_TEXT = str(_SRC.resolve())
sys.path[:] = [entry for entry in sys.path if entry != _SRC_TEXT]
sys.path.insert(0, _SRC_TEXT)

from invalid_agent.fresh import ensure_checkout, note_imports

ensure_checkout(_SRC)

import pandas as pd
import streamlit as st

from invalid_agent.artifacts.charts import before_after_figure, p_chart_figure, pareto_figure
from invalid_agent.config import find_repo_root, load_settings
from invalid_agent.data.frame import load_frame
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.guide import AUDIENCES, GUIDE_STEPS, progress_label
from invalid_agent.ui.plain import (
    PRACTICE_BANNER,
    PUBLIC_BANNER,
    gloss_once,
    gloss_seen_for_banner,
    plain_case_label,
    unexplained_jargon,
)
from invalid_agent.ui.records import logged_sections, note_sections, sections_from_run
from invalid_agent.ui.story import beat_lines, build_week_view
from invalid_agent.ui.talkback import accepted_signatures, example_prompts, part_fact, respond, reword_reply

note_imports()

_LOG = logging.getLogger("invalid_agent.ui")

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
    "open_items",
    "insight_serial",
    "flag_serial",
    "last_reply",
    "deck_bytes",
    "deck_error",
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
    if "talk_nonce" not in st.session_state:
        st.session_state.talk_nonce = 0
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
    if not isinstance(st.session_state.get("open_items"), list):
        st.session_state.open_items = []
    if "insight_serial" not in st.session_state:
        st.session_state.insight_serial = 0
    if "flag_serial" not in st.session_state:
        st.session_state.flag_serial = 0
    if "audience" not in st.session_state:
        st.session_state.audience = "customer"
    if not isinstance(st.session_state.get("done_parts"), list):
        st.session_state.done_parts = []
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
        st.session_state.done_parts = []
        st.session_state.open_items = []
        st.session_state.ask_cache = {}
        st.session_state.insight_serial = 0
        st.session_state.flag_serial = 0
        st.session_state.last_reply = None
        st.session_state.stratum_for_week = None
        st.session_state.deck_bytes = None
        st.session_state.deck_error = False
    st.session_state.locked_case = current


def _page_chrome(banner: str) -> None:
    st.set_page_config(page_title="Invalid Triage Bot", layout="wide")
    st.markdown(
        """
        <style>
          header[data-testid="stHeader"] { position: static !important; }
          [data-testid="stToolbar"] { position: static !important; }
          .block-container { padding-top: 1.4rem !important; padding-bottom: 7rem !important; }
          div[data-testid="stHtml"],
          div[data-testid="stHtml"] iframe,
          div[data-testid="stHtml"] div {
            height: auto !important;
            max-height: none !important;
            overflow: visible !important;
            white-space: normal !important;
          }
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
        "border-radius:6px;margin-top:8px;max-width:100%;box-sizing:border-box;"
        'height:auto;overflow:visible;">'
        '<p style="margin:0;color:#FFFFFF;font-size:16px;line-height:1.45;'
        "font-family:sans-serif;font-weight:500;white-space:normal;"
        'overflow-wrap:anywhere;word-break:break-word;">'
        f"{safe}</p></div>"
    )
    st.title("Invalid Triage Bot")
    st.caption(
        "It shows the invalid types and the complaints for a device, "
        "then tracks progress toward the failure mode and a way to reduce future complaints."
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
    ticket_key = f"Your ticket {int(st.session_state.insight_serial) + 1}"
    flag_key = f"Flag {int(st.session_state.flag_serial) + 1}"
    reply = respond(message, view, beat_id, ticket_key=ticket_key, flag_key=flag_key)
    signature = str(reply.get("signature") or "")
    existing = next(
        (
            item
            for item in st.session_state.open_items
            if (
                signature
                and item.get("signature") == signature
                and item.get("kind") == reply["log_kind"]
                and int(item.get("week") or 0) == int(week)
            )
        ),
        None,
    )
    text = str(reply.get("text") or "")
    if existing and reply["log_kind"] in {"ticket", "flag"}:
        text = text.replace(str(reply.get("log_key") or ""), str(existing["key"]))
    elif reply["log_kind"] == "ticket" and reply.get("bullet"):
        st.session_state.insight_serial = int(st.session_state.insight_serial) + 1
        st.session_state.open_items.append(
            {
                "week": week,
                "key": reply["log_key"],
                "text": reply["bullet"],
                "kind": "ticket",
                "signature": signature,
            }
        )
    elif reply["log_kind"] == "flag":
        st.session_state.flag_serial = int(st.session_state.flag_serial) + 1
        st.session_state.open_items.append(
            {
                "week": week,
                "key": reply["log_key"],
                "text": signature,
                "kind": "flag",
                "signature": signature,
            }
        )
    if reply.get("confirmed") and signature in accepted_signatures(view, beat_id):
        _mark_done(week, beat_id)
    shown = reword_reply(text, _talk_llm(rules_only))
    if unexplained_jargon(shown):
        shown = text
    st.session_state.last_reply = {
        "week": week,
        "beat": beat_id,
        "user_text": reply.get("user_text") or "",
        "text": shown,
    }
    st.session_state.talk_nonce = int(st.session_state.get("talk_nonce") or 0) + 1


def _mark_done(week: int, beat_id: str) -> None:
    key = f"{int(week)}:{beat_id}"
    done = st.session_state.done_parts
    if key not in done:
        done.append(key)


def _part_done(week: int, beat_id: str) -> bool:
    return f"{int(week)}:{beat_id}" in st.session_state.done_parts


def _fresh_gloss() -> None:
    public = load_settings().data_backend == "openfda"
    st.session_state._gloss_seen = gloss_seen_for_banner(public)


def _say(text: str) -> str:
    seen = st.session_state.get("_gloss_seen")
    if not isinstance(seen, set):
        seen = set()
        st.session_state._gloss_seen = seen
    return gloss_once(str(text or ""), seen)


def _item_line(item: dict) -> str:
    text = str(item.get("text") or "").strip()
    if item.get("kind") == "insight":
        return f"- **Insight:** {text}"
    key = str(item.get("key") or "")
    kind = "Ticket" if item.get("kind") == "ticket" else "Flag"
    prefix = f"{key}:"
    if text.startswith(prefix):
        text = text[len(prefix) :].strip()
    return f"- **{key}** ({kind}): {text}"


def _render_lines(lines: list[str]) -> None:
    for line in lines:
        if line.startswith("### "):
            st.subheader(_say(line[4:]))
        else:
            st.markdown(_say(line))


def _render_carried(week: int) -> None:
    if week <= 1:
        return
    carried = [
        item
        for item in st.session_state.open_items
        if int(item["week"]) < week and item.get("kind") in {"ticket", "flag"} and str(item.get("text") or "").strip()
    ]
    if not carried:
        return
    st.subheader("Still open from earlier weeks")
    for item in carried:
        st.markdown(_say(_item_line(item)))


def _render_insights(week: int) -> None:
    st.subheader(f"Week {week} insights")
    items = [
        item
        for item in st.session_state.open_items
        if int(item["week"]) == week and str(item.get("text") or "").strip()
    ]
    if not items:
        st.markdown("No confirmed insight yet. Tell the agent what you see. A confirmed insight will land here.")
        return
    for item in items:
        st.markdown(_say(_item_line(item)))


def _render_talk(view: dict, beat_id: str, week: int, rules_only: bool) -> None:
    st.subheader("Talk to the agent")
    st.caption("Type a question, or type what you think is going on. The reply uses this week's counts.")
    talk_key = f"talk_text_{int(st.session_state.get('talk_nonce') or 0)}"
    st.text_input("Your question or insight", key=talk_key)
    if st.button("Tell the agent", key="talk-send"):
        _apply_talk(str(st.session_state.get(talk_key) or ""), view, beat_id, week, rules_only)
        st.rerun()
    prompts = example_prompts(view, beat_id if beat_id != "done" else "wrap")
    st.caption("Or try one of these.")
    for index, prompt in enumerate(prompts):
        if st.button(_say(prompt), key=f"ex-{beat_id}-{index}"):
            _apply_talk(prompt, view, beat_id, week, rules_only)
            st.rerun()
    last = st.session_state.get("last_reply") or {}
    if last and int(last.get("week") or 0) == week and str(last.get("beat") or "") == beat_id:
        if last.get("user_text"):
            st.markdown("**You said.** " + str(last["user_text"]))
        st.markdown(_say(str(last.get("text") or "")))


def _render_metrics(view: dict) -> None:
    label = "Invalid rate" if view["estimable"] else "Share of reports"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label, view["rate_label"])
    c2.metric("Count", view["count_label"])
    c3.metric("Likely range", view["range_label"])
    c4.metric("This week's call", view["call_label"])


def _chart_words(view: dict) -> tuple[str, str, str]:
    if view.get("estimable"):
        return "Weekly invalid rate", "Invalid rate (%)", "Invalid %"
    return "Weekly share of reports", "Share of reports (%)", "Share of reports"


def _render_charts(view: dict, week: int) -> None:
    title, y_title, series = _chart_words(view)
    st.plotly_chart(
        p_chart_figure(view["chart"], title=title, y_title=y_title, series_name=series),
        width="stretch",
    )
    if view["pareto"]:
        legend = " ".join(
            f"{row['plain']}." for row in view["pareto"] if row.get("plain")
        )
        if legend:
            st.caption(_say(legend))
        count_title = "Invalids" if view.get("estimable") else "Reports"
        st.plotly_chart(pareto_figure(view["pareto"], count_title=count_title), width="stretch")
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
        share = "Share" if view.get("estimable") else "Share of reports"
        shown = pd.DataFrame(rows)[["level", "n", "k", "rate_label"]].rename(
            columns={"level": "Group", "n": "Rows", "k": "Invalids", "rate_label": share}
        )
        st.dataframe(shown, width="stretch", hide_index=True)
    else:
        st.info("Every row in this break is blank, so there is nothing to rank. A blank is not a cause.")


def _render_tickets(view: dict) -> None:
    rows = view["tickets"]
    if not rows:
        st.info("This week has no plan ticket yet.")
        return
    shown = pd.DataFrame(rows).rename(
        columns={"key": "Ticket", "name": "Work", "owner": "Owner", "status": "Status"}
    )
    st.dataframe(shown, width="stretch", hide_index=True)


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
        _title, y_title, _series = _chart_words(view)
        st.plotly_chart(
            before_after_figure(view["chart"], view["after_chart"], y_title=y_title),
            width="stretch",
        )


def _offer_deck(view: dict, scenario: dict) -> None:
    if int(view["story_week"]) < 4:
        return
    st.caption("The seven-slide deck is exec_deck.pptx. It uses the same numbers as this wrap-up.")
    if st.button("Prepare the slide file", key="prepare-deck"):
        payload = _deck_bytes(view, scenario)
        st.session_state.deck_bytes = payload
        st.session_state.deck_error = payload is None
        st.rerun()
    if st.session_state.get("deck_error"):
        st.error("The slide file did not build. Try again. This page does not show the error detail.")
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
        "banner": PUBLIC_BANNER if not view.get("estimable") else PRACTICE_BANNER,
        "estimable": bool(view.get("estimable")),
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
    except Exception as exc:
        _LOG.error("deck build failed: %s", type(exc).__name__)
        return None


@st.cache_data(show_spinner=False)
def _case_sections(scenario_path: str, story_week: int) -> list[dict[str, str]]:
    """Cached graph records for one story week. The model stays off for this call."""
    try:
        from invalid_agent.graph import run_case
        from invalid_agent.llm import DeterministicLLM

        out = ROOT / "out" / "dashboard" / Path(scenario_path).stem / f"week{int(story_week)}"
        result = run_case(str(scenario_path), int(story_week), out, llm=DeterministicLLM())
        scenario = load_scenario(Path(scenario_path))
        public = str(scenario.get("denominator") or "") == "reported_events"
        base = ""
        try:
            base = str(load_settings().jira_base_url or "")
        except Exception:
            base = ""
        return sections_from_run(result, base_url=base, public=public)
    except Exception as exc:
        _LOG.error("case run failed: %s", type(exc).__name__)
        return [
            {
                "title": "This week's write-ups",
                "what": "What this is: the agent's records for this week.",
                "body": (
                    "The write-ups did not load. The counts on this page are still the ones to use. "
                    "This page does not show a connection string."
                ),
            }
        ]


def _render_sections(sections: list[dict[str, str]]) -> None:
    if not sections:
        return
    st.caption("The agent's write-ups are closed. Open one if you want the detail.")
    for section in sections:
        with st.expander(section["title"]):
            st.markdown(section["what"])
            st.markdown(section["body"])


def _render_ask(scenario: dict, rules_only: bool) -> None:
    from invalid_agent.data.query import SUGGESTED_QUESTIONS

    fda = str(scenario.get("denominator") or "") == "reported_events"
    title = "Ask the public report table"
    if fda:
        title = (
            "Ask the public report table "
            "(MAUDE, the FDA's public database of device problem reports)"
        )
    with st.expander(title):
        st.markdown(
            "Python counts the rows. A language model, if one is on, only picks a prepared question."
        )
        code = str(scenario.get("product_code") or "").upper()
        items = []
        for item in SUGGESTED_QUESTIONS:
            params_code = str((item.get("params") or {}).get("product_code") or "").upper()
            if code and params_code and params_code != code:
                continue
            items.append(item)
        if not items:
            items = list(SUGGESTED_QUESTIONS)
        picked = None
        for item in items:
            if st.button(_say(str(item["label"])), key=f"ask-{item['id']}"):
                picked = item
        if picked:
            _show_answer(picked, rules_only)


def _show_answer(picked: dict, rules_only: bool) -> None:
    from invalid_agent.data.db import connect, query_url
    from invalid_agent.data.query import answer_question
    from invalid_agent.llm import get_llm

    cache = st.session_state.setdefault("ask_cache", {})
    cache_key = str(picked.get("id") or picked.get("text") or "")
    if cache_key and cache_key in cache:
        st.markdown(cache[cache_key])
        return
    try:
        public = load_settings().data_backend == "openfda"
        url = query_url(load_settings(), public=public)
        conn = connect(url, readonly=True)
    except Exception as exc:
        _LOG.error("report table unavailable: %s", type(exc).__name__)
        st.error(
            "The public report table is not connected, so this question cannot run. "
            "This page does not show a connection string."
        )
        return
    try:
        choice = None
        if picked.get("template_id"):
            choice = {
                "template_id": picked["template_id"],
                "params": dict(picked.get("params") or {}),
                "source": "suggested",
            }
        llm = None
        if not rules_only:
            try:
                llm = get_llm()
            except Exception:
                llm = None
        answered = answer_question(str(picked["text"]), conn, llm=llm, choice=choice)
    except Exception as exc:
        _LOG.error("report question failed: %s", type(exc).__name__)
        st.error(
            "The question did not run. This page does not show the error detail."
        )
        return
    finally:
        conn.close()
    from invalid_agent.ui.plain import safe_prose

    prose = safe_prose(str(answered.get("prose") or ""))
    if not prose:
        prose = "The table answered. The counts on this page stay the ones Python computed for this week."
    if cache_key:
        cache[cache_key] = prose
    st.markdown(prose)


def _reveal(view: dict, beat_id: str, week: int) -> None:
    """Log this part's key insight. The reader asked to be shown the point."""
    finding, body = part_fact(view, beat_id)
    body = str(body or "").strip()
    if not body:
        _mark_done(week, beat_id)
        return
    existing = next(
        (
            item
            for item in st.session_state.open_items
            if item.get("signature") == finding and int(item.get("week") or 0) == int(week)
        ),
        None,
    )
    if existing is None:
        text = f"Here is the point of this part. {body}"
        st.session_state.open_items.append(
            {
                "week": week,
                "key": "Insight",
                "text": body,
                "kind": "insight",
                "signature": finding,
            }
        )
        st.session_state.last_reply = {
            "week": week,
            "beat": beat_id,
            "user_text": "Show me",
            "text": text,
        }
        st.session_state.talk_nonce = int(st.session_state.get("talk_nonce") or 0) + 1
    _mark_done(week, beat_id)


def _nav(week: int, beat: int, finished: bool, view: dict) -> None:
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
        ready = _part_done(week, step.id)
        if st.button("Show me", key="show-me", disabled=ready):
            _reveal(view, step.id, week)
            st.rerun()
        if beat < len(GUIDE_STEPS) - 1:
            label = step.next_label
        elif week < 4:
            label = f"Start week {week + 1}"
        else:
            label = "Finish the story"
        if st.button(label, key="next", type="primary", disabled=not ready):
            if not _part_done(week, step.id):
                return
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
    _fresh_gloss()
    by_id = {str(scenario.get("id")): (path, scenario) for path, scenario, _label in rows}
    scenario_path, scenario = by_id[st.session_state.scenario_id]
    week = int(st.session_state.story_week)
    beat = int(st.session_state.beat)
    finished = bool(st.session_state.finished)
    try:
        view = _week_view(str(scenario_path), week)
    except Exception as exc:
        _LOG.error("week view failed: %s", type(exc).__name__)
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
        _nav(week, beat, True, view)
        return

    step = GUIDE_STEPS[beat]
    st.subheader(f"{progress_label(week, beat)} — {step.title}")
    if step.id == "complaint":
        st.markdown(
            _say(
                "Let's understand the invalid results in the context of what this device is supposed to do."
            )
        )
    if step.id not in {"complaint", "data"}:
        st.markdown(_say(f"**What the agent is doing.** {step.doing}"))
    st.markdown(_say(f"**Why.** {step.why}"))
    st.markdown(_say(f"**What to look at.** {step.look}"))
    if week == 1 and beat == 0:
        _render_case_picker(rows)
        scenario_path, scenario = by_id[st.session_state.scenario_id]
        try:
            view = _week_view(str(scenario_path), week)
        except Exception as exc:
            _LOG.error("week view failed: %s", type(exc).__name__)
            st.error(
                "The public report table is not connected, so this case cannot load. "
                "Pick a practice case. This page does not show a connection string."
            )
            st.stop()
    _render_carried(week)
    _render_lines(beat_lines(view, step.id))
    if step.id == "data":
        _render_metrics(view)
    elif step.id == "charts":
        _render_charts(view, week)
    elif step.id == "logged":
        _render_tickets(view)
        _render_sections(logged_sections(_case_sections(scenario_path, week)))
        _render_ask(scenario, rules_only)
    elif step.id == "notes":
        _render_notes(view)
        _render_sections(note_sections(_case_sections(scenario_path, week)))
    elif step.id == "wrap":
        _render_wrap_chart(view)
        _offer_deck(view, scenario)
    _render_talk(view, step.id, week, rules_only)
    _render_insights(week)
    _nav(week, beat, False, view)


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
    rules_only = bool(settings.rules_only)
    try:
        _render_guided(rows, rules_only)
    finally:
        # Lazy imports during the page run have to be stamped too, or the next
        # rerun treats them as leftovers from the previous release and reloads.
        note_imports()


main()
