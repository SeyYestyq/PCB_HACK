"""Dense retrieval for the shared answer path.

Platform submit has no Postgres: BGE-M3 comes from ``/embeddings`` and the
index stays in memory. The Docker prototype writes the same vectors into
Postgres + pgvector when ``DATABASE_URL`` is set. If the embed endpoint is
down, a local fastembed model fills pgvector so the demo still searches
vectors. BM25 remains the fallback.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from psb_config import env, llm_configured, llm_settings

_LOCK = threading.Lock()
_LOCAL = None
_API_DEAD = False
# Local fallback when the platform /embeddings proxy is absent.
# Multilingual MiniLM is in fastembed's supported set (384-d, ~0.22 GB).
LOCAL_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class VectorIndex:
    fingerprint: str = ""
    model: str = ""
    dim: int = 0
    source: str = ""  # api | local | ""
    vectors: dict[str, list[float]] = field(default_factory=dict)
    ready: bool = False
    pg: bool = False
    error: str = ""


_INDEX = VectorIndex()


def vectors_enabled() -> bool:
    flag = env("PSB_VECTORS", default="").lower()
    if flag in {"0", "false", "off", "no"}:
        return False
    if flag in {"1", "true", "on", "yes"}:
        return True
    # Platform injects EMB_MODEL. Compose injects DATABASE_URL.
    return bool(env("EMB_MODEL", "EMBED_BASE_URL", "DATABASE_URL"))


def unit_key(row: dict) -> str:
    raw = f"{row.get('doc_id', '')}|{row.get('section', '')}|{row.get('text', '')}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def status() -> dict:
    with _LOCK:
        idx = _INDEX
        return {
            "enabled": vectors_enabled(),
            "ready": idx.ready,
            "source": idx.source,
            "model": idx.model,
            "dim": idx.dim,
            "units": len(idx.vectors),
            "pgvector": idx.pg,
            "error": idx.error,
        }


def _fingerprint(rows: list[dict]) -> str:
    keys = sorted(unit_key(row) for row in rows)
    return hashlib.sha1("\n".join(keys).encode("utf-8")).hexdigest()


def _passage(row: dict) -> str:
    title = str(row.get("title") or "")
    section = str(row.get("section") or "")
    text = str(row.get("text") or "")
    return f"{title}. {section}. {text}"[:1800]


def _normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _as_floats(vec) -> list[float]:
    return _normalize([float(x) for x in vec])


def _embed_api(texts: list[str]) -> tuple[str, list[list[float]]] | None:
    global _API_DEAD
    if _API_DEAD or not texts or not llm_configured():
        return None
    base, key, _gen = llm_settings()
    model = env("EMB_MODEL", default="baai/bge-m3")
    url = f"{base.rstrip('/')}/embeddings"
    out: list[list[float] | None] = [None] * len(texts)
    batch = 16
    for start in range(0, len(texts), batch):
        chunk = texts[start : start + batch]
        payload = {"model": model, "input": chunk, "encoding_format": "float"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            code = getattr(exc, "code", None)
            _API_DEAD = True
            print(
                f"embeddings unavailable ({type(exc).__name__}{'' if code is None else ' ' + str(code)}); "
                "dense index falls back",
                file=sys.stderr,
            )
            return None
        data = body.get("data") if isinstance(body, dict) else None
        if not isinstance(data, list):
            _API_DEAD = True
            return None
        for pos, item in enumerate(data):
            if not isinstance(item, dict) or "embedding" not in item:
                _API_DEAD = True
                return None
            index = int(item.get("index", pos))
            if index < 0 or index >= len(chunk):
                _API_DEAD = True
                return None
            out[start + index] = _as_floats(item["embedding"])
    if any(v is None for v in out):
        _API_DEAD = True
        return None
    return model, out  # type: ignore[return-value]


def _local_model():
    global _LOCAL
    if _LOCAL is None:
        from fastembed import TextEmbedding

        _LOCAL = TextEmbedding(LOCAL_MODEL)
    return _LOCAL


def _embed_local(texts: list[str], *, query: bool) -> tuple[str, list[list[float]]] | None:
    if not texts:
        return None
    try:
        model = _local_model()
    except Exception as exc:
        print(f"local embedder unavailable: {type(exc).__name__}", file=sys.stderr)
        return None
    try:
        if query and hasattr(model, "query_embed"):
            raw = list(model.query_embed(texts))
        else:
            raw = list(model.embed(texts))
    except Exception as exc:
        print(f"local embed failed: {type(exc).__name__}", file=sys.stderr)
        return None
    if len(raw) != len(texts):
        print(
            f"local embed count mismatch: {len(raw)} != {len(texts)}",
            file=sys.stderr,
        )
        return None
    return LOCAL_MODEL, [_as_floats(v) for v in raw]


def _embed(texts: list[str], *, query: bool, source: str) -> tuple[str, str, list[list[float]]] | None:
    """Return (source, model, vectors). ``source`` is locked after the first success."""
    if source == "api":
        got = _embed_api(texts)
        if not got:
            return None
        model, vecs = got
        return "api", model, vecs
    if source == "local":
        got = _embed_local(texts, query=query)
        if not got:
            return None
        model, vecs = got
        return "local", model, vecs
    got = _embed_api(texts)
    if got:
        model, vecs = got
        return "api", model, vecs
    got = _embed_local(texts, query=query)
    if got:
        model, vecs = got
        return "local", model, vecs
    return None


def _vec_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


def _pg_url() -> str:
    return env("DATABASE_URL")


def _sync_pg(rows: list[dict], vectors: dict[str, list[float]], model: str, source: str, fingerprint: str) -> bool:
    url = _pg_url()
    if not url or not vectors:
        return False
    dim = len(next(iter(vectors.values())))
    try:
        import psycopg
    except ImportError:
        print("psycopg is not installed; vectors stay in memory", file=sys.stderr)
        return False
    try:
        with psycopg.connect(url, connect_timeout=4, autocommit=True) as conn:
            _prepare_schema(conn, dim)
            keys = list(vectors)
            with conn.transaction():
                conn.execute("DELETE FROM units WHERE NOT (unit_key = ANY(%s))", (keys,))
                for row in rows:
                    key = unit_key(row)
                    vec = vectors.get(key)
                    if vec is None:
                        continue
                    conn.execute(
                        """
                        INSERT INTO units (
                          unit_key, doc_id, title, section, kind, source_file,
                          effective_from, superseded, body, embedding
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                        ON CONFLICT (unit_key) DO UPDATE SET
                          doc_id = EXCLUDED.doc_id,
                          title = EXCLUDED.title,
                          section = EXCLUDED.section,
                          kind = EXCLUDED.kind,
                          source_file = EXCLUDED.source_file,
                          effective_from = EXCLUDED.effective_from,
                          superseded = EXCLUDED.superseded,
                          body = EXCLUDED.body,
                          embedding = EXCLUDED.embedding
                        """,
                        (
                            key,
                            str(row.get("doc_id") or ""),
                            str(row.get("title") or ""),
                            str(row.get("section") or ""),
                            str(row.get("kind") or "other"),
                            str(row.get("source_file") or ""),
                            row.get("effective_from"),
                            bool(row.get("superseded")),
                            str(row.get("text") or ""),
                            _vec_literal(vec),
                        ),
                    )
                conn.execute(
                    """
                    INSERT INTO kb_meta (id, kb_hash, model, dim, source, units)
                    VALUES (1, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                      kb_hash = EXCLUDED.kb_hash,
                      model = EXCLUDED.model,
                      dim = EXCLUDED.dim,
                      source = EXCLUDED.source,
                      units = EXCLUDED.units,
                      updated_at = now()
                    """,
                    (fingerprint, model, dim, source, len(vectors)),
                )
    except Exception as exc:
        print(f"pgvector sync failed: {type(exc).__name__}", file=sys.stderr)
        return False
    return True


def _create_units(conn, dim: int, regconfig: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS units (
          unit_key text PRIMARY KEY,
          doc_id text NOT NULL,
          title text NOT NULL,
          section text NOT NULL DEFAULT '',
          kind text NOT NULL DEFAULT 'other',
          source_file text NOT NULL DEFAULT '',
          effective_from int,
          superseded boolean NOT NULL DEFAULT false,
          body text NOT NULL,
          embedding vector({int(dim)}) NOT NULL,
          tsv tsvector GENERATED ALWAYS AS (
            to_tsvector(
              '{regconfig}',
              coalesce(title, '') || ' ' || coalesce(section, '') || ' ' || coalesce(body, '')
            )
          ) STORED
        )
        """
    )


def _prepare_schema(conn, dim: int) -> None:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    row = conn.execute(
        """
        SELECT format_type(a.atttypid, a.atttypmod)
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = 'units' AND a.attname = 'embedding'
          AND NOT a.attisdropped
        """
    ).fetchone()
    if row and f"({dim})" not in str(row[0]):
        conn.execute("DROP TABLE IF EXISTS units")
        conn.execute("DROP TABLE IF EXISTS kb_meta")
        row = None
    if row is None:
        try:
            _create_units(conn, dim, "russian")
        except Exception:
            conn.execute("DROP TABLE IF EXISTS units")
            _create_units(conn, dim, "simple")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kb_meta (
          id int PRIMARY KEY CHECK (id = 1),
          kb_hash text NOT NULL,
          model text NOT NULL,
          dim int NOT NULL,
          source text NOT NULL,
          units int NOT NULL,
          updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS units_embedding_hnsw ON units USING hnsw (embedding vector_cosine_ops)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS units_tsv_gin ON units USING gin (tsv)")


def ensure_index(rows: list[dict]) -> VectorIndex:
    """Embed ``rows`` once per process and upsert them into pgvector when configured."""
    global _INDEX
    if not vectors_enabled() or not rows:
        return _INDEX
    fingerprint = _fingerprint(rows)
    with _LOCK:
        if _INDEX.ready and _INDEX.fingerprint == fingerprint and _INDEX.vectors:
            if _pg_url() and not _INDEX.pg:
                _INDEX.pg = _sync_pg(rows, _INDEX.vectors, _INDEX.model, _INDEX.source, fingerprint)
            return _INDEX

        by_key: dict[str, dict] = {}
        for row in rows:
            by_key.setdefault(unit_key(row), row)
        passages = [_passage(row) for row in by_key.values()]
        embedded = _embed(passages, query=False, source="")
        if not embedded:
            _INDEX = VectorIndex(fingerprint=fingerprint, error="embeddings unavailable")
            return _INDEX
        source, model, vecs = embedded
        if len({len(v) for v in vecs}) != 1:
            _INDEX = VectorIndex(fingerprint=fingerprint, error="mixed embedding dimensions")
            return _INDEX
        vectors = {key: vec for key, vec in zip(by_key, vecs)}
        pg = _sync_pg(list(by_key.values()), vectors, model, source, fingerprint)
        _INDEX = VectorIndex(
            fingerprint=fingerprint,
            model=model,
            dim=len(vecs[0]),
            source=source,
            vectors=vectors,
            ready=True,
            pg=pg,
        )
        print(
            f"dense index: {len(vectors)} units, dim={_INDEX.dim}, source={source}, pgvector={pg}",
            file=sys.stderr,
        )
        return _INDEX


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _search_memory(qvec: list[float], allowed: dict[str, dict], k: int) -> list[tuple[float, dict]]:
    scored: list[tuple[float, dict]] = []
    for key, vec in _INDEX.vectors.items():
        row = allowed.get(key)
        if row is None or len(vec) != len(qvec):
            continue
        scored.append((_cosine(qvec, vec), row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:k]


def _search_pg(qvec: list[float], allowed: dict[str, dict], k: int) -> list[tuple[float, dict]] | None:
    url = _pg_url()
    if not url or not _INDEX.pg:
        return None
    try:
        import psycopg
    except ImportError:
        return None
    keys = list(allowed)
    literal = _vec_literal(qvec)
    try:
        with psycopg.connect(url, connect_timeout=4) as conn:
            rows = conn.execute(
                """
                SELECT unit_key, 1 - (embedding <=> %s::vector) AS score
                FROM units
                WHERE unit_key = ANY(%s)
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (literal, keys, literal, k),
            ).fetchall()
    except Exception as exc:
        print(f"pgvector query failed: {type(exc).__name__}", file=sys.stderr)
        return None
    out: list[tuple[float, dict]] = []
    for key, score in rows:
        row = allowed.get(key)
        if row is not None:
            out.append((float(score), row))
    return out


def search(question: str, allowed_rows: list[dict], k: int = 8) -> list[dict]:
    """Return allowed rows ranked by cosine similarity. Empty if the index is off."""
    if not vectors_enabled() or not allowed_rows or not (question or "").strip():
        return []
    if not _INDEX.ready:
        return []
    allowed = {unit_key(row): row for row in allowed_rows}
    embedded = _embed([question.strip()[:1800]], query=True, source=_INDEX.source)
    if not embedded:
        return []
    _source, _model, vecs = embedded
    qvec = vecs[0]
    if len(qvec) != _INDEX.dim:
        return []
    scored = _search_pg(qvec, allowed, k)
    if scored is None:
        scored = _search_memory(qvec, allowed, k)
    if not scored:
        return []
    best = scored[0][0]
    # Drop neighbours that are far from the best hit. Exact cutoff is cosine on L2-normalized vectors.
    floor = max(0.42, best * 0.82)
    return [row for score, row in scored if score >= floor][:k]
