"""Shared helpers for the golden-regression eval (ADR-0001, EXTRACTOR_SPEC §10).

The only place in the suite permitted to read ``tests/fixtures/golden/``. Everything else
builds synthetic graphs with the factory — see CLAUDE.md §7.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_atlas.extractor import parse, py_edges, py_nodes
from repo_atlas.extractor.models import RawEdge, RawNode

GOLDEN = Path(__file__).resolve().parents[1] / "fixtures" / "golden"
SOURCE_ROOT = GOLDEN / "broken-python"

#: Nodes the reference got from its LLM/document pipeline, which an AST extractor cannot
#: and should not reproduce (ADR-0001).
EXCLUDED_NODES = frozenset(
    {
        "license_mit_license",
        "readme_broken_python",
        "mathsquiz_readme_maths_quiz",
        "mathsquiz_mathsquiz_final_py",
    }
)

#: The one in-scope edge we knowingly cannot reach: it is a call site inside the region of
#: polygons.py that fails to parse, and the degraded scan does not guess at call edges.
KNOWN_MISS = ("calls", "polygons_polygons_calc_polygon_details", "polygons_polygons_polygon")


def reference() -> dict[str, Any]:
    data: dict[str, Any] = json.loads((GOLDEN / "reference_graph.json").read_text("utf-8"))
    return data


def reference_ast_nodes() -> dict[str, dict[str, Any]]:
    """The reference's AST-pipeline nodes, keyed by id. ``_origin`` is the discriminator."""
    return {n["id"]: n for n in reference()["nodes"] if n.get("_origin") == "ast"}


def reference_in_scope_edges() -> set[tuple[str, str, str]]:
    return {
        (e["relation"], e["source"], e["target"])
        for e in reference()["links"]
        if e["source"] not in EXCLUDED_NODES and e["target"] not in EXCLUDED_NODES
    }


def extract() -> tuple[dict[str, RawNode], list[RawEdge], set[str]]:
    """Run our extractor over the golden source. Returns nodes, edges, degraded files."""
    nodes: dict[str, RawNode] = {}
    edges: list[RawEdge] = []
    degraded: set[str] = set()
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        relative = path.relative_to(SOURCE_ROOT).as_posix()
        parsed = parse.parse_source(relative, path.read_text(encoding="utf-8"))
        if parsed.degraded:
            degraded.add(relative)
        built = py_nodes.build_file_nodes(parsed)
        nodes.update({node.id: node for node in built.nodes})
        edges.extend(py_edges.build_edges(parsed, built))
    return nodes, edges, degraded
