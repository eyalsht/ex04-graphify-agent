"""Vault rendering and writing (PRD R3.1).

The headline requirement is that a generated vault has zero dangling wikilinks. The
origin's writer linked every node note to a ``community-N.md`` it never created, and its
consistency gate only scanned index.md/hot.md, so nothing caught it.
"""

from __future__ import annotations

import re
from pathlib import Path

from repo_atlas.graph_reader import GraphReader
from repo_atlas.vault import VaultWriter
from tests.fixtures import graph_factory

_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")


def _reader(tmp_path: Path) -> GraphReader:
    nodes = [
        graph_factory.make_node("mod", label="mod.py", community=0),
        graph_factory.make_node("mod_hub", label="hub()", community=0),
        graph_factory.make_node("mod_leaf", label="leaf()", community=1),
    ]
    edges = [
        graph_factory.make_edge("mod", "mod_hub", relation="contains"),
        graph_factory.make_edge("mod", "mod_leaf", relation="contains"),
        graph_factory.make_edge("mod_hub", "mod_leaf", relation="calls"),
    ]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def _written(tmp_path: Path, seed: str | None = None) -> Path:
    vault = tmp_path / "vault"
    VaultWriter(_reader(tmp_path), vault).write_all(top_k=2, seed_id=seed)
    return vault


def test_writes_index_hot_and_a_note_per_node(tmp_path: Path) -> None:
    names = {path.name for path in _written(tmp_path).glob("*.md")}
    assert {"index.md", "hot.md", "mod.md", "mod_hub.md", "mod_leaf.md"} <= names


def test_writes_a_note_for_every_referenced_community(tmp_path: Path) -> None:
    names = {path.name for path in _written(tmp_path).glob("*.md")}
    assert {"community-0.md", "community-1.md"} <= names


def test_no_wikilink_dangles(tmp_path: Path) -> None:
    """The property the origin's vault could not satisfy."""
    vault = _written(tmp_path)
    stems = {path.stem for path in vault.glob("*.md")}
    for note in vault.glob("*.md"):
        for target in _WIKILINK.findall(note.read_text(encoding="utf-8")):
            assert target in stems, f"{note.name} -> [[{target}]]"


def test_node_note_carries_frontmatter_and_source(tmp_path: Path) -> None:
    body = (_written(tmp_path) / "mod_hub.md").read_text(encoding="utf-8")
    assert body.startswith("---\n")
    assert "label: hub()" in body


def test_node_note_lists_relations_in_both_directions(tmp_path: Path) -> None:
    body = (_written(tmp_path) / "mod_leaf.md").read_text(encoding="utf-8")
    assert "Incoming" in body and "[[mod_hub" in body


def test_hot_states_the_metric_it_actually_used(tmp_path: Path) -> None:
    unseeded = (_written(tmp_path) / "hot.md").read_text(encoding="utf-8")
    assert "proximity" not in unseeded
    seeded = (_written(tmp_path, seed="mod_leaf") / "hot.md").read_text(encoding="utf-8")
    assert "proximity" in seeded and "mod_leaf" in seeded


def test_hot_honours_top_k(tmp_path: Path) -> None:
    body = (_written(tmp_path) / "hot.md").read_text(encoding="utf-8")
    ranked = [line for line in body.splitlines() if re.match(r"^\d+\. ", line)]
    assert len(ranked) == 2


def test_index_lists_communities_and_every_node(tmp_path: Path) -> None:
    body = (_written(tmp_path) / "index.md").read_text(encoding="utf-8")
    assert "[[community-0|Community 0]]" in body
    assert "[[mod_hub|hub()]]" in body


def test_community_note_lists_its_members(tmp_path: Path) -> None:
    body = (_written(tmp_path) / "community-1.md").read_text(encoding="utf-8")
    assert "[[mod_leaf|leaf()]]" in body
    assert "[[mod_hub" not in body


def test_writing_twice_is_idempotent(tmp_path: Path) -> None:
    first = {p.name: p.read_text("utf-8") for p in _written(tmp_path).glob("*.md")}
    second = {p.name: p.read_text("utf-8") for p in _written(tmp_path).glob("*.md")}
    assert first == second


def test_an_endpoint_missing_from_the_nodes_array_still_gets_a_note(tmp_path: Path) -> None:
    """networkx materialises an id that appears only in `links`. The writer emits a note
    for it too, so a producer's incomplete `nodes` array cannot dangle a link."""
    nodes = [graph_factory.make_node("a"), graph_factory.make_node("b")]
    edges = [graph_factory.make_edge("a", "b", relation="calls")]
    data = graph_factory.graph_dict(nodes, edges)
    data["nodes"] = [node for node in data["nodes"] if node["id"] != "b"]
    path = graph_factory.write_graph(tmp_path, data, filename="partial.json")
    vault = tmp_path / "partial-vault"
    VaultWriter(GraphReader(path), vault).write_all(top_k=2)
    assert "[[b" in (vault / "a.md").read_text(encoding="utf-8")
    assert (vault / "b.md").is_file()
