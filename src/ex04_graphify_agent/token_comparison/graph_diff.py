"""diff_graphs — PRE-FIX vs POST-FIX graph.json structural diff (PHASE6-048..057, R5.6.3).

Compares node/edge counts, communities, confidence mix, and lists removed/added node ids.
TC-E3: if the POST-FIX graph is absent, fail loud (``FileNotFoundError``) - the report
section is rendered as "pending re-run" by ``render_graph_diff_pending``, never a
fabricated diff.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_USAGE_RELATION = "calls"
_USAGE_TARGET = "polygons_polygons_polygon"


@dataclass
class GraphDiff:
    """Structural PRE vs POST-FIX comparison (R5.6.3)."""

    pre_node_count: int
    post_node_count: int
    pre_edge_count: int
    post_edge_count: int
    removed_nodes: list[str] = field(default_factory=list)
    added_nodes: list[str] = field(default_factory=list)
    pre_communities: set[int] = field(default_factory=set)
    post_communities: set[int] = field(default_factory=set)
    usage_edge_note: str = ""

    @property
    def node_count_change(self) -> str:
        return f"{self.pre_node_count} -> {self.post_node_count}"

    @property
    def edge_count_change(self) -> str:
        return f"{self.pre_edge_count} -> {self.post_edge_count}"


def diff_graphs(pre_fix: str | Path, post_fix: str | Path) -> GraphDiff:
    """Diff the PRE-FIX baseline against the POST-FIX graph; fail loud if POST is absent."""
    post_path = Path(post_fix)
    if not post_path.is_file():
        msg = (
            f"POST-FIX graph not found ({post_path}) - graph diff is pending re-run "
            "(R5.6.3): re-run Graphify on the fixed data/broken-python/ to produce it."
        )
        raise FileNotFoundError(msg)
    pre = _load(Path(pre_fix))
    post = _load(post_path)
    pre_ids = {n["id"] for n in pre["nodes"]}
    post_ids = {n["id"] for n in post["nodes"]}
    return GraphDiff(
        pre_node_count=len(pre["nodes"]),
        post_node_count=len(post["nodes"]),
        pre_edge_count=len(pre["links"]),
        post_edge_count=len(post["links"]),
        removed_nodes=sorted(pre_ids - post_ids),
        added_nodes=sorted(post_ids - pre_ids),
        pre_communities={n["community"] for n in pre["nodes"]},
        post_communities={n["community"] for n in post["nodes"]},
        usage_edge_note=_usage_edge_note(post),
    )


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _usage_edge_note(post: dict[str, Any]) -> str:
    """PHASE6-056/057: confirm a real usage edge into the Polygon node post-fix."""
    for link in post["links"]:
        if link.get("relation") == _USAGE_RELATION and link.get("target") == _USAGE_TARGET:
            return (
                f"{link['source']} -{_USAGE_RELATION}-> {_USAGE_TARGET}: "
                "Polygon is used (not dead) post-fix."
            )
    return f"{_USAGE_TARGET}: no '{_USAGE_RELATION}' usage edge found post-fix."


def render_graph_diff(diff: GraphDiff) -> str:
    """Render the R5.6.3 graph-diff section as markdown."""
    lines = [
        "## R5.6.3 - PRE-FIX vs POST-FIX graph diff",
        "",
        f"- Nodes: {diff.node_count_change}",
        f"- Edges: {diff.edge_count_change}",
        f"- Communities (PRE): {sorted(diff.pre_communities)}",
        f"- Communities (POST): {sorted(diff.post_communities)}",
        f"- Removed nodes: {', '.join(diff.removed_nodes) or '(none)'}",
        f"- Added nodes: {', '.join(diff.added_nodes) or '(none)'}",
        f"- Usage edge: {diff.usage_edge_note}",
    ]
    return "\n".join(lines) + "\n"


def render_graph_diff_pending() -> str:
    """TC-E3: render the diff section as "pending re-run" when POST-FIX is absent."""
    return (
        "## R5.6.3 - PRE-FIX vs POST-FIX graph diff\n\n"
        "Graph diff pending re-run: artifacts/graphify_post_fix/graph.json does not exist "
        "yet. Re-run Graphify on the fixed data/broken-python/ to produce it (R5.6.3).\n"
    )
