# Session 1 quiz

Answer from the tag `session-1`, then check below.

1. Why is the invalid-rate spec derived from 0.98 instead of stored as its own literal?
2. Which environment variables turn Jira on?
3. What would be wrong with the default dataclass `repr`?
4. What does the backlog JSON represent, as opposed to the later investigation sync?
5. Name two non-goals from the PRD.

## Answers

1. `SPEC_INVALID_RATE = round(1 - PROMISED_VALIDITY, 2)` so the promised validity and the invalid cap cannot drift apart. 98% valid means at most 2% invalid.
2. A base URL (`JIRA_BASE_URL` or `JIRA_URL`), `JIRA_EMAIL`, and a token (`JIRA_API_TOKEN` or `JIRA_TOKEN`). Any missing piece leaves `jira_enabled` false.
3. A frozen dataclass repr includes every field, including `jira_api_token`. The override prints the redacted view only.
4. `docs/jira/backlog.json` is the build backlog (three sprints for constructing the agent). Session 5 creates a different set of issues: the fictional investigation's epic and stories. Both work without a live site.
5. Any two of: agent swarms, extra integrations (Notion/Slack/Asana/Salesforce), RAG for its own sake, fine-tuning, real customer data, clinical use, paid hosting.
