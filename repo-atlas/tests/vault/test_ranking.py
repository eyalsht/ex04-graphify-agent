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
