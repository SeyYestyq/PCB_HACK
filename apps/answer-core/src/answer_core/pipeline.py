from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ORGANIZER_KB = ROOT / "data" / "organizer" / "kb"
FIXTURE_KB = ROOT / "data" / "fixtures" / "kb.jsonl"
CHUNK_CHARS = 1200
LLM_TIMEOUT_SEC = 60


def _load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE from .env into os.environ if not already set. No secret logging."""
    env_path = path or (ROOT / ".env")
    if not env_path.is_file():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not key or key in os.environ:
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ[key] = value
    except OSError:
        return


_load_dotenv()


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value and value != name:
            return value
    return default


def default_kb_path() -> Path:
    env = os.getenv("PSB_KB_PATH", "").strip()
    if env:
        p = Path(env)
        return p if p.is_absolute() else (ROOT / p)
    if ORGANIZER_KB.is_dir() and any(ORGANIZER_KB.glob("*.txt")):
        return ORGANIZER_KB
    return FIXTURE_KB


DEFAULT_KB = default_kb_path()


def llm_configured() -> bool:
    base = _env("LLM_BASE_URL", "BASE_URL", "OPENAI_BASE_URL")
    key = _env("LLM_API_KEY", "OPENAI_API_KEY")
    return bool(base and key)


def _llm_settings() -> tuple[str, str, str]:
    base = _env("LLM_BASE_URL", "BASE_URL", "OPENAI_BASE_URL").rstrip("/")
    key = _env("LLM_API_KEY", "OPENAI_API_KEY")
    model = _env("LLM_MODEL", "GEN_MODEL", "OPENAI_MODEL", default="deepseek-chat")
    return base, key, model


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


# Demo counterparties / contract ids present in organizer KB (fail-open to retrieve).
_DEMO_ENTITY_FRAGMENTS = (
    "северн",
    "альфа-трейд",
    "альфа трейд",
    "альфа-трейдинг",
    "альфа трейдинг",
    "а-08",
    "п-17",
    "пт-05",
)
_LEGAL_FORM_RE = re.compile(r"(?<!\w)(?:ооо|ип|ао|пао|зао|нао|оао)(?!\w)", re.IGNORECASE)
_QUOTED_NAME_RE = re.compile(r"[«\"„“]([^»\"”]{2,80})[»\"”]")
_CONTRACT_NO_RE = re.compile(
    r"(?:№|#)\s*[\w./\-]+|(?<!\w)(?:а-\d{2}|п-\d{2}|пт-\d{2})(?!\w)",
    re.IGNORECASE,
)


def _has_counterparty_or_contract_id(question: str) -> bool:
    """True when the question already names a counterparty or contract identifier."""
    low = question.lower().replace("ё", "е")
    if _LEGAL_FORM_RE.search(low):
        return True
    if _QUOTED_NAME_RE.search(question):
        return True
    if _CONTRACT_NO_RE.search(low):
        return True
    if any(x in low for x in ("инн", "контрагент", "номер договора", "номер контракта")):
        return True
    if any(frag in low for frag in _DEMO_ENTITY_FRAGMENTS):
        return True
    return False


def _is_ambiguous_contract(question: str) -> bool:
    """Clarify only bare 'договор' questions without party/id/type anchors."""
    low = question.lower().replace("ё", "е")
    if "договор" not in low:
        return False
    if _has_counterparty_or_contract_id(question):
        return False
    # Narrow corpus without a named party (still searchable).
    type_anchors = ("регламент", "правоспособ", "аренд", "поставк", "кредитн")
    if any(a in low for a in type_anchors):
        return False
    return len(_tokens(question)) < 8


def _lexical_answer(citations: list[Citation]) -> str:
    parts = [f"Согласно {c.title} ({c.span}): {c.quote}" for c in citations]
    return " ".join(parts) + " Выводы ограничены найденными фрагментами базы знаний."


def _citations_verified(text: str, citations: list[Citation]) -> bool:
    if not text.strip() or not citations:
        return False
    return all(c.doc_id in text or c.title in text for c in citations)


def _call_llm(question: str, citations: list[Citation]) -> str | None:
    """OpenAI-compatible chat/completions. Returns polished text or None on failure."""
    if not llm_configured():
        return None
    base, key, model = _llm_settings()
    context_blocks = []
    for i, c in enumerate(citations, 1):
        context_blocks.append(
            f"[{i}] doc_id={c.doc_id}\ntitle={c.title}\nspan={c.span}\nquote={c.quote}"
        )
    context = "\n\n".join(context_blocks)
    system = (
        "Ты юридический ассистент банка. Отвечай ТОЛЬКО по приложенным фрагментам базы знаний. "
        "Не используй внешние знания и не выдумывай нормы. В ответе обязательно упомяни "
        "название документа (title) или doc_id каждого использованного фрагмента. "
        "Если фрагментов недостаточно — прямо скажи, что данных в базе не хватает."
    )
    user = f"Фрагменты базы знаний:\n{context}\n\nВопрос:\n{question}"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": 1024,
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
            return " ".join(content.split())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return None


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

    # Fail-closed: citations ONLY from retrieved KB spans (never from model knowledge).
    citations = [
        Citation(
            doc_id=h["doc_id"],
            title=h["title"],
            span=h.get("section", ""),
            quote=h["text"][:240],
        )
        for h in hits
    ]

    text: str | None = None
    if llm_configured():
        polished = _call_llm(q, citations)
        if polished and _citations_verified(polished, citations):
            text = polished
        elif polished:
            # Model answered but dropped citation anchors — append lexical anchors, keep KB cites.
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

    return Answer("grounded", text, citations=citations)


def answer_question_dict(question: str, kb_path: Path | None = None) -> dict:
    return answer_question(question, kb_path).to_dict()
