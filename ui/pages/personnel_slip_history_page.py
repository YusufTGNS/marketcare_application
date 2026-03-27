from typing import Optional, Dict, Any

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QAbstractItemView,
)

from ui.style import C, card_ss, btn_primary_ss, input_ss, TABLE_SS, shadow
from repositories.sales_repo import list_sales_for_user


class PersonnelSlipHistoryPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        self._selected_sale: Optional[Dict[str, str]] = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        title = QLabel("Slip Geçmişi")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        lay.addWidget(title)

        sub = QLabel("Yaptığınız satışların slip/fatura PDF’leri")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        lay.addWidget(sub)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Sale No", "Tarih", "Toplam", "Slip PDF", "Fatura PDF", "sale_id"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.setColumnHidden(5, True)
        self.table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.table, stretch=1)

        self.table.itemSelectionChanged.connect(self._on_row_selected)

        # actions
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

        self.lbl_paths = QLabel("Slip: —\nFatura: —")
        self.lbl_paths.setStyleSheet(f"color:{C['text']};font-size:12px;font-weight:700;")
        self.lbl_paths.setWordWrap(True)
        act_lay.addWidget(self.lbl_paths)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.btn_open_slip = QPushButton("Slip’i Aç")
        self.btn_open_slip.setStyleSheet(btn_primary_ss())
        self.btn_open_slip.setCursor(Qt.PointingHandCursor)
        self.btn_open_slip.clicked.connect(self._open_slip)
        btn_row.addWidget(self.btn_open_slip)

        self.btn_open_invoice = QPushButton("Fatura’yı Aç")
        self.btn_open_invoice.setStyleSheet(btn_primary_ss())
        self.btn_open_invoice.setCursor(Qt.PointingHandCursor)
        self.btn_open_invoice.clicked.connect(self._open_invoice)
        btn_row.addWidget(self.btn_open_invoice)

        act_lay.addLayout(btn_row)

        self.refresh()

    def _bildirim(self, msg: str, ok: bool = True):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("MarketCare")
        dlg.setText(msg)
        dlg.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        dlg.exec_()

    def refresh(self):
        uid = int(self.user["id"])
        rows = list_sales_for_user(uid, limit=200)
        self.table.setRowCount(0)

        for rdata in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(rdata.get("sale_no") or "")))
            self.table.setItem(r, 1, QTableWidgetItem(str(rdata.get("created_at") or "")))
            self.table.setItem(
                r,
                2,
                QTableWidgetItem(f"₺{float(rdata.get('grand_total') or 0):.2f}"),
            )
            self.table.setItem(r, 3, QTableWidgetItem(str(rdata.get("pdf_slip_path") or "")))
            self.table.setItem(r, 4, QTableWidgetItem(str(rdata.get("pdf_invoice_path") or "")))
            self.table.setItem(r, 5, QTableWidgetItem(str(int(rdata.get("id") or 0))))

        self._selected_sale = None
        self.lbl_selected.setText("Seçili satış: —")
        self.lbl_paths.setText("Slip: —\nFatura: —")
        self.table.resizeColumnsToContents()

    def _on_row_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()

        sale_no = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
        slip_path = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        invoice_path = self.table.item(row, 4).text() if self.table.item(row, 4) else ""

        self._selected_sale = {
            "sale_no": sale_no,
            "slip_path": slip_path,
            "invoice_path": invoice_path,
        }
        self.lbl_selected.setText(f"Seçili satış: {sale_no}")
        self.lbl_paths.setText(f"Slip: {slip_path or '—'}\nFatura: {invoice_path or '—'}")

    def _open_slip(self):
        if not self._selected_sale:
            return
        self._open_pdf(self._selected_sale.get("slip_path"))

    def _open_invoice(self):
        if not self._selected_sale:
            return
        self._open_pdf(self._selected_sale.get("invoice_path"))

    def _open_pdf(self, path: Optional[str]):
        if not path:
            self._bildirim("PDF yolu bulunamadı.", ok=False)
            return
        if not os.path.exists(path):
            self._bildirim("PDF dosyası bulunamadı (dosya silinmiş olabilir).", ok=False)
            return
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception:
            self._bildirim("PDF açma başarısız.", ok=False)

