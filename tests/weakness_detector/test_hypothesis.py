"""TDD for the WeaknessFinding / SourceValidation data contract (PHASE3-001..006)."""

from __future__ import annotations

import dataclasses

from ex04_graphify_agent.weakness_detector import SourceValidation, WeaknessFinding


def test_source_validation_fields() -> None:
    sv = SourceValidation(confirmed=True, note="opened polygons.py")
    assert sv.confirmed is True
    assert sv.note == "opened polygons.py"


def test_weakness_finding_fields() -> None:
    finding = WeaknessFinding(
        signal=1,
        tag="EXTRACTED",
        hypothesis="Polygon is the god node.",
        priority="primary",
        source_file="polygons/polygons.py",
        nodes=["polygons_polygons_polygon"],
        edges=[("a", "b")],
    )
    assert finding.signal == 1
    assert finding.tag == "EXTRACTED"
    assert finding.priority == "primary"
    assert finding.source_file == "polygons/polygons.py"
    assert finding.nodes == ["polygons_polygons_polygon"]
    assert finding.edges == [("a", "b")]


def test_source_validation_defaults_to_none() -> None:
    """A freshly-detected finding has pending (None) source_validation (WD-T8)."""
    finding = WeaknessFinding(
        signal=5,
        tag="EXTRACTED",
        hypothesis="The TODOs are the bug.",
        priority="primary",
        source_file="polygons/polygons.py",
        nodes=[],
        edges=[],
    )
    assert finding.source_validation is None
    field = {f.name: f for f in dataclasses.fields(finding)}["source_validation"]
    assert field.default is None
