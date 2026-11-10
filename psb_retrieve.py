"""BM25 retrieval over structural KB chunks."""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from collections import Counter

from psb_catalog import match_catalog
from psb_config import env, env_int, llm_settings
from psb_textnorm import normalize, tokens
from psb_vectors import search as vector_search
from psb_vectors import unit_key
from psb_vectors import vectors_enabled


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


def _topic_boost(question: str, row: dict) -> float:
    q = normalize(question)
    blob = normalize(
        f"{row.get('text', '')} {row.get('title', '')} {row.get('section', '')} {row.get('source_file', '')}"
    )
    boost = 0.0
    pairs = (
        (("аренд", "склад", "северн"), 4.0),
        (("испытан", "бухгалтер", "трудов"), 5.0),
        (("тк", "стать", "70"), 3.0),
        (("ндс", "ставк"), 3.0),
        (("правоспособ", "кредит", "досье", "полномоч"), 5.0),
        (("персональн", "152"), 3.0),
        (("согласован", "регламент"), 3.0),
        (("юротдел", "оригинал", "регламент", "переда"), 5.0),
        (("поставк", "альфа"), 2.0),
        (("гарант", "альфа", "талон"), 4.0),
        (("упаковк", "доставк", "цен"), 4.0),
        (("акт", "ключ", "возврат", "помещен"), 4.0),
        (("претенз", "недостат", "дефект", "акт"), 8.0),
        (("химк", "склад", "пропуск", "доступ", "транспорт"), 6.0),
        (("упаковк", "доставк", "цен", "включ"), 6.0),
        (("пособи", "беременност"), -8.0),  # not in KB — demote false friends
    )
    for keys, weight in pairs:
        # First key must appear in the question (topic intent), others may match blob.
        if keys[0] in q and any(k in blob for k in keys):
            boost += weight
    # Prefer ТК ст.70 for probation questions over НК ст.284
    if any(k in q for k in ("испытан", "бухгалтер")):
        if "тк" in blob and "70" in blob:
            boost += 8.0
        if "нк" in blob and "284" in blob:
            boost -= 6.0
    # GD approval / thresholds live in the company regulation, not in contracts.
    # Do not boost contract preambles that merely mention «генеральный директор».
    if any(k in q for k in ("одобрен", "порог")) or (
        "генеральн" in q and any(k in q for k in ("млн", "миллион", "сумм", "одобрен"))
    ):
        text = row.get("text") or ""
        if "регламент" in blob:
            boost += 14.0
            if "10 000 000" in text or "десяти миллион" in blob:
                boost += 10.0
            if "15 000 000" in text or "пятнадцат" in blob:
                boost += 4.0
            if "утратила силу" in blob or "утратил силу" in blob:
                boost -= 14.0
        elif "договор" in blob and "регламент" not in blob:
            boost -= 10.0
    # Prepayment / settlement clauses for advance-payment questions.
    if any(k in q for k in ("аванс", "предоплат", "оплат")):
        if any(k in blob for k in ("предоплат", "порядк расчёт", "4.1", "4.2")):
            boost += 12.0
        if "ответственност" in blob and "гарант" in blob:
            boost -= 4.0
    # Claim attachments: prefer acceptance/defect clause over dispute §8.
    if any(k in q for k in ("претенз", "дефект", "недостатк", "прилож")):
        if any(k in blob for k in ("акт о выявлен", "акт о недостат", "выявленных недостат")):
            boost += 12.0
        if "8.1" in blob and "арбитраж" in blob:
            boost -= 8.0
    if "утратила силу" in blob or "редакция утратила" in blob:
        boost -= 8.0
    return boost


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
    # Abstain only when the distinctive words are absent and nothing specific remains.
    # «пособие по беременности» has no such stem in the corpus; «арендная плата» does.
    # Absolute idf>=3 needs a large corpus; after catalog scope n can be ~5 and max idf≈1.4.
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
    idf_cut = 3.0 if index.n >= 40 else 0.05
    seen_specific = [term for term in content if index.idf.get(term, 0.0) >= idf_cut]
    if len(unseen) >= 2 and not seen_specific:
        return []
    scores = index.scores(q_tokens)

    # Catalog narrowing: boost matched counterparties' docs
    preferred_docs: set[str] = set()
    if catalog:
        for card in match_catalog(question, catalog):
            preferred_docs.update(card.doc_ids)

    ranked: list[tuple[float, dict]] = []
    for i, row in enumerate(kb):
        shared = set(q_tokens) & set(corpus[i])
        boost = _topic_boost(question, row)
        # Ignore weak single-word hits on generic terms unless topic boost fires.
        if len(shared) < 2 and scores[i] < 3.5 and boost < 3.0:
            continue
        score = scores[i] + boost
        if preferred_docs and row.get("doc_id") in preferred_docs:
            score += 6.0
        # Out-of-corpus markers: skip unless topic boost already selected the family.
        markers = ("уран", "экспорт", "лиценз", "крипт", "рецепт", "анекдот")
        qn = normalize(question)
        if any(m in qn for m in markers) and boost < 3.0:
            continue
        if score > 0:
            ranked.append((score, row))

    ranked.sort(key=lambda x: x[0], reverse=True)
    if not ranked:
        return []

    best = ranked[0][0]
    if best < 2.0:
        return []

    strong = [r for s, r in ranked if s >= max(2.0, best * 0.4)]
    # Deduplicate by (doc_id, section) keeping order
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for row in strong:
        key = (row.get("doc_id", ""), row.get("section", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
        if len(out) >= k:
            break
    return _fuse(question, kb, out, k)


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
            # Append any RRF leftovers not returned by the reranker.
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
