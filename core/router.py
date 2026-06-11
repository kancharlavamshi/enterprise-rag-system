from __future__ import annotations
from config import INTENT_SOURCE_MAP, VECTOR_CATEGORIES, SQL_CATEGORIES
from core.auth import User


class QueryRouter:
    def route(self, intents: list[str], user: User) -> dict[str, list[str]]:
        """
        Returns {"vector": [...categories], "sql": [...categories]}
        filtered to the user's permissions.
        """
        candidate_categories: set[str] = set()
        for intent in intents:
            candidate_categories.update(INTENT_SOURCE_MAP.get(intent, []))

        # RBAC filter
        allowed = {c for c in candidate_categories if c in user.permissions}
        denied  = candidate_categories - allowed

        vector_cats = sorted(allowed & VECTOR_CATEGORIES)
        sql_cats    = sorted(allowed & SQL_CATEGORIES)

        return {
            "vector":  vector_cats,
            "sql":     sql_cats,
            "denied":  sorted(denied),
            "intents": intents,
        }
