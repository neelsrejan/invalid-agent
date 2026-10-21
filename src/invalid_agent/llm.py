"""Language-model backends.

``deterministic`` fills a template and does not open a socket. That is the
default, the CI path, and the hosted-demo fallback.

``ollama`` talks to a local Ollama server (intended model ``llama3.1:8b``).
``llamacpp`` loads a GGUF through ``llama-cpp-python`` (intended model
Llama 3.2 1B). Neither package is imported unless that backend
is selected. If the call fails or the fidelity guard rejects the draft,
``narrate`` substitutes the template and records the rejection.
"""

from __future__ import annotations

from typing import Any, Protocol

from langchain_core.messages import HumanMessage, SystemMessage

from invalid_agent.config import Settings, load_settings
from invalid_agent.guards.numeric_fidelity import check_narrative
from invalid_agent.narrative import SYSTEM_PROMPT, prompt_for, render


class LLM(Protocol):
    name: str

    def complete(self, *, system: str, user: str, temperature: float = 0.1) -> str: ...


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


def get_llm(settings: Settings | None = None) -> LLM:
    settings = settings or load_settings()
    if settings.llm_backend == "ollama":
        return OllamaLLM(settings.ollama_host, settings.llm_model)
    if settings.llm_backend == "llamacpp":
        return LlamaCppLLM(settings.llamacpp_model_path)
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
