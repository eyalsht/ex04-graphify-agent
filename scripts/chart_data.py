"""Chart data — authoritative numbers for the README/notebook visuals (keyless).

Reuses the SDK token-comparison + the config-driven pricing for the keyless run, parses the
committed keyed run from ``reports/token_comparison.md`` (evidence, not estimates), and
builds the bug-localization ROC from the same ``ranking.composite_score`` that drives
``hot.md``. No plotting here — pure data so the figures stay a thin presentation layer.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import numpy as np

from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.graph_reader.models import NodeView
from ex04_graphify_agent.obsidian_writer import ranking
from ex04_graphify_agent.obsidian_writer.config import (
    default_bug_node_id,
    default_hot_md_weights,
)
from ex04_graphify_agent.sdk import Ex04Sdk
from ex04_graphify_agent.token_comparison import TokenComparison
from ex04_graphify_agent.token_comparison.cost import cost_usd, load_pricing

KEYED_REPORT = Path("reports/token_comparison.md")


def keyless_run() -> dict[str, dict[str, float]]:
    """Live keyless graph-guided vs naive metrics (authoritative gatekeeper ledger)."""
    with tempfile.TemporaryDirectory() as tmp:
        result = TokenComparison().run_both(Ex04Sdk(), runs_dir=Path(tmp) / "runs")
    pricing = load_pricing()
    gg, nv = result.graph_guided, result.naive
    return {
        "graph_guided": _row(gg.input_tokens, gg.output_tokens, pricing),
        "naive": _row(nv.input_tokens, nv.output_tokens, pricing),
    }


def keyed_run() -> dict[str, dict[str, float]]:
    """Parse the committed keyed live-run tokens; cost via the config-driven pricing."""
    text = KEYED_REPORT.read_text()
    pricing = load_pricing()
    out: dict[str, dict[str, float]] = {}
    for route in ("graph_guided", "naive"):
        match = re.search(rf"\|\s*{route}\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", text)
        if match is None:
            raise ValueError(f"keyed {route} row not found in {KEYED_REPORT}")
        out[route] = _row(int(match.group(1)), int(match.group(2)), pricing)
    return out


def _row(input_tokens: int, output_tokens: int, pricing: dict[str, float]) -> dict[str, float]:
    return {
        "input": float(input_tokens),
        "output": float(output_tokens),
        "cost": cost_usd(input_tokens, output_tokens, pricing),
    }


def reduction(a: float, b: float) -> float:
    """Percent that ``a`` is below ``b`` (the graph-guided saving vs naive)."""
    return round(100.0 * (b - a) / b, 1) if b else 0.0


def roc_curves() -> dict[str, tuple[np.ndarray, np.ndarray, float]]:
    """ROC for two node rankings vs ground truth 'belongs to the buggy file'.

    Curve ``composite`` = the hot.md metric (centrality * proximity-to-bug); ``centrality``
    = the raw degree/betweenness blend with no proximity term — visualizing exactly the
    R1.4 design choice that proximity floats the polygons file to the top.
    """
    reader = GraphReader()
    weights = default_hot_md_weights()
    bug_node = default_bug_node_id()
    bug_file = reader.node(bug_node).source_file
    nodes = [n for n in reader.all_nodes() if not n.is_file_root]
    distances = ranking.bfs_distances(reader, bug_node)
    max_deg = max((n.degree for n in nodes), default=1) or 1
    max_bw = max((n.betweenness for n in nodes), default=1.0) or 1.0
    labels = np.array([1 if n.source_file == bug_file else 0 for n in nodes])

    def _cent(node: NodeView) -> float:
        return (
            weights["degree"] * node.degree / max_deg
            + weights["betweenness"] * node.betweenness / max_bw
        )

    centrality = np.array([_cent(n) for n in nodes])
    composite = np.array(
        [ranking.composite_score(n, distances, weights, (max_deg, max_bw)) for n in nodes]
    )
    return {
        "composite": _roc(composite, labels),
        "centrality": _roc(centrality, labels),
    }


def _roc(scores: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Tie-aware ROC: returns (fpr, tpr, auc) with the trapezoidal area."""
    order = np.argsort(-scores, kind="stable")
    pos, neg = int(labels.sum()), int(len(labels) - labels.sum())
    assert pos and neg, "ROC needs at least one positive and one negative label"
    fpr, tpr = [0.0], [0.0]
    tp = fp = 0
    prev: float | None = None
    for idx in order:
        if prev is not None and scores[idx] != prev:
            tpr.append(tp / pos)
            fpr.append(fp / neg)
        tp, fp = (tp + 1, fp) if labels[idx] else (tp, fp + 1)
        prev = float(scores[idx])
    tpr.append(tp / pos)
    fpr.append(fp / neg)
    return np.array(fpr), np.array(tpr), float(np.trapezoid(tpr, fpr))
