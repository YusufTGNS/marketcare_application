from typing import Any, Dict, Optional

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from repositories.users_repo import list_users
from services.auth_service import create_user, reset_database
from ui.style import C, TABLE_SS, btn_danger_ss, btn_success_ss, card_ss, input_ss, shadow
from utilities.datetime_utils import format_db_datetime_local


class AdminPersonnelPage(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet(f"background:{C['bg']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        title = QLabel("Personel Yonetimi")
        title.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:900;")
        layout.addWidget(title)

        actions_card = QFrame()
        actions_card.setStyleSheet(card_ss())
        shadow(actions_card)
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(18, 16, 18, 16)
        actions_layout.setSpacing(12)
        layout.addWidget(actions_card)

        reset_label = QLabel("Veritabani Islemleri")
        reset_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        actions_layout.addWidget(reset_label)

        btn_reset = QPushButton("Veritabanini Sifirla")
        btn_reset.setStyleSheet(btn_danger_ss())
        btn_reset.clicked.connect(self._reset_db)
        actions_layout.addWidget(btn_reset)

        create_card = QFrame()
        create_card.setStyleSheet(card_ss())
        shadow(create_card)
        create_layout = QVBoxLayout(create_card)
        create_layout.setContentsMargins(18, 16, 18, 16)
        create_layout.setSpacing(12)
        layout.addWidget(create_card)

        create_label = QLabel("Yeni Kullanici")
        create_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        create_layout.addWidget(create_label)

        form = QHBoxLayout()
        form.setSpacing(8)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Kullanici adi")
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

        btn_create = QPushButton("Kullanici Ekle")
        btn_create.setStyleSheet(btn_success_ss())
        btn_create.clicked.connect(self._create_user)

        form.addWidget(self.inp_username, 2)
        form.addWidget(self.inp_password, 2)
        form.addWidget(self.cb_role, 1)
        form.addWidget(btn_create, 1)
        create_layout.addLayout(form)

        table_label = QLabel("Kullanicilar")
        table_label.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:900;")
        layout.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Kullanici", "Rol", "Aktif", "Olusturulma", "Son Giris"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_SS)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, stretch=1)

        self.refresh()

    def _bildirim(self, message: str, ok: bool = True) -> None:
        pencere = QMessageBox(self)
        pencere.setWindowTitle("MarketCare")
        pencere.setText(message)
        pencere.setIcon(QMessageBox.Information if ok else QMessageBox.Warning)
        pencere.setStyleSheet(f"QMessageBox{{background:{C['card']};}}")
        pencere.exec_()

    def refresh(self) -> None:
        self.table.setRowCount(0)
        for user in list_users():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(user.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(user.get("username", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(user.get("role", ""))))
            self.table.setItem(row, 3, QTableWidgetItem("Evet" if int(user.get("is_active", 0)) == 1 else "Hayir"))
            self.table.setItem(row, 4, QTableWidgetItem(format_db_datetime_local(str(user.get("created_at") or ""))))

            last_login = str(user.get("last_login_at") or "").strip()
            son_giris = format_db_datetime_local(last_login) if last_login else "Henuz yok"
            self.table.setItem(row, 5, QTableWidgetItem(son_giris))

    def _create_user(self) -> None:
        username = self.inp_username.text().strip()
        password = self.inp_password.text().strip()
        role = self.cb_role.currentText()

        if not username or not password:
            self._bildirim("Kullanici adi ve sifre zorunludur.", ok=False)
            return

        try:
            create_user(username=username, password=password, role=role)
        except Exception as exc:
            self._bildirim(str(exc), ok=False)
            return

        self._bildirim("Kullanici basariyla olusturuldu.")
        self.inp_username.clear()
        self.inp_password.clear()
        self.refresh()

    def _reset_db(self) -> None:
        onay = QMessageBox.question(
            self,
            "Veritabanini Sifirla",
            "Tum veriler silinecek ve veritabani yeniden kurulacak. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if onay != QMessageBox.Yes:
            return

        try:
            reset_database()
        except Exception as exc:
            self._bildirim(str(exc), ok=False)
            return

        self._bildirim("Veritabani sifirlandi. Uygulamayi yeniden baslatmaniz onerilir.")
        self.refresh()
