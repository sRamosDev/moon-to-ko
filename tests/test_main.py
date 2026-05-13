import pytest
from src.main import run_migration

def test_run_migration_file_not_found(tmp_path):
    input_file = tmp_path / "non_existent_file.mrpro"
    output_dir = tmp_path / "some_output_dir"

    # Ensure the file really does not exist
    input_file_str = str(input_file)
    output_dir_str = str(output_dir)

    with pytest.raises(FileNotFoundError) as excinfo:
        run_migration(input_file_str, output_dir_str, False, False)

    assert str(excinfo.value) == f"Input file '{input_file_str}' does not exist."
