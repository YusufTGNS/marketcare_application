# MarketCare

PyQt5 ile gelistirilmis masaustu market yonetim uygulamasi. Urun, stok, satis, belge ve personel akislari tek panelde toplanir.

## Ozellikler

- Urun ekleme, guncelleme ve arama
- Otomatik barkod uretme ve panoya kopyalama
- Urun adina gore KDV orani tahmini
- Sepet ve satis tamamlama akisi
- Slip ve fatura PDF olusturma
- Kritik stok ve stok hareketi takibi
- Personel ve oturum yonetimi

## Kurulum

```powershell
cd C:\...\market
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Calistirma

```powershell
cd C:\...\market
python market_gui.py
```

Ilk acilista veritabani otomatik olarak hazirlanir.

## Varsayilan Kullanicilar

| Rol | Kullanici Adi | Sifre |
|---|---|---|
| Admin | `admin` | `admin123` |
| Personel | `personel` | `personel123` |

## Paketleme

```powershell
pyinstaller --noconfirm MarketCare.spec
```

Dagitim icin `dist\\MarketCare\\` klasorunun tamami kullanilmalidir.

## Proje Yapisi

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
|-- MarketCare.spec
`-- requirements.txt
```

## Yerel Dosyalar

- `data/market.db`: SQLite veritabani
- `documents/`: Uretilen slip ve fatura PDF dosyalari
- `assets/barcodes/`: Uretilen barkod gorselleri
- `assets/product_images/`: Urun gorselleri

## Veritabani Sifirlama

Uygulamadaki sifirlama islemi veritabanini, uretilen PDF dosyalarini ve olusturulan gorselleri temizler.
