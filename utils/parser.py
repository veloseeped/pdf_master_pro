from pathlib import Path

def clean_path(path):
    """Очистка пути от артефактов Drag-and-Drop"""
    return str(Path(path.strip('{}').strip('"')))

def parse_to_blocks(query, max_pages, exclude_mode=False):
    """Разбор строки с диапазонами страниц (например '1, 3-5', "5-3") в индексы"""
    blocks = []
    if not query.strip(): 
        return None
    try:
        for part in query.split(','):
            part = part.strip()
            if not part: 
                continue
            if '-' in part:
                # Извлекаем числа: "3-1" -> [3, 1]
                # Строгое разделение: должно быть ровно две части
                nums_raw = [x.strip() for x in part.split('-')]
                if len(nums_raw) != 2 or not all(x.isdigit() for x in nums_raw):
                    raise ValueError ("Page out of range or not a digit")
                start, end = int(nums_raw[0]), int(nums_raw[1])
                if not (1 <= start <= max_pages and 1 <= end <= max_pages):
                    raise ValueError(f"Out of range: {start}-{end}")                
                # Если start > end, идем в обратном порядке (step = -1)
                # Для включения страницы 'end' в range, stop должен быть end - 2 при шаге -1
                step = 1 if start <= end else -1
                stop = end if start <= end else end - 2
                blocks.append(list(range(start - 1, stop, step)))
            else:
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < max_pages: 
                        blocks.append([idx])
                    else:
                        raise ValueError("Page out of range")
                else:
                    raise ValueError("Not a digit")
        final_indices = [p for sublist in blocks for p in sublist]
        
        if exclude_mode:
            all_indices = list(range(max_pages))
            # Сохраняем только те, которых нет в списке исключения
            return [[i for i in all_indices if i not in final_indices]]

        return blocks if blocks else None
    except Exception:
        return None