from typing import Any, Dict, List, Optional

from db.connection import get_connection


def list_sales(
    limit: int = 200,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        query = """
            SELECT s.id, s.sale_no, s.created_at,
                   u.username AS created_by,
                   s.customer_name, s.payment_type,
                   s.total_amount, s.tax_amount, s.grand_total,
                   s.pdf_slip_path, s.pdf_invoice_path
            FROM sales s
            JOIN users u ON u.id = s.created_by_user_id
        """
        params: List[Any] = []

        if start_date:
            query += " WHERE date(s.created_at) >= date(?)"
            params.append(str(start_date))

        if end_date:
            query += " AND date(s.created_at) <= date(?)" if start_date else " WHERE date(s.created_at) <= date(?)"
            params.append(str(end_date))

        query += " ORDER BY s.created_at DESC LIMIT ?"
        params.append(int(limit))

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def list_sales_for_user(
    user_id: int,
    limit: int = 200,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        query = """
            SELECT s.id, s.sale_no, s.created_at,
                   s.customer_name, s.payment_type,
                   s.total_amount, s.tax_amount, s.grand_total,
                   s.pdf_slip_path, s.pdf_invoice_path
            FROM sales s
            WHERE s.created_by_user_id = ?
        """
        params: List[Any] = [int(user_id)]

        if start_date:
            query += " AND date(s.created_at) >= date(?)"
            params.append(str(start_date))

        if end_date:
            query += " AND date(s.created_at) <= date(?)"
            params.append(str(end_date))

        query += " ORDER BY s.created_at DESC LIMIT ?"
        params.append(int(limit))

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]
