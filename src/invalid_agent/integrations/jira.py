"""Jira Cloud Free adapter.

No credentials → dry-run JSON on disk. The graph never opens a socket in
that mode. With ``JIRA_BASE_URL``, ``JIRA_EMAIL``, and ``JIRA_API_TOKEN``
set, ``LiveJira`` posts to ``/rest/api/3/issue``. A transport failure is
recorded on the payload and does not raise, so the rest of the case still
finishes. The token is not part of ``__repr__``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from invalid_agent.config import Settings


class Transport(Protocol):
    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]: ...


def _adf(text: str) -> dict[str, Any]:
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


class HttpxTransport:
    def __init__(self, base_url: str, email: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._email = email
        self._token = token

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        import httpx

        response = httpx.request(
            method,
            f"{self.base_url}{path}",
            json=body,
            auth=(self._email, self._token),
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()


class DryRunJira:
    """Local mirror of the epic and the stories. Keys are SIM-* so they cannot be confused with a real board."""

    mode = "dry-run"

    def __init__(self, path: Path, project: str = "INV") -> None:
        self.path = path
        self.project = project

    def __repr__(self) -> str:
        return f"DryRunJira(path={str(self.path)!r}, project={self.project!r})"

    def sync(self, plan: dict[str, Any]) -> dict[str, Any]:
        existing = _read(self.path)
        return _upsert(existing, plan, self.project, self.mode, creator=_local_creator(existing), path=self.path)


class LiveJira:
    mode = "live"

    def __init__(self, settings: Settings, path: Path, transport: Transport | None = None) -> None:
        self.project = settings.jira_project_key
        self.path = path
        self._email = settings.jira_email
        self._transport = transport or HttpxTransport(
            settings.jira_base_url, settings.jira_email, settings.jira_api_token
        )

    def __repr__(self) -> str:
        return f"LiveJira(project={self.project!r}, email={self._email!r})"

    def sync(self, plan: dict[str, Any]) -> dict[str, Any]:
        existing = _read(self.path)
        error = ""

        def creator(kind: str, summary: str, body: str) -> dict[str, Any]:
            payload = {
                "fields": {
                    "project": {"key": self.project},
                    "summary": summary[:255],
                    "issuetype": {"name": "Epic" if kind == "epic" else "Task"},
                    "labels": ["invalid-bot", "simulation"],
                    "description": _adf(body),
                }
            }
            created = self._transport.request("POST", "/rest/api/3/issue", payload)
            return {"id": str(created.get("id", "")), "key": str(created.get("key", ""))}

        try:
            return _upsert(existing, plan, self.project, self.mode, creator=creator, path=self.path)
        except Exception as exc:  # the demo still has the local file
            error = f"{type(exc).__name__}"
            existing["mode"] = self.mode
            existing["error"] = error
            existing.setdefault("issues", [])
            existing.setdefault("project", self.project)
            _write(self.path, existing)
            return existing


def make_client(settings: Settings, path: Path, transport: Transport | None = None):
    if settings.jira_enabled:
        return LiveJira(settings, path, transport=transport)
    return DryRunJira(path, project=settings.jira_project_key)


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _local_creator(existing: dict[str, Any]):
    used = 0
    if existing.get("epic", {}).get("key", "").startswith("SIM-"):
        used = max(used, int(existing["epic"]["key"].split("-")[1]))
    for issue in existing.get("issues") or []:
        if str(issue.get("key", "")).startswith("SIM-"):
            used = max(used, int(issue["key"].split("-")[1]))
    counter = {"n": used}

    def creator(kind: str, summary: str, body: str) -> dict[str, Any]:
        del kind, summary, body
        counter["n"] += 1
        number = counter["n"]
        return {"id": str(number), "key": f"SIM-{number}"}

    return creator


def _upsert(
    existing: dict[str, Any],
    plan: dict[str, Any],
    project: str,
    mode: str,
    creator,
    path: Path,
) -> dict[str, Any]:
    epic = existing.get("epic")
    if not epic:
        minted = creator(
            "epic",
            f"Investigation {plan.get('scenario_id', '')}: {plan.get('top_cause', '')}".strip(),
            "Synthetic investigation. Not for clinical use.",
        )
        epic = {
            "task_id": "EPIC",
            "key": minted.get("key", ""),
            "id": minted.get("id", ""),
            "summary": f"Investigation {plan.get('scenario_id', '')}",
        }
    by_task = {issue["task_id"]: issue for issue in existing.get("issues") or []}
    issues = list(existing.get("issues") or [])
    for task in plan["tasks"]:
        if task["id"] in by_task:
            by_task[task["id"]]["status"] = task["status"]
            by_task[task["id"]]["summary"] = task["name"]
            by_task[task["id"]]["owner"] = task["owner"]
            continue
        minted = creator("task", task["name"], f"Owner: {task['owner']}. Depends on: {', '.join(task['depends_on']) or 'nothing'}.")
        created = {
            "task_id": task["id"],
            "key": minted.get("key", ""),
            "id": minted.get("id", ""),
            "summary": task["name"],
            "status": task["status"],
            "owner": task["owner"],
            "sprint": "Investigation",
            "sim_week": task["sim_week"],
        }
        issues.append(created)
        by_task[task["id"]] = created
    payload = {
        "mode": mode,
        "project": project,
        "epic": epic,
        "issues": issues,
        "disclaimer": "Simulation. Not a live customer escalation.",
    }
    _write(path, payload)
    return payload
