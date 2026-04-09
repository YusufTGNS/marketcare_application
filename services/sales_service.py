from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from db.connection import get_connection
from repositories.products_repo import get_product_by_barcode
from repositories.users_repo import get_user_by_id
from services.permission_service import user_role
from utilities.vat_utils import split_gross_price


@dataclass(frozen=True)
class SaleLineInput:
    barcode_value: str
    qty: int


def _generate_sale_no(conn) -> str:
    today = datetime.now().strftime("%Y%m%d")
    row = conn.execute(
        """
        SELECT COALESCE(MAX(substr(sale_no, -4)), 0) AS last_seq
        FROM sales
        WHERE sale_no LIKE ?
        """,
        (f"MC-{today}-%",),
    ).fetchone()
    last_seq = int(row["last_seq"]) if row and row["last_seq"] is not None else 0
    return f"MC-{today}-{last_seq + 1:04d}"


def _generate_sale_documents(
    *,
    pdf_generator,
    sale_no: str,
    created_at: str,
    customer_name: Optional[str],
    payment_type: Optional[str],
    total_amount: float,
    tax_amount: float,
    grand_total: float,
    items,
) -> tuple[Optional[str], Optional[str], List[str]]:
    slip_path: Optional[str] = None
    invoice_path: Optional[str] = None
    warnings: List[str] = []

    try:
        slip_path = pdf_generator.generate_slip_pdf(
            sale_no=sale_no,
            created_at=created_at,
            customer_name=customer_name,
            payment_type=payment_type,
            total_amount=total_amount,
            tax_amount=tax_amount,
            grand_total=grand_total,
            items=items,
        )
    except Exception as exc:
        warnings.append(f"Slip oluşturulamadı: {exc}")

    try:
        invoice_path = pdf_generator.generate_invoice_pdf(
            sale_no=sale_no,
            created_at=created_at,
            customer_name=customer_name,
            payment_type=payment_type,
            total_amount=total_amount,
            tax_amount=tax_amount,
            grand_total=grand_total,
            items=items,
        )
    except Exception as exc:
        warnings.append(f"Fatura oluşturulamadı: {exc}")

    return slip_path, invoice_path, warnings


def perform_sale(
    *,
    lines: List[SaleLineInput],
    created_by_user_id: int,
    customer_name: Optional[str],
    payment_type: Optional[str],
    pdf_generator,
) -> Dict[str, Any]:
    if not lines:
        raise ValueError("Sepet boş olamaz.")

    customer_name = str(customer_name or "").strip() or None
    payment_type = str(payment_type or "").strip() or "Belirtilmedi"

    user = get_user_by_id(int(created_by_user_id))
    role = user_role(user or {})
    if role not in ("admin", "personnel"):
        raise PermissionError("Satış yapmak için yetkiniz yok.")

    prepared: List[Dict[str, Any]] = []
    gross_total = 0.0
    net_total = 0.0
    tax_total = 0.0

    for line in lines:
        barcode = str(line.barcode_value).strip()
        qty = int(line.qty)
        if not barcode:
            raise ValueError("Barkod boş olamaz.")
        if qty <= 0:
            raise ValueError("Miktar 1'den küçük olamaz.")

        product = get_product_by_barcode(barcode)
        if not product or int(product.get("is_active", 1)) == 0:
            raise ValueError(f"Barkod için ürün bulunamadı: {barcode}")

        stock_qty = int(product.get("stock_qty") or 0)
        if stock_qty < qty:
            raise ValueError(f"Yetersiz stok: {product['name']} (Mevcut: {stock_qty}, İstenen: {qty})")

        unit_price = float(product.get("unit_price") or 0)
        vat_rate = float(product.get("vat_rate") or 0)
        line_total = unit_price * qty
        line_net, line_tax = split_gross_price(line_total, vat_rate)

        gross_total += line_total
        net_total += line_net
        tax_total += line_tax

        prepared.append(
            {
                "product_id": int(product["id"]),
                "barcode_value": str(product["barcode_value"]),
                "product_name": str(product["name"]),
                "unit_price": unit_price,
                "vat_rate": vat_rate,
                "qty": qty,
                "line_total": line_total,
                "line_net_total": line_net,
                "line_tax_total": line_tax,
                "icon_path": product.get("icon_path"),
                "image_path": product.get("image_path"),
            }
        )

    sale_row: Optional[Dict[str, Any]] = None
    sale_no: Optional[str] = None

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        sale_no = _generate_sale_no(conn)

        cur = conn.execute(
            """
            INSERT INTO sales(
                sale_no, created_by_user_id, customer_name, payment_type,
                total_amount, tax_amount, grand_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sale_no,
                int(created_by_user_id),
                customer_name,
                payment_type,
                float(net_total),
                float(tax_total),
                float(gross_total),
            ),
        )
        sale_id = int(cur.lastrowid)

        for product in prepared:
            product_id = int(product["product_id"])
            qty = int(product["qty"])
            qty_before = conn.execute(
                "SELECT stock_qty FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()["stock_qty"]
            qty_before = int(qty_before)
            qty_after = qty_before - qty
            if qty_after < 0:
                raise ValueError(f"Yetersiz stok (transaction): {product['product_name']}")

            conn.execute(
                """
                INSERT INTO sale_items(
                    sale_id, product_id, qty, unit_price, vat_rate, tax_amount, line_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sale_id,
                    product_id,
                    qty,
                    float(product["unit_price"]),
                    float(product["vat_rate"]),
                    float(product["line_tax_total"]),
                    float(product["line_total"]),
                ),
            )
            conn.execute(
                "UPDATE products SET stock_qty = ? WHERE id = ?",
                (qty_after, product_id),
            )
            conn.execute(
                """
                INSERT INTO stock_movements(
                    product_id, delta_qty, movement_type, qty_before, qty_after, note, user_id
                ) VALUES (?, ?, 'out', ?, ?, ?, ?)
                """,
                (product_id, qty, qty_before, qty_after, f"Satış: {sale_no}", int(created_by_user_id)),
            )

        conn.commit()
        sale_row = {
            "sale_id": sale_id,
            "sale_no": sale_no,
            "customer_name": customer_name,
            "payment_type": payment_type,
            "total_amount": net_total,
            "tax_amount": tax_total,
            "grand_total": gross_total,
        }

    from documents.pdf_generator import SaleItemView

    items_view: List[SaleItemView] = []
    for product in prepared:
        line_net_total = float(product["line_net_total"])
        qty = int(product["qty"])
        items_view.append(
            SaleItemView(
                product_name=product["product_name"],
                barcode_value=product["barcode_value"],
                image_path=product.get("image_path"),
                icon_path=product.get("icon_path"),
                qty=qty,
                unit_price=float(product["unit_price"]),
                unit_net_price=(line_net_total / qty) if qty else 0.0,
                vat_rate=float(product["vat_rate"]),
                tax_amount=float(product["line_tax_total"]),
                line_total=float(product["line_total"]),
            )
        )

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_connection() as conn:
            row = conn.execute("SELECT created_at FROM sales WHERE sale_no = ?", (sale_no,)).fetchone()
            if row:
                created_at = str(row["created_at"])
    except Exception:
        pass

    slip_path, invoice_path, document_warnings = _generate_sale_documents(
        pdf_generator=pdf_generator,
        sale_no=sale_no,
        created_at=created_at,
        customer_name=customer_name,
        payment_type=payment_type,
        total_amount=net_total,
        tax_amount=tax_total,
        grand_total=gross_total,
        items=items_view,
    )

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sales
            SET pdf_slip_path = ?, pdf_invoice_path = ?
            WHERE sale_no = ?
            """,
            (slip_path, invoice_path, sale_no),
        )
        conn.commit()

    return {
        **(sale_row or {}),
        "sale_no": sale_no,
        "created_at": created_at,
        "slip_path": slip_path,
        "invoice_path": invoice_path,
        "total_amount": net_total,
        "tax_amount": tax_total,
        "grand_total": gross_total,
        "items": items_view,
        "document_warnings": document_warnings,
    }
