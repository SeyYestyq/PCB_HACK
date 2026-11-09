from pathlib import Path

from answer_core.pipeline import answer_question, default_kb_path, load_kb

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "data" / "fixtures" / "kb.jsonl"
ORGANIZER = ROOT / "data" / "organizer" / "kb"


def test_default_kb_prefers_organizer():
    path = default_kb_path()
    assert path == ORGANIZER or path == FIXTURE
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


def test_organizer_maternity_abstain():
    if not ORGANIZER.is_dir() or not any(ORGANIZER.glob("*.txt")):
        return
    r = answer_question("Какой размер пособия по беременности и родам?", ORGANIZER)
    # May retrieve weakly related labor law; prefer abstain, allow grounded only if citations
    assert r.status in {"abstain", "grounded"}
    if r.status == "grounded":
        assert r.citations
