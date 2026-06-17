"""TDD for fix_target.fixed_content — strip markdown fences/prose from the LLM's fix.

A live model often wraps the corrected file in a ```python ... ``` fence or adds a
"Here is the fix:" preamble. The raw text would not execute, so ``check_correctness``
fails. ``fixed_content`` must return just the code.
"""

from __future__ import annotations

from typing import cast

from ex04_graphify_agent.agent_workflow import fix_target
from ex04_graphify_agent.agent_workflow.state import AgentState, RunType

_CODE = "class Polygon(object):\n    pass"


def _state(run_type: str, validated_source: str | None = None) -> AgentState:
    state = cast(AgentState, dict.fromkeys(AgentState.__annotations__, None))
    state["run_type"] = cast(RunType, run_type)
    state["validated_source"] = validated_source
    state["target_file"] = "polygons/polygons.py"
    return state


def test_fixed_content_strips_fenced_block_with_language_tag() -> None:
    text = f"Here is the corrected file:\n```python\n{_CODE}\n```\nThat fixes it."
    assert fix_target.fixed_content(_state("graph_guided"), text) == _CODE


def test_fixed_content_strips_bare_fence() -> None:
    text = f"```\n{_CODE}\n```"
    assert fix_target.fixed_content(_state("graph_guided"), text) == _CODE


def test_fixed_content_plain_code_unchanged() -> None:
    assert fix_target.fixed_content(_state("graph_guided"), _CODE) == _CODE


def test_fixed_content_naive_strips_file_line_then_fence() -> None:
    text = f"FILE: polygons/polygons.py\n```python\n{_CODE}\n```"
    assert fix_target.fixed_content(_state("naive"), text) == _CODE


def test_fixed_content_naive_file_line_not_on_first_line() -> None:
    # _named_file scans all lines for FILE:; _strip_file_line must agree (preamble + marker dropped)
    text = f"Sure, here is your fix:\nFILE: polygons/polygons.py\n{_CODE}"
    assert fix_target.fixed_content(_state("naive"), text) == _CODE


def test_fixed_content_ignores_inline_backticks_before_real_fence() -> None:
    # a line-oriented fence must win over inline backticks earlier in the prose
    text = f"I noticed you used ```new```. Here is the fix:\n```python\n{_CODE}\n```"
    assert fix_target.fixed_content(_state("graph_guided"), text) == _CODE
