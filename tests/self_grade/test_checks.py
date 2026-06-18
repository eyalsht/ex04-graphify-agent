"""Structural self-grade checks (PHASE8-029/035/037/041): keyless, deterministic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04_graphify_agent.self_grade import checks
from ex04_graphify_agent.self_grade.config import load_config, repo_root, sha256_of


def _cfg() -> dict[str, Any]:
    return load_config(repo_root())


def test_requirement_coverage_passes_on_real_repo() -> None:
    result = checks.requirement_coverage(repo_root(), _cfg())
    assert result.passed is True
    assert "R-ids" in result.detail


def test_requirement_coverage_fails_on_missing_artifact(tmp_path: Path) -> None:
    cfg = {"requirement_artifacts": {"R9.9": "does/not/exist.md"}}
    result = checks.requirement_coverage(tmp_path, cfg)
    assert result.passed is False
    assert "R9.9" in result.detail


def test_hot_md_consistent_passes_on_real_vault() -> None:
    result = checks.hot_md_consistent(repo_root(), _cfg())
    assert result.passed is True


def test_hot_md_consistent_fails_when_absent(tmp_path: Path) -> None:
    result = checks.hot_md_consistent(tmp_path, {"hot_md": "obsidian/hot.md"})
    assert result.passed is False


def test_baselines_unmodified_passes_on_real_baseline() -> None:
    result = checks.baselines_unmodified(repo_root(), _cfg())
    assert result.passed is True


def test_baselines_unmodified_detects_drift(tmp_path: Path) -> None:
    rel = "artifacts/graphify/graph.json"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("tampered", encoding="utf-8")
    cfg = {"baseline_hashes": {rel: "deadbeef"}}
    result = checks.baselines_unmodified(tmp_path, cfg)
    assert result.passed is False
    assert rel in result.detail


def test_grade_documented_passes_when_number_present() -> None:
    result = checks.grade_documented(repo_root(), 90)
    assert result.passed is True


def test_grade_documented_fails_when_absent(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "KNOWN_LIMITATIONS.md").write_text("no grade here", encoding="utf-8")
    result = checks.grade_documented(tmp_path, 90)
    assert result.passed is False


def test_sha256_of_is_stable() -> None:
    path = repo_root() / "artifacts" / "graphify" / "graph.json"
    assert sha256_of(path) == sha256_of(path)
