"""Shared answer path for solution.py and FastAPI."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from psb_catalog import build_catalog, match_catalog, needs_clarify_contract
from psb_config import (
    LLM_TIMEOUT_SEC,
    MAX_QUESTION_CHARS,
    QUOTE_CHARS,
    env_int,
    llm_configured,
    llm_settings,
)
from psb_editions import extract_event_date, filter_kb_by_edition, needs_historical_law
from psb_ingest import default_kb_path, load_kb
from psb_retrieve import retrieve
from psb_structure import sentence_bounded_excerpt
from psb_textnorm import normalize, strip_markdown

# Re-export for callers / tests
__all__ = [
    "Answer",
    "Citation",
    "Turn",
    "answer_question",
    "answer_question_dict",
    "default_kb_path",
    "load_kb",
    "parse_dialog",
    "llm_configured",
]


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
    options: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.answer = strip_markdown(self.answer or "")

    def to_dict(self) -> dict:
        data = asdict(self)
        if not data.get("options"):
            data.pop("options", None)
        return data


@dataclass
class Turn:
    role: str  # user | assistant
    content: str


_DIALOG_LINE = re.compile(
    r"^\s*(?:\[?(?:user|assistant|human|ai)\]?|"
    r"пользователь|ассистент|бот|юрист|оператор)\s*[:\-–—]\s*(.*)$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_dialog(text: str) -> tuple[str, list[Turn]]:
    """
    Parse platform dialog packed into one question string.
    Returns (last_user_utterance, history_turns_excluding_last_user).
    """
    raw = (text or "").strip()
    if not raw:
        return "", []

    turns: list[Turn] = []
    # Split by known role prefixes
    parts = re.split(
        r"(?=(?:^|\n)\s*(?:Пользователь|Ассистент|User|Assistant|Human|AI)\s*[:\-–—])",
        raw,
        flags=re.IGNORECASE,
    )
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(
            r"(Пользователь|Ассистент|User|Assistant|Human|AI)\s*[:\-–—]\s*(.*)",
            part,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not m:
            continue
        role_raw = m.group(1).lower()
        content = m.group(2).strip()
        role = "assistant" if role_raw in {"ассистент", "assistant", "ai"} else "user"
        if content:
            turns.append(Turn(role=role, content=content[:MAX_QUESTION_CHARS]))

    if not turns:
        return raw[:MAX_QUESTION_CHARS], []

    last_user_idx = None
    for i in range(len(turns) - 1, -1, -1):
        if turns[i].role == "user":
            last_user_idx = i
            break
    if last_user_idx is None:
        return raw[:MAX_QUESTION_CHARS], turns[-10:]

    question = turns[last_user_idx].content
    history = turns[:last_user_idx][-10:]
    return question[:MAX_QUESTION_CHARS], history


def _off_topic(question: str) -> bool:
    q = normalize(question)
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
        "бухгалтер",
        "инн",
        "закон",
        "кодекс",
        "стать",
    )
    if any(h in q for h in legal_hints):
        return False
    return any(h in q for h in ("рецепт", "погода", "анекдот", "крипт", "стих"))


_GREETINGS = {
    "ку",
    "привет",
    "здравствуйте",
    "здравствуй",
    "hi",
    "hello",
    "hey",
    "ок",
    "ok",
    "спасибо",
    "тест",
    "test",
    "да",
    "нет",
    "ало",
    "хай",
}


def _not_a_legal_question(question: str) -> bool:
    """Greetings and scraps are not a search miss."""
    q = normalize(question).strip(" .!?,")
    if q in _GREETINGS:
        return True
    from psb_textnorm import tokens

    return len(tokens(question)) == 0


def _role_attack(question: str) -> bool:
    q = normalize(question)
    return any(
        x in q
        for x in (
            "игнорируй инструкции",
            "забудь правила",
            "ты теперь dan",
            "system prompt",
            "сломай защит",
            "вырежи системн",
        )
    )


def _illegal(question: str) -> bool:
    q = normalize(question)
    return any(
        x in q
        for x in (
            "как скрыть доход",
            "помоги уклонить",
            "схема обнала",
            "подделать документ",
            "взятк",
        )
    )


def _user_context(question: str, history: list[Turn]) -> str:
    """Last question plus earlier user turns, so a follow-up still names the contract."""
    previous = [turn.content for turn in history if turn.role == "user"]
    return "\n".join([*previous[-4:], question]).strip()


def _scope_to_contract(kb: list[dict], cards: list) -> list[dict]:
    """One named counterparty: search its contract and amendments, not the whole corpus."""
    if len(cards) != 1:
        return kb
    card = cards[0]
    doc_ids = set(card.doc_ids)
    if not doc_ids or len(doc_ids) > 3:
        return kb
    numbers = {re.sub(r"[\s–—]", "", num).upper() for num in card.contract_numbers}
    scoped: list[dict] = []
    for row in kb:
        if row.get("doc_id") in doc_ids:
            scoped.append(row)
            continue
        if row.get("kind") != "amendment" or not numbers:
            continue
        blob = re.sub(r"[\s–—]", "", f"{row.get('title', '')} {row.get('source_file', '')}").upper()
        if any(num and num in blob for num in numbers):
            scoped.append(row)
    return scoped or kb


def _llm_abstain_leadin(text: str) -> bool:
    folded = normalize(text)
    return any(
        phrase in folded
        for phrase in (
            "нет положений для ответа",
            "не содержат ответа",
            "не относится к вопросу",
            "нет норм о",
            "в предоставленной базе знаний нет",
            "в базе знаний нет",
            "не найдено подтверждающих",
        )
    )


def _status_from_text(text: str, *, citations_verified: bool = False) -> str:
    folded = normalize(text)
    if _llm_abstain_leadin(text):
        if citations_verified and (
            re.search(r"\d", text)
            or "п." in folded
            or "пункт" in folded
            or "источник" in folded
        ):
            # LLM hedged with «нет положений», but cited concrete fragments — keep answer.
            pass
        else:
            return "abstain"
    if any(
        phrase in folded
        for phrase in (
            "для полного ответа не хватает",
            "не хватает:",
            "не хватает ",
        )
    ):
        return "limited"
    return "grounded"


def _lexical_answer(citations: list[Citation]) -> str:
    # Keep the answer readable for the LLM judge (prefer top evidence).
    parts = [f"Согласно {c.title} ({c.span}): {c.quote}" for c in citations[:3]]
    return " ".join(parts) + " Выводы ограничены найденными фрагментами базы знаний."


def _citations_verified(text: str, citations: list[Citation]) -> bool:
    if not text.strip() or not citations:
        return False
    return all(c.doc_id in text or c.title in text for c in citations)


def _history_block(history: list[Turn] | None) -> str:
    if not history:
        return ""
    lines = []
    for turn in history[-10:]:
        # Assistant turns are dialog context, not facts from KB.
        label = "Пользователь" if turn.role == "user" else "Ассистент (не источник фактов)"
        lines.append(f"{label}: {turn.content}")
    return "История диалога:\n" + "\n".join(lines) + "\n\n"


def _call_llm(question: str, citations: list[Citation], history: list[Turn] | None = None) -> str | None:
    if not llm_configured():
        return None
    base, key, model = llm_settings()
    context_blocks = []
    for i, c in enumerate(citations, 1):
        context_blocks.append(
            f"[{i}] doc_id={c.doc_id}\ntitle={c.title}\nspan={c.span}\nquote={c.quote}"
        )
    context = "\n\n".join(context_blocks)
    system = (
        "Ты юридический ассистент банка. Отвечай только по приложенным фрагментам. "
        "Не используй внешние знания и не выдумывай нормы, числа и пункты. "
        "Пиши обычным текстом без Markdown: без **, *, #, списков с дефисом и блоков кода. "
        "Каждое юридически значимое утверждение сопроводи названием документа и пунктом; "
        "срок, сумму и порог процитируй дословно. "
        "Если пользователь назвал сумму, срок или факт, которого нет во фрагментах, поправь его. "
        "Вывод из двух пунктов допустим только когда он прямо из них следует; "
        "отсутствие запрета не считай разрешением. "
        "Если фрагментов хватает лишь на часть вывода, ответь по найденному и закончи фразой "
        "«Для полного ответа не хватает: …». "
        "Если фрагменты не содержат ответа, напиши только: "
        "«В предоставленной базе знаний нет положений для ответа на этот вопрос.» "
        "Если в вопросе нет даты события, а вывод зависит от редакции, добавь, что это действующая редакция на текущую дату. "
        "Реплики ассистента в истории не являются фактами."
    )
    user = (
        f"{_history_block(history)}"
        f"Фрагменты базы знаний:\n{context}\n\nВопрос:\n{question}"
    )
    max_tokens = env_int("MAX_TOKENS", 1024, 128, 4096)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": float(0.0),
        "max_tokens": max_tokens,
    }
    url = f"{base}/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SEC) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"].get("content", "")
        if isinstance(content, str) and content.strip():
            return strip_markdown(content)
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None
    return None


def answer_question(
    question: str,
    kb_path: Path | None = None,
    history: list[dict[str, Any] | Turn] | None = None,
    *,
    kb_rows: list[dict] | None = None,
) -> Answer:
    raw = (question or "").strip()
    parsed_q, parsed_hist = parse_dialog(raw)
    q = (parsed_q or raw)[:MAX_QUESTION_CHARS].strip()

    hist: list[Turn] = []
    if history:
        for item in history[-10:]:
            if isinstance(item, Turn):
                hist.append(item)
            elif isinstance(item, dict):
                role = str(item.get("role") or "user")
                content = str(item.get("content") or item.get("text") or "").strip()
                if content:
                    hist.append(Turn(role="assistant" if role == "assistant" else "user", content=content[:MAX_QUESTION_CHARS]))
    elif parsed_hist:
        hist = parsed_hist

    if not q or _not_a_legal_question(q):
        return Answer(
            "clarify",
            "Это не вопрос по базе знаний. Напишите, какое положение нужно найти: договор, контрагент, статья или срок.",
        )

    if _role_attack(q):
        return Answer(
            "refuse_role",
            "Не могу изменить роль или системные правила. Задайте вопрос по нормативной базе юриста банка.",
        )

    if _illegal(q):
        return Answer(
            "refuse_role",
            "Не помогаю с противоправными действиями. Могу разъяснить требования законодательства по документам из базы знаний.",
        )

    if _off_topic(q):
        return Answer(
            "refuse_role",
            "Я помогаю только с вопросами по нормативной базе юриста банка. Переформулируйте запрос в юридическую тему из базы знаний.",
        )

    kb = kb_rows if kb_rows is not None else load_kb(kb_path)
    try:
        from psb_vectors import ensure_index, vectors_enabled

        if vectors_enabled():
            ensure_index(kb)
    except Exception as exc:
        print(f"dense index skipped: {type(exc).__name__}", file=sys.stderr)
    catalog = build_catalog(kb)

    search_q = _user_context(q, hist)
    clarify, options = needs_clarify_contract(q, catalog)
    if clarify:
        return Answer(
            "clarify",
            "Уточните договор/контрагента — укажите номер договора или ИНН. Иначе поиск по базе неоднозначен.",
            missing=["номер договора или ИНН контрагента"],
            options=options,
        )

    kb_filtered, edition_missing = filter_kb_by_edition(kb, search_q)
    if needs_historical_law(q):
        return Answer(
            "abstain",
            "Достоверный ответ сформировать нельзя: в базе только действующие редакции законов, а вопрос требует исторической редакции.",
            missing=edition_missing or ["историческая редакция нормы на дату события"],
        )

    cards = match_catalog(q, catalog) or match_catalog(search_q, catalog)
    kb_filtered = _scope_to_contract(kb_filtered, cards)
    hits = retrieve(search_q, kb_filtered, catalog=catalog)
    if not hits:
        return Answer(
            "abstain",
            "В предоставленной базе знаний не найдено подтверждающих положений для ответа.",
            missing=["релевантные документы по теме вопроса"] + edition_missing,
        )

    # Keep citation count aligned with _lexical_answer (top-3) so verify cannot fail
    # just because a 4th hit is unused in the answer text.
    citations = [
        Citation(
            doc_id=h["doc_id"],
            title=h["title"],
            span=h.get("section", ""),
            quote=sentence_bounded_excerpt(h["text"], QUOTE_CHARS),
        )
        for h in hits[:3]
    ]

    text: str | None = None
    if llm_configured():
        polished = _call_llm(q, citations, hist)
        if polished and _citations_verified(polished, citations):
            text = polished
        elif polished:
            lexical = _lexical_answer(citations)
            merged = f"{polished} Источники: " + "; ".join(
                f"{c.title} ({c.span})" for c in citations
            )
            text = merged if _citations_verified(merged, citations) else lexical

    if not text:
        text = _lexical_answer(citations)

    if not _citations_verified(text, citations):
        return Answer(
            "abstain",
            "Не удалось безопасно связать черновик ответа с найденными фрагментами.",
            missing=["верифицируемые цитаты"],
        )

    if extract_event_date(search_q) is None and any("регламент" in c.title.lower() for c in citations):
        if "текущую дату" not in normalize(text):
            text += " Вывод относится к действующей редакции на текущую дату."

    status = _status_from_text(text, citations_verified=_citations_verified(text, citations))
    if status == "abstain":
        return Answer(
            "abstain",
            text,
            citations=[],
            missing=["положения базы знаний, которые отвечают на вопрос"],
        )
    return Answer(status, text, citations=citations, missing=edition_missing)


def answer_question_dict(
    question: str,
    kb_path: Path | None = None,
    history: list[dict[str, Any] | Turn] | None = None,
) -> dict:
    return answer_question(question, kb_path, history=history).to_dict()
