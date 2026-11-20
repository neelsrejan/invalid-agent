"""The guided walk has a fixed order and does not invent a rate."""

from invalid_agent.data.query import SUGGESTED_QUESTIONS
from invalid_agent.ui.guide import (
    ARTIFACTS,
    AUDIENCES,
    GUIDE_STEPS,
    arrivals,
    cause_sentence,
    decision_for_week,
    progress_label,
    questions_for,
    rag_label,
    stratum_label,
)


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
    assert [label for _value, label in ARTIFACTS] == [
        "Triage memo",
        "Fishbone",
        "5 Whys",
        "8D / CAPA",
        "Plan and risks",
    ]
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


def test_ranker_sentence_uses_the_hypothesis_not_a_new_number():
    assert cause_sentence({"cause": "no_single_cause", "summary": "No group cleared the bar."}).startswith(
        "No single group stands out yet."
    )
    sentence = cause_sentence(
        {
            "cause": "bad_reagent_lot",
            "level": "L-4419",
            "lift": 12.0,
            "summary": "L-4419 bad reagent lot rate is above the complement with lift 12.00",
        }
    )
    assert "L-4419" in sentence
    assert "12.0" in sentence
    assert "times" in sentence
    assert "inf" not in sentence.casefold()


def test_week_story_reads_injections_and_the_decision_log():
    scenario = {
        "injections": [
            {"week": 0, "source": "customer", "audience": "customer"},
            {"week": 1, "source": "QA", "audience": "internal"},
        ]
    }
    assert arrivals(scenario, 1) == "What arrived this week: QA (internal)."
    assert arrivals(scenario, 4) == ""
    log = [{"week": 2, "decision": "Keep the field ranking."}]
    assert decision_for_week(log, 2) == "Keep the field ranking."
    assert decision_for_week(log, 0) == ""


def test_rag_comes_from_the_leadership_note():
    assert rag_label({"leadership": "Investigation week 3. RAG: Amber."}) == "Amber"
    assert rag_label({"leadership": "Investigation week 4. RAG: Green."}) == "Green"
    assert rag_label({"leadership": "Investigation week 0. RAG: Red."}) == "Red"
    assert rag_label({}) == "Red"


def test_stratum_label_prefers_the_case_file():
    assert stratum_label("manufacturer", {"strata_labels": {"manufacturer": "Manufacturer"}}) == "Manufacturer"
    assert stratum_label("reagent_lot", {}) == "reagent lot"
