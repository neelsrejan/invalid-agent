# Guided page logic trace

The page is one script. It walks Week 1, then Week 2, then Week 3, then Week 4. Each week is one page: companies over 1% (`eda`), cause sets (`pareto`), simulated responses (`responses`), and the close-out (`closeout`). The JJE file is not sliced by week. Next stays off until that week's judge and guard both pass, or the reader presses Show me and the page logs the real sentence from `part_fact`. A question is answered and does not unlock Next. Python computes every count. Each week makes one Groq call. The model writes the reply and `meets_goal`. Python guards the entities and the numbers. The design is `docs/WEEK_DESIGN.md`.

There is no week switcher. The hosted picker lists JJE only.

## main

`main` (`app/streamlit_app.py:720`) loads dotenv and Streamlit secrets, then `load_settings`. The banner is `PUBLIC_BANNER` or `PRACTICE_BANNER`. `_scenarios` (`app/streamlit_app.py:113`) lists cases. On the hosted app that returns only `cases/openfda_jje.yaml`. A local run appends that file after every `scenarios/*.yaml` file.

`ensure_checkout` (`src/invalid_agent/fresh.py:120`) drops stale `invalid_agent` modules. `note_imports` is `src/invalid_agent/fresh.py:149`. `main` calls `_init_state` and `_render_guided`. `main()` runs at import so `streamlit run` and AppTest both enter here.

## _init_state

`_init_state` (`app/streamlit_app.py:122`). Keys in `_KEPT_KEYS` (`app/streamlit_app.py:59`) are re-assigned when already present. `story_week` cannot rise above `unlocked_week`, and `unlocked_week` cannot rise above 4. Changing `scenario_id` clears the story and locks the walk back to week 1.

## _render_guided

`_render_guided` (`app/streamlit_app.py:681`) loads one week view through `_week_view` (`app/streamlit_app.py:220`), which calls `build_week_view` (`src/invalid_agent/ui/story.py:59`). A load failure logs the exception type and shows one fixed sentence. Every week shows the case title as plain text. There is no case selectbox, and the view is not loaded a second time.

The title comes from `progress_label` (`src/invalid_agent/ui/guide.py:61`) and `GUIDE_STEPS` (`src/invalid_agent/ui/guide.py:26`). The four ids are `eda`, `pareto`, `responses`, `closeout`.

`_render_audit` (`app/streamlit_app.py:551`) draws that week's table, chart, and note. Week 2 draws one Pareto chart per flagged company (bars plus a cumulative line). `_render_talk` (`app/streamlit_app.py:403`) is on every week. `_nav` (`app/streamlit_app.py:648`) draws Back, Show me, and Next. Next is disabled until the week is done. Leaving week 1 logs the data-request tickets. Leaving week 2 logs the statement-and-triage tickets. Those messages are shown in the app and are not sent.

The week view cache key is `_VIEW_SCHEMA` (`app/streamlit_app.py:216`). Press Reboot app once after a deploy that changes the view.

## audit.py

`company_table` (`src/invalid_agent/ui/audit.py:47`) is one row per company. Share is invalid rows divided by total rows. A company with fewer than 100 reports is too few to judge. `cause_set_for` (`src/invalid_agent/ui/audit.py:146`) is the smallest top-of-Pareto set that brings the company to 1% or under. When the last slot is a tie, the set records every code at that count. `show_me_fact` (`src/invalid_agent/ui/audit.py:332`) is the sentence Show me logs. `hints_for` (`src/invalid_agent/ui/audit.py:366`) returns no lines.

## Week 1 judge

`judge_week1` (`src/invalid_agent/ui/week1.py:36`) makes one Groq call. The call carries the compact company table, the week rubric, and the user text, at temperature 0, with a 15 second timeout. The fallback model gets the same limit, so the two calls together stay near 30 seconds. The model writes the reply and a `meets_goal` JSON object.

`_guard` (`src/invalid_agent/ui/week1.py:326`) keeps `meets_goal` only when it is true and `_name_gap` (`src/invalid_agent/ui/week1.py:313`) finds every flagged company named in its own segment without a negation. An extra company blocks Next only when that same segment claims it is over the line. A segment that says under, below, not, no, neither, nor, less than, fine, or ok does not. Matching is case-insensitive and uses the company aliases (`abbott` is Abbott Labs). This is a name check, not a required phrase. When that check overrides a true `meets_goal`, the reply is one neutral line and does not name the missing or wrong company. Percents in the reply have to be on the table (`prose_numbers_match`, `src/invalid_agent/ui/week1.py:91`). An N-of-M pair is checked when its total is at least 100, or when that total belongs to a company named in the same sentence. A bare pair such as `2 of 3` is left alone. A failed call, an unparsed reply, or an invented number is replaced by `python_sentence` (`src/invalid_agent/ui/week1.py:77`). Week 1 does not run `reword_reply` (`src/invalid_agent/ui/talkback.py:260`). The decision is `docs/adr/0002-week1-model-judges.md`.

## talk-back

`example_prompts` (`src/invalid_agent/ui/talkback.py:146`) fills the prompt buttons. `respond` (`src/invalid_agent/ui/talkback.py:196`) sends every audit week through `_respond_audit` (`src/invalid_agent/ui/talkback.py:231`). Week 1 calls `judge_week1`. Weeks 2-4 call `judge_week` (`src/invalid_agent/ui/weeks.py:69`). `_guard` (`src/invalid_agent/ui/weeks.py:339`) keeps `meets_goal` only when the required entities are named in their own run and an extra entity is not claimed there. A negated required entity counts as missing. The override line does not name the entity. The audit weeks do not run `reword_reply` (`src/invalid_agent/ui/talkback.py:265`). `part_fact` (`src/invalid_agent/ui/talkback.py:557`) is the Show me sentence. Questions never confirm. The six-part grader below `AUDIT_WEEKS` remains for the synthetic practice cases.

`explore_facts` (`src/invalid_agent/ui/explore.py:81`) attaches the audit table. `_audit_for_week` (`src/invalid_agent/ui/explore.py:126`) hides cause sets until week 2, company notes until week 3, and close-outs until week 4. The rows themselves stay the whole file.
