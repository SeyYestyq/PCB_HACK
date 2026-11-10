"""Tokenization and lightweight Russian stemming (stdlib only)."""

from __future__ import annotations

import re

_WORD_RE = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)
_PERFECTIVE = (
    "ившись",
    "ывшись",
    "вшись",
    "ивши",
    "ывши",
    "вши",
    "ится",
    "ытся",
    "ется",
    "ать",
    "ять",
    "еть",
    "ить",
    "уть",
    "ыть",
)
_ADJECTIVE = (
    "ого",
    "ему",
    "ому",
    "ыми",
    "ими",
    "ую",
    "юю",
    "ая",
    "яя",
    "ое",
    "ее",
    "ые",
    "ие",
    "ый",
    "ий",
    "ой",
    "ей",
)
_NOUN = (
    "иями",
    "ями",
    "ами",
    "иях",
    "ях",
    "ах",
    "ием",
    "иям",
    "ям",
    "ам",
    "ией",
    "иями",
    "остью",
    "ости",
    "ость",
    "ие",
    "ье",
    "ия",
    "ья",
    "ов",
    "ев",
    "ей",
    "ий",
    "ый",
    "ой",
    "ом",
    "ем",
)
_REFLEXIVE = ("ся", "сь")
_PARTICIPLE = ("ущ", "ющ", "ащ", "ящ", "вш", "нн", "енн")


def normalize(text: str) -> str:
    return (text or "").lower().replace("ё", "е")


def _strip_suffix(word: str, suffixes: tuple[str, ...], min_stem: int = 3) -> str:
    for suf in suffixes:
        if word.endswith(suf) and len(word) - len(suf) >= min_stem:
            return word[: -len(suf)]
    return word


def stem(word: str) -> str:
    w = normalize(word)
    if len(w) <= 3:
        return w
    w = _strip_suffix(w, _REFLEXIVE, 4)
    w = _strip_suffix(w, _PERFECTIVE, 4)
    w = _strip_suffix(w, _ADJECTIVE, 4)
    w = _strip_suffix(w, _PARTICIPLE, 4)
    w = _strip_suffix(w, _NOUN, 3)
    return w


def tokens(text: str, *, stem_words: bool = True) -> list[str]:
    out: list[str] = []
    for raw in _WORD_RE.findall(normalize(text)):
        if len(raw) <= 2:
            continue
        out.append(stem(raw) if stem_words else raw)
    return out


def token_set(text: str) -> set[str]:
    return set(tokens(text))
