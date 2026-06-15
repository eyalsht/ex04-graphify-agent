"""sdk — the single façade for all EX04 business logic (SDK-first non-negotiable).

CLI/GUI hold no logic; they call this. Concrete methods are added as each phase lands.
"""

from __future__ import annotations

from pathlib import Path

from .graph_reader import GraphReader
from .obsidian_writer import ObsidianWriter
from .weakness_detector import WeaknessDetector, WeaknessFinding


class Ex04Sdk:
    """Top-level façade — orchestrates the lower-level modules, holds no algorithms."""

    def detect_weaknesses(self, graph_path: str | Path | None = None) -> list[WeaknessFinding]:
        """Run the six PART-C weakness signals and return ranked findings (Phase 3 façade).

        Thin delegation only — all detection logic lives in ``weakness_detector``.
        """
        return WeaknessDetector(GraphReader(graph_path)).detect()

    def generate_hot(self, vault_dir: str | Path | None = None) -> Path:
        """Render and write ``hot.md`` (R5.1.4 / R5.6.1).

        Keyless — no LLM call. ``vault_dir`` defaults to ``config/paths.json``
        ``obsidian_dir`` when omitted. Only ``hot.md`` is written (CLAUDE.md §4
        baseline immutability).
        """
        reader = GraphReader()
        writer = ObsidianWriter(reader, vault_dir=vault_dir)
        return writer.write_hot_md()
