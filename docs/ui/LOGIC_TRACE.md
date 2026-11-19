# Guided page logic trace

The page is one script. `main` keeps the case and the week, then draws one step. The step copy and the ranker sentences live in `ui/guide.py`. Python still computes every rate. This trace is the call chain, with the lines as they are on this commit.

## main

`app/streamlit_app.py:779` `main` loads dotenv and Streamlit secrets, then `load_settings`. `app/streamlit_app.py:785` sets `public` from `DATA_BACKEND=openfda`. `app/streamlit_app.py:789` calls `_scenarios` (`app/streamlit_app.py:92`). On the hosted app that returns only `cases/openfda_ooi.yaml` and `cases/openfda_jje.yaml`. A local run appends those two after every `scenarios/*.yaml` file.

`app/streamlit_app.py:798` calls `_init_state`. `app/streamlit_app.py:820` then branches: Free explore calls `_render_explore` (`app/streamlit_app.py:681`). The guided walk calls `_render_guided` (`app/streamlit_app.py:644`). `app/streamlit_app.py:826` calls `main()` at import so `streamlit run` and AppTest both enter here.

## _init_state

`app/streamlit_app.py:174`. The first loop, `app/streamlit_app.py:175`, re-assigns each key in `_KEPT_WIDGET_KEYS` (`app/streamlit_app.py:171`) to itself when the key is already present.

Those four keys are widget keys: `scenario_label` (the case select box), `week` (the week slider), `stratum` (Break by), and `audience` (the status radio). Streamlit deletes a widget key at the end of a run that did not render that widget. The guided steps do not render the sidebar select box or the slider, so without the re-assignment the next run finds the key missing and the defaults below put the case back on the first file and the week back on 0. Writing the key into this run's session state, before any widget is created, is the documented way to keep it.

`app/streamlit_app.py:191` fills week 0 when the key is absent, then clamps it to 0–4. `app/streamlit_app.py:194` fills the first case label when the saved label is missing or not in this run's list. `artifact` is not a widget key. `audience` is, and `app/streamlit_app.py:199` fills `customer` only when the saved value is not one of the three audiences.

## _render_guided

`app/streamlit_app.py:644`. `app/streamlit_app.py:650` reads `guide_step`. `app/streamlit_app.py:651` indexes `GUIDE_STEPS`. `app/streamlit_app.py:659` prints `progress_label` and the step title. `app/streamlit_app.py:660` calls `_render_brief` (`app/streamlit_app.py:511`), which prints the step's `doing`, `why`, and `look` strings. `app/streamlit_app.py:661` calls `_nav` (`app/streamlit_app.py:496`) for Back and the step's `next_label`.

`app/streamlit_app.py:664` resolves the case from `scenario_label`. On the case step, `app/streamlit_app.py:668` calls `_render_case_picker` and `app/streamlit_app.py:669` calls `_render_selected_complaint`. The picker buttons are the ids in `SUGGESTED_CASE_IDS` that this run actually loaded. The hosted list is OOI and JJE, so those are the two buttons. The reagent-lot file is a button only when that synthetic file is in the list.

`app/streamlit_app.py:673` calls `_load_result` (`app/streamlit_app.py:217`) when `step.needs_case` is true. That calls `run_case`. `app/streamlit_app.py:676` calls `_render_guided_body`. `app/streamlit_app.py:678` repeats Back and Next at the bottom.

## _render_guided_body

`app/streamlit_app.py:527`. The complaint step returns at `app/streamlit_app.py:537`. The case step returns at `app/streamlit_app.py:543` because the picker was already drawn. Every later step prints the case id and week at `app/streamlit_app.py:547`, then the week chips via `_week_row` (`app/streamlit_app.py:438`).

The chart step (`app/streamlit_app.py:556`) draws the five tiles and the p-chart, and `_week_story` (`app/streamlit_app.py:456`) adds who arrived and the decision log line. Pareto is `app/streamlit_app.py:559`. Strata is `app/streamlit_app.py:561`: one break, then `cause_sentence`. The projection is `app/streamlit_app.py:581`. Artifacts are `app/streamlit_app.py:583`. Notes are `app/streamlit_app.py:589` and call `_render_note`. Jira is `app/streamlit_app.py:595`. The pitch is `app/streamlit_app.py:597`, which calls `_render_pitch` (`app/streamlit_app.py:603`).

`_render_pitch` shows the week-4 close-out markdown once. It does not also print the recommendation as a separate outcome line. `_offer_deck` (`app/streamlit_app.py:626`) names `exec_deck.pptx` and offers a download. It does not print the server path.

`app/streamlit_app.py:600` calls `_guided_questions` (`app/streamlit_app.py:517`) on the hosted backend. That filters `SUGGESTED_QUESTIONS` through `questions_for`.

## ui/guide.py

`src/invalid_agent/ui/guide.py` holds the words. It does not compute a rate.

- `GUIDE_STEPS` at `src/invalid_agent/ui/guide.py:27` is the ten steps, in order. The case step's `look` (`src/invalid_agent/ui/guide.py:62`) says the hosted page offers OOI and JJE.
- `progress_label` at `src/invalid_agent/ui/guide.py:256` formats `Step N of 10`.
- `rag_label` at `src/invalid_agent/ui/guide.py:260` reads `RAG: Amber`, `RAG: Green`, or `RAG: Red` from the leadership note. `_render_metrics` (`app/streamlit_app.py:249`) uses it.
- `cause_sentence` at `src/invalid_agent/ui/guide.py:270` turns the ranker's top hypothesis into one sentence. The strata step prints it.
- `decision_for_week` at `src/invalid_agent/ui/guide.py:285` and `arrivals` at `src/invalid_agent/ui/guide.py:296` supply `_week_story`.
- `stratum_label` at `src/invalid_agent/ui/guide.py:314` is the button text for a break column.
- `questions_for` at `src/invalid_agent/ui/guide.py:321` keeps a suggested MAUDE question when it matches the open product code. The pitch step lists all four because `match_case` is false.
