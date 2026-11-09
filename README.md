# Юридический ассистент ПСБ

Кейс Changellenge >> Hack&Change 2026: RAG-ассистент для юристов банка с цитатами, fail-closed отказом и веб-чатом.

## Фабрика

- Главный агент: **orchestrator** — `.cursor/agents/orchestrator.md`
- Инструкция: [`FACTORY.md`](FACTORY.md)
- Intake: [`docs/00_intake/`](docs/00_intake/)
- Board: [`docs/00_intake/ORCHESTRATOR_BOARD.md`](docs/00_intake/ORCHESTRATOR_BOARD.md)

## Быстрый старт (чат)

```bash
# API (answer-core)
cd apps/answer-core
pip install -r requirements.txt
PYTHONPATH=src PSB_KB_PATH=../../data/fixtures/kb.jsonl \
  python3 -m uvicorn answer_core.server:app --reload --port 8090

# UI
cd apps/web
npm install
NEXT_PUBLIC_LEGAL_API_URL=http://localhost:8090 npm run dev
```

Открой http://localhost:3000 — чат юриста с панелью подтверждений.

Или: `docker compose up --build` (сервисы `answer` + `web`).

## solution.py (автооценка)

Единая точка входа хакатона. Тот же пайплайн, что UI (`apps/answer-core`):

```bash
python3 solution.py "Какие нормы учесть при проверке правоспособности компании для кредита?"
# JSON: status, answer, citations[], missing[]

# KB организаторов (когда появится):
PSB_KB_PATH=/path/to/kb.jsonl python3 solution.py "вопрос"
```

Пока данных кейса нет — используется `data/fixtures/kb.jsonl` (блокер на board).

## CLI answer-core

```bash
cd apps/answer-core
PYTHONPATH=src python3 -m answer_core.cli "Какие нормы учесть при проверке правоспособности компании для кредита?"
```

## Демо ≤ 3 мин

Чеклист curl + UI: [`docs/demo.md`](docs/demo.md) · критерии: [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md)

```bash
docker compose up --build   # answer :8090 + web :3000 (project name: psb)
```

> Нужен запущенный Docker daemon. KB в образе — `data/fixtures`; организаторскую базу подключать через `PSB_KB_PATH` / volume, не выдумывать.

## Структура

| Путь | Назначение |
|---|---|
| `solution.py` | Entry автооценки → answer-core |
| `apps/answer-core` | Shared retrieve → verify (Python) |
| `apps/web` | UI чат юриста + evidence |
| `apps/api` | Legacy stub API (`--profile legacy`) |
| `design/frames` | Предварительные фреймы |
| `data/fixtures` | Локальная KB до данных организаторов |
| `skills/unslop` | Дизайн-pass после UI |

Платформенные модели (регламент): DeepSeek V4.1 Flash · BGE-M3 · optional Qwen3 Reranker.
