"""Plain-language helpers for the guided page.

High-school wording lives here. A jargon check can import the same rules
the page uses, so a new sentence cannot ship a bare technical term.
"""

from __future__ import annotations

import re

# A term may appear only when the same text also contains one of the glosses.
# An empty gloss tuple means the word is banned on the page.
JARGON_RULES: tuple[tuple[re.Pattern[str], tuple[str, ...]], ...] = (
    (re.compile(r"\bestimable\b", re.I), ("cannot measure", "we cannot measure")),
    (re.compile(r"\bpareto\b", re.I), ("biggest problems first", "ranks the biggest")),
    (re.compile(r"\bstrata\b", re.I), ("groups in the file",)),
    (re.compile(r"\bstratum\b", re.I), ("one group", "one slice")),
    (re.compile(r"\bfidelity\b", re.I), ()),
    (re.compile(r"\bpooled\b", re.I), ("average across",)),
    (re.compile(r"\bcontrol chart\b", re.I), ("weekly rate chart",)),
    (re.compile(r"\bwestern electric\b", re.I), ("far above the usual rate", "far from the usual rate")),
    (re.compile(r"\blift\b", re.I), ("times the share", "times higher", "how many times")),
    (re.compile(r"\bucl\b", re.I), ()),
    (re.compile(r"\blcl\b", re.I), ()),
    (re.compile(r"\bp-chart\b", re.I), ("weekly rate chart",)),
    (re.compile(r"\bp chart\b", re.I), ("weekly rate chart",)),
    (re.compile(r"\bopenfda\b", re.I), ("fda's public download", "public download", "public files")),
    (re.compile(r"\bdenominator\b", re.I), ("bottom of the fraction", "every report", "every row")),
    (re.compile(r"\bdeterministic\b", re.I), ()),
    (re.compile(r"\bnarrative\b", re.I), ("written note",)),
    (re.compile(r"\bMAUDE\b", re.I), ("fda's public database of device problem reports",)),
    (re.compile(r"\bOOI\b", re.I), ("nucleic-acid",)),
    (re.compile(r"\bJJE\b", re.I), ("chemistry analyzer",)),
    (re.compile(r"\bIVD\b", re.I), ("lab test",)),
)

_GLOSS_SENTENCE: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bMAUDE\b", re.I), "MAUDE is the FDA's public database of device problem reports."),
    (re.compile(r"\bOOI\b", re.I), "OOI means machines that run many nucleic-acid tests at once."),
    (re.compile(r"\bJJE\b", re.I), "JJE means clinical chemistry analyzers, the machines that measure chemicals in blood."),
    (
        re.compile(r"\bopenFDA\b", re.I),
        "openFDA means the FDA's public download of device reports.",
    ),
    (
        re.compile(r"\bestimable\b", re.I),
        "Estimable would mean we can measure it here. We cannot measure the 2% cap from this file.",
    ),
    (
        re.compile(r"\bdenominator\b", re.I),
        "The denominator is the bottom of the fraction: every row in the file, not only the bad ones.",
    ),
    (re.compile(r"\bstrata\b", re.I), "Strata means groups in the file, such as a lot or a site."),
    (re.compile(r"\bstratum\b", re.I), "A stratum is one group, such as one lot or one site."),
    (re.compile(r"\bp-chart\b", re.I), "A p-chart is a weekly rate chart."),
    (re.compile(r"\bcontrol chart\b", re.I), "A control chart is a weekly rate chart."),
    (
        re.compile(r"\bWestern Electric\b", re.I),
        "Western Electric rules flag a week far from the usual rate.",
    ),
    (re.compile(r"\blift\b", re.I), "Lift means how many times higher this group's share is."),
    (re.compile(r"\bPareto\b", re.I), "A Pareto chart ranks the biggest problems first."),
    (re.compile(r"\bpooled\b", re.I), "Pooled means the average across weeks."),
    (re.compile(r"\bnarrative\b", re.I), "A narrative is the written note."),
    (
        re.compile(r"\bIVD\b", re.I),
        "IVD means a lab test run on a sample, not a treatment.",
    ),
)

CODE_PLAIN: dict[str, str] = {
    "INV-NOR": "no usable result (INV-NOR)",
    "INV-MECH": "a mechanical problem (INV-MECH)",
    "INV-SW": "a software abort (INV-SW)",
    "INV-CAL": "a calibration problem (INV-CAL)",
    "INV-USR": "someone used it the wrong way (INV-USR)",
    "INV-IC": "an internal-control failure (INV-IC)",
    "INV-EXT": "an extraction failure (INV-EXT)",
    "INV-INH": "a blocked reaction (INV-INH)",
    "INV-HEM": "a sample-quality flag (INV-HEM)",
    "INV-VOL": "not enough sample (INV-VOL)",
    "INV-TMP": "a temperature flag (INV-TMP)",
    "UNSPECIFIED": "an unlabeled problem",
    "NOT_INVALID": "not an invalid type",
}

CAUSE_PLAIN: dict[str, str] = {
    "bad_reagent_lot": "a bad reagent lot",
    "drifting_instrument": "an instrument that is drifting",
    "site_temperature": "the temperature at a site",
    "software_version": "a software version",
    "preanalytical_hemolysis": "a sample-quality problem",
    "user_process_error": "how people ran the test",
    "reported_manufacturer": "the company that made the device",
    "reported_brand": "the brand name",
    "no_single_cause": "no single cause",
}

PUBLIC_BANNER = (
    "These rows are from MAUDE, the FDA's public database of device problem reports. "
    "They come from the FDA's public download of device reports (openFDA). "
    "The bottom of the fraction is every report in the file, not the successful tests. "
    "The 2% cap is a promise about test runs. We cannot measure that promise from this file. "
    "Not for clinical use. Not a medical device."
)

PRACTICE_BANNER = (
    "This run uses practice cases because the public report table is not connected. "
    "The rows are simulated test runs, not a real hospital. "
    "Not for clinical use. Not a medical device."
)

CASE_GLOSSARY = (
    "MAUDE is the FDA's public database of device problem reports. "
    "OOI means machines that run many nucleic-acid tests at once. "
    "JJE means clinical chemistry analyzers, the machines that measure chemicals in blood."
)


def unexplained_jargon(text: str) -> list[str]:
    """Return jargon patterns that appear with no gloss in the same text."""
    found: list[str] = []
    lowered = text.casefold()
    for pattern, glosses in JARGON_RULES:
        if pattern.search(text) is None:
            continue
        if not glosses or not any(gloss in lowered for gloss in glosses):
            found.append(pattern.pattern)
    return found


def with_gloss(text: str) -> str:
    """Append a one-line explanation for any jargon already in ``text``."""
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    extra: list[str] = []
    for pattern, sentence in _GLOSS_SENTENCE:
        if pattern.search(cleaned) and sentence not in cleaned:
            extra.append(sentence)
    if not extra:
        return cleaned
    return cleaned + " " + " ".join(extra)


def plain_case_label(label: str) -> str:
    """Case menu text. Product codes and the public database are named in place."""
    text = str(label or "")
    text = re.sub(r"\bstrata\b", "groups in the file", text, flags=re.I)
    text = re.sub(r"\bstratum\b", "one group", text, flags=re.I)
    if re.search(r"\bMAUDE\b", text) and "public database of device problem reports" not in text:
        text = text.replace("MAUDE", "MAUDE (the FDA's public database of device problem reports)")
    if re.search(r"\bOOI\b", text) and "nucleic-acid" not in text.casefold():
        text = text.replace("OOI", "OOI (machines that run many nucleic-acid tests at once)")
    if re.search(r"\bJJE\b", text) and "chemistry analyzer" not in text.casefold():
        text = text.replace("JJE", "JJE (clinical chemistry analyzers)")
    return text


def format_percent(rate: float) -> str:
    """A percent a person can read. Tiny rates are not shown as 0.00%."""
    pct = float(rate) * 100.0
    if pct <= 0.0:
        return "0%"
    if pct < 0.01:
        return "under 0.01%"
    return f"{pct:.2f}%"


def code_plain(code: str) -> str:
    key = str(code or "").strip()
    if key in CODE_PLAIN:
        return CODE_PLAIN[key]
    if not key:
        return "an unlabeled problem"
    return f"type {key}"


def cause_plain(cause: str) -> str:
    key = str(cause or "no_single_cause")
    return CAUSE_PLAIN.get(key, key.replace("_", " "))
