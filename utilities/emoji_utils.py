import re


def emoji_for_product(product_name: str) -> str:
    """
    "AI gibi" davranan basit bir heuristics eşleştirme.
    Gerçek yapay zeka çağrısı yapmıyoruz; ürün adına göre en makul emojiyi seçiyoruz.
    """
    name = (product_name or "").strip().lower()
    if not name:
        return "🛍️"

    # drink
    if any(k in name for k in ("su", "maden", "soda")):
        return "💧"
    if "kahve" in name:
        return "☕"
    if "çay" in name or "cay" in name:
        return "🍵"
    if any(k in name for k in ("kola", "gazoz", "soda")):
        return "🥤"

    # dairy
    if "süt" in name or "sut" in name:
        return "🥛"
    if "yoğurt" in name or "yogurt" in name:
        return "🥣"
    if "peynir" in name:
        return "🧀"
    if "tereyağı" in name or "tereyagi" in name or "tereyağı" in name:
        return "🧈"

    # bread / food
    if "ekmek" in name:
        return "🍞"
    if "tavuk" in name:
        return "🍗"
    if "et" in name:
        return "🥩"

    # fruit
    if any(k in name for k in ("elma", "apple")):
        return "🍎"
    if any(k in name for k in ("muz", "banana")):
        return "🍌"
    if any(k in name for k in ("portakal", "orange")):
        return "🍊"
    if any(k in name for k in ("çilek", "cilek", "strawberry")):
        return "🍓"

    # sweets / snacks
    if "çikolata" in name or "cikolata" in name:
        return "🍫"
    if "bisküvi" in name or "biskuvi" in name:
        return "🍪"
    if "şeker" in name or "seker" in name:
        return "🍬"
    if "patates" in name:
        return "🥔"

    # home / cleaning
    if "deterjan" in name or "deterjan" in name:
        return "🧼"
    if "sabun" in name:
        return "🧴"

    # default
    # çok uzun isimlerde son sayılara bakarak "paket" hissi ver
    if re.search(r"\b\d+\b", name):
        return "📦"
    return "🛍️"

