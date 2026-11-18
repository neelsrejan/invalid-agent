"""Pytest must not read a developer's .env."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _ignore_dotenv(monkeypatch):
    monkeypatch.setenv("INVALID_AGENT_SKIP_DOTENV", "1")
