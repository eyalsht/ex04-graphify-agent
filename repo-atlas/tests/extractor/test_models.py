"""The extractor data contract serializes exactly as the graph.json schema expects."""

from __future__ import annotations

import dataclasses

import pytest

from repo_atlas.extractor.models import ORIGIN_AST, ORIGIN_SCAN, FileSymbols, RawEdge, RawNode


def _node(**overrides: object) -> RawNode:
    fields: dict[str, object] = {
        "id": "pkg_mod_thing",
        "label": "thing()",
        "norm_label": "thing()",
        "file_type": "code",
        "source_file": "pkg/mod.py",
        "source_location": "L7",
        "origin": ORIGIN_AST,
    }
    fields.update(overrides)
    return RawNode(**fields)  # type: ignore[arg-type]


def _edge(**overrides: object) -> RawEdge:
    fields: dict[str, object] = {
        "source": "pkg_mod",
        "target": "pkg_mod_thing",
        "relation": "contains",
        "confidence": "EXTRACTED",
        "confidence_score": 1.0,
        "source_file": "pkg/mod.py",
        "source_location": "L7",
    }
    fields.update(overrides)
    return RawEdge(**fields)  # type: ignore[arg-type]


def test_node_serializes_origin_under_the_reference_key() -> None:
    assert _node().to_dict()["_origin"] == ORIGIN_AST
    assert "origin" not in _node().to_dict()


def test_node_dict_carries_every_schema_key() -> None:
    expected = {
        "label",
        "file_type",
        "source_file",
        "source_location",
        "_origin",
        "norm_label",
        "id",
    }
    assert set(_node().to_dict()) == expected


def test_edge_omits_context_when_absent() -> None:
    assert "context" not in _edge().to_dict()


def test_edge_includes_context_when_present() -> None:
    assert _edge(relation="calls", context="call").to_dict()["context"] == "call"


def test_edge_weight_defaults_to_one() -> None:
    assert _edge().weight == 1.0


def test_records_are_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        _node().id = "other"  # type: ignore[misc]


def test_file_symbols_defaults_to_a_clean_parse_with_nothing_found() -> None:
    empty = FileSymbols(source_file="pkg/mod.py")
    assert (empty.degraded, empty.symbols, empty.calls, empty.markers) == (False, (), (), ())


def test_scan_origin_is_distinct_from_ast_origin() -> None:
    assert ORIGIN_SCAN != ORIGIN_AST
