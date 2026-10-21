"""Week-0 intake. Computes the memo fields, then asks for prose."""

from __future__ import annotations

from typing import Any

from invalid_agent.case.schemas import HypothesisRef, TriageMemo
from invalid_agent.case.state import CaseState
from invalid_agent.llm import get_llm, narrate
from invalid_agent.metrics.hypotheses import evidence_catalog, rank_hypotheses
from invalid_agent.metrics.pareto import pareto
from invalid_agent.metrics.rates import chi_square_by, overall_rate, stratified_rates
from invalid_agent.metrics.spc import p_chart
from invalid_agent.sim.generate import generate


def _pct(value: float) -> float:
    return round(float(value) * 100.0, 2)


def _top(rows: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    trimmed = []
    for row in rows[:limit]:
        trimmed.append(
            {
                "level": row["level"],
                "n": row["n"],
                "k": row["k"],
                "rate": row["rate"],
                "rate_pct": _pct(row["rate"]),
            }
        )
    return trimmed


def _severity(overall: dict[str, Any]) -> str:
    if not overall["exceeds_spec"]:
        return "low"
    if overall["ci_entirely_above_spec"] or overall["rate"] >= 1.5 * overall["spec_invalid_rate"]:
        return "high"
    return "moderate"


def _hypothesis_facts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rendered = []
    for item in items[:3]:
        lift = None if item.get("lift") is None else round(float(item["lift"]), 2)
        if item["cause"] == "no_single_cause":
            prose = item["summary"]
        else:
            prose = (
                f"{item['category']} / {item['cause']}: {item['level']} at "
                f"{_pct(item['rate']):.2f}% versus complement {_pct(item['complement_rate']):.2f}% "
                f"(lift {lift:.2f}, n={item['n']}, k={item['k']})."
            )
        rendered.append(
            {
                "cause": item["cause"],
                "category": item["category"],
                "level": item["level"],
                "score": round(float(item["score"]), 2),
                "rate": item["rate"],
                "rate_pct": None if item["rate"] is None else _pct(item["rate"]),
                "complement_rate": item.get("complement_rate"),
                "complement_rate_pct": None
                if item.get("complement_rate") is None
                else _pct(item["complement_rate"]),
                "lift": lift,
                "n": item["n"],
                "k": item["k"],
                "p_value": item.get("p_value"),
                "evidence_ids": list(item.get("evidence_ids") or []),
                "prose": prose,
            }
        )
    return rendered


def build_facts(scenario: dict[str, Any], df, hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    spec = float(scenario.get("spec_invalid_rate", 0.02))
    promised = float(scenario.get("promised_validity", 0.98))
    overall = overall_rate(df, spec, promised)
    chart = p_chart(df)
    rule1 = sum(1 for hit in chart["violations"] if hit["rule"] == 1)
    strata = {
        column: _top(stratified_rates(df, column))
        for column in ("reagent_lot", "instrument", "site", "software_version", "operator")
    }
    head = []
    for row in pareto(df)[:3]:
        head.append(
            {
                "code": row["code"],
                "count": row["count"],
                "share": row["share"],
                "share_pct": _pct(row["share"]),
            }
        )
    return {
        "scenario_id": str(scenario.get("id", "scenario")),
        "title": str(scenario.get("title", "")),
        "device": str(scenario.get("device", "molecular panel")),
        "week": 0,
        "complaint": str(scenario.get("complaint", "Synthetic complaint.")),
        "overall": {
            "n": overall["n"],
            "k": overall["k"],
            "rate": overall["rate"],
            "ci_low": overall["ci_low"],
            "ci_high": overall["ci_high"],
            "spec_invalid_rate": overall["spec_invalid_rate"],
            "promised_validity": overall["promised_validity"],
            "confidence": overall["confidence"],
            "rate_pct": _pct(overall["rate"]),
            "ci_low_pct": _pct(overall["ci_low"]),
            "ci_high_pct": _pct(overall["ci_high"]),
            "spec_pct": _pct(overall["spec_invalid_rate"]),
            "promised_pct": _pct(overall["promised_validity"]),
            "exceeds_spec": overall["exceeds_spec"],
            "ci_entirely_above_spec": overall["ci_entirely_above_spec"],
        },
        "severity": _severity(overall),
        "escalate": bool(overall["exceeds_spec"]),
        "strata": strata,
        "pareto": head,
        "spc": {
            "p_bar": chart["p_bar"],
            "p_bar_pct": _pct(chart["p_bar"]),
            "violation_count": len(chart["violations"]),
            "rule1_count": rule1,
            "rules_defined": [1, 2, 3, 4],
        },
        "hypotheses": _hypothesis_facts(hypotheses),
        "alpha": 0.01,
    }


def _metrics_blob(df, spec: float, promised: float) -> dict[str, Any]:
    """JSON-ready metrics for later nodes. Violations stay, raw rows do not."""
    chart = p_chart(df)
    return {
        "overall": overall_rate(df, spec, promised),
        "strata": {
            column: stratified_rates(df, column)
            for column in ("reagent_lot", "instrument", "site", "software_version", "operator")
        },
        "chi2": {
            column: chi_square_by(df, column)
            for column in ("reagent_lot", "instrument", "site", "software_version", "operator")
        },
        "pareto": pareto(df),
        "p_chart": chart,
    }


def triage_node(state: CaseState) -> dict[str, Any]:
    scenario = state["scenario"]
    df = generate(scenario)
    spec = float(scenario.get("spec_invalid_rate", 0.02))
    promised = float(scenario.get("promised_validity", 0.98))
    hypotheses = rank_hypotheses(df, spec)
    facts = build_facts(scenario, df, hypotheses)
    # Week on the state wins, so a later caller can restamp the header.
    facts["week"] = int(state.get("week", 0))
    prose, fidelity = narrate("triage", facts, get_llm())
    memo = TriageMemo(
        scenario_id=facts["scenario_id"],
        week=facts["week"],
        device=facts["device"],
        rate=facts["overall"]["rate"],
        ci_low=facts["overall"]["ci_low"],
        ci_high=facts["overall"]["ci_high"],
        spec_invalid_rate=facts["overall"]["spec_invalid_rate"],
        promised_validity=facts["overall"]["promised_validity"],
        exceeds_spec=facts["overall"]["exceeds_spec"],
        escalate=facts["escalate"],
        severity=facts["severity"],
        top_lot=facts["strata"]["reagent_lot"][0]["level"],
        hypotheses=[
            HypothesisRef(
                cause=item["cause"],
                category=item["category"],
                level=item["level"],
                score=item["score"],
                evidence_ids=item["evidence_ids"],
            )
            for item in facts["hypotheses"]
        ],
        fidelity_ok=bool(fidelity["ok"]) or bool(fidelity["rewritten"]),
    )
    # A rewritten memo is the safe text, so the artifact a human reads is faithful
    # even when the model draft was not. fidelity_ok on the schema means "the
    # stored prose passed the guard", which the template does.
    stored = check_stored(prose, facts, memo)
    return {
        "metrics": _metrics_blob(df, spec, promised),
        "hypotheses": hypotheses,
        "evidence_catalog": evidence_catalog(df, spec, promised),
        "triage_memo": stored.model_dump(),
        "triage_markdown": prose,
        "fidelity": fidelity,
    }


def check_stored(prose: str, facts: dict[str, Any], memo: TriageMemo) -> TriageMemo:
    from invalid_agent.guards.numeric_fidelity import check_narrative

    result = check_narrative(prose, facts)
    if not result.ok:
        raise RuntimeError(f"triage prose failed the fidelity guard: {result.unknown}")
    return memo.model_copy(update={"fidelity_ok": True})
