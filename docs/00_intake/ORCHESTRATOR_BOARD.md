# Orchestrator Board

> Главный агент: `orchestrator`  
> Статус: **ACTIVE** — ждём human «норм»  
> Обновлено: 2026-11-10 (Vite done + retrieval fixes green)

## Now

| ID | Задача | Worker | AC | Status |
|---|---|---|---|---|
| T0–T6b | BA → design → core → UI → acceptance | mixed | см. историю | **done** |
| T8 | Next.js → Vite+React+TS | frontend/orchestrator | LegalChat + nginx :3000 | **done** |
| T9 | Retrieval/pipeline bugs | backend/orchestrator | gate, editions, scope, status | **done** (29 pytest) |
| T10 | Unslop after Vite | orchestrator | light checklist, no BizStart | **done** (light pass) |
| T11 | QA verify | orchestrator | pytest + browser + docker build web | **done** |
| T7 | Human final | human | «норм» | **next** |

## Blockers

- Не объявлять проект готовым без явного «норм».
- Не коммитить в этом цикле (по запросу).
- Живой контейнер `answer` лучше перезапустить, чтобы подтянуть свежие `psb_*.py` с volume.

## Human gates

- [x] «действуй» / старт фабрики  
- [ ] финальное «норм»

## Notes

### Vite (`apps/web`)
- Стек: Vite 6 + React 19 + TS; `npm run dev` → :3000, proxy `/api` → `127.0.0.1:8090`
- Клиент: относительный `POST /api/v1/ask`
- Docker: `node:22-alpine` build → `nginx:alpine` + `dist`, `/api/` → `answer:8090`, host `3000:3000`
- Удалены Next/Tailwind/BizStart (`app/*`, genui, CashbackWheel, masha e2e)
- Оставлен `e2e/legal.spec.ts`

### Retrieval
- Support gate: adaptive `idf_cut` (3.0 если n≥40, иначе 0.05) + стоп-слова; rent/probation/august не пустые
- Edition: август 2024 → регламент 2023 / 10 млн; без даты → только текущая ред.
- Catalog: роли/Меридиан не перехватывают № договора; Альфа-Трейд ≠ Трейдинг; dialog Q15/Q16/Q18
- Status: abstain без citations; «не хватает» → limited
- Root `requirements.txt` без psycopg/fastembed
