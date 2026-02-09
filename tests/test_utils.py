import pytest
import os
from utils.parser import parse_to_blocks, clean_path
from core.io_handler import get_safe_unique_path

def test_parse_to_blocks_valid():
    """Проверка корректного парсинга диапазонов и одиночных страниц."""
    max_p = 10
    # Обычный список и диапазон
    assert parse_to_blocks("1, 3-5", max_p) == [[0], [2, 3, 4]] 
    # Реверсивный диапазон
    assert parse_to_blocks("5-3", max_p) == [[4, 3, 2]] 
    # Одиночная страница
    assert parse_to_blocks("10", max_p) == [[9]] 


def test_parse_to_blocks_invalid():
    """Проверка обработки некорректного ввода через исключения."""
    # Теперь мы ожидаем, что функция выбросит ValueError
    with pytest.raises(ValueError, match="Not a digit"):
        parse_to_blocks("abc", 10)
    
    with pytest.raises(ValueError, match="Out of range"):
        parse_to_blocks("15-20", 10)


def test_get_safe_unique_path_complex(tmp_path):
    """
    Комплексная проверка: очистка запрещенных символов + 
    обработка конфликта имен (генерация индекса).
    """
    import os
    from core.io_handler import get_safe_unique_path
    
    d = tmp_path / "test_dir"
    d.mkdir()
    
    # 1. Создаем файл с "чистым" именем, которое мы ожидаем после обработки
    # 'report?.pdf' -> после очистки 'report.pdf'
    existing_file = d / "report.pdf"
    existing_file.write_text("content")
    
    # 2. Вызываем функцию с "грязным" именем
    # Ожидаем: 'report?.pdf' -> 'report.pdf' (конфликт) -> 'report_1.pdf'
    result_path = get_safe_unique_path(str(d), "report?.pdf")
    
    filename = os.path.basename(result_path)
    
    # ПРОВЕРКИ:
    # Символ '?' должен быть удален
    assert "?" not in filename 
    # Так как report.pdf уже есть, должен появиться индекс _1
    assert filename == "report_1.pdf" 
    # Путь должен остаться в целевой директории
    assert os.path.dirname(result_path) == str(d) 

def test_get_safe_unique_path_empty_input(tmp_path):
    """Проверка обработки пустого или некорректного ввода."""
    from core.io_handler import get_safe_unique_path
    import os
    
    # Ввод, состоящий только из запрещенных символов
    result_path = get_safe_unique_path(str(tmp_path), "??//??")
    filename = os.path.basename(result_path)
    
    # Должно вернуться дефолтное имя с расширением .pdf
    assert "File_unnamed" in filename 
    assert filename.endswith(".pdf") 

def test_parse_to_blocks_edge_cases():
    max_p = 10
    # Дубликаты и лишние пробелы — остаются валидными (дублирование допустимо) [cite: 95]
    assert parse_to_blocks("1, 1, 2", max_p) == [[0], [0], [1]]
    
    # Огромные числа (больше max_pages) — теперь ожидаем ValueError [cite: 94]
    with pytest.raises(ValueError):
        parse_to_blocks("1, 100", max_p)
    
    # Отрицательные числа — теперь ожидаем ValueError [cite: 94]
    with pytest.raises(ValueError):
        parse_to_blocks("-1, 5", max_p)
    
    # Смешанный невалидный ввод (строки вместо цифр) — теперь ожидаем ValueError [cite: 95]
    with pytest.raises(ValueError):
        parse_to_blocks("1, dog, 3", max_p)

    # Запрет на исключение всех страниц (exclude_mode)
    # Если исключить диапазон 1-10 в документе из 10 страниц, должна возникнуть ошибка
    with pytest.raises(ValueError, match="Нельзя исключить все страницы документа."):
        parse_to_blocks(f"1-{max_p}", max_p, exclude_mode=True)

def test_parse_to_blocks_complex_input():
    """Проверка пересекающихся диапазонов и лишних пробелов."""
    max_p = 10
    # Пересекающиеся диапазоны: должны обрабатываться как есть (дублирование) [cite: 43]
    assert parse_to_blocks("1-3, 2-4", max_p) == [[0, 1, 2], [1, 2, 3]] 
    # Лишние запятые и пробелы [cite: 43, 90]
    assert parse_to_blocks("1, , 3", max_p) == [[0], [2]]
    # Страница равна max_pages (граничное значение) [cite: 41]
    assert parse_to_blocks(str(max_p), max_p) == [[max_p - 1]]

def test_parse_to_blocks_out_of_bounds():
    """Проверка ввода страницы за пределами документа."""
    with pytest.raises(ValueError):
        parse_to_blocks("11", 10)
    
    with pytest.raises(ValueError):
        parse_to_blocks("1-15", 10)