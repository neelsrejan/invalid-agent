# Session 5 quiz

1. Why is the PNG not `fig.write_image`?
2. What is the dependency rule, and why is an ISO date string comparison safe here?
3. What changes on the Gantt between week 0 and week 2, and what changes on the risk register?
4. Why are dry-run keys `SIM-*`?
5. What happens if the live Jira call raises?

## Answers

1. `write_image` needs kaleido. The matplotlib path runs in CI and on a laptop that has not installed it.
2. A task's start must be greater than or equal to the predecessor's end. The dates are `YYYY-MM-DD`, so lexicographic order matches calendar order.
3. Week 2 adds T11, the lab-director note. R1's trend goes from `new` to `down` and its likelihood drops. R4 appears with trend `up` because release testing and the field rate now disagree.
4. The build backlog in `docs/jira/backlog.json` uses `INV-*`. The investigation mirror uses `SIM-*` so a dry-run file is obviously not that board.
5. `LiveJira.sync` catches it, stores the exception class name, writes the JSON, and does not raise. The token is not put in the error string.
