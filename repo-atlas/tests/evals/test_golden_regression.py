"""Golden regression: our AST extractor vs the reference graph (ADR-0001, SPEC §10).

This is the eval that says the extractor is *correct*, not merely that it runs. It must
hold on every run. A failure here means the graph is wrong, not that a test is stale.
"""

from __future__ import annotations

import pytest

from tests.evals import golden

_ATTRS = ("label", "file_type", "source_file", "source_location", "norm_label")


@pytest.fixture(scope="module")
def extracted() -> tuple[dict[str, object], list[object], set[str]]:
    return golden.extract()


@pytest.mark.eval
def test_reproduces_every_in_scope_node_id(extracted) -> None:  # type: ignore[no-untyped-def]
    nodes, _, _ = extracted
    assert set(nodes) == set(golden.reference_ast_nodes())


@pytest.mark.eval
def test_every_node_matches_the_reference_attribute_for_attribute(extracted) -> None:  # type: ignore[no-untyped-def]
    nodes, _, _ = extracted
    for node_id, reference_node in sorted(golden.reference_ast_nodes().items()):
        ours = nodes[node_id]
        assert tuple(getattr(ours, attr) for attr in _ATTRS) == tuple(
            reference_node[attr] for attr in _ATTRS
        ), node_id


@pytest.mark.eval
def test_document_pipeline_nodes_are_absent(extracted) -> None:  # type: ignore[no-untyped-def]
    """We do not invent semantic nodes we cannot derive from source (ADR-0001)."""
    nodes, _, _ = extracted
    assert golden.EXCLUDED_NODES.isdisjoint(nodes)


@pytest.mark.eval
def test_reproduces_every_in_scope_edge_except_the_documented_miss(extracted) -> None:  # type: ignore[no-untyped-def]
    _, edges, _ = extracted
    ours = {(e.relation, e.source, e.target) for e in edges}
    assert golden.reference_in_scope_edges() - ours == {golden.KNOWN_MISS}


@pytest.mark.eval
def test_emits_no_edge_the_reference_does_not_have(extracted) -> None:  # type: ignore[no-untyped-def]
    _, edges, _ = extracted
    ours = {(e.relation, e.source, e.target) for e in edges}
    assert ours - golden.reference_in_scope_edges() == set()


@pytest.mark.eval
def test_the_two_unparseable_files_still_yield_their_structure(extracted) -> None:  # type: ignore[no-untyped-def]
    """The regression guard for §7: swap in a strict ast.parse and this fails first."""
    nodes, _, degraded = extracted
    assert degraded == {"mathsquiz/mathsquiz.py", "polygons/polygons.py"}
    recovered = {
        "polygons_polygons_polygon",
        "polygons_polygons_polygon_init",
        "polygons_polygons_calc_polygon_details",
        "polygons_polygons_draw_polygon",
    }
    assert recovered <= set(nodes)


@pytest.mark.eval
def test_marker_comments_survive_an_unparseable_file(extracted) -> None:  # type: ignore[no-untyped-def]
    nodes, _, _ = extracted
    assert {"polygons_polygons_rationale_18", "polygons_polygons_rationale_33"} <= set(nodes)


@pytest.mark.eval
def test_no_import_edges_are_emitted(extracted) -> None:  # type: ignore[no-untyped-def]
    """Negative constraint: the corpus imports turtle and random, the reference links neither."""
    _, edges, _ = extracted
    assert not [e for e in edges if e.relation == "references"]
