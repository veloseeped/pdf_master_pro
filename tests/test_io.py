import os
import pytest
from core.io_handler import get_reader, get_unique_path
from unittest.mock import MagicMock, patch
from utils.constants import ERR_ENCRYPTED

@patch('core.io_handler.PdfReader')
def test_get_reader_encrypted(mock_reader_cls):
    # Симуляция зашифрованного файла, который не открывается пустым паролем
    mock_reader = mock_reader_cls.return_value
    mock_reader.is_encrypted = True
    mock_reader.decrypt.return_value = 0 # 0 значит неудача 
    
    with pytest.raises(ValueError, match=ERR_ENCRYPTED):
        get_reader("dummy.pdf")

def test_save_pdf_creates_dir(tmp_path):
    from core.io_handler import save_pdf
    mock_writer = MagicMock()
    out_dir = tmp_path / "new_folder"
    out_file = out_dir / "test.pdf"
    
    # Проверка, что save_pdf создает директории автоматически 
    save_pdf(mock_writer, str(out_file))
    assert out_dir.exists()

def test_get_reader_invalid_file_content(tmp_path):
    """Проверка ошибки при чтении файла с неверным форматом."""
    fake_pdf = tmp_path / "not_a_pdf.pdf"
    fake_pdf.write_text("This is plain text, not PDF binary data.")
    
    with pytest.raises(ValueError, match="Ошибка доступа к PDF"):
        get_reader(str(fake_pdf))

def test_get_reader_none_path():
    """Проверка обработки отсутствующего пути[cite: 6]."""
    with pytest.raises(ValueError, match="Путь к файлу не указан"):
        get_reader(None)


def test_get_unique_path_collision(tmp_path):
    """Проверка генерации имен: file.pdf -> file_1.pdf -> file_2.pdf."""
    directory = str(tmp_path)
    filename = "report.pdf"
    
    # Создаем первый файл
    full_path_0 = os.path.join(directory, filename)
    with open(full_path_0, "w") as f: f.write("content")
    
    # 1-е столкновение: ожидаем report_1.pdf
    path_1 = get_unique_path(directory, filename)
    assert os.path.basename(path_1) == "report_1.pdf"
    
    # Создаем второй файл
    with open(path_1, "w") as f: f.write("content")
    
    # 2-е столкновение: ожидаем report_2.pdf
    path_2 = get_unique_path(directory, filename)
    assert os.path.basename(path_2) == "report_2.pdf"