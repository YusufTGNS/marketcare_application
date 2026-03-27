from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from repositories.products_repo import list_critical_products, list_products
from repositories.sales_repo import list_sales, list_sales_for_user
from repositories.users_repo import list_users
from services.permission_service import is_admin
from ui.style import C, TABLE_SS, card_ss, shadow


class StatCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str, accent: str, badge: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {C['card']};
                border: 1px solid {C['border']};
                border-radius: 14px;
            }}
            """
        )
        shadow(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        layout.addLayout(top)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color:{C['text_dim']};font-size:11px;font-weight:900;")
        top.addWidget(title_label)
        top.addStretch()

        badge_label = QLabel(badge)
        badge_label.setStyleSheet(
            f"background:{C['row_sel']};color:{accent};border:1px solid {C['border']};"
            "border-radius:10px;padding:4px 8px;font-size:10px;font-weight:900;"
        )
        top.addWidget(badge_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color:{accent};font-size:26px;font-weight:900;")
        layout.addWidget(value_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        layout.addWidget(subtitle_label)


class DashboardPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(16)

        hero = QFrame()
        hero.setStyleSheet(
            f"""
            QFrame {{
                border-radius: 20px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #20332A, stop:0.55 {C['accent2']}, stop:1 {C['accent']});
                border: 1px solid rgba(255,255,255,0.08);
            }}
            """
        )
        shadow(hero, blur=24, dy=6)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_layout.setSpacing(8)
        root.addWidget(hero)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)
        hero_layout.addLayout(brand_row)

        branch_badge = QLabel("SUBE 01")
        branch_badge.setStyleSheet(
            "background:rgba(255,255,255,0.14);color:#F4F0E7;border-radius:11px;padding:5px 10px;"
            "font-size:10px;font-weight:900;"
        )
        brand_row.addWidget(branch_badge)

        quality_badge = QLabel("RAF HAZIR")
        quality_badge.setStyleSheet(
            f"background:rgba(17,22,28,0.28);color:{C['accent']};border-radius:11px;padding:5px 10px;"
            "font-size:10px;font-weight:900;"
        )
        brand_row.addWidget(quality_badge)
        brand_row.addStretch()

        self.lbl_welcome = QLabel()
        self.lbl_welcome.setStyleSheet("color:white;font-size:28px;font-weight:900;")
        hero_layout.addWidget(self.lbl_welcome)

        self.lbl_intro = QLabel()
        self.lbl_intro.setWordWrap(True)
        self.lbl_intro.setStyleSheet("color:rgba(255,255,255,0.84);font-size:13px;font-weight:600;")
        hero_layout.addWidget(self.lbl_intro)

        self.lbl_focus = QLabel()
        self.lbl_focus.setStyleSheet(
            "color:#F2F0EA;font-size:12px;font-weight:800;background:rgba(17,22,28,0.26);"
            "padding:8px 12px;border-radius:12px;"
        )
        hero_layout.addWidget(self.lbl_focus)

        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(14)
        root.addLayout(self.stats_row)

        section_row = QHBoxLayout()
        section_row.setSpacing(16)
        root.addLayout(section_row, stretch=1)

        recent_card = QFrame()
        recent_card.setStyleSheet(card_ss())
        shadow(recent_card)
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(16, 16, 16, 16)
        recent_layout.setSpacing(10)
        section_row.addWidget(recent_card, 3)

        recent_title = QLabel("Son Hareketler")
        recent_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        recent_layout.addWidget(recent_title)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(["Satis No", "Tarih", "Odeme", "Toplam"])
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setStyleSheet(TABLE_SS)
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sales_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.sales_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.sales_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        recent_layout.addWidget(self.sales_table, stretch=1)

        side_card = QFrame()
        side_card.setStyleSheet(card_ss())
        shadow(side_card)
        side_layout = QVBoxLayout(side_card)
        side_layout.setContentsMargins(16, 16, 16, 16)
        side_layout.setSpacing(10)
        section_row.addWidget(side_card, 2)

        side_title = QLabel("Hizli Bakis")
        side_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        side_layout.addWidget(side_title)

        self.lbl_quick_summary = QLabel()
        self.lbl_quick_summary.setWordWrap(True)
        self.lbl_quick_summary.setStyleSheet(f"color:{C['text']};font-size:13px;font-weight:700;")
        side_layout.addWidget(self.lbl_quick_summary)

        service_badge = QLabel("GUNLUK OPERASYON")
        service_badge.setStyleSheet(
            f"background:{C['row_sel']};color:{C['accent2']};border:1px solid {C['border']};"
            "border-radius:12px;padding:8px 10px;font-size:11px;font-weight:900;"
        )
        side_layout.addWidget(service_badge)

        critical_title = QLabel("Kritik Urunler")
        critical_title.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        side_layout.addWidget(critical_title)

        self.critical_table = QTableWidget()
        self.critical_table.setColumnCount(3)
        self.critical_table.setHorizontalHeaderLabels(["Urun", "Stok", "Esik"])
        self.critical_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.critical_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.critical_table.verticalHeader().setVisible(False)
        self.critical_table.setAlternatingRowColors(True)
        self.critical_table.setStyleSheet(TABLE_SS)
        self.critical_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.critical_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.critical_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        side_layout.addWidget(self.critical_table, stretch=1)

        self.refresh()

    def _clear_layout(self, layout: QHBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh(self):
        username = str(self.user.get("username") or "")
        role = "Yonetici" if is_admin(self.user) else "Personel"
        now = datetime.now()

        products = list_products(include_inactive=True)
        active_products = [product for product in products if int(product.get("is_active", 1)) == 1]
        critical_products = list_critical_products()
        total_stock = sum(int(product.get("stock_qty") or 0) for product in active_products)
        soon_expiring = 0
        for product in active_products:
            expiration_date = product.get("expiration_date")
            if not expiration_date:
                continue
            try:
                date_value = datetime.fromisoformat(str(expiration_date)).date()
                if date_value <= now.date() + timedelta(days=7):
                    soon_expiring += 1
            except Exception:
                pass

        if is_admin(self.user):
            recent_sales = list_sales(limit=6)
            total_users = len(list_users())
        else:
            recent_sales = list_sales_for_user(user_id=int(self.user.get("id", 0)), limit=6)
            total_users = 1

        self.lbl_welcome.setText(f"Magaza akisi hazir, {username}")
        self.lbl_intro.setText(
            "Gunluk satis, stok ve raf takibini tek bakista gorebilmeniz icin ana ekran daha kurumsal ve daha sakin hale getirildi."
        )
        self.lbl_focus.setText(f"{role} oturumu acik | {now.strftime('%d.%m.%Y %H:%M')} | Vardiya akisi stabil")

        self._clear_layout(self.stats_row)
        stats = [
            ("Aktif Urun", str(len(active_products)), "Satista gorunen urun sayisi", C["accent"], "RAF"),
            ("Toplam Stok", str(total_stock), "Magaza ve depo adedi", C["success"], "DEPO"),
            ("Kritik Urun", str(len(critical_products)), "Hizli takibe alinmasi gerekenler", C["warning"], "ALARM"),
            ("Yaklasan SKT", str(soon_expiring), "7 gun icinde kontrol edilmesi gerekenler", C["danger"], "SKT"),
        ]
        if is_admin(self.user):
            stats[1] = ("Personel", str(total_users), "Sistemde kayitli ekip", C["success"], "EKIP")

        for title, value, subtitle, accent, badge in stats:
            self.stats_row.addWidget(StatCard(title, value, subtitle, accent, badge))

        self.sales_table.setRowCount(0)
        for sale in recent_sales:
            row = self.sales_table.rowCount()
            self.sales_table.insertRow(row)
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale.get("sale_no") or "")))
            self.sales_table.setItem(row, 1, QTableWidgetItem(str(sale.get("created_at") or "")))
            self.sales_table.setItem(row, 2, QTableWidgetItem(str(sale.get("payment_type") or "-")))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"TL{float(sale.get('grand_total') or 0):.2f}"))
            self.sales_table.setRowHeight(row, 42)

        if recent_sales:
            last_sale = recent_sales[0]
            quick_text = (
                f"Son islem: {last_sale.get('sale_no')}\n"
                f"Odeme tipi: {last_sale.get('payment_type') or '-'}\n"
                f"Tutar: TL{float(last_sale.get('grand_total') or 0):.2f}\n"
                f"Tarih: {last_sale.get('created_at') or '-'}"
            )
        else:
            quick_text = "Henuz satis kaydi yok. Ilk satis sonrasinda burada gunluk market ozeti gorunecek."
        self.lbl_quick_summary.setText(quick_text)

        self.critical_table.setRowCount(0)
        for product in critical_products[:6]:
            row = self.critical_table.rowCount()
            self.critical_table.insertRow(row)
            name_item = QTableWidgetItem(str(product.get("name") or ""))
            name_item.setForeground(QColor(C["warning"]))
            self.critical_table.setItem(row, 0, name_item)
            self.critical_table.setItem(row, 1, QTableWidgetItem(str(int(product.get("stock_qty") or 0))))
            self.critical_table.setItem(row, 2, QTableWidgetItem(str(int(product.get("critical_threshold") or 0))))
            self.critical_table.setRowHeight(row, 42)
