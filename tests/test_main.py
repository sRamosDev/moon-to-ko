import pytest
import zipfile
from unittest.mock import patch

from src.main import run_migration, main


def test_run_migration_file_not_found(tmp_path):
    input_file = tmp_path / "non_existent_file.mrpro"
    output_dir = tmp_path / "some_output_dir"

    # Ensure the file really does not exist
    input_file_str = str(input_file)
    output_dir_str = str(output_dir)

    with pytest.raises(FileNotFoundError) as excinfo:
        run_migration(input_file_str, output_dir_str, False, False)

    assert str(excinfo.value) == f"Input file '{input_file_str}' does not exist."


def test_run_migration(tmp_path):
    input_file = tmp_path / "test.mrpro"
    output_dir = tmp_path / "output"

    with zipfile.ZipFile(input_file, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        zf.writestr("com.flyersoft.moonreaderp/1.tag", b"")

    # We need a proper DB for run_migration so let's write a small valid sqlite db instead
    import sqlite3

    db_path = tmp_path / "fake.db"
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
    conn.commit()
    conn.close()

    with zipfile.ZipFile(input_file, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n?/sdcard/Books/mybook.epub\ncom.flyersoft.moonreaderp/shared_prefs/names_replacement\ncom.flyersoft.moonreaderp/shared_prefs/mybook.epub.r\n",
        )
        with open(db_path, "rb") as f:
            zf.writestr("com.flyersoft.moonreaderp/1.tag", f.read())

        zf.writestr("com.flyersoft.moonreaderp/2.tag", b"epub content")
        zf.writestr("com.flyersoft.moonreaderp/3.tag", b"A#->#B\n")
        zf.writestr("com.flyersoft.moonreaderp/4.tag", b"C#->#D\n")

    run_migration(
        str(input_file),
        str(output_dir),
        extract_epubs=True,
        extract_replacements=True,
    )

    assert (output_dir / "statistics.sqlite3").exists()
    assert (output_dir / "books" / "mybook.epub").exists()
    assert (output_dir / "replacements" / "htmlreplacer_global.lua").exists()


def test_run_migration_input_not_found(tmp_path):
    with pytest.raises(
        FileNotFoundError, match="Input file 'notfound.mrpro' does not exist."
    ):
        run_migration("notfound.mrpro", str(tmp_path / "out"), False, False)


def test_main_cli_success(tmp_path, monkeypatch):
    input_file = tmp_path / "test.mrpro"
    output_dir = tmp_path / "output"

    with zipfile.ZipFile(input_file, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )

    import sqlite3

    db_path = tmp_path / "fake.db"
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
    conn.commit()
    conn.close()

    with zipfile.ZipFile(input_file, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        with open(db_path, "rb") as f:
            zf.writestr("com.flyersoft.moonreaderp/1.tag", f.read())

    test_args = ["src.main", "-i", str(input_file), "-o", str(output_dir)]

    with patch("sys.argv", test_args):
        main()


def test_main_cli_exception(tmp_path):
    test_args = ["src.main", "-i", "nonexistent.mrpro", "-o", "out"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1


def test_run_migration_status_cb(tmp_path):
    input_file = tmp_path / "test.mrpro"
    output_dir = tmp_path / "output"

    import sqlite3

    db_path = tmp_path / "fake.db"
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
    conn.commit()
    conn.close()

    with zipfile.ZipFile(input_file, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        with open(db_path, "rb") as f:
            zf.writestr("com.flyersoft.moonreaderp/1.tag", f.read())

    msgs = []

    def status_cb(msg):
        msgs.append(msg)

    run_migration(
        str(input_file),
        str(output_dir),
        extract_epubs=False,
        extract_replacements=False,
        status_cb=status_cb,
    )

    assert len(msgs) > 0
    assert msgs[0].startswith("Starting migration")
