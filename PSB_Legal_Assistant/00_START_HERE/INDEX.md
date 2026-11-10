# Пакет документации: ИИ-ассистент для юристов банка (Changellenge Hack&Change 2026 × ПСБ)

> Версия 1.6, 10 ноября 2026 (as-is сверено с коммитом `d1f068c`; v1.6: полные ТЗ по ролям 08, 09, 10 в `01-product/`; четвёртый проход утром 10.11, что изменилось и что делать команде сейчас: [`../STATUS.md`](../STATUS.md), последний раздел). Размеры файлов указаны на момент сборки и меняются при правках. Язык: русский. Источник истины по условиям: официальный кейс и технический регламент организаторов ([`99-sources.md`](99-sources.md), коды K-*).
> Документы в репозитории `docs/strategy`, `docs/product`, `docs/architecture`, `docs/design`, `PROJECT.md`, `00-README.md` относятся к другому продукту («Бизнес: Старт»), являются заглушками и подлежат замене этим пакетом (задача R3.9 в [`01-product/03-tz-roles-3-people.md`](01-product/03-tz-roles-3-people.md)).

## Порядок чтения
| Если вы | Читайте |
|---|---|
| впервые в проекте | этот файл → 01-product/01 → 01-product/02 §1-3 → 02-architecture/01 §1-4 |
| пишете ядро (роль 1) | **01-product/09 (полное ТЗ)** → 01-product/04 → 06-nodes/00 → 06-nodes/01-07 → 07-tests/00, 01 → 08-review/01; фон: 01-product/02 §3-6, §8 → 05-rag/02 → 02-architecture/* |
| делаете интерфейс (роль 2) | **01-product/08 (полное ТЗ)** → 01-product/05 → 06-nodes/08 → 04-brand/* (07 обоснования) → 08-review/02; фон: 01-product/02 §3, §7 → 02-architecture/01 §5 (API) |
| отвечаете за базу, eval, документацию (роль 3) | **01-product/10 (полное ТЗ)** → 01-product/06 → 07-tests/04, 05 → 08-review/05, 06; фон: 02-architecture/03 → 01-product/02 §9-10 → 05-rag/01 §8 |
| ревьюите PR | 08-review/00 → файл нужного вида ревью → файл затронутого узла в 06-nodes |
| хотите знать, что делать прямо сейчас | `../STATUS.md`, последний раздел «Что делать команде сейчас» |
| ищете, кто чинит упавший тест | 07-tests/01 §2 «симптом → узел» → 06-nodes → 01-product/07 §4 (RACI) |
| готовите защиту | 01-product/01 → 03-analogs/02 §2 → 02-architecture/02 → 02-architecture/04 §5-6 → 05-rag/01 §10 |

## Состав
| Раздел | Файл | О чём | Размер |
|---|---|---|---|
| Продукт | [`01-product/01-problem-and-audience.md`](01-product/01-problem-and-audience.md) | проблема из кейса, ЦА, LLM-судья как потребитель, JTBD J1-J10, ожидания, анти-персоны | 17.3 КБ |
| | [`01-product/02-tz-complete.md`](01-product/02-tz-complete.md) | ТЗ: MUST/SHOULD/COULD/WON'T, контракт ответа `AnswerV2`, статусы и флаги, F1-F17, правила редакций E1-E12, безопасность SEC1-7, UI, сабмит и Docker, 19 типов eval-кейсов, связь с критериями | 46.4 КБ |
| | [`01-product/03-tz-roles-3-people.md`](01-product/03-tz-roles-3-people.md) | 3 роли, задачи с DoD и сроками, интерфейсы, ритм, DoD на 16.11 | 18.1 КБ |
| Архитектура | [`02-architecture/01-system-architecture.md`](02-architecture/01-system-architecture.md) | ограничения C1-C4, инварианты A1-A5, as-is, C4 (контекст, контейнеры, компоненты), потоки, API с полями, наблюдаемость, продакшен, режимы отказа | 27.1 КБ |
| | [`02-architecture/02-stack-and-decisions.md`](02-architecture/02-stack-and-decisions.md) | ADR-01..12 с вариантами и источниками: in-memory vs Postgres/pgvector vs Qdrant vs OpenSearch vs FTS, RRF, BM25+Snowball, BGE-M3, Qwen3-реранкер, чанкинг, FastAPI vs Go, Next vs Vite | 19.8 КБ |
| | [`02-architecture/03-data-model-and-kb.md`](02-architecture/03-data-model-and-kb.md) | инвентаризация 21 файла, аномалии KB-A1..A7, сущности и все поля, файлы индекса, правила парсинга, санитайзер | 22.1 КБ |
| | [`02-architecture/04-security.md`](02-architecture/04-security.md) | активы, границы доверия, угрозы T1-T12, многослойная защита от инъекций, секреты, ПДн, fail-closed, продакшен-требования банка | 17.3 КБ |
| Аналоги | [`03-analogs/01-analogs-deep-dive.md`](03-analogs/01-analogs-deep-dive.md) | НейроЮрист, ИСКРА, КонсультантПлюс, Doczilla, GigaLegal, Harvey, CoCounsel, Protégé, Legora, Spellbook, Luminance, COiN; матрица по 8 измерениям | 23.8 КБ |
| | [`03-analogs/02-what-we-take-and-reject.md`](03-analogs/02-what-we-take-and-reject.md) | 22 паттерна: берём / адаптируем / отвергаем с фильтрами и весами критериев | 10.7 КБ |
| Бренд и UI | [`04-brand/`](04-brand/) | брендбук, дизайн-система, компоненты и тексты, экраны и сценарии, анти-слоп, детальная спецификация отступов, типографики, движения и скелетонов ([`06-detail-spacing-type-motion-skeletons.md`](04-brand/06-detail-spacing-type-motion-skeletons.md)), обоснования решений с контраргументами ([`07-decision-justifications.md`](04-brand/07-decision-justifications.md)); PDF: [`pdf/PSB_Legal_Assistant_Brandbook.pdf`](../pdf/PSB_Legal_Assistant_Brandbook.pdf) | 7 файлов + PDF |
| RAG | [`05-rag/01-rag-deep-dive.md`](05-rag/01-rag-deep-dive.md) | требования R1-R14, архитектуры RAG, чанкинг, поиск, реранк, проверка, инъекция, дефекты D1-D28, прототип, метрики | 63.0 КБ |
| | [`05-rag/02-best-approaches-and-our-pipeline.md`](05-rag/02-best-approaches-and-our-pipeline.md) | инварианты I1-I10, стадии S0-S19, схемы JSON, проверки, решение статуса, бюджет времени L0-L4, ожидания по 18 демо-вопросам | 42.6 КБ |
| Роли | [`01-product/04-role-1-backend-rag.md`](01-product/04-role-1-backend-rag.md) | роль 1: карточки R1.1-R1.16 (зачем, вход, выход, шаги, готово / не готово, тесты, риск, влияние) | 31.5 КБ |
|  | [`01-product/05-role-2-frontend.md`](01-product/05-role-2-frontend.md) | роль 2: карточки R2.1-R2.11 | 15.4 КБ |
|  | [`01-product/06-role-3-kb-eval.md`](01-product/06-role-3-kb-eval.md) | роль 3: карточки R3.1-R3.10 (R3.6 демо не раскрыт) | 13.4 КБ |
|  | [`01-product/07-handoffs-and-interfaces.md`](01-product/07-handoffs-and-interfaces.md) | передачи H-01..H-12, протокол изменения контракта, RACI, эскалация | 7.4 КБ |
|  | [`01-product/08-tz-frontend-complete.md`](01-product/08-tz-frontend-complete.md) | полное ТЗ роли 2: каждый экран S0-S12, каждая кнопка K1-K10 и элемент (композер «Спросить»/«Остановить», чип `[n]`, панели, просмотр документа, уточнение, плашки, прогресс SSE), файлы `apps/web` на `d1f068c` as-is и to-be, FE-* с «где / как / зачем / готово / тест» | 73.3 КБ |
|  | [`01-product/09-tz-backend-complete.md`](01-product/09-tz-backend-complete.md) | полное ТЗ роли 1: модули ТЗ §8 и предложения узлов, ND1-ND7, эндпоинты, `solution.py` и CSV по шагам (D22), Docker и окружение, файлы на `d1f068c`, BE-* | 49.9 КБ |
|  | [`01-product/10-tz-kb-eval-complete.md`](01-product/10-tz-kb-eval-complete.md) | полное ТЗ роли 3: эталон базы, golden ≥ 135 по 19 типам, судья, отчёты, разбор ошибок, журнал сабмитов, README, презентация, замена документов «Бизнес: Старт», KE-* (R3.6 только указатель) | 23.8 КБ |
| Узлы | [`06-nodes/00-overview.md`](06-nodes/00-overview.md) | реестр узлов ND1-ND8, владельцы, потоки, формат файла узла, сводка as-is | 19.0 КБ |
|  | [`06-nodes/01-ingest-and-parse.md`](06-nodes/01-ingest-and-parse.md) | ND1 ингест, парсер, санитайзер | 18.9 КБ |
|  | [`06-nodes/02-index-and-retrieval.md`](06-nodes/02-index-and-retrieval.md) | ND2 токенизация, BM25, dense, RRF, гейт | 15.7 КБ |
|  | [`06-nodes/03-request-intake-and-guards.md`](06-nodes/03-request-intake-and-guards.md) | ND3 вход, история, лимиты, гарды | 13.1 КБ |
|  | [`06-nodes/04-clarify-and-counterparty-catalog.md`](06-nodes/04-clarify-and-counterparty-catalog.md) | ND4 понимание вопроса, каталог контрагентов, `clarify` | 19.4 КБ |
|  | [`06-nodes/05-editions-and-filters.md`](06-nodes/05-editions-and-filters.md) | ND5 редакции, ДС, граничные даты и пороги | 15.0 КБ |
|  | [`06-nodes/06-generate-verify-decide.md`](06-nodes/06-generate-verify-decide.md) | ND6 генерация, проверка claims, матрица статусов | 17.3 КБ |
|  | [`06-nodes/07-api-contract-and-submission.md`](06-nodes/07-api-contract-and-submission.md) | ND7 рендер, API, SSE, порты, `solution.py`, Docker | 19.6 КБ |
|  | [`06-nodes/08-frontend.md`](06-nodes/08-frontend.md) | ND8 фронтенд: композер, статусы, источники, генерация, ошибки | 13.2 КБ |
| Тесты | [`07-tests/00-strategy.md`](07-tests/00-strategy.md) | слои, LLM в тестах, флаки, ритм, определение регрессии, оценка текущих тестов | 15.8 КБ |
|  | [`07-tests/01-cascade.md`](07-tests/01-cascade.md) | каскадные тесты по 14 границам, «симптом → узел» | 32.8 КБ |
|  | [`07-tests/02-regression.md`](07-tests/02-regression.md) | регрессионный каталог: D1-D28, вопросы организатора, статусы, флаги, редакции, инъекции, API, сабмит, UI | 35.7 КБ |
|  | [`07-tests/03-unit-and-contract.md`](07-tests/03-unit-and-contract.md) | unit по модулям и контрактные тесты | 23.0 КБ |
|  | [`07-tests/04-eval-golden.md`](07-tests/04-eval-golden.md) | golden: формат, правила кейсов, dev/holdout, метрики, суррогатный судья | 16.9 КБ |
|  | [`07-tests/05-traceability.md`](07-tests/05-traceability.md) | требование → узел → тест → дефект → критерий | 9.2 КБ |
|  | [`07-tests/artifacts/asis-d1f068c-lexical-run.md`](07-tests/artifacts/asis-d1f068c-lexical-run.md) | артефакт: прогон as-is на `d1f068c` без LLM | 14.1 КБ |
| Ревью | [`08-review/00-overview.md`](08-review/00-overview.md) | виды ревью, метки, фиксация находок, готовность, ошибки ревьюера | 12.3 КБ |
|  | [`08-review/01-code-review-core.md`](08-review/01-code-review-core.md) | ревью кода ядра: RAG, проверка, `solution.py`, контракт | 15.9 КБ |
|  | [`08-review/02-frontend-design-review.md`](08-review/02-frontend-design-review.md) | ревью фронта и дизайна | 10.1 КБ |
|  | [`08-review/03-architecture-review.md`](08-review/03-architecture-review.md) | архитектурное ревью: ADR, узлы, границы, fail-closed | 9.1 КБ |
|  | [`08-review/04-security-review.md`](08-review/04-security-review.md) | ревью безопасности: инъекции, секреты, роль, API | 9.8 КБ |
|  | [`08-review/05-tests-and-eval-review.md`](08-review/05-tests-and-eval-review.md) | ревью тестов и eval: оракулы, покрытие, golden | 10.4 КБ |
|  | [`08-review/06-docs-review.md`](08-review/06-docs-review.md) | ревью документации на соответствие коду и кейсу | 7.8 КБ |
| Источники | [`99-sources.md`](99-sources.md) | реестр K-*, S-01..S-152, A-01..A-28, B1-B5 (бренд), неоткрывшиеся и неподтвердившиеся источники | 50.6 КБ |
| Изображения | [`../references/analogs/`](../references/analogs/) | 11 публичных изображений аналогов | |

## Сквозные идентификаторы
| Префикс | Где определён | Пример |
|---|---|---|
| K-*, S-*, A-*, B1-B5 | 99-sources | [K-REG], [S-24], [A-17], B1 (гайд ПСБ 2019) |
| M*, S1-S8, F*, E*, SEC*, NF* | 01-product/02 | M13 (формат CSV), E3 (редакция на дату события) |
| J1-J10 | 01-product/01 | J2 (редакция для прошлой сделки) |
| R1.*, R2.*, R3.* | 01-product/03 | R1.1 (плоские модули) |
| FE-*, BE-*, KE-* | 01-product/08, 09, 10 | BE-S04 (D22), FE-C01 (композер), KE-04 (golden) |
| C1-C4, A1-A5 | 02-architecture/01 | A1 (один путь ответа); не путать с аналогами A-01..A-28 (с дефисом) и активами A1-A6 в 02-architecture/04 |
| ADR-01..12 | 02-architecture/02 | ADR-02 (хранилище) |
| KB-A1..A7 | 02-architecture/03 | KB-A1 (инъекция в записке ЮО-7) |
| T1-T12 | 02-architecture/04 | T1 (косвенная инъекция) |
| P1-P22 | 03-analogs/02 | P4 (проверка до показа) |
| S0-S12 (экраны), F1-F5 (сценарии) | 04-brand/04 | S5 (отказ), F5 (демо для жюри) |
| ND1-ND8, FM-NDx-y | 06-nodes | ND6 (генерация и проверка), FM-ND2-1 (отказ `/embeddings`) |
| UT-*, CN-* | 07-tests/03 | UT-CAT-03 (точное равенство основ) |
| CT-Bn-* | 07-tests/01 | CT-B10-04 (D7) |
| RG-* | 07-tests/02 | RG-DEF-D18, RG-INJ-01 |
| EV-* | 07-tests/04 | EV-RET-12 (Q12) |
| H-01..H-12 | 01-product/07 | H-01 (`AnswerV2` схема) |
| BJ-01..BJ-10 | 04-brand/07 | BJ-02 (нет процента) |
| D1-D28, S0-S19 (стадии), I1-I10, L0-L4 | 05-rag | D1 (LLM видит только 240 символов) |

Префикс `S` занят трижды (требования SHOULD в ТЗ, экраны в 04-brand/04, стадии в 05-rag/02), `F` дважды (функциональные требования ТЗ и сценарии 04-brand/04). В ссылке всегда указывается файл: «05-rag/02 S15», «ТЗ S5», «04-brand/04 S5».

## Пять решений, которые важно знать всем
1. Один путь ответа: плоские модули `psb_*.py` в корне вызываются и `solution.py`, и FastAPI (ADR-01, A1).
2. В контуре хакатона нет БД: ~350 unit и векторы в памяти; Postgres+pgvector+FTS является продакшен-целью (ADR-02).
3. Ответ собирается только из claims, прошедших детерминированную проверку цитаты, чисел и редакции; иначе `limited`/`abstain` (ADR-08, 05-rag/02 S15-S17).
4. Редакции документов компании выбираются по дате события детерминированно, а не моделью (ТЗ E1-E12).
5. В базе есть настоящая промпт-инъекция (записка ЮО-7); она обрабатывается как данные и тест-кейс (KB-A1, T1).
