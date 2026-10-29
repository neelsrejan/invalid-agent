"""The academy quiz checker must reject a bank a length guesser can pass."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "academy"))

from quiz_checks import assert_guessers, assert_uniform_options  # noqa: E402


def _lopsided_session() -> list[dict]:
    items = []
    for index in range(8):
        items.append(
            {
                "session": 1,
                "prompt": f"Why does widget {index} behave this way in the sample",
                "choices": [
                    {
                        "id": "a",
                        "text": "The right claim is deliberately much longer than every other option here.",
                    },
                    {"id": "b", "text": "Short."},
                    {"id": "c", "text": "Tiny."},
                    {"id": "d", "text": "No."},
                ],
                "correct": "a",
            }
        )
    return items


def test_lopsided_bank_fails_the_guesser_check():
    with pytest.raises(SystemExit, match="quiz guesser check failed"):
        assert_guessers(_lopsided_session())


def test_repeated_distractor_clause_fails_the_guesser_check():
    """The same clause on every wrong option is a tell, so the build must fail."""
    items = []
    for index in range(8):
        items.append(
            {
                "session": 2,
                "prompt": f"What does control {index} change in the sample flow",
                "choices": [
                    {"id": "a", "text": "The right claim stays specific to this control and this flow."},
                    {"id": "b", "text": f"The demo command is visible, plus detail {index} alpha here."},
                    {"id": "c", "text": f"The demo command is visible, plus detail {index} beta here."},
                    {"id": "d", "text": f"The demo command is visible, plus detail {index} gamma here."},
                ],
                "correct": "a",
            }
        )
    with pytest.raises(SystemExit, match="quiz guesser check failed"):
        assert_guessers(items)


def test_uniform_check_rejects_a_double_space():
    item = {
        "session": 1,
        "prompt": "Why",
        "choices": [
            {"id": "a", "text": "The  generated view prints the planted token."},
            {"id": "b", "text": "It hides the repository top from the tests."},
            {"id": "c", "text": "It lowercases the model tag on this host."},
            {"id": "d", "text": "The test runner blocks that view entirely."},
        ],
        "correct": "a",
    }
    with pytest.raises(SystemExit, match="double space"):
        assert_uniform_options([item])


def test_uniform_check_rejects_a_two_sentence_option():
    item = {
        "session": 1,
        "prompt": "Why",
        "choices": [
            {"id": "a", "text": "One claim only."},
            {"id": "b", "text": "Also one claim."},
            {"id": "c", "text": "Still one claim."},
            {"id": "d", "text": "First claim. Second claim."},
        ],
        "correct": "a",
    }
    with pytest.raises(SystemExit, match="not one sentence"):
        assert_uniform_options([item])
