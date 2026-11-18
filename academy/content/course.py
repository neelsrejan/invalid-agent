"""Session metadata. Quizzes and clip notes live in their own modules."""

SESSIONS = [
    {
        "id": 1,
        "week": 1,
        "title": "PRD, backlog, and a skeleton that tests",
        "minutes": "40–55",
        "ticket": "INV-101, INV-102, INV-103",
        "artifact": "PRD, build backlog, green CI with no secrets",
        "blurb": "Name the promise, put the sprint stories in a file a reviewer can read, and make the repo install and test before any model exists.",
        "read": [
            "PRD.md — the complaint, the 98 percent validity promise, and the list of work this repo will not do.",
            "docs/jira/backlog.json — the build board. Sprint 1 is INV-101 through INV-109. It is not the investigation sync.",
        ],
        "trace": (
            "Settings is the only place that reads the Jira token and the openFDA key. "
            "The printed object hides them. The invalid-rate cap is calculated from the validity promise so the two limits cannot drift. "
            "CI installs the package and runs pytest. It does not download a model and it does not post to Jira."
        ),
        "practice": (
            "On a private branch, run pytest before you change anything. "
            "Then write two sentences: why a printed settings object must not contain the token, "
            "and why docs/jira/backlog.json is a different artifact from the investigation issues a later session will write. "
            "Do not merge the branch."
        ),
    },
    {
        "id": 2,
        "week": 1,
        "title": "A synthetic field file and the metrics",
        "minutes": "55–75",
        "ticket": "INV-104, INV-105",
        "artifact": "Seeded field file, Wilson interval, p-chart, Pareto",
        "blurb": "The scenario file is the cause. Python draws the table and computes the rate, the interval, the chart, and the Pareto. No model is involved.",
        "read": [
            "scenarios/bad_lot.yaml — lot, start day, and stratum rate are the knobs. The printed rate is not in this file.",
            "scenarios/README.md — the YAML is the process, not an answer key of rates.",
        ],
        "trace": (
            "A seed makes the walkthrough file repeatable. The generator draws a baseline, then redraws only the cause mask. "
            "Rates, the Wilson interval, the p-chart, and the Pareto are functions of that table. "
            "The language model is not in this session, and the printed percent is an output."
        ),
        "practice": (
            "Generate the walkthrough scenario. Name the three knobs in the YAML that are inputs, "
            "and point at one number in the printout that is not stored in the file. "
            "Leave that number out of the YAML."
        ),
    },
    {
        "id": 3,
        "week": 1,
        "title": "Week-0 triage memo and the fidelity guard",
        "minutes": "55–75",
        "ticket": "INV-108, INV-109",
        "artifact": "One-page triage memo whose numbers match the code",
        "blurb": "One graph node writes the escalation memo. The ranker reads the table. A number that is not in the facts does not survive the guard.",
        "read": [
            "Run python -m invalid_agent.graph --scenario bad_lot --week 0 and open out/week0_triage.md.",
            "The fidelity JSON beside it should name the deterministic backend when you have not selected a model.",
        ],
        "trace": (
            "Triage runs once, at the start of the case. The memo interpolates the metrics dict, and the hypothesis list comes from the strata, not from a stakeholder sentence. "
            "The guard rejects a narrative number the facts do not contain. "
            "If a model is attached later, it may rewrite wording, and the template replaces a draft that fails."
        ),
        "practice": (
            "Run the week-0 graph on the walkthrough scenario. "
            "Explain why a percentage that is not in the facts has to be rejected even when the sentence sounds more precise than the memo."
        ),
    },
    {
        "id": 4,
        "week": 2,
        "title": "Fishbone, 5 Whys, and an 8D/CAPA",
        "minutes": "40–55",
        "ticket": "INV-201",
        "artifact": "fishbone.md, five_whys.md, capa8d.md",
        "blurb": "The ranked hypothesis becomes a quality record. A Why with no citation is an error. A future note stays invisible until its week.",
        "read": [
            "After the week-0 run, open out/fishbone.md, out/five_whys.md, and out/capa8d.md.",
            "Find the later QA injection in scenarios/bad_lot.yaml and notice week 0 is not allowed to cite it.",
        ],
        "trace": (
            "The record is a 6M fishbone, a five-step Why chain, and an 8D/CAPA with DMAIC labels. "
            "Every step cites a catalog id. On the walkthrough lot the chain stops at that lot. "
            "Injections are filtered by week, so a note that has not arrived yet cannot be evidence."
        ),
        "practice": (
            "At week 0, name the injection the Why chain is not allowed to cite yet. "
            "Say why a missing citation is an error rather than a warning that still writes the file."
        ),
    },
    {
        "id": 5,
        "week": 2,
        "title": "Gantt, risk register, and a Jira dry-run",
        "minutes": "50–70",
        "ticket": "INV-204, INV-205, INV-206",
        "artifact": "Gantt HTML and PNG, risk register, jira_issues.json",
        "blurb": "The plan and the register follow the top hypothesis and the week. With no token the sync writes SIM keys and does not open a socket.",
        "read": [
            "Run python -m invalid_agent.graph --scenario bad_lot --week 2 and open the Gantt, risk_register.md, and jira_issues.json.",
            "Confirm the issue keys start with SIM- and that the lab-director task exists at week 2.",
        ],
        "trace": (
            "Owners, dates, and dependencies come from the top cause. Later weeks add tasks and can move a risk's trend. "
            "The HTML chart and the PNG are two views of that plan. "
            "Without all three Jira settings the client writes a JSON file of SIM issues. That file is not the build backlog."
        ),
        "practice": (
            "Run week 2 with no Jira variables set. "
            "Confirm the written keys start with SIM and that the command did not need a token. "
            "Say, in one sentence, how that file differs from docs/jira/backlog.json."
        ),
    },
    {
        "id": 6,
        "week": 2,
        "title": "Weekly injections and three status notes",
        "minutes": "50–70",
        "ticket": "INV-207, INV-208",
        "artifact": "Decision log and customer, internal, and leadership notes",
        "blurb": "Each week re-plans and writes three notes from the same rate. The customer note does not declare a cause. The color is red, amber, or green.",
        "read": [
            "Run the walkthrough through week 3 and compare out/week0 with out/week3.",
            "Read the customer note and the internal note for the same week side by side.",
        ],
        "trace": (
            "The loop is a graph edge back to the plan. Triage does not repeat, and the field file does not change. "
            "The three notes share a rate line. The customer copy does not state a cause. Leadership adds cost and the ask. "
            "The walkthrough stays over spec, so the color does not turn green."
        ),
        "practice": (
            "Compare the customer note with the internal note for the same week. "
            "Name the fact they must share, and name the conclusion the customer note is not allowed to state."
        ),
    },
    {
        "id": 7,
        "week": 3,
        "title": "A Streamlit dashboard and the hosted narrator",
        "minutes": "50–70",
        "ticket": "INV-301, INV-302",
        "artifact": "Clickable week stepper: rate, p-chart, Pareto, projection",
        "blurb": "The page calls the same case run. The public demo narrates with Groq's free tier. CI stays deterministic. The projection is labeled as not observed.",
        "read": [
            "streamlit run streamlit_app.py — the banner, the spec line, and the week control.",
            "The hosted page is the Streamlit card on the home page. It calls Groq, not a local model.",
        ],
        "trace": (
            "The dashboard is a view of run_case, not a second investigation. "
            "Charts read numbers Python already computed. The projection clears the leading stratum on a copy of the file and says the result was not observed. "
            "Ollama is the laptop path. Groq is the hosted path. CI does not call either."
        ),
        "practice": (
            "Open the dashboard and read the banner's data source. "
            "Say what the projection caption has to include, and why the hosted page does not run Llama 3.1 8B locally."
        ),
    },
    {
        "id": 8,
        "week": 3,
        "title": "An offline scorecard",
        "minutes": "45–60",
        "ticket": "INV-303",
        "artifact": "Eval report: evidence ranker versus a note-only ranker",
        "blurb": "Twenty-two seeded scenarios. The report compares a ranker that reads the table with a ranker that only reads the week-0 note. The models were not called.",
        "read": [
            "evals/reports/2026-10-20.md — both splits, and the failure notes under the table.",
            "scenarios/herring_lot.yaml — the note and the true cause are different on purpose.",
        ],
        "trace": (
            "The evidence ranker matched the planted cause on this constructed set, including the held-out files. "
            "The note-only ranker matched a few flat files and repeated the note on the red herrings. "
            "Four drift files also cleared a lot stratum, and top-1 stayed on the instrument. "
            "The report is two policies on the deterministic backend, not a Llama accuracy number."
        ),
        "practice": (
            "From the eval report, choose one number you would quote and one number you would refuse to drop. "
            "The second number is a miss that has to travel with the hit. Do not describe the table as a model score."
        ),
    },
    {
        "id": 9,
        "week": 3,
        "title": "Week-4 close-out, the exec deck, and the résumé",
        "minutes": "50–70",
        "ticket": "INV-304, INV-305",
        "artifact": "Seven-slide deck, close-out note, résumé bullets with the misses kept",
        "blurb": "Week 4 confirms the record and writes a seven-slide deck from computed facts. The résumé keeps the eval misses next to the hits.",
        "read": [
            "python -m invalid_agent.graph --scenario bad_lot --week 4 writes out/exec_deck.pptx and out/closeout.md.",
            "RESUME_BULLETS.md — the evidence-ranker cell is printed beside the note-only result.",
        ],
        "trace": (
            "Close-out runs only after week 4. The deck is seven slides written by code from the close-out facts, including the disclaimer and the labeled projection. "
            "A single cause recommends containing that stratum. No single cause recommends no quarantine. "
            "The résumé copies the eval counts and does not promote them into a model claim."
        ),
        "practice": (
            "Open the deck and the résumé bullets. "
            "Confirm the recommendation matches the top cause, and that the résumé keeps the note-only result next to the evidence-ranker result."
        ),
    },
]
