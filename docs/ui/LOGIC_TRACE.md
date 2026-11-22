# Guided page logic trace

The page is one script. It walks Week 1, then Week 2, then Week 3, then Week 4. Each week is one page: companies over 1% (`eda`), cause sets (`pareto`), simulated responses (`responses`), and the close-out (`closeout`). The JJE file is not sliced by week. Next stays off until that week's goal claim is confirmed, or the reader presses Show me and the page logs the real sentence from `part_fact`. A question is answered and does not unlock Next. Python computes every count. Groq may choose a tool and phrase. A phrased reply that adds a number, a code, a manufacturer, or a company the tool result did not name is replaced by the template.

There is no week switcher. The hosted picker lists JJE only.

## main

`app/streamlit_app.py:684` `main` loads dotenv and Streamlit secrets, then `load_settings`. The banner is `PUBLIC_BANNER` or `PRACTICE_BANNER`. `app/streamlit_app.py:111` `_scenarios` lists cases. On the hosted app that returns only `cases/openfda_jje.yaml`. A local run appends that file after every `scenarios/*.yaml` file.

`ensure_checkout` (`src/invalid_agent/fresh.py:120`) drops stale `invalid_agent` modules. `note_imports` is `src/invalid_agent/fresh.py:149`. `main` calls `_init_state` and `_render_guided`. `main()` runs at import so `streamlit run` and AppTest both enter here.

## _init_state

`app/streamlit_app.py:120`. Keys in `_KEPT_KEYS` (`app/streamlit_app.py:59`) are re-assigned when already present. `story_week` cannot rise above `unlocked_week`, and `unlocked_week` cannot rise above 4. Changing `scenario_id` clears the story and locks the walk back to week 1.

## _render_guided

`app/streamlit_app.py:631`. It loads one week view through `_week_view` (`app/streamlit_app.py:218`), which calls `build_week_view` (`src/invalid_agent/ui/story.py:59`). A load failure logs the exception type and shows one fixed sentence. On week 1, `_render_case_picker` (`app/streamlit_app.py:620`) draws the case box, then the view loads again.

The title comes from `progress_label` (`src/invalid_agent/ui/guide.py:76`) and `GUIDE_STEPS` (`src/invalid_agent/ui/guide.py:29`). The four ids are `eda`, `pareto`, `responses`, `closeout`.

`_render_audit` (`app/streamlit_app.py:524`) draws that week's table, chart, notes, and hints. Week 2 draws one Pareto chart per flagged company (bars plus a cumulative line). `_render_talk` is on every week. `_nav` draws Back, Show me, and Next. Next is disabled until the week is done. Leaving week 1 logs the data-request tickets. Leaving week 2 logs the statement-and-triage tickets. Those messages are shown in the app and are not sent.

The week view cache key is `_VIEW_SCHEMA` (`app/streamlit_app.py:214`). Press Reboot app once after a deploy that changes the view.

## audit.py

`company_table` (`src/invalid_agent/ui/audit.py:47`) is one row per company. Share is invalid rows divided by total rows. A company with fewer than 100 reports is too few to judge. `cause_set_for` (`src/invalid_agent/ui/audit.py:146`) is the smallest top-of-Pareto set that brings the company to 1% or under. When the last slot is a tie, the set records every code at that count. `goal_statement` (`src/invalid_agent/ui/audit.py:327`) accepts a claim only when the named companies, codes, branches, and numbers match that week. `show_me_fact` (`src/invalid_agent/ui/audit.py:409`) is the sentence Show me logs.

## talk-back

`example_prompts` (`src/invalid_agent/ui/talkback.py:150`) fills the prompt buttons. `respond` (`src/invalid_agent/ui/talkback.py:200`) answers a question from `explore.py` and grades a goal claim through `goal_statement`. `part_fact` (`src/invalid_agent/ui/talkback.py:537`) is the Show me sentence. Questions never confirm. The six-part grader below `AUDIT_WEEKS` remains for the synthetic practice cases.

`explore_facts` (`src/invalid_agent/ui/explore.py:81`) attaches the audit table. `_audit_for_week` (`src/invalid_agent/ui/explore.py:126`) hides cause sets until week 2, company notes until week 3, and close-outs until week 4. The rows themselves stay the whole file.
