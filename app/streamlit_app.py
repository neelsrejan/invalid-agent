"""Invalid Bot dashboard.

The guided walk is four JJE pages: companies over 1%, cause sets, simulated
responses, and the close-out. Next stays off until that page's goal is logged.
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

from invalid_agent.artifacts.charts import company_share_figure, fishbone_figure, pareto_figure
from invalid_agent.config import find_repo_root, load_settings
from invalid_agent.llm import ToolCaller
from invalid_agent.data.frame import load_frame
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.guide import GUIDE_STEPS, progress_label
from invalid_agent.ui.plain import (
    PRACTICE_BANNER,
    PUBLIC_BANNER,
    gloss_once,
    gloss_seen_for_banner,
    plain_case_label,
    unexplained_jargon,
)
from invalid_agent.ui.story import build_week_view
from invalid_agent.ui.talkback import (
    LOOKUP_PARTS,
    accepted_signatures,
    example_prompts,
    part_fact,
    respond,
    reword_reply,
)

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
        "WEEK1_GROQ_MODEL",
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
    hosted = [ROOT / "cases" / "openfda_jje.yaml"]
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


_VIEW_SCHEMA = 3


@st.cache_data(show_spinner=False)
def _week_view(scenario_path: str, story_week: int, view_schema: int) -> dict:
    del view_schema
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


def _tool_client(rules_only: bool) -> ToolCaller | None:
    llm = _talk_llm(rules_only)
    if not isinstance(llm, ToolCaller):
        return None
    return llm


def _talk_client(beat_id: str, rules_only: bool) -> ToolCaller | None:
    if beat_id != "eda":
        return _tool_client(rules_only)
    if rules_only:
        return None
    from invalid_agent.llm import GroqLLM

    settings = load_settings()
    if not settings.groq_api_key:
        return None
    return GroqLLM(settings.groq_api_key, settings.week1_groq_model)


def _apply_talk(message: str, view: dict, beat_id: str, week: int, rules_only: bool) -> None:
    ticket_key = f"Your ticket {int(st.session_state.insight_serial) + 1}"
    flag_key = f"Flag {int(st.session_state.flag_serial) + 1}"
    reply = respond(
        message,
        view,
        beat_id,
        ticket_key=ticket_key,
        flag_key=flag_key,
        tool_client=_talk_client(beat_id, rules_only),
    )
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
    elif reply.get("log_kind") == "insight" and reply.get("confirmed") and existing is None:
        st.session_state.open_items.append(
            {
                "week": week,
                "key": "Insight",
                "text": text,
                "kind": "insight",
                "signature": signature,
            }
        )
    if reply.get("confirmed") and signature in accepted_signatures(view, beat_id):
        _mark_done(week, beat_id)
    if beat_id in LOOKUP_PARTS or beat_id == "eda":
        shown = text
    else:
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
    with st.form("talk-form", clear_on_submit=True):
        message = st.text_input("Your question or insight", key=talk_key)
        submitted = st.form_submit_button("Tell the agent", key="talk-send")
    if submitted:
        _apply_talk(str(message or ""), view, beat_id, week, rules_only)
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


def _log_week_tickets(view: dict, week: int) -> None:
    facts = view.get("explore") or {}
    held = facts.get("_held") or {}
    if week == 1:
        rows = held.get("requests") or facts.get("requests") or []
    elif week == 2:
        rows = [
            {"summary": issue["ticket"], "message": issue["testimonial"]}
            for issue in (held.get("issues") or facts.get("issues") or [])
        ]
    else:
        return
    existing = {str(item.get("text") or "") for item in st.session_state.open_items}
    for row in rows:
        text = str(row.get("summary") or "")
        if not text or text in existing:
            continue
        st.session_state.open_items.append(
            {
                "week": week,
                "key": "Ticket",
                "text": text,
                "kind": "ticket",
                "signature": text,
                "message": str(row.get("message") or ""),
            }
        )


def _render_audit(view: dict, step_id: str, scenario: dict) -> None:
    from invalid_agent.ui.audit import hints_for

    facts = view.get("explore") or {}
    for line in hints_for(step_id):
        st.markdown(_say(line))
    st.caption(str(facts.get("share_line") or "invalid share of field problem reports"))
    if step_id == "eda":
        st.markdown(
            "Note: companies with fewer than 100 reports are marked too few reports to judge and are not flagged."
        )
        st.markdown("**First 10 rows of the dataset**")
        preview = facts.get("preview") or []
        if preview:
            st.dataframe(preview, use_container_width=True)
        st.markdown("**Aggregated invalid data by company**")
        companies = facts.get("companies") or []
        if companies:
            st.dataframe(
                [
                    {
                        "company": row["name"],
                        "reports": row["total"],
                        "invalid reports": row["invalid"],
                        "invalid share": f"{float(row['share']) * 100:.2f}%",
                        "note": row.get("note") or "",
                    }
                    for row in companies
                ],
                use_container_width=True,
            )
            st.plotly_chart(company_share_figure(companies), use_container_width=True)
        st.markdown("**Invalid by company exceeding 1% and has enough N**")
        flagged = facts.get("flagged") or []
        if flagged:
            st.dataframe(
                [
                    {
                        "company": row["name"],
                        "invalid": row["invalid"],
                        "total": row["total"],
                        "rate": f"{float(row['share']) * 100:.2f}%",
                    }
                    for row in flagged
                ],
                use_container_width=True,
            )
        return
    if step_id == "pareto":
        for bundle in facts.get("cause_sets") or []:
            st.markdown(_say(f"**{bundle['name']}**"))
            chart_rows = [
                {**row, "cumulative_share": row.get("cumulative") or 0}
                for row in bundle.get("pareto") or []
            ]
            if chart_rows:
                st.plotly_chart(pareto_figure(chart_rows, count_title="Invalid reports"), use_container_width=True)
            tied = bundle.get("tied") or []
            if tied:
                causes = " or ".join(str(code) for code in tied) + f" (tied at {int(bundle.get('tie_count') or 0)})"
            else:
                causes = ", ".join(f"{cause['code']} ({int(cause['count'])})" for cause in bundle["causes"])
            st.markdown(
                _say(
                    f"Smallest set that gets under 1%: {causes or 'none'}. "
                    f"Projected share {float(bundle.get('projected') or 0) * 100:.2f}%."
                )
            )
        for request in facts.get("requests") or []:
            st.markdown(_say(f"**{request['summary']}**"))
            st.markdown(_say(request["message"]))
        return
    if step_id == "responses":
        for issue in facts.get("issues") or []:
            st.markdown(_say(f"**{issue['ticket']}**"))
            st.markdown(_say(issue["testimonial"]))
            st.plotly_chart(fishbone_figure(issue["branch"]), use_container_width=True)
        return
    for row in facts.get("closeouts") or []:
        st.markdown(_say(row["statement"]))
    _offer_deck(view, scenario)


def _nav(week: int, beat: int, finished: bool, view: dict) -> None:
    del beat
    step = GUIDE_STEPS[week - 1]
    back, forward = st.columns(2)
    with back:
        if st.button("Back", key="back", disabled=week == 1 and not finished):
            if finished:
                st.session_state.finished = False
            elif week > 1:
                st.session_state.story_week = week - 1
                st.session_state.beat = 0
            st.rerun()
    with forward:
        if finished:
            return
        ready = _part_done(week, step.id)
        if st.button("Show me", key="show-me", disabled=ready):
            _reveal(view, step.id, week)
            st.rerun()
        label = "Finish the story" if week >= 4 else step.next_label
        if st.button(label, key="next", type="primary", disabled=not ready):
            if not _part_done(week, step.id):
                return
            _log_week_tickets(view, week)
            if week < 4:
                st.session_state.story_week = week + 1
                st.session_state.beat = 0
                st.session_state.unlocked_week = max(int(st.session_state.unlocked_week), week + 1)
            else:
                st.session_state.finished = True
            st.rerun()


def _render_guided(rows: list[tuple[Path, dict, str]], rules_only: bool) -> None:
    _fresh_gloss()
    by_id = {str(scenario.get("id")): (path, scenario) for path, scenario, _label in rows}
    scenario_path, scenario = by_id[st.session_state.scenario_id]
    week = int(st.session_state.story_week)
    beat = int(st.session_state.beat)
    finished = bool(st.session_state.finished)
    try:
        view = _week_view(str(scenario_path), week, _VIEW_SCHEMA)
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

    step = GUIDE_STEPS[week - 1]
    st.subheader(f"{progress_label(week, 0)} — {step.title}")
    if week == 1:
        st.markdown(plain_case_label(str(scenario.get("title") or "")))
    _render_carried(week)
    _render_audit(view, step.id, scenario)
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
