"""Graph state.

Keys added by later sessions are declared here so a node can fill them
without changing the channel list. Unused keys stay empty.
"""

from __future__ import annotations

from typing import Any, TypedDict


class CaseState(TypedDict, total=False):
    scenario_id: str
    scenario: dict[str, Any]
    week: int
    out_dir: str
    metrics: dict[str, Any]
    hypotheses: list[dict[str, Any]]
    evidence_catalog: dict[str, str]
    triage_memo: dict[str, Any]
    triage_markdown: str
    fidelity: dict[str, Any]
    fishbone: dict[str, Any]
    five_whys: dict[str, Any]
    capa: dict[str, Any]
    rca_fidelity: dict[str, Any]
    plan: dict[str, Any]
    risks: list[dict[str, Any]]
    decision_log: list[dict[str, Any]]
    status_updates: dict[str, str]
    jira: dict[str, Any]
    closeout: dict[str, Any]
    deck_path: str
