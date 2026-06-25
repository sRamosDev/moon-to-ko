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


def test_extract_file_to(dummy_mrpro, tmp_path):
    extractor = MrproExtractor(str(dummy_mrpro))
    dest = tmp_path / "mybook.epub.r"
    extractor.extract_file_to("?/sdcard/Books/mybook.epub.r", str(dest))
    assert dest.exists()
    assert dest.read_bytes() == b"fake_progress_data"


def test_extractor_missing_names_list(tmp_path):
    empty_zip_path = tmp_path / "empty.mrpro"
    with zipfile.ZipFile(empty_zip_path, "w"):
        pass

    extractor = MrproExtractor(str(empty_zip_path))

    with pytest.raises(
        FileNotFoundError,
        match="com.flyersoft.moonreaderp/_names.list not found in the backup archive.",
    ):
        extractor.get_all_original_paths()


def test_extractor_get_file_content_no_zf(dummy_mrpro):
    extractor = MrproExtractor(str(dummy_mrpro))
    # the method get_file_content has 2 branches for `zf` and we need to test `zf is None`
    content = extractor.get_file_content(
        "com.flyersoft.moonreaderp/databases/mrbooks.db", zf=None
    )
    assert content == b"fake_db_content"


def test_extractor_extract_file_to_no_zf(dummy_mrpro, tmp_path):
    extractor = MrproExtractor(str(dummy_mrpro))
    dest = tmp_path / "mrbooks.db"
    extractor.extract_file_to(
        "com.flyersoft.moonreaderp/databases/mrbooks.db", str(dest), zf=None
    )
    assert dest.exists()
    assert dest.read_bytes() == b"fake_db_content"


def test_extractor_get_file_content_missing_tag(tmp_path):
    # Test KeyError block in _read_from_zip
    mrpro_path = tmp_path / "missing_tag.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        # We don't write the tag file

    extractor = MrproExtractor(str(mrpro_path))
    with pytest.raises(
        FileNotFoundError,
        match="Mapped tag file 'com.flyersoft.moonreaderp/1.tag' not found in the backup archive.",
    ):
        extractor.get_file_content("com.flyersoft.moonreaderp/databases/mrbooks.db")


def test_extractor_extract_file_to_missing_tag(tmp_path):
    # Test KeyError block in _extract_from_zip
    mrpro_path = tmp_path / "missing_tag2.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        # We don't write the tag file

    extractor = MrproExtractor(str(mrpro_path))
    dest = tmp_path / "mrbooks.db"
    with pytest.raises(
        FileNotFoundError,
        match="Mapped tag file 'com.flyersoft.moonreaderp/1.tag' not found in the backup archive.",
    ):
        extractor.extract_file_to(
            "com.flyersoft.moonreaderp/databases/mrbooks.db", str(dest)
        )


def test_extractor_get_tag_filename_missing(tmp_path):
    mrpro_path = tmp_path / "missing_tag3.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )

    extractor = MrproExtractor(str(mrpro_path))
    with pytest.raises(
        FileNotFoundError,
        match="Original path 'nonexistent.db' not found in the backup mapping.",
    ):
        extractor.get_file_content("nonexistent.db")
