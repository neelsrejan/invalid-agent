# UI audit: hosted Invalid Bot demo

The page under review is `app/streamlit_app.py`, served from `main` by Streamlit Community Cloud at https://invalid-agent-lwycv4pt4vd4emwhuiqde3.streamlit.app/. The root `streamlit_app.py` only forwards to that file. This audit describes the control panel a first visitor met, where that panel made them invent the investigation order, and the guided flow that replaces it.

The navy banner, cream theme (`.streamlit/config.toml`), metric tiles, and Plotly charts stay. Free explore is the previous panel, one toggle away. Hosting stays Streamlit Community Cloud from `main`. Free tiers only. No API keys, tokens, or secrets belong in the repo, the git history, or the page source.

## Current layout

Top to bottom, one run of the page showed everything at once.

1. **Banner.** MAUDE cases use the public-report banner (reported events, the 2% cap is not estimable, not for clinical use). With `DATA_BACKEND` unset, the banner says the page is the CI fallback and lists synthetic cases under the MAUDE cases.
2. **Title.** "Invalid Bot", plus the promise line: validity at least 98%, so the invalid rate stays at or below 2%. Python does the math.
3. **Sidebar.** Three controls, with no sequence between them:
   - Scenario select box. Public mode lists `cases/openfda_ooi.yaml` and `cases/openfda_jje.yaml`. CI mode lists every `scenarios/*.yaml` file and then those two cases.
   - Investigation week slider, 0 through 4, default 0.
   - Rules-only toggle. On: templates only. Off: Groq on the hosted demo, Ollama on a laptop. A draft that fails the numeric check is replaced by the template.
4. **Five metric tiles.** Invalid rate or invalid-type share, the spec or the stated cap, the Wilson 95% interval, Escalate or Hold, and the RAG color read from the leadership note.
5. **Two charts side by side.** Weekly p-chart (Western Electric rule 1 in red) and the Pareto of invalid codes. A caption under the p-chart counts rule-1 marks. MAUDE cases add the received-date and manufacturer-name note.
6. **Strata.** A "Break by" select box and a table of level, n, k, and rate. No sentence says whether any slice cleared the evidence bar.
7. **Before / after.** The projection chart when a stratum cleared the bar, otherwise an info line. The caption carries the "Not observed" label.
8. **Artifact tabs.** Triage memo, Fishbone, 5 Whys, 8D / CAPA, Plan and risks (task table, risk table, Gantt caption), and Status notes. Status notes hide an audience radio: customer, internal, leadership.
9. **Jira.** Rendered only when the run returned issues. Mode, project, table, note, and live links when the mode is live.
10. **Ask the MAUDE table.** Four suggested questions (OOI share, JJE manufacturers, OOI invalid types, JJE weekly chart) and a typed question. Vetted read-only SQL. Python computes. A model may only choose a template.

The page calls `run_case` for the selected scenario and week. That is the same graph as the CLI. The field file does not change between weeks. Week changes the injections in scope, the plan, the three status notes, the decision log, the RAG color, and, at week 4 only, the close-out and the seven-slide deck.

## First-visitor confusion

A hiring manager landing on the URL has to invent the order of operations. The controls are real. Nothing says which one to touch first, or what the agent is doing.

- **No sequence.** Scenario, week, rules-only, charts, strata, projection, six tabs, Jira, and the question box are peers. The investigation has an order. The page does not.
- **The week slider looks like a filter on the chart.** The p-chart, Pareto, and strata are properties of the file. They stay put from week 0 to week 4. What moves is the story: who has spoken, what the note says, and whether close-out exists. A visitor who leaves the slider at 0 never sees the management pitch. A visitor who scrubs the slider looking for a new chart thinks the app is broken.
- **Week 4 is invisible.** Close-out and `exec_deck.pptx` are produced only when the requested week is 4. Nothing on the page says that. The deck path is not shown. The pitch is easy to miss inside the CAPA tab.
- **Every artifact is open at once.** The triage memo, fishbone, 5 Whys, 8D, plan, and three audience notes answer different questions. Tabs hide that. The audience radio is inside the last tab.
- **Strata and the projection have no plain-language call.** The evidence ranker can refuse a single cause. The table does not say so. The projection does not say, in the heading, that it is a counterfactual on the same file.
- **"Rules-only" is the first technical choice.** It matters, and it is unexplained relative to the complaint. A visitor cannot tell that Python already computed the tiles and that the toggle only changes wording.
- **Two products sit in one menu.** OOI and JJE are public MAUDE extracts in Neon. The other files are synthetic so CI can run with no database. The sidebar label "Scenario" does not say which complaint you are about to brief.
- **Jira and the questions are below the fold,** disconnected from the step that would use them. The four suggested questions are the right prompts, but they are not attached to the chart they explain.
- **The banner says the synthetic cases are "listed below."** They are in the sidebar. The sentence describes a layout the visitor cannot see.

## Redesign plan

The default experience is a guided walk, **Step 1 of 10**, with Back and a named Next button. Each step says what the agent is doing, why, and what to look at, and shows only that step's chart or artifact. Suggested actions are buttons on the step. The header keeps two toggles on every screen: **Free explore** and **Rules-only wording**.

| Step | Screen | What is on it | One-click actions |
|---|---|---|---|
| 1 | The complaint | The promise, the limit of the file, the ten-screen path | Next: Choose a case |
| 2 | Choose the case | Complaint text for the selected file. The hosted page offers OOI and JJE. A local run that also loads the synthetic files shows those too, and a full list when there are more files than the buttons | Case buttons, then Next: Investigate this case |
| 3 | The control chart | Rate tiles, Wilson interval, escalate/hold, RAG, p-chart | Week 0–4, the MAUDE question that matches this case, Next |
| 4 | Where invalids concentrate | Pareto only | Week, the invalid-type question when it matches, Next |
| 5 | Strata and root cause | One break at a time, then the ranker's sentence | Break buttons, the manufacturer question when it matches, Next |
| 6 | Before and after | The projection chart, or the line that no slice cleared the bar | Week, Next |
| 7 | This week's artifacts | One record: triage memo, fishbone, 5 Whys, 8D/CAPA, or plan and risks | Those five buttons, week, Next |
| 8 | Status notes | One audience note, plus what arrived this week and the decision log line | Customer, Internal, Leadership, week, Next |
| 9 | Jira tickets | The INV issues for this run. Live keys link out. This page does not create tickets | Week, Next |
| 10 | The management pitch | Week 4 close-out and the deck path. Earlier weeks explain that the pitch is week 4 and offer a button that opens it | Open the week-4 pitch, the four MAUDE questions on the hosted backend, Next: Look around on your own |

Free explore restores the control panel: sidebar scenario and week slider, the five tiles, both charts, Break by, before/after, the six tabs, Jira, and Ask the MAUDE table. The last Next button turns Free explore on. "Return to the guided steps" turns it off and lands back on the pitch.

Week chips are on every measured step so the visitor can walk week 0 through week 4 without guessing that a slider exists. The chart step says outright that the measurements stay on the file and the week changes the notes.

Ask the MAUDE table stays. On the hosted backend, each chart step offers the suggested question that matches the open case. The pitch step offers all four. The typed question stays with those blocks. Free explore keeps the original block, including on the CI fallback, where the buttons still call the same read-only path.

Rules-only stays a real toggle. On, no model is called. Off, Groq (hosted) or the configured local backend writes wording. A missing `GROQ_API_KEY` stops the run with the same instruction as before, after the visitor has seen the complaint, and the toggle is already on screen so they can switch to templates. Numbers stay in Python either way. The numeric-fidelity guard is unchanged.

## What stays

- `run_case` is still the only investigation. The page does not grow a second loop.
- Cache key remains scenario, week, backend, and model. The environment is restored after the call.
- OpenFDA rows still come from Neon through the read-only role. The page does not call openFDA.
- Jira is still read and linked. Seeding stays a local owner command.
- Streamlit Community Cloud still starts at `streamlit_app.py` on `main`. Secrets stay in the Streamlit secrets editor, from `.streamlit/secrets.toml.example`. Nothing in this redesign adds a secret to the tree.
