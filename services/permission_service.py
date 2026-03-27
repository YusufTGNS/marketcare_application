from typing import Dict, Any, Iterable


def user_role(user: Dict[str, Any]) -> str:
    return str(user.get("role", "")).lower()


def is_admin(user: Dict[str, Any]) -> bool:
    return user_role(user) == "admin"


def is_personnel(user: Dict[str, Any]) -> bool:
    return user_role(user) == "personnel"


def assert_allowed(user: Dict[str, Any], allowed_roles: Iterable[str]) -> None:
    allowed = {r.lower() for r in allowed_roles}
    if user_role(user) not in allowed:
        raise PermissionError("Bu işlem için yetkiniz yok.")

