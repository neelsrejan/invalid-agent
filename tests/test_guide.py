"""The guided walk is four weeks, one page each."""

from invalid_agent.data.query import SUGGESTED_QUESTIONS
from invalid_agent.ui.guide import AUDIENCES, GUIDE_STEPS, progress_label, questions_for


def test_guided_steps_cover_the_investigation_in_order():
    assert [step.id for step in GUIDE_STEPS] == ["eda", "pareto", "responses", "closeout"]
    assert progress_label(1, 0) == "Week 1 of 4"
    assert progress_label(4, 0) == "Week 4 of 4"
    assert len({step.next_label for step in GUIDE_STEPS}) == len(GUIDE_STEPS)
    assert all(step.needs_case for step in GUIDE_STEPS)
    assert [value for value, _label in AUDIENCES] == ["customer", "internal", "leadership"]


def test_suggested_questions_follow_the_open_case():
    known = {item["id"] for item in SUGGESTED_QUESTIONS}
    for step in GUIDE_STEPS:
        assert set(step.question_ids) <= known
        assert questions_for(step, "JJE", SUGGESTED_QUESTIONS) == []
