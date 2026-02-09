import os
from pypdf import PdfWriter, Transformation
from core.io_handler import save_pdf, get_safe_unique_path 
from utils.messages import get_msg
from utils.parser import parse_to_blocks


def extract_logic(reader, out_path, query, progress_cb):
    total_pages = len(reader.pages)
    successful_files = 0

    # Распаковываем кортеж (конфигурация страниц, желаемое имя)
    for i, (config_str, custom_name, is_exclude) in enumerate(query):
        raw_indices = parse_to_blocks(config_str, total_pages, is_exclude)
        if not raw_indices: 
            continue
        writer = PdfWriter()
        final_indices = [p for sublist in raw_indices for p in sublist]

        for p_idx in final_indices:
            writer.add_page(reader.pages[p_idx])

        # Очищаем имя от "мусора"
        
        final_path = get_safe_unique_path(out_path, custom_name)
        save_pdf(writer, final_path)
        successful_files += 1
        progress_cb(i + 1)

    
    if successful_files == 0:
        raise ValueError(get_msg("err_no_pages_extracted"))



def merge_logic(files, out_path, progress_cb):
    merger = PdfWriter()
    try:
        for i, f in enumerate(files):
            with open(f, "rb") as fh:
                merger.append(fh)
                progress_cb(i + 1)
        directory, filename = os.path.split(out_path)
        final_path = get_safe_unique_path(directory, filename)
        save_pdf(merger, final_path)
    finally:
        merger.close()


def editor_logic(reader, out_path, query, progress_cb):
    total_pages = len(reader.pages)

    raw_indices = parse_to_blocks(query, total_pages)
    if not raw_indices:
        return  
    writer = PdfWriter()
    # Определяем уже указанные пользователем страницы (0-indexed)
    final_indices = [p for block in raw_indices for p in block]
    
    # Находим отсутствующие страницы для автозаполнения
    all_indices = set(range(total_pages))
    used_indices = set(final_indices)
    remaining_indices = sorted(list(all_indices - used_indices))
    
    # Формируем итоговый список индексов: сначала ввод пользователя, затем остаток
    final_indices = final_indices + remaining_indices
    
    if not final_indices:
        raise ValueError(get_msg("err_page_numbers"))

    # Превращаем плоский список индексов обратно в формат блоков для extract_logic
    # Оборачиваем в список, так как extract_logic ожидает итератор кортежей (config, name)
    # Используем фиктивную конфигурацию, так как мы уже подготовили индексы
  
    for i, p_idx in enumerate(final_indices):
        writer.add_page(reader.pages[p_idx])
        progress_cb(i + 1)
    directory, filename = os.path.split(out_path)
    final_path = get_safe_unique_path(directory, filename) 
    save_pdf(writer, final_path)


def rotate_mirror_logic(reader, out_path, query, action_type, value, progress_cb):
    """
    Трансформация страниц: поворот (rotate) или отражение (mirror).
    action_type: 'rotate' или 'mirror'
    value: градусы (90, 180, 270) или направление ('h', 'v')
    """
    total_pages = len(reader.pages)
    raw_indices = parse_to_blocks(query, total_pages)
    if not raw_indices:
        return
    
    target_indices = set(p for sublist in raw_indices for p in sublist)
    writer = PdfWriter()
    
    for i in range(total_pages):
        page = reader.pages[i]
        if i in target_indices:
            if action_type == 'rotate':
                page.rotate(int(value))
            elif action_type == 'mirror':
                # Получаем размеры страницы для корректного смещения после отражения
                mb = page.mediabox
                if value == 'h':
                    # Отражение по горизонтали: масштабируем X на -1 и сдвигаем вправо на ширину
                    op = Transformation().scale(-1, 1).translate(mb.width, 0)
                else:
                    # Отражение по вертикали: масштабируем Y на -1 и сдвигаем вверх на высоту
                    op = Transformation().scale(1, -1).translate(0, mb.height)
                page.add_transformation(op)
        
        writer.add_page(page)
        progress_cb(i + 1)
    directory, filename = os.path.split(out_path)
    final_path = get_safe_unique_path(directory, filename)     
    save_pdf(writer, final_path)
