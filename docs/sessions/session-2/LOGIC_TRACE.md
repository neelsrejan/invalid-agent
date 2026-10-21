# Session 2 logic trace

Snapshot id: git tag `session-2`. Resolve the commit with `git rev-parse session-2^{}`.

Laptop folder `C:\Users\neels\Grok_Bot\Project_Agent\Session 2\` is not created here (no Windows path in this workspace). Check out the tag and copy the tree, excluding `.git/`, venvs, `out/`, and `.env`.

## 1. Goal

A 6-month synthetic field file with a known injected root cause, plus the calculations a PM would otherwise do in a spreadsheet: invalid rate, Wilson 95% interval, stratified rates, chi-square, a p-chart with Western Electric rules, and a Pareto of invalid codes. The demo command prints that summary. The LLM is not involved.

## 2. What had to be true before Session 3

The triage memo needs a stable row schema and a metrics dict it can quote without recomputing a different way. Session 3 will call `generate`, `overall_rate`, `stratified_rates`, `p_chart`, and `pareto`. It will not reimplement them.

## 3. Why these libraries

- **numpy** supplies the seeded generator (`default_rng`) so a scenario is a file, not a mood. The same YAML produces the same CSV.
- **pandas** is the frame the strata, the weekly grouper, and the Pareto `value_counts` run on.
- **scipy.stats** supplies `norm.ppf` for the Wilson z and `chi2_contingency` for the stratum test. The interval itself is written out in `rates.py` so a reviewer can check it by hand. statsmodels is not used; the plan listed it as optional.
- **PyYAML** loads the scenario. The cause, the lot calendar, and the injections live in data, not in a Python branch the eval cannot see.

## 4. Code, and why it is shaped this way

`src/invalid_agent/sim/seeds.py`

- `INVALID_CODES` and `BASE_CODE_WEIGHTS` are the Pareto vocabulary. Baseline invalids are a mix. A cause may push one code (INV-IC for a bad lot, INV-TMP for heat, INV-HEM for hemolysis, INV-SW for software or a drifting instrument, INV-USR for an operator).
- `HEMOLYSIS_BASELINE` / `HEMOLYSIS_SEVERE` are lognormal stand-ins for the published right-skewed HIL index (DOI 10.17632/vxkkdmw55f.1). They are not a fit to that file. `sample_hemolysis` (line 60) is the only place those parameters are used.
- `COMPLAINT_THEMES` are FDA product-problem labels. `openfda.py` can optionally ask the API for a count. `generate` does not call it. `fetch_event_count` (openfda.py line 27) swallows network errors and returns None.

`src/invalid_agent/sim/generate.py`

- `load_scenario` (line 36) is YAML in, dict out.
- `_levels` (line 44) accepts either `"SITE-A"` or `{id, start_day, end_day, weight}`. A calendar is how a lot "enters distribution" without a special case in the sampler.
- `_assign` (line 63) draws a level for each day from the levels active that day. Site, instrument, lot, software, and operator each get their own draw, so they are not the same column renamed. The module docstring states the reference-lab assumption that makes a lot effect separable from an instrument effect.
- `_redraw` (line 75) replaces the invalid flag on a mask. Baseline is a redraw of every row at `baseline_invalid_rate`. The cause then redraws only its mask, so the complement stays at baseline instead of stacking two probabilities.
- `_cause` (line 97) is the ground-truth injection. `bad_reagent_lot` masks on lot id and start day. `drifting_instrument` ramps the probability from baseline to `peak_invalid_rate`. `site_temperature` heats a fraction of one site's rows and invalidates those rows, not the whole site, so the temperature band is the signal. `preanalytical_hemolysis` redraws that site's index from the severe lognormal and invalidates rows at or above the cutoff. `no_single_cause` redraws every row at one global rate. `red_herring` applies `root_cause.true` and leaves the misleading text in the YAML for the eval to abuse.
- `generate` (line 165) builds 180 × 80 = 14,400 rows from day 0, then baseline, then cause. `df.attrs["scenario_id"]` records which file it was.
- `summarize` (line 207) is the demo print. It formats numbers from `overall_rate`, `stratified_rates`, `p_chart`, and `pareto`. It does not compute a second rate of its own.

`src/invalid_agent/metrics/rates.py`

- `wilson_interval` (line 20) is the formula in the module docstring. The last lines snap a ~1e-18 residue to 0 when k = 0, because the analytic lower bound is 0 and float subtraction is not.
- `overall_rate` (line 42) returns both `exceeds_spec` (point estimate above 2%) and `ci_entirely_above_spec` (interval clears 2%). The memo in Session 3 needs both.
- `chi_square_by` (line 85) returns p = 1 on a one-row table instead of throwing. A quiet scenario is not an exception.

`src/invalid_agent/metrics/spc.py`

- `control_limits` (line 26) is `p_bar ± 3 * sqrt(p_bar(1-p_bar)/n)`, floored at 0 and capped at 1.
- `western_electric` (line 35) implements the four zone rules on z-scores, in time order.
- `p_chart` (line 80) groups by week ending Sunday, pools `p_bar` across weeks, and attaches each violation to a period label.

`src/invalid_agent/metrics/pareto.py` sorts invalid codes by count and closes `cumulative_share` at 1. Valid rows (empty code) are excluded.

`scenarios/bad_lot.yaml` is the walkthrough. Lot L-4419 starts on day 120 at a stratum rate of 0.18. Both software versions run the whole horizon so a version cutover is not mistaken for the lot. On seed 4419 the file is 3.67% invalid (Wilson 3.38–3.99%) against a 2% spec, and L-4419 is about 17% against about 1–1.7% on the other lots. Those figures are outputs, not inputs. Re-running the command is the check.

## 5. What was documented, and why

- `scenarios/README.md` tells a reviewer that the YAML is the process, not the answer key of rates.
- `DATA_LICENSES.md` (Session 1) already says the HIL file is not vendored. `seeds.py` repeats the DOI next to the parameters so the number and the citation stay together.
- The README at this tag gains the generate command.

## 6. Stakeholder / Jira buy-in before Session 3

Ticket **INV-108** (Week-0 memo) and **INV-109** (fidelity guard), epic **INV-1**. The data contract they inherit is the column list in `generate` (run_id, date, day_index, customer, site, instrument, reagent_lot, software_version, operator, hemolysis_index, shipping_temp_c, invalid, invalid_code) and the dict from `overall_rate`. No Jira token.

## 7. Approval → capability added

`python -m invalid_agent.sim.generate scenarios/bad_lot.yaml` prints a summary that exceeds spec, names L-4419, and lists Western Electric hits. Unit tests lock the Wilson formula, the 3-sigma limit, three of the zone rules, and a planted out-of-control week.

## 8. What a hiring manager can see

A PM who can say where a rate came from. The spec comparison, the interval, the strata, and the control chart are code. Nothing in this session asks a model to do arithmetic.

## Line-by-line walkthrough

Check out `session-2` before using these line numbers.

1. Open `scenarios/bad_lot.yaml`. Read `root_cause`. The lot id, the start day, and the stratum rate are the only knobs. The 3.67% in a printout is not in this file.
2. Open `generate.py` at `generate` (line 165). `n = horizon * per_day`. `default_rng(seed)` is the entire source of randomness.
3. `day_index` repeats 0, then 1, then 2, `runs_per_day` times. `dates` adds that to `start_date`.
4. `_assign` (line 63) loops over unique days. For each day it keeps levels whose window contains the day, renormalizes weights, and draws. Because each category consumes its own draws, changing a software weight does not reshuffle the lot column's subsequent invalid draws only if the number of `choice` calls stays the same. It does. That is why the lot rate survived the software-weight edit during this session.
5. The DataFrame constructor fills shipping temperature from `NOMINAL_SHIPPING_TEMP_C` and hemolysis from the baseline lognormal. `invalid` starts false, then `_redraw` on a mask of all True applies the 1.2% baseline.
6. `_cause` for `bad_reagent_lot` (the branch around the lot mask) builds `mask = lot equals L-4419 AND day_index >= 120`, then `_redraw` at 0.18 with dominant code INV-IC. Rows outside the mask keep the baseline flag. That is the contrast the chi-square test sees.
7. `_redraw` (line 75) draws `rng.random(n) < probability`, writes the flag, and fills codes only on the True positions via `sample_codes`. Valid rows get an empty code so the Pareto cannot count them.
8. Open `rates.py` `wilson_interval`. For k=10, n=100 the test recomputes the same algebra in the test file, not by calling this function, and also checks the published rounding 5.5% to 17.4%. The snap-to-zero at the bottom is for k=0.
9. Open `spc.py` `control_limits`. For p_bar=0.02 and n=100, SE = sqrt(0.02 × 0.98 / 100) = 0.014, UCL = 0.062, LCL floors at 0 because 0.02 − 0.042 is negative.
10. `western_electric`: rule 1 is `abs(z) > 3` at that index. Rule 2 looks at a window of 3 ending at i. Rule 4 looks at a window of 8 and requires every z on one side of 0, strict, so a point sitting on the center line breaks the run.
11. `p_chart` groups with `pd.Grouper(freq="W-SUN")`, skips empty weeks, then one loop writes z and a second call to `western_electric` attaches the period string onto each hit.
12. `summarize` only formats. If a number in that printout is wrong, the bug is in metrics or in the generator, not in a sentence.

## Quiz

See `QUIZ.md`.
