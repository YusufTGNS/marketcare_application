from typing import Optional, Dict, Any

from db.connection import get_connection
from repositories.users_repo import get_user_by_id
from services.permission_service import is_admin


def adjust_stock(
    *,
    product_id: int,
    delta_qty: int,
    movement_type: str,
    user_id: int,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    movement_type: 'in' or 'out'
    delta_qty her zaman pozitif kabul edilir.
    """
    movement_type = str(movement_type).lower()
    if movement_type not in ("in", "out"):
        raise ValueError("movement_type 'in' veya 'out' olmalı.")

    user = get_user_by_id(int(user_id))
    if not user or not is_admin(user):
        raise PermissionError("Bu işlem için admin yetkisi gerekir.")

    delta_qty = int(delta_qty)
    if delta_qty <= 0:
        raise ValueError("delta_qty pozitif olmalı.")

    with get_connection() as conn:
        row = conn.execute("SELECT stock_qty FROM products WHERE id = ? AND is_active = 1", (int(product_id),)).fetchone()
        if not row:
            raise ValueError("Ürün bulunamadı.")

        qty_before = int(row["stock_qty"])
        qty_after = qty_before + delta_qty if movement_type == "in" else qty_before - delta_qty

        if movement_type == "out" and qty_after < 0:
            raise ValueError(f"Yetersiz stok! Mevcut: {qty_before}")

        conn.execute("UPDATE products SET stock_qty = ? WHERE id = ?", (qty_after, int(product_id)))
        conn.execute(
            """
            INSERT INTO stock_movements(
                product_id, delta_qty, movement_type, qty_before, qty_after, note, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (int(product_id), delta_qty, movement_type, qty_before, qty_after, note, int(user_id)),
        )
        conn.commit()

        return {
            "product_id": int(product_id),
            "qty_before": qty_before,
            "qty_after": qty_after,
            "movement_type": movement_type,
        }

