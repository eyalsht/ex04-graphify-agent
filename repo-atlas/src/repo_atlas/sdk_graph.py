"""Graph-side SDK operations: extract, vault, map. No provider involved.

Split from ``sdk.py`` for the 150-line cap; ``sdk`` re-exports these so callers still see
a single façade (CLAUDE.md §3).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repo_atlas.extractor.build import GRAPH_FILENAME, ExtractResult
from repo_atlas.extractor.build import extract as _build_extract
from repo_atlas.graph_reader import GraphReader
from repo_atlas.paths import RunConfig, RunPaths
from repo_atlas.vault import VaultWriter

VAULT_DIRNAME = "vault"


@dataclass(frozen=True)
class VaultResult:
    """Where the vault landed, and how many notes/communities it holds."""

    vault_dir: Path
    node_count: int
    community_count: int


def extract(paths: RunPaths, marker_limit: int | None = None) -> ExtractResult:
    """Walk ``paths.repo_root`` and write graph.json, manifest.json, GRAPH_REPORT.md."""
    return _build_extract(paths, marker_limit=marker_limit)


def vault(paths: RunPaths, top_k: int | None = None, seed_id: str | None = None) -> VaultResult:
    """Load the graph — extracting first if none exists yet — and write the vault.

    Raises:
        KeyError: ``seed_id`` is not a node in the graph.
    """
    RunConfig.load(paths.config_path)  # fail loud on a missing/invalid config, as extract() does
    graph_path = paths.out_dir / GRAPH_FILENAME
    if not graph_path.is_file():
        extract(paths)
    config = RunConfig.load(paths.config_path)
    reader = GraphReader(
        graph_path,
        exact_max_nodes=config.graph_reader.betweenness_exact_max_nodes,
        sample_k=config.graph_reader.betweenness_sample_k,
    )
    writer = VaultWriter(reader, paths.out_dir / VAULT_DIRNAME)
    vault_dir = writer.write_all(
        top_k=top_k if top_k is not None else config.vault.hot_top_k,
        weights=config.vault.hot_weights,
        seed_id=seed_id,
    )
    return VaultResult(
        vault_dir=vault_dir,
        node_count=len(reader.all_nodes()),
        community_count=len(reader.communities()),
    )


def map_repo(
    paths: RunPaths,
    marker_limit: int | None = None,
    seed_id: str | None = None,
) -> tuple[ExtractResult, VaultResult]:
    """Extract, then write the vault, in one pass. ``brief()`` joins this seam later.

    Raises:
        KeyError: ``seed_id`` is not a node in the freshly extracted graph.
    """
    extract_result = extract(paths, marker_limit=marker_limit)
    vault_result = vault(paths, seed_id=seed_id)
    return extract_result, vault_result
