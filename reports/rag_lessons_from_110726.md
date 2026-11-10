# Уроки RAG из референса 11.07.26 (не наш продукт)

Источник только для идей: `/Users/damir/Documents/NEW/11.07.26_new` (Tender AI / new4).  
Цель: улучшить ПСБ Legal Assistant без копипаста файлов, бренда, UI и доменной логики закупок.

## Где у референса «хорошо по документам»

| Узел | Где смотреть | Суть |
|---|---|---|
| Scoped dense retrieve | `new4/services/rag/rag_search/chunk_search.py` | Поиск в scope тендера/документов; cosine + фильтры |
| Soft lexical fallback | `soft_fallback_hits` там же | Если гейт пуст — предпочесть чанки с clause/needle match, не «чужой» PDF |
| Relevance gate | `relevance_controller.py` | Blended cosine×overlap; fail-closed по порогу; demote шумовых файлов |
| Clause / section intent | `fact_extractors/section*.py`, `intent_chunk_boost` | «п. 5.2» / «пункт 4» → boost чанка с маркером пункта |
| Hybrid + rerank fail-open | embeddings + optional semantic / API rerank | Внешний канал падает → порядок кандидатов сохраняется |
| Grounded consult | `tender_chat.py` + prompts | Пустой retrieve → честный отказ; ответ только по approved chunks |

## Transferable идеи (взяли / адаптировали)

1. **Clause-aware ranking** — если в вопросе или топике есть пункт/тема (качество, претензия, арендная плата), поднимать unit, где есть маркер пункта или needle в теле, а не «соседний» гарантийный абзац.
2. **Query-focused excerpt** — цитата не с начала чанка (lost-in-the-beginning), а с лучшего совпадения по запросу внутри unit (у нас 3.1 часто жил в хвосте чанка «п. 1.1»).
3. **Support / overlap gate** — после BM25(+dense/RRF) переранжировать и отсечь слабый lexical overlap; abstain, если топ не поддерживает вопрос.
4. **Dialog scope = last ask + entities** — follow-up «а за сколько дней проверить качество?» не должен смешиваться с полным текстом предыдущего «гарантийный срок»; из истории — номер договора / контрагент.
5. **Atomic clause chunking** — не склеивать 1.x и 3.x в один unit только ради `CHUNK_CHARS`; section-based units как в ТЗ S1.
6. **Rerank fail-open** — уже есть в `psb_retrieve._optional_rerank`; оставить и не делать зависимость judge от reranker.
7. **Citation content check** — проверять не только `doc_id`/`title` в ответе, но и что ключевые числа/маркеры ответа встречаются в quote (мягкий number gate → lexical fallback).
8. **Soft fallback needles** — идея `soft_fallback_hits`: тематические regex (акт о недостатках, 5 рабочих дней, 450 000) как ranking signal, не как хардкод ответа.

## Что нельзя переносить

- Код/структуру Tender AI, UI, бренд, OKPD/NMCK/закупочные extractors, pgvector-HNSW как обязательный путь judge.
- `psycopg` / `fastembed` в root `requirements.txt` сабмита.
- Копипаст промптов/ответов «как у тендеров».
- Любые внешние источники для юр. утверждений (только KB allowlist).

## Сопоставление с as-is ПСБ

| Референс-паттерн | Было в ПСБ | План |
|---|---|---|
| Clause boost + soft needles | topic_boost эвристики, часто мимо 6.1/6.2 | усилить clause/needle + focused excerpt |
| Lexical overlap gate | BM25 порог + unseen terms | post-RRF support score |
| Dialog rewrite | `_user_context` склеивал все user turns | last + entities |
| Section chunking | merge до 700 символов ломал метки | atomic clauses |
| Rerank fail-open | уже есть | без ломки |
| Verify numbers | только title/doc_id | мягкий number ⊆ quotes |

## Риски

- Слишком жёсткий number-gate → ложный abstain на прописи («пять» vs «5»).
- Atomic chunking меняет recall BM25 — нужен lexical pytest + soft demo.
- Reranker на платформе может отсутствовать — только fail-open.
