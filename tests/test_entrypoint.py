"""The root Streamlit entrypoint has to render week 1, including after a stale import."""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_OLD_CRUMB = (
    "Complaint · Case · Control chart · Pareto · Strata · "
    "Before / after · Artifacts · Status notes · Jira · Pitch"
)


def _visible(app) -> str:
    chunks = []
    for name in ("markdown", "caption", "header", "subheader", "title", "text", "info", "warning", "error"):
        for item in getattr(app, name, []):
            chunks.append(str(getattr(item, "value", "")))
    return "\n".join(chunk for chunk in chunks if chunk)


def _boot(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("DATA_BACKEND", "synthetic")
    monkeypatch.setenv("LLM_BACKEND", "deterministic")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=180)
    app.run()
    return app


def _saved_imports():
    modules = {
        name: sys.modules[name]
        for name in list(sys.modules)
        if name == "invalid_agent" or name.startswith("invalid_agent.")
    }
    return modules, list(sys.meta_path)


def _restore_imports(modules, meta_path) -> None:
    sys.meta_path[:] = meta_path
    for name in list(sys.modules):
        if name == "invalid_agent" or name.startswith("invalid_agent."):
            del sys.modules[name]
    sys.modules.update(modules)


def test_root_entrypoint_renders_week_one(monkeypatch):
    saved = _saved_imports()
    try:
        app = _boot(monkeypatch)
        assert not app.exception, app.exception
        text = _visible(app)
        assert "Week 1 of 4" in text
        assert _OLD_CRUMB not in text
    finally:
        _restore_imports(*saved)


def test_stale_guide_still_renders_week_one(monkeypatch):
    """A long-lived Streamlit process keeps the pre-rewrite guide in sys.modules.

    That module's progress_label takes the step index only, and its crumb is the
    old ten-step line. The root entrypoint has to load the guide from this
    checkout instead of crashing on progress_label(week, beat).
    """
    saved = _saved_imports()
    try:
        guide = types.ModuleType("invalid_agent.ui.guide")
        guide.__file__ = str(ROOT / "src" / "invalid_agent" / "ui" / "guide.py")

        class GuideStep:
            def __init__(self, short: str) -> None:
                self.short = short
                self.title = short
                self.id = "complaint"
                self.doing = "Reads the complaint."
                self.why = "So the numbers have a promise to compare with."
                self.look = "Read the promise."
                self.next_label = "Next"
                self.needs_case = True
                self.question_ids = ()
                self.match_case = True

        guide.GuideStep = GuideStep
        guide.GUIDE_STEPS = tuple(GuideStep(short) for short in _OLD_CRUMB.split(" · "))
        guide.AUDIENCES = ()

        def progress_label(index: int) -> str:
            return f"Step {index + 1} of 10"

        guide.progress_label = progress_label
        sys.modules["invalid_agent.ui.guide"] = guide
        app = _boot(monkeypatch)
        assert not app.exception, app.exception
        text = _visible(app)
        assert "Week 1 of 4" in text
        assert _OLD_CRUMB not in text
        assert "Step 1 of 10" not in text
    finally:
        _restore_imports(*saved)
