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
    assert "Narrative" not in blob
    assert "Wilson" not in blob
    assert "deterministic" not in blob.casefold()
    assert "bad_reagent_lot" not in blob
    assert "/tmp" not in blob
    for item in sections:
        assert unexplained_jargon(item["what"]) == [], item["title"]
        assert unexplained_jargon(item["body"]) == [], item["body"][:240]
