# Реестр источников

Все ссылки ниже открыты при подготовке пакета 9 ноября 2026 (вечер, Europe/Moscow). Для каждой указано, что именно из неё взято. В остальных документах ссылки идут с кодом `[S-xx]`, чтобы три человека в команде ссылались на одно и то же.

Правило: если источник не открывался (например, был заблокирован), это сказано явно. Утверждения про кейс берутся только из `[K-*]`.

Пространства идентификаторов в пакете (чтобы не путать): `K-*` материалы кейса и код; `S-01...S-152` внешние источники; `A-*` аналоги; `B1-B5` источники бренда (раздел B ниже, используются в `04-brand`). Отдельно от источников: `S0-S12` в `04-brand/04` это экраны, `S0-S19` в `05-rag/02` это стадии пайплайна, `S1-S8` в ТЗ §2.2 это требования SHOULD.

## K. Официальные материалы кейса и текущий репозиторий

| Код | Что | Где | Что взято |
|---|---|---|---|
| K-PDF | Кейс «ИИ-ассистент для юристов банка», Changellenge Hack&Change 2026 × ПСБ | `/workspace/pcb/PSB_case.pdf`, текст `/workspace/pcb/PSB_case.txt` (в репозитории PDF кейса не лежит) | ЦА, постановка задачи 01-06, ограничения 01-14, критерии онлайн-этапа и финала, формат сдачи |
| K-REG | Технический регламент секции ПСБ по проверке LLM-судьёй | `data/organizer/docs/Технический регламент _ ПСБ.docx` | формат `questions.csv`/`submission.csv`, DATA_DIR + `knowledge-base.zip`, только корневые `.py`, лимиты (5 сабмитов/день, 128 МБ, 8 CPU, 16 ГБ, 20 минут), переменные окружения, методика судьи (2 раунда, Match Rate 70% + Win Rate 30%, «выдуманный факт полностью обнуляет оценку») |
| K-SAMPLE | Минимальный пример сабмита организаторов | `data/organizer/sample/solution.py`, `sample/README.md` | вызовы `/embeddings`, `/rerank`, `/chat/completions`; дефолты `EMB_MODEL=baai/bge-m3`, `RERANKER_MODEL=cohere/rerank-5-fast` (расходится с регламентом), `TOP_K`, `MAX_WORKERS` |
| K-REQ | Разрешённый набор зависимостей | `data/organizer/requirements.txt` | список из 26 пакетов с версиями (numpy, faiss-cpu, chromadb, rank-bm25, bm25s, scikit-learn, rapidfuzz, httpx, openai, python-docx и др.). Нет PyStemmer, nltk, pymorphy, psycopg |
| K-KB | База знаний организаторов | `data/organizer/kb/*.txt`, `knowledge-base.zip` | 21 документ: 8 документов компании ООО «Меридиан», 13 выдержек статей законов (выгрузка ГАРАНТ от 10.10.2026) |
| K-DEMO | Демо-вопросы и эталонные ответы | `data/organizer/tests/demo_questions.csv`, `demo_output.csv` | 18 вопросов (5 с историей диалога), стиль эталона: коротко, номер договора, пункт, явный отказ |
| K-INTAKE | Intake юридического ассистента | `docs/00_intake/BA_BRIEF.md`, `ANALOGS.md`, `DECISIONS.md`, `SUMMARY.md`, `GARANT_SOURCE.md`, `STUBS.md`, `ORCHESTRATOR_BOARD.md`, `docs/ACCEPTANCE.md` | решения по стеку, контракт статусов, политика по ГАРАНТ, live-аудит Нейроюриста |
| K-CODE | Текущая реализация | `apps/answer-core/src/answer_core/{pipeline,server,cli}.py`, `solution.py`, `apps/web/src/components/LegalChat.tsx`, `apps/web/src/lib/legal-api.ts`, `docker-compose.yml`, `apps/answer-core/Dockerfile`, `.env.example`, `apps/answer-core/tests/test_pipeline.py` | как устроен пайплайн сейчас (коммит `07ae2f5`, 9 ноября 2026, 22:40 мск; сверено с `d1f068c`, 23:27 мск: эвристика `clarify`, локальный порт API 8090, тест `test_organizer_rent_short_question_grounded`, запись в `DECISIONS.md` о гранте Yandex Cloud только для local/dev) |

Репозиторий: https://github.com/SeyYestyq/PCB_HACK (ветка `main`, последние коммиты `ddf7ed6`, `1aac69d`, `07ae2f5`, `d1f068c`). Читался через raw-ссылки и GitHub API, без клонирования; `d1f068c` прочитан через GitHub API (патч и файлы на этом коммите).

## S. Внешние источники (открыты)

### RAG: обзоры и базовые работы
| Код | Источник | Что взято |
|---|---|---|
| S-01 | Lewis et al., 2020. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. https://arxiv.org/abs/2005.11401 | исходное определение RAG: параметрическая + непараметрическая память, provenance как открытая проблема |
| S-02 | Gao et al., 2023-2024. Retrieval-Augmented Generation for LLMs: A Survey. https://arxiv.org/abs/2312.10997 | таксономия Naive / Advanced / Modular RAG |
| S-03 | Huang, Huang, 2024. A Survey on Retrieval-Augmented Text Generation for LLMs. https://arxiv.org/abs/2404.10981 | деление на pre-retrieval, retrieval, post-retrieval, generation |
| S-04 | Singh et al., 2025. Agentic RAG: A Survey. https://arxiv.org/abs/2501.09136 | агентные паттерны: reflection, planning, tool use, multi-agent |
| S-05 | Wang et al., 2024. Searching for Best Practices in RAG. https://arxiv.org/abs/2407.01219 (HTML: https://arxiv.org/html/2407.01219v1) | эмпирика: query classification, Hybrid (+HyDE), reranking, «reverse» repacking; вес sparse α=0.3 лучший в их серии |

### Chunking и гранулярность
| Код | Источник | Что взято |
|---|---|---|
| S-06 | Günther et al., 2024. Late Chunking. https://arxiv.org/abs/2409.04701 | эмбеддинг всего документа, пулинг по чанкам после трансформера |
| S-07 | Anthropic, 2024. Introducing Contextual Retrieval. https://www.anthropic.com/news/contextual-retrieval | контекстный префикс 50-100 токенов к чанку; минус 49% неудачных извлечений, минус 67% с реранкингом; «если база меньше 200 000 токенов, можно положить всё в промпт» |
| S-08 | Chen et al., 2023. Dense X Retrieval: propositions. https://arxiv.org/abs/2312.06648 | мелкие единицы извлечения (propositions) лучше пассажей для поиска |
| S-09 | NitiBench, 2025. https://arxiv.org/abs/2502.10868 | юр. домен: section-based chunking значимо лучше naive; long-context LLM уступают RAG |
| S-10 | SAT-Graph RAG for Legal Norms, 2025. https://arxiv.org/abs/2505.00039 | структурная сегментация (статья, часть, пункт), point-in-time retrieval, версии норм |
| S-11 | VersionRAG, 2025. https://arxiv.org/abs/2510.08109 | на версионных вопросах naive RAG 58%, GraphRAG 64%, версионно-осознанный 90% |
| S-12 | RAPTOR, 2024. https://arxiv.org/abs/2401.18059 | иерархические рекурсивные саммари |
| S-13 | GraphRAG (Microsoft), 2024. https://arxiv.org/abs/2404.16130 | глобальные вопросы к корпусу, граф сущностей |
| S-14 | LightRAG, 2024. https://arxiv.org/abs/2410.05779 | облегчённый граф + вектор |

### Поиск, гибрид, переписывание запросов
| Код | Источник | Что взято |
|---|---|---|
| S-15 | Microsoft, Azure AI Search: Outperforming vector search with hybrid retrieval and reranking. https://techcommunity.microsoft.com/blog/azure-ai-services-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167 | таблица: keyword 40.6 / vector 43.8 / hybrid 48.4 / hybrid+reranker 60.1 NDCG@3 на клиентских данных; MIRACL 49.6 / 58.3 / 58.8 / 72.0 |
| S-16 | Qdrant docs, Hybrid Queries. https://qdrant.tech/documentation/concepts/hybrid-queries/ | RRF и DBSF, prefetch, формула RRF |
| S-17 | Elasticsearch Reference, Reciprocal rank fusion. https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion | `rank_constant` по умолчанию 60 |
| S-18 | OpenSearch docs, Hybrid search. https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/index/ | нормализация+комбинация скоров против RRF (score ranker) |
| S-19 | Weaviate, Hybrid Search Explained. https://weaviate.io/blog/hybrid-search-explained | параметр alpha, BM25F + вектор, RRF |
| S-20 | Gao et al., 2022. HyDE. https://arxiv.org/abs/2212.10496 | гипотетический документ для dense-поиска; «может содержать ложные детали» |
| S-21 | Ma et al., 2023. Query Rewriting for RAG (Rewrite-Retrieve-Read). https://arxiv.org/abs/2305.14283 | переписывание запроса перед поиском |
| S-22 | Rackauckas, 2024. RAG-Fusion. https://arxiv.org/abs/2402.03367 | multi-query + RRF |
| S-23 | Press et al., 2022. Self-Ask. https://arxiv.org/abs/2210.03350 | декомпозиция на подвопросы |
| S-24 | pgvector README. https://github.com/pgvector/pgvector | точный поиск по умолчанию, HNSW против IVFFlat, гибрид с FTS через RRF или cross-encoder |
| S-25 | PostgreSQL 18 docs, Text Search Dictionaries. https://www.postgresql.org/docs/current/textsearch-dictionaries.html | Snowball-стеммеры, конфигурация `russian` |
| S-26 | PostgreSQL 18 docs, Controlling Text Search. https://www.postgresql.org/docs/current/textsearch-controls.html | `ts_rank`, `ts_rank_cd`, подсветка |
| S-27 | Snowball, Russian stemming algorithm. https://snowballstem.org/algorithms/russian/stemmer.html | формальное описание русского стеммера (RV, R1, R2, классы окончаний) для собственной реализации без внешних пакетов |
| S-28 | bm25s. https://github.com/xhluca/bm25s | быстрая BM25 на numpy; стемминг требует PyStemmer (нет в разрешённом списке) |
| S-29 | rank_bm25. https://github.com/dorianbrown/rank_bm25 | BM25Okapi, чистый Python |
| S-30 | scikit-learn TfidfVectorizer. https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html | `analyzer='char_wb'` как морфологически устойчивый лексический канал без стеммера |
| S-31 | Faiss docs. https://faiss.ai/ | библиотека плотного поиска (разрешена, но избыточна для ~350 векторов) |
| S-32 | Chroma docs. https://docs.trychroma.com/docs/overview/introduction | встраиваемая векторная БД (разрешена) |

### Эмбеддинги и реранкеры
| Код | Источник | Что взято |
|---|---|---|
| S-33 | Chen et al., 2024. M3-Embedding (BGE-M3). https://arxiv.org/abs/2402.03216 | dense + sparse + multi-vector, 100+ языков, до 8192 токенов |
| S-34 | BAAI/bge-m3 model card. https://huggingface.co/BAAI/bge-m3 | размерность 1024, 8192 токена, рекомендация «hybrid retrieval + re-ranking» |
| S-35 | Snegirev et al., 2024. ruMTEB. https://arxiv.org/abs/2408.12503 (HTML v2) | на русском: BGE-M3 Retrieval 74.79 (лучший в таблице 5 среди 10 моделей), Rerank 69.71, Avg 61.58 |
| S-36 | Qwen3 Embedding / Reranker, 2025. https://arxiv.org/abs/2506.05176 | семейство 0.6B/4B/8B, instruction-aware |
| S-37 | Qwen/Qwen3-Reranker-8B model card. https://huggingface.co/Qwen/Qwen3-Reranker-8B | 32k контекст, 100+ языков, таблица MMTEB-R; инструкция на стороне запроса даёт +1-5% |
| S-38 | Izacard et al., 2021. Contriever. https://arxiv.org/abs/2112.09118 | плотный поиск без разметки, базовая линия для HyDE |

### Достоверность, цитирование, оценка
| Код | Источник | Что взято |
|---|---|---|
| S-39 | Asai et al., 2023. Self-RAG. https://arxiv.org/abs/2310.11511 | токены рефлексии: нужен ли поиск, релевантность, поддержка |
| S-40 | Yan et al., 2024. Corrective RAG (CRAG). https://arxiv.org/abs/2401.15884 | оценщик качества извлечения и ветвление действий; веб-поиск как расширение (нам запрещено) |
| S-41 | Gao et al., 2023. ALCE: Enabling LLMs to Generate Text with Citations. https://arxiv.org/abs/2305.14627 | метрики citation recall/precision; «даже лучшие модели в 50% случаев без полной поддержки цитатами» на ELI5 |
| S-42 | Honovich et al., 2022. TRUE: Re-evaluating Factual Consistency Evaluation. https://arxiv.org/abs/2204.04991 | NLI-проверка согласованности как метрика |
| S-43 | Dhuliawala et al., 2023. Chain-of-Verification. https://arxiv.org/abs/2309.11495 | черновик → проверочные вопросы → независимые ответы → финал |
| S-44 | Es et al., 2023. RAGAS. https://arxiv.org/abs/2309.15217 | faithfulness, answer relevance, context relevance |
| S-45 | Saad-Falcon et al., 2023. ARES. https://arxiv.org/abs/2311.09476 | автоматическая оценка RAG лёгкими судьями + PPI |
| S-46 | Liu et al., 2023. Lost in the Middle. https://arxiv.org/abs/2307.03172 | качество падает, когда релевантное в середине длинного контекста |
| S-47 | Ribeiro et al., 2020. CheckList. https://arxiv.org/abs/2005.04118 | поведенческое тестирование: MFT, INV, DIR |
| S-48 | Magesh et al., 2024. Hallucination-Free? https://arxiv.org/abs/2405.20362 | юр. RAG-инструменты ошибаются в 17-33% запросов; типология «incorrect» и «misgrounded» |
| S-49 | Stanford HAI. AI on Trial. https://hai.stanford.edu/news/ai-trial-legal-models-hallucinate-1-out-6-or-more-benchmarking-queries | «misgrounded»: норма описана верно, но источник её не подтверждает; >200 запросов |
| S-50 | Pipitone, Alami, 2024. LegalBench-RAG. https://arxiv.org/abs/2408.10343 | точное извлечение минимальных фрагментов важнее, чем ID документа или длинные куски |
| S-51 | CRAG Benchmark (Meta), 2024. https://arxiv.org/abs/2406.04744 | типы вопросов для RAG-оценки, включая false premise |
| S-52 | BehnamGhader et al., 2022. Can Retriever-Augmented LMs Reason? https://arxiv.org/abs/2212.09146 | похожесть не гарантирует извлечение всех нужных утверждений для вывода |

### LLM платформы
| Код | Источник | Что взято |
|---|---|---|
| S-53 | DeepSeek API docs. https://api-docs.deepseek.com/ | OpenAI-совместимый формат; `deepseek-flash` обслуживается DeepSeek-V4.1-Flash |
| S-54 | DeepSeek JSON Output. https://api-docs.deepseek.com/guides/json_mode.md | `response_format: json_object`, нужно слово json и пример; при сбое контент может быть пустыми пробелами |
| S-55 | DeepSeek Chat Completions API. https://api-docs.deepseek.com/api/create-chat-completion.md | `max_tokens` до 384K, дефолт 8K без thinking и 64K с thinking (128K при `reasoning_effort: max`); `temperature` в thinking-режиме не действует; перепроверено 10.11.2026 утром |
| S-56 | Radeon Cloud docs, DeepSeek-V4-Flash. https://amd-aim.github.io/radeon-cloud-docs/models/deepseek-v4-flash/ | сторонний провайдер и предыдущая версия V4: нативный контекст 1 048 576 токенов, thinking выключен, если не запрошен. Низкий вес; для V4.1 см. [S-69], [S-70] |
| S-69 | DeepSeek, Models & Pricing. https://api-docs.deepseek.com/quick_start/pricing | открыт на ревью 09.11.2026: `deepseek-flash` = DeepSeek-V4.1-Flash-1017, контекст 1M, max output 384K, JSON Output поддерживается, thinking «default» |
| S-70 | DeepSeek, Thinking Mode. https://api-docs.deepseek.com/guides/thinking_mode | открыт на ревью 09.11.2026: thinking включён по умолчанию (effort high), выключается `{"thinking": {"type": "disabled"}}` в `extra_body`; в thinking-режиме `temperature`, `presence_penalty`, `frequency_penalty` не действуют (ошибки нет); рассуждение возвращается полем `reasoning_content` рядом с `content`. Перепроверено 10.11.2026 утром. Поведение прокси организаторов неизвестно |

### Безопасность
| Код | Источник | Что взято |
|---|---|---|
| S-57 | OWASP GenAI, LLM01:2025 Prompt Injection. https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | прямые и косвенные инъекции; RAG не устраняет инъекции; least privilege |
| S-58 | OWASP GenAI, LLM08:2025 Vector and Embedding Weaknesses. https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/ | отравление данных, утечки через эмбеддинги, контроль доступа |
| S-59 | OWASP Cheat Sheet, LLM Prompt Injection Prevention. https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | структурированные промпты с разделением, валидация вывода, RAG poisoning, hidden text |
| S-60 | Greshake et al., 2023. Indirect Prompt Injection. https://arxiv.org/abs/2302.12173 | инъекции через извлекаемые данные |
| S-61 | Hines et al., 2024. Spotlighting. https://arxiv.org/abs/2403.14720 | маркировка источника данных снижает успех атак с >50% до <2% (на GPT) |
| S-62 | NIST AI 600-1, Generative AI Profile. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf | риск «Confabulation»: уверенно поданный ложный контент |
| S-63 | Microsoft Presidio. https://github.com/microsoft/presidio | детекция и маскирование ПДн для продакшен-контура |

### Стек
| Код | Источник | Что взято |
|---|---|---|
| S-64 | FastAPI, Concurrency and async/await. https://fastapi.tiangolo.com/async/ | `def`-эндпоинты выполняются в threadpool |
| S-65 | Next.js, `output: 'standalone'`. https://nextjs.org/docs/app/api-reference/config/next-config-js/output | минимальный образ для Docker |
| S-66 | Vite, Getting Started. https://vite.dev/guide/ | dev server + build, SPA без сервера |
| S-67 | React docs, Creating a React App. https://react.dev/learn/creating-a-react-app | React рекомендует стартовать с фреймворка; Vite как путь «с нуля» |
| S-68 | Docker docs, How Compose works. https://docs.docker.com/compose/intro/compose-application-model/ | канонический файл `compose.yaml` |

### Аналоги
| Код | Источник | Что взято |
|---|---|---|
| A-01 | Яндекс Нейроюрист, лендинг. https://neurolegal.ya.ru/ | тарифы 1 999 / 5 999 ₽, «Доступ к источникам», Гарант Лайт +3 000 ₽/мес, команды, Word |
| A-02 | Справка Нейроюриста. https://yandex.ru/support/neurolegal/ru/ | на базе Alice AI; автоматический выбор сфер права и источников; чаты и умные папки |
| A-03 | Справка, Быстрый старт. https://yandex.ru/support/neurolegal/ru/quick-start | ссылки на законы открываются в системе «Гарант», полные тексты платно; источники чата: файлы, ссылки, умные папки; лайк/дизлайк |
| A-04 | ИСКРА, LegalTech ГАРАНТ. https://lt.garant.ru/prod/iskra | ответы со ссылками, подборка документов, профили, отзыв «работает только по базе ГАРАНТа» |
| A-05 | ИСКРА, лендинг. https://iskra.garant.ru/ | ИСКРА 2.0: загрузка файлов, проверка договоров, профили, PDF-экспорт, реестр российского ПО |
| A-06 | Инструкция по работе с ИСКРОЙ (PDF). https://www.garant.ru/files/7/3/1929137/instruktsiya_po_rabote_s_iskroy.pdf | открыт через поисковую выдачу: статусы «Ищу ответы в системе ГАРАНТ», ссылка открывает документ на релевантной статье/пункте, экспорт диалога в PDF |
| A-07 | Функциональное описание ИСКРЫ (PDF). http://adm.garant.ru/files/7/3/1929137/funktsionalnie_harakteristiki.pdf | открыт через поисковую выдачу: анализ запроса → поиск норм в ЭПС → запрос к LLM; модель разработчика или клиента |
| A-08 | КонсультантПлюс, ИИ-сервис «Задать вопрос». https://www.consultant.ru/about/nc/ai_inform/ | подборка документов, уточняющие вопросы с контекстом, история диалогов |
| A-09 | КонсультантПлюс, «Спроси ИИ-помощник. Проверь в СПС». https://www.consultant.ru/news/558/ | режимы «Задать вопрос», «Проверка договоров», «Глубокий поиск» |
| A-10 | Новость о запуске 04.12.2025. https://cons-plus.ru/o-yu-soft/novosti/?newsid=6040 | экспериментальный режим, «всегда сверяться с системой» (открыт через выдачу поиска) |
| A-11 | Обзор legalai.guru. https://legalai.guru/ru/ii-funkcii-konsultantplyus-i-garanta/ | вторичный обзор, сравнение К+ и ГАРАНТ (вторичный, низкий вес) |
| A-12 | platforms.su, кейс ИИ-помощника К+. https://platforms.su/project/2911 | вторичный: «подсветка устаревших документов», 4 000 символов запроса (вторичный, низкий вес) |
| A-13 | Harvey, главная. https://www.harvey.ai/ | платформа: Agents, Vault, Knowledge, Spaces |
| A-14 | Harvey Vault. https://www.harvey.ai/products/vault | до 100 000 документов в vault, review tables, вопросы к таблице |
| A-15 | Harvey Knowledge. https://www.harvey.ai/products/knowledge | «accurately-cited answers» |
| A-16 | Harvey, Introducing BigLaw Bench. https://www.harvey.ai/blog/introducing-biglaw-bench | рубрики со штрафами за тон, длину, нерелевантность, галлюцинации |
| A-17 | Harvey, BigLaw Bench: Sources. https://www.harvey.ai/blog/biglaw-bench-sources | «source score»: связь фактических утверждений с документами |
| A-18 | Thomson Reuters, CoCounsel Legal. https://legal.thomsonreuters.com/en/products/cocounsel-legal | план шагов с прозрачным рассуждением, grounded в Westlaw и Practical Law, Deep Research |
| A-19 | Thomson Reuters, завершение покупки Casetext (2023). https://www.thomsonreuters.com/en/press-releases/2023/august/thomson-reuters-completes-acquisition-of-casetext-inc | происхождение CoCounsel |
| A-20 | LexisNexis Protégé. https://www.lexisnexis.com/en-us/products/protege.page | проверка связанных источников через Shepard's, Vault, «private, secure, authoritative» |
| A-21 | Legora. https://legora.com/ | Tabular Review, Workflows, Legal Research «citation-backed», Monitors, решения для банков |
| A-22 | Legora Tabular Review. https://legora.com/product/tabular-review | документ = строка, промпт = колонка, «each one cited to its source» |
| A-23 | Doczilla AI. https://doczilla.pro/ai/ | набор инструментов: сравнение версий, допсоглашение из договора, акты, ответы |
| A-24 | Doczilla, Модуль AI. https://help.doczilla.pro/articles/kb-dz/march-2025-ai | проверка договора по чек-листу внутри редактора |
| A-25 | Luminance. https://www.luminance.com/ | Contract Intelligence Platform |
| A-26 | Spellbook. https://www.spellbook.legal/ | ревью договоров в Word, Ask / Draft / Review, playbooks |
| A-27 | ABA Journal о JPMorgan COiN. https://www.abajournal.com/news/article/jpmorgan_chase_uses_tech_to_save_360000_hours_of_annual_work_by_lawyers_and | банковский прецедент: 12 000 кредитных договоров в год, 360 000 часов |
| A-28 | Сбер GigaLegal. https://gigalegal.sber.ru/ | страница открылась, но контент рендерится скриптом (39 символов текста); факты о продукте не подтверждены первичным источником |

### Тестирование, оценка, ревью, интерфейс (добавлено 10.11.2026)

Все ссылки открыты 10.11.2026 (HTTP 200; S-123 отдал PDF после ответа 202). Используются в `06-nodes`, `07-tests`, `08-review`, `04-brand/07`, `01-product/04`-`07`.

| Код | Источник | Что берём |
|---|---|---|
| S-71 | Vocke, Practical Test Pyramid (martinfowler.com), 2018. https://martinfowler.com/articles/practical-test-pyramid.html | тесты разной гранулярности; чем выше уровень, тем меньше тестов; узкие интеграционные тесты |
| S-72 | Robinson, Consumer-Driven Contracts: A Service Evolution Pattern (martinfowler.com). https://martinfowler.com/articles/consumerDrivenContracts.html | потребитель фиксирует ожидания, провайдер проверяет себя против них |
| S-73 | Pact docs, Introduction. https://docs.pact.io/ | инструмент контрактного тестирования |
| S-74 | Google Testing Blog, Just Say No to More End-to-End Tests, 2015. https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html | первая оценка 70/20/10; «рожок мороженого» как антипаттерн |
| S-75 | Software Engineering at Google, гл. 11 Testing Overview. https://abseil.io/resources/swe-book/html/ch11.html | размеры small/medium/large; примерно 80/15/5 |
| S-76 | Google Testing Blog, Flaky Tests at Google and How We Mitigate Them, 2016. https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html | около 1,5% флаки-прогонов; 84% переходов pass→fail связаны с флаки |
| S-77 | Thinking Machines, Defeating Nondeterminism in LLM Inference, 2025. https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/ | 1000 запусков при temperature 0 дали 80 уникальных завершений; batch invariance |
| S-78 | Barnett et al., 2024. Seven Failure Points When Engineering a RAG System. https://arxiv.org/abs/2401.05856 | FP1-FP7 |
| S-79 | Ru et al., 2024. RAGChecker. https://arxiv.org/abs/2408.08067 | диагностические метрики поиска и генерации |
| S-80 | Zheng et al., 2023. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. https://arxiv.org/abs/2306.05685 | позиционное смещение, многословие, самопредпочтение; согласие > 80% |
| S-81 | Min et al., 2023. FActScore. https://arxiv.org/abs/2305.14251 | оценка по атомарным фактам |
| S-82 | RAGAS docs, Faithfulness. https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/ | доля утверждений, выводимых из контекста |
| S-83 | Reuter et al., 2025. Towards Reliable Retrieval in RAG Systems for Large Legal Datasets. https://arxiv.org/abs/2510.06999 | DRM в юридическом RAG |
| S-84 | Aliannejadi et al., 2019. Asking Clarifying Questions in Open-Domain Information-Seeking Conversations. https://arxiv.org/abs/1907.06554 | одно уточнение: рост P@1 более 170% |
| S-85 | Zhang et al., 2024. CLAMBER. https://arxiv.org/abs/2405.12063 | LLM плохо распознают необходимость уточнения |
| S-86 | Chroma Research, Evaluating Chunking Strategies for Retrieval. https://research.trychroma.com/evaluating-chunking | выбор чанкинга меняет recall до 9% |
| S-87 | Google SRE Book, Addressing Cascading Failures. https://sre.google/sre-book/addressing-cascading-failures/ | каскадные отказы, повторы как усилитель |
| S-88 | AWS Architecture Blog, Exponential Backoff And Jitter. https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ | экспоненциальная пауза с jitter |
| S-89 | pip docs, Repeatable Installs. https://pip.pypa.io/en/stable/topics/repeatable-installs/ | закрепление версий |
| S-90 | The Twelve-Factor App, III. Config. https://12factor.net/config | конфигурация в окружении |
| S-91 | Hamel Husain, Your AI Product Needs Evals. https://hamel.dev/blog/posts/evals/ | три уровня оценки; смотреть на данные |
| S-92 | Schemathesis docs. https://schemathesis.readthedocs.io/ | свойство-ориентированное тестирование API по схеме |
| S-93 | Playwright docs, Accessibility testing. https://playwright.dev/docs/accessibility-testing | автоматические проверки находят не все проблемы |
| S-94 | Kent C. Dodds, The Testing Trophy and Testing Classifications. https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications | вес интеграционных тестов во фронтенде |
| S-95 | WHATWG HTML, Server-sent events. https://html.spec.whatwg.org/multipage/server-sent-events.html | формат потока |
| S-96 | MDN, EventSource. https://developer.mozilla.org/en-US/docs/Web/API/EventSource | лимит 6 соединений на HTTP/1; нет тела запроса |
| S-97 | Python docs, os.replace. https://docs.python.org/3/library/os.html#os.replace | атомарная замена файла |
| S-98 | Python docs, csv.QUOTE_ALL. https://docs.python.org/3/library/csv.html#csv.QUOTE_ALL | кавычки у всех полей |
| S-99 | Pydantic docs, Fields: string constraints. https://docs.pydantic.dev/latest/concepts/fields/#string-constraints | `max_length` |
| S-100 | Next.js docs, rewrites. https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites | rewrites как URL-прокси |
| S-101 | MDN, aria-live. https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-live | объявление изменений без фокуса |
| S-102 | FastAPI docs, Custom Response, StreamingResponse. https://fastapi.tiangolo.com/advanced/custom-response/ | потоковый ответ |
| S-103 | Apple HIG, Generative AI. https://developer.apple.com/design/human-interface-guidelines/generative-ai | конкретная обратная связь во время генерации вместо «Processing…»; модели ошибаются |
| S-104 | W3C, Understanding WCAG 1.4.8 Visual Presentation. https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html | строка не длиннее 80 символов |
| S-105 | NN/g, Horizontal Attention Leans Left. https://www.nngroup.com/articles/horizontal-attention-leans-left/ | около 80% внимания на левой половине |
| S-106 | NN/g, Progress Indicators Make a Slow System Less Insufferable. https://www.nngroup.com/articles/progress-indicators/ | зацикленная анимация для 2-10 с; дольше 10 с показывать прогресс |
| S-107 | NN/g, Serif vs. Sans-Serif Fonts for HD Screens. https://www.nngroup.com/articles/serif-vs-sans-serif-fonts-hd-screens/ | одно-два семейства |
| S-108 | Golos Text, README (GitHub). https://github.com/googlefonts/golos-text | заказан для государственных и социальных сайтов; ParaType 2019; OFL |
| S-109 | GOV.UK Design System, Button. https://design-system.service.gov.uk/components/button/ | избегать выключенных кнопок; защита от двойного клика |
| S-110 | Gnewuch et al., ECIS 2018. Faster Is Not Always Better. https://aisel.aisnet.org/ecis2018_rp/113/ | задержки ответа чат-бота повышают человечность и удовлетворённость |
| S-111 | Cohn et al., 2024. Believing Anthropomorphism. https://arxiv.org/abs/2405.06079 | первое лицо повышает воспринимаемую точность; n=2165 |
| S-112 | Colour Blind Awareness, Colour Blindness. https://www.colourblindawareness.org/colour-blindness/ | около 1 из 12 мужчин |
| S-113 | W3C, Understanding WCAG 4.1.3 Status Messages. https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | статусные сообщения без фокуса |
| S-114 | W3C, Understanding WCAG 2.2.2 Pause, Stop, Hide. https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html | движение дольше 5 с |
| S-115 | W3C, Understanding WCAG 1.4.1 Use of Color. https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | цвет не единственный носитель |
| S-116 | Primer, Size foundations. https://primer.style/foundations/primitives/size | радиусы 3 / 6 / 12 / full |
| S-117 | Python docs, zipfile metadata_encoding. https://docs.python.org/3/library/zipfile.html | имена без UTF-8 флага декодируются как cp437 |
| S-118 | Google Engineering Practices, The Standard of Code Review. https://google.github.io/eng-practices/review/reviewer/standard.html | одобрять, если изменение улучшает состояние кода; идеального кода нет |
| S-119 | Google Engineering Practices, What to look for in a code review. https://google.github.io/eng-practices/review/reviewer/looking-for.html | дизайн важнее всего |
| S-120 | Google Engineering Practices, Speed of Code Reviews. https://google.github.io/eng-practices/review/reviewer/speed.html | максимум один рабочий день |
| S-121 | Google Engineering Practices, Small CLs. https://google.github.io/eng-practices/review/developer/small-cls.html | 100 строк обычно разумно, 1000 обычно много |
| S-122 | Google Engineering Practices, How to write code review comments. https://google.github.io/eng-practices/review/reviewer/comments.html | метки Nit / Optional / FYI; комментировать код, а не автора |
| S-123 | Sadowski et al., ICSE-SEIP 2018. Modern Code Review: A Case Study at Google. https://sback.it/publications/icse2018seip.pdf | 9 млн изменений; медиана 24 строки; медиана 1 ревьюер; цели ревью |
| S-124 | Chromium docs, Code Reviews (OWNERS). https://chromium.googlesource.com/chromium/src/+/HEAD/docs/code_reviews.md | владельцы каталогов |
| S-125 | LLVM docs, Code Review. https://llvm.org/docs/CodeReview.html | ревью после коммита и откат |
| S-126 | OWASP Cheat Sheet, Secure Code Review. https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html | ручной разбор, ревью по diff с контекстом |
| S-127 | OWASP Code Review Guide. https://owasp.org/www-project-code-review-guide/ | перечень мест для поиска уязвимостей |
| S-128 | Microsoft ISE Engineering Playbook, Code Reviews. https://microsoft.github.io/code-with-engineering-playbook/code-reviews/ | практики ревью |
| S-129 | Microsoft Learn, About pull requests (Azure DevOps). https://learn.microsoft.com/en-us/azure/devops/repos/git/about-pull-requests | политики ветки |
| S-130 | SmartBear, Best Practices for Code Review. https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ | 200-400 строк за 60-90 минут; вендорское, вес низкий |
| S-131 | adr.github.io, Architectural Decision Records. https://adr.github.io/ | AD как обоснованный выбор; ASR |
| S-132 | Nygard, Documenting Architecture Decisions, 2011. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | контекст, решение, статус, последствия |
| S-133 | Ubl, Design Docs at Google. https://www.industrialempathy.com/posts/design-docs-at-google/ | обсуждение компромиссов до кода |
| S-134 | W3C WAI, Evaluating Web Accessibility Overview / WCAG-EM. https://www.w3.org/WAI/test-evaluate/ | процедура ручной оценки |
| S-135 | Conventional Comments. https://conventionalcomments.org/ | blocking / non-blocking |
| S-136 | Thoughtworks Technology Radar, Lightweight Architecture Decision Records (Adopt, ноябрь 2017). https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records | ADR хранить в системе контроля версий рядом с кодом, а не в вики; открыто при втором проходе 10.11.2026 |
| S-137 | Bacchelli, Bird, ICSE 2013. Expectations, Outcomes, and Challenges of Modern Code Review. https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf | Microsoft: 873 разработчика и 165 менеджеров; поиск дефектов остаётся главным мотивом (первый для 44%), но комментариев про дефекты мало и они в основном о мелких логических ошибках; главное в ревью понимание контекста изменения; открыто 10.11.2026 (PDF Microsoft Research) |
| S-138 | Amershi et al., CHI 2019. Guidelines for Human-AI Interaction. https://www.microsoft.com/en-us/research/uploads/prod/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf ; страница HAX Toolkit https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/ | 18 принципов, проверка с 49 практиками на 20 продуктах; G1 «что система умеет», G2 «насколько хорошо», G10 «при сомнении уточнять или сужать сервис», G11 «почему система так сделала»; открыто 10.11.2026 |
| S-139 | Parasuraman, Riley, 1997. Humans and Automation: Use, Misuse, Disuse, Abuse. Human Factors 39(2). Копия на сайте MIT: https://web.mit.edu/16.459/www/parasuraman.pdf | misuse = чрезмерное доверие автоматике; disuse = отказ от неё, чаще всего из-за ложных тревог; аннотация прочитана по скану 10.11.2026 (doi.org отдаёт 403) |
| S-140 | Material Components for Android, Shape (документация Material 3 в репозитории Google). https://github.com/material-components/material-components-android/blob/master/docs/theming/Shape.md | шкала углов M3: 0 / 4 / 8 / 12 / 16 / 20 / 28 / 32 / 48 dp и full 50%; m3.material.io отдаёт только скрипт, поэтому взята официальная документация компонентов |
| S-141 | nginx docs, ngx_http_proxy_module, proxy_buffering. https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering | буферизация ответа прокси включена по умолчанию; выключается директивой или заголовком ответа `X-Accel-Buffering: no` |
| S-142 | Next.js docs, compress. https://nextjs.org/docs/app/api-reference/config/next-config-js/compress | `next start` по умолчанию сжимает ответы gzip; `compress: false` выключает |
| S-143 | W3C WAI-ARIA APG, Developing a Keyboard Interface: Focusability of disabled controls. https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ | атрибут `disabled` убирает элемент из порядка табуляции, и пользователь скринридера его не находит; `aria-disabled="true"` сохраняет фокус |
| S-144 | Friedman, Smashing Magazine, 2021. Usability Pitfalls of Disabled Buttons, and How To Avoid Them. https://www.smashingmagazine.com/2021/08/frustrating-design-patterns-disabled-buttons/ | `aria-disabled` вместо `disabled`, подсказка по фокусу с клавиатуры, не `pointer-events: none`; вес ниже W3C |
| S-145 | Spring Batch Reference, Configuring Skip Logic. https://docs.spring.io/spring-batch/reference/step/chunk-oriented-processing/configuring-skip.html | пропуск записи при ошибке с лимитом пропусков; решение о пропуске принимает тот, кто понимает данные; пропущенные записи логируются |
| S-146 | ГК РФ ст. 4 «Действие гражданского законодательства во времени» (КонсультантПлюс). https://www.consultant.ru/document/cons_doc_LAW_5142/42424a8a7b508486936cd17cc02a84e09b591267/ | акты не имеют обратной силы; к договорам, заключённым раньше, применяется ст. 422 |
| S-147 | ГК РФ ст. 422 «Договор и закон» (КонсультантПлюс). https://www.consultant.ru/document/cons_doc_LAW_5142/478c38e91f6a68f9b7fa064f292dda8bf3049359/ | договор соответствует императивным нормам на момент заключения; новый закон распространяется на ранее заключённые договоры, только если это в нём прямо сказано |
| S-148 | ГК РФ ст. 1473 «Фирменное наименование» (КонсультантПлюс). https://www.consultant.ru/document/cons_doc_LAW_64629/d36a4b7f0e75db56ba6e7f8c76a44a8b8a22ade5/ | фирменное наименование = указание на организационно-правовую форму + собственно наименование; одно полное и одно сокращённое на русском |
| S-149 | КонсультантПлюс, учебный центр: «Исключительные права на средства индивидуализации». https://www.consultant.ru/edu/center/training/ip/theme4/ | регистрирующий орган не обязан проверять уникальность фирменного наименования, поэтому существуют юрлица с совпадающими именами; при совпадении определяющими являются ОГРН и ИНН; учебный материал, вес ниже текста кодекса |
| S-150 | Material Design 3, Shape: Corner radius scale. https://m3.material.io/styles/shape/corner-radius-scale | открыто 10.11.2026 утром (раньше отдавалось только скриптом): шкала из десяти стилей 0 / 4 / 8 / 12 / 16 / 20 / 28 / 32 / 48 dp и full; «Be careful not to apply large or full corners to information-dense components, such as cards»; кнопки по умолчанию привязаны к full, и продукт может переназначить их на small или medium; оптическая скруглённость вложенных объектов: внешний радиус минус отступ равно внутреннему, одинаковый радиус у вложенных объектов назван ошибкой |
| S-151 | Samsonov, NN/g, 16.05.2025. AI Chatbots Discourage Error Checking. https://www.nngroup.com/articles/ai-chatbots-discourage-error-checking/ | открыто 10.11.2026: уверенный тон и аккуратное оформление ответа LLM работают как сигналы авторитетности (эффект ореола), пользователи принимают ответ без проверки; предупреждение «может ошибаться» уезжает за край экрана после первых реплик; проверка цитаты дорога (найти текст, найти место, проверить контекст), поэтому совет: глубокая ссылка на процитированный фрагмент или его предпросмотр в источнике |
| S-152 | Starlette docs, Middleware: CORSMiddleware (https://github.com/encode/starlette/blob/master/docs/middleware.md) и исходник `starlette/middleware/cors.py` (https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py), ветка master | открыто 10.11.2026 утром: «`allow_origins`, `allow_methods` and `allow_headers` cannot be set to `['*']` for credentials to be allowed, all of them must be explicitly specified»; в коде при `*` и `allow_credentials=True` в ответ подставляется origin запроса («If credentials are allowed, then we must respond with the specific origin instead of '*'»). Поведение конкретной версии в проекте не проверено |

## B. Источники бренда ПСБ (коды в `04-brand/*`)
| Код | Источник | Что взято |
|---|---|---|
| B1 | «Руководство по использованию фирменного стиля ПАО «Промсвязьбанк»», 2019, разделы 02.10-02.12. Копия: https://petr-panda.ru/wp-content/uploads/2023/03/Brandbook.pdf (через Wayback), локально `references/brand/PSB_Brandbook.pdf` | Blue 072C #2B2C84, 172C #EA5614, 431 #646872, 5753C #4E621C; Gilroy, запасной Verdana. Сторонняя копия, не страница банка |
| B2 | psbank.ru/bank/style и PDF логотипа `PSB_brandbook_logo.pdf` | цвета знака #FF6200, #5B54E7, #8D87FF, #000F3C; «ПСБ Лавр»; охранное поле 1/2 высоты знака. Открыт с отключённой проверкой TLS (российский УЦ) |
| B3 | Depot WPF, кейс ребрендинга ПСБ. https://www.depotwpf.ru/portfolio/psb/ | перепроверен 09.11.2026: синий основной, оранжевый для акцентов; розница синий, МСБ серый, ГОЗ хаки |
| B4 | CSS psbank.ru (`/css-psb/page-layout.css`, `/css-psb/redesign.css`) | нейтрали #3E3E59, #5C5C73, #8D8DA6, #F8F8FC, #F0F0F7, #E6E6EF, #C7C7D9; ошибка #BB3E45; радиус кнопок 4px |
| B5 | Коммерсантъ, «Промсвязьбанк объявляет о ребрендинге». https://www.kommersant.ru/doc/4005173 | перепроверен 09.11.2026: сохранено сочетание оранжевого и синего; светлые тона в офисах |

Конфликт B1 и B2 (разные экранные цвета) не разрешён: продукт следует B1, цвета B2 только внутри файла логотипа. Нужна сверка с банком.

### Не удалось открыть или не подтвердилось
- base.garant.ru/483425826 (цитата про ИСКРУ «объясняет, почему выбрала именно их»): страница открывается, но текст отдаётся скриптом; на ревью 09.11.2026 цитата не подтверждена, в материалах не используется как факт.
- Cormack et al., 2009, RRF (dl.acm.org вернул 403, plg.uwaterloo.ca вернул 500). Формула и дефолт k=60 подтверждены по [S-16], [S-17].
- Thomson Reuters blog про агентный CoCounsel: 404.
- platforms.su/project/2441 (кейс GigaLegal): 503.
- NN/g, статья про automation bias (`/articles/automation-bias/`): 404 и при четвёртой попытке 10.11.2026 утром; в Wayback Machine снимков этого адреса нет, то есть статьи с таким адресом, вероятно, не было. Не используется; тему закрывают первоисточник [S-139] и статья NN/g о проверке ответов чат-ботов [S-151].
- Открылись при третьем проходе 10.11.2026 по альтернативным адресам и сняты из этого списка: Bacchelli & Bird 2013 (PDF Microsoft Research) [S-137], Microsoft HAX / Amershi et al. 2019 [S-138], Parasuraman & Riley 1997 (копия MIT) [S-139]. При четвёртом проходе 10.11.2026 открылась и страница m3.material.io о шкале углов [S-150].
