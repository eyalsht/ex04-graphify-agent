"""RED/GREEN tests for ``RunPaths`` — every path is a parameter (ADR-0003, PHASE1-003)."""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.paths import RunPaths

_SHIPPED_CONFIG = Path(__file__).resolve().parents[1] / "config" / "atlas.json"


def test_create_resolves_repo_root_to_an_absolute_path(tmp_path: Path) -> None:
    paths = RunPaths.create(repo=tmp_path)
    assert paths.repo_root == tmp_path.resolve()
    assert paths.repo_root.is_absolute()


def test_create_defaults_out_dir_to_dot_atlas_under_the_repo(tmp_path: Path) -> None:
    paths = RunPaths.create(repo=tmp_path)
    assert paths.out_dir == (tmp_path / ".atlas").resolve()


def test_create_honours_an_explicit_out_dir(tmp_path: Path) -> None:
    explicit = tmp_path / "elsewhere" / "out"
    paths = RunPaths.create(repo=tmp_path, out=explicit)
    assert paths.out_dir == explicit.resolve()


def test_create_defaults_config_path_to_the_shipped_config(tmp_path: Path) -> None:
    paths = RunPaths.create(repo=tmp_path)
    assert paths.config_path == _SHIPPED_CONFIG.resolve()
    assert paths.config_path.is_file()


def test_create_honours_an_explicit_config_path(tmp_path: Path) -> None:
    explicit = tmp_path / "custom-atlas.json"
    explicit.write_text("{}", encoding="utf-8")
    paths = RunPaths.create(repo=tmp_path, config=explicit)
    assert paths.config_path == explicit.resolve()


def test_create_resolves_a_relative_repo_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    monkeypatch.chdir(tmp_path)
    paths = RunPaths.create(repo=Path("nested"))
    assert paths.repo_root == nested.resolve()


def test_create_raises_file_not_found_when_repo_root_does_not_exist(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    with pytest.raises(FileNotFoundError):
        RunPaths.create(repo=missing)


def test_create_raises_not_a_directory_when_repo_root_is_a_file(tmp_path: Path) -> None:
    a_file = tmp_path / "not-a-dir.txt"
    a_file.write_text("x", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        RunPaths.create(repo=a_file)


def test_run_paths_is_frozen(tmp_path: Path) -> None:
    paths = RunPaths.create(repo=tmp_path)
    with pytest.raises(AttributeError):
        paths.repo_root = tmp_path
