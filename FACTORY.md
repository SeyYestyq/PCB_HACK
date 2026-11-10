# Factory — Юридический ассистент ПСБ

Инструкция автоматической сборки. Главный агент: **orchestrator** (`.cursor/agents/orchestrator.md`).

## Вход

ТЗ: `docs/00_intake/ПСБ_кейс.pdf`  
Человек даёт ТЗ / «го» / финальное «норм». Остальное ведёт Orchestrator.

## Этапы

| # | Этап | Worker | Артефакт | Блокер дальше |
|---|---|---|---|---|
| 1 | BA + аналоги | `ba` | `docs/00_intake/BA_BRIEF.md`, `ANALOGS.md` | да |
| 2 | Design / UI direction | `design` | характер чата + unslop | до polish UI |
| 3 | Backend / RAG / verify | `backend` | `apps/answer-core`, API, `solution.py` stub | — |
| 4 | Frontend chat | `frontend` | `apps/web` (Vite) чат+evidence | UI для допуска |
| 5 | Unslop | `design` | UI без AI-slop | перед демо |
| 6 | QA | `qa` | `docs/ACCEPTANCE.md` | 3 фейла → человек |
| 7 | Human | — | «норм» | **конец** |

## Стек (locked для этого кейса)

- **Answer core / submit:** Python (`apps/answer-core`, позже `solution.py`)
- **API demo:** можно держать/адаптировать `apps/api` (Go) как BFF к core **или** FastAPI-обёртку — решение Orchestrator фиксирует в `DECISIONS.md`
- **Web:** `apps/web` (Next stubs → переписать под юриста)
- **DB:** Postgres + pgvector
- **Models (platform):** DeepSeek V4.1 Flash, BAAI/bge-m3, optional Qwen3 Reranker 8B

## Правила

- Аналоги изучать, не копировать; превосходить слабости.
- Прошлые хакатоны — тихое вдохновение, без путей в продукте.
- pgvector — для поиска по документам текущего кейса.
- Один shared answer path для автооценки и UI.
- Board: `docs/00_intake/ORCHESTRATOR_BOARD.md`
