# Session 9 logic trace

Snapshot id: git tag `session-9`. Resolve the commit with `git rev-parse session-9^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 9\`. This workspace has no Windows path, so the tag is the snapshot.

## 1. Goal

Close the case at week 4. D7 and D8 are confirmed, the effectiveness check is a labeled projection, and `out/exec_deck.pptx` is a seven-slide deck a reviewer can open. The README and the résumé bullets use the Session 8 counts, including the misses.

## 2. What had to be true before calling the project done

Tags `session-1` through `session-9` exist. `pytest` passes offline. `streamlit run streamlit_app.py` renders the banner. `python -m invalid_agent.graph --scenario bad_lot --week 4` writes the deck. The model name in the repo is `LLM_MODEL`, default `llama3.1:8b`. Hosted Streamlit runs rules-only (deterministic). `llama3.2:1b` is the suggested small tag for local or self-hosted runs.

## 3. Why these libraries

- **python-pptx** writes a real `.pptx`. The deck does not go through a model, so a slide cannot invent a cost.
- **matplotlib** with the Agg backend writes the p-chart PNG embedded on the root-cause slide. Plotly's static export needs Kaleido, which we do not ship.
- No new model library. Close-out is a template plus the fidelity guard.

## 4. Code, and why it is shaped this way

`graph.py` `route_after_status` returns `closeout` when the week that just finished is at least 4. Weeks 0 through 3 still end or advance, so the earlier tests do not build a deck.

`nodes/closeout.py`

- `build_closeout_facts` regenerates the frame, calls `projection_summary`, and drops the frame before the record is stored. Cost is `k * cost_per_invalid_usd`.
- `render_closeout` interpolates those facts. The effectiveness sentence includes the projection label: "Not observed follow-up."
- `closeout_node` runs `check_narrative` and raises on an unknown number. It writes `closeout.md` and calls `write_deck`. D7 and D8 on the CAPA record are replaced, and `preliminary_close` becomes false.

`artifacts/deck.py` `write_deck` makes seven slides: title and disclaimer, executive summary, impact, root cause with the observed p-chart, options, recommendation, ask. Colors are navy `#0B3A5B` and teal `#1F7A8C`.

A single-cause call recommends containing that stratum and not expanding. `no_single_cause` recommends no quarantine.

## 5. What was documented, and why

`README.md` carries the disclaimer, the quickstart, the model table (Llama 3.1 8B locally, rules-only on hosted Streamlit, `llama3.2:1b` for a small local or self-hosted run, Gemma 3 and Phi-4 as alternatives), the eval table from `evals/reports/2026-10-20.md`, and the three things Neel still has to sign in for. `RESUME_BULLETS.md` repeats the 22/22 cell next to the keyword 3/22 and the four drift files that also cleared a lot. Quoting the first number alone would mislead.

## 6. Stakeholder / Jira buy-in

Ticket **INV-303**, epic **INV-6**: the deck. Leadership's week-4 injection on `bad_lot` asks for the recommendation and the effectiveness check. The deck is that answer. No Jira token is required to generate it.

## 7. Approval → capability added

`tests/test_closeout.py` runs `--week 4`, opens the pptx, and checks seven slides, the disclaimer, the projection label, the 3.67% rate, and lot L-4419.

## 8. What a hiring manager can see

A recommendation with a cost, a risk, and an ask, plus a scorecard that shows where a naive reading of the customer note goes wrong. The projection is marked as a projection.

## Line-by-line walkthrough

Check out `session-9` first.

1. Open `graph.py` `route_after_status`. Week 4 is the only route into `closeout`.
2. Open `nodes/closeout.py` `build_closeout_facts`. The cost line is `invalids * unit`. The label comes from `projection_summary` unchanged.
3. `render_closeout` is the only prose. `closeout_node` refuses to write it if `check_narrative` fails.
4. Open `artifacts/deck.py` `write_deck`. Count `_blank` calls. There are seven. The title slide paints the disclaimer in white on navy.
5. Run `python -m invalid_agent.graph --scenario bad_lot --week 4` and open `out/exec_deck.pptx`. The root-cause slide's chart is the observed weekly rate. The sentence under it says the removal figure is not follow-up.
6. Open `RESUME_BULLETS.md` and read the drift bullet before using the 22/22 line.

## Quiz

See `QUIZ.md`.
