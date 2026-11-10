"""D2/D4/D22 smoke for solution.py / psb_submission."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ORGANIZER_KB = ROOT / "data" / "organizer" / "kb"
DEMO_Q = ROOT / "data" / "organizer" / "tests" / "demo_questions.csv"
ZIP_KB = ROOT / "data" / "organizer" / "knowledge-base.zip"


def test_run_batch_atomic(tmp_path: Path):
    from psb_submission import run_batch

    if not DEMO_Q.is_file() or not ORGANIZER_KB.is_dir():
        return

    data = tmp_path / "data"
    data.mkdir()
    (data / "questions.csv").write_text(DEMO_Q.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "submission.csv"
    # Pre-existing file must survive preflight failure
    out.write_text("old\n", encoding="utf-8")

    # Broken KB path → preflight fails, old file kept
    try:
        run_batch(data, tmp_path / "missing-kb", out)
        assert False, "expected preflight failure"
    except Exception:
        assert out.read_text(encoding="utf-8") == "old\n"

    rc = run_batch(data, ORGANIZER_KB, out)
    assert rc == 0
    assert out.is_file()
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    expected_ids = {r["id"] for r in csv.DictReader(DEMO_Q.open(encoding="utf-8-sig"))}
    assert {r["id"] for r in rows} == expected_ids
    assert all(r["answer"].strip() for r in rows)


def test_solution_no_args_writes_csv(tmp_path: Path):
    if not DEMO_Q.is_file() or not ORGANIZER_KB.is_dir():
        return
    data = tmp_path / "data"
    data.mkdir()
    (data / "questions.csv").write_text(DEMO_Q.read_text(encoding="utf-8"), encoding="utf-8")
    env = os.environ.copy()
    env["DATA_DIR"] = str(data)
    env["PSB_KB_PATH"] = str(ORGANIZER_KB)
    env["PYTHONPATH"] = str(ROOT)
    out = tmp_path / "submission.csv"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "solution.py"), "--out", str(out)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "id" in text and "answer" in text


def test_zip_name_resolution(tmp_path: Path):
    from psb_ingest import find_kb_zip

    if not ZIP_KB.is_file():
        return
    data = tmp_path / "data"
    data.mkdir()
    target = data / "kb.zip"
    target.write_bytes(ZIP_KB.read_bytes())
    found = find_kb_zip([data])
    assert found == target
