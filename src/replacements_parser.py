# TEAM_001: Parses Text Replacements from Moon+ into KOReader htmlreplacer Lua format
import typing


class ReplacementRule:
    def __init__(self, pattern: str, replacement: str):
        self.pattern = pattern
        self.replacement = replacement


class ReplacementsParser:
    @staticmethod
    def parse(content: bytes) -> typing.List[ReplacementRule]:
        if not content:
            return []
        rules = []
        lines = content.decode("utf-8", errors="ignore").splitlines()
        for line in lines:
            line = line.strip()
            if not line or "#->#" not in line:
                continue
            parts = line.split("#->#", 1)
            if not parts[0]:
                continue
            # Both ends might have trailing spaces depending on what user entered,
            # but assume exact splits.
            rules.append(ReplacementRule(parts[0], parts[1]))
        return rules

    @staticmethod
    def format_lua_table(rules: typing.List[ReplacementRule]) -> str:
        if not rules:
            return ""
        lua_rules = []
        for r in rules:
            # Escape for Lua strings
            pat = (
                r.pattern.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            )
            rep = (
                r.replacement.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
            )
            lua_rules.append(f"""        {{
            ["pattern"] = "{pat}",
            ["replace"] = "{rep}",
            ["description"] = "Imported Moon+ rule"
        }}""")
        return "{\n" + ",\n".join(lua_rules) + "\n    }"
