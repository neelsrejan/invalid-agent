"""openFDA entry point.

``python -m invalid_agent.sim.openfda`` runs the cached extract and refuses
to start without ``OPENFDA_API_KEY``. ``fetch_event_count`` remains a
one-row probe that returns None when the network fails, so a unit test can
prove the synthetic generator does not need it.
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


def main(argv: list[str] | None = None) -> None:
    from invalid_agent.data.extract import main as extract_main

    extract_main(argv)


if __name__ == "__main__":
    main()
