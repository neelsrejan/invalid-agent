"""Score the evidence ranker against the injection-keyword ranker.

The language model is not required. ``--backend ollama`` is recorded when a
server answers; otherwise the report says the Llama comparison was not run.
Numbers in the report come from this script's counters.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

# The repo root is the parent of this file when the package is not installed.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from invalid_agent.metrics.hypotheses import rank_hypotheses
from invalid_agent.metrics.rates import overall_rate
from invalid_agent.sim.generate import generate, load_scenario

# First matching word wins. Software and hemolysis are checked before "lot"
# so a sentence that names both still has a deterministic naive call.
_KEYWORDS = (
    ("software", "software_version"),
    ("version", "software_version"),
    ("hemolysis", "preanalytical_hemolysis"),
    ("operator", "user_process_error"),
    ("temperature", "site_temperature"),
    ("excursion", "site_temperature"),
    ("instrument", "drifting_instrument"),
    ("drift", "drifting_instrument"),
    ("reagent", "bad_reagent_lot"),
    ("lot", "bad_reagent_lot"),
)


def scenario_paths(root: Path | None = None) -> list[Path]:
    folder = (root or _ROOT) / "scenarios"
    return sorted(folder.glob("*.yaml"))


def keyword_cause(scenario: dict[str, Any], week: int = 0) -> str:
    """Naive policy: the first cause-word in notes that have already arrived."""
    chunks: list[str] = []
    for item in scenario.get("injections") or []:
        if int(item.get("week", 0)) <= week:
            chunks.append(str(item.get("text", "")).lower())
    blob = "\n".join(chunks)
    for needle, cause in _KEYWORDS:
        if needle in blob:
            return cause
    return "no_single_cause"


def _expect(scenario: dict[str, Any]) -> str:
    block = scenario.get("eval") or {}
    if block.get("expect_cause"):
        return str(block["expect_cause"])
    cause = scenario.get("root_cause") or {}
    if cause.get("type") == "red_herring":
        return str(cause["true"]["type"])
    return str(cause.get("type", "no_single_cause"))


def score_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Rank-only score. Does not call the graph or a model."""
    frame = generate(scenario)
    spec = float(scenario.get("spec_invalid_rate", 0.02))
    ranked = rank_hypotheses(frame, spec)
    causes = [row["cause"] for row in ranked]
    expect = _expect(scenario)
    overall = overall_rate(frame, spec, float(scenario.get("promised_validity", 0.98)))
    extra = ""
    if len(ranked) > 1 and ranked[0]["cause"] != "no_single_cause":
        extra = str(ranked[1]["cause"])
    return {
        "id": str(scenario.get("id")),
        "expect": expect,
        "evidence": causes[0],
        "keyword": keyword_cause(scenario, 0),
        "top1": causes[0] == expect,
        "top3": expect in causes[:3],
        "keyword_hit": keyword_cause(scenario, 0) == expect,
        "holdout": bool((scenario.get("eval") or {}).get("holdout")),
        "below_bar": bool((scenario.get("eval") or {}).get("below_bar")),
        "injected_cause": str((scenario.get("eval") or {}).get("injected_cause") or ""),
        "extra_stratum": extra,
        "rate": overall["rate"],
        "exceeds_spec": bool(overall["exceeds_spec"]),
        "k": overall["k"],
        "n": overall["n"],
    }


def _rate(rows: list[dict[str, Any]], key: str) -> str:
    if not rows:
        return "n=0"
    hits = sum(1 for row in rows if row[key])
    return f"{hits}/{len(rows)} ({hits / len(rows) * 100:.1f}%)"


def run_graph_checks(scenario_name: str, out_dir: Path) -> dict[str, Any]:
    """Week-0 graph: fidelity, citations, escalation, latency."""
    from invalid_agent.graph import run_case

    started = time.perf_counter()
    result = run_case(scenario_name, 0, out_dir)
    elapsed = time.perf_counter() - started
    catalog = result.get("evidence_catalog") or {}
    citations_ok = True
    for step in (result.get("five_whys") or {}).get("steps") or []:
        cites = step.get("citations") or []
        if not cites or any(cite not in catalog for cite in cites):
            citations_ok = False
    fidelity_ok = bool((result.get("fidelity") or {}).get("ok", True))
    fidelity_ok = fidelity_ok and bool((result.get("rca_fidelity") or {}).get("ok", True))
    for record in (result.get("status_fidelity") or {}).values():
        if isinstance(record, dict) and not record.get("ok", True):
            fidelity_ok = False
    memo = result.get("triage_memo") or {}
    escalate_ok = bool(memo.get("escalate")) == bool(memo.get("exceeds_spec"))
    return {
        "fidelity_ok": fidelity_ok,
        "citations_ok": citations_ok,
        "escalate_ok": escalate_ok,
        "escalate": bool(memo.get("escalate")),
        "seconds": round(elapsed, 2),
    }


def _model_section(backend: str) -> str:
    probed = "not contacted"
    if backend == "ollama":
        probed = _probe_ollama()
    return "\n".join(
        [
            "## Model comparison",
            "",
            "Local default: Meta Llama 3.1 8B, Ollama tag `llama3.1:8b`, set by `LLM_MODEL`.",
            "Hosted Streamlit runs rules-only (deterministic); Streamlit Cloud has no Ollama.",
            "Suggested small tag for local or self-hosted runs: Llama 3.2 1B, tag `llama3.2:1b`.",
            "Documented alternatives, same variable: Gemma 3 (`gemma3`) and Phi-4 (`phi4`).",
            "",
            f"This command used `--backend {backend}`. Ollama probe: {probed}.",
            "The table is two ranking policies on the deterministic metrics, not two model weights.",
            "A model draft is shown only when the numeric-fidelity check accepts it.",
            "This report does not give an accuracy number for a model that did not run.",
            "",
        ]
    )


def _probe_ollama() -> str:
    try:
        import httpx

        from invalid_agent.config import load_settings

        settings = load_settings()
        response = httpx.get(f"{settings.ollama_host}/api/tags", timeout=2.0)
        response.raise_for_status()
        names = [str(item.get("name", "")) for item in response.json().get("models") or []]
        wanted = [settings.llm_model, "llama3.2:1b"]
        present = [name for name in wanted if any(name.split(":")[0] in item for item in names)]
        if not names:
            return "server answered and listed no models"
        if present:
            return "server has " + ", ".join(present)
        return "server answered; llama3.1:8b and llama3.2:1b were not both listed (" + ", ".join(names[:6]) + ")"
    except Exception as exc:
        return f"unavailable ({type(exc).__name__})"


def render_report(rows: list[dict[str, Any]], graph_rows: list[dict[str, Any]], backend: str) -> str:
    holdout = [row for row in rows if row["holdout"]]
    seen = [row for row in rows if not row["holdout"]]
    misses = [row for row in rows if not row["top1"]]
    keyword_misses = [row for row in rows if not row["keyword_hit"]]
    extras = [row for row in rows if row["extra_stratum"]]
    lines = [
        f"# Invalid Bot eval {date.today().isoformat()}",
        "",
        "Simulation. Synthetic data. Not for clinical use.",
        "",
        f"n = {len(rows)} scenarios. Holdout n = {len(holdout)}. "
        "Prompts were not edited against the full set or the holdout. "
        "The evidence gates are the Session 3 constants. They were not refit on this set.",
        "",
        "## Evidence ranker vs injection-keyword ranker",
        "",
        "Week-0 notes only. The keyword ranker never sees the table. The evidence ranker never sees the notes.",
        "",
        "| Split | n | Evidence top-1 | Evidence top-3 | Keyword top-1 |",
        "|---|---:|---:|---:|---:|",
        f"| All | {len(rows)} | {_rate(rows, 'top1')} | {_rate(rows, 'top3')} | {_rate(rows, 'keyword_hit')} |",
        f"| Not held out | {len(seen)} | {_rate(seen, 'top1')} | {_rate(seen, 'top3')} | {_rate(seen, 'keyword_hit')} |",
        f"| Holdout | {len(holdout)} | {_rate(holdout, 'top1')} | {_rate(holdout, 'top3')} | {_rate(holdout, 'keyword_hit')} |",
        "",
        "| Scenario | Expect | Evidence | Keyword | Holdout | Below bar | Rate |",
        "|---|---|---|---|---|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['expect']} | {row['evidence']} | {row['keyword']} | "
            f"{'yes' if row['holdout'] else ''} | {'yes' if row['below_bar'] else ''} | {row['rate'] * 100:.2f}% |"
        )
    lines.extend(["", "## Failure notes", ""])
    if not misses:
        lines.append("Evidence top-1 missed none of these scenarios, including the weak-lot case that should stay `no_single_cause`.")
    else:
        lines.append("Evidence top-1 misses:")
        for row in misses:
            lines.append(f"- {row['id']}: expected {row['expect']}, called {row['evidence']}.")
    lines.append("")
    lines.append(f"Keyword top-1 missed {len(keyword_misses)} of {len(rows)}. Those misses are the point of the comparison:")
    for row in keyword_misses:
        lines.append(f"- {row['id']}: keyword said {row['keyword']}, evidence said {row['evidence']} (expect {row['expect']}).")
    if extras:
        lines.extend(["", "A second stratum also cleared the evidence bar. Top-1 stayed with the injected cause:"])
        for row in extras:
            lines.append(f"- {row['id']}: extra `{row['extra_stratum']}` behind `{row['evidence']}`.")
    below = [row for row in rows if row["below_bar"]]
    if below:
        lines.extend(["", "Built under the evidence bar (a correct call is `no_single_cause`, not the injected bump):"])
        for row in below:
            lines.append(
                f"- {row['id']}: injected `{row['injected_cause'] or 'see YAML'}`, evidence `{row['evidence']}`, keyword `{row['keyword']}`."
            )
    if graph_rows:
        ok_f = sum(1 for row in graph_rows if row["fidelity_ok"])
        ok_c = sum(1 for row in graph_rows if row["citations_ok"])
        ok_e = sum(1 for row in graph_rows if row["escalate_ok"])
        mean_s = sum(row["seconds"] for row in graph_rows) / len(graph_rows)
        lines.extend(
            [
                "",
                "## Week-0 graph checks",
                "",
                f"Ran `run_case` at week 0 on {len(graph_rows)} scenarios, backend deterministic.",
                f"Numeric fidelity: {ok_f}/{len(graph_rows)}.",
                f"5 Whys citations resolve in the catalog: {ok_c}/{len(graph_rows)}.",
                f"Escalation matches the spec comparison in the memo: {ok_e}/{len(graph_rows)}.",
                f"Mean latency: {mean_s:.2f}s per scenario.",
                "",
            ]
        )
    lines.append(_model_section(backend))
    lines.append("Synthetic data. Not a medical device.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score Invalid Bot scenarios offline.")
    parser.add_argument("--backend", default="deterministic", choices=["deterministic", "ollama", "llamacpp"])
    parser.add_argument("--limit", type=int, default=0, help="Score only the first N scenarios. 0 means all.")
    parser.add_argument("--smoke", action="store_true", help="Write under out/ and exit 1 on an evidence or fidelity miss.")
    parser.add_argument("--skip-graph", action="store_true", help="Rank only. Used by unit tests.")
    parser.add_argument("--out", default="", help="Report path. Default: evals/reports/<date>.md or out/eval_smoke.md.")
    args = parser.parse_args(argv)

    paths = scenario_paths()
    if args.limit:
        paths = paths[: args.limit]
    rows = [score_scenario(load_scenario(path)) for path in paths]
    graph_rows: list[dict[str, Any]] = []
    if not args.skip_graph:
        base = _ROOT / "out" / "eval"
        for path, row in zip(paths, rows, strict=True):
            checked = run_graph_checks(str(path), base / row["id"])
            checked["id"] = row["id"]
            graph_rows.append(checked)
            row.update(checked)
    report = render_report(rows, graph_rows, args.backend)
    if args.out:
        destination = Path(args.out)
    elif args.smoke:
        destination = _ROOT / "out" / "eval_smoke.md"
    else:
        destination = _ROOT / "evals" / "reports" / f"{date.today().isoformat()}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote {destination}")
    if args.smoke:
        if any(not row["top1"] for row in rows):
            return 1
        if any(not row.get("fidelity_ok", True) or not row.get("citations_ok", True) or not row.get("escalate_ok", True) for row in rows):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
