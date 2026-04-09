from typing import Any, Dict, Optional

import os

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from repositories.sales_repo import list_sales, list_sales_for_user
from ui.style import C, TABLE_SS, btn_primary_ss, card_ss, input_ss, shadow
from utilities.datetime_utils import format_db_datetime_local


def _belge_durumu(path: str) -> str:
    return "Hazir" if path else "Yok"


class AdminInvoicesPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.is_admin = str(self.user.get("role", "")).lower() == "admin"
        self._selected_sale: Optional[Dict[str, Any]] = None
        self.setStyleSheet(f"background:{C['bg']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        title = QLabel("Belgeler")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        layout.addWidget(title)

        filter_card = QFrame()
        filter_card.setStyleSheet(card_ss())
        shadow(filter_card)
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 16, 16, 16)
        filter_layout.setSpacing(12)
        layout.addWidget(filter_card)

        filter_title = QLabel("Satis Belgeleri")
        filter_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        filter_layout.addWidget(filter_title)

        row = QHBoxLayout()
        row.setSpacing(10)
        filter_layout.addLayout(row)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(input_ss())

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(input_ss())

        btn_last_week = QPushButton("Son 7 Gun")
        btn_last_week.setStyleSheet(btn_primary_ss())
        btn_last_week.clicked.connect(self._set_last_seven_days)

        btn_today = QPushButton("Bugun")
        btn_today.setStyleSheet(btn_primary_ss())
        btn_today.clicked.connect(self._set_today)

        btn_refresh = QPushButton("Yenile")
        btn_refresh.setStyleSheet(btn_primary_ss())
        btn_refresh.clicked.connect(self.refresh)

        row.addWidget(QLabel("Baslangic"))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Bitis"))
        row.addWidget(self.date_to)
        row.addWidget(btn_last_week)
        row.addWidget(btn_today)
        row.addWidget(btn_refresh)
        row.addStretch()

        self.lbl_range = QLabel()
        self.lbl_range.setStyleSheet(f"color:{C['text_dim']};font-size:12px;font-weight:700;")
        filter_layout.addWidget(self.lbl_range)

        self.lbl_total_sales = QLabel()
        self.lbl_total_sales.setStyleSheet(f"color:{C['accent']};font-size:13px;font-weight:900;")
        filter_layout.addWidget(self.lbl_total_sales)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Satis No", "Tarih", "Personel", "Odeme", "Toplam", "Slip", "Fatura", "sale_id"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.setColumnHidden(7, True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        layout.addWidget(self.table, stretch=1)

        detail_card = QFrame()
        detail_card.setStyleSheet(card_ss())
        shadow(detail_card)
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(10)
        layout.addWidget(detail_card)

        self.lbl_selected = QLabel("Secili satis: -")
        self.lbl_selected.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        detail_layout.addWidget(self.lbl_selected)

        self.lbl_summary = QLabel("Bir satis secildiginde belge ozeti burada gorunecek.")
        self.lbl_summary.setStyleSheet(f"color:{C['text']};font-size:12px;font-weight:700;")
        self.lbl_summary.setWordWrap(True)
        detail_layout.addWidget(self.lbl_summary)

        button_row = QHBoxLayout()
        button_row.addStretch()

        btn_open_slip = QPushButton("Slip Ac")
        btn_open_slip.setStyleSheet(btn_primary_ss())
        btn_open_slip.clicked.connect(self._open_slip)
        button_row.addWidget(btn_open_slip)

        btn_open_invoice = QPushButton("Fatura Ac")
        btn_open_invoice.setStyleSheet(btn_primary_ss())
        btn_open_invoice.clicked.connect(self._open_invoice)
        button_row.addWidget(btn_open_invoice)
        detail_layout.addLayout(button_row)

        self._set_last_seven_days()

    def _bildirim(self, message: str, ok: bool = True) -> None:
        pencere = QMessageBox(self)
        pencere.setWindowTitle("MarketCare")
        pencere.setText(message)
        pencere.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        pencere.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        pencere.exec_()

    def _set_last_seven_days(self) -> None:
        today = QDate.currentDate()
        self.date_to.setDate(today)
        self.date_from.setDate(today.addDays(-6))
        self.refresh()

    def _set_today(self) -> None:
        today = QDate.currentDate()
        self.date_from.setDate(today)
        self.date_to.setDate(today)
        self.refresh()

    def refresh(self) -> None:
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        self.lbl_range.setText(f"Gosterilen aralik: {start_date} - {end_date}")

        if self.is_admin:
            rows = list_sales(limit=500, start_date=start_date, end_date=end_date)
        else:
            rows = list_sales_for_user(
                user_id=int(self.user.get("id", 0)),
                limit=500,
                start_date=start_date,
                end_date=end_date,
            )

        toplam = sum(float(row.get("grand_total") or 0) for row in rows)
        self.lbl_total_sales.setText(f"Toplam satis: TL{toplam:.2f} | Kayit sayisi: {len(rows)}")

        self.table.setRowCount(0)
        for row_data in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)

            sale_item = QTableWidgetItem(str(row_data.get("sale_no") or ""))
            sale_item.setData(Qt.UserRole, dict(row_data))
            self.table.setItem(row, 0, sale_item)
            self.table.setItem(row, 1, QTableWidgetItem(format_db_datetime_local(str(row_data.get("created_at") or ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(row_data.get("created_by") or self.user.get("username") or "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(row_data.get("payment_type") or "")))
            self.table.setItem(row, 4, QTableWidgetItem(f"TL{float(row_data.get('grand_total') or 0):.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(_belge_durumu(str(row_data.get("pdf_slip_path") or ""))))
            self.table.setItem(row, 6, QTableWidgetItem(_belge_durumu(str(row_data.get("pdf_invoice_path") or ""))))
            self.table.setItem(row, 7, QTableWidgetItem(str(int(row_data.get("id") or 0))))
            self.table.setRowHeight(row, 44)

        self._selected_sale = None
        self.lbl_selected.setText("Secili satis: -")
        self.lbl_summary.setText("Bir satis secildiginde belge ozeti burada gorunecek.")

    def _on_row_selected(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        sale_item = self.table.item(row, 0)
        sale_data = sale_item.data(Qt.UserRole) if sale_item else None
        if not sale_data:
            return

        sale_no = str(sale_data.get("sale_no") or "")
        slip_path = str(sale_data.get("pdf_slip_path") or "")
        invoice_path = str(sale_data.get("pdf_invoice_path") or "")
        created_at = format_db_datetime_local(str(sale_data.get("created_at") or ""))
        payment = str(sale_data.get("payment_type") or "")
        total = f"TL{float(sale_data.get('grand_total') or 0):.2f}"

        self._selected_sale = {
            "sale_no": sale_no,
            "slip_path": slip_path,
            "invoice_path": invoice_path,
        }
        self.lbl_selected.setText(f"Secili satis: {sale_no}")
        self.lbl_summary.setText(
            f"Tarih: {created_at}\n"
            f"Odeme: {payment}\n"
            f"Toplam: {total}\n"
            f"Slip durumu: {_belge_durumu(slip_path)}\n"
            f"Fatura durumu: {_belge_durumu(invoice_path)}"
        )

    def _open_slip(self) -> None:
        if self._selected_sale:
            self._open_pdf(self._selected_sale.get("slip_path"), "Slip")

    def _open_invoice(self) -> None:
        if self._selected_sale:
            self._open_pdf(self._selected_sale.get("invoice_path"), "Fatura")

    def _open_pdf(self, path: Optional[str], label: str) -> None:
        if not path:
            self._bildirim(f"{label} belgesi hazir degil.", ok=False)
            return
        if not os.path.exists(path):
            self._bildirim(f"{label} dosyasi bulunamadi.", ok=False)
            return
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            self._bildirim(f"{label} acilamadi.", ok=False)
