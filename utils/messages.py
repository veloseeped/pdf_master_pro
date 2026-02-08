MESSAGES = {
    "ru": {
        # Общие элементы UI
        "app_title": "PDF Master Pro",
        "btn_browse": "Обзор",
        "btn_add_block": "+ Добавить блок",
        "btn_clear_all": "Очистить всё",
        "btn_extract_run": "ИЗВЛЕЧЬ ВСЕ БЛОКИ",
        "btn_merge_run": "СКЛЕИТЬ",
        "btn_editor_run": "СОЗДАТЬ PDF",
        "label_source_pdf": "Исходный PDF:",
        "label_save_dir": "Папка сохранения:",
        "label_block_composition": "Состав блоков (каждый блок - отдельный файл):",
        "label_file_prefix": "Файл",
        
        # Вкладки
        "tab_extractor": "Извлечь страницы",
        "tab_merge": "Склеить PDF",
        "tab_editor": "Изменить порядок страниц",
        "tab_transform": "Повернуть или отразить",
        
        # Склейка и Редактор
        "label_file_list": "Список файлов:",
        "btn_add_file": "Добавить файл",
        "btn_up": "Выше",
        "btn_down": "Ниже",
        "btn_remove": "Удалить",
        "btn_clear": "Очистить",
        "label_save_as": "Сохранить как:",
        "label_new_order": "Новый порядок (например, 5, 1-3):",
        "label_result": "Результат:",
        
        # Сообщения об успехе
        "msg_success_title": "Готово",
        "msg_merge_success": "Файлы успешно склеены.",
        "msg_editor_success": "Новый файл успешно создан.",
        "msg_extract_success": "Создано файлов: {}",
        
        # Ошибки и предупреждения
        "msg_warning_title": "Внимание",
        "msg_error_title": "Ошибка",
        "err_paths_required": "Выберите исходный файл и папку сохранения",
        "err_pages_required": "Добавьте хотя бы один диапазон страниц",
        "err_merge_required": "Добавьте минимум 2 файла и путь сохранения",
        "err_all_paths_required": "Заполните все поля",
        "err_file_not_found": "Файл не найден",
        "err_encrypted": "Файл зашифрован или защищен паролем.",
        "err_no_pages_extracted": "Ни одна страница не была извлечена. Проверьте правильность номеров страниц.",
        "err_page_numbers": "Ошибка в номерах страниц"
    },
    "en": {
        # General UI
        "app_title": "PDF Master Pro",
        "btn_browse": "Browse",
        "btn_add_block": "+ Add Block",
        "btn_clear_all": "Clear All",
        "btn_extract_run": "EXTRACT ALL BLOCKS",
        "btn_merge_run": "MERGE",
        "btn_editor_run": "CREATE PDF",
        "label_source_pdf": "Source PDF:",
        "label_save_dir": "Save Directory:",
        "label_block_composition": "Block Composition (each block is a separate file):",
        "label_file_prefix": "File",
        
        # Tabs
        "tab_extractor": "Block Extractor",
        "tab_merge": "Merge PDF",
        "tab_editor": "Change Page Order",
        "tab_transform": "Rotate or Mirror",
        
        # Merge & Editor
        "label_file_list": "File List:",
        "btn_add_file": "Add file",
        "btn_up": "Up",
        "btn_down": "Down",
        "btn_remove": "Remove",
        "btn_clear": "Clear",
        "label_save_as": "Save As:",
        "label_new_order": "New Order (e.g., 5, 1-3):",
        "label_result": "Result:",
        
        # Success Messages
        "msg_success_title": "Done",
        "msg_merge_success": "Files merged successfully.",
        "msg_editor_success": "New file created successfully.",
        "msg_extract_success": "Files created: {}",
        
        # Errors & Warnings
        "msg_warning_title": "Warning",
        "msg_error_title": "Error",
        "err_paths_required": "Select source file and save directory",
        "err_pages_required": "Add at least one page range",
        "err_merge_required": "Add at least 2 files and a save path",
        "err_all_paths_required": "Fill in all paths",
        "err_file_not_found": "File not found",
        "err_encrypted": "File is encrypted or password protected.",
        "err_no_pages_extracted": "No pages were extracted. Check page numbers.",
        "err_page_numbers": "Error in page numbers"
    }
}

LANG = "ru"

def get_msg(key, *args):
    text = MESSAGES[LANG].get(key, key)
    if args:
        return text.format(*args)
    return text