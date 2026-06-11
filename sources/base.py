from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RetrievedChunk:
    content: str
    source: str          # file / table name
    source_category: str # e.g. "hr_docs"
    chunk_id: str
    relevance_score: float
    metadata: dict = field(default_factory=dict)

    def citation(self) -> str:
        return f"[{self.source_category}] {self.source} (score: {self.relevance_score:.2f})"
