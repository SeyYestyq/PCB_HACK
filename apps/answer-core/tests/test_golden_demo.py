"""Hard golden oracles for organizer demo Q1–Q18 (facts/status, not full answer text).

Run lexical-only (default in CI/local without LLM):
  PSB_VECTORS=0 PYTHONPATH=.:apps/answer-core/src pytest apps/answer-core/tests/test_golden_demo.py -q

Oracles derived from data/organizer/tests/demo_output.csv — check mandatory
numbers, clause markers, doc markers, and status. Full model prose is not asserted.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

import pytest

from answer_core.pipeline import answer_question
from psb_textnorm import normalize

ROOT = Path(__file__).resolve().parents[3]
ORGANIZER = ROOT / "data" / "organizer" / "kb"
Q_PATH = ROOT / "data" / "organizer" / "tests" / "demo_questions.csv"
GOLD_PATH = ROOT / "data" / "organizer" / "tests" / "demo_output.csv"


def _organizer_ready() -> bool:
    return ORGANIZER.is_dir() and any(ORGANIZER.glob("*.txt"))


def _load_questions() -> dict[str, str]:
    with Q_PATH.open(encoding="utf-8-sig", newline="") as f:
        return {row["id"].strip(): row["question"] for row in csv.DictReader(f)}


@dataclass(frozen=True)
class Oracle:
    status: str | None = None  # exact status if set
    status_not: tuple[str, ...] = ()
    answer_any: tuple[str, ...] = ()  # at least one must appear (normalized substr)
    answer_all: tuple[str, ...] = ()
    answer_none: tuple[str, ...] = ()
    cite_any: tuple[str, ...] = ()  # titles+quotes+spans joined
    cite_all: tuple[str, ...] = ()
    min_citations: int | None = None
    max_citations: int | None = None
    note: str = ""


# Critical facts per Q — aligned with demo_output.csv soft checks + clause markers.
ORACLES: dict[str, Oracle] = {
    "1": Oracle(
        status="grounded",
        min_citations=1,
        answer_all=("450", "аренд"),
        cite_any=("450", "3.1", "3.2"),
        note="аренда 450 000 + срок внесения",
    ),
    "2": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("шест", "6 месяц", "шести месяц"),
        cite_any=("70", "испытан"),
        note="испытание бухгалтера ≤ 6 мес (ТК 70)",
    ),
    "3": Oracle(
        status="abstain",
        max_citations=0,
        min_citations=0,
        note="пособие по беременности — нет в KB",
    ),
    "4": Oracle(
        status="grounded",
        min_citations=1,
        answer_all=("450",),
        answer_none=("составляет 500 000", "плата 500 000"),
        cite_any=("450", "3.1"),
        note="premise correction: 450 не 500",
    ),
    "5": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("10 000 000", "десяти миллион", "10 млн"),
        answer_none=("порог — 15 000 000", "порог 15"),
        cite_any=("10 000 000", "десяти миллион", "2023"),
        note="август 2024 → редакция 2023, порог 10 млн",
    ),
    "6": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("5", "пяти"),
        answer_all=("рабоч",),
        cite_any=("6.1", "качеств", "5 (пяти) рабочих"),
        note="dialog: приёмка по качеству 5 раб. дней",
    ),
    "7": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("круглосуточ", "беспрепятствен", "4.3"),
        cite_any=("круглосуточ", "4.3", "беспрепятствен"),
        note="доступ 24/7 п. 4.3",
    ),
    "8": Oracle(
        status="grounded",
        min_citations=1,
        answer_all=("акт",),
        answer_any=("недостат", "6.2", "претенз"),
        cite_any=("акт о выявлен", "6.2", "недостат"),
        note="к претензии — акт о недостатках п. 6.2",
    ),
    "9": Oracle(
        status_not=("clarify",),
        min_citations=1,
        answer_any=("предоплат", "аванс", "45"),
        cite_any=("трейдинг", "пт-05", "пт−05", "предоплат", "4.2", "4.1"),
        note="Альфа-Трейдинг / предоплата, не clarify",
    ),
    "10": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("руководитель", "инициатор"),
        cite_any=("регламент", "2025", "руководитель"),
        note="инициатор = руководитель подразделения",
    ),
    "11": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("трёх", "трех", "3 (трёх)", "3 (трех)", "не более трёх", "не более трех"),
        cite_any=("трёх", "трех", "3 (трёх)", "3 (трех)", "юо-7", "архив"),
        note="архив ≤ 3 рабочих дня",
    ),
    "12": Oracle(
        status="grounded",
        min_citations=1,
        answer_all=("испытан",),
        answer_any=("распространя", "трудов"),
        cite_any=("70", "испытан"),
        note="на испытании — обычные трудовые правила",
    ),
    "13": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("соглас",),
        cite_any=("152", "соглас", "персональн"),
        note="отзыв согласия 152-ФЗ",
    ),
    "14": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("срочн", "сезон", "59"),
        cite_any=("59", "сезон", "срочн"),
        note="сезонный срочный ТД",
    ),
    "15": Oracle(
        status="grounded",
        min_citations=1,
        answer_all=("акт",),
        answer_any=("а-08", "северн", "помещен", "возвращ"),
        cite_any=("6.3", "акт", "а-08", "северн"),
        note="dialog: возврат по акту А-08",
    ),
    "16": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("включа", "упаков", "доставк"),
        cite_any=("2.1", "упаков", "доставк", "п-17", "альфа-трейд"),
        note="dialog: упаковка/доставка в цене П-17",
    ),
    "17": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("талон", "производител", "не установлен"),
        cite_any=("талон", "пт-05", "трейдинг", "6.1"),
        note="dialog: гарантия по талону ПТ-05",
    ),
    "18": Oracle(
        status="grounded",
        min_citations=1,
        answer_any=("трёх", "трех", "3 (трёх)", "3 (трех)", "трёх рабочих", "трех рабочих"),
        cite_any=("юридическ", "3.2", "регламент", "2025", "трёх", "трех"),
        note="dialog: оригинал в юротдел за 3 дня (ред. 2025)",
    ),
}


def _cite_blob(result) -> str:
    parts = []
    for c in result.citations or []:
        parts.append(f"{c.doc_id} {c.title} {c.span} {c.quote}")
    return normalize(" ".join(parts))


def _check(qid: str, result, oracle: Oracle) -> list[str]:
    fails: list[str] = []
    a = normalize(result.answer or "")
    cites = _cite_blob(result)
    n = len(result.citations or [])

    if oracle.status is not None and result.status != oracle.status:
        fails.append(f"status={result.status} want={oracle.status}")
    for bad in oracle.status_not:
        if result.status == bad:
            fails.append(f"status must not be {bad}")

    if oracle.min_citations is not None and n < oracle.min_citations:
        fails.append(f"citations={n} < {oracle.min_citations}")
    if oracle.max_citations is not None and n > oracle.max_citations:
        fails.append(f"citations={n} > {oracle.max_citations}")

    for needle in oracle.answer_all:
        if normalize(needle) not in a:
            fails.append(f"answer missing all-req «{needle}»")
    if oracle.answer_any and not any(normalize(n) in a for n in oracle.answer_any):
        fails.append(f"answer missing any of {oracle.answer_any}")
    for needle in oracle.answer_none:
        # Allow negation phrases that mention the wrong number.
        if normalize(needle) in a and "не " + normalize(needle).split()[0] not in a:
            # crude: if exact bad phrase present
            fails.append(f"answer must not claim «{needle}»")

    if oracle.cite_any and not any(normalize(n) in cites for n in oracle.cite_any):
        fails.append(f"citations missing any of {oracle.cite_any}")
    for needle in oracle.cite_all:
        if normalize(needle) not in cites:
            fails.append(f"citations missing all-req «{needle}»")

    return fails


@pytest.mark.skipif(not _organizer_ready(), reason="organizer KB missing")
@pytest.mark.parametrize("qid", sorted(ORACLES, key=lambda x: int(x)))
def test_golden_demo_fact(qid: str):
    """Per-question fact oracle; lexical path must already surface evidence."""
    questions = _load_questions()
    assert qid in questions, f"missing question {qid} in demo_questions.csv"
    # Lexical-only by default; set PSB_GOLDEN_LLM=1 to exercise the LLM path.
    if os.environ.get("PSB_GOLDEN_LLM", "").lower() not in {"1", "true", "on", "yes"}:
        os.environ["PSB_LEXICAL_ONLY"] = "1"
    else:
        os.environ.pop("PSB_LEXICAL_ONLY", None)
    result = answer_question(questions[qid], ORGANIZER)
    fails = _check(qid, result, ORACLES[qid])
    assert not fails, (
        f"Q{qid} ({ORACLES[qid].note}) FAIL: {fails}\n"
        f"status={result.status} cites={len(result.citations)}\n"
        f"answer={result.answer[:400]}"
    )


@pytest.mark.skipif(not _organizer_ready(), reason="organizer KB missing")
def test_golden_csv_ids_align():
    questions = _load_questions()
    with GOLD_PATH.open(encoding="utf-8-sig", newline="") as f:
        gold_ids = {row["id"].strip() for row in csv.DictReader(f)}
    assert set(questions) == gold_ids == set(ORACLES.keys())
