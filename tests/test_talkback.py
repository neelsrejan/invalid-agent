"""The talk-back reply answers from facts the reader has already seen."""

from invalid_agent.ui.plain import unexplained_jargon
from invalid_agent.ui.talkback import example_prompts, part_fact, respond, reword_reply


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
    assert reply["kind"] == "hint"
    assert reply["confirmed"] is False
    assert "GOOD QUESTION" not in reply["text"]


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


def test_a_false_denial_is_not_a_ticket():
    reply = _reply("The main invalid is not INV-NOR")
    assert reply["confirmed"] is False
    assert reply["log_kind"] == ""
    assert not reply["text"].startswith("YEP")
    assert "GOOD QUESTION" not in reply["text"]
    denied = _reply("INV-NOR and INV-MECH are not in fact the majority of the invalids")
    assert denied["confirmed"] is False
    assert denied["log_kind"] == ""
    assert not denied["text"].startswith("YEP")
    extra = _reply("INV-NOR and INV-MECH and INV-SW do not make up the majority of the invalids")
    assert extra["confirmed"] is False
    assert extra["log_kind"] == ""
    assert not extra["text"].startswith("YEP")


def test_a_greeting_with_a_question_mark_is_still_not_a_question():
    reply = _reply("Hello?", "complaint")
    assert "GOOD QUESTION" not in reply["text"]
    assert reply["log_kind"] == ""


def test_a_true_denial_does_not_log_the_biggest_type():
    view = _view()
    view.update(
        majority_codes=["INV-IC"],
        majority_phrase="an internal-control failure (INV-IC)",
        code_shares={"INV-IC": 0.6, "INV-NOR": 0.1},
        top_code="INV-IC",
        top_plain="an internal-control failure (INV-IC)",
    )
    reply = respond(
        "INV-NOR is not the biggest",
        view,
        "charts",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert reply["confirmed"] is False
    assert reply["log_kind"] == ""
    assert not reply["text"].startswith("YEP")
    assert "internal-control failure (INV-IC)" in reply["text"]


def test_a_negated_statement_is_a_direct_correction():
    reply = _reply("INV-NOR is not the biggest")
    assert reply["confirmed"] is False
    assert reply["log_kind"] == ""
    assert not reply["text"].startswith("YEP")
    assert "GOOD QUESTION" not in reply["text"]
    assert reply["text"].startswith("NOT QUITE.")
    assert "no usable result (INV-NOR)" in reply["text"]


def test_doubt_words_are_not_confirmed():
    for message in (
        "Neither INV-NOR nor INV-MECH make up most of the invalids",
        "I doubt INV-NOR and INV-MECH make up most of the invalids",
        "It's false that INV-NOR and INV-MECH make up most of the invalids",
        "INV-NOR and INV-MECH make up most of the invalids or not",
        "INV-NOR and INV-MECH make up most of the invalids, I think not",
        "INV-NOR and INV-MECH make up most of the invalids. NOT!",
        "INV-NOR isn't even close to the majority",
        "INV-NOR is hardly the biggest",
    ):
        reply = _reply(message)
        assert reply["confirmed"] is False, message
        assert reply["log_kind"] == "", message
        assert not reply["text"].startswith("YEP"), message
        assert "GOOD QUESTION" not in reply["text"], message
        assert "Your ticket" not in reply["text"], message


def test_not_enough_sample_can_be_a_correct_majority():
    view = _view()
    view["majority_codes"] = ["INV-VOL"]
    view["majority_phrase"] = "not enough sample (INV-VOL)"
    view["top_code"] = "INV-VOL"
    view["top_plain"] = "not enough sample (INV-VOL)"
    view["code_shares"] = {"INV-VOL": 0.62, "INV-NOR": 0.2}
    reply = respond(
        "not enough sample makes up most of the invalids",
        view,
        "charts",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert reply["confirmed"] is True
    assert reply["text"].startswith("YEP, YOU GOT IT!")
    assert "Your ticket 1" in reply["text"]
    assert "do not agree" not in reply["text"].casefold()
    assert "Not enough sample (INV-VOL)" in reply["text"]


def test_this_week_rate_question_uses_the_rate_sentence():
    reply = _reply("What is the invalid rate this week?", "data")
    assert reply["kind"] == "question"
    assert "3.00%" in reply["text"]
    assert "30 of 1000" in reply["text"]
    assert "This chart" not in reply["text"]


def test_a_greeting_or_aside_is_not_called_a_question():
    for message in ("hello", "asdf", "tell me a joke", "calibration is a problem"):
        reply = _reply(message, "complaint")
        assert "GOOD QUESTION" not in reply["text"], message
        assert reply["log_kind"] == ""
        assert reply["confirmed"] is False


def test_increasing_and_decreasing_follow_the_direction():
    up = _reply("the invalids are increasing", "data")
    assert up["confirmed"] is True
    assert up["text"].startswith("YEP, YOU GOT IT!")
    down = _reply("the invalids are decreasing", "data")
    assert down["confirmed"] is False
    assert down["log_kind"] == "flag"
    assert not down["text"].startswith("YEP")
    falling = _reply("the rate is going down", "data")
    assert falling["confirmed"] is False
    assert falling["log_kind"] == "flag"


def test_main_invalid_matches_the_top_code_only():
    view = _view()
    view["majority_codes"] = ["INV-VOL"]
    view["majority_phrase"] = "not enough sample (INV-VOL)"
    view["top_code"] = "INV-VOL"
    view["top_plain"] = "not enough sample (INV-VOL)"
    view["code_shares"] = {"INV-VOL": 0.8}
    reply = respond(
        "INV-VOL is the main invalid",
        view,
        "charts",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert reply["confirmed"] is True
    assert "Your ticket 1" in reply["text"]


def test_two_unsupported_claims_name_different_codes():
    first = _reply("INV-SW makes up the majority of the invalids")
    second = _reply("INV-CAL makes up the majority of the invalids")
    assert first["log_kind"] == "flag"
    assert second["log_kind"] == "flag"
    assert first["signature"] != second["signature"]
    assert "INV-SW" in first["signature"] or "software" in first["signature"]
    assert "INV-CAL" in second["signature"] or "calibration" in second["signature"]


def test_a_rewritten_reply_cannot_swap_numbers_or_flip_a_negation():
    base = _reply("Why is the invalid rate going up?")["text"]

    class _Draft:
        name = "groq"

        def __init__(self, text: str):
            self.text = text

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return self.text

    swapped = base.replace("4.00%", "HOLD%").replace("1.00%", "4.00%").replace("HOLD%", "1.00%")
    assert reword_reply(base, _Draft(swapped)) == base
    yep = _reply("INV-NOR and INV-MECH make up the majority of the invalids")["text"]
    flipped = yep.replace("make up most", "do NOT make up most", 1)
    assert reword_reply(yep, _Draft(flipped)) == yep


def test_every_step_has_example_prompts():
    view = _view()
    for step in ("complaint", "data", "charts", "logged", "notes", "wrap"):
        prompts = example_prompts(view, step)
        assert len(prompts) >= 2
        assert any("going up" in prompt for prompt in prompts)


def test_doubt_with_a_code_in_between_is_not_a_ticket():
    for message in (
        "It's not true that INV-NOR is the biggest",
        "I don't believe INV-NOR and INV-MECH make up most of the invalids",
        "I wouldn't say INV-NOR is the biggest",
        "No way INV-NOR is the biggest",
        "INV-NOR is far from the biggest",
        "INV-NOR is unlikely to be the biggest",
        "I question whether INV-NOR is the biggest",
    ):
        reply = _reply(message)
        assert not reply["confirmed"], message
        assert reply["log_kind"] != "ticket", message
        assert not reply["text"].startswith("YEP"), message


def test_a_code_name_with_wrong_in_it_can_be_confirmed():
    view = _view()
    view.update(
        majority_codes=["INV-USR"],
        majority_phrase="someone used it the wrong way (INV-USR)",
        code_shares={"INV-USR": 0.6, "INV-NOR": 0.2},
        top_code="INV-USR",
        top_plain="someone used it the wrong way (INV-USR)",
    )
    reply = respond(
        "Someone used it the wrong way makes up most of the invalids",
        view,
        "charts",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert reply["confirmed"]
    assert reply["text"].startswith("YEP")


def test_doubt_waits_for_its_part_and_a_right_doubt_is_not_told_not_quite():
    early = _reply("I doubt that", "complaint")
    assert "INV-NOR" not in early["text"] and not early["text"].startswith("NOT QUITE")
    right = _reply("I doubt INV-SW makes up most")
    assert not right["text"].startswith(("NOT QUITE", "YEP")) and right["log_kind"] != "ticket"
    rate = _reply("I doubt the rate is going up", "data")
    assert "4.00%" in rate["text"]


def test_a_true_denial_of_a_falling_rate_is_not_flagged():
    for message in ("the rate is not going down", "the rate isn't dropping"):
        assert _reply(message, "data")["log_kind"] != "flag", message


def test_leaving_a_code_out_with_not_or_nor_still_confirms_the_majority():
    for message in (
        "not INV-SW but INV-NOR and INV-MECH make up most",
        "INV-NOR and INV-MECH make up most of the invalids, nor INV-SW",
    ):
        reply = _reply(message)
        assert reply["confirmed"] is True, message
        assert reply["text"].startswith("YEP"), message


def test_a_denied_extra_code_does_not_turn_a_majority_into_a_flag():
    reply = _reply("INV-NOR and INV-MECH make up most of the invalids, not INV-SW")
    assert reply["confirmed"] is True
    assert reply["log_kind"] == "ticket"


def test_the_echo_keeps_the_readers_spacing():
    reply = _reply("what   is maude ??")
    assert reply["user_text"] == "what   is maude ??"


def test_praise_after_not_quite_is_rejected():
    base = _reply("INV-SW makes up most of the invalids")["text"]

    class _Draft:
        name = "groq"

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            return "NOT QUITE. Great job, you nailed it. " + base.split(".", 1)[-1]

    assert reword_reply(base, _Draft()) == base


def test_each_part_accepts_a_typed_statement_of_its_point():
    view = _view()
    view["rate_label"] = "3.00%"
    view["plan_ticket_count"] = 1
    cases = (
        ("complaint", "The promise is at least 98% valid tests"),
        ("data", "The invalid rate this week is 3.00%"),
        ("logged", "The plan has 1 open ticket"),
        ("notes", "Tell the customer we have not confirmed a cause"),
        ("wrap", "We recommend opening the case"),
    )
    for step, message in cases:
        reply = respond(message, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert reply["confirmed"] is True, message
        assert reply["signature"]


def test_bare_false_or_hardly_in_a_correct_claim_still_confirms():
    for message in (
        "No false alarms: INV-NOR and INV-MECH make up most of the invalids",
        "INV-NOR and INV-MECH make up most, hardly a surprise",
    ):
        assert _reply(message)["confirmed"], message


def _typed(message: str, step: str, **view_extra):
    view = _view()
    view.update(rate_label="3.00%", **view_extra)
    return respond(message, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")


def test_a_wrong_statement_of_the_promise_is_not_a_yep_or_a_ticket():
    for message in (
        "98% of tests are invalid, which breaks the promise",
        "the promise is that 2% are valid",
        "the promise is that 2% of tests are valid",
        "the promise is 98% invalid",
        "I promise 98 dollars",
        "98 valid promise",
    ):
        reply = _typed(message, "complaint")
        assert not reply["confirmed"], message
        assert reply["log_kind"] != "ticket", message
        assert not reply["text"].startswith("YEP"), message
    for message in (
        "The promise is that at least 98% of tests are valid",
        "invalid results stay at or below 2% of tests",
    ):
        assert _typed(message, "complaint")["confirmed"], message


def test_the_logged_part_needs_the_real_count_of_tickets():
    for message in (
        "There are 12 tickets open about the software",
        "no tickets are open",
        "0 tickets open",
        "open tickets don't matter",
    ):
        reply = _typed(message, "logged", plan_ticket_count=1)
        assert not reply["confirmed"], message
        assert not reply["text"].startswith("YEP"), message
    assert _typed("There is 1 ticket open", "logged", plan_ticket_count=1)["confirmed"]
    view = _view()
    view["tickets"] = []
    view["plan_ticket_count"] = 12
    assert "no follow-up items" in part_fact(view, "logged")[1]


def test_the_logged_count_is_this_weeks_table_not_the_whole_plan():
    view = _view()
    view["tickets"] = [{"key": "INV-1"}, {"key": "INV-2"}]
    view["plan_ticket_count"] = 12
    assert part_fact(view, "logged")[1] == "This week the plan has 2 follow-up items."


def test_notes_and_wrap_need_the_note_not_just_a_keyword():
    for message in (
        "The customer was told the device is recalled",
        "tell the customer everything is fine",
        "the customer should be told we found the cause",
    ):
        assert not _typed(message, "notes")["confirmed"], message
    for message in ("I recommend we stop selling the device", "I recommend pizza", "recommend closing the case"):
        assert not _typed(message, "wrap")["confirmed"], message
        assert not _typed(message, "notes")["confirmed"], message
    assert _typed("Tell the customer we have not confirmed a cause", "notes")["confirmed"]
    assert not _typed("Tell the customer we have confirmed a cause", "notes")["confirmed"]


def test_a_longer_number_does_not_match_the_rate():
    assert not _typed("the invalid rate is 13.00%", "data")["confirmed"]
    assert _typed("the invalid rate is 3.00%", "data")["confirmed"]


def test_pasting_the_on_screen_sentence_confirms_and_a_denial_does_not():
    promise = "The promise is that at least 98% of tests are valid, so invalid results stay at or below 2%."
    assert _typed(promise, "complaint")["confirmed"]
    denied = _typed("The promise is not that at least 98% of tests are valid", "complaint")
    assert not denied["confirmed"] and not denied["text"].startswith("YEP")
    view = _view()
    view["rate_label"] = "0.97%"
    view["rate_sentence"] = "The invalid rate this week is 0.97% (35 of 3600)."
    rate = respond("The invalid rate this week is not 0.97%", view, "data", ticket_key="Your ticket 1", flag_key="Flag 1")
    assert not rate["confirmed"] and not rate["text"].startswith("YEP")
    logged = _typed("there are not 5 follow-up items", "logged", tickets=[{"key": f"INV-{i}"} for i in range(5)])
    assert not logged["confirmed"] and not logged["text"].startswith("YEP")
    notes = (
        "Hello. The invalid rate this week is 0.97% (35 of 3600). "
        "We have not confirmed a cause. We opened the case."
    )
    view = _view()
    view["notes"] = {"customer": notes}
    reply = respond(notes, view, "notes", ticket_key="Your ticket 1", flag_key="Flag 1")
    assert reply["confirmed"], reply["text"]
    wrap = "We opened the case. The leading read is no single group."
    reply = respond(wrap, _view(), "wrap", ticket_key="Your ticket 1", flag_key="Flag 1")
    assert reply["confirmed"], reply["text"]
    share = _view()
    share["rate_label"] = "40.00%"
    share["rate_sentence"] = "The share of reports this week is 40.00% (40 of 100)."
    reply = respond(share["rate_sentence"], share, "data", ticket_key="Your ticket 1", flag_key="Flag 1")
    assert reply["confirmed"], reply["text"]


def test_doubt_phrasings_do_not_confirm_the_claim_they_deny():
    view = _view()
    for message in (
        "I don't believe no usable result (INV-NOR) and a mechanical problem (INV-MECH) make up most of the invalids",
        "It's not true that no usable result (INV-NOR) is the biggest",
        "We doubt INV-NOR and INV-MECH make up most of the invalids",
        "I don't believe. INV-NOR and INV-MECH make up most of the invalids",
        "The invalid rate is not increasing",
        "I don't think the rate is up",
    ):
        step = "data" if "rate" in message else "charts"
        reply = respond(message, view, step, ticket_key="Your ticket 1", flag_key="Flag 1")
        assert not reply["confirmed"], message
        assert reply["log_kind"] != "ticket", message
        assert not reply["text"].startswith("YEP"), message


def test_a_week_with_no_invalids_does_not_invent_a_majority():
    finding, body = part_fact({"code_shares": {}, "majority_codes": []}, "charts")
    assert finding == "no invalids in this slice"
    assert "no invalids" in body
    assert "make up most" not in body


def test_a_restated_note_with_a_wrong_number_or_a_moved_not_is_not_a_yep():
    view = _view()
    view.update(rate_label="0.97%")
    notes = (
        "Hello. The invalid rate this week is 0.97% (35 of 3600). We have not confirmed a cause. "
        "We recommend holding L-4419. We do not hold every group on this file."
    )
    view["notes"] = {**(view.get("notes") or {}), "customer": notes}
    for message in (
        "tell the customer the invalid rate this week is 50%",
        "tell the customer the invalid rate this week is 9.97%",
        "tell the customer we hold every group on this file, not L-4419",
        "the customer was told the invalid rate this week is 0.97% (35 of 9999)",
    ):
        reply = respond(message, view, "notes", ticket_key="Your ticket 1", flag_key="Flag 1")
        assert not reply["confirmed"], message
    reply = respond("tell the customer the invalid rate this week is 0.97%", view, "notes", ticket_key="Your ticket 1", flag_key="Flag 1")
    assert reply["confirmed"]


def test_pasting_one_on_screen_sentence_next_to_a_changed_one_does_not_confirm():
    view = _view()
    view["decision"] = "We opened the case. The leading read is no single group."
    for message in (
        "We closed the case. The leading read is no single group.",
        "We opened every case. The leading read is no single group.",
    ):
        reply = respond(message, view, "wrap", ticket_key="Your ticket 1", flag_key="Flag 1")
        assert not reply["confirmed"], message
        assert not reply["text"].startswith("YEP"), message
    reply = respond(
        "We opened the case. The leading read is no single group.",
        view,
        "wrap",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert reply["confirmed"]


def test_not_in_front_of_a_quoted_fact_does_not_confirm():
    view = _view()
    decision = "We opened the case. The leading read is no single group."
    view["decision"] = decision
    reply = respond(
        f"not {decision}",
        view,
        "wrap",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
    )
    assert not reply["confirmed"]
    assert reply["log_kind"] != "ticket"
    assert not reply["text"].startswith("YEP")
