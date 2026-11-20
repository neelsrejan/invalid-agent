# Guided page logic trace

The page is one script. It walks Week 1, then Week 2, then Week 3, then Week 4. Each week has six parts: complaint, numbers, charts, what gets logged, root-cause notes, and a wrap-up. The next week unlocks only when the wrap-up's Next button is pressed. Python computes every count. A language model may only rephrase the talk-back reply.

There is no week switcher and no free-explore panel. Those were the old way to skip ahead.

## main

`app/streamlit_app.py:504` `main` loads dotenv and Streamlit secrets, then `load_settings`. `app/streamlit_app.py:510` sets `public` from `DATA_BACKEND=openfda`. The banner is `PUBLIC_BANNER` or `PRACTICE_BANNER` from `src/invalid_agent/ui/plain.py`. `app/streamlit_app.py:513` calls `_scenarios` (`app/streamlit_app.py:89`). On the hosted app that returns only `cases/openfda_ooi.yaml` and `cases/openfda_jje.yaml`. A local run appends those two after every `scenarios/*.yaml` file.

`app/streamlit_app.py:522` calls `_init_state`. `app/streamlit_app.py:531` calls `_render_guided`. `main()` runs at import so `streamlit run` and AppTest both enter here.

## _init_state

`app/streamlit_app.py:98`. The first loop re-assigns each key in `_KEPT_KEYS` (`app/streamlit_app.py:36`) to itself when the key is already present.

Streamlit deletes a widget key at the end of a run that did not render that widget. `scenario_id` is the case select box, and it is drawn only on week 1, part 1. `stratum` is the break select box, drawn only on the charts part. `audience` is the note radio, drawn only on the notes part. `talk_text` is drawn on every part, but it is in the list anyway. `story_week`, `beat`, `unlocked_week`, `week_insights`, and `open_items` are not widgets. Re-assigning them is harmless and keeps the same habit as the widget keys.

After the re-assign, the function clamps `story_week` so it cannot be higher than `unlocked_week`, and `unlocked_week` cannot be higher than 4. A session value of week 4 on a fresh visit is put back to week 1. Changing `scenario_id` clears the story, the insights, and the open tickets, and locks the walk back to week 1.

## _render_guided

`app/streamlit_app.py:443`. It loads one week view through `_week_view` (`app/streamlit_app.py:191`), which calls `build_week_view`. On week 1, part 1, `_render_case_picker` (`app/streamlit_app.py:432`) draws the case select box, then the view is loaded again so the complaint matches the case.

The part title comes from `progress_label` (`src/invalid_agent/ui/guide.py:110`) and `GUIDE_STEPS` (`src/invalid_agent/ui/guide.py:30`). The six ids are `complaint`, `data`, `charts`, `logged`, `notes`, `wrap`.

`beat_lines` (`src/invalid_agent/ui/story.py:196`) is the text. The charts part also draws the weekly rate chart and the invalid-type bars from `view["chart"]` and `view["pareto"]`. The red-mark sentence is `view["rule1_sentence"]`. The talk-back reply for "why is the rate going up" includes that same sentence. It does not run a second count.

`_render_carried` (`app/streamlit_app.py:244`) lists open tickets and flags from earlier weeks at the top of week 2, 3, and 4. `_render_talk` (`app/streamlit_app.py:265`) is on every part, including the finished screen. `_render_insights` (`app/streamlit_app.py:255`) prints `Week N insights` under the reply. `_nav` (`app/streamlit_app.py:398`) draws one Back button and one Next button, after the insights.

Next on the wrap-up of week N sets `story_week` to N+1 and raises `unlocked_week`. Next on the week-4 wrap-up sets `finished`. Back from week 2, part 1, returns to the week-1 wrap-up. Back does not lock the week again.

## The week view

`build_week_view` (`src/invalid_agent/ui/story.py:60`) slices the frame with `slice_through_story_week` (`src/invalid_agent/ui/story.py:34`). Week 1 keeps the first quarter of the dates. Week 2 keeps the first half. Week 3 keeps the first three quarters. Week 4 keeps the whole file. Rates, the weekly chart, the invalid-type bars, the ranker, and the what-if all use that slice.

Week 1 also shows the opening note that the old loop stored as week 0, plus the week-1 note. There is no week 0 on the page.

The break menu defaults to the ranker's column (`_default_break`, `src/invalid_agent/ui/story.py:458`). Blank levels (`UNREPORTED`) are left out of the table. The caption says a blank is not a cause.

A what-if that clears every invalid says `0%` and explains that this is a pretend cleanup, not a new test (`_projection_sentence`, `src/invalid_agent/ui/story.py:388`). It does not print `0.00%`.

Tickets come from `build_plan`. Display keys are `INV-1`, `INV-2`, and so on, in plan order, including the tasks from the old week 0 inside week 1. The old "Retest" task name is "Check the next-best group again".

The wrap-up text is built for the week on screen. Week 4 does not hide the recommendation behind a button.

## Talk-back

`respond` (`src/invalid_agent/ui/talkback.py:89`) classifies the message as correct, partly right, not supported, or a question. The facts are the week view. A correct insight returns a bullet: the finding, then the Jira ticket id, then what to remember. `_apply_talk` (`app/streamlit_app.py:211`) appends that bullet to `week_insights[week]` and appends an open item. Other replies log a flag (`Flag 1`, `Flag 2`, ...) and do not add a bullet. Open items are shown at the top of the next week.

`example_prompts` (`src/invalid_agent/ui/talkback.py:63`) builds three clickable prompts from the same view, including "Why is the invalid rate going up?"

`reword_reply` (`src/invalid_agent/ui/talkback.py:139`) calls the model only when fixed wording is off and a model exists. The draft is kept only when it still contains every number from the plain reply, still names the ticket or flag, and does not contain a banned token such as `fidelity` or a server path. Any failure returns the plain reply. The page never prints "Fidelity ok" or "model draft was rejected".

## Words

`src/invalid_agent/ui/plain.py` holds the banners, the percent formatter, and `unexplained_jargon`. A term such as MAUDE, OOI, JJE, or openFDA may appear only when the same text explains it. The page does not use the bare words estimable, Pareto, strata, fidelity, pooled, control chart, Western Electric, lift, UCL, LCL, p-chart, denominator, deterministic, or narrative. Case-file sentences that already contain one of those words go through `with_gloss` before they are shown.
