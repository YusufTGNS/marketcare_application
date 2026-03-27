"""
============================================================
  AKILLI ECZANE STOK VE SATIN ALMA KARAR SİSTEMİ
  Nesne Tabanlı Programlama - İş Mantığı
============================================================
OOP Kavramları:
  - Encapsulation  : Product (private + getter/setter)
  - Inheritance    : YerelTedarikci / UluslararasiTedarikci → Supplier
  - Polymorphism   : fiyat_getir() her tedarikçide farklı davranır
  - Composition    : RecommendationEngine → PharmacyStock + Supplier
"""

from datetime import date, datetime


# ──────────────────────────────────────────────────────────────
# 1. SINIF: Product  (Encapsulation)
# ──────────────────────────────────────────────────────────────
class Product:
    """Eczanedeki bir ürünü/ilacı temsil eder."""

    def __init__(self, urun_id: int, ad: str, fiyat: float, son_kullanma_tarihi: date):
        self.__id                 = urun_id
        self.__ad                 = ad
        self.__fiyat              = fiyat
        self.__son_kullanma_tarihi = son_kullanma_tarihi

    # --- Getter'lar ---
    def get_id(self)                  -> int:   return self.__id
    def get_ad(self)                  -> str:   return self.__ad
    def get_fiyat(self)               -> float: return self.__fiyat
    def get_son_kullanma_tarihi(self) -> date:  return self.__son_kullanma_tarihi

    # --- Setter ---
    def set_fiyat(self, yeni: float):
        """Fiyatı günceller; negatif değer reddeder."""
        if yeni < 0:
            raise ValueError("Fiyat negatif olamaz!")
        self.__fiyat = yeni

    def son_kullanma_gecti_mi(self) -> bool:
        """SKT bugünden önce ise True döner."""
        return self.__son_kullanma_tarihi < date.today()

    def __str__(self):
        return (f"[{self.__id}] {self.__ad} | "
                f"₺{self.__fiyat:.2f} | SKT: {self.__son_kullanma_tarihi}")


# ──────────────────────────────────────────────────────────────
# 2. SINIF: Supplier  (Temel sınıf — Inheritance + Polymorphism)
# ──────────────────────────────────────────────────────────────
class Supplier:
    """Tüm tedarikçiler için ortak temel sınıf."""

    def __init__(self, ad: str, fiyat_listesi: dict):
        self.ad              = ad
        self._fiyat_listesi  = fiyat_listesi   # protected

    def fiyat_getir(self, urun_adi: str):
        """Temel fiyatı döner; alt sınıflar override eder."""
        return self._fiyat_listesi.get(urun_adi, None)

    def tedarikci_bilgisi(self) -> str:
        return f"Tedarikçi: {self.ad}"

    def __str__(self):
        return self.tedarikci_bilgisi()


# ──────────────────────────────────────────────────────────────
# 3. SINIF: YerelTedarikci  (Inheritance + Polymorphism)
# ──────────────────────────────────────────────────────────────
class YerelTedarikci(Supplier):
    """Yerel tedarikçi — fiyata %5 yerel vergi ekler."""

    def __init__(self, ad: str, fiyat_listesi: dict, sehir: str):
        super().__init__(ad, fiyat_listesi)
        self.sehir          = sehir
        self.__vergi_orani  = 0.05

    def fiyat_getir(self, urun_adi: str):
        """[POLYMORPHISM] Yerel vergiyle fiyat döner."""
        f = super().fiyat_getir(urun_adi)
        return round(f * (1 + self.__vergi_orani), 2) if f else None

    def tedarikci_bilgisi(self) -> str:
        return f"[YEREL] {self.ad} — {self.sehir} | Vergi: %{self.__vergi_orani*100:.0f}"


# ──────────────────────────────────────────────────────────────
# 4. SINIF: UluslararasiTedarikci  (Inheritance + Polymorphism)
# ──────────────────────────────────────────────────────────────
class UluslararasiTedarikci(Supplier):
    """Uluslararası tedarikçi — döviz kuru + %18 gümrük uygular."""

    def __init__(self, ad: str, fiyat_listesi: dict, ulke: str, doviz_kuru: float):
        super().__init__(ad, fiyat_listesi)
        self.ulke            = ulke
        self.__doviz_kuru    = doviz_kuru
        self.__gumruk_orani  = 0.18

    def fiyat_getir(self, urun_adi: str):
        """[POLYMORPHISM] Döviz + gümrük dahil fiyat döner."""
        f = super().fiyat_getir(urun_adi)
        return round(f * self.__doviz_kuru * (1 + self.__gumruk_orani), 2) if f else None

    def tedarikci_bilgisi(self) -> str:
        return (f"[ULUSLARARASI] {self.ad} — {self.ulke} | "
                f"Kur: {self.__doviz_kuru} | Gümrük: %{self.__gumruk_orani*100:.0f}")


# ──────────────────────────────────────────────────────────────
# 5. SINIF: PharmacyStock  (Composition — Product barındırır)
# ──────────────────────────────────────────────────────────────
class PharmacyStock:
    """Eczane stok yönetimi."""

    def __init__(self, kritik_seviye: int = 10):
        self.__stoklar       = {}   # {id: {"urun": Product, "miktar": int, "satis_gecmisi": []}}
        self.__kritik_seviye = kritik_seviye

    def urun_ekle(self, urun: Product, baslangic_miktar: int):
        """Sisteme yeni ürün ekler."""
        if urun.get_id() in self.__stoklar:
            return False, f"{urun.get_ad()} zaten kayıtlı."
        self.__stoklar[urun.get_id()] = {
            "urun":          urun,
            "miktar":        baslangic_miktar,
            "satis_gecmisi": []
        }
        return True, f"{urun.get_ad()} eklendi."

    def stok_arttir(self, urun_id: int, miktar: int):
        """Stok miktarını artırır."""
        if urun_id not in self.__stoklar:
            return False, "Ürün bulunamadı."
        self.__stoklar[urun_id]["miktar"] += miktar
        ad = self.__stoklar[urun_id]["urun"].get_ad()
        yeni = self.__stoklar[urun_id]["miktar"]
        return True, f"{ad} stoğu artırıldı → {yeni} adet"

    def stok_azalt(self, urun_id: int, miktar: int):
        """Satış yapıldığında stoğu azaltır ve geçmişe ekler."""
        if urun_id not in self.__stoklar:
            return False, "Ürün bulunamadı."
        kayit = self.__stoklar[urun_id]
        if kayit["miktar"] < miktar:
            return False, f"Yetersiz stok! Mevcut: {kayit['miktar']}"
        kayit["miktar"] -= miktar
        kayit["satis_gecmisi"].append({"tarih": date.today(), "miktar": miktar})
        return True, f"{kayit['urun'].get_ad()} → kalan: {kayit['miktar']} adet"

    def kritik_stok_kontrol(self) -> list:
        """Kritik seviyenin altındaki ürünleri listeler."""
        return [
            {"urun": k["urun"], "miktar": k["miktar"]}
            for k in self.__stoklar.values()
            if k["miktar"] < self.__kritik_seviye
        ]

    def get_stok_kaydi(self, urun_id: int):
        return self.__stoklar.get(urun_id, None)

    def get_tum_stoklar(self) -> dict:
        return self.__stoklar

    def get_kritik_seviye(self) -> int:
        return self.__kritik_seviye


# ──────────────────────────────────────────────────────────────
# 6. SINIF: Order  (Composition — Product + Supplier kullanır)
# ──────────────────────────────────────────────────────────────
class Order:
    """Bir satın alma siparişini temsil eder."""

    def __init__(self, urun: Product, miktar: int, tedarikci: Supplier):
        self.__urun       = urun
        self.__miktar     = miktar
        self.__tedarikci  = tedarikci
        self.__tarih      = datetime.now()
        birim = tedarikci.fiyat_getir(urun.get_ad()) or 0
        self.__toplam     = birim * miktar

    def siparis_olustur(self) -> str:
        birim = self.__tedarikci.fiyat_getir(self.__urun.get_ad()) or 0
        return (
            f"Tarih: {self.__tarih.strftime('%d.%m.%Y %H:%M')} | "
            f"Ürün: {self.__urun.get_ad()} | "
            f"Miktar: {self.__miktar} | "
            f"Tedarikçi: {self.__tedarikci.ad} | "
            f"Birim: ₺{birim:.2f} | Toplam: ₺{self.__toplam:.2f}"
        )

    def get_maliyet(self) -> float:
        return self.__toplam

    def get_urun(self)      -> Product:  return self.__urun
    def get_miktar(self)    -> int:      return self.__miktar
    def get_tedarikci(self) -> Supplier: return self.__tedarikci


# ──────────────────────────────────────────────────────────────
# 7. SINIF: RecommendationEngine ⭐  (Composition)
# ──────────────────────────────────────────────────────────────
class RecommendationEngine:
    """
    Kritik stoktaki ürünler için akıllı sipariş önerisi üretir.
    Talep tahmini + en ucuz tedarikçi seçimi yapar.
    """

    def __init__(self, stok: PharmacyStock, tedarikciler: list):
        self.__stok         = stok
        self.__tedarikciler = tedarikciler

    def talep_tahmini_yap(self, urun_id: int, gun: int = 7) -> float:
        """Son N günün ortalamasına göre günlük talep tahmini."""
        kayit = self.__stok.get_stok_kaydi(urun_id)
        if not kayit or not kayit["satis_gecmisi"]:
            return 2.0
        bugun    = date.today()
        satirlar = [s["miktar"] for s in kayit["satis_gecmisi"]
                    if (bugun - s["tarih"]).days <= gun]
        return round(sum(satirlar) / gun, 2) if satirlar else 2.0

    def en_ucuz_tedarikci(self, urun_adi: str):
        """En düşük fiyatlı tedarikçiyi döndürür (Polymorphism burada çalışır)."""
        en_iyi, en_fiyat = None, float("inf")
        for t in self.__tedarikciler:
            f = t.fiyat_getir(urun_adi)
            if f is not None and f < en_fiyat:
                en_fiyat, en_iyi = f, t
        return en_iyi

    def siparis_oner(self) -> list:
        """Kritik ürünler için Order listesi oluşturur."""
        oneriler = []
        for bilgi in self.__stok.kritik_stok_kontrol():
            urun    = bilgi["urun"]
            mevcut  = bilgi["miktar"]
            gunluk  = self.talep_tahmini_yap(urun.get_id())
            miktar  = max(int(gunluk * 30) - mevcut, 20)
            t       = self.en_ucuz_tedarikci(urun.get_ad())
            if t:
                oneriler.append(Order(urun, miktar, t))
        return oneriler

    def get_tedarikciler(self) -> list:
        return self.__tedarikciler
