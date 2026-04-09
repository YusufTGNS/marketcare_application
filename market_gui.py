import sys

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from services.auth_service import clear_session, try_auto_login_from_session
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.style import C


def main() -> None:
    """MarketCare masaustu uygulamasini baslatir."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palet = QPalette()
    palet.setColor(QPalette.Window, QColor(C["bg"]))
    palet.setColor(QPalette.WindowText, QColor(C["text"]))
    palet.setColor(QPalette.Base, QColor(C["card"]))
    palet.setColor(QPalette.AlternateBase, QColor(C["row_alt"]))
    palet.setColor(QPalette.Text, QColor(C["text"]))
    palet.setColor(QPalette.Button, QColor(C["card"]))
    palet.setColor(QPalette.ButtonText, QColor(C["text"]))
    palet.setColor(QPalette.Highlight, QColor(C["accent"]))
    palet.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palet)

    ana_pencere = None
    giris_penceresi = None

    def cikis_yap() -> None:
        nonlocal ana_pencere, giris_penceresi
        clear_session()
        if ana_pencere is not None:
            ana_pencere.close()
            ana_pencere = None
        giris_penceresi = LoginWindow(on_success=giris_basarili)
        giris_penceresi.show()

    def giris_basarili(kullanici) -> None:
        nonlocal ana_pencere, giris_penceresi
        if giris_penceresi is not None:
            giris_penceresi.close()
            giris_penceresi = None
        ana_pencere = MainWindow(kullanici, on_logout=cikis_yap)
        ana_pencere.show()

    oturum = try_auto_login_from_session()
    if oturum.ok and oturum.user:
        ana_pencere = MainWindow(oturum.user, on_logout=cikis_yap)
        ana_pencere.show()
    else:
        giris_penceresi = LoginWindow(on_success=giris_basarili)
        giris_penceresi.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
