"""Invalid Bot dashboard.

Rules-only is the default: the page runs with no model download.
Move the week slider to replay the stakeholder loop.
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
from invalid_agent.config import DEFAULT_LLM_MODEL, HOSTED_LLM_MODEL, find_repo_root, load_settings
from invalid_agent.graph import run_case
from invalid_agent.metrics.effectiveness import projection_summary
from invalid_agent.metrics.spc import p_chart
from invalid_agent.sim.generate import generate, load_scenario

ROOT = find_repo_root()


def _scenarios() -> list[Path]:
    return sorted((ROOT / "scenarios").glob("*.yaml"))


def _dashboard_model(rules_only: bool) -> str:
    """Honor LLM_MODEL when it is set. A local toggle-off run asks for Llama 3.2 1B.

    Streamlit Cloud has no Ollama. The hosted page stays on rules-only.
    """
    pinned = os.environ.get("LLM_MODEL", "").strip()
    if pinned:
        return pinned
    if rules_only:
        return DEFAULT_LLM_MODEL
    return HOSTED_LLM_MODEL


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
    st.set_page_config(page_title="Invalid Bot", layout="wide")
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.2rem; }
          .banner {
            background: #0B3A5B; color: #F7F5F2; padding: 0.7rem 1rem;
            border-radius: 6px; font-size: 0.95rem; margin-bottom: 0.8rem;
          }
        </style>
        <div class="banner">Simulation. Synthetic data. Not for clinical use. Not a medical device.</div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Invalid Bot")
    st.caption("A simulated 4-week field-quality investigation. Promised validity ≥ 98% (invalid rate ≤ 2%).")

    files = _scenarios()
    labels = []
    for path in files:
        scenario = load_scenario(path)
        labels.append(f"{scenario.get('id')} — {scenario.get('title', '')}")
    settings = load_settings()

    with st.sidebar:
        st.header("Case")
        choice = st.selectbox("Scenario", labels, index=0)
        week = st.slider("Investigation week", 0, 4, 0)
        rules_only = st.toggle(
            "Rules-only mode",
            value=True,
            help="On: templates and computed numbers. Off: ask Ollama, and fall back to the template if that model is unavailable.",
        )
        model = _dashboard_model(rules_only)
        st.caption(f"Configured backend before this toggle: {settings.llm_backend}.")
        if rules_only:
            st.caption(f"Rules-only is on, so no model is called. Local default is `{DEFAULT_LLM_MODEL}`.")
        else:
            st.warning(
                f"Asking Ollama for `{model}`. If that model is not running, the notes fall back to the template."
            )

    scenario_path = files[labels.index(choice)]
    backend = "deterministic" if rules_only else "ollama"
    model = _dashboard_model(rules_only)
    with st.spinner("Running the week…"):
        result = _run(str(scenario_path), int(week), backend, model)

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
    c1.metric("Invalid rate", _pct(overall["rate"]), delta=f"{(overall['rate'] - overall['spec_invalid_rate']) * 100:.2f} pp vs spec", delta_color="inverse")
    c2.metric("Spec", _pct(overall["spec_invalid_rate"]))
    c3.metric("Wilson 95% CI", f"{_pct(overall['ci_low'])} – {_pct(overall['ci_high'])}")
    c4.metric("Decision", "Escalate" if memo["escalate"] else "Hold", delta=memo["severity"])
    c5.metric("RAG", rag, delta=f"week {week}")

    chart = result["metrics"]["p_chart"]
    left, right = st.columns(2)
    with left:
        st.plotly_chart(p_chart_figure(chart), use_container_width=True)
        rule1 = sum(1 for hit in chart["violations"] if hit["rule"] == 1)
        st.caption(f"Red marks are Western Electric rule 1. Count this week’s chart: {rule1}.")
    with right:
        st.plotly_chart(pareto_figure(result["metrics"]["pareto"]), use_container_width=True)

    st.subheader("Strata")
    strata = result["metrics"]["strata"]
    column = st.selectbox("Break by", list(strata), index=0)
    table = pd.DataFrame(strata[column])
    table["rate_pct"] = (table["rate"] * 100).round(2)
    st.dataframe(
        table[["level", "n", "k", "rate_pct"]],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Before / after")
    scenario = load_scenario(scenario_path)
    frame = generate(scenario)
    top = (result.get("hypotheses") or [{}])[0]
    summary = projection_summary(frame, top, float(scenario.get("spec_invalid_rate", 0.02)), float(scenario.get("promised_validity", 0.98)))
    if summary["applied"]:
        after_chart = p_chart(summary["frame"])
        st.plotly_chart(before_after_figure(chart, after_chart), use_container_width=True)
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
        st.dataframe(pd.DataFrame(result["plan"]["tasks"]), use_container_width=True, hide_index=True)
        st.dataframe(pd.DataFrame(result["risks"]), use_container_width=True, hide_index=True)
        gantt_path = ROOT / "out" / "dashboard" / scenario_path.stem / f"week{int(week)}" / "gantt.html"
        if gantt_path.is_file():
            st.caption("Gantt HTML is in the week folder next to this run. The task table above is the same plan.")
    with tabs[5]:
        audience = st.radio("Audience", ["customer", "internal", "leadership"], horizontal=True)
        st.markdown(updates.get(audience, "_No note for this audience._"))


main()
