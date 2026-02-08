import tkinter as tk
from unittest.mock import MagicMock, patch
from tkinterdnd2 import TkinterDnD
from ui.extractor_tab import ExtractorTab
from ui.merge_tab import MergeTab
from ui.editor_tab import EditorTab


def test_extractor_tab_data_collection():
    """Проверка сбора конфигураций из динамических полей ввода."""
    # Инициализация корня с поддержкой Drag-and-Drop для корректной работы виджетов 
    root = TkinterDnD.Tk()
    root.withdraw() # Скрываем окно при тестах
    
    try:
        mock_processor = MagicMock()
        
        # Создаем вкладку экстрактора
        tab = ExtractorTab(root, mock_processor)
        
        # 1. Добавляем второй блок (один создается автоматически при инициализации) 
        tab.add_block_field()
        
        # 2. Эмулируем ввод пользователя в Entry виджеты 
        # Структура строки: [Label, Entry(pages), Entry(name)]
        row1_children = tab.block_entries[0].winfo_children()
        row2_children = tab.block_entries[1].winfo_children()
        
        # Блок 1
        row1_children[1].insert(0, "1-3") 
        row1_children[2].delete(0, tk.END)
        row1_children[2].insert(0, "first_part")
        
        # Блок 2
        row2_children[1].insert(0, "5, 7")
        row2_children[2].delete(0, tk.END)
        row2_children[2].insert(0, "second_part")
        
        # 3. Устанавливаем пути [cite: 61]
        tab.ext_source.set("source.pdf")
        tab.ext_dest.set("/output/dir")
        
        # 4. Запускаем сборку данных
        tab._run_extractor()
        
        # Проверяем, что в процессор ушли корректно сформированные данные 
        mock_processor.process_extraction.assert_called_once_with(
            "source.pdf",
            "/output/dir",
            [("1-3", "first_part"), ("5, 7", "second_part")]
        )
    finally:
        root.destroy()

def test_extractor_tab_empty_pages_ignored():
    """Проверка, что пустые строки страниц игнорируются при запуске."""
    root = TkinterDnD.Tk()
    root.withdraw()
    
    try:
        mock_processor = MagicMock()
        tab = ExtractorTab(root, mock_processor)
        
        tab.ext_source.set("s.pdf")
        tab.ext_dest.set("d")
        
        # Поля страниц оставляем пустыми (default state)
        tab._run_extractor()
        
        # Процессор не должен вызываться, так как конфиги пусты 
        mock_processor.process_extraction.assert_not_called()
    finally:
        root.destroy()

def test_extractor_tab_auto_naming():
    """Проверка автоматического формирования имен файлов при выборе источника."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        tab = ExtractorTab(root, MagicMock())
        # Имитируем выбор файла 
        tab.ext_source.set("C:/docs/report_2024.pdf")
        
        # Проверяем, что имя первого блока обновилось 
        row_children = tab.block_entries[0].winfo_children()
        name_entry = row_children[2]
        assert "report_2024_part_1" in name_entry.get()
    finally:
        root.destroy()

def test_extractor_tab_clear_all():
    """Проверка сброса всех блоков до начального состояния."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        tab = ExtractorTab(root, MagicMock())
        tab.add_block_field() # Теперь 2 блока 
        
        tab.clear_blocks() # Очистка 
        
        # Должен остаться ровно один блок 
        assert len(tab.block_entries) == 1
    finally:
        root.destroy()

# --- ТЕСТЫ ДЛЯ MERGETAB ---

def test_merge_tab_data_collection():
    """Проверка сбора списка файлов и пути сохранения для объединения."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        mock_processor = MagicMock()
        tab = MergeTab(root, mock_processor)
        
        # Эмулируем заполнение списка файлов [cite: 80, 81]
        test_files = ["file1.pdf", "file2.pdf"]
        for f in test_files:
            tab.listbox.insert(tk.END, f)
        
        tab.merge_out.set("merged_result.pdf")
        
        # Запуск
        tab._run_merge()
        
        # Проверяем вызов процессора с корректными аргументами [cite: 84]
        # Важно: listbox.get возвращает кортеж
        mock_processor.process_merge.assert_called_once_with(tuple(test_files), "merged_result.pdf")
    finally:
        root.destroy()

def test_merge_tab_list_manipulation():
    """Проверка функций перемещения и удаления в списке[cite: 82, 83]."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        tab = MergeTab(root, MagicMock())
        tab.listbox.insert(tk.END, "f1.pdf")
        tab.listbox.insert(tk.END, "f2.pdf")
        
        # Тест перемещения вниз (f1 идет вниз) [cite: 83]
        tab.listbox.selection_set(0)
        tab._move_down()
        assert tab.listbox.get(1) == "f1.pdf"
        
        # Тест перемещения вверх (f1 возвращается вверх) [cite: 82]
        tab.listbox.selection_set(1)
        tab._move_up()
        assert tab.listbox.get(0) == "f1.pdf"
        
        # [cite_start]Тест удаления [cite: 79]
        tab.listbox.selection_set(0)
        tab._remove_from_list()
        assert tab.listbox.size() == 1
        assert tab.listbox.get(0) == "f2.pdf"
    finally:
        root.destroy()

# --- ТЕСТЫ ДЛЯ EDITORTAB ---

def test_editor_tab_run():
    """Проверка запуска редактора порядка страниц[cite: 60]."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        mock_processor = MagicMock()
        tab = EditorTab(root, mock_processor)
        
        tab.ed_source.set("input.pdf")
        tab.ed_out.set("output.pdf")
        tab.ed_pages.set("1, 5, 2-4")
        
        tab._run_editor()
        
        # Проверка передачи всех параметров в процессор [cite: 60]
        mock_processor.process_editor.assert_called_once_with(
            "input.pdf", "output.pdf", "1, 5, 2-4"
        )
    finally:
        root.destroy()

def test_editor_tab_reverse():
    """Проверка запуска функции реверса страниц[cite: 61]."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        mock_processor = MagicMock()
        tab = EditorTab(root, mock_processor)
        
        tab.ed_source.set("source.pdf")
        tab.ed_out.set("reversed.pdf")
        
        tab._run_reverse()
        
        # Проверка вызова специализированного метода процессора [cite: 61]
        mock_processor.process_reverse.assert_called_once_with(
            "source.pdf", "reversed.pdf"
        )
    finally:
        root.destroy()

@patch('tkinter.messagebox.showwarning')
def test_editor_tab_validation(mock_warning):
    """Проверка валидации пустых путей перед запуском."""
    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        tab = EditorTab(root, MagicMock())
        # Не устанавливаем пути
        tab._run_editor()
        
        # Проверяем, что выполнение прервано (процессор не вызван)
        tab.processor.process_editor.assert_not_called()
    finally:
        root.destroy()