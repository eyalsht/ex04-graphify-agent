"""Fixture AgentStates for token_comparison tests (TC-T1..3, T6, T9, T10).

Keyless, hand-built ``AgentState`` dicts with known ``token_usage`` / ``files_read`` /
``findings_tried`` so the metrics math is exactly checkable (no real LLM call).
"""

from __future__ import annotations

from typing import Any

from ex04_graphify_agent.agent_workflow.state import AgentState


def graph_guided_state(input_tokens: int = 1_200, output_tokens: int = 80) -> AgentState:
    """3 files read (index.md, hot.md, polygons.py), 1 validated iteration, 2 LLM calls."""
    token_usage: list[dict[str, Any]] = [
        {"node": "plan", "input_tokens": 50, "output_tokens": 5},
        {
            "node": "fix",
            "input_tokens": input_tokens - 50,
            "output_tokens": output_tokens - 5,
        },
    ]
    return AgentState(
        run_type="graph_guided",
        messages=[],
        vault_context="vault",
        dumped_context="",
        current_hypothesis=None,
        validated_source="source",
        validated=True,
        findings_tried=1,
        files_read=[
            "obsidian/index.md",
            "obsidian/hot.md",
            "data/broken-python/polygons/polygons.py",
        ],
        fix_diff="--- a\n+++ b\n",
        token_usage=token_usage,  # type: ignore[typeddict-item]
    )


def naive_state(input_tokens: int = 8_000, output_tokens: int = 80) -> AgentState:
    """9 files dumped (whole repo), 1 iteration, 2 LLM calls."""
    token_usage: list[dict[str, Any]] = [
        {"node": "plan", "input_tokens": 50, "output_tokens": 5},
        {
            "node": "fix",
            "input_tokens": input_tokens - 50,
            "output_tokens": output_tokens - 5,
        },
    ]
    files = [f"data/broken-python/file_{i}.py" for i in range(9)]
    return AgentState(
        run_type="naive",
        messages=[],
        vault_context="",
        dumped_context="dump",
        current_hypothesis=None,
        validated_source=None,
        validated=False,
        findings_tried=0,
        files_read=files,
        fix_diff="--- a\n+++ b\n",
        token_usage=token_usage,  # type: ignore[typeddict-item]
    )
