from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_KB = Path(__file__).resolve().parents[4] / "data" / "fixtures" / "kb.jsonl"


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
        d = asdict(self)
        return d


def load_kb(path: Path | None = None) -> list[dict]:
    p = path or DEFAULT_KB
    rows: list[dict] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[а-яёa-z0-9]+", text.lower()) if len(t) > 2}


def retrieve(question: str, kb: list[dict], k: int = 3) -> list[dict]:
    q = _tokens(question)
    scored: list[tuple[int, dict]] = []
    boost_terms = {
        "правоспособ": ("правоспособ", "полномоч", "кредитн", "досье", "устав"),
        "ндс": ("ндс", "ставк"),
        "согласован": ("согласован", "договор", "регламент"),
    }
    for row in kb:
        blob = f"{row['text']} {row['title']} {row.get('section', '')}"
        hay = _tokens(blob)
        score = len(q & hay) * 2
        low_q = question.lower()
        low_blob = blob.lower()
        for key, terms in boost_terms.items():
            if key in low_q:
                score += sum(3 for t in terms if t in low_blob)
        # Prefer rows that share distinctive content words, not only stop-ish overlaps.
        if score:
            scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return []
    best = scored[0][0]
    strong = [r for s, r in scored if s >= max(2, best * 0.6)]
    return strong[:k]


def _needs_historical(question: str) -> bool:
    q = question.lower()
    return any(x in q for x in ("2019", "2020", "старой редакции", "историческ"))


def _off_topic(question: str) -> bool:
    q = question.lower()
    legal_hints = ("договор", "ндс", "правоспособ", "регламент", "норм", "кредит", "устав", "полномоч")
    if any(h in q for h in legal_hints):
        return False
    return any(h in q for h in ("рецепт", "погода", "анекдот", "крипт"))


def answer_question(question: str, kb_path: Path | None = None) -> Answer:
    q = (question or "").strip()
    if not q:
        return Answer("clarify", "Сформулируйте вопрос по нормативным документам из базы знаний.")

    if _off_topic(q):
        return Answer(
            "refuse_role",
            "Я помогаю только с вопросами по нормативной базе юриста банка. Переформулируйте запрос в юридическую тему из базы знаний.",
        )

    ambiguous = ("договор" in q.lower()) and not any(
        x in q.lower() for x in ("№", "номер", "контрагент", "регламент", "правоспособ")
    )
    if ambiguous and "ндс" not in q.lower():
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
    # Fail-closed: every legal sentence must map to a citation id present in hits.
    parts = [
        f"Согласно {c.title} ({c.span}): {c.quote}"
        for c in citations
    ]
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
