# Юридический ассистент ПСБ

ИИ-ассистент для юристов банка (Hack&Change 2026 × ПСБ). Отвечает **только** по выданной базе знаний организаторов (RAG). Юридические утверждения — со ссылками на фрагменты документов; внешние источники для норм не используются.

**Репозиторий:** https://github.com/SeyYestyq/PCB_HACK  
**Ветка:** `version_15_11_21.444`

Если репозиторий приватный — выдайте read-доступ аккаунту `hack-and-change-2026`.

---

## Запуск

```bash
git clone https://github.com/SeyYestyq/PCB_HACK.git
cd PCB_HACK
git checkout version_15_11_21.444
cp .env.example .env
# заполните LLM_API_KEY в .env (секреты в git не коммитятся)
docker compose up --build
```

| Что | URL |
|-----|-----|
| Чат | http://localhost:3000 |
| Health API | http://localhost:8090/health |

Презентация: `psb_legal_assistant.pdf` в корне (слайд 1 — ссылка на репо).

### Локально без полного Docker

```bash
cp .env.example .env   # LLM_*

python3 -m venv .venv && source .venv/bin/activate
pip install -r apps/answer-core/requirements.txt -r requirements.txt
export PYTHONPATH=".:apps/answer-core/src"
export PSB_KB_PATH=data/organizer/kb
uvicorn answer_core.server:app --host 127.0.0.1 --port 8090

# другой терминал
cd apps/web && npm install && npm run dev
```

Без Postgres: `PSB_VECTORS=0` (lexical/BM25).

---

## Что смотреть экспертам

Контракт: `status` + `answer` + `citations[]` (+ `missing[]` при необходимости).

| `status` | Смысл |
|----------|--------|
| `grounded` | Ответ по KB, citations непустые |
| `limited` | Частичный / неполная опора |
| `abstain` | В базе нет данных — отказ без выдуманных норм |
| `clarify` | Нужно уточнение |
| `refuse_role` | Вне роли / off-topic |

В UI: ответ и панель Evidence / подтверждения (фрагменты документов).

**Демо-вопросы:**

1. *Какая арендная плата по договору с ООО «Северный Склад»?* → `grounded`, **450 000**, citations из договора А-08-2024.  
2. *Какой размер пособия по беременности и родам?* → `abstain` (нет в KB), без фейковых citations.  
3. Off-topic (*расскажи анекдот…*) → `refuse_role`.

```bash
curl -s http://localhost:8090/health
curl -s -X POST http://localhost:8090/api/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Какая арендная плата по договору с ООО «Северный Склад»?"}'
```

---

## Автооценка (платформа)

`DATA_DIR=<каталог> python3 solution.py` → `submission.csv`.  
Submit-пакет: `solution.py` + `psb_*.py` + `requirements.txt` (`httpx` — HTTPS к прокси платформы с CA-бандлом). Локально:

```bash
DATA_DIR=data/organizer/tests PSB_KB_PATH=data/organizer/kb \
LLM_BASE_URL=https://api.deepseek.com/v1 LLM_API_KEY=... LLM_MODEL=deepseek-chat \
python3 solution.py --out submission.csv
```
