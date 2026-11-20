"""Restored write-ups stay plain and say they cover the whole file."""

from pathlib import Path

from invalid_agent.graph import run_case
from invalid_agent.ui.plain import unexplained_jargon
from invalid_agent.ui.records import sections_from_run

ROOT = Path(__file__).resolve().parents[1]


def test_week_one_writeups_name_the_whole_file_and_drop_jargon(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    result = run_case(str(ROOT / "scenarios" / "bad_lot.yaml"), 1, tmp_path)
    sections = sections_from_run(result)
    blob = "\n".join(f"{item['what']}\n{item['body']}" for item in sections)
    assert "whole practice file" in blob
    assert "public report file" not in blob
    assert "Narrative" not in blob
    assert "Wilson" not in blob
    assert "deterministic" not in blob.casefold()
    assert "bad_reagent_lot" not in blob
    assert "/tmp" not in blob
    for item in sections:
        assert unexplained_jargon(item["what"]) == [], item["title"]
        assert unexplained_jargon(item["body"]) == [], item["body"][:240]


def test_a_public_writeup_names_the_public_report_file():
    result = {
        "triage_markdown": "The share of reports is the number on screen.",
        "fishbone": {"markdown": "Groups of possible causes."},
        "five_whys": {"markdown": "Why the share is high."},
        "capa": {"markdown": "The eight steps stay with the file."},
        "plan": {},
        "risks": [],
        "jira": {},
        "status_updates": {},
    }
    sections = sections_from_run(result, public=True)
    blob = "\n".join(f"{item['what']}\n{item['body']}" for item in sections)
    assert "whole public report file" in blob
    assert "practice" not in blob.casefold()


def test_run_case_with_an_explicit_model_does_not_change_the_backend(tmp_path, monkeypatch):
    import os

    monkeypatch.setenv("LLM_BACKEND", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key-not-real")
    from invalid_agent.llm import DeterministicLLM

    before = os.environ["LLM_BACKEND"]
    run_case(str(ROOT / "scenarios" / "bad_lot.yaml"), 1, tmp_path, llm=DeterministicLLM())
    assert os.environ["LLM_BACKEND"] == before == "groq"


def test_a_sentence_case_code_name_is_not_glossed_twice():
    from invalid_agent.ui.plain import gloss_once

    out = gloss_once("We found No usable result (INV-NOR) make up most of the invalids.", set())
    assert out.count("INV-NOR") == 1
    assert "(no usable result" not in out
