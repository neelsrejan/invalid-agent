# ADR 0001: Host the investigation on public MAUDE reports

## Status

Accepted for the draft pull request. The row extract has not run. It waits on `OPENFDA_API_KEY`.

## Context

The weekly loop used to rebuild a synthetic pandas frame from `scenarios/*.yaml`. openFDA device-event (MAUDE) reports are the public source for the demo. MAUDE records problems. It does not record how many runs succeeded. A hiring manager should be able to query a free hosted Postgres database, and the public page must not invent a clinical invalid rate.

Manufacturer names on those reports are public. The owner asked that the public page show them, including a firm the owner works for when that firm is the name on the report. The code must not hardcode any firm.

## Decision

- Two cases, chosen from public count queries and not from a row download: product code OOI for 2022-01-01 through 2024-12-31, and product code JJE for calendar 2024.
- Each stored row is one device-event report. The primary key is `(mdr_report_key, product_code)`. The numerator is a report whose `product_problems` map to an invalid type. The denominator is every extracted report in that window. The 2% cap stays visible and is labeled not estimable.
- Neon free Postgres holds the table. The loader creates a read-only role for the public page. Railway is not used. Supabase is acceptable only as a plain Postgres URL.
- The extract is one cached pass, page size 1000, cap 40 calls. A 429 waits for `Retry-After` or two seconds. Repeat runs do not call openFDA unless `--refresh` is passed.
- `MANUFACTURER_DISPLAY` defaults to `real`. Names on the page are the reported names after punctuation cleanup. `anonymized` still maps those names to Manufacturer A, B, C. The table always stores the reported name.
- Weekly chart dates use `date_of_event` when the report has one, otherwise the FDA received date. The page says which date that is.
- The public Streamlit page never creates Jira issues. The owner seeds them once. The page only reads and links issues that already exist. Labels are `openfda` or `simulation`.
- `load_settings()` reads the process environment only. CLI commands and Streamlit load `.env`. Pytest does not.
- Synthetic scenarios stay the CI path. CI does not need a network, a key, or a database.

## Consequences

- A share of reported events is not a field invalid rate. Every openFDA memo says so.
- Showing real firm names means the public page can name the owner's employer when MAUDE does. That is the public record, not a conclusion the code baked in.
- The owner still has to create the Neon database, the Groq key, the Jira site, and the Streamlit app, then run the extract after setting `OPENFDA_API_KEY`.
- Anonymized mode remains for a later choice. It is not the default.
