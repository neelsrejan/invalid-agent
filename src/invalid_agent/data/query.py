"""Vetted read-only SQL. The model may pick a template. It may not write SQL.

Python computes rates, Wilson intervals, and the p-chart from the rows the
template returns. The language model only narrates those facts.
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any

from invalid_agent.data.mapping import CASES, case_by_product
from invalid_agent.metrics.rates import wilson_interval
from invalid_agent.metrics.spc import control_limits, western_electric

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|copy|truncate|comment|vacuum|execute|call|do|into)\b",
    re.IGNORECASE,
)

CASE_ROWS_SQL = """
SELECT
    mdr_report_key,
    product_code,
    date_received,
    event_type,
    manufacturer_name,
    brand_name,
    generic_name,
    model_number,
    catalog_number,
    lot_number,
    device_operator,
    is_invalid_type,
    invalid_code
FROM maude_report
WHERE product_code = %(product_code)s
  AND date_received >= %(date_from)s
  AND date_received <= %(date_to)s
"""

TEMPLATES: dict[str, dict[str, Any]] = {
    "case_overview": {
        "question": "What is the invalid-type share of reports for this product code, and what can it not say about the 2% promise?",
        "sql": """
            SELECT
                COUNT(*)::int AS n,
                COUNT(*) FILTER (WHERE is_invalid_type)::int AS k
            FROM maude_report
            WHERE product_code = %(product_code)s
              AND date_received >= %(date_from)s
              AND date_received <= %(date_to)s
        """,
    },
    "invalid_share_by_manufacturer": {
        "question": "Which manufacturer has the highest invalid-type share of its own reports?",
        "sql": """
            SELECT
                manufacturer_name AS level,
                COUNT(*)::int AS n,
                COUNT(*) FILTER (WHERE is_invalid_type)::int AS k
            FROM maude_report
            WHERE product_code = %(product_code)s
              AND date_received >= %(date_from)s
              AND date_received <= %(date_to)s
            GROUP BY manufacturer_name
            ORDER BY n DESC
        """,
    },
    "invalid_share_by_brand": {
        "question": "Which brand has the highest invalid-type share of its own reports?",
        "sql": """
            SELECT
                COALESCE(NULLIF(brand_name, ''), 'UNREPORTED') AS level,
                COUNT(*)::int AS n,
                COUNT(*) FILTER (WHERE is_invalid_type)::int AS k
            FROM maude_report
            WHERE product_code = %(product_code)s
              AND date_received >= %(date_from)s
              AND date_received <= %(date_to)s
            GROUP BY 1
            ORDER BY n DESC
        """,
    },
    "invalid_type_counts": {
        "question": "Which invalid type is the largest slice of invalid-type reports?",
        "sql": """
            SELECT
                COALESCE(NULLIF(invalid_code, ''), 'NOT_INVALID') AS level,
                COUNT(*)::int AS n,
                COUNT(*) FILTER (WHERE is_invalid_type)::int AS k
            FROM maude_report
            WHERE product_code = %(product_code)s
              AND date_received >= %(date_from)s
              AND date_received <= %(date_to)s
            GROUP BY 1
            ORDER BY k DESC, n DESC
        """,
    },
    "weekly_counts": {
        "question": "Do the weekly invalid-type shares show a Western Electric rule 1 point?",
        "sql": """
            SELECT
                to_char(date_trunc('week', date_received::timestamp), 'YYYY-MM-DD') AS period,
                COUNT(*)::int AS n,
                COUNT(*) FILTER (WHERE is_invalid_type)::int AS k
            FROM maude_report
            WHERE product_code = %(product_code)s
              AND date_received >= %(date_from)s
              AND date_received <= %(date_to)s
            GROUP BY 1
            ORDER BY 1
        """,
    },
}

SUGGESTED_QUESTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "ooi_share",
        "label": "OOI share versus the 2% promise",
        "text": "What share of OOI reports are an invalid type, and how does that compare with the 2% run-level promise?",
        "template_id": "case_overview",
        "params": {"product_code": "OOI"},
    },
    {
        "id": "jje_manufacturer",
        "label": "JJE manufacturers",
        "text": "Which manufacturer of JJE chemistry analyzers has the highest invalid-type share of its reports?",
        "template_id": "invalid_share_by_manufacturer",
        "params": {"product_code": "JJE"},
    },
    {
        "id": "ooi_types",
        "label": "OOI invalid types",
        "text": "Which invalid type is the largest slice of OOI invalid-type reports?",
        "template_id": "invalid_type_counts",
        "params": {"product_code": "OOI"},
    },
    {
        "id": "jje_weeks",
        "label": "JJE weekly chart",
        "text": "Do JJE weekly invalid-type shares show a Western Electric rule 1 point in 2024?",
        "template_id": "weekly_counts",
        "params": {"product_code": "JJE"},
    },
)


def assert_readonly_sql(sql: str) -> str:
    """Reject anything that is not one SELECT or WITH statement."""
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        raise ValueError("empty SQL")
    if ";" in stripped:
        raise ValueError("only one SQL statement is allowed")
    if "--" in stripped or "/*" in stripped:
        raise ValueError("SQL comments are not allowed")
    if not re.match(r"(?is)^(select|with)\b", stripped):
        raise ValueError("only a SELECT is allowed")
    if _FORBIDDEN.search(stripped):
        raise ValueError("statement is not read-only")
    return stripped


def default_params(product_code: str) -> dict[str, str]:
    case = case_by_product(product_code)
    return {
        "product_code": case["product_code"],
        "date_from": case["date_from"],
        "date_to": case["date_to"],
    }


def validate_params(raw: dict[str, Any] | None) -> dict[str, str]:
    raw = dict(raw or {})
    product_code = str(raw.get("product_code") or "").strip().upper()
    try:
        case = case_by_product(product_code)
    except KeyError as exc:
        raise ValueError(str(exc)) from exc
    date_from = str(raw.get("date_from") or case["date_from"])
    date_to = str(raw.get("date_to") or case["date_to"])
    start = date.fromisoformat(date_from)
    end = date.fromisoformat(date_to)
    window_start = date.fromisoformat(case["date_from"])
    window_end = date.fromisoformat(case["date_to"])
    if start < window_start or end > window_end or start > end:
        raise ValueError(
            f"dates {date_from}..{date_to} are outside the extracted window "
            f"{case['date_from']}..{case['date_to']} for {case['product_code']}"
        )
    return {"product_code": case["product_code"], "date_from": date_from, "date_to": date_to}


def choose_template(question: str, llm: Any | None = None) -> dict[str, Any]:
    """Pick a template id and params. A model that returns anything else is ignored."""
    if llm is not None and getattr(llm, "name", "deterministic") != "deterministic":
        try:
            drafted = llm.complete(
                system=(
                    "You choose one analysis template. Reply with a JSON object only, "
                    'of the form {"template_id": "...", "params": {"product_code": "OOI"}}. '
                    "template_id must be one of: "
                    + ", ".join(TEMPLATES)
                    + ". product_code must be OOI or JJE. Do not write SQL. Do not invent numbers."
                ),
                user=question,
                temperature=0.0,
            )
            choice = _parse_choice(drafted)
            if choice is not None:
                choice["source"] = llm.name
                return choice
        except Exception:
            pass
    matched = match_question(question)
    matched["source"] = "keyword"
    return matched


def _parse_choice(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    payload = json.loads(text[start : end + 1])
    template_id = str(payload.get("template_id") or "")
    if template_id not in TEMPLATES:
        return None
    params = validate_params(payload.get("params") or {})
    return {"template_id": template_id, "params": params}


def match_question(question: str) -> dict[str, Any]:
    text = question.casefold()
    product = "JJE" if "jje" in text or "chemistry" in text else "OOI"
    if "ooi" in text or "nucleic" in text or "multiplex" in text:
        product = "OOI"
    if "week" in text or "control chart" in text or "western" in text or "spc" in text:
        template_id = "weekly_counts"
    elif "brand" in text:
        template_id = "invalid_share_by_brand"
    elif "manufacturer" in text or "roche" in text or "abbott" in text:
        template_id = "invalid_share_by_manufacturer"
    elif "slice" in text or "pareto" in text or "which invalid type" in text:
        template_id = "invalid_type_counts"
    else:
        template_id = "case_overview"
    return {"template_id": template_id, "params": default_params(product)}


def execute_template(conn, template_id: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    if template_id not in TEMPLATES:
        raise ValueError(f"unknown template {template_id}")
    sql = assert_readonly_sql(TEMPLATES[template_id]["sql"])
    bound = validate_params(params)
    cursor = conn.execute(sql, bound)
    columns = [item[0] for item in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def compute_answer(template_id: str, rows: list[dict[str, Any]], params: dict[str, str]) -> dict[str, Any]:
    """Rates and the control chart. No model arithmetic."""
    from invalid_agent.config import PROMISED_VALIDITY, SPEC_INVALID_RATE

    enriched: list[dict[str, Any]] = []
    for row in rows:
        n = int(row.get("n") or 0)
        k = int(row.get("k") or 0)
        if n > 0 and k > n:
            raise ValueError("template returned k greater than n")
        low, high = wilson_interval(k, n) if n else (0.0, 0.0)
        enriched.append(
            {
                **{key: row[key] for key in row if key not in {"n", "k"}},
                "n": n,
                "k": k,
                "rate": (k / n) if n else 0.0,
                "ci_low": low,
                "ci_high": high,
            }
        )
    spc = _weekly_spc(enriched) if template_id == "weekly_counts" else None
    if template_id == "case_overview" and enriched:
        head = enriched[0]
    elif enriched:
        ranked = sorted(enriched, key=lambda item: (-item["rate"], -item["k"], str(item.get("level", ""))))
        head = ranked[0]
    else:
        head = {"n": 0, "k": 0, "rate": 0.0, "ci_low": 0.0, "ci_high": 0.0}
    return {
        "template_id": template_id,
        "product_code": params["product_code"],
        "date_from": params["date_from"],
        "date_to": params["date_to"],
        "spec_invalid_rate": SPEC_INVALID_RATE,
        "promised_validity": PROMISED_VALIDITY,
        "confidence": 0.95,
        "spec_estimable": False,
        "denominator": "reported_events",
        "denominator_note": (
            "Share of device-event reports whose product_problems map to an invalid type. "
            "Not a count of test runs. The 2% cap is the stated promise and is not estimable here."
        ),
        "rows": enriched,
        "head": head,
        "spc": spc,
        "known_cases": [case["product_code"] for case in CASES],
    }


def _weekly_spc(rows: list[dict[str, Any]]) -> dict[str, Any]:
    points = []
    for row in rows:
        n = int(row["n"])
        if n <= 0:
            continue
        points.append({"period": str(row.get("period")), "n": n, "k": int(row["k"]), "p": row["rate"]})
    total_n = sum(point["n"] for point in points)
    total_k = sum(point["k"] for point in points)
    p_bar = (total_k / total_n) if total_n else 0.0
    for point in points:
        _lcl, _ucl, se = control_limits(p_bar, point["n"])
        point["z"] = ((point["p"] - p_bar) / se) if se > 0 else 0.0
    violations = western_electric([point["z"] for point in points])
    rule1 = sum(1 for hit in violations if hit["rule"] == 1)
    return {"p_bar": p_bar, "points": len(points), "rule1_count": rule1, "violation_count": len(violations)}


def answer_question(question: str, conn, llm: Any | None = None, choice: dict[str, Any] | None = None) -> dict[str, Any]:
    from invalid_agent.llm import narrate

    picked = choice or choose_template(question, llm)
    params = validate_params(picked.get("params") or {})
    template_id = str(picked["template_id"])
    rows = execute_template(conn, template_id, params)
    facts = compute_answer(template_id, rows, params)
    facts["question"] = question
    prose, fidelity = narrate("data_answer", facts, llm)
    return {
        "template_id": template_id,
        "params": params,
        "source": picked.get("source", "given"),
        "facts": facts,
        "prose": prose,
        "fidelity": fidelity,
    }
