import os
from utils.constants import ERR_FILE_NOT_FOUND

def validate_file_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{ERR_FILE_NOT_FOUND}: {path}")
    return True