# openFDA backend logic trace

This note is the build diary for the MAUDE table. Names of functions are the stable citations. A line number is only a location on this branch.

## 1. Goal

Replace the synthetic-only frame with a hosted table of public openFDA device-event reports, without letting the language model do the math, and without hiding the firm names those public reports already contain.

## 2. What stays true

`src/invalid_agent/config.py` lines 14–15 still own the promise: validity 0.98, invalid cap 0.02. `load_settings` reads the environment and does not open dotenv files. `load_dotenv` reads `.env` and then `.env.local` (the file `neon deploy` writes). `.env.local` wins over `.env`. The process environment wins over both. Pytest sets `INVALID_AGENT_SKIP_DOTENV`. A test writes a temporary `.env` and a `.env.local` and checks that `load_settings` ignores them until `load_dotenv` is called.

`load_settings` applies `MANUFACTURER_DISPLAY`. The default is `real`. `_display_mode` accepts `real` or `anonymized` and treats anything else as `real`.

## 3. Denominator and names

`src/invalid_agent/data/mapping.py` lines 8–38 state the denominator: one row is one report, the numerator is an invalid-type label, and the 2% cap is not estimable. `INVALID_LABELS` starts at line 60. Wrong-result labels are listed after that and are not in the map.

`normalize_manufacturer` (line 170) uppercases the reported name, drops a parenthetical city, and strips legal suffixes. It does not contain a list of firms. The string that comes out is the string MAUDE reported, cleaned. `frame_from_reports` (`src/invalid_agent/data/frame.py` line 67) copies that name onto the frame. With the default display mode it leaves the name in place. `display_labels` (`src/invalid_agent/data/manufacturers.py` line 16) is used only when `anonymized()` (line 29) is true, and then the labels are Manufacturer A, B, C in alphabetical order of the reported names.

## 4. Dates on the chart

`frame_from_reports` lines 80–83 use `date_of_event` when it is present and the FDA received date otherwise. The same rule is in the weekly SQL template at `src/invalid_agent/data/query.py` line 106 (`COALESCE(date_of_event, date_received)`). The caveat string is stored at `frame.py` lines 124–125 and repeated on the question facts at `query.py` lines 321–322. `p_chart` (`src/invalid_agent/metrics/spc.py` line 80) still bins whatever date column it is given. It does not know which FDA field that date came from. The caption does.

## 5. Extract, cache, and load

`retry_delay` (`src/invalid_agent/data/extract.py` line 141) reads `Retry-After` when it is a number of seconds and otherwise returns 2. `fetch_page` (line 156) sleeps that long before the one retry. The key is a query parameter and is not printed.

`prepare_report_rows` keeps one row per `(mdr_report_key, product_code)`. The schema primary key is the same pair. `REPORT_INSERT_SQL` uses `ON CONFLICT` on that pair. Rows are written with `executemany`. `ensure_readonly_role` tells the owner to generate `DEMO_READONLY_PASSWORD` with `secrets.token_urlsafe(32)`. A shorter password prints a warning and is not echoed.

## 6. Questions

`match_question` (`src/invalid_agent/data/query.py` line 236) picks a template from the words in the question. It does not look for a firm name. The model may return a template id. Python runs the vetted SELECT and computes the rates.

## 7. Jira

`make_client` (`src/invalid_agent/integrations/jira.py` line 209) returns `ReadOnlyJira` (line 145) when credentials exist. That class searches. It does not post issues. `plan_node` calls it at `src/invalid_agent/nodes/planner.py` line 256. `source_label` (jira.py line 71) is `openfda` or `simulation`, and `build_plan` copies `data_backend` at planner.py line 126 so the label follows the case.

`seed_cases` (jira.py line 220) is the owner command `python -m invalid_agent.integrations.jira seed`. It searches for the case label first. It creates issues only when that label is absent, and it writes each case to its own local JSON file so one case cannot hide the next.

## 8. Fidelity on a real extract

A numeric lot id such as `10713760` sits inside `metric:reagent_lot:10713760:rate`. The guard used to read that as a rate. `stratum_levels` copies the value between the dimension and `:rate` into the facts labels, so the id is stripped before the number scan. `structure_numbers` includes every rank heading, including rank 9 when the openFDA branches are present.

`MIN_CONTRAST_N` is 5. `_contrast_id` and `_first_rate` skip a stratum under that count. A 1-of-1 lot is not the next-best cause.

`spec_claim_errors` rejects "does not exceed the specification" when the rate is above the spec number, and the reverse claim when it is not. `prompt_for` rounds floats to four decimal places before a model sees them. `_maskable` strips a lot id only when it has four or more digits, contains a letter, is a dotted version such as `2.4.0`, or sits in a `lot <id>` or `model <id>` phrase. A lot named `12` does not make a fabricated `12%` legal.

`GroqLLM.complete` spaces calls by two seconds on a process-wide lock, honors `Retry-After` on 429, and stops if those waits in one call would pass 15 seconds so the template can take over. It sends `reasoning_effort=low` and retries an empty reply once with a larger `max_tokens`. `narrate_status` asks a hosted model for the three audience notes in one call. The deterministic backend still renders each template on its own. `load_dotenv` reads `.env` and `.env.local`.

## 9. What this trace does not claim

The owner loaded the extract into Neon from another machine. The tests in this repo still use constructed rows and a fake Jira transport. They do not call openFDA.
