import tkinter as tk
from ui.base_tab import BasePdfTab
from ui.styles import *
from utils.constants import ERR_ALL_PATHS_REQUIRED
from utils.messages import get_msg

class EditorTab(BasePdfTab):
    def __init__(self, master, processor):
        super().__init__(master, processor)
        self.ed_source = tk.StringVar()
        self.ed_pages = tk.StringVar()
        self.ed_out = tk.StringVar()
        self._setup_ui()

    def _setup_ui(self):
        # Выбор исходного файла
        self._create_path_row(self, "label_source_pdf", self.ed_source, "file")
        actions_frame = tk.Frame(self)
        actions_frame.pack(pady=10)        
        # Поле ввода порядка страниц
        tk.Label(self, text=get_msg("label_new_order")).pack(padx=TAB_PADDING, pady=(10,0), anchor="w")
        tk.Entry(self, textvariable=self.ed_pages).pack(fill="x", padx=TAB_PADDING, pady=5)
        
        # Результат
        tk.Label(self, text=get_msg("label_result")).pack(padx=TAB_PADDING, pady=(10,0), anchor="w")
        self._create_path_row(self, "label_save_as", self.ed_out, "save")
        
        # Кнопка запуска
        tk.Button(self, text=get_msg("btn_editor_run"), bg=COLOR_EDITOR, 
                  fg="white", font=FONT_BOLD, command=self._run_editor).pack(pady=20)
        tk.Button(actions_frame, text="РЕВЕРС СТРАНИЦ", bg="#546E7A", 
                  fg="white", font=FONT_BOLD, command=self._run_reverse).pack(side=tk.LEFT, padx=5)

    def _run_editor(self):
        if not all([self.ed_source.get(), self.ed_out.get(), self.ed_pages.get()]):
            return self.processor.app.safe_message("warning", "Внимание", ERR_ALL_PATHS_REQUIRED)
        
        self.processor.process_editor(
            self.ed_source.get(), 
            self.ed_out.get(), 
            self.ed_pages.get()
        )
    
    def _run_reverse(self):
        """Валидация и запуск реверса."""
        source = self.ed_source.get()
        out = self.ed_out.get()
        
        if not all([source, out]):
            return self.processor.app.safe_message("warning", "Внимание", ERR_ALL_PATHS_REQUIRED)
        self.processor.process_reverse(source, out)