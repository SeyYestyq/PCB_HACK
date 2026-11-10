# Orchestrator Board

> Главный агент: `orchestrator`  
> Статус: **ожидает человеческое норм** (не done)  
> Обновлено: 2026-11-11 (этапы 1→5)

## Now

| ID | Задача | Worker | AC | Status |
|---|---|---|---|---|
| T0–T11 | BA → design → core → Vite → retrieval → QA | mixed | см. историю | **done** |
| T12 | Чеклист готовности к «норм» | orchestrator | `HUMAN_NORM_CHECKLIST.md` | **done** |
| T13 | Прогон 18 демо-вопросов + фиксы | backend | `reports/demo_q_scoreboard.md` | **in progress** |
| T14 | Strip markdown из answer | backend | UI/pipeline без `**` | **queued** |
| T15 | RERANKER_MODEL + MAX_WORKERS env | backend | fail-open RRF; batch workers | **queued** |
| T16 | ZIP сабмит инструкция/скрипт | orchestrator | docs + script ≤128MB | **queued** |
| T7 | Human final | human | явное «норм» | **ожидает человеческое норм** |

## Blockers

- Не объявлять проект готовым без явного «норм» / «ок» / «принимаю».
- Не коммитить / не пушить в этом цикле (делает другой агент).
- ZIP на платформу не грузить.

## Human gates

- [x] «действуй» / старт фабрики  
- [x] «давай все поэтапно с 1 по 5»  
- [ ] финальное «норм»

## Notes

### Готовность (T12)
- Чеклист: `docs/00_intake/HUMAN_NORM_CHECKLIST.md`
- Vite :3000, answer :8090, pgvector, pytest — смотреть руками перед «норм»

### Демо (T13)
- Вход: `data/organizer/tests/demo_questions.csv` vs `demo_output.csv`
- Особо: Q5 (10 млн), Q8 (п.6.2 акт), Q15–18 диалоги, Q3 abstain, Q9 Альфа-Трейдинг
