# invalid-agent

Simulated field-quality investigation. A customer says the invalid rate on a molecular panel broke the promised validity (≥ 98%). Invalid Bot runs the PM loop: plan, execute, stakeholder update, new feedback, re-plan, resolve.

**Simulation. Synthetic data. Not for clinical use.**

Session 6 runs the weekly loop. Each new stakeholder note re-plans the Gantt and the risk register, appends a decision-log entry, and writes a RAG update for the customer, the internal team, and leadership. The dashboard, the evals, and the deck land in later tags.

```bash
python -m invalid_agent.graph --scenario bad_lot --week 3
```

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

## Models

`LLM_MODEL` is the only model setting.

| Where | Model | Notes |
|---|---|---|
| Local Ollama (default) | `llama3.1:8b` (Meta Llama 3.1 8B) | `ollama pull llama3.1:8b`, then `LLM_BACKEND=ollama` |
| Hosted Streamlit | Llama 3.2 1B (`llama3.2:1b`) | Used only when a model is available. Otherwise the page stays on the deterministic backend. No weights are bundled. |
| Alternatives | Gemma 3 (`gemma3`), Phi-4 (`phi4`) | Set `LLM_MODEL` to that Ollama tag. Same code path. |

`LLM_BACKEND=deterministic` is the default and the CI path. A missing model, a transport error, or a draft that fails the numeric-fidelity check is replaced by the template. The rejected draft is not shown.
