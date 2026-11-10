"""Load knowledge base from DATA_DIR zip, directory, or jsonl."""

from __future__ import annotations

import io
import json
import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from psb_config import FIXTURE_KB, ORGANIZER_KB, ROOT, data_dir, env
from psb_structure import chunk_text, date_mentions, parse_date_parts, slug

_ZIP_NAMES = ("knowledge-base.zip", "kb.zip", "knowledge_base.zip")
_DOC_SUFFIXES = {".txt", ".md", ".docx"}


def find_file(*names: str, roots: list[Path] | None = None) -> Path:
    search_roots = roots or [data_dir(), ROOT / "data", Path.cwd(), ROOT]
    for root in search_roots:
        for name in names:
            path = root / name
            if path.is_file():
                return path
    raise FileNotFoundError(f"Не найден один из файлов: {', '.join(names)}")


def find_kb_zip(roots: list[Path] | None = None) -> Path | None:
    try:
        return find_file(*_ZIP_NAMES, roots=roots)
    except FileNotFoundError:
        return None


def default_kb_path() -> Path:
    """Prefer PSB_KB_PATH / organizer dir for local; else DATA_DIR zip for platform."""
    env_path = env("PSB_KB_PATH")
    if env_path:
        candidates = []
        p = Path(env_path)
        candidates.append(p if p.is_absolute() else (ROOT / p))
        # Docker often mounts KB at /data/organizer/kb while host .env keeps a relative path.
        candidates.append(Path("/data/organizer/kb"))
        candidates.append(ORGANIZER_KB)
        for cand in candidates:
            if cand.is_dir() and any(cand.glob("*.txt")):
                return cand
            if cand.is_file():
                return cand
        return candidates[0]
    if ORGANIZER_KB.is_dir() and any(ORGANIZER_KB.glob("*.txt")):
        return ORGANIZER_KB
    docker_kb = Path("/data/organizer/kb")
    if docker_kb.is_dir() and any(docker_kb.glob("*.txt")):
        return docker_kb
    z = find_kb_zip()
    if z is not None:
        return z
    return FIXTURE_KB


def read_docx(raw: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(raw)) as doc:
        xml = doc.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    return "\n".join(
        "".join(node.text or "" for node in paragraph.iter(ns + "t"))
        for paragraph in root.iter(ns + "p")
    )


def _doc_kind(name: str) -> str:
    low = name.lower()
    if "закон" in low or "фз" in low or "ткодекс" in low or "/законы" in low:
        return "law"
    if "доп" in low and "соглаш" in low:
        return "amendment"
    if "регламент" in low or "договор" in low or "письм" in low or "записк" in low:
        return "company"
    if "документ" in low:
        return "company"
    return "other"


def _edition_meta(name: str, text: str) -> dict:
    """Edition start is the approval date, not the day a repealed text mentions its own end."""
    head = f"{name}\n{text[:900]}"
    mentions = date_mentions(head)
    superseded = "утратил" in name.lower() or "утратил" in head.lower()
    effective: int | None = None
    valid_to: int | None = None
    for stamp, prefix, suffix in mentions:
        if "утрат" in prefix or "силу с" in prefix or "утрач" in suffix:
            if "утрат" in prefix or "силу с" in prefix:
                valid_to = stamp
            continue
        if any(mark in prefix for mark in ("редакц", "утвержд", "действует", "приказ")):
            if "действует" in prefix or "редакц" in prefix:
                effective = stamp
            elif effective is None:
                effective = stamp
    if effective is None:
        candidates = [stamp for stamp, _prefix, suffix in mentions if "утрач" not in suffix and stamp != valid_to]
        if candidates:
            effective = min(candidates) if superseded else max(candidates)
    dates = parse_date_parts(head)
    return {
        "kind": _doc_kind(name),
        "effective_from": effective,
        "valid_to": valid_to,
        "superseded": superseded,
        "dates": dates,
    }


def _rows_from_document(name: str, text: str) -> list[dict]:
    title = Path(name).stem.replace("__", " — ")
    doc_id = slug(name)
    meta = _edition_meta(name, text)
    rows: list[dict] = []
    for section, chunk in chunk_text(text):
        rows.append(
            {
                "doc_id": doc_id,
                "title": title,
                "section": section,
                "edition": "current" if not meta["superseded"] else "superseded",
                "text": chunk,
                "source_file": name,
                "kind": meta["kind"],
                "effective_from": meta["effective_from"],
                "superseded": meta["superseded"],
                "full_text": text,
            }
        )
    return rows


def _rows_from_txt_dir(path: Path) -> list[dict]:
    rows: list[dict] = []
    for fp in sorted(path.glob("*.txt")):
        raw = fp.read_text(encoding="utf-8-sig")
        rows.extend(_rows_from_document(fp.name, raw))
    return rows


def _rows_from_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _rows_from_zip(path: Path) -> list[dict]:
    rows: list[dict] = []
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith("/") or name.startswith("__MACOSX/"):
                continue
            suffix = Path(name).suffix.lower()
            if suffix not in _DOC_SUFFIXES:
                continue
            raw = archive.read(name)
            try:
                text = read_docx(raw) if suffix == ".docx" else raw.decode("utf-8-sig")
            except (UnicodeDecodeError, KeyError, ValueError, zipfile.BadZipFile, ET.ParseError):
                continue
            if text.strip():
                rows.extend(_rows_from_document(name, text.strip()))
    if not rows:
        raise ValueError(f"В архиве базы знаний нет читаемых документов: {path}")
    return rows


def load_kb(path: Path | None = None) -> list[dict]:
    p = path or default_kb_path()
    if p.is_dir():
        rows = _rows_from_txt_dir(p)
        if not rows:
            raise FileNotFoundError(f"KB directory has no .txt files: {p}")
        return rows
    if p.suffix.lower() == ".jsonl":
        return _rows_from_jsonl(p)
    if p.suffix.lower() == ".zip":
        return _rows_from_zip(p)
    if p.is_file() and p.suffix.lower() == ".txt":
        return _rows_from_txt_dir(p.parent)
    raise FileNotFoundError(f"Unsupported KB path: {p}")


def resolve_platform_kb() -> Path:
    """Resolve KB for platform batch: DATA_DIR zip first, then local overrides."""
    env_path = env("PSB_KB_PATH")
    if env_path:
        p = Path(env_path)
        resolved = p if p.is_absolute() else (ROOT / p)
        if resolved.exists():
            return resolved
    z = find_kb_zip([data_dir(), Path.cwd(), ROOT / "data" / "organizer", ROOT])
    if z is not None:
        return z
    if ORGANIZER_KB.is_dir() and any(ORGANIZER_KB.glob("*.txt")):
        return ORGANIZER_KB
    raise FileNotFoundError(
        "База знаний не найдена: ожидается DATA_DIR/knowledge-base.zip "
        "(или kb.zip / knowledge_base.zip)"
    )


def extract_zip_to_cache(zip_path: Path) -> Path:
    """Optional helper: unpack zip under /tmp for debugging."""
    cache = Path(tempfile.gettempdir()) / "psb_cache" / zip_path.stem
    cache.mkdir(parents=True, exist_ok=True)
    marker = cache / ".ok"
    if marker.is_file():
        return cache
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(cache)
    marker.write_text("ok", encoding="utf-8")
    return cache
