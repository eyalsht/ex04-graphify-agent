"""End-to-end extraction: a repository directory in, ``graph.json`` and friends out.

The orchestration seam. Every rule lives in the module it belongs to; this file only
sequences them and decides where the bytes land.

One rule does live here, because it is about the tool rather than about Python: the
output directory is excluded from discovery. Without that, a second ``atlas`` run maps
its own prior output and the graph fills with nodes describing the map instead of the
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from repo_atlas.extractor import (
    communities,
    discovery,
    manifest,
    parse,
    policy,
    py_edges,
    py_nodes,
    report,
    resolve,
    serialize,
)
from repo_atlas.extractor.models import FileSymbols, RawEdge, RawNode
from repo_atlas.paths import RunConfig, RunPaths

GRAPH_FILENAME = "graph.json"
MANIFEST_FILENAME = "manifest.json"
REPORT_FILENAME = "GRAPH_REPORT.md"
PYTHON = "python"


@dataclass(frozen=True)
class ExtractResult:
    """Where the artifacts landed, and what was soft about the extraction."""

    graph_path: Path
    manifest_path: Path
    report_path: Path
    node_count: int
    edge_count: int
    degraded_files: tuple[str, ...]


def _extract_python(
    found: discovery.DiscoveredFile, marker_limit: int | None
) -> tuple[FileSymbols, py_nodes.FileNodes]:
    source = discovery.read_discovered_text(found)
    parsed = parse.parse_source(found.rel_path, source, marker_limit)
    return parsed, py_nodes.build_file_nodes(parsed, marker_limit)


def _deduplicate(nodes: list[RawNode]) -> list[RawNode]:
    """Collapse repeated external symbols; raise on any other duplicate id.

    An unresolved external (``source_file == ""``) is deliberately shared: two modules
    subclassing RuntimeError describe one RuntimeError, not two. Every other duplicate id
    means two real constructs collided, which would silently lose one of them.
    """
    seen: dict[str, RawNode] = {}
    for node in nodes:
        existing = seen.get(node.id)
        if existing is None:
            seen[node.id] = node
            continue
        if existing.source_file or node.source_file:
            raise ValueError(
                f"node id {node.id!r} is produced by both {existing.source_file!r} and "
                f"{node.source_file!r} — rename one construct or the graph loses it"
            )
    return list(seen.values())


def extract(paths: RunPaths, marker_limit: int | None = None) -> ExtractResult:
    """Walk the repo, build the graph, and write graph.json, manifest.json and the report."""
    config = RunConfig.load(paths.config_path)
    found = discovery.discover_files(paths.repo_root, policy.config_excluding_output(config, paths))

    nodes: list[RawNode] = []
    edges: list[RawEdge] = []
    degraded: list[str] = []
    python_files: dict[str, Path] = {}

    parsed_files: dict[str, FileSymbols] = {}
    built_files: dict[str, py_nodes.FileNodes] = {}
    for item in found:
        if item.kind != PYTHON:
            nodes.append(policy.document_node(item))
            continue
        python_files[item.rel_path] = item.abs_path
        parsed, built = _extract_python(item, marker_limit)
        parsed_files[item.rel_path] = parsed
        built_files[item.rel_path] = built
        nodes.extend(built.nodes)
        edges.extend(py_edges.build_edges(parsed, built))
        if parsed.degraded:
            degraded.append(item.rel_path)

    # Only now, with every module known, can imports resolve to real nodes. Without this
    # pass each file is an island and every centrality measure degenerates.
    edges.extend(resolve.cross_file_edges(parsed_files, built_files))

    nodes = _deduplicate(nodes)
    community_of = communities.assign_communities(nodes, edges)
    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    repo_name = paths.repo_root.name

    paths.out_dir.mkdir(parents=True, exist_ok=True)
    graph_path = paths.out_dir / GRAPH_FILENAME
    serialize.write_graph(
        graph_path,
        serialize.build_graph(
            nodes, edges, community_of, repo_name=repo_name, generated_at=generated_at
        ),
    )
    manifest_path = paths.out_dir / MANIFEST_FILENAME
    manifest.write_manifest(manifest_path, manifest.build_manifest(python_files))
    report_path = paths.out_dir / REPORT_FILENAME
    report.write_report(
        report_path,
        report.render_report(
            nodes,
            edges,
            community_of,
            repo_name=repo_name,
            generated_at=generated_at,
            degraded_files=degraded,
        ),
    )
    return ExtractResult(
        graph_path=graph_path,
        manifest_path=manifest_path,
        report_path=report_path,
        node_count=len(nodes),
        edge_count=len(edges),
        degraded_files=tuple(degraded),
    )
