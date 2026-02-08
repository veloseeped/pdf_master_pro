from core.validator import validate_file_exists
from core.operations import extract_logic, merge_logic, editor_logic
from core.task_manager import run_in_thread
from core.io_handler import get_reader
from utils.constants import MSG_SUCCESS_TITLE
from utils.messages import get_msg

class PdfProcessor:
    def __init__(self, app):
        self.app = app

    def _execute_safe(self, task_func, success_msg_key, *args):
        """
        Универсальная обертка для выполнения бизнес-логики в потоке.
        Обеспечивает валидацию, обработку ошибок и сброс прогресс-бара.
        """
        def worker():
            try:
                # Включаем индикатор ожидания (0/100), если максимум не задан явно
                self.app.root.after(0, lambda: self.app.update_progress(0, 100))
                
                # Выполнение основной логики
                task_func(*args)
                
                # Уведомление об успехе
                self.app.safe_message("info", MSG_SUCCESS_TITLE, success_msg_key)
            except Exception as e:
                self.app.safe_message("error", "Ошибка", str(e))
            finally:
                # Гарантированный сброс прогресса 
                self.app.update_progress(0)
                
        run_in_thread(worker, ())

    def process_extraction(self, src, dest, configs):
        def task(s, d, c):
            validate_file_exists(s)
            self.app.update_progress(0, len(c))
            with open(s, "rb") as f_stream:
                reader = get_reader(f_stream)
                extract_logic(reader, d, c, self.app.update_progress)
            
        self._execute_safe(task, f"Создано файлов: {len(configs)}", src, dest, configs)

    def process_merge(self, src, out_path):
        def task(f_list, out):
            if not f_list or len(f_list) < 2:
                raise ValueError(get_msg("err_merge_required"))
            for f in f_list: 
                validate_file_exists(f)
            self.app.update_progress(0, len(f_list))
            merge_logic(f_list, out, self.app.update_progress)
            
        self._execute_safe(task, "Файлы успешно склеены.", src, out_path)

    def process_editor(self, src, out_path, query):
        def task(s, o, q):
            validate_file_exists(s)
            with open(s, "rb") as f_stream:
                reader = get_reader(f_stream)
                editor_logic(reader, o, q, lambda v: self.app.update_progress(v, None))
            
        self._execute_safe(task, "Новый файл успешно создан.", src, out_path, query)

    def process_reverse(self, src, out_path):
        """Создает PDF с полностью обратным порядком страниц."""
        def task(s, o):
            validate_file_exists(s)
            with open(s, "rb") as f_stream:
                reader = get_reader(f_stream)
                total_pages = len(reader.pages)
                query = f"{total_pages}-1" if total_pages > 1 else "1"
                # Используем существующую логику редактора для применения реверса
                editor_logic(reader, o, query, lambda v: self.app.update_progress(v, None))
        
        self._execute_safe(task, "Файл успешно реверсирован.", src, out_path)
