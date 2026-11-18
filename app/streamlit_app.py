"""Invalid Bot dashboard.

CI, with no secrets, stays on templates and synthetic cases.
The public demo sets DATA_BACKEND=openfda and LLM_BACKEND=groq.
"""

from __future__ import annotations

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

ROOT = find_repo_root()


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


def main() -> None:
    from invalid_agent.config import load_dotenv

    load_dotenv()
    _apply_streamlit_secrets()
    settings = load_settings()
    public = settings.data_backend == "openfda"
    banner = (
        MAUDE_BANNER
        if public
        else "CI fallback when hosted secrets are unset. Synthetic cases are listed below the MAUDE cases. Not for clinical use. Not a medical device."
    )
    st.set_page_config(page_title="Invalid Bot", layout="wide")
    st.markdown(
        f"""
        <style>
          .block-container {{ padding-top: 1.2rem; }}
          .banner {{
            background: #0B3A5B; color: #F7F5F2; padding: 0.7rem 1rem;
            border-radius: 6px; font-size: 0.95rem; margin-bottom: 0.8rem;
          }}
        </style>
        <div class="banner">{banner}</div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Invalid Bot")
    st.caption("Promised validity ≥ 98% (invalid-rate cap ≤ 2%). MAUDE cannot measure that cap. Python does the math.")

    files = _scenarios(public)
    labels = []
    for path in files:
        scenario = load_scenario(path)
        labels.append(f"{scenario.get('id')} — {scenario.get('title', '')}")

    with st.sidebar:
        st.header("Case")
        choice = st.selectbox("Scenario", labels, index=0)
        week = st.slider("Investigation week", 0, 4, 0)
        rules_only = st.toggle(
            "Rules-only mode",
            value=settings.rules_only,
            help="On: templates only. Off: call the configured narrator (Groq on the hosted demo, Ollama on a laptop). A draft that fails the numeric check is replaced by the template.",
        )
        backend = _live_backend(rules_only, settings.llm_backend)
        model = _dashboard_model(rules_only, backend, settings.groq_model)
        st.caption(f"Configured backend: {settings.llm_backend}. This toggle is using `{backend}`.")
        if rules_only:
            st.caption("Rules-only is on, so no model is called. CI uses this path.")
        elif backend == "groq":
            st.caption(f"Asking Groq for `{model}` on the free tier.")
        else:
            st.warning(
                f"Asking {backend} for `{model}`. If that call fails, the notes fall back to the template and say so."
            )

    scenario_path = files[labels.index(choice)]
    if backend == "groq" and not settings.groq_api_key:
        st.error(
            "GROQ_API_KEY is not set. The hosted demo does not fall back to rules-only. "
            "Create a free key at https://console.groq.com/keys and add the Streamlit secret GROQ_API_KEY."
        )
        st.stop()
    with st.spinner("Running the week…"):
        try:
            result = _run(str(scenario_path), int(week), backend, model)
        except DataUnavailable as exc:
            st.error(str(exc))
            st.stop()

    overall = result["metrics"]["overall"]
    memo = result["triage_memo"]
    rag = "Red"
    updates = result.get("status_updates") or {}
    if updates.get("leadership") and "RAG: Amber" in updates["leadership"]:
        rag = "Amber"
    elif updates.get("leadership") and "RAG: Green" in updates["leadership"]:
        rag = "Green"
    elif updates.get("leadership") and "RAG: Red" in updates["leadership"]:
        rag = "Red"

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

    chart = result["metrics"]["p_chart"]
    left, right = st.columns(2)
    with left:
        st.plotly_chart(p_chart_figure(chart), width="stretch")
        rule1 = sum(1 for hit in chart["violations"] if hit["rule"] == 1)
        st.caption(f"Red marks are Western Electric rule 1. Count this week’s chart: {rule1}.")
        if not overall.get("spec_estimable", True):
            st.caption(
                "Bins use date_of_event when the report has one, otherwise the FDA received date. "
                "Received date is when FDA logged the report, not when the run happened. "
                "Manufacturer names are the reported names from public MAUDE. "
                "Set MANUFACTURER_DISPLAY=anonymized to show Manufacturer A, B, C instead."
            )
    with right:
        st.plotly_chart(pareto_figure(result["metrics"]["pareto"]), width="stretch")

    st.subheader("Strata")
    strata = result["metrics"]["strata"]
    column = st.selectbox("Break by", list(strata), index=0)
    table = pd.DataFrame(strata[column])
    table["rate_pct"] = (table["rate"] * 100).round(2)
    st.dataframe(
        table[["level", "n", "k", "rate_pct"]],
        width="stretch",
        hide_index=True,
    )

    st.subheader("Before / after")
    scenario = load_scenario(scenario_path)
    frame = load_frame(scenario)
    top = (result.get("hypotheses") or [{}])[0]
    summary = projection_summary(
        frame,
        top,
        float(scenario.get("spec_invalid_rate", 0.02)),
        float(scenario.get("promised_validity", 0.98)),
        spec_estimable=scenario.get("denominator") != "reported_events",
    )
    if summary["applied"]:
        after_chart = p_chart(summary["frame"])
        st.plotly_chart(before_after_figure(chart, after_chart), width="stretch")
        st.caption(
            f"{summary['label']} Observed {_pct(summary['before']['rate'])}. "
            f"Projected {_pct(summary['after']['rate'])}."
        )
    else:
        st.info("No single stratum cleared the evidence bar, so there is no removal projection.")

    st.subheader("This week’s artifacts")
    tabs = st.tabs(["Triage memo", "Fishbone", "5 Whys", "8D / CAPA", "Plan and risks", "Status notes"])
    with tabs[0]:
        st.markdown(result["triage_markdown"])
    with tabs[1]:
        st.markdown(result["fishbone"]["markdown"])
    with tabs[2]:
        st.markdown(result["five_whys"]["markdown"])
    with tabs[3]:
        st.markdown(result["capa"]["markdown"])
    with tabs[4]:
        st.dataframe(pd.DataFrame(result["plan"]["tasks"]), width="stretch", hide_index=True)
        st.dataframe(pd.DataFrame(result["risks"]), width="stretch", hide_index=True)
        gantt_path = ROOT / "out" / "dashboard" / scenario_path.stem / f"week{int(week)}" / "gantt.html"
        if gantt_path.is_file():
            st.caption("Gantt HTML is in the week folder next to this run. The task table above is the same plan.")
    with tabs[5]:
        audience = st.radio("Audience", ["customer", "internal", "leadership"], horizontal=True)
        st.markdown(updates.get(audience, "_No note for this audience._"))

    jira = result.get("jira") or {}
    if jira.get("issues"):
        st.subheader("Jira")
        st.caption(f"Mode: {jira.get('mode', '')}. Project {jira.get('project', '')}.")
        st.dataframe(pd.DataFrame(jira.get("issues") or []), width="stretch", hide_index=True)
        if jira.get("note"):
            st.info(str(jira["note"]))
        base = settings.jira_base_url
        if base and str(jira.get("mode", "")).startswith("live"):
            for issue in jira.get("issues") or []:
                key = issue.get("key")
                if key:
                    st.markdown(f"- [{key}]({base}/browse/{key})")

    st.subheader("Ask the MAUDE table")
    st.caption(
        "Suggested questions use vetted read-only SQL. Python computes the rates and the Wilson intervals. "
        "A model, when one is on, may only choose a template."
    )
    picked = None
    for item in SUGGESTED_QUESTIONS:
        if st.button(item["label"], key=item["id"]):
            picked = item
    typed = st.text_input("Or type a question about OOI or JJE")
    if st.button("Ask typed question") and typed.strip():
        picked = {"text": typed.strip(), "template_id": None, "params": {}}
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
            choice = {"template_id": picked["template_id"], "params": dict(picked.get("params") or {}), "source": "suggested"}
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
    st.caption(f"Template `{answered['template_id']}` chosen by {answered['source']}. Fidelity ok: {answered['fidelity'].get('ok')}.")


main()
