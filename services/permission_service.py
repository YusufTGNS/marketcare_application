from typing import Any, Dict


def user_role(user: Dict[str, Any]) -> str:
    return str(user.get("role", "")).lower()


def is_admin(user: Dict[str, Any]) -> bool:
    return user_role(user) == "admin"
