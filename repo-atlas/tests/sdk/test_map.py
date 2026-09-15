"""``sdk.map_repo`` — extract then vault in one pass; ``brief()`` joins later (CLAUDE.md §6)."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas import sdk
from repo_atlas.paths import RunPaths
from tests.sdk._repo import build_large_repo, build_repo

_SEED = "pkg_shapes_make"


def test_map_repo_extracts_then_writes_the_vault(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path))
    extract_result, vault_result = sdk.map_repo(paths)
    assert extract_result.graph_path.is_file()
    assert extract_result.node_count > 0
    assert (vault_result.vault_dir / "index.md").is_file()
    assert (vault_result.vault_dir / "hot.md").is_file()


def test_map_repo_forwards_the_seed_to_the_vault(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path))
    _, vault_result = sdk.map_repo(paths, seed_id=_SEED)
    hot = (vault_result.vault_dir / "hot.md").read_text(encoding="utf-8")
    assert "proximity" in hot
    assert _SEED in hot


def test_map_repo_propagates_an_unknown_seed_as_a_keyerror(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path))
    with pytest.raises(KeyError):
        sdk.map_repo(paths, seed_id="does-not-exist")


def test_brief_writes_a_brief_from_the_graph_and_vault(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path), out=tmp_path / "out")
    result = sdk.brief(paths)
    assert result.brief_path.is_file()
    assert result.brief_path.read_text(encoding="utf-8").startswith("#")


def test_brief_runs_extract_and_vault_first_when_needed(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path), out=tmp_path / "out")
    sdk.brief(paths)
    assert (paths.out_dir / "graph.json").is_file()
    assert (paths.out_dir / "vault" / "hot.md").is_file()


def test_brief_logs_its_token_usage(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path), out=tmp_path / "out")
    result = sdk.brief(paths)
    assert result.result.token_usage
    assert (paths.out_dir / "runs").is_dir()


def test_compare_writes_a_report_with_both_routes(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path), out=tmp_path / "out")
    outcome = sdk.compare(paths)
    assert outcome.report_path.is_file()
    body = outcome.report_path.read_text(encoding="utf-8")
    assert "graph_guided" in body and "naive" in body


def test_compare_shows_a_real_token_reduction_keylessly(tmp_path: Path) -> None:
    """The central claim, provable with no API key because the offline client counts the
    prompt's real tokens rather than returning a stub zero. Needs a repo past the crossover
    where retrieval beats dumping — see build_large_repo."""
    paths = RunPaths.create(build_large_repo(tmp_path), out=tmp_path / "out")
    outcome = sdk.compare(paths)
    assert outcome.result.input_token_reduction_pct > 0
    assert outcome.result.graph_guided.input_tokens < outcome.result.naive.input_tokens


def test_compare_logs_both_routes_separately(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path), out=tmp_path / "out")
    sdk.compare(paths)
    assert (paths.out_dir / "runs").is_dir()
