# Заглушки в репозитории

Подгружен каркас monorepo:
- `apps/web` — веб (сейчас Next.js)
- `apps/api` — API (сейчас Go + зачатки RAG/агентов)
- `docs/` — скелет strategy/product/architecture/design/engineering
- `docker-compose.yml`, `.env.example`, `AGENTS.md`

Intake ПСБ лежит отдельно и приоритетнее: `docs/00_intake/`.

Не использовать тексты/интенты старого демо (налоги, beauty, «Маша») в финальном продукте — только инфраструктурные паттерны: чат, SSE/API, docker, структура docs.