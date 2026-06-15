"""TDD for the six PART-C signals against the REAL graph.json (WD-T1..5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.weakness_detector import WeaknessDetector


@pytest.fixture
def detector(graph_json_path: Path) -> WeaknessDetector:
    return WeaknessDetector(GraphReader(graph_json_path))


def test_signal_1_god_node(detector: WeaknessDetector) -> None:  # WD-T1
    findings = detector.signal_1_god_node()
    assert findings, "expected the Polygon god node to fire"
    f = findings[0]
    assert f.signal == 1
    assert f.tag == "EXTRACTED"
    assert f.priority == "primary"
    assert "polygons_polygons_polygon" in f.nodes
    assert "Polygon" in f.hypothesis
    assert "bridges" in f.hypothesis or " is " in f.hypothesis
    assert "may" not in f.hypothesis and "suggests" not in f.hypothesis


def test_signal_1_threshold_from_config(graph_json_path: Path, tmp_path: Path) -> None:
    cfg = tmp_path / "th.json"
    cfg.write_text('{"god_node_min_degree": 99}', encoding="utf-8")
    det = WeaknessDetector(GraphReader(graph_json_path), thresholds_path=cfg)
    assert det.signal_1_god_node() == []


def test_signal_2_ambiguous_edge(detector: WeaknessDetector) -> None:  # WD-T3
    findings = detector.signal_2_ambiguous_edge()
    assert findings
    assert all(f.tag == "INFERRED" and f.priority == "secondary" for f in findings)
    pairs = {tuple(sorted(f.edges[0])) for f in findings}
    assert tuple(sorted(("mathsquiz_readme_maths_quiz", "readme_broken_python"))) in pairs
    assert all("suggests" in f.hypothesis or "may" in f.hypothesis for f in findings)


def test_signal_2_no_crash_on_zero_ambiguous(detector: WeaknessDetector) -> None:  # WD-E2
    # The real graph has 0 AMBIGUOUS edges; signal 2 must still work off INFERRED.
    assert detector._reader.edges_with_confidence("AMBIGUOUS") == []
    assert detector.signal_2_ambiguous_edge()


def test_signal_3_broken_path(detector: WeaknessDetector) -> None:  # WD-T4
    findings = detector.signal_3_broken_path()
    ids = {n for f in findings for n in f.nodes}
    assert "mathsquiz_mathsquiz_final_py" in ids
    assert all(f.priority == "secondary" for f in findings)


def test_signal_3_resolves_relative_to_data_root(
    graph_json_path: Path, tmp_path: Path
) -> None:  # WD-E4
    det = WeaknessDetector(GraphReader(graph_json_path), data_root=tmp_path)
    # With an empty data root, the referenced files are all absent — no raise.
    findings = det.signal_3_broken_path()
    assert any("mathsquiz_mathsquiz_final_py" in f.nodes for f in findings)


def test_signal_4_critical_path_break(detector: WeaknessDetector) -> None:
    findings = detector.signal_4_critical_path_break()
    assert findings
    f = findings[0]
    assert f.tag == "INFERRED"
    assert f.priority == "secondary"
    assert "may" in f.hypothesis
    assert "OOP" in f.hypothesis


def test_signal_5_isolated_cluster(detector: WeaknessDetector) -> None:  # WD-T2
    findings = detector.signal_5_isolated_cluster()
    assert len(findings) == 1
    f = findings[0]
    assert set(f.nodes) == {
        "polygons_polygons_rationale_18",
        "polygons_polygons_rationale_33",
        "polygons_polygons_rationale_50",
    }
    assert f.tag == "EXTRACTED"
    assert f.priority == "primary"
    assert "may" not in f.hypothesis and "suggests" not in f.hypothesis


def test_signal_6_semantic_duplicate_reads_source(detector: WeaknessDetector) -> None:  # WD-T5
    findings = detector.signal_6_semantic_duplicate()
    assert len(findings) == 1
    f = findings[0]
    assert f.signal == 6
    assert set(f.nodes) == {
        "polygons_polygons_polygon_init",
        "polygons_polygons_calc_polygon_details",
    }
    assert f.tag == "AMBIGUOUS"
    assert "manual" in f.hypothesis and "check" in f.hypothesis
    # The disclosed source-peek must have opened polygons.py and compared fields.
    assert "sides" in f.hypothesis
    assert "internal_angle" in f.hypothesis


def test_signal_6_skips_without_nodes(graph_json_path: Path, tmp_path: Path) -> None:
    # Source absent under an empty data root → still hypothesizes (AMBIGUOUS) but no peek.
    det = WeaknessDetector(GraphReader(graph_json_path), data_root=tmp_path)
    findings = det.signal_6_semantic_duplicate()
    assert findings and findings[0].tag == "AMBIGUOUS"
