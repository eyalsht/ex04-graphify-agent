"""TDD for detect() orchestration, ranking, language↔tag invariant (WD-T6/T7/T8)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.weakness_detector import WeaknessDetector

_HEDGES = ("may", "suggests", "might")


@pytest.fixture
def findings(graph_json_path: Path) -> list:
    return WeaknessDetector(GraphReader(graph_json_path)).detect()


def test_detect_runs_all_six_signals(findings: list) -> None:
    signals = {f.signal for f in findings}
    assert {1, 2, 3, 4, 5, 6} <= signals


def test_first_finding_is_primary_signal(findings: list) -> None:  # WD-T6
    assert findings[0].priority == "primary"
    assert findings[0].signal in {1, 5, 6}


def test_secondary_signals_rank_below_primary(findings: list) -> None:  # WD-T6
    priorities = [f.priority for f in findings]
    last_primary = max(i for i, p in enumerate(priorities) if p == "primary")
    first_secondary = min(i for i, p in enumerate(priorities) if p == "secondary")
    assert last_primary < first_secondary
    # mathsquiz-community signals (2 and 3) are secondary.
    for f in findings:
        if f.signal in {2, 3}:
            assert f.priority == "secondary"


def test_extracted_findings_have_no_hedge(findings: list) -> None:  # WD-T7
    for f in findings:
        if f.tag == "EXTRACTED":
            assert not any(h in f.hypothesis for h in _HEDGES), f.hypothesis


def test_inferred_findings_hedge(findings: list) -> None:  # WD-T7
    for f in findings:
        if f.tag == "INFERRED":
            assert any(h in f.hypothesis for h in _HEDGES), f.hypothesis


def test_ambiguous_findings_demand_manual_check(findings: list) -> None:  # WD-T7
    for f in findings:
        if f.tag == "AMBIGUOUS":
            assert "manual" in f.hypothesis and "check" in f.hypothesis


def test_no_source_validation_filled(findings: list) -> None:  # WD-T8
    assert all(f.source_validation is None for f in findings)


def test_detect_is_deterministic(graph_json_path: Path) -> None:  # PHASE3-116
    a = WeaknessDetector(GraphReader(graph_json_path)).detect()
    b = WeaknessDetector(GraphReader(graph_json_path)).detect()
    assert [(f.signal, tuple(f.nodes)) for f in a] == [(f.signal, tuple(f.nodes)) for f in b]


def test_six_signal_convergence_on_polygons(findings: list) -> None:  # PHASE3-118 / R4.5
    primaries = [f for f in findings if f.priority == "primary"]
    assert {f.signal for f in primaries} == {1, 5, 6}
    for f in primaries:
        assert f.source_file == "polygons/polygons.py"
