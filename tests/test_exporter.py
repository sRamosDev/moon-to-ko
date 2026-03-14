# TEAM_001: Tests for KOReader Exporter
import sqlite3
from src.db_mapper import BookRecord, ReadStatistic, ReadProgress
from src.koreader_exporter import KOReaderExporter


def test_export_statistics(tmp_path):
    exporter = KOReaderExporter(str(tmp_path))
    books = [
        BookRecord(
            id=1,
            title="Test",
            filename="/a/b.epub",
            author="Auth",
            description="",
            category="",
        )
    ]
    stats = [
        ReadStatistic(filename="/a/b.epub", usedTime=150000, readWords=100, dates="")
    ]

    exporter.export_statistics(books, stats)

    db_file = tmp_path / "statistics.sqlite3"
    assert db_file.exists()

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, authors, total_read_time FROM book")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "Test"
        assert rows[0][1] == "Auth"
        assert rows[0][2] == 150  # 150000 // 1000


def test_export_sdr_folders(tmp_path):
    exporter = KOReaderExporter(str(tmp_path))
    progs = [
        ReadProgress(
            filename="/sdcard/Books/mybook.epub",
            percentage=62.8,
            last_chapter=1,
            bookmark_text="",
        )
    ]

    exporter.export_sdr_folders(progs)

    sdr_dir = tmp_path / "mybook.sdr"
    assert sdr_dir.is_dir()

    lua_file = sdr_dir / "metadata.epub.lua"
    assert lua_file.exists()

    content = lua_file.read_text()
    assert '["percent_finished"] = 0.628' in content
    assert '["status"] = "reading"' in content
