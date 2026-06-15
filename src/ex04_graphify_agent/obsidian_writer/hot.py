"""hot.md — prioritized 'where to look first' note (centrality * proximity-to-bug).

R5.1.4 / R5.6.1: the ranking metric is derived from the graph — a degree/betweenness
centrality blend multiplied by proximity to the bug location (PLAN §5) — never arbitrary,
and is disclosed in the rendered output. ``ObsidianWriter`` only ever writes ``hot.md`` —
it must never touch ``graph.json``, ``GRAPH_REPORT.md``, ``index.md``, or any per-node note
(CLAUDE.md §4 baseline immutability).
"""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.graph_reader import GraphReader, NodeView

from . import ranking
from .config import (
    default_bug_node_id,
    default_hot_md_top_k,
    default_hot_md_weights,
    default_vault_dir,
)

_HEADING = "# Hot — Where to look first"


def _metric_line(weights: dict[str, float], bug_node_id: str) -> str:
    """Disclose the (non-arbitrary) ranking metric in the rendered note — R5.6.1."""
    return (
        f"Ranked by centrality * proximity to the bug node `{bug_node_id}` (R5.6.1, PLAN §5): "
        f"centrality = {weights['degree']}·degree + {weights['betweenness']}·betweenness "
        "(max-normalized); proximity = 1 / (1 + shortest-path distance to the bug node). "
        "File-container roots are excluded."
    )


class ObsidianWriter:
    """Generates ``obsidian/hot.md`` from a ``GraphReader`` (graph_reader's output)."""

    def __init__(self, reader: GraphReader, vault_dir: str | Path | None = None) -> None:
        self._reader = reader
        self.vault_dir = Path(vault_dir) if vault_dir is not None else default_vault_dir()

    def rank_hot_nodes(self, top_k: int = 5) -> list[NodeView]:
        """Top ``top_k`` nodes by centrality * proximity-to-bug — R5.6.1 / PLAN §5."""
        return ranking.rank_nodes(
            self._reader, top_k, default_hot_md_weights(), default_bug_node_id()
        )

    def wikilink(self, node: NodeView) -> str:
        """Render the exact vault wikilink convention: ``[[id|Label]]``."""
        return f"[[{node.id}|{node.label}]]"

    def render_hot_md(self, top_k: int | None = None) -> str:
        """Render the ``hot.md`` markdown body (pure, no I/O)."""
        resolved_k = top_k if top_k is not None else default_hot_md_top_k()
        ranked = self.rank_hot_nodes(resolved_k)
        metric = _metric_line(default_hot_md_weights(), default_bug_node_id())
        lines = [_HEADING, "", metric, ""]
        for index, node in enumerate(ranked, start=1):
            lines.append(f"{index}. {self.wikilink(node)} — {_item_metadata(node)}")
        lines.append("")
        return "\n".join(lines)

    def write_hot_md(self, top_k: int | None = None) -> Path:
        """Write ``hot.md`` to ``vault_dir`` (only file touched) and return its path."""
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        path = self.vault_dir / "hot.md"
        path.write_text(self.render_hot_md(top_k), encoding="utf-8", newline="\n")
        return path


def _item_metadata(node: NodeView) -> str:
    """``degree=D · bw=B · community=C · source_file:loc`` — null location omits ``:Lxx``."""
    location = _source_location(node)
    return (
        f"degree={node.degree} · bw={node.betweenness:.4f} · "
        f"community={node.community} · {location}"
    )


def _source_location(node: NodeView) -> str:
    """``source_file:Lxx``, or just ``source_file`` (no ``:None``) when location is null."""
    if node.source_location is None:
        return node.source_file
    return f"{node.source_file}:{node.source_location}"
