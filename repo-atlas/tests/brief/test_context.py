"""Budgeted context assembly (PRD R4.1, R4.2) — where the token thesis lives."""

from __future__ import annotations

from pathlib import Path

from repo_atlas.brief import context
from repo_atlas.graph_reader import GraphReader
from tests.fixtures import graph_factory

# Deliberately larger than a slice window: on a file smaller than its own slices,
# windowing costs more than the file and the comparison would be meaningless.
_SRC = "\n".join(f"line {index}" for index in range(1, 401)) + "\n"


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "proj"
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "core.py").write_text(_SRC, encoding="utf-8")
    return repo


def _reader(tmp_path: Path) -> GraphReader:
    nodes = [
        graph_factory.make_node("pkg_core", source_file="pkg/core.py", source_location="L1"),
        graph_factory.make_node("pkg_core_run", source_file="pkg/core.py", source_location="L10"),
        graph_factory.make_node(
            "pkg_core_helper", source_file="pkg/core.py", source_location="L20"
        ),
    ]
    edges = [
        graph_factory.make_edge("pkg_core", "pkg_core_run", relation="contains"),
        graph_factory.make_edge("pkg_core", "pkg_core_helper", relation="contains"),
        graph_factory.make_edge("pkg_core_run", "pkg_core_helper", relation="calls"),
    ]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def test_counts_tokens_as_whitespace_words() -> None:
    assert context.count_tokens("alpha beta  gamma") == 3


def test_slices_a_source_window_around_a_node(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    node = _reader(tmp_path).node("pkg_core_run")
    slice_text = context.source_slice(repo, node, window=3)
    assert "line 10" in slice_text
    assert "line 7" in slice_text and "line 13" in slice_text
    assert "line 1\n" not in slice_text


def test_a_slice_near_the_start_does_not_underflow(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    node = _reader(tmp_path).node("pkg_core")
    body = context.source_slice(repo, node, window=5)
    assert "```python\nline 1\n" in body  # clamped at the top of the file, no underflow


def test_a_missing_source_file_yields_nothing(tmp_path: Path) -> None:
    node = _reader(tmp_path).node("pkg_core_run")
    assert context.source_slice(tmp_path / "absent", node, window=3) == ""


def test_graph_context_stays_within_budget(tmp_path: Path) -> None:
    built = context.build_graph_context(
        _reader(tmp_path), _repo(tmp_path), vault_text="index\nhot\n", budget=40, hot_slices=3
    )
    assert context.count_tokens(built.text) <= 40


def test_graph_context_records_what_it_read(tmp_path: Path) -> None:
    built = context.build_graph_context(
        _reader(tmp_path), _repo(tmp_path), vault_text="index", budget=500, hot_slices=2
    )
    assert "pkg/core.py" in built.files_read


def test_graph_context_leads_with_the_vault(tmp_path: Path) -> None:
    """The vault is the map; source slices are the targeted follow-up."""
    built = context.build_graph_context(
        _reader(tmp_path), _repo(tmp_path), vault_text="INDEX-MARKER", budget=500, hot_slices=1
    )
    assert built.text.index("INDEX-MARKER") < 50


def test_a_tiny_budget_still_yields_the_vault(tmp_path: Path) -> None:
    built = context.build_graph_context(
        _reader(tmp_path), _repo(tmp_path), vault_text="index hot", budget=3, hot_slices=3
    )
    assert "index" in built.text


def test_naive_context_dumps_whole_files(tmp_path: Path) -> None:
    built = context.build_naive_context(_repo(tmp_path), ["pkg/core.py"])
    assert "line 1" in built.text and "line 400" in built.text


def test_naive_context_is_larger_than_graph_context(tmp_path: Path) -> None:
    """The whole claim in one assertion."""
    repo = _repo(tmp_path)
    graph = context.build_graph_context(
        _reader(tmp_path), repo, vault_text="index hot", budget=10_000, hot_slices=2
    )
    naive = context.build_naive_context(repo, ["pkg/core.py"])
    assert context.count_tokens(naive.text) > context.count_tokens(graph.text)
