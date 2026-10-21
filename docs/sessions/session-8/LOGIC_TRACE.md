# Session 8 logic trace

Snapshot id: git tag `session-8`. Resolve the commit with `git rev-parse session-8^{}`.

Laptop copy: check out the tag into `C:\Users\neels\Grok_Bot\Project_Agent\Session 8\`. This workspace has no Windows path, so the tag is the snapshot.

## 1. Goal

An offline scorecard. Twenty-two seeded scenarios, a known call in each YAML, and a report that compares the evidence ranker with a ranker that only reads the week-0 notes. The report records top-1, top-3, numeric fidelity, citation validity, escalation, and latency, plus the cases that mislead.

## 2. What had to be true before Session 9

The report file exists and its counts come from a run of `evals/run_eval.py`, not from a sentence typed into the README. Session 9 copies those counts into the résumé bullets and does not invent a model-accuracy number.

## 3. Why these libraries

No new package. Ranking reuses `rank_hypotheses` and `generate`. The week-0 graph check reuses `run_case`. CI calls the same script with `--limit 5 --smoke`.

The model comparison the plan named as 7B versus 1.5B is now Llama 3.1 8B (`llama3.1:8b`) versus Llama 3.2 1B (`llama3.2:1b`). Neither weight is installed in this environment, so the report compares two policies on the deterministic backend and says the models were not called. Gemma 3 and Phi-4 stay documented as other `LLM_MODEL` tags. They were not scored either.

## 4. Code, and why it is shaped this way

`scenarios/` holds the files. Six cause types appear at more than one severity or baseline. Three files are `no_single_cause`. Three are red herrings (`root_cause.type: red_herring`, with the real cause under the quoted key `"true"`, because unquoted `true` is a boolean in YAML 1.1). `weak_lot` raises lot L-4419 only to 0.04 against a 0.025 baseline, which stays under the lift gate, while the overall rate is still over the 2% spec. Four files set `eval.holdout: true` (bad_lot_noisy, drift_late, temp_mild, flat_border).

`evals/run_eval.py`

- `keyword_cause` scans week-0 injection text for the first word in a fixed list. It never opens the table.
- `score_scenario` generates the frame and calls `rank_hypotheses`. Top-1 is the cause at index 0. Top-3 is membership in the first three causes. `eval.expect_cause` is the label. The ranker does not receive that block.
- `run_graph_checks` runs week 0 and reads fidelity, 5 Whys citations, and whether `escalate` equals `exceeds_spec` on the memo. Mean latency on this run was 0.55s.
- The report writer prints n, both splits, every row, keyword misses, extra strata, and the below-bar case.

`nodes/rca.py` now puts hypothesis levels and software version ids into the fidelity facts as strings. The terminal Why for a software hit says `2.4.0`. That token was being scanned as the number 2.4, because the guard only strips an identifier when the exact string is in the facts. Lot ids were already safe behind a hyphen. The version id needed the same treatment. The guard's thresholds did not change.

## 5. What was documented, and why

`evals/reports/2026-10-20.md` is the run. Evidence top-1 was 22/22 on this constructed set, including the three herrings and the weak lot. Keyword top-1 was 3/22. The three keyword hits are the flat files, where the week-0 note names no cause. On the herrings and on `weak_lot` the keyword ranker repeats the note and the evidence ranker does not. Four drift files also cleared a lot stratum; top-1 stayed on the instrument. That second stratum is the failure note a résumé bullet has to keep.

CI runs five scenarios through the same script and fails if evidence top-1, fidelity, citations, or escalation miss.

## 6. Stakeholder / Jira buy-in before Session 9

Ticket **INV-302**, epic **INV-7**: the eval. Neel should read the weak-lot row and the drift extra-stratum rows before he quotes 22/22. No Jira token. The Llama weights are optional and were not required for this tag.

## 7. Approval → capability added

`tests/test_eval.py` checks every scenario's expected call, the software herring, and the weak lot. `tests/test_rca.py` checks that `2.4.0` survives the fidelity guard. `pytest` does not download a model.

## 8. What a hiring manager can see

A scorecard with n, a holdout split, and the cases the naive reading gets wrong. The 22/22 figure is the designed call on synthetic files with fixed gates. It is not a clinical accuracy claim, and it is not a Llama-versus-Llama result.

## Line-by-line walkthrough

Check out `session-8` first.

1. Open `evals/run_eval.py`. `_KEYWORDS` is the naive policy. `software` is before `lot` so a sentence that says both still has one call.
2. `score_scenario` generates, ranks, and compares to `eval.expect_cause`.
3. `render_report` writes the three split rows, then the failure notes. A clean top-1 list is still followed by keyword misses and extra strata.
4. `_model_section` names `llama3.1:8b` and `llama3.2:1b` and states when the probe did not run.
5. Open `evals/reports/2026-10-20.md` and read the weak_lot row and the drift extra-stratum lines before reading the 22/22 cell.
6. Open `scenarios/herring_software.yaml`. The week-0 note says software. `root_cause.true` is the lot. The quoted `"true"` key is required.
7. Open `src/invalid_agent/nodes/rca.py` at the facts dict. `labels` includes `2.4.0` so the Why can name the version.

## Quiz

See `QUIZ.md`.
