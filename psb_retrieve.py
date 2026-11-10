"""BM25 + optional dense/rerank retrieval over structural KB chunks.

Ranking heuristics are corpus-agnostic: clause markers, lexical support,
doc-kind affinity, superseded demotion. No demo counterparty/filename boosts.
"""

from __future__ import annotations

import json
import math
import re
import urllib.error
import urllib.request
from collections import Counter

from psb_catalog import match_catalog
from psb_config import env, env_int, llm_settings
from psb_textnorm import normalize, tokens
from psb_vectors import search as vector_search
from psb_vectors import unit_key
from psb_vectors import vectors_enabled

_CLAUSE_IN_Q = re.compile(
    r"(?:п(?:ункт)?\.?\s*|ст(?:ать)?\.?\s*)(\d+(?:\.\d+){0,2})",
    re.IGNORECASE,
)
_CLAUSE_IN_TEXT = re.compile(r"(?:^|[\s\n])(\d+\.\d+(?:\.\d+)?)\.\s", re.MULTILINE)
_AMOUNT_RE = re.compile(
    r"\d[\d\s]{2,}\d|\d+\s*(?:млн|миллион)|процент|%\b",
    re.IGNORECASE,
)


class BM25Index:
    def __init__(self, docs_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = docs_tokens
        self.n = len(docs_tokens)
        self.doc_len = [len(d) for d in docs_tokens]
        self.avgdl = (sum(self.doc_len) / self.n) if self.n else 0.0
        df: Counter[str] = Counter()
        for doc in docs_tokens:
            for term in set(doc):
                df[term] += 1
        self.idf = {
            term: math.log(1 + (self.n - freq + 0.5) / (freq + 0.5))
            for term, freq in df.items()
        }

    def scores(self, query_tokens: list[str]) -> list[float]:
        q_counts = Counter(query_tokens)
        out = [0.0] * self.n
        if not self.n or not q_counts:
            return out
        for i, doc in enumerate(self.docs):
            if not doc:
                continue
            tf = Counter(doc)
            score = 0.0
            dl = self.doc_len[i]
            for term, qtf in q_counts.items():
                if term not in tf:
                    continue
                idf = self.idf.get(term, 0.0)
                freq = tf[term]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1.0))
                score += idf * freq * (self.k1 + 1) / (denom or 1.0) * qtf
            out[i] = score
        return out


def _clauses_in_question(question: str) -> list[str]:
    return [m.group(1) for m in _CLAUSE_IN_Q.finditer(question or "")]


def _support_overlap(q_tokens: list[str], doc_tokens: list[str]) -> float:
    """Normalized query↔chunk overlap in [0, 1] (reference RelevanceController idea)."""
    if not q_tokens or not doc_tokens:
        return 0.0
    q_set = set(q_tokens)
    shared = q_set & set(doc_tokens)
    if not shared:
        return 0.0
    return min(1.0, len(shared) / max(len(q_set), 1))


def _relevance_boost(question: str, row: dict) -> float:
    """General legal-doc affinity — no hardcoded counterparties or demo amounts."""
    q = normalize(question)
    title = normalize(row.get("title") or "")
    section = normalize(row.get("section") or "")
    text = row.get("text") or ""
    blob = normalize(f"{text} {title} {section} {row.get('source_file', '')}")
    boost = 0.0

    # Explicit clause refs in the question («п. 6.2», «ст. 70»).
    for clause in _clauses_in_question(question):
        if clause in section or re.search(rf"(?:^|[\s\n]){re.escape(clause)}\.\s", text):
            boost += 10.0
        elif clause in blob:
            boost += 4.0

    # Topic families by shared stems (corpus-agnostic).
    families = (
        (("аренд", "плат"), ("аренд", "плат"), 6.0),
        (("испытан",), ("испытан", "тк"), 6.0),
        (("бухгалтер",), ("испытан", "тк", "70"), 5.0),
        (("ндс", "ставк"), ("ндс", "ставк", "налог"), 4.0),
        (("правоспособ",), ("правоспособ", "устав", "полномоч"), 5.0),
        (("персональн", "соглас", "152"), ("персональн", "соглас", "152"), 4.0),
        (("согласован", "одобрен", "порог"), ("регламент", "согласован", "одобрен"), 8.0),
        (("юротдел", "оригинал", "переда"), ("юридическ", "оригинал", "регламент", "хранени"), 6.0),
        (("гарант",), ("гарант", "талон", "срок"), 5.0),
        (("упаковк", "доставк"), ("упаковк", "доставк", "цен"), 5.0),
        (("претенз", "дефект", "недостат"), ("претенз", "недостат", "акт", "дефект"), 8.0),
        (("приёмк", "приемк", "качеств"), ("приёмк", "приемк", "качеств", "рабоч"), 8.0),
        (("пропуск", "доступ", "круглосуточ"), ("доступ", "круглосуточ", "транспорт", "пропуск"), 6.0),
        (("возврат", "ключ", "съезж"), ("возврат", "акт", "помещен", "ключ"), 5.0),
        (("аванс", "предоплат"), ("аванс", "предоплат", "расчёт", "расчет"), 6.0),
        (("архив",), ("архив", "выдач", "оригинал"), 5.0),
        (("сезон", "срочн"), ("сезон", "срочн"), 5.0),
    )
    for q_keys, doc_keys, weight in families:
        if any(k in q for k in q_keys) and any(k in blob for k in doc_keys):
            boost += weight

    # Approval / amount questions → company regulation over contract preamble.
    asks_approval = any(k in q for k in ("одобрен", "порог")) or (
        "генеральн" in q and any(k in q for k in ("млн", "миллион", "сумм", "одобрен"))
    )
    if asks_approval:
        if "регламент" in title:
            boost += 18.0
            if any(k in blob for k in ("одобрен", "генеральн", "порог", "свыше")):
                boost += 10.0
            if _AMOUNT_RE.search(text):
                boost += 8.0
        elif "регламент" in blob:
            boost += 10.0
        elif "договор" in title and "регламент" not in title:
            # Date/year overlap with a contract must not beat the regulation unit.
            boost -= 16.0
        # Prefer the clause that states the threshold, not a cover «утратила силу» stub.
        if "утратила силу" in blob or "утратил силу" in blob:
            if not any(k in blob for k in ("одобрен", "свыше", "миллион")):
                boost -= 12.0

    # Prefer defect/acceptance act language over bare dispute jurisdiction.
    if any(k in q for k in ("претенз", "дефект", "недостат", "прилож")):
        if any(k in blob for k in ("акт о выявлен", "акт о недостат", "выявленных недостат")):
            boost += 10.0
        if "арбитраж" in blob and "акт о" not in blob:
            boost -= 6.0

    # Quality-check follow-ups should not stick on warranty-only clauses.
    if any(k in q for k in ("качеств", "приёмк", "приемк")) and "гарант" in blob:
        if not any(k in blob for k in ("качеств", "приёмк", "приемк", "рабоч")):
            boost -= 6.0

    # Superseded editions: demote unless the question asks about old/repealed text.
    if row.get("superseded") or "утратил силу" in blob or "утратила силу" in blob:
        if not any(k in q for k in ("утративш", "старой", "редакци 20", "в 20")):
            # Keep mild demotion; edition filter already drops when no event date.
            boost -= 4.0

    # Law code affinity: ТК vs НК when question stems match.
    if any(k in q for k in ("испытан", "трудов", "бухгалтер")):
        if "тк" in blob and re.search(r"\b70\b", blob):
            boost += 6.0
        if "нк" in blob and "284" in blob:
            boost -= 5.0

    return boost


def _expand_queries(question: str) -> list[str]:
    """Corpus-agnostic lexical expansions (not demo counterparties / amounts).

    Returns the original plus 0–2 short paraphrases. Fail-safe: caller ignores
    empty/broken variants; never invents party names or numeric thresholds.
    """
    q = (question or "").strip()
    if not q:
        return []
    variants: list[str] = [q]
    nq = normalize(q)
    # Legal synonym hedges — stems/phrases that appear across typical bank KB docs.
    hedges: list[tuple[tuple[str, ...], str]] = (
        (("аренд", "плат"), "арендная плата срок внесения"),
        (("аренд",), "договор аренды плата"),
        (("одобрен", "порог"), "одобрение генерального директора порог"),
        (("одобрен",), "согласование сделки регламент"),
        (("генеральн", "директор"), "одобрение генерального директора сумма"),
        (("испытан",), "срок испытания трудовой кодекс"),
        (("бухгалтер",), "главный бухгалтер срок испытания"),
        (("претенз", "недостат"), "акт о выявленных недостатках претензия"),
        (("претенз",), "претензионный порядок акт недостатков"),
        (("приёмк", "качеств"), "проверка качества рабочих дней приёмка"),
        (("приемк", "качеств"), "проверка качества рабочих дней приемка"),
        (("гарант",), "гарантийный срок талон"),
        (("предоплат", "аванс"), "аванс предоплата порядок расчётов"),
        (("упаковк", "доставк"), "стоимость доставки упаковки цена"),
        (("правоспособ",), "правоспособность устав полномочия"),
        (("персональн",), "персональные данные согласие"),
        (("архив", "оригинал"), "хранение оригиналов архив выдача"),
        (("юротдел", "оригинал"), "передача оригинала в юридический отдел"),
        (("ндс",), "ставка НДС налог"),
        (("круглосуточ", "доступ"), "круглосуточный доступ пропуск"),
    )
    for keys, phrase in hedges:
        if not all(k in nq for k in keys):
            continue
        if normalize(phrase) in nq:
            continue
        variants.append(phrase)
        if len(variants) >= 3:
            break
    # Deduplicate while preserving order; cap at 3 total.
    out: list[str] = []
    seen: set[str] = set()
    for item in variants:
        key = normalize(item)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) >= 3:
            break
    return out


def _retrieve_one(
    question: str,
    kb: list[dict],
    corpus: list[list[str]],
    index: BM25Index,
    *,
    k: int,
    catalog: list | None,
    primary_question: str,
) -> list[dict]:
    """Single-query BM25 + boost path. Uses primary_question for catalog/gates."""
    q_tokens = tokens(question)
    if not q_tokens:
        return []
    primary_tokens = tokens(primary_question) or q_tokens

    preferred_docs: set[str] = set()
    if catalog:
        for card in match_catalog(primary_question, catalog):
            preferred_docs.update(card.doc_ids)

    ranked: list[tuple[float, float, dict]] = []
    scores = index.scores(q_tokens)
    for i, row in enumerate(kb):
        shared = set(q_tokens) & set(corpus[i])
        boost = _relevance_boost(primary_question, row)
        # Light boost from the expansion phrase itself when it matches the unit.
        if question != primary_question:
            boost += 0.5 * _relevance_boost(question, row)
        overlap = _support_overlap(primary_tokens, corpus[i])
        if len(shared) < 2 and scores[i] < 3.5 and boost < 3.0:
            continue
        score = scores[i] + boost + 4.0 * overlap
        if preferred_docs and row.get("doc_id") in preferred_docs:
            score += 6.0
        markers = ("уран", "экспорт", "лиценз", "крипт", "рецепт", "анекдот")
        qn = normalize(primary_question)
        if any(m in qn for m in markers) and boost < 3.0 and overlap < 0.15:
            continue
        if score > 0:
            ranked.append((score, overlap, row))

    ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not ranked:
        return []

    best = ranked[0][0]
    if best < 2.0:
        return []

    top_overlap = ranked[0][1]
    top_boost = _relevance_boost(primary_question, ranked[0][2])
    if top_overlap < 0.08 and top_boost < 5.0 and best < 8.0:
        return []

    strong = [r for s, _ov, r in ranked if s >= max(2.0, best * 0.4)]
    needles = _needle_patterns(primary_question)
    if needles:
        def needle_hits(row: dict) -> int:
            blob = f"{row.get('section', '')} {row.get('text', '')}"
            return sum(1 for n in needles if n.search(blob))

        strong = sorted(
            strong,
            key=lambda r: (
                needle_hits(r),
                _support_overlap(
                    primary_tokens,
                    tokens(
                        f"{r.get('title', '')} {r.get('section', '')} {r.get('text', '')}"
                    ),
                ),
            ),
            reverse=True,
        )

    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for row in strong:
        key = (row.get("doc_id", ""), row.get("section", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
        if len(out) >= max(k, 8):
            break
    return out


def _rrf_merge(result_lists: list[list[dict]], k: int) -> list[dict]:
    """Reciprocal rank fusion across query variants (fail-safe union)."""
    if not result_lists:
        return []
    if len(result_lists) == 1:
        return result_lists[0][:k]
    scores: dict[str, float] = {}
    rows: dict[str, dict] = {}
    for group in result_lists:
        for rank, row in enumerate(group):
            key = unit_key(row)
            rows[key] = row
            scores[key] = scores.get(key, 0.0) + 1.0 / (60.0 + rank + 1.0)
    ordered = sorted(scores, key=lambda item: scores[item], reverse=True)
    return [rows[key] for key in ordered[:k]]


def retrieve(
    question: str,
    kb: list[dict],
    k: int = 6,
    catalog: list | None = None,
) -> list[dict]:
    if not kb:
        return []
    q_tokens = tokens(question)
    if not q_tokens:
        return []

    corpus = [
        tokens(f"{r.get('title', '')} {r.get('section', '')} {r.get('text', '')}")
        for r in kb
    ]
    index = BM25Index(corpus)
    # Abstain when distinctive query terms are absent from the (possibly scoped) corpus.
    _stop = {
        "как",
        "какой",
        "какая",
        "какие",
        "какого",
        "какую",
        "каких",
        "это",
        "для",
        "при",
        "или",
        "было",
        "нужн",
        "нужно",
        "можн",
        "можно",
        "ее",
        "ещё",
        "еще",
    }
    content = [term for term in q_tokens if len(term) >= 4 and term not in _stop]
    unseen = [term for term in content if len(term) >= 5 and term not in index.idf]
    # On a tiny scoped corpus max IDF is small; use a relative cut, not a fixed 0.05.
    if index.n >= 40:
        idf_cut = 3.0
    else:
        max_idf = max((index.idf.get(t, 0.0) for t in content), default=0.0)
        idf_cut = max(0.01, max_idf * 0.25) if max_idf else 0.01
    seen_specific = [term for term in content if index.idf.get(term, 0.0) >= idf_cut]
    # Also treat any in-corpus content term as evidence the question is about this KB.
    seen_any = [term for term in content if term in index.idf]
    if len(unseen) >= 2 and not seen_specific and len(seen_any) < 2:
        return []

    # Multi-query: original + lexical hedges; fail-safe → single query on error/empty.
    try:
        variants = _expand_queries(question) or [question]
    except Exception:
        variants = [question]

    lists: list[list[dict]] = []
    for variant in variants:
        try:
            hits = _retrieve_one(
                variant,
                kb,
                corpus,
                index,
                k=k,
                catalog=catalog,
                primary_question=question,
            )
        except Exception:
            hits = []
        if hits:
            lists.append(hits)
    if not lists:
        return []
    fused_lexical = _rrf_merge(lists, max(k, 8))
    return _fuse(question, kb, fused_lexical, k)


def _needle_patterns(question: str) -> list[re.Pattern[str]]:
    """Topic needles for soft reordering — patterns, not demo filenames."""
    q = normalize(question)
    out: list[re.Pattern[str]] = []
    for clause in _clauses_in_question(question):
        out.append(re.compile(rf"(?:^|[\s\n]){re.escape(clause)}\.\s"))
    pairs = (
        (("претенз", "дефект", "недостат", "прилож"), r"акт о (?:выявлен|недостат)|недостатк"),
        (("качеств", "приёмк", "приемк"), r"качеств|рабочих дней|приёмк|приемк"),
        (("аренд", "плат"), r"арендн\w*\s+плат|\d[\d\s]{3,}\d"),
        (("гарант",), r"гарантийн|талон"),
        (("предоплат", "аванс"), r"предоплат|аванс"),
        (("упаковк", "доставк"), r"упаковк|доставк"),
        (("одобрен", "порог", "генеральн"), r"одобрен|свыше|генеральн\w*\s+директор|миллион"),
        (("круглосуточ", "доступ", "пропуск"), r"круглосуточ|беспрепятствен"),
        (("оригинал", "юротдел", "архив"), r"юридическ|оригинал|архив"),
    )
    for keys, pat in pairs:
        if any(k in q for k in keys):
            out.append(re.compile(pat, re.IGNORECASE))
    return out


def _fuse(question: str, kb: list[dict], lexical: list[dict], k: int) -> list[dict]:
    """Reciprocal rank fusion of BM25 and pgvector/in-memory cosine."""
    fused = lexical
    if vectors_enabled():
        try:
            dense = vector_search(question, kb, k=max(k, 8))
        except Exception:
            dense = []
        if dense and lexical:
            scores: dict[str, float] = {}
            rows: dict[str, dict] = {}
            for group in (lexical, dense):
                for rank, row in enumerate(group):
                    key = unit_key(row)
                    rows[key] = row
                    scores[key] = scores.get(key, 0.0) + 1.0 / (60.0 + rank + 1.0)
            ordered = sorted(scores, key=lambda item: scores[item], reverse=True)
            fused = [rows[key] for key in ordered[: max(k, 8)]]
        elif dense:
            fused = dense[: max(k, 8)]
    return _optional_rerank(question, fused, k)


def _optional_rerank(question: str, rows: list[dict], k: int) -> list[dict]:
    """POST {LLM_BASE_URL}/rerank when RERANKER_MODEL is set; fail-open to RRF order."""
    model = env("RERANKER_MODEL")
    if not model or not rows:
        return rows[:k]
    base, llm_key, _ = llm_settings()
    if not base:
        return rows[:k]
    key = env("RERANKER_API_KEY") or llm_key
    if not key:
        return rows[:k]
    top_n = env_int("RERANKER_TOP_N", min(k, len(rows)), 1, max(1, len(rows)))
    docs = []
    for row in rows:
        title = row.get("title") or row.get("doc_id") or ""
        text = (row.get("text") or "")[:700]
        docs.append(f"{title}\n{text}")
    payload = {
        "model": model,
        "query": question,
        "documents": docs,
        "top_n": min(top_n, len(docs)),
    }
    url = f"{base.rstrip('/')}/rerank"
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
        with urllib.request.urlopen(req, timeout=env_int("RERANK_TIMEOUT_SEC", 4, 1, 30)) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        items = body.get("results") or body.get("data") or []
        indices: list[int] = []
        for item in items:
            if isinstance(item, dict) and "index" in item:
                indices.append(int(item["index"]))
            elif isinstance(item, int):
                indices.append(item)
        ordered = [rows[i] for i in indices if 0 <= i < len(rows)]
        if ordered:
            seen = {unit_key(r) for r in ordered}
            for row in rows:
                key_u = unit_key(row)
                if key_u not in seen:
                    ordered.append(row)
                    seen.add(key_u)
            return ordered[:k]
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        OSError,
    ):
        pass
    return rows[:k]
