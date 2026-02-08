import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES
from utils.parser import clean_path
from utils.messages import get_msg

class BasePdfTab(ttk.Frame):
    def __init__(self, master, processor):
        super().__init__(master)
        self.processor = processor

    def _create_path_row(self, master, label_key, var, mode):
        """Унифицированный метод создания строки выбора пути (DRY)."""
        row = tk.Frame(master)
        row.pack(fill="x", pady=5)
        
        tk.Label(row, text=get_msg(label_key), width=15, anchor="w").pack(side=tk.LEFT)
        ent = tk.Entry(row, textvariable=var)
        ent.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Регистрация DND 
        ent.drop_target_register(DND_FILES)
        ent.dnd_bind('<<Drop>>', lambda e: var.set(clean_path(e.data)))
        
        tk.Button(row, text=get_msg("btn_browse"), 
                  command=lambda: self._browse(var, mode)).pack(side=tk.RIGHT)

    def _browse(self, var, mode):
        """Общая логика диалогов выбора[cite: 48]."""
        if mode == "file":
            p = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        elif mode == "dir":
            p = filedialog.askdirectory()
        elif mode == "save":
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        
        if p: var.set(p)