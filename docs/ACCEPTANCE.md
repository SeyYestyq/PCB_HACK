# ACCEPTANCE — ПСБ юридический ассистент

| ID | Критерий ТЗ | Проверка | Status |
|---|---|---|---|
| A1 | Поиск только по базе знаний | нет внешних источников в grounded; retrieve по fixture/KB | **pass** (fixture; organizer KB blocker) |
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
| A12 | Human «норм» | — | **open** |

## Blockers

- База знаний организаторов не в репо → `data/fixtures/kb.jsonl`. Подключить через `PSB_KB_PATH` / volume без выдумывания корпуса.

## Demo

См. [`docs/demo.md`](demo.md).
