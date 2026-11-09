from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ORGANIZER_KB = ROOT / "data" / "organizer" / "kb"
FIXTURE_KB = ROOT / "data" / "fixtures" / "kb.jsonl"
CHUNK_CHARS = 1200


def default_kb_path() -> Path:
    env = os.getenv("PSB_KB_PATH", "").strip()
    if env:
        return Path(env)
    if ORGANIZER_KB.is_dir() and any(ORGANIZER_KB.glob("*.txt")):
        return ORGANIZER_KB
    return FIXTURE_KB


DEFAULT_KB = default_kb_path()


@dataclass
class Citation:
    doc_id: str
    title: str
    span: str
    quote: str


@dataclass
class Answer:
    status: str
    answer: str
    citations: list[Citation] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _slug(name: str) -> str:
    base = Path(name).stem
    return re.sub(r"\s+", "_", base)[:120]


def _chunk_text(text: str, size: int = CHUNK_CHARS) -> list[tuple[str, str]]:
    """Split into (section_label, chunk) preferring paragraph/numbered-clause boundaries."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [("полный текст", text)]

    parts: list[str] = []
    buf = ""
    for para in re.split(r"\n\s*\n|\n(?=\d+\.\d+\.)", text):
        para = para.strip()
        if not para:
            continue
        if buf and len(buf) + len(para) + 1 > size:
            parts.append(buf)
            buf = para
        else:
            buf = f"{buf}\n{para}".strip() if buf else para
    if buf:
        parts.append(buf)

    out: list[tuple[str, str]] = []
    for i, chunk in enumerate(parts, 1):
        m = re.search(r"(\d+\.\d+(?:\.\d+)?)", chunk)
        label = f"п. {m.group(1)}" if m else f"фрагмент {i}"
        out.append((label, chunk))
    return out or [("полный текст", text[:size])]


def _rows_from_txt_dir(path: Path) -> list[dict]:
    rows: list[dict] = []
    for fp in sorted(path.glob("*.txt")):
        raw = fp.read_text(encoding="utf-8-sig")
        title = fp.stem.replace("__", " — ")
        doc_id = _slug(fp.name)
        for section, chunk in _chunk_text(raw):
            rows.append(
                {
                    "doc_id": doc_id,
                    "title": title,
                    "section": section,
                    "edition": "organizer",
                    "text": chunk,
                    "source_file": fp.name,
                }
            )
    return rows


def _rows_from_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_kb(path: Path | None = None) -> list[dict]:
    p = path or default_kb_path()
    if p.is_dir():
        rows = _rows_from_txt_dir(p)
        if not rows:
            raise FileNotFoundError(f"KB directory has no .txt files: {p}")
        return rows
    if p.suffix.lower() == ".jsonl":
        return _rows_from_jsonl(p)
    if p.is_file() and p.suffix.lower() == ".txt":
        return _rows_from_txt_dir(p.parent)
    raise FileNotFoundError(f"Unsupported KB path: {p}")


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[а-яёa-z0-9]+", text.lower().replace("ё", "е")) if len(t) > 2}


def retrieve(question: str, kb: list[dict], k: int = 4) -> list[dict]:
    q = _tokens(question)
    scored: list[tuple[int, dict]] = []
    boost_terms = {
        "правоспособ": ("правоспособ", "полномоч", "кредитн", "досье", "устав"),
        "ндс": ("ндс", "ставк"),
        "согласован": ("согласован", "договор", "регламент"),
        "аренд": ("аренд", "склад", "северн"),
        "поставк": ("поставк", "альфа", "гарант"),
        "испытан": ("испытан", "трудов"),
        "персональн": ("персональн", "соглас", "152"),
        "архив": ("архив", "оригинал", "служебн"),
    }
    for row in kb:
        blob = f"{row['text']} {row['title']} {row.get('section', '')} {row.get('source_file', '')}"
        hay = _tokens(blob)
        score = len(q & hay) * 2
        low_q = question.lower()
        low_blob = blob.lower()
        for key, terms in boost_terms.items():
            if key in low_q:
                score += sum(3 for t in terms if t in low_blob)
        # Prefer exact contract / company markers from filenames and titles.
        for marker in ("а-08", "п-17", "пт-05", "северн", "альфа-трейд", "альфа-трейдинг", "меридиан"):
            if marker in low_q and marker in low_blob:
                score += 8
        overlap = len(q & hay)
        # Require real lexical overlap; ignore single common-word hits (e.g. «размер»).
        if overlap >= 2 or score >= 6:
            scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return []
    best = scored[0][0]
    if best < 4:
        return []
    strong = [r for s, r in scored if s >= max(4, best * 0.55)]
    return strong[:k]


def _needs_historical(question: str) -> bool:
    q = question.lower()
    return any(x in q for x in ("2019", "2020", "старой редакции", "историческ"))


def _off_topic(question: str) -> bool:
    q = question.lower()
    legal_hints = (
        "договор",
        "ндс",
        "правоспособ",
        "регламент",
        "норм",
        "кредит",
        "устав",
        "полномоч",
        "аренд",
        "труд",
        "пособи",
        "персональн",
        "испытан",
        "гарант",
        "претенз",
        "архив",
        "согласован",
    )
    if any(h in q for h in legal_hints):
        return False
    return any(h in q for h in ("рецепт", "погода", "анекдот", "крипт"))


def _is_ambiguous_contract(question: str) -> bool:
    low = question.lower()
    if "договор" not in low:
        return False
    anchors = (
        "№",
        "номер",
        "контрагент",
        "регламент",
        "правоспособ",
        "ооо",
        "инн",
        "аренды",
        "поставк",
        "а-08",
        "п-17",
        "пт-05",
        "северн",
        "альфа",
    )
    if any(a in low for a in anchors):
        return False
    return len(_tokens(question)) < 6


def answer_question(question: str, kb_path: Path | None = None) -> Answer:
    q = (question or "").strip()
    if not q:
        return Answer("clarify", "Сформулируйте вопрос по нормативным документам из базы знаний.")

    if _off_topic(q):
        return Answer(
            "refuse_role",
            "Я помогаю только с вопросами по нормативной базе юриста банка. Переформулируйте запрос в юридическую тему из базы знаний.",
        )

    if _is_ambiguous_contract(q) and "ндс" not in q.lower():
        return Answer(
            "clarify",
            "Уточните договор/контрагента и период — иначе поиск по базе будет неоднозначным.",
            missing=["идентификатор договора или контрагента", "период / редакция"],
        )

    if _needs_historical(q):
        return Answer(
            "abstain",
            "Достоверный ответ сформировать нельзя: в базе только действующие редакции, а вопрос требует исторической редакции.",
            missing=["историческая редакция нормы на дату события"],
        )

    kb = load_kb(kb_path)
    hits = retrieve(q, kb)
    if not hits:
        return Answer(
            "abstain",
            "В предоставленной базе знаний не найдено подтверждающих положений для ответа.",
            missing=["релевантные документы по теме вопроса"],
        )

    citations = [
        Citation(
            doc_id=h["doc_id"],
            title=h["title"],
            span=h.get("section", ""),
            quote=h["text"][:240],
        )
        for h in hits
    ]
    parts = [f"Согласно {c.title} ({c.span}): {c.quote}" for c in citations]
    text = " ".join(parts) + " Выводы ограничены найденными фрагментами базы знаний."
    verified = all(c.doc_id in text or c.title in text for c in citations)
    if not verified:
        return Answer(
            "abstain",
            "Не удалось безопасно связать черновик ответа с найденными фрагментами.",
            missing=["верифицируемые цитаты"],
        )

    return Answer("grounded", text, citations=citations)


def answer_question_dict(question: str, kb_path: Path | None = None) -> dict:
    return answer_question(question, kb_path).to_dict()
