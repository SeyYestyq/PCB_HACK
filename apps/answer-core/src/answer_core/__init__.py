"""PSB legal answer core: retrieve → draft → verify (fail-closed)."""

from .pipeline import Answer, answer_question

__all__ = ["Answer", "answer_question"]
