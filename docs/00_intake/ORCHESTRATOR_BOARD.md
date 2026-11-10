# Orchestrator Board

> Главный агент: `orchestrator`  
> Статус: **принят человеком** («норм», 2026-11-11)  
> Обновлено: 2026-11-11 (финал зафиксирован)

## Now

| ID | Задача | Worker | AC | Status |
|---|---|---|---|---|
| T0–T11 | BA → design → core → Vite → retrieval → QA | mixed | см. историю | **done** |
| T12 | Чеклист готовности к «норм» | orchestrator | `HUMAN_NORM_CHECKLIST.md` | **done** |
| T13 | Прогон 18 демо-вопросов + фиксы | orchestrator/backend | `reports/demo_q_scoreboard.md` 18/18 | **done** |
| T14 | Strip markdown из answer | orchestrator | `strip_markdown` в pipeline/submission | **done** |
| T15 | RERANKER_MODEL + MAX_WORKERS env | orchestrator | fail-open `/rerank`; batch workers | **done** |
| T16 | ZIP сабмит инструкция/скрипт | orchestrator | `scripts/pack_submission_zip.sh` + docs | **done** |
| T7 | Human final | human | явное «норм» | **done** (принято человеком, 2026-11-11) |

## Blockers

- ZIP на платформу не грузить без человека (отдельный шаг сабмита).

## Human gates

- [x] «действуй» / старт фабрики  
- [x] «давай все поэтапно с 1 по 5»  
- [x] финальное «норм» (2026-11-11)

## Notes

### 1 — Готовность
- `docs/00_intake/HUMAN_NORM_CHECKLIST.md`
- Board: **принят человеком**; T7 / финал — **done**

### 2 — Демо 18/18
- Soft scoreboard: `reports/demo_q_scoreboard.md`
- Q5=10 млн; Q8=акт; Q3=abstain; Q9≠clarify; Q15–18 диалоги

### 3 — Markdown
- `psb_textnorm.strip_markdown` + `Answer.__post_init__` + submission clip + LLM prompt

### 4 — Env
- `RERANKER_MODEL` → `{LLM_BASE_URL}/rerank`, fail-open RRF
- `MAX_WORKERS` в `psb_submission.py`
- root `requirements.txt` без psycopg/fastembed

### 5 — ZIP
- `./scripts/pack_submission_zip.sh` → `dist/psb_submission.zip`
- `docs/SUBMIT_ZIP.md` + README
