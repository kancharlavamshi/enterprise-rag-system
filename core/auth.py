from __future__ import annotations
from dataclasses import dataclass
from config import USERS, ROLE_PERMISSIONS


@dataclass
class User:
    user_id: str
    name: str
    role: str
    department: str
    permissions: list[str]


class RBACAuthenticator:
    def get_user(self, user_id: str) -> User:
        if user_id not in USERS:
            raise PermissionError(f"Unknown user: {user_id!r}")
        info = USERS[user_id]
        role = info["role"]
        return User(
            user_id=user_id,
            name=info["name"],
            role=role,
            department=info["department"],
            permissions=ROLE_PERMISSIONS.get(role, []),
        )

    def can_access(self, user: User, category: str) -> bool:
        return category in user.permissions

    def filter_categories(self, user: User, requested: list[str]) -> tuple[list[str], list[str]]:
        allowed = [c for c in requested if self.can_access(user, c)]
        denied  = [c for c in requested if not self.can_access(user, c)]
        return allowed, denied
