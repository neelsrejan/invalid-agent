"""Build the investigation frame from Postgres, or from the seeded generator."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

_LOG = logging.getLogger(__name__)

from invalid_agent.data.mapping import case_by_id


class DataUnavailable(RuntimeError):
    """The openFDA case cannot run because the hosted table is not configured."""


def load_frame(scenario: dict[str, Any]) -> pd.DataFrame:
    """Return the case frame. Synthetic cases never open a database connection."""
    backend = str(scenario.get("data_backend") or "synthetic")
    if backend == "synthetic":
        from invalid_agent.sim.generate import generate

        frame = generate(scenario)
        frame.attrs["data_backend"] = "synthetic"
        frame.attrs["spec_estimable"] = True
        frame.attrs["denominator"] = "synthetic_runs"
        return frame
    if backend == "openfda":
        return load_openfda_frame(scenario)
    raise DataUnavailable(
        f"Unknown data_backend {backend!r}. Use synthetic or openfda."
    )


def load_openfda_frame(scenario: dict[str, Any]) -> pd.DataFrame:
    case_id = str(scenario.get("id") or "")
    case = case_by_id(case_id)
    product_code = str(scenario.get("product_code") or case["product_code"])
    date_from = str(scenario.get("date_from") or case["date_from"])
    date_to = str(scenario.get("date_to") or case["date_to"])
    try:
        records = _query_case_rows(product_code, date_from, date_to)
    except Exception as exc:
        if not _missing_problem_source(exc):
            raise
        if case_id != "openfda_jje":
            raise DataUnavailable(
                f"The MAUDE query has no product_problems for {case_id or product_code}."
            ) from exc
        _LOG.warning(
            "MAUDE query has no product_problems; using the cached JJE extract (%s)",
            type(exc).__name__,
        )
        records = _cached_jje_records()
    if not records:
        raise DataUnavailable(
            f"The MAUDE table has no rows for {product_code} between {date_from} and {date_to}. "
            "Load the cache with python -m invalid_agent.data.pipeline after OPENFDA_API_KEY and "
            "DATABASE_URL are set. This case does not invent rows."
        )
    return frame_from_reports(records, scenario)


def frame_from_reports(records: list[dict[str, Any]], scenario: dict[str, Any]) -> pd.DataFrame:
    """Map report rows onto the columns the weekly loop already knows.

    Lot, operator, and software are often blank in MAUDE. Blank values become
    ``UNREPORTED`` and the ranker ignores that level. Manufacturer and brand
    are the strata that can actually move.
    """
    from invalid_agent.data.manufacturers import anonymized, display_labels, relabel

    start = pd.Timestamp(str(scenario.get("date_from") or scenario.get("start_date") or "2022-01-01"))
    rows: list[dict[str, Any]] = []
    for record in records:
        received = pd.Timestamp(record["date_received"])
        event_raw = record.get("date_of_event")
        event_date = pd.Timestamp(event_raw) if event_raw else pd.NaT
        chart_date = received
        basis = "date_received"
        lot = str(record.get("lot_number") or "").strip() or "UNREPORTED"
        brand = str(record.get("brand_name") or "").strip() or "UNREPORTED"
        operator = str(record.get("device_operator") or "").strip() or "UNREPORTED"
        catalog = str(record.get("catalog_number") or "").strip() or "UNREPORTED"
        problems = _problem_values(record.get("product_problems"))
        if problems:
            from invalid_agent.data.mapping import primary_invalid_code

            invalid_code = primary_invalid_code(problems)
            is_invalid = bool(invalid_code)
        else:
            raw_code = record.get("invalid_code")
            invalid_code = "" if raw_code is None or (isinstance(raw_code, float) and pd.isna(raw_code)) else str(raw_code).strip()
            if invalid_code.casefold() == "nan":
                invalid_code = ""
            if record.get("is_invalid_type") is None:
                is_invalid = bool(invalid_code)
            else:
                is_invalid = bool(record.get("is_invalid_type"))
        rows.append(
            {
                "run_id": str(record["mdr_report_key"]),
                "date": chart_date,
                "date_of_event": event_date,
                "date_basis": basis,
                "day_index": int((chart_date.normalize() - start.normalize()).days),
                "customer": str(record.get("manufacturer_name") or "UNREPORTED"),
                "site": "PUBLIC-MAUDE",
                "instrument": brand,
                "reagent_lot": lot,
                "software_version": "UNREPORTED",
                "operator": operator,
                "manufacturer": str(record.get("manufacturer_name") or "UNREPORTED"),
                "brand_name": brand,
                "catalog_number": catalog,
                "product_code": str(record.get("product_code") or ""),
                "event_type": str(record.get("event_type") or ""),
                "invalid": is_invalid,
                "invalid_code": invalid_code if is_invalid else "",
                "product_problems": [str(item) for item in problems] if isinstance(problems, list) else [],
            }
        )
    frame = pd.DataFrame(rows)
    enabled = anonymized()
    labels = display_labels(frame["manufacturer"].astype(str).tolist())
    if enabled and labels:
        frame["manufacturer"] = [relabel(str(value), labels, enabled=True) for value in frame["manufacturer"]]
        frame["customer"] = [relabel(str(value), labels, enabled=True) for value in frame["customer"]]
    frame.attrs["scenario_id"] = str(scenario.get("id", "openfda"))
    frame.attrs["data_backend"] = "openfda"
    frame.attrs["denominator"] = "reported_events"
    frame.attrs["spec_estimable"] = False
    frame.attrs["manufacturer_display"] = "anonymized" if enabled else "real"
    frame.attrs["date_basis_note"] = (
        "Weekly bins use the FDA received date, which is when the report was logged."
    )
    return frame


def _query_case_rows(product_code: str, date_from: str, date_to: str) -> list[dict[str, Any]]:
    from invalid_agent.config import load_settings
    from invalid_agent.data.db import connect, query_url
    from invalid_agent.data.query import CASE_ROWS_SQL, assert_readonly_sql

    settings = load_settings()
    public = settings.data_backend == "openfda"
    url = query_url(settings, public=public)
    sql = assert_readonly_sql(CASE_ROWS_SQL)
    conn = connect(url, readonly=True)
    try:
        cursor = conn.execute(
            sql,
            {"product_code": product_code, "date_from": date_from, "date_to": date_to},
        )
        columns = [item[0] for item in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def _problem_values(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text or text.casefold() == "nan":
            return []
        return [part.strip() for part in text.split("|") if part.strip()]
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _missing_problem_source(exc: BaseException) -> bool:
    text = str(exc).casefold()
    return "product_problems" in text or "maude_problem" in text


def _cached_jje_records() -> list[dict[str, Any]]:
    from invalid_agent.data.cache import read_rows

    cached = read_rows("openfda_jje")
    if cached:
        _LOG.warning("cached JJE extract: data/cache/openfda/openfda_jje.jsonl (%s rows)", len(cached))
        return cached
    fixture = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "openfda_jje.csv"
    if not fixture.is_file():
        _LOG.warning("cached JJE extract is missing")
        return []
    raw = pd.read_csv(fixture, dtype=str).fillna("")
    _LOG.warning("cached JJE extract: %s (%s rows)", fixture, len(raw))
    return raw.to_dict(orient="records")
