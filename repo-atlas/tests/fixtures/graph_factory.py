"""Synthetic node-link graph builder for tests (CLAUDE.md §7 / docs/PLAN.md §7.1).

Every test builds its own small graph through this factory instead of reading a
committed artifact. The only fixture permitted to read ``tests/fixtures/golden/`` is
the extractor's golden-regression eval (``.claude/skills/eval-harness/SKILL.md``).
Pinning the rest of the suite to one real artifact is exactly what made the origin
project (``ex04-graphify-agent``) impossible to retarget — this module exists so that
never happens here.

Public surface: ``make_node``, ``make_edge`` (single-item builders, re-exported from
``_builders`` to keep this file under the 150-line cap), ``graph_dict`` (the top-level
envelope builder), and ``write_graph`` (writes one to a ``tmp_path`` file for loader
tests).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tests.fixtures._builders import (
    Confidence,
    EdgeDict,
    FileType,
    GraphDict,
    NodeDict,
    Relation,
    make_edge,
    make_node,
)

__all__ = [
    "Confidence",
    "EdgeDict",
    "FileType",
    "GraphDict",
    "NodeDict",
    "Relation",
    "graph_dict",
    "make_edge",
    "make_node",
    "write_graph",
]


def graph_dict(
    nodes: list[str | NodeDict] | None = None,
    edges: list[tuple[str, str] | EdgeDict] | None = None,
    *,
    graph_meta: dict[str, Any] | None = None,
) -> GraphDict:
    """Build a complete node-link envelope: ``{directed, multigraph, graph, nodes, links}``.

    Each item in ``nodes`` is either a bare node id (gets ``make_node`` defaults) or a
    full node dict — e.g. from ``make_node(...)`` with overrides — mixed freely. Each
    item in ``edges`` is either a bare ``(source, target)`` tuple (gets ``make_edge``
    defaults) or a full edge dict.

    Example (the common, one-line case):
        >>> g = graph_dict(nodes=["a", "b", "c"], edges=[("a", "b"), ("b", "c")])
        >>> (g["directed"], len(g["nodes"]), len(g["links"]))
        (False, 3, 2)

    Raises:
        ValueError: a node id repeats, or an edge names an id not in ``nodes``.
    """
    node_dicts: list[NodeDict] = [
        make_node(item) if isinstance(item, str) else dict(item) for item in (nodes or [])
    ]

    seen: set[str] = set()
    for node in node_dicts:
        node_id = node["id"]
        if node_id in seen:
            raise ValueError(f"duplicate node id: {node_id!r}")
        seen.add(node_id)

    edge_dicts: list[EdgeDict] = []
    for item in edges or []:
        edge = make_edge(item[0], item[1]) if isinstance(item, tuple) else dict(item)
        for endpoint in (edge["source"], edge["target"]):
            if endpoint not in seen:
                raise ValueError(f"edge endpoint {endpoint!r} is not a known node id")
        edge_dicts.append(edge)

    return {
        "directed": False,
        "multigraph": False,
        "graph": dict(graph_meta) if graph_meta else {},
        "nodes": node_dicts,
        "links": edge_dicts,
    }


def write_graph(tmp_path: Path, data: GraphDict, filename: str = "graph.json") -> Path:
    """Write ``data`` as JSON under ``tmp_path / filename`` and return that path.

    Loaders (e.g. ``graph_reader.loader``) take a path, not a dict — use this instead
    of hand-rolling the same three lines of ``json.dumps``/``write_text`` per test.
    """
    path = tmp_path / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path
