"""Language-model backends.

``deterministic`` fills a template and does not open a socket. That is the
default and the CI path. A hosted draft that fails the fidelity guard is
also replaced by the template. The public demo's configured backend is Groq.

``ollama`` talks to a local Ollama server (``LLM_MODEL``, default ``llama3.1:8b``).
``llamacpp`` loads a GGUF through ``llama-cpp-python``. The suggested small
file, for a local or self-hosted run, is Llama 3.2 1B.
``groq`` calls Groq's free hosted API (``GROQ_MODEL``, default
``openai/gpt-oss-20b``). That is the public-demo narrator. Streamlit
Community Cloud has no Ollama. Neither extra package is imported unless
that backend is selected. If the call fails or the fidelity
guard rejects the draft,
``narrate`` substitutes the template and records the rejection.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Protocol, runtime_checkable

from langchain_core.messages import HumanMessage, SystemMessage

from invalid_agent.config import Settings, load_settings
from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.narrative import SYSTEM_PROMPT, prompt_for, render


class LLM(Protocol):
    name: str

    def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str: ...


@runtime_checkable
class ToolCaller(Protocol):
    def select_tools(self, message: str, tools: list[dict[str, Any]]) -> list[dict[str, Any]]: ...

    def phrase(self, message: str, results: list[dict[str, Any]]) -> str: ...


def _chat_payload(system: str, user: str) -> list[dict[str, str]]:
    """Build role/content pairs via LangChain messages so the prompt has one shape."""
    system_message = SystemMessage(content=system)
    human_message = HumanMessage(content=user)
    role = {"system": "system", "human": "user"}
    return [
        {"role": role[system_message.type], "content": str(system_message.content)},
        {"role": role[human_message.type], "content": str(human_message.content)},
    ]


class DeterministicLLM:
    name = "deterministic"

    def complete(self, *, system: str, user: str, temperature: float = 0.0) -> str:
        del system, user, temperature
        raise RuntimeError("DeterministicLLM does not generate free text. Use narrate().")


class OllamaLLM:
    name = "ollama"

    def __init__(self, host: str, model: str) -> None:
        self.host = host.rstrip("/")
        self.model = model

    def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
        import httpx

        response = httpx.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": _chat_payload(system, user),
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=180.0,
        )
        response.raise_for_status()
        return str(response.json()["message"]["content"])


class GroqLLM:
    """Hosted free-tier narrator. The key stays in the Authorization header.

    Calls are spaced by two seconds across the process, so concurrent
    Streamlit sessions share one clock. A 429 waits for Retry-After, or two
    seconds when that header is missing. The waits in one call stop at 15
    seconds and the caller falls back to the template. An empty gpt-oss reply
    is retried once with a larger max_tokens. reasoning_effort stays low so
    the free token budget is not spent on hidden reasoning.
    """

    name = "groq"
    _pace_lock = threading.Lock()
    _next_ok = 0.0
    _min_interval = 2.0
    _max_retry_wait = 15.0

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is empty. Create a free key at https://console.groq.com/keys "
                "(no credit card on the free plan) and export GROQ_API_KEY. "
                "The public demo does not silently switch to the deterministic template "
                "when the hosted key is missing. CI sets LLM_BACKEND=deterministic and does not need the key."
            )
        self._api_key = api_key
        self.model = model or "openai/gpt-oss-20b"

    def _pace(self) -> None:
        import time

        with self._pace_lock:
            wait = GroqLLM._next_ok - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            GroqLLM._next_ok = time.monotonic() + self._min_interval

    def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
        import time

        import httpx

        from invalid_agent.config import GROQ_CHAT_URL

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": _chat_payload(system, user),
            "temperature": temperature,
            "max_tokens": 2048,
            "reasoning_effort": "low",
        }
        empty_retried = False
        waited = 0.0
        response: Any = None
        for attempt in range(4):
            self._pace()
            response = httpx.post(
                GROQ_CHAT_URL,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=180.0,
            )
            if response.status_code == 429 and attempt < 3:
                delay = _retry_after_seconds(response.headers)
                if waited + delay > self._max_retry_wait:
                    raise RuntimeError(
                        "Groq retry wait would exceed 15 seconds. Falling back to the template."
                    )
                time.sleep(delay)
                waited += delay
                continue
            response.raise_for_status()
            content = str(response.json()["choices"][0]["message"].get("content") or "")
            if content.strip():
                return content
            if empty_retried:
                raise RuntimeError("Groq returned an empty reply")
            empty_retried = True
            payload["max_tokens"] = 4096
        raise RuntimeError("Groq returned an empty reply")

    def select_tools(self, message: str, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        import json

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Choose the tools that answer the question about this week's complaint data. "
                        "Do not invent numbers. If none of the tools fit, call none."
                    ),
                },
                {"role": "user", "content": message},
            ],
            "tools": [{"type": "function", "function": spec} for spec in tools],
            "tool_choice": "auto",
            "temperature": 0,
            "max_tokens": 400,
        }
        message_obj = self._message(payload)
        picked: list[dict[str, Any]] = []
        for call in message_obj.get("tool_calls") or []:
            function = call.get("function") or {}
            raw = function.get("arguments") or "{}"
            if isinstance(raw, str):
                try:
                    arguments = json.loads(raw) if raw.strip() else {}
                except json.JSONDecodeError:
                    arguments = {}
            elif isinstance(raw, dict):
                arguments = raw
            else:
                arguments = {}
            if not isinstance(arguments, dict):
                arguments = {}
            name = str(function.get("name") or "")
            if name:
                picked.append({"name": name, "arguments": arguments})
        return picked

    def phrase(self, message: str, results: list[dict[str, Any]]) -> str:
        import json

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Write one or two short sentences a high school reader can follow. "
                        "Use only numbers that appear in the tool results. Do not add a count."
                    ),
                },
                {"role": "user", "content": json.dumps({"question": message, "results": results})},
            ],
            "temperature": 0,
            "max_tokens": 300,
        }
        return str(self._message(payload).get("content") or "").strip()

    def _message(self, payload: dict[str, Any]) -> dict[str, Any]:
        import time

        import httpx

        from invalid_agent.config import GROQ_CHAT_URL

        waited = 0.0
        response: Any = None
        for attempt in range(4):
            self._pace()
            response = httpx.post(
                GROQ_CHAT_URL,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=60.0,
            )
            if response.status_code == 429 and attempt < 3:
                delay = _retry_after_seconds(response.headers)
                if waited + delay > self._max_retry_wait:
                    raise RuntimeError("Groq retry wait would exceed 15 seconds.")
                time.sleep(delay)
                waited += delay
                continue
            response.raise_for_status()
            return dict(response.json()["choices"][0]["message"])
        raise RuntimeError("Groq returned no tool message")


class LlamaCppLLM:
    name = "llamacpp"

    def __init__(self, model_path: str) -> None:
        if not model_path:
            raise FileNotFoundError(
                "LLAMACPP_MODEL_PATH is empty. Point it at a Llama 3.2 1B GGUF, "
                "or leave LLM_BACKEND=deterministic."
            )
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError(
                "llama-cpp-python is not installed. The deterministic backend is the supported fallback."
            ) from exc
        self._llama = Llama(model_path=model_path, n_ctx=4096, n_threads=2, verbose=False)

    def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str:
        result = self._llama.create_chat_completion(
            messages=_chat_payload(system, user),
            temperature=temperature,
        )
        return str(result["choices"][0]["message"]["content"])


def _retry_after_seconds(headers: Any) -> float:
    raw = ""
    getter = getattr(headers, "get", None)
    if getter is not None:
        raw = str(getter("Retry-After", "") or getter("retry-after", "") or "")
    try:
        delay = float(raw)
    except (TypeError, ValueError):
        return 2.0
    if delay < 0:
        return 2.0
    return delay


_llm_override: ContextVar[LLM | None] = ContextVar("invalid_agent_llm_override", default=None)


@contextmanager
def using_llm(llm: LLM):
    """Use ``llm`` for ``get_llm()`` on this thread until the block ends."""
    token = _llm_override.set(llm)
    try:
        yield
    finally:
        _llm_override.reset(token)


def get_llm(settings: Settings | None = None) -> LLM:
    override = _llm_override.get()
    if override is not None:
        return override
    settings = settings or load_settings()
    if settings.llm_backend == "ollama":
        return OllamaLLM(settings.ollama_host, settings.llm_model)
    if settings.llm_backend == "llamacpp":
        return LlamaCppLLM(settings.llamacpp_model_path)
    if settings.llm_backend == "groq":
        return GroqLLM(settings.groq_api_key, settings.groq_model)
    return DeterministicLLM()


def narrate(task: str, facts: dict[str, Any], llm: LLM | None = None) -> tuple[str, dict[str, Any]]:
    """Return prose plus a fidelity record.

    The deterministic backend returns the template directly. Any other
    backend is checked. A failed check, an empty draft, or a transport
    error is replaced by the template. The caller shows the replacement,
    not the rejected draft.
    """
    llm = llm or get_llm()
    safe = render(task, facts)
    if llm.name == "deterministic":
        check = check_narrative(safe, facts)
        text = safe + "\n_Narrative source: deterministic template._\n"
        return text, {
            "ok": check.ok,
            "backend": llm.name,
            "unknown": check.unknown,
            "rewritten": False,
            "error": "",
        }
    error = ""
    draft = ""
    try:
        draft = llm.complete(system=SYSTEM_PROMPT, user=prompt_for(task, facts), temperature=0.1)
    except Exception as exc:  # network, missing model, parse error from the server
        error = f"{type(exc).__name__}: {exc}"
    check = check_narrative(draft, facts) if draft else None
    if check is not None and check.ok:
        text = draft.rstrip() + "\n\n_Narrative source: model draft accepted by the numeric-fidelity check._\n"
        return text, {
            "ok": True,
            "backend": llm.name,
            "unknown": [],
            "rewritten": False,
            "error": "",
        }
    text = safe + "\n_Narrative source: deterministic template. The model draft was rejected or unavailable._\n"
    return text, {
        "ok": False,
        "backend": llm.name,
        "unknown": [] if check is None else check.unknown,
        "rewritten": True,
        "error": error,
    }


_STATUS_AUDIENCES = (
    ("customer", "status_customer"),
    ("internal", "status_internal"),
    ("leadership", "status_leadership"),
)


def narrate_status(facts: dict[str, Any], llm: LLM | None = None) -> dict[str, tuple[str, dict[str, Any]]]:
    """Three audience notes.

    The deterministic backend still renders each template. A hosted model
    gets one call for all three, so a week-4 replay stays near six calls
    instead of sixteen.
    """
    llm = llm or get_llm()
    if llm.name == "deterministic":
        return {audience: narrate(task, facts, llm) for audience, task in _STATUS_AUDIENCES}
    draft = ""
    error = ""
    try:
        draft = llm.complete(
            system=(
                SYSTEM_PROMPT
                + " Do not say the rate exceeds or stays within the spec unless FACTS shows that comparison."
            ),
            user=(
                "Write three notes from the same FACTS: customer, internal, and leadership.\n"
                "Start each note with its marker on its own line, exactly:\n"
                "<<<customer>>>\n<<<internal>>>\n<<<leadership>>>\n"
                + prompt_for("status", facts)
            ),
            temperature=0.1,
        )
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    sections = _split_status(draft)
    rendered: dict[str, tuple[str, dict[str, Any]]] = {}
    for audience, task in _STATUS_AUDIENCES:
        section = sections.get(audience, "")
        check = check_narrative(section, facts) if section else None
        if check is not None and check.ok:
            text = section.rstrip() + "\n\n_Narrative source: model draft accepted by the numeric-fidelity check._\n"
            rendered[audience] = (
                text,
                {"ok": True, "backend": llm.name, "unknown": [], "rewritten": False, "error": ""},
            )
            continue
        safe = render(task, facts)
        text = safe + "\n_Narrative source: deterministic template. The model draft was rejected or unavailable._\n"
        rendered[audience] = (
            text,
            {
                "ok": False,
                "backend": llm.name,
                "unknown": [] if check is None else check.unknown,
                "rewritten": True,
                "error": error,
            },
        )
    return rendered


def _split_status(draft: str) -> dict[str, str]:
    import re

    matches = list(re.finditer(r"<<<(customer|internal|leadership)>>>", draft))
    parts: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(draft)
        parts[match.group(1)] = draft[start:end].strip()
    return parts
