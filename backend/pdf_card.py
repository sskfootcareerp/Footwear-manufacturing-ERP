"""PDF: Printable Production Card (for worker reference on the floor)."""
import base64
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

BLACK = colors.black
HEAD = colors.HexColor("#0F172A")
ACCENT = colors.HexColor("#C27842")
LINE = colors.HexColor("#94A3B8")
LIGHT = colors.HexColor("#F1F5F9")


def _img_from_dataurl(image_url: str, max_h_mm: float = 60, max_w_mm: float = 60):
    """Decode a base64 data URL into a reportlab Image. Returns None on failure."""
    if not image_url or not image_url.startswith("data:image"):
        return None
    try:
        header, b64 = image_url.split(",", 1)
        raw = base64.b64decode(b64)
        bio = io.BytesIO(raw)
        img = Image(bio)
        # scale to fit
        ratio = img.imageWidth / img.imageHeight if img.imageHeight else 1
        target_h_pt = max_h_mm * mm
        target_w_pt = max_w_mm * mm
        if ratio > (target_w_pt / target_h_pt):
            img.drawWidth = target_w_pt
            img.drawHeight = target_w_pt / ratio
        else:
            img.drawHeight = target_h_pt
            img.drawWidth = target_h_pt * ratio
        return img
    except Exception:
        return None


def build_production_card(job_group: dict, style: dict | None) -> bytes:
    """job_group keys:
       po_number, client_name, style_code, color, description, delivery_date,
       sizes:[{size,quantity}], total_qty, components{upper_done,bottom_done,sole_done},
       assignments:{role:{worker_name,rate_per_pair}}
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title=f"Production Card {job_group.get('style_code','')}-{job_group.get('color','')}",
    )
    S = {
        "h0": ParagraphStyle("h0", fontName="Helvetica-Bold", fontSize=16, leading=18, textColor=BLACK),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=24, textColor=BLACK),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, leading=13, textColor=ACCENT),
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=8, textColor=ACCENT, leading=10),
        "val": ParagraphStyle("v", fontName="Helvetica", fontSize=9, textColor=BLACK, leading=11),
        "valb": ParagraphStyle("vb", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK, leading=12),
        "small": ParagraphStyle("sm", fontName="Helvetica", fontSize=7, textColor=colors.HexColor("#475569"), leading=9),
        "huge_color": ParagraphStyle("hc", fontName="Helvetica-Bold", fontSize=20, textColor=ACCENT, leading=22),
    }

    # Company strip
    company = Table([[Paragraph("SSK FOOTCARE MANUFACTURING LLP", S["h0"]),
                      Paragraph(f"Production Card · {datetime.now().strftime('%d %b %Y %H:%M')}",
                                ParagraphStyle("d", fontName="Helvetica", fontSize=8, alignment=2, textColor=colors.HexColor("#475569")))]],
                    colWidths=[120 * mm, 60 * mm])
    company.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), HEAD),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))

    # Header card: image | identifying info | color/qty
    img_cell = _img_from_dataurl((style or {}).get("image_url", ""), max_h_mm=55, max_w_mm=55)
    if img_cell is None:
        img_cell = Table([[Paragraph("👟<br/>No Image", ParagraphStyle("ni", fontName="Helvetica", fontSize=10, alignment=1, leading=14))]],
                         colWidths=[55 * mm], rowHeights=[55 * mm])
        img_cell.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, LINE),
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

    info_rows = [
        [Paragraph("PO NUMBER", S["lab"]), Paragraph(job_group.get("po_number", "—"), S["valb"])],
        [Paragraph("CLIENT", S["lab"]), Paragraph(job_group.get("client_name", "—"), S["val"])],
        [Paragraph("STYLE", S["lab"]), Paragraph(f"<b>{job_group.get('style_code','—')}</b>", S["h1"])],
        [Paragraph("ARTICLE", S["lab"]), Paragraph((style or {}).get("name", "") or job_group.get("description", "—"), S["val"])],
        [Paragraph("DELIVERY", S["lab"]), Paragraph(job_group.get("delivery_date", "—"), S["valb"])],
    ]
    info_t = Table(info_rows, colWidths=[24 * mm, 65 * mm])
    info_t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))

    color_qty = Table([
        [Paragraph("COLOR", S["lab"])],
        [Paragraph(job_group.get("color", "—"), S["huge_color"])],
        [Spacer(1, 4)],
        [Paragraph("TOTAL PAIRS", S["lab"])],
        [Paragraph(str(job_group.get("total_qty", 0)),
                   ParagraphStyle("tp", fontName="Helvetica-Bold", fontSize=28, textColor=HEAD, leading=30))],
    ], colWidths=[40 * mm])
    color_qty.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, ACCENT),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    header_card = Table([[img_cell, info_t, color_qty]],
                        colWidths=[60 * mm, 90 * mm, 40 * mm])
    header_card.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    # Size matrix
    sizes = job_group.get("sizes", [])
    size_data = [["SIZE"] + [str(s["size"]) for s in sizes] + ["TOTAL"]]
    qty_row = [job_group.get("color", "")] + [str(s["quantity"]) for s in sizes] + [str(job_group.get("total_qty", 0))]
    size_data.append(qty_row)
    size_t = Table(size_data, colWidths=[36 * mm] + [22 * mm] * len(sizes) + [22 * mm])
    size_t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BLACK),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), HEAD),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 11),
        ("FONT", (0, 1), (-1, -1), "Helvetica-Bold", 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (-1, 1), (-1, 1), LIGHT),
        ("TEXTCOLOR", (-1, 1), (-1, 1), ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    # Components (Upper / Bottom / Sole) with sub-layers
    comp = job_group.get("components", {}) or {}
    def comp_cell(title, done, layers):
        check = "☑" if done else "☐"
        layer_lines = "<br/>".join([f"   • {l}" for l in layers])
        return Paragraph(
            f"<font size=14><b>{check} {title}</b></font><br/><font size=8 color='#475569'>{layer_lines}</font>",
            ParagraphStyle("c", fontName="Helvetica", fontSize=10, leading=12),
        )

    comp_t = Table([[
        comp_cell("UPPER", comp.get("upper_done"),
                  ["Upper Top", "Mid Layer / Reinforcement", "Lining"]),
        comp_cell("BOTTOM / INSOLE", comp.get("bottom_done"),
                  ["Bottom Layer", "Insole Board + Cushion", "Insole Cover (PU/Leather)"]),
        comp_cell("SOLE", comp.get("sole_done"), ["Sole"]),
    ]], colWidths=[63 * mm, 63 * mm, 64 * mm])
    comp_t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BLACK),
        ("LINEAFTER", (0, 0), (-2, -1), 1, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    # Karigar assignments
    assigns = job_group.get("assignments", {}) or {}
    role_labels = [
        ("cutting", "CUTTING"), ("upper", "UPPER"), ("bottom", "BOTTOM"),
        ("stitching", "STITCHING"), ("lasting", "LASTING"),
        ("sole_pasting", "SOLE PASTING"), ("finishing", "FINISHING"),
    ]
    kar_rows = [["ROLE", "KARIGAR", "RATE / PAIR", "SIGN"]]
    for rk, rl in role_labels:
        a = assigns.get(rk) or {}
        kar_rows.append([
            rl,
            a.get("worker_name", "_______________"),
            f"₹{a.get('rate_per_pair', '')}" if a.get("rate_per_pair") is not None else "_______",
            "________________",
        ])
    kar_t = Table(kar_rows, colWidths=[40 * mm, 60 * mm, 30 * mm, 60 * mm])
    kar_t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BLACK),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), HEAD),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    # Footer notes
    footer_t = Table([[
        Paragraph("<b>NOTES / INSTRUCTIONS:</b><br/><br/>________________________________________________________________<br/><br/>________________________________________________________________<br/><br/>________________________________________________________________",
                  ParagraphStyle("n", fontName="Helvetica", fontSize=9, leading=14)),
        Paragraph("<b>QC PASS:</b> ☐<br/><br/><b>SIGN:</b><br/><br/>____________________<br/>Supervisor",
                  ParagraphStyle("qc", fontName="Helvetica", fontSize=9, leading=14, alignment=1)),
    ]], colWidths=[125 * mm, 65 * mm])
    footer_t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BLACK),
        ("LINEAFTER", (0, 0), (0, 0), 1, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements = [
        company,
        Spacer(1, 4),
        header_card,
        Spacer(1, 6),
        Paragraph("SIZE BREAKDOWN", S["h2"]),
        Spacer(1, 2),
        size_t,
        Spacer(1, 8),
        Paragraph("COMPONENTS", S["h2"]),
        Spacer(1, 2),
        comp_t,
        Spacer(1, 8),
        Paragraph("KARIGAR ASSIGNMENTS", S["h2"]),
        Spacer(1, 2),
        kar_t,
        Spacer(1, 8),
        footer_t,
    ]
    doc.build(elements)
    return buf.getvalue()
