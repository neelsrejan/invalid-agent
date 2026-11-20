"""The talk-back reply answers from facts the reader has already seen."""

from invalid_agent.ui.plain import unexplained_jargon
from invalid_agent.ui.talkback import example_prompts, respond, reword_reply


def _view() -> dict:
    return {
        "majority": True,
        "majority_codes": ["INV-NOR", "INV-MECH"],
        "majority_phrase": "no usable result (INV-NOR) and a mechanical problem (INV-MECH)",
        "code_shares": {"INV-NOR": 0.4, "INV-MECH": 0.25, "INV-SW": 0.05},
        "top_code": "INV-NOR",
        "top_plain": "no usable result (INV-NOR)",
        "direction": "up",
        "direction_sentence": (
            "The later weeks in this slice are higher (4.00%) than the early weeks (1.00%). "
            "This chart counts 10 weeks far above the usual rate."
        ),
        "rule1_sentence": "This chart counts 10 weeks far above the usual rate.",
        "rule1_count": 10,
        "cause_sentence": "No single group stands out yet. We will not pretend we know the cause.",
        "single": False,
        "rate_sentence": "The invalid rate this week is 3.00% (30 of 1000).",
        "promise_sentence": "The promise is that at least 98% of tests are valid, so invalid results stay at or below 2%.",
        "measure_sentence": "This file counts test runs, so we can compare the invalid rate with the 2% cap.",
        "decision": "We opened the case. The leading read is no single group.",
        "notes": {"customer": "Hello. We have not confirmed a cause."},
        "tickets": [{"key": "INV-1", "name": "Confirm the rate", "status": "In Progress"}],
        "device_line": "Device: MDx-24 Respiratory Panel.",
        "fda": False,
    }


def _reply(message: str, step: str = "charts"):
    return respond(message, _view(), step, ticket_key="Your ticket 1", flag_key="Flag 1")


def test_majority_insight_is_confirmed_and_names_your_ticket():
    reply = _reply("It looks like the Pareto is saying INV-NOR and INV-MECH make up the majority of the invalids")
    assert reply["kind"] == "correct"
    assert reply["confirmed"] is True
    assert reply["text"].startswith("YEP, YOU GOT IT!")
    assert "Your ticket 1" in reply["text"]
    assert "On a real team this would go in Jira." in reply["text"]
    assert reply["text"].count("root cause") == 1
    assert "INV-13" not in reply["text"]
    assert reply["log_kind"] == "ticket"
    assert "Your ticket 1" in reply["bullet"]
    assert unexplained_jargon(reply["text"]) == []


def test_rate_question_uses_the_chart_count_and_is_not_a_flag():
    reply = _reply("Why is the invalid rate going up?")
    assert reply["kind"] == "question"
    assert reply["confirmed"] is False
    assert reply["log_kind"] == ""
    assert "Flag" not in reply["text"]
    assert _view()["rule1_sentence"] in reply["text"]
    assert "21" not in reply["text"]
    assert "GOOD QUESTION." in reply["text"]


def test_wrong_majority_is_a_flag():
    reply = _reply("INV-SW makes up the majority of the invalids")
    assert reply["kind"] in {"unsupported", "partial"}
    assert reply["confirmed"] is False
    assert reply["log_kind"] == "flag"
    assert "Flag 1" in reply["text"]
    assert reply["bullet"] is None


def test_code_claim_before_charts_is_not_confirmed():
    message = "It looks like INV-NOR and INV-MECH make up the majority of the invalids"
    for step in ("complaint", "data"):
        reply = _reply(message, step)
        assert reply["confirmed"] is False
        assert reply["log_kind"] == ""
        assert reply["bullet"] is None
        assert "NOT YET — you'll see that on the charts part" in reply["text"]
    assert _reply(message, "charts")["confirmed"] is True


def test_negated_or_asked_claims_are_not_confirmed():
    for message in (
        "INV-NOR and INV-MECH do NOT make up the majority of the invalids",
        "Do INV-NOR and INV-MECH make up the majority of the invalids?",
        "INV-NOR is not the biggest invalid type",
    ):
        reply = _reply(message)
        assert reply["confirmed"] is False, message
        assert reply["log_kind"] == ""
        assert not reply["text"].startswith("YEP")


def test_plain_questions_get_a_real_answer_and_no_flag():
    maude = _reply("What is MAUDE?", "complaint")
    assert "public database of device problem reports" in maude["text"]
    assert maude["log_kind"] == ""
    maker = _reply("Who made the device?", "complaint")
    assert "MDx-24" in maker["text"]
    assert maker["log_kind"] == ""
    hello = _reply("hello", "complaint")
    assert "complaint" in hello["text"].casefold()
    assert "3.00%" not in hello["text"]
    assert hello["log_kind"] == ""
    early = _reply("why is it going up?", "complaint")
    assert "NOT YET — you'll see that on the numbers part" in early["text"]
    assert early["log_kind"] == ""


def test_example_prompts_hide_the_code_claim_before_charts():
    view = _view()
    for step in ("complaint", "data"):
        prompts = " ".join(example_prompts(view, step))
        assert "make up most" not in prompts
        assert "going up" in prompts
    assert any("make up most" in prompt for prompt in example_prompts(view, "charts"))


def test_ticket_key_is_not_read_as_an_invalid_type():
    reply = _reply("Your ticket 1 and INV-13 are the problem", "charts")
    assert reply["kind"] == "question"
    assert reply["confirmed"] is False


def test_failed_model_keeps_the_plain_answer():
    base = _reply("Why is the invalid rate going up?")["text"]

    class _Bad:
        name = "groq"

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return "Fidelity ok: False. The chart actually shows 21. model draft was rejected."

    assert reword_reply(base, _Bad()) == base


def test_faithful_rewrite_is_kept_and_added_number_or_jargon_is_not():
    base = _reply("Why is the invalid rate going up?")["text"]
    faithful = base.replace("The later weeks", "The later weeks in this file")

    class _Ok:
        name = "groq"

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return faithful

    assert reword_reply(base, _Ok()) == faithful

    class _Extra:
        name = "groq"

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return faithful + " The real count is 21."

    assert reword_reply(base, _Extra()) == base

    class _Jargon:
        name = "groq"

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return faithful.replace("GOOD QUESTION.", "GOOD QUESTION. The Pareto chart says")

    assert reword_reply(base, _Jargon()) == base


def test_negation_and_question_shapes_are_not_tickets():
    for message in (
        "INV-NOR and INV-MECH cannot make up most of the invalids",
        "The biggest problem is not INV-NOR",
        "I do not believe the invalid rate is going up",
        "(Is INV-NOR the biggest invalid type?)",
        "would you say INV-NOR is the biggest invalid type",
    ):
        reply = _reply(message)
        assert reply["confirmed"] is False, message
        assert reply["log_kind"] == ""
        assert not reply["text"].startswith("YEP")


def test_most_claim_and_ticket_questions_wait_for_their_part():
    early = _reply("Most invalids are INV-NOR", "complaint")
    assert "NOT YET — you'll see that on the charts part" in early["text"]
    assert early["log_kind"] == ""
    for message in ("What got logged?", "what is in jira?"):
        reply = _reply(message, "complaint")
        assert "NOT YET — you'll see that on the logged part" in reply["text"]
        assert "INV-1" not in reply["text"]
    view = _view()
    view["majority_codes"] = ["INV-VOL", "INV-IC"]
    view["majority_phrase"] = "not enough sample (INV-VOL) and an internal-control failure (INV-IC)"
    view["code_shares"] = {"INV-VOL": 0.4, "INV-IC": 0.3}
    kept = respond(
        "It looks like not enough sample (INV-VOL) and an internal-control failure (INV-IC) make up most of the invalids",
        view,
        "charts",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert kept["confirmed"] is True


def test_a_rewritten_reply_cannot_smuggle_a_number_or_a_longer_verdict():
    base = _reply("Why is the invalid rate going up?")["text"]

    class _Draft:
        name = "groq"

        def __init__(self, text: str):
            self.text = text

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return self.text

    smuggled = (
        "GOOD QUESTION. The later weeks in this slice are higher (4.00%) than the early weeks (1.00%). "
        "This chart counts 10 weeks far above the usual rate. Remember: use the sentence on this screen "
        "before you lock a cause. The hidden figure is 91."
    )
    assert reword_reply(base, _Draft(smuggled)) == base
    assert reword_reply(base, _Draft("GOOD QUESTIONS. " + base)) == base
    assert reword_reply(base, _Draft(base + " The Paretos chart agrees.")) == base
    yep = _reply("INV-NOR and INV-MECH make up the majority of the invalids")["text"]
    assert reword_reply(yep, _Draft(yep.replace("YEP, YOU GOT IT!", "YEP, YOU GOT IT WRONG!", 1))) == yep


def test_every_step_has_example_prompts():
    view = _view()
    for step in ("complaint", "data", "charts", "logged", "notes", "wrap"):
        prompts = example_prompts(view, step)
        assert len(prompts) >= 2
        assert any("going up" in prompt for prompt in prompts)
