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

    def _refresh(self, active: bool) -> None:
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

    def setChecked(self, value: bool) -> None:
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

        rol = str(user.get("role", "")).upper()
        self.setWindowTitle(f"MarketCare - {rol}")
        self.setMinimumSize(1150, 750)
        self.resize(1320, 820)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};color:{C['text']};}}")

        self._build_ui()
        self._start_clock()

    def _build_ui(self) -> None:
        merkez = QWidget()
        merkez.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(merkez)

        ana_dizilim = QHBoxLayout(merkez)
        ana_dizilim.setContentsMargins(0, 0, 0, 0)
        ana_dizilim.setSpacing(0)

        yan_menu = QFrame()
        yan_menu.setFixedWidth(240)
        yan_menu.setStyleSheet(f"background:{C['sidebar']};border-right:1px solid {C['border']};")

        yan_dizilim = QVBoxLayout(yan_menu)
        yan_dizilim.setContentsMargins(0, 0, 0, 18)
        yan_dizilim.setSpacing(0)

        logo = QFrame()
        logo.setFixedHeight(86)
        logo.setStyleSheet(
            f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {C['accent2']},stop:1 {C['accent']});
            """
        )
        logo_dizilim = QVBoxLayout(logo)
        logo_dizilim.setContentsMargins(16, 14, 16, 12)

        baslik = QLabel("MarketCare")
        baslik.setStyleSheet("color:white;font-size:16px;font-weight:900;background:transparent;")
        alt_baslik = QLabel("Mini Market Yonetimi")
        alt_baslik.setStyleSheet(
            "color:rgba(255,255,255,0.72);font-size:10px;font-weight:700;background:transparent;"
        )
        logo_dizilim.addWidget(baslik)
        logo_dizilim.addWidget(alt_baslik)
        yan_dizilim.addWidget(logo)
        yan_dizilim.addSpacing(14)

        self.nav_buttons: List[SideBtn] = []
        sayfalar: List[Tuple[str, str, QWidget]] = [
            ("🏠", "Panel", DashboardPage(user=self.user)),
            ("🛒", "Satis", PersonnelSalesPage(user=self.user)),
            ("🧾", "Belgeler", AdminInvoicesPage(user=self.user)),
        ]

        self._add_sidebar_section(yan_dizilim, "Genel")
        for icon, ad, _ in sayfalar:
            buton = SideBtn(icon, ad)
            buton.clicked.connect(lambda _, page_name=ad: self._goto(page_name))
            yan_dizilim.addWidget(buton)
            self.nav_buttons.append(buton)

        if is_admin(self.user):
            self._add_sidebar_section(yan_dizilim, "Yonetim")
            yonetici_sayfalari = [
                ("📦", "Urunler", AdminProductsPage()),
                ("↕", "Stok Hareketleri", AdminStockPage(user=self.user)),
                ("👥", "Personel", AdminPersonnelPage(user=self.user)),
            ]
            for sayfa in yonetici_sayfalari:
                sayfalar.append(sayfa)
                buton = SideBtn(sayfa[0], sayfa[1])
                buton.clicked.connect(lambda _, page_name=sayfa[1]: self._goto(page_name))
                yan_dizilim.addWidget(buton)
                self.nav_buttons.append(buton)

        yan_dizilim.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;")
        yan_dizilim.addWidget(self.lbl_time)

        ana_dizilim.addWidget(yan_menu)

        icerik = QWidget()
        icerik.setStyleSheet(f"background:{C['bg']};")
        icerik_dizilim = QVBoxLayout(icerik)
        icerik_dizilim.setContentsMargins(0, 0, 0, 0)
        icerik_dizilim.setSpacing(0)

        ust_cubuk = QFrame()
        ust_cubuk.setFixedHeight(64)
        ust_cubuk.setStyleSheet(f"background:{C['sidebar']};border-bottom:1px solid {C['border']};")
        ust_dizilim = QHBoxLayout(ust_cubuk)
        ust_dizilim.setContentsMargins(22, 0, 22, 0)
        ust_dizilim.setSpacing(12)

        self.lbl_page = QLabel("Panel")
        self.lbl_page.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        ust_dizilim.addWidget(self.lbl_page)
        ust_dizilim.addStretch()

        kullanici_etiketi = QLabel(
            f"👤  {self.user.get('username', '')} ({str(self.user.get('role', '')).upper()})"
        )
        kullanici_etiketi.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        ust_dizilim.addWidget(kullanici_etiketi)

        durum_etiketi = QLabel("MARKET AKTIF")
        durum_etiketi.setStyleSheet(
            f"background:{C['row_sel']};color:{C['accent']};border:1px solid {C['border']};"
            "border-radius:11px;padding:6px 10px;font-size:10px;font-weight:900;"
        )
        ust_dizilim.addWidget(durum_etiketi)

        cikis_butonu = QPushButton("Cikis Yap")
        cikis_butonu.setStyleSheet(btn_danger_ss())
        cikis_butonu.setCursor(Qt.PointingHandCursor)
        cikis_butonu.setMinimumHeight(38)
        cikis_butonu.setMinimumWidth(132)
        cikis_butonu.clicked.connect(self._logout_and_save)
        ust_dizilim.addWidget(cikis_butonu)

        icerik_dizilim.addWidget(ust_cubuk)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C['bg']};")
        self.page_names: List[str] = []
        for _, ad, widget in sayfalar:
            self.stack.addWidget(widget)
            self.page_names.append(ad)

        icerik_dizilim.addWidget(self.stack)
        ana_dizilim.addWidget(icerik, stretch=1)

        self._goto("Panel")

    def _add_sidebar_section(self, layout: QVBoxLayout, text: str) -> None:
        etiket = QLabel(text)
        etiket.setStyleSheet(f"color:{C['text_dim']};font-size:11px;font-weight:900;padding:10px 16px 6px 16px;")
        layout.addWidget(etiket)

    def _goto(self, page_name: str) -> None:
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
                return

    def _on_logout(self) -> None:
        if callable(self.on_logout):
            self.on_logout()
        self.close()

    def _save_database(self) -> None:
        from db.connection import get_connection

        try:
            with get_connection() as conn:
                conn.commit()
            self.statusBar().showMessage("Veritabani kaydedildi.", 3000)
        except Exception as exc:
            self.statusBar().showMessage(f"Veritabani kaydetme hatasi: {exc}", 5000)

    def _logout_and_save(self) -> None:
        self._save_database()
        self._on_logout()

    def _start_clock(self) -> None:
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _update_clock(self) -> None:
        self.lbl_time.setText(datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))
