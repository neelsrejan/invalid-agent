"""Plain sections from one cached investigation run.

The graph still writes the memo, the cause diagram, the five whys, the
eight-step form, the schedule, the risks, the status notes, and the
read-only ticket list. This module turns those records into sentences a
high-school reader can open. It does not print a file path.
"""

from __future__ import annotations

from typing import Any

from invalid_agent.ui.plain import safe_prose
from invalid_agent.ui.story import _plain_task_name


_WHOLE_FILE = (
    "This write-up covers the whole practice file, not only this week's dates. "
    "The rate in the sentences above is the one for this week."
)
_PUBLIC_FILE = (
    "This write-up covers the whole public report file, not only this week's dates. "
    "The rate in the sentences above is the one for this week."
)


def _file_line(public: bool) -> str:
    return _PUBLIC_FILE if public else _WHOLE_FILE


def sections_from_run(
    result: dict[str, Any],
    *,
    base_url: str = "",
    public: bool = False,
) -> list[dict[str, str]]:
    """One dict per collapsed block: title, what, body."""

    def block(title: str, what: str, body: Any) -> dict[str, str]:
        return _section(title, what, body, public=public)

    sections = [
        block(
            "First read of the complaint",
            "What this is: the agent's first written read of the complaint.",
            result.get("triage_markdown"),
        ),
        block(
            "Cause groups",
            "What this is: a fishbone diagram sorts possible causes into groups. " + _file_line(public),
            (result.get("fishbone") or {}).get("markdown"),
        ),
        block(
            "Ask why five times",
            "What this is: five questions that follow the leading cause one step deeper each time.",
            (result.get("five_whys") or {}).get("markdown"),
        ),
        block(
            "Eight-step write-up",
            "What this is: a standard problem form. 8D means eight disciplines, from the team through the close.",
            (result.get("capa") or {}).get("markdown"),
        ),
        block(
            "Ticket schedule",
            "What this is: a Gantt chart is a bar for each ticket across days. The list below is that schedule.",
            _plan_text(result.get("plan") or {}),
        ),
        block(
            "Risk list",
            "What this is: the risks the plan is watching, with how likely each one is.",
            _risk_text(result.get("risks") or []),
        ),
        block(
            "Read-only ticket links",
            "What this is: links to tickets that already exist. This page does not create a live ticket.",
            _jira_text(result.get("jira") or {}, base_url),
        ),
    ]
    notes = result.get("status_updates") or {}
    for key, title in (
        ("customer", "Status note for the customer"),
        ("internal", "Status note for the team"),
        ("leadership", "Status note for leadership"),
    ):
        sections.append(
            block(
                title,
                "What this is: the note the agent wrote for that reader.",
                notes.get(key),
            )
        )
    return sections


def logged_sections(sections: list[dict[str, str]]) -> list[dict[str, str]]:
    skip = {"Status note for the customer", "Status note for the team", "Status note for leadership"}
    return [item for item in sections if item["title"] not in skip]


def note_sections(sections: list[dict[str, str]]) -> list[dict[str, str]]:
    keep = {"Status note for the customer", "Status note for the team", "Status note for leadership"}
    return [item for item in sections if item["title"] in keep]


def _section(title: str, what: str, body: Any, *, public: bool = False) -> dict[str, str]:
    line = _file_line(public)
    if line not in what and _WHOLE_FILE not in what and _PUBLIC_FILE not in what:
        what = f"{what} {line}"
    prose = safe_prose(str(body or ""))
    if not prose:
        prose = "This week's record did not add a new sentence here. The counts above are still the ones to use."
    return {"title": title, "what": what, "body": prose}


def _plan_text(plan: dict[str, Any]) -> str:
    tasks = plan.get("tasks") or []
    if not tasks:
        return ""
    lines = []
    for task in tasks:
        name = _plain_task_name(str(task.get("name") or "task"))
        lines.append(f"{name}. Status {task.get('status', 'To Do')}. Owner {task.get('owner', 'the team')}.")
    return " ".join(lines)


def _risk_text(risks: list[dict[str, Any]]) -> str:
    if not risks:
        return ""
    lines = []
    for risk in risks:
        lines.append(
            f"{risk.get('id', 'Risk')}: {risk.get('description', '')} "
            f"Likelihood {risk.get('likelihood', '')}, impact {risk.get('impact', '')}."
        )
    return " ".join(lines)


def _jira_text(jira: dict[str, Any], base_url: str) -> str:
    issues = list(jira.get("issues") or [])
    epic = jira.get("epic") or {}
    if epic.get("key"):
        issues = [epic, *issues]
    if not issues:
        return "No ticket link came back for this run."
    live = str(jira.get("mode") or "").startswith("live") and bool(base_url)
    lines = []
    for issue in issues:
        key = str(issue.get("key") or "")
        if not key:
            continue
        summary = safe_prose(str(issue.get("summary") or issue.get("name") or "ticket"))
        if live:
            lines.append(f"{key}: {summary} Link {base_url.rstrip('/')}/browse/{key}.")
        else:
            lines.append(f"{key}: {summary}")
    return " ".join(lines) if lines else "No ticket link came back for this run."
