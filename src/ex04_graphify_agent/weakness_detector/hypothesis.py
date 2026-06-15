"""WeaknessFinding / SourceValidation data types (confidence-tagged).

The detector *proposes* falsifiable hypotheses from graph structure; ``source_validation``
stays ``None`` (pending) until ``agent_workflow``'s validate node opens the source file
(WD-T8). Language strength must match ``tag`` (CLAUDE.md inference discipline):
EXTRACTED states facts, INFERRED hedges, AMBIGUOUS demands a manual source check.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Tag = Literal["EXTRACTED", "INFERRED", "AMBIGUOUS"]
Priority = Literal["primary", "secondary"]


@dataclass
class SourceValidation:
    """Outcome of opening ``source_file`` to confirm/deny a hypothesis (filled later)."""

    confirmed: bool
    note: str


@dataclass
class WeaknessFinding:
    """One triggered PART-C signal → a ranked, falsifiable bug-class hypothesis."""

    signal: int
    tag: Tag
    hypothesis: str
    priority: Priority
    source_file: str
    nodes: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    source_validation: SourceValidation | None = None
