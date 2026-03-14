# TEAM_001: Tests for the Moon+ Reader Pro database mapper
import pytest
import sqlite3
from src.db_mapper import DbMapper


@pytest.fixture
def dummy_db(tmp_path):
    db_path = tmp_path / "mrbooks.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE books (_id integer primary key autoincrement, book text, filename text, author text, description text, category text)
    """)
    cursor.execute("""
        CREATE TABLE statistics (_id integer primary key autoincrement, filename text, usedTime NUMERIC, readWords NUMERIC, dates text)
    """)
    cursor.execute("""
        CREATE TABLE notes (_id integer primary key autoincrement, filename text, lastChapter NUMERIC, bookmark text)
    """)

    cursor.execute(
        "INSERT INTO books (book, filename) VALUES ('Test Book', '/a/b.epub')"
    )
    cursor.execute(
        "INSERT INTO statistics (filename, usedTime) VALUES ('/a/b.epub', 1000)"
    )
    cursor.execute(
        "INSERT INTO notes (filename, lastChapter, bookmark) VALUES ('/a/b.epub', 12, '(62.8%) some text here')"
    )
    cursor.execute(
        "INSERT INTO notes (filename, lastChapter, bookmark) VALUES ('/c/d.epub', 5, 'no percentage text')"
    )

    conn.commit()
    conn.close()
    return db_path


def test_mapper_books(dummy_db):
    mapper = DbMapper(str(dummy_db))
    books = mapper.get_books()
    assert len(books) == 1
    assert books[0].title == "Test Book"


def test_mapper_stats(dummy_db):
    mapper = DbMapper(str(dummy_db))
    stats = mapper.get_statistics()
    assert len(stats) == 1
    assert stats[0].usedTime == 1000


def test_mapper_read_progress(dummy_db):
    mapper = DbMapper(str(dummy_db))
    prog = mapper.get_read_progresses()
    assert len(prog) == 2
    assert prog[0].percentage == 62.8
    assert prog[1].percentage == 0.0
