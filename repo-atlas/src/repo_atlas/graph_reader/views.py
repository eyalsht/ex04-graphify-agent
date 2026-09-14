"""Raw ``graph.json`` attributes -> typed views.

Split out of the reader so the reader is about *querying* a graph and this module is
about *interpreting* one producer's attribute dict. It is also where tolerance lives:
missing fields fall back to documented defaults, and an unknown confidence degrades to
AMBIGUOUS with a warning rather than crashing on a graph from another producer (R2.3).
"""

from __future__ import annotations

import warnings
from typing import Any

from repo_atlas.graph_reader import filters
from repo_atlas.graph_reader.models import Confidence, EdgeView, NodeView

#: Used when a node carries no community — visible as "unassigned" rather than 0.
MISSING_COMMUNITY = -1


def parse_confidence(raw: Any, edge: tuple[str, str]) -> Confidence:
    """Parse a confidence value, degrading unknown ones rather than crashing (R2.3)."""
    try:
        return filters.as_confidence(str(raw))
    except ValueError:
        warnings.warn(
            f"unknown confidence {raw!r} on edge {edge[0]}->{edge[1]}; treating as AMBIGUOUS",
            UserWarning,
            stacklevel=3,
        )
        return Confidence.AMBIGUOUS


def location(raw: Any) -> str | None:
    """Normalise a location: null and empty string both mean 'no location'."""
    text = str(raw) if raw is not None else ""
    return text or None


def edge_view(source: Any, target: Any, attrs: dict[str, Any]) -> EdgeView:
    """Build one typed edge view from its raw attributes."""
    endpoints = (str(source), str(target))
    return EdgeView(
        source=endpoints[0],
        target=endpoints[1],
        relation=str(attrs.get("relation", "")),
        confidence=parse_confidence(attrs.get("confidence", Confidence.EXTRACTED), endpoints),
        confidence_score=float(attrs.get("confidence_score", 1.0)),
        weight=float(attrs.get("weight", 1.0)),
        source_file=str(attrs.get("source_file", "")),
        source_location=location(attrs.get("source_location")),
    )


def node_view(
    node_id: Any,
    attrs: dict[str, Any],
    degrees: dict[str, int],
    betweens: dict[str, float],
    roots: set[str],
) -> NodeView:
    """Build one typed node view, enriched with its computed centrality."""
    key = str(node_id)
    label = str(attrs.get("label", key))
    return NodeView(
        id=key,
        label=label,
        file_type=str(attrs.get("file_type", "code")),
        source_file=str(attrs.get("source_file", "")),
        source_location=location(attrs.get("source_location")),
        community=int(attrs.get("community", MISSING_COMMUNITY)),
        norm_label=str(attrs.get("norm_label", label.lower())),
        degree=degrees.get(key, 0),
        betweenness=betweens.get(key, 0.0),
        is_file_root=key in roots,
    )
