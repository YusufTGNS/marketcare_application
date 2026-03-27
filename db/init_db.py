import os
from pathlib import Path

from .connection import get_connection


def init_db() -> None:
    """
    Uygulama ilk çalıştırıldığında şemayı kurar.
    """
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")

    with get_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()


def ensure_default_admin() -> None:
    """
    İlk kurulumda admin yoksa varsayılan admin oluşturur.
    """
    from services.auth_service import hash_password  # local import to avoid cycles

    with get_connection() as conn:
        row_admin = conn.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
        if not row_admin:
            # Varsayılan admin: kullanıcı adı/admin, şifre/admin123
            username = "admin"
            password = "admin123"
            pw_hash = hash_password(password)
            conn.execute(
                """
                INSERT INTO users(username, password_hash, role, is_active)
                VALUES (?, ?, 'admin', 1)
                """,
                (username, pw_hash),
            )

        row_personnel = conn.execute("SELECT id FROM users WHERE role='personnel' LIMIT 1").fetchone()
        if not row_personnel:
            # Varsayılan personel: kullanıcı adı/personel, şifre/personel123
            username = "personel"
            password = "personel123"
            pw_hash = hash_password(password)
            conn.execute(
                """
                INSERT INTO users(username, password_hash, role, is_active)
                VALUES (?, ?, 'personnel', 1)
                """,
                (username, pw_hash),
            )

        conn.commit()


def bootstrap_db() -> None:
    init_db()
    with get_connection() as conn:
        user_cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "last_login_at" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN last_login_at TEXT NULL")
            conn.commit()
        product_cols = [row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()]
        if "vat_rate" not in product_cols:
            conn.execute("ALTER TABLE products ADD COLUMN vat_rate REAL NOT NULL DEFAULT 20")
            conn.commit()
        sale_item_cols = [row[1] for row in conn.execute("PRAGMA table_info(sale_items)").fetchall()]
        if "vat_rate" not in sale_item_cols:
            conn.execute("ALTER TABLE sale_items ADD COLUMN vat_rate REAL NOT NULL DEFAULT 20")
            conn.commit()
        if "tax_amount" not in sale_item_cols:
            conn.execute("ALTER TABLE sale_items ADD COLUMN tax_amount REAL NOT NULL DEFAULT 0")
            conn.commit()
    ensure_default_admin()
