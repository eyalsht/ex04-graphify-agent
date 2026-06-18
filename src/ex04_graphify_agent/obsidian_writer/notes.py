"""Per-node Markdown note rendering with [[wikilinks]] (R5.1 vault notes).

Pure rendering for regenerating per-node notes into a SCRATCH dir to diff against the
committed PRE-FIX vault — never overwrites the baseline ``obsidian/*`` notes (CLAUDE.md §4).
"""

from __future__ import annotations

from ex04_graphify_agent.graph_reader import GraphReader, NodeView


def _wikilink(node: NodeView) -> str:
    return f"[[{node.id}|{node.label}]]"


def render_node_note(reader: GraphReader, node: NodeView) -> str:
    """Render one node's note: frontmatter, source, in/out relations, community link."""
    loc = node.source_location
    lines = [
        "---",
        f'label: "{node.label}"',
        f'file_type: "{node.file_type}"',
        f'source_file: "{node.source_file}"',
        f'source_location: "{loc}"' if loc is not None else "source_location: null",
        f"community: {node.community}",
        "---",
        "",
        f"# {node.label}",
        "",
        f"**Source:** `{node.source_file}:{loc}`"
        if loc is not None
        else f"**Source:** `{node.source_file}`",
        "",
    ]
    outgoing: list[str] = []
    incoming: list[str] = []
    for edge in reader.edges_of(node.id):
        if edge.source == node.id:
            outgoing.append(f"- **{edge.relation}** → {_wikilink(reader.node(edge.target))}")
        else:
            incoming.append(f"- {_wikilink(reader.node(edge.source))} → **{edge.relation}**")
    if outgoing:
        lines += ["## Outgoing relations", *outgoing, ""]
    if incoming:
        lines += ["## Incoming relations", *incoming, ""]
    if node.community is not None:
        lines.append(f"Community: [[community-{node.community}|Community {node.community}]]")
    return "\n".join(lines)
