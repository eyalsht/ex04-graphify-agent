"""``sdk.extract`` — thin delegation to the AST extractor (CLAUDE.md §6, PLAN §5)."""

from __future__ import annotations

import json
from pathlib import Path

from repo_atlas import sdk
from repo_atlas.extractor.build import ExtractResult
from repo_atlas.paths import RunPaths
from tests.sdk._repo import build_repo


def test_extract_writes_graph_manifest_and_report(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path))
    result = sdk.extract(paths)
    assert isinstance(result, ExtractResult)
    assert result.graph_path.is_file()
    assert result.manifest_path.is_file()
    assert result.report_path.is_file()
    assert result.node_count > 0


def test_extract_writes_under_the_run_paths_out_dir(tmp_path: Path) -> None:
    paths = RunPaths.create(build_repo(tmp_path))
    result = sdk.extract(paths)
    assert result.graph_path.parent == paths.out_dir


def test_extract_forwards_marker_limit_to_the_extractor(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    (repo / "pkg" / "shapes.py").write_text(
        "# TODO: one\n# TODO: two\n# TODO: three\n\n\ndef f():\n    return 1\n",
        encoding="utf-8",
    )
    result = sdk.extract(RunPaths.create(repo), marker_limit=1)
    data = json.loads(result.graph_path.read_text(encoding="utf-8"))
    rationale = [node for node in data["nodes"] if node["file_type"] == "rationale"]
    assert len(rationale) == 1
