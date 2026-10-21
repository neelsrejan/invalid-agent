# Session 5 logic trace

Snapshot id: git tag `session-5`. Resolve the commit with `git rev-parse session-5^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 5\`. The tag is the snapshot.

## 1. Goal

A 4-week investigation plan (owners, dependencies, dates) drawn as a Gantt, a likelihood × impact risk register, and a Jira epic plus stories. With no token the sync writes `jira_issues.json` and does not open a socket. Week 2 adds the lab-director task and moves a risk's trend, which is the diff a PM would show in a re-plan.

## 2. What had to be true before Session 6

The plan and the register are functions of `(scenario, top hypothesis, week)`. Session 6 can call them again after each injection and append a decision-log row. It should not invent a second scheduler. The graph order is now triage → plan → rca. Status updates are the missing node.

## 3. Why these libraries

- **plotly** draws the interactive HTML Gantt (`px.timeline`). A reviewer can open the file and hover owners.
- **matplotlib** draws the PNG. Kaleido is the plotly path to PNG and it needs a browser. CI and a 32 GB laptop without that extra download still need a picture for the deck, so `_write_png` does not call `write_image`.
- **httpx** is the live Jira transport, imported only inside `HttpxTransport.request`. Tests pass a fake transport and never construct it for the dry-run.

## 4. Code, and why it is shaped this way

`nodes/planner.py`

- `investigation_start` (line 34) is the day after the field window, unless the YAML sets `investigation_start`. The Gantt is anchored there so it does not float on "today".
- `_task` (line 41) stores an exclusive end (`start + days`). The dependency rule is "start >= predecessor end", which is the same instant the predecessor finishes, not the day before.
- `build_plan` (line 62) lays down T1–T10 inside 28 days. T11 (lab director) appears only when `week >= 2`. T12 (lane temperature) appears only when `week >= 3`. Those are the injection-driven adds. The baseline tasks are not deleted, because a re-plan that throws away the fishbone review is not a re-plan.
- The containment owner comes from `_OWNER`. A lot is QA. An instrument or a temperature lane is Manufacturing. Software is R&D. No single cause stays with the PM, which is the "do not quarantine yet" owner.
- `_assert_dependencies` (line 116) raises if a start is earlier than a predecessor end. The test repeats the check so a hand-edited date cannot sneak through.
- `build_risks` (line 146) scores `likelihood * impact` and raises if that product is wrong. R1 opens at trend `new` and, once a real cause is in hand at week 2, drops to likelihood 2 and trend `down`. R4 (release data versus field data) appears at week 2 with trend `up`. R5 and R6 wait for week 3, which is when manufacturing and leadership speak in the scenario.
- `plan_node` (line 223) writes the HTML, the PNG, `risk_register.md`, `plan.json`, and calls `make_client(...).sync(plan)`.

`artifacts/gantt.py`

- `write_gantt` (line 47) builds the plotly figure and then `_write_png` (line 66). The PNG y-axis is reversed to match the HTML (first task at the top). Colors are a fixed owner map, not a random palette.

`integrations/jira.py`

- `make_client` (line 114) returns `DryRunJira` unless all three Jira settings are present. That is the same gate as `settings.jira_enabled`.
- `DryRunJira.sync` mints `SIM-*` keys so a dry-run file cannot be mistaken for the build backlog in `docs/jira/backlog.json`.
- `_upsert` (line 149) is shared. If `task_id` is already in the file, the story is updated in place and `creator` is not called. That is the idempotent part. The live test counts POST `/rest/api/3/issue` calls: 11 the first time (epic + 10 tasks), 0 the second time.
- `LiveJira.sync` catches transport failures, stores the exception class name, and still writes the JSON. The token is not interpolated into the error or into `__repr__`.
- Descriptions use Jira's Atlassian document format (`_adf`, line 23) because API v3 rejects a plain string.

`graph.py` `build_graph` (line 20) inserts `plan` between triage and rca. `run_case` (line 61) creates the output directory before `invoke`, because the plan node writes files during the node, using `state["out_dir"]`.

## 5. What was documented, and why

The risk markdown states the scoring rule in the header so a reader does not have to reverse it from the column. The Jira JSON carries `"disclaimer": "Simulation. Not a live customer escalation."` The Gantt title says the same. Dry-run keys are `SIM-*` on purpose.

## 6. Stakeholder / Jira buy-in before Session 6

Ticket **INV-207** (injections update the plan and the decision log) and **INV-208** (RAG notes per audience), epic **INV-4**. The plan function already takes `week`. Session 6 has to record *why* the plan changed. Neel still does not need a token. If he creates a Free site later, the three env vars switch `make_client` to `LiveJira` without a code change.

## 7. Approval → capability added

Tests cover dependency order, the week-2 task diff, the R1 trend change, R4 appearing, PNG magic bytes, dry-run idempotency, live POST counts against a fake transport, a hidden token, and a recorded live failure. `pytest` stays offline.

## 8. What a hiring manager can see

A Gantt with functional owners and a risk register whose score is a product. Jira is there, and the demo does not depend on Neel's site existing. That is the planning / risk / Jira cluster from the JD research, with the integration optional.

## Line-by-line walkthrough

Check out `session-5`.

1. `graph.py` `build_graph` (line 20). Three nodes. Edges: triage → plan → rca → END. Plan runs after triage because it reads `state["hypotheses"]`. It does not read the fishbone. RCA does not read the plan. The order matches "plan from the intake, then the quality record".
2. `run_case` (line 61) makes the directory, then `initial_state(..., destination)` stores `out_dir` on the state so the node and the CLI agree on one folder.
3. `plan_node` (line 223). It takes `hypotheses[0]` or a no-single-cause placeholder. Then `build_plan`, `build_risks`, four files, then Jira.
4. `build_plan` (line 62). Pick the owner from `_OWNER`. Build T1 at `start` for 3 days, so its end is `start+3`. T2 starts at that end. Walk one dependency in the test rather than trusting the comment: T8 starts at day 18 and depends on T6, and T6 ends at day 18.
5. The `if week >= 2` block appends T11. Week 0's id set does not contain it. That is the Gantt diff.
6. `_assert_dependencies` (line 116) is a string comparison of ISO dates, which sorts correctly for `YYYY-MM-DD`.
7. `build_risks` (line 146). `misread_l` is 3 until week 2, then 2 if a cause exists. `misread_trend` follows the same cut. R4's trend is the literal `"up"`. The loop at the bottom recomputes nothing; it checks the product so a future edit cannot set `score` by hand and drift.
8. `write_gantt` (line 47 in `gantt.py`). `px.timeline` needs datetime columns; `_frame` parses the ISO strings. `update_yaxes(autorange="reversed")` puts T1 at the top. `include_plotlyjs="cdn"` keeps the HTML small. `_write_png` does not import kaleido. It draws one `barh` per task. `max(end - start, 0.4)` stops a zero-width bar if a task is ever shorter than a day.
9. `make_client` (jira.py line 114). False `jira_enabled` returns `DryRunJira` and does not evaluate `HttpxTransport`.
10. `_upsert` (line 149). Epic is created once. The `by_task` map skips creator when the id exists, and still refreshes summary, status, and owner. The file is rewritten at the end, so a crash before `_write` leaves the previous file, which is the last good sync.
11. `LiveJira.__repr__` prints project and email only. The test sets the token to `super-secret-token` and asserts it is absent from `repr`.

## Quiz

See `QUIZ.md`.
