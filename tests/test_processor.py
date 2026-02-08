import pytest
import time
from unittest.mock import MagicMock, patch, ANY
from core.processor import PdfProcessor
from utils.constants import ERR_MERGE_REQUIRED

def test_process_merge_validation_error():
    """Проверка, что мерж не запускается, если файлов меньше двух."""
    mock_app = MagicMock()
    processor = PdfProcessor(mock_app)
    
    # Пытаемся склеить только один файл
    processor.process_merge(["file1.pdf"], "output.pdf")
    
    # Даем время отработать потоку
    time.sleep(0.1)
    
    # Проверяем, что вызвана ошибка валидации, а не логика склейки
    mock_app.safe_message.assert_called_with("error", "Ошибка", ANY)
    # Проверяем, что сообщение содержит текст о необходимости минимум 2 файлов
    args = mock_app.safe_message.call_args[0]
    assert "минимум 2 файла" in str(args[2])

@patch('core.processor.get_reader')
@patch('core.processor.extract_logic')
@patch('core.processor.validate_file_exists')
@patch('core.processor.open', create=True)
def test_process_extraction_flow(mock_open, mock_val, mock_logic, mock_reader, tmp_path):
    """Проверка полной цепочки извлечения страниц."""
    mock_app = MagicMock()
    processor = PdfProcessor(mock_app)
    
    src = "input.pdf"
    dest = str(tmp_path)
    configs = [("1-2", "part1"), ("5", "part2")]
    
    processor.process_extraction(src, dest, configs)
    
    time.sleep(0.1)
    
    # Проверка вызовов
    mock_val.assert_called_once_with(src)
    mock_logic.assert_called_once()
    mock_app.update_progress.assert_any_call(0, len(configs))

@patch('core.processor.get_reader')
@patch('core.processor.editor_logic')
@patch('core.processor.validate_file_exists')
@patch('core.processor.open', create=True)
def test_process_reverse_flow(mock_open, mock_val, mock_logic, mock_reader):
    """Проверка логики реверса страниц."""
    mock_app = MagicMock()
    processor = PdfProcessor(mock_app)
    
    # Имитируем PDF на 10 страниц
    mock_reader.return_value.pages = [MagicMock() for _ in range(10)]
    
    processor.process_reverse("src.pdf", "out.pdf")
    
    time.sleep(0.1)
    
    # Проверяем, что вызван editor_logic с запросом "10-1"
    mock_logic.assert_called_once_with(ANY, "out.pdf", "10-1", ANY)

@patch('core.processor.get_reader')
@patch('core.processor.editor_logic')
@patch('core.processor.validate_file_exists')
@patch('core.processor.open', create=True)
def test_process_reverse_single_page(mock_open, mock_val, mock_logic, mock_reader):
    """Проверка реверса для документа из одной страницы."""
    mock_app = MagicMock()
    processor = PdfProcessor(mock_app)
    
    # Имитируем PDF на 1 страницу 
    mock_reader.return_value.pages = [MagicMock()]
    
    processor.process_reverse("one_page.pdf", "out.pdf")
    
    time.sleep(0.1)

    # Для одной страницы запрос должен быть "1-1" 
    mock_logic.assert_called_once_with(ANY, "out.pdf", "1", ANY)