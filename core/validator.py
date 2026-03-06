import os
from utils.messages import get_msg

def validate_file_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f'{get_msg("err_file_not_found")}: {path}')
    return True