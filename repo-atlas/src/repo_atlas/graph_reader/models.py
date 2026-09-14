"""Typed views over ``graph.json`` nodes and edges.

The public data contract every consumer (vault, brief, comparison) reads. Ported from
the origin project, which had these right — the layer was always target-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Confidence(StrEnum):
    """How far a claim can be trusted (CLAUDE.md §4).

    ``EXTRACTED`` states facts, ``INFERRED`` suggests, ``AMBIGUOUS`` needs a human to
    open the source and check.
    """

    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class NodeView:
    """Read-only view of a graph node, enriched with computed centrality."""

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
    """Read-only view of a graph edge."""

    source: str
    target: str
    relation: str
    confidence: Confidence
    confidence_score: float
    weight: float
    source_file: str
    source_location: str | None
