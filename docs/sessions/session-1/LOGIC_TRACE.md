# Session 1 logic trace

Snapshot id: git tag `session-1`. Resolve the commit with `git rev-parse session-1`.

The plan also asks for a full tree at `C:\Users\neels\Grok_Bot\Project_Agent\Session 1\`. This session was built in a cloud workspace that does not have that Windows path. The tag is the snapshot. To make the laptop folder, check out `session-1` and copy the tree, excluding `.git/`, any venv, and `.env`.

## 1. Goal

Ship the framing for Invalid Bot: a PRD, a simulation disclaimer, a data-license note, an importable Jira backlog (3 sprints, 7 epics, Sprint 1 holding at least 8 stories), a config object that refuses to print secrets, and a GitHub Actions workflow that runs pytest with no network and no keys.

## 2. What had to be true before Session 2

Session 2 needs a package layout, a place to read the spec (validity ≥ 98%, invalid rate ≤ 2%), and a CI job that goes red if the Wilson interval test is wrong. It does not need a model, Jira, or Streamlit.

## 3. Why these libraries

Session 1 uses the standard library plus pytest.

- **pytest** runs the config tests locally and in CI. It is the smallest check that the skeleton installs.
- **setuptools** (via `pyproject.toml`) makes `pip install -e .` put `invalid_agent` on the path. Later sessions add pandas, scipy, LangGraph, plotly, python-pptx, and Streamlit to that same file. They are not dependencies yet because nothing imports them yet.
- No LangGraph, Ollama, or Jira client this session. Adding them now would make CI download stacks the tests do not exercise.

## 4. Code, and why it is shaped this way

`src/invalid_agent/config.py` is the only runtime module.

- Lines 14–15 lock the spec: `PROMISED_VALIDITY = 0.98`, and `SPEC_INVALID_RATE` is `1 - 0.98` rounded to 2 decimal places so the spec is 0.02 rather than 0.020000000000000018.
- Lines 20–29, `find_repo_root`, walk the working directory and then the file's parents until it sees `pyproject.toml` next to either `scenarios/` or `src/invalid_agent/`. Later sessions resolve scenario paths from `settings.repo_root`, which stays correct when Streamlit's working directory is the repo and also when the package is imported from an editable install.
- Lines 36–50, `Settings`, is a frozen dataclass. Jira and openFDA fields are plain strings, empty when unset.
- Lines 52–55, `jira_enabled`, is the single switch the Session 5 client will use. It is true only when base URL, email, and token are all non-empty. Two out of three stays offline. That is what "optional integration" means.
- Lines 61–78, `redacted`, and lines 80–87, `__repr__`, rebuild a display string from the masked view. The dataclass is frozen, so the generated repr would have included the token. Overriding `__repr__` is the fix. `test_jira_requires_all_three_values` sets the token to `super-secret-token` and asserts that string is absent from `repr(settings)`.
- Lines 90–119, `load_settings`, read the environment. `JIRA_BASE_URL` wins over `JIRA_URL`, and `JIRA_API_TOKEN` wins over `JIRA_TOKEN`, so the plan's names and the runbook's names both work. An unknown `LLM_BACKEND` becomes `deterministic` (lines 100–101) rather than raising, because a hosted demo with a typo should fall back to rules, not crash.

`tests/test_config.py` covers defaults, the three-part Jira gate, both aliases, alias precedence, and the backend fallback.

`docs/jira/backlog.json` is the board. Sprint 1 contains INV-101 through INV-109 (nine stories). Epics are Triage, RCA, Planning, Comms, Dashboard, Deck, Evals. A live Jira site is not created here; Neel imports this file when he has a Free site. The mock client in Session 5 is a different backlog: it creates the *investigation* epic from a scenario plan. This file is the *build* backlog.

## 5. What was documented, and why

- `PRD.md` is the session deliverable a PM reviewer reads first: problem, users, stories, success metrics, non-goals, risks.
- `SIMULATION_DISCLAIMER.md` is the sentence that has to be true on the memo, the app, and the deck later. Writing it now keeps those sessions from softening it.
- `DATA_LICENSES.md` records that MAUDE, the Mendeley HIL set (DOI 10.17632/vxkkdmw55f.1), and Zenodo CBC 15674541 are sources we cite and do not redistribute.
- `.env.example` lists every variable, with empty secrets, so the absence of a credential is visible.
- `.github/workflows/ci.yml` runs Python 3.11 and 3.12. The plan names 3.11; 3.12 is the laptop interpreter this workspace has, so both are gated.

## 6. Stakeholder / Jira buy-in before Session 2

Ticket **INV-104** (synthetic generator) is the next story, epic **INV-1**. Neel does not need a Jira token for it. He does need to accept the spec in the PRD: validity ≥ 98%, fictional molecular panel, not a chemistry analyzer. That choice is locked in `config.py` lines 14–15 so Session 2 does not reopen it.

## 7. Approval → capability added

Config loads offline, pytest covers it, and CI is wired. That is the gate Session 2 builds on: a package with a spec constant and a test runner.

## 8. What a hiring manager can see

A PRD with non-goals, a backlog split into three sprints, and a config that treats a token as a secret. The agile artifact is the backlog file, not a screenshot of a tool the reviewer cannot log into.

## Line-by-line walkthrough (for a narrated review of this tag)

Check out `session-1` before following line numbers.

1. Open `src/invalid_agent/config.py`.
2. Line 13 states the product rule in a comment. Lines 14–15 turn it into the two constants every later metric compares against.
3. Line 17 is the allow-list of backends. `load_settings` (line 100) refuses anything else.
4. `find_repo_root` (lines 20–29) is boring on purpose. Line 23 prefers the current working directory, then parents of this file. Line 25 matches a checkout that already has `scenarios/`. Line 27 matches this session, which does not have that folder yet. Line 29 is the last resort.
5. `_env` (lines 32–33) strips whitespace so a token of `"  "` does not count as configured.
6. Walk `jira_enabled` (lines 52–55) with an example: URL set, email set, token empty → `bool("https://…" and "pm@…" and "")` is false.
7. Walk `redacted` (lines 70 and 74): the raw token is replaced with `***` only when it is non-empty, so a log can still show "no token configured".
8. Walk `__repr__` (lines 80–87): it calls `redacted()` first, then formats three fields. It never reads `self.jira_api_token`.
9. Walk `load_settings` (lines 97–118) in order: normalize the backend, resolve the repo root, resolve the output directory (default `<root>/out`, override `INVALID_AGENT_OUT`), then fill the dataclass. Line 110 is the alias precedence. Line 105 calls `.rstrip("/")` so a trailing slash cannot create two different site identities later.
10. Open `tests/test_config.py` and read `test_jira_requires_all_three_values`: it proves the gate and the repr rule with a planted secret.
11. Open `docs/jira/backlog.json` and count stories with `"sprint": 1`. There are nine. The plan's demo bar is eight.

## Quiz

1. Why is the invalid-rate spec 0.02 and not a second independent constant someone could edit alone?
2. Which three environment variables must all be set before `jira_enabled` is true?
3. Why does `__repr__` not use the dataclass default?
4. What is the difference between `docs/jira/backlog.json` and the Jira sync that Session 5 will add?
5. Name two things the PRD puts out of scope, and the JD reason.

Answers are at the bottom of `QUIZ.md` in this folder. Try them before reading it.
