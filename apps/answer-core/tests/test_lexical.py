"""Lexical retrieve / support-gate checks (no LLM)."""

from pathlib import Path

from answer_core.pipeline import load_kb
from psb_catalog import build_catalog, match_catalog
from psb_editions import extract_event_date, filter_kb_by_edition
from psb_pipeline import _scope_to_contract, _status_from_text, _user_context, parse_dialog
from psb_retrieve import retrieve

ROOT = Path(__file__).resolve().parents[3]
ORGANIZER = ROOT / "data" / "organizer" / "kb"
FIXTURE = ROOT / "data" / "fixtures" / "kb.jsonl"


def _organizer_ready() -> bool:
    return ORGANIZER.is_dir() and any(ORGANIZER.glob("*.txt"))


def test_support_gate_maternity_empty():
    if not _organizer_ready():
        return
    kb = load_kb(ORGANIZER)
    hits = retrieve("Какой размер пособия по беременности и родам?", kb)
    assert hits == []


def test_support_gate_rent_hits_even_when_scoped():
    if not _organizer_ready():
        return
    kb = load_kb(ORGANIZER)
    catalog = build_catalog(kb)
    q = (
        "Какая арендная плата по договору с ООО «Северный Склад» "
        "и до какого числа её нужно вносить?"
    )
    cards = match_catalog(q, catalog)
    scoped = _scope_to_contract(kb, cards)
    assert len(scoped) < len(kb)
    hits = retrieve(q, scoped, catalog=catalog)
    assert hits
    assert any("северн" in (h.get("title") or "").lower() for h in hits)


def test_support_gate_probation_hits():
    if not _organizer_ready():
        return
    kb = load_kb(ORGANIZER)
    hits = retrieve(
        "Какой максимальный срок испытания можно установить главному бухгалтеру?",
        kb,
    )
    assert hits
    blob = " ".join(
        f"{h.get('title','')} {h.get('section','')} {h.get('text','')}" for h in hits[:3]
    ).lower()
    assert "70" in blob or "испытан" in blob


def test_support_gate_august_reg_hits():
    if not _organizer_ready():
        return
    kb = load_kb(ORGANIZER)
    q = (
        "Договор на 12 млн рублей заключали в августе 2024 года. "
        "Нужно ли было одобрение генерального директора?"
    )
    assert extract_event_date(q) == 20240815
    filtered, _ = filter_kb_by_edition(kb, q)
    hits = retrieve(q, filtered)
    assert hits
    top = " ".join(
        f"{h.get('title','')} {h.get('text','')}" for h in hits[:2]
    ).lower()
    assert "регламент" in top
    assert "десяти миллион" in top or "10 000 000" in top


def test_fixture_capacity_not_gated():
    kb = load_kb(FIXTURE)
    hits = retrieve(
        "Какие нормы учесть при проверке правоспособности компании для кредита?",
        kb,
    )
    assert hits


def test_status_abstain_and_limited_phrases():
    assert _status_from_text(
        "В предоставленной базе знаний нет положений для ответа на этот вопрос."
    ) == "abstain"
    assert (
        _status_from_text(
            "По п. 2.1 цена включает доставку. Для полного ответа не хватает: гарантийный талон."
        )
        == "limited"
    )


def test_dialog_q15_keeps_warehouse_context():
    if not _organizer_ready():
        return
    text = (
        "Пользователь: Мы арендуем склад у «Северного Склада». Планируем съезжать.\n"
        "Ассистент: Подскажите номер договора.\n"
        "Пользователь: А-08/2024. Можно просто сдать ключи или обязательно оформлять акт?"
    )
    q, hist = parse_dialog(text)
    search = _user_context(q, hist)
    assert "а-08" in search.lower() or "северн" in search.lower()
    kb = load_kb(ORGANIZER)
    catalog = build_catalog(kb)
    cards = match_catalog(q, catalog) or match_catalog(search, catalog)
    assert len(cards) == 1
    assert "северн" in cards[0].name.lower()


def test_dialog_q16_alfa_trade_not_trading():
    if not _organizer_ready():
        return
    text = (
        "Пользователь: Мы заключили договор поставки мебели с «Альфа-Трейд».\n"
        "Ассистент: Подскажите номер договора.\n"
        "Пользователь: П-17/2024. Доставка и упаковка уже включены в цену "
        "или их оплачиваем отдельно?"
    )
    q, hist = parse_dialog(text)
    search = _user_context(q, hist)
    kb = load_kb(ORGANIZER)
    catalog = build_catalog(kb)
    cards = match_catalog(q, catalog) or match_catalog(search, catalog)
    assert len(cards) == 1
    assert cards[0].name.lower() == "альфа-трейд"


def test_dialog_q18_current_reg_not_2023():
    if not _organizer_ready():
        return
    text = (
        "Пользователь: Подписали новый договор, оригинал пока у меня.\n"
        "Ассистент: Вы про порядок передачи документов?\n"
        "Пользователь: Да. В юротдел нужно отнести сразу или есть какой-то срок?"
    )
    q, hist = parse_dialog(text)
    search = _user_context(q, hist)
    kb = load_kb(ORGANIZER)
    filtered, _ = filter_kb_by_edition(kb, search)
    titles = " ".join(r.get("title") or "" for r in filtered).lower()
    assert "2025" in titles or "ред 2025" in titles
    assert "утратил" not in titles
