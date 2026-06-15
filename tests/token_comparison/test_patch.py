"""TDD for apply_unified_diff (round-trips with agent_workflow.context.make_diff)."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow.context import make_diff
from ex04_graphify_agent.token_comparison.patch import apply_unified_diff


def test_apply_unified_diff_round_trips_multiline_change() -> None:
    original = "line1\nline2\nline3\nline4\nline5\n"
    fixed = "line1\nCHANGED\nline3\nline4\nADDED\nline5\n"
    diff = make_diff(original, fixed, "f.py")
    assert apply_unified_diff(original, diff) == fixed


def test_apply_unified_diff_full_file_replacement() -> None:
    original = "old content\n"
    fixed = "mock-response"
    diff = make_diff(original, fixed, "f.py")
    assert apply_unified_diff(original, diff) == fixed


def test_apply_unified_diff_empty_diff_returns_original() -> None:
    original = "unchanged\n"
    assert apply_unified_diff(original, "") == original


def test_apply_unified_diff_multiple_hunks() -> None:
    """A diff with two separated hunks (far-apart edits) applies both."""
    original = "".join(f"line{i}\n" for i in range(1, 21))
    fixed = original.replace("line2\n", "CHANGED2\n").replace("line18\n", "CHANGED18\n")
    diff = make_diff(original, fixed, "f.py")
    assert diff.count("@@") >= 4  # at least two hunk headers
    assert apply_unified_diff(original, diff) == fixed
