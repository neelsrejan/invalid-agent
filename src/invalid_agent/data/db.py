"""Postgres connections. The demo query path is read-only."""

from __future__ import annotations

from urllib.parse import unquote, urlsplit

from invalid_agent.config import Settings, load_settings
from invalid_agent.data.mapping import READONLY_ROLE


def normalize_url(url: str) -> str:
    text = url.strip()
    if text.startswith("postgres://"):
        text = "postgresql://" + text[len("postgres://") :]
    return text


def url_user(url: str) -> str:
    netloc = urlsplit(normalize_url(url)).netloc
    if "@" not in netloc:
        return ""
    userinfo = netloc.rsplit("@", 1)[0]
    return unquote(userinfo.split(":", 1)[0])


def connect(url: str, *, readonly: bool):
    import psycopg

    conn = psycopg.connect(normalize_url(url), connect_timeout=20)
    if readonly:
        conn.execute("SET default_transaction_read_only = on")
        conn.commit()
    return conn


def query_url(settings: Settings | None = None, *, public: bool = False) -> str:
    """URL for SELECTs.

    The public demo must use the ``invalid_demo_ro`` role. A loader session
    may use the admin URL, and this function still opens it read-only, but
    ``public=True`` refuses that shortcut.
    """
    from invalid_agent.data.frame import DataUnavailable

    settings = settings or load_settings()
    readonly = settings.database_url_readonly
    admin = settings.database_url
    if public:
        if not readonly:
            raise DataUnavailable(
                "DATABASE_URL_READONLY is not set. The public demo queries as the "
                f"read-only role {READONLY_ROLE}. Run python -m invalid_agent.data.load "
                "and paste the printed URL into the Streamlit secret DATABASE_URL_READONLY. "
                "Do not point the demo at the admin connection string."
            )
        if url_user(readonly) != READONLY_ROLE:
            raise DataUnavailable(
                "DATABASE_URL_READONLY must log in as "
                f"{READONLY_ROLE}. The loader prints that URL. "
                "The admin role is for the one-time load only."
            )
        return readonly
    if readonly:
        return readonly
    if admin:
        return admin
    raise DataUnavailable(
        "Neither DATABASE_URL_READONLY nor DATABASE_URL is set. "
        "This case reads the hosted MAUDE table and does not fall back to synthetic rows. "
        "Create the free Neon database, export DATABASE_URL, and run "
        "python -m invalid_agent.data.pipeline once the openFDA key is set."
    )
