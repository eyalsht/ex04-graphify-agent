"""The public façade — every business decision funnels through here (CLAUDE.md §3).

``cli.py`` builds a ``RunPaths`` and calls into this module; it never imports an extractor,
graph_reader, vault or brief module directly. The implementation is split across
``sdk_graph`` (filesystem only) and ``sdk_llm`` (needs a provider) to stay inside the
150-line cap; this module is the single import point.
"""

from __future__ import annotations

from repo_atlas.sdk_graph import VAULT_DIRNAME, VaultResult, extract, map_repo, vault
from repo_atlas.sdk_llm import (
    BRIEF_FILENAME,
    COMPARISON_FILENAME,
    RUNS_DIRNAME,
    BriefOutcome,
    ComparisonOutcome,
    brief,
    compare,
)

__all__ = [
    "BRIEF_FILENAME",
    "COMPARISON_FILENAME",
    "RUNS_DIRNAME",
    "VAULT_DIRNAME",
    "BriefOutcome",
    "ComparisonOutcome",
    "VaultResult",
    "brief",
    "compare",
    "extract",
    "map_repo",
    "vault",
]
