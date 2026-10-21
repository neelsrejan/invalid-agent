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


class FishboneBranch(BaseModel):
    category: str
    cause: str
    statement: str
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    score: float
    rank: int


class Fishbone(BaseModel):
    branches: list[FishboneBranch]


class WhyStep(BaseModel):
    number: int
    question: str
    answer: str
    citations: list[str]


class FiveWhys(BaseModel):
    cause: str
    terminal_cause: str
    steps: list[WhyStep]


class CAPA8D(BaseModel):
    d1_team: str
    d2_problem: str
    d3_containment: str
    d4_root_cause: str
    d5_corrective_action: str
    d6_validation: str
    d7_prevention: str
    d8_closure: str
    dmaic: dict[str, str]
    preliminary_close: bool = True


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
