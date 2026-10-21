# Session 7 logic trace

Snapshot id: git tag `session-7`. Resolve the commit with `git rev-parse session-7^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 7\`. This workspace has no Windows path, so the tag is the snapshot.

## 1. Goal

A Streamlit page a reviewer can click through: pick a scenario, move the week, and see the rate against the 2% spec, the p-chart, the Pareto, the strata, a before/after projection, and the week's memo, fishbone, 5 Whys, CAPA, plan, risks, and status notes. Rules-only is the default. The page carries the simulation banner.

## 2. What had to be true before Session 8

`run_case` already returns the metrics, the hypotheses, and the markdown. The dashboard calls that function. It does not grow a second investigation loop. Session 8 can score the same scenarios the picker lists.

## 3. Why these libraries

- **Streamlit** is the page and the free host. `st.cache_data` keeps a week from recomputing when the reviewer switches a tab.
- **Plotly** draws the p-chart, the Pareto, and the before/after chart in the browser. The PNG path for later slides stays on matplotlib, because Plotly's static export needs Kaleido and a browser binary we are not shipping.
- No new model library. Rules-only sets `LLM_BACKEND=deterministic`. That is what hosted Streamlit runs: Streamlit Cloud has no Ollama. Turning the toggle off on a local or self-hosted machine asks Ollama for `LLM_MODEL` when that variable is set, and for Llama 3.2 1B (`llama3.2:1b`) when it is not. `narrate` still replaces a missing or rejected draft with the template.

## 4. Code, and why it is shaped this way

`app/streamlit_app.py` is the page. `streamlit_app.py` at the repo root runs that file with `runpy`, so both `streamlit run streamlit_app.py` and Streamlit Community Cloud's default filename work.

- `_dashboard_model` (line 29) is the only place the page chooses a model name. An explicit `LLM_MODEL` wins. Rules-only does not call a model. Hosted Streamlit stays on that default. With the toggle off and `LLM_MODEL` unset, a local or self-hosted run asks for `HOSTED_LLM_MODEL` (`llama3.2:1b`).
- `_run` (line 40) sets `LLM_BACKEND` for the call and puts `LLM_MODEL` on the environment only when the backend is not deterministic. It restores the previous environment afterwards, so a cached run cannot pin a model for the next CLI command in the same process. The cache key is scenario, week, backend, and model.
- The banner is the first markdown on the page (line 71). The spec line under the title restates validity ≥ 98%.
- KPI tiles use `result["metrics"]["overall"]` and the triage memo's escalate flag. RAG is read off the leadership note (`RAG: Red`, `RAG: Amber`, `RAG: Green`), which is the same string `status.py` wrote.
- The strata select box and the projection both call code that already existed: `rank_hypotheses` inside `run_case`, and `projection_summary` for the counterfactual. The caption repeats the projection label, including "Not observed".
- Tabs render the markdown the graph already stored. The Gantt HTML stays a file under `out/dashboard/<scenario>/weekN/`. The task table on the page is the same plan.

`artifacts/charts.py` builds the three Plotly figures. Colors are navy `#0B3A5B`, teal `#1F7A8C`, and red `#B23A48` for rule-1 marks. No purple gradient.

`metrics/effectiveness.py` copies the frame, clears invalids on the leading stratum, and returns before/after rates. It does not rewrite the scenario file.

`.streamlit/config.toml` sets the navy theme, headless mode, and turns usage stats off. `requirements.txt` is the Streamlit Cloud install list. It does not install a GGUF.

## 5. What was documented, and why

The README model table names `llama3.1:8b` as the local default. Hosted Streamlit runs rules-only (deterministic). `llama3.2:1b` is the suggested small tag for local or self-hosted runs. Gemma 3 (`gemma3`) and Phi-4 (`phi4`) are other `LLM_MODEL` values. The page caption says when no model is called. `.env.example` lists the same single variable.

## 6. Stakeholder / Jira buy-in before Session 8

Ticket **INV-301**, epic **INV-5**: the dashboard. Neel still has to sign in to Streamlit Community Cloud himself and pick `app/streamlit_app.py`. This session does not create that account. No Jira token.

## 7. Approval → capability added

`tests/test_dashboard.py` checks that removing the bad lot lowers the projected rate, and that `AppTest` renders the banner without an exception. `pytest` stays offline.

## 8. What a hiring manager can see

A decision page: the rate versus the promise, where the points leave the control limits, and the week's note to the customer. The numbers on the tiles are the metrics object, not a sentence the model wrote.

## Line-by-line walkthrough

Check out `session-7` first.

1. Open `app/streamlit_app.py`. `main` starts at `set_page_config`, then the banner HTML.
2. The sidebar builds labels from every `scenarios/*.yaml`, defaulting the week slider to 0 and rules-only to on.
3. `_dashboard_model` reads `LLM_MODEL` from the environment before `load_settings` fills the local default, so an unset variable on this page means Llama 3.2 1B only when the toggle is off.
4. `_run` points `run_case` at `out/dashboard/<stem>/week<N>` and restores the environment in `finally`.
5. Five metric tiles. The delta on the rate tile is percentage points versus the spec, colored inverse so "above spec" reads as bad.
6. `p_chart_figure` and `pareto_figure` take the dicts already on `result["metrics"]`.
7. `projection_summary` regenerates the frame from the scenario seed. Same rows as the graph. The chart is labeled as a projection.
8. The six tabs are the strings on the result. Switching tabs does not call `run_case` again, because of the cache.
9. `tests/test_dashboard.py` `test_streamlit_app_renders_the_banner` loads the page with `AppTest` and asserts the disclaimer and at least one metric.

## Quiz

See `QUIZ.md`.
