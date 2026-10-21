"""Hand checks for the Wilson interval, the p-chart, and the Pareto."""

import math

import pandas as pd
import pytest
from scipy import stats

from invalid_agent.metrics.pareto import pareto
from invalid_agent.metrics.rates import chi_square_by, overall_rate, stratified_rates, wilson_interval
from invalid_agent.metrics.spc import control_limits, p_chart, western_electric


def test_wilson_matches_an_independent_hand_calculation():
    k, n = 10, 100
    low, high = wilson_interval(k, n)
    z = float(stats.norm.ppf(0.975))
    p_hat = k / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    center = (p_hat + z2 / (2.0 * n)) / denominator
    margin = z * math.sqrt(p_hat * (1.0 - p_hat) / n + z2 / (4.0 * n * n)) / denominator
    assert low == pytest.approx(center - margin, abs=1e-12)
    assert high == pytest.approx(center + margin, abs=1e-12)
    # Published rounding for 10/100 at 95% is about 5.5% to 17.4%.
    assert round(low, 3) == pytest.approx(0.055, abs=0.002)
    assert round(high, 3) == pytest.approx(0.174, abs=0.002)


def test_wilson_zero_events_stays_inside_the_unit_interval():
    low, high = wilson_interval(0, 100)
    assert low == 0.0
    assert 0.0 < high < 0.05


def test_control_limits_match_a_hand_calculation():
    lcl, ucl, se = control_limits(0.02, 100)
    expected_se = math.sqrt(0.02 * 0.98 / 100)
    assert se == pytest.approx(expected_se)
    assert ucl == pytest.approx(0.02 + 3 * expected_se)
    assert lcl == pytest.approx(0.0)  # 0.02 - 3*se is negative, so the chart floors at 0


def test_western_electric_rules_on_a_fixed_z_series():
    rule1 = western_electric([0.0, 0.0, 0.0, 3.5])
    assert any(hit["rule"] == 1 and hit["index"] == 3 for hit in rule1)

    rule2 = western_electric([0.0, 2.4, 2.6])
    assert any(hit["rule"] == 2 and hit["side"] == "high" for hit in rule2)

    rule4 = western_electric([0.2] * 8)
    assert any(hit["rule"] == 4 and hit["index"] == 7 for hit in rule4)


def test_p_chart_flags_a_planted_three_sigma_week():
    # Six quiet weeks at 2/100 and one week at 15/100. The quiet side has
    # only six points, so rule 4 (eight in a row) cannot fire. Rule 1 can.
    rows = []
    for week, invalids in enumerate([2, 2, 2, 2, 2, 2, 15]):
        for i in range(100):
            rows.append(
                {
                    "date": pd.Timestamp("2025-04-07") + pd.Timedelta(days=7 * week),
                    "invalid": i < invalids,
                }
            )
    chart = p_chart(pd.DataFrame(rows))
    assert any(hit["rule"] == 1 for hit in chart["violations"])
    loud = chart["points"][-1]
    assert loud["z"] > 3


def test_pareto_orders_and_closes_at_one():
    df = pd.DataFrame(
        {
            "invalid": [True, True, True, True, True, True, False],
            "invalid_code": ["INV-IC", "INV-IC", "INV-IC", "INV-SW", "INV-SW", "INV-HEM", ""],
        }
    )
    rows = pareto(df)
    assert [row["code"] for row in rows] == ["INV-IC", "INV-SW", "INV-HEM"]
    assert rows[-1]["cumulative_share"] == pytest.approx(1.0)
    assert rows[0]["share"] == pytest.approx(0.5)


def test_stratified_rate_and_chi_square_see_a_lot_split():
    df = pd.DataFrame(
        {
            "reagent_lot": ["L-BAD"] * 50 + ["L-OK"] * 50,
            "invalid": [True] * 20 + [False] * 30 + [True] * 2 + [False] * 48,
        }
    )
    strata = stratified_rates(df, "reagent_lot")
    assert strata[0]["level"] == "L-BAD"
    assert strata[0]["rate"] == pytest.approx(0.40)
    result = chi_square_by(df, "reagent_lot")
    assert result["p_value"] < 0.01
    overall = overall_rate(df, spec_invalid_rate=0.02)
    assert overall["k"] == 22
    assert overall["exceeds_spec"] is True
