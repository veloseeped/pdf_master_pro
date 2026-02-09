import tkinter as tk
from tkinterdnd2 import DND_FILES
from ui.base_tab import BasePdfTab
from ui.styles import *
from utils.parser import clean_path
from utils.messages import get_msg

class MergeTab(BasePdfTab):
    def __init__(self, master, processor):
        super().__init__(master, processor)
        self.out_dir = self.processor.app.shared_output_dir
        self.merge_out = tk.StringVar(value=self.out_dir)
        self._setup_ui()
        

    def _setup_ui(self):
        tk.Label(self, text=get_msg("label_file_list")).pack(pady=5, anchor="w", padx=TAB_PADDING)
        
        # Список файлов
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=TAB_PADDING)
        
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.listbox.pack(side=tk.LEFT, fill="both", expand=True)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self._handle_drop)
        
        # Кнопки управления
        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(side=tk.RIGHT, fill="y", padx=(10, 0))
        
        # DRY: Использование словаря для генерации кнопок
        actions = [
            ("btn_add_file", self._add_file_manual),
            ("btn_up", self._move_up),
            ("btn_down", self._move_down),
            ("btn_remove", self._remove_from_list),
            ("btn_clear", self._clear_list)
        ]
        for msg_key, cmd in actions:
            tk.Button(btn_frame, text=get_msg(msg_key), command=cmd).pack(fill="x", pady=2)

        # Путь сохранения
        self._create_path_row(self, "label_save_as", self.merge_out, "save")
        
        tk.Button(self, text=get_msg("btn_merge_run"), bg=COLOR_MERGE, 
                  fg="white", font=FONT_BOLD, command=self._run_merge).pack(pady=10)

    def _handle_drop(self, event):
        for f in self.tk.splitlist(event.data):
            cp = clean_path(f)
            if cp.lower().endswith('.pdf'): 
                self.listbox.insert(tk.END, cp) 

    def _add_file_manual(self):
        """Выбор файла через диалоговое окно."""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if files:
            for f in files:
                self.listbox.insert(tk.END, f)

    def _move_up(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == 0: 
            return
        v = self.listbox.get(idx[0])
        self.listbox.delete(idx[0]) 
        self.listbox.insert(idx[0]-1, v)
        self.listbox.selection_set(idx[0]-1)

    def _move_down(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == self.listbox.size()-1: 
            return
        v = self.listbox.get(idx[0])
        self.listbox.delete(idx[0]); self.listbox.insert(idx[0]+1, v)
        self.listbox.selection_set(idx[0]+1)

    def _remove_from_list(self):
        selected_indices = self.listbox.curselection()
        for i in reversed(selected_indices): 
            self.listbox.delete(i)

    def _clear_list(self): 
        
        self.listbox.delete(0, tk.END) 

    def _run_merge(self):
        files = self.listbox.get(0, tk.END)
        out = self.merge_out.get()
        if len(files) < 2 or not out:
            return self.processor.app.safe_message(
                "warning", 
                get_msg("msg_warning_title"), 
                get_msg("err_merge_required")
            )
        self.processor.process_merge(files, out) 