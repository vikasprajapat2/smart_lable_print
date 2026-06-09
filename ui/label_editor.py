import tkinter as tk
# pyrefly: ignore [missing-import]
import customtkinter as ctk

class LabelEditorDialog(ctk.CTkToplevel):
    def __init__(self, parent, position, label_data, on_save):
        super().__init__(parent)
        self.title(f"Edit Label #{position}")
        self.resizable(False, False)
        self.geometry("450x450")
        
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
        for i in range(1, 5):
            row = ctk.CTkFrame(lines_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"Line {i}:", width=60, anchor="w", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
            
            var = tk.StringVar(value=label_data.get(f"line{i}", ""))
            entry = ctk.CTkEntry(row, textvariable=var, font=ctk.CTkFont("Segoe UI", 12))
            entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
            self.line_vars.append(var)
            
            if i == 1:
                entry.focus_set()

        # Formatting
        fmt_frame = ctk.CTkFrame(self, fg_color="transparent")
        fmt_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Font size
        ctk.CTkLabel(fmt_frame, text="Font Size:", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
        self.font_size_var = tk.StringVar(value=str(int(label_data.get("font_size", 10))))
        size_entry = ctk.CTkEntry(fmt_frame, textvariable=self.font_size_var, width=50, font=ctk.CTkFont("Segoe UI", 12))
        size_entry.pack(side="left", padx=(10, 20))

        # Bold
        self.bold_var = ctk.BooleanVar(value=bool(label_data.get("bold", 0)))
        bold_cb = ctk.CTkCheckBox(fmt_frame, text="Bold", variable=self.bold_var, font=ctk.CTkFont("Segoe UI", 12))
        bold_cb.pack(side="left", padx=(0, 20))

        # Alignment
        ctk.CTkLabel(fmt_frame, text="Align:", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        self.align_var = ctk.StringVar(value=label_data.get("alignment", "center"))
        align_opt = ctk.CTkOptionMenu(fmt_frame, variable=self.align_var, values=["left", "center", "right"], width=100, font=ctk.CTkFont("Segoe UI", 12))
        align_opt.pack(side="left")

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
        w, h = 450, 450
        self.geometry(f"+{pw - w//2}+{ph - h//2}")

    def _clear(self):
        for v in self.line_vars:
            v.set("")

    def _save(self):
        try:
            fsize = int(self.font_size_var.get())
        except ValueError:
            fsize = 10

        data = {
            "line1": self.line_vars[0].get(),
            "line2": self.line_vars[1].get(),
            "line3": self.line_vars[2].get(),
            "line4": self.line_vars[3].get(),
            "font_size": fsize,
            "bold": 1 if self.bold_var.get() else 0,
            "alignment": self.align_var.get(),
        }
        self.on_save(self.position, data)
        self.destroy()
