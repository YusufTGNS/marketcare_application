from typing import Optional, List, Dict, Any

import sqlite3

from db.connection import get_connection


def create_sale(
    conn: Optional[sqlite3.Connection],
    *,
    sale_no: str,
    created_by_user_id: int,
    customer_name: Optional[str],
    payment_type: Optional[str],
    total_amount: float,
    tax_amount: float,
    grand_total: float,
    pdf_slip_path: Optional[str] = None,
    pdf_invoice_path: Optional[str] = None,
) -> int:
    owns_conn = False
    if conn is None:
        owns_conn = True
        cm = get_connection()
        conn = cm.__enter__()

    try:
        cur = conn.execute(
            """
            INSERT INTO sales(
                sale_no, created_by_user_id, customer_name, payment_type,
                total_amount, tax_amount, grand_total,
                pdf_slip_path, pdf_invoice_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sale_no,
                int(created_by_user_id),
                customer_name,
                payment_type,
                float(total_amount),
                float(tax_amount),
                float(grand_total),
                pdf_slip_path,
                pdf_invoice_path,
            ),
        )
        if owns_conn:
            conn.commit()
        return int(cur.lastrowid)
    finally:
        if owns_conn:
            cm.__exit__(None, None, None)


def add_sale_item(
    conn: Optional[sqlite3.Connection],
    *,
    sale_id: int,
    product_id: int,
    qty: int,
    unit_price: float,
) -> None:
    owns_conn = False
    if conn is None:
        owns_conn = True
        cm = get_connection()
        conn = cm.__enter__()

    try:
        line_total = float(unit_price) * int(qty)
        conn.execute(
            """
            INSERT INTO sale_items(sale_id, product_id, qty, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            (int(sale_id), int(product_id), int(qty), float(unit_price), float(line_total)),
        )
        if owns_conn:
            conn.commit()
    finally:
        if owns_conn:
            cm.__exit__(None, None, None)


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
        params = []

        if start_date:
            query += " WHERE date(s.created_at) >= date(?)"
            params.append(str(start_date))

        if end_date:
            if start_date:
                query += " AND date(s.created_at) <= date(?)"
            else:
                query += " WHERE date(s.created_at) <= date(?)"
            params.append(str(end_date))

        query += " ORDER BY s.created_at DESC LIMIT ?"
        params.append(int(limit))

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]


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
        params = [int(user_id)]

        if start_date:
            query += " AND date(s.created_at) >= date(?)"
            params.append(str(start_date))

        if end_date:
            query += " AND date(s.created_at) <= date(?)"
            params.append(str(end_date))

        query += " ORDER BY s.created_at DESC LIMIT ?"
        params.append(int(limit))

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def get_sale_items(sale_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT si.id, si.qty, si.unit_price, si.vat_rate, si.tax_amount, si.line_total,
                   p.name AS product_name,
                   p.barcode_value, p.image_path
            FROM sale_items si
            JOIN products p ON p.id = si.product_id
            WHERE si.sale_id = ?
            ORDER BY si.id ASC
            """,
            (int(sale_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def get_sale_by_sale_no(sale_no: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, sale_no, created_at, created_by_user_id, customer_name, payment_type,
                   total_amount, tax_amount, grand_total,
                   pdf_slip_path, pdf_invoice_path
            FROM sales WHERE sale_no = ?
            """,
            (sale_no,),
        ).fetchone()
        return dict(row) if row else None
