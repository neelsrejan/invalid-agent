# PRD: Invalid Bot

**Product:** Invalid Bot (`invalid-agent`)
**Owner:** Neel Srejan
**Status:** Portfolio simulation, not a medical device and not for clinical use
**Spec locked for the simulation:** promised validity **≥ 98%** (invalid rate **≤ 2%**)
**Assay flavor:** a fictional multiplex **molecular diagnostic panel** ("MDx-24 Respiratory Panel"). It is not a real product and it is not GenMark, Roche, or any other manufacturer's assay.

## 1. Problem

A simulated customer reports that the field invalid rate on MDx-24 is above the validity rate they were promised. Example shape of the complaint: about 4% invalids against a ≤ 2% invalid spec. A field-quality / program manager has to, in one week-by-week loop:

1. Measure the rate against the spec, with an interval and a breakdown.
2. Decide whether to escalate.
3. Plan the investigation (owners, dates, dependencies) and name the risks.
4. Re-plan when QA, R&D, manufacturing, the customer, or leadership adds information.
5. Close with a root cause (or an honest "no single cause"), an 8D/CAPA record, and a recommendation leadership can act on.

The work products are the ones a hiring manager already recognizes: a triage memo, a Gantt, a risk register, Jira issues, a RAG status note per audience, a CAPA record, a control chart, and an executive deck.

## 2. Users

| User | What they need from the agent |
|---|---|
| Field-quality PM / program manager (primary) | A weekly loop that drafts the artifacts above from computed numbers |
| QA, R&D, Manufacturing | A shared evidence table, not a prose guess |
| Customer / lab director | A customer-safe update that does not speculate past the evidence |
| Leadership | Cost, risk, options, and a specific ask |
| Recruiter or hiring manager (portfolio reader) | A repo they can run with no API key and a README that says what is simulated |

The agent is the PM's tool. It does not replace the PM's judgment, and the portfolio story is that Neel can explain every number it prints.

## 3. Job to be done

When a validity complaint arrives, produce a defensible Week-0 position the same day, then carry that case through four investigation weeks until there is a recommendation. Every number in those artifacts must match the calculation. Narrative that invents a rate is rejected.

## 4. Scope of v1

In scope:

- One LangGraph case graph with typed state.
- A synthetic 6-month field dataset per scenario, with a known injected root cause.
- Metrics: invalid rate, Wilson score interval, stratified rates, chi-square, p-chart with Western Electric rules, Pareto of invalid codes.
- Week-0 triage memo.
- Fishbone (6M) → 5 Whys → 8D/CAPA, with DMAIC labels.
- Four-week plan, Gantt, likelihood × impact risk register, decision log.
- Stakeholder injections and a RAG status update for customer, internal, and leadership audiences.
- Optional Jira Cloud Free sync, with a mock mode that writes JSON when no token is set.
- Streamlit dashboard and a python-pptx executive deck.
- An offline eval harness over 15–30 seeded scenarios.

Out of scope (deliberate):

- Multi-agent crews, fine-tuning, and a vector database added only so the repo can say "RAG".
- Slack, Notion, Asana, Salesforce, or any second integration.
- Real customer data, real complaints, or any proprietary SOP.
- Clinical decision support. The banner on the app, the memo, the deck, and this PRD all say not for clinical use.
- Hosting that costs money. Streamlit Community Cloud and a local Ollama install are the two runtimes.

## 5. User stories

Sprint placement matches the build (Sprint 1 = sessions 1–3, Sprint 2 = sessions 4–6, Sprint 3 = sessions 7–9). The importable backlog is `docs/jira/backlog.json`.

### Sprint 1 — Framing, data, Week-0 triage

1. As a field-quality PM, I want a written PRD so scope, non-goals, and success metrics are agreed before build.
2. As a field-quality PM, I want the repo to install and test with no API keys so a reviewer can run it.
3. As a field-quality PM, I want the simulation labeled on every artifact so nobody can mistake it for a field complaint.
4. As a field-quality PM, I want a 6-month synthetic run file with sites, instruments, lots, software versions, and invalid codes so the investigation has something to stratify.
5. As a field-quality PM, I want the invalid rate, a Wilson 95% interval, and a spec comparison computed in code.
6. As a field-quality PM, I want stratified rates and a chi-square test so I can see which lot, site, or instrument moved.
7. As a field-quality PM, I want a p-chart and Western Electric flags so I can say whether the process left control.
8. As a field-quality PM, I want a Pareto of invalid codes so containment targets the dominant failure mode.
9. As a field-quality PM, I want a one-page Week-0 memo that states the rate, the interval, the affected strata, the severity, and whether to escalate.
10. As a field-quality PM, I want any narrative number that is not in the computed set rejected.

### Sprint 2 — RCA, plan, weekly loop

11. As a field-quality PM, I want a fishbone whose branches cite evidence for and against, ranked from the data.
12. As a field-quality PM, I want a 5 Whys on the top branch where each step cites a data fact or a stakeholder injection.
13. As a field-quality PM, I want an 8D/CAPA record (D1–D8) labeled with DMAIC so the file matches a quality-system read.
14. As a field-quality PM, I want a 4-week plan with functional owners, dependencies, and dates, drawn as a Gantt.
15. As a field-quality PM, I want a likelihood × impact risk register with an owner, a mitigation, and a trend.
16. As a field-quality PM, I want the plan pushed to Jira as an epic and stories, and I want a JSON dry-run when I have no site.
17. As a field-quality PM, I want each new stakeholder message to force a re-plan and a decision-log entry.
18. As a field-quality PM, I want a RAG status update written separately for the customer, the internal team, and leadership.

### Sprint 3 — Dashboard, evals, close-out

19. As a reviewer, I want a Streamlit dashboard with the rate, the p-chart, the Pareto, the strata, and the week's artifacts.
20. As a reviewer, I want a rules-only mode that answers with no model download.
21. As a field-quality PM, I want 15–30 seeded scenarios scored for root-cause hit rate, numeric fidelity, and citation validity.
22. As a field-quality PM, I want Week 4 to close with a confidence-qualified cause, an effectiveness check, and an executive deck.

## 6. Success metrics

| Metric | Target | How it is measured |
|---|---|---|
| Numeric fidelity | 100% of narrative numbers match a computed value | `guards/numeric_fidelity.py`, eval report |
| Week-0 escalation | Escalate if and only if the rate is above spec (interval reported either way) | Eval column `escalation_correct` |
| Root-cause top-1 / top-3 | Reported with n, the scenario list, and the failures. No accuracy slogan. | `evals/run_eval.py` |
| Citation validity | Every 5 Whys step cites an evidence id that exists | Unit test + eval |
| Offline run | `pytest` and the dashboard run with no keys and no GPU | GitHub Actions, Streamlit rules-only mode |
| Jira | Dry-run JSON always works; live sync only when env vars are set | Mocked API test |

The résumé may quote only numbers that appear in `evals/reports/`.

## 7. Experience principles

- **Numbers are code.** The model ranks and writes. It does not calculate.
- **One graph.** Intake → plan → RCA → status → (feedback → plan) or close-out.
- **Audience changes the words, not the facts.** Customer copy omits unconfirmed internal blame. Leadership copy leads with cost, risk, and the ask.
- **A weak signal stays weak.** If no stratum clears the evidence bar, the answer is "no single cause", not the loudest injection.
- **Simulation labeling is part of the UI,** not a footnote.

## 8. Functional requirements

1. `python -m invalid_agent.sim.generate scenarios/bad_lot.yaml` prints rate vs spec, top strata, and rule violations.
2. `python -m invalid_agent.graph --scenario bad_lot --week 0` writes `out/week0_triage.md`.
3. `--week 4` writes `out/exec_deck.pptx` and the CAPA record.
4. The fidelity guard rejects a planted wrong number (test).
5. On `bad_lot`, the top fishbone branch is Material and the 5 Whys ends on a lot-level cause.
6. With no Jira env vars, sync writes `out/jira_issues.json` and does not open a socket.
7. `streamlit run app/streamlit_app.py` renders the case without a model.
8. `python evals/run_eval.py --backend deterministic --limit 5 --smoke` finishes in CI.

## 9. Data

Synthetic run-level rows. Distributions are **seeded from** public sources and are not copies of those files:

- openFDA Device Adverse Events (MAUDE): failure-mode themes and product-problem categories. Optional API key. Default path uses a bundled theme list and does not call the network.
- Mendeley HIL indices (Merrill, Mainali, Krasowski 2021, DOI 10.17632/vxkkdmw55f.1): the shape of a hemolysis-index distribution for pre-analytical scenarios.
- Zenodo pseudonymized CBC (record 15674541, CC BY 4.0): cited as the public CBC source we did **not** redistribute. v1 does not download the 45.9 MB workbook; pre-analytical signal is carried by the HIL-style index.

Details and the "do not redistribute" rule are in `DATA_LICENSES.md`. The customer, lots, instruments, sites, and complaint text are fictional.

## 10. Root-cause catalog

The generator can inject one of:

| Id | 6M home | What the field sees |
|---|---|---|
| `bad_reagent_lot` | Material | One lot's invalid rate jumps; other lots on the same instruments stay in spec |
| `drifting_instrument` | Machine | One instrument drifts; lots look normal once you stratify |
| `site_temperature` | Environment | Shipping/storage temperature excursion at one site, code INV-TMP |
| `software_version` | Method | One software version, code INV-SW |
| `preanalytical_hemolysis` | Material | One site's specimens show a high hemolysis index, code INV-HEM |
| `user_process_error` | Man | One operator, code INV-USR |
| `no_single_cause` | — | Rate is up, but no stratum clears the evidence bar |
| Red herring | — | An injection names the wrong cause; the table names the right one |

## 11. Non-functional requirements

- Runs on a 32 GB laptop with no GPU. Dev model, when used, is Ollama `llama3.1:8b`.
- Hosted demo target is Streamlit Community Cloud. Default backend is deterministic so the app fits the free RAM limit. Llama 3.2 1B via `llama-cpp-python` is optional and off by default.
- No secret in the repo. `.env.example` has empty values.
- CI is GitHub Actions, offline, Python 3.11 and 3.12.

## 12. Risks to the product

| Risk | Mitigation |
|---|---|
| A small model invents a rate or a cause | Deterministic metrics, evidence-required 5 Whys, fidelity guard, rules-only default |
| Synthetic RCA is too easy | Noise, a below-threshold case, red herrings, "no single cause" |
| Jira Cloud field ids differ by site | One adapter, dry-run default, live path best-effort |
| A reader thinks the data are real | Disclaimer on README, app banner, memo, and deck |
| Free-host terms change | The app is a Streamlit script plus a CLI. No host-specific SDK |

## 13. Analytics events

None. This is a local simulation. The eval report is the only scorecard.

## 14. Open items that need Neel

1. Create the Jira Cloud Free site and, when he wants live sync, an API token in the environment. The repo runs without it.
2. Sign in to Streamlit Community Cloud with GitHub and pick `app/streamlit_app.py`.
3. Install Ollama and `llama3.1:8b` only if he wants the local model comparison.
4. Sanity-check the root-cause list and the weekly injections against his QC experience before he quotes the eval numbers.
