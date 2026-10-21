"""Week-0 memo quotes the computed rate and escalates the bad lot."""

from pathlib import Path

from invalid_agent.metrics.hypotheses import rank_hypotheses
from invalid_agent.metrics.rates import overall_rate
from invalid_agent.sim.generate import generate, load_scenario

ROOT = Path(__file__).resolve().parents[1]
BAD_LOT = ROOT / "scenarios" / "bad_lot.yaml"


def test_bad_lot_hypothesis_is_the_reagent_lot():
    scenario = load_scenario(BAD_LOT)
    df = generate(scenario)
    ranked = rank_hypotheses(df, scenario["spec_invalid_rate"])
    assert ranked[0]["cause"] == "bad_reagent_lot"
    assert ranked[0]["category"] == "Material"
    assert ranked[0]["level"] == "L-4419"
    assert ranked[0]["evidence_ids"]


def test_flat_table_is_not_a_single_cause():
    import pandas as pd

    n = 400
    index = list(range(n))
    df = pd.DataFrame(
        {
            "reagent_lot": ["L-1"] * (n // 2) + ["L-2"] * (n // 2),
            "instrument": ["INS-01" if i % 2 == 0 else "INS-02" for i in index],
            "software_version": ["2.3.1"] * n,
            "operator": ["OP-01" if i % 2 == 0 else "OP-02" for i in index],
            "site": ["SITE-A" if i % 2 == 0 else "SITE-B" for i in index],
            "shipping_temp_c": [20.0] * n,
            "hemolysis_index": [5.0] * n,
            # Every 25th row. The stride shares those hits across lots and instruments.
            "invalid": [i % 25 == 0 for i in index],
        }
    )
    ranked = rank_hypotheses(df, 0.02)
    assert ranked[0]["cause"] == "no_single_cause"


def test_week0_command_writes_a_faithful_memo(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    from invalid_agent.graph import main

    main(["--scenario", str(BAD_LOT), "--week", "0", "--out", str(tmp_path)])
    text = (tmp_path / "week0_triage.md").read_text(encoding="utf-8")
    scenario = load_scenario(BAD_LOT)
    df = generate(scenario)
    overall = overall_rate(df, scenario["spec_invalid_rate"], scenario["promised_validity"])
    assert f"{overall['rate'] * 100:.2f}%" in text
    assert "Escalate" in text
    assert "L-4419" in text
    assert "Not for clinical use" in text
    assert "27.40" not in text
    fidelity = (tmp_path / "week0_fidelity.json").read_text(encoding="utf-8")
    assert '"ok": true' in fidelity
