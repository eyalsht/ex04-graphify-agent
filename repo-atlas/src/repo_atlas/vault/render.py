"""Markdown renderers: index, per-node notes, community notes, hot list."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from repo_atlas.graph_reader import GraphReader
from repo_atlas.graph_reader.models import EdgeView, NodeView
from repo_atlas.vault import links, ranking


def render_index(reader: GraphReader) -> str:
    """The vault's entry point: communities, then every node."""
    nodes = sorted(reader.all_nodes(), key=lambda n: n.id)
    communities = sorted(reader.communities())
    lines = ["# Graph Index", "", "## Communities", ""]
    lines += [f"- {links.community_link(community)}" for community in communities]
    lines += ["", "## All Nodes", ""]
    lines += [f"- {links.node_link(node)}" for node in nodes]
    return "\n".join(lines) + "\n"


def render_community(reader: GraphReader, community: int) -> str:
    """One community's members, so the links from index and node notes resolve."""
    members = sorted(reader.nodes_in_community(community), key=lambda n: n.id)
    lines = [f"# {links.community_title(community)}", "", f"{len(members)} node(s).", ""]
    lines += [f"- {links.node_link(node)}" for node in members]
    lines += ["", f"Back to {links.wikilink('index', 'Graph Index')}."]
    return "\n".join(lines) + "\n"


def _relation_lines(reader: GraphReader, edges: Sequence[EdgeView], outgoing: bool) -> list[str]:
    lines: list[str] = []
    # Every edge endpoint is guaranteed to be a node: networkx materialises any id that
    # appears only in `links`, and the writer emits a note per node — so links resolve
    # even when the producer's `nodes` array was incomplete.
    for edge in sorted(edges, key=lambda e: (e.relation, e.target, e.source)):
        other = edge.target if outgoing else edge.source
        lines.append(f"- `{edge.relation}` -> {links.node_link(reader.node(other))}")
    return lines


def render_node_note(reader: GraphReader, node: NodeView) -> str:
    """One node's note: what it is, where it lives, and what it connects to."""
    incident = reader.edges_of(node.id)
    outgoing = [edge for edge in incident if edge.source == node.id]
    incoming = [edge for edge in incident if edge.target == node.id]
    location = f"{node.source_file}:{node.source_location}" if node.source_file else "—"
    lines = [
        "---",
        f"label: {node.label}",
        f"file_type: {node.file_type}",
        f"source_file: {node.source_file}",
        f"source_location: {node.source_location or ''}",
        f"community: {node.community}",
        f"degree: {node.degree}",
        "---",
        "",
        f"# {node.label}",
        "",
        f"**Source:** `{location}`",
        "",
        "## Outgoing relations",
        "",
        *(_relation_lines(reader, outgoing, outgoing=True) or ["- none"]),
        "",
        "## Incoming relations",
        "",
        *(_relation_lines(reader, incoming, outgoing=False) or ["- none"]),
        "",
        f"Community: {links.community_link(node.community)}",
    ]
    return "\n".join(lines) + "\n"


def render_hot(
    reader: GraphReader,
    top_k: int,
    weights: Mapping[str, float],
    seed_id: str | None = None,
) -> str:
    """The "read these first" list, stating the metric it actually used."""
    ranked = ranking.rank_nodes(reader, top_k, weights, seed_id)
    lines = [
        "# Hot — where to look first",
        "",
        ranking.metric_description(weights, seed_id),
        "",
    ]
    for position, node in enumerate(ranked, start=1):
        location = f" — `{node.source_file}:{node.source_location}`" if node.source_file else ""
        lines.append(
            f"{position}. {links.node_link(node)} (degree {node.degree},"
            f" betweenness {node.betweenness:.3f}){location}"
        )
    lines += ["", f"Back to {links.wikilink('index', 'Graph Index')}."]
    return "\n".join(lines) + "\n"
