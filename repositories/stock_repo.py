from typing import Optional

from db.connection import get_connection


def record_stock_movement(
    *,
    product_id: int,
    delta_qty: int,
    movement_type: str,
    qty_before: int,
    qty_after: int,
    user_id: int,
    note: Optional[str] = None,
) -> int:
    """
    Tek başına stok miktarını değiştirmez; yalnızca hareket kaydını yazar.
    Stok miktarı genelde service katmanında transaction içinde güncellenir.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO stock_movements(
                product_id, delta_qty, movement_type, qty_before, qty_after, note, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(product_id),
                int(delta_qty),
                movement_type,
                int(qty_before),
                int(qty_after),
                note,
                int(user_id),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_stock_movements(limit: int = 200):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sm.id, sm.product_id, p.name AS product_name,
                   sm.delta_qty, sm.movement_type, sm.qty_before, sm.qty_after,
                   sm.note, sm.created_at, sm.user_id, u.username AS user_name
            FROM stock_movements sm
            JOIN products p ON p.id = sm.product_id
            JOIN users u ON u.id = sm.user_id
            ORDER BY sm.created_at DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
        return [dict(r) for r in rows]

