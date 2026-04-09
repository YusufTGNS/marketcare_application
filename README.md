# MarketCare

MarketCare, PyQt5 ile geliştirilen masaüstü market yönetim uygulamasıdır. Ürün, stok, satış, belge ve personel akışlarını tek arayüzde toplar.

## Ne Sunuyor?

- Hızlı giriş ekranı ve oturum hatırlama
- Ürün ekleme, güncelleme ve barkod üretimi
- Satış sepeti, KDV hesaplama ve stok düşümü
- Slip ve fatura PDF üretimi
- Kritik stok ve SKT takibi
- Personel oluşturma ve temel kullanıcı yönetimi
- SQLite tabanlı yerel veri saklama

## Ekranlar

- `Panel`: günlük özet, kritik ürünler ve son satışlar
- `Satış`: barkod ile ürün ekleme, sepet ve ödeme akışı
- `Belgeler`: tarih aralığına göre satış belgeleri
- `Ürün Yönetimi`: ürün kaydı, KDV önizlemesi ve görsel işlemleri
- `Stok Hareketleri`: stok giriş/çıkış ve ürün durumu güncelleme
- `Personel Yönetimi`: kullanıcı oluşturma ve veritabanı sıfırlama

## Kurulum

```powershell
cd C:\...\market
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Çalıştırma

```powershell
cd C:\...\market
python market_gui.py
```

Uygulama ilk açılışta veritabanını otomatik hazırlar.

## Varsayılan Hesaplar

| Rol | Kullanıcı Adı | Şifre |
|---|---|---|
| Admin | `admin` | `admin123` |
| Personel | `personel` | `personel123` |

## Proje Yapısı

```text
market/
|-- assets/
|-- data/
|-- db/
|-- documents/
|-- repositories/
|-- services/
|-- ui/
|-- utilities/
|-- market_gui.py
`-- requirements.txt
```

## Veri ve Çıktılar

- `data/market.db`: ana SQLite veritabanı
- `data/session.json`: beni hatırla oturumu
- `documents/`: üretilen slip ve fatura PDF dosyaları
- `assets/barcodes/`: üretilen barkod görselleri
- `assets/product_images/`: ürün görselleri ve yerel önizlemeler

## Notlar

- Satış sonrası PDF üretimi başarısız olsa bile satış kaydı korunur.
- Ürün görseli seçilmezse ağ bağımlılığı olmadan yerel bir önizleme görseli oluşturulur.
- Kritik stok kontrolü, eşik değeri ve altı için çalışır.

## Geliştirme İçin Kısa Yol

- Veritabanı şemasını: `db/schema.sql`
- İş kurallarını: `services/`
- Veri erişimini: `repositories/`
- Arayüz ekranlarını: `ui/`
- Yardımcı fonksiyonları: `utilities/`

## Sıfırlama

Personel yönetimi ekranındaki sıfırlama işlemi:

- veritabanını yeniden oluşturur
- üretilen PDF dosyalarını temizler
- oluşturulan barkod ve ürün görsellerini temizler
- oturumu kapatır
