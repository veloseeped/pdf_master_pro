import os
import re
from pypdf import PdfReader
from utils.constants import ERR_ENCRYPTED

def sanitize_filename(filename, i=0):
    """Удаляет запрещенные символы из имени файла."""
    # Оставляем буквы, цифры, пробелы, точки, тире и подчеркивания
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    if not filename.strip(): # Если имя стало пустым после очистки
        filename = f"File_{i+1}"           
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    return filename.strip()


def get_unique_path(directory, filename):
    """
    Проверяет, существует ли файл. Если да, добавляет индекс в конец имени.
    Пример: 'document.pdf' -> 'document_(1).pdf'
    """
    base, ext = os.path.splitext(filename)
    final_path = os.path.join(directory, filename)
    counter = 1
    
    while os.path.exists(final_path):
        final_path = os.path.join(directory, f"{base}_{counter}{ext}")
        counter += 1
    return final_path


def get_reader(path):
    """Возвращает PdfReader или выбрасывает ValueError, если файл защищен."""
    if not path:
        raise ValueError("Путь к файлу не указан")
    try:
        reader = PdfReader(path, strict=False)
        if reader.is_encrypted:
            # Пытаемся открыть с пустым паролем
            if reader.decrypt("") == 0:
                raise ValueError(ERR_ENCRYPTED)
        return reader
    except Exception as e:
        raise ValueError(f"Ошибка доступа к PDF: {str(e)}")


def save_pdf(writer, clear_output_path):
    os.makedirs(os.path.dirname(clear_output_path), exist_ok=True)
    with open(clear_output_path, "wb") as f_out:
        writer.write(f_out)
    writer.close()