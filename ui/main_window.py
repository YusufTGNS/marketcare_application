from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from services.permission_service import is_admin
from ui.pages.admin_invoices_page import AdminInvoicesPage
from ui.pages.admin_personnel_page import AdminPersonnelPage
from ui.pages.admin_products_page import AdminProductsPage
from ui.pages.admin_stock_page import AdminStockPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.personnel_sales_page import PersonnelSalesPage
from ui.style import C, btn_danger_ss


class SideBtn(QPushButton):
    def __init__(self, icon: str, text: str, parent: Optional[QWidget] = None):
        super().__init__(f"  {icon}  {text}", parent)
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, active: bool):
        if active:
            self.setStyleSheet(
                f"""
                QPushButton{{background:{C['row_sel']};color:{C['accent2']};
                    border:none;border-left:3px solid {C['accent']};
                    border-radius:0;text-align:left;padding-left:16px;
                    font-size:13px;font-weight:700;}}
                """
            )
        else:
            self.setStyleSheet(
                f"""
                QPushButton{{background:transparent;color:{C['text_sub']};
                    border:none;border-left:3px solid transparent;
                    border-radius:0;text-align:left;padding-left:16px;font-size:13px;}}
                QPushButton:hover{{background:{C['card']};color:{C['text']};
                    border-left:3px solid {C['accent']};}}
                """
            )

    def setChecked(self, value: bool):
        super().setChecked(value)
        self._refresh(value)


class MainWindow(QMainWindow):
    def __init__(
        self,
        user: Dict[str, Any],
        on_logout: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout

        role = str(user.get("role", "")).upper()
        self.setWindowTitle(f"MarketCare - {role}")
        self.setMinimumSize(1150, 750)
        self.resize(1320, 820)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};color:{C['text']};}}")

        self._build_ui()
        self._start_clock()

    def _build_ui(self):
        center = QWidget()
        center.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(center)

        main = QHBoxLayout(center)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background:{C['sidebar']};border-right:1px solid {C['border']};")

        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 18)
        sb.setSpacing(0)

        logo = QFrame()
        logo.setFixedHeight(86)
        logo.setStyleSheet(
            f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {C['accent2']},stop:1 {C['accent']});
            """
        )
        logo_lay = QVBoxLayout(logo)
        logo_lay.setContentsMargins(16, 14, 16, 12)

        title = QLabel("MarketCare")
        title.setStyleSheet("color:white;font-size:16px;font-weight:900;background:transparent;")
        subtitle = QLabel("Mini Market Zinciri")
        subtitle.setStyleSheet("color:rgba(255,255,255,0.72);font-size:10px;font-weight:700;background:transparent;")
        logo_lay.addWidget(title)
        logo_lay.addWidget(subtitle)
        sb.addWidget(logo)
        sb.addSpacing(14)

        self.nav_buttons: List[SideBtn] = []
        pages: List[Tuple[str, str, QWidget]] = [
            ("🏠", "Dashboard", DashboardPage(user=self.user)),
            ("🛒", "Satış", PersonnelSalesPage(user=self.user)),
            ("🧾", "Faturalar", AdminInvoicesPage(user=self.user)),
        ]

        self._add_sidebar_section(sb, "Genel")
        for icon, name, _ in pages:
            button = SideBtn(icon, name)
            button.clicked.connect(lambda _, n=name: self._goto(n))
            sb.addWidget(button)
            self.nav_buttons.append(button)

        if is_admin(self.user):
            self._add_sidebar_section(sb, "Yönetici Özel")
            admin_pages = [
                ("📦", "Ürünler", AdminProductsPage()),
                ("↕️", "Stok Hareketleri", AdminStockPage(user=self.user)),
                ("👥", "Personel", AdminPersonnelPage(user=self.user)),
            ]
            for page in admin_pages:
                pages.append(page)
                button = SideBtn(page[0], page[1])
                button.clicked.connect(lambda _, n=page[1]: self._goto(n))
                sb.addWidget(button)
                self.nav_buttons.append(button)

        sb.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;")
        sb.addWidget(self.lbl_time)

        main.addWidget(sidebar)

        content = QWidget()
        content.setStyleSheet(f"background:{C['bg']};")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        topbar = QFrame()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet(f"background:{C['sidebar']};border-bottom:1px solid {C['border']};")
        top_lay = QHBoxLayout(topbar)
        top_lay.setContentsMargins(22, 0, 22, 0)
        top_lay.setSpacing(12)

        self.lbl_page = QLabel("Dashboard")
        self.lbl_page.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        top_lay.addWidget(self.lbl_page)
        top_lay.addStretch()

        user_lbl = QLabel(f"👤  {self.user.get('username', '')} ({str(self.user.get('role', '')).upper()})")
        user_lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        top_lay.addWidget(user_lbl)

        badge_lbl = QLabel("MARKET AKTIF")
        badge_lbl.setStyleSheet(
            f"background:{C['row_sel']};color:{C['accent']};border:1px solid {C['border']};"
            "border-radius:11px;padding:6px 10px;font-size:10px;font-weight:900;"
        )
        top_lay.addWidget(badge_lbl)

        btn_logout = QPushButton("Çıkış Yap")
        btn_logout.setStyleSheet(btn_danger_ss())
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setMinimumHeight(38)
        btn_logout.setMinimumWidth(132)
        btn_logout.clicked.connect(self._logout_and_save)
        top_lay.addWidget(btn_logout)

        content_lay.addWidget(topbar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C['bg']};")
        self.page_names: List[str] = []
        for _, name, widget in pages:
            self.stack.addWidget(widget)
            self.page_names.append(name)

        content_lay.addWidget(self.stack)
        main.addWidget(content, stretch=1)

        self._goto("Dashboard")

    def _add_sidebar_section(self, layout: QVBoxLayout, text: str):
        label = QLabel(text)
        label.setStyleSheet(f"color:{C['text_dim']};font-size:11px;font-weight:900;padding:10px 16px 6px 16px;")
        layout.addWidget(label)

    def _goto(self, page_name: str):
        if page_name not in self.page_names:
            return
        index = self.page_names.index(page_name)
        self.stack.setCurrentIndex(index)
        self.lbl_page.setText(page_name)
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

        widget = self.stack.widget(index)
        refresh_fn = getattr(widget, "refresh", None)
        if callable(refresh_fn):
            try:
                refresh_fn()
            except TypeError:
                pass

    def _on_logout(self):
        if callable(self.on_logout):
            self.on_logout()
        self.close()

    def _save_database(self):
        from db.connection import get_connection

        try:
            with get_connection() as conn:
                conn.commit()
            self.statusBar().showMessage("Veritabani kaydedildi.", 3000)
        except Exception as exc:
            self.statusBar().showMessage(f"Veritabani kaydetme hatasi: {exc}", 5000)

    def _logout_and_save(self):
        self._save_database()
        self._on_logout()

    def _start_clock(self):
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        self.lbl_time.setText(datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))
