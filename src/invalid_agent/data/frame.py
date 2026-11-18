"""Build the investigation frame from Postgres, or from the seeded generator."""

from __future__ import annotations

from typing import Any

import pandas as pd

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
    from invalid_agent.config import load_settings
    from invalid_agent.data.db import connect, query_url
    from invalid_agent.data.query import CASE_ROWS_SQL, assert_readonly_sql

    case_id = str(scenario.get("id") or "")
    case = case_by_id(case_id)
    product_code = str(scenario.get("product_code") or case["product_code"])
    date_from = str(scenario.get("date_from") or case["date_from"])
    date_to = str(scenario.get("date_to") or case["date_to"])
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
        records = [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()
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
        if event_raw:
            chart_date = pd.Timestamp(event_raw)
            basis = "date_of_event"
        else:
            chart_date = received
            basis = "date_received"
        lot = str(record.get("lot_number") or "").strip() or "UNREPORTED"
        brand = str(record.get("brand_name") or "").strip() or "UNREPORTED"
        operator = str(record.get("device_operator") or "").strip() or "UNREPORTED"
        catalog = str(record.get("catalog_number") or "").strip() or "UNREPORTED"
        invalid_code = str(record.get("invalid_code") or "")
        rows.append(
            {
                "run_id": str(record["mdr_report_key"]),
                "date": chart_date,
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
                "invalid": bool(record.get("is_invalid_type")),
                "invalid_code": invalid_code if record.get("is_invalid_type") else "",
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
        "Weekly bins use date_of_event when the report has one. "
        "Otherwise they use the FDA received date, which is when the report was logged, "
        "not when the run happened."
    )
    return frame
