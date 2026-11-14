# Handoff наставнику: как мы били Score и что делать дальше

**Кому:** наставник / тимлид по метрике судьи  
**От:** команда ПСБ (Hack&Change 2026)  
**Дата:** 2026-11-14  
**Цель этого документа:** дать полную картину экспериментов и поставить задачу — **разработать новую стратегию, чтобы platform Score > 19.452**.

---

## 1. Задача продукта (коротко)

ИИ-ассистент юриста банка: RAG **только** по KB организатора, ответы со ссылками, статусы  
`grounded | limited | abstain | clarify | refuse_role`. Без внешних норм.

**Онлайн-этап ≈ 70% LLM-судья + 30% эксперты.**

Судья (авто):

\[
\text{Score} = 0.7 \cdot \text{MatchRate} + 0.3 \cdot \text{WinRate}
\]

- Выдуманный факт по вопросу → **0** за вопрос.  
- Pairwise vs baseline относительно golden (2 раунда).  
- ZIP ≤ 128 MB: `solution.py` + `requirements.txt` + `psb_*.py`.  
- Заливка только человеком: https://changellenge.com/personal/championships/stage/932581/  
- Агент/бот **не** логинится и не грузит с паролем.

**North star = platform Score, не local demo 18/18.** Local soft-pass стабильно врёт относительно сайта.

---

## 2. Где лежит код и эталон

| Что | Путь |
|---|---|
| Workspace | `/Users/damir/Documents/хакатоны/ПСБ` |
| Рабочие отчёты | `/Users/damir/Documents/хакатоны/рабочие файлы псб/reports/` |
| Лучший platform ZIP | `artifacts/psb_submission_score_19.zip` = `dist/psb_submission_best.zip` |
| **Лучший Score** | **19.452** @ ~11:25 |
| md5 эталона | `38c9e34c4191ee5c73ec01f744f17023` (40503 bytes) |
| Ветка freeze | `version_12_11_19.452` (внимание: **git tip ≠ etalon ZIP**; истина эталона = ZIP) |
| Паковка | `./scripts/pack_submission_zip.sh "$(pwd)/dist/psb_submission.zip"` |
| Local smoke | `PSB_VECTORS=0 PYTHONPATH=".:apps/answer-core/src" apps/answer-core/.venv/bin/python scripts/local_judge_runs.py --runs 5` |

**Правило freeze:** пока Score < 19.452 — откат на `38c9e34…`, best ZIP не затираем.

---

## 3. Стек answer-core (что внутри ZIP)

```
question → parse dialog → refuse/clarify
  → edition filter → catalog scope → retrieve (BM25 ± dense RRF)
  → top-5 → order → citations[:3]
  → LLM(citations[:2]) → trim(~560) → number-verify
      → cite_named? иначе merge «Источник: title» → иначе LEX dump
  → used citations → status grounded|limited|abstain
  → (etalon) optional append про «действующую редакцию на текущую дату»
```

LLM: DeepSeek V4.1 Flash (platform). Embeddings: BGE-M3 (на платформе; локально часто `PSB_VECTORS=0`).

UI отдельно: `apps/web` (Vite) — на автобалл ZIP не влияет, но на **30% экспертов** влияет.

---

## 4. Журнал экспериментов на платформе (хронология)

| Время (прибл.) | Что меняли | Score | Вердикт |
|---|---|---:|---|
| 11:25 | **Etalon / baseline freeze** | **19.452** | **BEST — держать** |
| 11:39 | soft-cite (post-hoc подгонка citations) | 16.482 | CLOSED |
| 11:49 | промежуточный climb | 17.333 | CLOSED |
| 12:45 | hedge-strip + number-peek | 18.285 | CLOSED |
| 23:20 | PDN Q13 + law-slug + guard 11152 (**пакет**) | **13.472** | WORST; CLOSED |
| 23:58 | H1: только PDN prompt + 11152 | 15.268 | CLOSED (PDN больше не трогать) |
| 02:20 | H3: убрать forced edition-suffix | 14.732 | CLOSED |
| 11:05 | H5: `DD.MM` из даты ≠ claim-number | 18.381 | CLOSED как *одиночный* сабмит; идея жива как база |
| — | **H5+H4** (date-skip + soft `_cite_named_in`) | **ещё не на платформе** | Climb ZIP готов: md5 `3774b1ff6124f751caf0e9ca86d14a20` |

### Локально закрыто без заливки

| Код | Идея | Итог |
|---|---|---|
| H2 | `llm_citations = [:1]` вместо `[:2]` | 14–15/18 local (Q5/12/14 → limited) — не лить |

---

## 5. Чему научила платформа (обязательные выводы)

1. **Local 18/18 ≠ Score.** Несколько раз local green → на сайте −1…−6.  
2. **Одна переменная на сабмит.** Пакеты (PDN+law-slug+11152, hedge+peek) стабильно хуже.  
3. **«Честность» и укорочение вредят** сильнее, чем кажутся полезными (PDN honesty, drop edition-suffix).  
4. **Post-hoc citation repair (soft-cite) запрещён** — бьёт Match/Win.  
5. **H5 один дал 18.381** — ближе к эталону, чем PDN/H3; чинит реальный баг Q5, но **один** не обогнал 19.452.  
6. Истина эталона = **байты ZIP**, не обязательно `git HEAD` (в истории ветки ещё старые soft-cite/hedge).

### Закрытые рычаги (не повторять как есть)

PDN-prompt · soft-cite · hedge-strip · number-peek · law-slug · llm_top1 · edition-suffix-drop · H5-alone (как единственный сабмит без доп. рычага — спорно; стек H5+X допустим как новая гипотеза).

---

## 6. Аудит эталона (где теряем относительно demo golden)

Полный разбор: `complex_audit_etalon_2026-11-14.md`, gaps: `artifacts/audit_etalon_gap.json`.

| Симптом | Суть |
|---|---|
| **Q5 → LEX** | LLM пишет хороший ответ, но `_cite_named_in` не матчит `ред. 2023` vs `ред 2023 (утратил силу)`; merge → из `01.03.2025` парсится фейк-claim `01.03` → number-verify fail → lexical dump (ovlp ~0.25) |
| **Q13 ovlp ~0.12** | Overclaim ст.6/10/11 из текста ст.9; PDN-prompt на платформе **убил** Score |
| **Q10 ~2.4× длиннее gold** | Факт верный; WinRate-риск verbosity; слепое укорочение (H3) → 14.732 |
| Q4/6/12 | Слабый lexical overlap к golden (proxy, не Score) |

**H5** чинит date→claim. **H4** чинит cite_named (это *не* soft-cite: не подменяем чужие citations, а узнаём то же имя документа). Вместе упакованы в climb `3774b1…` — ждут решения человека по заливке.

---

## 7. Текущее состояние репо (на момент handoff)

- Best / rollback: `38c9e34…` → **19.452**  
- WT + `dist/psb_submission.zip`: **H5+H4** (`3774b1…`), platform score **unknown**  
- Если H5+H4 < 19.452 → сразу откат на etalon, гипотеза «стек H5+H4» закрывается  
- Экспертный UI в целом есть (`apps/web`: AnswerCard, EvidenceRail, статусы); перед демо — unslop + README-схема пайплайна

---

## 8. ЗАДАЧА НАСТАВНИКУ

### Постановка

Разработать **новую стратегию роста platform Score выше 19.452** (и желательно выше любого следующего climb), опираясь на:

- формулу Match/Win и штраф invent→0;  
- журнал провалов выше;  
- аудит Q5/Q10/Q13;  
- статьи/идеи: `articles_for_score_climb_2026-11-14.md` (MT-Bench verbosity, RAGAS faithfulness, attribution ≠ soft-cite).

### Что сдать на выходе

1. **Диагноз:** почему 19.452 «застрял» — Match vs Win, какие классы вопросов на private, скорее всего, режут балл (гипотезы, не гадание).  
2. **Стратегия на 3–7 сабмитов:** очередь **однофакторных** A/B с kill-criteria и rollback на `38c9e34…`.  
3. **Явный список «не делать»** (расширить закрытые рычаги).  
4. **Offline-метрика**, которая лучше коррелирует с сайтом, чем demo 18/18 (например claim-faithfulness vs quotes + pairwise vs golden; длина как Win-proxy).  
5. **Параллельный план экспертов 30%** (UI/README/финальный пакет) — без сжигания judge-слотов.  
6. Рекомендация: **лить ли сейчас H5+H4** (`3774b1…`) или сначала другая гипотеза.

### Ограничения

- Не предлагать пакет из 3+ рычагов в один ZIP без offline A/B.  
- Не предлагать повтор PDN / soft-cite / hedge-strip / number-peek / edition-drop «как было».  
- Не считать победой local 18/18.  
- Секреты/логин Changellenge — только человек.

### Полезные файлы

| Файл | Зачем |
|---|---|
| `artifacts/ETALON.txt` | freeze + failed climbs |
| `reports/score_max_strategy.md` | стратегия max балла |
| `reports/claude_skills_metric_plan.md` | A/B / eval pitfalls |
| `reports/rlm_for_psb_judge.md` | RLM-light идеи |
| `reports/complex_audit_etalon_2026-11-14.md` | разбор etalon |
| `reports/h5_date_claim_2026-11-14.md` | H5 |
| `reports/articles_for_score_climb_2026-11-14.md` | литература |
| `artifacts/local_judge_runs_*.jsonl` | local прогоны |
| `AGENTS.md`, `FACTORY.md` | процесс репо |

---

## 9. Одной фразой

Мы заморозили **19.452**; все попытки «починить» Match/Win поверх эталона пока **ниже**; самый близкий провал — **H5=18.381**; следующий кандидат в очереди — **H5+H4**; нужна **новая стратегия**, которая бьёт 19.452, не повторяя закрытые рычаги и не доверяя local 18/18.
