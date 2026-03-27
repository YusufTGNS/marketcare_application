import os
from typing import Optional

from barcode import Code128
from barcode.writer import ImageWriter


def _get_assets_base() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


def ensure_barcode_png(barcode_value: str, *, out_dir: Optional[str] = None) -> str:
    """
    Verilen barkod değeri için PNG üretir (cache mantığı).
    Dönen değer: oluşturulan PNG dosya yolu.
    """
    if not out_dir:
        out_dir = os.path.join(_get_assets_base(), "barcodes")

    os.makedirs(out_dir, exist_ok=True)

    safe_name = "".join(ch for ch in str(barcode_value) if ch.isalnum() or ch in ("-", "_"))
    if not safe_name:
        safe_name = "barcode"

    png_path = os.path.join(out_dir, f"{safe_name}.png")
    if os.path.exists(png_path) and os.path.getsize(png_path) > 0:
        return png_path

    # python-barcode writer ImageWriter ile dosyaya yazar.
    cls = Code128
    writer = ImageWriter()
    # save() uzantıyı otomatik ekler; bu yüzden extension'ı vermeden base path kullanılır.
    base_no_ext = os.path.join(out_dir, f"{safe_name}")
    bc_obj = cls(str(barcode_value), writer=writer)
    bc_obj.save(base_no_ext)

    # Code128 default olarak .png üretir.
    if not os.path.exists(png_path):
        # fallback: oluşan dosyayı bul (bazı writer’lar farklı uzantı basabilir)
        for ext in (".png", ".jpg", ".jpeg"):
            p = base_no_ext + ext
            if os.path.exists(p):
                return p
        raise FileNotFoundError("Barkod görseli üretilemedi.")

    return png_path

