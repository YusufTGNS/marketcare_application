from typing import Optional, Dict, Any

import os

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QAbstractItemView,
    QDateEdit,
    QHeaderView,
)

from ui.style import C, card_ss, btn_primary_ss, input_ss, TABLE_SS, shadow
from repositories.sales_repo import list_sales, list_sales_for_user
from utilities.datetime_utils import format_db_datetime_local


def _doc_status(path: str) -> str:
    return "Hazır" if path else "Yok"


class AdminInvoicesPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        self._selected_sale: Optional[Dict[str, Any]] = None
        self.is_admin = str(self.user.get("role", "")).lower() == "admin"

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        title = QLabel("Faturalar")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        lay.addWidget(title)

        filter_card = QFrame()
        filter_card.setStyleSheet(card_ss())
        shadow(filter_card)
        filter_lay = QVBoxLayout(filter_card)
        filter_lay.setContentsMargins(16, 16, 16, 16)
        filter_lay.setSpacing(12)
        lay.addWidget(filter_card)

        filter_title = QLabel("Son 7 Gün Satış Akışı")
        filter_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        filter_lay.addWidget(filter_title)

        row = QHBoxLayout()
        row.setSpacing(10)
        filter_lay.addLayout(row)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(input_ss())

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(input_ss())

        self.btn_last_week = QPushButton("Son 7 Gün")
        self.btn_last_week.setStyleSheet(btn_primary_ss())
        self.btn_last_week.clicked.connect(self._set_last_seven_days)

        self.btn_today = QPushButton("Bugün")
        self.btn_today.setStyleSheet(btn_primary_ss())
        self.btn_today.clicked.connect(self._set_today)

        self.btn_refresh = QPushButton("Yenile")
        self.btn_refresh.setStyleSheet(btn_primary_ss())
        self.btn_refresh.clicked.connect(self.refresh)

        row.addWidget(QLabel("Başlangıç"))
        row.addWidget(self.date_from)
        row.addWidget(QLabel("Bitiş"))
        row.addWidget(self.date_to)
        row.addWidget(self.btn_last_week)
        row.addWidget(self.btn_today)
        row.addWidget(self.btn_refresh)
        row.addStretch()

        self.lbl_range = QLabel()
        self.lbl_range.setStyleSheet(f"color:{C['text_dim']};font-size:12px;font-weight:700;")
        filter_lay.addWidget(self.lbl_range)

        self.lbl_total_sales = QLabel()
        self.lbl_total_sales.setStyleSheet(f"color:{C['accent']};font-size:13px;font-weight:900;")
        filter_lay.addWidget(self.lbl_total_sales)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Satış No", "Tarih", "Personel", "Ödeme", "Toplam", "Slip", "Fatura", "sale_id"]
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
        lay.addWidget(self.table, stretch=1)

        self.table.itemSelectionChanged.connect(self._on_row_selected)

        action_card = QFrame()
        action_card.setStyleSheet(card_ss())
        shadow(action_card)
        act_lay = QVBoxLayout(action_card)
        act_lay.setContentsMargins(16, 16, 16, 16)
        act_lay.setSpacing(10)
        lay.addWidget(action_card)

        self.lbl_selected = QLabel("Seçili satış: —")
        self.lbl_selected.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        act_lay.addWidget(self.lbl_selected)

        self.lbl_summary = QLabel("Satış seçildiğinde belge durumu burada görünecek.")
        self.lbl_summary.setStyleSheet(f"color:{C['text']};font-size:12px;font-weight:700;")
        self.lbl_summary.setWordWrap(True)
        act_lay.addWidget(self.lbl_summary)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_open_slip = QPushButton("Slip Görüntüle")
        self.btn_open_slip.setStyleSheet(btn_primary_ss())
        self.btn_open_slip.clicked.connect(self._open_slip)
        btn_row.addWidget(self.btn_open_slip)

        self.btn_open_invoice = QPushButton("Fatura Görüntüle")
        self.btn_open_invoice.setStyleSheet(btn_primary_ss())
        self.btn_open_invoice.clicked.connect(self._open_invoice)
        btn_row.addWidget(self.btn_open_invoice)

        act_lay.addLayout(btn_row)

        self._set_last_seven_days()

    def _bildirim(self, msg: str, ok: bool = True):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("MarketCare")
        dlg.setText(msg)
        dlg.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        dlg.exec_()

    def _set_last_seven_days(self):
        today = QDate.currentDate()
        self.date_to.setDate(today)
        self.date_from.setDate(today.addDays(-6))
        self.refresh()

    def _set_today(self):
        today = QDate.currentDate()
        self.date_from.setDate(today)
        self.date_to.setDate(today)
        self.refresh()

    def refresh(self):
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        self.lbl_range.setText(f"Gösterilen aralık: {start_date} - {end_date}")

        if self.is_admin:
            rows = list_sales(limit=500, start_date=start_date, end_date=end_date)
        else:
            rows = list_sales_for_user(
                user_id=int(self.user.get("id", 0)),
                limit=500,
                start_date=start_date,
                end_date=end_date,
            )

        total_sales_amount = sum(float(r.get("grand_total") or 0) for r in rows)
        self.lbl_total_sales.setText(
            f"Toplam Satış: ₺{total_sales_amount:.2f}  |  Kayıt Sayısı: {len(rows)}"
        )

        self.table.setRowCount(0)
        for rdata in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)

            sale_item = QTableWidgetItem(str(rdata.get("sale_no") or ""))
            sale_item.setData(Qt.UserRole, dict(rdata))
            self.table.setItem(r, 0, sale_item)
            self.table.setItem(r, 1, QTableWidgetItem(format_db_datetime_local(str(rdata.get("created_at") or ""))))
            self.table.setItem(r, 2, QTableWidgetItem(str(rdata.get("created_by") or self.user.get("username") or "")))
            self.table.setItem(r, 3, QTableWidgetItem(str(rdata.get("payment_type") or "")))
            self.table.setItem(r, 4, QTableWidgetItem(f"₺{float(rdata.get('grand_total') or 0):.2f}"))
            self.table.setItem(r, 5, QTableWidgetItem(_doc_status(str(rdata.get("pdf_slip_path") or ""))))
            self.table.setItem(r, 6, QTableWidgetItem(_doc_status(str(rdata.get("pdf_invoice_path") or ""))))
            self.table.setItem(r, 7, QTableWidgetItem(str(int(rdata.get("id") or 0))))
            self.table.setRowHeight(r, 44)

        self._selected_sale = None
        self.lbl_selected.setText("Seçili satış: —")
        self.lbl_summary.setText("Satış seçildiğinde belge durumu burada görünecek.")

    def _on_row_selected(self):
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
        total = f"₺{float(sale_data.get('grand_total') or 0):.2f}"
        payment = str(sale_data.get("payment_type") or "")

        self._selected_sale = {
            "sale_no": sale_no,
            "slip_path": slip_path,
            "invoice_path": invoice_path,
        }
        self.lbl_selected.setText(f"Seçili satış: {sale_no}")
        self.lbl_summary.setText(
            f"Tarih: {created_at}\nÖdeme: {payment}\nToplam: {total}\nSlip durumu: {_doc_status(slip_path)}\nFatura durumu: {_doc_status(invoice_path)}"
        )

    def _open_slip(self):
        if not self._selected_sale:
            return
        self._open_pdf(self._selected_sale.get("slip_path"), "Slip")

    def _open_invoice(self):
        if not self._selected_sale:
            return
        self._open_pdf(self._selected_sale.get("invoice_path"), "Fatura")

    def _open_pdf(self, path: Optional[str], label: str):
        if not path:
            self._bildirim(f"{label} belgesi hazır değil.", ok=False)
            return
        if not os.path.exists(path):
            self._bildirim(f"{label} dosyası bulunamadı.", ok=False)
            return
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            self._bildirim(f"{label} açma başarısız.", ok=False)
