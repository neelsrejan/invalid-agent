# Week design

One week of a guided audit decides whether Next unlocks. Python computes the tables. One model call judges the reader's words. A thin guard checks the named entities. The same shape ports to another project by swapping the tables, the rubric, and the entity list. Care Ops and Fit Finder are later ports. They are not implemented here.

The Invalid Bot weeks are the worked example. Week 1 already ships this design. Weeks 2, 3, and 4 use it too. Do not change Week 1 behavior.

## Judge

Each user message makes one Groq call. The model is `qwen/qwen3.8-27b`. If that call fails and a key is present, one fallback call uses `openai/gpt-oss-20b`. Temperature is 0. Each call times out after 15 seconds.

The prompt carries three things.

- The tables Python already computed for that week.
- A goal rubric that says when the week is met, and that a question is not met.
- The user text.

The model answers in its own words. It then returns one JSON object on its own line, with `meets_goal` and a short reason. Python computed every count, share, and code before the call. The model does not invent a percent or a count. A percent, or a checked N-of-M pair, that is not on the week's table replaces the reply with the Python sentence and keeps Next locked.

A missing key, a failed call, or an unparsed reply uses the same Python sentence and does not unlock Next.

## Guard

The guard runs after a parsed reply. It does not grade wording and it does not require a phrase.

Split the user text on commas, semicolons, periods, and the words and and but. A segment that names an entity starts that entity's run. Later segments stay in the run until a segment names a different entity. Read a claim and a negation only inside that run.

Negation always includes n't, no, neither, nor, and not. A week whose correct claim is "over" also treats under, below, less than, fine, ok, and okay as negation, because those words deny the over-claim. A week whose correct claim is "under" does not treat under as negation.

Each week supplies its own claim markers. On a company week the markers are the over-phrases: over, above, exceed, more than, greater than, >1, over one, too, also, and flagged. The word too does not match the phrase "too few". On a code week, a code in a non-negated segment is the claim.

A required entity whose every mention is negated counts as missing. A missing required entity keeps Next locked. An extra entity keeps Next locked only when its own run makes the week's claim and that run is not negated.

When the guard overrides a true `meets_goal`, the page shows one neutral line. The line does not name the missing or wrong entity. When `meets_goal` is false, the page shows the model's prose.

## Reply

The page shows the raw model reply. It does not add YEP, GOOD QUESTION, NOT QUITE, CLOSE, Remember, or a praise line. It does not fall through to a capabilities menu. It does not run a second wording pass.

Show me does not call the model. It logs the Python sentence for that week and unlocks Next.

Next unlocks only when `meets_goal` is still true after the guard, or the reader presses Show me.

## UI

The page does not show "What the agent is doing", why the agent does it, or what to look at. There is no case dropdown and no "things to notice" list. The case title is plain text. Each table, chart, or note block has a plain title. A short note line states the rule the table is using, such as which rows are too small to judge. Enter submits the same way as the **Tell the agent** button.

## Tests

Tests load the real fixture. A paraphrase that names the right entities unlocks when the model returns `meets_goal` true. A wrong set, a negated required entity, and a missing entity stay locked even when the model returns true. The override line does not contain the missing or wrong name. One live-call test skips when the API key is absent.

## Invalid Bot weeks

Week 1. Companies over 1% with at least 100 reports. The guard entities are company names. This week already ships. Leave it.

Week 2. Pareto of product problems for each flagged company. The codes that bring that company under 1% are the action items. On the JJE fixture the sets are Roche `INV-MECH` and `INV-NOR`, Siemens `INV-MECH` and `INV-USR`, and Abbott Labs `INV-MECH`. Abbott Labs also records a tie at the same count with `INV-SW`, so either tied code fills the Abbott Labs slot. The guard entities are those company and code pairs. An extra code in that company's run, or an extra company claimed in the set, keeps Next locked.

Week 3. One simulated testimonial per company and issue, the ticket line for that issue, and the fishbone branch the note points at. The rubric asks the judge to check the note, the ticket, and the branch. The guard checks only the company and the code of each issue.

Week 4. One simulated close-out per flagged company. It states the root cause, the corrective action, and the public statement, including the projected share. The rubric asks the judge to check that statement. The guard checks only the flagged companies.
