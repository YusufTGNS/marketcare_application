from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QMessageBox,
)

from ui.style import C, card_ss, input_ss, btn_success_ss, btn_danger_ss, TABLE_SS, shadow
from repositories.users_repo import list_users
from services.auth_service import create_user, reset_database
from utilities.datetime_utils import format_db_datetime_local


class AdminPersonnelPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        title = QLabel("Personel Yönetimi")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        lay.addWidget(title)

        action_card = QFrame()
        action_card.setStyleSheet(card_ss())
        shadow(action_card)
        action_lay = QVBoxLayout(action_card)
        action_lay.setContentsMargins(18, 16, 18, 16)
        action_lay.setSpacing(12)
        lay.addWidget(action_card)

        lbl_reset = QLabel("Veritabanı İşlemleri")
        lbl_reset.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        action_lay.addWidget(lbl_reset)

        btn_reset = QPushButton("DB Sıfırla")
        btn_reset.setStyleSheet(btn_danger_ss())
        btn_reset.clicked.connect(self._reset_db)
        action_lay.addWidget(btn_reset)

        create_card = QFrame()
        create_card.setStyleSheet(card_ss())
        shadow(create_card)
        create_lay = QVBoxLayout(create_card)
        create_lay.setContentsMargins(18, 16, 18, 16)
        create_lay.setSpacing(12)
        lay.addWidget(create_card)

        lbl_create = QLabel("Yeni Kullanıcı Oluştur")
        lbl_create.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        create_lay.addWidget(lbl_create)

        form = QHBoxLayout()
        form.setSpacing(8)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Kullanıcı adı")
        self.inp_username.setStyleSheet(input_ss())

        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Parola")
        self.inp_password.setEchoMode(QLineEdit.Password)
        self.inp_password.setStyleSheet(input_ss())

        self.cb_role = QComboBox()
        self.cb_role.addItems(["personnel", "admin"])
        self.cb_role.setStyleSheet(
            f"QComboBox{{background:{C['input_bg']};color:{C['text']};border:1px solid {C['border']};"
            "border-radius:8px;padding:7px 10px;font-size:13px;}}"
        )

        self.btn_create_user = QPushButton("Kullanıcı Ekle")
        self.btn_create_user.setStyleSheet(btn_success_ss())
        self.btn_create_user.clicked.connect(self._create_user)

        form.addWidget(self.inp_username, 2)
        form.addWidget(self.inp_password, 2)
        form.addWidget(self.cb_role, 1)
        form.addWidget(self.btn_create_user, 1)
        create_lay.addLayout(form)

        user_table_label = QLabel("Kullanıcılar")
        user_table_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        lay.addWidget(user_table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Kullanıcı", "Rol", "Aktif", "Oluşturulma", "Son Giriş"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.table, stretch=1)

        self.refresh()

    def _bildirim(self, mesaj: str, ok: bool = True):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("MarketCare")
        dlg.setText(mesaj)
        dlg.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        dlg.exec_()

    def refresh(self):
        self.table.setRowCount(0)
        for u in list_users():
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(u.get("id", ""))))
            self.table.setItem(r, 1, QTableWidgetItem(str(u.get("username", ""))))
            self.table.setItem(r, 2, QTableWidgetItem(str(u.get("role", ""))))
            self.table.setItem(r, 3, QTableWidgetItem("Evet" if int(u.get("is_active", 0)) == 1 else "Hayır"))
            self.table.setItem(r, 4, QTableWidgetItem(format_db_datetime_local(str(u.get("created_at") or ""))))

            last_login = str(u.get("last_login_at") or "").strip()
            self.table.setItem(r, 5, QTableWidgetItem(format_db_datetime_local(last_login) if last_login else "Henüz yok"))

    def _create_user(self):
        username = self.inp_username.text().strip()
        password = self.inp_password.text().strip()
        role = self.cb_role.currentText()

        if not username or not password:
            self._bildirim("Kullanıcı adı ve şifre girilmelidir.", ok=False)
            return

        try:
            create_user(username=username, password=password, role=role)
            self._bildirim("Kullanıcı başarıyla oluşturuldu.")
            self.inp_username.setText("")
            self.inp_password.setText("")
            self.refresh()
        except Exception as e:
            self._bildirim(str(e), ok=False)

    def _reset_db(self):
        confirm = QMessageBox.question(
            self,
            "DB Sıfırla",
            "Tüm veriler silinecek ve veritabanı yeniden oluşturulacak. Devam edilsin mi?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            reset_database()
            self._bildirim("Veritabanı başarıyla sıfırlandı. Uygulamayı yeniden başlatın.")
            self.refresh()
        except Exception as e:
            self._bildirim(str(e), ok=False)
