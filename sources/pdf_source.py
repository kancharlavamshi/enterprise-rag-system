from __future__ import annotations
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from config import VECTOR_STORE_PATH, TOP_K_RESULTS
from sources.base import RetrievedChunk


class VectorSource:
    """Retrieves from ChromaDB; covers docs, logs, and alerts."""

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
        self._embed_fn = DefaultEmbeddingFunction()
        self._collection = self._client.get_or_create_collection(
            name="enterprise_docs",
            embedding_function=self._embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def retrieve(
        self,
        query: str,
        allowed_categories: list[str],
        top_k: int = TOP_K_RESULTS,
    ) -> list[RetrievedChunk]:
        if not allowed_categories or self._collection.count() == 0:
            return []

        where = (
            {"source_category": {"$in": allowed_categories}}
            if len(allowed_categories) > 1
            else {"source_category": allowed_categories[0]}
        )

        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, self._collection.count()),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        chunks: list[RetrievedChunk] = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                RetrievedChunk(
                    content=doc,
                    source=meta.get("source_file", "unknown"),
                    source_category=meta.get("source_category", "unknown"),
                    chunk_id=meta.get("chunk_id", ""),
                    relevance_score=round(1.0 - dist, 4),  # cosine → similarity
                    metadata=meta,
                )
            )

        return sorted(chunks, key=lambda c: c.relevance_score, reverse=True)

    def add_documents(self, chunks: list[dict]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
            ids=[c["id"] for c in chunks],
        )
