from __future__ import annotations
import json
import re
from openai import OpenAI
from config import LLM_MODEL


_SYSTEM = """You are an intent classifier for an enterprise RAG system.
Classify the following query into one or more of these categories:
- HR_POLICY: vacation, benefits, leave, conduct, employee policies
- FINANCIAL: budget, revenue, expenses, financial reports, transactions
- TECHNICAL: system architecture, APIs, technical documentation, infrastructure
- COMPLIANCE: GDPR, SOX, regulations, compliance policies, legal
- EMPLOYEE: employee records, departments, org chart, salaries
- INCIDENT: security incidents, alerts, system outages, breach reports
- AUDIT: audit logs, access logs, user activity tracking
- GENERAL: anything else

Return ONLY valid JSON: {"intents": ["INTENT1"], "confidence": 0.95, "reasoning": "brief reason"}"""


class IntentDetector:
    def __init__(self) -> None:
        self._client = OpenAI()

    def detect(self, query: str) -> dict:
        try:
            resp = self._client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=256,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user",   "content": query},
                ],
            )
            raw = resp.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception:
            return {"intents": ["GENERAL"], "confidence": 0.5, "reasoning": "fallback"}
