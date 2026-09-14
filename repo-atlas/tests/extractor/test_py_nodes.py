"""FileSymbols -> RawNode (EXTRACTOR_SPEC §1-§6)."""

from __future__ import annotations

import pytest

from repo_atlas.extractor import parse, py_nodes
from repo_atlas.extractor.models import ORIGIN_AST, ORIGIN_SCAN

_SRC = """class Polygon(Object):
    def __init__(self):
        pass


def calc(n):
    # TODO: tidy this up
    return n
"""


def _nodes(source: str = _SRC, path: str = "polygons/polygons.py") -> list:
    return py_nodes.build_nodes(parse.parse_source(path, source))


def _by_id(source: str = _SRC) -> dict:
    return {node.id: node for node in _nodes(source)}


def test_emits_a_module_node_anchored_at_line_one() -> None:
    module = _by_id()["polygons_polygons"]
    assert (module.label, module.source_location, module.file_type) == (
        "polygons.py",
        "L1",
        "code",
    )


def test_module_node_is_line_one_even_when_the_file_starts_blank() -> None:
    assert _by_id("\n\n\ndef f():\n    pass\n")["polygons_polygons"].source_location == "L1"


def test_class_and_method_ids_chain_correctly() -> None:
    ids = set(_by_id())
    assert "polygons_polygons_polygon" in ids
    assert "polygons_polygons_polygon_init" in ids


def test_method_label_omits_the_class() -> None:
    assert _by_id()["polygons_polygons_polygon_init"].label == ".__init__()"


def test_module_level_function_is_not_nested_under_the_class() -> None:
    assert _by_id()["polygons_polygons_calc"].label == "calc()"


def test_unresolved_base_class_becomes_an_external_node() -> None:
    external = _by_id()["object"]
    assert (external.label, external.source_file, external.source_location) == ("Object", "", "")


def test_a_base_defined_in_the_same_file_is_not_external() -> None:
    source = "class Base:\n    pass\n\n\nclass Child(Base):\n    pass\n"
    assert "base" not in _by_id(source)


def test_marker_comments_become_rationale_nodes() -> None:
    node = _by_id()["polygons_polygons_rationale_7"]
    assert (node.file_type, node.label, node.source_location) == (
        "rationale",
        "# TODO: tidy this up",
        "L7",
    )


def test_norm_label_is_the_lowercased_label() -> None:
    assert _by_id()["polygons_polygons_polygon"].norm_label == "polygon"


def test_a_clean_parse_marks_every_node_ast_origin() -> None:
    assert {node.origin for node in _nodes()} == {ORIGIN_AST}


def test_a_degraded_parse_marks_code_nodes_scan_but_rationale_stays_ast() -> None:
    """Rationale comes off the line stream, which never failed — it is not weaker."""
    source = 'print "py2"\n# TODO: port\nclass A:\n    pass\n'
    origins = {node.id: node.origin for node in _nodes(source)}
    assert origins["polygons_polygons_a"] == ORIGIN_SCAN
    assert origins["polygons_polygons_rationale_2"] == ORIGIN_AST


def test_output_is_deterministic() -> None:
    assert [n.id for n in _nodes()] == [n.id for n in _nodes()]


def test_duplicate_ids_raise_rather_than_silently_merging() -> None:
    """__init__ and init collapse to one id; a silently merged node is a wrong graph."""
    source = (
        "class A:\n    def __init__(self):\n        pass\n\n    def init(self):\n        pass\n"
    )
    with pytest.raises(ValueError, match="collide"):
        _nodes(source)
