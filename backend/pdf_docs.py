"""PDF document generation: Tax Invoice and Dispatch Challan."""
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether,
)


COMPANY = {
    "name": "SSK FOOTCARE MANUFACTURING LLP",
    "address": "Industrial Area, Factory Floor",
    "city": "India",
    "gstin": "00AAAAA0000A1Z5",
    "phone": "+91 0000000000",
    "email": "ops@sskfootcare.com",
}

BRAND = colors.HexColor("#0F172A")
ACCENT = colors.HexColor("#C27842")
MUTED = colors.HexColor("#475569")
LIGHT = colors.HexColor("#F1F5F9")


def _inr(n) -> str:
    try:
        n = float(n or 0)
    except Exception:
        return str(n)
    s = f"{n:,.2f}"
    return f"Rs. {s}"


def _header(title: str, doc_no: str, doc_date: str):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("t", parent=styles["Heading1"], fontName="Helvetica-Bold",
                                 fontSize=20, leading=22, textColor=BRAND, spaceAfter=2)
    sub_style = ParagraphStyle("s", parent=styles["Normal"], fontName="Helvetica",
                               fontSize=8, textColor=MUTED, leading=10)
    small_bold = ParagraphStyle("sb", parent=styles["Normal"], fontName="Helvetica-Bold",
                                fontSize=9, textColor=BRAND, leading=11)

    left = [
        Paragraph(COMPANY["name"], small_bold),
        Paragraph(COMPANY["address"], sub_style),
        Paragraph(COMPANY["city"], sub_style),
        Paragraph(f"GSTIN: {COMPANY['gstin']}", sub_style),
        Paragraph(f"{COMPANY['phone']} &nbsp;|&nbsp; {COMPANY['email']}", sub_style),
    ]
    right = [
        Paragraph(title, title_style),
        Paragraph(f"<b>No.</b> {doc_no}", sub_style),
        Paragraph(f"<b>Date</b> {doc_date}", sub_style),
    ]

    t = Table([[left, right]], colWidths=[110 * mm, 70 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.4, BRAND),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def _addr_block(po: dict):
    styles = getSampleStyleSheet()
    label = ParagraphStyle("lab", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=8, textColor=ACCENT, leading=10, spaceAfter=1)
    body = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica",
                          fontSize=9, leading=12)

    bill = po.get("billing_address") or po.get("client_address") or "—"
    ship = po.get("shipping_address") or po.get("client_address") or "—"

    left = [
        Paragraph("BILL TO", label),
        Paragraph(f"<b>{po.get('client_name', '—')}</b>", body),
        Paragraph(bill.replace("\n", "<br/>"), body),
    ]
    right = [
        Paragraph("SHIP TO", label),
        Paragraph(f"<b>{po.get('client_name', '—')}</b>", body),
        Paragraph(ship.replace("\n", "<br/>"), body),
    ]
    t = Table([[left, right]], colWidths=[90 * mm, 90 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def _items_table(items: list, show_amount: bool = True):
    headers = ["#", "Style / Description", "Color", "Size", "HSN", "Qty"]
    widths = [10, 70, 22, 14, 22, 16]
    if show_amount:
        headers += ["Rate", "Amount"]
        widths += [22, 26]

    data = [headers]
    for i, li in enumerate(items, 1):
        desc = li.get("description") or li.get("style_code", "")
        style = li.get("style_code", "")
        cell = f"<b>{style}</b><br/><font size=7 color='#64748B'>{desc}</font>"
        row = [
            str(i),
            Paragraph(cell, ParagraphStyle("c", fontName="Helvetica", fontSize=9, leading=11)),
            str(li.get("color", "") or ""),
            str(li.get("size", "") or ""),
            str(li.get("hsn_code", "") or ""),
            str(li.get("quantity", 0)),
        ]
        if show_amount:
            row += [_inr(li.get("unit_price", 0)), _inr(li.get("amount", 0))]
        data.append(row)

    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (5, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (2, 1), (4, -1), "CENTER"),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D1CB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(style))
    return t


def _totals_block(po: dict):
    rows = [
        ["Subtotal", _inr(po.get("subtotal", 0))],
        [f"CGST ({po.get('cgst_rate', 0)}%)", _inr(po.get("cgst_amount", 0))],
        [f"SGST ({po.get('sgst_rate', 0)}%)", _inr(po.get("sgst_amount", 0))],
        [f"IGST ({po.get('igst_rate', 0)}%)", _inr(po.get("igst_amount", 0))],
        ["Total Quantity", str(po.get("total_quantity", 0))],
    ]
    grand = [["GRAND TOTAL", _inr(po.get("grand_total", 0))]]

    t1 = Table(rows, colWidths=[40 * mm, 35 * mm])
    t1.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    t2 = Table(grand, colWidths=[40 * mm, 35 * mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONT", (0, 0), (-1, -1), "Helvetica-Bold", 11),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))

    wrap = Table([[t1], [t2]], colWidths=[75 * mm])
    wrap.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    outer = Table([["", wrap]], colWidths=[105 * mm, 75 * mm])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return outer


def _footer(notes: str = "", terms: str = ""):
    styles = getSampleStyleSheet()
    label = ParagraphStyle("lab", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=8, textColor=ACCENT, leading=10, spaceAfter=2)
    body = ParagraphStyle("body", parent=styles["Normal"], fontName="Helvetica",
                          fontSize=8, leading=11, textColor=MUTED)
    parts = []
    if notes:
        parts += [Paragraph("NOTES", label), Paragraph(notes.replace("\n", "<br/>"), body), Spacer(1, 6)]
    if terms:
        parts += [Paragraph("TERMS", label), Paragraph(terms.replace("\n", "<br/>"), body), Spacer(1, 6)]
    parts += [
        Spacer(1, 20),
        Paragraph("For " + COMPANY["name"],
                  ParagraphStyle("sig", fontName="Helvetica-Bold", fontSize=9, textColor=BRAND, alignment=2)),
        Spacer(1, 36),
        Paragraph("Authorised Signatory",
                  ParagraphStyle("sigl", fontName="Helvetica", fontSize=8, textColor=MUTED, alignment=2)),
    ]
    return parts


def generate_tax_invoice_pdf(po: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title=f"Tax Invoice {po.get('po_number')}")
    elements = [
        _header("TAX INVOICE", po.get("po_number", "—"),
                po.get("po_date") or datetime.now().strftime("%Y-%m-%d")),
        Spacer(1, 4),
        _addr_block(po),
        _items_table(po.get("line_items", []), show_amount=True),
        Spacer(1, 10),
        _totals_block(po),
        Spacer(1, 16),
        *_footer(notes=po.get("notes", ""),
                 terms=po.get("payment_terms") and f"Payment Terms: {po['payment_terms']}" or ""),
    ]
    doc.build(elements)
    return buf.getvalue()


def generate_dispatch_challan_pdf(po: dict, dispatch_qty: int = None, transporter: str = "", vehicle: str = "") -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title=f"Dispatch Challan {po.get('po_number')}")

    styles = getSampleStyleSheet()
    label = ParagraphStyle("lab", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=8, textColor=ACCENT, leading=10)
    val = ParagraphStyle("v", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=11)

    dispatch_qty = dispatch_qty or po.get("total_quantity", 0)

    info = Table([
        [Paragraph("PO REFERENCE", label), Paragraph(po.get("po_number", "—"), val),
         Paragraph("DISPATCH DATE", label), Paragraph(datetime.now().strftime("%d %b %Y"), val)],
        [Paragraph("CLIENT", label), Paragraph(po.get("client_name", "—"), val),
         Paragraph("DELIVERY DATE", label), Paragraph(po.get("delivery_date", "—"), val)],
        [Paragraph("TRANSPORTER", label), Paragraph(transporter or "—", val),
         Paragraph("VEHICLE NO", label), Paragraph(vehicle or "—", val)],
        [Paragraph("DISPATCH QTY", label), Paragraph(f"<b>{dispatch_qty}</b> pairs", val),
         Paragraph("TOTAL ORDER QTY", label), Paragraph(f"{po.get('total_quantity', 0)} pairs", val)],
    ], colWidths=[28 * mm, 60 * mm, 28 * mm, 60 * mm])
    info.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements = [
        _header("DISPATCH CHALLAN", po.get("po_number", "—"),
                datetime.now().strftime("%Y-%m-%d")),
        Spacer(1, 4),
        _addr_block(po),
        info,
        Spacer(1, 10),
        _items_table(po.get("line_items", []), show_amount=False),
        Spacer(1, 16),
        *_footer(notes="Goods received in good condition. Please sign and return one copy.",
                 terms="This is a delivery challan, not a sale invoice."),
    ]
    doc.build(elements)
    return buf.getvalue()
