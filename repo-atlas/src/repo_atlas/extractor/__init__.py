"""AST-based graph extraction — see ``docs/EXTRACTOR_SPEC.md`` for the frozen contract."""

from __future__ import annotations

from repo_atlas.extractor.communities import assign_communities
from repo_atlas.extractor.models import (
    CallSite,
    FileSymbols,
    MarkerComment,
    RawEdge,
    RawNode,
    Symbol,
)

__all__ = [
    "CallSite",
    "FileSymbols",
    "MarkerComment",
    "RawEdge",
    "RawNode",
    "Symbol",
    "assign_communities",
]
