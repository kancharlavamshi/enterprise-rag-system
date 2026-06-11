from __future__ import annotations
import re
from openai import OpenAI
from sources.base import RetrievedChunk
from config import LLM_MODEL

_SYSTEM = """You are an enterprise AI assistant. Generate accurate, grounded answers
using ONLY the provided context. Never fabricate information.

Rules:
1. Base every claim on the provided context chunks.
2. Cite sources using [SOURCE_N] markers inline.
3. If context is insufficient, say so explicitly.
4. At the end, list all cited sources.
5. Provide a confidence level: HIGH / MEDIUM / LOW.

Format your response exactly as:
<answer>
Your answer with [SOURCE_1], [SOURCE_2] citations inline.
</answer>
<confidence>HIGH|MEDIUM|LOW — reason</confidence>
<sources>
[SOURCE_1] source_category | file_name
[SOURCE_2] ...
</sources>
"""


class AnswerGenerator:
    def __init__(self) -> None:
        self._client = OpenAI()

    def generate(self, query: str, chunks: list[RetrievedChunk], user_name: str, denied_categories: list[str]) -> dict:
        if not chunks:
            return self._no_context_response(query, denied_categories)

        context_block = self._build_context(chunks)
        user_msg = f"User: {user_name}\nQuestion: {query}\n\nContext:\n{context_block}"

        resp = self._client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user",   "content": user_msg},
            ],
        )
        raw = resp.choices[0].message.content

        return {
            "answer":            self._extract_tag(raw, "answer"),
            "confidence":        self._extract_tag(raw, "confidence"),
            "sources":           self._extract_tag(raw, "sources"),
            "raw_response":      raw,
            "retrieval_trace":   self._build_trace(chunks),
            "denied_categories": denied_categories,
            "chunks_used":       len(chunks),
        }

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(
                f"[SOURCE_{i}] ({c.source_category} | {c.source} | score={c.relevance_score})\n{c.content}\n"
            )
        return "\n---\n".join(parts)

    def _build_trace(self, chunks: list[RetrievedChunk]) -> list[dict]:
        return [
            {
                "rank":            i + 1,
                "chunk_id":        c.chunk_id,
                "source":          c.source,
                "source_category": c.source_category,
                "relevance_score": c.relevance_score,
                "content_preview": c.content[:120] + "..." if len(c.content) > 120 else c.content,
            }
            for i, c in enumerate(chunks)
        ]

    def _no_context_response(self, query: str, denied: list[str]) -> dict:
        if denied:
            answer = (
                f"You do not have access to the data sources required to answer this query. "
                f"Restricted categories: {', '.join(denied)}. "
                f"Please contact your administrator if you believe this is incorrect."
            )
            confidence = "LOW — access denied to relevant sources"
        else:
            answer = "No relevant information was found in the accessible data sources for your query."
            confidence = "LOW — no matching context"
        return {
            "answer": answer, "confidence": confidence, "sources": "",
            "raw_response": "", "retrieval_trace": [],
            "denied_categories": denied, "chunks_used": 0,
        }

    @staticmethod
    def _extract_tag(text: str, tag: str) -> str:
        m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        return m.group(1).strip() if m else text.strip()
