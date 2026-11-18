"""Print which owner secrets are present. This command does not call openFDA."""

from __future__ import annotations

from invalid_agent.config import load_settings
from invalid_agent.data.cache import is_complete
from invalid_agent.data.mapping import CASES, READONLY_ROLE


def main() -> None:
    settings = load_settings()
    rows = [
        ("OPENFDA_API_KEY", bool(settings.openfda_api_key), "free key at https://open.fda.gov/apis/authentication/"),
        ("DATABASE_URL", bool(settings.database_url), "Neon admin connection string, sslmode=require"),
        ("DEMO_READONLY_PASSWORD", bool(settings.demo_readonly_password), f"password for role {READONLY_ROLE}"),
        ("DATABASE_URL_READONLY", bool(settings.database_url_readonly), "printed by the loader; Streamlit secret"),
        ("GROQ_API_KEY", bool(settings.groq_api_key), "free key at https://console.groq.com/keys"),
        ("JIRA_BASE_URL", bool(settings.jira_base_url), "https://<site>.atlassian.net"),
        ("JIRA_EMAIL", bool(settings.jira_email), "Atlassian account email"),
        ("JIRA_API_TOKEN", bool(settings.jira_api_token), "https://id.atlassian.com/manage-profile/security/api-tokens"),
    ]
    print(f"data_backend={settings.data_backend} llm_backend={settings.llm_backend}")
    for name, present, where in rows:
        state = "set" if present else "MISSING"
        print(f"{state:7} {name} — {where}")
    for case in CASES:
        state = "complete" if is_complete(case["id"]) else "absent"
        print(f"cache {case['id']}: {state}")
    if not settings.openfda_api_key:
        print("Extract is blocked until OPENFDA_API_KEY is set. This doctor did not call openFDA.")


if __name__ == "__main__":
    main()
