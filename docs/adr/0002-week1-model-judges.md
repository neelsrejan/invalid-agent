# ADR 0002: The Week 1 model judges, and Python guards the names and numbers

## Status

Accepted.

## Context

Week 1 used to require the words "over 1" and an exact official company name. A correct sentence that said "abbott" failed that gate. A model that sees the company table can recognize the claim. The same model can also mark a wrong set as meeting the goal, or agree in prose while Next stays locked.

## Decision

- Python computes the company table and the flagged set: over 1% and at least 100 reports.
- One Groq call writes the reply and `meets_goal`. Temperature is 0. Each call times out after 15 seconds.
- Python keeps `meets_goal` only when the user's message names every flagged company. An extra company blocks Next only when that company's clause claims it is over 1% or flagged. A clause that says under, below, not, less than, fine, or ok does not. There is no required phrase.
- A percent or a large N-of-M pair that is not on the table is replaced by a Python sentence. When the name check overrides a true `meets_goal`, the page shows one neutral line and does not name the gap. It does not show the model's agreeing prose.
- Weeks 2-4 still grade with `goal_statement`.

## Consequences

- Next can open on a paraphrase that never says "over 1".
- A model cannot unlock Next by agreeing with a company the user claimed is over the line when that company is not flagged.
- The call chain is `docs/ui/LOGIC_TRACE.md`.
