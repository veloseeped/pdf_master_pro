import tkinter as tk
from tkinter import messagebox, ttk
from ui.styles import *
from ui.extractor_tab import ExtractorTab
from ui.merge_tab import MergeTab
from ui.editor_tab import EditorTab
from ui.transform_tab import TransformTab
from core.processor import PdfProcessor
from utils.messages import get_msg
from utils.constants import APP_TITLE, APP_GEOMETRY

class PdfProApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE) 
        self.root.geometry(APP_GEOMETRY) 
        self.processor = PdfProcessor(self)

        # Виджеты прогресса
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=10, side=tk.BOTTOM)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # SRP: Каждая вкладка — отдельный класс
        self.tabs = {
            "extractor": ExtractorTab(self.notebook, self.processor),
            "merge": MergeTab(self.notebook, self.processor),
            "editor": EditorTab(self.notebook, self.processor),
            "transform": TransformTab(self.notebook, self.processor)
        }
        
        for key, tab_obj in self.tabs.items():
            self.notebook.add(tab_obj, text=get_msg(f"tab_{key}")) 

    def safe_message(self, type_, title, message):
        """Потокобезопасный вызов сообщений."""
        func = getattr(messagebox, f"show{type_}")
        self.root.after(0, lambda: func(title, message))
    
    def update_progress(self, value, maximum=None):
        """Обновление прогресс-бара."""
        def _update():
            if maximum is not None: self.progress["maximum"] = maximum
            self.progress["value"] = value
        self.root.after(0, _update)
