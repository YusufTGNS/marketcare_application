from datetime import datetime
from typing import Any, Dict, List, Optional

from db.connection import get_connection


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role, is_active, created_at, last_login_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role, is_active, created_at, last_login_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def list_users() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, username, role, is_active, created_at, last_login_at FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def create_user(username: str, password_hash: str, role: str, is_active: int = 1) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users(username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, int(is_active)),
        )
        conn.commit()
        return int(cur.lastrowid)


def set_last_login_now(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), int(user_id)),
        )
        conn.commit()
