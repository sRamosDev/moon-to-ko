# TEAM_001: Maps the Moon+ Reader SQLite database to generic Python objects
import sqlite3
import typing
from dataclasses import dataclass


@dataclass
class BookRecord:
    id: int
    title: str
    filename: str
    author: str
    description: str
    category: str
    # There are other fields like addTime, coverFile, but we primarily need the core metadata


@dataclass
class ReadStatistic:
    filename: str
    usedTime: int
    readWords: int
    dates: str


@dataclass
class ReadProgress:
    filename: str
    percentage: float  # e.g., 62.8 for 62.8%
    last_chapter: int
    bookmark_text: str


class DbMapper:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_books(self) -> typing.List[BookRecord]:
        books = []
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT _id, book, filename, author, description, category FROM books"
            )
            for row in cursor.fetchall():
                books.append(
                    BookRecord(
                        id=row["_id"],
                        title=row["book"],
                        filename=row["filename"],
                        author=row["author"],
                        description=row["description"],
                        category=row["category"],
                    )
                )
        finally:
            conn.close()
        return books

    def get_statistics(self) -> typing.List[ReadStatistic]:
        stats = []
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT filename, usedTime, readWords, dates FROM statistics"
            )
            for row in cursor.fetchall():
                stats.append(
                    ReadStatistic(
                        filename=row["filename"],
                        usedTime=row["usedTime"],
                        readWords=row["readWords"],
                        dates=row["dates"],
                    )
                )
        finally:
            conn.close()
        return stats

    def get_read_progresses(self) -> typing.List[ReadProgress]:
        import re

        # Regex to extract numeric percentage at start of bookmark text e.g. "(62.8%)"
        pct_regex = re.compile(r"^\((\d+(?:\.\d+)?)\%\)")
        progresses = []
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # `notes` table holds bookmarks. Progress bookmarks are usually prefixed with (XX.X%)
            cursor.execute("SELECT filename, lastChapter, bookmark FROM notes")
            for row in cursor.fetchall():
                bookmark = row["bookmark"] or ""
                match = pct_regex.search(bookmark)
                pct = float(match.group(1)) if match else 0.0

                progresses.append(
                    ReadProgress(
                        filename=row["filename"],
                        percentage=pct,
                        last_chapter=row["lastChapter"] or 0,
                        bookmark_text=bookmark,
                    )
                )
        finally:
            conn.close()
        return progresses
