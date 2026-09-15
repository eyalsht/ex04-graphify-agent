"""Self-hosting: repo-atlas maps itself (PRD §6.1).

The real acceptance test. The golden regression proves the extractor reproduces a known
graph; this proves the whole pipeline produces a *useful* map of a repository we know well
enough to judge. Keyless, so it asserts structure and retrieval — not the LLM's prose.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas import sdk
from repo_atlas.paths import RunPaths

_PROJECT = Path(__file__).resolve().parents[2]
#: Modules a reader of this repository genuinely needs; if the map omits them it is wrong.
_CORE_MODULES = (
    "src/repo_atlas/extractor/parse.py",
    "src/repo_atlas/extractor/build.py",
    "src/repo_atlas/graph_reader/reader.py",
    "src/repo_atlas/vault/writer.py",
    "src/repo_atlas/brief/runner.py",
)


@pytest.fixture(scope="module")
def mapped(tmp_path_factory: pytest.TempPathFactory) -> tuple[object, Path]:
    out = tmp_path_factory.mktemp("self_atlas")
    paths = RunPaths.create(_PROJECT, out=out)
    extract_result, vault_result = sdk.map_repo(paths)
    return extract_result, vault_result.vault_dir


@pytest.mark.eval
def test_maps_its_own_core_modules(mapped) -> None:  # type: ignore[no-untyped-def]
    extract_result, _ = mapped
    import json

    data = json.loads(extract_result.graph_path.read_text(encoding="utf-8"))
    mapped_files = {node["source_file"] for node in data["nodes"]}
    missing = [module for module in _CORE_MODULES if module not in mapped_files]
    assert missing == [], f"core modules absent from the graph: {missing}"


@pytest.mark.eval
def test_the_graph_is_connected_enough_to_be_a_map(mapped) -> None:  # type: ignore[no-untyped-def]
    """Cross-file edges are what stop this being a pile of per-file islands."""
    extract_result, _ = mapped
    import json

    data = json.loads(extract_result.graph_path.read_text(encoding="utf-8"))
    cross_file = [link for link in data["links"] if link["relation"] == "references"]
    assert len(cross_file) > 50, "too few cross-file edges — the graph has fragmented"


@pytest.mark.eval
def test_hot_leads_with_source_not_test_helpers(mapped) -> None:  # type: ignore[no-untyped-def]
    """The defect self-hosting originally exposed: hot.md ranked test fixtures first."""
    _, vault_dir = mapped
    ranked = [
        line
        for line in (vault_dir / "hot.md").read_text(encoding="utf-8").splitlines()
        if line[:1].isdigit() and ". " in line[:4]
    ]
    assert ranked, "hot.md ranked nothing"
    from_source = [line for line in ranked[:5] if "src/repo_atlas" in line]
    assert len(from_source) >= 3, "hot.md is dominated by non-source nodes:\n" + "\n".join(
        ranked[:5]
    )


@pytest.mark.eval
def test_the_vault_has_no_dangling_links(mapped) -> None:  # type: ignore[no-untyped-def]
    import re

    _, vault_dir = mapped
    wikilink = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
    stems = {path.stem for path in vault_dir.glob("*.md")}
    dangling = [
        (note.name, target)
        for note in vault_dir.glob("*.md")
        for target in wikilink.findall(note.read_text(encoding="utf-8"))
        if target not in stems
    ]
    assert dangling == [], f"dangling wikilinks: {dangling[:5]}"
