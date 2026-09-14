"""FileSymbols + FileNodes -> RawEdge (EXTRACTOR_SPEC §5, §6)."""

from __future__ import annotations

from repo_atlas.extractor import parse, py_edges, py_nodes

_SRC = '''class Polygon(Object):
    def __init__(self):
        pass


def calc(n):
    # TODO: tidy
    poly = Polygon(n)
    print(n)
    turtle.forward(n)
    return poly


calc(3)
'''


def _edges(source: str = _SRC, path: str = "polygons/polygons.py") -> list:
    parsed = parse.parse_source(path, source)
    return py_edges.build_edges(parsed, py_nodes.build_file_nodes(parsed))


def _triples(source: str = _SRC) -> set[tuple[str, str, str]]:
    return {(e.relation, e.source, e.target) for e in _edges(source)}


def test_contains_links_the_module_to_top_level_symbols() -> None:
    triples = _triples()
    assert ("contains", "polygons_polygons", "polygons_polygons_polygon") in triples
    assert ("contains", "polygons_polygons", "polygons_polygons_calc") in triples


def test_contains_never_reaches_a_method() -> None:
    """§5: contains is top-level only; methods hang off their class via `method`."""
    assert ("contains", "polygons_polygons", "polygons_polygons_polygon_init") not in _triples()


def test_method_links_the_class_to_its_method() -> None:
    assert ("method", "polygons_polygons_polygon", "polygons_polygons_polygon_init") in _triples()


def test_inherits_points_at_the_unresolved_base() -> None:
    assert ("inherits", "polygons_polygons_polygon", "object") in _triples()


def test_calls_links_caller_to_a_callee_defined_in_the_same_file() -> None:
    assert ("calls", "polygons_polygons_calc", "polygons_polygons_polygon") in _triples()


def test_builtins_do_not_produce_call_edges() -> None:
    assert not [e for e in _edges() if e.target == "print"]


def test_attribute_calls_do_not_produce_call_edges() -> None:
    assert not [e for e in _edges() if e.target.endswith("forward")]


def test_module_level_calls_produce_no_edge() -> None:
    """`calc(3)` at module level is a real call, but the reference emits nothing for it."""
    assert not [e for e in _edges() if e.source == "polygons_polygons" and e.relation == "calls"]


def test_calls_edges_carry_the_call_context_marker() -> None:
    call = next(e for e in _edges() if e.relation == "calls")
    assert call.context == "call"
    assert call.source_location == "L8"


def test_only_calls_edges_carry_context() -> None:
    assert {e.context for e in _edges() if e.relation != "calls"} == {None}


def test_rationale_for_points_from_the_comment_to_the_module() -> None:
    """Inverted relative to contains, and it targets the module even inside a function."""
    assert ("rationale_for", "polygons_polygons_rationale_7", "polygons_polygons") in _triples()


def test_no_import_edges_are_emitted() -> None:
    edges = _edges("import os\nimport sys\n\n\ndef f():\n    pass\n")
    assert {e.relation for e in edges} == {"contains"}


def test_a_clean_parse_yields_extracted_edges_at_full_confidence() -> None:
    contains = next(e for e in _edges() if e.relation == "contains")
    assert (contains.confidence, contains.confidence_score, contains.weight) == (
        "EXTRACTED",
        1.0,
        1.0,
    )


def test_a_degraded_file_yields_inferred_edges() -> None:
    source = 'print "py2"\nclass A(Base):\n    def m(self):\n        pass\n'
    for edge in _edges(source):
        assert (edge.confidence, edge.confidence_score) == ("INFERRED", 0.7)


def test_contains_anchors_to_the_targets_definition_line() -> None:
    contains = next(
        e for e in _edges() if e.relation == "contains" and e.target.endswith("_calc")
    )
    assert contains.source_location == "L6"


def test_inherits_anchors_to_the_class_header_line() -> None:
    assert next(e for e in _edges() if e.relation == "inherits").source_location == "L1"


def test_output_is_deterministic() -> None:
    first = [(e.relation, e.source, e.target) for e in _edges()]
    assert first == [(e.relation, e.source, e.target) for e in _edges()]
