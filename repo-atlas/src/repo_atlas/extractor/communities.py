"""Community labels via greedy modularity (``docs/EXTRACTOR_SPEC.md`` §9).

Community ids are **not stable across source edits** — a small change to the edge set
can merge, split, or renumber communities entirely, which is why ``docs/KNOWN_LIMITATIONS.md``
warns that it renames ``community-N.md`` vault notes. They are also **not comparable to the
reference graph's** partition: the reference was computed over a larger edge set that
included five document-pipeline edges this extractor does not produce (ADR-0001), so an
id that happens to match a reference id is coincidence, not agreement.

What *is* guaranteed: numbering is deterministic for a fixed ``(nodes, edges)`` input.
``networkx``'s own community order is not reliable across processes (ties among
same-size communities depend on internal set/hash iteration), so we re-sort before
numbering.
"""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx

from repo_atlas.extractor.models import RawEdge, RawNode


def assign_communities(nodes: Iterable[RawNode], edges: Iterable[RawEdge]) -> dict[str, int]:
    """Map every node id to a community integer.

    An empty node set yields an empty mapping. A node with zero edges (isolated, or the
    whole graph edgeless) still gets a community of its own — greedy modularity starts
    every node in a singleton community and only merges pairs that raise modularity, so
    an isolated node never has anything to merge with.

    Numbering: communities are sorted by size descending, then by their lexicographically
    smallest member id ascending, and numbered from 0 in that order. This is a stable key
    over the *content* of the partition, not networkx's return order, so it is safe to
    call twice on the same graph and diff the results.
    """
    graph: nx.Graph[str] = nx.Graph()
    graph.add_nodes_from(node.id for node in nodes)
    graph.add_edges_from((edge.source, edge.target) for edge in edges)
    if graph.number_of_nodes() == 0:
        return {}

    found = nx.algorithms.community.greedy_modularity_communities(graph)
    ordered = sorted(found, key=lambda community: (-len(community), min(community)))
    return {member: index for index, community in enumerate(ordered) for member in community}
