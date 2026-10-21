# Résumé bullets

Copied from `evals/reports/2026-10-21.md`. n = 22 synthetic scenarios, 4 held out. These are not clinical accuracy claims. Llama 3.1 8B and Llama 3.2 1B were not installed for that run, so there is no model-versus-model number.

- Built a simulated 4-week field investigation for a fictional molecular panel (promised validity at least 98%). The loop produces a plan, stakeholder notes, a fishbone, 5 Whys, an 8D/CAPA record, and a 7-slide exec deck. Rates and costs are computed in code. A narrative that introduces a number outside those facts is replaced by the template.
- Scored 22 seeded scenarios offline (4 held out, gates not refit). The evidence ranker matched the designed call on 22/22, including 3 red herrings and 1 lot bump that correctly stayed `no_single_cause`. A ranker that only read the week-0 note matched 3/22.
- On 4 of the drift scenarios a second stratum, a reagent lot, also cleared the evidence bar. Top-1 stayed on the instrument. That second call is part of the result, not a footnote to drop.
- Week-0 graph checks on the same 22 scenarios: numeric fidelity 22/22, 5 Whys citations 22/22, escalation matched the spec comparison 22/22. Mean latency 0.55 seconds on the deterministic backend.
