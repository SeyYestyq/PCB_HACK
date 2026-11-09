from answer_core.pipeline import answer_question


def test_grounded_legal_capacity():
    r = answer_question("Какие нормы учесть при проверке правоспособности компании для кредита?")
    assert r.status == "grounded"
    assert r.citations
    assert all(c.doc_id for c in r.citations)
    assert not r.missing


def test_abstain_historical():
    r = answer_question("Какая ставка НДС была в старой редакции в 2019 году?")
    assert r.status == "abstain"
    assert r.missing
    assert r.citations == []


def test_abstain_no_hits():
    r = answer_question("Какие требования к лицензии на экспорт урана по регламенту банка?")
    assert r.status == "abstain"
    assert r.missing


def test_refuse_offtopic():
    r = answer_question("Расскажи анекдот про погоду")
    assert r.status == "refuse_role"
    assert r.citations == []


def test_clarify_ambiguous_contract():
    r = answer_question("Что сказано в договоре?")
    assert r.status == "clarify"
    assert r.missing


def test_clarify_empty():
    r = answer_question("   ")
    assert r.status == "clarify"
