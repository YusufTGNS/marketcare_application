from db.connection import get_connection


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
        return [dict(row) for row in rows]
