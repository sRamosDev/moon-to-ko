import pytest
import os
import zipfile
from src.replacements_exporter import ReplacementsExporter
from src.mrpro_extractor import MrproExtractor


@pytest.fixture
def dummy_mrpro_replacements(tmp_path):
    mrpro_path = tmp_path / "test_reps.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/shared_prefs/names_replacement\ncom.flyersoft.moonreaderp/shared_prefs/book1.epub.r\ncom.flyersoft.moonreaderp/shared_prefs/book2.epub.r\ncom.flyersoft.moonreaderp/shared_prefs/book3.epub.r\n",
        )
        # Global replacements
        zf.writestr(
            "com.flyersoft.moonreaderp/1.tag", b"Dr\\.#->#Doctor\nMr\\.#->#Mister\n"
        )
        # Book 1 replacements
        zf.writestr("com.flyersoft.moonreaderp/2.tag", b"foo#->#bar\n")
        # Book 2 replacements - empty but valid file
        zf.writestr("com.flyersoft.moonreaderp/3.tag", b"")
        # Book 3 - simulate file not found by not creating the tag file, but the names list thinks it's there
    return mrpro_path


def test_export_global_rules(dummy_mrpro_replacements, tmp_path):
    extractor = MrproExtractor(str(dummy_mrpro_replacements))
    output_dir = str(tmp_path / "output")

    count = ReplacementsExporter.export_global_rules(extractor, output_dir)
    assert count == 2

    rep_dir = os.path.join(output_dir, "replacements")
    assert os.path.exists(rep_dir)

    lua_file = os.path.join(rep_dir, "htmlreplacer_global.lua")
    assert os.path.exists(lua_file)
    with open(lua_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Doctor" in content
        assert "Mister" in content


def test_export_global_rules_not_found(tmp_path):
    mrpro_path = tmp_path / "test_no_global.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/databases/mrbooks.db\n",
        )
        zf.writestr("com.flyersoft.moonreaderp/1.tag", b"db_data")

    extractor = MrproExtractor(str(mrpro_path))
    output_dir = str(tmp_path / "output")

    count = ReplacementsExporter.export_global_rules(extractor, output_dir)
    assert count == 0


def test_export_global_rules_empty(tmp_path):
    mrpro_path = tmp_path / "test_empty_global.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/shared_prefs/names_replacement\n",
        )
        zf.writestr("com.flyersoft.moonreaderp/1.tag", b"")

    extractor = MrproExtractor(str(mrpro_path))
    output_dir = str(tmp_path / "output")

    count = ReplacementsExporter.export_global_rules(extractor, output_dir)
    assert count == 0


def test_export_global_rules_invalid(tmp_path):
    mrpro_path = tmp_path / "test_invalid_global.mrpro"
    with zipfile.ZipFile(mrpro_path, "w") as zf:
        zf.writestr(
            "com.flyersoft.moonreaderp/_names.list",
            "com.flyersoft.moonreaderp/shared_prefs/names_replacement\n",
        )
        # Invalid content, parse returns empty list
        zf.writestr(
            "com.flyersoft.moonreaderp/1.tag", b"justsometextwithoutseparator\n"
        )

    extractor = MrproExtractor(str(mrpro_path))
    output_dir = str(tmp_path / "output")

    count = ReplacementsExporter.export_global_rules(extractor, output_dir)
    assert count == 0


def test_extract_book_rules(dummy_mrpro_replacements):
    extractor = MrproExtractor(str(dummy_mrpro_replacements))

    book_rules_map = ReplacementsExporter.extract_book_rules(extractor)

    assert "book1.epub" in book_rules_map
    assert "foo" in book_rules_map["book1.epub"]
    assert "bar" in book_rules_map["book1.epub"]

    assert "book2.epub" not in book_rules_map
    assert "book3.epub" not in book_rules_map
