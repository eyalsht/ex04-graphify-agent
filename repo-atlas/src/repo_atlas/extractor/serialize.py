"""Assemble and write the ``graph.json`` envelope (``docs/EXTRACTOR_SPEC.md`` §9).

``build_graph`` is the single place that turns extractor output — nodes, edges, and the
community labels ``communities.assign_communities`` computed for them — into the
node-link dict a downstream reader loads with
``networkx.node_link_graph(data, edges="links")``. It validates before returning: a
silently corrupt graph poisons every later phase (graph reader, vault, brief), so
catching a dangling edge or a duplicate id here, with a clear message naming the
offender, is cheaper than debugging it three modules downstream.

Ordering is deterministic on purpose — nodes by id, links by
``(relation, source, target)`` — so that re-running the extractor over unchanged source
produces byte-identical ``nodes``/``links`` and a graph diff shows only real changes.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from repo_atlas import __version__
from repo_atlas.extractor.models import AMBIGUOUS, EXTRACTED, INFERRED, RawEdge, RawNode

_VALID_CONFIDENCE = frozenset({EXTRACTED, INFERRED, AMBIGUOUS})


def _validate(
    nodes: Sequence[RawNode], edges: Sequence[RawEdge], community_of: Mapping[str, int]
) -> None:
    seen: set[str] = set()
    for node in nodes:
        if node.id in seen:
            raise ValueError(f"duplicate node id: {node.id!r}")
        seen.add(node.id)
        if node.id not in community_of:
            raise ValueError(f"node {node.id!r} has no assigned community")

    for edge in edges:
        for endpoint in (edge.source, edge.target):
            if endpoint not in seen:
                raise ValueError(
                    f"edge {edge.relation!r} {edge.source!r} -> {edge.target!r} "
                    f"names unknown node {endpoint!r}"
                )
        if edge.confidence not in _VALID_CONFIDENCE:
            raise ValueError(
                f"edge {edge.source!r} -> {edge.target!r} has invalid confidence "
                f"{edge.confidence!r}; expected one of {sorted(_VALID_CONFIDENCE)}"
            )


def _graph_metadata(
    nodes: Sequence[RawNode],
    edges: Sequence[RawEdge],
    community_of: Mapping[str, int],
    repo_name: str,
    generated_at: str,
) -> dict[str, Any]:
    community_count = len({community_of[node.id] for node in nodes})
    return {
        "tool_version": __version__,
        "generated_at": generated_at,
        "repo_name": repo_name,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "community_count": community_count,
    }


def build_graph(
    nodes: Sequence[RawNode],
    edges: Sequence[RawEdge],
    community_of: Mapping[str, int],
    *,
    repo_name: str,
    generated_at: str,
) -> dict[str, Any]:
    """Build the validated ``graph.json`` envelope.

    Args:
        nodes: every node the extractor produced.
        edges: every edge the extractor produced.
        community_of: node id -> community int, from ``communities.assign_communities``.
            Every node id must have an entry.
        repo_name: the repository this graph describes, for the ``graph`` metadata block.
        generated_at: a UTC timestamp (ISO-8601 string) for the ``graph`` metadata block.
            Passed in rather than read from the clock so the same inputs always produce
            the same envelope — see the byte-stability test in ``tests/extractor/``.

    Returns:
        A dict shaped ``{"directed": False, "multigraph": False, "graph": {...},
        "nodes": [...], "links": [...]}``, with ``nodes`` sorted by ``id`` and ``links``
        sorted by ``(relation, source, target)``.

    Raises:
        ValueError: a node id repeats, an edge names an id not in ``nodes``, an edge's
            ``confidence`` is not one of EXTRACTED/INFERRED/AMBIGUOUS, or a node has no
            entry in ``community_of``.
    """
    _validate(nodes, edges, community_of)

    node_dicts = [
        {**node.to_dict(), "community": community_of[node.id]}
        for node in sorted(nodes, key=lambda node: node.id)
    ]
    link_dicts = [
        edge.to_dict()
        for edge in sorted(edges, key=lambda edge: (edge.relation, edge.source, edge.target))
    ]

    return {
        "directed": False,
        "multigraph": False,
        "graph": _graph_metadata(nodes, edges, community_of, repo_name, generated_at),
        "nodes": node_dicts,
        "links": link_dicts,
    }


def write_graph(path: Path, data: Mapping[str, Any]) -> None:
    """Write ``data`` as UTF-8 JSON to ``path``, creating parent directories as needed.

    The file ends with a trailing newline, matching the repo's other generated JSON.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
