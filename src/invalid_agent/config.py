"""Runtime settings.

Secrets are read from the environment only. ``Settings.__repr__`` never
prints a Jira token or an openFDA key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Promised validity ≥ 98% is an invalid-rate spec of ≤ 2%.
PROMISED_VALIDITY = 0.98
SPEC_INVALID_RATE = round(1.0 - PROMISED_VALIDITY, 2)

_LLM_BACKENDS = {"deterministic", "ollama", "llamacpp", "groq"}

# Local Ollama default is Meta Llama 3.1 8B.
# llama3.2:1b is the suggested small tag for a laptop that cannot run 8B.
# The public demo narrates with Groq's free tier. Llama 3.1 8B Instant left
# that free tier on 2026-08-16, so the hosted model is gpt-oss-20b.
DEFAULT_LLM_MODEL = "llama3.1:8b"
HOSTED_LLM_MODEL = "llama3.2:1b"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def find_repo_root() -> Path:
    """Locate the repo whether the process was started from it or from site-packages."""
    here = Path(__file__).resolve()
    candidates = [Path.cwd(), *here.parents]
    for candidate in candidates:
        if (candidate / "pyproject.toml").is_file() and (candidate / "scenarios").is_dir():
            return candidate
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "invalid_agent").is_dir():
            return candidate
    return here.parents[2]


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def load_dotenv() -> None:
    """Read a gitignored .env without overriding variables already in the environment."""
    path = find_repo_root() / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    llm_backend: str
    ollama_host: str
    llm_model: str
    llamacpp_model_path: str
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str
    openfda_api_key: str
    database_url: str
    database_url_readonly: str
    demo_readonly_password: str
    groq_api_key: str
    groq_model: str
    data_backend: str
    spec_invalid_rate: float
    promised_validity: float
    repo_root: Path
    out_dir: Path

    @property
    def jira_enabled(self) -> bool:
        """True only when a site, an email, and a token are all present."""
        return bool(self.jira_base_url and self.jira_email and self.jira_api_token)

    @property
    def rules_only(self) -> bool:
        return self.llm_backend == "deterministic"

    def redacted(self) -> dict[str, object]:
        """Safe-to-log view. Tokens are masked, not omitted, so a missing key is obvious."""
        return {
            "llm_backend": self.llm_backend,
            "ollama_host": self.ollama_host,
            "llm_model": self.llm_model,
            "llamacpp_model_path": self.llamacpp_model_path,
            "jira_base_url": self.jira_base_url,
            "jira_email": self.jira_email,
            "jira_api_token": "***" if self.jira_api_token else "",
            "jira_project_key": self.jira_project_key,
            "jira_enabled": self.jira_enabled,
            "openfda_api_key": "***" if self.openfda_api_key else "",
            "database_url": "***" if self.database_url else "",
            "database_url_readonly": "***" if self.database_url_readonly else "",
            "demo_readonly_password": "***" if self.demo_readonly_password else "",
            "groq_api_key": "***" if self.groq_api_key else "",
            "groq_model": self.groq_model,
            "data_backend": self.data_backend,
            "spec_invalid_rate": self.spec_invalid_rate,
            "promised_validity": self.promised_validity,
            "repo_root": str(self.repo_root),
            "out_dir": str(self.out_dir),
        }

    def __repr__(self) -> str:
        view = self.redacted()
        return (
            "Settings("
            f"llm_backend={view['llm_backend']!r}, "
            f"jira_enabled={view['jira_enabled']!r}, "
            f"spec_invalid_rate={view['spec_invalid_rate']!r})"
        )


def load_settings() -> Settings:
    """Build settings from the environment.

    Jira aliases from the build plan (``JIRA_URL``, ``JIRA_TOKEN``) are
    accepted. The names ``JIRA_BASE_URL`` and ``JIRA_API_TOKEN`` win when
    both are set.
    """
    load_dotenv()
    backend = _env("LLM_BACKEND", "deterministic").lower()
    if backend in {"rules", "rules-only", "mock"}:
        backend = "deterministic"
    if backend not in _LLM_BACKENDS:
        backend = "deterministic"

    root = find_repo_root()
    out = Path(_env("INVALID_AGENT_OUT", str(root / "out")))
    return Settings(
        llm_backend=backend,
        ollama_host=_env("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/"),
        llm_model=_env("LLM_MODEL", DEFAULT_LLM_MODEL),
        llamacpp_model_path=_env("LLAMACPP_MODEL_PATH"),
        jira_base_url=(_env("JIRA_BASE_URL") or _env("JIRA_URL")).rstrip("/"),
        jira_email=_env("JIRA_EMAIL"),
        jira_api_token=_env("JIRA_API_TOKEN") or _env("JIRA_TOKEN"),
        jira_project_key=_env("JIRA_PROJECT_KEY", "INV"),
        openfda_api_key=_env("OPENFDA_API_KEY"),
        database_url=_env("DATABASE_URL"),
        database_url_readonly=_env("DATABASE_URL_READONLY"),
        demo_readonly_password=_env("DEMO_READONLY_PASSWORD"),
        groq_api_key=_env("GROQ_API_KEY"),
        groq_model=_env("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        data_backend=_env("DATA_BACKEND", "synthetic").lower() or "synthetic",
        spec_invalid_rate=SPEC_INVALID_RATE,
        promised_validity=PROMISED_VALIDITY,
        repo_root=root,
        out_dir=out,
    )
