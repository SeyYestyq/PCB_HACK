# Юридический ассистент ПСБ

Кейс Changellenge >> Hack&Change 2026: RAG-ассистент для юристов банка с цитатами, fail-closed отказом и веб-чатом.

## Фабрика

- Главный агент: **orchestrator** — `.cursor/agents/orchestrator.md`
- Инструкция: [`FACTORY.md`](FACTORY.md)
- Intake: [`docs/00_intake/`](docs/00_intake/)
- Board: [`docs/00_intake/ORCHESTRATOR_BOARD.md`](docs/00_intake/ORCHESTRATOR_BOARD.md)

## База знаний организаторов

Канонический путь: [`data/organizer/`](data/organizer/) (`kb/` — 21 TXT, `tests/` — demo Q/A, `sample/` — стартер сабмита).

```bash
export PSB_KB_PATH=data/organizer/kb   # default, если папка есть
```

Fixtures (`data/fixtures/kb.jsonl`) — только fallback для unit-тестов.

## Быстрый старт (чат)

```bash
# API (answer-core)
cd apps/answer-core
pip install -r requirements.txt
PYTHONPATH=src PSB_KB_PATH=../../data/organizer/kb \
  python3 -m uvicorn answer_core.server:app --reload --port 8090

# UI
cd apps/web
npm install
NEXT_PUBLIC_LEGAL_API_URL=http://localhost:8090 npm run dev
```

Открой http://localhost:3000 — чат юриста с панелью подтверждений.

Или: `docker compose up --build` (сервисы `answer` + `web`, KB = `/data/organizer/kb`).

## solution.py (автооценка)

Единая точка входа. Тот же пайплайн, что UI (`apps/answer-core`):

```bash
# JSON на один вопрос
python3 solution.py "Какая арендная плата по договору с ООО «Северный Склад»?"

# Batch → submission.csv (формат организаторов: id,answer)
python3 solution.py --batch --data-dir data/organizer/tests --out submission.csv
```

## CLI answer-core

```bash
cd apps/answer-core
PYTHONPATH=src python3 -m answer_core.cli "Какой максимальный срок испытания можно установить главному бухгалтеру?"
```

## Демо ≤ 3 мин

Чеклист curl + UI: [`docs/demo.md`](docs/demo.md) · критерии: [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md)

```bash
docker compose up --build   # answer :8090 + web :3000 (project name: psb)
```

## Структура

| Путь | Назначение |
|---|---|
| `solution.py` | Entry автооценки → answer-core (JSON / batch CSV) |
| `apps/answer-core` | Shared retrieve → verify (Python) |
| `apps/web` | UI чат юриста + evidence |
| `data/organizer` | KB + demo Q/A + sample submission организаторов |
| `data/fixtures` | Fallback fixture KB для unit-тестов |
| `skills/unslop` | Дизайн-pass после UI |

Платформенные модели (регламент): DeepSeek V4.1 Flash · BGE-M3 · optional Qwen3 Reranker.
Не скрейпить Гарант — только пакет организаторов.
