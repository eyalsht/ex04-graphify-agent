"""AST-based graph extraction — see ``docs/EXTRACTOR_SPEC.md`` for the frozen contract."""

from __future__ import annotations

from repo_atlas.extractor.communities import assign_communities
from repo_atlas.extractor.manifest import (
    ManifestDiff,
    ast_hash,
    build_manifest,
    diff_manifest,
    load_manifest,
    write_manifest,
)
from repo_atlas.extractor.models import (
    CallSite,
    FileSymbols,
    MarkerComment,
    RawEdge,
    RawNode,
    Symbol,
)
from repo_atlas.extractor.report import render_report, write_report
from repo_atlas.extractor.serialize import build_graph, write_graph

__all__ = [
    "CallSite",
    "FileSymbols",
    "ManifestDiff",
    "MarkerComment",
    "RawEdge",
    "RawNode",
    "Symbol",
    "assign_communities",
    "ast_hash",
    "build_graph",
    "build_manifest",
    "diff_manifest",
    "load_manifest",
    "render_report",
    "write_graph",
    "write_manifest",
    "write_report",
]
