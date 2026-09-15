"""Hot-node ranking (PRD R3.2, R3.3).

The origin ranked by proximity to a hardcoded bug node and, when that id was absent,
silently scored every node 0.0 while still printing that it had ranked by proximity.
Both halves of that failure are pinned here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.graph_reader import GraphReader
from repo_atlas.vault import ranking
from tests.fixtures import graph_factory

_WEIGHTS = {"degree": 0.6, "betweenness": 0.4}


def _reader(tmp_path: Path) -> GraphReader:
    nodes = ["mod", "hub", "mid", "far", "lonely"]
    edges = [
        graph_factory.make_edge("mod", "hub", relation="contains"),
        graph_factory.make_edge("hub", "mid"),
        graph_factory.make_edge("hub", "far"),
        graph_factory.make_edge("mid", "far"),
    ]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def test_unseeded_ranking_uses_centrality_alone(tmp_path: Path) -> None:
    ranked = ranking.rank_nodes(_reader(tmp_path), top_k=3, weights=_WEIGHTS)
    assert ranked[0].id == "hub"


def test_unseeded_ranking_is_never_degenerate(tmp_path: Path) -> None:
    """The origin's silent failure mode: every score 0.0, order meaningless."""
    scores = ranking.score_nodes(_reader(tmp_path), weights=_WEIGHTS)
    assert len({round(value, 6) for value in scores.values()}) > 1


def test_file_roots_are_excluded_from_the_ranking(tmp_path: Path) -> None:
    ranked = ranking.rank_nodes(_reader(tmp_path), top_k=10, weights=_WEIGHTS)
    assert "mod" not in {node.id for node in ranked}


def test_isolated_nodes_rank_last(tmp_path: Path) -> None:
    ranked = ranking.rank_nodes(_reader(tmp_path), top_k=10, weights=_WEIGHTS)
    assert ranked[-1].id == "lonely"


def test_a_seed_pulls_its_neighbourhood_up(tmp_path: Path) -> None:
    """Proximity is a multiplier, not an override: a seeded node rises, but a much more
    central node can still outrank it. The property that matters is the improvement."""
    reader = _reader(tmp_path)
    unseeded = [n.id for n in ranking.rank_nodes(reader, top_k=10, weights=_WEIGHTS)]
    seeded = [n.id for n in ranking.rank_nodes(reader, top_k=10, weights=_WEIGHTS, seed_id="mid")]
    assert seeded.index("mid") < unseeded.index("mid")


def test_a_seed_demotes_what_is_far_from_it(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    scores = ranking.score_nodes(reader, _WEIGHTS, seed_id="far")
    assert scores["far"] > scores["mid"]


def test_a_node_unreachable_from_the_seed_scores_zero(tmp_path: Path) -> None:
    assert ranking.score_nodes(_reader(tmp_path), _WEIGHTS, seed_id="far")["lonely"] == 0.0


def test_an_unknown_seed_raises_instead_of_silently_degrading(tmp_path: Path) -> None:
    """The origin scored everything 0.0 and said nothing. That is the bug."""
    with pytest.raises(KeyError, match="seed"):
        ranking.rank_nodes(_reader(tmp_path), top_k=3, weights=_WEIGHTS, seed_id="nope")


def test_top_k_limits_the_result(tmp_path: Path) -> None:
    assert len(ranking.rank_nodes(_reader(tmp_path), top_k=2, weights=_WEIGHTS)) == 2


def test_ranking_is_deterministic(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    first = [n.id for n in ranking.rank_nodes(reader, top_k=5, weights=_WEIGHTS)]
    assert first == [n.id for n in ranking.rank_nodes(reader, top_k=5, weights=_WEIGHTS)]


def test_an_empty_graph_ranks_to_nothing(tmp_path: Path) -> None:
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(), filename="empty.json")
    assert ranking.rank_nodes(GraphReader(path), top_k=5, weights=_WEIGHTS) == []


def test_metric_description_states_what_was_actually_used(tmp_path: Path) -> None:
    """hot.md must not claim proximity weighting when no seed was given."""
    assert "proximity" not in ranking.metric_description(_WEIGHTS, None)
    assert "far" in ranking.metric_description(_WEIGHTS, "far")


def _mixed(tmp_path: Path) -> GraphReader:
    """A test helper with more edges than the source symbol it exercises."""
    nodes = [
        graph_factory.make_node("src_core", source_file="src/pkg/core.py"),
        graph_factory.make_node("src_core_run", source_file="src/pkg/core.py"),
        graph_factory.make_node("tests_t", source_file="tests/test_core.py"),
        graph_factory.make_node("tests_t_helper", source_file="tests/test_core.py"),
        graph_factory.make_node("tests_t_a", source_file="tests/test_core.py"),
        graph_factory.make_node("tests_t_b", source_file="tests/test_core.py"),
    ]
    edges = [
        graph_factory.make_edge("src_core", "src_core_run", relation="contains"),
        graph_factory.make_edge("tests_t", "tests_t_helper", relation="contains"),
        graph_factory.make_edge("tests_t_a", "tests_t_helper", relation="calls"),
        graph_factory.make_edge("tests_t_b", "tests_t_helper", relation="calls"),
        graph_factory.make_edge("tests_t_a", "src_core_run", relation="calls"),
    ]
    path = graph_factory.write_graph(
        tmp_path, graph_factory.graph_dict(nodes, edges), filename="mixed.json"
    )
    return GraphReader(path)


def test_without_a_penalty_a_test_helper_outranks_real_source(tmp_path: Path) -> None:
    """The observed defect: hot.md led with test fixtures on a real repository."""
    ranked = ranking.rank_nodes(_mixed(tmp_path), top_k=1, weights=_WEIGHTS, test_penalty=1.0)
    assert ranked[0].id == "tests_t_helper"


def test_the_penalty_puts_source_first(tmp_path: Path) -> None:
    ranked = ranking.rank_nodes(_mixed(tmp_path), top_k=1, weights=_WEIGHTS)
    assert ranked[0].id == "src_core_run"


def test_tests_are_still_ranked_not_dropped(tmp_path: Path) -> None:
    """Tests are real structure and often the best documentation — demote, never hide."""
    ranked = ranking.rank_nodes(_mixed(tmp_path), top_k=10, weights=_WEIGHTS)
    assert "tests_t_helper" in {node.id for node in ranked}


def test_test_detection_matches_common_layouts(tmp_path: Path) -> None:
    for path in ("tests/test_x.py", "src/pkg/test_x.py", "src/pkg/x_test.py", "tests/conftest.py"):
        assert ranking.is_test_path(path), path


def test_ordinary_source_is_not_mistaken_for_a_test(tmp_path: Path) -> None:
    for path in ("src/pkg/contest.py", "src/latest.py", "src/pkg/protest_handler.py"):
        assert not ranking.is_test_path(path), path
