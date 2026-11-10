"""Counterparty / contract catalog built from company documents."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from psb_structure import extract_contract_numbers, extract_inns, extract_quoted_names
from psb_textnorm import normalize, stem, tokens


@dataclass
class CounterpartyCard:
    name: str
    name_stem: str
    inn: str = ""
    contract_numbers: list[str] = field(default_factory=list)
    doc_ids: list[str] = field(default_factory=list)
    titles: list[str] = field(default_factory=list)


_CONTRACT_IN_Q = re.compile(
    r"(?:№|#)\s*([А-ЯA-Zа-яa-z]{1,4}[-–—/]?\d{1,4}(?:/\d{4})?)|"
    r"(?<!\w)((?:А|A|П|P|ПТ|PT)[-–—]?\d{2}(?:/\d{4})?)(?!\w)",
    re.IGNORECASE,
)
_INN_IN_Q = re.compile(r"(?:инн\s*)?(\d{10}|\d{12})", re.IGNORECASE)
_LEGAL_FORM = re.compile(r"(?<!\w)(?:ооо|ип|ао|пао|зао|нао|оао)(?!\w)", re.IGNORECASE)

# Quoted role labels and our own company must not swallow every contract number.
_SKIP_NAME_STEMS = {
    "арендодатель",
    "арендатор",
    "поставщик",
    "покупатель",
    "заказчик",
    "исполнитель",
    "подрядчик",
    "продавец",
    "клиент",
    "общество",
}
# Seed only; runtime also treats frequent preamble names as "own" when detected.
_OWN_COMPANY_STEMS_SEED = {"меридиан"}
_OWN_COMPANY_STEMS: set[str] = set(_OWN_COMPANY_STEMS_SEED)


def _norm_contract(raw: str) -> str:
    return re.sub(r"[\s–—]", "", raw).upper().replace("P-", "П-").replace("PT-", "ПТ-").replace("A-", "А-")


def _is_real_counterparty(name: str) -> bool:
    key = stem(name)
    return bool(key) and key not in _SKIP_NAME_STEMS and key not in _OWN_COMPANY_STEMS


def _prefer_counterparties(cards: list[CounterpartyCard]) -> list[CounterpartyCard]:
    if len(cards) <= 1:
        return cards
    preferred = [c for c in cards if _is_real_counterparty(c.name)]
    return preferred or cards


def _detect_own_stems(kb: list[dict]) -> set[str]:
    """Names quoted in many company preambles are likely the bank/org itself."""
    counts: dict[str, int] = {}
    docs = 0
    seen: set[str] = set()
    for row in kb:
        doc_id = row.get("doc_id") or ""
        if not doc_id or doc_id in seen:
            continue
        if row.get("kind") not in {"company", "amendment", "other"}:
            continue
        seen.add(doc_id)
        docs += 1
        full = row.get("full_text") or row.get("text") or ""
        for name in extract_quoted_names(full[:900]):
            key = stem(name)
            if key and key not in _SKIP_NAME_STEMS:
                counts[key] = counts.get(key, 0) + 1
    if docs < 3:
        return set(_OWN_COMPANY_STEMS_SEED)
    threshold = max(2, docs // 2)
    detected = {k for k, n in counts.items() if n >= threshold}
    return detected | set(_OWN_COMPANY_STEMS_SEED)


def build_catalog(kb: list[dict]) -> list[CounterpartyCard]:
    global _OWN_COMPANY_STEMS
    _OWN_COMPANY_STEMS = _detect_own_stems(kb)
    by_key: dict[str, CounterpartyCard] = {}
    seen_docs: set[str] = set()
    for row in kb:
        if row.get("kind") not in {"company", "amendment", "other"} and "документ" not in (
            row.get("source_file") or ""
        ).lower():
            # Prefer company docs; still scan if preamble has INN.
            if "инн" not in (row.get("full_text") or row.get("text") or "").lower()[:500]:
                continue
        doc_id = row.get("doc_id") or ""
        if doc_id in seen_docs:
            continue
        # Use full preamble once per document.
        full = row.get("full_text") or row.get("text") or ""
        seen_docs.add(doc_id)
        preamble = full[:900]
        names = extract_quoted_names(preamble)
        inns = extract_inns(preamble)
        title = row.get("title") or ""
        contracts = [_norm_contract(c) for c in extract_contract_numbers(preamble + " " + title)]
        title_n = normalize(title)
        # First quoted org after legal form is usually the counterparty of interest.
        for i, name in enumerate(names):
            key = stem(name)
            if not key or key in _SKIP_NAME_STEMS:
                continue
            name_n = normalize(name)
            # Own company appears in every preamble — only keep docs whose title names it,
            # and never attach foreign contract numbers to it.
            own = key in _OWN_COMPANY_STEMS
            if own and name_n not in title_n and "регламент" not in title_n and "служебн" not in title_n:
                continue
            card = by_key.get(key)
            if card is None:
                card = CounterpartyCard(
                    name=name,
                    name_stem=key,
                    inn=inns[i] if i < len(inns) else (inns[0] if inns else ""),
                )
                by_key[key] = card
            if not card.inn and inns:
                card.inn = inns[0]
            if not own:
                for c in contracts:
                    # Attach a contract only when the counterparty is named in the title
                    # or this is the sole non-role quoted party in the preamble.
                    real_names = [n for n in names if _is_real_counterparty(n)]
                    if name_n in title_n or (len(real_names) == 1 and real_names[0] == name):
                        if c not in card.contract_numbers:
                            card.contract_numbers.append(c)
            if doc_id and doc_id not in card.doc_ids:
                if not own or name_n in title_n or "регламент" in title_n or "служебн" in title_n:
                    card.doc_ids.append(doc_id)
            if title and title not in card.titles:
                card.titles.append(title)
    return list(by_key.values())


def contracts_in_question(question: str) -> list[str]:
    found: list[str] = []
    for m in _CONTRACT_IN_Q.finditer(question or ""):
        raw = m.group(1) or m.group(2) or ""
        if not raw:
            continue
        norm = _norm_contract(raw)
        if norm and norm not in found:
            found.append(norm)
    return found


def inns_in_question(question: str) -> list[str]:
    # Prefer explicit «ИНН …»
    explicit = re.findall(r"инн\s*(\d{10}|\d{12})", normalize(question or ""), flags=re.I)
    if explicit:
        return list(dict.fromkeys(explicit))
    return []


def _name_in_question(name: str, question_norm: str) -> bool:
    """Match the full name, so «Альфа-Трейд» is not found inside «Альфа-Трейдинг»."""
    name_n = normalize(name).strip()
    if len(name_n) < 3:
        return False
    return re.search(rf"(?<![\w]){re.escape(name_n)}(?![\w])", question_norm) is not None


def _name_tokens_align(lhs: str, rhs: str) -> bool:
    """Inflected quoted party («Северным Складом») vs catalog name."""
    left = sorted(tokens(lhs), key=len)
    right = sorted(tokens(rhs), key=len)
    if not left or not right or len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if a == b:
            continue
        # Prefix allowance for inflection only (склад/складом), not трейд/трейдинг.
        if (
            len(a) >= 5
            and len(b) >= 5
            and a[:5] == b[:5]
            and abs(len(a) - len(b)) <= 2
        ):
            continue
        return False
    return True


def _prefer_specific_name_hits(
    hits: list[CounterpartyCard], question: str
) -> list[CounterpartyCard]:
    """If the question names a longer party («Альфа-Трейдинг»), drop prefix siblings."""
    if len(hits) <= 1:
        return hits
    q = normalize(question or "")
    kept: list[CounterpartyCard] = []
    for card in hits:
        name = normalize(card.name)
        dominated = False
        for other in hits:
            if other is card:
                continue
            other_name = normalize(other.name)
            if len(other_name) <= len(name):
                continue
            if name and other_name.startswith(name) and _name_in_question(other.name, q):
                dominated = True
                break
            # Quoted longer form in the question wins over a shorter catalog sibling.
            if name and other_name.startswith(name) and other_name in q.replace("«", "").replace("»", ""):
                dominated = True
                break
        if not dominated:
            kept.append(card)
    return kept or hits


def match_catalog(question: str, catalog: list[CounterpartyCard]) -> list[CounterpartyCard]:
    q = normalize(question or "")
    q_tokens = set(tokens(question or ""))
    hits: list[CounterpartyCard] = []

    for num in contracts_in_question(question):
        for card in catalog:
            if any(_norm_contract(c) == num or num in _norm_contract(c) for c in card.contract_numbers):
                if card not in hits:
                    hits.append(card)

    for inn in inns_in_question(question):
        for card in catalog:
            if card.inn == inn and card not in hits:
                hits.append(card)

    if hits:
        return _prefer_counterparties(hits)

    # Exact stem equality of counterparty name (not substring of «альфа» alone).
    for card in catalog:
        if not _is_real_counterparty(card.name):
            continue
        name_toks = set(tokens(card.name))
        if name_toks and name_toks <= q_tokens:
            hits.append(card)
            continue
        if _name_in_question(card.name, q):
            hits.append(card)
            continue
        for quoted in extract_quoted_names(question):
            if _name_tokens_align(quoted, card.name):
                hits.append(card)
                break

    return _prefer_counterparties(_prefer_specific_name_hits(hits, question))


def needs_clarify_contract(question: str, catalog: list[CounterpartyCard]) -> tuple[bool, list[str]]:
    """Clarify when question talks about a contract but party is ambiguous."""
    q = normalize(question or "")
    if "договор" not in q and "контрагент" not in q:
        return False, []

    if contracts_in_question(question) or inns_in_question(question):
        return False, []

    matches = match_catalog(question, catalog)
    if len(matches) == 1:
        return False, []
    if len(matches) > 1:
        options = []
        for card in matches:
            label = f"ООО «{card.name}»"
            if card.inn:
                label += f", ИНН {card.inn}"
            if card.contract_numbers:
                label += f", договор № {card.contract_numbers[0]}"
            options.append(label)
        return True, options

    # Vague shared prefix of several counterparties («Альфа…») without a unique card.
    if len(matches) != 1:
        prefix_groups: dict[str, list[CounterpartyCard]] = {}
        for card in catalog:
            if not _is_real_counterparty(card.name):
                continue
            name_n = normalize(card.name)
            toks = name_n.replace("-", " ").split()
            if not toks:
                continue
            prefix = toks[0]
            if len(prefix) < 4 or prefix not in q:
                continue
            # Longer unique form already in the question → not vague.
            if _name_in_question(card.name, q):
                continue
            prefix_groups.setdefault(prefix, []).append(card)
        for prefix, cards in prefix_groups.items():
            uniq: list[CounterpartyCard] = []
            seen_names: set[str] = set()
            for card in cards:
                key = normalize(card.name)
                if key in seen_names:
                    continue
                seen_names.add(key)
                uniq.append(card)
            if len(uniq) > 1:
                options = [
                    f"ООО «{c.name}»"
                    + (f", ИНН {c.inn}" if c.inn else "")
                    + (f", договор № {c.contract_numbers[0]}" if c.contract_numbers else "")
                    for c in uniq
                ]
                return True, options

    # Legal form or quotes alone are not enough when catalog has no unique hit.
    type_anchors = ("регламент", "правоспособ", "аренд", "поставк", "кредитн", "ндс")
    if any(a in q for a in type_anchors):
        return False, []

    if "договор" in q and len(tokens(question)) < 8 and not matches:
        # Only if no strong entity from catalog
        if _LEGAL_FORM.search(q) or extract_quoted_names(question):
            # Named but not in catalog — still try retrieve
            return False, []
        return True, [
            "укажите номер договора",
            "укажите ИНН контрагента",
        ]

    return False, []
