import pytest
from unittest.mock import MagicMock, patch
from core.operations import extract_logic, merge_logic

@pytest.fixture
def mock_reader():
    """Создает фиктивный объект PDF Reader с 10 страницами."""
    reader = MagicMock()
    reader.pages = [MagicMock() for _ in range(10)]
    return reader

@patch('core.operations.PdfWriter')
@patch('core.operations.save_pdf')
def test_extract_logic_calls(mock_save, mock_writer_cls, mock_reader):
    """Проверка, что логика извлечения вызывает методы записи нужных страниц."""
    mock_writer = mock_writer_cls.return_value
    query = [("1-2", "part1.pdf")]
    
    extract_logic(mock_reader, "/fake/path", query, lambda x: None)
    
    # Проверяем, что добавлены страницы с индексами 0 и 1
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