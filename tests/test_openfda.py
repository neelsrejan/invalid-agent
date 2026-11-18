"""MAUDE mapping, cache, SQL guard, and the weekly loop on a constructed frame.

Nothing in this file calls openFDA or a hosted database. The constructed
frame is not the extract.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import httpx
import pytest

from invalid_agent.data.extract import main as extract_main
from invalid_agent.data.extract import run_extract
from invalid_agent.data.frame import DataUnavailable, frame_from_reports
from invalid_agent.data.load import readonly_url_from, sql_statements, schema_sql
from invalid_agent.data.mapping import (
    MAX_API_CALLS,
    normalize_manufacturer,
    primary_invalid_code,
)
from invalid_agent.data.query import (
    TEMPLATES,
    assert_readonly_sql,
    choose_template,
    execute_template,
    match_question,
    validate_params,
)
from invalid_agent.llm import GroqLLM


def test_extract_refuses_to_start_without_a_key(monkeypatch):
    monkeypatch.delenv("OPENFDA_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="OPENFDA_API_KEY"):
        extract_main([])


def test_invalid_labels_keep_wrong_results_out_of_the_numerator():
    assert primary_invalid_code(["False Positive Result"]) == ""
    assert primary_invalid_code(["High Test Results", "Output Problem"]) == ""
    assert primary_invalid_code(["Unable to Obtain Readings"]) == "INV-NOR"
    assert primary_invalid_code(["Computer Software Problem", "Unable to Obtain Readings"]) == "INV-NOR"
    assert primary_invalid_code(["Mechanical Problem"]) == "INV-MECH"
    assert primary_invalid_code(["Calibration Problem"]) == "INV-CAL"


def test_manufacturer_names_collapse_punctuation_and_keep_distinct_firms():
    assert normalize_manufacturer("NORTH LAB") == "NORTH LAB"
    assert normalize_manufacturer("SOUTH  HEALTH INC.") == "SOUTH HEALTH"
    assert normalize_manufacturer("WEST ANALYZERS, INC.") == "WEST ANALYZERS"
    assert normalize_manufacturer("EAST, WEST & CO. (CITY)") == "EAST WEST"
    assert normalize_manufacturer("FIRM ONE, INC.") == "FIRM ONE"
    assert normalize_manufacturer("FIRM TWO") == "FIRM TWO"
    assert normalize_manufacturer("FIRM ONE, INC.") != normalize_manufacturer("FIRM TWO (GROUP)")


def test_extract_caches_and_refresh_is_the_only_second_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("INVALID_AGENT_CACHE", str(tmp_path))
    monkeypatch.setenv("OPENFDA_API_KEY", "test-key-not-real")
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        assert "test-key-not-real" in str(request.url)
        assert "api_key" not in request.url.path
        code = "JJE" if "JJE" in str(request.url) else "OOI"
        payload = {
            "meta": {"results": {"total": 1, "skip": 0, "limit": 1000}},
            "results": [
                {
                    "mdr_report_key": f"{code}-1",
                    "date_received": "20240601",
                    "date_of_event": "20240512",
                    "event_type": "Malfunction",
                    "product_problems": ["Unable to Obtain Readings", "Unable to Obtain Readings"],
                    "mdr_text": [{"text": "narrative that must not be stored"}],
                    "patient": [{"patient_sequence_number": "1"}],
                    "device": [
                        {
                            "device_report_product_code": code,
                            "manufacturer_d_name": "Firm North",
                            "brand_name": "brand-one",
                            "lot_number": "",
                        }
                    ],
                }
            ],
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    first = run_extract(client=client, api_key="test-key-not-real")
    assert first["api_calls"] == 2
    assert calls["n"] == 2
    cached = (tmp_path / "openfda_ooi.jsonl").read_text(encoding="utf-8")
    assert "narrative that must not be stored" not in cached
    assert "patient_sequence_number" not in cached
    second = run_extract(client=client, api_key="test-key-not-real")
    assert second["api_calls"] == 0
    assert calls["n"] == 2
    run_extract(refresh=True, client=client, api_key="test-key-not-real")
    assert calls["n"] == 4
    assert MAX_API_CALLS == 40


def test_sql_templates_are_single_selects_and_writes_are_rejected():
    for spec in TEMPLATES.values():
        assert_readonly_sql(spec["sql"])
    with pytest.raises(ValueError):
        assert_readonly_sql("SELECT 1; DROP TABLE maude_report")
    with pytest.raises(ValueError):
        assert_readonly_sql("DELETE FROM maude_report")
    with pytest.raises(ValueError):
        assert_readonly_sql("WITH moved AS (SELECT 1) INSERT INTO maude_report SELECT 1")
    statements = sql_statements(schema_sql())
    assert len(statements) >= 5
    assert any("maude_report" in statement for statement in statements)


def test_question_matcher_and_param_window():
    overview = match_question("What share of OOI reports are an invalid type versus the 2% promise?")
    assert overview["template_id"] == "case_overview"
    assert overview["params"]["product_code"] == "OOI"
    manufacturers = match_question("Which manufacturer of JJE chemistry analyzers is highest?")
    assert manufacturers["template_id"] == "invalid_share_by_manufacturer"
    assert manufacturers["params"]["product_code"] == "JJE"
    with pytest.raises(ValueError):
        validate_params({"product_code": "OOI", "date_from": "2010-01-01", "date_to": "2010-02-01"})
    with pytest.raises(ValueError):
        validate_params({"product_code": "NBW"})


class _Cursor:
    def __init__(self, rows):
        self._rows = rows
        self.description = [("level",), ("n",), ("k",)]

    def fetchall(self):
        return self._rows


class _Conn:
    def __init__(self):
        self.sql = ""
        self.params = {}

    def execute(self, sql, params):
        self.sql = sql
        self.params = params
        return _Cursor([("Firm North", 100, 20)])


def test_execute_template_binds_params_and_python_computes_the_rate():
    from invalid_agent.data.query import answer_question

    conn = _Conn()
    rows = execute_template(conn, "invalid_share_by_manufacturer", {"product_code": "JJE"})
    assert rows[0]["k"] == 20
    assert "SELECT" in conn.sql.upper()
    assert conn.params["product_code"] == "JJE"
    answered = answer_question(
        "Which manufacturer of JJE chemistry analyzers has the highest invalid-type share?",
        conn,
        choice={"template_id": "invalid_share_by_manufacturer", "params": {"product_code": "JJE"}, "source": "test"},
    )
    assert answered["fidelity"]["ok"] is True
    assert "20.00%" in answered["prose"] or "20%" in answered["prose"]
    assert "Firm North" in answered["prose"]
    assert "not estimable" in answered["prose"].lower()
    assert choose_template("weekly western electric for JJE")["template_id"] == "weekly_counts"


def test_groq_client_requires_a_key():
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        GroqLLM("", "openai/gpt-oss-20b")


def _url(user: str, password: str, host: str, path: str, query: str = "") -> str:
    """Build a URL without a connection-string literal in the source."""
    from urllib.parse import urlunsplit

    return urlunsplit(("postgresql", f"{user}:{password}@{host}", path, query, ""))


def test_readonly_url_replaces_the_admin_user_and_keeps_the_host():
    owner_password = "placeholder-owner"
    reader_password = "placeholder-reader"
    host = "db.example.test"
    admin = _url("owner", owner_password, host, "/neondb", "sslmode=require")
    readonly = readonly_url_from(admin, reader_password)
    assert owner_password not in readonly
    assert f"invalid_demo_ro:{reader_password}@{host}" in readonly
    assert readonly.endswith("/neondb?sslmode=require")


def test_openfda_case_does_not_fall_back_to_synthetic_rows(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_READONLY", raising=False)
    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    from invalid_agent.graph import run_case

    with pytest.raises(DataUnavailable, match="DATABASE_URL"):
        run_case("openfda_ooi", 0)


def _spike(scenario):
    product = scenario["product_code"]
    start = date.fromisoformat(scenario["date_from"])
    rows = []
    plan = (("Firm North", 200, 80), ("Firm South", 200, 10))
    for name, n, k in plan:
        for index in range(n):
            rows.append(
                {
                    "mdr_report_key": f"{product}-{name[:4]}-{index}",
                    "product_code": product,
                    "date_received": start + timedelta(days=index % 90),
                    "event_type": "Malfunction",
                    "manufacturer_name": name,
                    "brand_name": "ANALYZER",
                    "catalog_number": "",
                    "lot_number": "",
                    "device_operator": "",
                    "is_invalid_type": index < k,
                    "invalid_code": "INV-NOR" if index < k else "",
                }
            )
    return frame_from_reports(rows, scenario)


def test_weekly_loop_runs_on_two_openfda_cases_with_a_constructed_frame(tmp_path, monkeypatch):
    """Proves the graph, not the live extract. Rows are built in this test."""
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.setattr("invalid_agent.data.frame.load_openfda_frame", lambda scenario: _spike(scenario))
    from invalid_agent.graph import main

    for case_id in ("openfda_ooi", "openfda_jje"):
        out = tmp_path / case_id
        main(["--scenario", case_id, "--week", "4", "--out", str(out)])
        closeout = (out / "closeout.md").read_text(encoding="utf-8")
        assert "Not for clinical use" in closeout
        assert "not estimable" in closeout.lower()
        assert "reported_manufacturer" in closeout
        assert "Firm North" in closeout
        fishbone = (out / "fishbone.md").read_text(encoding="utf-8")
        assert "reported_manufacturer" in fishbone
        assert (out / "exec_deck.pptx").is_file()
        assert (out / "capa8d.md").is_file()


def test_overlapping_report_keys_collapse_per_product_code():
    from invalid_agent.data.load import PROBLEM_INSERT_SQL, REPORT_INSERT_SQL, prepare_report_rows

    rows = prepare_report_rows(
        [
            {"mdr_report_key": "SAME", "product_code": "OOI", "invalid_code": "INV-NOR"},
            {"mdr_report_key": "SAME", "product_code": "JJE", "invalid_code": "INV-MECH"},
            {"mdr_report_key": "SAME", "product_code": "OOI", "invalid_code": ""},
        ]
    )
    assert len(rows) == 2
    by_code = {row["product_code"]: row["invalid_code"] for row in rows}
    assert by_code["OOI"] == ""
    assert by_code["JJE"] == "INV-MECH"
    assert "ON CONFLICT (mdr_report_key, product_code)" in REPORT_INSERT_SQL
    assert "ON CONFLICT (mdr_report_key, product_code, product_problem)" in PROBLEM_INSERT_SQL


def test_chart_date_prefers_the_event_date():
    from invalid_agent.sim.generate import load_scenario

    scenario = load_scenario(Path(__file__).resolve().parents[1] / "cases" / "openfda_ooi.yaml")
    frame = frame_from_reports(
        [
            {
                "mdr_report_key": "1",
                "product_code": "OOI",
                "date_received": "2024-06-01",
                "date_of_event": "2024-05-01",
                "manufacturer_name": "Firm North",
                "brand_name": "brand-one",
                "is_invalid_type": False,
                "invalid_code": "",
            }
        ],
        scenario,
    )
    assert str(frame.loc[0, "date"].date()) == "2024-05-01"
    assert frame.loc[0, "date_basis"] == "date_of_event"
    assert frame.loc[0, "manufacturer"] == "Firm North"


def test_429_waits_for_retry_after_or_two_seconds():
    from invalid_agent.data.extract import CallLog, fetch_page, retry_delay

    assert retry_delay({"Retry-After": "5"}) == 5.0
    assert retry_delay({}) == 2.0

    class _Response:
        def __init__(self, code, headers, payload):
            self.status_code = code
            self.headers = headers
            self._payload = payload

        def json(self):
            return self._payload

    calls = {"n": 0}

    class _Client:
        def get(self, url, params=None):
            calls["n"] += 1
            if calls["n"] == 1:
                return _Response(429, {"Retry-After": "5"}, {})
            return _Response(200, {}, {"meta": {"results": {"total": 0}}, "results": []})

    delays: list[float] = []
    fetch_page(_Client(), "search", "not-a-key", CallLog(), sleeper=delays.append)
    assert delays == [5.0]


def test_anonymized_display_is_still_available(monkeypatch):
    monkeypatch.setenv("MANUFACTURER_DISPLAY", "anonymized")
    from invalid_agent.sim.generate import load_scenario

    scenario = load_scenario(Path(__file__).resolve().parents[1] / "cases" / "openfda_jje.yaml")
    frame = frame_from_reports(
        [
            {
                "mdr_report_key": "1",
                "product_code": "JJE",
                "date_received": "2024-02-01",
                "manufacturer_name": "Firm South",
                "is_invalid_type": False,
                "invalid_code": "",
            },
            {
                "mdr_report_key": "2",
                "product_code": "JJE",
                "date_received": "2024-02-02",
                "manufacturer_name": "Firm North",
                "is_invalid_type": True,
                "invalid_code": "INV-NOR",
            },
        ],
        scenario,
    )
    assert set(frame["manufacturer"]) == {"Manufacturer A", "Manufacturer B"}
    assert "Firm North" not in set(frame["manufacturer"])
