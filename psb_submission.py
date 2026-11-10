"""Platform batch: questions.csv → submission.csv with D22 isolation."""

from __future__ import annotations

import csv
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from psb_config import FALLBACK_ANSWER, MAX_ANSWER_CHARS, data_dir, env_int
from psb_ingest import load_kb, resolve_platform_kb
from psb_pipeline import answer_question
from psb_textnorm import strip_markdown


def find_questions(data: Path) -> Path:
    for name in ("questions.csv", "demo_questions.csv"):
        path = data / name
        if path.is_file():
            return path
    raise FileNotFoundError(f"No questions.csv in {data}")


def load_questions(path: Path) -> list[tuple[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {"id", "question"}.issubset(set(reader.fieldnames)):
            raise ValueError("questions.csv needs columns id,question")
        rows: list[tuple[str, str]] = []
        seen: set[str] = set()
        for raw in reader:
            qid = str(raw.get("id", "")).strip()
            question = str(raw.get("question", "")).strip()
            if not qid:
                continue
            if qid in seen:
                print(f"warning: duplicate id {qid} ignored", file=sys.stderr)
                continue
            seen.add(qid)
            rows.append((qid, question))
    if not rows:
        raise ValueError("questions.csv has no rows")
    return rows


def _clip_answer(text: str) -> str:
    cleaned = strip_markdown(text or FALLBACK_ANSWER)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        cleaned = FALLBACK_ANSWER
    if len(cleaned) > MAX_ANSWER_CHARS:
        cleaned = cleaned[: MAX_ANSWER_CHARS - 1].rstrip() + "…"
    return cleaned


def run_batch(
    data_path: Path | None = None,
    kb_path: Path | None = None,
    out_path: Path | None = None,
) -> int:
    data = data_path or data_dir()
    out = out_path or Path("submission.csv")
    workers = env_int("MAX_WORKERS", 2, 1, 8)

    # Preflight BEFORE touching submission.csv (D22 / RG-SUB-09)
    try:
        qpath = find_questions(data)
        questions = load_questions(qpath)
        kb = kb_path or resolve_platform_kb()
        kb_rows = load_kb(kb)
        if not kb_rows:
            raise ValueError(f"empty knowledge base: {kb}")
    except Exception as exc:
        print(f"preflight failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

    def work(qid: str, question: str) -> tuple[str, str]:
        try:
            result = answer_question(question, kb, kb_rows=kb_rows)
            return qid, _clip_answer(result.answer)
        except Exception as exc:
            print(f"question {qid} failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return qid, FALLBACK_ANSWER

    answers: list[tuple[str, str]] = [("", "")] * len(questions)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(work, qid, question): idx
            for idx, (qid, question) in enumerate(questions)
        }
        done = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            qid, answer = fut.result()
            answers[idx] = (qid, answer)
            done += 1
            if done % 10 == 0 or done == len(questions):
                print(f"Processed {done}/{len(questions)}", flush=True)

    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix="submission_",
        suffix=".csv",
        dir=str(out.parent if out.parent.exists() else Path.cwd()),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
            writer.writerow(["id", "answer"])
            for qid, answer in answers:
                writer.writerow([qid, answer])
        os.replace(tmp_path, out)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise

    print(f"Wrote {out} ({len(answers)} answers); KB={kb}; workers={workers}", flush=True)
    return 0
