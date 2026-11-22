"""Product codes, invalid-type labels, and the denominator this demo will defend.

Choices below come from public openFDA device-event count queries run on
2026-11-18 (anonymous ``count=`` calls, not the row extract). The extract
itself is a later step and refuses to start without ``OPENFDA_API_KEY``.

Denominator
-----------
MAUDE stores device-event reports. It does not store how many runs, tests,
or patients were successful. A report is filed because someone observed a
problem, so the file cannot support a clinical invalid rate.

Each stored row is one report. The numerator is a report whose
``product_problems`` include at least one label in ``INVALID_LABELS``.
The denominator is every extracted report in the same product-code window,
including reports that are only wrong-result or harm labels.

The resulting figure is an **invalid-type share of reported events**.
``SPEC_INVALID_RATE`` (2%) stays the customer's stated run-level promise.
It is not estimable from this denominator. Outputs say that in words.
Escalation for these cases is a stratum that clears the existing evidence
bar (lift, excess, chi-square), not "share > 2%".

Product codes
-------------
* ``OOI`` — instrumentation for clinical multiplex test systems and
  real-time nucleic acid amplification. About 1,422 reports from
  2022-01-01 through 2024-12-31. This is the molecular-panel case.
  The dominant labels in that window were false-positive and false-negative
  results, which this map does **not** treat as invalids. "Unable to Obtain
  Readings" was a small slice. That mix is the point of the case.
* ``JJE`` — clinical chemistry analyzer (photometric, discrete). 4,221
  reports in calendar 2024. Dominant labels were high and low test results,
  also not invalids. Mechanical problems and "Unable to Obtain Readings"
  are the invalid-type slice. Raw counts follow how many reports a firm
  files. Python computes the share before anyone calls a count a signal.
  The public page shows the reported firm name. Set
  MANUFACTURER_DISPLAY=anonymized to print Manufacturer A, B, C instead.

Call budget
-----------
Page size is 1,000 (the openFDA maximum). Planning counts imply about
2 pages for OOI and 5 pages for JJE, about 7 calls. ``MAX_API_CALLS`` is
40 so a rerun that paginates both windows still stays in the tens, and
the run stops rather than walking into the thousands. Repeat runs read
``data/cache/openfda`` and make zero calls unless ``--refresh`` is passed.
"""

from __future__ import annotations

MAX_API_CALLS = 40
PAGE_LIMIT = 1000
# openFDA rejects skip past this. The planned windows are far below it.
SKIP_CEILING = 25000

READONLY_ROLE = "invalid_demo_ro"

# FDA product-problem text, casefolded, mapped to an invalid type.
# A label absent from this dict is stored on the report and is not an invalid.
INVALID_LABELS: dict[str, str] = {
    "unable to obtain readings": "INV-NOR",
    "failure to obtain readings": "INV-NOR",
    "failure to obtain sample": "INV-NOR",
    "no device output": "INV-NOR",
    "failure to run": "INV-NOR",
    "failure to power up": "INV-NOR",
    "device stops intermittently": "INV-NOR",
    "computer software problem": "INV-SW",
    "application program problem": "INV-SW",
    "application program freezes or crashes": "INV-SW",
    "computer software in medical device": "INV-SW",
    "program or algorithm problem": "INV-SW",
    "program or algorithm execution problem": "INV-SW",
    "program or algorithm execution failure": "INV-SW",
    "calibration problem": "INV-CAL",
    "calibration error": "INV-CAL",
    "failure to calibrate": "INV-CAL",
    "mechanical problem": "INV-MECH",
    "improper or incorrect procedure or method": "INV-USR",
    "human-device interface problem": "INV-USR",
    "human device interface problem": "INV-USR",
}

# When one report carries several invalid labels, the earliest code wins.
INVALID_PRIORITY: tuple[str, ...] = ("INV-NOR", "INV-SW", "INV-CAL", "INV-MECH", "INV-USR")

INVALID_CODE_MEANING: dict[str, str] = {
    "INV-NOR": "No usable result (unable to obtain readings, failure to run, no output, power loss)",
    "INV-SW": "Software or application abort",
    "INV-CAL": "Calibration failure",
    "INV-MECH": "Mechanical problem",
    "INV-USR": "Use or human-device interface problem",
}

# Seen in the count queries and deliberately left out of the numerator.
# Wrong results and broad "any output deviation" are not invalids.
EXCLUDED_LABEL_NOTES: dict[str, str] = {
    "false positive result": "A result was produced and called positive. That is not an invalid.",
    "false negative result": "A result was produced and called negative. That is not an invalid.",
    "incorrect, inadequate or imprecise result or readings": "Wrong or imprecise result, not a missing result.",
    "high test results": "A high result was produced. That is not an invalid.",
    "low test results": "A low result was produced. That is not an invalid.",
    "incorrect measurement": "A measurement was produced and disagreed with expectations.",
    "non reproducible results": "Results were produced and did not repeat. Not an invalid.",
    "output problem": "FDA uses this for any output deviation, including wrong results, so it is not an invalid type.",
}

CASES: tuple[dict[str, str], ...] = (
    {
        "id": "openfda_ooi",
        "product_code": "OOI",
        "date_from": "2022-01-01",
        "date_to": "2024-12-31",
        "device": "Multiplex / nucleic acid amplification systems (FDA product code OOI)",
        "title": "OOI nucleic-acid systems: invalid-type share of MAUDE reports",
    },
    {
        "id": "openfda_jje",
        "product_code": "JJE",
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "device": "Clinical chemistry analyzers (FDA product code JJE)",
        "title": "JJE chemistry analyzers: invalid-type share of MAUDE reports",
    },
)

MAUDE_BANNER = (
    "Public openFDA MAUDE device-event reports. "
    "Denominator: reported events, not test runs. "
    "The 2% invalid cap is the stated run-level promise and is not estimable from this table. "
    "Not for clinical use. Not a medical device."
)

SYNTHETIC_BANNER = "Simulation. Synthetic data. Not for clinical use."


def case_by_id(case_id: str) -> dict[str, str]:
    for case in CASES:
        if case["id"] == case_id:
            return case
    known = ", ".join(case["id"] for case in CASES)
    raise KeyError(f"unknown openFDA case {case_id!r}. Known cases: {known}")


def case_by_product(product_code: str) -> dict[str, str]:
    code = product_code.strip().upper()
    for case in CASES:
        if case["product_code"] == code:
            return case
    known = ", ".join(case["product_code"] for case in CASES)
    raise KeyError(f"product code {product_code!r} is not in the extract. Known codes: {known}")


def normalize_label(label: str) -> str:
    return " ".join(str(label).casefold().replace("-", " ").split())


def invalid_codes_for(labels: list[str]) -> list[str]:
    """Return the distinct invalid codes on these problem labels, priority order."""
    found: set[str] = set()
    for label in labels:
        code = INVALID_LABELS.get(normalize_label(label))
        if code:
            found.add(code)
    return [code for code in INVALID_PRIORITY if code in found]


def primary_invalid_code(labels: list[str]) -> str:
    codes = invalid_codes_for(labels)
    return codes[0] if codes else ""


def normalize_manufacturer(name: str) -> str:
    """Collapse punctuation and legal suffixes so one firm is one stratum.

    Parenthetical cities are dropped. Two different firm strings stay
    different after that cleanup. The public page shows these names.
    MANUFACTURER_DISPLAY=anonymized replaces them with Manufacturer A, B, C.
    """
    import re

    text = str(name or "").upper()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = text.replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    suffixes = (
        " INCORPORATED",
        " CORPORATION",
        " COMPANY",
        " INC",
        " LLC",
        " LTD",
        " GMBH",
        " CORP",
        " CO",
        " SPA",
        " S P A",
    )
    changed = True
    while changed and text:
        changed = False
        for suffix in suffixes:
            if text.endswith(suffix):
                text = text[: -len(suffix)].strip()
                changed = True
    # "& CO." becomes "AND CO", then "CO" is stripped and "AND" is left over.
    if text.endswith(" AND"):
        text = text[: -len(" AND")].strip()
    return text or "UNREPORTED"


def search_for(case: dict[str, str]) -> str:
    start = case["date_from"].replace("-", "")
    end = case["date_to"].replace("-", "")
    code = case["product_code"]
    return (
        f'device.device_report_product_code.exact:"{code}" '
        f"AND date_received:[{start} TO {end}]"
    )
