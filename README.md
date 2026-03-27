# MarketCare

Modern, masaüstü tabanlı market ve satış yönetim uygulaması.  
PyQt5 ile geliştirilmiştir; ürün, stok, satış, fatura/slip ve personel yönetimi akışları sunar.

---

## İçerik

- [Özellikler](#özellikler)
- [Ekranlar](#ekranlar)
- [Teknolojiler](#teknolojiler)
- [Kurulum](#kurulum)
- [Çalıştırma](#çalıştırma)
- [Varsayılan Kullanıcılar](#varsayılan-kullanıcılar)
- [Exe Oluşturma](#exe-oluşturma)
- [Proje Yapısı](#proje-yapısı)
- [Veri ve Dosyalar](#veri-ve-dosyalar)
- [DB Sıfırlama](#db-sıfırlama)
- [Katkı](#katkı)
- [Lisans](#lisans)

---

## Özellikler

- Ürün ekleme, güncelleme ve arama
- Otomatik barkod oluşturma
- Barkodu panoya kopyalama
- Ürün bazlı KDV oranı tahmini
- Satış ve sepet yönetimi
- Slip ve fatura PDF oluşturma
- Stok hareketleri ve kritik stok takibi
- Personel yönetimi
- Dashboard ve özet ekranları

---

## Ekranlar

- Dashboard
- Satış
- Faturalar
- Ürünler
- Stok Hareketleri
- Personel

---

## Teknolojiler

| Teknoloji     | Kullanım Amacı              |
|---------------|-----------------------------|
| Python        | Ana programlama dili        |
| PyQt5         | Masaüstü arayüz             |
| SQLite        | Yerel veritabanı            |
| ReportLab     | PDF oluşturma               |
| PyInstaller   | Exe paketleme               |

---

## Kurulum

### Gereksinimler

- Windows
- Python 3.10 veya üstü
- `pip`

### Adımlar

```powershell
cd C:\...\market
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Çalıştırma

```powershell
cd C:\...\market
python market_gui.py
```

> İlk açılışta veritabanı otomatik olarak oluşturulur.

---

## Varsayılan Kullanıcılar

Uygulama ilk kurulumda iki varsayılan kullanıcı oluşturur:

| Rol       | Kullanıcı Adı | Şifre        |
|-----------|---------------|--------------|
| Admin     | `admin`       | `admin123`   |
| Personel  | `personel`    | `personel123`|

---

## Exe Oluşturma

Projede hazır PyInstaller spec dosyası bulunur.

### Build Alma

```powershell
cd C:\...\market
pyinstaller --noconfirm MarketCare.spec
```

### Çıktı Klasörü

```
dist\MarketCare\
```

### Dağıtım

Başka birine gönderirken sadece `.exe` dosyasını değil, **aşağıdaki klasörün tamamını** paylaşın:

```
dist\MarketCare\
```

İçeriği:

- `MarketCare.exe`
- `_internal` klasörü
- Build ile gelen diğer dosyalar

---

## Proje Yapısı

```
market/
├── assets/
├── data/
├── db/
├── documents/
├── repositories/
├── services/
├── ui/
├── utilities/
├── market_gui.py
├── MarketCare.spec
└── requirements.txt
```

---

## Veri ve Dosyalar

Uygulama yerel olarak şu alanları kullanır:

| Yol                     | Açıklama                        |
|-------------------------|---------------------------------|
| `data/market.db`        | Yerel SQLite veritabanı         |
| `documents/`            | Üretilen slip ve fatura PDF'leri|
| `assets/barcodes/`      | Üretilen barkod görselleri      |
| `assets/product_images/`| Ürün görselleri                 |

---

## DB Sıfırlama

Uygulamadaki **DB Sıfırla** işlemi şu verileri temizler:

- SQLite veritabanı
- Üretilmiş PDF dosyaları
- Barkod görselleri
- Otomatik ürün görselleri

> Bu işlem temiz bir başlangıç sağlar.

---

## Katkı

Katkı vermek için:

1. Repoyu fork edin
2. Yeni bir branch oluşturun
3. Değişikliklerinizi yapın
4. Commit alın
5. Pull request açın

---

## Lisans

Bu proje açık kaynaklıdır. Lisans bilgisi için `LICENSE` dosyasına bakın.