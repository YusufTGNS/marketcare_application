"""
============================================================
  AKILLI ECZANE STOK YÖNETİM SİSTEMİ — PyQt5 Arayüzü
============================================================
Kurulum  : pip install PyQt5
Çalıştır : py -3.13 eczane_gui.py
Not      : eczane_sistemi.py ile aynı klasörde olmalıdır.
"""

import sys
from datetime import date, datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QGridLayout,
    QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
    QAbstractItemView, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

from market_sistemi import (
    Product, PharmacyStock,
    YerelTedarikci, UluslararasiTedarikci,
    Order, RecommendationEngine
)

from ui.style import C, card_ss, btn_primary_ss, btn_success_ss, btn_danger_ss, input_ss, TABLE_SS, shadow

# ══════════════════════════════════════════════════════════
#  BİLEŞEN: KPI Kartı
# ══════════════════════════════════════════════════════════
class KpiCard(QFrame):
    def __init__(self, baslik, deger, alt, renk, parent=None):
        super().__init__(parent)
        self.setFixedHeight(114)
        self.setStyleSheet(f"""
            QFrame{{background:{C['card']};border:1px solid {C['border']};
                border-radius:13px;border-left:4px solid {renk};}}
        """)
        shadow(self)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(3)

        t = f"color:{C['text_sub']};font-size:10px;font-weight:700;letter-spacing:1px;background:transparent;border:none;"
        v = f"color:{renk};font-size:29px;font-weight:800;background:transparent;border:none;"
        a = f"color:{C['text_dim']};font-size:11px;background:transparent;border:none;"

        lbl_t = QLabel(baslik.upper()); lbl_t.setStyleSheet(t)
        lbl_v = QLabel(str(deger));     lbl_v.setStyleSheet(v)
        lbl_a = QLabel(alt);            lbl_a.setStyleSheet(a)

        lay.addWidget(lbl_t)
        lay.addWidget(lbl_v)
        lay.addWidget(lbl_a)


# ══════════════════════════════════════════════════════════
#  BİLEŞEN: Sidebar Butonu
# ══════════════════════════════════════════════════════════
class SideBtn(QPushButton):
    def __init__(self, ikon, metin, parent=None):
        super().__init__(f"  {ikon}  {metin}", parent)
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, aktif):
        if aktif:
            self.setStyleSheet(f"""
                QPushButton{{background:rgba(0,180,216,0.08);color:{C['accent']};
                    border:none;border-left:3px solid {C['accent']};
                    border-radius:0;text-align:left;padding-left:16px;
                    font-size:13px;font-weight:700;}}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton{{background:transparent;color:{C['text_sub']};
                    border:none;border-left:3px solid transparent;
                    border-radius:0;text-align:left;padding-left:16px;font-size:13px;}}
                QPushButton:hover{{background:{C['card']};color:{C['text']};
                    border-left:3px solid {C['text_dim']};}}
            """)

    def setChecked(self, v):
        super().setChecked(v)
        self._refresh(v)


# ══════════════════════════════════════════════════════════
#  EKRAN 1: Dashboard
# ══════════════════════════════════════════════════════════
class DashboardPage(QWidget):
    def __init__(self, stok: PharmacyStock, parent=None):
        super().__init__(parent)
        self.stok = stok
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(18)

        lbl = QLabel("📊  Dashboard")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        lay.addWidget(lbl)

        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(14)
        lay.addLayout(self.kpi_row)

        sub = QLabel("Stok Durumu")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)

        self.tablo = self._tablo(["Ürün", "Stok", "Durum", "Son Kullanma Tarihi"])
        lay.addWidget(self.tablo)

        self.refresh()

    def _tablo(self, headers):
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        t.setAlternatingRowColors(True)
        t.setStyleSheet(TABLE_SS)
        return t

    def refresh(self):
        stoklar = self.stok.get_tum_stoklar()
        toplam  = len(stoklar)
        kritik  = len(self.stok.kritik_stok_kontrol())
        deger   = sum(k["urun"].get_fiyat() * k["miktar"] for k in stoklar.values())

        # KPI kartları sıfırla
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.kpi_row.addWidget(KpiCard("Toplam Ürün",  toplam,           "kayıtlı ilaç",          C['accent']))
        self.kpi_row.addWidget(KpiCard("Normal Stok",  toplam - kritik,  "yeterli seviyede",       C['success']))
        self.kpi_row.addWidget(KpiCard("Kritik Stok",  kritik,           "acil sipariş gerekli",   C['danger']))
        self.kpi_row.addWidget(KpiCard("Stok Değeri",  f"₺{deger:,.0f}", "toplam envanter",        C['warning']))

        # Tablo
        self.tablo.setRowCount(0)
        for k in stoklar.values():
            u, m = k["urun"], k["miktar"]
            r = self.tablo.rowCount()
            self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(u.get_ad()))
            self.tablo.setItem(r, 1, QTableWidgetItem(str(m)))

            durum = QTableWidgetItem("⚠  KRİTİK" if m < self.stok.get_kritik_seviye() else "✓  Normal")
            durum.setForeground(QColor(C['danger'] if m < self.stok.get_kritik_seviye() else C['success']))
            self.tablo.setItem(r, 2, durum)

            skt = QTableWidgetItem(
                f"⚠ {u.get_son_kullanma_tarihi()} (GEÇMİŞ!)" if u.son_kullanma_gecti_mi()
                else str(u.get_son_kullanma_tarihi())
            )
            if u.son_kullanma_gecti_mi():
                skt.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 3, skt)
            self.tablo.setRowHeight(r, 42)


# ══════════════════════════════════════════════════════════
#  EKRAN 2: Ürün Yönetimi
# ══════════════════════════════════════════════════════════
class UrunPage(QWidget):
    def __init__(self, stok: PharmacyStock, dashboard: DashboardPage, parent=None):
        super().__init__(parent)
        self.stok      = stok
        self.dashboard = dashboard
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _lbl(self, txt):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{C['text_sub']};font-size:11px;font-weight:700;")
        return l

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        lbl = QLabel("💊  Ürün Yönetimi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        lay.addWidget(lbl)

        # ── Yeni ürün formu ──
        kart = QFrame(); kart.setStyleSheet(card_ss()); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22,18,22,18); klay.setSpacing(12)

        klay.addWidget(self._section_lbl("Yeni Ürün Ekle", C['accent']))

        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_id     = QSpinBox();        self.inp_id.setRange(1, 9999)
        self.inp_ad     = QLineEdit();       self.inp_ad.setPlaceholderText("örn. Aspirin 500mg")
        self.inp_fiyat  = QDoubleSpinBox();  self.inp_fiyat.setRange(0, 99999); self.inp_fiyat.setDecimals(2)
        self.inp_skt    = QDateEdit();       self.inp_skt.setCalendarPopup(True); self.inp_skt.setDate(QDate.currentDate().addYears(2))
        self.inp_miktar = QSpinBox();        self.inp_miktar.setRange(0, 9999)

        for w in [self.inp_id, self.inp_ad, self.inp_fiyat, self.inp_skt, self.inp_miktar]:
            w.setStyleSheet(input_ss())

        fields = [("Ürün ID", self.inp_id), ("Ürün Adı", self.inp_ad),
                  ("Fiyat (₺)", self.inp_fiyat), ("Son Kullanma", self.inp_skt),
                  ("Başlangıç Stok", self.inp_miktar)]
        for col, (lbl_txt, wid) in enumerate(fields):
            grid.addWidget(self._lbl(lbl_txt), 0, col)
            grid.addWidget(wid, 1, col)

        klay.addLayout(grid)

        btn_ekle = QPushButton("＋  Ürün Ekle")
        btn_ekle.setStyleSheet(btn_primary_ss())
        btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.clicked.connect(self._ekle)
        btn_ekle.setFixedWidth(140)
        klay.addWidget(btn_ekle)
        lay.addWidget(kart)

        # ── Stok güncelleme ──
        kart2 = QFrame(); kart2.setStyleSheet(card_ss()); shadow(kart2)
        k2lay = QVBoxLayout(kart2); k2lay.setContentsMargins(22,16,22,16); k2lay.setSpacing(10)
        k2lay.addWidget(self._section_lbl("Stok Güncelle", C['warning']))

        row = QHBoxLayout(); row.setSpacing(10)
        self.g_id     = QSpinBox(); self.g_id.setRange(1, 9999); self.g_id.setFixedWidth(110)
        self.g_miktar = QSpinBox(); self.g_miktar.setRange(1, 9999); self.g_miktar.setFixedWidth(110)
        for w in [self.g_id, self.g_miktar]:
            w.setStyleSheet(input_ss())

        row.addWidget(self._lbl("Ürün ID"))
        row.addWidget(self.g_id)
        row.addWidget(self._lbl("Miktar"))
        row.addWidget(self.g_miktar)

        b_art = QPushButton("▲  Stok Artır")
        b_art.setStyleSheet(btn_success_ss())
        b_art.setCursor(Qt.PointingHandCursor)
        b_art.clicked.connect(self._arttir)

        b_sat = QPushButton("▼  Satış Yap")
        b_sat.setStyleSheet(btn_danger_ss())
        b_sat.setCursor(Qt.PointingHandCursor)
        b_sat.clicked.connect(self._azalt)

        row.addWidget(b_art)
        row.addWidget(b_sat)
        row.addStretch()
        k2lay.addLayout(row)
        lay.addWidget(kart2)

        # ── Tablo ──
        sub = QLabel("Tüm Ürünler")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ürün Adı", "Satış Fiyatı", "Stok", "Son Kullanma"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)

        self._tablo_yenile()

    def _section_lbl(self, txt, renk):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{renk};font-size:13px;font-weight:700;background:transparent;")
        return l

    def _tablo_yenile(self):
        self.tablo.setRowCount(0)
        for k in self.stok.get_tum_stoklar().values():
            u, m = k["urun"], k["miktar"]
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(u.get_id())))
            self.tablo.setItem(r, 1, QTableWidgetItem(u.get_ad()))
            self.tablo.setItem(r, 2, QTableWidgetItem(f"₺{u.get_fiyat():.2f}"))
            m_item = QTableWidgetItem(str(m))
            m_item.setForeground(QColor(C['danger'] if m < self.stok.get_kritik_seviye() else C['success']))
            self.tablo.setItem(r, 3, m_item)
            skt = QTableWidgetItem(
                f"⚠ {u.get_son_kullanma_tarihi()} (GEÇMİŞ!)" if u.son_kullanma_gecti_mi()
                else str(u.get_son_kullanma_tarihi())
            )
            if u.son_kullanma_gecti_mi():
                skt.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 4, skt)
            self.tablo.setRowHeight(r, 42)

    def _bildirim(self, mesaj, ok=True):
        renk = C['success'] if ok else C['danger']
        dlg = QMessageBox(self)
        dlg.setText(mesaj)
        dlg.setWindowTitle("Sistem")
        dlg.setStyleSheet(f"""
            QMessageBox{{background:{C['card']};}}
            QLabel{{color:{renk};font-size:13px;}}
            QPushButton{{{btn_primary_ss()[len('QPushButton'):].split('}')[0]}padding:6px 18px;}}
        """)
        dlg.exec_()

    def _ekle(self):
        try:
            ad = self.inp_ad.text().strip()
            if not ad: raise ValueError("Ürün adı boş olamaz.")
            q = self.inp_skt.date()
            skt = date(q.year(), q.month(), q.day())
            u = Product(self.inp_id.value(), ad, self.inp_fiyat.value(), skt)
            ok, msg = self.stok.urun_ekle(u, self.inp_miktar.value())
            self._bildirim(msg, ok)
            if ok:
                self._tablo_yenile()
                self.dashboard.refresh()
        except Exception as e:
            self._bildirim(str(e), False)

    def _arttir(self):
        ok, msg = self.stok.stok_arttir(self.g_id.value(), self.g_miktar.value())
        self._bildirim(msg, ok)
        if ok: self._tablo_yenile(); self.dashboard.refresh()

    def _azalt(self):
        ok, msg = self.stok.stok_azalt(self.g_id.value(), self.g_miktar.value())
        self._bildirim(msg, ok)
        if ok: self._tablo_yenile(); self.dashboard.refresh()


# ══════════════════════════════════════════════════════════
#  EKRAN 3: Kritik Stok Uyarıları
# ══════════════════════════════════════════════════════════
class KritikPage(QWidget):
    def __init__(self, stok: PharmacyStock, parent=None):
        super().__init__(parent)
        self.stok = stok
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        ust = QHBoxLayout()
        lbl = QLabel("⚠️  Kritik Stok Uyarıları")
        lbl.setStyleSheet(f"color:{C['danger']};font-size:21px;font-weight:800;")
        ust.addWidget(lbl); ust.addStretch()
        btn = QPushButton("↻  Yenile")
        btn.setStyleSheet(btn_primary_ss())
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.refresh)
        ust.addWidget(btn)
        lay.addLayout(ust)

        self.banner = QLabel()
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setFixedHeight(44)
        lay.addWidget(self.banner)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Ürün Adı", "Mevcut Stok", "Kritik Eşik", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)

        self.refresh()

    def refresh(self):
        kritikler = self.stok.kritik_stok_kontrol()
        if kritikler:
            self.banner.setText(f"⚠  {len(kritikler)} ürün kritik seviyenin altında!")
            self.banner.setStyleSheet(f"""
                background:rgba(239,71,111,0.12);border:1px solid rgba(239,71,111,0.4);
                border-radius:9px;color:{C['danger']};font-size:13px;font-weight:700;
            """)
        else:
            self.banner.setText("✓  Tüm ürünler yeterli stok seviyesinde.")
            self.banner.setStyleSheet(f"""
                background:rgba(6,214,160,0.10);border:1px solid rgba(6,214,160,0.35);
                border-radius:9px;color:{C['success']};font-size:13px;font-weight:700;
            """)

        self.tablo.setRowCount(0)
        for bilgi in kritikler:
            u, m = bilgi["urun"], bilgi["miktar"]
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(u.get_ad()))
            m_item = QTableWidgetItem(str(m))
            m_item.setForeground(QColor(C['danger']))
            f = QFont(); f.setBold(True)
            m_item.setFont(f)
            self.tablo.setItem(r, 1, m_item)
            self.tablo.setItem(r, 2, QTableWidgetItem(str(self.stok.get_kritik_seviye())))
            durum = "⚠  KRİTİK + SKT GEÇMİŞ" if u.son_kullanma_gecti_mi() else "⚠  KRİTİK STOK"
            d = QTableWidgetItem(durum); d.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 3, d)
            self.tablo.setRowHeight(r, 46)


# ══════════════════════════════════════════════════════════
#  EKRAN 4: Sipariş Önerisi
# ══════════════════════════════════════════════════════════
class SiparisPage(QWidget):
    def __init__(self, stok: PharmacyStock, motor: RecommendationEngine, parent=None):
        super().__init__(parent)
        self.stok  = stok
        self.motor = motor
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        ust = QHBoxLayout()
        lbl = QLabel("🤖  Akıllı Sipariş Önerisi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        ust.addWidget(lbl); ust.addStretch()
        btn = QPushButton("▶  Analiz Başlat")
        btn.setStyleSheet(btn_primary_ss())
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._analiz)
        ust.addWidget(btn)
        lay.addLayout(ust)

        # Bilgi bandı
        info = QFrame()
        info.setStyleSheet(f"""
            background:rgba(0,119,182,0.12);border:1px solid rgba(0,180,216,0.3);
            border-radius:9px;
        """)
        info_lay = QHBoxLayout(info); info_lay.setContentsMargins(14,8,14,8)
        info_lbl = QLabel(
            "ℹ  Sistem kritik stoktaki ürünler için son 7 günün satış ortalamasını kullanarak "
            "talep tahmini yapar ve en uygun tedarikçiyi otomatik seçer."
        )
        info_lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        info_lbl.setWordWrap(True)
        info_lay.addWidget(info_lbl)
        lay.addWidget(info)

        sub = QLabel("Önerilen Siparişler")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(
            ["Ürün", "Mevcut Stok", "Günlük Talep", "Sipariş Miktarı", "Tedarikçi", "Tahmini Maliyet"]
        )
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)

        self.lbl_toplam = QLabel("Toplam Tahmini Maliyet: —")
        self.lbl_toplam.setAlignment(Qt.AlignRight)
        self.lbl_toplam.setStyleSheet(f"""
            color:{C['accent']};font-size:15px;font-weight:800;
            padding:10px 16px;background:{C['card']};
            border:1px solid {C['border']};border-radius:9px;
        """)
        lay.addWidget(self.lbl_toplam)

    def _analiz(self):
        kritikler = self.stok.kritik_stok_kontrol()
        self.tablo.setRowCount(0)

        if not kritikler:
            self.lbl_toplam.setText("✓  Kritik stokta ürün yok — sipariş gerekmiyor.")
            return

        toplam = 0.0
        for bilgi in kritikler:
            urun   = bilgi["urun"]
            mevcut = bilgi["miktar"]
            gunluk = self.motor.talep_tahmini_yap(urun.get_id())
            siparis = max(int(gunluk * 30) - mevcut, 20)
            t = self.motor.en_ucuz_tedarikci(urun.get_ad())
            if not t: continue
            fiyat   = t.fiyat_getir(urun.get_ad()) or 0
            maliyet = fiyat * siparis
            toplam += maliyet

            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(urun.get_ad()))

            m = QTableWidgetItem(str(mevcut))
            m.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 1, m)

            self.tablo.setItem(r, 2, QTableWidgetItem(f"~{gunluk} adet/gün"))

            s = QTableWidgetItem(str(siparis))
            s.setForeground(QColor(C['warning']))
            font = QFont(); font.setBold(True); s.setFont(font)
            self.tablo.setItem(r, 3, s)

            self.tablo.setItem(r, 4, QTableWidgetItem(t.ad))

            mal = QTableWidgetItem(f"₺{maliyet:,.2f}")
            mal.setForeground(QColor(C['accent']))
            self.tablo.setItem(r, 5, mal)
            self.tablo.setRowHeight(r, 46)

        self.lbl_toplam.setText(f"Toplam Tahmini Maliyet:  ₺{toplam:,.2f}")


# ══════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💊  PharmaCare — Akıllı Eczane Stok Yönetim Sistemi")
        self.setMinimumSize(1150, 700)
        self.resize(1300, 780)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};color:{C['text']};}}")

        self.stok, self.motor = self._veri_kur()
        self._build_ui()
        self._saat_timer()

    # ── Demo veri ───────────────────────────────────────
    def _veri_kur(self):
        stok = PharmacyStock(kritik_seviye=10)
        urunler = [
            Product(1, "Aspirin 500mg",      25.90, date(2026, 12, 31)),
            Product(2, "Parol 500mg",         18.50, date(2025,  6, 30)),
            Product(3, "Novalgin 500mg",      45.00, date(2027,  3, 15)),
            Product(4, "Amoksisilin 500mg",   38.75, date(2026,  9,  1)),
        ]
        baslangic = [5, 15, 3, 22]
        for u, m in zip(urunler, baslangic):
            stok.urun_ekle(u, m)

        for _ in range(5): stok.stok_azalt(1, 1)
        stok.stok_arttir(1, 5)
        for _ in range(3): stok.stok_azalt(2, 2)
        stok.stok_arttir(2, 6)

        yerel = YerelTedarikci(
            "İstanbul İlaç A.Ş.",
            {"Aspirin 500mg": 20.0, "Novalgin 500mg": 38.0,
             "Parol 500mg": 15.0,  "Amoksisilin 500mg": 32.0},
            "İstanbul"
        )
        ulusal = UluslararasiTedarikci(
            "EuroPharma GmbH",
            {"Aspirin 500mg": 1.5, "Novalgin 500mg": 2.8, "Amoksisilin 500mg": 0.9},
            "Almanya", doviz_kuru=38.5
        )
        motor = RecommendationEngine(stok, [yerel, ulusal])
        return stok, motor

    # ── UI inşa ────────────────────────────────────────
    def _build_ui(self):
        merkez = QWidget()
        merkez.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(merkez)

        ana = QHBoxLayout(merkez)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)

        # ─ Sidebar ─
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"background:{C['sidebar']};border-right:1px solid {C['border']};")

        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 18)
        sb.setSpacing(0)

        # Logo
        logo = QFrame()
        logo.setFixedHeight(76)
        logo.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {C['accent2']},stop:1 {C['accent']});
        """)
        ll = QVBoxLayout(logo); ll.setContentsMargins(16, 10, 16, 10)
        t1 = QLabel("💊  PharmaCare")
        t1.setStyleSheet("color:white;font-size:16px;font-weight:800;background:transparent;")
        t2 = QLabel("Stok Yönetim Sistemi")
        t2.setStyleSheet("color:rgba(255,255,255,0.72);font-size:10px;background:transparent;")
        ll.addWidget(t1); ll.addWidget(t2)
        sb.addWidget(logo)
        sb.addSpacing(18)

        self.nav = []
        pages = [("📊", "Dashboard"), ("💊", "Ürün Yönetimi"),
                 ("⚠️", "Kritik Stoklar"), ("🤖", "Sipariş Önerisi")]
        for ikon, metin in pages:
            btn = SideBtn(ikon, metin)
            btn.clicked.connect(lambda _, m=metin: self._goto(m))
            sb.addWidget(btn)
            self.nav.append(btn)

        sb.addStretch()

        self.lbl_saat = QLabel()
        self.lbl_saat.setAlignment(Qt.AlignCenter)
        self.lbl_saat.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;")
        sb.addWidget(self.lbl_saat)
        ana.addWidget(sidebar)

        # ─ İçerik ─
        icerik = QWidget()
        icerik.setStyleSheet(f"background:{C['bg']};")
        il = QVBoxLayout(icerik); il.setContentsMargins(0,0,0,0); il.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setFixedHeight(50)
        topbar.setStyleSheet(f"background:{C['sidebar']};border-bottom:1px solid {C['border']};")
        tl = QHBoxLayout(topbar); tl.setContentsMargins(22, 0, 22, 0)
        self.lbl_page = QLabel("Dashboard")
        self.lbl_page.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        tl.addWidget(self.lbl_page); tl.addStretch()
        user_lbl = QLabel("👤  Eczane Yöneticisi")
        user_lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        tl.addWidget(user_lbl)
        il.addWidget(topbar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C['bg']};")

        self.p_dashboard = DashboardPage(self.stok)
        self.p_urun      = UrunPage(self.stok, self.p_dashboard)
        self.p_kritik    = KritikPage(self.stok)
        self.p_siparis   = SiparisPage(self.stok, self.motor)

        for p in [self.p_dashboard, self.p_urun, self.p_kritik, self.p_siparis]:
            self.stack.addWidget(p)

        il.addWidget(self.stack)
        ana.addWidget(icerik)

        self._goto("Dashboard")

    def _goto(self, sayfa):
        idx = {"Dashboard": 0, "Ürün Yönetimi": 1, "Kritik Stoklar": 2, "Sipariş Önerisi": 3}[sayfa]
        self.stack.setCurrentIndex(idx)
        self.lbl_page.setText(sayfa)
        for i, b in enumerate(self.nav):
            b.setChecked(i == idx)
        if idx == 0: self.p_dashboard.refresh()
        if idx == 2: self.p_kritik.refresh()

    def _saat_timer(self):
        self._saat_guncelle()
        t = QTimer(self); t.timeout.connect(self._saat_guncelle); t.start(1000)

    def _saat_guncelle(self):
        self.lbl_saat.setText(datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))


# ══════════════════════════════════════════════════════════
#  GİRİŞ NOKTASI
# ══════════════════════════════════════════════════════════
def main():
    """
    Yeni MarketCare yönetim paneli giriş noktası.
    """
    # UI içinden import ederek isim çakışmalarını engelliyoruz.
    from ui.login_window import LoginWindow
    from ui.main_window import MainWindow as MarketMainWindow

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    p = QPalette()
    p.setColor(QPalette.Window,        QColor(C["bg"]))
    p.setColor(QPalette.WindowText,    QColor(C["text"]))
    p.setColor(QPalette.Base,          QColor(C["card"]))
    p.setColor(QPalette.AlternateBase, QColor(C["row_alt"]))
    p.setColor(QPalette.Text,          QColor(C["text"]))
    p.setColor(QPalette.Button,        QColor(C["card"]))
    p.setColor(QPalette.ButtonText,    QColor(C["text"]))
    p.setColor(QPalette.Highlight,     QColor(C["accent"]))
    p.setColor(QPalette.HighlightedText, QColor("#fff"))
    app.setPalette(p)

    from services.auth_service import try_auto_login_from_session, clear_session

    main_win = None
    login_win = None

    def _logout():
        nonlocal main_win, login_win
        clear_session()
        if main_win is not None:
            main_win.close()
            main_win = None
        login_win = LoginWindow(on_success=_on_success)
        login_win.show()

    def _on_success(user):
        nonlocal main_win, login_win
        if login_win is not None:
            login_win.close()
            login_win = None
        main_win = MarketMainWindow(user, on_logout=_logout)
        main_win.show()

    # Otomatik oturum bilgisi varsa doğrudan ana pencereyi aç
    session_res = try_auto_login_from_session()
    if session_res.ok and session_res.user:
        main_win = MarketMainWindow(session_res.user, on_logout=_logout)
        main_win.show()
    else:
        login_win = LoginWindow(on_success=_on_success)
        login_win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
