from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.auth_service import clear_session, login as do_login, login_with_remember
from ui.style import C, btn_primary_ss, card_ss, input_ss, shadow


class LoginWindow(QMainWindow):
    def __init__(self, on_success: Callable[[Dict[str, Any]], None], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.on_success = on_success

        self.setWindowTitle("MarketCare - Kurumsal Giris")
        self.setMinimumSize(980, 620)
        self._build()

    def _build(self) -> None:
        root = QWidget()
        root.setStyleSheet(
            f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {C['sidebar']}, stop:0.55 {C['bg']}, stop:1 {C['bg_soft']});
            """
        )
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(42, 34, 42, 34)
        outer.setSpacing(0)

        shell = QFrame()
        shell.setStyleSheet(
            f"""
            QFrame {{
                background: rgba(9, 16, 30, 0.92);
                border: 1px solid {C['border_soft']};
                border-radius: 28px;
            }}
            """
        )
        shadow(shell, blur=28, dy=8)
        outer.addWidget(shell, stretch=1)

        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        left_panel = QFrame()
        left_panel.setMinimumWidth(420)
        left_panel.setStyleSheet(
            f"""
            QFrame {{
                border-top-left-radius: 24px;
                border-bottom-left-radius: 24px;
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0F3C88, stop:0.55 {C['accent2']}, stop:1 {C['accent']});
            }}
            """
        )
        shell_layout.addWidget(left_panel, 5)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(34, 34, 34, 34)
        left_layout.setSpacing(18)

        brand_badge = QLabel("MARKETCARE SUITE")
        brand_badge.setStyleSheet(
            "color:rgba(255,255,255,0.84);font-size:11px;font-weight:900;letter-spacing:1px;background:transparent;"
        )
        left_layout.addWidget(brand_badge)

        title = QLabel("Perakende operasyonlarini tek merkezden yonetin.")
        title.setWordWrap(True)
        title.setStyleSheet("color:white;font-size:31px;font-weight:900;line-height:1.2;background:transparent;")
        left_layout.addWidget(title)

        intro = QLabel(
            "Satis, stok, belge ve personel akislarini daha hizli, daha net ve daha denetlenebilir bir yapida yonetin."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(
            "color:rgba(255,255,255,0.82);font-size:14px;font-weight:600;background:transparent;line-height:1.4;"
        )
        left_layout.addWidget(intro)

        highlight_card = QFrame()
        highlight_card.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 22px;
            }
            """
        )
        highlight_layout = QVBoxLayout(highlight_card)
        highlight_layout.setContentsMargins(20, 18, 20, 18)
        highlight_layout.setSpacing(12)
        left_layout.addWidget(highlight_card)

        for text in (
            "Canli stok gorunurlugu ve kritik esik takibi",
            "PDF slip ve fatura uretimi ile kayit duzeni",
            "Yetkili personel girisi ve guvenli oturum akisi",
        ):
            item = QLabel(f"• {text}")
            item.setWordWrap(True)
            item.setStyleSheet("color:white;font-size:13px;font-weight:700;background:transparent;")
            highlight_layout.addWidget(item)

        left_layout.addStretch()

        footer = QLabel("Kurumsal market operasyonlari icin sade, resmi ve hizli masaustu deneyimi.")
        footer.setWordWrap(True)
        footer.setStyleSheet("color:rgba(255,255,255,0.74);font-size:12px;font-weight:600;background:transparent;")
        left_layout.addWidget(footer)

        right_panel = QWidget()
        right_panel.setStyleSheet("background:transparent;")
        shell_layout.addWidget(right_panel, 6)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(42, 42, 42, 42)
        right_layout.setSpacing(18)

        header = QLabel("Oturum Ac")
        header.setStyleSheet(f"color:{C['text']};font-size:28px;font-weight:900;")
        right_layout.addWidget(header)

        subheader = QLabel("Yetkili hesap bilgileriniz ile sisteme guvenli giris yapin.")
        subheader.setWordWrap(True)
        subheader.setStyleSheet(f"color:{C['text_sub']};font-size:13px;font-weight:700;")
        right_layout.addWidget(subheader)

        trust_row = QHBoxLayout()
        trust_row.setSpacing(10)
        right_layout.addLayout(trust_row)

        for badge_text in ("Yetkili Giris", "Lokal Veri", "Oturum Kaydi"):
            badge = QLabel(badge_text)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                f"""
                background:{C['row_sel']};
                color:{C['accent']};
                border:1px solid {C['border_soft']};
                border-radius:15px;
                padding:8px 10px;
                font-size:11px;
                font-weight:800;
                """
            )
            trust_row.addWidget(badge)

        form_card = QFrame()
        form_card.setStyleSheet(card_ss())
        shadow(form_card, blur=18, dy=4)
        right_layout.addWidget(form_card)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(12)
        form_grid.setVerticalSpacing(12)
        form_layout.addLayout(form_grid)

        username_label = QLabel("Kullanici Adi")
        username_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Kullanıcı Adı")
        self.inp_username.setStyleSheet(input_ss())
        self.inp_username.setMinimumHeight(46)

        password_label = QLabel("Sifre")
        password_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Sifrenizi girin")
        self.inp_password.setEchoMode(QLineEdit.Password)
        self.inp_password.setStyleSheet(input_ss())
        self.inp_password.setMinimumHeight(46)

        form_grid.addWidget(username_label, 0, 0)
        form_grid.addWidget(self.inp_username, 1, 0)
        form_grid.addWidget(password_label, 2, 0)
        form_grid.addWidget(self.inp_password, 3, 0)

        self.cb_show_pw = QCheckBox("Sifreyi goster")
        self.cb_show_pw.setStyleSheet(
            f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;"
        )
        self.cb_show_pw.stateChanged.connect(self._toggle_show_password)

        self.cb_remember = QCheckBox("Beni hatirla")
        self.cb_remember.setStyleSheet(
            f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;"
        )

        option_row = QHBoxLayout()
        option_row.setSpacing(14)
        option_row.addWidget(self.cb_show_pw)
        option_row.addWidget(self.cb_remember)
        option_row.addStretch()
        form_layout.addLayout(option_row)

        info_note = QLabel("Varsayilan hesaplar README dosyasinda yer alir. Giris basarisiz olursa sistem uyarisi gosterilir.")
        info_note.setWordWrap(True)
        info_note.setStyleSheet(
            f"background:rgba(255,255,255,0.03);color:{C['text_dim']};border:1px solid {C['border_soft']};"
            "border-radius:15px;padding:10px 12px;font-size:12px;font-weight:700;"
        )
        form_layout.addWidget(info_note)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self.btn_login = QPushButton("Giris Yap")
        self.btn_login.setStyleSheet(btn_primary_ss())
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setMinimumWidth(180)
        self.btn_login.setMinimumHeight(46)
        button_row.addWidget(self.btn_login)
        form_layout.addLayout(button_row)

        right_layout.addStretch()

        self.btn_login.clicked.connect(self._try_login)
        self.inp_password.returnPressed.connect(self._try_login)
        self.inp_username.returnPressed.connect(self.inp_password.setFocus)
        self.inp_username.setFocus()

    def _toggle_show_password(self) -> None:
        self.inp_password.setEchoMode(QLineEdit.Normal if self.cb_show_pw.isChecked() else QLineEdit.Password)

    def _show_error(self, mesaj: str) -> None:
        pencere = QMessageBox(self)
        pencere.setIcon(QMessageBox.Warning)
        pencere.setText(mesaj)
        pencere.setWindowTitle("Giris Hatasi")
        pencere.setStyleSheet(f"QMessageBox{{background:{C['card']};color:{C['text']};}}")
        pencere.exec_()

    def _try_login(self) -> None:
        kullanici_adi = self.inp_username.text().strip()
        sifre = self.inp_password.text()

        if not kullanici_adi:
            self._show_error("Kullanici adi bos olamaz.")
            return
        if not sifre:
            self._show_error("Sifre bos olamaz.")
            return

        sonuc = do_login(kullanici_adi, sifre)
        if not sonuc.ok or not sonuc.user:
            self._show_error(sonuc.error or "Giris basarisiz.")
            return

        if self.cb_remember.isChecked():
            login_with_remember(kullanici_adi)
        else:
            clear_session()

        self.on_success(sonuc.user)
        self.close()
