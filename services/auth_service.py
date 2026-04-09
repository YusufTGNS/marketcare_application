import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

import hashlib

from db.init_db import bootstrap_db
from repositories.users_repo import get_user_by_username, set_last_login_now


SESSION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "session.json"
)


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    user: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def hash_password(password: str, *, salt: Optional[bytes] = None, iterations: int = 200_000) -> str:
    if salt is None:
        salt = secrets.token_bytes(16)
    pwd_bytes = password.encode("utf-8")
    dk = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, iterations)
    return f"{salt.hex()}${dk.hex()}"


def verify_password(password: str, password_hash: str, *, iterations: int = 200_000) -> bool:
    try:
        salt_hex, hash_hex = password_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        pwd_bytes = password.encode("utf-8")
        actual = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, iterations)
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False


def _read_session() -> Optional[Dict[str, Any]]:
    if not os.path.exists(SESSION_PATH):
        return None
    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_session(session: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)


def clear_session() -> None:
    try:
        if os.path.exists(SESSION_PATH):
            os.remove(SESSION_PATH)
    except Exception:
        pass


def _clear_generated_documents() -> None:
    documents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")
    if not os.path.isdir(documents_dir):
        return

    for name in os.listdir(documents_dir):
        path = os.path.join(documents_dir, name)
        if not os.path.isfile(path):
            continue
        if name.lower() == "pdf_generator.py":
            continue
        if name.lower().endswith(".pdf"):
            try:
                os.remove(path)
            except Exception:
                pass


def _clear_generated_assets() -> None:
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    target_dirs = [
        os.path.join(assets_dir, "barcodes"),
        os.path.join(assets_dir, "product_images"),
    ]

    for target_dir in target_dirs:
        if not os.path.isdir(target_dir):
            continue
        for name in os.listdir(target_dir):
            path = os.path.join(target_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                os.remove(path)
            except Exception:
                pass


def login(username: str, password: str) -> AuthResult:
    bootstrap_db()
    username = str(username or "").strip()
    user = get_user_by_username(username)
    if not user:
        return AuthResult(ok=False, error="Kullanıcı bulunamadı.")
    if not user.get("is_active", 1):
        return AuthResult(ok=False, error="Kullanıcı pasif.")

    if not verify_password(password, user["password_hash"]):
        return AuthResult(ok=False, error="Şifre hatalı.")

    set_last_login_now(int(user["id"]))
    user = get_user_by_username(username)
    return AuthResult(ok=True, user=user)


def login_with_remember(username: str) -> str:
    token = secrets.token_urlsafe(32)
    session = {
        "session_token": token,
        "username": username,
        "remembered_at": datetime.now().isoformat(timespec="seconds"),
    }
    _write_session(session)
    return token


def create_user(username: str, password: str, role: str = "personnel") -> Dict[str, Any]:
    bootstrap_db()
    username = str(username or "").strip()
    password = str(password or "")

    if not username or not password:
        raise ValueError("Kullanıcı adı ve parola zorunludur.")
    if len(username) < 3:
        raise ValueError("Kullanıcı adı en az 3 karakter olmalıdır.")
    if len(password) < 4:
        raise ValueError("Parola en az 4 karakter olmalıdır.")

    role = str(role).strip().lower()
    if role not in ("admin", "personnel"):
        raise ValueError("Rol admin veya personnel olmalıdır.")

    from repositories.users_repo import get_user_by_username, create_user as repo_create_user

    existing = get_user_by_username(username)
    if existing:
        raise ValueError("Bu kullanıcı adı zaten mevcut.")

    password_hash = hash_password(password)
    user_id = repo_create_user(username=username, password_hash=password_hash, role=role, is_active=1)
    return {
        "id": user_id,
        "username": username,
        "role": role,
        "is_active": 1,
    }


def reset_database() -> None:
    from db.connection import get_db_path

    db_path = get_db_path()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception:
        pass

    _clear_generated_documents()
    _clear_generated_assets()
    bootstrap_db()
    clear_session()


def try_auto_login_from_session() -> AuthResult:
    bootstrap_db()
    session = _read_session()
    if not session:
        return AuthResult(ok=False, error=None)

    username = session.get("username")
    if not username:
        return AuthResult(ok=False, error=None)

    user = get_user_by_username(username)
    if not user or not user.get("is_active", 1):
        clear_session()
        return AuthResult(ok=False, error=None)

    return AuthResult(ok=True, user=user)
