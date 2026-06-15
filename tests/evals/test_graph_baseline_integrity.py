"""Structural eval: the PRE-FIX Graphify baseline is intact and matches GRAPH_REPORT.md.

Keyless, known-answer (the answer is fixed by the committed artifact): 23 nodes, 20 edges,
6 communities. This is the first member of the `tests/evals/` suite; the thesis evals
(token delta, weakness known-answers) land in Phase 5. ``pass^k = 100%`` — it must hold on
every run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.eval


def test_pre_fix_graph_has_known_shape(graph_json_path: Path) -> None:
    data = json.loads(graph_json_path.read_text(encoding="utf-8"))
    assert len(data["nodes"]) == 23
    assert len(data["links"]) == 20
    communities = {node["community"] for node in data["nodes"]}
    assert len(communities) == 6


def test_god_node_polygon_present(graph_json_path: Path) -> None:
    data = json.loads(graph_json_path.read_text(encoding="utf-8"))
    ids = {node["id"] for node in data["nodes"]}
    assert "polygons_polygons_polygon" in ids


def test_three_rationale_todo_nodes_present(graph_json_path: Path) -> None:
    data = json.loads(graph_json_path.read_text(encoding="utf-8"))
    ids = {node["id"] for node in data["nodes"]}
    assert {
        "polygons_polygons_rationale_18",
        "polygons_polygons_rationale_33",
        "polygons_polygons_rationale_50",
    } <= ids
