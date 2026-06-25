import pytest
import os
import zipfile
from src.epub_exporter import EpubExporter
from src.mrpro_extractor import MrproExtractor


@pytest.fixture
def dummy_mrpro_epubs(tmp_path):
    mrpro_path = tmp_path / "test_epubs.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n?/sdcard/Books/mybook1.epub\n?/sdcard/Books/mybook2.EPUB\n?/sdcard/Books/mybook3.pdf\n",
        )
        zf.writestr("com.flyersoft.moonreaderp/1.tag", b"fake_db_content")
        zf.writestr("com.flyersoft.moonreaderp/2.tag", b"epub1_content")
        zf.writestr("com.flyersoft.moonreaderp/3.tag", b"epub2_content")
        zf.writestr("com.flyersoft.moonreaderp/4.tag", b"pdf_content")
    return mrpro_path


def test_export_epubs(dummy_mrpro_epubs, tmp_path):
    extractor = MrproExtractor(str(dummy_mrpro_epubs))
    output_dir = str(tmp_path / "output")

    count = EpubExporter.export(extractor, output_dir)

    assert count == 2

    books_dir = os.path.join(output_dir, "books")
    assert os.path.exists(books_dir)

    book1_path = os.path.join(books_dir, "mybook1.epub")
    assert os.path.exists(book1_path)
    with open(book1_path, "rb") as f:
        assert f.read() == b"epub1_content"

    book2_path = os.path.join(books_dir, "mybook2.EPUB")
    assert os.path.exists(book2_path)
    with open(book2_path, "rb") as f:
        assert f.read() == b"epub2_content"

    pdf_path = os.path.join(books_dir, "mybook3.pdf")
    assert not os.path.exists(pdf_path)


def test_export_epubs_progress_cb(dummy_mrpro_epubs, tmp_path):
    extractor = MrproExtractor(str(dummy_mrpro_epubs))
    output_dir = str(tmp_path / "output")

    progresses = []

    def progress_cb(current, total):
        progresses.append((current, total))

    count = EpubExporter.export(extractor, output_dir, progress_cb=progress_cb)

    assert count == 2
    assert progresses == [(1, 2), (2, 2)]


def test_export_epubs_exception_handling(dummy_mrpro_epubs, tmp_path, monkeypatch):
    extractor = MrproExtractor(str(dummy_mrpro_epubs))
    output_dir = str(tmp_path / "output")

    # Mock extract_file_to to raise an Exception
    def mock_extract_file_to(original_path, destination_path, zf=None):
        if original_path == "?/sdcard/Books/mybook1.epub":
            raise Exception("Mock error")
        else:
            # Simulate correct extraction for other files so we don't just fail everything
            with open(destination_path, "wb") as f:
                f.write(b"mocked_success")

    monkeypatch.setattr(extractor, "extract_file_to", mock_extract_file_to)

    count = EpubExporter.export(extractor, output_dir)
    # The first epub fails, the second one succeeds
    assert count == 1
