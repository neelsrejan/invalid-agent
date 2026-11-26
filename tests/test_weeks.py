"""Weeks 2-4 judge and guard, on the frozen JJE fixture."""

import json
import os

import pytest

from invalid_agent.ui.talkback import respond
from tests.test_jje_audit import _view

BANNED = ("YEP", "GOOD QUESTION", "NOT QUITE", "CLOSE", "Remember:", "Jira", "I can look up")
NAMES = ("Roche", "Abbott", "Siemens", "Beckman", "Binding", "INV-")


def _model(prose: str, meets: bool = True) -> str:
    return prose + "\n" + json.dumps({"meets_goal": meets, "reason": "checked", "companies": []})


class _Recorder:
    def __init__(self, text: str, model: str = "qwen/qwen3.8-27b"):
        self.text = text
        self.model = model
        self.calls: list[dict] = []

    def complete(self, *, system: str, user: str, temperature: float = 0.1, reasoning_effort: str = "low", timeout: float | None = None) -> str:
        self.calls.append(
            {"system": system, "user": user, "temperature": temperature, "reasoning_effort": reasoning_effort, "timeout": timeout}
        )
        return self.text


def _talk(step: str, text: str, client=None, week: int = 0) -> dict:
    weeks = {"pareto": 2, "responses": 3, "closeout": 4}
    view = _view(week or weeks[step])
    return respond(text, view, step, ticket_key="Your ticket 1", flag_key="Flag 1", tool_client=client)


def _locked(step: str, text: str) -> None:
    reply = _talk(step, text, _Recorder(_model("Agreed.")))
    assert reply["confirmed"] is False, text
    assert "Check the " in reply["text"]
    for name in NAMES:
        assert name not in reply["text"], (text, name)
    for banned in BANNED:
        assert banned not in reply["text"]


def test_week_two_paraphrases_unlock_and_the_wrong_set_stays_locked():
    prose = "Roche needs INV-MECH and INV-NOR. Abbott Labs needs INV-MECH. Siemens needs INV-MECH and INV-USR."
    client = _Recorder(_model(prose))
    reply = _talk(
        "pareto",
        "Roche's action items are a mechanical problem and no usable result. Abbott can use INV-MECH. Siemens needs INV-MECH and INV-USR.",
        client,
    )
    assert reply["confirmed"] is True
    assert reply["text"] == prose
    assert client.calls[0]["temperature"] == 0
    assert client.calls[0]["timeout"] == 15
    assert "INV-MECH" in client.calls[0]["user"]
    either = _talk(
        "pareto",
        "Roche needs INV-MECH and INV-NOR, Abbott Labs needs INV-SW, and Siemens needs INV-MECH and INV-USR.",
        _Recorder(_model(prose)),
    )
    assert either["confirmed"] is True
    for text in (
        "Roche needs INV-MECH, Abbott Labs needs INV-MECH, and Siemens needs INV-MECH and INV-USR.",
        "Roche needs INV-MECH and INV-NOR and INV-CAL, Abbott Labs needs INV-MECH, and Siemens needs INV-MECH and INV-USR.",
        "Roche needs INV-MECH and INV-NOR, Abbott Labs needs INV-MECH, Siemens needs INV-MECH and INV-USR, and Beckman needs INV-MECH.",
        "Roche isn't in the set. Abbott Labs needs INV-MECH. Siemens needs INV-MECH and INV-USR.",
        "Abbott Labs needs INV-MECH, and Siemens needs INV-MECH and INV-USR.",
    ):
        _locked("pareto", text)
    spared = _talk(
        "pareto",
        "Roche needs INV-MECH and INV-NOR, not INV-CAL. Abbott Labs needs INV-MECH. Siemens needs INV-MECH and INV-USR.",
        _Recorder(_model(prose)),
    )
    assert spared["confirmed"] is True


def test_week_three_guard_checks_codes_and_leaves_the_branch_to_the_judge():
    prose = "Each issue is on the notes."
    right = (
        "Roche INV-MECH is Machine, Roche INV-NOR is Material, Abbott Labs INV-MECH is Machine, "
        "Siemens INV-MECH is Machine, and Siemens INV-USR is Man."
    )
    reply = _talk("responses", right, _Recorder(_model(prose)))
    assert reply["confirmed"] is True
    assert reply["text"] == prose
    wrong_branch = right.replace("Siemens INV-USR is Man", "Siemens INV-USR is Machine")
    assert _talk("responses", wrong_branch, _Recorder(_model(prose, True)))["confirmed"] is True
    assert _talk("responses", right, _Recorder(_model(prose, False)))["confirmed"] is False
    for text in (
        "Roche INV-MECH is Machine, Abbott Labs INV-MECH is Machine, Siemens INV-MECH is Machine, and Siemens INV-USR is Man.",
        "Roche INV-MECH is Machine, Roche INV-NOR is Material, Abbott Labs INV-MECH is Machine, Siemens INV-MECH is Machine, Siemens INV-USR is Man, and Beckman INV-MECH is Machine.",
        "Roche and Abbott are over 1%, Siemens is not",
    ):
        _locked("responses", text)


def test_week_four_companies_unlock_and_an_extra_company_stays_locked():
    prose = "Each plan gets under 1%."
    reply = _talk(
        "closeout",
        "Roche, Abbott and Siemens get under 1% after the corrective action.",
        _Recorder(_model(prose)),
    )
    assert reply["confirmed"] is True
    assert reply["text"] == prose
    kept = _talk(
        "closeout",
        "Roche, Abbott and Siemens get under 1%, Beckman isn't",
        _Recorder(_model(prose)),
    )
    assert kept["confirmed"] is True
    for text in (
        "Roche and Abbott get under 1%",
        "Roche, Abbott and Siemens get under 1%, Beckman too.",
        "Roche and Abbott get under 1%, Siemens is not",
        "Roche and Abbott get under 1%, neither Siemens nor Beckman",
    ):
        _locked("closeout", text)


def test_a_question_does_not_unlock_and_an_invented_number_is_replaced():
    asked = _talk("pareto", "how many complaints are in the dataset", _Recorder(_model("There are 4221 reports.", False)))
    assert asked["confirmed"] is False
    assert "4221" in asked["text"]
    for banned in BANNED:
        assert banned not in asked["text"]
    invented = _talk(
        "closeout",
        "Roche, Abbott and Siemens get under 1%.",
        _Recorder(_model("Roche falls to 9.99%.", True)),
    )
    assert invented["confirmed"] is False
    assert "9.99" not in invented["text"]
    assert "Roche gets under 1%" in invented["text"]


def test_missing_model_answers_from_python(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    reply = _talk("pareto", "Roche needs INV-MECH and INV-NOR, Abbott Labs needs INV-MECH, and Siemens needs INV-MECH and INV-USR.")
    assert reply["confirmed"] is False
    assert "INV-MECH" in reply["text"]
    for banned in BANNED:
        assert banned not in reply["text"]
    counted = _talk("responses", "how many complaints are in the dataset")
    assert counted["confirmed"] is False
    assert "4221" in counted["text"]


@pytest.mark.skipif(not os.environ.get("GROQ_API_KEY"), reason="set GROQ_API_KEY to run the live week 2 check")
def test_live_week_two_sentence_unlocks():
    from invalid_agent.config import load_settings
    from invalid_agent.llm import GroqLLM

    settings = load_settings()
    client = GroqLLM(settings.groq_api_key, settings.week1_groq_model)
    reply = _talk(
        "pareto",
        "Roche needs INV-MECH and INV-NOR, Abbott Labs needs INV-MECH, and Siemens needs INV-MECH and INV-USR to get under 1%.",
        client,
    )
    assert reply["confirmed"] is True
    for banned in BANNED:
        assert banned not in reply["text"]
