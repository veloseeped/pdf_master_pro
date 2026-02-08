import pytest
from unittest.mock import MagicMock, patch, ANY
from core.operations import editor_logic, extract_logic, merge_logic, rotate_mirror_logic
from pypdf import PageObject
from pypdf.constants import PageAttributes as PA


@pytest.fixture
def mock_reader():
    """Создает фиктивный объект PDF Reader с 10 страницами, совместимыми с PdfWriter."""
    reader = MagicMock()
    pages = []
    for _ in range(10):
        # Создаем мок, который прикидывается PageObject
        page = MagicMock()
        # Имитируем внутреннюю структуру словаря PDF, которую проверяет pypdf
        page.get.return_value = "/Page" 
        # Если pypdf обращается через PageAttributes.TYPE
        page.__getitem__.side_effect = lambda key: "/Page" if key == "/Type" else None
        pages.append(page)
        
    reader.pages = pages
    return reader


@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
def test_extract_logic_with_exclude_mode(mock_save, mock_writer_cls, mock_reader):
    """Проверка логики исключения страниц в ядре[cite: 25, 134]."""
    mock_writer = mock_writer_cls.return_value
    # Тест режима исключения: документ 10 страниц, исключаем 1-8, должны остаться 9 и 10 (индексы 8, 9)
    query = [("1-8", "excluded.pdf", True)]
    
    extract_logic(mock_reader, "/fake/path", query, lambda x: None)
    
    # Проверяем, что добавлены именно 2 страницы (9-я и 10-я) [cite: 26]
    assert mock_writer.add_page.call_count == 2
    mock_save.assert_called_once()


@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
@patch('core.operations.get_safe_unique_path')
def test_extract_logic_multiple_blocks_path_consistency(mock_get_unique, mock_save, mock_writer_cls):
    """
    Проверяет, что второй блок использует базовую директорию, 
    а не путь к первому файлу.
    """
    # Имитируем ридер с 10 страницами
    mock_reader = MagicMock()
    mock_reader.pages = [MagicMock() for _ in range(10)]
    
    # Настройка: два блока
    base_dir = "C:/output"
    query = [("1", "part1", False), ("2", "part2", False)]
    
    # Имитируем возврат путей от get_unique_path
    mock_get_unique.side_effect = [
        "C:/output/part1.pdf",
        "C:/output/part2.pdf"
    ]

    # Запуск логики
    extract_logic(mock_reader, base_dir, query, lambda x: None)

    # ПРОВЕРКА: get_unique_path должен оба раза вызываться с base_dir
    # Если ошибка есть, второй вызов будет с "C:/output/part1.pdf" вместо "C:/output"
    assert mock_get_unique.call_args_list[0][0][0] == base_dir
    assert mock_get_unique.call_args_list[1][0][0] == base_dir
    
    # Проверка, что было создано 2 файла
    assert mock_save.call_count == 2


def test_extract_logic_no_overwrite_error(tmp_path):
    """
    Проверка, что экстрактор не падает, если файл уже существует,
    и использует уникальное имя для нового блока.
    """
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    
    # Создаем файл, который спровоцирует конфликт
    existing_file = out_dir / "Part_1.pdf"
    existing_file.write_text("original content")
    
    # Подготовка фиктивного PDF ридера
    mock_reader = MagicMock()
    mock_reader.pages = [MagicMock()] # Документ из 1 страницы
    
    # Задача: извлечь 1-ю страницу в файл с именем "Part_1"
    query = [("1", "Part_1", False)]    
   
    # Мокаем PdfWriter и сохранение, чтобы не создавать реальные бинарные файлы,
    # но перехватываем путь, который выбрала логика
    with patch('core.operations.PdfWriter'), \
         patch('core.operations.save_pdf') as mock_save:
        
        
        # Выполнение (здесь раньше возникал WinError 183)
        extract_logic(mock_reader, str(out_dir), query, lambda x: None)
        
        # Проверяем, какой путь в итоге был передан в функцию сохранения
        called_path = mock_save.call_args[0][1]
        
        # Убеждаемся, что имя было изменено для предотвращения конфликта 
        assert "Part_1_1.pdf" in called_path
        # Убеждаемся, что оригинальный файл не был затронут
        assert existing_file.read_text() == "original content"


@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
def test_extract_logic_calls(mock_save, mock_writer_cls, mock_reader):
    """Обновленный тест обычного извлечения с учетом нового аргумента[cite: 25, 26]."""
    mock_writer = mock_writer_cls.return_value
    # Добавлен флаг False для обычного извлечения
    query = [("1-2", "part1.pdf", False)]
    
    extract_logic(mock_reader, "/fake/path", query, lambda x: None)
    
    assert mock_writer.add_page.call_count == 2 
    mock_save.assert_called_once()

@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
@patch('core.operations.open', create=True)

def test_merge_logic_calls(mock_open, mock_save, mock_writer_cls):
    """Проверка корректности объединения нескольких файлов."""
    mock_writer = mock_writer_cls.return_value
    files = ["f1.pdf", "f2.pdf"]
    
    merge_logic(files, "/out/merged.pdf", lambda x: None)
    
    # Проверяем, что метод append был вызван для каждого файла
    assert mock_writer.append.call_count == 2 
    mock_save.assert_called_once() 

@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
# Порядок: 1. save_pdf -> mock_save, 2. PdfWriter -> mock_writer_cls, 3. fixture -> mock_reader
def test_rotate_mirror_logic_rotation(mock_save, mock_writer_cls, mock_reader):
    """Проверка поворота выбранных страниц на 90 градусов[cite: 59]."""
    from core.operations import rotate_mirror_logic
    mock_writer = mock_writer_cls.return_value
    
    query = "1"
    # Передаем реальный mock_reader (фиксчуру)
    rotate_mirror_logic(mock_reader, "/out.pdf", query, 'rotate', "90", lambda x: None)
    
    # Теперь mock_reader[0] — это объект из фиксчуры, который прошел через логику [cite: 60]
    mock_reader.pages[0].rotate.assert_called_with(90)
    assert mock_writer.add_page.called 
    mock_save.assert_called_once() 

@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
def test_rotate_mirror_logic_mirror_h(mock_save, mock_writer_cls, mock_reader):
    """Проверка горизонтального отражения через add_transformation (совместимость с pypdf 3.0+)."""
    from core.operations import rotate_mirror_logic
    mock_writer = mock_writer_cls.return_value
    
    # Настраиваем размеры страницы, так как логика использует их для translate() 
    target_page = mock_reader.pages[1]  # Индекс 1 соответствует странице "2" в запросе [cite: 60, 61]
    target_page.mediabox.width = 500
    target_page.mediabox.height = 800
    
    query = "2"
    rotate_mirror_logic(mock_reader, "/out.pdf", query, 'mirror', "h", lambda x: None)
    
    # Проверяем, что вместо удаленного метода .mirror() вызывается .add_transformation() 
    target_page.add_transformation.assert_called_once()
    
    # Убеждаемся, что все страницы документа (10 шт.) переданы в writer 
    assert mock_writer.add_page.call_count == len(mock_reader.pages) 
    
    # Проверяем вызов функции сохранения [cite: 34, 61]
    mock_save.assert_called_once()


@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
def test_rotate_mirror_logic_mirror_v(mock_save, mock_writer_cls, mock_reader):
    """Проверка вертикального отражения (зеркало по оси Y)[cite: 31, 33]."""
    from core.operations import rotate_mirror_logic
    mock_writer = mock_writer_cls.return_value
    
    # Подготовка страницы: добавляем mediabox, так как он нужен для translate() [cite: 50]
    target_page = mock_reader.pages[0] 
    target_page.mediabox.width = 600
    target_page.mediabox.height = 900
    
    query = "1"
    # Запуск логики трансформации [cite: 31]
    rotate_mirror_logic(mock_reader, "/out.pdf", query, 'mirror', "v", lambda x: None)
    
    # Проверяем, что была вызвана трансформация [cite: 32]
    target_page.add_transformation.assert_called_once()
    
    # Проверяем, что в итоговый документ попали все страницы [cite: 33]
    assert mock_writer.add_page.call_count == len(mock_reader.pages)
    mock_save.assert_called_once()


@patch('core.operations.get_safe_unique_path')
@patch('core.operations.save_pdf')
@patch('core.operations.PdfWriter')
def test_editor_logic_unique_path_call(mock_writer_cls, mock_save, mock_get_unique, mock_reader):
    """Проверка, что editor_logic запрашивает уникальный путь перед сохранением[cite: 22, 31]."""
    mock_get_unique.return_value = "/fake/dir/output_1.pdf"
    
    # Вызываем логику (out_path уже существует в воображаемой ФС)
    editor_logic(mock_reader, "/fake/dir/output.pdf", "1", lambda x: None)
    
    # Проверяем, что утилита уникальности была вызвана [cite: 22]
    mock_get_unique.assert_called_once()
    # Проверяем, что сохранение произошло по уникальному пути [cite: 24, 31]
    mock_save.assert_called_once_with(ANY, "/fake/dir/output_1.pdf")

@patch('core.operations.get_safe_unique_path')
@patch('core.operations.save_pdf')
@patch('core.operations.PdfWriter')
def test_transform_logic_unique_path_call(mock_writer_cls, mock_save, mock_get_unique, mock_reader):
    """Проверка, что rotate_mirror_logic запрашивает уникальный путь[cite: 32, 34]."""
    mock_get_unique.return_value = "/fake/dir/transformed_1.pdf"
    
    rotate_mirror_logic(mock_reader, "/fake/dir/transformed.pdf", "1", "rotate", "90", lambda x: None)
    
    # Путь должен быть обработан через get_safe_unique_path 
    mock_get_unique.assert_called_once()
    mock_save.assert_called_once_with(ANY, "/fake/dir/transformed_1.pdf")