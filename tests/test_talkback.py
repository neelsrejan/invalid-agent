"""The talk-back reply answers from the week view, even with no model."""

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
        "plan_ticket_count": 12,
    }


def test_majority_insight_is_confirmed_and_names_the_ticket():
    view = _view()
    message = "It looks like the Pareto is saying INV-NOR and INV-MECH make up the majority of the invalids"
    reply = respond(message, view, "charts", ticket_key="INV-13", flag_key="Flag 1")
    assert reply["kind"] == "correct"
    assert reply["confirmed"] is True
    assert reply["text"].startswith("YEP, YOU GOT IT!")
    assert "INV-13" in reply["text"]
    assert "Remember:" in reply["text"]
    assert "Fidelity" not in reply["text"]
    assert "rejected" not in reply["text"].casefold()
    assert reply["bullet"].startswith("We found ")
    assert "logged as Jira ticket INV-13" in reply["bullet"]
    assert unexplained_jargon(reply["text"]) == []


def test_rate_question_uses_the_chart_count_not_a_second_number():
    view = _view()
    reply = respond("Why is the invalid rate going up?", view, "charts", ticket_key="INV-13", flag_key="Flag 1")
    assert reply["kind"] == "question"
    assert reply["confirmed"] is False
    assert view["rule1_sentence"] in reply["text"]
    assert "21" not in reply["text"]
    assert "Fidelity" not in reply["text"]
    assert "model draft" not in reply["text"].casefold()
    assert "Flag 1" in reply["text"]
    assert "Remember:" in reply["text"]


def test_wrong_majority_is_not_confirmed():
    view = _view()
    reply = respond(
        "INV-SW makes up the majority of the invalids",
        view,
        "charts",
        ticket_key="INV-13",
        flag_key="Flag 2",
    )
    assert reply["kind"] in {"unsupported", "partial"}
    assert reply["confirmed"] is False
    assert "Flag 2" in reply["text"]
    assert reply["bullet"] is None


def test_failed_model_keeps_the_plain_answer():
    view = _view()
    base = respond("Why is the invalid rate going up?", view, "data", ticket_key="INV-13", flag_key="Flag 1")["text"]

    class _Bad:
        name = "groq"

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return "Fidelity ok: False. The chart actually shows 21. model draft was rejected."

    assert reword_reply(base, _Bad()) == base
    assert "Fidelity" not in reword_reply(base, _Bad())


def test_every_step_has_example_prompts():
    view = _view()
    for step in ("complaint", "data", "charts", "logged", "notes", "wrap"):
        prompts = example_prompts(view, step)
        assert len(prompts) >= 2
        assert any("going up" in prompt for prompt in prompts)
