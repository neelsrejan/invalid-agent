"""The guided walk has a fixed order and does not invent a rate."""

from invalid_agent.data.query import SUGGESTED_QUESTIONS
from invalid_agent.ui.guide import AUDIENCES, GUIDE_STEPS, progress_label, questions_for


def test_guided_steps_cover_the_investigation_in_order():
    assert [step.id for step in GUIDE_STEPS] == [
        "complaint",
        "data",
        "charts",
        "logged",
        "notes",
        "wrap",
    ]
    assert progress_label(1, 0) == "Week 1 of 4 — Part 1 of 6"
    assert progress_label(4, 5) == "Week 4 of 4 — Part 6 of 6"
    assert len({step.next_label for step in GUIDE_STEPS}) == len(GUIDE_STEPS)
    assert all(step.needs_case for step in GUIDE_STEPS)
    assert [value for value, _label in AUDIENCES] == ["customer", "internal", "leadership"]


def test_suggested_questions_follow_the_open_case():
    known = {item["id"] for item in SUGGESTED_QUESTIONS}
    for step in GUIDE_STEPS:
        assert set(step.question_ids) <= known
    chart = next(step for step in GUIDE_STEPS if step.id == "charts")
    assert [item["id"] for item in questions_for(chart, "OOI", SUGGESTED_QUESTIONS)] == ["ooi_share"]
    assert [item["id"] for item in questions_for(chart, "JJE", SUGGESTED_QUESTIONS)] == ["jje_weeks"]
    assert questions_for(chart, "", SUGGESTED_QUESTIONS) == []
    pitch = next(step for step in GUIDE_STEPS if step.id == "wrap")
    assert [item["id"] for item in questions_for(pitch, "OOI", SUGGESTED_QUESTIONS)] == [
        "ooi_share",
        "jje_manufacturer",
        "ooi_types",
        "jje_weeks",
    ]
