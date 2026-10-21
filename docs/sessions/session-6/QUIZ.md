# Session 6 quiz

1. Why does triage not run on every lap of the loop?
2. What makes week 2 Amber or Red on bad_lot, and why does the case never go Green?
3. What is stored in the decision log at week 2, in one sentence?
4. How can the customer note mention a rate without the template doing arithmetic?
5. Where do you look to diff week 0 and week 2 without re-running anything?

## Answers

1. The field file is fixed by the scenario seed. Re-running triage would recompute the same metrics. The lap re-enters at `plan`, where the week changes which injections and tasks are in scope.
2. Week 2 is Red because the rate is over spec and week 3 is the containment week. It never goes Green because the synthetic file is not rewritten to a cured process. Amber means containment is underway, not that the rate recovered.
3. Keep the field ranking after release testing was reported as a pass, and add the lab-director note to the plan.
4. `build_status_facts` rounds the computed rate onto `rate_pct`. The template interpolates that field. The guard then checks the sentence against those facts.
5. `out/week0/` and `out/week2/`. Compare `plan.json` and `risk_register.md`.
