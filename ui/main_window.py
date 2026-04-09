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
        self.setFixedHeight(52)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, active: bool) -> None:
        if active:
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 rgba(37,99,235,0.28), stop:1 rgba(56,189,248,0.16));
                    color:{C['text']};
                    border:1px solid rgba(125,211,252,0.22);
                    border-radius:16px;
                    text-align:left;
                    padding-left:18px;
                    font-size:13px;
                    font-weight:800;
                }}
                """
            )
        else:
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background:transparent;
                    color:{C['text_sub']};
                    border:1px solid transparent;
                    border-radius:16px;
                    text-align:left;
                    padding-left:18px;
                    font-size:13px;
                    font-weight:700;
                }}
                QPushButton:hover {{
                    background:{C['card_soft']};
                    color:{C['text']};
                    border:1px solid {C['border_soft']};
                }}
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
        self.setMinimumSize(1220, 780)
        self.resize(1400, 860)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};color:{C['text']};}}")

        self._build_ui()
        self._start_clock()

    def _build_ui(self) -> None:
        merkez = QWidget()
        merkez.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(merkez)

        ana_dizilim = QHBoxLayout(merkez)
        ana_dizilim.setContentsMargins(18, 18, 18, 18)
        ana_dizilim.setSpacing(18)

        yan_menu = QFrame()
        yan_menu.setFixedWidth(286)
        yan_menu.setStyleSheet(
            f"""
            background:{C['sidebar']};
            border:1px solid {C['border_soft']};
            border-radius:28px;
            """
        )
        ana_dizilim.addWidget(yan_menu)

        yan_dizilim = QVBoxLayout(yan_menu)
        yan_dizilim.setContentsMargins(18, 18, 18, 18)
        yan_dizilim.setSpacing(10)

        brand_card = QFrame()
        brand_card.setStyleSheet(
            f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #0F3C88, stop:0.55 {C['accent2']}, stop:1 {C['accent']});
            border-radius:20px;
            """
        )
        brand_card.setMinimumHeight(132)
        yan_dizilim.addWidget(brand_card)

        brand_layout = QVBoxLayout(brand_card)
        brand_layout.setContentsMargins(18, 16, 18, 16)
        brand_layout.setSpacing(6)

        brand_badge = QLabel("MARKETCARE")
        brand_badge.setStyleSheet("color:rgba(255,255,255,0.82);font-size:10px;font-weight:900;letter-spacing:1px;")
        brand_layout.addWidget(brand_badge)

        brand_title = QLabel("Kurumsal Market Yönetimi")
        brand_title.setWordWrap(True)
        brand_title.setStyleSheet("color:white;font-size:20px;font-weight:900;")
        brand_layout.addWidget(brand_title)

        brand_subtitle = QLabel("Satış, stok, belge ve ekip akışları tek panelde")
        brand_subtitle.setWordWrap(True)
        brand_subtitle.setStyleSheet("color:rgba(255,255,255,0.78);font-size:12px;font-weight:700;")
        brand_layout.addWidget(brand_subtitle)

        self.nav_buttons: List[SideBtn] = []
        sayfalar: List[Tuple[str, str, QWidget]] = [
            ("⌂", "Panel", DashboardPage(user=self.user)),
            ("⌕", "Satis", PersonnelSalesPage(user=self.user)),
            ("▣", "Belgeler", AdminInvoicesPage(user=self.user)),
        ]

        self._add_sidebar_section(yan_dizilim, "Operasyon")
        for icon, ad, _ in sayfalar:
            buton = SideBtn(icon, ad)
            buton.clicked.connect(lambda _, page_name=ad: self._goto(page_name))
            yan_dizilim.addWidget(buton)
            self.nav_buttons.append(buton)

        if is_admin(self.user):
            self._add_sidebar_section(yan_dizilim, "Yonetim")
            yonetici_sayfalari = [
                ("◫", "Urunler", AdminProductsPage()),
                ("↕", "Stok Hareketleri", AdminStockPage(user=self.user)),
                ("◉", "Personel", AdminPersonnelPage(user=self.user)),
            ]
            for sayfa in yonetici_sayfalari:
                sayfalar.append(sayfa)
                buton = SideBtn(sayfa[0], sayfa[1])
                buton.clicked.connect(lambda _, page_name=sayfa[1]: self._goto(page_name))
                yan_dizilim.addWidget(buton)
                self.nav_buttons.append(buton)

        yan_dizilim.addStretch()

        session_card = QFrame()
        session_card.setStyleSheet(
            f"""
            background:{C['card_soft']};
            border:1px solid {C['border_soft']};
            border-radius:20px;
            """
        )
        yan_dizilim.addWidget(session_card)

        session_layout = QVBoxLayout(session_card)
        session_layout.setContentsMargins(16, 14, 16, 14)
        session_layout.setSpacing(6)

        lbl_session_title = QLabel("Aktif Oturum")
        lbl_session_title.setStyleSheet(f"color:{C['text_dim']};font-size:11px;font-weight:900;")
        session_layout.addWidget(lbl_session_title)

        lbl_session_user = QLabel(str(self.user.get("username", "")))
        lbl_session_user.setStyleSheet(f"color:{C['text']};font-size:16px;font-weight:900;")
        session_layout.addWidget(lbl_session_user)

        lbl_session_role = QLabel(f"Yetki: {str(self.user.get('role', '')).upper()}")
        lbl_session_role.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        session_layout.addWidget(lbl_session_role)

        self.lbl_time = QLabel()
        self.lbl_time.setAlignment(Qt.AlignLeft)
        self.lbl_time.setStyleSheet(f"color:{C['accent']};font-size:12px;font-weight:800;")
        session_layout.addWidget(self.lbl_time)

        icerik = QWidget()
        icerik.setStyleSheet("background:transparent;")
        ana_dizilim.addWidget(icerik, stretch=1)

        icerik_dizilim = QVBoxLayout(icerik)
        icerik_dizilim.setContentsMargins(0, 0, 0, 0)
        icerik_dizilim.setSpacing(16)

        ust_cubuk = QFrame()
        ust_cubuk.setFixedHeight(96)
        ust_cubuk.setStyleSheet(
            f"""
            background:{C['sidebar']};
            border:1px solid {C['border_soft']};
            border-radius:28px;
            """
        )
        icerik_dizilim.addWidget(ust_cubuk)

        ust_dizilim = QHBoxLayout(ust_cubuk)
        ust_dizilim.setContentsMargins(24, 18, 24, 18)
        ust_dizilim.setSpacing(14)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        ust_dizilim.addLayout(title_col)

        self.lbl_page = QLabel("Panel")
        self.lbl_page.setStyleSheet(f"color:{C['text']};font-size:24px;font-weight:900;background:transparent;")
        title_col.addWidget(self.lbl_page)

        self.lbl_page_hint = QLabel("Operasyon ekranı hazır.")
        self.lbl_page_hint.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;")
        title_col.addWidget(self.lbl_page_hint)

        ust_dizilim.addStretch()

        durum_etiketi = QLabel("SISTEM AKTIF")
        durum_etiketi.setStyleSheet(
            f"""
            background:rgba(56,189,248,0.10);
            color:{C['accent']};
            border:1px solid rgba(125,211,252,0.14);
            border-radius:16px;
            padding:9px 12px;
            font-size:11px;
            font-weight:900;
            """
        )
        ust_dizilim.addWidget(durum_etiketi)

        kullanici_etiketi = QLabel(f"{self.user.get('username', '')} | {str(self.user.get('role', '')).upper()}")
        kullanici_etiketi.setStyleSheet(
            f"""
            background:rgba(255,255,255,0.04);
            color:{C['text_sub']};
            border:1px solid {C['border_soft']};
            border-radius:16px;
            padding:9px 12px;
            font-size:12px;
            font-weight:800;
            """
        )
        ust_dizilim.addWidget(kullanici_etiketi)

        self.info_chip = QLabel("Guncelleme akisi hazir")
        self.info_chip.setStyleSheet(
            f"""
            background:rgba(255,255,255,0.04);
            color:{C['text_dim']};
            border:1px solid {C['border_soft']};
            border-radius:16px;
            padding:9px 12px;
            font-size:12px;
            font-weight:700;
            """
        )
        ust_dizilim.addWidget(self.info_chip)

        cikis_butonu = QPushButton("Cikis Yap")
        cikis_butonu.setStyleSheet(btn_danger_ss())
        cikis_butonu.setCursor(Qt.PointingHandCursor)
        cikis_butonu.setMinimumHeight(42)
        cikis_butonu.setMinimumWidth(138)
        cikis_butonu.clicked.connect(self._logout_and_save)
        ust_dizilim.addWidget(cikis_butonu)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(
            f"""
            QStackedWidget {{
                background:{C['bg']};
                border:1px solid {C['border_soft']};
                border-radius:28px;
            }}
            """
        )
        self.page_names: List[str] = []
        for _, ad, widget in sayfalar:
            self.stack.addWidget(widget)
            self.page_names.append(ad)
        icerik_dizilim.addWidget(self.stack, stretch=1)

        self._goto("Panel")

    def _add_sidebar_section(self, layout: QVBoxLayout, text: str) -> None:
        etiket = QLabel(text)
        etiket.setStyleSheet(f"color:{C['text_dim']};font-size:11px;font-weight:900;padding:12px 4px 6px 4px;")
        layout.addWidget(etiket)

    def _goto(self, page_name: str) -> None:
        if page_name not in self.page_names:
            return

        index = self.page_names.index(page_name)
        self.stack.setCurrentIndex(index)
        self.lbl_page.setText(page_name)
        self.lbl_page_hint.setText(f"{page_name} modulu aktif.")
        self.info_chip.setText(f"V2 arayuz aktif | {page_name} gorunumu optimize edildi")

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
        self.lbl_time.setText(datetime.now().strftime("%d.%m.%Y | %H:%M:%S"))
