"""sdk — the single façade for all EX04 business logic (SDK-first non-negotiable).

CLI/GUI hold no logic; they call this. Concrete methods are added as each phase lands.
"""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.obsidian_writer import ObsidianWriter


class Ex04Sdk:
    """Top-level façade — orchestrates the lower-level modules, holds no algorithms."""

    def generate_hot(self, vault_dir: str | Path | None = None) -> Path:
        """Render and write ``hot.md`` (R5.1.4 / R5.6.1).

        Keyless — no LLM call. ``vault_dir`` defaults to ``config/paths.json``
        ``obsidian_dir`` when omitted. Only ``hot.md`` is written (CLAUDE.md §4
        baseline immutability).
        """
        reader = GraphReader()
        writer = ObsidianWriter(reader, vault_dir=vault_dir)
        return writer.write_hot_md()
