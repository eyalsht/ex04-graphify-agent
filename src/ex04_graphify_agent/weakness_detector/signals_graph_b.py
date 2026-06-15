"""Graph-only PART-C signals 3 (broken path), 4 (critical-path break), 5 (isolated cluster).

Continuation of ``signals_graph`` (split to keep each file ≤150 lines, CLAUDE.md §3).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .hypothesis import WeaknessFinding

if TYPE_CHECKING:
    from ex04_graphify_agent.graph_reader import GraphReader

TARGET_SOURCE = "polygons/polygons.py"


def broken_path(reader: GraphReader, data_root: Path) -> list[WeaknessFinding]:
    """Signal 3 — node referenced by an EXTRACTED edge whose source_file is absent on disk.

    Existence is resolved relative to ``data_root`` (WD-E4); a missing dir never raises.
    """
    findings: list[WeaknessFinding] = []
    for edge in reader.edges_with_confidence("EXTRACTED"):
        target = reader.node(edge.target)
        if not target.source_file or (data_root / target.source_file).exists():
            continue
        hypo = (
            f"`{target.label}` is referenced by `{reader.node(edge.source).label}` but the "
            f"file is absent on disk ({target.source_file}) — a PRD-to-code gap. Secondary, "
            "not the primary fix."
        )
        findings.append(
            WeaknessFinding(
                signal=3,
                tag="EXTRACTED",
                hypothesis=hypo,
                priority="secondary",
                source_file=target.source_file,
                nodes=[target.id],
                edges=[(edge.source, edge.target)],
            )
        )
    return findings


def critical_path_break(reader: GraphReader) -> list[WeaknessFinding]:
    """Signal 4 — compute/draw functions with no preceding validation guard (INFERRED)."""
    candidates = (
        "polygons_polygons_calc_polygon_details",
        "polygons_polygons_draw_polygon",
    )
    present = [c for c in candidates if reader.node_exists(c)]
    if not present:
        return []
    hypo = (
        "`polygons.py` may lack a `sides >= 3` guard before `calc_polygon_details` / "
        "`draw_polygon`; mention in the OOP-improvement summary, not a blocking fix. "
        "Secondary."
    )
    return [
        WeaknessFinding(
            signal=4,
            tag="INFERRED",
            hypothesis=hypo,
            priority="secondary",
            source_file=TARGET_SOURCE,
            nodes=list(present),
            edges=[],
        )
    ]


def isolated_cluster(reader: GraphReader, thresholds: dict[str, object]) -> list[WeaknessFinding]:
    """Signal 5 — weakly-connected, untested rationale/dead nodes grouped by community."""
    max_edges = int(thresholds["isolated_cluster_max_edges"])  # type: ignore[call-overload]
    isolated = [
        n for n in reader.all_nodes() if n.file_type == "rationale" and n.degree <= max_edges
    ]
    if not isolated:
        return []
    ids = sorted(n.id for n in isolated)
    community = isolated[0].community
    hypo = (
        f"Three weakly-connected rationale TODO nodes in Community {community} are the "
        "developer's own notes describing the incompleteness — they are the bug. Primary."
    )
    return [
        WeaknessFinding(
            signal=5,
            tag="EXTRACTED",
            hypothesis=hypo,
            priority="primary",
            source_file=isolated[0].source_file or TARGET_SOURCE,
            nodes=ids,
            edges=[],
        )
    ]
