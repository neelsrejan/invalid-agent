"""Fishbone rank, citation rule, and the 8D headings on the bad lot."""

import pytest

from invalid_agent.nodes.rca import rca_node, validate_whys
from invalid_agent.sim.generate import generate, load_scenario
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _state(week: int = 1) -> dict:
    scenario = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    return {"scenario": scenario, "scenario_id": scenario["id"], "week": week}


def test_why_without_a_citation_is_rejected():
    with pytest.raises(ValueError, match="no citation"):
        validate_whys(
            [{"number": 1, "question": "Why?", "answer": "Because.", "citations": []}],
            {"metric:overall:rate": "overall"},
        )


def test_unknown_citation_is_rejected():
    with pytest.raises(ValueError, match="unknown id"):
        validate_whys(
            [{"number": 2, "question": "Why?", "answer": "Because.", "citations": ["made:up"]}],
            {"metric:overall:rate": "overall"},
        )


def test_bad_lot_fishbone_ranks_material_and_whys_end_on_the_lot():
    update = rca_node(_state(1))
    top = update["fishbone"]["branches"][0]
    assert top["category"] == "Material"
    assert top["cause"] == "bad_reagent_lot"
    steps = update["five_whys"]["steps"]
    assert len(steps) == 5
    for step in steps:
        assert step["citations"]
        for citation in step["citations"]:
            assert citation in update["evidence_catalog"]
    terminal = steps[-1]["answer"]
    assert "L-4419" in terminal
    assert "lot-level" in terminal
    capa = update["capa"]["markdown"]
    for heading in ("D1 Team", "D2 Problem", "D3 Containment", "D4 Root cause", "D5 Corrective action", "D6 Validation", "D7 Prevention", "D8 Closure"):
        assert heading in capa
    assert "define" in update["capa"]["dmaic"]
    joined = update["fishbone"]["markdown"] + update["five_whys"]["markdown"]
    assert "Not for clinical use" in joined


def test_week0_command_still_writes_the_memo_and_now_the_rca(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    from invalid_agent.graph import main

    main(["--scenario", "bad_lot", "--week", "0", "--out", str(tmp_path)])
    assert (tmp_path / "week0_triage.md").exists()
    assert "Material" in (tmp_path / "fishbone.md").read_text(encoding="utf-8")
    assert (tmp_path / "capa8d.md").exists()
