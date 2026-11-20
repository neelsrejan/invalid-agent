"""A public-report deck does not pretend the file is a test-run rate."""

import re
from pathlib import Path

from pptx import Presentation

from invalid_agent.artifacts.deck import write_deck
from invalid_agent.ui.plain import PUBLIC_BANNER


def _facts() -> dict:
    return {
        "scenario_id": "openfda_ooi",
        "device": "OOI panel",
        "banner": PUBLIC_BANNER,
        "estimable": False,
        "rate_pct": 0.004,
        "k": 1,
        "n": 25000,
        "ci_low_pct": 0.001,
        "ci_high_pct": 0.02,
        "spec_pct": 2.0,
        "promised_pct": 98.0,
        "cause": "reported_manufacturer",
        "level": "ABBOTT",
        "category": "Leading group",
        "recommendation": "We do not hold one group.",
        "after_pct": 0.0,
        "label": "The what-if is a share of reports, not a repair.",
        "single": True,
        "cost": 85,
        "unit": 85,
        "d7": "Keep watching the file.",
        "chart": {
            "p_bar": 0.00004,
            "points": [
                {"period": "2024-01-07", "p": 0.00004, "ucl": 0.001, "lcl": 0.0},
            ],
            "violations": [],
        },
    }


def _slide_text(path: Path) -> str:
    presentation = Presentation(str(path))
    chunks: list[str] = []
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                chunks.append(shape.text_frame.text)
    return "\n".join(chunks)


def test_ooi_deck_says_share_of_reports(tmp_path):
    path = tmp_path / "exec_deck.pptx"
    write_deck(path, _facts())
    text = _slide_text(path)
    assert "Practice data" not in text
    assert "share of reports" in text.casefold()
    assert "Spec is" not in text
    assert "Wilson" not in text
    assert " of runs" not in text
    assert re.search(r"(?<![\d.])0\.00%", text) is None
    assert "under 0.01%" in text
    assert PUBLIC_BANNER.split(".")[0] in text
    assert "per invalid" not in text
    assert "reported_manufacturer" not in text
    assert "the company that made the device" in text
