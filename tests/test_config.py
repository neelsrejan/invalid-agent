"""Settings stay offline-safe and never leak secrets."""

from invalid_agent.config import (
    DEFAULT_LLM_MODEL,
    HOSTED_LLM_MODEL,
    PROMISED_VALIDITY,
    SPEC_INVALID_RATE,
    load_settings,
)

_SECRET_KEYS = (
    "LLM_BACKEND",
    "JIRA_BASE_URL",
    "JIRA_URL",
    "JIRA_EMAIL",
    "JIRA_API_TOKEN",
    "JIRA_TOKEN",
    "OPENFDA_API_KEY",
    "DATABASE_URL",
    "DATABASE_URL_READONLY",
    "DEMO_READONLY_PASSWORD",
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "DATA_BACKEND",
    "OLLAMA_HOST",
    "LLM_MODEL",
    "OLLAMA_MODEL",
    "LLAMACPP_MODEL_PATH",
)


def _clear(monkeypatch):
    for key in _SECRET_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_defaults_are_offline(monkeypatch):
    _clear(monkeypatch)
    settings = load_settings()
    assert settings.spec_invalid_rate == SPEC_INVALID_RATE == 0.02
    assert settings.promised_validity == PROMISED_VALIDITY == 0.98
    assert settings.llm_backend == "deterministic"
    assert settings.llm_model == DEFAULT_LLM_MODEL == "llama3.1:8b"
    assert HOSTED_LLM_MODEL == "llama3.2:1b"
    assert settings.rules_only is True
    assert settings.jira_enabled is False
    assert settings.jira_api_token == ""
    assert settings.openfda_api_key == ""
    assert settings.database_url == ""
    assert settings.database_url_readonly == ""
    assert settings.groq_api_key == ""
    assert settings.groq_model == "openai/gpt-oss-20b"
    assert settings.data_backend == "synthetic"


def test_jira_requires_all_three_values(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    assert load_settings().jira_enabled is False
    monkeypatch.setenv("JIRA_API_TOKEN", "super-secret-token")
    settings = load_settings()
    assert settings.jira_enabled is True
    assert settings.jira_base_url == "https://example.atlassian.net"
    assert "super-secret-token" not in repr(settings)
    assert settings.redacted()["jira_api_token"] == "***"


def test_plan_aliases_for_jira(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("JIRA_URL", "https://alias.atlassian.net/")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    monkeypatch.setenv("JIRA_TOKEN", "alias-token-value")
    settings = load_settings()
    assert settings.jira_enabled is True
    assert settings.jira_base_url == "https://alias.atlassian.net"
    assert "alias-token-value" not in repr(settings)


def test_preferred_jira_names_win_over_aliases(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("JIRA_URL", "https://alias.atlassian.net")
    monkeypatch.setenv("JIRA_BASE_URL", "https://preferred.atlassian.net")
    monkeypatch.setenv("JIRA_TOKEN", "alias-token")
    monkeypatch.setenv("JIRA_API_TOKEN", "preferred-token")
    monkeypatch.setenv("JIRA_EMAIL", "pm@example.com")
    settings = load_settings()
    assert settings.jira_base_url == "https://preferred.atlassian.net"
    assert settings.jira_api_token == "preferred-token"
    assert "preferred-token" not in repr(settings)


def test_llm_model_overrides_the_default(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("LLM_MODEL", "llama3.2:1b")
    assert load_settings().llm_model == "llama3.2:1b"
    monkeypatch.setenv("LLM_MODEL", "gemma3")
    assert load_settings().llm_model == "gemma3"
    monkeypatch.setenv("LLM_MODEL", "phi4")
    assert load_settings().llm_model == "phi4"


def test_ollama_model_env_is_not_a_second_setting(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:1b")
    assert load_settings().llm_model == DEFAULT_LLM_MODEL


def test_database_and_groq_secrets_are_masked(monkeypatch):
    from urllib.parse import urlunsplit

    _clear(monkeypatch)
    db_password = "placeholder-db"
    groq_token = "placeholder-groq"
    demo_password = "placeholder-demo"
    monkeypatch.setenv(
        "DATABASE_URL",
        urlunsplit(("postgresql", f"owner:{db_password}@localhost", "/maude", "", "")),
    )
    monkeypatch.setenv("GROQ_API_KEY", groq_token)
    monkeypatch.setenv("DEMO_READONLY_PASSWORD", demo_password)
    settings = load_settings()
    rendered = repr(settings)
    assert db_password not in rendered
    assert groq_token not in rendered
    assert demo_password not in rendered
    assert settings.redacted()["database_url"] == "***"
    assert settings.redacted()["groq_api_key"] == "***"


def test_unknown_backend_falls_back(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("LLM_BACKEND", "hosted-gpu")
    assert load_settings().llm_backend == "deterministic"
    monkeypatch.setenv("LLM_BACKEND", "rules-only")
    assert load_settings().llm_backend == "deterministic"
