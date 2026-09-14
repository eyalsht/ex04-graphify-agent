"""Guard test: the vendored golden fixture stays intact and correctly pinned (PHASE1-002).

Only this test and the extractor's golden-regression eval may read
``tests/fixtures/golden/`` (``.claude/skills/eval-harness/SKILL.md``). If this test
ever fails after a "just refresh the fixture" commit, read
``tests/fixtures/golden/PROVENANCE.md`` first: ``polygons.py`` is pinned to a specific
git blob on purpose, because the working tree's current version is *not* what the
reference graph was built from.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

_GOLDEN = Path(__file__).resolve().parent / "golden"
_POLYGONS = _GOLDEN / "broken-python" / "polygons" / "polygons.py"
_REFERENCE_GRAPH = _GOLDEN / "reference_graph.json"
_PROVENANCE = _GOLDEN / "PROVENANCE.md"

_TODO_LINES = (18, 33, 50)
_SHA_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", re.MULTILINE)


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_polygons_py_is_pinned_to_the_75_line_pre_rewrite_blob() -> None:
    assert len(_lines(_POLYGONS)) == 75


def test_polygons_py_still_has_the_new_keyword_bug_at_line_29() -> None:
    assert "new Polygon(" in _lines(_POLYGONS)[28]


def test_polygons_py_still_has_all_three_todo_comments() -> None:
    lines = _lines(_POLYGONS)
    for line_no in _TODO_LINES:
        assert lines[line_no - 1].lstrip().startswith("# TODO:"), f"line {line_no}"


def test_reference_graph_parses_with_23_nodes_and_20_links() -> None:
    data = json.loads(_REFERENCE_GRAPH.read_text(encoding="utf-8"))
    assert len(data["nodes"]) == 23
    assert len(data["links"]) == 20


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _recorded_hashes() -> dict[str, str]:
    text = _PROVENANCE.read_text(encoding="utf-8")
    return dict(_SHA_ROW.findall(text))


def test_every_vendored_file_matches_its_recorded_sha256() -> None:
    recorded = _recorded_hashes()
    assert recorded, "PROVENANCE.md has no parseable SHA-256 table"

    source_files = sorted(p for p in (_GOLDEN / "broken-python").rglob("*") if p.is_file())
    vendored = [_REFERENCE_GRAPH, *source_files]

    seen: set[str] = set()
    for path in vendored:
        rel = path.relative_to(_GOLDEN).as_posix()
        seen.add(rel)
        assert rel in recorded, f"{rel} is vendored but missing from PROVENANCE.md"
        assert _sha256(path) == recorded[rel], f"{rel} no longer matches its recorded SHA-256"

    stale = set(recorded) - seen
    assert not stale, f"PROVENANCE.md records hashes for files no longer vendored: {stale}"
