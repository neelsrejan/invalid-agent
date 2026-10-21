# Session 4 logic trace

Snapshot id: git tag `session-4`. Resolve the commit with `git rev-parse session-4^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 4\`. The tag is the snapshot.

## 1. Goal

Turn the ranked hypothesis into a quality-system record: a 6M fishbone with evidence for and against each branch, a 5 Whys on the top branch where every step cites a data fact or an injection, and an 8D/CAPA (D1–D8) labeled with DMAIC. On `bad_lot`, Material ranks first and the chain ends on lot L-4419. A Why with no citation is an error, not a warning.

## 2. What had to be true before Session 5

The case state now carries `fishbone`, `five_whys`, and `capa`. Session 5's planner can read the top cause and write tasks against it (quarantine a lot versus service an instrument) without re-deriving the rank. The graph is still linear: triage → rca → END. The Gantt and Jira sync are not in this tag.

## 3. Why these libraries

No new package. Pydantic checks the branch and the Why step before markdown is written. The fidelity guard from Session 3 is reused on the three markdown files, with the evidence-catalog sentences treated as known text so a rate is not retyped by hand in a second format.

## 4. Code, and why it is shaped this way

`nodes/rca.py`

- `_BRANCH_SPECS` lists the 6M branches. Material appears twice (lot and hemolysis) because both are material failures and they are different actions. Measurement is an explicit empty branch so the diagram is not missing a bone just because the ranker has no "measurement" column.
- `index_injections` (line 68) adds only injections with `week <=` the case week. At week 0 the QA lot note is invisible. At week 1 it becomes citable. The id is `injection:{week}:{source}`.
- `validate_whys` (line 85) is the rule the test plants a failure against. Empty `citations` raises. An id missing from the catalog raises. `build_whys` calls it before the markdown exists, so a broken chain never becomes a file.
- `build_fishbone` (line 104) copies a hit's evidence ids into `evidence_for` and asks `_against` (line 140) for a contrary citation. For the lot, a "passed release" injection is the contrary evidence once that week has arrived. For a branch that did not fire, the contrary citation is the overall rate: the panel moved, and this branch did not explain it. Branches sort by score. Rank 1 on `bad_lot` is Material / `bad_reagent_lot`.
- `_whys_for_hit` (line 182) builds five steps. Step 1 is overall versus spec. Step 2 is the winning stratum's catalog sentence. Step 3 cites a different column (`_contrast_id`, line 228) so the chain has to say why the next stratum is not the cause. Step 4 cites an injection that names the level, or the stratum's `n` sentence when no injection has arrived. Step 5 stops. For a lot, the stop sentence is required to say `lot-level` and it includes the catalog sentence that names L-4419.
- `_whys_unresolved` (line 237) is the chain when the ranker returned `no_single_cause`. It still has five cited steps. It does not invent a lot to satisfy the bad-lot test.
- `build_capa` (line 283) maps the top cause to a containment and a corrective action in words. D6 names the effectiveness metric (back to spec, no rule-1 point) and says a before/after number is a projection until follow-up exists. D7 and D8 are written and marked preliminary. `dmaic` maps Define through Control onto those D fields.
- `rca_node` (line 391) regenerates the frame only if triage did not already put hypotheses on the state. It extends the catalog with injections, builds the three objects, renders markdown, validates the Pydantic models, and runs `check_narrative`. A fidelity failure raises. The rejected text is not returned.

`graph.py` `build_graph` (line 19) is now triage → rca → END. `run_case` (line 55) accepts weeks 0–4 and writes `week0_triage.md`, `fishbone.md`, `five_whys.md`, and `capa8d.md`. Weeks above 0 do not yet re-plan; they only change which injections the RCA can cite. That split is deliberate: Session 5 owns the plan.

## 5. What was documented, and why

The three markdown files repeat the simulation banner. The CAPA says D7 and D8 are planned, so a reader does not think the investigation is already closed. DMAIC labels are in the file because a quality hiring manager looks for that mapping, not for the word "agent".

## 6. Stakeholder / Jira buy-in before Session 5

Ticket **INV-204** (Gantt) and **INV-205** (risk register), epic **INV-3**, plus **INV-206** (Jira dry-run). The containment sentence in D3 is what the first plan tasks have to match. No token yet. The dry-run is the path that must work with an empty environment.

## 7. Approval → capability added

`tests/test_rca.py` rejects an empty citation and an unknown id, asserts Material is rank 1, asserts the fifth Why names L-4419 and says lot-level, and checks D1 through D8 in the markdown. The week-0 command still writes the memo and now also writes the RCA files.

## 8. What a hiring manager can see

A structured problem-solving record: fishbone, 5 Whys with citations, 8D, DMAIC. The cause is the lot the data named, and the chain is not allowed to skip the citation. That is the RCA / CAPA signal in the quality and med-device JDs, labeled as a simulation.

## Line-by-line walkthrough

Check out `session-4`.

1. Open `graph.py` `build_graph` (line 19). Two nodes. The edge list is the whole control flow: triage, then rca, then END.
2. `run_case` (line 55) still starts from `initial_state`. `invoke` runs both nodes. After it returns, four files are written. `fishbone.md` is `result["fishbone"]["markdown"]`, not a second rendering.
3. Open `nodes/rca.py` `rca_node` (line 391). `week = state["week"]`. Hypotheses are reused from triage when present, otherwise `rank_hypotheses` runs on a fresh `generate`.
4. `index_injections` (line 68) loops the YAML list. The comparison `int(inj["week"]) > week` drops the future. The key is stable for a source, and a second note from the same source in the same week gets a numeric suffix.
5. `catalog.update(injections)` is what makes an injection a legal citation. Before that line, `validate_whys` would reject it.
6. `build_fishbone` (line 104). For each spec row, look up the cause in `_by_cause`. `_by_cause` (line 100) drops `no_single_cause`, because that is a call, not a bone. A miss gets score 0 and the statement "This branch did not clear the evidence bar." A hit uses the catalog rate sentence as the statement so the number on the page is the same sentence Session 2 computed.
7. Sort key `(-score, category, cause)`. On `bad_lot` the lot score is the only non-zero score, so Material / bad_reagent_lot is rank 1. Hemolysis is also Material and stays at 0, under it.
8. `_against` (line 140). Read the release-test branch first: it only attaches to `bad_reagent_lot`, and only when an injection contains "passed release". Otherwise a live hit cites the customer injection, which does not name the lot. A dead branch cites `metric:overall:rate`.
9. `build_whys` (line 165) takes `hypotheses[0]`. If that cause is `no_single_cause`, it does not look at a later contender and pretend. Otherwise `_whys_for_hit`.
10. Inside `_whys_for_hit` (line 182), `rate_id` is `metric:{column}:{level}:rate`. Step 5's answer starts with "Stop at a lot-level cause." only when the cause is `bad_reagent_lot`. Other causes say "Stop at {cause} {level}." The catalog sentence is appended so the rate stays a quoted fact.
11. `validate_whys` (line 85) runs before return. Walk the test `test_why_without_a_citation_is_rejected`: citations `[]` hits the first branch and raises `why 1 has no citation`.
12. `build_capa` (line 283) picks containment from `_CONTAINMENT` by cause. D2 pastes the overall rate sentence and the spec sentence. D6 uses the words "rule-1" so the digit is glued to a hyphen and the fidelity scanner does not treat it as a free number. The `preliminary_close` flag is what the markdown uses to print that D7 and D8 are not done.
13. Back in `rca_node`, the combined markdown is checked with facts `{catalog, structure: 0..8, week}`. Catalog sentences are strings, so wherever the markdown pastes one verbatim, the scanner masks it. A digit that is not inside one of those sentences and not in 0..8 fails the run.

## Quiz

See `QUIZ.md`.
