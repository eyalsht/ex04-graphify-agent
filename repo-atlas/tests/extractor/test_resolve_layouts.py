"""Module-name resolution across the two standard Python project layouts.

Split from test_resolve.py for the 150-line cap; these cases are about *how a file is
addressed* rather than which edges come out of it.
"""

from __future__ import annotations

from repo_atlas.extractor import parse, py_nodes, resolve


def _triples(sources: dict[str, str]) -> set[tuple[str, str, str]]:
    parsed = {path: parse.parse_source(path, text) for path, text in sources.items()}
    built = {path: py_nodes.build_file_nodes(item) for path, item in parsed.items()}
    return {(e.relation, e.source, e.target) for e in resolve.cross_file_edges(parsed, built)}


_SRC_LAYOUT = {
    "src/pkg/__init__.py": "",
    "src/pkg/core.py": "def run():\n    return 1\n",
    "src/pkg/user.py": "from pkg.core import run\n\n\ndef go():\n    return run()\n",
}


def test_a_src_layout_package_resolves_its_own_imports() -> None:
    """`src/pkg/core.py` is imported as `pkg.core`, not `src.pkg.core`.

    Regression: deriving the module name straight from the file path meant every
    src-layout repository — one of the two standard layouts — resolved almost no
    cross-file edges at all, leaving its graph a pile of islands.
    """
    triples = _triples(_SRC_LAYOUT)
    assert ("references", "src_pkg_user", "src_pkg_core") in triples
    assert ("calls", "src_pkg_user_go", "src_pkg_core_run") in triples


def test_a_flat_layout_still_resolves() -> None:
    """The fix must not break the layout that already worked."""
    sources = {
        "pkg/__init__.py": "",
        "pkg/core.py": "def run():\n    return 1\n",
        "pkg/user.py": "from pkg.core import run\n",
    }
    assert ("references", "pkg_user", "pkg_core") in _triples(sources)


def test_a_directory_without_an_init_is_treated_as_a_source_root() -> None:
    sources = {
        "lib/pkg/__init__.py": "",
        "lib/pkg/a.py": "def f():\n    return 1\n",
        "lib/pkg/b.py": "from pkg.a import f\n",
    }
    assert ("references", "lib_pkg_b", "lib_pkg_a") in _triples(sources)
