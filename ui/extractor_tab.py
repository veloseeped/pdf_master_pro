import os
import tkinter as tk
from tkinter import ttk
from ui.base_tab import BasePdfTab
from ui.styles import *
from utils.messages import get_msg

class ExtractorTab(BasePdfTab):
    def __init__(self, master, processor):
        super().__init__(master, processor)
        self.ext_source = tk.StringVar()
        self.ext_dest = tk.StringVar()
        self.block_entries = []
        
        # Следим за изменением пути, чтобы обновить имена файлов (DRY)
        self.ext_source.trace_add("write", self._update_block_names)
        self._setup_ui()

    def _setup_ui(self):
        # Секция настроек путей
        top = tk.LabelFrame(self, text=f" {get_msg('label_file_prefix')} ", padx=FRAME_PADDING, pady=FRAME_PADDING)
        top.pack(fill="x", padx=15, pady=10)
        
        self._create_path_row(top, "label_source_pdf", self.ext_source, "file")
        self._create_path_row(top, "label_save_dir", self.ext_dest, "dir")

        tk.Label(self, text=get_msg("label_block_composition")).pack(anchor="w", padx=TAB_PADDING)
        
        # --- Шапка таблицы ---
        header_row = tk.Frame(self)
        header_row.pack(fill="x", padx=TAB_PADDING, pady=(5, 0))
        
        # Отступ под индекс строки (выравнивание с Label "1:") 
        tk.Label(header_row, text="", width=4).pack(side="left") 
        
        # Заголовки (ширина подобрана под размеры Entry и Checkbutton) 
        tk.Label(header_row, text="Страницы", width=15, font=FONT_SMALL_BOLD, anchor="w").pack(side="left", padx=2)
        tk.Label(header_row, text="Исключить", width=12, font=FONT_SMALL_BOLD, anchor="w").pack(side="left")
        tk.Label(header_row, text="Имя файла", font=FONT_SMALL_BOLD, anchor="w").pack(side="left", padx=5)
        # ---------------------
        # Контейнер для списка блоков со скроллом
        list_container = tk.Frame(self)
        list_container.pack(fill="both", expand=True, padx=TAB_PADDING, pady=5)

        self.canvas = tk.Canvas(list_container, highlightthickness=0)
        sb = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Кнопки управления блоками
        btn_f = tk.Frame(self)
        btn_f.pack(fill="x", padx=TAB_PADDING, pady=10)
        
        tk.Button(btn_f, text=get_msg("btn_add_block"), fg=COLOR_ADD, 
                  font=FONT_SMALL_BOLD, command=self.add_block_field).pack(side="left")
        tk.Button(btn_f, text=get_msg("btn_clear_all"), command=self.clear_blocks).pack(side="left", padx=10)
        
        tk.Button(self, text=get_msg("btn_extract_run"), bg=COLOR_EXTRACT, 
                  fg="white", font=FONT_BOLD, command=self._run_extractor).pack(pady=10)
        
        self.add_block_field()

    def add_block_field(self):
        """Добавляет новую строку для ввода страниц и имени файла."""
        row = tk.Frame(self.scrollable_frame)
        row.pack(fill="x", pady=2, expand=True)
        
        idx = len([r for r in self.block_entries if r.winfo_exists()]) + 1
        tk.Label(row, text=f"{idx}:", width=3).pack(side="left")
        
        ent_pages = tk.Entry(row, width=15)
        ent_pages.pack(side="left", padx=2)

        # Переключатель режима: False = Извлечь, True = Исключить
        exclude_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(row, variable=exclude_var)
        cb.pack(side="left", padx=(42, 42))
        cb.exclude_var = exclude_var # Сохраняем ссылку в объекте строки

        ent_name = tk.Entry(row)
        ent_name.pack(side="left", fill="x", expand=True, padx=5)
        
        # Дефолтное имя
        source_path = self.ext_source.get()
        base = os.path.basename(source_path) if source_path else ""
        prefix = os.path.splitext(base)[0] if base else "Document"
        ent_name.insert(0, f"{prefix}_part_{idx}")
        
        self.block_entries.append(row)
        self.canvas.yview_moveto(1.0)

    def clear_blocks(self):
        for r in self.block_entries: r.destroy()
        self.block_entries = []
        self.add_block_field()

    def _update_block_names(self, *args):
        """Обновляет имена файлов в блоках при изменении исходного PDF."""
        source_path = self.ext_source.get()
        if not source_path: 
            return

        base_name = os.path.splitext(os.path.basename(source_path))[0]
        
        for i, row in enumerate(self.block_entries):
            if not row.winfo_exists(): 
                continue
            
            # В каждой строке (row) виджеты упакованы так: [Label, Entry(pages), Entry(name)]
            children = row.winfo_children()
            if len(children) >= 3:
                ent_name = children[3]  # Поле ввода имени файла 
                current_val = ent_name.get()
                new_default = f"{base_name}_part_{i+1}"
                # Обновляем имя только если оно пустое или содержит старый шаблон "_part_"
                if not current_val or "_part_" in current_val:
                    ent_name.delete(0, tk.END)
                    ent_name.insert(0, new_default)


    def _run_extractor(self):
        """Собирает данные из динамических полей и запускает процесс."""
        from utils.constants import ERR_PATHS_REQUIRED, ERR_PAGES_REQUIRED
        
        source = self.ext_source.get()
        dest = self.ext_dest.get()
        
        # Guard Clauses: Проверка путей
        if not source or not dest:
            return self.processor.app.safe_message("warning", "Внимание", ERR_PATHS_REQUIRED)
        
        configs = []
        for row in self.block_entries:
            if not row.winfo_exists(): continue
            children = row.winfo_children()
            #  1-Entry(pages), 2-Checkbutton, 3-Entry(name)
            pages = children[1].get().strip()
            exclude_mode = children[2].exclude_var.get()
            name = children[3].get().strip()
            if pages:
                configs.append((pages, name, exclude_mode))
        
        # Проверка наличия задач
        if not configs:
            return self.processor.app.safe_message("warning", "Внимание", ERR_PAGES_REQUIRED)
            
        self.processor.process_extraction(source, dest, configs)