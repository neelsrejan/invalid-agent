"""Dry-run never touches the network. Live sync is idempotent against a fake transport."""

import json

from invalid_agent.config import load_settings
from invalid_agent.integrations.jira import DryRunJira, LiveJira, make_client
from invalid_agent.nodes.planner import build_plan


def _plan():
    return build_plan(
        {"id": "bad_lot", "start_date": "2025-04-01", "horizon_days": 180},
        {"cause": "bad_reagent_lot", "level": "L-4419"},
        week=0,
    )


class _FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        number = len(self.calls)
        return {"id": str(1000 + number), "key": f"INV-{number}"}


class _BrokenTransport:
    def request(self, method, path, body=None):
        raise RuntimeError("401 from the fake site")


def test_dry_run_is_idempotent_and_offline(tmp_path, monkeypatch):
    for key in ("JIRA_BASE_URL", "JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    path = tmp_path / "jira_issues.json"
    settings = load_settings()
    client = make_client(settings, path)
    assert isinstance(client, DryRunJira)
    first = client.sync(_plan())
    second = client.sync(_plan())
    assert first["mode"] == "dry-run"
    assert len(second["issues"]) == len(first["issues"]) == 10
    assert second["issues"][0]["key"] == first["issues"][0]["key"]
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["epic"]["key"] == "SIM-1"
    assert "super-secret" not in path.read_text(encoding="utf-8")


def test_live_sync_posts_once_per_task_and_hides_the_token(tmp_path, monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "super-secret-token")
    settings = load_settings()
    transport = _FakeTransport()
    client = LiveJira(settings, tmp_path / "jira_issues.json", transport=transport)
    assert "super-secret-token" not in repr(client)
    first = client.sync(_plan())
    posts_after_first = len(transport.calls)
    assert posts_after_first == 11  # epic + 10 tasks
    assert all(call[0] == "POST" and call[1] == "/rest/api/3/issue" for call in transport.calls)
    second = client.sync(_plan())
    assert len(transport.calls) == posts_after_first
    assert len(second["issues"]) == len(first["issues"])
    assert first["mode"] == "live"


def test_live_failure_is_recorded_and_does_not_raise(tmp_path, monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "super-secret-token")
    settings = load_settings()
    client = LiveJira(settings, tmp_path / "jira_issues.json", transport=_BrokenTransport())
    result = client.sync(_plan())
    assert result["error"] == "RuntimeError"
    assert "super-secret-token" not in json.dumps(result)
