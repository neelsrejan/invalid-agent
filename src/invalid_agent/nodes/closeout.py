"""Week-4 close-out: D7, D8, and a projection that is not follow-up data.

The effectiveness figure clears the leading stratum on the same synthetic
file. The prose has to say that. A missing follow-up file is not rewritten
into a cured rate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from invalid_agent.artifacts.deck import write_deck
from invalid_agent.case.state import CaseState
from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.metrics.effectiveness import projection_summary
from invalid_agent.sim.generate import generate


def _pct(value: float) -> float:
    return round(float(value) * 100.0, 2)


def build_closeout_facts(state: CaseState) -> dict[str, Any]:
    scenario = state["scenario"]
    frame = generate(scenario)
    top = (state.get("hypotheses") or [{}])[0]
    spec = float(scenario.get("spec_invalid_rate", 0.02))
    promised = float(scenario.get("promised_validity", 0.98))
    summary = projection_summary(frame, top, spec, promised)
    before = summary["before"]
    after = summary["after"]
    unit = int(scenario.get("cost_per_invalid_usd", 85))
    invalids = int(before["k"])
    cause = str(top.get("cause") or "no_single_cause")
    level = str(top.get("level") or "none")
    single = cause != "no_single_cause" and bool(summary["applied"])
    if single:
        recommendation = (
            f"Contain {level}. Do not extend the field action to every stratum "
            "on this file."
        )
        d7 = (
            "Add the leading stratum to the routine SPC review and to incoming release "
            "for the dominant invalid code. Confirmed as the prevention action at week 4."
        )
    else:
        recommendation = (
            "Do not quarantine a single stratum. Keep the investigation open and widen the data pull."
        )
        d7 = (
            "No single-stratum prevention action is confirmed. Keep the SPC review on the overall rate "
            "until a stratum clears the evidence bar."
        )
    d8 = (
        f"{summary['label']} Observed invalid rate {_pct(before['rate']):.2f}%. "
        f"Projected invalid rate {_pct(after['rate']):.2f}%. "
        "The record stays open until observed follow-up replaces the projection."
    )
    return {
        "scenario_id": str(scenario.get("id", "")),
        "device": str(scenario.get("device", "MDx-24")),
        "cause": cause,
        "level": level,
        "category": str(top.get("category") or "Unresolved"),
        "single": single,
        "rate_pct": _pct(before["rate"]),
        "ci_low_pct": _pct(before["ci_low"]),
        "ci_high_pct": _pct(before["ci_high"]),
        "spec_pct": _pct(spec),
        "promised_pct": _pct(promised),
        "after_pct": _pct(after["rate"]),
        "k": invalids,
        "n": int(before["n"]),
        "unit": unit,
        "cost": invalids * unit,
        "evidence_ids": list(top.get("evidence_ids") or ["metric:overall:rate"]),
        "confidence_pct": round(float(before.get("confidence", 0.95)) * 100.0, 0),
        "label": summary["label"],
        "recommendation": recommendation,
        "d7": d7,
        "d8": d8,
        "chart": state.get("metrics", {}).get("p_chart"),
    }


def render_closeout(facts: dict[str, Any]) -> str:
    evidence = ", ".join(facts["evidence_ids"])
    option_contain = (
        f"Option A. Contain {facts['level']}. Invalids on this file: {facts['k']} of {facts['n']}. "
        f"Cost at ${facts['unit']} each: ${facts['cost']}. "
        "Risk: a second stratum that also cleared the bar would stay in the field."
        if facts["single"]
        else "Option A. Do not contain a stratum. No leading stratum cleared the evidence bar."
    )
    return "\n".join(
        [
            "# Week-4 close-out",
            "",
            "**Simulation. Synthetic data. Not for clinical use. Not a medical device.**",
            "",
            f"Device: {facts['device']}. Scenario: {facts['scenario_id']}.",
            "",
            "## Call",
            "",
            (
                f"Call: {facts['cause']} / {facts['level']} ({facts['category']}). "
                f"Evidence: {evidence}."
            ),
            "",
            "## Effectiveness",
            "",
            facts["d8"],
            "",
            f"Observed rate {facts['rate_pct']:.2f}% "
            f"(Wilson {facts['confidence_pct']:.0f}% CI {facts['ci_low_pct']:.2f}% to {facts['ci_high_pct']:.2f}%). "
            f"Spec {facts['spec_pct']:.2f}% invalid (promised validity {facts['promised_pct']:.2f}%). "
            f"Projected rate {facts['after_pct']:.2f}%.",
            "",
            "## D7 Prevention",
            "",
            facts["d7"],
            "",
            "## D8 Closure",
            "",
            facts["d8"],
            "",
            "## Options",
            "",
            option_contain,
            "",
            "Option B. Widen the pull before a field action. No second cost is estimated in this file. "
            "Risk: the invalids continue while the team waits.",
            "",
            "## Recommendation",
            "",
            facts["recommendation"],
            "",
            "## Ask",
            "",
            "Approve the recommendation this week, or send the case back for the wider pull. "
            "Do not treat the projected rate as observed follow-up.",
            "",
        ]
    )


def closeout_node(state: CaseState) -> dict[str, Any]:
    facts = build_closeout_facts(state)
    markdown = render_closeout(facts)
    checked = check_narrative(markdown, facts)
    if not checked.ok:
        raise RuntimeError(f"close-out failed the fidelity guard: {checked.unknown}")
    out = Path(state["out_dir"]) if state.get("out_dir") else Path("out")
    out.mkdir(parents=True, exist_ok=True)
    (out / "closeout.md").write_text(markdown, encoding="utf-8")
    deck_path = write_deck(out / "exec_deck.pptx", facts)
    capa = dict(state.get("capa") or {})
    capa["d7_prevention"] = facts["d7"]
    capa["d8_closure"] = facts["d8"]
    capa["preliminary_close"] = False
    previous = str(capa.get("markdown") or "")
    capa["markdown"] = previous.rstrip() + "\n\n" + markdown
    record = {key: value for key, value in facts.items() if key != "chart"}
    record["fidelity_ok"] = checked.ok
    record["deck_path"] = str(deck_path)
    return {"closeout": record, "capa": capa, "deck_path": str(deck_path)}
