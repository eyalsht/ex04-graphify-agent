"""Load graph.json into an in-memory networkx graph.

The default graph path is config-driven (``config/paths.json`` ``graph_json``) — never a
literal (CLAUDE.md §3). ``networkx.node_link_graph`` is the canonical reader for this exact
node-link schema (the file was produced by it — note the ``"links"`` key).
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

_PATHS_CONFIG = "config/paths.json"
_GRAPH_JSON_KEY = "graph_json"


@functools.cache
def _find_repo_root() -> Path:
    """Walk up from this module until a directory containing ``config/`` is found.

    Cached: the repo root is static for the process, so the filesystem walk runs once.
    """
    for parent in Path(__file__).resolve().parents:
        if (parent / _PATHS_CONFIG).is_file():
            return parent
    msg = f"could not locate {_PATHS_CONFIG} above {__file__}"
    raise FileNotFoundError(msg)


def default_graph_path() -> Path:
    """Resolve the baseline graph path from ``config/paths.json`` (config-driven)."""
    root = _find_repo_root()
    config = json.loads((root / _PATHS_CONFIG).read_text(encoding="utf-8"))
    return root / str(config[_GRAPH_JSON_KEY])


def load_graph_data(path: Path) -> dict[str, Any]:
    """Read the raw node-link JSON payload from ``path`` (streamed, no intermediate str)."""
    with path.open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    return data


def build_graph(data: dict[str, Any]) -> nx.Graph:
    """Reconstruct an undirected networkx graph from node-link JSON."""
    graph: nx.Graph = nx.node_link_graph(data, edges="links")
    return graph


def load_graph(path: str | Path | None = None) -> nx.Graph:
    """Load ``graph.json`` (default: config path) into a networkx graph."""
    resolved = Path(path) if path is not None else default_graph_path()
    return build_graph(load_graph_data(resolved))
