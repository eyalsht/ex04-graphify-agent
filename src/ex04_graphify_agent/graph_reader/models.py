"""Typed views over graph.json nodes/edges (NodeView, EdgeView, Confidence).

These are the public data contract consumed by ``weakness_detector`` and
``obsidian_writer`` (see ``docs/PLAN.md`` §7.1 and ``docs/PRD_graph_reader.md``).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Confidence(StrEnum):
    """Edge confidence levels (CLAUDE.md §3 inference discipline).

    ``EXTRACTED`` states facts, ``INFERRED`` suggests, ``AMBIGUOUS`` requires a
    manual/source check. ``AMBIGUOUS`` is valid in the schema but absent (0%) in the
    PRE-FIX baseline graph.
    """

    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class NodeView:
    """Read-only view of a graph node enriched with computed metrics."""

    id: str
    label: str
    file_type: str
    source_file: str
    source_location: str | None
    community: int
    norm_label: str
    degree: int
    betweenness: float
    is_file_root: bool = False


@dataclass(frozen=True)
class EdgeView:
    """Read-only view of a graph edge (undirected ``links`` entry)."""

    source: str
    target: str
    relation: str
    confidence: Confidence
    confidence_score: float
    weight: float
    source_file: str
    source_location: str | None
