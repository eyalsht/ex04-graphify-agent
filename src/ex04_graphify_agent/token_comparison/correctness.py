"""check_correctness — the 3-part automated correctness check (PHASE6-015..028).

Loads a candidate ``polygons.py`` source and asserts all three TODO resolutions from
``docs/PRD_token_comparison.md`` "Correctness check": (1) the general internal-angle
formula for pentagon/hexagon, (2) ``Polygon`` is valid and actually used, and (3)
``draw_polygon`` is generalized (mocked turtle, sides-many forward/right calls). A run is
``correctness == True`` only if ALL three hold (TC-T4); the original broken source
(``SyntaxError`` from ``new Polygon(...)``) fails immediately (TC-T5).
"""

from __future__ import annotations

import builtins
import sys
import types
from typing import Any
from unittest.mock import MagicMock


def check_correctness(fixed_source: str) -> bool:
    """True only if the angle formula, Polygon usage, and draw_polygon are all fixed."""
    module_ns = _exec_module(fixed_source)
    if module_ns is None:
        return False
    return (
        _check_angle_formula(module_ns)
        and _check_polygon_usage(module_ns)
        and _check_draw_polygon(module_ns)
    )


def _exec_module(source: str) -> dict[str, Any] | None:
    """Compile + exec ``source`` with a mocked turtle/input; ``None`` on any failure."""
    mock_turtle = _make_mock_turtle_module()
    namespace: dict[str, Any] = {
        "__name__": "polygons_under_test",
        "__builtins__": builtins,
    }
    real_turtle = sys.modules.get("turtle")
    sys.modules["turtle"] = mock_turtle
    try:
        code = compile(source, "<polygons_fixed>", "exec")
        with _MockedInput(["5", "n"]):
            exec(code, namespace)
    except Exception:
        return None
    finally:
        if real_turtle is not None:
            sys.modules["turtle"] = real_turtle
        else:
            sys.modules.pop("turtle", None)
    return namespace


def _make_mock_turtle_module() -> types.ModuleType:
    """A ``turtle`` stand-in: ``Screen``/``Turtle`` return inert mocks (no window)."""
    module = types.ModuleType("turtle")
    module.Screen = MagicMock(return_value=MagicMock())  # type: ignore[attr-defined]
    module.Turtle = MagicMock(return_value=MagicMock())  # type: ignore[attr-defined]
    return module


class _MockedInput:
    """Context manager swapping ``builtins.input`` for a canned-answer queue."""

    def __init__(self, answers: list[str]) -> None:
        self._answers = list(answers)
        self._original = builtins.input

    def __enter__(self) -> None:
        answers = iter(self._answers)
        builtins.input = lambda *_args: next(answers, "n")

    def __exit__(self, *exc_info: object) -> None:
        builtins.input = self._original


def _check_angle_formula(module_ns: dict[str, Any]) -> bool:
    """TODO@L18: pentagon -> 540/108, hexagon -> 720/120 (sum=(n-2)*180, each=sum/n)."""
    calc = module_ns.get("calc_polygon_details")
    if not callable(calc):
        return False
    pentagon = _angle_fields(calc(5))
    hexagon = _angle_fields(calc(6))
    if pentagon is None or hexagon is None:
        return False
    return pentagon == (540, 108) and hexagon == (720, 120)


def _angle_fields(result: Any) -> tuple[int, int] | None:
    """Extract ``(internal_angles_sum, internal_angle)`` from an attr- or dict-shaped result."""
    for sum_key, angle_key in (("internal_angles_sum", "internal_angle"),):
        if hasattr(result, sum_key) and hasattr(result, angle_key):
            return int(getattr(result, sum_key)), int(getattr(result, angle_key))
        if isinstance(result, dict) and sum_key in result and angle_key in result:
            return int(result[sum_key]), int(result[angle_key])
    return None


def _check_polygon_usage(module_ns: dict[str, Any]) -> bool:
    """TODO@L33: ``Polygon`` is a valid class and ``calc_polygon_details`` returns one."""
    polygon_cls = module_ns.get("Polygon")
    calc = module_ns.get("calc_polygon_details")
    if not isinstance(polygon_cls, type) or not callable(calc):
        return False
    return isinstance(calc(5), polygon_cls)


def _check_draw_polygon(module_ns: dict[str, Any]) -> bool:
    """TODO@L50: mocked-turtle draw_polygon(pentagon) -> 5 forward/right, turn 360/5."""
    draw = module_ns.get("draw_polygon")
    polygon_cls = module_ns.get("Polygon")
    turtle_module = module_ns.get("turtle")
    if not callable(draw) or not isinstance(polygon_cls, type) or turtle_module is None:
        return False
    pentagon = polygon_cls(5, 540, 108)
    mock_turtle = MagicMock()
    turtle_module.Turtle = MagicMock(return_value=mock_turtle)
    try:
        draw(pentagon)
    except Exception:
        return False
    if mock_turtle.forward.call_count != 5 or mock_turtle.right.call_count != 5:
        return False
    expected_turn = 360 / 5
    return all(call.args[0] == expected_turn for call in mock_turtle.right.call_args_list)
