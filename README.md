# invalid-agent

Simulated field-quality investigation. A customer says the invalid rate on a molecular panel broke the promised validity (≥ 98%). Invalid Bot runs the PM loop: plan, execute, stakeholder update, new feedback, re-plan, resolve.

**Simulation. Synthetic data. Not for clinical use.**

Session 3 adds the Week-0 triage memo. The graph calls the metrics, ranks hypotheses from the strata, and runs a numeric-fidelity check on the prose. The default backend is a template, not a model. RCA, the plan, the dashboard, and the deck land in later tags.

```bash
python -m invalid_agent.sim.generate scenarios/bad_lot.yaml
python -m invalid_agent.graph --scenario bad_lot --week 0
```

Read [PRD.md](PRD.md), [SIMULATION_DISCLAIMER.md](SIMULATION_DISCLAIMER.md), and [DATA_LICENSES.md](DATA_LICENSES.md). The backlog a Jira Free site can import is [docs/jira/backlog.json](docs/jira/backlog.json).

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

No API keys. Copy `.env.example` to `.env` only when you have a Jira site or a local Ollama model.
