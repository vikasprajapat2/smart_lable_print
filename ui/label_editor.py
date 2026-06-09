import tkinter as tk
# pyrefly: ignore [missing-import]
import customtkinter as ctk

class LabelEditorDialog(ctk.CTkToplevel):
    def __init__(self, parent, position, label_data, on_save):
        super().__init__(parent)
        self.title(f"Edit Label #{position}")
        self.resizable(False, False)
        self.geometry("650x450")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        self.on_save = on_save
        self.position = position

        # Title
        title_lbl = ctk.CTkLabel(self, text=f"✏  Label {position}", font=ctk.CTkFont("Segoe UI", 18, "bold"))
        title_lbl.pack(anchor="w", padx=20, pady=(20, 10))

        # Line entries
        lines_frame = ctk.CTkFrame(self, fg_color="transparent")
        lines_frame.pack(fill="x", padx=20)

        self.line_vars = []
        self.line_styles = [] # list of (size_var, bold_var, align_var) tuples

        # Parse existing line styles or fallback
        line_styles_dict = label_data.get("line_styles_dict", {})
        fallback_size = int(label_data.get("font_size", 10))
        fallback_bold = bool(label_data.get("bold", 0))
        fallback_align = label_data.get("alignment", "center")

        for i in range(1, 5):
            line_key = f"line{i}"
            style = line_styles_dict.get(line_key, {})
            
            row = ctk.CTkFrame(lines_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            ctk.CTkLabel(row, text=f"Line {i}:", width=50, anchor="w", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
            
            var = tk.StringVar(value=label_data.get(line_key, ""))
            entry = ctk.CTkEntry(row, textvariable=var, width=150, font=ctk.CTkFont("Segoe UI", 12))
            entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
            self.line_vars.append(var)
            
            if i == 1:
                entry.focus_set()

            # Formatting Controls for this line
            ctk.CTkLabel(row, text="Size:", font=ctk.CTkFont("Segoe UI", 11)).pack(side="left")
            size_var = tk.StringVar(value=str(style.get("font_size", fallback_size)))
            size_entry = ctk.CTkEntry(row, textvariable=size_var, width=40, font=ctk.CTkFont("Segoe UI", 11))
            size_entry.pack(side="left", padx=(5, 15))

            bold_var = ctk.BooleanVar(value=bool(style.get("bold", fallback_bold)))
            bold_cb = ctk.CTkCheckBox(row, text="B", variable=bold_var, width=30, font=ctk.CTkFont("Segoe UI", 11, "bold"))
            bold_cb.pack(side="left", padx=(0, 15))

            align_var = ctk.StringVar(value=style.get("alignment", fallback_align))
            align_opt = ctk.CTkOptionMenu(row, variable=align_var, values=["left", "center", "right"], width=80, font=ctk.CTkFont("Segoe UI", 11))
            align_opt.pack(side="left")

            self.line_styles.append((size_var, bold_var, align_var))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        clear_btn = ctk.CTkButton(btn_frame, text="🗑 Clear", command=self._clear, fg_color="#f38ba8", text_color="#1e1e2e", hover_color="#eba0b5", width=80, font=ctk.CTkFont("Segoe UI", 12, "bold"))
        clear_btn.pack(side="left")

        save_btn = ctk.CTkButton(btn_frame, text="💾 Save", command=self._save, width=100, font=ctk.CTkFont("Segoe UI", 12, "bold"))
        save_btn.pack(side="right")

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), width=80, font=ctk.CTkFont("Segoe UI", 12))
        cancel_btn.pack(side="right", padx=10)

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

        self._center()

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = 650, 400
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _clear(self):
        for v in self.line_vars:
            v.set("")

    def _save(self):
        line_styles_dict = {}
        for i in range(4):
            sz_var, b_var, a_var = self.line_styles[i]
            try:
                fsize = int(sz_var.get())
            except ValueError:
                fsize = 10
            line_styles_dict[f"line{i+1}"] = {
                "font_size": fsize,
                "bold": 1 if b_var.get() else 0,
                "alignment": a_var.get()
            }

        data = {
            "line1": self.line_vars[0].get(),
            "line2": self.line_vars[1].get(),
            "line3": self.line_vars[2].get(),
            "line4": self.line_vars[3].get(),
            "font_size": line_styles_dict["line1"]["font_size"],
            "bold": line_styles_dict["line1"]["bold"],
            "alignment": line_styles_dict["line1"]["alignment"],
            "line_styles_dict": line_styles_dict
        }
        self.on_save(self.position, data)
        self.destroy()
