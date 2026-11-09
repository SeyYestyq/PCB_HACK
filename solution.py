#!/usr/bin/env python3
"""Hackathon auto-eval entrypoint for PSB legal assistant.

Single shared path with the UI: both call `apps/answer-core`
(`answer_core.pipeline.answer_question`).

Usage:
  python3 solution.py "Какие нормы учесть при проверке правоспособности?"
  echo "вопрос" | python3 solution.py --stdin
  PSB_KB_PATH=/path/to/organizer/kb.jsonl python3 solution.py "..."

Output: JSON with status, answer, citations[], missing[].
KB default: data/fixtures/kb.jsonl until organizers ship the real corpus.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORE_SRC = ROOT / "apps" / "answer-core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from answer_core.pipeline import answer_question  # noqa: E402

DEFAULT_KB = ROOT / "data" / "fixtures" / "kb.jsonl"


def solve(question: str, kb_path: Path | None = None) -> dict:
    """Question in → contract JSON (shared with /api/v1/ask)."""
    path = kb_path
    if path is None:
        env = os.getenv("PSB_KB_PATH")
        path = Path(env) if env else DEFAULT_KB
    return answer_question(question, path).to_dict()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="PSB legal assistant — solution.py")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--stdin", action="store_true", help="Read question from stdin")
    p.add_argument("--kb", type=Path, default=None, help="Override KB jsonl path")
    args = p.parse_args(argv)

    question = sys.stdin.read() if args.stdin else args.question
    if not question.strip():
        print("usage: solution.py \"вопрос\" | solution.py --stdin", file=sys.stderr)
        return 2

    result = solve(question.strip(), args.kb)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
