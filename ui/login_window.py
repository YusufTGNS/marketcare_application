from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
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

        self.setWindowTitle("MarketCare - Yonetim Girisi")
        self.setMinimumSize(620, 520)
        self._build()

    def _build(self) -> None:
        kok = QWidget()
        kok.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(kok)

        ana_dizilim = QVBoxLayout(kok)
        ana_dizilim.setContentsMargins(36, 30, 36, 30)
        ana_dizilim.setSpacing(20)

        kahraman = QFrame()
        kahraman.setStyleSheet(
            f"""
            QFrame {{
                border-radius: 18px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1F2F27, stop:0.6 {C['accent2']}, stop:1 {C['accent']});
            }}
            """
        )
        shadow(kahraman, blur=24, dy=6)
        kahraman_dizilim = QVBoxLayout(kahraman)
        kahraman_dizilim.setContentsMargins(24, 22, 24, 22)
        kahraman_dizilim.setSpacing(6)

        baslik = QLabel("MarketCare")
        baslik.setStyleSheet("color:white;font-size:28px;font-weight:900;letter-spacing:0.4px;")
        alt_baslik = QLabel("Satis ve stok yonetimine hizli giris yapin.")
        alt_baslik.setStyleSheet("color:rgba(255,255,255,0.78);font-size:13px;font-weight:600;")
        kahraman_dizilim.addWidget(baslik)
        kahraman_dizilim.addWidget(alt_baslik)
        ana_dizilim.addWidget(kahraman)

        kart = QWidget()
        kart.setStyleSheet(card_ss())
        shadow(kart)
        kart_dizilim = QVBoxLayout(kart)
        kart_dizilim.setContentsMargins(22, 22, 22, 22)
        kart_dizilim.setSpacing(14)
        ana_dizilim.addWidget(kart)

        kart_baslik = QLabel("Oturum Ac")
        kart_baslik.setStyleSheet(f"color:{C['text']};font-size:18px;font-weight:900;")
        kart_bilgi = QLabel("Kullanici adinizi ve sifrenizi girin.")
        kart_bilgi.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        kart_dizilim.addWidget(kart_baslik)
        kart_dizilim.addWidget(kart_bilgi)

        kullanici_etiketi = QLabel("Kullanici Adi")
        kullanici_etiketi.setFixedWidth(120)
        kullanici_etiketi.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("orn. admin")
        self.inp_username.setStyleSheet(input_ss())

        sifre_etiketi = QLabel("Sifre")
        sifre_etiketi.setFixedWidth(120)
        sifre_etiketi.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Sifrenizi girin")
        self.inp_password.setEchoMode(QLineEdit.Password)
        self.inp_password.setStyleSheet(input_ss())

        self.cb_show_pw = QCheckBox("Sifreyi goster")
        self.cb_show_pw.setStyleSheet(
            f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;"
        )
        self.cb_show_pw.stateChanged.connect(self._toggle_show_password)

        self.cb_remember = QCheckBox("Beni hatirla")
        self.cb_remember.setStyleSheet(
            f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;"
        )

        kullanici_satiri = QHBoxLayout()
        kullanici_satiri.setSpacing(12)
        kullanici_satiri.addWidget(kullanici_etiketi)
        kullanici_satiri.addWidget(self.inp_username, 1)

        sifre_satiri = QHBoxLayout()
        sifre_satiri.setSpacing(12)
        sifre_satiri.addWidget(sifre_etiketi)
        sifre_satiri.addWidget(self.inp_password, 1)

        kart_dizilim.addLayout(kullanici_satiri)
        kart_dizilim.addLayout(sifre_satiri)

        secenek_satiri = QHBoxLayout()
        secenek_satiri.setSpacing(12)
        secenek_satiri.addWidget(self.cb_show_pw)
        secenek_satiri.addWidget(self.cb_remember)
        secenek_satiri.addStretch()
        kart_dizilim.addLayout(secenek_satiri)

        buton_satiri = QHBoxLayout()
        buton_satiri.setSpacing(10)
        buton_satiri.addStretch()
        self.btn_login = QPushButton("Giris Yap")
        self.btn_login.setStyleSheet(btn_primary_ss())
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setFixedWidth(160)
        buton_satiri.addWidget(self.btn_login)
        kart_dizilim.addLayout(buton_satiri)

        self.btn_login.clicked.connect(self._try_login)
        self.inp_password.returnPressed.connect(self._try_login)

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
