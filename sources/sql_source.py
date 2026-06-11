from __future__ import annotations
import json
import sqlite3
from openai import OpenAI
from config import DB_PATH, LLM_MODEL
from sources.base import RetrievedChunk

_SCHEMA = """
Tables in the enterprise SQLite database:

employees(id, name, department, position, salary, manager_id, hire_date, email, status)
departments(id, name, head_id, budget, headcount)
projects(id, name, department_id, budget, spent, status, start_date, end_date, lead_id)
financial_transactions(id, date, category, amount, department_id, approved_by, description)
budget_allocations(id, year, department_id, allocated, spent, category)
"""

_SQL_SYSTEM = f"""You are a SQL expert for an enterprise database.
{_SCHEMA}
Given a natural language question, write a single safe READ-ONLY SELECT query.
Return ONLY valid JSON: {{"sql": "SELECT ...", "explanation": "what the query does"}}
Rules:
- Only SELECT statements. No INSERT/UPDATE/DELETE/DROP.
- Use LIMIT 20 unless the user asks for aggregations.
- Use proper SQLite syntax.
"""


class SQLSource:
    def __init__(self) -> None:
        self._client = OpenAI()

    def retrieve(self, query: str, allowed_categories: list[str], top_k: int = 5) -> list[RetrievedChunk]:
        sql_cats = [c for c in allowed_categories if c in {"employee_db", "financial_db", "project_db"}]
        if not sql_cats:
            return []

        try:
            nl2sql = self._nl_to_sql(query, sql_cats)
            sql = nl2sql.get("sql", "")
            explanation = nl2sql.get("explanation", "")

            if not sql or not sql.strip().upper().startswith("SELECT"):
                return []

            rows, columns = self._execute(sql)
            if not rows:
                return []

            content = self._format_rows(rows, columns, explanation)
            category = self._infer_category(sql, sql_cats)

            return [RetrievedChunk(
                content=content,
                source=f"SQL: {explanation}",
                source_category=category,
                chunk_id=f"sql_{hash(sql) & 0xFFFFFFFF}",
                relevance_score=0.9,
                metadata={"sql": sql, "row_count": len(rows)},
            )]
        except Exception as exc:
            return [RetrievedChunk(
                content=f"SQL query error: {exc}",
                source="sql_error",
                source_category=sql_cats[0] if sql_cats else "unknown",
                chunk_id="sql_error",
                relevance_score=0.0,
            )]

    def _nl_to_sql(self, query: str, allowed_categories: list[str]) -> dict:
        context = f"User has access to: {', '.join(allowed_categories)}\nQuestion: {query}"
        resp = self._client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=512,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SQL_SYSTEM},
                {"role": "user",   "content": context},
            ],
        )
        return json.loads(resp.choices[0].message.content)

    def _execute(self, sql: str) -> tuple[list[tuple], list[str]]:
        # Keep only the first statement in case the model returns multiple
        sql = sql.split(";")[0].strip() + ";"
        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.execute(sql)
            columns = [d[0] for d in cur.description] if cur.description else []
            return cur.fetchall(), columns
        finally:
            conn.close()

    def _format_rows(self, rows: list[tuple], columns: list[str], explanation: str) -> str:
        lines = [f"Query result: {explanation}", ""]
        if columns:
            lines.append(" | ".join(columns))
            lines.append("-" * len(" | ".join(columns)))
        for row in rows[:20]:
            lines.append(" | ".join(str(v) for v in row))
        if len(rows) > 20:
            lines.append(f"... and {len(rows) - 20} more rows")
        return "\n".join(lines)

    def _infer_category(self, sql: str, cats: list[str]) -> str:
        sql_lower = sql.lower()
        if any(t in sql_lower for t in ("employee", "department")):
            return "employee_db" if "employee_db" in cats else cats[0]
        if any(t in sql_lower for t in ("financial", "transaction", "budget")):
            return "financial_db" if "financial_db" in cats else cats[0]
        if "project" in sql_lower:
            return "project_db" if "project_db" in cats else cats[0]
        return cats[0]
