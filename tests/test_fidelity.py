"""The guard rejects a planted rate and the node refuses to keep a lying draft."""

from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.llm import narrate
from invalid_agent.sim.generate import generate, load_scenario
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _facts():
    return {
        "overall": {"rate_pct": 3.67, "spec_pct": 2.0, "n": 14400, "k": 529, "confidence": 0.95},
        "week": 0,
        "lots": ["L-4419"],
    }


def test_guard_accepts_computed_numbers_and_rejects_an_invented_rate():
    facts = _facts()
    good = "The invalid rate is 3.67% versus a spec of 2.00% on 14400 runs (529 invalids). Week 0."
    bad = "The invalid rate is 27.40% versus a spec of 2.00% on 14400 runs."
    assert check_narrative(good, facts).ok
    rejected = check_narrative(bad, facts)
    assert rejected.ok is False
    assert 27.4 in rejected.unknown or 27.40 in rejected.unknown


def test_lot_identifier_is_not_scored_as_a_rate():
    facts = _facts()
    text = "Lot L-4419 is the leading stratum. The rate is 3.67%."
    assert check_narrative(text, facts).ok


class _Liar:
    name = "liar"

    def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
        del system, user, temperature
        return "The invalid rate is 27.40% and the spec is 2.00%."


def test_groq_paces_retries_and_replaces_an_empty_reply(monkeypatch):
    import httpx

    from invalid_agent.llm import GroqLLM

    GroqLLM._next_ok = 0.0
    sleeps: list[float] = []
    bodies: list[dict] = []

    class _Response:
        def __init__(self, code: int, content: str, retry_after: str = ""):
            self.status_code = code
            self._content = content
            self.headers = {"Retry-After": retry_after} if retry_after else {}

        def json(self):
            return {"choices": [{"message": {"content": self._content}}]}

        def raise_for_status(self):
            if self.status_code >= 400:
                request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
                response = httpx.Response(self.status_code, request=request)
                raise httpx.HTTPStatusError("limited", request=request, response=response)

    queue = [
        _Response(429, "", "3"),
        _Response(200, ""),
        _Response(200, "The note is ready."),
    ]

    def fake_post(url, headers=None, json=None, timeout=None):
        del url, headers, timeout
        bodies.append(dict(json or {}))
        return queue[len(bodies) - 1]

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr("time.sleep", lambda seconds: sleeps.append(seconds))
    text = GroqLLM("test-key", "openai/gpt-oss-20b").complete(system="sys", user="user")
    assert text == "The note is ready."
    assert bodies[0]["reasoning_effort"] == "low"
    assert bodies[0]["max_tokens"] == 2048
    assert bodies[-1]["max_tokens"] == 4096
    assert 3.0 in sleeps
    assert "test-key" not in str(bodies)


def test_status_batch_uses_one_hosted_call():
    from invalid_agent.llm import narrate_status

    class _Once:
        name = "hosted"
        calls = 0

        def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
            del system, user, temperature
            self.calls += 1
            return "<<<customer>>>\nNoted.\n<<<internal>>>\nNoted.\n<<<leadership>>>\nNoted.\n"

    model = _Once()
    result = narrate_status({"week": 0, "overall": {"n": 10, "k": 1, "rate": 0.1, "spec_invalid_rate": 0.02}}, model)
    assert model.calls == 1
    assert set(result) == {"customer", "internal", "leadership"}
    assert all(record["ok"] for _text, record in result.values())


def test_rejected_draft_is_replaced_by_the_template():
    scenario = load_scenario(ROOT / "scenarios" / "bad_lot.yaml")
    df = generate(scenario)
    from invalid_agent.metrics.hypotheses import rank_hypotheses
    from invalid_agent.nodes.triage import build_facts

    facts = build_facts(scenario, df, rank_hypotheses(df, 0.02))
    text, meta = narrate("triage", facts, _Liar())
    assert meta["rewritten"] is True
    assert meta["ok"] is False
    assert 27.4 not in meta["unknown"] or 27.4 in meta["unknown"]
    assert "27.40" not in text
    assert "Not for clinical use" in text
    assert check_narrative(text, facts).ok
