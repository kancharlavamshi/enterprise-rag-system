from __future__ import annotations
from sources.base import RetrievedChunk
from sources.pdf_source import VectorSource
from sources.sql_source import SQLSource
from sources.json_source import JSONSource
from config import TOP_K_RESULTS


class MultiSourceRetriever:
    def __init__(self) -> None:
        self._vector = VectorSource()
        self._sql    = SQLSource()
        self._json   = JSONSource()

    def retrieve(
        self,
        query: str,
        routing: dict,
    ) -> list[RetrievedChunk]:
        all_chunks: list[RetrievedChunk] = []

        # ── Vector / document retrieval ─────────────────────────────────────
        vector_cats = routing.get("vector", [])
        if vector_cats:
            chunks = self._vector.retrieve(query, vector_cats, top_k=TOP_K_RESULTS)
            all_chunks.extend(chunks)

        # ── SQL retrieval ───────────────────────────────────────────────────
        sql_cats = routing.get("sql", [])
        if sql_cats:
            chunks = self._sql.retrieve(query, sql_cats)
            all_chunks.extend(chunks)

        # ── JSON / log augmentation ─────────────────────────────────────────
        intents = routing.get("intents", [])
        if "INCIDENT" in intents and "system_alerts" in vector_cats:
            all_chunks.extend(self._json.recent_alerts())
        if "AUDIT" in intents and "audit_logs" in vector_cats:
            all_chunks.extend(self._json.search_audit(query))

        # Sort by relevance, deduplicate by chunk_id
        seen: set[str] = set()
        unique: list[RetrievedChunk] = []
        for c in sorted(all_chunks, key=lambda x: x.relevance_score, reverse=True):
            if c.chunk_id not in seen:
                seen.add(c.chunk_id)
                unique.append(c)

        return unique[:TOP_K_RESULTS * 2]  # cap context size

    def add_to_index(self, chunks: list[dict]) -> None:
        self._vector.add_documents(chunks)
