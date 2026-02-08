import pytest
import threading
import time
import tkinter as tk
from tkinterdnd2 import TkinterDnD
from unittest.mock import MagicMock, patch
from ui.tkinter_gui import PdfProApp
from core.task_manager import run_in_thread
from core.processor import PdfProcessor

def test_run_in_thread_execution():
    """Проверка, что run_in_thread действительно запускает функцию в отдельном потоке[cite: 25]."""
    execution_flag = threading.Event()
    
    def target():
        execution_flag.set()
        
    run_in_thread(target, ())
    
    # Ожидаем выполнения потока (timeout чтобы тест не завис)
    assert execution_flag.wait(timeout=1.0) is True

def test_execute_safe_success_flow():
    """Проверка цепочки _execute_safe: выполнение -> уведомление об успехе[cite: 16, 18]."""
    mock_app = MagicMock()
    processor = PdfProcessor(mock_app)
    
    task_func = MagicMock()
    
    # Запускаем обертку. Она вызывает run_in_thread внутри.
    processor._execute_safe(task_func, "success_key")
    
    # Даем небольшую паузу для отработки потока
    time.sleep(0.1)
    
    # Проверяем, что основная логика была вызвана [cite: 18]
    task_func.assert_called_once()
    # Проверяем, что вызвано сообщение об успехе через безопасный метод [cite: 18]
    mock_app.safe_message.assert_called_with("info", "Готово", "success_key")

def test_execute_safe_error_handling():
    """Проверка перехвата исключений в потоке и вывода ошибки в UI."""
    mock_app = MagicMock()
    processor = PdfProcessor(mock_app)
    
    def failing_task():
        raise ValueError("Critical failure")
    
    processor._execute_safe(failing_task, "success_key")
    
    time.sleep(0.1)
    
    # Проверяем, что ошибка была поймана и передана в safe_message 
    mock_app.safe_message.assert_called_with("error", "Ошибка", "Critical failure")
    # Проверяем, что прогресс-бар сброшен в блоке finally 
    mock_app.update_progress.assert_any_call(0)


@patch('tkinter.messagebox.showinfo')
def test_safe_message_integration(mock_showinfo):
    """Проверка, что safe_message использует root.after для работы с Tkinter[cite: 77]."""
    
    # Используем TkinterDnD.Tk вместо tk.Tk, чтобы избежать TclError 
    root = TkinterDnD.Tk()
    root.withdraw() # Скрываем окно 
    
    try:
        # Инициализация приложения теперь пройдет успешно, так как DnD команды доступны 
        app = PdfProApp(root)
        
        # Перехватываем метод after у существующего объекта
        with patch.object(root, 'after') as mock_after:
            app.safe_message("info", "Title", "Message")
            
            # Убеждаемся, что вызов запланирован через after(0, ...) [cite: 77]
            mock_after.assert_called_once()
            
            # Извлекаем и выполняем лямбду, которую передали в after
            callback = mock_after.call_args[0][1]
            callback()
            
            # Проверяем финальный вызов окна сообщения
            mock_showinfo.assert_called_with("Title", "Message")
    finally:
        root.destroy() # Обязательная очистка ресурсов