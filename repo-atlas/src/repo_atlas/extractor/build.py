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
    py_edges,
    py_nodes,
    report,
    serialize,
)
from repo_atlas.extractor.models import RawEdge, RawNode
from repo_atlas.paths import ExtractorConfig, RunConfig, RunPaths

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


def _config_excluding_output(config: RunConfig, paths: RunPaths) -> ExtractorConfig:
    """Add the output directory to the exclusions, so a re-run never maps its own output."""
    extractor = config.extractor
    try:
        output_dir = paths.out_dir.relative_to(paths.repo_root).parts[0]
    except ValueError:
        return extractor  # output lives outside the repo; nothing to exclude
    if output_dir in extractor.exclude_dirs:
        return extractor
    return ExtractorConfig(
        exclude_dirs=(*extractor.exclude_dirs, output_dir),
        exclude_globs=extractor.exclude_globs,
        max_file_bytes=extractor.max_file_bytes,
        document_extensions=extractor.document_extensions,
    )


def _extract_python(
    found: discovery.DiscoveredFile, marker_limit: int | None
) -> tuple[list[RawNode], list[RawEdge], bool]:
    source = discovery.read_discovered_text(found)
    parsed = parse.parse_source(found.rel_path, source, marker_limit)
    built = py_nodes.build_file_nodes(parsed, marker_limit)
    return list(built.nodes), py_edges.build_edges(parsed, built), parsed.degraded


def _document_node(found: discovery.DiscoveredFile) -> RawNode:
    """A non-Python file is on the map as a file node, with no internal structure."""
    from repo_atlas.extractor import ids, labels

    label = labels.module_label(found.rel_path)
    return RawNode(
        id=ids.module_id(found.rel_path),
        label=label,
        norm_label=labels.norm_label(label),
        file_type="document",
        source_file=found.rel_path,
        source_location=labels.MODULE_LOCATION,
        origin="ast",
    )


def extract(paths: RunPaths, marker_limit: int | None = None) -> ExtractResult:
    """Walk the repo, build the graph, and write graph.json, manifest.json and the report."""
    config = RunConfig.load(paths.config_path)
    found = discovery.discover_files(paths.repo_root, _config_excluding_output(config, paths))

    nodes: list[RawNode] = []
    edges: list[RawEdge] = []
    degraded: list[str] = []
    python_files: dict[str, Path] = {}

    for item in found:
        if item.kind != PYTHON:
            nodes.append(_document_node(item))
            continue
        python_files[item.rel_path] = item.abs_path
        file_nodes, file_edges, was_degraded = _extract_python(item, marker_limit)
        nodes.extend(file_nodes)
        edges.extend(file_edges)
        if was_degraded:
            degraded.append(item.rel_path)

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
