import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import database_service as db, backup_service, print_service
from ui.label_editor import LabelEditorDialog
from ui.preview import PrintPreviewWindow
from ui.settings import SettingsDialog

COLS, ROWS = 2, 8

# Initialize CustomTkinter settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

STATUS_COLORS = {
    "EMPTY": ("#ffffff", "#bbbbbb", "#e5e5e5", 1),
    "FILLED": ("#ffffff", "#1e1e2e", "#f9e2af", 2),
    "PRINTED": ("#ffffff", "#1e1e2e", "#a6e3a1", 2),
}


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Label Printer – ST-16 A4 | Laser / Inkjet / Copier")
        self.geometry("1100x750")
        self.minsize(1000, 680)

        db.init_db()

        self.current_sheet_id = None
        self.labels_data = {}
        self.selected_positions = set()
        self.sheet_widgets = {}

        self._build_menu()
        self._build_layout()
        self._show_welcome()

    # ──────────────────────────────────────────────────────────────────────────
    # MENU BAR
    # ──────────────────────────────────────────────────────────────────────────
    def _build_menu(self):
        # We can still use standard tk.Menu for the window menu
        mb = tk.Menu(self)
        self.config(menu=mb)

        file_menu = tk.Menu(mb, tearoff=False)
        mb.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Sheet        Ctrl+N", command=self._new_sheet)
        file_menu.add_command(label="Open Sheet       Ctrl+O", command=self._open_sheet_dialog)
        file_menu.add_command(label="Save Sheet       Ctrl+S", command=self._save_sheet)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        print_menu = tk.Menu(mb, tearoff=False)
        mb.add_cascade(label="Print", menu=print_menu)
        print_menu.add_command(label="Print Preview    Ctrl+P", command=self._print_preview)
        print_menu.add_command(label="Print Selected", command=self._print_selected)

        tools_menu = tk.Menu(mb, tearoff=False)
        mb.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self._open_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Backup Database", command=self._backup)
        tools_menu.add_command(label="Restore Database", command=self._restore)

        self.bind_all("<Control-n>", lambda e: self._new_sheet())
        self.bind_all("<Control-o>", lambda e: self._open_sheet_dialog())
        self.bind_all("<Control-s>", lambda e: self._save_sheet())
        self.bind_all("<Control-p>", lambda e: self._print_preview())

    # ──────────────────────────────────────────────────────────────────────────
    # MAIN LAYOUT
    # ──────────────────────────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Top toolbar ───────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color=("gray85", "gray15"), corner_radius=0)
        toolbar.pack(fill="x", pady=0)

        btn_kwargs = {"height": 32, "font": ctk.CTkFont("Segoe UI", 12, "bold")}

        ctk.CTkButton(toolbar, text="＋ New Sheet", command=self._new_sheet, **btn_kwargs).pack(side="left", padx=(10, 5), pady=8)
        ctk.CTkButton(toolbar, text="📂 Open Sheet", command=self._open_sheet_dialog, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)
        ctk.CTkButton(toolbar, text="💾 Save", command=self._save_sheet, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)
        
        sep1 = ctk.CTkFrame(toolbar, width=2, height=30, fg_color="gray50")
        sep1.pack(side="left", padx=10, pady=8)

        ctk.CTkButton(toolbar, text="🖨 Print", command=self._print_selected, fg_color="#cba6f7", hover_color="#d6b5fa", text_color="#1e1e2e", **btn_kwargs).pack(side="left", padx=5, pady=8)
        ctk.CTkButton(toolbar, text="📥 Download PDF", command=self._download_pdf, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)
        ctk.CTkButton(toolbar, text="👁 Preview", command=self._print_preview, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)

        sep2 = ctk.CTkFrame(toolbar, width=2, height=30, fg_color="gray50")
        sep2.pack(side="left", padx=10, pady=8)

        ctk.CTkButton(toolbar, text="⚙ Settings", command=self._open_settings, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)
        ctk.CTkButton(toolbar, text="📦 Backup", command=self._backup, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)
        ctk.CTkButton(toolbar, text="🔄 Restore", command=self._restore, fg_color="transparent", text_color=("gray10", "gray90"), border_width=1, **btn_kwargs).pack(side="left", padx=5, pady=8)

        # sheet name label
        self.sheet_name_lbl = ctk.CTkLabel(toolbar, text="No sheet open", font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"), text_color="gray")
        self.sheet_name_lbl.pack(side="right", padx=20)

        # ── Main body ─────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # Left panel – sheet list
        self.left_panel = ctk.CTkFrame(body, width=240, fg_color=("gray90", "gray12"), corner_radius=0)
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)
        self._build_left_panel()

        # Right – grid + status bar
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        self.grid_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w", fg_color=("gray85", "gray15"), text_color=("gray30", "gray70"), height=30, font=ctk.CTkFont("Segoe UI", 11), padx=10)
        self.status_bar.pack(fill="x", side="bottom")

    def _build_left_panel(self):
        # Header
        ctk.CTkLabel(self.left_panel, text="Sheets", font=ctk.CTkFont("Segoe UI", 16, "bold")).pack(fill="x", padx=15, pady=(15, 10))

        # Search
        sf = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        sf.pack(fill="x", padx=10, pady=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_sheet_list())
        se = ctk.CTkEntry(sf, textvariable=self.search_var, placeholder_text="Search sheets...", height=32, font=ctk.CTkFont("Segoe UI", 12))
        se.pack(fill="x", expand=True)

        ctk.CTkFrame(self.left_panel, height=1, fg_color="gray30").pack(fill="x", padx=10)

        # List
        self.sheet_scrollable = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent", corner_radius=0)
        self.sheet_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

        self.sheet_count_lbl = ctk.CTkLabel(self.left_panel, text="", font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), text_color="gray")
        self.sheet_count_lbl.pack(fill="x", padx=15, pady=(0, 5))

        self._refresh_sheet_list()

        # Delete button
        ctk.CTkButton(self.left_panel, text="🗑 Delete Selected Sheet", command=self._delete_sheet, fg_color="transparent", text_color="#f38ba8", border_width=1, border_color="#f38ba8", hover_color="#f38ba8", font=ctk.CTkFont("Segoe UI", 12)).pack(fill="x", padx=15, pady=15)

    def _refresh_sheet_list(self):
        for widget in self.sheet_scrollable.winfo_children():
            widget.destroy()

        self.sheet_widgets = {}
        q = self.search_var.get().strip()
        sheets = db.search_sheets(q) if q else db.get_all_sheets()
        self._sheet_list_data = sheets

        for s in sheets:
            sid = s["id"]
            name = f"{s['name']}"
            btn = ctk.CTkButton(
                self.sheet_scrollable, text=name, anchor="w", fg_color="transparent",
                text_color=("gray10", "gray90"), hover_color=("gray80", "gray20"),
                command=lambda id=sid: self._load_sheet(id), font=ctk.CTkFont("Segoe UI", 12)
            )
            btn.pack(fill="x", pady=2, padx=2)
            self.sheet_widgets[sid] = btn

            if self.current_sheet_id == sid:
                btn.configure(fg_color="#89b4fa", text_color="#1e1e2e")

        total = len(sheets)
        self.sheet_count_lbl.configure(text=f"{total} sheet{'s' if total != 1 else ''} found")

    # ──────────────────────────────────────────────────────────────────────────
    # LABEL GRID
    # ──────────────────────────────────────────────────────────────────────────
    def _build_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        if not self.current_sheet_id:
            return

        # Header
        hf = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        hf.pack(fill="x", pady=(0, 15))
        sheet = db.get_sheet(self.current_sheet_id)
        ctk.CTkLabel(hf, text=f"📄  {sheet['name']}", font=ctk.CTkFont("Segoe UI", 20, "bold")).pack(side="left")
        ctk.CTkLabel(hf, text=f"Created: {sheet['created_at'][:10]}   Status: {sheet['status']}", text_color="gray", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left", padx=20)

        # Select-all / deselect
        ctrl_f = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        ctrl_f.pack(fill="x", pady=(0, 15))
        
        btn_kw = {"height": 28, "fg_color": ("gray80", "gray25"), "text_color": ("gray10", "gray90"), "hover_color": ("gray70", "gray30"), "font": ctk.CTkFont("Segoe UI", 11)}
        ctk.CTkButton(ctrl_f, text="☑ Select All Empty", command=self._select_empty, **btn_kw).pack(side="left")
        ctk.CTkButton(ctrl_f, text="☐ Deselect All", command=self._deselect_all, **btn_kw).pack(side="left", padx=10)
        ctk.CTkButton(ctrl_f, text="📋 Select Filled", command=self._select_filled, **btn_kw).pack(side="left")

        # Grid container (Scrollable)
        grid_container = ctk.CTkScrollableFrame(self.grid_frame, fg_color="transparent")
        grid_container.pack(expand=True, fill="both")

        # A4 Sheet Simulation
        # Real A4: 210 x 297 mm
        # Scale: 3 -> Width: 630px, Height: 891px
        sheet_w = 630
        sheet_h = 891
        
        # Paper frame
        paper = ctk.CTkFrame(grid_container, width=sheet_w, height=sheet_h, fg_color="#ffffff", corner_radius=2, border_color="#cccccc", border_width=1)
        paper.pack(pady=20, padx=20)
        
        # ST-16 Label: 99.1 x 33.9 mm -> 297 x 101 px
        lbl_w = 297
        lbl_h = 101
        margin_x = 18
        margin_y = 41 # (891 - 8*101) / 2 = 41.5

        self.label_buttons = {}

        for pos in range(1, 17):
            row = (pos - 1) // COLS
            col = (pos - 1) % COLS

            lbl = self.labels_data.get(pos, {})
            bg_col, fg_col, status_border_col, status_border_w = self._label_colors(pos)
            
            if pos in self.selected_positions:
                border_color = "#89b4fa"
                border_width = 3
            else:
                border_color = status_border_col
                border_width = status_border_w

            # Wrapping in a frame to give click area
            btn_frame = ctk.CTkFrame(paper, width=lbl_w, height=lbl_h, fg_color=bg_col, corner_radius=8, 
                                     border_color=border_color, border_width=border_width)
            btn_frame.pack_propagate(False)
            
            x = margin_x + col * lbl_w
            y = margin_y + row * lbl_h
            
            btn_frame.place(x=x, y=y)
            
            # Use inner frame for layout to allow simple place/pack
            inner = tk.Frame(btn_frame, bg=bg_col)
            inner.pack(fill="both", expand=True, padx=4, pady=4)
            
            # Position badge
            pos_lbl = tk.Label(inner, text=str(pos), bg=bg_col, fg="#999999", font=("Segoe UI", 8, "bold"))
            pos_lbl.place(x=0, y=0)

            # Content preview (per-line styles)
            line_styles_dict = lbl.get("line_styles_dict", {})
            fallback_size = int(lbl.get("font_size", 10))
            fallback_bold = bool(lbl.get("bold", 0))
            fallback_align = lbl.get("alignment", "center")

            preview_lines = []
            for i in range(1, 5):
                text = lbl.get(f"line{i}", "").strip()
                if text:
                    style = line_styles_dict.get(f"line{i}", {})
                    fsize = min(16, int(style.get("font_size", fallback_size)))
                    bold = bool(style.get("bold", fallback_bold))
                    align = style.get("alignment", fallback_align)
                    preview_lines.append((text, fsize, bold, align))

            if not preview_lines:
                content_lbl = tk.Label(inner, text="Double-click to edit...", bg=bg_col, fg="#cccccc",
                                        font=("Segoe UI", 10, "italic"), wraplength=260, justify="center")
                content_lbl.pack(expand=True, fill="both")
            else:
                # Pack an inner container to center vertically
                v_center = tk.Frame(inner, bg=bg_col)
                v_center.pack(expand=True, fill="both")
                # Add flexible space above
                tk.Frame(v_center, bg=bg_col).pack(expand=True, fill="both")
                
                for text, fsize, bold, align in preview_lines:
                    font_cfg = ("Segoe UI", fsize, "bold") if bold else ("Segoe UI", fsize)
                    justify_map = {"left": "w", "center": "center", "right": "e"}
                    anchor = justify_map.get(align, "center")
                    tk.Label(v_center, text=text, bg=bg_col, fg=fg_col,
                             font=font_cfg, wraplength=260, anchor=anchor).pack(fill="x")
                             
                # Add flexible space below
                tk.Frame(v_center, bg=bg_col).pack(expand=True, fill="both")

            status = self._label_status(pos)
            if status != "EMPTY":
                # Text Details Footer (Font Size & Alignment)
                align_icon = {"left": "⫷", "center": "≡", "right": "⫸"}.get(justify, "≡")
                bold_txt = "B " if bold else ""
                details_txt = f"{bold_txt}{font_size}pt {align_icon}"
                details_lbl = tk.Label(inner, text=details_txt, bg=bg_col, fg="#b4befe", font=("Segoe UI", 7, "bold"))
                details_lbl.place(relx=0.0, rely=1.0, anchor="sw")

            if lbl.get("printed"):
                chk = tk.Label(inner, text="✓ PRINTED", bg=bg_col, fg="#a6e3a1", font=("Segoe UI", 7, "bold"))
                chk.place(relx=1.0, rely=1.0, anchor="se")
            
            # Sub-widgets list for click binding
            sub_widgets = [btn_frame, inner, content_lbl, pos_lbl]
            if status != "EMPTY":
                sub_widgets.append(details_lbl)
            if lbl.get("printed"):
                sub_widgets.append(chk)

            # Bind clicks for all sub-widgets
            for w in sub_widgets:
                w.bind("<Button-1>", lambda e, p=pos: self._toggle_select(p))
                w.bind("<Double-Button-1>", lambda e, p=pos: self._edit_label(p))
                w.bind("<Button-3>", lambda e, p=pos: self._show_label_menu(e, p))

            self.label_buttons[pos] = btn_frame

        self._update_status()

    def _label_colors(self, pos):
        status = self._label_status(pos)
        return STATUS_COLORS.get(status, ("#ffffff", "#666666", "#e5e5e5", 1))

    def _label_status(self, pos):
        lbl = self.labels_data.get(pos, {})
        if lbl.get("printed"):
            return "PRINTED"
        has_content = any(lbl.get(f"line{i}", "").strip() for i in range(1, 5))
        return "FILLED" if has_content else "EMPTY"

    def _toggle_select(self, pos):
        if pos in self.selected_positions:
            self.selected_positions.discard(pos)
        else:
            self.selected_positions.add(pos)
        self._refresh_grid()

    def _show_label_menu(self, event, pos):
        if not self.current_sheet_id:
            return
        class CTkPopupMenu(ctk.CTkToplevel):
            def __init__(self, master, x, y, commands):
                super().__init__(master)
                self.overrideredirect(True)
                self.geometry(f"+{x}+{y}")
                self.attributes("-topmost", True)
                
                self.frame = ctk.CTkFrame(self, corner_radius=6, border_width=1, border_color="#313244", fg_color="#1e1e2e")
                self.frame.pack(fill="both", expand=True)

                for text, cmd in commands:
                    if text == "-":
                        ctk.CTkFrame(self.frame, height=1, fg_color="#313244").pack(fill="x", padx=10, pady=2)
                    else:
                        btn = ctk.CTkButton(self.frame, text=text, fg_color="transparent", corner_radius=4,
                                            text_color="#cdd6f4", anchor="w", font=("Segoe UI", 12),
                                            hover_color="#313244", command=lambda c=cmd: self._execute(c))
                        btn.pack(fill="x", padx=4, pady=2)

                self.bind("<FocusOut>", lambda e: self.destroy())
                
            def _execute(self, cmd):
                self.destroy()
                cmd()

        commands = [
            ("✏ Edit Label", lambda: self._edit_label(pos)),
            ("🧹 Clear Label", lambda: self._clear_label(pos)),
            ("-", None),
            ("☑ Toggle Select", lambda: self._toggle_select(pos))
        ]
        
        # Destroy any existing popup
        if hasattr(self, "_active_popup") and self._active_popup.winfo_exists():
            self._active_popup.destroy()
            
        self._active_popup = CTkPopupMenu(self, event.x_root, event.y_root, commands)
        self._active_popup.after(50, self._active_popup.focus_set)

    def _clear_label(self, pos):
        if not self.current_sheet_id:
            return
        self.labels_data[pos] = {
            "position": pos,
            "line1": "", "line2": "", "line3": "", "line4": "",
            "font_size": 10, "bold": 0, "alignment": "center", "printed": 0,
        }
        db.save_label(self.current_sheet_id, pos, "", "", "", "", 10, 0, "center")
        self._refresh_grid()
        self._set_status(f"Label {pos} cleared.")

    def _refresh_grid(self):
        if not self.current_sheet_id:
            return
        self._build_grid()

    def _select_empty(self):
        self.selected_positions = {p for p in range(1, 17) if self._label_status(p) == "EMPTY"}
        self._refresh_grid()

    def _select_filled(self):
        self.selected_positions = {p for p in range(1, 17) if self._label_status(p) == "FILLED"}
        self._refresh_grid()

    def _deselect_all(self):
        self.selected_positions.clear()
        self._refresh_grid()

    # ──────────────────────────────────────────────────────────────────────────
    # SHEET OPERATIONS
    # ──────────────────────────────────────────────────────────────────────────
    def _show_welcome(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        
        frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame, text="🏷", text_color="#89b4fa", font=ctk.CTkFont("Segoe UI", 64)).pack()
        ctk.CTkLabel(frame, text="Smart Label Printer", font=ctk.CTkFont("Segoe UI", 28, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(frame, text="ST-16 A4 Label Sheet Manager for Laser, Inkjet & Copier", text_color="gray", font=ctk.CTkFont("Segoe UI", 14)).pack()
        ctk.CTkLabel(frame, text="Create a new sheet or open an existing one to get started.", text_color="gray", font=ctk.CTkFont("Segoe UI", 12)).pack(pady=(20, 30))
        
        ctk.CTkButton(frame, text="＋ Create New Sheet", command=self._new_sheet, font=ctk.CTkFont("Segoe UI", 14, "bold"), height=40, width=200).pack()

    def _new_sheet(self):
        name = simpledialog.askstring("New Sheet", "Enter sheet name:",
                                      parent=self, initialvalue=f"Sheet {len(db.get_all_sheets())+1}")
        if not name:
            return
        sheet_id = db.create_sheet(name.strip())
        self._load_sheet(sheet_id)
        self._set_status(f"Created new sheet: {name}")

    def _load_sheet(self, sheet_id):
        self.current_sheet_id = sheet_id
        rows = db.get_labels(sheet_id)
        self.labels_data = {r["position"]: dict(r) for r in rows}
        self.selected_positions.clear()
        sheet = db.get_sheet(sheet_id)
        self.sheet_name_lbl.configure(text=f"📄  {sheet['name']}  (ID #{sheet_id})")
        self._build_grid()
        self._refresh_sheet_list()
        self._set_status(f"Opened: {sheet['name']}")

    def _open_sheet_dialog(self):
        dlg = _OpenSheetDialog(self, on_open=self._load_sheet)

    def _save_sheet(self):
        if not self.current_sheet_id:
            CTkMessagebox(title="No Sheet", message="No sheet is currently open.", icon='info')
            return
        for pos, lbl in self.labels_data.items():
            db.save_label(
                self.current_sheet_id, pos,
                lbl.get("line1", ""), lbl.get("line2", ""),
                lbl.get("line3", ""), lbl.get("line4", ""),
                lbl.get("font_size", 10), lbl.get("bold", 0),
                lbl.get("alignment", "center"),
                lbl.get("line_styles_dict", {})
            )
        self._set_status("Sheet saved.")
        CTkMessagebox(title="Saved", message="Sheet saved successfully.", icon='info')

    def _delete_sheet(self):
        if not hasattr(self, "_sheet_list_data") or not self.current_sheet_id:
            CTkMessagebox(title="Delete", message="Open a sheet to delete it first.", icon='info')
            return
        
        sheet = db.get_sheet(self.current_sheet_id)
        msg = CTkMessagebox(title="Delete Sheet", message=f"Delete sheet '{sheet['name']}'?\nThis cannot be undone.", icon='question', option_1='No', option_2='Yes')
        if msg.get() != 'Yes':
            return
            
        db.delete_sheet(sheet["id"])
        self.current_sheet_id = None
        self.labels_data = {}
        self.sheet_name_lbl.configure(text="No sheet open")
        self._refresh_sheet_list()
        self._show_welcome()
        self._set_status(f"Deleted sheet: {sheet['name']}")

    # ──────────────────────────────────────────────────────────────────────────
    # LABEL EDITING
    # ──────────────────────────────────────────────────────────────────────────
    def _edit_label(self, pos):
        if not self.current_sheet_id:
            return
        lbl = self.labels_data.get(pos, {})
        LabelEditorDialog(self, pos, lbl, self._on_label_save)

    def _on_label_save(self, pos, data):
        if not self.current_sheet_id:
            return
        if pos not in self.labels_data:
            self.labels_data[pos] = {}
        self.labels_data[pos].update(data)
        db.save_label(
            self.current_sheet_id, pos,
            data["line1"], data["line2"], data["line3"], data["line4"],
            data["font_size"], data["bold"], data["alignment"],
            data.get("line_styles_dict", {})
        )
        self._refresh_grid()
        self._set_status(f"Label {pos} updated.")

    # ──────────────────────────────────────────────────────────────────────────
    # PRINTING
    # ──────────────────────────────────────────────────────────────────────────
    def _print_preview(self):
        if not self.current_sheet_id:
            CTkMessagebox(title="No Sheet", message="Open a sheet first.", icon='info')
            return
        labels = list(self.labels_data.values())
        labels = sorted(labels, key=lambda l: l.get("position", 0))
        print_labels = []
        for pos in range(1, 17):
            lbl = dict(self.labels_data.get(pos, {}))
            lbl["selected"] = pos in self.selected_positions
            print_labels.append(lbl)
        page_margins = {
            'margin_top': db.get_setting("margin_top", 10),
            'margin_bottom': db.get_setting("margin_bottom", 10),
            'margin_left': db.get_setting("margin_left", 10),
            'margin_right': db.get_setting("margin_right", 10)
        }
        from ui.preview import PrintPreviewWindow
        PrintPreviewWindow(self, print_labels, list(self.selected_positions), page_margins=page_margins)

    def _print_selected(self):
        if not self.current_sheet_id:
            CTkMessagebox(title="No Sheet", message="Open a sheet first.", icon='info')
            return
        if not self.selected_positions:
            CTkMessagebox(title="No Selection", message="Select one or more labels to print.\nClick a label to select it.", icon='info')
            return

        already_printed = [p for p in self.selected_positions if self.labels_data.get(p, {}).get("printed")]
        if already_printed:
            positions_str = ", ".join(str(p) for p in sorted(already_printed))
            msg = CTkMessagebox(title="⚠ Already Printed", message=f"Label(s) {positions_str} have already been printed.\n\nDo you want to reprint them?", icon='question', option_1='No', option_2='Yes')
            if msg.get() != 'Yes':
                self.selected_positions -= set(already_printed)
                self._refresh_grid()
                if not self.selected_positions:
                    return

        print_labels = []
        for pos in range(1, 17):
            lbl = dict(self.labels_data.get(pos, {}))
            lbl["selected"] = pos in self.selected_positions
            print_labels.append(lbl)

        page_margins = {
            'margin_top': db.get_setting("margin_top", 10),
            'margin_bottom': db.get_setting("margin_bottom", 10),
            'margin_left': db.get_setting("margin_left", 10),
            'margin_right': db.get_setting("margin_right", 10)
        }

        ok, msg = print_service.print_labels(print_labels, page_margins=page_margins)

        if ok:
            for pos in self.selected_positions:
                db.mark_printed(self.current_sheet_id, pos)
                if pos in self.labels_data:
                    self.labels_data[pos]["printed"] = 1

            CTkMessagebox(title="Print", message=msg, icon='info')
            self.selected_positions.clear()
            self._refresh_grid()
            self._set_status(f"Printed {len(self.selected_positions)} labels.")
        else:
            CTkMessagebox(title="Print Error", message=f"Printing failed:\n{msg}", icon='cancel')

    def _download_pdf(self):
        if not self.current_sheet_id:
            CTkMessagebox(title="No Sheet", message="Open a sheet first.", icon='info')
            return
        if not self.selected_positions:
            CTkMessagebox(title="No Selection", message="Select one or more labels to download.\nClick a label to select it.", icon='info')
            return

        sheet = db.get_sheet(self.current_sheet_id)
        suggested_name = f"{sheet['name'].replace(' ', '_')}_Labels.pdf"

        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf")],
            initialfile=suggested_name,
            title="Download PDF"
        )
        if not path:
            return
            
        print_labels = []
        for pos in range(1, 17):
            lbl = dict(self.labels_data.get(pos, {}))
            lbl["selected"] = pos in self.selected_positions
            print_labels.append(lbl)

        try:
            page_margins = {
                'margin_top': db.get_setting("margin_top", 10),
                'margin_bottom': db.get_setting("margin_bottom", 10),
                'margin_left': db.get_setting("margin_left", 10),
                'margin_right': db.get_setting("margin_right", 10)
            }
            print_service.build_pdf(print_labels, path, page_margins=page_margins)
            
            # Optionally mark as printed since they exported it
            for pos in self.selected_positions:
                db.mark_printed(self.current_sheet_id, pos)
                if pos in self.labels_data:
                    self.labels_data[pos]["printed"] = 1
                    
            self.selected_positions.clear()
            self._refresh_grid()
            
            CTkMessagebox(title="Downloaded", message=f"PDF saved successfully:\n{path}", icon='info')
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to generate PDF:\n{str(e)}", icon='cancel')

    # ──────────────────────────────────────────────────────────────────────────
    # BACKUP / RESTORE / SETTINGS
    # ──────────────────────────────────────────────────────────────────────────
    def _backup(self):
        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".db",
            filetypes=[("SQLite DB", "*.db")],
            initialfile="backup.db",
            title="Save Backup As"
        )
        if path:
            try:
                backup_service.backup_database(path)
                CTkMessagebox(title="Backup", message=f"Backup saved:\n{path}", icon='info')
            except Exception as e:
                CTkMessagebox(title="Backup Error", message=str(e), icon='cancel')

    def _restore(self):
        path = filedialog.askopenfilename(
            parent=self, filetypes=[("SQLite DB", "*.db")],
            title="Select Backup File to Restore"
        )
        if path:
            msg = CTkMessagebox(title="Restore", message="Restore will OVERWRITE the current database.\nContinue?", icon='question', option_1='No', option_2='Yes')
            if msg.get() == 'Yes':
                try:
                    backup_service.restore_database(path)
                    CTkMessagebox(title="Restored", message="Database restored. Restarting application...", icon='info')
                    self.destroy()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                except Exception as e:
                    CTkMessagebox(title="Restore Error", message=str(e), icon='cancel')

    def _open_settings(self):
        SettingsDialog(self)

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _set_status(self, text):
        self.status_bar.configure(text=f"  {text}")

    def _update_status(self):
        if not self.current_sheet_id:
            return
        total = 16
        printed = sum(1 for p in range(1, 17) if self.labels_data.get(p, {}).get("printed"))
        filled = sum(1 for p in range(1, 17) if self._label_status(p) == "FILLED")
        empty = total - printed - filled
        self._set_status(
            f"Sheet #{self.current_sheet_id}  |  Empty: {empty}  Filled: {filled}  Printed: {printed}  |  Selected: {len(self.selected_positions)}"
        )


class _OpenSheetDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_open):
        super().__init__(parent)
        self.title("Open Sheet")
        self.geometry("600x450")
        self.resizable(True, True)
        self.grab_set()
        self.on_open = on_open
        self._build()
        self._center()

    def _build(self):
        ctk.CTkLabel(self, text="📂  Open Sheet", font=ctk.CTkFont("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 10))

        # Search
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(sf, text="Search:", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh())
        ctk.CTkEntry(sf, textvariable=self.search_var, font=ctk.CTkFont("Segoe UI", 12)).pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Treeview (Since ctk doesn't have a data grid yet, fallback to ttk Treeview styled cleanly)
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        cols = ("ID", "Name", "Created", "Updated", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2a2a2a", foreground="white", fieldbackground="#2a2a2a", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#1a1a1a", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#89b4fa")], foreground=[("selected", "#1e1e2e")])

        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Created", width=100)
        self.tree.column("Updated", width=100)
        self.tree.column("Status", width=80)

        sb = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-Button-1>", self._open)

        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(bf, text="Cancel", command=self.destroy, fg_color="transparent", border_width=1, text_color=("gray10", "gray90")).pack(side="right", padx=(10, 0))
        ctk.CTkButton(bf, text="📂 Open Selected", command=self._open, font=ctk.CTkFont("Segoe UI", 12, "bold")).pack(side="right")

        self._refresh()

    def _refresh(self):
        q = self.search_var.get().strip()
        sheets = db.search_sheets(q) if q else db.get_all_sheets()
        self.tree.delete(*self.tree.get_children())
        for s in sheets:
            created = s["created_at"][:10] if s["created_at"] else ""
            updated = s["updated_at"][:10] if s["updated_at"] else ""
            self.tree.insert("", "end", iid=str(s["id"]), values=(s["id"], s["name"], created, updated, s["status"]))

    def _open(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        sheet_id = int(sel[0])
        self.destroy()
        self.on_open(sheet_id)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = 600, 450
        self.geometry(f"+{max(0, pw-w//2)}+{max(0, ph-h//2)}")
