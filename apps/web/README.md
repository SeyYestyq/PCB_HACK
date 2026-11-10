# Веб-чат юриста

Vite, React и TypeScript. На экране один чат: вопрос по базе знаний, ответ и фрагменты документов. Клиент не выводит нормы сам и только показывает поля ответа API.

Браузер всегда отправляет `POST /api/v1/ask` на тот же адрес, с которого открыт чат.

## Локально

Сначала поднимите API на `http://127.0.0.1:8090`.

```bash
cd apps/web
npm install
npm run dev
```

Чат: http://localhost:3000

Vite проксирует `/api` на `http://127.0.0.1:8090`. Отдельный URL API через переменные окружения не задаётся.

```bash
npm run build
npm run preview
```

`build` проверяет типы и кладёт статику в `dist/`. `preview` отдаёт её на порту 3000 и проксирует `/api` туда же.

## Docker

Образ собирает фронт на `node:22-alpine`, затем `nginx:alpine` раздаёт `dist` на порту 3000. Запросы `/api/` nginx отправляет на `http://answer:8090/api/`.

Из корня репозитория:

```bash
docker compose build web
docker compose up web
```

У сервиса `web` в `compose.yaml` нет аргументов сборки и нет `NEXT_PUBLIC_*` / `API_UPSTREAM`. Проброс порта: `3000:3000`.

## Скрипты

| Скрипт | Команда |
|---|---|
| `dev` | `vite --port 3000` |
| `build` | `tsc --noEmit && vite build` |
| `preview` | `vite preview --port 3000` |
| `test:e2e` | Playwright, `e2e/legal.spec.ts` |

## Файлы

- `src/components/LegalChat.tsx` — лента, поле вопроса, панель подтверждений
- `src/lib/legal-api.ts` — запрос `POST /api/v1/ask`
- `src/lib/brand.ts` — название и короткая оговорка
- `src/index.css` — стили чата, IBM Plex Sans и Source Serif 4
