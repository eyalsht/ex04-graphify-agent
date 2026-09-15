"""Decisions that are about the tool rather than about Python.

Two of them: the output directory must never be discovered (a re-run would map its own
prior output), and a non-Python file goes on the map as a file node with no internal
structure.
"""

from __future__ import annotations

from repo_atlas.extractor import discovery, ids, labels
from repo_atlas.extractor.models import ORIGIN_AST, RawNode
from repo_atlas.paths import ExtractorConfig, RunConfig, RunPaths

DOCUMENT = "document"


def config_excluding_output(config: RunConfig, paths: RunPaths) -> ExtractorConfig:
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


def document_node(found: discovery.DiscoveredFile) -> RawNode:
    """A non-Python file is on the map as a file node, with no internal structure."""
    label = labels.module_label(found.rel_path)
    return RawNode(
        id=ids.module_id(found.rel_path),
        label=label,
        norm_label=labels.norm_label(label),
        file_type=DOCUMENT,
        source_file=found.rel_path,
        source_location=labels.MODULE_LOCATION,
        origin=ORIGIN_AST,
    )
