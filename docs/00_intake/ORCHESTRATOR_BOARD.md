# Orchestrator Board

> Главный агент: `orchestrator`  
> Статус: **ACTIVE** — ждём human «норм»  
> Обновлено: 2026-11-09 (organizer KB integrated)

## Now

| ID | Задача | Worker | AC | Status |
|---|---|---|---|---|
| T0 | BA intake | ba | BA_BRIEF + ANALOGS | **done** |
| T1 | Назначить orchestrator + FACTORY | orchestrator | agents + FACTORY.md | **done** |
| T2 | Фреймы чата юриста | design | 3 HTML frames | **done** |
| T3 | Answer-core stub (retrieve→verify) | backend | Python package + fixture answer | **done** |
| T4 | UI чат + answer API | frontend/backend | LegalChat + /api/v1/ask | **done** |
| T5 | unslop UI | design | audit+passes | **done** |
| T5b | `solution.py` stub (shared core) | backend/orchestrator | root entry → JSON contract | **done** |
| T6 | ACCEPTANCE + demo + compose | qa/orchestrator | checklist + docs/demo.md | **done** (unit+compose green; human gate open) |
| T6b | Organizer KB → `data/organizer/` + wire PSB_KB_PATH | backend | txt loader + smoke asks | **done** |
| T7 | Human final | human | «норм» | **next** |

## Blockers

- Organizer KB в репо: `data/organizer/kb` (default over fixtures).
- Не объявлять проект готовым без явного «норм».

## Human gates

- [x] «действуй» / старт фабрики  
- [ ] финальное «норм»

## Notes (T5b / T6)

- `solution.py` → `answer_core.pipeline.answer_question` (тот же путь, что `/api/v1/ask`).
- Unit: grounded / abstain / refuse_role / clarify в `apps/answer-core/tests/`.
- Demo script: `docs/demo.md`.
- Compose: сервисы `answer` + `web` (default profile).
