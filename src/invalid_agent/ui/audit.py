"""JJE field-invalid audit. Four weeks, one page each, the whole file in hand.

Weeks are steps in the investigation. They do not hide later rows.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from invalid_agent.data.mapping import INVALID_LABELS, normalize_label
from invalid_agent.ui.plain import code_plain

THRESHOLD = 0.01
MIN_REPORTS = 100
_ASK = re.compile(
    r"\?|\b(?:name|show|tell|list|give|what|how|which|who|whos|why|when|where|does|do|can|could)\b"
)
_SHORT = (
    ("BINDING SITE", "The Binding Site"),
    ("ROCHE", "Roche"),
    ("SIEMENS", "Siemens"),
    ("ABBOTT", "Abbott Labs"),
    ("BECKMAN", "Beckman"),
    ("ORTHO", "Ortho"),
)
_BRANCH = {
    "INV-MECH": "Machine",
    "INV-SW": "Method",
    "INV-NOR": "Material",
    "INV-CAL": "Measurement",
    "INV-USR": "Man",
}


def short_name(raw: str) -> str:
    text = str(raw or "").upper()
    for needle, label in _SHORT:
        if re.search(rf"\b{needle}\b", text):
            return label
    cleaned = " ".join(text.split())
    return cleaned.title() if cleaned else "Unreported"


def company_table(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """One row per company. Share is invalid rows divided by total rows."""
    if frame is None or frame.empty:
        return []
    if "manufacturer" not in frame.columns and "manufacturer_name" not in frame.columns:
        return []
    names = _names(frame)
    codes = _codes(frame)
    buckets: dict[str, dict[str, int]] = {}
    for name, code in zip(names, codes):
        label = short_name(name)
        bucket = buckets.setdefault(label, {"total": 0, "invalid": 0})
        bucket["total"] += 1
        if str(code or "").strip():
            bucket["invalid"] += 1
    rows = []
    for label, bucket in buckets.items():
        total = int(bucket["total"])
        invalid = int(bucket["invalid"])
        share = (invalid / total) if total else 0.0
        enough = total >= MIN_REPORTS
        rows.append(
            {
                "name": label,
                "total": total,
                "invalid": invalid,
                "share": share,
                "enough": enough,
                "over": bool(enough and share > THRESHOLD),
                "note": "" if enough else "too few reports to judge",
            }
        )
    rows.sort(key=lambda row: (-row["total"], row["name"]))
    return rows


def flagged_companies(table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in table if row.get("over")]


def small_companies(table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in table if not row.get("enough")]


def _names(frame: pd.DataFrame) -> list[str]:
    if "manufacturer" in frame.columns:
        return [str(value or "") for value in frame["manufacturer"].tolist()]
    return [str(value or "") for value in frame["manufacturer_name"].tolist()]


def _codes(frame: pd.DataFrame) -> list[str]:
    if "invalid_code" not in frame.columns:
        return [""] * len(frame)
    return [str(value or "") for value in frame["invalid_code"].tolist()]


def _company_mask(frame: pd.DataFrame, company: str) -> pd.Series:
    target = short_name(company).casefold()
    return pd.Series([short_name(name).casefold() == target for name in _names(frame)], index=frame.index)


def pareto_for(frame: pd.DataFrame, company: str) -> list[dict[str, Any]]:
    mask = _company_mask(frame, company)
    subset = frame.loc[mask]
    if subset.empty:
        return []
    codes = [code for code in _codes(subset) if code]
    counts: dict[str, int] = {}
    for code in codes:
        counts[code] = counts.get(code, 0) + 1
    labels = _problem_lists(subset)
    triggers: dict[str, dict[str, int]] = {}
    for code, problems in zip(_codes(subset), labels):
        if not code:
            continue
        bucket = triggers.setdefault(code, {})
        for label in problems:
            if normalize_label(label) in INVALID_LABELS and INVALID_LABELS[normalize_label(label)] == code:
                bucket[label] = bucket.get(label, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    total = sum(counts.values()) or 1
    running = 0
    rows = []
    for code, count in ranked:
        running += count
        trigger = sorted(triggers.get(code, {}).items(), key=lambda item: (-item[1], item[0]))
        rows.append(
            {
                "code": code,
                "plain": code_plain(code),
                "count": count,
                "share": count / total,
                "cumulative": running / total,
                "triggers": [label for label, _count in trigger[:3]],
            }
        )
    return rows


def cause_set_for(frame: pd.DataFrame, company: str, table: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Smallest top-of-Pareto set that brings this company to 1% or under."""
    rows = table if table is not None else company_table(frame)
    company_row = next((row for row in rows if row["name"].casefold() == short_name(company).casefold()), None)
    pareto = pareto_for(frame, company)
    if company_row is None:
        return {"name": short_name(company), "causes": [], "projected": None, "total": 0, "invalid": 0}
    total = int(company_row["total"])
    invalid = int(company_row["invalid"])
    chosen: list[dict[str, Any]] = []
    removed = 0
    for row in pareto:
        if total and (invalid - removed) / total <= THRESHOLD:
            break
        chosen.append(row)
        removed += int(row["count"])
    projected = ((invalid - removed) / total) if total else 0.0
    tied: list[str] = []
    tie_count = 0
    if chosen:
        last_count = int(chosen[-1]["count"])
        peers = [row for row in pareto if int(row["count"]) == last_count]
        needed = [row for row in chosen if int(row["count"]) == last_count]
        earlier = [row for row in chosen if int(row["count"]) != last_count]
        if not earlier and len(needed) == 1 and len(peers) > 1:
            tied = [str(row["code"]) for row in peers]
            tie_count = last_count
    return {
        "name": company_row["name"],
        "causes": [{"code": row["code"], "plain": row["plain"], "count": row["count"]} for row in chosen],
        "pareto": pareto,
        "tied": tied,
        "tie_count": tie_count,
        "projected": projected,
        "total": total,
        "invalid": invalid,
        "share": company_row["share"],
    }


def _problem_lists(frame: pd.DataFrame) -> list[list[str]]:
    if "product_problems" not in frame.columns:
        return [[] for _ in range(len(frame))]
    lists = []
    for value in frame["product_problems"].tolist():
        if isinstance(value, list):
            lists.append([str(item) for item in value])
        elif isinstance(value, str) and value.strip():
            lists.append([part.strip() for part in value.split("|") if part.strip()])
        else:
            lists.append([])
    return lists


def co_reported(frame: pd.DataFrame, company: str, code: str) -> list[str]:
    mask = _company_mask(frame, company)
    subset = frame.loc[mask]
    codes = _codes(subset)
    found: dict[str, int] = {}
    for row_code, problems in zip(codes, _problem_lists(subset)):
        if row_code != code:
            continue
        for label in problems:
            if normalize_label(label) in INVALID_LABELS:
                continue
            found[label] = found.get(label, 0) + 1
    ranked = sorted(found.items(), key=lambda item: (-item[1], item[0]))
    return [label for label, _count in ranked[:3]]


def issues_for(frame: pd.DataFrame, table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues = []
    for company in flagged_companies(table):
        bundle = cause_set_for(frame, company["name"], table)
        for cause in bundle["causes"]:
            others = co_reported(frame, company["name"], cause["code"])
            branch = _BRANCH.get(cause["code"], "Environment")
            issues.append(
                {
                    "company": company["name"],
                    "code": cause["code"],
                    "plain": cause["plain"],
                    "count": cause["count"],
                    "branch": branch,
                    "co_reported": others,
                    "testimonial": _testimonial(company["name"], cause, branch, others),
                    "ticket": f"{company['name']} {cause['code']}: Statement + triage required",
                }
            )
    return issues


def _plain_core(plain: str) -> str:
    return re.sub(r"^(?:a|an|the)\s+", "", str(plain or "").split("(")[0].strip())


def _testimonial(company: str, cause: dict[str, Any], branch: str, others: list[str]) -> str:
    extra = f" The same reports also carry {others[0]}." if others else ""
    return (
        f"Simulated note from {company}. "
        f"The {int(cause['count'])} {cause['code']} reports ({_plain_core(cause['plain'])}) point at the {branch} branch.{extra} "
        "This note was written for the exercise and was not sent."
    )


def closeouts_for(frame: pd.DataFrame, table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for company in flagged_companies(table):
        bundle = cause_set_for(frame, company["name"], table)
        causes = ", ".join(cause["code"] for cause in bundle["causes"]) or "no code"
        branches = _join(sorted({_BRANCH.get(cause["code"], "Environment") for cause in bundle["causes"]})) or "Environment"
        projected = float(bundle["projected"] or 0.0)
        share = float(company["share"])
        rows.append(
            {
                "company": company["name"],
                "causes": [cause["code"] for cause in bundle["causes"]],
                "branches": branches,
                "share": share,
                "projected": projected,
                "under": projected <= THRESHOLD,
                "statement": (
                    f"Simulated close-out for {company['name']}. "
                    f"Root cause: the {branches} {'branches' if ' and ' in branches else 'branch'} behind {causes}. "
                    f"Corrective action: fix that failure on the open complaints. "
                    f"Preventive action: add a release check so it cannot ship again. "
                    f"Public statement: {company['name']} will move its invalid share of field problem reports "
                    f"from {share * 100:.2f}% to {projected * 100:.2f}%, under the 1% line. "
                    "This note was written for the exercise and was not sent."
                ),
            }
        )
    return rows


def request_messages(table: list[dict[str, Any]]) -> list[dict[str, str]]:
    messages = []
    for row in flagged_companies(table):
        messages.append(
            {
                "company": row["name"],
                "summary": f"{row['name']}: Request complaint detail to explain elevated invalid share",
                "message": (
                    f"Hello {row['name']}. Your invalid share of field problem reports is "
                    f"{row['share'] * 100:.2f}% ({int(row['invalid'])} of {int(row['total'])}), over 1%. "
                    "Please send the complaint detail behind these reports. "
                    "This message stays in the app and is not sent."
                ),
            }
        )
    return messages


def preview_rows(frame: pd.DataFrame, limit: int = 10) -> list[dict[str, str]]:
    if frame is None or frame.empty:
        return []
    hidden = {"product_problems"}
    columns = [column for column in frame.columns if column not in hidden]
    head = frame.loc[:, columns].head(limit)
    rows = []
    for record in head.to_dict(orient="records"):
        rows.append({str(key): "" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value) for key, value in record.items()})
    return rows


def attach(frame: pd.DataFrame) -> dict[str, Any]:
    table = company_table(frame)
    flagged = flagged_companies(table)
    return {
        "companies": table,
        "flagged": flagged,
        "small": small_companies(table),
        "cause_sets": [cause_set_for(frame, row["name"], table) for row in flagged],
        "issues": issues_for(frame, table),
        "closeouts": closeouts_for(frame, table),
        "requests": request_messages(table),
        "preview": preview_rows(frame),
        "share_line": "invalid share of field problem reports",
    }


def goal_statement(text: str, view: dict[str, Any], step_id: str) -> tuple[str, str, str] | None:
    facts = view.get("explore") or {}
    if not facts.get("companies"):
        return None
    if _ASK.search(str(text or "").casefold()):
        return None
    lowered = _with_codes(" ".join(str(text or "").casefold().split()))
    if re.search(r"\b(?:not|never|no|without|except|but|only|unless)\b|n't", lowered):
        return None
    if not _numbers_ok(lowered, facts):
        return None
    finding, sentence = show_me_fact(view, step_id)
    if step_id == "pareto" and _pareto_claim(lowered, facts):
        return "correct", sentence, finding
    if step_id == "responses" and _response_claim(lowered, facts):
        return "correct", sentence, finding
    if step_id == "closeout" and _closeout_claim(lowered, facts):
        return "correct", sentence, finding
    return None


_CODE = re.compile(r"\binv-[a-z]+\b")
_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent)")
_N_OF_M = re.compile(r"(\d[\d,]*)\s*(?:of|/|out of)\s*(\d[\d,]*)")


def _cause_label(bundle: dict[str, Any]) -> str:
    tied = [str(code) for code in bundle.get("tied") or []]
    if len(tied) > 1:
        return f"{' or '.join(tied)} (tied at {int(bundle.get('tie_count') or 0)})"
    codes = [str(cause["code"]) for cause in bundle.get("causes") or []]
    return " and ".join(codes) or "no code"


def _with_codes(lowered: str) -> str:
    """Swap a plain category name for its code so 'no usable result' is not read as a negation."""
    for code in _BRANCH:
        plain = code_plain(code).casefold()
        core = re.sub(r"^(?:a|an|the)\s+", "", plain.split("(")[0].strip())
        for phrase in (plain, core):
            if phrase:
                lowered = lowered.replace(phrase, code.casefold())
    return re.sub(r"\(\s*(inv-[a-z]+)\s*\)", r"\1", lowered)


def _segments(lowered: str, facts: dict[str, Any]) -> dict[str, str]:
    """Text after each named company, up to the next company name."""
    hits = []
    for row in facts.get("companies") or []:
        name = str(row["name"]).casefold()
        for match in re.finditer(r"\b" + re.escape(name) + r"\b", lowered):
            hits.append((match.start(), match.end(), name))
    hits.sort()
    out: dict[str, str] = {}
    for index, (_start, stop, name) in enumerate(hits):
        nxt = hits[index + 1][0] if index + 1 < len(hits) else len(lowered)
        out[name] = out.get(name, "") + " " + lowered[stop:nxt]
    return out


def _numbers_ok(lowered: str, facts: dict[str, Any]) -> bool:
    """Every percent must be the 1% line or a share we computed; every N of M must be a real pair."""
    shares = {"1", "1.0", "1.00"}
    pairs = set()
    for row in facts.get("companies") or []:
        shares |= {f"{row['share'] * 100:.2f}", f"{row['share'] * 100:.1f}"}
        pairs.add((int(row["invalid"]), int(row["total"])))
    for bundle in facts.get("cause_sets") or []:
        if bundle.get("projected") is not None:
            shares |= {f"{bundle['projected'] * 100:.2f}", f"{bundle['projected'] * 100:.1f}"}
        for cause in bundle.get("causes") or []:
            pairs.add((int(cause["count"]), int(bundle["invalid"])))
    if any(value not in shares for value in _PCT.findall(lowered)):
        return False
    for left, right in _N_OF_M.findall(lowered):
        if (int(left.replace(",", "")), int(right.replace(",", ""))) not in pairs:
            return False
    return True


def show_me_fact(view: dict[str, Any], step_id: str) -> tuple[str, str]:
    facts = view.get("explore") or {}
    if step_id == "eda":
        names = _join([row["name"] for row in facts.get("flagged") or []])
        sentence = f"{names} are over 1%." if names else "No company with enough reports is over 1%."
        return "the companies over 1%", sentence
    if step_id == "pareto":
        parts = []
        for bundle in facts.get("cause_sets") or []:
            parts.append(f"{bundle['name']} needs {_cause_label(bundle)}")
        sentence = f"{_join(parts)} to get under 1%." if parts else "No company is over 1%."
        return "the causes that get each company under 1%", sentence
    if step_id == "responses":
        parts = [f"{issue['company']} {issue['code']} is {issue['branch']}" for issue in facts.get("issues") or []]
        sentence = f"{_join(parts)}." if parts else "There is no open issue."
        return "the most likely cause branch per issue", sentence
    parts = []
    for row in facts.get("closeouts") or []:
        word = "gets under 1%" if row.get("under") else "stays over 1%"
        parts.append(f"{row['company']} {word}")
    sentence = f"{_join(parts)}." if parts else "No company plan is open."
    return "whether each plan gets under 1%", sentence


def _pareto_claim(lowered: str, facts: dict[str, Any]) -> bool:
    if not re.search(r"\b(?:under|below)\s+1\b", lowered):
        return False
    bundles = {str(bundle["name"]).casefold(): bundle for bundle in facts.get("cause_sets") or []}
    segments = _segments(lowered, facts)
    if not bundles or set(segments) != set(bundles):
        return False
    for name, bundle in bundles.items():
        wanted = {str(cause["code"]).casefold() for cause in bundle["causes"]}
        tied = {str(code).casefold() for code in bundle.get("tied") or []}
        said = set(_CODE.findall(segments[name]))
        if said == wanted:
            continue
        if tied and said in [{code} for code in tied]:
            continue
        if tied and said == tied and re.search(r"\b(?:tied|or)\b", segments[name]):
            continue
        return False
    return True


def _response_claim(lowered: str, facts: dict[str, Any]) -> bool:
    issues = facts.get("issues") or []
    segments = _segments(lowered, facts)
    if not issues or set(segments) != {str(issue["company"]).casefold() for issue in issues}:
        return False
    branches = "|".join(sorted({name.casefold() for name in _BRANCH.values()} | {"environment"}))
    for issue in issues:
        segment = segments[str(issue["company"]).casefold()]
        code = str(issue["code"]).casefold()
        chunk = re.search(re.escape(code) + r"(.*?)(?=\binv-[a-z]+\b|$)", segment)
        if not chunk:
            return False
        said = set(re.findall(r"\b(" + branches + r")\b", chunk.group(1)))
        if said != {str(issue["branch"]).casefold()}:
            return False
    return True


def _closeout_claim(lowered: str, facts: dict[str, Any]) -> bool:
    rows = facts.get("closeouts") or []
    segments = _segments(lowered, facts)
    if not rows or set(segments) != {str(row["company"]).casefold() for row in rows}:
        return False
    for row in rows:
        segment = segments[str(row["company"]).casefold()]
        under = bool(re.search(r"\b(?:under|below)\s+1\b", segment))
        over = bool(re.search(r"\b(?:over|above|stays)\b", segment))
        if not under and not over:
            under = bool(re.search(r"\b(?:under|below)\s+1\b", lowered))
            over = bool(re.search(r"\b(?:over|above|stays)\b", lowered))
        if row.get("under") and not (under and not over):
            return False
        if not row.get("under") and not (over and not under):
            return False
    if re.search(r"\b(?:under|below)\s+1\b", lowered) is None:
        return False
    return True


def _join(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def hints_for(step_id: str) -> list[str]:
    if step_id == "eda":
        return []
    if step_id == "pareto":
        return [
            "Things to notice: the chart ranks the biggest problems first. The line adds them up.",
            "The cause set is the smallest group at the top of that ranking that brings the company under 1%.",
            "Mention to the agent: name the biggest invalid category for one flagged company.",
        ]
    if step_id == "responses":
        return [
            "Things to notice: each company note is simulated and labeled. It was not sent.",
            "The cause diagram groups possible causes. The marked branch is the one the note points at.",
            "Mention to the agent: which labels are co-reported with a company's invalid category.",
        ]
    return [
        "Things to notice: the projected share is what remains after the cause set is removed.",
        "Each close-out is simulated and labeled. It was not sent.",
        "Mention to the agent: does each company's plan get under 1%.",
    ]


def prompts_for(step_id: str, facts: dict[str, Any]) -> list[str]:
    flagged = [row["name"] for row in facts.get("flagged") or []]
    first = flagged[0] if flagged else "Roche"
    if step_id == "eda":
        return [
            "how many complaints are in the dataset",
            "which companies are over 1%",
            "which companies have too few reports to judge",
        ]
    if step_id == "pareto":
        return [
            f"name the biggest invalid category for {first}",
            f"which causes bring {first} under 1%",
            "how many complaints are in the dataset",
        ]
    if step_id == "responses":
        code = ""
        issues = facts.get("issues") or []
        if issues:
            code = str(issues[0]["code"])
        return [
            f"what is the most likely root cause for {first} {code}".strip(),
            f"which labels are co-reported with {first} {code}".strip(),
            "which companies are over 1%",
        ]
    return [
        f"does {first}'s plan get under 1%",
        "what is the projected invalid share after the fix",
        "how many complaints are in the dataset",
    ]
