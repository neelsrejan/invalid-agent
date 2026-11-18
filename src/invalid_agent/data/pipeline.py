"""One command the owner runs after the key and the database URL exist.

Extract (cached) then load. A missing openFDA key stops the process before
any HTTP call and before any database connection.
"""

from __future__ import annotations

from invalid_agent.data.extract import MissingAPIKey, run_extract
from invalid_agent.data.load import main as load_main


def main() -> None:
    from invalid_agent.config import load_dotenv

    load_dotenv()
    try:
        run_extract(refresh=False)
    except MissingAPIKey as exc:
        raise SystemExit(str(exc)) from exc
    load_main([])


if __name__ == "__main__":
    main()
