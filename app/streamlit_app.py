"""Invalid Bot dashboard.

The default path is a guided walk: one chart or artifact per step.
Free explore restores the full control panel. CI, with no secrets, stays
on templates and synthetic cases. The public demo sets DATA_BACKEND=openfda
and LLM_BACKEND=groq.

Python does the math. The model, when one is on, only writes wording.
"""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

# Repo root is the parent of app/. Works for `streamlit run app/streamlit_app.py`
# and for the root wrapper, which executes this file via runpy.
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pandas as pd
import streamlit as st

from invalid_agent.artifacts.charts import before_after_figure, p_chart_figure, pareto_figure
from invalid_agent.config import DEFAULT_LLM_MODEL, find_repo_root, load_settings
from invalid_agent.data.frame import DataUnavailable, load_frame
from invalid_agent.data.mapping import MAUDE_BANNER
from invalid_agent.data.query import SUGGESTED_QUESTIONS, answer_question
from invalid_agent.graph import run_case
from invalid_agent.metrics.effectiveness import projection_summary
from invalid_agent.metrics.spc import p_chart
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.guide import (
    ARTIFACTS,
    AUDIENCES,
    GUIDE_STEPS,
    SUGGESTED_CASE_IDS,
    GuideStep,
    arrivals,
    cause_sentence,
    decision_for_week,
    progress_label,
    questions_for,
    rag_label,
    stratum_label,
)

ROOT = find_repo_root()

_SYNTHETIC_BANNER = (
    "CI fallback when hosted secrets are unset. "
    "Synthetic cases are in the case list, after the MAUDE cases when those files are present. "
    "Not for clinical use. Not a medical device."
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


def _live_backend(rules_only: bool, configured: str) -> str:
    if rules_only:
        return "deterministic"
    if configured in {"ollama", "groq", "llamacpp"}:
        return configured
    return "ollama"


def _dashboard_model(rules_only: bool, backend: str, groq_model: str) -> str:
    """Rules-only does not call a model. Groq uses GROQ_MODEL. Ollama uses LLM_MODEL."""
    if backend == "groq" and not rules_only:
        return groq_model
    pinned = os.environ.get("LLM_MODEL", "").strip()
    if pinned:
        return pinned
    return DEFAULT_LLM_MODEL


@st.cache_data(show_spinner=False)
def _run(scenario_path: str, week: int, backend: str, model: str) -> dict:
    saved = {key: os.environ.get(key) for key in ("LLM_BACKEND", "LLM_MODEL")}
    os.environ["LLM_BACKEND"] = backend
    if backend != "deterministic":
        os.environ["LLM_MODEL"] = model
    try:
        out = ROOT / "out" / "dashboard" / Path(scenario_path).stem / f"week{week}"
        return run_case(scenario_path, week, out)
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _scenario_label(scenario: dict) -> str:
    return f"{scenario.get('id')} — {scenario.get('title', '')}"


def _choice_row(
    items: list[tuple[str, str]],
    key_prefix: str,
    current: str,
    per_row: int,
) -> str | None:
    """Render one-click choices. Returns the value that was clicked."""
    if not items:
        return None
    width = max(1, min(per_row, len(items)))
    clicked = None
    for start in range(0, len(items), width):
        chunk = items[start : start + width]
        columns = st.columns(len(chunk))
        for column, (value, label) in zip(columns, chunk):
            with column:
                kwargs = {"type": "primary"} if value == current else {}
                if st.button(label, key=f"{key_prefix}-{value}", **kwargs):
                    clicked = value
    return clicked


# These are widget keys. Streamlit deletes a widget key at the end of a run
# that did not render that widget. Re-assigning the key before any widget is
# created writes it into this run's session state, which is the documented way
# to keep the value. scenario_label and week are the case picker and the week
# slider. stratum and audience are the free-explore select box and radio.
_KEPT_WIDGET_KEYS = ("scenario_label", "week", "stratum", "audience")


def _init_state(settings, labels: list[str]) -> None:
    for key in _KEPT_WIDGET_KEYS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
    if st.session_state.get("_enter_explore"):
        st.session_state.explore = True
        del st.session_state["_enter_explore"]
    if st.session_state.get("_leave_explore"):
        st.session_state.explore = False
        del st.session_state["_leave_explore"]
    if "explore" not in st.session_state:
        st.session_state.explore = False
    if "rules_only" not in st.session_state:
        st.session_state.rules_only = settings.rules_only
    if "guide_step" not in st.session_state:
        st.session_state.guide_step = 0
    st.session_state.guide_step = max(0, min(len(GUIDE_STEPS) - 1, int(st.session_state.guide_step)))
    if "week" not in st.session_state:
        st.session_state.week = 0
    st.session_state.week = max(0, min(4, int(st.session_state.week)))
    if st.session_state.get("scenario_label") not in labels:
        st.session_state.scenario_label = labels[0]
    artifact_ids = {item[0] for item in ARTIFACTS}
    if st.session_state.get("artifact") not in artifact_ids:
        st.session_state.artifact = "triage"
    audience_ids = {item[0] for item in AUDIENCES}
    if st.session_state.get("audience") not in audience_ids:
        st.session_state.audience = "customer"


def _backend_caption(rules_only: bool, settings) -> None:
    backend = _live_backend(rules_only, settings.llm_backend)
    model = _dashboard_model(rules_only, backend, settings.groq_model)
    if rules_only:
        st.caption("Rules-only wording is on. Python still does the math. No model is called. CI uses this path.")
    elif backend == "groq":
        st.caption(f"Wording comes from Groq `{model}` on the free tier. Numbers stay in Python.")
    else:
        st.caption(
            f"Wording is requested from {backend} `{model}`. If that call fails, the template replaces it."
        )


def _load_result(scenario_path: Path, week: int, rules_only: bool, settings) -> dict:
    backend = _live_backend(rules_only, settings.llm_backend)
    model = _dashboard_model(rules_only, backend, settings.groq_model)
    if backend == "groq" and not settings.groq_api_key:
        st.error(
            "GROQ_API_KEY is not set. The hosted demo does not fall back to rules-only. "
            "Create a free key at https://console.groq.com/keys and add the Streamlit secret GROQ_API_KEY. "
            "Or turn on Rules-only wording in the header."
        )
        st.stop()
    with st.spinner("Running the week…"):
        try:
            return _run(str(scenario_path), int(week), backend, model)
        except DataUnavailable as exc:
            st.error(str(exc))
            st.stop()


def _rate_line(overall: dict) -> str:
    if overall.get("spec_estimable", True):
        return (
            f"Invalid rate {_pct(overall['rate'])} "
            f"({overall['k']} of {overall['n']}). "
            f"Spec {_pct(overall['spec_invalid_rate'])}."
        )
    return (
        f"Invalid-type share of reports {_pct(overall['rate'])} "
        f"({overall['k']} of {overall['n']}). "
        f"The 2% cap is not estimable from this file."
    )


def _render_metrics(result: dict, week: int) -> None:
    overall = result["metrics"]["overall"]
    memo = result["triage_memo"]
    rag = rag_label(result.get("status_updates") or {})
    c1, c2, c3, c4, c5 = st.columns(5)
    if overall.get("spec_estimable", True):
        c1.metric(
            "Invalid rate",
            _pct(overall["rate"]),
            delta=f"{(overall['rate'] - overall['spec_invalid_rate']) * 100:.2f} pp vs spec",
            delta_color="inverse",
        )
        c2.metric("Spec", _pct(overall["spec_invalid_rate"]))
    else:
        c1.metric("Invalid-type share", _pct(overall["rate"]), delta="reports, not runs")
        c2.metric("Stated cap", _pct(overall["spec_invalid_rate"]), delta="not estimable")
    c3.metric("Wilson 95% CI", f"{_pct(overall['ci_low'])} – {_pct(overall['ci_high'])}")
    c4.metric("Decision", "Escalate" if memo["escalate"] else "Hold", delta=memo["severity"])
    c5.metric("RAG", rag, delta=f"week {week}")


def _maude_chart_caption(overall: dict) -> None:
    if overall.get("spec_estimable", True):
        return
    st.caption(
        "Bins use date_of_event when the report has one, otherwise the FDA received date. "
        "Received date is when FDA logged the report, not when the run happened. "
        "Manufacturer names are the reported names from public MAUDE. "
        "Set MANUFACTURER_DISPLAY=anonymized to show Manufacturer A, B, C instead."
    )


def _render_pchart(result: dict) -> None:
    chart = result["metrics"]["p_chart"]
    st.plotly_chart(p_chart_figure(chart), width="stretch")
    rule1 = sum(1 for hit in chart["violations"] if hit["rule"] == 1)
    st.caption(f"Red marks are Western Electric rule 1. Count on this chart: {rule1}.")
    _maude_chart_caption(result["metrics"]["overall"])


def _render_pareto(result: dict) -> None:
    st.plotly_chart(pareto_figure(result["metrics"]["pareto"]), width="stretch")


def _active_stratum(strata: dict) -> str:
    columns = list(strata)
    if not columns:
        return ""
    if st.session_state.get("stratum") not in columns:
        st.session_state.stratum = columns[0]
    return str(st.session_state.stratum)


def _render_strata_table(result: dict, column: str) -> None:
    table = pd.DataFrame(result["metrics"]["strata"][column])
    table["rate_pct"] = (table["rate"] * 100).round(2)
    st.dataframe(
        table[["level", "n", "k", "rate_pct"]],
        width="stretch",
        hide_index=True,
    )


def _projection(result: dict, scenario: dict):
    frame = load_frame(scenario)
    top = (result.get("hypotheses") or [{}])[0]
    return projection_summary(
        frame,
        top,
        float(scenario.get("spec_invalid_rate", 0.02)),
        float(scenario.get("promised_validity", 0.98)),
        spec_estimable=scenario.get("denominator") != "reported_events",
    )


def _render_projection(result: dict, scenario: dict) -> None:
    summary = _projection(result, scenario)
    if summary["applied"]:
        after_chart = p_chart(summary["frame"])
        st.plotly_chart(
            before_after_figure(result["metrics"]["p_chart"], after_chart),
            width="stretch",
        )
        st.caption(
            f"{summary['label']} Observed {_pct(summary['before']['rate'])}. "
            f"Projected {_pct(summary['after']['rate'])}."
        )
    else:
        st.info("No single stratum cleared the evidence bar, so there is no removal projection.")


def _render_artifact(result: dict, scenario_path: Path, week: int, which: str) -> None:
    if which == "triage":
        st.markdown(result["triage_markdown"])
    elif which == "fishbone":
        st.markdown(result["fishbone"]["markdown"])
    elif which == "five_whys":
        st.markdown(result["five_whys"]["markdown"])
    elif which == "capa":
        st.markdown(result["capa"]["markdown"])
    else:
        st.dataframe(pd.DataFrame(result["plan"]["tasks"]), width="stretch", hide_index=True)
        st.dataframe(pd.DataFrame(result["risks"]), width="stretch", hide_index=True)
        gantt_path = ROOT / "out" / "dashboard" / scenario_path.stem / f"week{int(week)}" / "gantt.html"
        if gantt_path.is_file():
            st.caption("Gantt HTML is in the week folder next to this run. The task table above is the same plan.")


def _render_note(result: dict, audience: str) -> None:
    updates = result.get("status_updates") or {}
    st.markdown(updates.get(audience, "_No note for this audience._"))


def _render_jira(result: dict, settings) -> None:
    jira = result.get("jira") or {}
    st.caption(f"Mode: {jira.get('mode', '')}. Project {jira.get('project', '')}.")
    issues = jira.get("issues") or []
    if issues:
        st.dataframe(pd.DataFrame(issues), width="stretch", hide_index=True)
    else:
        st.info("This run did not return Jira issues.")
    if jira.get("note"):
        st.info(str(jira["note"]))
    base = settings.jira_base_url
    if base and str(jira.get("mode", "")).startswith("live"):
        for issue in issues:
            key = issue.get("key")
            if key:
                st.markdown(f"- [{key}]({base}/browse/{key})")


def _render_ask(items: list[dict], rules_only: bool, *, key_prefix: str, typed: bool) -> None:
    if not items and not typed:
        return
    st.subheader("Ask the MAUDE table")
    st.caption(
        "Suggested questions use vetted read-only SQL. Python computes the rates and the Wilson intervals. "
        "A model, when one is on, may only choose a template."
    )
    picked = None
    for item in items:
        if st.button(item["label"], key=f"{key_prefix}-{item['id']}"):
            picked = item
    if typed:
        typed_text = st.text_input("Or type a question about OOI or JJE", key=f"{key_prefix}-typed")
        if st.button("Ask typed question", key=f"{key_prefix}-ask") and typed_text.strip():
            picked = {"text": typed_text.strip(), "template_id": None, "params": {}}
    if picked:
        _show_answer(picked, rules_only)


def _show_answer(picked: dict, rules_only: bool) -> None:
    from invalid_agent.data.db import connect, query_url
    from invalid_agent.llm import get_llm

    try:
        public = load_settings().data_backend == "openfda"
        url = query_url(load_settings(), public=public)
        conn = connect(url, readonly=True)
    except DataUnavailable as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"Database connection failed: {type(exc).__name__}")
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
            llm = get_llm()
        answered = answer_question(str(picked["text"]), conn, llm=llm, choice=choice)
    except Exception as exc:
        st.error(f"The question did not run: {type(exc).__name__}: {exc}")
        return
    finally:
        conn.close()
    st.markdown(answered["prose"])
    st.caption(
        f"Template `{answered['template_id']}` chosen by {answered['source']}. "
        f"Fidelity ok: {answered['fidelity'].get('ok')}."
    )


def _week_row(teach: bool) -> None:
    st.caption("Investigation week")
    picked = _choice_row(
        [(str(week), f"Week {week}") for week in range(5)],
        "week",
        str(int(st.session_state.week)),
        per_row=5,
    )
    if picked is not None:
        st.session_state.week = int(picked)
        st.rerun()
    if teach:
        st.caption(
            "The measurements stay on this file when the week changes. "
            "The week changes what the team has been told, the status color, and the written notes."
        )


def _week_story(result: dict, scenario: dict, week: int) -> None:
    arrived = arrivals(scenario, week)
    if arrived:
        st.caption(arrived)
    decision = decision_for_week(result.get("decision_log") or [], week)
    if decision:
        st.markdown(f"**This week's decision.** {decision}")


def _render_case_picker(rows: list[tuple[Path, dict, str]]) -> None:
    suggested = [row for row in rows if str(row[1].get("id")) in SUGGESTED_CASE_IDS]
    suggested.sort(key=lambda row: SUGGESTED_CASE_IDS.index(str(row[1].get("id"))))
    if suggested:
        st.caption("Suggested cases")
        current = st.session_state.scenario_label
        columns = st.columns(len(suggested))
        for column, (_path, scenario, label) in zip(columns, suggested):
            with column:
                kwargs = {"type": "primary"} if label == current else {}
                if st.button(str(scenario.get("title") or scenario.get("id")), key=f"case-{scenario.get('id')}", **kwargs):
                    st.session_state.scenario_label = label
                    st.rerun()
    if len(rows) != len(suggested):
        st.selectbox("All cases", [row[2] for row in rows], key="scenario_label")


def _render_selected_complaint(scenario: dict) -> None:
    bits = [str(scenario.get("device") or "")]
    if scenario.get("product_code"):
        bits.append(f"Product code {scenario['product_code']}")
    if scenario.get("date_from") and scenario.get("date_to"):
        bits.append(f"{scenario['date_from']} to {scenario['date_to']}")
    st.caption(" · ".join(bit for bit in bits if bit))
    if scenario.get("denominator") == "reported_events":
        st.caption("These rows are MAUDE reports. The share is an invalid-type share of reports.")
    complaint = str(scenario.get("complaint") or "").strip()
    if complaint:
        st.markdown(complaint)


def _nav(index: int, step: GuideStep, suffix: str) -> None:
    back, forward = st.columns(2)
    with back:
        if st.button("Back", key=f"back-{suffix}", disabled=index == 0):
            st.session_state.guide_step = index - 1
            st.rerun()
    with forward:
        if st.button(step.next_label, key=f"next-{suffix}", type="primary"):
            if index >= len(GUIDE_STEPS) - 1:
                st.session_state["_enter_explore"] = True
            else:
                st.session_state.guide_step = index + 1
            st.rerun()


def _render_brief(step: GuideStep) -> None:
    st.markdown(f"**What the agent is doing.** {step.doing}")
    st.markdown(f"**Why.** {step.why}")
    st.markdown(f"**What to look at.** {step.look}")


def _guided_questions(step: GuideStep, scenario: dict, public: bool, rules_only: bool) -> None:
    if not public:
        return
    items = questions_for(step, str(scenario.get("product_code") or ""), SUGGESTED_QUESTIONS)
    if not items and not step.question_ids:
        return
    if items or step.id == "pitch":
        _render_ask(items, rules_only, key_prefix=f"ask-{step.id}", typed=True)


def _render_guided_body(
    step: GuideStep,
    result: dict | None,
    scenario: dict,
    scenario_path: Path,
    week: int,
    settings,
    public: bool,
    rules_only: bool,
) -> None:
    if step.id == "complaint":
        st.markdown(
            "Promised validity is at least 98%. The invalid rate has to stay at or below 2%. "
            "Python will measure the file. The model, when rules-only is off, only writes the notes."
        )
        return
    if step.id == "case":
        return
    if result is None:
        return
    st.caption(f"Case {scenario.get('id')} · week {int(week)}")
    teach = step.id == "chart"
    if step.needs_case:
        _week_row(teach)
    if step.id in {"chart", "notes"}:
        _week_story(result, scenario, week)
    if step.id != "chart":
        st.caption(_rate_line(result["metrics"]["overall"]))

    if step.id == "chart":
        _render_metrics(result, week)
        _render_pchart(result)
    elif step.id == "pareto":
        _render_pareto(result)
    elif step.id == "strata":
        strata = result["metrics"]["strata"]
        columns = list(strata)
        if not columns:
            st.info("This case has no strata to break on.")
        else:
            current = _active_stratum(strata)
            picked = _choice_row(
                [(column, stratum_label(column, scenario)) for column in columns],
                "stratum",
                current,
                per_row=4,
            )
            if picked is not None:
                st.session_state.stratum = picked
                st.rerun()
            st.caption(f"Break: {stratum_label(current, scenario)}")
            _render_strata_table(result, current)
            top = (result.get("hypotheses") or [{}])[0]
            st.markdown(cause_sentence(top))
    elif step.id == "projection":
        _render_projection(result, scenario)
    elif step.id == "artifacts":
        picked = _choice_row(list(ARTIFACTS), "artifact", st.session_state.artifact, per_row=3)
        if picked is not None:
            st.session_state.artifact = picked
            st.rerun()
        _render_artifact(result, scenario_path, week, st.session_state.artifact)
    elif step.id == "notes":
        picked = _choice_row(list(AUDIENCES), "audience", st.session_state.audience, per_row=3)
        if picked is not None:
            st.session_state.audience = picked
            st.rerun()
        _render_note(result, st.session_state.audience)
    elif step.id == "jira":
        _render_jira(result, settings)
    elif step.id == "pitch":
        _render_pitch(result, scenario_path, week)

    _guided_questions(step, scenario, public, rules_only)


def _render_pitch(result: dict, scenario_path: Path, week: int) -> None:
    if int(week) < 4:
        st.info(
            f"The management pitch is written at week 4. This screen is week {int(week)}. "
            "Earlier weeks keep the case open on purpose."
        )
        decision = decision_for_week(result.get("decision_log") or [], week)
        if decision:
            st.markdown(f"**This week's decision.** {decision}")
        if st.button("Open the week-4 pitch", key="open-week-4", type="primary"):
            st.session_state.week = 4
            st.rerun()
        return
    closeout_path = ROOT / "out" / "dashboard" / scenario_path.stem / f"week{int(week)}" / "closeout.md"
    if closeout_path.is_file():
        st.markdown(closeout_path.read_text(encoding="utf-8"))
    else:
        record = result.get("closeout") or {}
        if record.get("recommendation"):
            st.markdown(str(record["recommendation"]))
    _offer_deck(result)


def _offer_deck(result: dict) -> None:
    """Name the deck file. Do not print the server path."""
    deck = result.get("deck_path")
    if not deck:
        return
    path = Path(str(deck))
    st.caption(f"The seven-slide deck is {path.name}. It uses the same numbers as this pitch.")
    if not path.is_file():
        return
    st.download_button(
        "Download the deck",
        data=path.read_bytes(),
        file_name=path.name,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        key="download-deck",
    )


def _render_guided(
    rows: list[tuple[Path, dict, str]],
    settings,
    public: bool,
    rules_only: bool,
) -> None:
    index = int(st.session_state.guide_step)
    step = GUIDE_STEPS[index]
    trail = []
    for position, item in enumerate(GUIDE_STEPS):
        label = item.short
        if position == index:
            label = f"**{label}**"
        trail.append(label)
    st.caption(" · ".join(trail))
    st.subheader(f"{progress_label(index)} — {step.title}")
    _render_brief(step)
    _nav(index, step, "top")
    st.divider()

    scenario_path, scenario, _label = next(
        row for row in rows if row[2] == st.session_state.scenario_label
    )
    if step.id == "case":
        _render_case_picker(rows)
        _render_selected_complaint(scenario)

    result = None
    week = int(st.session_state.week)
    if step.needs_case:
        result = _load_result(scenario_path, week, rules_only, settings)
        week = int(st.session_state.week)
    _render_guided_body(step, result, scenario, scenario_path, week, settings, public, rules_only)
    st.divider()
    _nav(index, step, "bottom")


def _render_explore(
    rows: list[tuple[Path, dict, str]],
    settings,
    rules_only: bool,
) -> None:
    st.caption("Free explore shows every control on this page.")
    if st.button("Return to the guided steps", key="return-guided"):
        st.session_state["_leave_explore"] = True
        st.rerun()
    labels = [row[2] for row in rows]
    with st.sidebar:
        st.header("Case")
        st.selectbox("Scenario", labels, key="scenario_label")
        st.slider("Investigation week", 0, 4, key="week")
        st.caption("Rules-only wording and Free explore are in the header.")

    scenario_path, scenario, _label = next(
        row for row in rows if row[2] == st.session_state.scenario_label
    )
    week = int(st.session_state.week)
    result = _load_result(scenario_path, week, rules_only, settings)
    _render_metrics(result, week)

    chart = result["metrics"]["p_chart"]
    left, right = st.columns(2)
    with left:
        st.plotly_chart(p_chart_figure(chart), width="stretch")
        rule1 = sum(1 for hit in chart["violations"] if hit["rule"] == 1)
        st.caption(f"Red marks are Western Electric rule 1. Count on this chart: {rule1}.")
        _maude_chart_caption(result["metrics"]["overall"])
    with right:
        _render_pareto(result)

    st.subheader("Strata")
    strata = result["metrics"]["strata"]
    column = _active_stratum(strata)
    if column:
        st.selectbox(
            "Break by",
            list(strata),
            key="stratum",
            format_func=lambda name: stratum_label(name, scenario),
        )
        _render_strata_table(result, st.session_state.stratum)
        st.caption(cause_sentence((result.get("hypotheses") or [{}])[0]))

    st.subheader("Before / after")
    _render_projection(result, scenario)

    st.subheader("This week’s artifacts")
    tabs = st.tabs([label for _value, label in ARTIFACTS] + ["Status notes"])
    for tab, (value, _label) in zip(tabs, ARTIFACTS):
        with tab:
            _render_artifact(result, scenario_path, week, value)
    with tabs[len(ARTIFACTS)]:
        st.radio(
            "Audience",
            [value for value, _label in AUDIENCES],
            key="audience",
            horizontal=True,
            format_func=lambda value: dict(AUDIENCES)[value],
        )
        _render_note(result, st.session_state.audience)

    jira = result.get("jira") or {}
    if jira.get("issues"):
        st.subheader("Jira")
        _render_jira(result, settings)

    _render_ask(list(SUGGESTED_QUESTIONS), rules_only, key_prefix="ask-explore", typed=True)


def _page_chrome(banner: str) -> None:
    st.set_page_config(page_title="Invalid Bot", layout="wide")
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Inline styles on the element itself. A stylesheet on a parent was
    # painting the navy fill without keeping the sentence readable.
    safe = html.escape(banner)
    st.html(
        '<div style="background:#0B3A5B;color:#FFFFFF;padding:14px 16px;border-radius:6px;">'
        '<p style="margin:0;color:#FFFFFF;font-size:16px;line-height:1.45;'
        "font-family:sans-serif;font-weight:500;white-space:normal;\">"
        f"{safe}</p></div>"
    )
    st.title("Invalid Bot")
    st.caption(
        "Promised validity ≥ 98% (invalid-rate cap ≤ 2%). "
        "MAUDE cannot measure that cap. Python does the math."
    )


def main() -> None:
    from invalid_agent.config import load_dotenv

    load_dotenv()
    _apply_streamlit_secrets()
    settings = load_settings()
    public = settings.data_backend == "openfda"
    banner = MAUDE_BANNER if public else _SYNTHETIC_BANNER
    _page_chrome(banner)

    files = _scenarios(public)
    if not files:
        st.error("No case files were found.")
        st.stop()
    rows = []
    for path in files:
        scenario = load_scenario(path)
        rows.append((path, scenario, _scenario_label(scenario)))
    labels = [row[2] for row in rows]
    _init_state(settings, labels)

    toggles = st.columns(2)
    with toggles[0]:
        st.toggle(
            "Free explore",
            key="explore",
            help="Every chart, the week slider, the artifact tabs, Jira, and Ask the MAUDE table on one page.",
        )
    with toggles[1]:
        st.toggle(
            "Rules-only wording",
            key="rules_only",
            help=(
                "On: templates only. Off: call the configured narrator "
                "(Groq on the hosted demo, Ollama on a laptop). "
                "A draft that fails the numeric check is replaced by the template."
            ),
        )
    rules_only = bool(st.session_state.rules_only)
    _backend_caption(rules_only, settings)

    if st.session_state.explore:
        _render_explore(rows, settings, rules_only)
    else:
        _render_guided(rows, settings, public, rules_only)


main()
