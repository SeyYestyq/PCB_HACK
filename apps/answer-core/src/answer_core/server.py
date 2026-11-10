from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .pipeline import answer_question, default_kb_path, load_kb


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """Build the pgvector/in-memory dense index once, before the first question."""
    try:
        from psb_vectors import ensure_index, vectors_enabled

        if vectors_enabled():
            ensure_index(load_kb(default_kb_path()))
    except Exception as exc:
        print(f"dense index skipped: {type(exc).__name__}")
    yield


app = FastAPI(title="PSB Legal Answer Core", version="0.2.0", lifespan=_lifespan)

origins = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HistoryTurn(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    history: list[HistoryTurn] = Field(default_factory=list)


class CitationOut(BaseModel):
    doc_id: str
    title: str
    span: str
    quote: str


class AskResponse(BaseModel):
    status: str
    answer: str
    citations: list[CitationOut]
    missing: list[str]
    options: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    vectors: dict[str, Any] = {"enabled": False}
    try:
        from psb_vectors import status

        vectors = status()
    except Exception as exc:
        vectors = {"enabled": False, "error": type(exc).__name__}
    return {"ok": True, "service": "psb-answer-core", "vectors": vectors}


@app.post("/api/v1/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    kb = default_kb_path()
    history: list[dict[str, Any]] = [
        {"role": t.role, "content": t.content} for t in body.history[-10:]
    ]
    result = answer_question(body.question, kb, history=history)
    return AskResponse(
        status=result.status,
        answer=result.answer,
        citations=[CitationOut(**c.__dict__) for c in result.citations],
        missing=result.missing,
        options=list(getattr(result, "options", []) or []),
    )


@app.get("/api/v1/kb")
def kb_info() -> dict:
    path = default_kb_path()
    return {"psb_kb_path": str(path), "exists": path.exists(), "env": os.getenv("PSB_KB_PATH", "")}
