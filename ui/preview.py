import tkinter as tk
import customtkinter as ctk

# ST-16 proportions (scaled to screen)
COLS, ROWS = 2, 8
LABEL_W_MM = 99.1
LABEL_H_MM = 33.9
A4_W_MM = 210
A4_H_MM = 297

SCALE = 2.2  # px per mm

A4_W_PX = int(A4_W_MM * SCALE)
A4_H_PX = int(A4_H_MM * SCALE)
LABEL_W_PX = int(LABEL_W_MM * SCALE)
LABEL_H_PX = int(LABEL_H_MM * SCALE)
MARGIN_L_PX = int(((A4_W_MM - COLS * LABEL_W_MM) / 2) * SCALE)
MARGIN_T_PX = int(((A4_H_MM - ROWS * LABEL_H_MM) / 2) * SCALE)


class PrintPreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, labels_data, selected_positions):
        super().__init__(parent)
        self.title("Print Preview – ST-16")
        self.resizable(True, True)
        self.geometry("1000x800")
        
        self.transient(parent)
        self.grab_set()

        self.zoom = 1.0
        self.labels_data = labels_data
        self.selected_positions = selected_positions
        self._build_ui(labels_data, selected_positions)
        self._center()

    def _build_ui(self, labels_data, selected_positions):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=10)
        
        title_lbl = ctk.CTkLabel(hdr, text="🖨  Print Preview – ST-16 A4", font=ctk.CTkFont("Segoe UI", 16, "bold"))
        title_lbl.pack(side="left")
        
        sub_lbl = ctk.CTkLabel(hdr, text=f"{len(selected_positions)} label(s) selected · 99.1 x 33.9 mm · 16 labels", text_color="gray", font=ctk.CTkFont("Segoe UI", 12))
        sub_lbl.pack(side="left", padx=20)

        ctrl = ctk.CTkFrame(hdr, fg_color="transparent")
        ctrl.pack(side="right")
        
        ctk.CTkButton(ctrl, text="−", width=30, command=self._zoom_out, font=ctk.CTkFont("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        self.zoom_label = ctk.CTkLabel(ctrl, text="100%", width=40, font=ctk.CTkFont("Segoe UI", 12, "bold"))
        self.zoom_label.pack(side="left", padx=5)
        ctk.CTkButton(ctrl, text="＋", width=30, command=self._zoom_in, font=ctk.CTkFont("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl, text="Fit", width=60, command=self._fit_page, fg_color="transparent", border_width=1, text_color=("gray10", "gray90")).pack(side="left", padx=(15, 0))
        
        ctk.CTkButton(hdr, text="✕ Close", command=self.destroy, fg_color="#f38ba8", hover_color="#eba0b5", text_color="#1e1e2e", width=80, font=ctk.CTkFont("Segoe UI", 12, "bold")).pack(side="right", padx=(0, 20))

        # Canvas container
        canvas_frame = ctk.CTkFrame(self)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.canvas = tk.Canvas(canvas_frame, bg="#2a2a2a", highlightthickness=0,
                                width=int(A4_W_PX * self.zoom) + 60,
                                height=min(int(A4_H_PX * self.zoom) + 60, 700))
        
        # Scrollbars (using CTkScrollbar)
        vsb = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=self.canvas.yview)
        hsb = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self._draw_page(labels_data, selected_positions)

    def _draw_page(self, labels_data, selected_positions):
        c = self.canvas
        c.delete("all")
        ox, oy = 20, 20  # page offset on canvas

        scale = SCALE * self.zoom
        page_w = int(A4_W_MM * scale)
        page_h = int(A4_H_MM * scale)
        label_w = int(LABEL_W_MM * scale)
        label_h = int(LABEL_H_MM * scale)
        margin_l = int(((A4_W_MM - COLS * LABEL_W_MM) / 2) * scale)
        margin_t = int(((A4_H_MM - ROWS * LABEL_H_MM) / 2) * scale)

        # Shadow
        c.create_rectangle(ox + 5, oy + 5, ox + page_w + 5, oy + page_h + 5, fill="#111111", outline="")
        # Page background
        c.create_rectangle(ox, oy, ox + page_w, oy + page_h, fill="white", outline="#888", width=1)

        labels_dict = {l["position"]: l for l in labels_data}

        for pos in range(1, 17):
            col = (pos - 1) % COLS
            row = (pos - 1) // COLS
            x = ox + margin_l + col * label_w
            y = oy + margin_t + row * label_h

            lbl = labels_dict.get(pos, {})
            selected = pos in selected_positions
            printed = bool(lbl.get("printed", 0))

            # Fill
            if selected:
                fill = "#e8f4fd"
            elif printed:
                fill = "#f0fff0"
            else:
                fill = "#ffffff"

            c.create_rectangle(x, y, x + label_w, y + label_h,
                                fill=fill, outline="#aaa", width=1,
                                dash=(4, 2) if not selected else None)

            if selected:
                c.create_rectangle(x, y, x + label_w, y + max(4, int(4 * self.zoom)),
                                    fill="#3b82f6", outline="")

            # Text
            lines = [lbl.get(f"line{i}", "") for i in range(1, 5)]
            lines = [l for l in lines if l.strip()]
            font_size = max(6, min(14, int(lbl.get("font_size", 10)) - 2))
            bold = bool(lbl.get("bold", 0))
            alignment = lbl.get("alignment", "center")
            anchor_map = {"left": "w", "center": "center", "right": "e"}
            anchor = anchor_map.get(alignment, "center")

            if alignment == "left":
                tx = x + int(6 * self.zoom)
            elif alignment == "right":
                tx = x + label_w - int(6 * self.zoom)
            else:
                tx = x + label_w // 2

            total_h = len(lines) * (font_size + 2)
            start_ty = y + label_h // 2 - total_h // 2 + font_size // 2
            font_cfg = ("Segoe UI", font_size, "bold") if bold else ("Segoe UI", font_size)

            for i, line in enumerate(lines):
                ty = start_ty + i * (font_size + 2)
                c.create_text(tx, ty, text=line, font=font_cfg, fill="#111", anchor=anchor)

            c.create_text(x + label_w - int(6 * self.zoom), y + int(6 * self.zoom),
                          text=str(pos), font=("Segoe UI", max(6, int(6 * self.zoom))),
                          fill="#aaaaaa", anchor="ne")

        width = page_w + 40
        height = page_h + 40
        self.canvas.configure(width=min(width, 1000), height=min(height, 800))
        c.configure(scrollregion=(0, 0, width, height))

    def _zoom_in(self):
        self.zoom = min(self.zoom + 0.15, 2.5)
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self._draw_page(self.labels_data, self.selected_positions)

    def _zoom_out(self):
        self.zoom = max(self.zoom - 0.15, 0.4)
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self._draw_page(self.labels_data, self.selected_positions)

    def _fit_page(self):
        self.zoom = 0.8
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self._draw_page(self.labels_data, self.selected_positions)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = 1000, 800
        self.geometry(f"+{max(0, pw - w//2)}+{max(0, ph - h//2)}")
