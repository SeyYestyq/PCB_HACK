from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import answer_question


def main() -> None:
    p = argparse.ArgumentParser(description="PSB legal answer-core CLI")
    p.add_argument("question", nargs="?", default="")
    p.add_argument("--kb", type=Path, default=None)
    p.add_argument("--stdin", action="store_true")
    args = p.parse_args()
    q = args.question
    if args.stdin:
        q = Path("/dev/stdin").read_text(encoding="utf-8")
    result = answer_question(q, args.kb)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
