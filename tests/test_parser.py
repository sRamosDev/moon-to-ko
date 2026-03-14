# TEAM_001: Tests for the text replacement parser
from src.replacements_parser import ReplacementsParser


def test_parse_rules():
    content = b"Dr\\.#->#Doctor\nMr\\.#->#Mister\n#->#Ignored\n"
    rules = ReplacementsParser.parse(content)
    assert len(rules) == 2
    assert rules[0].pattern == "Dr\\."
    assert rules[0].replacement == "Doctor"


def test_format_lua_table():
    content = b"\\+1#->#plus one"
    rules = ReplacementsParser.parse(content)
    lua_str = ReplacementsParser.format_lua_table(rules)
    assert '["pattern"] = "\\\\+1"' in lua_str
    assert '["replace"] = "plus one"' in lua_str
