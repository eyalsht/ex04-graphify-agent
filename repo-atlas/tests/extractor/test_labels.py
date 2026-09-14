"""Label/location rules (EXTRACTOR_SPEC §3, §4).

The function/method asymmetry is deliberate and evidenced by the reference graph:
a module-level function is ``name()``, a method is ``.name()`` with a leading dot and
no class name, and a class is bare with no parens at all.
"""

from __future__ import annotations

import pytest

from repo_atlas.extractor import labels
from repo_atlas.extractor.models import Symbol


def test_module_label_is_the_basename_with_its_extension() -> None:
    assert labels.module_label("mathsquiz/mathsquiz-step1.py") == "mathsquiz-step1.py"


def test_class_label_has_no_parens() -> None:
    assert labels.symbol_label(Symbol(kind="class", name="Polygon", lineno=3)) == "Polygon"


def test_function_label_has_empty_parens() -> None:
    symbol = Symbol(kind="function", name="calc_polygon_details", lineno=13)
    assert labels.symbol_label(symbol) == "calc_polygon_details()"


def test_method_label_leads_with_a_dot_and_omits_the_class() -> None:
    symbol = Symbol(kind="method", name="__init__", lineno=5, parent="Polygon")
    assert labels.symbol_label(symbol) == ".__init__()"


def test_symbol_label_rejects_an_unknown_kind() -> None:
    with pytest.raises(ValueError, match="unknown symbol kind"):
        labels.symbol_label(Symbol(kind="widget", name="x", lineno=1))


def test_norm_label_is_exactly_lowercase() -> None:
    """No trimming, no punctuation stripping — the reference does nothing else."""
    assert labels.norm_label("# TODO: Fix This") == "# todo: fix this"
    assert labels.norm_label("MIT License") == "mit license"


def test_location_is_an_l_prefixed_one_based_line() -> None:
    assert labels.location(18) == "L18"


def test_module_location_is_always_line_one() -> None:
    """Even when the file starts with blank lines — the reference always says L1."""
    assert labels.MODULE_LOCATION == "L1"


def test_external_symbols_use_empty_string_sentinels() -> None:
    """§2 rule 4: empty strings, not None. The only place this sentinel appears."""
    assert labels.EXTERNAL_LOCATION == ""
    assert labels.EXTERNAL_SOURCE_FILE == ""
