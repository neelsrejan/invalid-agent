"""Load the on-disk MAUDE cache into Postgres and create the read-only role.

This command does not call openFDA. If the cache is missing it stops and
names the extract command.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

from invalid_agent.config import load_settings
from invalid_agent.data.cache import cache_root, is_complete, read_meta, read_rows, case_paths
from invalid_agent.data.db import connect, normalize_url
from invalid_agent.data.mapping import CASES, READONLY_ROLE

DENOMINATOR_NOTE = (
    "Each row is one openFDA device-event report. "
    "is_invalid_type is the invalid-type numerator. "
    "The denominator is reports in the extract, not test runs. "
    "The 2% run-level invalid cap is not estimable from this table."
)

MISSING_CACHE_MESSAGE = (
    "No complete openFDA cache was found under data/cache/openfda.\n"
    "Run python -m invalid_agent.data.extract first. That command needs OPENFDA_API_KEY "
    "and is the only step that calls openFDA.\n"
    "This loader only reads the cache and writes Postgres."
)


def schema_sql() -> str:
    return (Path(__file__).resolve().parent / "schema.sql").read_text(encoding="utf-8")


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


def apply_schema(conn) -> None:
    for statement in sql_statements(schema_sql()):
        conn.execute(statement)


def sql_statements(script: str) -> list[str]:
    """Split a simple DDL script. The schema file has no semicolons inside literals."""
    parts: list[str] = []
    for chunk in script.split(";"):
        lines = [line for line in chunk.splitlines() if not line.strip().startswith("--")]
        text = "\n".join(lines).strip()
        if text:
            parts.append(text)
    return parts


def replace_rows(conn, rows: list[dict[str, Any]]) -> int:
    from invalid_agent.data.mapping import INVALID_LABELS, normalize_label

    conn.execute("TRUNCATE maude_problem, maude_report")
    report_sql = """
        INSERT INTO maude_report (
            mdr_report_key, product_code, date_received, date_of_event, event_type,
            manufacturer_name, manufacturer_raw, brand_name, generic_name, model_number,
            catalog_number, lot_number, device_operator, is_invalid_type, invalid_code
        ) VALUES (
            %(mdr_report_key)s, %(product_code)s, %(date_received)s, %(date_of_event)s, %(event_type)s,
            %(manufacturer_name)s, %(manufacturer_raw)s, %(brand_name)s, %(generic_name)s, %(model_number)s,
            %(catalog_number)s, %(lot_number)s, %(device_operator)s, %(is_invalid_type)s, %(invalid_code)s
        )
    """
    problem_sql = """
        INSERT INTO maude_problem (mdr_report_key, product_problem, invalid_code)
        VALUES (%(mdr_report_key)s, %(product_problem)s, %(invalid_code)s)
        ON CONFLICT DO NOTHING
    """
    loaded = 0
    with conn.cursor() as cur:
        for row in rows:
            key = str(row.get("mdr_report_key") or "").strip()
            received = _parse_date(row.get("date_received"))
            if not key or received is None:
                continue
            invalid_code = str(row.get("invalid_code") or "")
            cur.execute(
                report_sql,
                {
                    "mdr_report_key": key,
                    "product_code": str(row.get("product_code") or ""),
                    "date_received": received,
                    "date_of_event": _parse_date(row.get("date_of_event")),
                    "event_type": str(row.get("event_type") or ""),
                    "manufacturer_name": str(row.get("manufacturer_name") or "UNREPORTED"),
                    "manufacturer_raw": str(row.get("manufacturer_raw") or ""),
                    "brand_name": str(row.get("brand_name") or ""),
                    "generic_name": str(row.get("generic_name") or ""),
                    "model_number": str(row.get("model_number") or ""),
                    "catalog_number": str(row.get("catalog_number") or ""),
                    "lot_number": str(row.get("lot_number") or ""),
                    "device_operator": str(row.get("device_operator") or ""),
                    "is_invalid_type": bool(invalid_code),
                    "invalid_code": invalid_code,
                },
            )
            for label in row.get("product_problems") or []:
                cur.execute(
                    problem_sql,
                    {
                        "mdr_report_key": key,
                        "product_problem": str(label),
                        "invalid_code": INVALID_LABELS.get(normalize_label(str(label)), ""),
                    },
                )
            loaded += 1
    return loaded


def write_manifest(conn, *, api_calls: int, report_count: int, cache: str) -> None:
    windows = [(case["date_from"], case["date_to"]) for case in CASES]
    start = min(date.fromisoformat(item[0]) for item in windows)
    end = max(date.fromisoformat(item[1]) for item in windows)
    codes = ",".join(case["product_code"] for case in CASES)
    conn.execute("DELETE FROM load_manifest WHERE id = 1")
    conn.execute(
        """
        INSERT INTO load_manifest (
            id, extracted_at, api_calls, report_count, product_codes,
            window_start, window_end, denominator, cache_dir, note
        ) VALUES (1, now(), %(api_calls)s, %(report_count)s, %(product_codes)s,
                  %(window_start)s, %(window_end)s, %(denominator)s, %(cache_dir)s, %(note)s)
        """,
        {
            "api_calls": api_calls,
            "report_count": report_count,
            "product_codes": codes,
            "window_start": start,
            "window_end": end,
            "denominator": "reported_events",
            "cache_dir": cache,
            "note": DENOMINATOR_NOTE,
        },
    )


def ensure_readonly_role(conn, password: str) -> None:
    from psycopg import sql

    if not password:
        raise SystemExit(
            "DEMO_READONLY_PASSWORD is empty. Choose a password, export it, and rerun the loader. "
            f"The loader creates the login role {READONLY_ROLE} with default_transaction_read_only=on "
            "and SELECT on the MAUDE tables. The public demo uses that role, not the admin URL."
        )
    exists = conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (READONLY_ROLE,)).fetchone()
    password_sql = sql.SQL("PASSWORD {}").format(sql.Literal(password))
    if exists:
        conn.execute(sql.SQL("ALTER ROLE {} WITH LOGIN {}").format(sql.Identifier(READONLY_ROLE), password_sql))
    else:
        conn.execute(sql.SQL("CREATE ROLE {} LOGIN {}").format(sql.Identifier(READONLY_ROLE), password_sql))
    conn.execute(
        sql.SQL("ALTER ROLE {} SET default_transaction_read_only = on").format(sql.Identifier(READONLY_ROLE))
    )
    database = conn.execute("SELECT current_database()").fetchone()[0]
    conn.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(database), sql.Identifier(READONLY_ROLE))
    )
    conn.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(READONLY_ROLE)))
    conn.execute(
        sql.SQL("GRANT SELECT ON maude_report, maude_problem, load_manifest TO {}").format(
            sql.Identifier(READONLY_ROLE)
        )
    )
    conn.execute(sql.SQL("REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM {}").format(
        sql.Identifier(READONLY_ROLE)
    ))


def readonly_url_from(admin_url: str, password: str) -> str:
    parts = urlsplit(normalize_url(admin_url))
    host = parts.hostname or ""
    if ":" in host:
        host = f"[{host}]"
    netloc = f"{READONLY_ROLE}:{quote(password, safe='')}@{host}"
    if parts.port:
        netloc += f":{parts.port}"
    query = parts.query or "sslmode=require"
    if "sslmode=" not in query:
        query = query + "&sslmode=require"
    return urlunsplit(("postgresql", netloc, parts.path, query, ""))


def load_cache(conn, root: Path | None = None) -> dict[str, Any]:
    folder = root or cache_root()
    missing = [case["id"] for case in CASES if not is_complete(case["id"], folder)]
    if missing:
        raise SystemExit(MISSING_CACHE_MESSAGE + f"\nMissing complete cache for: {', '.join(missing)}")
    rows: list[dict[str, Any]] = []
    api_calls = 0
    for case in CASES:
        rows.extend(read_rows(case["id"], folder))
        _jsonl, meta_path = case_paths(case["id"], folder)
        meta = read_meta(meta_path) or {}
        api_calls += int(meta.get("pages") or 0)
    apply_schema(conn)
    loaded = replace_rows(conn, rows)
    write_manifest(conn, api_calls=api_calls, report_count=loaded, cache=str(folder))
    return {"loaded": loaded, "api_calls_recorded_as_pages": api_calls}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Load the MAUDE cache into Postgres and create the read-only role.")
    parser.parse_args(argv)
    settings = load_settings()
    if not settings.database_url:
        raise SystemExit(
            "DATABASE_URL is missing. Create a free Neon project, copy the pooled connection string "
            "(include sslmode=require), export it as DATABASE_URL, and rerun. "
            "The loader does not embed a host or a password."
        )
    conn = connect(settings.database_url, readonly=False)
    try:
        summary = load_cache(conn)
        ensure_readonly_role(conn, settings.demo_readonly_password)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    printed = readonly_url_from(settings.database_url, settings.demo_readonly_password)
    print(f"Loaded {summary['loaded']} reports.")
    print("Set this Streamlit secret and do not commit it:")
    print(f"DATABASE_URL_READONLY={printed}")


if __name__ == "__main__":
    main()
