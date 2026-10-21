# invalid-agent

Simulated field-quality investigation for a program manager's portfolio. A customer says the invalid rate on a fictional molecular panel broke the promised validity (at least 98%, so the invalid rate must stay at or below 2%). Invalid Bot runs the weekly loop: plan, execute, stakeholder update, new feedback, re-plan, resolve. It ends in a fishbone, 5 Whys, an 8D/CAPA record, and a seven-slide exec deck.

**Simulation. Synthetic data. Not for clinical use. Not a medical device.**

The language model does not calculate. Rates, intervals, control limits, hypothesis scores, costs, and the projection are Python. The model, when one is connected, only narrates. A numeric-fidelity check rejects a draft that introduces a number the facts do not contain, and the template replaces that draft.

## Architecture

```mermaid
flowchart LR
  yaml[Scenario YAML] --> gen[Seeded generator]
  gen --> metrics[Rates, SPC, Pareto]
  metrics --> rank[Evidence ranker]
  rank --> graph[LangGraph]
  graph --> notes[Memos, RAG notes, CAPA]
  notes --> guard[Numeric-fidelity check]
  graph --> deck[Week-4 exec deck]
  llm["LLM_MODEL, optional"] --> notes
```

The graph is triage once, then plan, RCA, and status, repeating until the requested week. Week 4 adds close-out. The dataframe is not stored on the graph state. Each node regenerates it from the scenario seed.

## Quickstart

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m invalid_agent.graph --scenario bad_lot --week 4
streamlit run streamlit_app.py
```

Week 4 writes `out/exec_deck.pptx` and `out/closeout.md`. The dashboard default is rules-only: templates and computed numbers, no model download.

```bash
python evals/run_eval.py --backend deterministic
```

That command rewrites `evals/reports/<date>.md`. CI runs the same script with `--limit 5 --smoke`.

## Models

`LLM_MODEL` is the only model setting.

| Where | Model | Notes |
|---|---|---|
| Local Ollama (default) | `llama3.1:8b` (Meta Llama 3.1 8B) | `ollama pull llama3.1:8b`, then `LLM_BACKEND=ollama` |
| Hosted Streamlit | Rules-only (deterministic) | Streamlit Community Cloud has no Ollama, so the hosted page does not run a model. `llama3.2:1b` is the suggested small tag for local or self-hosted Ollama (`LLM_MODEL=llama3.2:1b`). |
| Alternatives | Gemma 3 (`gemma3`), Phi-4 (`phi4`) | Set `LLM_MODEL` to that Ollama tag. Same code path. |

`LLM_BACKEND=deterministic` is the default and the CI path. `LLAMACPP_MODEL_PATH` is a file path for an optional Llama 3.2 1B GGUF, not a second model name. Leave the backend on `deterministic` when the file is absent.

## Eval

From `evals/reports/2026-10-20.md`. n = 22 synthetic scenarios, 4 held out. Gates were the Session 3 constants. They were not refit. Prompts were not edited against either split.

| Split | n | Evidence top-1 | Evidence top-3 | Keyword top-1 |
|---|---:|---:|---:|---:|
| All | 22 | 22/22 | 22/22 | 3/22 |
| Not held out | 18 | 18/18 | 18/18 | 2/18 |
| Holdout | 4 | 4/4 | 4/4 | 1/4 |

Week-0 graph on the same 22: numeric fidelity 22/22, 5 Whys citations 22/22, escalation matched the spec comparison 22/22. Mean latency 0.55s on the deterministic backend.

Failure notes that have to travel with the 22/22 cell:

- The keyword ranker, which only reads the week-0 note, matched 3/22. Those three are the flat files. On the three red herrings it repeated the note. On `weak_lot` it named the lot; the evidence ranker correctly stayed at `no_single_cause`.
- On four drift scenarios a reagent-lot stratum also cleared the bar. Top-1 stayed on the instrument.
- Llama 3.1 8B and Llama 3.2 1B were not installed for that run. The table is two ranking policies, not two models. Do not quote it as a model-accuracy number.

## What Neel sets up

The repo runs with no keys.

1. Jira Cloud Free, only if live sync is wanted. Set `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`. Otherwise the investigation writes `SIM-*` issues to JSON.
2. Streamlit Community Cloud sign-in with GitHub. Select `app/streamlit_app.py` or the root `streamlit_app.py`. The hosted page runs rules-only (deterministic). Cloud has no Ollama.
3. Ollama, only for a local or self-hosted model: `ollama pull llama3.1:8b`. For the smaller tag, `ollama pull llama3.2:1b` and `LLM_MODEL=llama3.2:1b`. Gemma 3 and Phi-4 are the other documented tags.

## Limits

- The panel, the customers, and the field file are synthetic. openFDA MAUDE, the Mendeley HIL DOI, and Zenodo CBC are cited in `DATA_LICENSES.md` and are not redistributed.
- The projection clears the leading stratum on the same file. It is not observed follow-up. `bad_lot` never turns Green, because the file is not rewritten.
- Laptop snapshot folders under `C:\Users\neels\Grok_Bot\Project_Agent\` are not created here. Annotated tags `session-1` through `session-9` are the snapshots. Check out the tag and copy the tree.
- There is no narrated MP4. `walkthroughs/session-N.yaml` is the beat list for a recording.
- No agent swarm, no extra integrations, no fine-tune.

## Layout

Session notes: `docs/sessions/session-N/LOGIC_TRACE.md` and `QUIZ.md`. Résumé lines copied from the eval report: `RESUME_BULLETS.md`. Product framing: `PRD.md`. Disclaimer: `SIMULATION_DISCLAIMER.md`.
