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


def source_label(plan: dict[str, Any]) -> str:
    """openfda for the public MAUDE cases, simulation for the synthetic file."""
    if plan.get("data_backend") == "openfda" or plan.get("denominator") == "reported_events":
        return "openfda"
    return "simulation"


def case_label(plan: dict[str, Any]) -> str:
    raw = str(plan.get("scenario_id") or "case")
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in raw)
    return f"case-{safe}"


def _search_jql(project: str, plan: dict[str, Any]) -> str:
    return f'project = {project} AND labels = "{case_label(plan)}"'


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

    def search(self, jql: str) -> list[dict[str, Any]]:
        payload = self._transport.request(
            "POST",
            "/rest/api/3/search/jql",
            {"jql": jql, "maxResults": 50, "fields": ["summary", "labels", "status"]},
        )
        issues = payload.get("issues") or []
        return list(issues) if isinstance(issues, list) else []

    def sync(self, plan: dict[str, Any]) -> dict[str, Any]:
        existing = _read(self.path)
        source = source_label(plan)
        label = case_label(plan)
        try:
            found = self.search(_search_jql(self.project, plan))
        except Exception as exc:
            return _record_failure(existing, self.path, self.project, self.mode, exc, self._email)
        if found:
            payload = _from_remote(found, plan, self.project, self.mode, source, label)
            _write(self.path, payload)
            return payload

        def creator(kind: str, summary: str, body: str, parent_key: str = "") -> dict[str, Any]:
            fields: dict[str, Any] = {
                "project": {"key": self.project},
                "summary": summary[:255],
                "issuetype": {"name": "Epic" if kind == "epic" else "Task"},
                "labels": ["invalid-bot", source, label],
                "description": _adf(body),
            }
            # Team-managed Jira Cloud parents a task to an epic with this field.
            if parent_key and kind != "epic":
                fields["parent"] = {"key": parent_key}
            payload = {"fields": fields}
            created = self._transport.request("POST", "/rest/api/3/issue", payload)
            return {"id": str(created.get("id", "")), "key": str(created.get("key", ""))}

        try:
            return _upsert(existing, plan, self.project, self.mode, creator=creator, path=self.path)
        except Exception as exc:  # the demo still has the local file
            return _record_failure(existing, self.path, self.project, self.mode, exc, self._email)


class ReadOnlyJira:
    """Public-page client. Search and link. Never creates an issue."""

    mode = "live-read"

    def __init__(self, settings: Settings, path: Path, transport: Transport | None = None) -> None:
        self.project = settings.jira_project_key
        self.path = path
        self._email = settings.jira_email
        self._transport = transport or HttpxTransport(
            settings.jira_base_url, settings.jira_email, settings.jira_api_token
        )

    def __repr__(self) -> str:
        return f"ReadOnlyJira(project={self.project!r}, email={self._email!r})"

    def sync(self, plan: dict[str, Any]) -> dict[str, Any]:
        source = source_label(plan)
        label = case_label(plan)
        try:
            payload = self._transport.request(
                "POST",
                "/rest/api/3/search/jql",
                {"jql": _search_jql(self.project, plan), "maxResults": 50, "fields": ["summary", "labels", "status"]},
            )
            found = list(payload.get("issues") or [])
        except Exception as exc:
            existing = _read(self.path)
            return _record_failure(existing, self.path, self.project, self.mode, exc, self._email)
        record = _from_remote(found, plan, self.project, self.mode, source, label)
        if not found:
            record["note"] = "No live issues yet. The owner runs: python -m invalid_agent.integrations.jira seed"
        _write(self.path, record)
        return record


def doctor(settings: Settings, transport: Transport | None = None) -> dict[str, Any]:
    """Check a Jira Cloud Free site. Does nothing when the three secrets are absent."""
    if not settings.jira_enabled:
        return {
            "ok": False,
            "reason": "Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN. Two out of three stays a dry run.",
        }
    client = transport or HttpxTransport(settings.jira_base_url, settings.jira_email, settings.jira_api_token)
    myself = client.request("GET", "/rest/api/3/myself")
    project = client.request("GET", f"/rest/api/3/project/{settings.jira_project_key}")
    meta = client.request("GET", f"/rest/api/3/issue/createmeta/{settings.jira_project_key}/issuetypes")
    raw_types = meta.get("issueTypes") if isinstance(meta, dict) else meta
    if isinstance(meta, dict) and "values" in meta:
        raw_types = meta["values"]
    names = sorted({str(item.get("name", "")) for item in (raw_types or []) if isinstance(item, dict)})
    missing = [name for name in ("Epic", "Task") if name not in names]
    return {
        "ok": not missing,
        "account": str(myself.get("emailAddress") or myself.get("displayName") or ""),
        "project": str(project.get("key") or settings.jira_project_key),
        "issue_types": names,
        "missing_issue_types": missing,
        "hint": ""
        if not missing
        else "Create a team-managed Jira software project so Epic and Task exist by those names.",
    }


def make_client(settings: Settings, path: Path, transport: Transport | None = None):
    """The investigation loop never creates issues.

    With credentials this is a read of issues the owner already seeded.
    Without credentials it is the SIM-* dry run.
    """
    if settings.jira_enabled:
        return ReadOnlyJira(settings, path, transport=transport)
    return DryRunJira(path, project=settings.jira_project_key)


def seed_cases(settings: Settings, transport: Transport | None = None) -> list[dict[str, Any]]:
    """Create the public-case issues once. A second run finds them and does not post."""
    from invalid_agent.nodes.planner import build_plan
    from invalid_agent.sim.generate import load_scenario

    if not settings.jira_enabled:
        raise SystemExit(
            "Refusing to seed Jira. Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN. "
            "The public page does not create issues."
        )
    results = []
    for name in ("openfda_ooi", "openfda_jje"):
        scenario = load_scenario(settings.repo_root / "cases" / f"{name}.yaml")
        plan = build_plan(scenario, {"cause": "no_single_cause", "level": "none"}, 0)
        client = LiveJira(settings, settings.out_dir / f"jira_seed_{name}.json", transport=transport)
        results.append({"scenario_id": name, "result": client.sync(plan)})
    return results


def main(argv: list[str] | None = None) -> None:
    import argparse
    import json

    from invalid_agent.config import load_dotenv, load_settings

    load_dotenv()
    parser = argparse.ArgumentParser(description="Check Jira, or seed the public cases once.")
    parser.add_argument("command", nargs="?", choices=["doctor", "seed"], default="doctor")
    args = parser.parse_args(argv)
    settings = load_settings()
    if args.command == "seed":
        seeded = seed_cases(settings)
        print(json.dumps({"ok": True, "cases": [row["scenario_id"] for row in seeded]}, indent=2))
        return
    report = doctor(settings)
    print(json.dumps(report, indent=2))
    if not report.get("ok"):
        raise SystemExit(1)


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

    def creator(kind: str, summary: str, body: str, parent_key: str = "") -> dict[str, Any]:
        del kind, summary, body, parent_key
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
            str(plan.get("disclaimer") or "Not for clinical use."),
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
        minted = creator(
            "task",
            task["name"],
            f"Owner: {task['owner']}. Depends on: {', '.join(task['depends_on']) or 'nothing'}.",
            parent_key=str(epic.get("key") or ""),
        )
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
        "source": source_label(plan),
        "labels": ["invalid-bot", source_label(plan), case_label(plan)],
        "epic": epic,
        "issues": issues,
        "disclaimer": str(plan.get("disclaimer") or "Simulation. Not a live customer escalation."),
    }
    _write(path, payload)
    return payload


def _from_remote(
    found: list[dict[str, Any]],
    plan: dict[str, Any],
    project: str,
    mode: str,
    source: str,
    label: str,
) -> dict[str, Any]:
    epic = None
    issues: list[dict[str, Any]] = []
    for item in found:
        fields = item.get("fields") or {}
        summary = str(fields.get("summary") or "")
        row = {
            "key": str(item.get("key") or ""),
            "id": str(item.get("id") or ""),
            "summary": summary,
            "task_id": str(item.get("key") or ""),
        }
        if epic is None and summary.startswith("Investigation "):
            epic = {"task_id": "EPIC", "key": row["key"], "id": row["id"], "summary": summary}
        else:
            issues.append(row)
    return {
        "mode": mode,
        "project": project,
        "source": source,
        "labels": ["invalid-bot", source, label],
        "epic": epic or {},
        "issues": issues,
        "disclaimer": str(plan.get("disclaimer") or "Not for clinical use."),
    }


def _record_failure(existing: dict[str, Any], path: Path, project: str, mode: str, exc: Exception, email: str) -> dict[str, Any]:
    detail = str(exc)
    if email:
        detail = detail.replace(email, "***")
    existing["mode"] = mode
    existing["error"] = type(exc).__name__
    existing["error_detail"] = detail[:300]
    existing.setdefault("issues", [])
    existing.setdefault("project", project)
    _write(path, existing)
    return existing


if __name__ == "__main__":
    main()
