#!/usr/bin/env python3
"""Local multi-run smoke before platform upload.

Measures stability of climb vs organizer demo oracles (not platform score).
Usage:
  PYTHONPATH=.:apps/answer-core/src PSB_VECTORS=0 \\
    apps/answer-core/.venv/bin/python scripts/local_judge_runs.py --runs 5
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps" / "answer-core" / "src"))

from answer_core.pipeline import answer_question  # noqa: E402
from psb_textnorm import normalize  # noqa: E402

# Keep in sync with soft facts from test_golden_demo / demo_output.
CHECKS: dict[str, dict] = {
    "1": {"status": "grounded", "all": ("450", "аренд"), "none": ()},
    "2": {"status": "grounded", "any": ("шест", "6 месяц", "шести месяц"), "none": ()},
    "3": {"status": "abstain", "all": (), "none": ()},
    "4": {"status": "grounded", "all": ("450",), "none": ("составляет 500 000", "плата 500 000")},
    "5": {"status": "grounded", "all": ("10", "одобрен"), "none": ("15 000 000", "15 млн")},
    "6": {"status": "grounded", "any": ("5", "пяти"), "none": ()},
    "7": {"status": "grounded", "any": ("доступ", "круглосуточ", "беспрепятствен"), "none": ()},
    "8": {"status": "grounded", "any": ("акт",), "none": ()},
    "9": {"status": "grounded", "any": ("предоплат", "аванс", "45"), "none": ()},
    "10": {"status": "grounded", "any": ("руководител", "инициатор"), "none": ()},
    "11": {"status": ("grounded", "limited"), "any": ("3", "трёх", "трех"), "none": ()},
    "12": {"status": "grounded", "any": ("испытан", "трудов", "тк"), "none": ()},
    # Golden: ст.9 + missing 6/10/11 → limited preferred; grounded still has core fact.
    "13": {
        "status": ("limited", "grounded"),
        "any": ("152", "соглас"),
        "all": (),
        "none": (),
    },
    "14": {"status": "grounded", "any": ("сезон", "срочн"), "none": ()},
    "15": {"status": "grounded", "any": ("акт", "возврат"), "none": ()},
    "16": {"status": "grounded", "any": ("упаков", "достав", "цен"), "none": ()},
    "17": {"status": ("grounded", "limited"), "any": ("гарант", "талон", "производител"), "none": ()},
    "18": {"status": "grounded", "any": ("3", "юридическ", "оригинал"), "none": ()},
}


def _pass(qid: str, status: str, answer: str) -> tuple[bool, str]:
    spec = CHECKS[qid]
    n = normalize(answer)
    want = spec["status"]
    if isinstance(want, (tuple, list)):
        if status not in want:
            return False, f"status={status} want={want}"
    elif status != want:
        return False, f"status={status} want={want}"
    for needle in spec.get("all") or ():
        if normalize(needle) not in n:
            return False, f"missing:{needle}"
    any_needles = spec.get("any") or ()
    if any_needles and not any(normalize(x) in n for x in any_needles):
        return False, f"missing_any:{any_needles}"
    for bad in spec.get("none") or ():
        if normalize(bad) in n:
            return False, f"forbidden:{bad}"
    if spec.get("need_hedge") and "не хватает" not in n:
        return False, "need_hedge"
    if status != "abstain" and "не хватает" in n and not spec.get("need_hedge"):
        # soft flag — still pass facts, but track limited-style hedges
        return True, "hedge"
    return True, "ok"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--kb", type=Path, default=ROOT / "data" / "organizer" / "kb")
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "local_judge_runs.jsonl",
    )
    args = ap.parse_args()

    qs = list(csv.DictReader((ROOT / "data/organizer/tests/demo_questions.csv").open(encoding="utf-8-sig")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    print(f"local judge runs={args.runs} kb={args.kb}")
    for run in range(1, args.runs + 1):
        t0 = time.time()
        passed = 0
        hedges = 0
        fails: list[str] = []
        lex = 0
        limited = 0
        long_ans = 0
        statuses: Counter[str] = Counter()
        per_q = []
        for row in qs:
            qid = str(row["id"]).strip()
            r = answer_question(row["question"], args.kb)
            ans = r.answer or ""
            ok, reason = _pass(qid, r.status, ans)
            is_lex = ans.startswith("Согласно ")
            lex += int(is_lex)
            limited += int(r.status == "limited")
            long_ans += int(len(ans) > 560)
            statuses[r.status] += 1
            if ok:
                passed += 1
                if reason == "hedge":
                    hedges += 1
            else:
                fails.append(f"Q{qid}:{reason}")
            per_q.append(
                {
                    "id": qid,
                    "ok": ok,
                    "reason": reason,
                    "status": r.status,
                    "lex": is_lex,
                    "len": len(ans),
                    "head": ans[:120].replace("\n", " "),
                }
            )
        elapsed = round(time.time() - t0, 2)
        row_out = {
            "run": run,
            "passed": passed,
            "total": len(qs),
            "hedges": hedges,
            "lex": lex,
            "limited": limited,
            "long": long_ans,
            "statuses": dict(statuses),
            "fails": fails,
            "elapsed_sec": elapsed,
            "per_q": per_q,
        }
        summary_rows.append(row_out)
        with args.out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row_out, ensure_ascii=False) + "\n")
        fail_s = ",".join(fails) if fails else "-"
        print(
            f"run {run}/{args.runs}: {passed}/{len(qs)} "
            f"lex={lex} limited={limited} hedge={hedges} long={long_ans} "
            f"{elapsed}s fails={fail_s}"
        )

    all_pass = all(r["passed"] == r["total"] for r in summary_rows)
    print("---")
    print(f"stable_all_pass={all_pass}")
    print(f"log={args.out}")
    if all_pass:
        print("VERDICT: local green ×", args.runs, "— candidate for platform upload (human)")
        return 0
    print("VERDICT: unstable or failed locally — do not upload yet")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
