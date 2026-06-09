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

        # Text processing with per-line styles
        line_styles_dict = lbl.get("line_styles_dict", {})
        fallback_size = int(lbl.get("font_size", 10))
        fallback_bold = bool(lbl.get("bold", 0))
        fallback_align = lbl.get("alignment", "center")

        lines_data = []
        total_text_h = 0

        for i in range(1, 5):
            text = lbl.get(f"line{i}", "").strip()
            if text:
                style = line_styles_dict.get(f"line{i}", {})
                fsize = int(style.get("font_size", fallback_size))
                bold = bool(style.get("bold", fallback_bold))
                align = style.get("alignment", fallback_align)
                lines_data.append({"text": text, "size": fsize, "bold": bold, "align": align})
                total_text_h += (fsize + 2)

        if lines_data:
            # start_y is the top edge of the text block
            current_y = y + lh / 2 + total_text_h / 2

            for line_data in lines_data:
                fsize = line_data["size"]
                bold = line_data["bold"]
                align = line_data["align"]
                text = line_data["text"]

                font_name = "Helvetica-Bold" if bold else "Helvetica"
                c.setFont(font_name, fsize)

                # Move to the baseline for drawing
                current_y -= fsize
                
                if align == "left":
                    c.drawString(x + 3, current_y, text)
                elif align == "right":
                    c.drawRightString(x + lw - 3, current_y, text)
                else:
                    c.drawCentredString(x + lw / 2, current_y, text)

                # 2pt spacing
                current_y -= 2

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
