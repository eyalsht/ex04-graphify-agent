"""Turning a graph and a vault into a written explanation of a repository."""

from __future__ import annotations

from repo_atlas.brief.models import BriefResult, Section
from repo_atlas.brief.prompts import SECTIONS, SYSTEM
from repo_atlas.brief.runner import GRAPH_GUIDED, NAIVE, BriefRunner

__all__ = [
    "GRAPH_GUIDED",
    "NAIVE",
    "SECTIONS",
    "SYSTEM",
    "BriefResult",
    "BriefRunner",
    "Section",
]
