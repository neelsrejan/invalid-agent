# Academy quiz letters

These are the letters after `build_site.py` shuffles each question.
The salted hash on the page is a self-study speed bump, not protection.
Reading this file, or trying all four choices, bypasses it.
The prose quizzes in `docs/sessions/` are a separate set and are not these letters.

## Session 1

1. **A.** So the promised validity and the 2% invalid cap cannot drift apart. The unit test on this tag is the check.

2. **A.** A base URL, an email, and a token. Any missing piece leaves jira_enabled false. The logic trace names the same function. The unit test on this tag is the check.

3. **D.** It prints every field, including jira_api_token.

4. **C.** The build backlog for constructing the agent. Sprint 1 is INV-101 through INV-109.

5. **C.** Nothing in this tag imports them yet, so CI should not download pandas, LangGraph, or a model client. The logic trace names the same function. The unit test on this tag is the check.

6. **D.** pyproject.toml sitting next to scenarios/ or src/invalid_agent/.

7. **B.** deterministic. The unit test on this tag is the check.

8. **A.** Python 3.11 and 3.12, editable install with the dev extra, then pytest. No secrets. The logic trace names the same function.

## Session 2

1. **A.** Stacking two draws would raise the complement too, or double-count the mask. Replacing the mask leaves everyone else at baseline.

2. **C.** The analytic lower bound is 0. Floating point leaves a tiny residue, so anything under 1e-12 snaps back to 0. The unit test on this tag is the check.

3. **C.** Site, instrument, lot, software, and operator are drawn independently. A collection site is not tied to one instrument. The logic trace names the same function.

4. **B.** One point beyond 3 sigma; two of three beyond 2 sigma on one side; four of five beyond 1 sigma on one side; eight in a row on one side of the center.

5. **D.** They do not. seeds.py holds a lognormal stand-in and the DOI. The file is cited, not redistributed.

6. **D.** A scenario file plus a seed is the whole source of randomness, so the same YAML reprints the same field file. The logic trace names the same function.

7. **D.** p_value 1 and chi2 0. A quiet scenario is not an exception.

8. **C.** Valid rows. An empty invalid code must not count as a failure mode. The unit test on this tag is the check.

## Session 3

1. **B.** It stores metrics, hypotheses, the evidence catalog, the memo, and the fidelity record. A later node calls generate(scenario) again. The seed makes that the same frame. The logic trace names the same function. The unit test on this tag is the check.

2. **B.** Other strata miss at least one gate: 80 runs, lift 1.8, 15 excess invalids, and chi-square p < 0.01.

3. **D.** It survives masking, it is not within 0.03 of a walked fact, it lands in unknown, and ok is false.

4. **B.** narrate catches the exception, sets rewritten true, and returns the template. The failed draft is not saved. The logic trace names the same function. The unit test on this tag is the check.

5. **D.** A cause has to come from the table. A QA sentence does not get a vote.

6. **B.** It exits on purpose, so the tag cannot pretend the weekly loop already exists. The unit test on this tag is the check.

7. **D.** One httpx call is easier to mock, and it is not called when the backend is deterministic. The logic trace names the same function.

8. **D.** So 4419 cannot be reused as a permitted rate.

## Session 4

1. **B.** The 6M set is the diagram a quality reviewer expects. An empty bone with score zero says the category was considered.

2. **B.** An empty citation list, or an id that is not in the catalog. It runs inside build_whys, before markdown exists. The logic trace names the same function. The unit test on this tag is the check.

3. **A.** No. index_injections keeps only injections whose week is less than or equal to the case week. That note is week 1.

4. **A.** Return to the spec and no rule-1 point on the weekly p-chart. Follow-up runs do not exist, so a before/after figure would be a projection.

5. **B.** Define is D1–D2, Measure is the metrics, Analyze is D4 plus the fishbone and 5 Whys, Improve is D3 and D5, Control is D6 and D7. D8 is closure, not a DMAIC phase. The logic trace names the same function. The unit test on this tag is the check.

6. **C.** Material / bad_reagent_lot. Step 5 starts with a lot-level stop and includes the catalog sentence that names L-4419.

7. **D.** A different column, so the chain says why the next stratum is not the cause. The unit test on this tag is the check.

8. **D.** None. Pydantic checks the branch and the Why. The Session 3 fidelity guard is reused on the three markdown files. The logic trace names the same function.

## Session 5

1. **D.** write_image needs kaleido and a browser. The matplotlib path runs in CI and on a laptop without that download.

2. **D.** A task's start must be greater than or equal to the predecessor's end. The dates are YYYY-MM-DD, so dictionary order matches calendar order.

3. **C.** Week 2 adds T11, the lab-director note. R1's trend goes from new to down and its likelihood drops. R4 appears with trend up. The logic trace names the same function.

4. **D.** The build backlog uses INV-*. SIM-* makes a dry-run file obviously not that board.

5. **C.** LiveJira.sync catches it, stores the exception class name, writes the JSON, and does not raise. The token is not put in the error or in repr. The unit test on this tag is the check.

6. **C.** Zero new POSTs. The first sync posts the epic plus the tasks. _upsert updates a story in place when the task id is already in the file. The logic trace names the same function. The unit test on this tag is the check.

7. **D.** The planner reads the top hypothesis. It does not read the fishbone. RCA does not read the plan.

8. **A.** A lot is QA. An instrument or a temperature lane is Manufacturing. Software is R&D. No single cause stays with the PM, which means do not quarantine yet. The unit test on this tag is the check.

## Session 6

1. **B.** The field file is fixed by the scenario seed. Re-running triage would recompute the same metrics. The lap re-enters at plan. The logic trace names the same function.

2. **A.** The rate is still over spec, and containment is week 3, so week 2 is Red. The synthetic file is not rewritten, so it never goes Green. Amber means containment is underway, not that the rate recovered.

3. **D.** Keep the field ranking after release testing was reported as a pass, and add the lab-director note to the plan. The unit test on this tag is the check.

4. **C.** build_status_facts rounds the computed rate onto rate_pct. The template interpolates that field. The guard then checks the sentence. The logic trace names the same function.

5. **A.** out/week0/ and out/week2/. Compare plan.json and risk_register.md. The root copy is latest. The week folder is as of that week.

6. **D.** It must not state a confirmed cause. Internal gets the hypothesis. Leadership gets the cost and the ask.

7. **B.** Status is a comparison of integers. T1 (sim week 0) is Done and T11 (sim week 2) is Done. T10 (sim week 4) is still To Do. The logic trace names the same function.

8. **A.** advance, which adds one to the week and edges back to plan.

## Session 7

1. **B.** Streamlit Community Cloud has no Ollama, and this repo does not ship weights. The deterministic templates answer without a download. The unit test on this tag is the check.

2. **C.** LLM_MODEL. An explicit value wins. With the toggle off and the variable unset, a local or self-hosted run asks Ollama for llama3.2:1b. The CLI default remains llama3.1:8b. The logic trace names the same function. The unit test on this tag is the check.

3. **B.** projection_summary clears invalids on the leading stratum of the same synthetic file. No new field data were collected.

4. **A.** _run is cached on scenario, week, backend, and model. The radio only picks a string already stored on status_updates.

5. **C.** Sign in to Streamlit Community Cloud with GitHub and select app/streamlit_app.py or the root streamlit_app.py. The repo cannot do that sign-in. The logic trace names the same function. The unit test on this tag is the check.

6. **C.** Navy #0B3A5B and teal #1F7A8C for the series, red #B23A48 for rule-1 marks. No purple gradient.

7. **C.** A GGUF weight file. The install list is pandas, numpy, scipy, PyYAML, Pydantic, httpx, LangGraph, langchain-core, Plotly, matplotlib, python-pptx, and Streamlit.

8. **B.** AppTest renders the banner without an exception, including the clinical-use line, and at least one metric. A second test checks that removing the bad lot lowers the projected rate. The logic trace names the same function.

## Session 8

1. **B.** Evidence top-1 and top-3 were 22/22. Keyword top-1 was 3/22. The three keyword hits are the flat files, whose week-0 note names no cause.

2. **D.** The lot bump was built to stay under the lift gate. The correct call is to withhold. The keyword ranker repeats the note and says bad_reagent_lot.

3. **A.** A reagent-lot stratum also cleared the bar. Top-1 stayed drifting_instrument. The report lists that second stratum on purpose. The logic trace names the same function. The unit test on this tag is the check.

4. **C.** Neither model was installed. The table compares two ranking policies on the deterministic backend.

5. **B.** PyYAML 1.1 treats an unquoted true as a boolean. The generator looks up the string key "true". The unit test on this tag is the check.

6. **C.** eval.expect_cause. That block is the label for the score, not an input. The logic trace names the same function. The unit test on this tag is the check.

7. **A.** The guard strips an identifier only when the exact string is in the facts. Otherwise 2.4.0 was scanned as the number 2.4. Lot ids were already safe behind a hyphen. The guard's thresholds did not change.

8. **B.** The same eval entry point with --limit 5 --smoke. It fails if evidence top-1, fidelity, citations, or escalation miss. The unit test on this tag is the check.

## Session 9

1. **D.** Status is the weekly note. Close-out confirms D7 and D8 and writes the deck. Routing week 4 to closeout keeps that work inside the graph, under the fidelity check. The logic trace names the same function.

2. **B.** The generator does not rewrite the field file. Clearing the leading stratum is a counterfactual. bad_lot stays over spec in the observed series.

3. **B.** k times cost_per_invalid_usd from the scenario. For bad_lot that is 529 times 85. The template does not type the product. The unit test on this tag is the check.

4. **B.** Safe: evidence top-1 22/22 on this constructed set, keyword top-1 3/22, fidelity 22/22, and the four drift files where a lot also cleared the bar. Not safe: calling 22/22 a clinical accuracy rate, or a Llama 3.1 versus Llama 3.2 comparison. Those models were not run. The logic trace names the same function.

5. **C.** Seven blank-layout slides: title and disclaimer, summary, impact, root cause, options, recommendation, ask. No single cause recommends not containing a stratum.

6. **C.** LLM_MODEL defaults to llama3.1:8b, Meta Llama 3.1 8B via Ollama. Hosted Streamlit runs rules-only. llama3.2:1b is the small tag for a local or self-hosted run.

7. **C.** The recommendation and the effectiveness check. The deck is that answer. Ticket INV-303, epic INV-6. No Jira token is required to generate it. The logic trace names the same function. The unit test on this tag is the check.

8. **A.** A lab says a fictional panel missed a 98% validity promise. The ranker only keeps strata that clear a fixed bar. Notes that name the wrong cause do not outvote the table. The deck labels the before/after chart as a projection. On 22 synthetic scenarios the evidence ranker matched the designed call 22 times, a note-only ranker matched 3, and four drift cases also cleared a lot.
