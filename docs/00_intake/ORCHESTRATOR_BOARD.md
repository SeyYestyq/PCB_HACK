# Orchestrator Board

> Главный агент: `orchestrator`  
> Статус: **post-norm hardening** (человек: «действуй» — дожать + push)  
> Обновлено: 2026-11-11 (RAG verify / dense / general KB)

## Now

| ID | Задача | Worker | AC | Status |
|---|---|---|---|---|
| T17 | LLM number-verify (числа ⊆ quotes) | orchestrator | тесты + fallback lexical | **done** |
| T18 | Multi-query / expansion fail-safe | orchestrator | без demo-hardcode; общий KB | **done** |
| T19 | Dense vectors+RRF smoke `PSB_VECTORS=1` | orchestrator | Docker ask :8090/:3000 | **done** |
| T20 | Generality: `PSB_KB_PATH`, no counterparty topic_boost | orchestrator | grep/AC | **done** |
| T21 | Golden lexical pytest + `reports/rag_hillclimb.md` | orchestrator | 49 passed | **done** |
| T22 | Commit + push `origin/main` | orchestrator | no .env/secrets/force | **doing** |

## Done (prior)

| ID | Задача | Status |
|---|---|---|
| T0–T16 | BA→design→core→QA→norm | **done** |
| T7 | Human «норм» | **done** |

## Blockers

- ZIP на платформу не грузить без человека.

## Human gates

- [x] «действуй» / старт фабрики  
- [x] финальное «норм» (2026-11-11)  
- [x] «действуй» post-norm: strengthen RAG + push

## Notes

- Allowlist: root `requirements.txt` без psycopg/fastembed.
- Референс идей: `reports/rag_lessons_from_110726.md` (не копипаст).
