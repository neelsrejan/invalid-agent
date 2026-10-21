"""Pydantic contracts for the artifacts the graph stores.

Narrative markdown lives beside these objects. The objects are the
fields a test can assert without parsing prose.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HypothesisRef(BaseModel):
    cause: str
    category: str
    level: str | None = None
    score: float
    evidence_ids: list[str] = Field(default_factory=list)


class TriageMemo(BaseModel):
    scenario_id: str
    week: int
    device: str
    rate: float
    ci_low: float
    ci_high: float
    spec_invalid_rate: float
    promised_validity: float
    exceeds_spec: bool
    escalate: bool
    severity: str
    top_lot: str
    hypotheses: list[HypothesisRef]
    fidelity_ok: bool
