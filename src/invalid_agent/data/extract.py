"""Pull the planned MAUDE windows once, page by page, and cache them.

The command refuses to start when ``OPENFDA_API_KEY`` is empty. It does not
fall back to an anonymous call. ``--refresh`` is the only way to hit the
API again after a complete cache exists.

Narratives, patient blocks, and street addresses are dropped before the
cache is written. The demo's math uses the structured fields only.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from invalid_agent.config import load_settings
from invalid_agent.data.cache import cache_root, is_complete, write_case
from invalid_agent.data.mapping import (
    CASES,
    MAX_API_CALLS,
    PAGE_LIMIT,
    SKIP_CEILING,
    normalize_manufacturer,
    primary_invalid_code,
    search_for,
)

OPENFDA_EVENT_URL = "https://api.fda.gov/device/event.json"

MISSING_KEY_MESSAGE = (
    "OPENFDA_API_KEY is missing, so the extract did not start and no openFDA call was made.\n"
    "Create a free key at https://open.fda.gov/apis/authentication/ "
    "(no fee; the key raises the daily quota above the anonymous IP cap).\n"
    "Export it in the environment, or put OPENFDA_API_KEY=... in a gitignored .env file, then rerun:\n"
    "  python -m invalid_agent.data.pipeline\n"
    "Do not paste the key into the repo, the dashboard source, or a Streamlit secret. "
    "The public demo reads Postgres and does not call openFDA."
)


class MissingAPIKey(RuntimeError):
    """Raised when an extract is requested without OPENFDA_API_KEY."""


def require_api_key(key: str | None = None) -> str:
    if key is None:
        key = load_settings().openfda_api_key
    cleaned = (key or "").strip()
    if not cleaned:
        raise MissingAPIKey(MISSING_KEY_MESSAGE)
    return cleaned


def slim_record(record: dict[str, Any], product_code: str) -> dict[str, Any]:
    """Keep structured device fields. Drop narrative and patient text."""
    devices = record.get("device") or []
    device: dict[str, Any] = {}
    if isinstance(devices, list):
        for item in devices:
            if isinstance(item, dict) and str(item.get("device_report_product_code", "")).upper() == product_code:
                device = item
                break
        if not device and devices and isinstance(devices[0], dict):
            device = devices[0]
    labels = _labels(record.get("product_problems"))
    raw_name = str(device.get("manufacturer_d_name") or record.get("manufacturer_name") or "")
    return {
        "mdr_report_key": str(record.get("mdr_report_key") or ""),
        "product_code": product_code,
        "date_received": _yyyymmdd(record.get("date_received")),
        "date_of_event": _yyyymmdd(record.get("date_of_event")),
        "event_type": str(record.get("event_type") or ""),
        "manufacturer_raw": raw_name.strip(),
        "manufacturer_name": normalize_manufacturer(raw_name),
        "brand_name": str(device.get("brand_name") or "").strip(),
        "generic_name": str(device.get("generic_name") or "").strip(),
        "model_number": str(device.get("model_number") or "").strip(),
        "catalog_number": str(device.get("catalog_number") or "").strip(),
        "lot_number": str(device.get("lot_number") or "").strip(),
        "device_operator": str(device.get("device_operator") or "").strip(),
        "product_problems": labels,
        "invalid_code": primary_invalid_code(labels),
    }


def _labels(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    seen: list[str] = []
    for item in raw:
        text = " ".join(str(item).split())
        if text and text not in seen:
            seen.append(text)
    return seen


def _yyyymmdd(value: Any) -> str | None:
    text = str(value or "").strip()
    if len(text) < 8 or not text[:8].isdigit():
        return None
    return f"{text[:4]}-{text[4:6]}-{text[6:8]}"


class CallLog:
    def __init__(self, cap: int = MAX_API_CALLS) -> None:
        self.cap = cap
        self.count = 0
        self.notes: list[str] = []

    def mark(self, note: str) -> None:
        if self.count >= self.cap:
            raise RuntimeError(
                f"Stopped at {self.cap} openFDA calls ({note}). "
                "Narrow the case window in mapping.CASES instead of raising the cap."
            )
        self.count += 1
        self.notes.append(note)
        print(f"openFDA call {self.count}/{self.cap}: {note}", flush=True)


def _next_from_link(link: str) -> dict[str, str] | None:
    if not link or 'rel="next"' not in link:
        return None
    start = link.find("<")
    end = link.find(">")
    if start < 0 or end <= start:
        return None
    parsed = urlparse(link[start + 1 : end])
    query = {key: values[-1] for key, values in parse_qs(parsed.query).items() if key != "api_key"}
    if "search_after" in query or "skip" in query:
        return query
    return None


def fetch_page(
    client: httpx.Client,
    search: str,
    api_key: str,
    log: CallLog,
    *,
    skip: int = 0,
    search_after: str = "",
) -> tuple[dict[str, Any], dict[str, str] | None]:
    params: dict[str, str] = {"search": search, "limit": str(PAGE_LIMIT)}
    if search_after:
        params["search_after"] = search_after
        note = f"search_after page limit={PAGE_LIMIT}"
    else:
        if skip:
            params["skip"] = str(skip)
        note = f"skip={skip} limit={PAGE_LIMIT}"
    params["api_key"] = api_key
    log.mark(note)
    try:
        response = client.get(OPENFDA_EVENT_URL, params=params)
    except Exception as exc:
        raise RuntimeError(f"openFDA request failed on {note}: {type(exc).__name__}") from None
    if response.status_code == 404:
        empty = {"meta": {"results": {"skip": skip, "limit": PAGE_LIMIT, "total": 0}}, "results": []}
        return empty, None
    if response.status_code == 429 and log.count < log.cap:
        log.mark("retry after 429")
        try:
            response = client.get(OPENFDA_EVENT_URL, params=params)
        except Exception as exc:
            raise RuntimeError(f"openFDA retry failed on {note}: {type(exc).__name__}") from None
    if response.status_code >= 400:
        # The body must not be echoed if it ever repeated the key. It does not
        # on this API, but the message stays generic plus the status code.
        raise RuntimeError(f"openFDA returned HTTP {response.status_code} on {note}. The key was not logged.")
    payload = response.json()
    nxt = _next_from_link(response.headers.get("link") or response.headers.get("Link") or "")
    return payload, nxt


def extract_case(
    case: dict[str, str],
    api_key: str,
    client: httpx.Client,
    log: CallLog,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    search = search_for(case)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    skip = 0
    search_after = ""
    total: int | None = None
    pages = 0
    while True:
        if skip > SKIP_CEILING and not search_after:
            raise RuntimeError(
                f"{case['id']} reached the openFDA skip ceiling ({SKIP_CEILING}). "
                "Narrow the date window. search_after was not offered on the previous page."
            )
        payload, nxt = fetch_page(client, search, api_key, log, skip=skip, search_after=search_after)
        pages += 1
        batch = payload.get("results") or []
        meta_total = int((payload.get("meta") or {}).get("results", {}).get("total") or 0)
        total = meta_total
        for record in batch:
            if not isinstance(record, dict):
                continue
            slim = slim_record(record, case["product_code"])
            key = slim["mdr_report_key"]
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append(slim)
        if not batch or len(rows) >= (total or 0):
            break
        if nxt and nxt.get("search_after"):
            search_after = nxt["search_after"]
            skip = 0
            continue
        search_after = ""
        skip += len(batch)
        if skip >= (total or 0):
            break
    meta = {
        "case_id": case["id"],
        "product_code": case["product_code"],
        "date_from": case["date_from"],
        "date_to": case["date_to"],
        "search": search,
        "complete": True,
        "rows": len(rows),
        "total_reported_by_api": total,
        "pages": pages,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "narratives_stored": False,
    }
    return rows, meta


def run_extract(*, refresh: bool = False, client: httpx.Client | None = None, api_key: str | None = None) -> dict[str, Any]:
    key = require_api_key(api_key)
    root = cache_root()
    log = CallLog()
    own_client = client is None
    http = client or httpx.Client(timeout=60.0)
    summary: dict[str, Any] = {"cases": [], "api_calls": 0, "cache": str(root)}
    try:
        for case in CASES:
            if is_complete(case["id"], root) and not refresh:
                print(f"{case['id']}: cache hit, 0 openFDA calls", flush=True)
                summary["cases"].append({"id": case["id"], "cached": True, "api_calls": 0})
                continue
            rows, meta = extract_case(case, key, http, log)
            meta["api_calls_so_far"] = log.count
            write_case(case["id"], rows, meta, root)
            print(
                f"{case['id']}: cached {meta['rows']} reports "
                f"(API total {meta['total_reported_by_api']}).",
                flush=True,
            )
            summary["cases"].append({"id": case["id"], "cached": False, "rows": meta["rows"]})
    finally:
        if own_client:
            http.close()
    summary["api_calls"] = log.count
    root.mkdir(parents=True, exist_ok=True)
    (root / "call_log.json").write_text(
        json.dumps({"api_calls": log.count, "cap": log.cap, "notes": log.notes}, indent=2),
        encoding="utf-8",
    )
    print(f"openFDA calls this run: {log.count} (cap {log.cap})", flush=True)
    return summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Extract the planned openFDA MAUDE windows into the on-disk cache.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore a complete cache and call openFDA again.",
    )
    args = parser.parse_args(argv)
    try:
        run_extract(refresh=args.refresh)
    except MissingAPIKey as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
