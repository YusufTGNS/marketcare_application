from typing import Optional

import os
import uuid

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from repositories.products_repo import add_or_update_product, list_products
from ui.style import C, TABLE_SS, btn_primary_ss, btn_success_ss, card_ss, info_box_ss, input_ss, shadow
from utilities.emoji_utils import emoji_for_product
from utilities.vat_utils import infer_vat_rate_by_name, split_gross_price


class AdminProductsPage(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C['bg']};")

        self._editing_id: Optional[int] = None
        self._editing_is_active: int = 1
        self._editing_vat_rate: float = 20.0
        self._all_products = []

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(16)

        title = QLabel("Ürün Yönetimi")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        root.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {C['border_soft']};
                border-radius: 20px;
                background: transparent;
                top: -1px;
            }}
            QTabBar::tab {{
                background: {C['input_bg']};
                color: {C['text']};
                border: 1px solid {C['border_soft']};
                min-width: 170px;
                min-height: 24px;
                padding: 9px 16px;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
                margin-right: 6px;
                font-size: 13px;
                font-weight: 800;
            }}
            QTabBar::tab:selected {{
                background: {C['row_sel']};
                color: {C['accent']};
            }}
            QTabBar::tab:hover {{
                color: {C['accent']};
            }}
            """
        )
        root.addWidget(self.tabs, stretch=1)

        self._build_new_product_tab()
        self._build_products_tab()

        self._clear_form()
        self.refresh()

    def _build_new_product_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(8, 12, 8, 8)
        tab_layout.setSpacing(14)

        form_card = QFrame()
        form_card.setStyleSheet(card_ss())
        shadow(form_card)
        form_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(14)
        tab_layout.addWidget(form_card)

        section = QLabel("Yeni Ürün")
        section.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        form_layout.addWidget(section)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)
        form_layout.addLayout(grid)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ürün adını yazın")
        self.inp_name.textChanged.connect(self._refresh_vat_preview)

        self.inp_barcode = QLineEdit()
        self.inp_barcode.setReadOnly(True)
        self.inp_barcode.setPlaceholderText("Barkod sistem tarafından oluşturulur")

        self.inp_price = QDoubleSpinBox()
        self.inp_price.setRange(0, 999999)
        self.inp_price.setDecimals(2)
        self.inp_price.valueChanged.connect(self._refresh_vat_preview)

        self.inp_stock = QSpinBox()
        self.inp_stock.setRange(0, 999999)

        self.inp_critical = QSpinBox()
        self.inp_critical.setRange(0, 999999)
        self.inp_critical.setValue(10)

        self.inp_skt = QDateEdit()
        self.inp_skt.setCalendarPopup(True)
        self.inp_skt.setDate(QDate.currentDate().addYears(2))

        self.inp_image_path = QLineEdit()
        self.inp_image_path.setReadOnly(True)

        for widget in [
            self.inp_name,
            self.inp_barcode,
            self.inp_price,
            self.inp_stock,
            self.inp_critical,
            self.inp_skt,
            self.inp_image_path,
        ]:
            widget.setStyleSheet(input_ss())
            widget.setMinimumHeight(38)

        btn_img = QPushButton("Görsel Yükle")
        btn_img.setStyleSheet(btn_primary_ss())
        btn_img.setCursor(Qt.PointingHandCursor)
        btn_img.clicked.connect(self._choose_image)

        grid.addWidget(self._form_label("Ürün Adı"), 0, 0)
        grid.addWidget(self._form_label("Barkod"), 0, 1)
        grid.addWidget(self.inp_name, 1, 0)
        grid.addWidget(self.inp_barcode, 1, 1)

        grid.addWidget(self._form_label("Satış Fiyatı (KDV dahil)"), 2, 0)
        grid.addWidget(self._form_label("Son Kullanma"), 2, 1)
        grid.addWidget(self.inp_price, 3, 0)
        grid.addWidget(self.inp_skt, 3, 1)

        grid.addWidget(self._form_label("Stok Miktarı"), 4, 0)
        grid.addWidget(self._form_label("Kritik Eşik"), 4, 1)
        grid.addWidget(self.inp_stock, 5, 0)
        grid.addWidget(self.inp_critical, 5, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        tax_card = QFrame()
        tax_card.setStyleSheet(card_ss())
        tax_layout = QVBoxLayout(tax_card)
        tax_layout.setContentsMargins(16, 16, 16, 16)
        tax_layout.setSpacing(10)
        form_layout.addWidget(tax_card)

        tax_title = QLabel("Vergi ve Görsel")
        tax_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        tax_layout.addWidget(tax_title)

        img_row = QHBoxLayout()
        img_row.setSpacing(10)
        img_row.addWidget(self.inp_image_path, 1)
        img_row.addWidget(btn_img)
        tax_layout.addLayout(img_row)

        self.lbl_image_hint = QLabel("Görsel yüklenmezse ürün adına göre otomatik görsel indirilecek.")
        self.lbl_image_hint.setStyleSheet(f"color:{C['text_dim']};font-size:11px;font-weight:700;")
        tax_layout.addWidget(self.lbl_image_hint)

        self.lbl_vat = QLabel()
        self.lbl_vat.setWordWrap(True)
        self.lbl_vat.setMinimumHeight(96)
        self.lbl_vat.setStyleSheet(
            f"{info_box_ss(C['border_soft'])}color:{C['text']};font-size:12px;font-weight:700;"
        )
        tax_layout.addWidget(self.lbl_vat)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setStyleSheet(btn_success_ss())
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_product)
        btn_row.addWidget(self.btn_save)

        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.setStyleSheet(btn_primary_ss())
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_form)
        btn_row.addWidget(self.btn_clear)
        tax_layout.addLayout(btn_row)

        tab_layout.addStretch()
        self.tabs.addTab(tab, "Yeni Ürün")

    def _build_products_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(8, 12, 8, 8)
        tab_layout.setSpacing(12)

        list_card = QFrame()
        list_card.setStyleSheet(card_ss())
        shadow(list_card)
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(16, 16, 16, 16)
        list_layout.setSpacing(12)
        tab_layout.addWidget(list_card, stretch=1)

        sub = QLabel("Ürünler")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        list_layout.addWidget(sub)

        self.lbl_summary = QLabel()
        self.lbl_summary.setStyleSheet(f"color:{C['text_dim']};font-size:12px;font-weight:700;")
        list_layout.addWidget(self.lbl_summary)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Ürün ara... (isim veya barkod)")
        self.inp_search.setStyleSheet(input_ss())
        self.inp_search.setMinimumHeight(38)
        self.inp_search.textChanged.connect(self._apply_filter)
        search_row.addWidget(self.inp_search, 1)
        list_layout.addLayout(search_row)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["Ürün", "Barkod", "Fiyat", "KDV", "Stok", "Kritik", "Son Kullanma", "Görsel", "ID"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.setColumnHidden(8, True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 86)
        list_layout.addWidget(self.table, stretch=1)

        self.table.itemSelectionChanged.connect(self._on_row_selected)
        self.table.cellClicked.connect(self._copy_barcode_from_row)

        self.tabs.addTab(tab, "Ürünler")

    def _bildirim(self, mesaj: str, ok: bool = True):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("MarketCare")
        dlg.setText(mesaj)
        dlg.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        dlg.exec_()

    def _form_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color:{C['text']};font-size:12px;font-weight:800;padding-bottom:2px;")
        return label

    def _products_image_dir(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        out_dir = os.path.join(base_dir, "assets", "product_images")
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Ürün görseli seç",
            self._products_image_dir(),
            "Resim dosyaları (*.png *.jpg *.jpeg *.webp);;Tüm dosyalar (*.*)",
        )
        if path:
            self.inp_image_path.setText(path)

    def _clear_form(self):
        self._editing_id = None
        self._editing_is_active = 1
        self._editing_vat_rate = 20.0
        self.inp_name.setText("")
        self.inp_barcode.setText(self._generate_barcode_value())
        self.inp_price.setValue(0.0)
        self.inp_stock.setValue(0)
        self.inp_critical.setValue(10)
        self.inp_skt.setDate(QDate.currentDate().addYears(2))
        self.inp_image_path.setText("")
        self._refresh_vat_preview()

    def _generate_barcode_value(self) -> str:
        from repositories.products_repo import get_product_by_barcode

        for _ in range(20):
            token = uuid.uuid4().hex[:12].upper()
            candidate = f"P{token}"
            if not get_product_by_barcode(candidate):
                return candidate
        return f"P{uuid.uuid4().hex[:12].upper()}"

    def _create_local_placeholder_image(self, product_name: str, barcode: str) -> Optional[str]:
        out_path = os.path.join(self._products_image_dir(), f"{barcode}_auto.png")
        try:
            pixmap = QPixmap(600, 400)
            pixmap.fill(QColor(C["card"]))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(24, 24, 552, 352, QColor(C["row_sel"]))
            painter.setPen(QColor(C["accent"]))
            painter.drawRect(24, 24, 552, 352)
            painter.setPen(QColor(C["text"]))
            painter.setFont(self.font())
            painter.drawText(48, 160, (product_name.strip() or "Yeni Urun")[:28])
            painter.setPen(QColor(C["text_sub"]))
            painter.drawText(48, 205, f"Barkod: {barcode}")
            painter.drawText(48, 235, "Yerel onizleme gorseli")
            painter.end()

            pixmap.save(out_path, "PNG")
            return out_path
        except Exception:
            return None

    def _current_vat_info(self):
        product_name = self.inp_name.text().strip()
        price = float(self.inp_price.value())
        if self._editing_id is None:
            vat_rate, reason = infer_vat_rate_by_name(product_name)
        else:
            vat_rate, reason = self._editing_vat_rate, "Kayıtlı ürün KDV oranı kullanılıyor"
        net_price, tax_amount = split_gross_price(price, vat_rate)
        return vat_rate, reason, net_price, tax_amount

    def _refresh_vat_preview(self):
        vat_rate, reason, net_price, tax_amount = self._current_vat_info()
        self.lbl_vat.setText(
            f"Yapay zeka KDV tahmini: %{vat_rate:.0f}\n"
            f"Gerekçe: {reason}\n"
            f"KDV hariç fiyat: TL{net_price:.2f}\n"
            f"KDV tutarı: TL{tax_amount:.2f}"
        )

    def refresh(self):
        self._all_products = list_products(include_inactive=True)
        self._apply_filter()

    def _apply_filter(self):
        query = self.inp_search.text().strip().lower()
        rows = self._all_products
        if query:
            rows = [
                product
                for product in rows
                if query in str(product.get("name", "")).lower()
                or query in str(product.get("barcode_value", "")).lower()
            ]

        active_count = sum(1 for product in self._all_products if int(product.get("is_active", 1)) == 1)
        self.lbl_summary.setText(
            f"Toplam urun: {len(self._all_products)} | Aktif: {active_count} | Listelenen: {len(rows)}"
        )

        self.table.setRowCount(0)
        for product in rows:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            name_item = QTableWidgetItem(f"{emoji_for_product(str(product.get('name') or ''))} {product['name']}")
            name_item.setData(Qt.UserRole, dict(product))
            if int(product.get("is_active", 1)) == 0:
                name_item.setForeground(QColor(C["danger"]))
            self.table.setItem(row_index, 0, name_item)
            self.table.setItem(row_index, 1, QTableWidgetItem(str(product["barcode_value"])))
            self.table.setItem(row_index, 2, QTableWidgetItem(f"TL{float(product['unit_price']):.2f}"))
            self.table.setItem(row_index, 3, QTableWidgetItem(f"%{float(product.get('vat_rate') or 0):.0f}"))
            self.table.setItem(row_index, 4, QTableWidgetItem(str(int(product["stock_qty"]))))
            self.table.setItem(row_index, 5, QTableWidgetItem(str(int(product["critical_threshold"]))))
            self.table.setItem(row_index, 6, QTableWidgetItem(str(product.get("expiration_date") or "")))

            image_path = product.get("image_path")
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    self.table.setCellWidget(row_index, 7, image_label)
                else:
                    self.table.setItem(row_index, 7, QTableWidgetItem("-"))
            else:
                self.table.setItem(row_index, 7, QTableWidgetItem("-"))

            self.table.setItem(row_index, 8, QTableWidgetItem(str(int(product["id"]))))
            self.table.setRowHeight(row_index, 58)

    def _selected_product(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        item = self.table.item(selected[0].row(), 0)
        if not item:
            return None
        return item.data(Qt.UserRole)

    def _on_row_selected(self):
        product = self._selected_product()
        if not product:
            return

        self._editing_id = int(product["id"])
        self._editing_is_active = int(product.get("is_active", 1))
        self._editing_vat_rate = float(product.get("vat_rate") or 20.0)
        self.inp_name.setText(str(product["name"]))
        self.inp_barcode.setText(str(product["barcode_value"]))
        self.inp_price.setValue(float(product["unit_price"]))
        self.inp_stock.setValue(int(product["stock_qty"]))
        self.inp_critical.setValue(int(product["critical_threshold"]))

        expiration_date = product.get("expiration_date")
        if expiration_date:
            try:
                year, month, day = map(int, str(expiration_date).split("-"))
                self.inp_skt.setDate(QDate(year, month, day))
            except Exception:
                pass
        self.inp_image_path.setText(str(product.get("image_path") or ""))
        self._refresh_vat_preview()
        self.tabs.setCurrentIndex(0)

    def _copy_barcode_from_row(self, row: int, column: int):
        if column != 1:
            return
        barcode_item = self.table.item(row, 1)
        if not barcode_item:
            return
        QApplication.clipboard().setText(barcode_item.text())
        self.lbl_summary.setText(f"Barkod panoya kopyalandi: {barcode_item.text()}")

    def _save_product(self):
        try:
            name = self.inp_name.text().strip()
            barcode = self.inp_barcode.text().strip()
            if not name:
                raise ValueError("Ürün adı boş olamaz.")

            if not barcode:
                barcode = self._generate_barcode_value()
                self.inp_barcode.setText(barcode)

            qdate = self.inp_skt.date()
            expiration_date = f"{qdate.year():04d}-{qdate.month():02d}-{qdate.day():02d}"
            unit_price = float(self.inp_price.value())
            if unit_price < 0:
                raise ValueError("Birim fiyat negatif olamaz.")

            vat_rate = self._editing_vat_rate if self._editing_id is not None else infer_vat_rate_by_name(name)[0]
            image_path = self.inp_image_path.text().strip() or None
            if not image_path:
                image_path = self._create_local_placeholder_image(name, barcode)

            add_or_update_product(
                product_id=self._editing_id,
                name=name,
                barcode_value=barcode,
                unit_price=unit_price,
                vat_rate=vat_rate,
                expiration_date=expiration_date,
                image_path=image_path,
                icon_path=None,
                stock_qty=int(self.inp_stock.value()),
                critical_threshold=int(self.inp_critical.value()),
                is_active=self._editing_is_active,
            )

            self._bildirim("Ürün kaydedildi.", ok=True)
            self._clear_form()
            self.refresh()
            self.tabs.setCurrentIndex(1)
        except Exception as exc:
            self._bildirim(str(exc), ok=False)
