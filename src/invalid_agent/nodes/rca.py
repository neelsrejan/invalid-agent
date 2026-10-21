"""Fishbone, 5 Whys, and an 8D/CAPA record.

The ranking comes from ``rank_hypotheses``. A Why step that does not cite
an evidence-catalog id is a hard error. Injections are citations only
after their week has arrived; they never create a score.
"""

from __future__ import annotations

from typing import Any

from invalid_agent.case.schemas import CAPA8D, Fishbone, FishboneBranch, FiveWhys, WhyStep
from invalid_agent.case.state import CaseState
from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.metrics.hypotheses import evidence_catalog, rank_hypotheses
from invalid_agent.sim.generate import generate

_BRANCH_SPECS = (
    ("bad_reagent_lot", "Material", "reagent_lot"),
    ("preanalytical_hemolysis", "Material", "hil_band"),
    ("drifting_instrument", "Machine", "instrument"),
    ("software_version", "Method", "software_version"),
    ("user_process_error", "Man", "operator"),
    ("site_temperature", "Environment", "temp_band"),
    ("measurement_system", "Measurement", None),
)

_CONTAINMENT = {
    "bad_reagent_lot": (
        "Quarantine the implicated lot and stop further shipments of that lot. "
        "Other lots that stayed inside the spec can keep running."
    ),
    "drifting_instrument": (
        "Take the implicated instrument out of service and move its queue to the other instruments."
    ),
    "site_temperature": (
        "Hold the shipping lane that produced the excursion and quarantine the loads on that lane."
    ),
    "software_version": (
        "Pin the instruments back to the software version that stayed inside the spec."
    ),
    "preanalytical_hemolysis": (
        "Stop reporting results for high-index specimens from the implicated site and request redraws."
    ),
    "user_process_error": (
        "Remove the implicated operator from the assay until retraining and a supervised run are done."
    ),
    "no_single_cause": (
        "Do not quarantine a lot or an instrument on this evidence. Widen the data pull before a field action."
    ),
    "measurement_system": (
        "No measurement-system action. This branch did not clear the evidence bar."
    ),
}

_CORRECTIVE = {
    "bad_reagent_lot": "Disposition the lot, and add a field sentinel to release testing for the failure code that dominated.",
    "drifting_instrument": "Service the instrument and require a passing control run before it returns to the queue.",
    "site_temperature": "Add a lane sensor alarm and a receiving check for that shipper.",
    "software_version": "Roll the version back in the field and gate the next build on the invalid-rate spec.",
    "preanalytical_hemolysis": "Add a hemolysis-index hold at the implicated site before the panel is run.",
    "user_process_error": "Retrain the operator and add the step they missed to the competency check.",
    "no_single_cause": "Keep the investigation open. Do not write a single-cause corrective action.",
    "measurement_system": "No corrective action on the measurement system.",
}


def index_injections(scenario: dict[str, Any], week: int) -> dict[str, str]:
    """Injections whose week has arrived, keyed so a citation can point at them."""
    catalog: dict[str, str] = {}
    for inj in scenario.get("injections") or []:
        if int(inj["week"]) > week:
            continue
        source = str(inj["source"]).lower().replace(" ", "_")
        base = f"injection:{int(inj['week'])}:{source}"
        key = base
        suffix = 2
        while key in catalog:
            key = f"{base}:{suffix}"
            suffix += 1
        catalog[key] = " ".join(str(inj.get("text", "")).split())
    return catalog


def validate_whys(steps: list[dict[str, Any]], catalog: dict[str, str]) -> None:
    """Raise if any step has an empty citation list or an id that is not in the catalog."""
    errors: list[str] = []
    for step in steps:
        citations = list(step.get("citations") or [])
        if not citations:
            errors.append(f"why {step.get('number')} has no citation")
            continue
        for citation in citations:
            if citation not in catalog:
                errors.append(f"why {step.get('number')} cites unknown id {citation}")
    if errors:
        raise ValueError("; ".join(errors))


def _by_cause(hypotheses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["cause"]: item for item in hypotheses if item.get("cause") not in {None, "no_single_cause"}}


def build_fishbone(
    hypotheses: list[dict[str, Any]],
    catalog: dict[str, str],
    injections: dict[str, str],
) -> dict[str, Any]:
    found = _by_cause(hypotheses)
    branches: list[dict[str, Any]] = []
    for cause, category, column in _BRANCH_SPECS:
        hit = found.get(cause)
        if hit is None:
            statement = "This branch did not clear the evidence bar."
            evidence_for: list[str] = []
            score = 0.0
        else:
            rate_id = f"metric:{hit['column']}:{hit['level']}:rate"
            statement = catalog.get(rate_id, hit.get("summary", cause))
            evidence_for = [item for item in hit.get("evidence_ids") or [] if item in catalog]
            score = float(hit["score"])
        evidence_against = _against(cause, hit, catalog, injections)
        branches.append(
            {
                "category": category,
                "cause": cause,
                "statement": statement,
                "evidence_for": evidence_for,
                "evidence_against": evidence_against,
                "score": round(score, 2),
                "column": column,
            }
        )
    branches.sort(key=lambda row: (-row["score"], row["category"], row["cause"]))
    for index, branch in enumerate(branches, start=1):
        branch["rank"] = index
    return {"branches": branches}


def _against(
    cause: str,
    hit: dict[str, Any] | None,
    catalog: dict[str, str],
    injections: dict[str, str],
) -> list[str]:
    """Contrary citations: a release-pass note, or the overall rate for a branch that did not fire."""
    contrary = [
        key
        for key, text in injections.items()
        if "passed release" in text.lower() or "pass" in text.lower() and "release" in text.lower()
    ]
    if hit is not None and contrary and cause == "bad_reagent_lot":
        return contrary[:1]
    if hit is None and "metric:overall:rate" in catalog:
        return ["metric:overall:rate"]
    # The customer complaint does not name the stratum. That limits how hard we lean on it.
    customer = [key for key in injections if ":customer" in key]
    if hit is not None and customer:
        return customer[:1]
    if "metric:overall:spec" in catalog:
        return ["metric:overall:spec"]
    return []


def build_whys(
    hypotheses: list[dict[str, Any]],
    catalog: dict[str, str],
    injections: dict[str, str],
) -> dict[str, Any]:
    top = hypotheses[0]
    cause = str(top["cause"])
    if cause == "no_single_cause":
        steps = _whys_unresolved(catalog)
        terminal = "no_single_cause"
    else:
        steps = _whys_for_hit(top, catalog, injections)
        terminal = f"{cause}:{top.get('level')}"
    validate_whys(steps, catalog)
    return {"cause": cause, "terminal_cause": terminal, "steps": steps}


def _whys_for_hit(hit: dict[str, Any], catalog: dict[str, str], injections: dict[str, str]) -> list[dict[str, Any]]:
    rate_id = f"metric:{hit['column']}:{hit['level']}:rate"
    n_id = f"metric:{hit['column']}:{hit['level']}:n"
    mentioning = [key for key, text in injections.items() if str(hit.get("level")) in text]
    fourth_citation = mentioning[0] if mentioning else n_id
    fourth_answer = catalog[fourth_citation]
    terminal_answer = f"Stop at a lot-level cause. {catalog[rate_id]}" if hit["cause"] == "bad_reagent_lot" else (
        f"Stop at {hit['cause']} {hit['level']}. {catalog[rate_id]}"
    )
    # The instrument contrast is the highest instrument sentence that is not the winning column.
    contrast_id = _contrast_id(hit, catalog)
    steps = [
        {
            "number": 1,
            "question": "Why is the invalid rate above the promised validity?",
            "answer": f"{catalog['metric:overall:rate']} {catalog['metric:overall:spec']}",
            "citations": ["metric:overall:rate", "metric:overall:spec"],
        },
        {
            "number": 2,
            "question": "Why is that elevation concentrated instead of spread across the panel?",
            "answer": catalog[rate_id],
            "citations": [rate_id],
        },
        {
            "number": 3,
            "question": "Why is the next-best stratum not the cause?",
            "answer": catalog[contrast_id],
            "citations": [contrast_id],
        },
        {
            "number": 4,
            "question": "What in the record ties the timing or the complaint to this stratum?",
            "answer": fourth_answer,
            "citations": [fourth_citation],
        },
        {
            "number": 5,
            "question": "Why does the chain stop here?",
            "answer": terminal_answer,
            "citations": [rate_id],
        },
    ]
    return steps


def _contrast_id(hit: dict[str, Any], catalog: dict[str, str]) -> str:
    """Prefer a different column's rate sentence so the third Why is a real contrast."""
    prefix = f"metric:{hit['column']}:"
    for key in catalog:
        if key.endswith(":rate") and not key.startswith(prefix) and not key.startswith("metric:overall"):
            return key
    return "metric:overall:rate"


def _whys_unresolved(catalog: dict[str, str]) -> list[dict[str, Any]]:
    lot_key = _first_rate(catalog, "reagent_lot")
    instrument_key = _first_rate(catalog, "instrument")
    steps = [
        {
            "number": 1,
            "question": "Why is the invalid rate above the promised validity?",
            "answer": f"{catalog['metric:overall:rate']} {catalog['metric:overall:spec']}",
            "citations": ["metric:overall:rate", "metric:overall:spec"],
        },
        {
            "number": 2,
            "question": "Why is a reagent lot not the cause?",
            "answer": catalog[lot_key],
            "citations": [lot_key],
        },
        {
            "number": 3,
            "question": "Why is an instrument not the cause?",
            "answer": catalog[instrument_key],
            "citations": [instrument_key],
        },
        {
            "number": 4,
            "question": "Why is there no temperature or hemolysis call either?",
            "answer": catalog["spc:p_bar"],
            "citations": ["spc:p_bar"],
        },
        {
            "number": 5,
            "question": "Why does the chain stop here?",
            "answer": "Stop at no single cause. No stratum cleared the evidence bar.",
            "citations": ["metric:overall:rate"],
        },
    ]
    return steps


def _first_rate(catalog: dict[str, str], column: str) -> str:
    prefix = f"metric:{column}:"
    for key in catalog:
        if key.startswith(prefix) and key.endswith(":rate"):
            return key
    return "metric:overall:rate"


def build_capa(top: dict[str, Any], catalog: dict[str, str]) -> dict[str, Any]:
    cause = str(top["cause"])
    level = top.get("level") or "no single stratum"
    d4 = catalog.get(f"metric:{top.get('column')}:{level}:rate", catalog["metric:overall:rate"])
    if cause == "no_single_cause":
        d4 = "No single cause. " + catalog["metric:overall:rate"]
    record = CAPA8D(
        d1_team="PM leads. QA, R&D, Manufacturing, and Regulatory sit on the team. The customer is informed, not assigned actions.",
        d2_problem=catalog["metric:overall:rate"] + " " + catalog["metric:overall:spec"],
        d3_containment=_CONTAINMENT.get(cause, _CONTAINMENT["no_single_cause"]),
        d4_root_cause=d4,
        d5_corrective_action=_CORRECTIVE.get(cause, _CORRECTIVE["no_single_cause"]),
        d6_validation=(
            "Effectiveness metric: the invalid rate returns to the spec and the weekly p-chart shows no rule-1 point. "
            "Until follow-up runs exist, any before/after figure is a projection, not an observed cure."
        ),
        d7_prevention=(
            "Add the winning stratum to the routine SPC review and to incoming release for the dominant invalid code. "
            "Planned at this stage and confirmed at close-out."
        ),
        d8_closure=(
            "Recognize the team when the effectiveness metric passes. "
            "The record stays open until that check. Planned at this stage and confirmed at close-out."
        ),
        dmaic={
            "define": "D1 and D2",
            "measure": "Invalid rate, Wilson interval, strata, p-chart, Pareto",
            "analyze": "D4, fishbone, and 5 Whys",
            "improve": "D3 containment and D5 corrective action",
            "control": "D6 effectiveness metric and D7 prevention",
        },
        preliminary_close=True,
    )
    return record.model_dump()


def _markdown_fishbone(fishbone: dict[str, Any]) -> str:
    lines = [
        "# Fishbone",
        "",
        "**Simulation. Synthetic data. Not for clinical use.**",
        "",
        "Branches are the 6M set. Rank is by the evidence score. A branch that did not clear the bar stays on the diagram at score zero.",
        "",
    ]
    for branch in fishbone["branches"]:
        lines.append(
            f"## Rank {branch['rank']}. {branch['category']} — {branch['cause']}"
        )
        lines.append("")
        lines.append(branch["statement"])
        lines.append("")
        lines.append("Evidence for: " + (", ".join(branch["evidence_for"]) or "none."))
        lines.append("Evidence against: " + (", ".join(branch["evidence_against"]) or "none."))
        lines.append("")
    return "\n".join(lines)


def _markdown_whys(whys: dict[str, Any]) -> str:
    lines = [
        "# 5 Whys",
        "",
        "**Simulation. Synthetic data. Not for clinical use.**",
        "",
        f"Top call: {whys['cause']}. Terminal: {whys['terminal_cause']}.",
        "",
    ]
    for step in whys["steps"]:
        lines.append(f"## Why {step['number']}")
        lines.append("")
        lines.append(step["question"])
        lines.append("")
        lines.append(step["answer"])
        lines.append("")
        lines.append("Citations: " + ", ".join(step["citations"]) + ".")
        lines.append("")
    return "\n".join(lines)


def _markdown_capa(capa: dict[str, Any]) -> str:
    lines = [
        "# 8D / CAPA",
        "",
        "**Simulation. Synthetic data. Not for clinical use.**",
        "",
        "DMAIC labels: " + "; ".join(f"{key} = {value}" for key, value in capa["dmaic"].items()) + ".",
        "",
    ]
    for key, title in (
        ("d1_team", "D1 Team"),
        ("d2_problem", "D2 Problem"),
        ("d3_containment", "D3 Containment"),
        ("d4_root_cause", "D4 Root cause"),
        ("d5_corrective_action", "D5 Corrective action"),
        ("d6_validation", "D6 Validation"),
        ("d7_prevention", "D7 Prevention"),
        ("d8_closure", "D8 Closure"),
    ):
        lines.append(f"## {title}")
        lines.append("")
        lines.append(capa[key])
        lines.append("")
    if capa.get("preliminary_close"):
        lines.append("D7 and D8 are planned. Close-out confirms them.")
        lines.append("")
    return "\n".join(lines)


def rca_node(state: CaseState) -> dict[str, Any]:
    scenario = state["scenario"]
    week = int(state.get("week", 0))
    df = generate(scenario)
    spec = float(scenario.get("spec_invalid_rate", 0.02))
    promised = float(scenario.get("promised_validity", 0.98))
    hypotheses = state.get("hypotheses") or rank_hypotheses(df, spec)
    catalog = dict(state.get("evidence_catalog") or evidence_catalog(df, spec, promised))
    injections = index_injections(scenario, week)
    catalog.update(injections)
    fishbone = build_fishbone(hypotheses, catalog, injections)
    whys = build_whys(hypotheses, catalog, injections)
    capa = build_capa(hypotheses[0], catalog)
    fishbone["markdown"] = _markdown_fishbone(fishbone)
    whys["markdown"] = _markdown_whys(whys)
    capa["markdown"] = _markdown_capa(capa)
    # Schema check. A bad citation already raised in build_whys.
    Fishbone(branches=[FishboneBranch(**{k: b[k] for k in FishboneBranch.model_fields}) for b in fishbone["branches"]])
    FiveWhys(
        cause=whys["cause"],
        terminal_cause=whys["terminal_cause"],
        steps=[WhyStep(**step) for step in whys["steps"]],
    )
    combined = "\n".join([fishbone["markdown"], whys["markdown"], capa["markdown"]])
    # Level ids such as 2.4.0 are labels. They have to be in the facts as
    # strings so the fidelity scan does not read the version as a rate.
    labels = [str(item["level"]) for item in hypotheses if item.get("level")]
    for version in scenario.get("software_versions") or []:
        if isinstance(version, dict) and version.get("id"):
            labels.append(str(version["id"]))
    facts = {"catalog": catalog, "labels": labels, "structure": [0, 1, 2, 3, 4, 5, 6, 7, 8], "week": week}
    fidelity = check_narrative(combined, facts).to_dict()
    if not fidelity["ok"]:
        raise RuntimeError(f"RCA prose failed the fidelity guard: {fidelity['unknown']}")
    return {
        "hypotheses": hypotheses,
        "evidence_catalog": catalog,
        "fishbone": fishbone,
        "five_whys": whys,
        "capa": capa,
        "rca_fidelity": fidelity,
    }
