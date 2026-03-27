from typing import Optional, List, Dict, Any

from db.connection import get_connection


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, name, barcode_value, unit_price, vat_rate, expiration_date,
                   image_path, icon_path, stock_qty, critical_threshold, is_active, created_at
            FROM products WHERE id = ?
            """,
            (int(product_id),),
        ).fetchone()
        return dict(row) if row else None


def get_product_by_barcode(barcode_value: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, name, barcode_value, unit_price, vat_rate, expiration_date,
                   image_path, icon_path, stock_qty, critical_threshold, is_active, created_at
            FROM products WHERE barcode_value = ?
            """,
            (barcode_value,),
        ).fetchone()
        return dict(row) if row else None


def list_products(include_inactive: bool = False) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        if include_inactive:
            rows = conn.execute(
                """
                SELECT id, name, barcode_value, unit_price, vat_rate, expiration_date,
                       image_path, icon_path, stock_qty, critical_threshold, is_active, created_at
                FROM products ORDER BY name ASC
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, name, barcode_value, unit_price, vat_rate, expiration_date,
                       image_path, icon_path, stock_qty, critical_threshold, is_active, created_at
                FROM products WHERE is_active = 1 ORDER BY name ASC
                """
            ).fetchall()
        return [dict(r) for r in rows]


def add_or_update_product(
    *,
    product_id: Optional[int],
    name: str,
    barcode_value: str,
    unit_price: float,
    vat_rate: float,
    expiration_date: Optional[str],
    image_path: Optional[str],
    icon_path: Optional[str],
    stock_qty: int,
    critical_threshold: int,
    is_active: int = 1,
) -> int:
    with get_connection() as conn:
        if product_id is None:
            cur = conn.execute(
                """
                INSERT INTO products(
                    name, barcode_value, unit_price, vat_rate, expiration_date,
                    image_path, icon_path, stock_qty, critical_threshold, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    barcode_value,
                    float(unit_price),
                    float(vat_rate),
                    expiration_date,
                    image_path,
                    icon_path,
                    int(stock_qty),
                    int(critical_threshold),
                    int(is_active),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

        conn.execute(
            """
            UPDATE products
            SET name = ?, barcode_value = ?, unit_price = ?, vat_rate = ?, expiration_date = ?,
                image_path = ?, icon_path = ?, stock_qty = ?, critical_threshold = ?, is_active = ?
            WHERE id = ?
            """,
            (
                name,
                barcode_value,
                float(unit_price),
                float(vat_rate),
                expiration_date,
                image_path,
                icon_path,
                int(stock_qty),
                int(critical_threshold),
                int(is_active),
                int(product_id),
            ),
        )
        conn.commit()
        return int(product_id)


def update_stock_qty(product_id: int, new_qty: int) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE products SET stock_qty = ? WHERE id = ?", (int(new_qty), int(product_id)))
        conn.commit()


def update_product_active_status(product_id: int, is_active: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE products SET is_active = ? WHERE id = ?",
            (int(is_active), int(product_id)),
        )
        conn.commit()


def list_critical_products() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, barcode_value, unit_price, vat_rate, expiration_date,
                   image_path, icon_path, stock_qty, critical_threshold, created_at
            FROM products
            WHERE is_active = 1 AND stock_qty < critical_threshold
            ORDER BY stock_qty ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
