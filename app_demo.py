"""
v1 — Demo version (public)
User selector dropdown, no authentication required.
"""
from __future__ import annotations
import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from config import USERS, ROLE_PERMISSIONS
from core.auth import RBACAuthenticator
from core.intent import IntentDetector
from core.router import QueryRouter
from core.retriever import MultiSourceRetriever
from core.generator import AnswerGenerator

app = FastAPI(
    title="Enterprise RAG Intelligence System — Demo",
    description="Secure, multi-source RAG with RBAC, citations, and explainability",
    version="1.0.0",
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

auth      = RBACAuthenticator()
intent_d  = IntentDetector()
router    = QueryRouter()
retriever = MultiSourceRetriever()
generator = AnswerGenerator()


class QueryRequest(BaseModel):
    user_id:     str
    query:       str
    max_results: int = 5


class QueryResponse(BaseModel):
    user:               dict
    query:              str
    intents:            list[str]
    intent_confidence:  float
    sources_queried:    list[str]
    denied_categories:  list[str]
    answer:             str
    confidence:         str
    citations:          str
    retrieval_trace:    list[dict]
    chunks_used:        int
    latency_ms:         float


@app.get("/health")
def health():
    return {"status": "ok", "service": "Enterprise RAG v1 Demo"}


@app.get("/users")
def list_users():
    return [
        {"user_id": uid, "name": info["name"], "role": info["role"],
         "department": info["department"],
         "permissions": ROLE_PERMISSIONS.get(info["role"], [])}
        for uid, info in USERS.items()
    ]


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    t0 = time.monotonic()
    try:
        user = auth.get_user(req.user_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    intent_result = intent_d.detect(req.query)
    intents       = intent_result.get("intents", ["GENERAL"])
    confidence    = intent_result.get("confidence", 0.5)
    routing       = router.route(intents, user)
    chunks        = retriever.retrieve(req.query, routing)
    result        = generator.generate(
        query=req.query, chunks=chunks,
        user_name=user.name,
        denied_categories=routing.get("denied", []),
    )
    latency = round((time.monotonic() - t0) * 1000, 1)

    return QueryResponse(
        user={"user_id": user.user_id, "name": user.name,
              "role": user.role, "department": user.department},
        query=req.query, intents=intents, intent_confidence=confidence,
        sources_queried=routing.get("vector", []) + routing.get("sql", []),
        denied_categories=routing.get("denied", []),
        answer=result["answer"], confidence=result["confidence"],
        citations=result["sources"], retrieval_trace=result["retrieval_trace"],
        chunks_used=result["chunks_used"], latency_ms=latency,
    )


@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
