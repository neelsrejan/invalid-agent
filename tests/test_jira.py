"""Dry-run never touches the network. Live sync is idempotent against a fake transport."""

import json

from invalid_agent.config import load_settings
from invalid_agent.integrations.jira import DryRunJira, LiveJira, ReadOnlyJira, make_client
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
        self.issues: list[dict] = []

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        if path == "/rest/api/3/search/jql":
            jql = str((body or {}).get("jql") or "")
            matched = [
                issue
                for issue in self.issues
                if any(label.startswith("case-") and label in jql for label in issue["fields"].get("labels", []))
            ]
            return {"issues": matched}
        number = len(self.issues) + 1
        fields = (body or {}).get("fields", {})
        issue = {
            "id": str(1000 + number),
            "key": f"INV-{number}",
            "fields": {"summary": fields.get("summary", ""), "labels": list(fields.get("labels") or [])},
        }
        self.issues.append(issue)
        return {"id": issue["id"], "key": issue["key"]}


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
    assert saved["source"] == "simulation"
    assert "simulation" in saved["labels"]
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
    creates = [call for call in transport.calls if call[1] == "/rest/api/3/issue"]
    assert transport.calls[0][1] == "/rest/api/3/search/jql"
    assert len(creates) == 11  # epic + 10 tasks, after the search found nothing
    assert creates[0][2]["fields"]["labels"] == ["invalid-bot", "simulation", "case-bad_lot"]
    second = client.sync(_plan())
    creates_after = [call for call in transport.calls if call[1] == "/rest/api/3/issue"]
    assert len(creates_after) == len(creates)
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


def test_public_client_never_creates_issues(tmp_path, monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "super-secret-token")
    settings = load_settings()
    transport = _FakeTransport()
    client = make_client(settings, tmp_path / "jira_issues.json", transport=transport)
    assert isinstance(client, ReadOnlyJira)
    result = client.sync(_plan())
    assert result["mode"] == "live-read"
    assert not any(call[1] == "/rest/api/3/issue" for call in transport.calls)
    assert "seed" in result["note"]


def test_seed_labels_openfda_and_does_not_post_twice(tmp_path, monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "super-secret-token")
    monkeypatch.setenv("INVALID_AGENT_OUT", str(tmp_path))
    settings = load_settings()
    transport = _FakeTransport()
    from invalid_agent.integrations.jira import seed_cases

    seed_cases(settings, transport=transport)
    creates = [call for call in transport.calls if call[1] == "/rest/api/3/issue"]
    assert creates
    assert all("openfda" in call[2]["fields"]["labels"] for call in creates)
    assert any("case-openfda_ooi" in call[2]["fields"]["labels"] for call in creates)
    assert any("case-openfda_jje" in call[2]["fields"]["labels"] for call in creates)
    created = len(creates)
    seed_cases(settings, transport=transport)
    assert len([call for call in transport.calls if call[1] == "/rest/api/3/issue"]) == created
