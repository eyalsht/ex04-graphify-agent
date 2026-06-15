"""Rank weakness findings: primary band (signals 1/5/6) above secondary (2/3/4).

Within a band, sort by the strongest graph evidence first: highest max-degree of the
involved nodes, then lowest confidence-rank tie-break is *not* applied to primaries (they
are all EXTRACTED facts); secondaries break ties by lower confidence first so the most
uncertain noise sinks predictably. Final tie-break is signal number then node id, so the
ordering is fully deterministic (PHASE3-116).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .hypothesis import WeaknessFinding

if TYPE_CHECKING:
    from ex04_graphify_agent.graph_reader import GraphReader

_PRIORITY_RANK = {"primary": 0, "secondary": 1}


def _max_degree(finding: WeaknessFinding, reader: GraphReader) -> int:
    degrees = [reader.degree(n) for n in finding.nodes if reader.node_exists(n)]
    return max(degrees) if degrees else 0


def rank_findings(findings: list[WeaknessFinding], reader: GraphReader) -> list[WeaknessFinding]:
    """Return findings ordered primary-first, strongest-evidence-first (deterministic)."""

    def key(finding: WeaknessFinding) -> tuple[int, int, int, str]:
        return (
            _PRIORITY_RANK[finding.priority],
            -_max_degree(finding, reader),
            finding.signal,
            finding.nodes[0] if finding.nodes else "",
        )

    return sorted(findings, key=key)
