from typing import Optional, Dict, Any

import os
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
)

from ui.style import C, card_ss, combo_ss, info_box_ss, input_ss, btn_primary_ss, btn_success_ss, TABLE_SS, shadow
from repositories.products_repo import (
    get_product_by_barcode,
    list_products,
    update_product_active_status,
)
from repositories.stock_repo import list_stock_movements
from services.stock_service import adjust_stock


class AdminStockPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        self._found_product: Optional[Dict[str, Any]] = None
        self._product_rows = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        title = QLabel("Stok Hareketleri")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        lay.addWidget(title)

        form_card = QFrame()
        form_card.setStyleSheet(card_ss())
        shadow(form_card)
        form_lay = QVBoxLayout(form_card)
        form_lay.setContentsMargins(18, 16, 18, 16)
        form_lay.setSpacing(12)
        lay.addWidget(form_card)

        section = QLabel("Ürün Seç ve Durumu Güncelle")
        section.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        form_lay.addWidget(section)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        form_lay.addLayout(top_row)

        self.inp_barcode = QLineEdit()
        self.inp_barcode.setStyleSheet(input_ss())
        self.inp_barcode.setPlaceholderText("Barkod girin")
        self.inp_barcode.returnPressed.connect(self._lookup_product)
        top_row.addWidget(self.inp_barcode, 1)

        self.inp_search = QLineEdit()
        self.inp_search.setStyleSheet(input_ss())
        self.inp_search.setPlaceholderText("Ürün seçmek için ara")
        self.inp_search.textChanged.connect(self._refresh_product_list)
        top_row.addWidget(self.inp_search, 1)

        btn_find = QPushButton("Bul")
        btn_find.setStyleSheet(btn_primary_ss())
        btn_find.clicked.connect(self._lookup_product)
        top_row.addWidget(btn_find)

        body_row = QHBoxLayout()
        body_row.setSpacing(14)
        form_lay.addLayout(body_row)

        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        body_row.addLayout(left_col, 3)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["Ürün", "Barkod", "Stok", "Durum", "SKT"])
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
        self.products_table.cellClicked.connect(self._select_product_from_table)
        left_col.addWidget(self.products_table)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        left_col.addLayout(grid)

        self.inp_qty = QSpinBox()
        self.inp_qty.setRange(1, 999999)
        self.inp_qty.setStyleSheet(input_ss())

        self.cb_move_type = QComboBox()
        self.cb_move_type.addItems(["Stok Girişi", "Stok Çıkışı"])
        self.cb_move_type.setStyleSheet(combo_ss())

        self.cb_active = QComboBox()
        self.cb_active.addItems(["Aktif", "Pasif"])
        self.cb_active.setStyleSheet(combo_ss())

        self.inp_note = QLineEdit()
        self.inp_note.setStyleSheet(input_ss())
        self.inp_note.setPlaceholderText("Not")

        self.lbl_product = QLabel("Ürün: —")
        self.lbl_product.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")

        grid.addWidget(QLabel("Miktar"), 0, 0)
        grid.addWidget(self.inp_qty, 1, 0)
        grid.addWidget(QLabel("Hareket"), 0, 1)
        grid.addWidget(self.cb_move_type, 1, 1)
        grid.addWidget(QLabel("Ürün Durumu"), 0, 2)
        grid.addWidget(self.cb_active, 1, 2)
        grid.addWidget(QLabel("Not"), 2, 0, 1, 3)
        grid.addWidget(self.inp_note, 3, 0, 1, 3)
        grid.addWidget(self.lbl_product, 4, 0, 1, 3)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.btn_status = QPushButton("Durumu Güncelle")
        self.btn_status.setStyleSheet(btn_primary_ss())
        self.btn_status.clicked.connect(self._update_status)
        btn_row.addWidget(self.btn_status)

        self.btn_apply = QPushButton("Stoğu Uygula")
        self.btn_apply.setStyleSheet(btn_success_ss())
        self.btn_apply.clicked.connect(self._apply_stock)
        btn_row.addWidget(self.btn_apply)

        left_col.addLayout(btn_row)

        right_card = QFrame()
        right_card.setStyleSheet(card_ss())
        shadow(right_card)
        right_lay = QVBoxLayout(right_card)
        right_lay.setContentsMargins(14, 14, 14, 14)
        right_lay.setSpacing(10)
        body_row.addWidget(right_card, 2)

        quick_title = QLabel("Hızlı Bilgi")
        quick_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        right_lay.addWidget(quick_title)

        self.lbl_inventory_summary = QLabel()
        self.lbl_inventory_summary.setWordWrap(True)
        self.lbl_inventory_summary.setStyleSheet(f"color:{C['text_dim']};font-size:12px;font-weight:700;")
        right_lay.addWidget(self.lbl_inventory_summary)

        self.lbl_image = QLabel("Görsel yok")
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setMinimumHeight(180)
        self.lbl_image.setStyleSheet(
            f"{info_box_ss(C['border_soft'])}color:{C['text_dim']};"
        )
        right_lay.addWidget(self.lbl_image)

        self.lbl_quick_name = QLabel("Ürün seçilmedi")
        self.lbl_quick_name.setStyleSheet(f"color:{C['text']};font-size:16px;font-weight:900;")
        right_lay.addWidget(self.lbl_quick_name)

        self.lbl_quick_meta = QLabel("Barkod, stok ve son kullanma bilgisi burada görünecek.")
        self.lbl_quick_meta.setWordWrap(True)
        self.lbl_quick_meta.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        right_lay.addWidget(self.lbl_quick_meta)

        self.lbl_stock_badge = QLabel("Durum: —")
        self.lbl_stock_badge.setStyleSheet(
            f"{info_box_ss(C['border_soft'])}color:{C['text']};font-size:12px;font-weight:800;"
        )
        right_lay.addWidget(self.lbl_stock_badge)
        right_lay.addStretch()

        sub = QLabel("Son Stok Hareketleri")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        lay.addWidget(sub)

        self.lbl_skt_status = QLabel("SKT Durumu: -")
        self.lbl_skt_status.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        lay.addWidget(self.lbl_skt_status)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Ürün", "Değişim", "Tür", "Önce", "Sonra", "Not", "Tarih", "Kullanıcı", "user_id"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(9, True)
        lay.addWidget(self.table, stretch=1)

        self.refresh()

    def _bildirim(self, msg: str, ok: bool = True):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("MarketCare")
        dlg.setText(msg)
        dlg.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        dlg.exec_()

    def _render_quick_card(self, prod: Optional[Dict[str, Any]]):
        if not prod:
            self.lbl_image.setPixmap(QPixmap())
            self.lbl_image.setText("Görsel yok")
            self.lbl_quick_name.setText("Ürün seçilmedi")
            self.lbl_quick_meta.setText("Barkod, stok ve son kullanma bilgisi burada görünecek.")
            self.lbl_stock_badge.setText("Durum: —")
            return

        image_path = str(prod.get("image_path") or "")
        if image_path and os.path.exists(image_path):
            pix = QPixmap(image_path)
            if not pix.isNull():
                pix = pix.scaled(220, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_image.setPixmap(pix)
                self.lbl_image.setText("")
            else:
                self.lbl_image.setPixmap(QPixmap())
                self.lbl_image.setText("Görsel açılamadı")
        else:
            self.lbl_image.setPixmap(QPixmap())
            self.lbl_image.setText("Görsel yok")

        status_text = "Aktif" if int(prod.get("is_active", 1)) == 1 else "Pasif"
        stock_qty = int(prod.get("stock_qty") or 0)
        critical = int(prod.get("critical_threshold") or 0)
        expiration = str(prod.get("expiration_date") or "-")

        self.lbl_quick_name.setText(str(prod.get("name") or ""))
        self.lbl_quick_meta.setText(
            f"Barkod: {prod.get('barcode_value')}\nStok: {stock_qty}\nKritik Eşik: {critical}\nSon Kullanma: {expiration}"
        )

        if stock_qty <= critical:
            badge_color = C["warning"]
            badge_text = f"Durum: Kritik stok | {status_text}"
        else:
            badge_color = C["success"]
            badge_text = f"Durum: Normal stok | {status_text}"
        self.lbl_stock_badge.setStyleSheet(
            f"{info_box_ss(badge_color)}color:{badge_color};font-size:12px;font-weight:900;"
        )
        self.lbl_stock_badge.setText(badge_text)

    def _set_found_product(self, prod: Optional[Dict[str, Any]]):
        self._found_product = prod
        if not prod:
            self.lbl_product.setText("Ürün: Bulunamadı")
            self._render_quick_card(None)
            return

        status_text = "Aktif" if int(prod.get("is_active", 1)) == 1 else "Pasif"
        self.lbl_product.setText(
            f"Ürün: {prod['name']} | Barkod: {prod['barcode_value']} | Stok: {int(prod['stock_qty'])} | Durum: {status_text}"
        )
        self.inp_barcode.setText(str(prod.get("barcode_value") or ""))
        self.cb_active.setCurrentIndex(0 if int(prod.get("is_active", 1)) == 1 else 1)
        self._render_quick_card(prod)

    def _lookup_product(self):
        barcode = self.inp_barcode.text().strip()
        if not barcode:
            return
        self._set_found_product(get_product_by_barcode(barcode))

    def _select_product_from_table(self, row: int, _column: int):
        if row < 0 or row >= len(self._product_rows):
            return
        self._set_found_product(self._product_rows[row])

    def _update_status(self):
        if not self._found_product:
            self._lookup_product()
            if not self._found_product:
                self._bildirim("Önce bir ürün seçin.", ok=False)
                return

        is_active = 1 if self.cb_active.currentIndex() == 0 else 0
        update_product_active_status(int(self._found_product["id"]), is_active)
        self._found_product["is_active"] = is_active
        self._bildirim("Ürün durumu güncellendi.")
        self.refresh()
        self._set_found_product(get_product_by_barcode(self.inp_barcode.text().strip()))

    def _apply_stock(self):
        if not self._found_product:
            self._lookup_product()
            if not self._found_product:
                self._bildirim("Önce geçerli barkodla veya listeden ürün seçin.", ok=False)
                return

        qty = int(self.inp_qty.value())
        if qty <= 0:
            self._bildirim("Miktar 1'den küçük olamaz.", ok=False)
            return

        move_text = self.cb_move_type.currentText()
        movement_type = "in" if "Girişi" in move_text else "out"
        note = self.inp_note.text().strip() or None

        try:
            res = adjust_stock(
                product_id=int(self._found_product["id"]),
                delta_qty=qty,
                movement_type=movement_type,
                user_id=int(self.user["id"]),
                note=note,
            )
            self._bildirim(f"Stok güncellendi. {res['qty_before']} -> {res['qty_after']}", ok=True)
            self.inp_qty.setValue(1)
            self.inp_note.setText("")
            self.refresh()
            self._set_found_product(get_product_by_barcode(self.inp_barcode.text().strip()))
        except Exception as e:
            self._bildirim(str(e), ok=False)

    def refresh(self):
        selected_barcode = str(self._found_product.get("barcode_value") or "") if self._found_product else ""
        self._refresh_product_list()

        rows = list_stock_movements(limit=200)
        self.table.setRowCount(0)
        for rdata in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(int(rdata["id"]))))
            self.table.setItem(r, 1, QTableWidgetItem(str(rdata.get("product_name") or "")))
            delta = int(rdata["delta_qty"])
            delta_item = QTableWidgetItem(str(delta))
            delta_item.setForeground(QColor(C["success"] if str(rdata.get("movement_type")) == "in" else C["danger"]))
            self.table.setItem(r, 2, delta_item)
            self.table.setItem(r, 3, QTableWidgetItem(str(rdata.get("movement_type") or "")))
            self.table.setItem(r, 4, QTableWidgetItem(str(int(rdata["qty_before"]))))
            self.table.setItem(r, 5, QTableWidgetItem(str(int(rdata["qty_after"]))))
            self.table.setItem(r, 6, QTableWidgetItem(str(rdata.get("note") or "")))
            self.table.setItem(r, 7, QTableWidgetItem(str(rdata.get("created_at") or "")))
            self.table.setItem(r, 8, QTableWidgetItem(str(rdata.get("user_name") or "")))
            self.table.setItem(r, 9, QTableWidgetItem(str(int(rdata.get("user_id") or 0))))

        self._refresh_skt_status()
        if selected_barcode:
            self._set_found_product(get_product_by_barcode(selected_barcode))

    def _refresh_product_list(self, query: str = ""):
        products = list_products(include_inactive=True)
        q = str(query or self.inp_search.text().strip()).strip().lower()
        if q:
            products = [
                p
                for p in products
                if q in str(p.get("name", "")).lower() or q in str(p.get("barcode_value", "")).lower()
            ]

        active_count = sum(1 for product in products if int(product.get("is_active", 1)) == 1)
        critical_count = sum(
            1
            for product in products
            if int(product.get("is_active", 1)) == 1
            and int(product.get("stock_qty") or 0) <= int(product.get("critical_threshold") or 0)
        )
        self.lbl_inventory_summary.setText(
            f"Aktif urun: {active_count} | Kritik stok: {critical_count} | Listelenen: {len(products)}"
        )

        self._product_rows = products
        self.products_table.setRowCount(0)
        for p in products:
            r = self.products_table.rowCount()
            self.products_table.insertRow(r)
            self.products_table.setItem(r, 0, QTableWidgetItem(str(p.get("name") or "")))
            self.products_table.setItem(r, 1, QTableWidgetItem(str(p.get("barcode_value") or "")))
            self.products_table.setItem(r, 2, QTableWidgetItem(str(int(p.get("stock_qty") or 0))))
            status_item = QTableWidgetItem("Aktif" if int(p.get("is_active", 1)) == 1 else "Pasif")
            status_item.setForeground(QColor(C["success"] if int(p.get("is_active", 1)) == 1 else C["danger"]))
            self.products_table.setItem(r, 3, status_item)
            self.products_table.setItem(r, 4, QTableWidgetItem(str(p.get("expiration_date") or "-")))
            self.products_table.setRowHeight(r, 44)

    def _refresh_skt_status(self):
        products = list_products(include_inactive=True)
        now = datetime.now().date()
        expired = []
        upcoming = []

        for p in products:
            exp_date = p.get("expiration_date")
            if not exp_date:
                continue
            try:
                dt = datetime.fromisoformat(str(exp_date)).date()
            except Exception:
                continue

            if dt < now:
                expired.append(p)
            elif dt <= now + timedelta(days=7):
                upcoming.append(p)

        self.lbl_skt_status.setText(f"SKT: {len(expired)} geçmiş, {len(upcoming)} yakında (7 gün içinde)")
