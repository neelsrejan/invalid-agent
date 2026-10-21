# Session 3 quiz

1. What does the triage node store on the graph state instead of the 14,400-row frame, and how does a later node get the rows back?
2. Why does the bad-lot memo list one hypothesis rather than six?
3. Walk a planted sentence "the invalid rate is 27.40%" through `check_narrative`. Where does it die?
4. What happens if Ollama is selected and the process cannot reach it?
5. Why does `rank_hypotheses` ignore stakeholder injections?

## Answers

1. It stores metrics, hypotheses, the evidence catalog, the memo schema, the markdown, and the fidelity record. Any later node calls `generate(scenario)` again. The seed makes that the same frame.
2. The other strata do not clear min n, lift 1.8, excess 15, and chi-square p < 0.01. They stay in the strata list and stay off the hypothesis list.
3. `27.40` is not part of an identifier string in the facts, so masking leaves it. It is more than 0.03 away from every walked number, so it is appended to `unknown` and `ok` is false.
4. `narrate` catches the exception, sets `rewritten` true, and returns the template. The memo a person reads does not contain the failed draft.
5. A cause has to come from the table. Injections are text. Session 6 will show them to the status writer. They do not get a vote in the ranking.
