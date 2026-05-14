# TEAM_001: Tests for the Moon+ Reader Pro extractor
import pytest
import zipfile
from src.mrpro_extractor import MrproExtractor


@pytest.fixture
def dummy_mrpro(tmp_path):
    mrpro_path = tmp_path / "test.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n?/sdcard/Books/mybook.epub.r\n",
        )
        zf.writestr("com.flyersoft.moonreaderp/1.tag", b"fake_db_content")
        zf.writestr("com.flyersoft.moonreaderp/2.tag", b"fake_progress_data")
    return mrpro_path


def test_extractor_gets_paths(dummy_mrpro):
    extractor = MrproExtractor(str(dummy_mrpro))
    paths = extractor.get_all_original_paths()
    assert len(paths) == 2
    assert "com.flyersoft.moonreaderp/databases/mrbooks.db" in paths
    assert "?/sdcard/Books/mybook.epub.r" in paths


def test_extractor_gets_content(dummy_mrpro):
    extractor = MrproExtractor(str(dummy_mrpro))
    content = extractor.get_file_content(
        "com.flyersoft.moonreaderp/databases/mrbooks.db"
    )
    assert content == b"fake_db_content"

    content2 = extractor.get_file_content("?/sdcard/Books/mybook.epub.r")
    assert content2 == b"fake_progress_data"


def test_extract_db_to(dummy_mrpro, tmp_path):
    extractor = MrproExtractor(str(dummy_mrpro))
    dest = tmp_path / "mrbooks.db"
    extractor.extract_db_to(str(dest))
    assert dest.exists()
    assert dest.read_bytes() == b"fake_db_content"

def test_extractor_get_content_not_found(dummy_mrpro):
    extractor = MrproExtractor(str(dummy_mrpro))
    with pytest.raises(FileNotFoundError, match="Original path 'nonexistent.file' not found in the backup mapping."):
        extractor.get_file_content("nonexistent.file")

def test_extractor_get_content_tag_file_missing(tmp_path):
    # Create an archive with a valid name map but missing tag file
    mrpro_path = tmp_path / "missing_tag.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        # We purposely do not write "com.flyersoft.moonreaderp/1.tag"

    extractor = MrproExtractor(str(mrpro_path))
    with pytest.raises(FileNotFoundError, match="Mapped tag file 'com.flyersoft.moonreaderp/1.tag' not found in the backup archive."):
        extractor.get_file_content("com.flyersoft.moonreaderp/databases/mrbooks.db")
