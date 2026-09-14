"""``GRAPH_REPORT.md`` rendering (PHASE1-024/026 follow-on, CLAUDE.md §4 claim discipline)."""

from __future__ import annotations

from repo_atlas.extractor import report
from repo_atlas.extractor.models import RawEdge, RawNode


def _node(node_id: str) -> RawNode:
    return RawNode(
        id=node_id,
        label=node_id.title(),
        norm_label=node_id,
        file_type="code",
        source_file=f"{node_id}.py",
        source_location="L1",
        origin="ast",
    )


def _edge(source: str, target: str, confidence: str = "EXTRACTED") -> RawEdge:
    return RawEdge(
        source=source,
        target=target,
        relation="calls",
        confidence=confidence,
        confidence_score=1.0 if confidence == "EXTRACTED" else 0.7,
        source_file=f"{source}.py",
        source_location="L1",
    )


_NODES = [_node(n) for n in ("a", "b", "c", "lonely")]
_EDGES = [_edge("a", "b"), _edge("b", "c", confidence="INFERRED")]
_COMMUNITY = {"a": 0, "b": 0, "c": 0, "lonely": 1}


def _render(**overrides):
    kwargs = {
        "nodes": _NODES,
        "edges": _EDGES,
        "community_of": _COMMUNITY,
        "repo_name": "demo-repo",
        "generated_at": "2026-01-01T00:00:00Z",
    }
    kwargs.update(overrides)
    return report.render_report(**kwargs)


def test_header_names_the_repo_and_date() -> None:
    text = _render()
    assert "demo-repo" in text
    assert "2026-01-01T00:00:00Z" in text


def test_totals_section_counts_nodes_edges_and_communities() -> None:
    text = _render()
    assert "Nodes: 4" in text
    assert "Edges: 2" in text
    assert "Communities: 2" in text


def test_confidence_breakdown_reports_percentages() -> None:
    text = _render()
    assert "EXTRACTED" in text
    assert "INFERRED" in text
    assert "50.0%" in text


def test_confidence_breakdown_handles_zero_edges() -> None:
    text = _render(edges=[])
    assert "no edges" in text.lower()


def test_most_connected_nodes_are_listed_with_degree() -> None:
    text = _render()
    b_line = next(line for line in text.splitlines() if line.strip().startswith("| b "))
    assert "2" in b_line


def test_per_community_node_lists() -> None:
    text = _render()
    assert "Community 0" in text
    assert "Community 1" in text
    idx_c0 = text.index("Community 0")
    idx_c1 = text.index("Community 1")
    section = text[idx_c0:idx_c1]
    assert "a" in section and "b" in section and "c" in section


def test_isolated_nodes_are_flagged_as_knowledge_gaps() -> None:
    text = _render()
    assert "lonely" in text
    assert "Knowledge gap" in text or "knowledge gap" in text


def test_no_isolated_nodes_says_so() -> None:
    text = _render(
        nodes=[_node("a"), _node("b")],
        edges=[_edge("a", "b")],
        community_of={"a": 0, "b": 0},
    )
    idx = text.index("Isolated")
    tail = text[idx : idx + 300]
    assert "none" in tail.lower()


def test_degraded_files_section_lists_the_given_files() -> None:
    text = _render(degraded_files=["polygons/polygons.py", "mathsquiz/mathsquiz.py"])
    assert "polygons/polygons.py" in text
    assert "mathsquiz/mathsquiz.py" in text
    assert "INFERRED" in text


def test_no_degraded_files_says_so() -> None:
    text = _render(degraded_files=[])
    idx = text.index("Degraded")
    tail = text[idx : idx + 300]
    assert "none" in tail.lower() or "cleanly" in tail.lower()


def test_render_report_is_a_pure_function_returning_a_string() -> None:
    assert isinstance(_render(), str)
    assert _render() == _render()


def test_write_report_writes_the_text(tmp_path) -> None:
    target = tmp_path / "nested" / "GRAPH_REPORT.md"
    report.write_report(target, "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"
