"""TDD for compute_coverage — fraction of hot nodes / modules the brief actually cites.

Coverage definition (documented again in ``coverage.py``'s module docstring): a hot node or
module counts as "cited" when its label, or its source file's repo-relative path, appears
(case-insensitively) anywhere in the brief's section bodies. PRD R5.3.
"""

from __future__ import annotations

from pathlib import Path

from repo_atlas.brief.models import BriefResult, Section
from repo_atlas.graph_reader import GraphReader
from repo_atlas.token_comparison.coverage import compute_coverage
from tests.fixtures import graph_factory


def _reader(tmp_path: Path) -> GraphReader:
    nodes = [
        graph_factory.make_node("pkg_core", source_file="pkg/core.py"),
        graph_factory.make_node("pkg_core_run", source_file="pkg/core.py"),
        graph_factory.make_node("pkg_core_helper", source_file="pkg/core.py"),
        graph_factory.make_node("pkg_util", source_file="pkg/util.py"),
        graph_factory.make_node("pkg_util_helper", source_file="pkg/util.py"),
    ]
    edges = [
        graph_factory.make_edge("pkg_core", "pkg_core_run", relation="contains"),
        graph_factory.make_edge("pkg_core", "pkg_core_helper", relation="contains"),
        graph_factory.make_edge("pkg_util", "pkg_util_helper", relation="contains"),
    ]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def _result(body: str, vault_links: tuple[tuple[str, str], ...]) -> BriefResult:
    return BriefResult(
        repo_name="proj",
        run_type="graph_guided",
        sections=[Section(title="t", body=body, tag="INFERRED")],
        vault_links=vault_links,
    )


def test_hot_node_cited_by_label(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    result = _result(
        "The `pkg_core_run` function drives everything.",
        (("pkg_core_run", "pkg_core_run"), ("pkg_util_helper", "pkg_util_helper")),
    )
    coverage = compute_coverage(result, reader)
    assert coverage.hot_nodes_total == 2
    assert coverage.hot_nodes_cited == 1
    assert coverage.hot_node_coverage == 0.5


def test_hot_node_cited_by_source_file_when_label_is_not_named(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    result = _result(
        "Most of the interesting logic lives in `pkg/util.py`.",
        (("pkg_util_helper", "pkg_util_helper"),),
    )
    coverage = compute_coverage(result, reader)
    assert coverage.hot_nodes_cited == 1
    assert coverage.hot_node_coverage == 1.0


def test_module_coverage_counts_file_root_nodes(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    result = _result("Read `pkg/core.py` first.", ())
    coverage = compute_coverage(result, reader)
    assert coverage.modules_total == 2
    assert coverage.modules_cited == 1
    assert coverage.module_coverage == 0.5


def test_matching_is_case_insensitive(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    result = _result("See PKG_CORE_RUN for the entry point.", (("pkg_core_run", "pkg_core_run"),))
    coverage = compute_coverage(result, reader)
    assert coverage.hot_nodes_cited == 1


def test_empty_brief_scores_zero_coverage(tmp_path: Path) -> None:
    """The degenerate case the coverage metric exists to catch: brevity is not free."""
    reader = _reader(tmp_path)
    result = _result("", (("pkg_core_run", "pkg_core_run"),))
    coverage = compute_coverage(result, reader)
    assert coverage.hot_nodes_cited == 0
    assert coverage.hot_node_coverage == 0.0
    assert coverage.modules_cited == 0
    assert coverage.module_coverage == 0.0


def test_no_hot_nodes_and_no_modules_does_not_divide_by_zero(tmp_path: Path) -> None:
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict())
    reader = GraphReader(path)
    result = _result("anything", ())
    coverage = compute_coverage(result, reader)
    assert coverage.hot_node_coverage == 0.0
    assert coverage.module_coverage == 0.0


def test_unresolvable_hot_node_id_falls_back_to_its_stored_label(tmp_path: Path) -> None:
    """A BriefResult built directly (not via a live reader) still scores on its own label."""
    reader = _reader(tmp_path)
    result = _result("Mentions ghost_node right here.", (("ghost_node", "ghost_node"),))
    coverage = compute_coverage(result, reader)
    assert coverage.hot_nodes_total == 1
    assert coverage.hot_nodes_cited == 1


def test_unresolvable_hot_node_not_cited_when_its_label_is_absent(tmp_path: Path) -> None:
    """No live-graph source file to fall back on, and the label isn't in the prose either."""
    reader = _reader(tmp_path)
    result = _result("Nothing here names it.", (("ghost_node", "ghost_node"),))
    coverage = compute_coverage(result, reader)
    assert coverage.hot_nodes_cited == 0
