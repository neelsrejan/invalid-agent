"""Session metadata and practice tasks. Line numbers match the session tag."""

SESSIONS = [
    {
        "id": 1,
        "week": 1,
        "title": "PRD, backlog, and a skeleton that tests",
        "minutes": "75–90",
        "ticket": "INV-101, INV-102, INV-103",
        "artifact": "PRD, build backlog, green CI with no secrets",
        "blurb": "Name the promise (validity at least 98%), put nine Sprint 1 stories on a board, and make the repo install and test with an empty dependency list.",
        "read": [
            "PRD.md — the problem, the spec, and the out-of-scope list.",
            "docs/jira/backlog.json — count the Sprint 1 stories. There are nine, INV-101 to INV-109.",
        ],
        "practice": """On a private branch from the tag. Do not merge it to main.

```bash
git fetch --tags
git switch -c practice/session-1 session-1
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

On Windows the activate script is `.venv\\Scripts\\activate`. Expect the Session 1 suite to pass before you edit anything.

1. In `src/invalid_agent/config.py`, inside `load_settings`, add `"offline"` to the synonym set `{"rules", "rules-only", "mock"}`.
2. At the end of `test_unknown_backend_falls_back` in `tests/test_config.py`, add:

```python
monkeypatch.setenv("LLM_BACKEND", "OFFLINE")
assert load_settings().llm_backend == "deterministic"
```

3. Run `pytest` again.

**Extra credit.** Why does `"OFFLINE"` in capitals still work? Look at the `.lower()` on the environment value. And would the test pass even if you skipped step 1? Yes, because an unknown backend also falls back. Write a second assertion that fails unless `"offline"` is actually in the synonym set, so the test locks your change.

Commit on the practice branch. Pushing is optional. If you push, CI runs on that branch.
""",
    },
    {
        "id": 2,
        "week": 1,
        "title": "A synthetic field file and the metrics",
        "minutes": "80–100",
        "ticket": "INV-104, INV-105",
        "artifact": "Seeded field file, Wilson interval, p-chart, Pareto",
        "blurb": "The YAML is the cause, not the rate. Numpy, pandas, and scipy compute the spreadsheet a PM would otherwise rebuild by hand. No model is involved.",
        "read": [
            "scenarios/bad_lot.yaml — lot, start day, and stratum rate are the knobs. 3.67% is not in this file.",
            "scenarios/README.md — the YAML is the process, not an answer key of rates.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-2 session-2
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

`chi_square_by` in `src/invalid_agent/metrics/rates.py` returns p = 1 when the table has a single level. That branch is easy to "clean up" into a crash later. Lock it.

At the end of `tests/test_metrics.py` add:

```python
def test_one_stratum_chi_square_is_quiet():
    frame = pd.DataFrame(
        {
            "reagent_lot": ["L-ONLY"] * 30,
            "invalid": [True] * 4 + [False] * 26,
        }
    )
    result = chi_square_by(frame, "reagent_lot")
    assert result["p_value"] == 1.0
    assert result["chi2"] == 0.0
    assert result["levels"] == 1
```

`chi_square_by` and `pd` are already imported in that file. Run `pytest tests/test_metrics.py`.

**Extra credit.** Generate the walkthrough file and read the printout, then open the YAML again and point at the three knobs that are inputs. The command is `python -m invalid_agent.sim.generate scenarios/bad_lot.yaml`.
""",
    },
    {
        "id": 3,
        "week": 1,
        "title": "Week-0 triage memo and the fidelity guard",
        "minutes": "80–100",
        "ticket": "INV-108, INV-109",
        "artifact": "One-page triage memo whose numbers match the code",
        "blurb": "One LangGraph node writes the escalation memo. The model, if you attach one, does not get to invent a rate. A planted 27.40% dies in the guard.",
        "read": [
            "Run `python -m invalid_agent.graph --scenario bad_lot --week 0` and open `out/week0_triage.md`.",
            "The fidelity JSON next to it should say the backend is deterministic.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-3 session-3
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Proportions in (0, 1] contribute their percent form, which is why 3.67 is legal when the fact is 0.0367. Add a test that locks both sides of that bridge. In `tests/test_fidelity.py`:

```python
def test_percent_form_is_allowed_and_an_invented_percent_is_not():
    allowed = check_narrative("The rate is 3.67%.", {"rate": 0.0367})
    assert allowed.ok
    rejected = check_narrative("The rate is 27.40%.", {"rate": 0.0367})
    assert rejected.ok is False
    assert 27.4 in rejected.unknown or 27.40 in rejected.unknown
```

`check_narrative` is already imported. Run `pytest tests/test_fidelity.py`.

**Extra credit.** Explain why `{"rate": 0.0367}` allows the characters `3.67` without those characters being stored as a string. The walk is in `_walk_numbers`.
""",
    },
    {
        "id": 4,
        "week": 2,
        "title": "Fishbone, 5 Whys, and an 8D/CAPA",
        "minutes": "80–100",
        "ticket": "INV-201",
        "artifact": "fishbone.md, five_whys.md, capa8d.md",
        "blurb": "Turn the ranked hypothesis into a quality record. A Why with no citation is an error. On bad_lot the chain stops at lot L-4419, and a future QA note stays invisible at week 0.",
        "read": [
            "After `python -m invalid_agent.graph --scenario bad_lot --week 0`, open `out/fishbone.md`, `out/five_whys.md`, and `out/capa8d.md`.",
            "Find the week-1 QA injection in `scenarios/bad_lot.yaml` and notice it is not yet citable.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-4 session-4
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Add this to `tests/test_rca.py`. `index_injections` and `load_scenario` need importing if they are not already.

```python
def test_week_zero_hides_the_qa_lot_note():
    from invalid_agent.nodes.rca import index_injections
    from invalid_agent.sim.generate import load_scenario

    scenario = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    week0 = index_injections(scenario, week=0)
    assert not any("L-4419" in text for text in week0.values())
    week1 = index_injections(scenario, week=1)
    assert any(key.startswith("injection:1:") for key in week1)
    assert any("L-4419" in text for text in week1.values())
```

`ROOT` is already defined in that test file on this tag. If it is not, use `Path(__file__).resolve().parents[1]`. Run `pytest tests/test_rca.py`.

**Extra credit.** At week 2 the release-test injection is the contrary evidence on the lot bone. Say which week gate makes that sentence legal, in one line.
""",
    },
    {
        "id": 5,
        "week": 2,
        "title": "Gantt, risk register, and a Jira dry-run",
        "minutes": "80–100",
        "ticket": "INV-204, INV-205, INV-206",
        "artifact": "Gantt HTML and PNG, risk register, jira_issues.json",
        "blurb": "A four-week plan with owners and a likelihood-times-impact register. With no token the sync writes SIM-* keys and does not open a socket.",
        "read": [
            "Run `python -m invalid_agent.graph --scenario bad_lot --week 2` and open the Gantt HTML, `risk_register.md`, and `jira_issues.json`.",
            "Confirm the epic key starts with SIM- and that T11 exists at week 2.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-5 session-5
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

`_assert_dependencies` compares ISO dates as strings and raises when a task starts before its predecessor ends. Lock that with a test in `tests/test_plan.py`:

```python
import pytest
from invalid_agent.nodes.planner import _assert_dependencies

def test_an_early_start_is_rejected():
    tasks = [
        {"id": "T1", "start": "2025-04-01", "end": "2025-04-04", "depends_on": []},
        {"id": "T2", "start": "2025-04-03", "end": "2025-04-06", "depends_on": ["T1"]},
    ]
    with pytest.raises(ValueError, match="T2 starts before T1"):
        _assert_dependencies(tasks)
```

Run `pytest tests/test_plan.py tests/test_jira.py`.

**Extra credit.** Why is `"2025-04-03" < "2025-04-04"` safe, and what date format would make the same comparison lie?
""",
    },
    {
        "id": 6,
        "week": 2,
        "title": "Weekly injections and three RAG notes",
        "minutes": "80–100",
        "ticket": "INV-207, INV-208",
        "artifact": "Decision log, customer / internal / leadership notes",
        "blurb": "The same rate header goes to three audiences. The customer note does not name the cause. Here RAG means Red, Amber, Green.",
        "read": [
            "Run `python -m invalid_agent.graph --scenario bad_lot --week 3`.",
            "Diff `out/week0/plan.json` with `out/week2/plan.json`, and the two risk registers.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-6 session-6
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

The customer template must keep the rate and drop the lot. Add this to `tests/test_status.py`:

```python
def test_customer_note_keeps_the_rate_and_hides_the_lot():
    from invalid_agent.narrative import status_customer

    facts = {
        "week": 2,
        "rag": "Red",
        "customer_action": "The review is still limited to one lot.",
        "overall": {
            "rate_pct": 3.67,
            "k": 529,
            "n": 14400,
            "ci_low_pct": 3.38,
            "ci_high_pct": 3.99,
            "promised_pct": 98.0,
            "spec_pct": 2.0,
        },
        "hypothesis": {
            "category": "Material",
            "cause": "bad_reagent_lot",
            "level": "L-4419",
        },
    }
    text = status_customer(facts)
    assert "3.67" in text
    assert "does not state a confirmed cause" in text
    assert "L-4419" not in text
    assert "bad_reagent_lot" not in text
```

Run `pytest tests/test_status.py`.

**Extra credit.** What does `rag_color(True, 2)` return, and what does `rag_color(True, 3)` return? Why is the second one not Green?
""",
    },
    {
        "id": 7,
        "week": 3,
        "title": "A Streamlit dashboard, rules-only by default",
        "minutes": "70–90",
        "ticket": "INV-301",
        "artifact": "Clickable week stepper: rate, p-chart, Pareto, projection",
        "blurb": "A reviewer can move the week without a model download. Community Cloud stays deterministic. A local toggle, with LLM_MODEL unset, asks Ollama for Llama 3.2 1B.",
        "read": [
            "`.streamlit/config.toml` for the navy theme and the telemetry switch.",
            "`requirements.txt` — notice it does not install a weight file.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-7 session-7
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

`_dashboard_model` is the only place the page chooses a model name. Add this to `tests/test_dashboard.py`:

```python
def test_toggle_asks_for_llama_32_only_when_rules_only_is_off(monkeypatch):
    import importlib.util

    monkeypatch.delenv("LLM_MODEL", raising=False)
    path = ROOT / "app" / "streamlit_app.py"
    spec = importlib.util.spec_from_file_location("dash_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module._dashboard_model(True) == "llama3.1:8b"
    assert module._dashboard_model(False) == "llama3.2:1b"
    monkeypatch.setenv("LLM_MODEL", "phi4")
    assert module._dashboard_model(False) == "phi4"
```

`ROOT` is already defined in that file. Run `pytest tests/test_dashboard.py`.

**Extra credit.** Why does the hosted page still not call Llama 3.2 1B even though that tag is what the toggle asks for locally?
""",
    },
    {
        "id": 8,
        "week": 3,
        "title": "An offline scorecard",
        "minutes": "70–90",
        "ticket": "INV-302",
        "artifact": "Eval report: evidence ranker versus a note-only ranker",
        "blurb": "Twenty-two seeded scenarios. 22/22 is the designed call on this constructed set. It is not a clinical accuracy number, and it is not Llama versus Llama.",
        "read": [
            "The report under `evals/reports/` on this tag. Read the weak_lot row and the drift extra stratum before the 22/22 cell.",
            "`scenarios/herring_software.yaml` — the note says software. The true cause is the lot.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-8 session-8
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

An unquoted `true` in YAML 1.1 becomes a boolean, and the generator would miss the real cause. Lock the quotes. Add to `tests/test_eval.py`:

```python
def test_herring_true_key_is_a_string_not_a_boolean():
    import yaml

    raw = (ROOT / "scenarios" / "herring_software.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    assert "true" in data["root_cause"]
    assert isinstance(data["root_cause"]["true"], dict)
    assert data["root_cause"]["true"]["type"] == "bad_reagent_lot"
    bare = yaml.safe_load("root_cause:\\n  true:\\n    type: bad_reagent_lot\\n")
    assert True in bare["root_cause"]
    assert "true" not in bare["root_cause"]
```

If `ROOT` is not in that file, define it as `Path(__file__).resolve().parents[1]`. Run `pytest tests/test_eval.py`.

**Extra credit.** In one sentence, why is weak_lot a success when the evidence call is `no_single_cause`?
""",
    },
    {
        "id": 9,
        "week": 3,
        "title": "Week-4 close-out, the exec deck, and the résumé",
        "minutes": "70–90",
        "ticket": "INV-303",
        "artifact": "Seven-slide deck, close-out note, résumé bullets with the misses kept",
        "blurb": "D7 and D8 are confirmed. The deck's cost is k times the unit price. The projection stays labeled as a projection. The 22/22 cell keeps its failure notes.",
        "read": [
            "README.md on this tag — the model table and the eval table.",
            "RESUME_BULLETS.md — read the drift bullet before you reuse the 22/22 line.",
        ],
        "practice": """```bash
git fetch --tags
git switch -c practice/session-9 session-9
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/test_closeout.py
```

A no-single-cause call must not tell leadership to contain a stratum. Add this to `tests/test_closeout.py`:

```python
def test_unresolved_deck_does_not_contain_a_stratum(tmp_path):
    from invalid_agent.artifacts.deck import write_deck

    facts = {
        "scenario_id": "flat_high",
        "device": "MDx-24 Respiratory Panel",
        "rate_pct": 2.4,
        "k": 100,
        "n": 4000,
        "ci_low_pct": 2.1,
        "ci_high_pct": 2.8,
        "spec_pct": 2.0,
        "promised_pct": 98.0,
        "cause": "no_single_cause",
        "level": "no single stratum",
        "category": "Unresolved",
        "recommendation": "Do not quarantine.",
        "unit": 85,
        "cost": 8500,
        "after_pct": 2.4,
        "label": "Not observed follow-up.",
        "single": False,
        "d7": "D7 stays a prevention plan, not a claim that the rate recovered.",
    }
    path = tmp_path / "exec_deck.pptx"
    write_deck(path, facts)
    presentation = Presentation(str(path))
    assert len(presentation.slides) == 7
    chunks = []
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                chunks.append(shape.text_frame.text)
    text = "\\n".join(chunks)
    assert "Do not contain a stratum" in text
    assert "Not observed follow-up" in text
    assert "Contain no single stratum" not in text
```

`Presentation` is already imported in that test file. Run `pytest tests/test_closeout.py`.

**Extra credit.** Say the two-minute pitch out loud. Keep the keyword 3/22 and the four drift files in the same breath as 22/22.
""",
    },
]
