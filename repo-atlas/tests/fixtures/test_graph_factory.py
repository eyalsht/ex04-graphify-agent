"""Node/edge builder tests for ``tests/fixtures/graph_factory.py`` (PHASE1-001)."""

from __future__ import annotations

from tests.fixtures.graph_factory import make_edge, make_node


def test_make_node_applies_sensible_defaults() -> None:
    node = make_node("a")
    assert node == {
        "id": "a",
        "label": "a",
        "norm_label": "a",
        "file_type": "code",
        "source_file": "a.py",
        "source_location": "L1",
        "community": 0,
        "_origin": "ast",
    }


def test_make_node_norm_label_defaults_from_label_lowercased() -> None:
    node = make_node("a", label="Polygon")
    assert node["norm_label"] == "polygon"


def test_make_node_overrides_win() -> None:
    node = make_node(
        "a",
        label="Custom",
        file_type="document",
        source_file="docs/a.md",
        source_location="L42",
        community=3,
        origin="manual",
    )
    assert node["label"] == "Custom"
    assert node["file_type"] == "document"
    assert node["source_file"] == "docs/a.md"
    assert node["source_location"] == "L42"
    assert node["community"] == 3
    assert node["_origin"] == "manual"


def test_make_node_extra_kwargs_pass_through() -> None:
    node = make_node("a", source_url="https://example.com")
    assert node["source_url"] == "https://example.com"


def test_make_edge_applies_sensible_defaults() -> None:
    edge = make_edge("a", "b")
    assert edge == {
        "source": "a",
        "target": "b",
        "relation": "calls",
        "confidence": "EXTRACTED",
        "confidence_score": 1.0,
        "weight": 1.0,
        "source_file": "a.py",
        "source_location": "L1",
    }


def test_make_edge_inferred_defaults_below_extracted_score() -> None:
    edge = make_edge("a", "b", confidence="INFERRED")
    assert edge["confidence_score"] < 1.0


def test_make_edge_overrides_win() -> None:
    edge = make_edge(
        "a",
        "b",
        relation="inherits",
        confidence="AMBIGUOUS",
        confidence_score=0.42,
        weight=0.5,
        source_file="pkg/a.py",
        source_location="L9",
    )
    assert edge["relation"] == "inherits"
    assert edge["confidence"] == "AMBIGUOUS"
    assert edge["confidence_score"] == 0.42
    assert edge["weight"] == 0.5
    assert edge["source_file"] == "pkg/a.py"
    assert edge["source_location"] == "L9"
