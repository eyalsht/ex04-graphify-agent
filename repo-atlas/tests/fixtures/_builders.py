"""Node/edge builders backing ``tests/fixtures/graph_factory.py``.

Split out to keep ``graph_factory.py`` under the 150-line cap (CLAUDE.md §3) — import
from ``graph_factory``, not from here; this module is not part of the public surface.
"""

from __future__ import annotations

from typing import Any, Literal

FileType = Literal["code", "document"]
Relation = Literal["contains", "calls", "inherits", "method", "references"]
Confidence = Literal["EXTRACTED", "INFERRED", "AMBIGUOUS"]

NodeDict = dict[str, Any]
EdgeDict = dict[str, Any]
GraphDict = dict[str, Any]

_INFERRED_DEFAULT_SCORE = 0.7


def make_node(
    node_id: str,
    *,
    label: str | None = None,
    norm_label: str | None = None,
    file_type: FileType = "code",
    source_file: str | None = None,
    source_location: str = "L1",
    community: int = 0,
    origin: str = "ast",
    **extra: Any,
) -> NodeDict:
    """Build one node dict with every §7.1 field defaulted from ``node_id``.

    Defaults: ``label`` falls back to ``node_id``; ``norm_label`` falls back to
    ``label.lower()``; ``source_file`` falls back to ``f"{node_id}.py"``. Any keyword
    not listed above is merged into the result as-is, so a test can carry extra fields
    the contract does not require (e.g. ``source_url``).

    Example:
        >>> make_node("a")["source_file"]
        'a.py'
        >>> make_node("a", community=3)["community"]
        3
    """
    resolved_label = label if label is not None else node_id
    node: NodeDict = {
        "id": node_id,
        "label": resolved_label,
        "norm_label": norm_label if norm_label is not None else resolved_label.lower(),
        "file_type": file_type,
        "source_file": source_file if source_file is not None else f"{node_id}.py",
        "source_location": source_location,
        "community": community,
        "_origin": origin,
    }
    node.update(extra)
    return node


def make_edge(
    source: str,
    target: str,
    *,
    relation: Relation = "calls",
    confidence: Confidence = "EXTRACTED",
    confidence_score: float | None = None,
    weight: float = 1.0,
    source_file: str | None = None,
    source_location: str = "L1",
    **extra: Any,
) -> EdgeDict:
    """Build one edge dict. ``source``/``target`` are node ids, not validated here.

    ``confidence_score`` defaults to ``1.0`` for ``EXTRACTED``, ``0.7`` otherwise —
    pass an explicit score to build e.g. "one INFERRED edge below 0.9".

    Example:
        >>> make_edge("a", "b", confidence="INFERRED", confidence_score=0.75)["weight"]
        1.0
    """
    if confidence_score is None:
        confidence_score = 1.0 if confidence == "EXTRACTED" else _INFERRED_DEFAULT_SCORE
    edge: EdgeDict = {
        "source": source,
        "target": target,
        "relation": relation,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "weight": weight,
        "source_file": source_file if source_file is not None else f"{source}.py",
        "source_location": source_location,
    }
    edge.update(extra)
    return edge
