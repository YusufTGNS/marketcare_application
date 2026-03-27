import os
from dataclasses import dataclass
from typing import List, Optional

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from utilities.barcode_utils import ensure_barcode_png
from utilities.datetime_utils import format_db_datetime_local


def _try_register_fonts():
    candidates_normal = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\DejaVuSans.ttf",
    ]
    candidates_bold = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf",
        r"C:\Windows\Fonts\DejaVuSans-Bold.ttf",
    ]

    font_normal = next((path for path in candidates_normal if os.path.exists(path)), None)
    font_bold = next((path for path in candidates_bold if os.path.exists(path)), None)
    if not font_normal:
        return "Helvetica", "Helvetica-Bold"

    try:
        pdfmetrics.registerFont(TTFont("MarketFont", font_normal))
        if font_bold:
            pdfmetrics.registerFont(TTFont("MarketFontBold", font_bold))
            return "MarketFont", "MarketFontBold"
        return "MarketFont", "MarketFont"
    except Exception:
        return "Helvetica", "Helvetica-Bold"


@dataclass(frozen=True)
class SaleItemView:
    product_name: str
    barcode_value: str
    image_path: Optional[str]
    icon_path: Optional[str]
    qty: int
    unit_price: float
    unit_net_price: float
    vat_rate: float
    tax_amount: float
    line_total: float


class PDFGenerator:
    def __init__(self, out_dir: Optional[str] = None):
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        self.font_reg, self.font_bold = _try_register_fonts()
        self.currency_symbol = "TL"
        self.colors = {
            "navy": HexColor("#14324A"),
            "cyan": HexColor("#00B4D8"),
            "sky": HexColor("#EAF7FB"),
            "line": HexColor("#CFE3EC"),
            "text": HexColor("#203544"),
            "muted": HexColor("#5D7485"),
        }

    def _save_path(self, sale_no: str, kind: str) -> str:
        return os.path.join(self.out_dir, f"{sale_no}_{kind}.pdf")

    def _parse_datetime(self, created_at: str) -> str:
        return format_db_datetime_local(created_at)

    def _money(self, value: float) -> str:
        return f"{self.currency_symbol}{float(value):.2f}"

    def _draw_info_block(self, c, x, y, w, h, title: str, value: str):
        c.setFillColor(self.colors["sky"])
        c.roundRect(x, y - h, w, h, 4 * mm, fill=1, stroke=0)
        c.setFillColor(self.colors["muted"])
        c.setFont(self.font_reg, 8)
        c.drawString(x + 4 * mm, y - 6 * mm, title)
        c.setFillColor(self.colors["text"])
        c.setFont(self.font_bold, 10)
        c.drawString(x + 4 * mm, y - 12 * mm, value)

    def generate_slip_pdf(
        self,
        *,
        sale_no: str,
        created_at: str,
        customer_name: Optional[str],
        payment_type: Optional[str],
        total_amount: float,
        tax_amount: float,
        grand_total: float,
        items: List[SaleItemView],
        store_name: str = "MarketCare",
    ) -> str:
        out_path = self._save_path(sale_no, "slip")
        c = canvas.Canvas(out_path, pagesize=A6)
        width, height = A6

        c.setFillColor(self.colors["navy"])
        c.roundRect(8 * mm, height - 28 * mm, width - 16 * mm, 18 * mm, 4 * mm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont(self.font_bold, 13)
        c.drawString(12 * mm, height - 17 * mm, store_name)
        c.setFont(self.font_reg, 8)
        c.drawString(12 * mm, height - 22 * mm, f"Satis Ozeti | {self._parse_datetime(created_at)}")

        y = height - 34 * mm
        c.setFillColor(self.colors["text"])
        c.setFont(self.font_bold, 9)
        c.drawString(10 * mm, y, f"Satis No: {sale_no}")
        y -= 5 * mm
        c.setFont(self.font_reg, 8)
        c.drawString(10 * mm, y, f"Odeme: {payment_type or '-'}")
        y -= 4 * mm
        if customer_name:
            c.drawString(10 * mm, y, f"Musteri: {customer_name}")
            y -= 4 * mm

        c.setStrokeColor(self.colors["line"])
        c.line(10 * mm, y, width - 10 * mm, y)
        y -= 5 * mm

        c.setFont(self.font_bold, 8)
        c.drawString(10 * mm, y, "Urun")
        c.drawRightString(width - 10 * mm, y, "Toplam")
        y -= 4.5 * mm

        c.setFont(self.font_reg, 7.5)
        for item in items:
            label = f"{item.qty} x {item.product_name}"
            if len(label) > 26:
                label = label[:25] + "..."
            c.drawString(10 * mm, y, label)
            c.drawRightString(width - 10 * mm, y, self._money(item.line_total))
            y -= 3.8 * mm

            kdv_text = f"KDV %{item.vat_rate:.0f} | KDV {self._money(item.tax_amount)}"
            c.setFillColor(self.colors["muted"])
            c.drawString(12 * mm, y, kdv_text)
            c.setFillColor(self.colors["text"])
            y -= 4.2 * mm

            try:
                png = ensure_barcode_png(str(item.barcode_value))
                c.drawImage(
                    png,
                    12 * mm,
                    y - 7 * mm,
                    width=34 * mm,
                    height=10 * mm,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                y -= 9 * mm
            except Exception:
                y -= 2 * mm

            if y < 28 * mm:
                c.showPage()
                y = height - 18 * mm
                c.setFillColor(self.colors["text"])
                c.setFont(self.font_reg, 8)

        c.setStrokeColor(self.colors["line"])
        c.line(10 * mm, y, width - 10 * mm, y)
        y -= 5 * mm

        c.setFont(self.font_reg, 8)
        c.drawRightString(width - 10 * mm, y, f"Ara Toplam: {self._money(total_amount)}")
        y -= 4 * mm
        c.drawRightString(width - 10 * mm, y, f"Toplam KDV: {self._money(tax_amount)}")
        y -= 5 * mm
        c.setFont(self.font_bold, 11)
        c.drawRightString(width - 10 * mm, y, f"Genel Toplam: {self._money(grand_total)}")

        c.save()
        return out_path

    def generate_invoice_pdf(
        self,
        *,
        sale_no: str,
        created_at: str,
        customer_name: Optional[str],
        payment_type: Optional[str],
        total_amount: float,
        tax_amount: float,
        grand_total: float,
        items: List[SaleItemView],
        store_name: str = "MarketCare",
    ) -> str:
        out_path = self._save_path(sale_no, "invoice")
        c = canvas.Canvas(out_path, pagesize=A4)
        width, height = A4

        c.setFillColor(self.colors["navy"])
        c.rect(0, height - 42 * mm, width, 42 * mm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont(self.font_bold, 22)
        c.drawString(16 * mm, height - 18 * mm, store_name)
        c.setFont(self.font_reg, 10)
        c.drawString(16 * mm, height - 25 * mm, "Perakende satis faturasi")
        c.drawRightString(width - 16 * mm, height - 18 * mm, f"FATURA {sale_no}")
        c.drawRightString(width - 16 * mm, height - 25 * mm, self._parse_datetime(created_at))

        block_y = height - 50 * mm
        self._draw_info_block(c, 16 * mm, block_y, 54 * mm, 16 * mm, "Odeme", payment_type or "-")
        self._draw_info_block(c, 74 * mm, block_y, 54 * mm, 16 * mm, "Musteri", customer_name or "Perakende Musteri")
        self._draw_info_block(c, 132 * mm, block_y, 54 * mm, 16 * mm, "Genel Toplam", self._money(grand_total))

        table_top = height - 74 * mm
        x_name = 18 * mm
        x_barcode = 82 * mm
        x_qty = 114 * mm
        x_unit = 128 * mm
        x_vat = 153 * mm
        x_tax = 170 * mm
        x_total = 190 * mm

        c.setFillColor(self.colors["sky"])
        c.roundRect(16 * mm, table_top - 10 * mm, width - 32 * mm, 10 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(self.colors["navy"])
        c.setFont(self.font_bold, 9)
        c.drawString(x_name, table_top - 6.5 * mm, "Urun")
        c.drawString(x_barcode, table_top - 6.5 * mm, "Barkod")
        c.drawString(x_qty, table_top - 6.5 * mm, "Adet")
        c.drawString(x_unit, table_top - 6.5 * mm, "Net")
        c.drawString(x_vat, table_top - 6.5 * mm, "KDV")
        c.drawString(x_tax, table_top - 6.5 * mm, "KDV Tutar")
        c.drawString(x_total, table_top - 6.5 * mm, "Toplam")

        y = table_top - 16 * mm
        row_height = 12 * mm
        c.setFont(self.font_reg, 8.5)
        c.setFillColor(self.colors["text"])

        for index, item in enumerate(items):
            if y < 38 * mm:
                c.showPage()
                c.setFillColor(self.colors["text"])
                c.setFont(self.font_reg, 8.5)
                y = height - 26 * mm

            if index % 2 == 0:
                c.setFillColor(HexColor("#F8FBFD"))
                c.roundRect(16 * mm, y - 8 * mm, width - 32 * mm, 10 * mm, 2 * mm, fill=1, stroke=0)
                c.setFillColor(self.colors["text"])

            product_name = str(item.product_name or "")
            if len(product_name) > 20:
                product_name = product_name[:19] + "..."
            barcode_value = str(item.barcode_value or "")
            if len(barcode_value) > 14:
                barcode_value = barcode_value[:14]

            c.drawString(x_name, y - 2 * mm, product_name)
            c.drawString(x_barcode, y - 2 * mm, barcode_value)
            c.drawString(x_qty, y - 2 * mm, str(item.qty))
            c.drawString(x_unit, y - 2 * mm, self._money(item.unit_net_price))
            c.drawString(x_vat, y - 2 * mm, f"%{item.vat_rate:.0f}")
            c.drawString(x_tax, y - 2 * mm, self._money(item.tax_amount))
            c.drawString(x_total, y - 2 * mm, self._money(item.line_total))
            y -= row_height

        summary_y = max(y - 2 * mm, 42 * mm)
        c.setFillColor(self.colors["navy"])
        c.roundRect(width - 82 * mm, summary_y - 22 * mm, 66 * mm, 24 * mm, 4 * mm, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont(self.font_reg, 10)
        c.drawString(width - 76 * mm, summary_y - 7 * mm, f"Ara Toplam: {self._money(total_amount)}")
        c.drawString(width - 76 * mm, summary_y - 13 * mm, f"Toplam KDV: {self._money(tax_amount)}")
        c.setFont(self.font_bold, 11)
        c.drawString(width - 76 * mm, summary_y - 19 * mm, f"Genel Toplam: {self._money(grand_total)}")

        footer_y = 20 * mm
        c.setFillColor(self.colors["muted"])
        c.setFont(self.font_reg, 9)
        c.drawString(16 * mm, footer_y, "Bu belge sistem tarafindan otomatik olusturulmustur.")
        c.drawRightString(width - 16 * mm, footer_y, "info@marketcare.example")

        c.save()
        return out_path
