"""index.md (navigation hub) rendering with [[wikilinks]] (R5.1.3).

Pure rendering for scratch regeneration; never overwrites the committed ``obsidian/index.md``
baseline (CLAUDE.md §4).
"""

from __future__ import annotations

from ex04_graphify_agent.graph_reader import GraphReader, NodeView


def _wikilink(node: NodeView) -> str:
    return f"[[{node.id}|{node.label}]]"


def render_index(reader: GraphReader) -> str:
    """Render ``index.md``: the 6 community links + every node as a wikilink."""
    lines = ["# Graph Index", "", "## Communities", ""]
    lines += [f"- [[community-{c}|Community {c}]]" for c in sorted(reader.communities())]
    lines += ["", "## All Nodes", ""]
    nodes = sorted(reader.all_nodes(), key=lambda node: node.id)
    lines += [f"- {_wikilink(node)}" for node in nodes]
    lines.append("")
    return "\n".join(lines)
