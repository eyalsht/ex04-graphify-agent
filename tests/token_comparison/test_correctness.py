"""TDD for check_correctness (PHASE6-015..028, TC-T4/TC-T5).

A run is correctness=pass only if all three TODO resolutions hold:
1. calc_polygon_details(5) -> 540/108, (6) -> 720/120 (general formula).
2. Module imports without NameError/SyntaxError; calc_polygon_details uses a real Polygon.
3. Mocked-turtle draw_polygon(pentagon) issues 5 forward/right, each turn 360/5.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ex04_graphify_agent.token_comparison.correctness import _exec_module, check_correctness

_FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _fixed_source() -> str:
    return (_FIXTURES / "polygons_fixed.txt").read_text(encoding="utf-8")


def _broken_source() -> str:
    # Pinned to the PRE-FIX fixture: the live data/broken-python/polygons/polygons.py is now
    # the POST-FIX deliverable (Phase 7), so TC-T5 reads the committed original instead.
    return (_FIXTURES / "polygons_broken.txt").read_text(encoding="utf-8")


def test_check_correctness_true_for_fixed_source() -> None:
    """TC-T4: pentagon 540/108, hexagon 720/120, Polygon used, mocked-turtle 5 sides."""
    assert check_correctness(_fixed_source()) is True


def test_check_correctness_false_for_broken_source() -> None:
    """TC-T5: original broken polygons.py (else 1000/200, hardcoded 6) fails."""
    assert check_correctness(_broken_source()) is False


def test_pentagon_formula_540_108() -> None:
    source = _fixed_source()
    assert check_correctness(source) is True
    # The pentagon formula is exercised inside check_correctness; a source with the
    # original else-branch hardcode (1000/200) must fail even if syntactically valid.
    broken_formula = source.replace(
        "internal_angles_sum = (sides - 2) * 180",
        "internal_angles_sum = 1000",
    )
    assert check_correctness(broken_formula) is False


def test_hexagon_formula_720_120() -> None:
    source = _fixed_source()
    broken_formula = source.replace(
        "internal_angle = internal_angles_sum / sides",
        "internal_angle = 200",
    )
    assert check_correctness(broken_formula) is False


def test_draw_polygon_hardcoded_six_fails() -> None:
    source = _fixed_source()
    hardcoded = source.replace(
        "for i in range(0, polygon.sides):", "for i in range(0, 6):"
    ).replace("t.right(360 / polygon.sides)", "t.right(60)")
    assert check_correctness(hardcoded) is False


def test_calc_polygon_details_rejects_fewer_than_three_sides() -> None:
    """Signal-4 critical-path guard: <3 sides is invalid geometry and would otherwise
    ZeroDivisionError on `360 / sides`; calc_polygon_details must raise ValueError instead."""
    namespace = _exec_module(_fixed_source())
    assert namespace is not None
    calc = namespace["calc_polygon_details"]
    for bad in (2, 1, 0, -3):
        with pytest.raises(ValueError):
            calc(bad)
    # A valid polygon still works (no over-eager guard).
    assert calc(3).sides == 3


def test_all_three_resolutions_must_hold() -> None:
    """PHASE6-027/028: pass requires ALL three; a single failing axis fails the gate."""
    source = _fixed_source()
    # Break only the Polygon usage (axis 2): calc_polygon_details returns a bare dict.
    broken_polygon_usage = source.replace(
        "poly = Polygon(sides, internal_angles_sum, internal_angle)\n\n    return poly",
        '    return {"sides": sides}',
    )
    assert check_correctness(broken_polygon_usage) is False
