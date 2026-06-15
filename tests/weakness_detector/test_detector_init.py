"""TDD for WeaknessDetector construction + threshold loading (PHASE3-007..010, WD-E5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.weakness_detector import WeaknessDetector


def test_detector_constructs_with_reader(graph_json_path: Path) -> None:
    detector = WeaknessDetector(GraphReader(graph_json_path))
    assert detector is not None


def test_detector_loads_thresholds_from_config(graph_json_path: Path) -> None:
    detector = WeaknessDetector(GraphReader(graph_json_path))
    assert detector.thresholds["god_node_min_degree"] == 4
    assert detector.thresholds["ambiguous_confidence_max"] == 0.85


def test_detector_accepts_explicit_thresholds_path(graph_json_path: Path, tmp_path: Path) -> None:
    cfg = tmp_path / "th.json"
    cfg.write_text(json.dumps({"god_node_min_degree": 9}), encoding="utf-8")
    detector = WeaknessDetector(GraphReader(graph_json_path), thresholds_path=cfg)
    assert detector.thresholds["god_node_min_degree"] == 9


def test_missing_thresholds_config_fails_loud(graph_json_path: Path, tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(FileNotFoundError):
        WeaknessDetector(GraphReader(graph_json_path), thresholds_path=missing)
