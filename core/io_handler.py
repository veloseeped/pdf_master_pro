import os
import re
from pypdf import PdfReader
from utils.constants import ERR_ENCRYPTED

def get_safe_unique_path(directory, filename):
    """
    Гарантирует безопасный и уникальный путь к файлу.
    1. Очищает имя файла от запрещенных символов.
    2. Добавляет индекс, если файл уже существует[cite: 21, 22].
    """
    # 1. Очистка имени (логика из sanitize_filename)
    clean_name = re.sub(r'[\\/*?:"<>|]', "", filename) 
    if not clean_name.strip():
        clean_name = "File_unnamed"
    if not clean_name.lower().endswith(".pdf"):
        clean_name += ".pdf" 
    
    # 2. Обеспечение уникальности (логика из get_unique_path)
    base, ext = os.path.splitext(clean_name) 
    final_path = os.path.join(directory, clean_name) 
    counter = 1
    
    while os.path.exists(final_path): 
        final_path = os.path.join(directory, f"{base}_{counter}{ext}") 
        counter += 1 
        
    return final_path


def get_reader(stream_or_path):
    """Возвращает PdfReader или выбрасывает ValueError, если файл защищен."""
    if not stream_or_path:
        raise ValueError("Путь к файлу не указан")
    try:
        reader = PdfReader(stream_or_path, strict=False)
    except Exception as e:
        source_name = getattr(stream_or_path, 'name', 'PDF Stream')
        raise ValueError(f"Ошибка доступа к PDF: {source_name}")
    if reader.is_encrypted:
        # Пытаемся открыть с пустым паролем
        if reader.decrypt("") == 0:
            raise ValueError(ERR_ENCRYPTED)
    return reader


def save_pdf(writer, clear_output_path):
    directory = os.path.dirname(clear_output_path)
    if directory:   
        os.makedirs(directory, exist_ok=True)
    with open(clear_output_path, "wb") as f_out:
        writer.write(f_out)
    writer.close()