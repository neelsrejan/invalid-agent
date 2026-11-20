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
    (re.compile(r"\bparetos?\b", re.I), ("biggest problems first", "ranks the biggest")),
    (re.compile(r"\bstrata\b", re.I), ("groups in the file",)),
    (re.compile(r"\bstratum\b", re.I), ("one group", "one slice")),
    (re.compile(r"\bfidelity\b", re.I), ()),
    (re.compile(r"\bpooled\b", re.I), ("average across",)),
    (re.compile(r"\bcontrol charts?\b", re.I), ("weekly rate chart",)),
    (re.compile(r"\bwestern electric\b", re.I), ("far above the usual rate", "far from the usual rate")),
    (re.compile(r"\blift\b", re.I), ("times the share", "times higher", "how many times")),
    (re.compile(r"\bucl\b", re.I), ()),
    (re.compile(r"\blcl\b", re.I), ()),
    (re.compile(r"\bp-charts?\b", re.I), ("weekly rate chart",)),
    (re.compile(r"\bp charts?\b", re.I), ("weekly rate chart",)),
    (re.compile(r"\bopenfda\b", re.I), ("fda's public download", "public download", "public files")),
    (re.compile(r"\bdenominators?\b", re.I), ("bottom of the fraction", "every report", "every row")),
    (re.compile(r"\bdeterministic\b", re.I), ()),
    (re.compile(r"\bnarrative\b", re.I), ("written note",)),
    (re.compile(r"\bMAUDE\b", re.I), ("fda's public database of device problem reports",)),
    (re.compile(r"\bOOI\b", re.I), ("nucleic-acid",)),
    (re.compile(r"\bJJE\b", re.I), ("chemistry analyzer",)),
    (re.compile(r"\bIVD\b", re.I), ("lab test",)),
    (re.compile(r"\bfishbones?\b", re.I), ("possible causes",)),
    (re.compile(r"\bcontainment\b", re.I), ("stopping the bad units",)),
    (re.compile(r"\bwilson\b", re.I), ("likely range",)),
)

# Inserted into the same sentence as the term. The phrase is one of the glosses above.
_INLINE: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bMAUDE\b", re.I), "the FDA's public database of device problem reports"),
    (re.compile(r"\bOOI\b", re.I), "machines that run many nucleic-acid tests at once"),
    (re.compile(r"\bJJE\b", re.I), "clinical chemistry analyzers"),
    (re.compile(r"\bopenFDA\b", re.I), "the FDA's public download"),
    (re.compile(r"\bestimable\b", re.I), "we cannot measure it from this file"),
    (re.compile(r"\bdenominator\b", re.I), "the bottom of the fraction"),
    (re.compile(r"\bstrata\b", re.I), "groups in the file"),
    (re.compile(r"\bstratum\b", re.I), "one group"),
    (re.compile(r"\bp-chart\b", re.I), "weekly rate chart"),
    (re.compile(r"\bp chart\b", re.I), "weekly rate chart"),
    (re.compile(r"\bcontrol chart\b", re.I), "weekly rate chart"),
    (re.compile(r"\bWestern Electric\b", re.I), "far from the usual rate"),
    (re.compile(r"\blift\b", re.I), "how many times higher"),
    (re.compile(r"\bPareto\b", re.I), "biggest problems first"),
    (re.compile(r"\bpooled\b", re.I), "average across weeks"),
    (re.compile(r"\bnarrative\b", re.I), "written note"),
    (re.compile(r"\bIVD\b", re.I), "a lab test run on a sample"),
    (re.compile(r"\b6M\b"), "six cause groups"),
    (re.compile(r"\bfishbone\b", re.I), "possible causes sorted into groups"),
    (re.compile(r"\bcontainment\b", re.I), "stopping the bad units"),
    (re.compile(r"\bWilson\b", re.I), "likely range"),
)

# Artifact prose is rewritten so the raw term is gone. The "what this is" line teaches it.
_SOFTEN: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bWilson(?:\s+95%\s*CI|\s+interval)?\b", re.I), "likely range"),
    (re.compile(r"\bp-charts?\b", re.I), "weekly rate charts"),
    (re.compile(r"\bp charts?\b", re.I), "weekly rate charts"),
    (re.compile(r"\bcontrol charts?\b", re.I), "weekly rate charts"),
    (re.compile(r"\bWestern Electric(?:\s+rules?)?\b", re.I), "the far-from-usual check"),
    (re.compile(r"\bParetos?\b", re.I), "the ranking of the biggest problems"),
    (re.compile(r"\bstrata\b", re.I), "groups"),
    (re.compile(r"\bstratum\b", re.I), "group"),
    (re.compile(r"\blift\b", re.I), "times-higher share"),
    (re.compile(r"\bdenominator\b", re.I), "count of all rows"),
    (re.compile(r"\bestimable\b", re.I), "measurable from this file"),
    (re.compile(r"\bpooled\b", re.I), "averaged"),
    (re.compile(r"\bnarrative\b", re.I), "written note"),
    (re.compile(r"\bopenFDA\b", re.I), "the FDA public download"),
    (re.compile(r"\bfishbones?\b", re.I), "cause diagram"),
    (re.compile(r"\bcontainment\b", re.I), "the stop on bad units"),
    (re.compile(r"\bfidelity\b", re.I), ""),
    (re.compile(r"\bdeterministic\b", re.I), ""),
    (re.compile(r"\bUCL\b", re.I), "high line"),
    (re.compile(r"\bLCL\b", re.I), "low line"),
    (re.compile(r"\bMAUDE\b", re.I), "the FDA public database of device problem reports"),
    (re.compile(r"\bOOI\b", re.I), "machines that run many nucleic-acid tests at once"),
    (re.compile(r"\bJJE\b", re.I), "clinical chemistry analyzers"),
    (re.compile(r"\bRAG\b", re.I), "status color"),
    (re.compile(r"\bDMAIC\b", re.I), "the problem-solving steps"),
    (re.compile(r"\bCAPA\b", re.I), "the corrective-action record"),
    (re.compile(r"\bIVD\b", re.I), "a lab test"),
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


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", str(text or "").strip())
    return [part for part in parts if part.strip()]


def _readable(text: str) -> str:
    """Drop markdown marks so `_Narrative_` and `**Wilson**` still count as the word.

    An underscore inside an id such as ``openfda_ooi`` stays, so the id is not
    read as the word openfda.
    """
    cleaned = re.sub(r"[*`#]", " ", str(text or ""))
    return re.sub(r"(?<![A-Za-z0-9])_+|_+(?![A-Za-z0-9])", " ", cleaned)


def unexplained_jargon(text: str) -> list[str]:
    """Jargon in a sentence that does not explain itself.

    A gloss in one sentence does not excuse the same word in another sentence.
    Call this once per rendered element (a caption, a cell, a chart title).
    """
    found: list[str] = []
    chunks = _sentences(text) or [str(text or "")]
    for sentence in chunks:
        readable = _readable(sentence)
        lowered = readable.casefold()
        for pattern, glosses in JARGON_RULES:
            if pattern.search(readable) is None:
                continue
            if not glosses or not any(gloss in lowered for gloss in glosses):
                found.append(pattern.pattern)
    return list(dict.fromkeys(found))


def with_gloss(text: str) -> str:
    """Put the explanation in the same sentence as the term."""
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    return " ".join(_gloss_sentence(sentence) for sentence in _sentences(cleaned))


def _gloss_sentence(sentence: str) -> str:
    updated = sentence
    for pattern, insertion in _INLINE:
        if pattern.search(updated) is None:
            continue
        lowered = updated.casefold()
        if insertion.casefold() in lowered:
            continue
        updated = pattern.sub(lambda match: f"{match.group(0)} ({insertion})", updated, count=1)
    return updated


def soften(text: str) -> str:
    """Rewrite agent prose so a raw term is a plain phrase. Drops empty leftovers."""
    updated = _readable(text)
    for pattern, replacement in _SOFTEN:
        updated = pattern.sub(replacement, updated)
    for key, phrase in CAUSE_PLAIN.items():
        updated = re.sub(rf"\b{re.escape(key)}\b", phrase, updated)
    updated = updated.replace("6M", "six cause groups")
    updated = updated.replace("metric:", "count ")
    updated = updated.replace("injection:", "note ")
    updated = re.sub(r"[ \t]{2,}", " ", updated)
    updated = re.sub(r" +([.,;:])", r"\1", updated)
    return updated.strip()


_HIDDEN = re.compile(
    r"(://|api_key|traceback|/home/|/opt/|/agent/|/var/|connection string|\w+Error:)",
    re.I,
)


def safe_prose(text: str) -> str:
    """Prose that can be shown. Sentences that still fail the jargon check are left out."""
    cleaned = soften(text)
    kept = [
        sentence
        for sentence in _sentences(cleaned)
        if not unexplained_jargon(sentence) and _HIDDEN.search(sentence) is None
    ]
    return " ".join(kept).strip()


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
