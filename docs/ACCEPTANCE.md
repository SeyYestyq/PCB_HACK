# ACCEPTANCE — ПСБ юридический ассистент

| ID | Критерий ТЗ | Проверка | Status |
|---|---|---|---|
| A1 | Поиск только по базе знаний | нет внешних источников в grounded; retrieve по `data/organizer/kb` | **pass** (organizer TXT corpus wired 2026-11-09) |
| A2 | Ответ со ссылками на положения | citations[] непустой при grounded | **pass** (unit) |
| A3 | Отказ при недостатке данных | abstain + missing | **pass** (unit) |
| A4 | Не отказываться, если ответ в базе | grounded на правоспособность | **pass** (unit) |
| A5 | Ошибка / неоднозначность вопроса | clarify | **pass** (unit) |
| A6 | Редакции / даты | abstain на historical | **pass** (unit) |
| A7 | Роль / off-topic | refuse_role | **pass** (unit) |
| A8 | Веб-чат + фрагменты | UI LegalChat + /api/v1/ask | **pass** |
| A9 | Docker one-command | `docker compose up --build` (answer+web); `name: psb` | **pass** (verified 2026-11-09) |
| A10 | solution.py / автооценка | root `solution.py` → answer-core JSON | **pass** |
| A11 | unslop UI | design pass | **pass** (LegalChat unslop 2026-11-09) |
| A12 | Human «норм» | чат «норм» | **pass** (2026-11-11) |

## Blockers

- Organizer KB подключена: `data/organizer/kb` (21 TXT). Fixtures — только unit fallback.
- Human gate «норм» закрыт (2026-11-11).

## Demo

См. [`docs/demo.md`](demo.md).
