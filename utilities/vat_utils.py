from typing import Tuple


VAT_FOOD_KEYWORDS = {
    "su", "soda", "meyve", "sebze", "ekmek", "süt", "peynir", "yoğurt", "yogurt",
    "yumurta", "çay", "cay", "kahve", "şeker", "seker", "makarna", "pirinç", "pirinc",
    "un", "tuz", "yağ", "yag", "domates", "salatalık", "salatalik", "muz", "elma",
    "bisküvi", "biskuvi", "çikolata", "cikolata", "kraker", "cips", "kola", "gazoz"
}

VAT_COSMETIC_KEYWORDS = {
    "şampuan", "sampuan", "sabun", "parfüm", "parfum", "deodorant", "krem", "losyon",
    "makyaj", "ruj", "diş macunu", "dis macunu", "diş fırçası", "dis fircasi", "jilet"
}

VAT_MEDICAL_KEYWORDS = {
    "maske", "sargı", "sargi", "bandaj", "termometre", "vitamin", "medikal"
}


def infer_vat_rate_by_name(product_name: str) -> Tuple[float, str]:
    """
    Basit yerel 'AI benzeri' sınıflandırma.
    Ürün adındaki anahtar kelimelere göre en uygun KDV oranını tahmin eder.
    """
    name = (product_name or "").strip().lower()

    if any(keyword in name for keyword in VAT_FOOD_KEYWORDS):
        return 1.0, "Temel gıda / içecek sınıfı algılandı"
    if any(keyword in name for keyword in VAT_MEDICAL_KEYWORDS):
        return 10.0, "Medikal / sağlık kategorisi algılandı"
    if any(keyword in name for keyword in VAT_COSMETIC_KEYWORDS):
        return 20.0, "Kozmetik / kişisel bakım kategorisi algılandı"
    return 20.0, "Genel perakende ürünü olarak değerlendirildi"


def split_gross_price(gross_price: float, vat_rate: float) -> Tuple[float, float]:
    gross = float(gross_price)
    rate = float(vat_rate)
    if rate <= 0:
        return gross, 0.0
    net = gross / (1.0 + (rate / 100.0))
    tax = gross - net
    return net, tax
