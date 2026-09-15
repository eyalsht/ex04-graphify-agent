"""Cross-file edge resolution.

Without these, every file is an island: betweenness is 0.000 everywhere, communities are
just file boundaries, and hot.md degenerates to raw degree — which favours whichever
helper a single test file calls most.
"""

from __future__ import annotations

from repo_atlas.extractor import parse, py_nodes, resolve

_SHAPES = "class Shape:\n    pass\n\n\ndef make():\n    return Shape()\n"
_USER = "from pkg.shapes import make\n\n\ndef run():\n    return make()\n"


def _resolved(sources: dict[str, str]) -> list:
    parsed = {path: parse.parse_source(path, text) for path, text in sources.items()}
    built = {path: py_nodes.build_file_nodes(item) for path, item in parsed.items()}
    return resolve.cross_file_edges(parsed, built)


def _triples(sources: dict[str, str]) -> set[tuple[str, str, str]]:
    return {(e.relation, e.source, e.target) for e in _resolved(sources)}


def test_an_import_links_the_two_modules() -> None:
    triples = _triples({"pkg/shapes.py": _SHAPES, "pkg/user.py": _USER})
    assert ("references", "pkg_user", "pkg_shapes") in triples


def test_an_imported_symbol_resolves_a_cross_file_call() -> None:
    triples = _triples({"pkg/shapes.py": _SHAPES, "pkg/user.py": _USER})
    assert ("calls", "pkg_user_run", "pkg_shapes_make") in triples


def test_a_third_party_import_produces_no_edge() -> None:
    """os is not part of this repository, so it is not part of this repository's map."""
    assert _triples({"m.py": "import os\n\n\ndef f():\n    return os.getcwd()\n"}) == set()


def test_a_dotted_import_resolves_to_the_module() -> None:
    sources = {"pkg/shapes.py": _SHAPES, "m.py": "import pkg.shapes\n"}
    assert ("references", "m", "pkg_shapes") in _triples(sources)


def test_a_package_init_resolves_by_its_package_name() -> None:
    sources = {"pkg/__init__.py": "VALUE = 1\n", "m.py": "from pkg import VALUE\n"}
    assert ("references", "m", "pkg___init__") in _triples(sources)


def test_a_relative_import_resolves_within_the_package() -> None:
    sources = {"pkg/shapes.py": _SHAPES, "pkg/user.py": "from .shapes import make\n"}
    assert ("references", "pkg_user", "pkg_shapes") in _triples(sources)


def test_an_aliased_import_still_resolves_its_calls() -> None:
    sources = {
        "pkg/shapes.py": _SHAPES,
        "pkg/user.py": "from pkg.shapes import make as build\n\n\ndef run():\n    return build()\n",
    }
    assert ("calls", "pkg_user_run", "pkg_shapes_make") in _triples(sources)


def test_cross_file_edges_are_extracted_confidence() -> None:
    edges = _resolved({"pkg/shapes.py": _SHAPES, "pkg/user.py": _USER})
    assert {e.confidence for e in edges} == {"EXTRACTED"}


def test_a_module_level_cross_file_call_produces_no_call_edge() -> None:
    """Same rule as intra-file: a call must sit inside a definition."""
    sources = {"pkg/shapes.py": _SHAPES, "pkg/user.py": "from pkg.shapes import make\n\nmake()\n"}
    assert not [t for t in _triples(sources) if t[0] == "calls"]


def test_no_self_reference_edge_for_a_module_importing_itself() -> None:
    sources = {"pkg/m.py": "from pkg.m import thing\n\n\ndef thing():\n    pass\n"}
    assert not [t for t in _triples(sources) if t[0] == "references"]


def test_results_are_deterministic() -> None:
    sources = {"pkg/shapes.py": _SHAPES, "pkg/user.py": _USER}
    first = [(e.relation, e.source, e.target) for e in _resolved(sources)]
    assert first == [(e.relation, e.source, e.target) for e in _resolved(sources)]


def test_duplicate_imports_yield_one_edge() -> None:
    sources = {
        "pkg/shapes.py": _SHAPES,
        "pkg/user.py": "from pkg.shapes import make\nfrom pkg.shapes import Shape\n",
    }
    references = [t for t in _triples(sources) if t[0] == "references"]
    assert len(references) == 1


_HELPERS = "def build():\n    return 1\n"


def test_a_module_attribute_call_resolves() -> None:
    """`from pkg import helpers` then `helpers.build()` — the commonest Python idiom."""
    sources = {
        "pkg/helpers.py": _HELPERS,
        "pkg/user.py": "from pkg import helpers\n\n\ndef run():\n    return helpers.build()\n",
    }
    assert ("calls", "pkg_user_run", "pkg_helpers_build") in _triples(sources)


def test_an_aliased_module_attribute_call_resolves() -> None:
    sources = {
        "pkg/helpers.py": _HELPERS,
        "pkg/user.py": "import pkg.helpers as h\n\n\ndef run():\n    return h.build()\n",
    }
    assert ("calls", "pkg_user_run", "pkg_helpers_build") in _triples(sources)


def test_an_attribute_call_on_a_local_object_is_not_resolved() -> None:
    """`self.x()` and `obj.method()` need type inference we deliberately do not attempt."""
    sources = {
        "pkg/helpers.py": _HELPERS,
        "pkg/user.py": "from pkg import helpers\n\n\ndef run(obj):\n    return obj.build()\n",
    }
    assert not [t for t in _triples(sources) if t[0] == "calls"]


def test_an_attribute_call_on_a_third_party_module_is_not_resolved() -> None:
    sources = {"m.py": "import os\n\n\ndef f():\n    return os.getcwd()\n"}
    assert _triples(sources) == set()


def test_importing_a_module_links_the_two_modules() -> None:
    sources = {"pkg/helpers.py": _HELPERS, "pkg/user.py": "from pkg import helpers\n"}
    assert ("references", "pkg_user", "pkg_helpers") in _triples(sources)
