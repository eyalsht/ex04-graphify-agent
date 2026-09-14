"""repo-atlas — graph-guided comprehension for arbitrary Python repositories.

Pipeline: repo -> extractor (AST) -> graph.json -> graph_reader -> vault -> brief.
Public entry point is ``repo_atlas.sdk``; ``repo_atlas.cli`` is a thin wrapper over it.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
