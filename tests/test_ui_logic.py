import pytest
import tkinter as tk
from tkinterdnd2 import TkinterDnD
from ui.extractor_tab import ExtractorTab
from ui.merge_tab import MergeTab
from ui.editor_tab import EditorTab
from unittest.mock import MagicMock, patch, ANY

@pytest.fixture(scope="module")
def root():
    """Инициализирует один экземпляр Tk для всех тестов модуля."""
    _root = TkinterDnD.Tk()
    _root.withdraw()
    yield _root
    _root.destroy()

@pytest.fixture(autouse=True)
def cleanup_widgets(root):
    """Очищает все дочерние виджеты после каждого теста."""
    yield
    for child in root.winfo_children():
        child.destroy()

def test_extractor_tab_data_collection(root):
    mock_processor = MagicMock()
    tab = ExtractorTab(root, mock_processor)
    tab.add_block_field()
    
    # Блок 1
    row1_children = tab.block_entries[0].winfo_children()
    row1_children[1].insert(0, "1-3") 
    row1_children[3].delete(0, tk.END)
    row1_children[3].insert(0, "first_part")
    
    # Блок 2
    row2_children = tab.block_entries[1].winfo_children()
    row2_children[1].insert(0, "5, 7")
    row2_children[2].exclude_var.set(True)
    row2_children[3].delete(0, tk.END)
    row2_children[3].insert(0, "second_part")
    
    tab.ext_source.set("source.pdf")
    tab.ext_dest.set("/output/dir")
    tab._run_extractor()
    
    mock_processor.process_extraction.assert_called_once_with(
        "source.pdf", "/output/dir", [("1-3", "first_part", False), ("5, 7", "second_part", True)]
    )

def test_extractor_tab_empty_pages_ignored(root):
    mock_processor = MagicMock()
    tab = ExtractorTab(root, mock_processor)
    tab.ext_source.set("s.pdf")
    tab.ext_dest.set("d")
    tab._run_extractor()
    mock_processor.process_extraction.assert_not_called()

def test_extractor_tab_auto_naming(root):
    tab = ExtractorTab(root, MagicMock())
    tab.ext_source.set("C:/docs/report_2024.pdf")
    name_entry = tab.block_entries[0].winfo_children()[3]
    assert "report_2024_part_1" in name_entry.get()

def test_extractor_tab_clear_all(root):
    tab = ExtractorTab(root, MagicMock())
    tab.add_block_field() 
    tab.clear_blocks() 
    assert len(tab.block_entries) == 1

def test_merge_tab_data_collection(root):
    mock_processor = MagicMock()
    tab = MergeTab(root, mock_processor)
    test_files = ["file1.pdf", "file2.pdf"]
    for f in test_files:
        tab.listbox.insert(tk.END, f)
    tab.merge_out.set("merged_result.pdf")
    tab._run_merge()
    mock_processor.process_merge.assert_called_once_with(tuple(test_files), "merged_result.pdf")

def test_merge_tab_list_manipulation(root):
    tab = MergeTab(root, MagicMock())
    tab.listbox.insert(tk.END, "f1.pdf")
    tab.listbox.insert(tk.END, "f2.pdf")
    
    tab.listbox.selection_set(0)
    tab._move_down()
    assert tab.listbox.get(1) == "f1.pdf"
    
    tab.listbox.selection_set(1)
    tab._move_up()
    assert tab.listbox.get(0) == "f1.pdf"
    
    tab.listbox.selection_set(0)
    tab._remove_from_list()
    assert tab.listbox.size() == 1

def test_editor_tab_run(root):
    mock_processor = MagicMock()
    tab = EditorTab(root, mock_processor)
    tab.ed_source.set("input.pdf")
    tab.ed_out.set("output.pdf")
    tab.ed_pages.set("1, 5, 2-4")
    tab._run_editor()
    mock_processor.process_editor.assert_called_once_with("input.pdf", "output.pdf", "1, 5, 2-4")

def test_editor_tab_reverse(root):
    mock_processor = MagicMock()
    tab = EditorTab(root, mock_processor)
    tab.ed_source.set("source.pdf")
    tab.ed_out.set("reversed.pdf")
    tab._run_reverse()
    mock_processor.process_reverse.assert_called_once_with("source.pdf", "reversed.pdf")

def test_ui_unique_default_names_for_multiple_blocks(root):
    tab = ExtractorTab(root, MagicMock())
    tab.ext_source.set("document.pdf")
    tab.add_block_field() 
    name_entry_1 = tab.block_entries[0].winfo_children()[3]
    name_entry_2 = tab.block_entries[1].winfo_children()[3]
    assert "part_1" in name_entry_1.get()
    assert "part_2" in name_entry_2.get()

def test_transform_tab_data_collection(root):
    """Проверка сбора параметров трансформации из UI."""
    from ui.transform_tab import TransformTab
    mock_processor = MagicMock()
    tab = TransformTab(root, mock_processor)
    
    tab.src.set("input.pdf")
    tab.out.set("output.pdf")
    tab.pages.set("5-10")
    tab.action.set("rotate")
    target_key = "270 градусов"
    tab.rot_val.set(target_key)
    
    tab._run()
    
    # Убеждаемся, что данные из StringVar корректно переданы в процессор
    expected_flag = tab.ROT_MAP[target_key]
    mock_processor.process_transform.assert_called_once_with(
        "input.pdf", "output.pdf", "5-10", "rotate", expected_flag
    )

def test_transform_tab_mirror_data_collection(root):
    """Проверка сбора параметров отражения (горизонтальное и вертикальное)."""
    from ui.transform_tab import TransformTab
    mock_processor = MagicMock()
    tab = TransformTab(root, mock_processor)
    
    # Базовые настройки
    tab.src.set("input.pdf")
    tab.out.set("output.pdf")
    tab.pages.set("1-5")
    tab.action.set("mirror")
    
    # 1. Тестируем горизонтальное отражение
    # Устанавливаем ключ, который видит пользователь
    target_key_h = "По горизонтали (слева направо)" 
    tab.mir_val.set(target_key_h)
    
    tab._run()
    
    # Проверяем, что в процессор ушел флаг "h"
    mock_processor.process_transform.assert_called_with(
        "input.pdf", "output.pdf", "1-5", "mirror", "h"
    )
    
    # 2. Тестируем вертикальное отражение
    mock_processor.process_transform.reset_mock()
    target_key_v = "По вертикали (сверху вниз)"
    tab.mir_val.set(target_key_v)
    
    tab._run()
    
    # Проверяем, что в процессор ушел флаг "v"
    mock_processor.process_transform.assert_called_with(
        "input.pdf", "output.pdf", "1-5", "mirror", "v"
    )

def test_transform_tab_validation(root):
    """Проверка блокировки запуска при пустых полях."""
    from ui.transform_tab import TransformTab
    mock_processor = MagicMock()
    tab = TransformTab(root, mock_processor)
    
    # Оставляем поле страниц пустым
    tab.src.set("in.pdf")
    tab.out.set("out.pdf")
    tab.pages.set("")
    
    tab._run()
    
    # Процессор не должен вызываться [cite: 79]
    mock_processor.process_transform.assert_not_called()
    # Должно появиться предупреждение о заполнении всех путей [cite: 93]
    tab.processor.app.safe_message.assert_called_with("warning", "Внимание", ANY)

def test_editor_tab_and_transform_overlap_naming(root):
    """Проверка, что UI передает базовые имена, полагаясь на уникальность в ядре[cite: 73, 75]."""
    mock_processor = MagicMock()
    from ui.editor_tab import EditorTab
    from ui.transform_tab import TransformTab
    
    ed_tab = EditorTab(root, mock_processor)
    tr_tab = TransformTab(root, mock_processor)
    
    # Настраиваем одинаковые выходные пути
    shared_path = "C:/output/result.pdf"
    
    # 1. Запуск из редактора
    ed_tab.ed_source.set("source1.pdf")
    ed_tab.ed_out.set(shared_path)
    ed_tab.ed_pages.set("1")
    ed_tab._run_editor()
    
    # 2. Запуск из трансформации
    tr_tab.src.set("source2.pdf")
    tr_tab.out.set(shared_path)
    tr_tab.pages.set("1")
    tr_tab._run()
    
    # Проверяем, что оба вызова дошли до процессора с оригинальным путем [cite: 35, 42, 44]
    # Ядро само разберется с индексами _1, _2 и т.д. [cite: 22, 31, 34]
    mock_processor.process_editor.assert_called_with("source1.pdf", shared_path, "1")
    mock_processor.process_transform.assert_called_with("source2.pdf", shared_path, "1", ANY, ANY)