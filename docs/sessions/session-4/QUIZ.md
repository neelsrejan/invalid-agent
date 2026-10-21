# Session 4 quiz

1. Why is Measurement on the fishbone if the ranker has no measurement cause?
2. What does `validate_whys` reject, and when does it run?
3. On `bad_lot` at week 0, can the 5 Whys cite the QA note about lot L-4419? Why?
4. What is the effectiveness metric in D6, and why does the record not claim the rate has already recovered?
5. Where do DMAIC labels sit relative to the eight Ds?

## Answers

1. The 6M set is the diagram a quality reviewer expects. An empty bone with score zero is honest. Dropping the bone would look like the category was never considered.
2. An empty citation list, or a citation id that is not in the catalog. It runs inside `build_whys`, before markdown is rendered.
3. No. `index_injections` keeps only injections whose week is less than or equal to the case week. The QA note is week 1.
4. Return to the spec and no rule-1 point on the weekly p-chart. Follow-up runs do not exist yet, so D6 says any before/after figure would be a projection.
5. Define is D1–D2, Measure is the metrics, Analyze is D4 plus the fishbone and 5 Whys, Improve is D3 and D5, Control is D6 and D7. D8 is closure, not a DMAIC phase.
