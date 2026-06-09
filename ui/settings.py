import tkinter as tk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import database_service as db


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.geometry("400x480")
        
        # Bring to front and make it modal
        self.transient(parent)
        self.grab_set()
        
        self._build()
        self._center()

    def _build(self):
        title_lbl = ctk.CTkLabel(self, text="⚙  Settings", font=ctk.CTkFont("Segoe UI", 20, "bold"))
        title_lbl.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Default font size
        f1 = ctk.CTkFrame(self, fg_color="transparent")
        f1.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f1, text="Default Font Size:", width=150, anchor="w", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
        
        self.font_var = tk.StringVar(value=str(db.get_setting("default_font_size", "10")))
        font_entry = ctk.CTkEntry(f1, textvariable=self.font_var, width=80, font=ctk.CTkFont("Segoe UI", 12))
        font_entry.pack(side="left", padx=10)

        # Default alignment
        f2 = ctk.CTkFrame(self, fg_color="transparent")
        f2.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f2, text="Default Alignment:", width=150, anchor="w", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
        
        self.align_var = ctk.StringVar(value=db.get_setting("default_alignment", "center"))
        align_opt = ctk.CTkOptionMenu(f2, variable=self.align_var, values=["left", "center", "right"], width=120, font=ctk.CTkFont("Segoe UI", 12))
        align_opt.pack(side="left", padx=10)

        # Margins
        ctk.CTkLabel(self, text="Page Margins (mm):", font=ctk.CTkFont("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

        self.margin_vars = {}
        for side in ["top", "bottom", "left", "right"]:
            f = ctk.CTkFrame(self, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=f"Margin {side.capitalize()}:", width=150, anchor="w", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
            
            var = tk.StringVar(value=str(db.get_setting(f"margin_{side}", "10")))
            self.margin_vars[side] = var
            entry = ctk.CTkEntry(f, textvariable=var, width=80, font=ctk.CTkFont("Segoe UI", 12))
            entry.pack(side="left", padx=10)

        # Buttons
        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(fill="x", side="bottom", pady=20, padx=20)
        
        save_btn = ctk.CTkButton(bf, text="💾 Save Settings", command=self._save, font=ctk.CTkFont("Segoe UI", 12, "bold"))
        save_btn.pack(side="right")
        
        cancel_btn = ctk.CTkButton(bf, text="Cancel", command=self.destroy, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), font=ctk.CTkFont("Segoe UI", 12))
        cancel_btn.pack(side="right", padx=10)

    def _save(self):
        try:
            db.set_setting("default_font_size", int(self.font_var.get()))
            db.set_setting("default_alignment", self.align_var.get())
            for side, var in self.margin_vars.items():
                db.set_setting(f"margin_{side}", int(var.get()))
            self.destroy()
        except ValueError:
            CTkMessagebox(title="Invalid Input", message="Please enter valid integers for font size and margins.", icon='cancel')

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_rootx() + self.master.winfo_width() // 2
        ph = self.master.winfo_rooty() + self.master.winfo_height() // 2
        w, h = 400, 480
        self.geometry(f"+{pw - w//2}+{ph - h//2}")
