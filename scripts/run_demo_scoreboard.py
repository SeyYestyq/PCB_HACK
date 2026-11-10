#!/usr/bin/env python3
"""Run demo_questions.csv through answer_question and write reports/demo_q_scoreboard.md."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from psb_ingest import default_kb_path  # noqa: E402
from psb_pipeline import answer_question  # noqa: E402
from psb_textnorm import normalize  # noqa: E402

Q_PATH = ROOT / "data" / "organizer" / "tests" / "demo_questions.csv"
GOLD_PATH = ROOT / "data" / "organizer" / "tests" / "demo_output.csv"
OUT_PATH = ROOT / "reports" / "demo_q_scoreboard.md"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def soft_check(qid: str, status: str, answer: str, citations: list) -> tuple[bool, str]:
    a = normalize(answer)
    n_cit = len(citations or [])
    checks: dict[str, tuple[bool, str]] = {
        "1": (
            ("450" in a or "450 000" in answer) and "аренд" in a,
            "аренда 450 000",
        ),
        "2": ("шест" in a or "6 месяц" in a or "шести месяц" in a, "испытание ≤ 6 мес"),
        "3": (status == "abstain" and n_cit == 0, "abstain без citations"),
        "4": (
            ("450" in a or "450 000" in answer)
            and "500 000" not in answer.replace("не 500", ""),
            "аренда 450 000 (не утверждать 500 000)",
        ),
        "5": (
            ("10 000 000" in answer or "десяти миллион" in a)
            and "15 000 000" not in answer
            and "пятнадцат" not in a,
            "август 2024 → 10 млн, не 15",
        ),
        "6": ("5" in a and ("рабоч" in a or "качеств" in a), "5 раб. дней качество"),
        "7": ("круглосуточ" in a or "беспрепятствен" in a or "4.3" in a, "доступ 24/7"),
        "8": ("акт" in a and ("недостат" in a or "6.2" in a or "претенз" in a), "акт / п.6.2"),
        "9": (
            status != "clarify"
            and ("предоплат" in a or "аванс" in a or "45" in a)
            and ("трейдинг" in a or "пт-05" in a or "пт−05" in a),
            "Альфа-Трейдинг / предоплата, не clarify",
        ),
        "10": ("руководитель" in a or "инициатор" in a, "инициатор = руководитель"),
        "11": ("трёх" in a or "трех" in a or "3" in a, "архив ≤ 3 дня"),
        "12": ("испытан" in a and ("распространя" in a or "трудов" in a), "испытание = ТК"),
        "13": ("соглас" in a and ("152" in a or "персональн" in a), "отзыв согласия 152-ФЗ"),
        "14": ("срочн" in a or "сезон" in a or "59" in a, "сезонный срочный ТД"),
        "15": ("акт" in a and ("а-08" in a or "северн" in a or "помещен" in a), "А-08 акт возврата"),
        "16": (
            ("включа" in a or "упаков" in a or "доставк" in a)
            and ("п-17" in a or "альфа-трейд" in a),
            "П-17 упаковка/доставка в цене",
        ),
        "17": (
            ("талон" in a or "производител" in a or "не установлен" in a)
            and ("трейдинг" in a or "пт-05" in a),
            "ПТ-05 гарантия по талону",
        ),
        "18": (
            ("трёх" in a or "трех" in a or "3" in a)
            and ("юридическ" in a or "юротдел" in a or "регламент" in a),
            "оригинал в юротдел за 3 дня",
        ),
    }
    ok, note = checks.get(qid, (True, "no hard check"))
    return ok, note


def main() -> int:
    questions = load_csv(Q_PATH)
    gold = {row["id"]: row["answer"] for row in load_csv(GOLD_PATH)}
    kb = default_kb_path()
    rows: list[str] = []
    passed = 0
    for row in questions:
        qid = row["id"].strip()
        question = row["question"]
        result = answer_question(question, kb)
        ok, note = soft_check(qid, result.status, result.answer, result.citations)
        passed += int(ok)
        mark = "PASS" if ok else "FAIL"
        snippet = result.answer.replace("\n", " ")[:220]
        rows.append(
            f"| {qid} | {mark} | `{result.status}` | {len(result.citations)} | {note} | {snippet} |"
        )
        print(f"{qid}: {mark} ({result.status}) {note}", flush=True)

    total = len(questions)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# Demo questions scoreboard",
            "",
            f"Источник: `{Q_PATH.relative_to(ROOT)}` vs `{GOLD_PATH.relative_to(ROOT)}`.",
            f"Прогон: `answer_question` / KB `{kb}`.",
            f"Итог: **{passed}/{total}** soft-pass (не exact match к golden).",
            "",
            "Особые AC: Q5=10 млн не 15; Q8=акт/6.2; Q15–18 диалоги; Q3=abstain без citations; Q9≠clarify.",
            "",
            "| Q | Result | status | citations | check | answer snippet |",
            "|---|---|---|---|---|---|",
            *rows,
            "",
            "## Notes",
            "",
            "- Soft checks по ключевым фактам golden; ответы не хардкодятся под id.",
            "- Markdown (`**`) снимается в pipeline (`strip_markdown`).",
            "",
        ]
    )
    OUT_PATH.write_text(body, encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({passed}/{total})", flush=True)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
