"""obsidian_writer — generate/update index.md, hot.md, per-node notes.

See ``docs/PRD_graph_reader.md`` (vault is graph_reader's output). Phase 4.
"""

from __future__ import annotations

from .hot import ObsidianWriter

__all__ = ["ObsidianWriter"]
