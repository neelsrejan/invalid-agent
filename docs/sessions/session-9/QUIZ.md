# Session 9 quiz

The last two questions are the whole-system check and a two-minute pitch.

1. Why does week 4 not simply end on the status node?
2. What would be false about the deck if the projected rate were labeled as follow-up?
3. Where does the $ cost on the impact slide come from?
4. Which eval numbers are safe to put on a résumé, and which sentence has to sit next to them?
5. Explain the system in one pass, then give the two-minute pitch below out loud.

## Answers

1. Status is the weekly note. Close-out confirms D7 and D8 and writes the deck. Routing week 4 to `closeout` keeps that work inside the graph instead of a script that forgets the fidelity check.
2. The generator does not rewrite the field file. Clearing the leading stratum is a counterfactual. Calling it observed follow-up would claim a cure the data do not contain. `bad_lot` stays over spec in the observed series.
3. `k * cost_per_invalid_usd` from the scenario. For `bad_lot` that is 529 times 85. The template does not type the product.
4. Safe: evidence top-1 22/22 on this constructed set, keyword top-1 3/22, fidelity 22/22, and the four drift files where a lot also cleared the bar. Not safe: any sentence that turns 22/22 into a clinical accuracy rate, or a Llama 3.1 versus Llama 3.2 comparison. Those models were not run.
5. Pitch, about two minutes:

Invalid Bot is a simulated investigation, not a device and not a customer's file. A lab says a molecular panel missed its 98% validity promise. Each week the agent re-reads the same seeded field file, updates the plan and the risk register, and drafts three notes: customer, internal, leadership. The customer note does not declare a cause. The ranking comes from strata that clear a fixed evidence bar. Notes that name the wrong cause do not outrank the table. At week 4 the deck asks leadership to contain the leading stratum or to widen the pull, and it labels the before/after chart as a projection. On 22 synthetic scenarios the evidence ranker matched the designed call 22 times, including three red herrings and a weak lot that correctly stayed unresolved. A ranker that only read the complaint matched 3. Four drift cases also cleared a lot, and that second call stays in the write-up. I can run it here with no API key.

## Whole system, one pass

Scenario YAML fixes the seed and the injected cause. The generator draws sites, instruments, lots, software, and operators independently, then redraws invalids on the cause mask. Metrics compute the rate, the Wilson interval, the p-chart, and the Pareto. The ranker scores strata that pass minimum n, lift, excess, and a chi-square gate. LangGraph triages once, then loops plan, RCA, and status. RCA will not store a Why that lacks a catalog id. The fidelity guard strips identifiers and dates, then rejects any number that is not near a fact. Week 4 writes D7, D8, and the deck. Jira is optional and dry-run by default. The model is optional. `LLM_MODEL` defaults to `llama3.1:8b`. Hosted Streamlit runs rules-only (deterministic). `llama3.2:1b` is the suggested small tag for local or self-hosted runs.
