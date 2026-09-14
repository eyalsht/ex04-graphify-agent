"""AST parsing into FileSymbols (EXTRACTOR_SPEC §7)."""

from __future__ import annotations

from repo_atlas.extractor import parse

_CLEAN = '''
class Polygon(Object):
    """Doc."""

    def __init__(self, sides):
        self.sides = sides


def calc(sides):
    poly = Polygon(sides)
    print(sides)
    return poly


def draw(details):
    turtle.forward(10)
'''


def _parsed() -> object:
    return parse.parse_source("polygons/polygons.py", _CLEAN)


def _kinds(source: str = _CLEAN) -> list[tuple[str, str, int]]:
    result = parse.parse_source("m.py", source)
    return [(s.kind, s.name, s.lineno) for s in result.symbols]


def test_a_clean_parse_is_not_degraded() -> None:
    assert parse.parse_source("m.py", _CLEAN).degraded is False


def test_finds_classes_functions_and_methods_with_their_def_lines() -> None:
    assert _kinds() == [
        ("class", "Polygon", 2),
        ("method", "__init__", 5),
        ("function", "calc", 9),
        ("function", "draw", 15),
    ]


def test_method_records_its_enclosing_class() -> None:
    method = next(s for s in parse.parse_source("m.py", _CLEAN).symbols if s.kind == "method")
    assert method.parent == "Polygon"


def test_base_classes_are_recorded_as_written() -> None:
    cls = parse.parse_source("m.py", _CLEAN).symbols[0]
    assert cls.bases == ("Object",)


def test_dotted_base_class_is_kept_whole() -> None:
    cls = parse.parse_source("m.py", "class A(mod.Base):\n    pass\n").symbols[0]
    assert cls.bases == ("mod.Base",)


def test_call_sites_record_the_enclosing_symbol() -> None:
    calls = {(c.callee, c.enclosing, c.is_attribute) for c in _parsed().calls}  # type: ignore[attr-defined]
    assert ("Polygon", "calc", False) in calls
    assert ("print", "calc", False) in calls


def test_attribute_calls_are_flagged_not_dropped() -> None:
    """Selection is the edge layer's job; parsing only records what it saw."""
    calls = {(c.callee, c.is_attribute) for c in _parsed().calls}  # type: ignore[attr-defined]
    assert ("forward", True) in calls


def test_module_level_calls_have_no_enclosing_symbol() -> None:
    result = parse.parse_source("m.py", "def f():\n    pass\n\n\nf()\n")
    assert [(c.callee, c.enclosing) for c in result.calls] == [("f", None)]


def test_nested_function_chains_off_its_parent() -> None:
    result = parse.parse_source("m.py", "def outer():\n    def inner():\n        pass\n")
    nested = [(s.kind, s.name, s.parent) for s in result.symbols]
    assert nested == [("function", "outer", None), ("function", "inner", "outer")]


def test_async_def_is_treated_as_a_function() -> None:
    result = parse.parse_source("m.py", "async def fetch():\n    pass\n")
    assert [(s.kind, s.name) for s in result.symbols] == [("function", "fetch")]


def test_markers_are_collected_alongside_symbols() -> None:
    result = parse.parse_source("m.py", "# TODO: later\ndef f():\n    pass\n")
    assert [m.lineno for m in result.markers] == [1]


def test_source_file_is_carried_through() -> None:
    assert parse.parse_source("pkg/mod.py", "").source_file == "pkg/mod.py"


def test_a_call_on_an_expression_yields_no_callee() -> None:
    """``factory()()`` and lambda calls have no name to resolve — record nothing."""
    result = parse.parse_source("m.py", "def f():\n    (lambda: 1)()\n")
    assert result.calls == ()
