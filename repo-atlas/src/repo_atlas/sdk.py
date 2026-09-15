"""The public façade — every business decision funnels through here (CLAUDE.md §3).

``cli.py`` builds a ``RunPaths`` and calls into this module; it never imports an
extractor, graph_reader, or vault module directly. ``brief()``/``compare()`` join this
surface in a later phase — the seam is left clean rather than stubbed with a fake, so
``map_repo`` does exactly what it can do today: extract, then vault.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repo_atlas.extractor.build import GRAPH_FILENAME, ExtractResult
from repo_atlas.extractor.build import extract as _build_extract
from repo_atlas.graph_reader import GraphReader
from repo_atlas.graph_reader.metrics import DEFAULT_EXACT_MAX_NODES, DEFAULT_SAMPLE_K
from repo_atlas.paths import RunConfig, RunPaths
from repo_atlas.vault import DEFAULT_WEIGHTS, VaultWriter

VAULT_DIRNAME = "vault"
_VAULT_SECTION = "vault"
_GRAPH_READER_SECTION = "graph_reader"
_TOP_K_KEY = "hot_top_k"
_WEIGHTS_KEY = "hot_weights"
_EXACT_MAX_NODES_KEY = "betweenness_exact_max_nodes"
_SAMPLE_K_KEY = "betweenness_sample_k"
_DEFAULT_TOP_K = 8  # VaultWriter.write_all's own default, used only if config omits it


@dataclass(frozen=True)
class VaultResult:
    """Where the vault landed, and how many notes/communities it holds."""

    vault_dir: Path
    node_count: int
    community_count: int


@dataclass(frozen=True)
class _Tunables:
    """Vault-ranking and graph-reader settings, read from the atlas config."""

    top_k: int
    weights: Mapping[str, float]
    exact_max_nodes: int
    sample_k: int


def _section(raw: Any, key: str) -> dict[str, Any]:
    value = raw.get(key) if isinstance(raw, dict) else None
    return value if isinstance(value, dict) else {}


def _load_tunables(config_path: Path) -> _Tunables:
    """Read the optional ``vault``/``graph_reader`` sections of the atlas config.

    ``RunConfig`` (``paths.py``) does not model these yet, so they are read here
    directly; a missing section or key falls back to the same module's own published
    default rather than a value invented in this file.
    """
    raw: Any = json.loads(config_path.read_text(encoding="utf-8"))
    vault_section = _section(raw, _VAULT_SECTION)
    reader_section = _section(raw, _GRAPH_READER_SECTION)
    return _Tunables(
        top_k=int(vault_section.get(_TOP_K_KEY, _DEFAULT_TOP_K)),
        weights=vault_section.get(_WEIGHTS_KEY, DEFAULT_WEIGHTS),
        exact_max_nodes=int(reader_section.get(_EXACT_MAX_NODES_KEY, DEFAULT_EXACT_MAX_NODES)),
        sample_k=int(reader_section.get(_SAMPLE_K_KEY, DEFAULT_SAMPLE_K)),
    )


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
    tunables = _load_tunables(paths.config_path)
    reader = GraphReader(
        graph_path,
        exact_max_nodes=tunables.exact_max_nodes,
        sample_k=tunables.sample_k,
    )
    writer = VaultWriter(reader, paths.out_dir / VAULT_DIRNAME)
    vault_dir = writer.write_all(
        top_k=top_k if top_k is not None else tunables.top_k,
        weights=tunables.weights,
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
