"""``sdk.vault`` — load-or-build the graph, then write the vault (CLAUDE.md §6)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from repo_atlas import sdk
from repo_atlas.paths import RunPaths
from tests.fixtures import graph_factory
from tests.sdk._repo import build_repo

_RANKED_LINE = re.compile(r"^\d+\. ", re.MULTILINE)

_MINIMAL_EXTRACTOR: dict[str, object] = {
    "exclude_dirs": [],
    "exclude_globs": [],
    "max_file_bytes": 1,
    "document_extensions": [],
}


def _graph() -> graph_factory.GraphDict:
    nodes = [
        graph_factory.make_node("mod", community=0),
        graph_factory.make_node("mod_hub", community=0),
        graph_factory.make_node("mod_leaf", community=0),
    ]
    edges = [
        graph_factory.make_edge("mod", "mod_hub", relation="contains"),
        graph_factory.make_edge("mod", "mod_leaf", relation="contains"),
        graph_factory.make_edge("mod_hub", "mod_leaf", relation="calls"),
    ]
    return graph_factory.graph_dict(nodes, edges)


def _paths_with_graph(tmp_path: Path) -> RunPaths:
    repo = tmp_path / "empty-repo"
    repo.mkdir()
    paths = RunPaths.create(repo, out=tmp_path / "out")
    paths.out_dir.mkdir(parents=True, exist_ok=True)
    (paths.out_dir / "graph.json").write_text(json.dumps(_graph()), encoding="utf-8")
    return paths


def test_vault_extracts_first_when_no_graph_exists(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path))
    result = sdk.vault(paths)
    assert (paths.out_dir / "graph.json").is_file()
    assert (result.vault_dir / "index.md").is_file()
    assert (result.vault_dir / "hot.md").is_file()
    assert result.node_count > 0


def test_vault_reuses_an_existing_graph_instead_of_re_extracting(tmp_path: Path) -> None:
    """The repo behind ``paths`` is empty — a re-extract would produce an empty graph."""
    paths = _paths_with_graph(tmp_path)
    result = sdk.vault(paths)
    index = (result.vault_dir / "index.md").read_text(encoding="utf-8")
    assert "mod_hub" in index
    assert "mod_leaf" in index


def test_vault_top_k_argument_overrides_the_config_default(tmp_path: Path) -> None:
    paths = _paths_with_graph(tmp_path)
    result = sdk.vault(paths, top_k=1)
    hot = (result.vault_dir / "hot.md").read_text(encoding="utf-8")
    assert len(_RANKED_LINE.findall(hot)) == 1


def test_vault_reads_hot_top_k_from_the_atlas_config_when_not_overridden(tmp_path: Path) -> None:
    paths = _paths_with_graph(tmp_path)
    config = {
        "provider": "offline",
        "model": "mock-offline",
        "api_key_env": "ATLAS_API_KEY",
        "extractor": _MINIMAL_EXTRACTOR,
        "vault": {"hot_top_k": 1, "hot_weights": {"degree": 1.0, "betweenness": 0.0}},
    }
    config_path = tmp_path / "atlas.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    scoped = RunPaths.create(paths.repo_root, out=paths.out_dir, config=config_path)
    result = sdk.vault(scoped)
    hot = (result.vault_dir / "hot.md").read_text(encoding="utf-8")
    assert len(_RANKED_LINE.findall(hot)) == 1


def test_vault_raises_keyerror_for_an_unknown_seed(tmp_path: Path) -> None:
    paths = _paths_with_graph(tmp_path)
    with pytest.raises(KeyError):
        sdk.vault(paths, seed_id="does-not-exist")


def test_vault_result_reports_node_and_community_counts(tmp_path: Path) -> None:
    paths = _paths_with_graph(tmp_path)
    result = sdk.vault(paths)
    assert result.node_count == 3
    assert result.community_count == 1
