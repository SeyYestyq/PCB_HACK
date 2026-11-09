from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .pipeline import answer_question

app = FastAPI(title="PSB Legal Answer Core", version="0.1.0")

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


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    history: list[dict] = Field(default_factory=list)


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


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "psb-answer-core"}


@app.post("/api/v1/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    kb = os.getenv("PSB_KB_PATH")
    result = answer_question(body.question, Path(kb) if kb else None)
    return AskResponse(
        status=result.status,
        answer=result.answer,
        citations=[CitationOut(**c.__dict__) for c in result.citations],
        missing=result.missing,
    )
