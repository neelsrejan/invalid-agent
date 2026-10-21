"""Build a synthetic run-level field file from a scenario YAML.

Each scenario fixes the random seed and the true root cause. Sites,
instruments, lots, software versions, and operators are assigned so that
a lot effect, an instrument effect, a temperature effect, a software
effect, a hemolysis effect, and an operator effect are not the same
column in disguise:

- The story is a reference lab. Collection site and instrument are independent.
- Lots and software versions follow a calendar, shared across the lab.
- Operators are independent of instrument.

``python -m invalid_agent.sim.generate scenarios/bad_lot.yaml`` prints the
rate, the interval, the top strata, and any Western Electric hits.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from invalid_agent.config import SPEC_INVALID_RATE, load_settings
from invalid_agent.metrics.pareto import pareto
from invalid_agent.metrics.rates import overall_rate, stratified_rates
from invalid_agent.metrics.spc import p_chart
from invalid_agent.sim.seeds import NOMINAL_SHIPPING_TEMP_C, sample_codes, sample_hemolysis

FAR = 10**9


def load_scenario(path: str | Path) -> dict[str, Any]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    raw["_path"] = str(path)
    return raw


def _levels(raw: Any) -> list[dict[str, Any]]:
    levels: list[dict[str, Any]] = []
    for item in raw or []:
        if isinstance(item, str):
            levels.append({"id": item, "start_day": 0, "end_day": FAR, "weight": 1.0})
        else:
            levels.append(
                {
                    "id": str(item["id"]),
                    "start_day": int(item.get("start_day", 0)),
                    "end_day": int(item.get("end_day", FAR)),
                    "weight": float(item.get("weight", 1.0)),
                }
            )
    if not levels:
        raise ValueError("a scenario list of sites, lots, or instruments is empty")
    return levels


def _assign(day_index: np.ndarray, levels: list[dict[str, Any]], rng: np.random.Generator) -> np.ndarray:
    out = np.empty(len(day_index), dtype=object)
    for day in np.unique(day_index):
        active = [level for level in levels if level["start_day"] <= int(day) < level["end_day"]] or levels
        weights = np.array([level["weight"] for level in active], dtype=float)
        weights = weights / weights.sum()
        positions = np.flatnonzero(day_index == day)
        picks = rng.choice(len(active), size=len(positions), p=weights)
        out[positions] = [active[int(i)]["id"] for i in picks]
    return out


def _redraw(
    df: pd.DataFrame,
    mask: np.ndarray,
    rate: float | np.ndarray,
    rng: np.random.Generator,
    dominant: str | None,
    dominant_weight: float = 0.7,
) -> None:
    """Replace invalid flags on ``mask``. ``rate`` is a scalar or a per-row probability."""
    positions = np.flatnonzero(mask)
    if len(positions) == 0:
        return
    probabilities = np.full(len(positions), float(rate)) if np.isscalar(rate) else np.asarray(rate, dtype=float)
    flags = rng.random(len(positions)) < probabilities
    df.loc[df.index[positions], "invalid"] = flags
    codes = np.full(len(positions), "", dtype=object)
    n_invalid = int(flags.sum())
    if n_invalid:
        codes[np.flatnonzero(flags)] = sample_codes(rng, n_invalid, dominant, dominant_weight)
    df.loc[df.index[positions], "invalid_code"] = codes


def _cause(df: pd.DataFrame, scenario: dict[str, Any], rng: np.random.Generator) -> None:
    rc = scenario.get("root_cause") or {"type": "none"}
    kind = str(rc.get("type", "none"))
    baseline = float(scenario["baseline_invalid_rate"])
    if kind in {"none", "null"}:
        return
    if kind == "red_herring":
        nested = dict(scenario)
        nested["root_cause"] = rc["true"]
        _cause(df, nested, rng)
        return
    if kind == "no_single_cause":
        _redraw(df, np.ones(len(df), dtype=bool), float(rc.get("global_invalid_rate", baseline * 2.3)), rng, None)
        return
    if kind == "bad_reagent_lot":
        mask = (df["reagent_lot"].to_numpy() == rc["lot_id"]) & (
            df["day_index"].to_numpy() >= int(rc.get("start_day", 0))
        )
        _redraw(df, mask, float(rc["stratum_invalid_rate"]), rng, rc.get("dominant_code", "INV-IC"))
        return
    if kind == "drifting_instrument":
        start = int(rc.get("start_day", 0))
        end = int(rc.get("end_day", int(df["day_index"].max()) + 1))
        mask = (df["instrument"].to_numpy() == rc["instrument_id"]) & (df["day_index"].to_numpy() >= start)
        days = df.loc[mask, "day_index"].to_numpy()
        span = max(1, end - start)
        progress = np.clip((days - start) / span, 0.0, 1.0)
        peak = float(rc["peak_invalid_rate"])
        probabilities = baseline + progress * (peak - baseline)
        _redraw(df, mask, probabilities, rng, rc.get("dominant_code", "INV-SW"))
        return
    if kind == "site_temperature":
        start = int(rc.get("start_day", 0))
        site_mask = (df["site"].to_numpy() == rc["site_id"]) & (df["day_index"].to_numpy() >= start)
        positions = np.flatnonzero(site_mask)
        fraction = float(rc.get("excursion_fraction", 0.6))
        n_pick = int(round(len(positions) * fraction))
        if n_pick == 0:
            return
        chosen = rng.choice(positions, size=n_pick, replace=False)
        low = float(rc.get("temp_low_c", 32.0))
        high = float(rc.get("temp_high_c", 38.0))
        df.loc[df.index[chosen], "shipping_temp_c"] = rng.uniform(low, high, size=n_pick)
        mask = np.zeros(len(df), dtype=bool)
        mask[chosen] = True
        _redraw(df, mask, float(rc["stratum_invalid_rate"]), rng, rc.get("dominant_code", "INV-TMP"))
        return
    if kind == "software_version":
        mask = df["software_version"].to_numpy() == str(rc["version"])
        if "start_day" in rc:
            mask = mask & (df["day_index"].to_numpy() >= int(rc["start_day"]))
        _redraw(df, mask, float(rc["stratum_invalid_rate"]), rng, rc.get("dominant_code", "INV-SW"))
        return
    if kind == "preanalytical_hemolysis":
        site_mask = df["site"].to_numpy() == rc["site_id"]
        n_site = int(site_mask.sum())
        df.loc[site_mask, "hemolysis_index"] = sample_hemolysis(rng, n_site, severe=True)
        cutoff = float(rc.get("index_cutoff", 100.0))
        high = site_mask & (df["hemolysis_index"].to_numpy() >= cutoff)
        _redraw(df, high, float(rc["stratum_invalid_rate"]), rng, rc.get("dominant_code", "INV-HEM"))
        return
    if kind == "user_process_error":
        mask = df["operator"].to_numpy() == rc["operator_id"]
        _redraw(df, mask, float(rc["stratum_invalid_rate"]), rng, rc.get("dominant_code", "INV-USR"))
        return
    raise ValueError(f"unknown root_cause.type: {kind}")


def generate(scenario: dict[str, Any]) -> pd.DataFrame:
    """Return one row per run. Re-running with the same scenario returns the same rows."""
    horizon = int(scenario.get("horizon_days", 180))
    per_day = int(scenario.get("runs_per_day", 80))
    n = horizon * per_day
    rng = np.random.default_rng(int(scenario["seed"]))
    day_index = np.repeat(np.arange(horizon, dtype=int), per_day)
    start = np.datetime64(str(scenario.get("start_date", "2025-04-01")), "D")
    dates = start + day_index.astype("timedelta64[D]")

    sites = _levels(scenario["sites"])
    site_ids = _assign(day_index, sites, rng)
    customers = [str(c) for c in scenario["customers"]]
    site_order = [level["id"] for level in sites]
    customer_for = {site: customers[i % len(customers)] for i, site in enumerate(site_order)}

    mean_t, sd_t = NOMINAL_SHIPPING_TEMP_C
    df = pd.DataFrame(
        {
            "run_id": [f"R{i:06d}" for i in range(n)],
            "date": pd.to_datetime(dates),
            "day_index": day_index,
            "customer": [customer_for[site] for site in site_ids],
            "site": site_ids,
            "instrument": _assign(day_index, _levels(scenario["instruments"]), rng),
            "reagent_lot": _assign(day_index, _levels(scenario["lots"]), rng),
            "software_version": _assign(day_index, _levels(scenario["software_versions"]), rng),
            "operator": _assign(day_index, _levels(scenario["operators"]), rng),
            "hemolysis_index": sample_hemolysis(rng, n, severe=False),
            "shipping_temp_c": rng.normal(mean_t, sd_t, size=n),
            "invalid": False,
            "invalid_code": "",
        }
    )
    baseline = float(scenario["baseline_invalid_rate"])
    _redraw(df, np.ones(n, dtype=bool), baseline, rng, None)
    _cause(df, scenario, rng)
    df["invalid"] = df["invalid"].astype(bool)
    df.attrs["scenario_id"] = str(scenario.get("id", "scenario"))
    return df


def summarize(df: pd.DataFrame, scenario: dict[str, Any]) -> str:
    spec = float(scenario.get("spec_invalid_rate", SPEC_INVALID_RATE))
    promised = float(scenario.get("promised_validity", 1.0 - spec))
    overall = overall_rate(df, spec, promised)
    lines = [
        f"Scenario: {scenario.get('id')} — {scenario.get('title', '')}".rstrip(" —"),
        (
            f"Runs: {overall['n']}   Invalids: {overall['k']}   "
            f"Invalid rate: {overall['rate'] * 100:.2f}%"
        ),
        (
            f"Wilson 95% CI: {overall['ci_low'] * 100:.2f}% – {overall['ci_high'] * 100:.2f}%"
        ),
        (
            f"Spec: invalid rate ≤ {spec * 100:.2f}% "
            f"(promised validity ≥ {promised * 100:.2f}%)  "
            f"{'EXCEEDS SPEC' if overall['exceeds_spec'] else 'within spec'}"
        ),
    ]
    for column, label in (
        ("reagent_lot", "lot"),
        ("instrument", "instrument"),
        ("site", "site"),
        ("software_version", "software"),
        ("operator", "operator"),
    ):
        top = stratified_rates(df, column)[:3]
        pretty = ", ".join(f"{row['level']} {row['rate'] * 100:.2f}% (n={row['n']})" for row in top)
        lines.append(f"Top {label}: {pretty}")
    chart = p_chart(df)
    rule_counts: dict[int, int] = {}
    for hit in chart["violations"]:
        rule_counts[hit["rule"]] = rule_counts.get(hit["rule"], 0) + 1
    if rule_counts:
        rendered = ", ".join(f"rule {rule}: {count}" for rule, count in sorted(rule_counts.items()))
        lines.append(f"Western Electric violations: {rendered}")
    else:
        lines.append("Western Electric violations: none")
    head = pareto(df)[:3]
    if head:
        lines.append(
            "Pareto head: " + ", ".join(f"{row['code']} {row['share'] * 100:.1f}%" for row in head)
        )
    lines.append("Synthetic data. Not for clinical use.")
    return "\n".join(lines)


def write_dataset(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic field file and print the SPC summary.")
    parser.add_argument("scenario", help="Path to a scenario YAML, e.g. scenarios/bad_lot.yaml")
    parser.add_argument("--out", default="", help="CSV path. Default: <out>/<scenario id>.csv")
    args = parser.parse_args(argv)
    scenario = load_scenario(args.scenario)
    df = generate(scenario)
    settings = load_settings()
    destination = Path(args.out) if args.out else settings.out_dir / "data" / f"{scenario.get('id', 'scenario')}.csv"
    write_dataset(df, destination)
    print(summarize(df, scenario))
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
