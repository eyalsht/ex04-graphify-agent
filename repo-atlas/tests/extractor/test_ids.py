"""Id derivation pins EXTRACTOR_SPEC §2's irregularities, not a plausible approximation.

Each test here exists because a reasonable-looking implementation gets it wrong: strip ``.py``
after slugging and you get ``..._step1_py``; strip only leading underscores and ``__init__``
becomes ``init__``; chain a method off the module and the class segment vanishes.
"""

from __future__ import annotations

import pytest

from repo_atlas.extractor import ids
from repo_atlas.extractor.models import Symbol


def test_slug_lowercases_and_maps_separator_punctuation() -> None:
    assert ids.slug("Pkg/Sub-Mod.Name") == "pkg_sub_mod_name"


def test_module_id_strips_the_py_suffix_before_slugging() -> None:
    """Slug first and the trailing ``.py`` becomes ``_py`` — the classic wrong answer."""
    assert ids.module_id("mathsquiz/mathsquiz-step1.py") == "mathsquiz_mathsquiz_step1"


def test_module_id_strips_only_a_trailing_py() -> None:
    assert ids.module_id("pkg/py_utils.py") == "pkg_py_utils"
    assert ids.module_id("pkg/mod.pyx") == "pkg_mod_pyx"
    assert ids.module_id("pkg/py") == "pkg_py"


def test_module_id_keeps_the_dunder_segment_of_a_package_init() -> None:
    """§2 rule 6: dunder stripping is a symbol rule, not a path rule."""
    assert ids.module_id("pkg/__init__.py") == "pkg___init__"


def test_module_id_of_a_non_python_file_keeps_its_extension() -> None:
    assert ids.module_id("docs/README.md") == "docs_readme_md"


def test_method_id_strips_dunders_on_both_sides_and_chains_off_the_class() -> None:
    class_identifier = ids.class_id(ids.module_id("polygons/polygons.py"), "Polygon")
    assert class_identifier == "polygons_polygons_polygon"
    assert ids.method_id(class_identifier, "__init__") == "polygons_polygons_polygon_init"


def test_module_level_function_chains_off_the_module_not_a_class() -> None:
    module = ids.module_id("mathsquiz/mathsquiz-step2.py")
    assert ids.function_id(module, "welcome_message") == "mathsquiz_mathsquiz_step2_welcome_message"


def test_module_level_function_id_does_not_strip_underscores() -> None:
    """The §2 table applies ``strip('_')`` to methods only. Asymmetric on purpose."""
    assert ids.function_id("pkg_mod", "_helper") == "pkg_mod__helper"
    assert ids.method_id("pkg_mod_cls", "_helper") == "pkg_mod_cls_helper"


def test_external_id_is_bare_lowercase_with_no_module_prefix() -> None:
    assert ids.external_id("Object") == "object"


def test_rationale_id_uses_the_one_based_line() -> None:
    assert ids.rationale_id("polygons_polygons", 18) == "polygons_polygons_rationale_18"


def test_symbol_id_dispatches_on_kind() -> None:
    cls = Symbol(kind="class", name="Polygon", lineno=3)
    method = Symbol(kind="method", name="__init__", lineno=4, parent="Polygon")
    func = Symbol(kind="function", name="draw", lineno=9)
    assert ids.symbol_id("m", cls) == "m_polygon"
    assert ids.symbol_id("m_polygon", method) == "m_polygon_init"
    assert ids.symbol_id("m", func) == "m_draw"


def test_symbol_id_rejects_an_unknown_kind() -> None:
    with pytest.raises(ValueError, match="unknown symbol kind"):
        ids.symbol_id("m", Symbol(kind="widget", name="x", lineno=1))


def test_qualified_name_joins_the_parent_path() -> None:
    assert ids.qualified_name(Symbol(kind="function", name="f", lineno=1)) == "f"
    nested = Symbol(kind="method", name="m", lineno=2, parent="Outer.Inner")
    assert ids.qualified_name(nested) == "Outer.Inner.m"
