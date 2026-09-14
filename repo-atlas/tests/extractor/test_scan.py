"""Degraded line-scan recovery (EXTRACTOR_SPEC §7).

These cases are all files that raise SyntaxError. The reference corpus contains two of
them, and one carries roughly half the graph's structure, so "give up on the file" is
not an acceptable behaviour.
"""

from __future__ import annotations

from repo_atlas.extractor import parse, scan

_PY2 = 'print "hello"\n\n\nclass Quiz(Base):\n    def ask(self):\n        pass\n'
_JS_NEW = (
    "class Polygon(Object):\n    def __init__(self):\n        pass\n\n\n"
    "def calc(n):\n    p = new Polygon(n)\n    return p\n"
)


def _symbols(source: str) -> list[tuple[str, str, int, str | None]]:
    result = parse.parse_source("m.py", source)
    return [(s.kind, s.name, s.lineno, s.parent) for s in result.symbols]


def test_a_python2_file_still_yields_its_structure() -> None:
    assert parse.parse_source("m.py", _PY2).degraded is True
    assert _symbols(_PY2) == [("class", "Quiz", 4, None), ("method", "ask", 5, "Quiz")]


def test_a_file_with_foreign_syntax_still_yields_its_structure() -> None:
    """The reference's polygons.py fails on a JavaScript `new`; we keep 4 of its symbols."""
    assert _symbols(_JS_NEW) == [
        ("class", "Polygon", 1, None),
        ("method", "__init__", 2, "Polygon"),
        ("function", "calc", 6, None),
    ]


def test_base_classes_survive_the_degraded_path() -> None:
    assert parse.parse_source("m.py", _PY2).symbols[0].bases == ("Base",)


def test_multiple_base_classes_are_split() -> None:
    assert scan.scan_source("m.py", "class A(B, C):\n").symbols[0].bases == ("B", "C")


def test_a_class_with_no_bases_records_none() -> None:
    assert scan.scan_source("m.py", "class A:\n").symbols[0].bases == ()


def test_a_def_dedented_back_to_module_level_is_not_a_method() -> None:
    source = "class A:\n    def m(self):\n        pass\n\n\ndef free():\n    pass\n"
    assert _symbols(source)[-1] == ("function", "free", 6, None)


def test_async_def_is_recovered() -> None:
    assert scan.scan_source("m.py", "async def fetch():\n").symbols[0].name == "fetch"


def test_call_sites_are_not_recovered() -> None:
    """A line scan cannot resolve scope; a wrong edge is worse than a missing one."""
    assert parse.parse_source("m.py", _JS_NEW).calls == ()


def test_markers_still_come_through_on_an_unparseable_file() -> None:
    result = parse.parse_source("m.py", 'print "py2"\n# TODO: port me\n')
    assert [m.text for m in result.markers] == ["# TODO: port me"]


def test_a_second_class_at_the_same_indent_closes_the_first() -> None:
    """Otherwise the next class's methods get attributed to the previous class."""
    # The leading Python-2 print forces the degraded path; valid source takes the AST.
    source = (
        'print "py2"\n'
        "class A:\n    def a(self):\n        pass\n\n\n"
        "class B:\n    def b(self):\n        pass\n"
    )
    assert _symbols(source) == [
        ("class", "A", 2, None),
        ("method", "a", 3, "A"),
        ("class", "B", 7, None),
        ("method", "b", 8, "B"),
    ]
