"""Graph-only PART-C signals 1 (god node) and 2 (ambiguous edge).

Signals 3/4/5 live in ``signals_graph_b``; signal 6 (source-peek) in ``signals_source``.
Language strength is locked to the confidence tag (CLAUDE.md inference discipline):
EXTRACTED states facts (no "may"/"suggests"); INFERRED hedges. Nodes are addressed by id
never label (WD-E3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .hypothesis import WeaknessFinding

if TYPE_CHECKING:
    from ex04_graphify_agent.graph_reader import GraphReader

TARGET_SOURCE = "polygons/polygons.py"


def god_node(reader: GraphReader, thresholds: dict[str, Any]) -> list[WeaknessFinding]:
    """Signal 1 — highest-degree bottleneck node (EXTRACTED, primary)."""
    floor = int(thresholds["god_node_min_degree"])
    findings: list[WeaknessFinding] = []
    for node in reader.top_n_by_degree(len(reader.all_nodes())):
        if node.degree < floor:
            break
        hypo = (
            f"`{node.label}` (`{node.id}`) is the highest-degree node "
            f"(degree {node.degree}) and bridges its communities — it is the core "
            "abstraction and the first place to investigate."
        )
        findings.append(
            WeaknessFinding(
                signal=1,
                tag="EXTRACTED",
                hypothesis=hypo,
                priority="primary",
                source_file=node.source_file or TARGET_SOURCE,
                nodes=[node.id],
                edges=[(e.source, e.target) for e in reader.edges_of(node.id)],
            )
        )
    return findings


def ambiguous_edge(reader: GraphReader, thresholds: dict[str, Any]) -> list[WeaknessFinding]:
    """Signal 2 — INFERRED edges flagged for a source-peek-first (INFERRED, secondary).

    Works off INFERRED edges + threshold; never crashes on 0 AMBIGUOUS edges (WD-E2).
    The ``ambiguous_confidence_max`` threshold marks which edges most need confirming.
    """
    floor = float(thresholds["ambiguous_confidence_max"])
    findings: list[WeaknessFinding] = []
    inferred = sorted(
        reader.edges_with_confidence("INFERRED"),
        key=lambda e: (e.confidence_score, e.source, e.target),
    )
    for edge in inferred:
        flag = "open `source_file` to confirm" if edge.confidence_score <= floor else "review"
        src = reader.node(edge.source)
        tgt = reader.node(edge.target)
        hypo = (
            f"The graph suggests `{src.label}` may be {edge.relation.replace('_', ' ')} "
            f"`{tgt.label}` (confidence {edge.confidence_score}); {flag} before treating "
            "as fact. Secondary — not the primary fix."
        )
        findings.append(
            WeaknessFinding(
                signal=2,
                tag="INFERRED",
                hypothesis=hypo,
                priority="secondary",
                source_file=edge.source_file or src.source_file,
                nodes=[edge.source, edge.target],
                edges=[(edge.source, edge.target)],
            )
        )
    return findings
