# Session 6 logic trace

Snapshot id: git tag `session-6`. Resolve the commit with `git rev-parse session-6^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 6\`. The tag is the snapshot.

## 1. Goal

Step one scenario from week 0 through week 3. Each week re-runs the plan and the RCA with the injections that have arrived, writes a decision-log entry, syncs Jira status, and drafts three RAG notes: customer, internal, leadership. The customer note does not declare a cause. The Gantt and the risk register differ across weeks. The notes pass the numeric-fidelity guard.

## 2. What had to be true before Session 7

The case state at the end of a run holds the latest plan, risks, decision log, and the three notes, and `out/weekN/` holds the snapshot for each week. The dashboard can read those files or call `run_case` without inventing a second loop.

## 3. Why these libraries

No new package. The new piece is a conditional edge in LangGraph. `route_after_status` returns `"advance"` or `"end"`. That is the loop. A `for` loop in the CLI would have worked and would have hidden the control flow. The edge is the control flow.

## 4. Code, and why it is shaped this way

`graph.py`

- `advance_week` (line 21) returns `week + 1` and nothing else. The decision log, the metrics, and the scenario stay on the state.
- `route_after_status` (line 26) compares `week` with `target_week`. Equal means stop, including week 0, so a one-week run does not spin.
- `build_graph` (line 34) is triage → plan → rca → status, and status either ends or advances back to plan. Triage does not run again. The field file does not change between weeks. What changes is which injections are visible and which tasks are in progress.
- `run_case` always starts at week 0 and sets `target_week` to the CLI value, with `recursion_limit` 80. Four weeks of four nodes is well under that. The limit is there so a routing bug fails fast instead of hanging.

`nodes/planner.py` around line 108 sets Jira status from `sim_week` versus the current week: earlier tasks are Done, this week's tasks are In Progress, later tasks stay To Do. The dry-run upsert from Session 5 refreshes status in place, so the file at the end of week 3 shows T1 Done and T11 Done.

`nodes/status.py`

- `rag_color` (line 20) is Red while the rate is over spec and containment week has not arrived, Amber from week 3 (containment is on the plan, effectiveness is not observed), Green only when the rate is inside spec. The field file does not shrink, so bad_lot never goes Green. That is honest.
- `_customer_action` (line 32) is words. It does not name `bad_reagent_lot` and it does not say "the root cause is".
- `_decision` (line 51) is one sentence per week. Week 2 records that release testing passed and the ranking stayed. Week 3 records that the shipping note did not take over.
- `upsert_decision` (line 74) replaces an existing row for the same week. A second pass cannot double the log.
- `build_status_facts` (line 100) is the only number source for the three notes: rounded percents, the invalid count, the unit cost from the YAML, and the product. Cost is `k * unit`, computed here, not typed into the template.
- `status_node` (line 146) calls `narrate` per audience and then `check_narrative` again. A failure raises. The three strings are what get written.
- `_write` (line 172) puts the notes and the full decision log in `out/` and in `out/weekN/`. The week folder is the diff the test reads.

`narrative.py` `status_customer`, `status_internal`, and `status_leadership` share `_status_header`, so the rate line cannot drift between audiences. Internal adds the hypothesis and pastes injection text verbatim (so the guard can mask it). Leadership adds the cost line and the ask.

## 5. What was documented, and why

Each note and the decision log repeat the simulation banner. The customer note says it does not state a confirmed cause, in the note, not only in a code comment. The decision log cites evidence ids so a reader can see that week 2's choice was "keep the field ranking", not "believe the release report".

## 6. Stakeholder / Jira buy-in before Session 7

Ticket **INV-301**, epic **INV-5**: the dashboard. It should show the week folders this session writes: the p-chart was already computed, and the memo, fishbone, Gantt, register, and notes are files. No token. Streamlit sign-in is Neel's step at deploy time, not a code step.

## 7. Approval → capability added

`tests/test_status.py` runs `--week 3`, counts four decision headings, checks T11 is absent in week 0 and present in week 2, checks R4 appears only later, checks the customer note, checks leadership is Red at week 2 and states a dollar cost, and checks Jira status moved to Done for tasks whose week has passed.

## 8. What a hiring manager can see

A weekly stakeholder loop with a decision log and three audiences. The customer does not get an unconfirmed cause stated as fact. Leadership gets the cost and an ask. The plan actually changes when the week changes. That is the stakeholder and status-report work the JD research ranked near the top.

## Line-by-line walkthrough

Check out `session-6`.

1. Start at `graph.py` `build_graph` (line 34). Read the edges in order. The conditional is the only branch. `"end"` maps to `END`. `"advance"` maps to the node that adds one to `week`.
2. `route_after_status` (line 26). For `--week 3`, `target_week` is 3. After the week-0 status node, 0 >= 3 is false, so the next node is `advance`. After the week-3 status node, 3 >= 3 is true, so the graph stops. The decision log has four rows because weeks 0, 1, 2, and 3 each called `status_node` once.
3. `advance_week` (line 21) returns a one-key dict. LangGraph merges it. `decision_log` is not in the return, so it survives.
4. Open `status.py` `status_node` (line 146). `build_status_facts` first. Cost is `invalids * unit` at the bottom of that function. Both factors and the product sit on `facts["cost"]` before any sentence is rendered.
5. The audience loop calls `narrate`. Deterministic mode returns the template plus the source footer. `check_narrative` runs on that exact string. Unknown numbers raise, so a bad template never becomes a file.
6. `_decision` (line 51) picks the sentence from `week`. It stores evidence ids from the hypothesis the ranker already produced. It does not score anything.
7. `upsert_decision` (line 74) filters out the same week, appends, sorts. The test inserts week 1 twice and week 0 once and expects order `[0, 1]` with the replaced text.
8. `_write` writes three files and `decision_log.md` into the root and the week folder. Root is "latest". The week folder is "as of that week", which is why week 0's register has no R4 and week 2's does. Those registers were written by `plan_node` on that lap, not reconstructed later.
9. Back in `planner.py` near line 108, status is a comparison of integers. At the end of a week-3 run, T1 (`sim_week` 0) is Done and T11 (`sim_week` 2) is Done. T10 (`sim_week` 4) is still To Do. The Jira file is the sync of that last plan.
10. Customer template: search the week-2 file for `bad_reagent_lot` and for `the root cause is`. Neither is there. The rate line is the shared header, so the customer sees the same 3.67% the internal note sees.

## Quiz

See `QUIZ.md`.
