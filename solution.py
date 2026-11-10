#!/usr/bin/env python3
"""Hackathon entrypoint for PSB legal assistant.

Platform mode (default, no args):
  DATA_DIR=data python3 solution.py
  → reads DATA_DIR/questions.csv + knowledge-base.zip
  → writes submission.csv

Local single-question JSON:
  python3 solution.py "вопрос"
  echo "вопрос" | python3 solution.py --stdin
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from psb_ingest import default_kb_path
from psb_pipeline import answer_question
from psb_submission import run_batch


def solve(question: str, kb_path: Path | None = None) -> dict:
    return answer_question(question, kb_path or default_kb_path()).to_dict()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="PSB legal assistant — solution.py")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--stdin", action="store_true", help="Read question from stdin")
    p.add_argument("--kb", type=Path, default=None, help="KB dir, .zip or .jsonl")
    p.add_argument(
        "--batch",
        action="store_true",
        help="Force batch mode (default when no question given)",
    )
    p.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Batch input dir (default: DATA_DIR or data)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("submission.csv"),
        help="Batch output CSV path",
    )
    args = p.parse_args(argv)

    question = sys.stdin.read() if args.stdin else args.question
    batch_mode = args.batch or not (question or "").strip()

    if batch_mode:
        return run_batch(args.data_dir, args.kb, args.out)

    result = solve(question.strip(), args.kb)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
