from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from documents.pdf_generator import PDFGenerator
from repositories.products_repo import get_product_by_barcode, list_products
from services.sales_service import SaleLineInput, perform_sale
from ui.style import C, TABLE_SS, btn_danger_ss, btn_primary_ss, btn_success_ss, card_ss, combo_ss, info_box_ss, input_ss, shadow
from utilities.emoji_utils import emoji_for_product


class PersonnelSalesPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        self._cart: Dict[str, Dict[str, Any]] = {}
        self._product_rows = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        title = QLabel("Satış")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        lay.addWidget(title)

        top_card = QFrame()
        top_card.setStyleSheet(card_ss())
        shadow(top_card)
        top_lay = QHBoxLayout(top_card)
        top_lay.setContentsMargins(18, 16, 18, 16)
        top_lay.setSpacing(12)
        lay.addWidget(top_card)

        barcode_label = QLabel("Barkod")
        barcode_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        top_lay.addWidget(barcode_label)

        self.inp_barcode = QLineEdit()
        self.inp_barcode.setPlaceholderText("Barkodu okutun veya yazın")
        self.inp_barcode.setStyleSheet(input_ss())
        self.inp_barcode.returnPressed.connect(self._add_by_barcode)
        top_lay.addWidget(self.inp_barcode, 1)

        btn_barcode_add = QPushButton("Ekle")
        btn_barcode_add.setStyleSheet(btn_primary_ss())
        btn_barcode_add.setCursor(Qt.PointingHandCursor)
        btn_barcode_add.clicked.connect(self._add_by_barcode)
        top_lay.addWidget(btn_barcode_add)

        content_row = QHBoxLayout()
        content_row.setSpacing(16)
        lay.addLayout(content_row, stretch=1)

        cart_card = QFrame()
        cart_card.setStyleSheet(card_ss())
        shadow(cart_card)
        cart_lay = QVBoxLayout(cart_card)
        cart_lay.setContentsMargins(16, 16, 16, 16)
        cart_lay.setSpacing(12)
        content_row.addWidget(cart_card, 3)

        cart_header = QHBoxLayout()
        cart_header.setSpacing(12)
        cart_lay.addLayout(cart_header)

        sub = QLabel("Sepet")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        cart_header.addWidget(sub)
        cart_header.addStretch()

        qty_badge = QLabel("Ürün Adedi")
        qty_badge.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        cart_header.addWidget(qty_badge)

        self.spn_product_count = QSpinBox()
        self.spn_product_count.setRange(0, 9999)
        self.spn_product_count.setValue(0)
        self.spn_product_count.setEnabled(False)
        self.spn_product_count.setFixedWidth(90)
        self.spn_product_count.setStyleSheet(input_ss())
        cart_header.addWidget(self.spn_product_count)

        pay_row = QHBoxLayout()
        pay_row.setSpacing(10)
        cart_lay.addLayout(pay_row)

        pay_label = QLabel("Ödeme")
        pay_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        pay_row.addWidget(pay_label)

        self.cb_payment = QComboBox()
        self.cb_payment.addItems(["💵 Nakit", "💳 Kart"])
        self.cb_payment.setStyleSheet(combo_ss())
        self.cb_payment.setFixedWidth(180)
        pay_row.addWidget(self.cb_payment)
        pay_row.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Ürün", "Barkod", "Adet", "Birim Fiyat", "Tutar", "İşlem"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 124)
        self.table.setColumnWidth(5, 88)
        cart_lay.addWidget(self.table, stretch=1)

        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        cart_lay.addLayout(bottom)

        self.lbl_total = QLabel("Genel Toplam: TL0.00")
        self.lbl_total.setStyleSheet(
            f"color:{C['accent']};font-size:15px;font-weight:900;{info_box_ss(C['border_soft'])}"
        )
        bottom.addWidget(self.lbl_total)
        bottom.addStretch()

        self.btn_clear = QPushButton("Sepeti Boşalt")
        self.btn_clear.setStyleSheet(btn_primary_ss())
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_cart)
        bottom.addWidget(self.btn_clear)

        self.btn_checkout = QPushButton("Satışı Tamamla")
        self.btn_checkout.setStyleSheet(btn_success_ss())
        self.btn_checkout.setCursor(Qt.PointingHandCursor)
        self.btn_checkout.clicked.connect(self._checkout)
        bottom.addWidget(self.btn_checkout)

        self.lbl_tax_summary = QLabel("Ara Toplam: TL0.00 | KDV: TL0.00")
        self.lbl_tax_summary.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        cart_lay.addWidget(self.lbl_tax_summary)

        side_card = QFrame()
        side_card.setStyleSheet(card_ss())
        shadow(side_card)
        side_lay = QVBoxLayout(side_card)
        side_lay.setContentsMargins(16, 16, 16, 16)
        side_lay.setSpacing(12)
        content_row.addWidget(side_card, 2)

        product_header = QHBoxLayout()
        product_header.setSpacing(10)
        side_lay.addLayout(product_header)

        sub_products = QLabel("Ürün Listesi")
        sub_products.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        product_header.addWidget(sub_products)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Ara...")
        self.inp_search.setStyleSheet(input_ss())
        self.inp_search.textChanged.connect(self._refresh_product_list)
        product_header.addWidget(self.inp_search, 1)

        self.lbl_product_summary = QLabel()
        self.lbl_product_summary.setWordWrap(True)
        self.lbl_product_summary.setStyleSheet(f"color:{C['text_dim']};font-size:12px;font-weight:700;")
        side_lay.addWidget(self.lbl_product_summary)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["Ürün", "Barkod", "Fiyat", "Stok", "Son Kullanma", "Durum"])
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet(TABLE_SS)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.products_table.cellClicked.connect(self._add_from_product_list)
        side_lay.addWidget(self.products_table, stretch=1)

        self.lbl_preview_text = QLabel("Henüz satış yapılmadı.")
        self.lbl_preview_text.setStyleSheet(f"color:{C['text']};font-size:12px;font-weight:700;")
        self.lbl_preview_text.setWordWrap(True)
        side_lay.addWidget(self.lbl_preview_text)

        self._refresh_product_list()

    def _bildirim(self, mesaj: str, ok: bool = True):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("MarketCare")
        dlg.setText(mesaj)
        dlg.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        dlg.exec_()

    def refresh(self):
        self._refresh_product_list()
        self._render_cart()
        self._update_total()
        self.inp_barcode.setFocus()

    def _clear_cart(self):
        self._cart.clear()
        self._render_cart()
        self._update_total()
        self.lbl_preview_text.setText("Henüz satış yapılmadı.")
        self.inp_barcode.clear()
        self.inp_barcode.setFocus()

    def _update_total(self):
        gross_total = 0.0
        tax_total = 0.0
        total_qty = 0
        for item in self._cart.values():
            line_total = float(item["unit_price"]) * int(item["qty"])
            vat_rate = float(item.get("vat_rate") or 0)
            gross_total += line_total
            total_qty += int(item["qty"])
            if vat_rate > 0:
                tax_total += line_total - (line_total / (1.0 + (vat_rate / 100.0)))

        net_total = gross_total - tax_total
        self.lbl_total.setText(f"Genel Toplam: TL{gross_total:.2f}")
        self.lbl_tax_summary.setText(f"Ara Toplam: TL{net_total:.2f} | KDV: TL{tax_total:.2f}")
        self.spn_product_count.setValue(total_qty)
        has_items = bool(self._cart)
        self.btn_clear.setEnabled(has_items)
        self.btn_checkout.setEnabled(has_items)

    def _add_to_cart(self, product: Dict[str, Any], qty_delta: int = 1):
        barcode = str(product.get("barcode_value") or "").strip()
        if not barcode:
            return

        stock_qty = int(product.get("stock_qty", 0))
        current_qty = int(self._cart.get(barcode, {}).get("qty", 0))
        new_qty = current_qty + qty_delta

        if new_qty <= 0:
            self._cart.pop(barcode, None)
            self._render_cart()
            self._update_total()
            return

        if new_qty > stock_qty:
            self._bildirim(f"Yetersiz stok ({product.get('name')}). Mevcut: {stock_qty}", ok=False)
            return

        self._cart[barcode] = {
            "product_id": int(product["id"]),
            "barcode_value": barcode,
            "product_name": str(product.get("name") or ""),
            "unit_price": float(product.get("unit_price") or 0),
            "vat_rate": float(product.get("vat_rate") or 0),
            "qty": new_qty,
            "stock_qty": stock_qty,
        }
        self._render_cart()
        self._update_total()

    def _add_by_barcode(self):
        barcode = self.inp_barcode.text().strip()
        if not barcode:
            return

        product = get_product_by_barcode(barcode)
        if not product or int(product.get("is_active", 1)) == 0:
            self._bildirim("Barkodda ürün bulunamadı.", ok=False)
            self.inp_barcode.selectAll()
            return

        self._add_to_cart(product, qty_delta=1)
        self.inp_barcode.clear()
        self.inp_barcode.setFocus()

    def _set_cart_qty(self, barcode: str, qty: int):
        if barcode not in self._cart:
            return
        stock_qty = int(self._cart[barcode]["stock_qty"])
        if qty <= 0:
            self._cart.pop(barcode, None)
        elif qty > stock_qty:
            self._bildirim(f"Yetersiz stok. Mevcut: {stock_qty}", ok=False)
            self._cart[barcode]["qty"] = stock_qty
        else:
            self._cart[barcode]["qty"] = qty
        self._render_cart()
        self._update_total()

    def _remove_from_cart(self, barcode: str):
        self._cart.pop(barcode, None)
        self._render_cart()
        self._update_total()

    def _render_cart(self):
        self.table.setRowCount(0)
        for barcode, item in self._cart.items():
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            self.table.setItem(
                row_index,
                0,
                QTableWidgetItem(f"{emoji_for_product(item['product_name'])} {item['product_name']}"),
            )
            self.table.setItem(row_index, 1, QTableWidgetItem(str(barcode)))

            qty_spin = QSpinBox()
            qty_spin.setRange(1, int(item["stock_qty"]))
            qty_spin.setValue(int(item["qty"]))
            qty_spin.setButtonSymbols(QSpinBox.UpDownArrows)
            qty_spin.setAlignment(Qt.AlignCenter)
            qty_spin.setMinimumHeight(40)
            qty_spin.setFixedWidth(108)
            qty_spin.setStyleSheet(input_ss())
            qty_spin.valueChanged.connect(lambda value, current_barcode=barcode: self._set_cart_qty(current_barcode, value))
            self.table.setCellWidget(row_index, 2, qty_spin)

            self.table.setItem(row_index, 3, QTableWidgetItem(f"TL{float(item['unit_price']):.2f}"))
            line_total = float(item["unit_price"]) * int(item["qty"])
            self.table.setItem(row_index, 4, QTableWidgetItem(f"TL{line_total:.2f}"))

            btn_remove = QPushButton("🗑")
            btn_remove.setStyleSheet(btn_danger_ss())
            btn_remove.setCursor(Qt.PointingHandCursor)
            btn_remove.setMinimumSize(56, 40)
            btn_remove.clicked.connect(lambda _, current_barcode=barcode: self._remove_from_cart(current_barcode))
            self.table.setCellWidget(row_index, 5, btn_remove)
            self.table.setRowHeight(row_index, 64)

    def _checkout(self):
        if not self._cart:
            self._bildirim("Sepet boş olamaz.", ok=False)
            return

        try:
            lines = [SaleLineInput(barcode_value=barcode, qty=int(item["qty"])) for barcode, item in self._cart.items()]
            pdf_gen = PDFGenerator()
            payment_type = self.cb_payment.currentText()
            result = perform_sale(
                lines=lines,
                created_by_user_id=int(self.user["id"]),
                customer_name=None,
                payment_type=payment_type,
                pdf_generator=pdf_gen,
            )

            self._render_preview(result)
            self._bildirim(f"Satış tamamlandı. {result['sale_no']}", ok=True)
            self._cart.clear()
            self._render_cart()
            self._update_total()
            self.inp_barcode.clear()
            self.inp_search.clear()
            self.inp_barcode.setFocus()
        except Exception as exc:
            self._bildirim(str(exc), ok=False)

        self._refresh_product_list()

    def _render_preview(self, sale_res: Dict[str, Any]):
        items = sale_res.get("items") or []
        lines = [
            f"Satış No: {sale_res.get('sale_no')}",
            f"Tarih: {sale_res.get('created_at')}",
            f"Ödeme: {self.cb_payment.currentText()}",
            f"Ara Toplam: TL{float(sale_res.get('total_amount') or 0):.2f}",
            f"KDV: TL{float(sale_res.get('tax_amount') or 0):.2f}",
            f"Toplam: TL{float(sale_res.get('grand_total') or 0):.2f}",
            f"Slip durumu: {'Hazır' if sale_res.get('slip_path') else 'Yok'}",
            f"Fatura durumu: {'Hazır' if sale_res.get('invoice_path') else 'Yok'}",
            "",
            "Kalemler:",
        ]
        warnings = sale_res.get("document_warnings") or []
        if warnings:
            lines.extend(["", "Belge uyarıları:"])
            lines.extend(str(warning) for warning in warnings)
            lines.append("")
        for item in items:
            lines.append(
                f"{int(item.qty)} x {item.product_name} -> TL{float(item.line_total):.2f} | KDV %{float(item.vat_rate):.0f}"
            )
        self.lbl_preview_text.setText("\n".join(lines))

    def _add_from_product_list(self, row: int, _column: int):
        if row < 0 or row >= len(self._product_rows):
            return
        self._add_to_cart(self._product_rows[row], qty_delta=1)
        self.inp_search.selectAll()

    def _refresh_product_list(self, query: str = ""):
        products = list_products(include_inactive=False)
        all_products = products[:]
        search_text = str(query or self.inp_search.text().strip()).strip().lower()
        if search_text:
            products = [
                product
                for product in products
                if search_text in str(product.get("name", "")).lower()
                or search_text in str(product.get("barcode_value", "")).lower()
            ]

        critical_count = sum(
            1
            for product in all_products
            if int(product.get("stock_qty") or 0) <= int(product.get("critical_threshold") or 0)
        )
        zero_stock_count = sum(1 for product in all_products if int(product.get("stock_qty") or 0) <= 0)
        self.lbl_product_summary.setText(
            f"Listelenen urun: {len(products)} | Kritik stok: {critical_count} | Stokta olmayan: {zero_stock_count}"
        )

        self._product_rows = products
        self.products_table.setRowCount(0)

        now = datetime.now().date()
        for product in products:
            row_index = self.products_table.rowCount()
            self.products_table.insertRow(row_index)

            expiration_date = product.get("expiration_date")
            status = "-"
            try:
                if expiration_date:
                    expiry = datetime.fromisoformat(str(expiration_date)).date()
                    if expiry < now:
                        status = "Geçti"
                    elif expiry <= now + timedelta(days=7):
                        status = "Yakın"
                    else:
                        status = "Uygun"
            except Exception:
                status = "Bilinmiyor"

            vat_rate = float(product.get("vat_rate") or 0)
            self.products_table.setItem(
                row_index,
                0,
                QTableWidgetItem(f"{emoji_for_product(str(product.get('name') or ''))} {product.get('name') or ''}"),
            )
            self.products_table.setItem(row_index, 1, QTableWidgetItem(str(product.get("barcode_value") or "")))
            self.products_table.setItem(
                row_index,
                2,
                QTableWidgetItem(f"TL{float(product.get('unit_price') or 0):.2f} | %{vat_rate:.0f}"),
            )
            self.products_table.setItem(row_index, 3, QTableWidgetItem(str(int(product.get("stock_qty") or 0))))
            self.products_table.setItem(row_index, 4, QTableWidgetItem(str(expiration_date or "-")))

            status_item = QTableWidgetItem(status)
            if status == "Geçti":
                status_item.setForeground(QColor(C["danger"]))
            elif status == "Yakın":
                status_item.setForeground(QColor(C["warning"]))
            else:
                status_item.setForeground(QColor(C["success"]))
            self.products_table.setItem(row_index, 5, status_item)
            self.products_table.setRowHeight(row_index, 48)
