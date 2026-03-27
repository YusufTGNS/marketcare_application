from typing import Callable, Dict, Any, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QFrame,
)

from ui.style import C, card_ss, btn_primary_ss, input_ss, shadow
from services.auth_service import login as do_login
from services.auth_service import (
    try_auto_login_from_session,
    login_with_remember,
    clear_session,
)


class LoginWindow(QMainWindow):
    def __init__(self, on_success: Callable[[Dict[str, Any]], None], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.on_success = on_success

        self.setWindowTitle("MarketCare - Yönetim Paneli")
        self.setMinimumSize(620, 520)

        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(root)

        lay = QVBoxLayout(root)
        lay.setContentsMargins(36, 30, 36, 30)
        lay.setSpacing(20)

        hero = QFrame()
        hero.setStyleSheet(
            f"""
            QFrame {{
                border-radius: 18px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1F2F27, stop:0.6 {C['accent2']}, stop:1 {C['accent']});
            }}
            """
        )
        shadow(hero, blur=24, dy=6)
        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(24, 22, 24, 22)
        hero_lay.setSpacing(6)

        title = QLabel("MarketCare")
        title.setStyleSheet("color:white;font-size:28px;font-weight:900;letter-spacing:0.4px;")
        subtitle = QLabel("Hızlı giriş yapın ve satış ekranına kaldığınız yerden dönün.")
        subtitle.setStyleSheet("color:rgba(255,255,255,0.78);font-size:13px;font-weight:600;")
        hero_lay.addWidget(title)
        hero_lay.addWidget(subtitle)
        lay.addWidget(hero)

        card = QWidget()
        card.setStyleSheet(card_ss())
        shadow(card)
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(22, 22, 22, 22)
        c_lay.setSpacing(14)
        lay.addWidget(card)

        head = QLabel("Oturum Aç")
        head.setStyleSheet(f"color:{C['text']};font-size:18px;font-weight:900;")
        info = QLabel("Kullanıcı adı ve şifrenizi girin.")
        info.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        c_lay.addWidget(head)
        c_lay.addWidget(info)

        lbl_u = QLabel("Kullanıcı Adı")
        lbl_u.setFixedWidth(120)
        lbl_u.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("örn. admin")
        self.inp_username.setStyleSheet(input_ss())

        lbl_p = QLabel("Şifre")
        lbl_p.setFixedWidth(120)
        lbl_p.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:800;")
        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Şifrenizi girin")
        self.inp_password.setEchoMode(QLineEdit.Password)
        self.inp_password.setStyleSheet(input_ss())

        self.cb_show_pw = QCheckBox("Şifreyi göster")
        self.cb_show_pw.setStyleSheet(
            f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;"
        )
        self.cb_show_pw.stateChanged.connect(self._toggle_show_password)

        self.cb_remember = QCheckBox("Beni hatırla")
        self.cb_remember.setStyleSheet(
            f"color:{C['text_sub']};font-size:12px;font-weight:700;background:transparent;"
        )

        form_u = QHBoxLayout()
        form_u.setSpacing(12)
        form_u.addWidget(lbl_u)
        form_u.addWidget(self.inp_username, 1)

        form_p = QHBoxLayout()
        form_p.setSpacing(12)
        form_p.addWidget(lbl_p)
        form_p.addWidget(self.inp_password, 1)

        c_lay.addLayout(form_u)
        c_lay.addLayout(form_p)

        options_row = QHBoxLayout()
        options_row.setSpacing(12)
        options_row.addWidget(self.cb_show_pw)
        options_row.addWidget(self.cb_remember)
        options_row.addStretch()
        c_lay.addLayout(options_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()
        self.btn_login = QPushButton("Giriş Yap")
        self.btn_login.setStyleSheet(btn_primary_ss())
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setFixedWidth(160)
        btn_row.addWidget(self.btn_login)
        c_lay.addLayout(btn_row)

        self.btn_login.clicked.connect(self._try_login)
        self.inp_password.returnPressed.connect(self._try_login)

    def _toggle_show_password(self):
        if self.cb_show_pw.isChecked():
            self.inp_password.setEchoMode(QLineEdit.Normal)
        else:
            self.inp_password.setEchoMode(QLineEdit.Password)

    def _show_error(self, msg: str):
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Warning)
        dlg.setText(msg)
        dlg.setWindowTitle("Giriş Hatası")
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};color:{C['text']};}}")
        dlg.exec_()

    def _try_autologin(self):
        res = try_auto_login_from_session()
        if res.ok and res.user:
            self.on_success(res.user)
            self.close()

    def _try_login(self):
        username = self.inp_username.text().strip()
        password = self.inp_password.text()
        if not username:
            self._show_error("Kullanıcı adı boş olamaz.")
            return
        if not password:
            self._show_error("Şifre boş olamaz.")
            return

        res = do_login(username, password)
        if not res.ok or not res.user:
            self._show_error(res.error or "Giriş başarısız.")
            return

        if self.cb_remember.isChecked():
            login_with_remember(username)
        else:
            clear_session()

        self.on_success(res.user)
        self.close()
