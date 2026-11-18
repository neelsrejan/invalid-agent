"""Real MAUDE shapes: numeric lot ids, a ninth fishbone rank, and spec claims."""

from __future__ import annotations

import pandas as pd

from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.metrics.hypotheses import evidence_catalog
from invalid_agent.narrative import prompt_for
from invalid_agent.nodes.rca import (
    MIN_CONTRAST_N,
    _contrast_id,
    rca_node,
    structure_numbers,
)
from invalid_agent.sim.generate import load_scenario

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_structure_numbers_include_rank_nine():
    assert 9 in structure_numbers(1, 9)
    assert 8 in structure_numbers(1, 1)
    assert structure_numbers(1, 1) == list(range(0, 9))


def test_contrast_skips_a_one_report_lot():
    assert MIN_CONTRAST_N == 5
    catalog = {
        "metric:overall:rate": "Invalid-type share of reported events 4.00% (8 of 200 reports).",
        "metric:manufacturer:Firm North:rate": "manufacturer Firm North invalid rate 40.00% (40 of 100).",
        "metric:manufacturer:Firm North:n": "manufacturer Firm North has 100 runs.",
        "metric:reagent_lot:10713760:rate": "reagent_lot 10713760 invalid rate 100.00% (1 of 1).",
        "metric:reagent_lot:10713760:n": "reagent_lot 10713760 has 1 runs.",
        "metric:reagent_lot:LOT-A:rate": "reagent_lot LOT-A invalid rate 10.00% (10 of 100).",
        "metric:reagent_lot:LOT-A:n": "reagent_lot LOT-A has 100 runs.",
    }
    hit = {"column": "manufacturer", "level": "Firm North"}
    chosen = _contrast_id(hit, catalog)
    assert chosen == "metric:reagent_lot:LOT-A:rate"
    assert "10713760" not in chosen


def _shaped_frame() -> pd.DataFrame:
    start = pd.Timestamp("2024-01-01")
    rows: list[dict] = []

    def add(count: int, invalids: int, manufacturer: str, lot: str, brand: str) -> None:
        for index in range(count):
            rows.append(
                {
                    "date": start + pd.Timedelta(days=index % 50),
                    "invalid": index < invalids,
                    "invalid_code": "INV-NOR" if index < invalids else "",
                    "manufacturer": manufacturer,
                    "brand_name": brand,
                    "reagent_lot": lot,
                    "instrument": brand,
                    "site": "PUBLIC-MAUDE",
                    "software_version": "UNREPORTED",
                    "operator": "UNREPORTED",
                    "customer": manufacturer,
                }
            )

    add(120, 50, "Firm North", "LOT-A", "Brand One")
    add(120, 6, "Firm South", "LOT-B", "Brand Two")
    add(1, 1, "Firm North", "10713760", "Brand One")
    frame = pd.DataFrame(rows)
    frame.attrs["spec_estimable"] = False
    frame.attrs["denominator"] = "reported_events"
    return frame


def test_rca_accepts_a_numeric_lot_id_and_a_ninth_rank(monkeypatch):
    frame = _shaped_frame()
    monkeypatch.setattr("invalid_agent.nodes.rca.load_frame", lambda scenario: frame)
    scenario = load_scenario(ROOT / "cases" / "openfda_ooi.yaml")
    update = rca_node({"scenario": scenario, "scenario_id": scenario["id"], "week": 4})
    assert update["rca_fidelity"]["ok"] is True
    assert len(update["fishbone"]["branches"]) >= 8
    step3 = update["five_whys"]["steps"][2]
    assert all("10713760" not in citation for citation in step3["citations"])
    catalog = evidence_catalog(frame, 0.02, 0.98)
    facts_text = (
        "## Rank 9. Material — reported_manufacturer\n"
        "Citations: metric:reagent_lot:10713760:rate.\n"
        "reagent_lot 10713760 invalid rate 100.00% (1 of 1)."
    )
    from invalid_agent.nodes.rca import stratum_levels

    labels = stratum_levels(catalog)
    assert "10713760" in labels
    checked = check_narrative(
        facts_text,
        {"catalog": catalog, "labels": labels, "structure": structure_numbers(2, 9), "week": 4},
    )
    assert checked.ok is True
    assert 10713760.0 not in checked.unknown
    assert 9.0 not in checked.unknown


def test_spec_claim_must_match_the_rate():
    facts = {
        "overall": {
            "rate": 0.0261,
            "spec_invalid_rate": 0.02,
            "rate_pct": 2.61,
            "spec_pct": 2.0,
            "n": 4221,
            "k": 110,
        }
    }
    denied = "The overall invalid rate is 2.61% and does not exceed the specification."
    rejected = check_narrative(denied, facts)
    assert rejected.ok is False
    assert rejected.claims
    honest = "The overall invalid rate is 2.61% (110 of 4221). The 2% cap is not estimable from reports."
    assert check_narrative(honest, facts).ok is True
    low = {
        "overall": {"rate": 0.01, "spec_invalid_rate": 0.02, "rate_pct": 1.0, "spec_pct": 2.0, "n": 100, "k": 1}
    }
    assert check_narrative("The rate is 1.00% and exceeds the specification.", low).ok is False
    assert check_narrative("The rate is 1.00% and does not exceed the specification.", low).ok is True


def test_prompt_rounds_raw_floats():
    text = prompt_for("triage", {"rate": 0.026060175312})
    assert "0.026060175" not in text
    assert "0.0261" in text
