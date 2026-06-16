"""Render a Graphify graph.json to a static PNG (keyless, deterministic layout).

A committed *visual* of the knowledge graph for the Phase-7 reports - distinct from the
required Obsidian graph-view screenshot (R5.4.1), which a human captures from the Obsidian
app. Nodes are coloured by community, sized by degree, and the bug/god node
(``polygons_polygons_polygon``) is ringed so the "core abstraction" is obvious at a glance.

Usage:
    uv run python scripts/render_graph.py [GRAPH_JSON] [OUT_PNG] [TITLE]

Defaults to the PRE-FIX baseline from ``config/paths.json`` -> ``reports/img/graph_pre_fix.png``.
No LLM, no API key, no network. The spring layout is seeded so output is reproducible.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

_ROOT = Path(__file__).resolve().parent.parent
_BUG_NODE = "polygons_polygons_polygon"
_SEED = 7


def _default_graph_path() -> Path:
    paths = json.loads((_ROOT / "config" / "paths.json").read_text(encoding="utf-8"))
    return _ROOT / str(paths["graph_json"])


def _load_graph(path: Path) -> nx.Graph:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    graph: nx.Graph = nx.node_link_graph(data, edges="links")
    return graph


def _node_label(graph: nx.Graph, node_id: str) -> str:
    label = graph.nodes[node_id].get("label", node_id)
    return str(label)


def render(graph_path: Path, out_png: Path, title: str) -> Path:
    """Draw ``graph_path`` to ``out_png`` and return the written path."""
    graph = _load_graph(graph_path)
    pos = nx.spring_layout(graph, seed=_SEED, k=0.9)
    communities = [int(graph.nodes[n].get("community", 0)) for n in graph.nodes]
    degrees = dict(graph.degree())
    sizes = [300 + 700 * degrees[n] for n in graph.nodes]

    fig, ax = plt.subplots(figsize=(15, 11))
    nx.draw_networkx_edges(graph, pos, ax=ax, alpha=0.3, width=1.2)
    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_size=sizes,
        node_color=communities,
        cmap=plt.cm.tab10,
        vmin=0,
        vmax=9,  # type: ignore[attr-defined]
    )
    if _BUG_NODE in graph:
        nx.draw_networkx_nodes(
            graph,
            pos,
            ax=ax,
            nodelist=[_BUG_NODE],
            node_size=300 + 700 * degrees[_BUG_NODE],
            node_color="none",
            edgecolors="red",
            linewidths=3.5,
        )
    labels = {n: _node_label(graph, n) for n in graph.nodes}
    nx.draw_networkx_labels(graph, pos, labels=labels, ax=ax, font_size=7)

    ax.set_title(title, fontsize=15)
    ax.text(
        0.01,
        0.01,
        f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges - "
        "node size = degree, colour = community, red ring = Polygon god node",
        transform=ax.transAxes,
        fontsize=9,
        color="#444",
    )
    ax.axis("off")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out_png


def main(argv: list[str]) -> int:
    graph_path = Path(argv[0]) if len(argv) > 0 else _default_graph_path()
    out_png = Path(argv[1]) if len(argv) > 1 else _ROOT / "reports" / "img" / "graph_pre_fix.png"
    title = argv[2] if len(argv) > 2 else "Graphify knowledge graph - broken-python (PRE-FIX)"
    written = render(graph_path, out_png, title)
    print(f"Wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
