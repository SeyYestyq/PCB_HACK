# Demo ≤ 3 мин — ПСБ юридический ассистент

**Блокер:** база организаторов ещё не в репо → демо на `data/fixtures/kb.jsonl`.

## Поднять стек

```bash
cd /path/to/ПСБ
# нужен запущенный Docker Desktop / daemon
docker compose up --build
# UI:  http://localhost:3000
# API: http://localhost:8090/health
```

Compose project name зафиксирован как `psb` (кириллический путь иначе ломает имя проекта).

Локально без Docker — см. README.

## Curl-чеклист (≈ 1 мин)

```bash
# health
curl -s http://localhost:8090/health

# A4 grounded — правоспособность (должны быть citations)
curl -s -X POST http://localhost:8090/api/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Какие нормы учесть при проверке правоспособности компании для кредита?"}' | jq .

# A3/A6 abstain — историческая редакция
curl -s -X POST http://localhost:8090/api/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Какая ставка НДС была в старой редакции в 2019 году?"}' | jq .

# A7 refuse_role — off-topic
curl -s -X POST http://localhost:8090/api/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Расскажи анекдот про погоду"}' | jq .
```

Ожидание: `status` ∈ `grounded` | `abstain` | `refuse_role`; у grounded — непустой `citations[]`.

## solution.py (автооценка)

```bash
python3 solution.py "Какие нормы учесть при проверке правоспособности компании для кредита?"
```

## UI-сценарий (≈ 2 мин)

1. Открыть http://localhost:3000  
2. Задать вопрос про правоспособность → ответ + фрагменты в сайдбаре  
3. Задать off-topic / историческую редакцию → явный отказ, без выдуманных норм  

## Unit smoke

```bash
cd apps/answer-core
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest
PYTHONPATH=src pytest tests/ -q
```
