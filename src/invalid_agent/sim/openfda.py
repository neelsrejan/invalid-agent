"""Optional openFDA device-event probe.

The generator does not call this. A reviewer who wants a live count can
run ``python -m invalid_agent.sim.openfda``. Anonymous access works;
``OPENFDA_API_KEY`` is sent only when it is set. Failures return None
so a missing network cannot break the simulation.
"""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

OPENFDA_EVENT_URL = "https://api.fda.gov/device/event.json"


def build_query(api_key: str = "") -> tuple[str, dict[str, str]]:
    """A one-row count query. No narrative text is requested."""
    params = {"limit": "1"}
    if api_key:
        params["api_key"] = api_key
    return OPENFDA_EVENT_URL, params


def fetch_event_count(api_key: str = "", timeout: float = 10.0) -> int | None:
    url, params = build_query(api_key)
    try:
        with urlopen(f"{url}?{urlencode(params)}", timeout=timeout) as response:
            payload = json.load(response)
        return int(payload["meta"]["results"]["total"])
    except (URLError, TimeoutError, KeyError, ValueError, OSError):
        return None


def main() -> None:
    from invalid_agent.config import load_settings

    settings = load_settings()
    total = fetch_event_count(settings.openfda_api_key)
    if total is None:
        print("openFDA unreachable or unexpected payload. The simulation does not need this call.")
        return
    print(f"openFDA device/event reports currently indexed (meta.results.total): {total}")
    print("Unvalidated public data. Not for medical decisions. Not used as rows in this simulation.")


if __name__ == "__main__":
    main()
