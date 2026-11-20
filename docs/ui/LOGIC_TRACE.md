# Guided page logic trace

The page is one script. It walks Week 1, then Week 2, then Week 3, then Week 4. Each week has six parts: complaint, numbers, charts, what gets logged, root-cause notes, and a wrap-up. Next stays off until that part's key insight is confirmed, or the reader presses Show me and the page logs it. Start week N+1 is that same Next button on the wrap-up, so it stays off until the wrap-up insight is logged. Python computes every count. A language model may only rephrase the talk-back reply.

There is no week switcher and no free-explore panel. Those were the old way to skip ahead.

## main

`app/streamlit_app.py:805` `main` loads dotenv and Streamlit secrets, then `load_settings`. It sets `public` from `DATA_BACKEND=openfda`. The banner is `PUBLIC_BANNER` or `PRACTICE_BANNER` from `src/invalid_agent/ui/plain.py`. `app/streamlit_app.py:106` `_scenarios` lists the cases. On the hosted app that returns only `cases/openfda_ooi.yaml` and `cases/openfda_jje.yaml`. A local run appends those two after every `scenarios/*.yaml` file.

Before those imports, `src/invalid_agent/fresh.py` `ensure_checkout` drops `invalid_agent` modules whose files sit outside `src`, or whose files are newer than the mtime `note_imports` recorded. A rename of a step in memory does not reload the package. `.streamlit/config.toml` sets `fileWatcherType = "poll"` so a deploy can drop a changed module. `none` left the previous module in memory, and the first load after a deploy could still raise `TypeError` until a reload.

`app/streamlit_app.py:805` calls `_init_state` and `_render_guided`. `main()` runs at import so `streamlit run` and AppTest both enter here.

## _init_state

`app/streamlit_app.py:115`. The first loop re-assigns each key in `_KEPT_KEYS` (`app/streamlit_app.py:53`) to itself when the key is already present.

Streamlit deletes a widget key at the end of a run that did not render that widget. `scenario_id` is the case select box, and it is drawn only on week 1, part 1. `stratum` is the break select box, drawn only on the charts part. `audience` is the note radio, drawn only on the notes part. `story_week`, `beat`, `unlocked_week`, `week_insights`, and `open_items` are not widgets. Re-assigning them is harmless and keeps the same habit as the widget keys.

`talk_text` is drawn on every part, so it is not in `_KEPT_KEYS`. After a reply, `_apply_talk` bumps `talk_nonce` (`app/streamlit_app.py:244`). The box key includes that number, so the next run draws an empty box. The page does not pop `talk_text`.

After the re-assign, the function clamps `story_week` so it cannot be higher than `unlocked_week`, and `unlocked_week` cannot be higher than 4. A session value of week 4 on a fresh visit is put back to week 1. Changing `scenario_id` clears the story, the insights, the open tickets, and the deck, and locks the walk back to week 1.

## _render_guided

`app/streamlit_app.py:731`. It loads one week view through `_week_view` (`app/streamlit_app.py:224`), which calls `build_week_view`. A load failure, including a connection error, logs only the exception type and shows one fixed sentence. The sentence does not include the exception text or a connection string. On week 1, part 1, `_render_case_picker` (`app/streamlit_app.py:720`) draws the case select box, then the view is loaded again so the complaint matches the case. That second load uses the same fixed sentence.

The part title comes from `progress_label` (`src/invalid_agent/ui/guide.py:99`) and `GUIDE_STEPS` (`src/invalid_agent/ui/guide.py:30`). The six ids are `complaint`, `data`, `charts`, `logged`, `notes`, `wrap`.

`beat_lines` (`src/invalid_agent/ui/story.py:205`) is the text. The charts part also draws the weekly rate chart and the invalid-type bars from `view["chart"]` and `view["pareto"]`. Bar labels are the plain invalid-type names from `code_plain`. A public-report case titles the chart "Weekly share of reports". A practice case titles it "Weekly invalid rate". The red-mark sentence is `view["rule1_sentence"]`, and `direction_sentence` already includes it, so the charts part does not print it a second time. The talk-back reply for "why is the rate going up" includes that same sentence. It does not run a second count.

The numbers part uses `direction_head`, which does not say "This chart". The charts part and the wrap-up still use `direction_sentence`, which includes that sentence once.

The logged part and the notes part also open cached write-ups from `_case_sections` (`app/streamlit_app.py:523`). That call runs `run_case(..., llm=DeterministicLLM())`. It does not set `LLM_BACKEND` in the environment, so another session can still use Groq. Those write-ups cover the whole file, not the date slice on screen. A practice case says "whole practice file". A public-report case says "whole public report file". Each block says the rate in the sentences above the block is the one for this week. `sections_from_run` (`src/invalid_agent/ui/records.py`) turns the records into plain sentences and drops a sentence that still has unexplained jargon or a server path. Markdown marks are stripped before that check, so a word wrapped in underscores is still checked. An underscore inside an id stays. Each block is an expander, closed by default. The logged part also has Ask, which runs a prepared question against the report table. A missing table shows the same fixed sentence and does not print the exception.

The talk box uses a new key after every reply (`talk_nonce` in `_apply_talk`). That empties the box. Deleting the old key did not, because the browser sent the typed value back on the same run.

`_render_carried` (`app/streamlit_app.py:334`) lists open tickets and flags from earlier weeks at the top of week 2, 3, and 4. Each line is the key once, then Ticket or Flag, then the finding. It does not print "Flag 1: Flag 1". `_render_talk` (`app/streamlit_app.py:355`) is on every part, including the finished screen. The "You said" line is the reader's own words. It does not insert a gloss into that echo. `_render_insights` (`app/streamlit_app.py:345`) prints `Week N insights` under the reply. A ticket and a flag both show there as soon as the reply says they were logged. `_nav` (`app/streamlit_app.py:680`) draws Back, Show me, and Next. Next is disabled until the part is done.

Show me logs that part's key insight as Your ticket N and then enables Next. A confirmed talk-back reply enables Next when its finding is that same key insight. Next on the wrap-up of week N sets `story_week` to N+1 and raises `unlocked_week`, and only after the wrap-up insight is logged. Next on the week-4 wrap-up sets `finished`. Back from week 2, part 1, returns to the week-1 wrap-up. Back does not lock the week again. Back does not skip a part that is not done.

Week 4's wrap-up can build `exec_deck.pptx` in a temporary directory. The path is never shown. A public-report case (`estimable` false) uses the public banner, says "share of reports", and omits the 2% spec line. A practice case keeps the practice banner and the spec line. A build failure logs only the exception type and shows "The slide file did not build. Try again. This page does not show the error detail."

## The week view

`build_week_view` (`src/invalid_agent/ui/story.py:59`) slices the frame with `slice_through_story_week` (`src/invalid_agent/ui/story.py:33`). Week 1 keeps the first quarter of the dates. Week 2 keeps the first half. Week 3 keeps the first three quarters. Week 4 keeps the whole file. Rates, the weekly chart, the invalid-type bars, the ranker, and the what-if all use that slice. The week-1 sentence says those are the dates that would have arrived first, so the story does not peek ahead. When every date in the file is already inside the slice, the sentence says this week uses the whole file.

Week 1 also shows the opening note that the old loop stored as week 0, plus the week-1 note. There is no week 0 on the page.

The break menu defaults to the ranker's column (`_default_break`, `src/invalid_agent/ui/story.py:467`). Blank levels (`UNREPORTED`) are left out of the table. The caption says a blank is not a cause.

A what-if that clears every invalid says `0%` and explains that this is a pretend cleanup, not a new test (`_projection_sentence`, `src/invalid_agent/ui/story.py:397`). It does not print `0.00%`.

Plan tickets come from `build_plan`. Display keys are `INV-1`, `INV-2`, and so on, in plan order, including the tasks from the old week 0 inside week 1. The old "Retest" task name is "Check the next-best group again". A confirmed insight is not given the next INV number. It is "Your ticket 1", then "Your ticket 2". The reply says a real team would put that in Jira. This page does not create that ticket.

The week's call is "Look harder" or "Watch". It is not "Hold". Week 4 may still recommend holding one group, because that sentence is the recommendation, not the call label.

The decision for week 2 or 3 compares this week's leading group with the previous week's slice. It does not reuse a fixed sentence.

The MAUDE, OOI, and JJE glossary is on the complaint only when the case is a public-report file (`denominator` `reported_events`, or product code OOI or JJE). A practice case does not print it. The talk-back glossary still answers "What is MAUDE?" if the reader asks.

The wrap-up text is built for the week on screen. Week 4 does not hide the recommendation behind a button.

## Talk-back

`respond` (`src/invalid_agent/ui/talkback.py:155`) classifies the message against facts already on screen. The part order is complaint, numbers, charts, logged, notes, wrap-up. A claim that names invalid types as "most" or "biggest" before the charts part is `early`: the reply is `NOT YET — you'll see that on the charts part.` There is no ticket and no flag. A "going up", "increasing", "going down", or "decreasing" statement before the numbers part is the same kind of early reply, naming the numbers part.

A question, including one that starts with "would" or hides the question mark in parentheses, is answered and is not a ticket. "What is the invalid rate this week?" returns the rate sentence, not the chart sentence. A statement that denies a count, such as "INV-NOR is not the biggest", is a direct correction or agreement. It is not labeled "GOOD QUESTION." A doubt word (neither, nor when it is not the end of INV-NOR, doubt, false, hardly, isn't even close, or not, I think not, NOT!) is not confirmed and does not get a ticket. A code name that contains "not", such as "not enough sample", can still be confirmed when the counts agree. "hello", "asdf", and a remark that is not a question are a tip, not "GOOD QUESTION."

A correct insight returns a bullet and logs "Your ticket N". `_apply_talk` (`app/streamlit_app.py:244`) appends an open item. The same finding sent again does not take a new number. A partly right or unsupported insight logs a flag (`Flag 1`, `Flag 2`, ...) and that flag is in the Week N insights list, labeled Flag. Two unsupported claims about different codes do not share one flag signature. A question, including "What is MAUDE?" and "Who made the device?", gets a plain answer and logs nothing. Open items from earlier weeks are shown at the top of the next week, with the key printed once.

`example_prompts` (`src/invalid_agent/ui/talkback.py:91`) builds three clickable prompts from the same view. The "make up most of the invalids" prompt is not offered before the charts part. "Why is the invalid rate going up?" is on every part.

`reword_reply` (`src/invalid_agent/ui/talkback.py:185`) calls the model only when fixed wording is off and a model exists. `_draft_ok` (`src/invalid_agent/ui/talkback.py:208`) keeps the draft only when it still starts with the same opening verdict, the number tokens are the same sequence as the plain reply, the draft is negated only when the plain reply is negated, a ticket or flag id is still there as its own id, `unexplained_jargon` is empty, and `check_narrative` accepts the draft. Swapping 4.00% and 1.00% is rejected. Putting "NOT" into a YEP reply is rejected. The facts passed to `check_narrative` are the numbers parsed from the plain reply plus the ticket and flag ids. The plain reply itself is not passed as a string, because a long fact string would hide extra numbers. A draft that adds a number, lengthens the verdict, or uses an unexplained term is rejected. Any failure returns the plain reply. The page never prints "Fidelity ok" or "model draft was rejected".

## Words

`src/invalid_agent/ui/plain.py` holds the banners, the percent formatter, and `unexplained_jargon`. The check is per sentence. A gloss in one sentence does not excuse the same word in the next sentence. The page lint runs that check on each rendered element, not on the page glued together. A term such as MAUDE, OOI, JJE, openFDA, fishbone, containment, or Wilson may appear only when the same sentence explains it. The page does not use the bare words estimable, Pareto, strata, fidelity, pooled, control chart, Western Electric, lift, UCL, LCL, p-chart, denominator, deterministic, or narrative. Case-file sentences that already contain one of those words go through `with_gloss` before they are shown. On the page, `gloss_once` explains MAUDE, OOI, JJE, and each INV code the first time that token appears, and later sentences keep the short form. A sentence that is only "What is MAUDE?" is allowed, and "(FDA product code OOI)" is allowed, because the question or the label is the term itself. A bare OOI in a normal sentence is still unexplained. "nucleic acid" counts as the OOI gloss, as does "nucleic-acid". Agent write-ups go through `soften` and then `safe_prose`, which drops a sentence that still fails.

A public-report deck says "the company that made the device" instead of `reported_manufacturer` on the call line, and its impact slide does not print a dollar amount per invalid. A practice deck still prints the practice cost line.
