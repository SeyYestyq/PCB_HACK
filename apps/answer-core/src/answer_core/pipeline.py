"""Thin wrapper: shared pipeline lives in root psb_*.py for platform ZIP."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()


def _candidate_roots() -> list[Path]:
    roots: list[Path] = []
    # Walk up from this file; monorepo root is several levels above.
    for parent in _HERE.parents:
        roots.append(parent)
    for extra in (Path("/app"), Path.cwd()):
        roots.append(extra)
    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[Path] = []
    for root in roots:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        out.append(root)
    return out


def _bootstrap() -> None:
    for root in _candidate_roots():
        if (root / "psb_pipeline.py").is_file():
            path = str(root)
            if path not in sys.path:
                sys.path.insert(0, path)
            return
    raise ImportError(
        "psb_pipeline.py not found; copy root psb_*.py next to the runtime "
        f"(searched: {[str(c) for c in _candidate_roots()[:8]]})"
    )


_bootstrap()

from psb_config import llm_configured  # noqa: E402
from psb_ingest import default_kb_path, load_kb  # noqa: E402
from psb_pipeline import (  # noqa: E402
    Answer,
    Citation,
    Turn,
    answer_question,
    answer_question_dict,
    parse_dialog,
)
from psb_retrieve import retrieve  # noqa: E402

__all__ = [
    "Answer",
    "Citation",
    "Turn",
    "answer_question",
    "answer_question_dict",
    "default_kb_path",
    "load_kb",
    "llm_configured",
    "parse_dialog",
    "retrieve",
]
