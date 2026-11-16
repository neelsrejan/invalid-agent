#!/usr/bin/env python3
"""Write the high-level narration scripts. Two clips a session, like the sibling sites.

Each clip opens with an architecture overview, then three or four ranges on main.
The renderer speaks the overview on a title card before the code.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "academy" / "narration"


def clip(session: int, stem: str, title: str, file: str, overview: str, segments: list[tuple[str, str]]) -> dict:
    return {
        "session": session,
        "stem": stem,
        "title": title,
        "file": file,
        "overview": " ".join(overview.split()),
        "voice": "en-US-AndrewNeural",
        "rate": "+0%",
        "pause": 0.35,
        "segments": [{"lines": lines, "say": " ".join(say.split())} for lines, say in segments],
    }


CLIPS = [
    clip(
        1, "01_config", "Session 1 · Settings and the secret boundary",
        "src/invalid_agent/config.py",
        "config.py is the only place that reads the Jira token and the openFDA key. "
        "Printing the settings object shows a redacted view, so a log cannot become a leak. "
        "The invalid-rate cap is calculated from the 98 percent validity promise, and a missing "
        "or unknown model backend falls back to deterministic. That is the path CI runs.",
        [
            ("14-23", "The two spec constants are one promise. Ninety-eight percent valid means the invalid rate stays at or under two percent, and the cap is computed so the two cannot be edited apart. The default local model tag is Llama 3.1 8B. The smaller tag is only a suggestion for a laptop. Hosted Streamlit does not use either one."),
            ("43-94", "Settings is frozen after it loads. Jira turns on only when the site, the email, and the token are all present. Two out of three stays off. The redacted view masks the token and the openFDA key, and the printed form of the object uses that view. The raw token is not interpolated into the string."),
            ("96-119", "load_settings reads the environment. Friendly names such as rules-only become deterministic, and an unknown name does too, so a typo on a demo falls back to the template instead of crashing. The longer Jira variable names win when both aliases are set. Nothing in this function opens a socket."),
        ],
    ),
    clip(
        1, "02_ci", "Session 1 · CI proves the repo, not the model",
        ".github/workflows/ci.yml",
        "CI is the contract that a stranger can install the package and run the tests. "
        "It does not download a model, it does not hold a Jira token, and it does not call Ollama. "
        "A second job rebuilds the learning site and fails if the committed pages drift from the generator.",
        [
            ("1-26", "The test job runs on two Python versions. It installs the package with the dev extra and runs pytest, then a five-scenario slice of the eval on the deterministic backend. There is no secret in the workflow. A green run means the repo works without an account."),
            ("28-39", "The academy job installs the page generator and rebuilds the HTML. It fails if the site or the quiz answer key drifts from what the script writes. It does not render the videos. Those are produced locally, because the speech service is not part of CI."),
        ],
    ),
    clip(
        2, "01_generate", "Session 2 · The YAML is the cause",
        "src/invalid_agent/sim/generate.py",
        "generate.py turns a scenario file into one seeded table. The YAML names the cause, "
        "the calendar, and the injections. The printed invalid rate is an output of this module, "
        "not a number stored in the file. The language model is not called.",
        [
            ("36-63", "load_scenario is YAML in and a dictionary out. Levels may be a plain id or a calendar with a start day, an end day, and a weight. That calendar is how a lot enters distribution without a special case in the sampler."),
            ("97-164", "The cause function is the ground truth. It redraws only the rows in its mask, so the baseline and the cause are not stacked into one probability. A bad lot, a drifting instrument, heat, hemolysis, a flat rate, and a red herring are different masks. The misleading sentence in a herring stays in the YAML for a later reader to abuse. This function does not rank a hypothesis."),
            ("165-206", "generate builds the horizon from the seed. The same file always produces the same rows. Site, instrument, lot, software, and operator are separate draws, so a lot effect can be told apart from an instrument. The scenario id is stored on the frame. The frame itself is not kept on the case graph."),
            ("207-230", "summarize prints the rate, the interval, the strata, the chart, and the Pareto by calling those modules. It does not compute a second rate of its own. If the printout and the YAML disagree, the printout is the output and the YAML is the input."),
        ],
    ),
    clip(
        2, "02_rates", "Session 2 · Rates stay in Python",
        "src/invalid_agent/metrics/rates.py",
        "Rates, the Wilson interval, the spec comparison, and the chi-square live here. "
        "The week-0 memo quotes this dictionary. It does not recompute the rate a second way, "
        "and a model is not asked to do the arithmetic.",
        [
            ("20-40", "The Wilson interval is written out so a reviewer can check it. A residue that should be zero is snapped to zero, because the analytic lower bound is zero and floating point subtraction is not."),
            ("42-60", "overall_rate returns both facts the memo needs: whether the point estimate is over the two percent cap, and whether the whole interval clears that cap. Those are different claims. The function does not decide the root cause."),
            ("85-110", "chi_square_by compares invalid and valid counts across the levels of one column. A single level, or a column with no variation, returns a quiet p-value of one instead of raising. A quiet scenario is not an exception."),
        ],
    ),
    clip(
        3, "01_triage", "Session 3 · The week-0 memo",
        "src/invalid_agent/nodes/triage.py",
        "Triage runs once, at the start of the case. It writes the escalation memo from the metrics "
        "dictionary: the rate, the interval, the spec, the strata, the severity, and the first hypothesis. "
        "The complaint text is copied from the scenario. The memo does not calculate a new rate while it writes.",
        [
            ("79-136", "build_facts is the only number source for the memo. It rounds the values the guard will later accept, including the percent form of a proportion. The hypothesis sentence is built from those same fields. A stakeholder injection is not an input here."),
            ("156-204", "triage_node regenerates the frame from the scenario seed, ranks hypotheses, fills the facts, and narrates the memo. The draft goes through the fidelity guard. A failure raises, and the rejected text is not the file that gets written. The node does not loop."),
        ],
    ),
    clip(
        3, "02_fidelity", "Session 3 · A number must already exist",
        "src/invalid_agent/guards/numeric_fidelity.py",
        "The fidelity guard sits between any prose and the reader. Triage, the quality record, "
        "the status notes, and close-out all pass through it. It does not compute rates. "
        "It rejects a number that is not already in the facts, which is why a model may rewrite wording and may not invent a percentage.",
        [
            ("27-45", "Walking the facts collects the raw value and, for a proportion between zero and one, the percent form as well. That is why a sentence may say 3.67 percent when the stored rate is the matching proportion, and why a nearby invention still fails."),
            ("60-72", "Allowed numbers are that walk. The tolerance is tighter on small values than on large ones, so a rounded percent can match and a different percent cannot. Identifiers are not added to this set."),
            ("74-88", "check_narrative strips dates, removes identifier strings so a lot id cannot be reused as a rate, and then every remaining number must sit near an allowed value. A miss returns not ok. Callers treat that as a failed draft, not as a warning to ignore."),
        ],
    ),
    clip(
        4, "01_rca", "Session 4 · Fishbone, five Whys, and the 8D record",
        "src/invalid_agent/nodes/rca.py",
        "rca.py turns the ranked hypothesis into a 6M fishbone, a five-step Why chain, and an 8D record "
        "with DMAIC labels. Every Why step needs a citation that exists in the catalog. "
        "A missing citation raises before markdown is written. Injections are visible only once their week has arrived.",
        [
            ("68-98", "index_injections keeps notes whose week is at or before the case week. A QA sentence dated later is not evidence yet. validate_whys raises on an empty citation list and on an id that is not in the catalog. A broken chain never becomes a file."),
            ("104-138", "The fishbone copies the evidence for a hit and asks for a contrary citation. Branches sort by score. A branch that did not fire still appears, with the overall rate as the reason it did not explain the panel. Measurement can be an empty bone so the diagram is not missing a category."),
            ("165-226", "The Why chain has five cited steps. The first is the rate against the spec. A later step has to say why the next stratum is not the cause. On a lot, the chain is required to stop at that lot. When the ranker returned no single cause, the chain still has five citations and does not invent a lot to satisfy the test."),
            ("283-317", "The CAPA maps the top cause to a containment and a corrective action in words. The effectiveness check is named, and it says a before-and-after number is a projection until follow-up exists. Prevention and closure are written and marked preliminary. This function does not close the case."),
        ],
    ),
    clip(
        4, "02_test_rca", "Session 4 · A broken chain never becomes a file",
        "tests/test_rca.py",
        "The RCA tests are the rule, not a tour of the markdown. A Why with no citation is an error. "
        "An unknown citation id is an error. On the walkthrough lot the top bone is material and the chain names that lot. "
        "The tests do not call Jira or a model.",
        [
            ("17-31", "Two tests plant a failure. One step has no citations. Another cites an id that was never in the catalog. Both must raise. A warning that still wrote the file would be the wrong contract."),
            ("33-53", "The walkthrough scenario is checked as a record, not as a screenshot. Material ranks first, the chain ends on the lot, and the citations resolve. That is the behavior a later plan is allowed to trust."),
        ],
    ),
    clip(
        5, "01_planner", "Session 5 · A four-week plan that can grow",
        "src/invalid_agent/nodes/planner.py",
        "The plan, the owners, and the risk register are functions of the top hypothesis and the week. "
        "Later weeks add tasks. They do not delete the baseline plan. "
        "A start that lands before its predecessor finishes raises. Likelihood times impact is checked, not typed twice.",
        [
            ("22-40", "The owner follows the cause. A lot is QA. An instrument or a temperature lane is manufacturing. Software is R and D. No single cause stays with the program manager, which is the decision not to quarantine yet. The schedule is anchored to the investigation start, not to today's date."),
            ("62-122", "The baseline tasks fit inside four weeks. The lab-director task appears from week two. A lane-temperature task waits for week three. Those are the injection-driven adds. The containment task's owner comes from the map above. Re-planning keeps the earlier tasks and refreshes their status."),
            ("123-131", "Dependencies compare dates as text. A task that starts before its predecessor ends raises. The format has to stay sortable as text, which is why the dates are ISO dates and not a locale string."),
            ("153-229", "Risks store likelihood times impact and raise if that product is wrong. A real cause in hand can move one trend down. A disagreement between release data and the field can open another risk with the trend up. Some risks wait until the week that stakeholder speaks."),
        ],
    ),
    clip(
        5, "02_jira", "Session 5 · Dry-run unless all three secrets exist",
        "src/invalid_agent/integrations/jira.py",
        "The Jira client uses the same gate as settings. Without a site, an email, and a token, "
        "sync writes SIM keys to a JSON file and does not open a socket. "
        "Those keys are the fictional investigation. They are not the build-board keys in the backlog file.",
        [
            ("54-69", "The dry-run client keeps a local mirror of the epic and the stories. Keys are minted with a SIM prefix so a rehearsal file cannot be mistaken for project INV on the build board. Sync reads the file, upserts, and writes it back."),
            ("71-111", "The live client knows the REST shape and posts only when sync is called. A failure still leaves the local file, with the error recorded, so a demo does not lose the plan because the network failed. The token is not printed by the object's repr."),
            ("114-118", "make_client is the switch. The live client is constructed only when jira_enabled is true. Tests pass a fake transport and never need a token. CI takes this dry-run path."),
        ],
    ),
    clip(
        6, "01_graph", "Session 6 · The week is a graph edge",
        "src/invalid_agent/graph.py",
        "The case is one graph. Triage runs once, then plan, the quality record, and a status note repeat "
        "until the requested week. The field file does not change between weeks. "
        "Week four continues into close-out. The dataframe is not stored on the graph state.",
        [
            ("25-38", "Advancing the week adds one to the counter and nothing else. The decision log, the scenario, and the metrics stay on the state. After the status note, the route stops, advances, or, at week four, goes to close-out. A one-week run does not spin."),
            ("40-60", "The edges are the control flow. Triage leads to plan, plan to the record, the record to status. Status either ends, advances back to plan, or closes out. A loop hidden in the command line would have done the work and hidden the decision."),
            ("97-121", "run_case always starts at week zero and walks forward to the requested week. It writes the memo, the fidelity file, and the three quality records. Close-out, when it runs, adds the deck. The frame is regenerated inside the nodes from the seed."),
        ],
    ),
    clip(
        6, "02_status", "Session 6 · Three audiences, one rate",
        "src/invalid_agent/nodes/status.py",
        "Customer, internal, and leadership notes share one rate line. The customer note does not state a cause as fact. "
        "The color is red, amber, or green, which the code calls RAG. It is not a retrieval index. "
        "The walkthrough file is not rewritten, so that case does not turn green.",
        [
            ("20-26", "Green requires the rate to be back inside the spec. Red is an open breach before the containment week. Amber means containment is on the plan and the effect has not been observed. The color is a rule about the rate and the week, not a sentence the model picks."),
            ("32-41", "The customer actions are words. They do not name the cause type and they do not say the root cause is confirmed. A later week can talk about the lot under review without turning the note into a finding."),
            ("100-144", "The facts dictionary is the only number source for the three notes. Cost is the invalid count times the unit cost from the scenario, computed here, not typed into the template. Rounded percents are what the guard will accept."),
            ("146-169", "status_node narrates each audience, then runs the guard again. A new number fails the note. The decision log keeps one row per week, replaced if that week is written twice. The three strings are what get written to disk."),
        ],
    ),
    clip(
        7, "01_streamlit", "Session 7 · A page over the same run",
        "app/streamlit_app.py",
        "The dashboard calls the same case graph. It does not grow a second investigation loop. "
        "Rules-only is the default, because hosted Streamlit Community Cloud has no Ollama. "
        "The public page stays on templates and the numbers Python already computed.",
        [
            ("36-48", "The page chooses a model name in one place. An explicit LLM_MODEL wins. Rules-only does not call a model. With the toggle off and no model set, a local run asks for the smaller Llama 3.2 tag. The hosted app does not take that path."),
            ("50-64", "The run sets the backend for the call and restores the previous environment afterwards, so a cached dashboard run cannot pin a model for the next command in the same process. The cache key is the scenario, the week, the backend, and the model."),
            ("70-117", "The banner is the first thing on the page, and the title restates the 98 percent promise. The week slider and the rules-only toggle are the controls. Turning the toggle off asks Ollama and still falls back to the template if that model is not running. The tiles read the case result."),
        ],
    ),
    clip(
        7, "02_effectiveness", "Session 7 · A projection, not follow-up",
        "src/invalid_agent/metrics/effectiveness.py",
        "The projection copies the frame, clears invalids on the leading stratum, and reports before and after. "
        "It does not rewrite the scenario file. The label says the result is not observed follow-up. "
        "The walkthrough case never turns green for that reason.",
        [
            ("1-15", "The module docstring is the contract. This is a counterfactual on the same file. Callers have to keep that label. A chart without the label would look like a result the field had already delivered."),
            ("17-31", "The function copies the frame and clears the invalid flag on the leading stratum only. If that column or level is missing, it changes nothing and says so. The original scenario file is not opened for writing."),
            ("33-43", "The summary runs the same rate function on the original frame and on the copy. The label is a fixed sentence, not a number the model composed. The projected frame is returned for the chart and is not stored on the case as if it were new field data."),
        ],
    ),
    clip(
        8, "01_eval", "Session 8 · Score two ranking policies",
        "evals/run_eval.py",
        "The harness compares an evidence ranker, which reads the table, with a ranker that only reads the week-zero note. "
        "Llama 3.1 8B and Llama 3.2 1B are not required for this run. "
        "The table is two policies on the deterministic path, not a model-accuracy number.",
        [
            ("47-57", "The keyword policy scans notes that have already arrived and returns the first cause word it finds. It never opens the table. On a red herring it repeats the note."),
            ("70-97", "The evidence score generates the frame and ranks hypotheses. Top one is the first cause. Top three is membership in the first three. The expected label comes from the scenario, and the ranker is not given that block. A second stratum that also cleared the bar is recorded, not hidden."),
            ("107-133", "The week-zero graph check reuses the case run. It records whether the fidelity guard passed, whether every Why citation resolves, and whether the escalate flag matches the spec comparison. Latency is the time of that run, not a model call."),
            ("136-153", "The model section names the local default, the hosted rules-only path, and the smaller tag. It then says this command's table is two ranking policies. It refuses to print an accuracy number for a model that did not run."),
        ],
    ),
    clip(
        8, "02_herring", "Session 8 · A note can name the wrong cause",
        "scenarios/herring_lot.yaml",
        "A red-herring file keeps the true cause under a quoted key, because an unquoted true would be a boolean in YAML. "
        "The complaint and the week-zero note blame a reagent lot. The table does not. "
        "The evidence ranker is allowed to disagree with the note.",
        [
            ("28-39", "The cause type is red herring. The true block is hemolysis at one site. The complaint says the attached note names a lot, and that sentence is the herring. The expected answer is not the lot."),
            ("41-55", "The week-zero injection tells the reader to quarantine the lot. A note-only ranker stops there. The evidence ranker still has to look at the strata. Later notes do not get to rewrite week zero."),
            ("76-80", "The eval block names the cause the ranker should recover. It is not passed into the ranker. It is the label the report scores against, including on files that are not in the holdout split."),
        ],
    ),
    clip(
        9, "01_closeout", "Session 9 · Confirm the record from facts",
        "src/invalid_agent/nodes/closeout.py",
        "Close-out runs only after week four. It regenerates the frame, computes the projection and the cost, "
        "and drops the frame before the record is stored. D7 and D8 are confirmed. "
        "An unknown number raises, and the rejected text is not the file you ship.",
        [
            ("24-86", "The facts rebuild the rate, the projection, and the cost from the scenario seed. Cost is the invalid count times the unit cost. The effectiveness sentence keeps the label that follow-up was not observed. The frame is not one of the fields that gets stored."),
            ("87-147", "The close-out note is a template filled from those facts. It does not ask a model for a new percentage. The recommendation depends on whether a single cause cleared the bar. No single cause does not become a quarantine."),
            ("148-167", "The node runs the guard and raises on a miss. It writes the note, writes the deck from the same facts, and replaces the preliminary prevention and closure text. The deck path is the only new artifact path on the state."),
        ],
    ),
    clip(
        9, "02_deck", "Session 9 · Seven slides, written by code",
        "src/invalid_agent/artifacts/deck.py",
        "python-pptx writes the seven-slide deck from the close-out facts, so a slide cannot invent a cost. "
        "A single cause recommends containing that stratum and not expanding the hold. "
        "No single cause recommends no quarantine. The chart is the observed p-chart, and the projection stays labeled.",
        [
            ("13-21", "The palette is the same navy and teal as the dashboard. The deck is a real PowerPoint file, not an image of one, and not a slide a model composed."),
            ("80-111", "The title slide carries the scenario and the simulation banner. The banner is the same sentence as the memo and the Streamlit page. A reader who only opens the deck still sees that this is not a clinical result."),
            ("150-188", "The cause slide prints the observed rate and the projected rate, then the label that says the projection is not observed follow-up. The picture is the p-chart from the file, not a chart of the counterfactual. The options slide contains only when a single stratum cleared the bar, and it does not invent a second cost."),
            ("190-216", "The recommendation slide uses the sentence close-out already computed. The ask is to approve that recommendation or send the case back. The last box repeats the warning not to treat the projected rate as follow-up."),
        ],
    ),
]


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for item in CLIPS:
        folder = OUT / f"session-{item['session']}"
        folder.mkdir(parents=True, exist_ok=True)
        payload = {
            "title": item["title"],
            "file": item["file"],
            "overview": item["overview"],
            "voice": item["voice"],
            "rate": item["rate"],
            "pause": item["pause"],
            "segments": item["segments"],
        }
        path = folder / f"{item['stem']}.yaml"
        path.write_text(yaml.safe_dump(payload, sort_keys=False, width=100, allow_unicode=True))
        code = (ROOT / item["file"]).resolve()
        if not code.is_file():
            raise SystemExit(f"missing {item['file']}")
        nlines = len(code.read_text().splitlines())
        for segment in item["segments"]:
            start, end = segment["lines"].split("-")
            if int(start) < 1 or int(end) > nlines:
                raise SystemExit(f"{path.name} range {segment['lines']} outside 1..{nlines}")
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"{len(CLIPS)} clips")


if __name__ == "__main__":
    main()
