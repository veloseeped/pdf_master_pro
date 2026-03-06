import pytest
from core.validator import validate_file_exists
from utils.messages import get_msg

def test_validate_file_exists_success(tmp_path):
    f = tmp_path / "exists.pdf"
    f.write_text("data")
    assert validate_file_exists(str(f)) is True

def test_validate_file_not_found():
    with pytest.raises(FileNotFoundError) as exc:
        validate_file_exists("non_existent_file.pdf")
    assert get_msg("err_file_not_found") in str(exc.value)
