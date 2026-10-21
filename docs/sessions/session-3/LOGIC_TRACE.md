# Session 3 logic trace

Snapshot id: git tag `session-3`. Resolve the commit with `git rev-parse session-3^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 3\`. This workspace has no Windows path, so the tag is the snapshot.

## 1. Goal

A one-page Week-0 triage memo for `bad_lot`. It states the invalid rate, the Wilson interval, the spec (validity ≥ 98%), the strata, the severity, an escalate decision, and the initial hypothesis. The language model does not calculate. A guard rejects a narrative number that is not in the computed facts. The demo command is `python -m invalid_agent.graph --scenario bad_lot --week 0`, which writes `out/week0_triage.md`.

## 2. What had to be true before Session 4

Session 4's fishbone needs the ranked hypothesis list, the evidence-id catalog, and a graph it can add nodes to. Those three now exist on the case state. The fishbone itself is not in this session. `--week` other than 0 exits on purpose (`graph.py` lines 52–55) so this tag cannot pretend the weekly loop already runs.

## 3. Why these libraries

- **LangGraph** is the case graph. Session 3 has one node, `triage`, with an edge to END. Later sessions add nodes to the same `StateGraph` instead of starting a second framework.
- **langchain-core** supplies `SystemMessage` and `HumanMessage` in `llm.py` `_chat_payload` (line 30). Ollama and llama.cpp both receive the same role/content pairs. We do not take LangChain's Ollama integration, because one `httpx` call is easier to mock and does not pull a model client into CI.
- **Pydantic** is the memo contract (`TriageMemo`). Tests assert fields. They do not scrape the markdown for "Escalate".
- **httpx** is the Ollama transport. It is not called when `LLM_BACKEND` is `deterministic`, which is the default.
- **llama-cpp-python** is not a dependency. `LlamaCppLLM` imports it only if that backend is selected, and a missing install becomes a recorded fallback to the template.

## 4. Code, and why it is shaped this way

`metrics/hypotheses.py` ranks causes from the Session 2 frame.

- Constants at lines 45–51 are the evidence bar: at least 80 runs, lift at least 1.8, at least 15 excess invalids, chi-square p < 0.01. Two causes within 80% of each other's score become `no_single_cause` instead of a coin flip.
- `_COLUMN_CAUSE` (lines 36–43) maps a column to a cause and, via `CAUSE_CATEGORY`, to a 6M bucket. Temperature and hemolysis are bands (`with_bands`, line 54), not raw continuous columns, so one hot shipment does not look like a site effect and one high index does not look like "the site" alone.
- `_best_level` (line 64) scores each level against its complement. A level that fails a gate is dropped, not given a small score. That is why the bad-lot memo lists one hypothesis: L-4419 clears the bar and the instruments, at roughly 4%, do not.
- `rank_hypotheses` (line 117) never reads `injections`. A QA sentence cannot outrank the table.
- `evidence_catalog` (line 167) is the dictionary Session 4 citations have to use. An id that is not a key is not a citation.

`guards/numeric_fidelity.py`

- `check_narrative` (line 74) strips ISO dates, then replaces any fact string of length ≥ 2 (so `L-4419` and `2.4.0` disappear), then scans for numbers.
- A remaining number must sit within `_atol` (line 66) of some number walked out of the facts. Proportions in (0, 1] also contribute their percent form (`_walk_numbers`), which is why 3.67 is allowed when the stored rate is 0.0367 and `rate_pct` is 3.67.
- Identifiers are removed rather than added to the allow-list. `4419` does not become a permitted rate.

`narrative.py` `triage_memo` (line 39) interpolates `facts` only. The complaint text is copied from the YAML. The hypothesis sentence is built in `nodes/triage.py` `_hypothesis_facts` from the same rounded fields the guard will see.

`llm.py` `narrate` (line 107) is the policy:

1. Always render the template first (`safe`).
2. If the backend is deterministic, return that text after checking it. If the template itself fails, `ok` is false and `triage_node` raises in `check_stored`. A broken template is a bug, not a fallback.
3. Otherwise call the model. On exception, empty text, or a failed check, return `safe` and set `rewritten: true`. The rejected draft is not written to the memo.

`nodes/triage.py` `triage_node` (line 156) regenerates the frame from the scenario seed. The rows are not stored on the graph state. It then builds facts, narrates, validates a `TriageMemo`, and refuses to store prose that fails the guard (`check_stored`, line 205).

`graph.py` `build_graph` (lines 18–23) compiles the one-node graph. `run_case` writes `week0_triage.md` and `week0_fidelity.json`.

On seed 4419 the memo reports 3.67% (529 of 14400), CI 3.38–3.99%, escalate, severity high, and Material / bad_reagent_lot / L-4419 at 17.10% versus a 1.09% complement. Those are outputs of this tag's command, not constants in the template.

## 5. What was documented, and why

The memo carries the simulation banner in the template, not as an afterthought in the CLI print. The fidelity JSON is written beside the memo so a reviewer can see `backend: deterministic` without reading the code. The README at this tag shows the week-0 command.

## 6. Stakeholder / Jira buy-in before Session 4

Ticket **INV-201**, epic **INV-2**: fishbone with evidence for and against. The evidence ids from `evidence_catalog` are the buy-in. If a 5 Whys step cannot cite one, it does not ship. No Jira token.

## 7. Approval → capability added

`pytest` covers a planted 27.40% rate, a lying draft that gets replaced, a flat table that stays `no_single_cause`, and the week-0 command. The memo file is the demo.

## 8. What a hiring manager can see

A customer escalation turned into a one-page position: the rate versus the promise, where it concentrates, and a hypothesis that cites the lot. The escalate decision is a comparison in code (`exceeds_spec`), which is the data-driven piece. The model is optional and, by default, absent.

## Line-by-line walkthrough

Check out `session-3` first.

1. Start at `graph.py` `main` (line 73). `--scenario bad_lot` is resolved by `resolve_scenario` (line 26): a bare id gets `scenarios/<id>.yaml`.
2. `run_case` (line 51) rejects any week other than 0. It loads settings, loads YAML, builds the graph, and calls `invoke` on `initial_state` (line 39). The state holds the scenario dict and empty lists for the later artifacts. It does not hold a dataframe.
3. `build_graph` (line 18) registers one node. LangGraph will call `triage_node` with that state and merge the returned dict.
4. Open `nodes/triage.py` `triage_node` (line 156). First line that matters: `df = generate(scenario)`. Same seed as Session 2, same 14,400 rows.
5. `rank_hypotheses` in `hypotheses.py` (line 117) copies the frame, adds `temp_band` and `hil_band`, and calls `_best_level` for each column in `_COLUMN_CAUSE`.
6. Inside `_best_level` (line 64), follow one lot. n and complement n must both be ≥ 80 (line 45). The 2×2 table is `[k, n-k]` against the complement. Lift is rate / complement rate. Excess is `k - complement_rate * n`. All three gates must pass or the level is `continue`d away. The winning level is the max score, not the max rate.
7. Back in `rank_hypotheses`, a single winner is returned as a one-element list. Two close winners would be prefixed with `no_single_cause` (`CLOSE_CALL_RATIO`, line 49). An empty list becomes `_unresolved`.
8. `build_facts` (triage.py line 79) rounds percents with `_pct` (line 17) *before* the template sees them, so the characters `3.67` in the file are the same float the guard walks.
9. `narrate` (llm.py line 107). With the default backend, line 117 is true. Line 116 has already rendered the template. Line 118 checks it. Line 119 appends the source footer, which contains no digits.
10. Open `numeric_fidelity.py` `check_narrative` (line 74) against the sentence "the rate is 27.40%". `27.40` is not an identifier in the facts, so it survives masking (lines 79–80). It is not within 0.03 of 3.67 or 2.00 or any other fact (lines 83–87). `unknown` is non-empty, `ok` is false.
11. The same function on the template returns ok, because every digit cluster is either inside a fact string (`L-4419`, `INV-IC`, `2.4.0`) or near a walked number (`529`, `14400`, `17.10`, `1.09`, `15.64`, `23`, `78`, `95`, `98.00`, `2.00`).
12. `check_stored` (triage.py line 205) runs the guard again on the exact string about to be saved and raises if it fails. The schema object is then stored via `model_dump()`.
13. `run_case` writes the markdown and the fidelity JSON. The CLI prints escalate and severity from the schema, not from a regex on the prose.

## Quiz

See `QUIZ.md`.
