"""Write a complete, internally consistent vault to disk (PRD R3.1)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from repo_atlas.graph_reader import GraphReader
from repo_atlas.vault import links, render

DEFAULT_WEIGHTS: Mapping[str, float] = {"degree": 0.6, "betweenness": 0.4}


class VaultWriter:
    """Renders every note the vault needs — including the community notes the
    index and node notes link to, which the origin project never wrote."""

    def __init__(self, reader: GraphReader, vault_dir: str | Path) -> None:
        self._reader = reader
        self._dir = Path(vault_dir)

    def write_all(
        self,
        top_k: int = 8,
        weights: Mapping[str, float] | None = None,
        seed_id: str | None = None,
    ) -> Path:
        """Write index, hot, one note per node and one per community. Returns the dir."""
        self._dir.mkdir(parents=True, exist_ok=True)
        self._write("index.md", render.render_index(self._reader))
        self._write(
            "hot.md",
            render.render_hot(self._reader, top_k, weights or DEFAULT_WEIGHTS, seed_id),
        )
        for node in self._reader.all_nodes():
            self._write(f"{node.id}.md", render.render_node_note(self._reader, node))
        for community in self._reader.communities():
            self._write(
                f"{links.community_note_id(community)}.md",
                render.render_community(self._reader, community),
            )
        return self._dir

    def _write(self, name: str, body: str) -> None:
        (self._dir / name).write_text(body, encoding="utf-8")
