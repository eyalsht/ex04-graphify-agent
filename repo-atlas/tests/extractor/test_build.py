"""End-to-end extraction: a repo directory in, graph.json + manifest + report out."""

from __future__ import annotations

import json
from pathlib import Path

from repo_atlas.extractor import build
from repo_atlas.paths import RunPaths

_MOD = """class Shape:
    def area(self):
        return 0


def make(kind):
    # TODO: support more kinds
    return Shape()
"""


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "proj"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "shapes.py").write_text(_MOD, encoding="utf-8")
    (repo / "README.md").write_text("# Proj\n", encoding="utf-8")
    return repo


def _run(tmp_path: Path) -> tuple[Path, dict]:
    paths = RunPaths.create(_repo(tmp_path))
    result = build.extract(paths)
    return result.graph_path, json.loads(result.graph_path.read_text(encoding="utf-8"))


def test_writes_all_three_artifacts(tmp_path: Path) -> None:
    paths = RunPaths.create(_repo(tmp_path))
    result = build.extract(paths)
    assert result.graph_path.is_file()
    assert result.manifest_path.is_file()
    assert result.report_path.is_file()


def test_graph_has_the_expected_envelope(tmp_path: Path) -> None:
    _, data = _run(tmp_path)
    assert data["directed"] is False
    assert data["multigraph"] is False
    assert {"nodes", "links", "graph"} <= set(data)


def test_nodes_cover_the_modules_classes_and_functions(tmp_path: Path) -> None:
    _, data = _run(tmp_path)
    ids = {node["id"] for node in data["nodes"]}
    assert {"pkg_shapes", "pkg_shapes_shape", "pkg_shapes_shape_area", "pkg_shapes_make"} <= ids


def test_every_node_carries_a_community(tmp_path: Path) -> None:
    _, data = _run(tmp_path)
    assert all(isinstance(node["community"], int) for node in data["nodes"])


def test_marker_comments_become_rationale_nodes(tmp_path: Path) -> None:
    _, data = _run(tmp_path)
    assert any(node["file_type"] == "rationale" for node in data["nodes"])


def test_documents_are_indexed_as_file_nodes(tmp_path: Path) -> None:
    _, data = _run(tmp_path)
    assert "readme_md" in {node["id"] for node in data["nodes"]}


def test_output_directory_is_not_re_discovered_on_a_second_run(tmp_path: Path) -> None:
    """The tool must never map its own output — nothing about .atlas is repo structure."""
    paths = RunPaths.create(_repo(tmp_path))
    build.extract(paths)
    second = build.extract(paths)
    data = json.loads(second.graph_path.read_text(encoding="utf-8"))
    assert not [n for n in data["nodes"] if n["source_file"].startswith(".atlas")]


def test_a_second_run_differs_only_in_its_timestamp(tmp_path: Path) -> None:
    """Deterministic output is what makes a graph diff mean anything. The build stamp is
    the one field allowed to move, so it is normalised out rather than asserted stable —
    comparing raw bytes here would flake whenever two runs straddle a second boundary."""
    paths = RunPaths.create(_repo(tmp_path))
    first = json.loads(build.extract(paths).graph_path.read_text(encoding="utf-8"))
    second = json.loads(build.extract(paths).graph_path.read_text(encoding="utf-8"))
    for payload in (first, second):
        payload["graph"].pop("generated_at", None)
    assert first == second


def test_degraded_files_are_reported(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "legacy.py").write_text('print "python 2"\n', encoding="utf-8")
    result = build.extract(RunPaths.create(repo))
    assert "legacy.py" in result.degraded_files
    assert "legacy.py" in result.report_path.read_text(encoding="utf-8")


def test_an_empty_repo_produces_an_empty_graph(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    data = json.loads(build.extract(RunPaths.create(empty)).graph_path.read_text(encoding="utf-8"))
    assert data["nodes"] == []


def test_two_files_inheriting_the_same_external_share_one_node(tmp_path: Path) -> None:
    """An external symbol is one fact about the repo, not one per file that mentions it.

    Regression: two modules each defining `class X(RuntimeError)` both emitted an external
    node `runtimeerror`, and graph assembly rejected the duplicate — so any repo with two
    exception subclasses in different files could not be mapped at all.
    """
    repo = _repo(tmp_path)
    (repo / "pkg" / "a.py").write_text("class AError(RuntimeError):\n    pass\n", encoding="utf-8")
    (repo / "pkg" / "b.py").write_text("class BError(RuntimeError):\n    pass\n", encoding="utf-8")
    result = build.extract(RunPaths.create(repo))
    data = json.loads(result.graph_path.read_text(encoding="utf-8"))
    externals = [node for node in data["nodes"] if node["id"] == "runtimeerror"]
    assert len(externals) == 1
    inherits = [
        link
        for link in data["links"]
        if link["relation"] == "inherits" and link["target"] == "runtimeerror"
    ]
    assert len(inherits) == 2
