# invalid-agent

Field-quality investigation for a program manager's portfolio. The promise is still validity of at least 98%, so the invalid rate must stay at or below 2% (`SPEC_INVALID_RATE` in `config.py`). Invalid Bot runs the weekly loop: triage, plan, root-cause analysis, status, through weeks 0–4. Week 4 writes a fishbone, 5 Whys, an 8D/CAPA record, and a seven-slide exec deck.

The public demo reads a hosted Postgres table of openFDA device-event (MAUDE) reports for two IVD product codes. Synthetic scenarios remain the CI fallback. They are not the public demo.

**Not for clinical use. Not a medical device.** MAUDE is unvalidated public data. The 2% cap is the stated run-level promise and is **not estimable** from MAUDE.

The language model does not calculate. Rates, Wilson intervals, control limits, hypothesis scores, costs, and the projection are Python. For questions over the table, the model may only choose a vetted read-only SQL template. Python executes it and computes. The model narrates. A numeric-fidelity check rejects a draft that introduces a number the facts do not contain, and the template replaces that draft.

## Denominator

openFDA device events are reports of problems. There is no count of successful runs. Each stored row is one report.

- **Numerator:** the report's `product_problems` include at least one label in `INVALID_LABELS` (`src/invalid_agent/data/mapping.py`).
- **Denominator:** every extracted report in the same product-code window, including reports that are only wrong-result labels.
- **Figure:** invalid-type share of reported events. Outputs say this in words. `exceeds_spec` stays false on these cases, because a share above 2% is not a broken clinical invalid rate.
- **Escalate** when a stratum clears the existing evidence bar (minimum n, lift, excess invalids, chi-square), not when the share exceeds 2%.

Wrong-result labels stay in the denominator and out of the numerator. That includes false positive, false negative, high test results, low test results, incorrect measurement, non-reproducible results, and "Output Problem" (FDA uses that term for any output deviation).

## Product codes and invalid types

Counted from public openFDA `count=` queries on 2026-11-18. Those calls chose the windows. They are not the row extract.

| Case | Code | Window | What the counts showed |
|---|---|---|---|
| `openfda_ooi` | OOI | 2022-01-01 to 2024-12-31 | About 1,422 reports. Multiplex / nucleic-acid amplification. Dominant labels were false positive and false negative, which are not invalids. |
| `openfda_jje` | JJE | 2024-01-01 to 2024-12-31 | 4,221 reports. Clinical chemistry analyzers. Dominant labels were high and low test results, which are not invalids. |

Invalid types, in priority order when one report has several:

| Code | Meaning | Example labels |
|---|---|---|
| INV-NOR | No usable result | Unable to Obtain Readings, Failure to Run, No Device Output |
| INV-SW | Software abort | Computer Software Problem, Application Program Problem |
| INV-CAL | Calibration | Calibration Problem, Failure to Calibrate |
| INV-MECH | Mechanical | Mechanical Problem |
| INV-USR | Use | Improper or Incorrect Procedure or Method, Human-Device Interface Problem |

A gitignored `.env.local` overrides `.env` for CLI and Streamlit commands. `neon deploy` writes that file. The process environment still wins. Pytest does not read either file.

Manufacturer names come straight from the public openFDA records. They are uppercased, parenthetical cities are dropped, and legal suffixes (`INC`, `LLC`, `CO`) are removed so punctuation does not split one firm. The public page shows those names. Set `MANUFACTURER_DISPLAY=anonymized` to print Manufacturer A/B/C instead. Blank lot, brand, and operator values are `UNREPORTED` and the ranker ignores that level.

## Call budget

Page size is 1,000, the openFDA maximum. Planning totals imply about 2 pages for OOI and 5 for JJE, about 7 calls. `MAX_API_CALLS` is 40. The run stops at the cap instead of paging into the thousands. Pages use `skip`, and a `Link` header with `search_after` is followed when openFDA sends one. Skip above 25,000 aborts with a message to narrow the window.

Each call is printed as `openFDA call N/40` without the key. The cache is `data/cache/openfda/` (gitignored). A complete cache makes the next run, the tests, and the dashboard use zero API calls. `--refresh` is the only flag that calls again. Narratives, patient blocks, and street addresses are dropped before the cache is written.

## Architecture

```mermaid
flowchart LR
  api[openFDA device event] --> cache[On-disk cache]
  cache --> pg[Neon Postgres]
  pg --> frame[Report frame]
  yaml[Synthetic YAML] --> gen[Seeded generator]
  gen --> frame
  frame --> metrics[Rates, SPC, Pareto]
  metrics --> rank[Evidence ranker]
  rank --> graph[LangGraph]
  graph --> notes[Memos, CAPA, deck]
  notes --> guard[Numeric-fidelity check]
  ask[Question] --> sql[Vetted SQL template]
  sql --> pg
  pg --> metrics
```

The graph is triage once, then plan, RCA, and status, repeating until the requested week. Week 4 adds close-out. The dataframe is not stored on the graph state. Synthetic nodes rebuild it from the scenario seed. MAUDE nodes read the hosted table. CI does not need a network, a key, or a database.

## Quickstart for CI

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m invalid_agent.graph --scenario bad_lot --week 4
```

Week 4 writes `out/exec_deck.pptx` and `out/closeout.md`. With no secrets, `streamlit run streamlit_app.py` is the CI fallback and says so on the banner. The public demo is the hosted app after the owner checklist below.

```bash
python evals/run_eval.py --backend deterministic
```

That command rewrites `evals/reports/<date>.md`. CI runs the same script with `--limit 5 --smoke`.

## Models

`LLM_BACKEND` selects the narrator. `LLM_MODEL` is the local Ollama tag. `GROQ_MODEL` is the hosted tag.

| Where | Backend | Model | Notes |
|---|---|---|---|
| Public Streamlit | `groq` | `openai/gpt-oss-20b` | Free Groq tier, no credit card. Llama 3.1 8B Instant left that free tier on 2026-08-16. |
| Laptop | `ollama` | `llama3.1:8b` | `ollama pull llama3.1:8b`, then `LLM_BACKEND=ollama`. |
| Smaller laptop tag | `ollama` | `llama3.2:1b` | `LLM_MODEL=llama3.2:1b`. |
| CI | `deterministic` | none | Templates only. No socket. |

`gemma3` and `phi4` are the other documented Ollama tags. `LLAMACPP_MODEL_PATH` is an optional local GGUF, not the public path.

## Host

**Neon** (https://neon.tech) is the database. The free plan is Postgres with a connection string and SSL, which is the whole integration. Railway's standing free plan is gone, so it is not a zero-spend host. Supabase's free Postgres also works if the URL is a normal Postgres connection string with `sslmode=require`; the loader does not use any Supabase API.

The loader creates a login role `invalid_demo_ro` with `default_transaction_read_only=on` and `SELECT` on the three tables. The public app must use that URL (`DATABASE_URL_READONLY`). The admin URL is only for the load.

The public narrator is **Groq's free tier** (https://console.groq.com). The local narrator is Ollama. Jira is **Jira Cloud Free** with a team-managed project so the issue types Epic and Task exist by name. The dashboard is **Streamlit Community Cloud**.

## Owner checklist

Do these in order. The agent cannot create the accounts. Nothing below is a paid tier.

1. **openFDA key (blocks the extract).** Create a free key at https://open.fda.gov/apis/authentication/. Export `OPENFDA_API_KEY`. Do not put this key in Streamlit secrets. The public app does not call openFDA.
2. **Neon.** Sign up at https://neon.tech on the free plan (no credit card for the free plan). Create a project. Copy the connection string, including `sslmode=require`, into `DATABASE_URL`.
3. **Read-only password.** Generate a long random value and export `DEMO_READONLY_PASSWORD`. At least 32 characters:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
4. **Load, one command.** From the repo, with those three variables set:

   ```bash
   python -m pip install -e ".[dev]"
   python -m invalid_agent.data.pipeline
   ```

   The first run calls openFDA (about 7 calls, cap 40), writes `data/cache/openfda/`, loads Postgres, creates `invalid_demo_ro`, and prints `DATABASE_URL_READONLY=...`. A second run uses the cache and makes zero API calls. `python -m invalid_agent.data.doctor` prints which variables are still empty and does not call openFDA.
5. **Groq.** Create a free key at https://console.groq.com/keys (free plan, no credit card). That value is `GROQ_API_KEY`. Leave `GROQ_MODEL=openai/gpt-oss-20b` unless Groq renames the free production model.
6. **Jira Cloud Free.** Create a site at https://www.atlassian.com/software/jira/free. Make a **team-managed** software project with key `INV`. Create an API token at https://id.atlassian.com/manage-profile/security/api-tokens. Set `JIRA_BASE_URL` (https://&lt;site&gt;.atlassian.net), `JIRA_EMAIL`, and `JIRA_API_TOKEN`. Check with `python -m invalid_agent.integrations.jira`. It must report Epic and Task. Seed once, from your machine, after the credentials are set:

   ```bash
   python -m invalid_agent.integrations.jira seed
   ```

   That command searches first and creates issues only when the case label is absent. A second run does not post. Issues are labeled `openfda` or `simulation`. The public page only reads and links those issues. A visitor cannot create one. Invite the reader to the free site (the free plan is not a public anonymous board).
7. **Streamlit Community Cloud.** Sign in at https://share.streamlit.io with GitHub. Deploy this repo. Main file: `streamlit_app.py`. Paste `.streamlit/secrets.toml.example` into the secrets editor with the real values: `DATA_BACKEND=openfda`, `LLM_BACKEND=groq`, `GROQ_API_KEY`, `GROQ_MODEL`, `DATABASE_URL_READONLY`, and the three Jira secrets. Do not paste `OPENFDA_API_KEY` or the admin `DATABASE_URL`. Leave `MANUFACTURER_DISPLAY=real` so the page shows the firm names from the public reports. Set it to `anonymized` only to print Manufacturer A/B/C.
8. **Confirm.** Open the public URL. The banner must say the rows are MAUDE reports and that the 2% cap is not estimable. Run `openfda_ooi` and `openfda_jje` to week 4. Ask the four suggested questions. The Jira section should show live keys.

Local Ollama, after `ollama pull llama3.1:8b`:

```bash
LLM_BACKEND=ollama python -m invalid_agent.graph --scenario bad_lot --week 0
```

MAUDE cases, after step 4, from a laptop that has `DATABASE_URL` or `DATABASE_URL_READONLY`:

```bash
python -m invalid_agent.graph --scenario openfda_ooi --week 4
python -m invalid_agent.graph --scenario openfda_jje --week 4
```

## Limits

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

## Limits

- Synthetic scenarios (`scenarios/*.yaml`) are the CI fallback. The public cases (`cases/openfda_ooi.yaml`, `cases/openfda_jje.yaml`) read hosted MAUDE rows and do not fall back to synthetic rows when the database is missing.
- The MAUDE share is not a clinical invalid rate. The 2% cap stays visible and is labeled not estimable.
- The projection clears the leading stratum on the same file. It is not observed follow-up. `bad_lot` never turns Green, because the file is not rewritten.
- Laptop snapshot folders under `C:\Users\neels\Grok_Bot\Project_Agent\` are not created here. Annotated tags `session-1` through `session-9` are the snapshots. Check out the tag and copy the tree.
- Narrated MP4s are the academy on GitHub Pages, not files in `main`. Each session is two short clips pinned at tag `academy-v2` (`d057d3e`), not a line-by-line reading of every file. `academy/narration/` is that script. The logic traces under `docs/sessions/` remain the build diary.
- No agent swarm, no extra integrations, no fine-tune.

## Layout

Session notes: `docs/sessions/session-N/LOGIC_TRACE.md` and `QUIZ.md`. Résumé lines copied from the eval report: `RESUME_BULLETS.md`. Product framing: `PRD.md`. Disclaimer: `SIMULATION_DISCLAIMER.md`.

## Academy

`academy/` is the static course: two short clips a session, an architecture note, a session summary, and an 8-question quiz on the boundaries. The clips and the line links are pinned at tag `academy-v2` (`d057d3e`) so a later edit to main cannot move them. Pass at 80% to open the next session. Videos are published on the `gh-pages` branch so a clone of `main` stays light. See `academy/README.md`.
