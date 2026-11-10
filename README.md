# Юридический ассистент ПСБ

ИИ-ассистент для юристов банка (Changellenge >> Hack&Change 2026 × ПСБ): поиск по базе знаний организаторов, ответы со ссылками на положения, обоснованный отказ.

## Одна команда (Docker)

```bash
docker compose up --build
```

- Чат: http://localhost:3000  
- API: http://localhost:8090/health  
- Postgres + pgvector: localhost:5432 (`copilot` / `copilot`, база `copilot`)  
- База знаний: `data/organizer/kb` (монтируется в контейнер)

При старте `answer` кладёт эмбеддинги фрагментов в pgvector. Если у прокси нет `/embeddings`, контейнер считает векторы моделью `paraphrase-multilingual-MiniLM-L12-v2`. На платформе Postgres нет: `solution.py` берёт BGE-M3 из `EMB_MODEL` и ищет по тем же векторам в памяти. Без эмбеддингов остаётся BM25.

Конфиг: [`compose.yaml`](compose.yaml) (имя по требованиям кейса).

## Переменные окружения

Скопируйте `.env.example` → `.env` (секреты не коммитить).

| Переменная | Назначение |
|---|---|
| `LLM_BASE_URL` / `OPENAI_BASE_URL` | OpenAI-совместимый прокси (на платформе подставляется автоматически) |
| `LLM_API_KEY` / `OPENAI_API_KEY` | ключ прокси (на платформе автоматически) |
| `LLM_MODEL` / `GEN_MODEL` | модель из окружения платформы (DeepSeek V4.1 Flash); не зашивать другое имя для сабмита |
| `DATA_DIR` | каталог с `questions.csv` и `knowledge-base.zip` (по умолчанию `data`) |
| `PSB_KB_PATH` | локальный путь к KB (каталог `.txt` или `.zip`) для разработки |
| `CORS_ORIGINS` | разрешённые origin для API |

Веб-чат вызывает `POST /api/v1/ask` на своём origin. В dev Vite проксирует `/api` на `127.0.0.1:8090`. В Docker nginx проксирует `/api/` на `http://answer:8090/api/`.

Платформенные модели: DeepSeek V4.1 Flash · BGE-M3 · опционально Qwen3 Reranker. Внешние источники для юридических утверждений не используются.

## Проверка основного сценария

1. `docker compose up --build`
2. Открыть http://localhost:3000
3. Спросить: `Какая арендная плата по договору с ООО «Северный Склад»?`
4. Ожидание: статус «Подтверждено источниками», в панели справа фрагмент договора с суммой 450 000
5. Спросить: `Какой размер пособия по беременности и родам?` — ожидается обоснованный отказ (в базе нет)

Локально без Docker:

```bash
# API
pip install -r apps/answer-core/requirements.txt
PYTHONPATH=.:apps/answer-core/src PSB_KB_PATH=data/organizer/kb \
  python3 -m uvicorn answer_core.server:app --host 127.0.0.1 --port 8090

# UI
cd apps/web && npm install && npm run dev
```

## Сабмит на платформу (`solution.py`)

В ZIP — только корневые `solution.py`, `psb_*.py`, `requirements.txt` (без `.env`, KB, `vendor/`, `node_modules/`, Docker/UI). Лимит платформы: **≤ 128 MB**.

```bash
# Собрать ZIP локально (не загружает на платформу)
./scripts/pack_submission_zip.sh
# → dist/psb_submission.zip

# Как на платформе: без аргументов → submission.csv
DATA_DIR=data/organizer/tests PSB_KB_PATH=data/organizer/kb python3 solution.py

# Один вопрос (JSON)
python3 solution.py "Какая арендная плата по договору с ООО «Северный Склад»?"
```

Платформа передаёт `DATA_DIR/questions.csv` и `DATA_DIR/knowledge-base.zip`. Скрипт пишет `submission.csv` (`id,answer`), параллелит через `MAX_WORKERS`, изолирует сбой одного вопроса, пишет через временный файл.

Опционально: `RERANKER_MODEL` → `POST {LLM_BASE_URL}/rerank` (fail-open на порядок RRF). Не хардкодить Cohere — брать модель из env платформы.

Подробнее: [`docs/SUBMIT_ZIP.md`](docs/SUBMIT_ZIP.md).

## Структура

| Путь | Назначение |
|---|---|
| `solution.py`, `psb_*.py` | Точка входа и ядро для автооценки (корень ZIP) |
| `apps/answer-core` | FastAPI-обёртка над тем же ядром |
| `apps/web` | Веб-чат с панелью фрагментов |
| `data/organizer` | KB, demo Q/A, sample ZIP организаторов |
| `PSB_Legal_Assistant` | Пакет документации по ролям (не нужен для запуска) |

## Известные ограничения

- Реранкер на платформе опционален. Dense-канал: BGE-M3 через `/embeddings` (в Docker те же векторы лежат в pgvector). Если эмбеддинги недоступны, поиск остаётся на BM25.
- В базе только действующие редакции законов; запрос старой редакции → отказ с пояснением.
- Смоук интерфейса: `apps/web/e2e/legal.spec.ts`.
- Живой ключ LLM нужен для генерации; без ключа ответы лексические по найденным фрагментам.
