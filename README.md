# invalid-agent

Simulated field-quality investigation. A customer says the invalid rate on a molecular panel broke the promised validity (≥ 98%). Invalid Bot runs the PM loop: plan, execute, stakeholder update, new feedback, re-plan, resolve.

**Simulation. Synthetic data. Not for clinical use.**

Session 5 adds the 4-week Gantt, the likelihood × impact risk register, and a Jira sync that writes a JSON dry-run when no token is set. Stakeholder updates, the dashboard, and the deck land in later tags.

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
