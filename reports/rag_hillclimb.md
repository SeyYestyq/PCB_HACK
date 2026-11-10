# RAG hillclimb — organizer golden (метрика) + общие фиксы

Дата: 2026-11-11 (post-norm: number-verify / multi-query / dense smoke).

## Метрики

| Прогон | Результат |
|---|---|
| `test_golden_demo.py` + `test_lexical.py` + `test_pipeline.py` (PSB_LEXICAL_ONLY=1, PSB_VECTORS=0) | **49 passed** |
| Soft-pass demo Q1–Q18 (lexical) | **18/18** (prior) |
| Atomic chunk check (А-08) | `п. 3.1` содержит `450` |
| `PSB_KB_PATH=data/fixtures/kb.jsonl` | `grounded` без правок кода |
| `load_kb(knowledge-base.zip)` | 188 rows |
| Docker dense (`PSB_VECTORS=1`) | health: `vectors.ready=true`, `pgvector=true`, units=188; smoke ask `:8090` / `:3000` → grounded |

Golden-оракулы: `apps/answer-core/tests/test_golden_demo.py` (факты/status/clause markers из `demo_output.csv`, не полный текст модели).  
Лексический режим: `PSB_LEXICAL_ONLY=1` (не полагаться на pop ключей — `.env` их возвращает).

## Что обобщили (любая KB)

1. **Clause-aware chunking** (`psb_structure.chunk_text`) — режет по `N.` / `N.M.`, не склеивает разные major-секции; метка unit = реальный пункт.
2. **Focused excerpt** (`focused_excerpt`) — цитата из окна с max overlap к вопросу, не с начала чанка.
3. **Dialog scope** (`_user_context`) — last ask + entity cues (№ договора, ИНН, кавычки), без склейки прошлых полных вопросов (нет bleed «гарантия»→«качество»).
4. **Retrieve без demo counterparties** (`_relevance_boost`) — семьи stems (аренд/претенз/одобрен/…), clause refs, регламент vs договор для approval, soft needles, overlap support gate; убраны «Северный/Альфа/Химки» boosts и хардкод 10/15 млн.
5. **Стеммер** (`psb_textnorm`) — короткие падежные окончания (`доставка`≈`доставки`), иначе in-corpus gate ложно abstain’ил на любой KB.
6. **Support gate на scoped corpus** — относительный IDF cut, не фиксированный порог как на полном корпусе.
7. **Catalog** — own-company по частоте preamble + seed; ambiguous prefix (не только «альфа»).
8. **Edition meta** — `valid_to` прокидывается в rows; filter по дате события.
9. **Rerank / dense** — fail-open; hybrid RRF без обязательного pgvector в judge.
10. **KB path** — dir / zip / jsonl / `PSB_KB_PATH` без правок кода.
11. **Number-verify** (`_numbers_grounded`) — значимые числа/суммы ответа ⊆ title+span+quote; `10 млн` ≡ `10 000 000`; провал → lexical fallback.
12. **Multi-query hedges** (`_expand_queries`) — 0–2 лексических парафраза по legal stems (не контрагенты/пороги); RRF merge; fail-safe на исходный query.

## Demo-eval only (метрика, не стратегия ответа)

- Набор `data/organizer/tests/demo_questions.csv` + `demo_output.csv`.
- Pytest-оракулы и soft-checks в `test_golden_demo.py` / scoreboard (числа 450, 10 млн, ТК 70, П-17…).
- Seed `_OWN_COMPANY_STEMS_SEED = {меридиан}` — только fallback, поверх frequency detect.
- Широкий regex номеров договоров `А-/П-/ПТ-` в парсере — эвристика РФ-договоров, не имена файлов demo.

## Уроки референса 11.07.26 (идеи, не копипаст)

См. `reports/rag_lessons_from_110726.md`: soft lexical fallback, overlap gate, clause boost, dialog entities, rerank fail-open, number ⊆ quotes.

## Что ещё слабо / следующий круг

- Own-company frequency может ошибиться на крошечной KB (&lt;3 docs) → seed.
- LLM soft-pass таблица на платформенных моделях — отдельный прогон (не блокер lexical DoD).
- Reranker на платформе может отсутствовать — только fail-open.

## Как гонять

```bash
PSB_VECTORS=0 PSB_LEXICAL_ONLY=1 PYTHONPATH=".:apps/answer-core/src" \
  apps/answer-core/.venv/bin/python -m pytest \
  apps/answer-core/tests/test_golden_demo.py \
  apps/answer-core/tests/test_lexical.py \
  apps/answer-core/tests/test_pipeline.py -q

# Dense smoke (Docker):
docker compose up -d --build answer
curl -s http://127.0.0.1:8090/health   # vectors.ready / pgvector
curl -s -X POST http://127.0.0.1:8090/api/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Какая арендная плата по договору с ООО «Северный Склад»?"}'

# LLM path (секреты из окружения / .env, не коммитить):
PSB_GOLDEN_LLM=1 PYTHONPATH=".:apps/answer-core/src" \
  apps/answer-core/.venv/bin/python -m pytest \
  apps/answer-core/tests/test_golden_demo.py -q
```
