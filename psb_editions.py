"""Edition / date filters for company documents and laws."""

from __future__ import annotations

import re
from datetime import date

from psb_structure import date_to_int, parse_date_parts
from psb_textnorm import normalize

_EVENT_HINTS = (
    "на дату",
    "по состоянию",
    "действовавш",
    "редакци",
    "в 20",
    "за 20",
    "от 20",
)


_MONTH_STEMS = (
    ("январ", 1),
    ("феврал", 2),
    ("март", 3),
    ("апрел", 4),
    ("ма", 5),
    ("июн", 6),
    ("июл", 7),
    ("август", 8),
    ("сентябр", 9),
    ("октябр", 10),
    ("ноябр", 11),
    ("декабр", 12),
)


def extract_event_date(question: str) -> int | None:
    """Return YYYYMMDD int if the question binds an event date."""
    dates = parse_date_parts(question or "")
    if dates:
        return date_to_int(dates[-1])
    q = normalize(question or "")
    # «в августе 2024» has a month and a year, but no day number.
    for stem, month in _MONTH_STEMS:
        found = re.search(rf"{stem}\w*\s+(20\d{{2}})", q)
        if found and not (stem == "ма" and not q[found.start() :].startswith("ма")):
            if stem == "ма" and not re.match(r"ма[йяе]", q[found.start() :]):
                continue
            return int(found.group(1)) * 10_000 + month * 100 + 15
    years = re.findall(r"\b(20\d{2})\b", question or "")
    if years:
        return int(years[-1]) * 10_000 + 101
    return None


def needs_historical_law(question: str) -> bool:
    q = normalize(question or "")
    return any(
        x in q
        for x in (
            "старой редакции",
            "историческ",
            "редакции 2019",
            "в 2019",
            "за 2019",
            "в 2020",
            "редакции закона",
        )
    ) and any(x in q for x in ("закон", "нк", "тк", "ндс", "ставк", "кодекс"))


def filter_kb_by_edition(kb: list[dict], question: str) -> tuple[list[dict], list[str]]:
    """
    Prefer company-doc edition effective on event date.
    Laws stay current-only; missing historical law → missing note.
    """
    missing: list[str] = []
    event = extract_event_date(question)
    q = normalize(question or "")

    if needs_historical_law(question):
        missing.append("историческая редакция нормы на дату события")

    out: list[dict] = []
    # Group company regs by family (согласования договоров)
    for row in kb:
        kind = row.get("kind") or "other"
        superseded = bool(row.get("superseded"))
        effective = row.get("effective_from")

        if kind == "law":
            # Only current laws in corpus
            if superseded:
                continue
            out.append(row)
            continue

        if kind in {"company", "amendment", "other"}:
            valid_to = row.get("valid_to")
            if event is None:
                # No event date: the edition in force today. Say so in the answer.
                if superseded and "2023" not in q and "утративш" not in q and "старой" not in q:
                    continue
                out.append(row)
                continue

            # In force on the event date: started on/before it and not yet repealed.
            if effective is not None and effective > event and kind != "amendment":
                continue
            if valid_to is not None and valid_to <= event and kind != "amendment":
                continue
            out.append(row)
            continue

        out.append(row)

    asks_reg = any(
        x in q
        for x in (
            "регламент",
            "согласован",
            "одобрен",
            "генеральн",
            "юротдел",
            "юридическ отдел",
        )
    )
    if event is not None and asks_reg:
        # Prefer the company-regulation edition in force on the event date.
        company = [r for r in out if "регламент" in normalize(r.get("title") or "")]
        if company:
            before = [r for r in company if (r.get("effective_from") or 0) <= event]
            if before:
                best_eff = max(r.get("effective_from") or 0 for r in before)
                keep_ids = {
                    r["doc_id"]
                    for r in before
                    if (r.get("effective_from") or 0) == best_eff
                }
                # Prefer non-superseded twin at the same effective date when present.
                live = {i for i in keep_ids if not any(
                    r.get("doc_id") == i and r.get("superseded") for r in before
                )}
                if live:
                    keep_ids = live
                if keep_ids:
                    out = [
                        r
                        for r in out
                        if r.get("doc_id") in keep_ids
                        or "регламент" not in normalize(r.get("title") or "")
                    ]
    elif event is None and asks_reg:
        # No event date → current regulation only (drop superseded editions).
        out = [
            r
            for r in out
            if not (
                "регламент" in normalize(r.get("title") or "")
                and r.get("superseded")
            )
        ]

    return out, missing


def today_int() -> int:
    t = date.today()
    return t.year * 10_000 + t.month * 100 + t.day
