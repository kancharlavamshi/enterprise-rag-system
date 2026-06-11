"""JSON logs are indexed into ChromaDB in setup_data.py.
This module handles direct structured lookups on raw JSON when needed."""
from __future__ import annotations
import json
import os
from config import LOGS_DIR
from sources.base import RetrievedChunk


class JSONSource:
    def __init__(self) -> None:
        self._logs: dict[str, list[dict]] = {}
        self._load_logs()

    def _load_logs(self) -> None:
        for fname in ("audit_log.json", "system_alerts.json", "access_log.json"):
            path = os.path.join(LOGS_DIR, fname)
            if os.path.exists(path):
                with open(path) as f:
                    self._logs[fname] = json.load(f)

    def recent_alerts(self, n: int = 5) -> list[RetrievedChunk]:
        alerts = self._logs.get("system_alerts.json", [])[-n:]
        if not alerts:
            return []
        content = "\n".join(
            f"[{a.get('timestamp')}] {a.get('severity', 'INFO').upper()}: {a.get('message', '')}"
            for a in alerts
        )
        return [
            RetrievedChunk(
                content=content,
                source="system_alerts.json",
                source_category="system_alerts",
                chunk_id="alerts_recent",
                relevance_score=0.85,
            )
        ]

    def search_audit(self, keyword: str) -> list[RetrievedChunk]:
        entries = self._logs.get("audit_log.json", [])
        matches = [
            e for e in entries
            if keyword.lower() in json.dumps(e).lower()
        ][:10]
        if not matches:
            return []
        content = json.dumps(matches, indent=2)
        return [
            RetrievedChunk(
                content=content,
                source="audit_log.json",
                source_category="audit_logs",
                chunk_id=f"audit_{hash(keyword) & 0xFFFFFF}",
                relevance_score=0.80,
            )
        ]
