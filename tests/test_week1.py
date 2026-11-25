import json
import os
from pathlib import Path

import pandas as pd
import pytest

from invalid_agent.data.frame import frame_from_reports
from invalid_agent.data.mapping import primary_invalid_code
from invalid_agent.sim.generate import load_scenario
from invalid_agent.ui.story import build_week_view
from invalid_agent.ui.talkback import respond

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "openfda_jje.csv"
NEEL = (
    "Roche, abbott and siemens have enough data to reliably say that "
    "there is an invalid issue in the field."
)
BANNED = ("YEP", "GOOD QUESTION", "NOT QUITE", "CLOSE", "Remember:", "Jira", "I can look up")


def _view() -> dict:
    raw = pd.read_csv(FIXTURE, dtype=str).fillna("")
    records = []
    for row in raw.to_dict(orient="records"):
        labels = [part.strip() for part in str(row["product_problems"]).split("|") if part.strip()]
        assert primary_invalid_code(labels) == str(row["invalid_code"])
        row["product_problems"] = labels
        records.append(row)
    scenario = load_scenario(ROOT / "cases" / "openfda_jje.yaml")
    return build_week_view(scenario, frame_from_reports(records, scenario), 1)


def _model(prose: str, meets: bool, companies: list[str], reason: str = "names the flagged companies") -> str:
    payload = {"meets_goal": meets, "reason": reason, "companies": companies}
    return prose + "\n" + json.dumps(payload)


class _Recorder:
    def __init__(self, text: str, model: str = "qwen/qwen3.8-27b"):
        self.text = text
        self.model = model
        self.calls: list[dict] = []
        self.tools = 0

    def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.1,
        reasoning_effort: str = "low",
        timeout: float | None = None,
    ) -> str:
        self.calls.append(
            {
                "system": system,
                "user": user,
                "temperature": temperature,
                "reasoning_effort": reasoning_effort,
                "timeout": timeout,
            }
        )
        return self.text

    def select_tools(self, message, tools):
        del message, tools
        self.tools += 1
        return []

    def phrase(self, message, results):
        del message, results
        return "phrased"


class _Down:
    model = "qwen/qwen3.8-27b"

    def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.1,
        reasoning_effort: str = "low",
        timeout: float | None = None,
    ) -> str:
        del system, user, temperature, reasoning_effort, timeout
        raise RuntimeError("model down")


def _talk(text: str, client=None) -> dict:
    return respond(text, _view(), "eda", ticket_key="Your ticket 1", flag_key="Flag 1", tool_client=client)


def _assert_raw(reply: dict, prose: str) -> None:
    assert reply["text"] == prose
    assert reply["log_text"] == prose
    for banned in BANNED:
        assert banned not in reply["text"]


def test_neel_sentence_and_paraphrases_unlock_from_recorded_model_output():
    flagged = ["Roche", "Abbott Labs", "Siemens"]
    cases = [
        (NEEL, ["roche", "abbott", "siemens"], "Roche, Abbott Labs, and Siemens have enough reports to call an invalid issue."),
        (
            "Roche, Abbott Labs, and Siemens are over the 1% line.",
            flagged,
            "Roche, Abbott Labs, and Siemens are over the 1% line with enough reports.",
        ),
        (
            "roche, abbott and siemens have enough N",
            ["ROCHE", "Abbott", "SIEMENS"],
            "Roche, Abbott Labs, and Siemens are the ones with enough N.",
        ),
        (
            "The firms over the line are Roche, Abbott and Siemens",
            ["Roche", "abbott labs", "Siemens"],
            "Roche, Abbott Labs, and Siemens are over 1%.",
        ),
        (
            "siemens abbott and roche clear 1% and have enough reports",
            ["Siemens", "abbott", "Roche"],
            "Siemens, Abbott Labs, and Roche clear 1% and each has enough reports.",
        ),
        (
            "Roche 81 of 2249, Abbott Labs 10 of 748, Siemens 13 of 485",
            ["abbott", "roche", "siemens"],
            "Roche is 3.60% (81 of 2249), Abbott Labs is 1.34% (10 of 748), and Siemens is 2.68% (13 of 485).",
        ),
    ]
    assert len(cases) >= 6
    for text, companies, prose in cases:
        client = _Recorder(_model(prose, True, companies))
        reply = _talk(text, client)
        assert reply["confirmed"] is True, text
        _assert_raw(reply, prose)
        assert len(client.calls) == 1
        assert client.tools == 0
        call = client.calls[0]
        assert call["temperature"] == 0
        assert call["reasoning_effort"] == "none"
        assert call["timeout"] == 15
        assert text in call["user"]
        assert "81" in call["user"] and "2249" in call["user"]
        assert "13" in call["user"] and "485" in call["user"]
        assert "10" in call["user"] and "748" in call["user"]
        assert "product_problems" not in call["user"]
        assert len(call["user"]) < 8000
        assert "N >= 100" in call["system"]
        assert "too few" in call["system"]


def test_wrong_company_set_binding_site_and_invented_numbers_do_not_unlock():
    right = ["Roche", "Abbott Labs", "Siemens"]
    prose = "Roche, Abbott Labs, and Siemens are over 1%."
    wrong = _Recorder(_model(prose, True, ["Roche", "Beckman"]))
    reply = _talk("Roche and Beckman are over 1% with enough reports.", wrong)
    assert reply["confirmed"] is False
    assert reply["text"] == prose

    binding = _Recorder(_model(prose, True, right + ["The Binding Site"]))
    reply = _talk("Roche, Abbott, Siemens, and Binding Site are over 1%.", binding)
    assert reply["confirmed"] is False

    invented = "Roche is at 9.99% (99 of 2249)."
    bad = _Recorder(_model(invented, True, right))
    reply = _talk("Roche is at 9.99% (99 of 2249) so it is over the line.", bad)
    assert reply["confirmed"] is False
    assert "9.99" not in reply["text"]
    assert "99 of 2249" not in reply["text"]
    assert "Roche, Abbott Labs, and Siemens are over 1%." in reply["text"]

    question = _Recorder(
        _model("This file has 4221 complaints.", False, right, reason="this is a question")
    )
    reply = _talk("how many complaints are in the dataset", question)
    assert reply["confirmed"] is False
    assert "4221" in reply["text"]


def test_empty_week1_reply_has_no_wrapper():
    reply = respond("   ", _view(), "eda", ticket_key="Your ticket 1", flag_key="Flag 1")
    assert reply["confirmed"] is False
    assert reply["text"] == "Type a question, or type what you think the screen is saying."
    for banned in BANNED:
        assert banned not in reply["text"]


def test_unrecognized_question_stays_on_the_table_and_skips_the_menu():
    from invalid_agent.ui.explore import answer_message
    from invalid_agent.ui.week1 import python_sentence

    view = _view()
    facts = view["explore"]
    unknown = "what should I have for lunch"
    assert "I can look up" in answer_message(unknown, view)
    sentence = python_sentence(unknown, facts)
    assert sentence == "Roche, Abbott Labs, and Siemens are over 1%."
    assert "I can look up" not in sentence
    counted = python_sentence("how many complaints are in the dataset", facts)
    assert counted.startswith("This file has 4221")
    flagged = python_sentence("which companies are over 1%", facts)
    assert flagged.startswith("Over 1% with enough reports: Roche")
    assert "The Binding Site" in flagged


def test_lying_model_leaves_next_locked():
    from invalid_agent.ui.talkback import accepted_signatures

    prose = "Roche, Abbott Labs, and Siemens are over 1%."
    flagged = ["Roche", "Abbott Labs", "Siemens"]
    view = _view()
    liar = _Recorder(_model(prose, True, flagged))
    reply = respond(
        "Roche and Beckman",
        view,
        "eda",
        ticket_key="Your ticket 1",
        flag_key="Flag 1",
        tool_client=liar,
    )
    assert reply["confirmed"] is False
    assert "the companies over 1%" in accepted_signatures(view, "eda")
    assert reply["text"] == prose

    excused = (
        "Roche, abbott and siemens have enough data to call an invalid issue. "
        "Binding Site has too few reports to judge."
    )
    reply = _talk(excused, _Recorder(_model(prose, True, flagged)))
    assert reply["confirmed"] is True
    assert reply["text"] == prose

    kept = _Recorder(_model(prose + " A side count is 2 of 3.", True, flagged))
    reply = _talk(NEEL, kept)
    assert reply["confirmed"] is True
    assert "2 of 3" in reply["text"]

    cited = _Recorder(_model("The Binding Site is 2 of 3. " + prose, True, flagged))
    reply = _talk(NEEL, cited)
    assert reply["confirmed"] is False
    assert "2 of 3" not in reply["text"]


def test_missing_model_answers_from_python_and_does_not_unlock(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    fallback_calls: list[dict] = []

    class _Fallback:
        model = "openai/gpt-oss-20b"

        def complete(self, **kwargs):
            fallback_calls.append(kwargs)
            raise RuntimeError("fallback down")

    monkeypatch.setattr("invalid_agent.ui.week1._fallback_client", lambda client: _Fallback())
    reply = _talk(NEEL)
    assert reply["confirmed"] is False
    assert "Roche, Abbott Labs, and Siemens are over 1%." in reply["text"]
    for banned in BANNED:
        assert banned not in reply["text"]
    counted = _talk("how many complaints are in the dataset")
    assert counted["confirmed"] is False
    assert "4221" in counted["text"]
    assert "I can look up" not in counted["text"]
    down = _talk("which companies are over 1%", _Down())
    assert down["confirmed"] is False
    assert "Roche" in down["text"]
    assert "I can look up" not in down["text"]
    assert fallback_calls
    assert fallback_calls[0]["timeout"] == 15


@pytest.mark.skipif(not os.environ.get("GROQ_API_KEY"), reason="set GROQ_API_KEY to run the live week 1 check")
def test_live_neel_sentence_unlocks():
    from invalid_agent.config import load_settings
    from invalid_agent.llm import GroqLLM

    settings = load_settings()
    client = GroqLLM(settings.groq_api_key, settings.week1_groq_model)
    reply = _talk(NEEL, client)
    assert reply["confirmed"] is True
    for banned in BANNED:
        assert banned not in reply["text"]
