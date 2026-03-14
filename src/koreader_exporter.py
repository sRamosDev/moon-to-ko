# TEAM_001: Exports parsed records to KOReader statistics.sqlite and .sdr Lua sidecars
import sqlite3
import os
from typing import List
from src.db_mapper import BookRecord, ReadStatistic, ReadProgress


class KOReaderExporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.db_path = os.path.join(self.output_dir, "statistics.sqlite3")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS book (
                    id integer PRIMARY KEY autoincrement,
                    title text,
                    authors text,
                    notes integer,
                    last_open integer,
                    highlights integer,
                    pages integer,
                    series text,
                    language text,
                    md5 text,
                    total_read_time integer,
                    total_read_pages integer
                )
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS book_title_authors_md5 ON book(title, authors, md5)
            """)
            conn.commit()
        finally:
            conn.close()

    def export_statistics(self, books: List[BookRecord], stats: List[ReadStatistic]):
        self._init_db()

        # We join books with stats to get total read time
        # Moon+ usedTime is roughly in milliseconds or seconds? We'll just pass it directly as seconds
        # (KOReader total_read_time is in seconds)
        stat_map = {s.filename: s for s in stats}

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            for b in books:
                s = stat_map.get(b.filename)
                total_time = (
                    s.usedTime // 1000
                    if s and s.usedTime > 10000
                    else (s.usedTime if s else 0)
                )
                # Just insert what we have
                cursor.execute(
                    """
                    INSERT INTO book (title, authors, total_read_time)
                    VALUES (?, ?, ?)
                """,
                    (b.title, b.author, total_time),
                )
            conn.commit()
        finally:
            conn.close()

    def export_sdr_folders(
        self, progresses: List[ReadProgress], book_rules_map: dict = None
    ):
        book_rules_map = book_rules_map or {}

        # Collect all books that need an .sdr (either because of progress or rules)
        all_basenames = set(
            [os.path.basename(p.filename) for p in progresses if p.filename]
        )
        all_basenames.update(book_rules_map.keys())

        prog_map = {os.path.basename(p.filename): p for p in progresses if p.filename}

        for basename in all_basenames:
            name_ext = os.path.splitext(basename)
            sdr_dir = os.path.join(self.output_dir, f"{name_ext[0]}.sdr")
            os.makedirs(sdr_dir, exist_ok=True)
            lua_file = os.path.join(sdr_dir, f"metadata.{name_ext[1].lstrip('.')}.lua")

            p = prog_map.get(basename)
            rules_lua = book_rules_map.get(basename)

            lines = ["return {"]
            if p:
                percent_float = p.percentage / 100.0 if p.percentage > 0 else 0.0
                status = "complete" if percent_float >= 0.99 else "reading"
                lines.append(f'    ["percent_finished"] = {percent_float},')
                lines.append(
                    f'    ["summary"] = {{\n        ["status"] = "{status}"\n    }},'
                )

            if rules_lua:
                lines.append(f'    ["htmlreplacer"] = {rules_lua},')

            # Strip trailing comma from last item if present
            if lines[-1].endswith(","):
                lines[-1] = lines[-1][:-1]

            lines.append("}")

            with open(lua_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
