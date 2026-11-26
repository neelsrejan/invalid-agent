# ADR 0003: Weeks 2, 3, and 4 use the Week 1 judge

## Status

Accepted.

## Context

Week 1 judges a reply with one Groq call and a Python guard. Weeks 2, 3, and 4 still required an exact phrase and then wrapped the reply in YEP. ADR 0002 left that split in place. A correct paraphrase of a later week failed the phrase gate, and a wrong set could not be separated from the model's agreeing prose.

## Decision

- Weeks 2, 3, and 4 use the design in `docs/WEEK_DESIGN.md`.
- Week 2 guards the cause-set codes. On the JJE fixture those sets are Roche `INV-MECH` and `INV-NOR`, Siemens `INV-MECH` and `INV-USR`, and Abbott Labs `INV-MECH`, with `INV-SW` accepted because it is tied at the same count.
- Week 3's rubric asks for the simulated note, the ticket, and the fishbone branch. The guard checks the company and the code of each issue.
- Week 4's rubric asks for the root cause, the corrective action, and the public statement. The guard checks the flagged companies.
- The old phrase grader is gone. The synthetic practice screens still use their own grader.

## Consequences

- Next on weeks 2, 3, and 4 opens on a paraphrase that names the right entities.
- A model cannot unlock Next by agreeing with an entity the user did not name.
- Week 1 is unchanged.
