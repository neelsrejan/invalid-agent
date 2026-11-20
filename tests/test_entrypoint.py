"""The root Streamlit entrypoint has to render week 1, including after a stale import."""

import importlib.util
import inspect
import sys
from dataclasses import replace
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


def test_file_watcher_polls_so_a_deploy_drops_stale_modules():
    text = (ROOT / ".streamlit" / "config.toml").read_text()
    assert 'fileWatcherType = "poll"' in text
    assert 'fileWatcherType = "none"' not in text


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


def _load_fixture(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_stale_guide_outside_the_checkout_still_renders_week_one(monkeypatch):
    """The real pre-rewrite guide, loaded from outside this source tree, is evicted.

    The fixture is the guide from commit cfd403f, the parent of the week rewrite.
    Its progress_label takes one argument. The page has to load the checkout copy.
    """
    saved = _saved_imports()
    try:
        _load_fixture("invalid_agent.ui.guide", ROOT / "tests" / "fixtures" / "pre_pr9_guide.py")
        app = _boot(monkeypatch)
        assert not app.exception, app.exception
        text = _visible(app)
        assert "Week 1 of 4" in text
        assert _OLD_CRUMB not in text
        assert "Step 1 of 10" not in text
    finally:
        _restore_imports(*saved)


def test_a_step_rename_in_memory_does_not_reload_every_run():
    import invalid_agent.fresh as fresh
    import invalid_agent.ui.guide as guide

    saved_steps = guide.GUIDE_STEPS
    saved_stamps = dict(fresh._STAMPS)
    identity = id(guide)
    try:
        fresh.note_imports()
        guide.GUIDE_STEPS = (replace(guide.GUIDE_STEPS[0], short="Renamed"),) + guide.GUIDE_STEPS[1:]
        assert fresh.ensure_checkout(ROOT / "src") is False
        assert fresh.ensure_checkout(ROOT / "src") is False
        assert id(guide) == identity
        assert guide.GUIDE_STEPS[0].short == "Renamed"
    finally:
        guide.GUIDE_STEPS = saved_steps
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)


def test_a_stale_charts_module_outside_src_is_replaced_by_the_checkout():
    import invalid_agent.fresh as fresh

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh.note_imports()
        old = _load_fixture(
            "invalid_agent.artifacts.charts",
            ROOT / "tests" / "fixtures" / "pre_pr9_charts.py",
        )
        assert "y_title" not in inspect.signature(old.p_chart_figure).parameters
        assert fresh.ensure_checkout(ROOT / "src") is True
        charts = importlib.import_module("invalid_agent.artifacts.charts")
        assert "y_title" in inspect.signature(charts.p_chart_figure).parameters
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)


def test_a_current_module_without_a_stamp_is_kept():
    """The suite's already-imported modules match the files. A boot must not replace them."""
    import invalid_agent.fresh as fresh
    import invalid_agent.ui.plain as plain

    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh._STAMPS.clear()
        assert hasattr(plain, "gloss_once")
        assert fresh.ensure_checkout(ROOT / "src") is False
        assert sys.modules["invalid_agent.ui.plain"] is plain
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)


def test_an_unstamped_module_without_bytecode_is_still_dropped():
    import types

    import invalid_agent.fresh as fresh

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh._STAMPS.clear()
        stub = types.ModuleType("invalid_agent.ui.plain")
        stub.__file__ = str(ROOT / "src" / "invalid_agent" / "ui" / "plain.py")
        sys.modules["invalid_agent.ui.plain"] = stub
        assert fresh.ensure_checkout(ROOT / "src") is True
        assert "invalid_agent.ui.plain" not in sys.modules
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)


def test_an_unstamped_module_with_a_newer_pyc_is_still_dropped(tmp_path):
    import os
    import types

    import invalid_agent.fresh as fresh

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh._STAMPS.clear()
        source = ROOT / "src" / "invalid_agent" / "ui" / "plain.py"
        newer = tmp_path / "plain.pyc"
        newer.write_bytes(b"")
        os.utime(newer, (source.stat().st_mtime + 60, source.stat().st_mtime + 60))
        stub = types.ModuleType("invalid_agent.ui.plain")
        stub.__file__ = str(source)
        stub.__cached__ = str(newer)
        sys.modules["invalid_agent.ui.plain"] = stub
        assert fresh.ensure_checkout(ROOT / "src") is True
        assert "invalid_agent.ui.plain" not in sys.modules
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)


def test_pr10_modules_without_bytecode_boot_without_an_import_error(monkeypatch):
    """Python -B never writes a .pyc, so the old module has no bytecode to compare."""
    import types

    import invalid_agent.fresh as fresh

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh._STAMPS.clear()
        for module_name, relative in (
            ("invalid_agent.ui.plain", "src/invalid_agent/ui/plain.py"),
            ("invalid_agent.ui.talkback", "src/invalid_agent/ui/talkback.py"),
        ):
            stub = types.ModuleType(module_name)
            stub.__file__ = str(ROOT / relative)
            sys.modules[module_name] = stub
        app = _boot(monkeypatch)
        assert not app.exception, app.exception
        assert "ImportError" not in _visible(app)
        assert "Week 1 of 4" in _visible(app)
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)


def test_pr10_era_modules_boot_without_an_import_error(monkeypatch, tmp_path):
    """A process still holding the PR #10 modules has no stamps and no new names."""
    import os
    import types

    import invalid_agent.fresh as fresh

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh._STAMPS.clear()
        for module_name, relative in (
            ("invalid_agent.ui.plain", "src/invalid_agent/ui/plain.py"),
            ("invalid_agent.ui.talkback", "src/invalid_agent/ui/talkback.py"),
        ):
            source = ROOT / relative
            stub = types.ModuleType(module_name)
            stub.__file__ = str(source)
            old_pyc = tmp_path / f"{module_name}.pyc"
            old_pyc.write_bytes(b"")
            older = source.stat().st_mtime - 60
            os.utime(old_pyc, (older, older))
            stub.__cached__ = str(old_pyc)
            sys.modules[module_name] = stub
        assert not hasattr(sys.modules["invalid_agent.ui.plain"], "gloss_once")
        assert not hasattr(sys.modules["invalid_agent.ui.talkback"], "part_fact")
        app = _boot(monkeypatch)
        assert not app.exception, app.exception
        assert "ImportError" not in _visible(app)
        assert "Week 1 of 4" in _visible(app)
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)


def test_a_module_replaced_before_the_first_stamp_is_dropped(tmp_path):
    """A deploy into a process whose page predates fresh.py: nothing is stamped yet."""
    import os
    import invalid_agent.fresh as fresh
    import invalid_agent.ui.plain as plain

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    saved_cached = plain.__cached__
    try:
        fresh._STAMPS.clear()
        old_pyc = tmp_path / "plain.pyc"
        old_pyc.write_bytes(b"")
        source_mtime = Path(plain.__file__).stat().st_mtime
        os.utime(old_pyc, (source_mtime - 60, source_mtime - 60))
        plain.__cached__ = str(old_pyc)
        assert fresh.ensure_checkout(ROOT / "src") is True
        assert "invalid_agent.ui.plain" not in sys.modules
    finally:
        plain.__cached__ = saved_cached
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)


def test_a_file_changed_in_place_drops_the_package():
    import invalid_agent.fresh as fresh
    import invalid_agent.ui.plain  # noqa: F401

    saved = _saved_imports()
    saved_stamps = dict(fresh._STAMPS)
    try:
        fresh.note_imports()
        fresh._STAMPS["invalid_agent.ui.plain"] -= 60.0
        assert fresh.ensure_checkout(ROOT / "src") is True
        assert "invalid_agent.ui.plain" not in sys.modules
    finally:
        fresh._STAMPS.clear()
        fresh._STAMPS.update(saved_stamps)
        _restore_imports(*saved)
