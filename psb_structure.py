"""Structural chunking by numbered clauses and paragraphs."""

from __future__ import annotations

import re
from pathlib import Path

from psb_config import CHUNK_CHARS

_CLAUSE_SPLIT = re.compile(r"\n(?=\d+\.\d+(?:\.\d+)?\.)")
_MAJOR_SPLIT = re.compile(r"\n(?=\d+\.\s+[А-ЯЁA-Z])")
_CLAUSE_LABEL = re.compile(r"^(\d+\.\d+(?:\.\d+)?)")
_MAJOR_LABEL = re.compile(r"^(\d+)\.\s+")
_CLAUSE_START = re.compile(r"(?m)^(\d+\.\d+(?:\.\d+)?)\.\s+")
_DATE_RE = re.compile(
    r"(?:от\s+)?(\d{1,2})[./](\d{1,2})[./](\d{4})|"
    r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})",
    re.IGNORECASE,
)
_MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}
_CONTRACT_NO = re.compile(
    r"(?:№|#)\s*([А-ЯA-Zа-яa-z]{1,4}[-–—/]?\d{1,4}(?:/\d{4})?)",
    re.IGNORECASE,
)
_INN = re.compile(r"ИНН\s*(\d{10}|\d{12})", re.IGNORECASE)
_QUOTED = re.compile(r"[«\"„“]([^»\"”]{2,80})[»\"”]")


def slug(name: str) -> str:
    base = Path(name).stem
    return re.sub(r"\s+", "_", base)[:120]


def parse_date_parts(text: str) -> list[tuple[int, int, int]]:
    dates: list[tuple[int, int, int]] = []
    for m in _DATE_RE.finditer(text or ""):
        if m.group(1) and m.group(2) and m.group(3):
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            d = int(m.group(4))
            mo = _MONTHS.get((m.group(5) or "").lower(), 0)
            y = int(m.group(6))
        if mo and 1 <= d <= 31 and 1900 <= y <= 2100:
            dates.append((y, mo, d))
    return dates


def date_to_int(parts: tuple[int, int, int]) -> int:
    y, m, d = parts
    return y * 10_000 + m * 100 + d


def date_mentions(text: str) -> list[tuple[int, str, str]]:
    """Each date as (YYYYMMDD, lowercase prefix, lowercase suffix)."""
    found: list[tuple[int, str, str]] = []
    raw = text or ""
    for m in _DATE_RE.finditer(raw):
        if m.group(1) and m.group(2) and m.group(3):
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            day = int(m.group(4))
            month = _MONTHS.get((m.group(5) or "").lower(), 0)
            year = int(m.group(6))
        if not month or not (1 <= day <= 31) or not (1900 <= year <= 2100):
            continue
        prefix = raw[max(0, m.start() - 60) : m.start()].lower()
        suffix = raw[m.end() : m.end() + 40].lower()
        found.append((date_to_int((year, month, day)), prefix, suffix))
    return found


def extract_contract_numbers(text: str) -> list[str]:
    found: list[str] = []
    for m in _CONTRACT_NO.finditer(text or ""):
        raw = m.group(1).replace("–", "-").replace("—", "-").upper()
        raw = re.sub(r"\s+", "", raw)
        if raw and raw not in found:
            found.append(raw)
    # Filename-style markers without №
    for m in re.finditer(r"(?<!\w)([АA]-?\d{2}/\d{4}|П-?\d{2}/\d{4}|ПТ-?\d{2}/\d{4})(?!\w)", text or "", re.I):
        raw = m.group(1).replace("–", "-").replace("—", "-").upper()
        if raw not in found:
            found.append(raw)
    return found


def extract_inns(text: str) -> list[str]:
    return list(dict.fromkeys(m.group(1) for m in _INN.finditer(text or "")))


def extract_quoted_names(text: str) -> list[str]:
    return [m.group(1).strip() for m in _QUOTED.finditer(text or "") if m.group(1).strip()]


def _major_num(piece: str) -> str | None:
    stripped = piece.strip()
    m = _CLAUSE_LABEL.search(stripped) or _MAJOR_LABEL.search(stripped)
    if not m:
        return None
    return m.group(1).split(".")[0]


def chunk_text(text: str, size: int = CHUNK_CHARS) -> list[tuple[str, str]]:
    """Split into (section_label, chunk) on numbered clauses; avoid cross-section merges."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= size:
        label = "полный текст"
        m = _CLAUSE_LABEL.search(text)
        if m:
            label = f"п. {m.group(1)}"
        return [(label, text)]

    # First cut on major section headers («3. Арендная плата»), then on N.M clauses.
    rough = [p.strip() for p in _MAJOR_SPLIT.split(text) if p.strip()]
    pieces: list[str] = []
    for block in rough:
        parts = [p.strip() for p in _CLAUSE_SPLIT.split(block) if p.strip()]
        pieces.extend(parts or [block])
    if len(pieces) <= 1:
        pieces = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    parts: list[str] = []
    buf = ""
    buf_major: str | None = None
    for para in pieces:
        major = _major_num(para)
        # Keep each numbered clause atomic when it already fits; never merge across majors.
        crosses = buf and buf_major and major and major != buf_major
        too_big = buf and len(buf) + len(para) + 1 > size
        if crosses or too_big:
            parts.append(buf)
            buf = para
            buf_major = major
        else:
            buf = f"{buf}\n{para}".strip() if buf else para
            if buf_major is None:
                buf_major = major
    if buf:
        parts.append(buf)

    out: list[tuple[str, str]] = []
    for i, chunk in enumerate(parts, 1):
        m = _CLAUSE_LABEL.search(chunk) or re.search(r"(\d+\.\d+(?:\.\d+)?)", chunk)
        label = f"п. {m.group(1)}" if m else f"фрагмент {i}"
        out.append((label, chunk))
    return out or [("полный текст", text[:size])]


def sentence_bounded_excerpt(text: str, limit: int = CHUNK_CHARS) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    piece = text[:limit]
    for sep in (". ", ".\n", "; ", "\n"):
        idx = piece.rfind(sep)
        if idx >= limit // 2:
            return piece[: idx + 1].strip()
    return piece.strip()


def focused_excerpt(question: str, text: str, limit: int = CHUNK_CHARS) -> str:
    """Prefer the clause/window inside a unit that best matches the question."""
    from psb_textnorm import tokens as _tokens

    text = (text or "").strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text

    q_tokens = set(_tokens(question or ""))
    # Candidate starts: clause markers and paragraph breaks.
    starts = {0}
    for m in re.finditer(r"(?:^|\n)(\d+\.\d+(?:\.\d+)?)\.\s", text):
        starts.add(m.start() if text[m.start()] != "\n" else m.start() + 1)
    for m in re.finditer(r"\n\s*\n", text):
        starts.add(m.end())

    best_score = -1.0
    best = text[:limit]
    for start in sorted(starts):
        window = text[start : start + limit]
        if not window.strip():
            continue
        # Trim to sentence end when possible.
        piece = window
        for sep in (". ", ".\n", "; ", "\n"):
            idx = piece.rfind(sep)
            if idx >= limit // 3:
                piece = piece[: idx + 1]
                break
        overlap = len(q_tokens & set(_tokens(piece))) if q_tokens else 0
        # Bonus if window opens on a numbered clause mentioned in the question.
        bonus = 0
        head = re.match(r"(\d+\.\d+(?:\.\d+)?)", piece.strip())
        if head and head.group(1) in (question or ""):
            bonus = 3
        score = overlap + bonus
        if score > best_score:
            best_score = score
            best = piece.strip()
    return best or sentence_bounded_excerpt(text, limit)
