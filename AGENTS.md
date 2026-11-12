# AGENTS.md — Юридический ассистент ПСБ

> Hack&Change 2026 × ПСБ. Этот файл — закон для любого агента в репо.

## Главный агент

**Orchestrator** — `.cursor/agents/orchestrator.md` (копия в `agents/orchestrator.md`).  
Он планирует, режет задачи, проверяет AC. Workers: `ba`, `design`, `backend`, `frontend`, `qa`.

Пайплайн и DoD: **`FACTORY.md`**. Intake: **`docs/00_intake/`**.

## Продукт

ИИ-ассистент для юристов банка: RAG **только** по выданной базе знаний, ответы со ссылками на положения, обоснованный отказ, веб-чат с просмотром фрагментов. Без внешних источников для юр. утверждений.

## Стек

| Слой | Технология |
|------|------------|
| Answer core / `solution.py` | Python |
| Web UI | `apps/web` (Next stubs → UI юриста) |
| API / BFF | `apps/api` и/или FastAPI к core |
| DB | Postgres + **pgvector** |
| Platform LLM | DeepSeek V4.1 Flash |
| Embeddings | BAAI/bge-m3 |
| Rerank (opt.) | Qwen3 Reranker 8B |

## Контракт ответа

`status`: `grounded` | `limited` | `abstain` | `clarify` | `refuse_role`  
+ `answer`, `citations[]`, `missing[]`  
Юр. утверждения только с citations из retrieved.

## Порядок работы

1. Читать `FACTORY.md` + `docs/00_intake/BA_BRIEF.md`.
2. Не писать UI/код до готового BA (уже есть) и актуального board.
3. После UI — **unslop** (`skills/unslop/SKILL.md`).
4. Отчёты анализа — в `../рабочие файлы псб/reports/` или `docs/00_intake/`, не только в чат.
5. Финал проекта — только после человеческого «норм».

## Запреты

- Галлюцинации норм / документов  
- Секреты в git  
- Копипаст аналогов и чужих продуктов под видом своего  
- Указывать в UI/README пути к старым личным проектам  

## Skills

| Skill | Когда |
|---|---|
| `skills/unslop` | После UI / перед демо |
| `docs/design/09-unslop.md` | Как гоняем unslop здесь |
