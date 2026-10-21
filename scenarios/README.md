# Scenarios

Each YAML file is one simulated investigation.

- `seed` makes the field file repeatable.
- `root_cause.type` is the ground truth the eval harness scores against.
- `injections` are the weekly stakeholder messages. The Week-0 graph does not need them; Session 6 reads them.
- Rates, intervals, and control limits are computed from the generated rows. The YAML holds the *process* that creates the rows, not the answer numbers.

`bad_lot.yaml` is the walkthrough case: lot L-4419, fictional molecular panel, promised validity ≥ 98%.

The other files are the eval set: six cause types at more than one severity, three flat `no_single_cause` files, three red herrings, and `weak_lot` (a lot bump that stays under the evidence bar). `eval.expect_cause` is the call the harness scores. The ranker does not read it. Four files set `eval.holdout: true`.
