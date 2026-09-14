"""Render ``GRAPH_REPORT.md`` (CLAUDE.md §4 claim discipline; ``docs/PRD.md``).

Every number here traces back to the same ``nodes``/``edges``/``community_of`` inputs
``serialize.build_graph`` validates and writes, so the report and the graph can never
silently disagree about counts. ``render_report`` is a pure function — no I/O, no
clock reads (the caller supplies ``generated_at``) — so it is trivial to snapshot-test;
``write_report`` is the thin, separately-tested writer.

The degraded-files section exists because a reader who only sees node counts has no
way to tell a fact the AST confirmed from one a regex guessed at (``docs/EXTRACTOR_SPEC.md``
§7). Naming the files that fell back to line-scan recovery, and saying plainly that
everything from them is INFERRED rather than EXTRACTED, is what keeps that distinction
visible instead of buried in a per-node ``_origin`` field nobody reads.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from repo_atlas.extractor.models import AMBIGUOUS, EXTRACTED, INFERRED, RawEdge, RawNode

_CONFIDENCE_ORDER = (EXTRACTED, INFERRED, AMBIGUOUS)


def _degree(nodes: Sequence[RawNode], edges: Sequence[RawEdge]) -> Counter[str]:
    degree: Counter[str] = Counter({node.id: 0 for node in nodes})
    for edge in edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
    return degree


def _totals_section(nodes: Sequence[RawNode], edges: Sequence[RawEdge], communities: int) -> str:
    return (
        f"## Totals\n\n- Nodes: {len(nodes)}\n- Edges: {len(edges)}\n- Communities: {communities}\n"
    )


def _confidence_section(edges: Sequence[RawEdge]) -> str:
    if not edges:
        return "## Confidence breakdown\n\nNo edges were extracted.\n"
    counts = Counter(edge.confidence for edge in edges)
    total = len(edges)
    lines = [
        f"- {label}: {counts.get(label, 0)} ({counts.get(label, 0) / total * 100:.1f}%)"
        for label in _CONFIDENCE_ORDER
    ]
    return "## Confidence breakdown (edges)\n\n" + "\n".join(lines) + "\n"


def _degraded_section(degraded_files: Iterable[str]) -> str:
    files = sorted(degraded_files)
    if not files:
        return "## Degraded extraction\n\nEvery file parsed cleanly — nothing fell back.\n"
    body = "\n".join(f"- `{path}`" for path in files)
    return (
        "## Degraded extraction\n\n"
        "These files failed `ast.parse` and were recovered by line scan. Every node and "
        "edge attributed to them is tagged INFERRED, not EXTRACTED:\n\n" + body + "\n"
    )


def _most_connected_section(nodes: Sequence[RawNode], degree: Counter[str], top_n: int) -> str:
    by_id = {node.id: node for node in nodes}
    ranked = sorted(degree.items(), key=lambda item: (-item[1], item[0]))[:top_n]
    rows = "\n".join(
        f"| {node_id} | {by_id[node_id].label} | {count} |" for node_id, count in ranked
    )
    header = "## Most-connected nodes\n\n| id | label | degree |\n| --- | --- | --- |\n"
    return header + rows + "\n"


def _community_section(nodes: Sequence[RawNode], community_of: Mapping[str, int]) -> str:
    groups: dict[int, list[RawNode]] = {}
    for node in nodes:
        groups.setdefault(community_of[node.id], []).append(node)
    parts = ["## Communities\n"]
    for community_id in sorted(groups):
        members = sorted(groups[community_id], key=lambda node: node.id)
        parts.append(f"\n### Community {community_id} ({len(members)} nodes)\n")
        parts.extend(f"- `{node.id}` ({node.label})" for node in members)
        parts.append("")
    return "\n".join(parts) + "\n"


def _isolated_section(nodes: Sequence[RawNode], degree: Counter[str]) -> str:
    isolated = sorted((node for node in nodes if degree[node.id] == 0), key=lambda n: n.id)
    if not isolated:
        return "## Isolated nodes (knowledge gaps)\n\nNone — every node has at least one edge.\n"
    body = "\n".join(f"- `{node.id}` ({node.label})" for node in isolated)
    return "## Isolated nodes (knowledge gaps)\n\n" + body + "\n"


def render_report(
    nodes: Sequence[RawNode],
    edges: Sequence[RawEdge],
    community_of: Mapping[str, int],
    *,
    repo_name: str,
    generated_at: str,
    degraded_files: Iterable[str] = (),
    top_n: int = 10,
) -> str:
    """Render ``GRAPH_REPORT.md`` as a markdown string. No I/O; no clock reads."""
    degree = _degree(nodes, edges)
    community_count = len({community_of[node.id] for node in nodes}) if nodes else 0
    sections = [
        f"# GRAPH_REPORT — {repo_name}\n\nGenerated: {generated_at}\n",
        _totals_section(nodes, edges, community_count),
        _confidence_section(edges),
        _degraded_section(degraded_files),
        _most_connected_section(nodes, degree, top_n),
        _community_section(nodes, community_of),
        _isolated_section(nodes, degree),
    ]
    return "\n".join(sections)


def write_report(path: Path, text: str) -> None:
    """Write ``text`` to ``path``, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
