import os
import sys
import tempfile
from datetime import datetime

try:
    import win32print
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# ST-16 A4 label sheet format for laser, inkjet, and copier printers
PAGE_W_MM, PAGE_H_MM = 210, 297
COLS, ROWS = 2, 8
LABEL_W_MM = 99.1
LABEL_H_MM = 33.9

# Margins calculated to center 4 cols × 4 rows on A4
MARGIN_LEFT_MM = (PAGE_W_MM - COLS * LABEL_W_MM) / 2
MARGIN_TOP_MM = (PAGE_H_MM - ROWS * LABEL_H_MM) / 2


def build_pdf(labels_data, output_path, page_margins=None):
    """
    labels_data: list of 16 dicts, index 0 = position 1, etc.
    Each dict: line1..line4, font_size, bold, alignment, selected (bool)
    """
    if not HAS_REPORTLAB:
        raise RuntimeError("reportlab is not installed")

    ml = MARGIN_LEFT_MM * mm
    mt = MARGIN_TOP_MM * mm
    lw = LABEL_W_MM * mm
    lh = LABEL_H_MM * mm

    c = canvas.Canvas(output_path, pagesize=A4)
    page_w, page_h = A4

    for idx, lbl in enumerate(labels_data):
        if not lbl.get("selected", True):
            continue

        col = idx % COLS
        row = idx // COLS

        x = ml + col * lw
        # PDF y=0 is bottom; flip
        y = page_h - mt - (row + 1) * lh

        # Draw border
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setLineWidth(0.5)
        c.rect(x, y, lw, lh, stroke=1, fill=0)

        # Text
        font_size = int(lbl.get("font_size", 10))
        bold = lbl.get("bold", 0)
        font_name = "Helvetica-Bold" if bold else "Helvetica"
        alignment = lbl.get("alignment", "center")

        lines = [
            lbl.get("line1", ""),
            lbl.get("line2", ""),
            lbl.get("line3", ""),
            lbl.get("line4", ""),
        ]
        lines = [l for l in lines if l.strip()]

        if lines:
            total_text_h = len(lines) * (font_size + 2)
            start_y = y + lh / 2 + total_text_h / 2 - font_size

            for i, line in enumerate(lines):
                ty = start_y - i * (font_size + 2)
                c.setFont(font_name, font_size)
                if alignment == "left":
                    c.drawString(x + 3, ty, line)
                elif alignment == "right":
                    c.drawRightString(x + lw - 3, ty, line)
                else:
                    c.drawCentredString(x + lw / 2, ty, line)

    c.save()
    return output_path


def print_labels(labels_data, printer_name=None):
    """Build a PDF and send it to the printer."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    pdf_path = tmp.name

    build_pdf(labels_data, pdf_path)

    try:
        os.startfile(pdf_path)
        return True, "PDF opened successfully. Please use your PDF viewer to print."
    except Exception as e:
        return False, f"Could not open PDF: {e}"


def get_printers():
    if HAS_WIN32:
        try:
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            return [p[2] for p in printers]
        except Exception:
            pass
    return []


def get_default_printer():
    if HAS_WIN32:
        try:
            return win32print.GetDefaultPrinter()
        except Exception:
            pass
    return ""
