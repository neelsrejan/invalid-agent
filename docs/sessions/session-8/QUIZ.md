# Session 8 quiz

1. What did the evidence ranker score on the 22 scenarios, and what did the keyword ranker score?
2. Why is `weak_lot` a success when the evidence call is `no_single_cause`?
3. What extra call showed up on the drift scenarios, and did it change top-1?
4. Why does the report not claim a Llama 3.1 8B versus Llama 3.2 1B accuracy?
5. Why is the red-herring key written `"true"` with quotes?

## Answers

1. Evidence top-1 and top-3 were 22/22. Keyword top-1 was 3/22. The three keyword hits are the flat scenarios, whose week-0 note names no cause. Holdout was 4 of 22. Gates were not refit.
2. The lot bump was built to stay under the lift gate. The correct call is to withhold. The keyword ranker repeats the note and says `bad_reagent_lot`.
3. A reagent-lot stratum also cleared the bar on the drift files. Top-1 stayed `drifting_instrument`. The report lists that second stratum on purpose.
4. Neither model was installed for this run. The table compares two ranking policies. A model draft would still have to pass the numeric-fidelity check before it was shown.
5. PyYAML treats an unquoted `true` as a boolean. The generator looks up the string key `"true"`.
