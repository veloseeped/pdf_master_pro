import tkinter as tk
from ui.page_preview import PagePreviewControl
from ui.base_tab import BasePdfTab
from ui.styles import *
from utils.messages import get_msg

class EditorTab(BasePdfTab):
    def __init__(self, master, processor):
        super().__init__(master, processor)
        self.ed_source = tk.StringVar()
        self.ed_pages = tk.StringVar()
        self.out_dir = self.processor.app.shared_output_dir
        self.ed_out = tk.StringVar(value=self.out_dir)
        self.ed_source.trace_add("write", lambda *a: self.preview.update_preview(self.ed_source.get()))
        self._setup_ui()

    def _setup_ui(self):
        # Выбор исходного файла
        self._create_path_row(self, "label_source_pdf", self.ed_source, "file")
        main_container = tk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=TAB_PADDING, pady=5)
        
         # Левая колонка (Настройки)
        left_frame = tk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=True)
        
        actions_frame = tk.Frame(left_frame)
        actions_frame.pack(pady=10, anchor="w")

        # Поле ввода порядка страниц
        tk.Label(self, text=get_msg("label_new_order")).pack(pady=(10,0), anchor="w")
        tk.Entry(self, textvariable=self.ed_pages).pack(fill="x", pady=5)
        
        # Результат
        tk.Label(self, text=get_msg("label_result")).pack(pady=(10,0), anchor="w")
        self._create_path_row(self, "label_save_as", self.ed_out, "save")
        
        # Кнопка запуска
        tk.Button(self, text=get_msg("btn_editor_run"), bg=COLOR_EDITOR, 
                  fg="white", font=FONT_BOLD, command=self._run_editor).pack(pady=20)
        tk.Button(actions_frame, text="РЕВЕРС СТРАНИЦ", bg="#546E7A", 
                  fg="white", font=FONT_BOLD, command=self._run_reverse).pack(side=tk.LEFT)
        
        # Правая колонка (Превью)
        self.preview = PagePreviewControl(main_container)
        self.preview.pack(side="right", fill="y", padx=(10, 0))

    def _run_editor(self):
        if not all([self.ed_source.get(), self.ed_out.get(), self.ed_pages.get()]):
            return self.processor.app.safe_message("warning", get_msg("msg_warning_title"), get_msg("err_paths_required"))
        
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
            return self.processor.app.safe_message("warning", get_msg("msg_warning_title"), get_msg("err_paths_required"))
        self.processor.process_reverse(source, out)