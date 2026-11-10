from pathlib import Path

from answer_core.pipeline import (
    answer_question,
    default_kb_path,
    load_kb,
    parse_dialog,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "data" / "fixtures" / "kb.jsonl"
ORGANIZER = ROOT / "data" / "organizer" / "kb"
ZIP_KB = ROOT / "data" / "organizer" / "knowledge-base.zip"


def test_default_kb_prefers_organizer():
    path = default_kb_path()
    assert path == ORGANIZER or path == FIXTURE or path == ZIP_KB
    if ORGANIZER.is_dir() and any(ORGANIZER.glob("*.txt")):
        assert path == ORGANIZER


def test_grounded_legal_capacity():
    r = answer_question(
        "Какие нормы учесть при проверке правоспособности компании для кредита?",
        FIXTURE,
    )
    assert r.status == "grounded"
    assert r.citations
    assert all(c.doc_id for c in r.citations)
    assert not r.missing


def test_abstain_historical():
    r = answer_question("Какая ставка НДС была в старой редакции в 2019 году?", FIXTURE)
    assert r.status == "abstain"
    assert r.missing
    assert r.citations == []


def test_abstain_no_hits():
    r = answer_question(
        "Какие требования к лицензии на экспорт урана по регламенту банка?",
        FIXTURE,
    )
    assert r.status == "abstain"
    assert r.missing


def test_refuse_offtopic():
    r = answer_question("Расскажи анекдот про погоду", FIXTURE)
    assert r.status == "refuse_role"
    assert r.citations == []


def test_clarify_ambiguous_contract():
    r = answer_question("Что сказано в договоре?", FIXTURE)
    assert r.status == "clarify"
    assert r.missing


def test_clarify_empty():
    r = answer_question("   ", FIXTURE)
    assert r.status == "clarify"


def test_greeting_is_clarify_not_abstain():
    r = answer_question("ку", FIXTURE)
    assert r.status == "clarify"
    assert r.citations == []


def test_organizer_kb_loads():
    if not ORGANIZER.is_dir():
        return
    rows = load_kb(ORGANIZER)
    assert len(rows) >= 21


def test_organizer_rent_grounded():
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    r = answer_question(
        "Какая арендная плата по договору с ООО «Северный Склад» и до какого числа её нужно вносить?",
        ORGANIZER,
    )
    assert r.status == "grounded"
    assert r.citations
    assert "450" in r.answer or "аренд" in r.answer.lower()


def test_organizer_rent_short_question_grounded():
    """Counterparty name must resolve via catalog, not false clarify."""
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    q = "Какая арендная плата по договору с ООО «Северный Склад»?"
    r = answer_question(q, ORGANIZER)
    assert r.status == "grounded", f"expected grounded, got {r.status}: {r.answer}"
    assert r.citations
    assert not r.missing
    joined = " ".join(c.title.lower() + " " + c.quote.lower() for c in r.citations)
    assert "северн" in joined or "аренд" in joined
    # Quotes are full clause fragments, not 240-char stubs only
    assert any(len(c.quote) > 80 for c in r.citations)


def test_organizer_maternity_abstain():
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    r = answer_question("Какой размер пособия по беременности и родам?", ORGANIZER)
    assert r.status == "abstain"
    assert r.citations == []


def test_august_2024_approval_uses_edition_then_in_force():
    """12 млн в августе 2024 — порог 10 млн из редакции 2023, не 15 млн из редакции 2025."""
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    r = answer_question(
        "Договор на 12 млн рублей заключали в августе 2024 года. Нужно ли было одобрение генерального директора?",
        ORGANIZER,
    )
    assert r.status == "grounded", r.answer
    blob = " ".join(c.title.lower() + " " + c.quote.lower() for c in r.citations)
    assert "2023" in blob
    assert "десяти миллион" in blob or "10 000 000" in blob


def test_parse_dialog_history():
    text = (
        "Пользователь: Какой договор с Альфа?\n"
        "Ассистент: Уточните ИНН.\n"
        "Пользователь: ИНН 7701234567, какой срок оплаты?"
    )
    q, hist = parse_dialog(text)
    assert "срок оплаты" in q.lower() or "7701234567" in q
    assert len(hist) >= 1
    assert hist[0].role == "user"


def test_zip_kb_loads():
    if not ZIP_KB.is_file():
        return
    rows = load_kb(ZIP_KB)
    assert len(rows) >= 10


def test_alfa_trading_is_not_ambiguous():
    """«Альфа-Трейдинг» must not clarify against the shorter «Альфа-Трейд»."""
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    r = answer_question(
        "По договору с «Альфа-Трейдинг» можем оплатить технику авансом или только после поставки?",
        ORGANIZER,
    )
    assert r.status != "clarify", r.answer


def test_probation_prefers_tk70():
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    r = answer_question(
        "Какой максимальный срок испытания можно установить главному бухгалтеру?",
        ORGANIZER,
    )
    assert r.status == "grounded"
    joined = " ".join(c.title.lower() + " " + c.quote.lower() for c in r.citations[:3])
    assert "70" in joined or "испытан" in joined
