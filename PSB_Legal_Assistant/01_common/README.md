# Общая часть (все роли)

Здесь лежат материалы, которые нужны каждой роли: официальный кейс, сквозное ТЗ, архитектура, контракт API, обзор ролей, передачи, источники, обоснования решений и список дефектов D1-D28 (`docs/05-rag/01-rag-deep-dive.md`, §7).

## Что читать и в каком порядке

1. `official_case/PSB_case.pdf` (или `.txt`) - источник истины по условиям.
2. `docs/01-product/01-problem-and-audience.md` - задача и аудитория.
3. `docs/01-product/02-tz-complete.md`, разделы 1-3, затем 3-6 по мере работы.
4. `docs/02-architecture/01-system-architecture.md` - ограничения и API.
5. `docs/01-product/03-tz-roles-3-people.md` - кто за что отвечает.
6. `docs/01-product/07-handoffs-and-interfaces.md` - передачи H-01..H-12 и RACI.
7. `docs/06-nodes/00-overview.md` и `docs/06-nodes/07-api-contract-and-submission.md` - узлы и контракт сабмита.
8. `docs/05-rag/01-rag-deep-dive.md` §7 - дефекты D1-D28, с чего начинать (D2, D3, D4, затем D22).
9. `docs/99-sources.md` - когда нужна ссылка на регламент или источник.
10. По необходимости: ADR в `docs/02-architecture/02-stack-and-decisions.md`, модель базы в `03-data-model-and-kb.md`, безопасность в `04-security.md`, аналоги в `docs/03-analogs/`, обоснования BJ-* в `docs/04-brand/07-decision-justifications.md`.

## Что здесь общее, а что нет

Эта папка никому не «принадлежит» целиком. Менять контракт API, статусы ответа и правила редакций можно только по протоколу из `07-handoffs-and-interfaces.md`. Список дефектов ведёт роль 1 в согласовании с ролью 3 (eval).

Дальше расходитесь по своим папкам: `03_backend_rag/`, `02_frontend/`, `04_kb_eval/`. Полный каталог тестов и ревью: `05_review_and_tests/`.
