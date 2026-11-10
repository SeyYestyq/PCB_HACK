# Системная архитектура: as-is, to-be, C4, потоки данных, API

> Статус: RFC, версия 1.0, 9 ноября 2026. Владелец: роль 1. Ревью: роли 2 и 3.
> Связанные документы: ТЗ [`../01-product/02-tz-complete.md`](../01-product/02-tz-complete.md), пайплайн [`../05-rag/02-best-approaches-and-our-pipeline.md`](../05-rag/02-best-approaches-and-our-pipeline.md), стек [`02-stack-and-decisions.md`](02-stack-and-decisions.md), данные [`03-data-model-and-kb.md`](03-data-model-and-kb.md), безопасность [`04-security.md`](04-security.md).
> Узлы ответственности ND1-ND8 с инвариантами, режимами отказа и тестами: [`../06-nodes/00-overview.md`](../06-nodes/00-overview.md); архитектурное ревью: [`../08-review/03-architecture-review.md`](../08-review/03-architecture-review.md) (v1.3).

## 1. Контекст и движущие силы
Архитектуру определяют четыре внешних ограничения, а не вкус:
| ID | Ограничение | Источник | Архитектурное следствие |
|---|---|---|---|
| C1 | Автооценка запускает только корневые `.py` из ZIP + `requirements.txt` из разрешённого списка | [K-REG §4], [K-REQ] | ядро должно быть плоским набором модулей без внешней БД и без нативных зависимостей вне списка |
| C2 | 20 минут, 8 CPU, 16 ГБ на весь прогон, LLM/эмбеддинги/реранк через один OpenAI-совместимый прокси | [K-REG §5-6] | бюджет времени, пул потоков, деградация, кеш индекса |
| C3 | Веб-чат обязателен и запускается одной командой Docker | [K-PDF Допуск, Формат сдачи 2] | второй вход в то же ядро; compose из двух сервисов |
| C4 | Один и тот же ответ в демо и у судьи | [K-INTAKE DECISIONS] | единственный путь ответа (инвариант A1) |

Архитектурные инварианты:
- **A1 Один путь.** `solution.py` и HTTP-сервис вызывают одну функцию `psb_pipeline.answer(question, history, kb) -> AnswerV2`. Любая логика ответа вне неё запрещена.
- **A2 Ядро без состояния между вопросами**, кроме неизменяемого индекса базы. Нет записи в базу знаний в runtime.
- **A3 Нет сетевых вызовов, кроме LLM-прокси.** Никаких внешних правовых систем [K-PDF Огр. 05], [K-INTAKE GARANT_SOURCE].
- **A4 Fail-closed.** Ошибка любой стадии понижает уровень (L0 → L4) или даёт `abstain`, но не выдаёт непроверенный факт.
- **A5 Наблюдаемость без секретов.** Трассировка каждой стадии; ключи не логируются.

## 2. As-is (состояние репозитория на 9 ноября 2026, коммит `07ae2f5`, сверено с `d1f068c`)
### 2.1. Компоненты [K-CODE]
| Компонент | Путь | Что делает | Проблемы |
|---|---|---|---|
| answer-core | `apps/answer-core/src/answer_core/pipeline.py` (433 строки на `d1f068c`) | чанки по 1200 символов, пересечение токенов + словарь «boost»-терминов, top-4, LLM получает `quote=text[:240]`; `clarify` только на голое «договор» без контрагента, номера или типа (05-rag/01 §7.1) | D1 (LLM не видит ответ), D5 (метки-даты), D6 (нет редакций), D7 (тавтологичная проверка), D8 (инъекция), boost-термины подогнаны под демо |
| HTTP API | `server.py`, FastAPI | `GET /health`, `POST /api/v1/ask`, `GET /api/v1/kb` | `history` принимается схемой, но **не передаётся** в `answer_question`; база **перечитывается с диска на каждый запрос** (`load_kb` внутри `answer_question`); нет просмотра документа |
| CLI / сабмит | `solution.py` в корне → импорт из `apps/answer-core/src` | JSON-режим и `--batch` | D2 (без аргументов exit 2), D3 (вложенный импорт), D4 (база не из `DATA_DIR/knowledge-base.zip`) |
| Web | `apps/web`, Next.js 15.1.0, пакет `copilot-web` | `LegalChat.tsx`: лента, панель подтверждений; запрос на `NEXT_PUBLIC_LEGAL_API_URL` (по умолчанию `http://localhost:8090`), локальный rewrite Next `/api/*` → `API_UPSTREAM` (по умолчанию `:8090` с `d1f068c`, до него `:8080`, то есть Go-заглушка) | нет истории, ключ `doc_id`, наследие другого продукта, `--brand-red` |
| Legacy API | `apps/api` (Go) | заглушка | профиль `legacy` в compose (порт 8080), не используется; в `.env.example` с `d1f068c` `HTTP_ADDR=:8090`, при локальном запуске Go с этим файлом порт совпадёт с `answer` |
| Инфраструктура | `docker-compose.yml` | `answer`(8090) + `web`(3000); `postgres`(pgvector pg16) и `redis` в профиле `full` | нет `compose.yaml`, нет корневого `.dockerignore`, `requirements.txt` без `==` |

### 2.2. As-is диаграмма
```
Браузер ──HTTP──> web (Next 15, :3000) ──fetch──> answer (FastAPI, :8090)
                                                   │ на каждый запрос:
                                                   ├─ load_kb(data/organizer/kb)   (диск)
                                                   ├─ retrieve: token overlap + boost
                                                   ├─ LLM (/chat/completions) с quote[:240]
                                                   └─ citations = найденные чанки (без проверки)
solution.py --batch ──import apps/answer-core/src──> та же функция (на платформе не найдётся модуль)
```

## 3. To-be: C4
### 3.1. Уровень 1: контекст
```
 ┌─────────────────────┐        вопросы, история         ┌──────────────────────────────┐
 │ Юрист банка          │ ─────────────────────────────> │                              │
 │ Руководитель юр.подр.│ <───── ответ + цитаты ──────── │  Юридический ассистент (наш)  │
 └─────────────────────┘                                  │                              │
 ┌─────────────────────┐   questions.csv, KB zip          │                              │
 │ Платформа автооценки │ ─────────────────────────────> │                              │
 │ (LLM-судья)          │ <──── submission.csv ───────── │                              │
 └─────────────────────┘                                  └──────────────┬───────────────┘
                                                                         │ /chat/completions
                                                                         │ /embeddings, /rerank
                                                          ┌──────────────▼───────────────┐
                                                          │ OpenAI-совместимый LLM-прокси │
                                                          │ DeepSeek V4.1 Flash, BGE-M3,  │
                                                          │ Qwen3-Reranker-8B             │
                                                          └──────────────────────────────┘
```
Внешних систем, кроме прокси, нет (A3).

### 3.2. Уровень 2: контейнеры
| Контейнер | Технология | Ответственность | Порт | Состояние |
|---|---|---|---|---|
| `answer` | Python 3.12, FastAPI + uvicorn, ядро `psb_*.py` | API ответа, документы, здоровье, SSE | 8090 | индекс в памяти, кеш на диске `/tmp/psb_cache/<kb_hash>/` (индекс `psb_index_<kb_hash>.npz`, `units.jsonl`, `kb_manifest.json`; `03` §3) |
| `web` | Next.js 15 standalone [S-65] | UI чата, панель доказательств, drawer документа | 3000 | без состояния; история диалога в памяти вкладки |
| `solution.py` (не контейнер) | Python, те же модули | батч для платформы | нет | без состояния |
| (продакшен, вне хакатона) `postgres` | Postgres 16 + pgvector + FTS | хранилище unit, векторов, аудита | 5432 | см. §7 |

### 3.3. Уровень 3: компоненты ядра
```
psb_config ── читает окружение (LLM_*, TOP_K, MAX_WORKERS, PSB_*), валидирует, маскирует ключ в repr
psb_ingest ── zip/папка → RawDoc[]  (txt/md/docx, кодировки utf-8/cp1251)
psb_structure ── RawDoc → Document + Unit[] + Edition + Relation[]  (детерминированные регэкспы)
psb_textnorm ── нормализация, токенайзер с защитой номеров/сумм/дат, Snowball RU стеммер
psb_index ── BM25 (свой, по стеммам) + Dense (numpy, BGE-M3) + сериализация по kb_hash
psb_llm ── httpx-клиент: chat/embeddings/rerank, ретраи 429/5xx, таймауты, семафор, учёт токенов
psb_pipeline ── S5..S18: guard → understand → retrieve → fuse → resolve editions → rerank → gate → expand → generate → verify → repair → decide
psb_verify ── quote/number/edition/injection-echo проверки (чистые функции)
psb_render ── AnswerV2 → текст для судьи / JSON для API
solution.py ── батч-оркестратор: пул, бюджет времени, атомарная запись CSV
server.py (answer) ── FastAPI-обвязка над psb_pipeline
```
Направление зависимостей строго сверху вниз; `psb_verify` и `psb_textnorm` не зависят от сети и полностью покрываются юнит-тестами.

## 4. Потоки данных
### 4.1. Поток F-INGEST (старт процесса)
1. `psb_config.load()` → `DATA_DIR` (сабмит) или `PSB_KB_PATH` (веб).
2. Найти `knowledge-base.zip` (варианты имени, ТЗ F1) или папку; посчитать `kb_hash = sha256(отсортированные (имя, sha256(содержимое)))`.
3. Если в `/tmp/psb_cache/<kb_hash>/` есть `psb_index_<kb_hash>.npz`, `units.jsonl` и `kb_manifest.json` (или готовый индекс с тем же `kb_hash` в корне ZIP) → загрузить (≤ 3 с, NF2); раскладка файлов в `03-data-model-and-kb.md` §3.
4. Иначе: распаковать в память, `psb_structure` → `units`, санитайзер помечает инъекции, `psb_index.build_bm25(units)`, `psb_llm.embed(batch=32)` (~350 unit → 11 батчей), сохранить кеш атомарно (`tmp` + `os.replace`).
5. Отказ эмбеддингов → индекс без dense (`dense_available=false`), уровень L2 по умолчанию для всех вопросов, событие в лог.
Инварианты: unit_id стабилен при одинаковом тексте; повторный ингест той же базы даёт байт-в-байт тот же `units.jsonl`.

### 4.2. Поток F-ASK (один вопрос, общий для веба и сабмита)
```
question(+history) ─S5 dialog parse + нормализация─> turns[], q_norm
  ─S6 guard (regex + словари)─> {ok | refuse_role(role_attack/off_topic/illegal) | flag injection_ignored}
  ─S7 understand (LLM JSON, ≤ 1 вызов)─> {intent, entities(doc_no, counterparty, amount, dates), event_date, rewrite[], needs_clarify}
  ─S8 retrieve: BM25(q_norm ∪ rewrite) ‖ Dense(BGE-M3)─> 2 × top-30
  ─S9 RRF(k=60) + фильтр по doc_id при распознанном договоре─> top-20
  ─S10 resolve editions(event_date)─> помечает applicable / superseded / conditional
  ─S11 rerank (Qwen3, опционально, таймаут)─> top-8
  ─S12 gate: достаточно ли? нет → abstain(missing) без генерации
  ─S13 context pack: документ компании целиком (короткие), соседние части статьи закона
  ─S14 generate (spotlighting, JSON claims)─> draft
  ─S15 verify (детерминированно)─> claim.ok / fail
  ─S16 repair (≤ 1 LLM-вызов, только упавшие claims)─> draft'
  ─S17 decide status─> grounded/limited/abstain/clarify/refuse_role + flags
  ─S18 render─> AnswerV2 (+ judge text)
  ─S19 trace─> stderr JSON
```
Номера стадий совпадают с `05-rag/02` (S0-S4 относятся к ингесту, поток 4.1). Число LLM-вызовов на вопрос: 1 (understand) + 1 (generate) + 0-1 (repair) + 0-1 (rerank) + 1 (embed запроса). Худший случай 5 вызовов, типичный 3-4.

### 4.3. Поток F-BATCH (`solution.py`)
1. Ингест (4.1), чтение `questions.csv` (`id,question`, кодировка utf-8-sig).
2. `ThreadPoolExecutor(MAX_WORKERS)`; у каждого вопроса жёсткий дедлайн `min(60 с, оставшийся бюджет / оставшиеся вопросы × коэффициент)`.
3. Глобальный бюджет `T_total = 17 мин` от старта; по мере исчерпания уровень пайплайна понижается L0 → L1 → L2 → L3 (детали в 05-rag/02 §4).
4. Результаты пишутся в словарь; каждые 20 ответов и в конце `submission.csv` перезаписывается атомарно; отсутствующие ответы заполняются L4-ответом (извлечение без LLM) или корректным `abstain`-текстом, чтобы ни один ID не был пустым (M13).
5. Финальная валидация CSV перед выходом; код возврата 0.

### 4.4. Поток F-UI
1. Пользователь вводит вопрос; web добавляет его в локальную историю и вызывает `POST /api/v1/ask/stream` (SSE). Если SSE недоступен, `POST /api/v1/ask`.
2. События стадий отображаются строкой прогресса («Ищу положения в базе» → «Сверяю ответ с найденными фрагментами» → «Проверяю ссылки», ключи `progress.*` из `../04-brand/03-components-and-copy.md`).
3. Финальное событие `answer` содержит `AnswerV2`; лента рисует статус, текст, `[n]`; панель доказательств рисует `citations[]`.
4. Клик «Открыть документ» → `GET /api/v1/docs/{doc_id}` (кешируется в браузере) → drawer с подсветкой `char_start..char_end`.
5. `clarify` → кнопки вариантов; выбор отправляет уточнённый вопрос с историей.

## 5. API (контракт сервиса `answer`)
Версия `v1`, JSON, UTF-8, без авторизации в демо (продакшен: §7, security). Ошибки в формате `{"error": {"code": "...", "message": "...", "trace_id": "..."}}`.

### 5.1. `POST /api/v1/ask`
Запрос:
| Поле | Тип | Обяз. | Ограничения | Описание |
|---|---|---|---|---|
| `question` | string | да | 1..4000 символов после trim (ТЗ SEC7, совпадает с лимитом композера) | последняя реплика пользователя |
| `history` | array of `{role: "user"\|"assistant", content: string}` | нет | сервер берёт последние 10 (лишние отбрасывает, не 400), каждая ≤ 4000 | история; реплики `assistant` используются только для разрешения ссылок («этот договор»), не как факты (F11) |
| `options.debug` | bool | нет | | включить `trace` в ответ |
| `options.level` | `"auto"\|"L0".."L4"` | нет | | принудительный уровень (демо деградации) |
| `client_msg_id` | string | нет | ≤ 64 | для идемпотентности в UI |

Ответ 200: `AnswerV2` (ТЗ §3.3) плюс v1-совместимые поля: `citations[].title` (= `doc_title`), `citations[].span` (= `label`).
Коды: 400 `invalid_request` (пустой вопрос, лимиты), 422 (валидация pydantic), 503 `kb_not_ready` (ингест не завершён), 504 `deadline_exceeded` (≥ 60 с; тело всё равно содержит `abstain`-ответ с `flags.degraded=true`), 500 `internal` (никогда без `trace_id`).
Пример запроса из демо (Q4 [K-DEMO]):
```json
{"question": "Почему арендная плата по договору аренды склада составляет 500 000 рублей в месяц?", "history": []}
```
Ожидаемое: `status=grounded`, `flags.premise_corrected=true`, цитата `п. 3.1` договора А-08/2024 (450 000).

### 5.2. `POST /api/v1/ask/stream` (SSE)
Тот же запрос. События `text/event-stream`:
| event | data | Когда |
|---|---|---|
| `stage` | `{"stage":"retrieve","label_key":"progress.search","t_ms":140}` | при входе в S8 (`progress.search`), S14 (`progress.verify`), S15 (`progress.cite`); тексты ключей в `../04-brand/03-components-and-copy.md` §11 и §15, сервер отдаёт ключ, а не строку |
| `answer` | `AnswerV2` | один раз, финал |
| `error` | `{"code":..., "trace_id":...}` | вместо `answer` при сбое |
Токен-стриминг текста не делаем: текст формируется из проверенных claims и не может показываться до проверки (A4).

### 5.3. `GET /api/v1/docs/{doc_id}`
Ответ:
| Поле | Тип | Описание |
|---|---|---|
| `doc_id` | string | стабильный slug |
| `title`, `doc_type`, `number`, `date`, `parties[]` | | из модели данных |
| `edition` | object | `status`, `effective_from`, `effective_to`, `label` |
| `relations[]` | `{type, target_doc_id, target_unit_id, note}` | `amends`, `supplements`, `superseded_by`, `supersedes` |
| `text` | string | полный текст в нормализованном виде (по нему считаются `char_start/end`) |
| `units[]` | `{unit_id, label, char_start, char_end, section_title, flags}` | разметка для навигации |
| `warnings[]` | string | `superseded`, `suspected_injection` с диапазоном |
| `source` | object | `file`, для законов `url` и `exported_at` из шапки ГАРАНТ |
404 `doc_not_found`.

### 5.4. `GET /api/v1/kb`
`{kb_hash, built_at, documents: [{doc_id, title, doc_type, edition_status}], units_count, dense_available, injection_flags_count, model_ids: {gen, emb, rerank}}`. Имена моделей берутся из окружения; ключ никогда.

### 5.5. `GET /health`
`{"ok": true, "kb_ready": true, "dense_available": true, "llm_reachable": "unknown|ok|fail", "version": "<git sha>"}`. `llm_reachable` кешируется 60 с, чтобы health-чеки не тратили квоту.

### 5.6. Нефункциональные свойства API
- Синхронные `def`-эндпоинты выполняются FastAPI в threadpool [S-64]; ядро блокирующее (httpx sync) и потокобезопасное, индекс read-only.
- Ограничение параллельных LLM-вызовов семафором (`PSB_LLM_CONCURRENCY`, по умолчанию 8).
- CORS: только `CORS_ORIGINS`, без `*` при `allow_credentials` (сейчас fallback `["*"]` при пустом списке [K-CODE], исправить).

## 6. Наблюдаемость
Одна JSON-строка в stderr на стадию: `{"trace_id","q_id","stage","t_ms","level","n_candidates","top_units":[...],"status","flags","llm":{"model","prompt_tokens","completion_tokens","retries"}}`. Текст вопроса логируется только при `PSB_LOG_TEXT=1` (демо). Сводка прогона в конце `solution.py`: распределение статусов, p50/p95 времени, число деградаций, число repair. Эти же поля кормят режим «как получен ответ» в UI.

## 7. Продакшен-архитектура (сценарий внедрения, 15% защиты)
Хакатонный контур намеренно без БД (C1). Для банка целевая схема:
| Слой | Хакатон | Продакшен | Почему так |
|---|---|---|---|
| Хранилище unit | JSONL + numpy в памяти | Postgres: таблицы `documents`, `editions`, `units`, `relations`; pgvector для векторов; FTS `tsvector` с конфигурацией `russian` (Snowball) | один сервер для метаданных, векторов и полнотекста; гибрид через SQL [S-24], [S-25], [S-26] |
| Индексы | точный поиск | HNSW при росте > 100 тыс. unit | pgvector по умолчанию точный, HNSW даёт лучший speed-recall [S-24] |
| Ингест | при старте | очередь загрузки, версионирование документов, ручная разметка редакций юристом | редакции являются юридическим фактом, их нельзя только угадывать |
| LLM | платформенный прокси | on-prem модель в контуре банка | ПДн и банковская тайна, см. security |
| Доступ | без авторизации | SSO, RBAC по подразделениям, ACL на документы в фильтре поиска | OWASP LLM08: утечки через общий векторный индекс [S-58] |
| Аудит | stderr | журнал вопросов/ответов/цитат с неизменяемостью и сроком хранения | проверяемость выводов руководителем (J9, J10) |
| Оценка | golden + суррогатный судья | регрессия на каждый релиз + выборочная экспертная разметка | RAGAS/ARES-подобный контур [S-44], [S-45] |
Ядро (`psb_pipeline`) при этом не меняется: меняется реализация интерфейса `Retriever` (in-memory → Postgres). Это и есть аргумент «один путь» для защиты.

## 8. Рассмотренные альтернативы архитектуры
| Альтернатива | Плюсы | Почему нет |
|---|---|---|
| Оставить вложенный пакет `apps/answer-core` и копировать его в ZIP | меньше рефакторинга | платформа переносит только корневые `.py` [K-REG §4]; копия = два пути (нарушение A1) |
| Postgres в compose для веба, in-memory для сабмита | «продакшен-вид» | два ретривера = разные ответы в демо и у судьи; на 350 unit нет выигрыша; лишний сервис в одной команде запуска |
| Go BFF между web и answer | типизация, кеш | лишний хоп и язык без функциональной пользы; Go уже вынесен в профиль `legacy` |
| Агентный цикл (LLM решает, когда искать) | гибкость | недетерминизм и время в лимите 20 мин; на 21 документе фиксированный конвейер с гейтом проще проверить (05-rag/01 §2) |
| Long-context: вся база (~270 тыс. символов) в промпт | нет ошибок поиска | стоимость и время на 200 вопросов, «Lost in the Middle» [S-46]; NitiBench: long-context уступает RAG в юр. домене [S-09]; оставляем как L-fallback только для документов компании (~16 тыс. символов) |

## 9. Режимы отказа
| Сбой | Обнаружение | Поведение |
|---|---|---|
| `/embeddings` недоступен | исключение при ингесте/запросе | BM25-only (L2), флаг `degraded` |
| `/rerank` медленный | таймаут 4 с | пропуск реранка (L1) |
| `/chat/completions` 429/5xx | код ответа | ≤ 2 ретрая с экспоненциальной паузой и jitter, затем L3/L4 |
| JSON модели не парсится | исключение парсера | извлечение первого `{...}`, затем повтор без `response_format`, затем L4 |
| пустой `content` в JSON-режиме (известное поведение [S-54]) | `content == ""` | повтор один раз с увеличенным `max_tokens`, затем L4 |
| битый файл в базе | исключение ингеста | пропуск файла, событие в лог, `kb.warnings` |
| закончился бюджет времени | таймер | понижение уровня, затем L4 для остатка |
| процесс убит | n/a | `submission.csv` уже частично записан атомарно (последний чекпоинт) |
