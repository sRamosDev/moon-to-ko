# TEAM_001: Orchestrates extraction of Global and Book-specific text replacements from .mrpro into Lua formats.
import os

from src.replacements_parser import ReplacementsParser


class ReplacementsExporter:
    @staticmethod
    def export_global_rules(extractor, output_dir: str) -> int:
        global_content = extractor.get_file_content(
            "com.flyersoft.moonreaderp/shared_prefs/names_replacement"
        )
        if not global_content:
            return 0

        rules = ReplacementsParser.parse(global_content)
        if rules:
            lua_str = ReplacementsParser.format_lua_table(rules)
            rep_dir = os.path.join(output_dir, "replacements")
            os.makedirs(rep_dir, exist_ok=True)
            with open(
                os.path.join(rep_dir, "htmlreplacer_global.lua"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("return " + lua_str + "\n")
            return len(rules)
        return 0

    @staticmethod
    def extract_book_rules(extractor) -> dict:
        book_rules_map = {}
        paths = extractor.get_all_original_paths()
        book_rules = [
            p
            for p in paths
            if p.startswith("com.flyersoft.moonreaderp/shared_prefs/")
            and p.endswith(".r")
        ]
        for rule_path in book_rules:
            basename = os.path.basename(rule_path)
            original_book = basename[:-2] if basename.endswith(".r") else basename
            content = extractor.get_file_content(rule_path)
            if content:
                rules = ReplacementsParser.parse(content)
                if rules:
                    lua_str = ReplacementsParser.format_lua_table(rules)
                    book_rules_map[original_book] = lua_str
        return book_rules_map
