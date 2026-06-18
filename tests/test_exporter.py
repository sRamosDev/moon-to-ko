# TEAM_001: Tests for KOReader Exporter
import sqlite3
from src.db_mapper import BookRecord, ReadStatistic, ReadProgress
from src.koreader_exporter import KOReaderExporter


def test_export_statistics(tmp_path):
    exporter = KOReaderExporter(str(tmp_path))
    books = [
        BookRecord(
            id=1,
            title="Test 1",
            filename="/a/b.epub",
            author="Auth 1",
            description="",
            category="",
        ),
        BookRecord(
            id=2,
            title="Test 2",
            filename="/a/c.epub",
            author="Auth 2",
            description="",
            category="",
        ),
        BookRecord(
            id=3,
            title="Test 3",
            filename="/a/d.epub",
            author="Auth 3",
            description="",
            category="",
        ),
    ]
    stats = [
        ReadStatistic(filename="/a/b.epub", usedTime=150000, readWords=100, dates=""),
        ReadStatistic(filename="/a/c.epub", usedTime=5000, readWords=50, dates=""),
    ]

    exporter.export_statistics(books, stats)

    db_file = tmp_path / "statistics.sqlite3"
    assert db_file.exists()

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, authors, total_read_time FROM book ORDER BY id")
        rows = cursor.fetchall()
        assert len(rows) == 3

        # Book 1: usedTime > 10000
        assert rows[0][0] == "Test 1"
        assert rows[0][1] == "Auth 1"
        assert rows[0][2] == 150  # 150000 // 1000

        # Book 2: usedTime <= 10000
        assert rows[1][0] == "Test 2"
        assert rows[1][1] == "Auth 2"
        assert rows[1][2] == 5000

        # Book 3: No ReadStatistic
        assert rows[2][0] == "Test 3"
        assert rows[2][1] == "Auth 3"
        assert rows[2][2] == 0


def test_export_sdr_folders(tmp_path):
    exporter = KOReaderExporter(str(tmp_path))
    progs = [
        ReadProgress(
            filename="/sdcard/Books/mybook.epub",
            percentage=62.8,
            last_chapter=1,
            bookmark_text="",
        ),
        ReadProgress(
            filename="/sdcard/Books/mybook_no_replacer.epub",
            percentage=100.0,
            last_chapter=1,
            bookmark_text="",
        )
    ]

    book_rules_map = {
        "mybook.epub": '{\n        ["replacements"] = {\n            ["foo"] = "bar"\n        }\n    }'
    }

    exporter.export_sdr_folders(progs, book_rules_map=book_rules_map)

    sdr_dir = tmp_path / "mybook.sdr"
    assert sdr_dir.is_dir()

    lua_file = sdr_dir / "metadata.epub.lua"
    assert lua_file.exists()

    content = lua_file.read_text()
    assert '["percent_finished"] = 0.628' in content
    assert '["status"] = "reading"' in content
    assert '["htmlreplacer"] =' in content
    assert '["foo"] = "bar"' in content

    sdr_dir_no_replacer = tmp_path / "mybook_no_replacer.sdr"
    assert sdr_dir_no_replacer.is_dir()

    lua_file_no_replacer = sdr_dir_no_replacer / "metadata.epub.lua"
    assert lua_file_no_replacer.exists()

    content_no_replacer = lua_file_no_replacer.read_text()
    assert '["htmlreplacer"] =' not in content_no_replacer
