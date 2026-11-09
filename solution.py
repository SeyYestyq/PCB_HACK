#!/usr/bin/env python3
"""Hackathon entrypoint for PSB legal assistant.

Shared pipeline with UI (`apps/answer-core`). Two modes:

1) Local / API-style JSON (single question):
   python3 solution.py "вопрос"
   echo "вопрос" | python3 solution.py --stdin

2) Platform batch (organizer format → submission.csv):
   DATA_DIR=data/organizer/tests python3 solution.py --batch
   # expects questions.csv (or demo_questions.csv) + KB via PSB_KB_PATH / data/organizer/kb
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORE_SRC = ROOT / "apps" / "answer-core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from answer_core.pipeline import answer_question, default_kb_path  # noqa: E402


def resolve_kb(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit
    return default_kb_path()


def solve(question: str, kb_path: Path | None = None) -> dict:
    return answer_question(question, resolve_kb(kb_path)).to_dict()


def _find_questions(data_dir: Path) -> Path:
    for name in ("questions.csv", "demo_questions.csv"):
        p = data_dir / name
        if p.is_file():
            return p
    raise FileNotFoundError(f"No questions.csv in {data_dir}")


def run_batch(data_dir: Path, kb_path: Path, out_path: Path) -> int:
    qpath = _find_questions(data_dir)
    with qpath.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {"id", "question"}.issubset(set(reader.fieldnames)):
            raise ValueError("questions.csv needs columns id,question")
        rows = [(str(r["id"]).strip(), str(r["question"]).strip()) for r in reader]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerow(["id", "answer"])
        for qid, question in rows:
            result = answer_question(question, kb_path)
            writer.writerow([qid, " ".join(result.answer.split())])
    print(f"Wrote {out_path} ({len(rows)} answers); KB={kb_path}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="PSB legal assistant — solution.py")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--stdin", action="store_true", help="Read question from stdin")
    p.add_argument("--kb", type=Path, default=None, help="KB dir (.txt) or .jsonl")
    p.add_argument(
        "--batch",
        action="store_true",
        help="Organizer mode: read questions.csv → write submission.csv",
    )
    p.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Batch input dir (default: DATA_DIR or data/organizer/tests)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("submission.csv"),
        help="Batch output CSV path",
    )
    args = p.parse_args(argv)
    kb = resolve_kb(args.kb)

    if args.batch:
        data_dir = args.data_dir
        if data_dir is None:
            env = os.getenv("DATA_DIR", "").strip()
            data_dir = Path(env) if env else ROOT / "data" / "organizer" / "tests"
        return run_batch(data_dir, kb, args.out)

    question = sys.stdin.read() if args.stdin else args.question
    if not question.strip():
        print(
            'usage: solution.py "вопрос" | solution.py --stdin | solution.py --batch',
            file=sys.stderr,
        )
        return 2

    result = solve(question.strip(), kb)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
