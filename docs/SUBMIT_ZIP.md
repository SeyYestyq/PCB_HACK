# Сборка ZIP для автооценки

## Что класть

| Включить | Не включать |
|---|---|
| `solution.py` | `.env` / ключи |
| `psb_*.py` | `vendor/`, `node_modules/`, `apps/` |
| `requirements.txt` (stdlib-only) | KB, CSV вопросов, Docker, видео |
| — | `__pycache__`, `.git`, `dist/` кроме готового ZIP |

Лимит: **≤ 128 MB**. Базу и вопросы подставляет платформа в `DATA_DIR`.

## Команда

```bash
./scripts/pack_submission_zip.sh
# или явно:
./scripts/pack_submission_zip.sh /tmp/psb_submission.zip
```

Скрипт копирует только нужные файлы, пакует `zip -9`, проверяет размер. **На платформу не загружает** — загрузка вручную.

## Локальная проверка batch

```bash
DATA_DIR=data/organizer/tests PSB_KB_PATH=data/organizer/kb \
  MAX_WORKERS=2 python3 solution.py --out /tmp/submission.csv
```

Демо-скорборд: `python3 scripts/run_demo_scoreboard.py` (по умолчанию пишет в `reports/`; каталог можно держать в `../рабочие файлы псб/reports/`).
