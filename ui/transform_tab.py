import tkinter as tk
from ui.base_tab import BasePdfTab
from ui.styles import *
from utils.constants import ERR_ALL_PATHS_REQUIRED
from utils.messages import get_msg


class TransformTab(BasePdfTab):
    def __init__(self, master, processor):
        super().__init__(master, processor)
        
        self.ROT_MAP = {
            "90 градусов": "90",
            "180 градусов": "180",
            "270 градусов": "270",
            "Против часовой (-90)": "-90"
        }
        self.MIR_MAP = {
            "По горизонтали (слева направо)": "h",
            "По вертикали (сверху вниз)": "v"
        }

        self.src = tk.StringVar()
        self.out_dir = self.processor.app.shared_output_dir
        self.out = tk.StringVar(value=self.out_dir)
        self.pages = tk.StringVar()
        self.action = tk.StringVar(value="rotate")
        self.rot_val = tk.StringVar(value=list(self.ROT_MAP.keys())[0])
        self.mir_val = tk.StringVar(value=list(self.MIR_MAP.keys())[0])
        
        
        # Добавляем отслеживание изменения выбора
        self.action.trace_add("write", self._update_menu_states)
        
        self._setup_ui()
        # Устанавливаем начальное состояние при запуске
        self._update_menu_states()


    def _update_menu_states(self, *args):
        """Актуализирует доступность выпадающих списков в зависимости от выбранного действия."""
        current_action = self.action.get()
        
        if current_action == "rotate":
            self.rot_menu.config(state="normal")
            self.mir_menu.config(state="disabled")
        elif current_action == "mirror":
            self.rot_menu.config(state="disabled")
            self.mir_menu.config(state="normal")

    def _setup_ui(self):
        # Строки выбора файлов (используют .pack() внутри базового класса)
        self._create_path_row(self, "label_source_pdf", self.src, "file")
        
        # Настройки трансформации
        cfg_frame = tk.LabelFrame(self, text=" Настройки трансформации ", padx=10, pady=10)
        cfg_frame.pack(fill="x", padx=20, pady=10)
        
        # Сетка (Grid) внутри фрейма
        tk.Label(cfg_frame, text="Страницы (1, 3-5):").grid(row=0, column=0, sticky="w")
        
        # ИСПРАВЛЕНО: удален fill="x", добавлено sticky="ew"
        tk.Entry(cfg_frame, textvariable=self.pages).grid(row=0, column=1, sticky="ew", padx=5)
        
        # Настройка веса колонки, чтобы Entry мог растягиваться
        cfg_frame.grid_columnconfigure(1, weight=1)
        
        # Тип действия
        # Поворот
        tk.Radiobutton(cfg_frame, text="Поворот", variable=self.action, value="rotate").grid(row=1, column=0, sticky="w")
        self.rot_menu = tk.OptionMenu(cfg_frame, self.rot_val, *self.ROT_MAP.keys())
        self.rot_menu.grid(row=1, column=1, sticky="w")

        # Отражение
        tk.Radiobutton(cfg_frame, text="Отражение", variable=self.action, value="mirror").grid(row=2, column=0, sticky="w")
        self.mir_menu = tk.OptionMenu(cfg_frame, self.mir_val, *self.MIR_MAP.keys())
        self.mir_menu.grid(row=2, column=1, sticky="w")

        # Строка сохранения (снова .pack() через базовый класс)
        self._create_path_row(self, "label_save_as", self.out, "save")
        
        tk.Button(self, text="Создать новый PDF", bg=COLOR_MERGE, fg="white", 
                  font=FONT_BOLD, command=self._run).pack(pady=20)

    def _run(self):
        if not all([self.src.get(), self.out.get(), self.pages.get()]):
            return self.processor.app.safe_message("warning", "Внимание", ERR_ALL_PATHS_REQUIRED)
        
        # Логика извлечения флага
        if self.action.get() == "rotate":
            display_text = self.rot_val.get()
            final_value = self.ROT_MAP.get(display_text)
        else:
            display_text = self.mir_val.get()
            final_value = self.MIR_MAP.get(display_text)
            
        # В процессор уходит уже технический флаг ("90", "h" и т.д.)
        self.processor.process_transform(
            self.src.get(), 
            self.out.get(), 
            self.pages.get(), 
            self.action.get(), 
            final_value
        )